"""
AI Agent Observability Integration
===================================
تكامل المراقبة لوكلاء الذكاء الاصطناعي

Provides unified observability for AI agents including:
- Sentry error tracking with AI context
- OpenTelemetry distributed tracing
- Prometheus metrics collection
- Test framework integration
- CI/CD pipeline feedback

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import json
import logging
import os
import time
from collections.abc import Callable
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from functools import wraps
from pathlib import Path
from typing import Any

from .metrics import get_metrics_collector

logger = logging.getLogger(__name__)


# ============================================================================
# SENTRY INTEGRATION
# ============================================================================

try:
    import sentry_sdk
    from sentry_sdk import capture_exception, capture_message, set_tag, set_user

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None


class AgentErrorType(StrEnum):
    """Types of agent errors for categorization."""

    ANALYSIS_FAILED = "analysis_failed"
    FIX_GENERATION_FAILED = "fix_generation_failed"
    TOOL_EXECUTION_FAILED = "tool_execution_failed"
    LLM_CALL_FAILED = "llm_call_failed"
    VALIDATION_FAILED = "validation_failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    CONFIGURATION_ERROR = "configuration_error"


@dataclass
class AgentContext:
    """Context for AI agent operations."""

    agent_id: str
    agent_type: str
    operation: str
    tenant_id: str = "default"
    user_id: str | None = None
    file_path: str | None = None
    language: str | None = None
    model: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class SentryIntegration:
    """
    Sentry integration for AI agents.

    تكامل Sentry لوكلاء الذكاء الاصطناعي

    Provides error tracking with AI-specific context including:
    - Agent metadata and state
    - LLM call information
    - Code analysis context
    - Performance metrics
    """

    def __init__(
        self,
        dsn: str | None = None,
        environment: str | None = None,
        sample_rate: float = 1.0,
        traces_sample_rate: float = 0.1,
    ):
        """
        Initialize Sentry integration.

        Args:
            dsn: Sentry DSN (from env SENTRY_DSN if not provided)
            environment: Environment name (from env ENVIRONMENT if not provided)
            sample_rate: Error sampling rate (0.0 to 1.0)
            traces_sample_rate: Performance tracing sample rate
        """
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.sample_rate = sample_rate
        self.traces_sample_rate = traces_sample_rate
        self.initialized = False

        if self.dsn and SENTRY_AVAILABLE:
            self._initialize()

    def _initialize(self) -> None:
        """Initialize Sentry SDK."""
        if not SENTRY_AVAILABLE:
            logger.warning("Sentry SDK not installed. Error tracking disabled.")
            return

        try:
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                sample_rate=self.sample_rate,
                traces_sample_rate=self.traces_sample_rate,
                # AI-specific configuration
                attach_stacktrace=True,
                send_default_pii=False,
                max_breadcrumbs=50,
                before_send=self._before_send,
                before_send_transaction=self._before_send_transaction,
            )
            self.initialized = True
            logger.info(f"Sentry initialized for environment: {self.environment}")
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")

    def _before_send(self, event: dict, hint: dict) -> dict | None:
        """
        Filter and enrich events before sending to Sentry.

        تصفية وإثراء الأحداث قبل إرسالها إلى Sentry
        """
        # Remove sensitive data
        if "extra" in event:
            sensitive_keys = ["api_key", "token", "password", "secret", "jwt"]
            for key in list(event["extra"].keys()):
                if any(s in key.lower() for s in sensitive_keys):
                    event["extra"][key] = "[REDACTED]"

        # Add AI context fingerprint
        if "tags" in event and event["tags"].get("agent_id"):
            event["fingerprint"] = [
                event["tags"].get("agent_id"),
                event["tags"].get("agent_type", "unknown"),
                event["tags"].get("error_type", "unknown"),
            ]

        return event

    def _before_send_transaction(self, event: dict, hint: dict) -> dict | None:
        """Filter transactions for performance monitoring."""
        # Skip health checks and metrics endpoints
        transaction = event.get("transaction", "")
        if any(path in transaction for path in ["/health", "/metrics", "/ready"]):
            return None
        return event

    def set_context(self, context: AgentContext) -> None:
        """
        Set agent context for error tracking.

        تعيين سياق الوكيل لتتبع الأخطاء
        """
        if not self.initialized:
            return

        # Set tags
        set_tag("agent_id", context.agent_id)
        set_tag("agent_type", context.agent_type)
        set_tag("operation", context.operation)
        set_tag("tenant_id", context.tenant_id)

        if context.language:
            set_tag("language", context.language)
        if context.model:
            set_tag("model", context.model)

        # Set user context
        if context.user_id:
            set_user({"id": context.user_id, "tenant_id": context.tenant_id})

        # Set additional context
        sentry_sdk.set_context(
            "ai_agent",
            {
                "agent_id": context.agent_id,
                "agent_type": context.agent_type,
                "operation": context.operation,
                "file_path": context.file_path,
                "language": context.language,
                "model": context.model,
                **context.extra,
            },
        )

    def capture_agent_error(
        self,
        error: Exception,
        context: AgentContext,
        error_type: AgentErrorType = AgentErrorType.ANALYSIS_FAILED,
        additional_data: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Capture an AI agent error with context.

        التقاط خطأ وكيل الذكاء الاصطناعي مع السياق

        Returns:
            Sentry event ID or None if not sent
        """
        if not self.initialized:
            logger.warning(f"Sentry not initialized. Error not captured: {error}")
            return None

        # Set context
        self.set_context(context)
        set_tag("error_type", error_type.value)

        # Add breadcrumb for debugging
        sentry_sdk.add_breadcrumb(
            category="ai.agent",
            message=f"Agent {context.agent_id} failed during {context.operation}",
            level="error",
            data={
                "error_type": error_type.value,
                **(additional_data or {}),
            },
        )

        # Capture exception
        event_id = capture_exception(error)
        logger.info(f"Error captured in Sentry: {event_id}")
        return event_id

    def capture_warning(
        self,
        message: str,
        context: AgentContext,
        additional_data: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Capture a warning message.

        التقاط رسالة تحذير
        """
        if not self.initialized:
            return None

        self.set_context(context)
        event_id = capture_message(
            message,
            level="warning",
            extras=additional_data,
        )
        return event_id

    def add_breadcrumb(
        self,
        category: str,
        message: str,
        level: str = "info",
        data: dict[str, Any] | None = None,
    ) -> None:
        """Add a breadcrumb for debugging context."""
        if not self.initialized:
            return

        sentry_sdk.add_breadcrumb(
            category=category,
            message=message,
            level=level,
            data=data or {},
        )


# ============================================================================
# OPENTELEMETRY INTEGRATION
# ============================================================================

try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind, Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None


class AgentTracer:
    """
    OpenTelemetry tracer for AI agents.

    متتبع OpenTelemetry لوكلاء الذكاء الاصطناعي

    Provides distributed tracing for:
    - Agent operations
    - LLM calls
    - Tool executions
    - Code analysis
    """

    def __init__(self, service_name: str = "ai-agents"):
        """Initialize agent tracer."""
        self.service_name = service_name
        self.enabled = OTEL_AVAILABLE

        if self.enabled:
            try:
                self.tracer = trace.get_tracer(
                    service_name,
                    schema_url="https://opentelemetry.io/schemas/1.21.0",
                )
            except Exception as e:
                logger.warning(f"Failed to get OpenTelemetry tracer: {e}")
                self.enabled = False
                self.tracer = None
        else:
            self.tracer = None
            logger.info("OpenTelemetry not available. Tracing disabled.")

    @contextmanager
    def span(
        self,
        name: str,
        kind: str = "internal",
        attributes: dict[str, Any] | None = None,
    ):
        """
        Create a traced span for an operation.

        إنشاء نطاق متتبع لعملية

        Usage:
            with tracer.span("analyze_code", attributes={"file": path}):
                # Analysis code here
                pass
        """
        if not self.enabled or not self.tracer:
            yield None
            return

        span_kind = {
            "internal": SpanKind.INTERNAL,
            "client": SpanKind.CLIENT,
            "server": SpanKind.SERVER,
            "producer": SpanKind.PRODUCER,
            "consumer": SpanKind.CONSUMER,
        }.get(kind, SpanKind.INTERNAL)

        with self.tracer.start_as_current_span(
            name,
            kind=span_kind,
            attributes=attributes or {},
        ) as span:
            try:
                yield span
            except Exception as e:
                if span:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                raise

    @asynccontextmanager
    async def async_span(
        self,
        name: str,
        kind: str = "internal",
        attributes: dict[str, Any] | None = None,
    ):
        """Async version of span context manager."""
        if not self.enabled or not self.tracer:
            yield None
            return

        span_kind = {
            "internal": SpanKind.INTERNAL,
            "client": SpanKind.CLIENT,
            "server": SpanKind.SERVER,
            "producer": SpanKind.PRODUCER,
            "consumer": SpanKind.CONSUMER,
        }.get(kind, SpanKind.INTERNAL)

        with self.tracer.start_as_current_span(
            name,
            kind=span_kind,
            attributes=attributes or {},
        ) as span:
            try:
                yield span
            except Exception as e:
                if span:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                raise

    def trace_agent_operation(
        self,
        agent_id: str,
        operation: str,
    ) -> Callable:
        """
        Decorator to trace agent operations.

        مزخرف لتتبع عمليات الوكيل

        Usage:
            @tracer.trace_agent_operation("code-fix-agent", "analyze")
            async def analyze_file(path: str):
                # Analysis code
                pass
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.enabled or not self.tracer:
                    return await func(*args, **kwargs)

                with self.tracer.start_as_current_span(
                    f"agent.{agent_id}.{operation}",
                    kind=SpanKind.INTERNAL,
                    attributes={
                        "agent.id": agent_id,
                        "agent.operation": operation,
                    },
                ) as span:
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
                    finally:
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("duration_ms", duration_ms)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self.enabled or not self.tracer:
                    return func(*args, **kwargs)

                with self.tracer.start_as_current_span(
                    f"agent.{agent_id}.{operation}",
                    kind=SpanKind.INTERNAL,
                    attributes={
                        "agent.id": agent_id,
                        "agent.operation": operation,
                    },
                ) as span:
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
                    finally:
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("duration_ms", duration_ms)

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    def trace_llm_call(
        self,
        provider: str,
        model: str,
    ) -> Callable:
        """
        Decorator to trace LLM API calls.

        مزخرف لتتبع استدعاءات LLM API

        Usage:
            @tracer.trace_llm_call("ollama", "codellama:7b")
            async def generate_fix(prompt: str):
                # LLM call
                pass
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.enabled or not self.tracer:
                    return await func(*args, **kwargs)

                with self.tracer.start_as_current_span(
                    f"llm.{provider}.{model}",
                    kind=SpanKind.CLIENT,
                    attributes={
                        "llm.provider": provider,
                        "llm.model": model,
                        "llm.request.type": "completion",
                    },
                ) as span:
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))

                        # Record token usage if available
                        if hasattr(result, "tokens_used"):
                            span.set_attribute("llm.tokens.total", result.tokens_used)
                        if hasattr(result, "prompt_tokens"):
                            span.set_attribute("llm.tokens.prompt", result.prompt_tokens)
                        if hasattr(result, "completion_tokens"):
                            span.set_attribute("llm.tokens.completion", result.completion_tokens)

                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
                    finally:
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("llm.latency_ms", duration_ms)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self.enabled or not self.tracer:
                    return func(*args, **kwargs)

                with self.tracer.start_as_current_span(
                    f"llm.{provider}.{model}",
                    kind=SpanKind.CLIENT,
                    attributes={
                        "llm.provider": provider,
                        "llm.model": model,
                    },
                ) as span:
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
                    finally:
                        duration_ms = (time.time() - start_time) * 1000
                        span.set_attribute("llm.latency_ms", duration_ms)

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    def add_event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Add an event to the current span."""
        if not self.enabled or not OTEL_AVAILABLE:
            return

        span = trace.get_current_span()
        if span and span.is_recording():
            span.add_event(name, attributes=attributes or {})

    def set_attributes(self, **attributes: Any) -> None:
        """Set attributes on the current span."""
        if not self.enabled or not OTEL_AVAILABLE:
            return

        span = trace.get_current_span()
        if span and span.is_recording():
            for key, value in attributes.items():
                if isinstance(value, str | int | float | bool):
                    span.set_attribute(key, value)
                else:
                    span.set_attribute(key, str(value))


# ============================================================================
# TEST FRAMEWORK INTEGRATION
# ============================================================================


@dataclass
class TestResult:
    """Result from test execution."""

    test_name: str
    passed: bool
    duration_ms: float
    error_message: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    output: str | None = None


class TestFrameworkIntegration:
    """
    Integration with test frameworks for validation.

    تكامل أطر الاختبار للتحقق

    Supports:
    - pytest (Python)
    - Vitest (TypeScript/JavaScript)
    - Playwright (E2E)
    - k6 (Load testing)
    """

    def __init__(self, working_dir: str | None = None):
        """Initialize test framework integration."""
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self._pytest_available = self._check_pytest()
        self._vitest_available = self._check_vitest()

    def _check_pytest(self) -> bool:
        """Check if pytest is available."""
        try:
            import pytest

            return True
        except ImportError:
            return False

    def _check_vitest(self) -> bool:
        """Check if Vitest is configured."""
        vitest_config = self.working_dir / "vitest.config.ts"
        return vitest_config.exists()

    async def run_pytest(
        self,
        test_path: str | None = None,
        markers: list[str] | None = None,
        verbose: bool = False,
        collect_only: bool = False,
    ) -> list[TestResult]:
        """
        Run pytest and collect results.

        تشغيل pytest وجمع النتائج

        Args:
            test_path: Specific test file or directory
            markers: Pytest markers to filter tests
            verbose: Enable verbose output
            collect_only: Only collect tests without running

        Returns:
            List of test results
        """
        if not self._pytest_available:
            logger.warning("pytest not available")
            return []

        cmd = ["python", "-m", "pytest", "--json-report", "--json-report-file=-"]

        if test_path:
            cmd.append(test_path)
        if markers:
            cmd.extend(["-m", " or ".join(markers)])
        if verbose:
            cmd.append("-v")
        if collect_only:
            cmd.append("--collect-only")

        results: list[TestResult] = []

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.working_dir),
            )

            stdout, stderr = await proc.communicate()

            if stdout:
                try:
                    report = json.loads(stdout.decode())
                    for test in report.get("tests", []):
                        results.append(
                            TestResult(
                                test_name=test.get("nodeid", "unknown"),
                                passed=test.get("outcome") == "passed",
                                duration_ms=test.get("duration", 0) * 1000,
                                error_message=test.get("call", {}).get("longrepr"),
                                file_path=test.get("location", [None])[0],
                                line_number=test.get("location", [None, None])[1],
                            )
                        )
                except json.JSONDecodeError:
                    logger.warning("Failed to parse pytest JSON output")

        except Exception as e:
            logger.error(f"Failed to run pytest: {e}")

        return results

    async def run_vitest(
        self,
        test_path: str | None = None,
        run_all: bool = False,
    ) -> list[TestResult]:
        """
        Run Vitest and collect results.

        تشغيل Vitest وجمع النتائج
        """
        if not self._vitest_available:
            logger.warning("Vitest not configured")
            return []

        cmd = ["npx", "vitest", "run", "--reporter=json"]

        if test_path:
            cmd.append(test_path)
        if run_all:
            cmd.append("--all")

        results: list[TestResult] = []

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.working_dir),
            )

            stdout, stderr = await proc.communicate()

            if stdout:
                try:
                    report = json.loads(stdout.decode())
                    for file_result in report.get("testResults", []):
                        for test in file_result.get("assertionResults", []):
                            results.append(
                                TestResult(
                                    test_name=test.get("fullName", "unknown"),
                                    passed=test.get("status") == "passed",
                                    duration_ms=test.get("duration", 0),
                                    error_message="\n".join(test.get("failureMessages", [])),
                                    file_path=file_result.get("name"),
                                )
                            )
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Vitest JSON output")

        except Exception as e:
            logger.error(f"Failed to run Vitest: {e}")

        return results

    async def validate_fix(
        self,
        file_path: str,
        language: str = "python",
    ) -> tuple[bool, list[TestResult]]:
        """
        Validate a fix by running relevant tests.

        التحقق من الإصلاح عن طريق تشغيل الاختبارات ذات الصلة

        Args:
            file_path: Path to the fixed file
            language: Programming language

        Returns:
            Tuple of (all_passed, test_results)
        """
        results: list[TestResult] = []

        if language == "python":
            # Find related test files
            file_name = Path(file_path).stem
            test_patterns = [
                f"**/test_{file_name}.py",
                f"**/{file_name}_test.py",
                f"**/tests/test_{file_name}.py",
            ]

            for pattern in test_patterns:
                test_files = list(self.working_dir.glob(pattern))
                for test_file in test_files:
                    test_results = await self.run_pytest(str(test_file))
                    results.extend(test_results)

        elif language in ("typescript", "javascript"):
            file_name = Path(file_path).stem
            test_patterns = [
                f"**/{file_name}.test.ts",
                f"**/{file_name}.test.tsx",
                f"**/{file_name}.spec.ts",
                f"**/__tests__/{file_name}.ts",
            ]

            for pattern in test_patterns:
                test_files = list(self.working_dir.glob(pattern))
                for test_file in test_files:
                    test_results = await self.run_vitest(str(test_file))
                    results.extend(test_results)

        all_passed = all(r.passed for r in results) if results else True
        return all_passed, results


