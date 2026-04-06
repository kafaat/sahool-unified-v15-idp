"""
SAHOOL Saga Orchestrator
=========================
منسق الـ Saga مع حالة مستدامة وتعويض تلقائي

Orchestrated Saga pattern with:
- Persistent state in PostgreSQL (audit trail and failure inspection)
- Per-step timeout with asyncio.wait_for
- Compensation with retry + exponential backoff
- Idempotency keys (no duplicate sagas)
- Structured logging for observability
- Context passing between steps

Error handling:
- If a step fails → compensate all completed steps in reverse
- If compensation fails → retry up to 3 times with backoff
- If compensation still fails → mark saga as FAILED with details
- Failed sagas can be inspected and manually resolved

Usage:
    saga = SagaDefinition(
        name="create_field",
        steps=[
            SagaStep(
                name="create_field",
                action=create_field_fn,
                compensate=delete_field_fn,
                timeout=30.0,
            ),
            SagaStep(
                name="setup_billing",
                action=setup_billing_fn,
                compensate=cancel_billing_fn,
            ),
        ],
    )

    orchestrator = SagaOrchestrator(db_factory=get_session)
    result = await orchestrator.execute(
        saga,
        context={"tenant_id": "t1"},
        idempotency_key="create-field-req-123",
    )
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import SagaExecution, SagaState, SagaStepRecord, StepState

logger = logging.getLogger(__name__)

# Type alias for step functions
# action(context: dict) -> dict (result merged into context)
# compensate(context: dict) -> None
StepAction = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
StepCompensation = Callable[[dict[str, Any]], Awaitable[None]]


@dataclass
class SagaStep:
    """
    Definition of a single saga step.

    Args:
        name: Human-readable step name
        action: Async function to execute (receives context, returns result dict)
        compensate: Async function to undo the action (receives context)
        timeout: Maximum seconds for the action (default 30)
        compensation_retries: Max retries for compensation (default 3)
    """

    name: str
    action: StepAction
    compensate: StepCompensation | None = None
    timeout: float = 30.0
    compensation_retries: int = 3


@dataclass
class SagaDefinition:
    """
    Definition of a saga with ordered steps.

    Args:
        name: Saga name (e.g., "create_field", "process_payment")
        steps: Ordered list of saga steps
    """

    name: str
    steps: list[SagaStep]


@dataclass
class SagaResult:
    """Result of a saga execution."""

    saga_id: str
    state: SagaState
    context: dict[str, Any]
    error: str | None = None
    compensation_errors: list[str] = field(default_factory=list)


class SagaOrchestrator:
    """
    Saga orchestrator with persistent state.

    Executes saga steps sequentially, persisting state after
    each step. If a step fails, compensates all completed steps
    in reverse order with retry and backoff.

    Args:
        db_factory: Callable that returns a SQLAlchemy Session
    """

    def __init__(self, db_factory: Callable[[], Session]):
        self._db_factory = db_factory

    async def execute(
        self,
        saga: SagaDefinition,
        context: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        tenant_id: str | None = None,
    ) -> SagaResult:
        """
        Execute a saga.

        Args:
            saga: Saga definition with steps
            context: Initial context data passed to steps
            idempotency_key: Unique key to prevent duplicate execution
            tenant_id: Tenant identifier for multi-tenancy

        Returns:
            SagaResult with final state and context

        Raises:
            ValueError: If saga with same idempotency_key already completed
        """
        ctx = dict(context or {})
        idem_key = idempotency_key or str(uuid4())

        db = self._db_factory()
        try:
            # Check idempotency
            existing = self._find_existing(db, idem_key)
            if existing:
                if existing.state == SagaState.COMPLETED:
                    logger.info(
                        "saga_already_completed",
                        extra={"saga_id": existing.id, "key": idem_key},
                    )
                    return SagaResult(
                        saga_id=existing.id,
                        state=SagaState.COMPLETED,
                        context=json.loads(existing.context_json),
                    )
                if existing.state in (SagaState.RUNNING, SagaState.COMPENSATING):
                    raise ValueError(f"Saga {idem_key} is already in progress (state={existing.state})")
                # Terminal states (FAILED, COMPENSATED) — return existing result
                # to avoid unique constraint violation on idempotency_key
                return SagaResult(
                    saga_id=existing.id,
                    state=SagaState(existing.state),
                    context=json.loads(existing.context_json),
                    error=existing.error_message,
                )

            # Create saga execution record
            saga_id = str(uuid4())
            execution = SagaExecution(
                id=saga_id,
                saga_name=saga.name,
                idempotency_key=idem_key,
                state=SagaState.RUNNING,
                context_json=json.dumps(ctx, default=str),
                current_step=0,
                total_steps=len(saga.steps),
                tenant_id=tenant_id,
            )
            db.add(execution)

            # Create step records
            step_records = []
            for i, step in enumerate(saga.steps):
                record = SagaStepRecord(
                    id=str(uuid4()),
                    saga_id=execution.id,
                    step_index=i,
                    step_name=step.name,
                    state=StepState.PENDING,
                )
                db.add(record)
                step_records.append(record)

            try:
                db.commit()
            except Exception:
                db.rollback()
                # Race condition: another process created the saga first
                # Reload and return the existing saga
                existing = self._find_existing(db, idem_key)
                if existing:
                    return SagaResult(
                        saga_id=existing.id,
                        state=SagaState(existing.state),
                        context=json.loads(existing.context_json),
                        error=existing.error_message,
                    )
                raise

            logger.info(
                "saga_started",
                extra={
                    "saga_id": execution.id,
                    "saga_name": saga.name,
                    "steps": len(saga.steps),
                    "tenant_id": tenant_id,
                },
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        # Execute steps
        completed_steps: list[tuple[SagaStep, SagaStepRecord]] = []
        failed_step_index = -1
        failure_error = None

        for i, step in enumerate(saga.steps):
            record = step_records[i]

            db = self._db_factory()
            try:
                # Mark step as running
                record.state = StepState.RUNNING
                record.started_at = datetime.now(UTC)
                execution.current_step = i
                db.merge(record)
                db.merge(execution)
                db.commit()
            finally:
                db.close()

            # Execute the step action with timeout
            try:
                result = await asyncio.wait_for(
                    step.action(ctx),
                    timeout=step.timeout,
                )

                # Merge result into context
                if isinstance(result, dict):
                    ctx.update(result)

                # Mark step completed
                db = self._db_factory()
                try:
                    record.state = StepState.COMPLETED
                    record.completed_at = datetime.now(UTC)
                    record.result_json = json.dumps(result, default=str) if result else None
                    execution.context_json = json.dumps(ctx, default=str)
                    db.merge(record)
                    db.merge(execution)
                    db.commit()
                finally:
                    db.close()

                completed_steps.append((step, record))

                logger.info(
                    "saga_step_completed",
                    extra={
                        "saga_id": execution.id,
                        "step": step.name,
                        "step_index": i,
                    },
                )

            except TimeoutError:
                failure_error = f"Step '{step.name}' timed out after {step.timeout}s"
                failed_step_index = i
                break
            except Exception as e:
                failure_error = f"Step '{step.name}' failed: {e}"
                failed_step_index = i
                break

        # Handle failure — compensate
        if failure_error:
            logger.warning(
                "saga_step_failed",
                extra={
                    "saga_id": execution.id,
                    "step": saga.steps[failed_step_index].name,
                    "error": failure_error,
                },
            )

            # Update failed step
            db = self._db_factory()
            try:
                record = step_records[failed_step_index]
                record.state = StepState.FAILED
                record.error_message = failure_error[:1000]
                record.completed_at = datetime.now(UTC)
                execution.state = SagaState.COMPENSATING
                execution.error_message = failure_error[:1000]
                db.merge(record)
                db.merge(execution)
                db.commit()
            finally:
                db.close()

            # Compensate completed steps in reverse
            compensation_errors = await self._compensate(execution, completed_steps, ctx)

            # Final state
            final_state = SagaState.COMPENSATED if not compensation_errors else SagaState.FAILED

            db = self._db_factory()
            try:
                execution.state = final_state
                execution.completed_at = datetime.now(UTC)
                db.merge(execution)
                db.commit()
            finally:
                db.close()

            logger.info(
                "saga_compensation_complete",
                extra={
                    "saga_id": execution.id,
                    "final_state": final_state.value,
                    "compensation_errors": len(compensation_errors),
                },
            )

            return SagaResult(
                saga_id=execution.id,
                state=final_state,
                context=ctx,
                error=failure_error,
                compensation_errors=compensation_errors,
            )

        # Success
        db = self._db_factory()
        try:
            execution.state = SagaState.COMPLETED
            execution.completed_at = datetime.now(UTC)
            execution.context_json = json.dumps(ctx, default=str)
            db.merge(execution)
            db.commit()
        finally:
            db.close()

        logger.info(
            "saga_completed",
            extra={"saga_id": execution.id, "saga_name": saga.name},
        )

        return SagaResult(
            saga_id=execution.id,
            state=SagaState.COMPLETED,
            context=ctx,
        )

    async def _compensate(
        self,
        execution: SagaExecution,
        completed_steps: list[tuple[SagaStep, SagaStepRecord]],
        ctx: dict[str, Any],
    ) -> list[str]:
        """
        Compensate completed steps in reverse order.

        Each compensation is retried up to step.compensation_retries
        times with exponential backoff.

        Returns list of compensation error messages (empty = all succeeded).
        """
        errors: list[str] = []

        for step, record in reversed(completed_steps):
            if step.compensate is None:
                continue

            db = self._db_factory()
            try:
                record.state = StepState.COMPENSATING
                db.merge(record)
                db.commit()
            finally:
                db.close()

            compensated = False
            last_error = ""
            retries = max(1, step.compensation_retries)

            for attempt in range(1, retries + 1):
                try:
                    await asyncio.wait_for(
                        step.compensate(ctx),
                        timeout=step.timeout,
                    )
                    compensated = True
                    break
                except Exception as e:
                    last_error = f"Compensation '{step.name}' attempt {attempt}/{retries}: {e}"
                    logger.warning(
                        "saga_compensation_retry",
                        extra={
                            "saga_id": execution.id,
                            "step": step.name,
                            "attempt": attempt,
                            "error": str(e),
                        },
                    )
                    if attempt < retries:
                        # Exponential backoff: 1s, 2s, 4s
                        await asyncio.sleep(min(2 ** (attempt - 1), 8))

            db = self._db_factory()
            try:
                if compensated:
                    record.state = StepState.COMPENSATED
                    record.completed_at = datetime.now(UTC)
                else:
                    record.state = StepState.FAILED
                    record.compensation_error = last_error[:1000]
                    errors.append(last_error)
                db.merge(record)
                db.commit()
            finally:
                db.close()

        return errors

    def _find_existing(self, db: Session, idempotency_key: str) -> SagaExecution | None:
        """Find existing saga by idempotency key."""
        stmt = select(SagaExecution).where(SagaExecution.idempotency_key == idempotency_key)
        return db.execute(stmt).scalar_one_or_none()

    def get_saga_status(self, saga_id: str) -> SagaExecution | None:
        """Get saga execution status by ID."""
        db = self._db_factory()
        try:
            stmt = select(SagaExecution).where(SagaExecution.id == saga_id)
            return db.execute(stmt).scalar_one_or_none()
        finally:
            db.close()

    def get_failed_sagas(self, limit: int = 50, tenant_id: str | None = None) -> list[SagaExecution]:
        """Get failed sagas for manual inspection."""
        db = self._db_factory()
        try:
            stmt = (
                select(SagaExecution)
                .where(SagaExecution.state == SagaState.FAILED)
                .order_by(SagaExecution.started_at.desc())
                .limit(limit)
            )
            if tenant_id:
                stmt = stmt.where(SagaExecution.tenant_id == tenant_id)
            return list(db.execute(stmt).scalars())
        finally:
            db.close()
