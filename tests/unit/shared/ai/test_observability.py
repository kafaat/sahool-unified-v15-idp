"""
Tests for shared/ai/observability.py
اختبارات مراقبة وكلاء الذكاء الاصطناعي

Tests cover:
- AgentErrorType enum
- AgentContext dataclass
- SentryIntegration (without actual Sentry SDK)
- AgentTracer (without actual OpenTelemetry)
- TestResult dataclass
- TestFrameworkIntegration
- GitHubActionsIntegration
- AIAgentObservability unified class
- CIFeedback dataclass
- Factory functions
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import UTC, datetime

from shared.ai.observability import (
    AgentErrorType,
    AgentContext,
    SentryIntegration,
    AgentTracer,
    TestResult,
    TestFrameworkIntegration,
    GitHubActionsIntegration,
    AIAgentObservability,
    CIFeedback,
    create_observability,
    get_sentry_integration,
    get_agent_tracer,
    get_ci_integration,
)


class TestAgentErrorType:
    """Tests for AgentErrorType enum.
    اختبارات أنواع أخطاء الوكيل"""

    def test_all_error_types_exist(self):
        """Test that all error types are defined."""
        assert AgentErrorType.ANALYSIS_FAILED == "analysis_failed"
        assert AgentErrorType.FIX_GENERATION_FAILED == "fix_generation_failed"
        assert AgentErrorType.TOOL_EXECUTION_FAILED == "tool_execution_failed"
        assert AgentErrorType.LLM_CALL_FAILED == "llm_call_failed"
        assert AgentErrorType.VALIDATION_FAILED == "validation_failed"
        assert AgentErrorType.TIMEOUT == "timeout"
        assert AgentErrorType.RATE_LIMITED == "rate_limited"
        assert AgentErrorType.CONFIGURATION_ERROR == "configuration_error"

    def test_error_type_count(self):
        """Test the total number of error types."""
        assert len(AgentErrorType) == 8


class TestAgentContext:
    """Tests for AgentContext dataclass.
    اختبارات سياق الوكيل"""

    def test_create_context_minimal(self):
        """Test creating context with minimal fields."""
        ctx = AgentContext(
            agent_id="test-agent",
            agent_type="code_fix",
            operation="analyze",
        )
        assert ctx.agent_id == "test-agent"
        assert ctx.agent_type == "code_fix"
        assert ctx.operation == "analyze"
        assert ctx.tenant_id == "default"
        assert ctx.user_id is None
        assert ctx.file_path is None
        assert ctx.language is None
        assert ctx.model is None
        assert ctx.extra == {}

    def test_create_context_full(self):
        """Test creating context with all fields."""
        ctx = AgentContext(
            agent_id="agent-1",
            agent_type="code_review",
            operation="review",
            tenant_id="farm_001",
            user_id="user-123",
            file_path="/app/main.py",
            language="python",
            model="codellama:7b",
            extra={"severity": "high"},
        )
        assert ctx.tenant_id == "farm_001"
        assert ctx.user_id == "user-123"
        assert ctx.file_path == "/app/main.py"
        assert ctx.language == "python"
        assert ctx.model == "codellama:7b"
        assert ctx.extra["severity"] == "high"


class TestSentryIntegration:
    """Tests for SentryIntegration class (without actual Sentry SDK).
    اختبارات تكامل Sentry"""

    def test_init_no_dsn(self):
        """Test initialization without DSN does not initialize Sentry."""
        with patch.dict(os.environ, {}, clear=True):
            sentry = SentryIntegration(dsn=None)
            assert sentry.initialized is False

    def test_init_with_dsn_no_sdk(self):
        """Test initialization with DSN but no Sentry SDK installed."""
        with patch("shared.ai.observability.SENTRY_AVAILABLE", False):
            sentry = SentryIntegration(dsn="https://fake@sentry.io/123")
            assert sentry.initialized is False

    def test_set_context_not_initialized(self):
        """Test set_context does nothing when not initialized."""
        sentry = SentryIntegration()
        ctx = AgentContext(agent_id="a", agent_type="b", operation="c")
        # Should not raise
        sentry.set_context(ctx)

    def test_capture_error_not_initialized(self):
        """Test capture_agent_error returns None when not initialized."""
        sentry = SentryIntegration()
        ctx = AgentContext(agent_id="a", agent_type="b", operation="c")
        result = sentry.capture_agent_error(
            error=ValueError("test"),
            context=ctx,
            error_type=AgentErrorType.ANALYSIS_FAILED,
        )
        assert result is None

    def test_capture_warning_not_initialized(self):
        """Test capture_warning returns None when not initialized."""
        sentry = SentryIntegration()
        ctx = AgentContext(agent_id="a", agent_type="b", operation="c")
        result = sentry.capture_warning("test warning", ctx)
        assert result is None

    def test_add_breadcrumb_not_initialized(self):
        """Test add_breadcrumb does nothing when not initialized."""
        sentry = SentryIntegration()
        # Should not raise
        sentry.add_breadcrumb("test", "message", "info")

    def test_before_send_redacts_sensitive(self):
        """Test _before_send removes sensitive data."""
        sentry = SentryIntegration()
        event = {
            "extra": {
                "api_key": "secret123",
                "token": "jwt_token",
                "user_name": "Ahmed",
                "password_hash": "hash",
            }
        }
        result = sentry._before_send(event, {})
        assert result["extra"]["api_key"] == "[REDACTED]"
        assert result["extra"]["token"] == "[REDACTED]"
        assert result["extra"]["password_hash"] == "[REDACTED]"
        assert result["extra"]["user_name"] == "Ahmed"  # Not sensitive

    def test_before_send_fingerprint(self):
        """Test _before_send sets fingerprint when agent_id is in tags."""
        sentry = SentryIntegration()
        event = {
            "tags": {
                "agent_id": "code-fix",
                "agent_type": "fixer",
                "error_type": "analysis_failed",
            },
            "extra": {},
        }
        result = sentry._before_send(event, {})
        assert result["fingerprint"] == ["code-fix", "fixer", "analysis_failed"]

    def test_before_send_transaction_filters_health(self):
        """Test _before_send_transaction filters health endpoints."""
        sentry = SentryIntegration()
        event = {"transaction": "/health"}
        assert sentry._before_send_transaction(event, {}) is None

    def test_before_send_transaction_filters_metrics(self):
        """Test _before_send_transaction filters metrics endpoints."""
        sentry = SentryIntegration()
        event = {"transaction": "/metrics"}
        assert sentry._before_send_transaction(event, {}) is None

    def test_before_send_transaction_passes_normal(self):
        """Test _before_send_transaction passes normal transactions."""
        sentry = SentryIntegration()
        event = {"transaction": "/api/v1/fields"}
        assert sentry._before_send_transaction(event, {}) is event


class TestAgentTracer:
    """Tests for AgentTracer class (without actual OpenTelemetry).
    اختبارات متتبع الوكيل"""

    def test_init_without_otel(self):
        """Test initialization without OpenTelemetry."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")
            assert tracer.enabled is False
            assert tracer.tracer is None

    def test_span_disabled(self):
        """Test span context manager when tracing is disabled."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")
            with tracer.span("test_op") as span:
                assert span is None

    @pytest.mark.asyncio
    async def test_async_span_disabled(self):
        """Test async span context manager when tracing is disabled."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")
            async with tracer.async_span("test_op") as span:
                assert span is None

    def test_trace_agent_operation_disabled(self):
        """Test trace_agent_operation decorator when disabled."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")

            @tracer.trace_agent_operation("agent-1", "analyze")
            def my_func():
                return 42

            assert my_func() == 42

    @pytest.mark.asyncio
    async def test_trace_agent_operation_async_disabled(self):
        """Test trace_agent_operation with async function when disabled."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")

            @tracer.trace_agent_operation("agent-1", "analyze")
            async def my_async_func():
                return 42

            result = await my_async_func()
            assert result == 42

    def test_trace_llm_call_disabled(self):
        """Test trace_llm_call decorator when disabled."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")

            @tracer.trace_llm_call("ollama", "codellama:7b")
            def my_llm_func():
                return "response"

            assert my_llm_func() == "response"

    @pytest.mark.asyncio
    async def test_trace_llm_call_async_disabled(self):
        """Test trace_llm_call with async function when disabled."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")

            @tracer.trace_llm_call("ollama", "codellama:7b")
            async def my_async_llm():
                return "response"

            result = await my_async_llm()
            assert result == "response"

    def test_add_event_disabled(self):
        """Test add_event does nothing when disabled."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")
            tracer.add_event("test_event", {"key": "value"})  # Should not raise

    def test_set_attributes_disabled(self):
        """Test set_attributes does nothing when disabled."""
        with patch("shared.ai.observability.OTEL_AVAILABLE", False):
            tracer = AgentTracer("test-service")
            tracer.set_attributes(key="value")  # Should not raise


class TestTestResult:
    """Tests for TestResult dataclass.
    اختبارات نتائج الاختبار"""

    def test_create_test_result_minimal(self):
        """Test creating a minimal test result."""
        result = TestResult(test_name="test_foo", passed=True, duration_ms=10.5)
        assert result.test_name == "test_foo"
        assert result.passed is True
        assert result.duration_ms == 10.5
        assert result.error_message is None

    def test_create_test_result_failed(self):
        """Test creating a failed test result."""
        result = TestResult(
            test_name="test_bar",
            passed=False,
            duration_ms=500.0,
            error_message="AssertionError: expected 1 got 2",
            file_path="tests/test_foo.py",
            line_number=42,
        )
        assert result.passed is False
        assert result.error_message is not None
        assert result.line_number == 42


class TestTestFrameworkIntegration:
    """Tests for TestFrameworkIntegration.
    اختبارات تكامل أطر الاختبار"""

    def test_init_default(self):
        """Test default initialization."""
        tfi = TestFrameworkIntegration()
        assert tfi._pytest_available is True  # pytest is installed

    def test_init_with_working_dir(self):
        """Test initialization with custom working dir."""
        tfi = TestFrameworkIntegration(working_dir="/tmp")
        assert str(tfi.working_dir) == "/tmp"

    @pytest.mark.asyncio
    async def test_validate_fix_no_tests(self):
        """Test validate_fix returns True when no tests found."""
        tfi = TestFrameworkIntegration(working_dir="/tmp/nonexistent")
        passed, results = await tfi.validate_fix("/tmp/nonexistent/main.py", "python")
        assert passed is True
        assert results == []


class TestCIFeedback:
    """Tests for CIFeedback dataclass.
    اختبارات ملاحظات CI"""

    def test_create_ci_feedback(self):
        """Test creating CI feedback instance."""
        fb = CIFeedback(
            workflow_name="ci.yml",
            job_name="test",
            status="success",
            run_id="12345",
            duration_seconds=120.5,
        )
        assert fb.workflow_name == "ci.yml"
        assert fb.status == "success"
        assert fb.errors == []
        assert fb.warnings == []


class TestGitHubActionsIntegration:
    """Tests for GitHubActionsIntegration.
    اختبارات تكامل GitHub Actions"""

    def test_init_not_in_ci(self):
        """Test initialization outside CI environment."""
        with patch.dict(os.environ, {}, clear=True):
            ci = GitHubActionsIntegration()
            assert ci.is_ci is False
            assert ci.github_actions is False

    def test_init_in_github_actions(self):
        """Test initialization inside GitHub Actions."""
        env = {
            "CI": "true",
            "GITHUB_ACTIONS": "true",
            "GITHUB_RUN_ID": "12345",
            "GITHUB_WORKFLOW": "ci.yml",
            "GITHUB_JOB": "test",
            "GITHUB_REPOSITORY": "kafaat/sahool",
            "GITHUB_SHA": "abc123",
            "GITHUB_REF": "refs/heads/main",
        }
        with patch.dict(os.environ, env, clear=True):
            ci = GitHubActionsIntegration()
            assert ci.is_ci is True
            assert ci.github_actions is True
            assert ci.run_id == "12345"

    def test_output_annotation_not_in_ci(self):
        """Test output_annotation logs when not in CI."""
        with patch.dict(os.environ, {}, clear=True):
            ci = GitHubActionsIntegration()
            # Should not raise, just logs
            ci.output_annotation(
                file_path="main.py",
                line=10,
                message="unused import",
                level="warning",
            )

    def test_set_output_not_in_ci(self):
        """Test set_output does nothing when not in CI."""
        with patch.dict(os.environ, {}, clear=True):
            ci = GitHubActionsIntegration()
            ci.set_output("key", "value")  # Should not raise

    def test_create_summary_not_in_ci(self):
        """Test create_summary logs when not in CI."""
        with patch.dict(os.environ, {}, clear=True):
            ci = GitHubActionsIntegration()
            ci.create_summary("# Test Summary")  # Should not raise

    def test_group_start_not_in_ci(self):
        """Test group_start logs when not in CI."""
        with patch.dict(os.environ, {}, clear=True):
            ci = GitHubActionsIntegration()
            ci.group_start("Test Group")  # Should not raise

    def test_group_end_not_in_ci(self):
        """Test group_end does nothing when not in CI."""
        with patch.dict(os.environ, {}, clear=True):
            ci = GitHubActionsIntegration()
            ci.group_end()  # Should not raise

    def test_create_agent_summary(self):
        """Test creating an agent summary."""
        with patch.dict(os.environ, {}, clear=True):
            ci = GitHubActionsIntegration()
            # Should not raise even outside CI
            ci.create_agent_summary(
                agent_id="code-fix-agent",
                operation="analyze",
                files_analyzed=10,
                issues_found=5,
                fixes_applied=3,
                duration_seconds=45.0,
                errors=["Error 1"],
            )


class TestAIAgentObservability:
    """Tests for unified AIAgentObservability class.
    اختبارات المراقبة الموحدة"""

    def test_init(self):
        """Test initialization of unified observability."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="code_fix",
        )
        assert obs.agent_id == "test-agent"
        assert obs.agent_type == "code_fix"
        assert obs.sentry is not None
        assert obs.tracer is not None
        assert obs.test_runner is not None
        assert obs.ci is not None

    def test_init_without_tracing(self):
        """Test initialization with tracing disabled."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="code_fix",
            enable_tracing=False,
        )
        assert obs.tracer is None

    def test_init_without_metrics(self):
        """Test initialization with metrics disabled."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="code_fix",
            enable_metrics=False,
        )
        assert obs.metrics is None

    @pytest.mark.asyncio
    async def test_operation_context_manager_success(self):
        """Test operation context manager on success."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="test",
            enable_tracing=False,
        )
        async with obs.operation("analyze", file_path="test.py") as ctx:
            assert ctx.agent_id == "test-agent"
            assert ctx.operation == "analyze"
            assert ctx.file_path == "test.py"

    @pytest.mark.asyncio
    async def test_operation_context_manager_error(self):
        """Test operation context manager captures errors."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="test",
            enable_tracing=False,
        )
        with pytest.raises(ValueError, match="test error"):
            async with obs.operation("analyze"):
                raise ValueError("test error")

    def test_add_breadcrumb(self):
        """Test adding a breadcrumb."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="test",
            enable_tracing=False,
        )
        # Should not raise
        obs.add_breadcrumb("test", "message", "info", {"key": "value"})

    def test_record_llm_call_no_metrics(self):
        """Test recording LLM call when metrics disabled."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="test",
            enable_metrics=False,
        )
        # Should not raise
        obs.record_llm_call(
            provider="ollama",
            model="codellama:7b",
            latency_ms=100.0,
            tokens_input=50,
            tokens_output=100,
        )

    def test_get_prometheus_metrics_no_metrics(self):
        """Test getting metrics when metrics disabled."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="test",
            enable_metrics=False,
        )
        assert obs.get_prometheus_metrics() == ""

    def test_create_ci_summary(self):
        """Test creating CI summary."""
        obs = AIAgentObservability(
            agent_id="test-agent",
            agent_type="test",
        )
        # Should not raise
        obs.create_ci_summary(
            operation="analyze",
            files_analyzed=5,
            issues_found=2,
            fixes_applied=1,
            duration_seconds=10.0,
        )


class TestFactoryFunctions:
    """Tests for factory/helper functions.
    اختبارات دوال الإنشاء"""

    def test_create_observability(self):
        """Test create_observability factory."""
        obs = create_observability(agent_id="my-agent", agent_type="reviewer")
        assert isinstance(obs, AIAgentObservability)
        assert obs.agent_id == "my-agent"
        assert obs.agent_type == "reviewer"

    def test_get_sentry_integration(self):
        """Test get_sentry_integration factory."""
        sentry = get_sentry_integration()
        assert isinstance(sentry, SentryIntegration)

    def test_get_agent_tracer(self):
        """Test get_agent_tracer factory."""
        tracer = get_agent_tracer("test-service")
        assert isinstance(tracer, AgentTracer)
        assert tracer.service_name == "test-service"

    def test_get_ci_integration(self):
        """Test get_ci_integration factory."""
        ci = get_ci_integration()
        assert isinstance(ci, GitHubActionsIntegration)