# ============================================================================
# CI/CD INTEGRATION
# ============================================================================


@dataclass
class CIFeedback:
    """Feedback from CI/CD pipeline."""

    workflow_name: str
    job_name: str
    status: str  # success, failure, cancelled
    run_id: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    annotations: list[dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0
    url: str | None = None


class GitHubActionsIntegration:
    """
    Integration with GitHub Actions for CI feedback.

    تكامل GitHub Actions لملاحظات CI
    """

    def __init__(self):
        """Initialize GitHub Actions integration."""
        self.is_ci = os.getenv("CI", "").lower() == "true"
        self.github_actions = os.getenv("GITHUB_ACTIONS", "").lower() == "true"
        self.run_id = os.getenv("GITHUB_RUN_ID", "")
        self.workflow = os.getenv("GITHUB_WORKFLOW", "")
        self.job = os.getenv("GITHUB_JOB", "")
        self.repository = os.getenv("GITHUB_REPOSITORY", "")
        self.sha = os.getenv("GITHUB_SHA", "")
        self.ref = os.getenv("GITHUB_REF", "")

    def output_annotation(
        self,
        file_path: str,
        line: int,
        message: str,
        level: str = "warning",  # notice, warning, error
        title: str | None = None,
        end_line: int | None = None,
        col: int | None = None,
        end_col: int | None = None,
    ) -> None:
        """
        Output a GitHub Actions annotation.

        إخراج تعليق توضيحي في GitHub Actions

        This will create an annotation that appears on the PR diff.
        """
        if not self.github_actions:
            # Log locally if not in GitHub Actions
            logger.log(
                getattr(logging, level.upper(), logging.WARNING),
                f"{file_path}:{line}: {message}",
            )
            return

        # Build annotation command
        props = [f"file={file_path}", f"line={line}"]

        if title:
            props.append(f"title={title}")
        if end_line:
            props.append(f"endLine={end_line}")
        if col:
            props.append(f"col={col}")
        if end_col:
            props.append(f"endColumn={end_col}")

        props_str = ",".join(props)
        print(f"::{level} {props_str}::{message}")

    def set_output(self, name: str, value: str) -> None:
        """Set a GitHub Actions output."""
        if not self.github_actions:
            return

        output_file = os.getenv("GITHUB_OUTPUT", "")
        if output_file:
            with open(output_file, "a") as f:
                f.write(f"{name}={value}\n")
        else:
            print(f"::set-output name={name}::{value}")

    def create_summary(self, content: str) -> None:
        """
        Add content to the job summary.

        إضافة محتوى إلى ملخص الوظيفة
        """
        if not self.github_actions:
            logger.info(f"Summary:\n{content}")
            return

        summary_file = os.getenv("GITHUB_STEP_SUMMARY", "")
        if summary_file:
            with open(summary_file, "a") as f:
                f.write(content + "\n")

    def group_start(self, name: str) -> None:
        """Start a log group."""
        if self.github_actions:
            print(f"::group::{name}")
        else:
            logger.info(f"=== {name} ===")

    def group_end(self) -> None:
        """End a log group."""
        if self.github_actions:
            print("::endgroup::")

    def create_agent_summary(
        self,
        agent_id: str,
        operation: str,
        files_analyzed: int,
        issues_found: int,
        fixes_applied: int,
        duration_seconds: float,
        errors: list[str] | None = None,
    ) -> None:
        """
        Create a summary for agent operations.

        إنشاء ملخص لعمليات الوكيل
        """
        summary = f"""
## 🤖 AI Agent Report: {agent_id}

### Operation: {operation}

| Metric | Value |
|--------|-------|
| Files Analyzed | {files_analyzed} |
| Issues Found | {issues_found} |
| Fixes Applied | {fixes_applied} |
| Duration | {duration_seconds:.2f}s |

"""

        if errors:
            summary += "### ❌ Errors\n\n"
            for error in errors:
                summary += f"- {error}\n"

        self.create_summary(summary)


# ============================================================================
# UNIFIED OBSERVABILITY
# ============================================================================


class AIAgentObservability:
    """
    Unified observability for AI agents.

    مراقبة موحدة لوكلاء الذكاء الاصطناعي

    Combines:
    - Sentry error tracking
    - OpenTelemetry tracing
    - Prometheus metrics
    - Test framework integration
    - CI/CD feedback

    Example:
        obs = AIAgentObservability(
            agent_id="code-fix-agent",
            agent_type="code_fix",
        )

        async with obs.operation("analyze_file", file_path=path):
            # Analysis code
            obs.add_metric("issues_found", 5)
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        sentry_dsn: str | None = None,
        enable_tracing: bool = True,
        enable_metrics: bool = True,
    ):
        """
        Initialize unified observability.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (code_fix, code_review, etc.)
            sentry_dsn: Sentry DSN (from env if not provided)
            enable_tracing: Enable OpenTelemetry tracing
            enable_metrics: Enable Prometheus metrics
        """
        self.agent_id = agent_id
        self.agent_type = agent_type

        # Initialize components
        self.sentry = SentryIntegration(dsn=sentry_dsn)
        self.tracer = AgentTracer(f"ai-agent-{agent_id}") if enable_tracing else None
        self.metrics = get_metrics_collector() if enable_metrics else None
        self.test_runner = TestFrameworkIntegration()
        self.ci = GitHubActionsIntegration()

        # Operation tracking
        self._operation_start: float | None = None
        self._current_context: AgentContext | None = None

    @asynccontextmanager
    async def operation(
        self,
        name: str,
        file_path: str | None = None,
        language: str | None = None,
        model: str | None = None,
        tenant_id: str = "default",
        user_id: str | None = None,
        **extra_context,
    ):
        """
        Context manager for traced operations.

        مدير السياق للعمليات المتتبعة

        Usage:
            async with obs.operation("analyze", file_path=path):
                # Your code here
                pass
        """
        # Create context
        context = AgentContext(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            operation=name,
            tenant_id=tenant_id,
            user_id=user_id,
            file_path=file_path,
            language=language,
            model=model,
            extra=extra_context,
        )
        self._current_context = context

        # Set Sentry context
        self.sentry.set_context(context)

        # Start timing
        start_time = time.time()
        success = True
        error: Exception | None = None

        # Start trace span
        span_context = None
        if self.tracer:
            span_context = self.tracer.async_span(
                f"agent.{self.agent_id}.{name}",
                attributes={
                    "agent.id": self.agent_id,
                    "agent.type": self.agent_type,
                    "agent.operation": name,
                    "file.path": file_path or "",
                    "code.language": language or "",
                    "llm.model": model or "",
                },
            )

        try:
            if span_context:
                async with span_context:
                    yield context
            else:
                yield context

        except Exception as e:
            success = False
            error = e

            # Capture in Sentry
            self.sentry.capture_agent_error(
                error=e,
                context=context,
                error_type=AgentErrorType.ANALYSIS_FAILED,
            )

            # Output CI annotation
            if file_path:
                self.ci.output_annotation(
                    file_path=file_path,
                    line=1,
                    message=str(e),
                    level="error",
                    title=f"Agent Error: {name}",
                )

            raise

        finally:
            duration_ms = (time.time() - start_time) * 1000

            # Record metrics
            if self.metrics:
                self.metrics.record_agent_invocation(
                    agent_id=self.agent_id,
                    latency_ms=duration_ms,
                    success=success,
                    tenant_id=tenant_id,
                )

                if not success and error:
                    self.metrics.record_agent_error(
                        agent_id=self.agent_id,
                        error_type=type(error).__name__,
                        tenant_id=tenant_id,
                    )

    def add_breadcrumb(
        self,
        category: str,
        message: str,
        level: str = "info",
        data: dict[str, Any] | None = None,
    ) -> None:
        """Add a debugging breadcrumb."""
        self.sentry.add_breadcrumb(category, message, level, data)

        if self.tracer:
            self.tracer.add_event(
                f"breadcrumb.{category}",
                attributes={"message": message, **(data or {})},
            )

    def record_llm_call(
        self,
        provider: str,
        model: str,
        latency_ms: float,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_usd: float = 0.0,
        success: bool = True,
    ) -> None:
        """Record an LLM API call for metrics."""
        if self.metrics:
            self.metrics.record_llm_call(
                provider=provider,
                model=model,
                latency_ms=latency_ms,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost_usd=cost_usd,
                success=success,
            )

    async def validate_fix(
        self,
        file_path: str,
        language: str = "python",
    ) -> tuple[bool, list[TestResult]]:
        """Run tests to validate a fix."""
        return await self.test_runner.validate_fix(file_path, language)

    def create_ci_summary(
        self,
        operation: str,
        files_analyzed: int,
        issues_found: int,
        fixes_applied: int,
        duration_seconds: float,
        errors: list[str] | None = None,
    ) -> None:
        """Create a CI job summary."""
        self.ci.create_agent_summary(
            agent_id=self.agent_id,
            operation=operation,
            files_analyzed=files_analyzed,
            issues_found=issues_found,
            fixes_applied=fixes_applied,
            duration_seconds=duration_seconds,
            errors=errors,
        )

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus-formatted metrics."""
        if self.metrics:
            return self.metrics.get_prometheus_metrics()
        return ""


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


def create_observability(
    agent_id: str,
    agent_type: str = "general",
    **kwargs,
) -> AIAgentObservability:
    """
    Create an observability instance for an AI agent.

    إنشاء مثيل المراقبة لوكيل الذكاء الاصطناعي

    Args:
        agent_id: Unique agent identifier
        agent_type: Type of agent
        **kwargs: Additional configuration

    Returns:
        AIAgentObservability instance
    """
    return AIAgentObservability(
        agent_id=agent_id,
        agent_type=agent_type,
        **kwargs,
    )


def get_sentry_integration(dsn: str | None = None) -> SentryIntegration:
    """Get Sentry integration instance."""
    return SentryIntegration(dsn=dsn)


def get_agent_tracer(service_name: str = "ai-agents") -> AgentTracer:
    """Get OpenTelemetry tracer for agents."""
    return AgentTracer(service_name=service_name)


def get_ci_integration() -> GitHubActionsIntegration:
    """Get GitHub Actions integration."""
    return GitHubActionsIntegration()
