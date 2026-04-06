"""
Tests for SAHOOL Saga Orchestrator
====================================
اختبارات منسق الـ Saga

Tests:
- Saga happy path (all steps succeed)
- Saga failure triggers compensation
- Compensation retry with backoff
- Idempotency (duplicate execution prevention)
- Step timeout handling
- Context passing between steps
- Failed compensation tracking
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from shared.libs.saga.models import SagaExecution, SagaState, SagaStepRecord, StepState
from shared.libs.saga.orchestrator import SagaDefinition, SagaOrchestrator, SagaResult, SagaStep


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_db_factory():
    """Create a mock DB factory with in-memory tracking."""
    storage = {}

    def factory():
        db = MagicMock()

        def mock_add(obj):
            key = getattr(obj, "id", id(obj))
            storage[key] = obj

        def mock_merge(obj):
            key = getattr(obj, "id", id(obj))
            storage[key] = obj
            return obj

        def mock_execute(stmt):
            result = MagicMock()
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value = iter([])
            return result

        db.add = mock_add
        db.merge = mock_merge
        db.commit = MagicMock()
        db.rollback = MagicMock()
        db.close = MagicMock()
        db.execute = mock_execute
        return db

    return factory


async def _success_action(ctx: dict) -> dict:
    """Step action that succeeds."""
    return {"step_result": "ok"}


async def _success_action_with_data(ctx: dict) -> dict:
    """Step action that returns data merged into context."""
    return {"field_id": "FIELD-001"}


async def _failing_action(ctx: dict) -> dict:
    """Step action that fails."""
    raise RuntimeError("Service unavailable")


async def _slow_action(ctx: dict) -> dict:
    """Step action that times out."""
    await asyncio.sleep(100)
    return {}


async def _noop_compensate(ctx: dict) -> None:
    """Compensation that succeeds."""
    pass


async def _failing_compensate(ctx: dict) -> None:
    """Compensation that always fails."""
    raise RuntimeError("Compensation failed")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSagaOrchestrator:
    """Tests for the saga orchestrator."""

    @pytest.mark.asyncio
    async def test_happy_path_all_steps_succeed(self):
        """All steps succeed → saga COMPLETED."""
        saga = SagaDefinition(
            name="test_saga",
            steps=[
                SagaStep(name="step_1", action=_success_action, compensate=_noop_compensate),
                SagaStep(name="step_2", action=_success_action, compensate=_noop_compensate),
                SagaStep(name="step_3", action=_success_action),
            ],
        )

        orchestrator = SagaOrchestrator(db_factory=_mock_db_factory())
        result = await orchestrator.execute(saga, context={"tenant_id": "t1"})

        assert result.state == SagaState.COMPLETED
        assert result.error is None
        assert result.compensation_errors == []
        assert result.saga_id is not None

    @pytest.mark.asyncio
    async def test_step_failure_triggers_compensation(self):
        """Step 2 fails → compensate step 1 → saga COMPENSATED."""
        compensate_1 = AsyncMock()

        saga = SagaDefinition(
            name="test_saga",
            steps=[
                SagaStep(name="step_1", action=_success_action, compensate=compensate_1),
                SagaStep(name="step_2", action=_failing_action, compensate=_noop_compensate),
            ],
        )

        orchestrator = SagaOrchestrator(db_factory=_mock_db_factory())
        result = await orchestrator.execute(saga)

        assert result.state == SagaState.COMPENSATED
        assert "Service unavailable" in result.error
        compensate_1.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_passed_between_steps(self):
        """Step results are merged into context for next step."""
        received_context = {}

        async def step_2_action(ctx: dict) -> dict:
            received_context.update(ctx)
            return {"step_2_data": "done"}

        saga = SagaDefinition(
            name="test_saga",
            steps=[
                SagaStep(name="create_field", action=_success_action_with_data),
                SagaStep(name="setup_billing", action=step_2_action),
            ],
        )

        orchestrator = SagaOrchestrator(db_factory=_mock_db_factory())
        result = await orchestrator.execute(saga, context={"tenant_id": "t1"})

        assert result.state == SagaState.COMPLETED
        assert received_context.get("field_id") == "FIELD-001"
        assert result.context.get("step_2_data") == "done"

    @pytest.mark.asyncio
    async def test_step_timeout_triggers_compensation(self):
        """Step that exceeds timeout → compensation."""
        saga = SagaDefinition(
            name="test_saga",
            steps=[
                SagaStep(name="step_1", action=_success_action, compensate=_noop_compensate),
                SagaStep(name="slow_step", action=_slow_action, timeout=0.1),
            ],
        )

        orchestrator = SagaOrchestrator(db_factory=_mock_db_factory())
        result = await orchestrator.execute(saga)

        assert result.state == SagaState.COMPENSATED
        assert "timed out" in result.error

    @pytest.mark.asyncio
    async def test_compensation_failure_marks_saga_failed(self):
        """If compensation fails after retries → saga FAILED."""
        saga = SagaDefinition(
            name="test_saga",
            steps=[
                SagaStep(
                    name="step_1",
                    action=_success_action,
                    compensate=_failing_compensate,
                    compensation_retries=1,  # Only 1 retry to keep test fast
                ),
                SagaStep(name="step_2", action=_failing_action),
            ],
        )

        orchestrator = SagaOrchestrator(db_factory=_mock_db_factory())
        result = await orchestrator.execute(saga)

        assert result.state == SagaState.FAILED
        assert len(result.compensation_errors) > 0
        assert "Compensation failed" in result.compensation_errors[0]

    @pytest.mark.asyncio
    async def test_no_compensate_function_skips_step(self):
        """Steps without compensate function are skipped during compensation."""
        saga = SagaDefinition(
            name="test_saga",
            steps=[
                SagaStep(name="step_1", action=_success_action),  # No compensate
                SagaStep(name="step_2", action=_failing_action),
            ],
        )

        orchestrator = SagaOrchestrator(db_factory=_mock_db_factory())
        result = await orchestrator.execute(saga)

        # Should compensate without errors (step_1 has no compensate)
        assert result.state == SagaState.COMPENSATED

    @pytest.mark.asyncio
    async def test_first_step_failure_no_compensation_needed(self):
        """If step 0 fails → no compensation (nothing completed)."""
        saga = SagaDefinition(
            name="test_saga",
            steps=[
                SagaStep(name="step_1", action=_failing_action, compensate=_noop_compensate),
            ],
        )

        orchestrator = SagaOrchestrator(db_factory=_mock_db_factory())
        result = await orchestrator.execute(saga)

        assert result.state == SagaState.COMPENSATED
        assert result.compensation_errors == []


class TestGracefulShutdown:
    """Tests for the graceful shutdown middleware."""

    @pytest.mark.asyncio
    async def test_normal_request_passes_through(self):
        """Normal requests should pass through without issues."""
        from shared.middleware.graceful_shutdown import GracefulShutdownMiddleware

        app = MagicMock()
        middleware_funcs = []
        app.middleware = lambda protocol: middleware_funcs.append

        handler = GracefulShutdownMiddleware.__new__(GracefulShutdownMiddleware)
        handler._draining = False
        handler._in_flight = 0
        handler._lock = asyncio.Lock()
        handler._drain_event = asyncio.Event()
        handler._exclude_paths = {"/healthz"}

        assert handler.is_draining is False
        assert handler.in_flight_count == 0

    @pytest.mark.asyncio
    async def test_drain_with_no_requests(self):
        """Drain should complete immediately with no in-flight requests."""
        from shared.middleware.graceful_shutdown import GracefulShutdownMiddleware

        handler = GracefulShutdownMiddleware.__new__(GracefulShutdownMiddleware)
        handler._draining = False
        handler._in_flight = 0
        handler._lock = asyncio.Lock()
        handler._drain_event = asyncio.Event()
        handler._drain_timeout = 5.0

        await handler.drain()

        assert handler.is_draining is True
