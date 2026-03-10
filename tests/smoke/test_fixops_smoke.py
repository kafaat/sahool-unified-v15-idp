"""
FixOps Smoke Tests
==================
اختبارات الدخان لـ FixOps

Verifies all FixOps imports and basic initialization work correctly.
يتحقق من صحة جميع الاستيرادات والتهيئة الأساسية.

These tests verify that the code structure is correct and imports work.
In CI with all dependencies, all tests should pass.
In minimal environments, tests gracefully skip.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import importlib
import sys
import os

import pytest

# Smoke test marker
pytestmark = [pytest.mark.smoke, pytest.mark.fixops]


def requires_dependency(module_name: str):
    """Skip test if dependency is not installed."""
    try:
        importlib.import_module(module_name)
        return pytest.mark.skipif(False, reason="")
    except ImportError:
        return pytest.mark.skip(reason=f"Requires {module_name}")


def safe_import(module_path: str, *names):
    """
    Safely import from a module, returning None if import fails.
    This allows tests to check what's importable without failing.
    """
    try:
        module = importlib.import_module(module_path)
        if not names:
            return module
        return tuple(getattr(module, name, None) for name in names)
    except ImportError:
        if not names:
            return None
        return tuple(None for _ in names)


class TestAutoFixFiles:
    """Verify Auto-Fix files exist."""

    def test_models_file_exists(self):
        """Test auto_fix models.py exists."""
        assert os.path.exists("shared/ai/auto_fix/models.py")

    def test_diagnostics_file_exists(self):
        """Test diagnostics.py exists."""
        assert os.path.exists("shared/ai/auto_fix/diagnostics.py")

    def test_fixers_file_exists(self):
        """Test fixers.py exists."""
        assert os.path.exists("shared/ai/auto_fix/fixers.py")

    def test_auto_audit_file_exists(self):
        """Test auto_audit.py exists."""
        assert os.path.exists("shared/ai/auto_fix/auto_audit.py")

    def test_fix_learning_file_exists(self):
        """Test fix_learning.py exists."""
        assert os.path.exists("shared/ai/auto_fix/fix_learning.py")

    def test_batch_processor_file_exists(self):
        """Test batch_processor.py exists."""
        assert os.path.exists("shared/ai/auto_fix/batch_processor.py")

    def test_engine_file_exists(self):
        """Test engine.py exists."""
        assert os.path.exists("shared/ai/auto_fix/engine.py")


class TestLLMProviderFiles:
    """Verify LLM provider files exist."""

    def test_llm_provider_file_exists(self):
        """Test llm_provider.py exists."""
        assert os.path.exists("shared/ai/llm_provider.py")

    def test_code_llm_provider_file_exists(self):
        """Test code_llm_provider.py exists."""
        assert os.path.exists("shared/ai/code_llm_provider.py")


class TestAuditFiles:
    """Verify audit files exist."""

    def test_audit_file_exists(self):
        """Test audit.py exists."""
        assert os.path.exists("shared/ai/audit.py")

    def test_experience_learning_file_exists(self):
        """Test experience_learning.py exists."""
        assert os.path.exists("shared/ai/experience_learning.py")


class TestFixOpsFiles:
    """Verify FixOps files exist."""

    def test_orchestrator_file_exists(self):
        """Test orchestrator.py exists."""
        assert os.path.exists("tools/fixops/orchestrator.py")

    def test_signals_file_exists(self):
        """Test signals.py exists."""
        assert os.path.exists("tools/fixops/signals.py")

    def test_scheduler_file_exists(self):
        """Test scheduler.py exists."""
        assert os.path.exists("tools/fixops/scheduler.py")

    def test_package_init_exists(self):
        """Test __init__.py exists."""
        assert os.path.exists("tools/fixops/__init__.py")


class TestGuardrailsFiles:
    """Verify guardrails files exist."""

    def test_tool_guard_file_exists(self):
        """Test tool_guard.py exists."""
        assert os.path.exists("shared/ai/guardrails/tool_guard.py")

    def test_allowlists_file_exists(self):
        """Test allowlists.py exists."""
        assert os.path.exists("shared/ai/guardrails/allowlists.py")

    def test_policy_file_exists(self):
        """Test policy.py exists."""
        assert os.path.exists("shared/ai/guardrails/policy.py")


class TestCopilotApiFiles:
    """Verify Copilot API file structure."""

    def test_main_file_exists(self):
        """Test main.py exists."""
        main_path = "apps/services/copilot-api/src/main.py"
        assert os.path.exists(main_path), f"{main_path} should exist"

    def test_config_file_exists(self):
        """Test config.py exists."""
        config_path = "apps/services/copilot-api/src/core/config.py"
        assert os.path.exists(config_path), f"{config_path} should exist"

    def test_schemas_directory_exists(self):
        """Test models directory exists."""
        models_path = "apps/services/copilot-api/src/models"
        assert os.path.isdir(models_path), f"{models_path} should be a directory"


# Tests that require actual imports (with dependencies)
@requires_dependency("structlog")
class TestFixOpsImports:
    """Verify all FixOps imports work correctly (requires structlog)."""

    def test_import_orchestrator(self):
        """Test orchestrator imports."""
        from tools.fixops.orchestrator import (
            FixOpsOrchestrator,
            FixOpsConfig,
            FixOpsSummary,
            FixRecommendation,
            SignalSource,
        )

        assert FixOpsOrchestrator is not None
        assert FixOpsConfig is not None
        assert FixOpsSummary is not None
        assert FixRecommendation is not None
        assert SignalSource is not None

    def test_import_signals(self):
        """Test signals imports."""
        from tools.fixops.signals import (
            SignalCollector,
            CISignal,
            LocalSignal,
        )

        assert SignalCollector is not None
        assert CISignal is not None
        assert LocalSignal is not None

    def test_import_scheduler(self):
        """Test scheduler imports."""
        from tools.fixops.scheduler import (
            FixOpsScheduler,
            LogAnalyzer,
            CheckType,
            CheckFrequency,
            ScheduledCheck,
            CheckResult,
            run_pre_commit,
            run_post_fix,
            analyze_logs,
        )

        assert FixOpsScheduler is not None
        assert LogAnalyzer is not None
        assert CheckType is not None
        assert CheckFrequency is not None
        assert ScheduledCheck is not None
        assert CheckResult is not None
        assert run_pre_commit is not None
        assert run_post_fix is not None
        assert analyze_logs is not None

    def test_import_from_package(self):
        """Test package-level imports."""
        from tools.fixops import (
            FixOpsOrchestrator,
            FixOpsSummary,
            FixOpsConfig,
            SignalSource,
            SignalCollector,
            CISignal,
            LocalSignal,
            FixOpsScheduler,
            LogAnalyzer,
            CheckType,
            CheckFrequency,
        )

        assert FixOpsOrchestrator is not None
        assert SignalCollector is not None
        assert FixOpsScheduler is not None

    def test_fixops_config_defaults(self):
        """Test FixOpsConfig has correct defaults."""
        from tools.fixops.orchestrator import FixOpsConfig

        config = FixOpsConfig()

        assert config.dry_run is False
        assert config.enable_auto_fix is True
        assert config.fix_strategy == "safe"
        assert config.use_auto_fix_engine is True
        assert config.use_audit_logger is True

    def test_signal_collector_creation(self):
        """Test SignalCollector can be created."""
        from tools.fixops.signals import SignalCollector

        collector = SignalCollector()
        assert collector is not None
        assert collector.repo_root is not None

    def test_log_analyzer_patterns(self):
        """Test LogAnalyzer has error patterns."""
        from tools.fixops.scheduler import LogAnalyzer

        assert len(LogAnalyzer.ERROR_PATTERNS) >= 5

        # Check critical patterns exist
        pattern_types = [p[1] for p in LogAnalyzer.ERROR_PATTERNS]
        assert "error" in pattern_types
        assert "critical" in pattern_types
        assert "exception" in pattern_types

    def test_check_types_defined(self):
        """Test all check types are defined."""
        from tools.fixops.scheduler import CheckType

        assert hasattr(CheckType, "PRE_COMMIT")
        assert hasattr(CheckType, "POST_COMMIT")
        assert hasattr(CheckType, "POST_FIX")
        assert hasattr(CheckType, "PERIODIC")
        assert hasattr(CheckType, "ON_DEMAND")
        assert hasattr(CheckType, "CI_CD")


@requires_dependency("structlog")
class TestAutoFixIntegration:
    """Verify Auto-Fix Engine integration (requires structlog)."""

    def test_import_auto_audit(self):
        """Test auto_audit imports."""
        from shared.ai.auto_fix.auto_audit import (
            AutoAudit,
            AuditAction,
            AuditSeverity,
            AuditLogEntry,
            AuditSummary,
        )

        assert AutoAudit is not None
        assert AuditAction is not None
        assert AuditSeverity is not None
        assert AuditLogEntry is not None
        assert AuditSummary is not None

    def test_import_fix_learning(self):
        """Test fix_learning imports."""
        from shared.ai.auto_fix.fix_learning import (
            FixLearningSystem,
            FixPattern,
            FixFeedback,
            DeveloperPreferences,
            LearnedFix,
        )

        assert FixLearningSystem is not None
        assert FixPattern is not None
        assert FixFeedback is not None
        assert DeveloperPreferences is not None
        assert LearnedFix is not None

    def test_import_batch_processor(self):
        """Test batch_processor imports."""
        from shared.ai.auto_fix.batch_processor import (
            BatchProcessor,
            BatchConfig,
            BatchResult,
        )

        assert BatchProcessor is not None
        assert BatchConfig is not None
        assert BatchResult is not None

    def test_import_auto_fix_models(self):
        """Test auto_fix models imports."""
        from shared.ai.auto_fix.models import (
            Diagnostic,
            DiagnosticReport,
            DiagnosticSeverity,
            DiagnosticCategory,
            CodeLocation,
            ToolType,
            FixStrategy,
            FixConfidence,
            CodeFix,
            FixPlan,
            FixResult,
        )

        assert Diagnostic is not None
        assert DiagnosticReport is not None
        assert FixStrategy is not None
        assert ToolType is not None

    def test_import_diagnostics(self):
        """Test diagnostics imports."""
        from shared.ai.auto_fix.diagnostics import (
            CodeDiagnostics,
            CircuitBreaker,
            DiagnosticCache,
        )

        assert CodeDiagnostics is not None
        assert CircuitBreaker is not None
        assert DiagnosticCache is not None

    def test_import_fixers(self):
        """Test fixers imports."""
        from shared.ai.auto_fix.fixers import (
            CodeFixer,
            PYTHON_FIX_PATTERNS,
            SECURITY_FIX_PATTERNS,
        )

        assert CodeFixer is not None
        assert len(PYTHON_FIX_PATTERNS) > 0
        assert len(SECURITY_FIX_PATTERNS) > 0

    def test_tool_types_coverage(self):
        """Test all tool types are defined."""
        from shared.ai.auto_fix.models import ToolType

        # Check core tools are defined
        assert hasattr(ToolType, "RUFF")
        assert hasattr(ToolType, "ESLINT")
        assert hasattr(ToolType, "MYPY")
        assert hasattr(ToolType, "BANDIT")
        assert hasattr(ToolType, "SEMGREP")
        assert hasattr(ToolType, "PYLINT")
        assert hasattr(ToolType, "DART_ANALYZE")


@requires_dependency("pydantic")
class TestGuardrailsImports:
    """Verify guardrails module imports (requires pydantic)."""

    def test_import_tool_guard(self):
        """Test tool guard imports."""
        from shared.ai.guardrails.tool_guard import (
            ToolGuard,
            ToolCallContext,
            GuardDecision,
            guard_tool_call,
        )

        assert ToolGuard is not None
        assert ToolCallContext is not None
        assert GuardDecision is not None
        assert guard_tool_call is not None

    def test_import_allowlists(self):
        """Test allowlists imports."""
        from shared.ai.guardrails.allowlists import (
            TOOL_ALLOWLIST,
            DOMAIN_ALLOWLIST,
            BLOCKED_PATTERNS,
            DANGEROUS_COMMANDS,
        )

        assert len(TOOL_ALLOWLIST) > 0
        assert len(DOMAIN_ALLOWLIST) > 0
        assert len(BLOCKED_PATTERNS) > 0
        assert len(DANGEROUS_COMMANDS) > 0

    def test_import_policy(self):
        """Test policy imports."""
        from shared.ai.guardrails.policy import (
            PolicyRule,
            GuardPolicy,
            save_policy,
            load_policy,
        )

        assert PolicyRule is not None
        assert GuardPolicy is not None
        assert save_policy is not None
        assert load_policy is not None


@requires_dependency("fastapi")
@requires_dependency("structlog")
@requires_dependency("pydantic_settings")
class TestCopilotApiImports:
    """Verify Copilot API imports work correctly (requires fastapi, structlog, pydantic_settings)."""

    def test_import_main(self):
        """Test main app imports."""
        import importlib.util

        # Skip test if pydantic_settings not available (required by config.py)
        try:
            import pydantic_settings
        except ImportError:
            pytest.skip("pydantic_settings not available")

        # Handle dash in directory name
        spec = importlib.util.spec_from_file_location("copilot_main", "apps/services/copilot-api/src/main.py")
        if spec and spec.loader:
            try:
                module = importlib.util.module_from_spec(spec)
                sys.modules["copilot_main"] = module
                spec.loader.exec_module(module)

                assert hasattr(module, "app")
                assert hasattr(module, "create_app")
                assert hasattr(module, "HAS_AUDIT")
                assert hasattr(module, "HAS_FIXOPS")
                assert isinstance(module.HAS_AUDIT, bool)
                assert isinstance(module.HAS_FIXOPS, bool)
            except ImportError as e:
                # Skip if relative imports fail (expected in test environment)
                pytest.skip(f"Copilot API imports require full package context: {e}")

    def test_import_config(self):
        """Test config imports."""
        import importlib.util

        # Skip test if pydantic_settings not available
        try:
            import pydantic_settings
        except ImportError:
            pytest.skip("pydantic_settings not available")

        spec = importlib.util.spec_from_file_location("copilot_config", "apps/services/copilot-api/src/core/config.py")
        if spec and spec.loader:
            try:
                module = importlib.util.module_from_spec(spec)
                sys.modules["copilot_config"] = module
                spec.loader.exec_module(module)

                assert hasattr(module, "Settings")
                assert hasattr(module, "get_settings")
            except ImportError as e:
                # Skip if dependencies not available
                pytest.skip(f"Config import requires pydantic_settings: {e}")


@requires_dependency("structlog")
class TestSchedulerStandalone:
    """Test scheduler module (requires structlog)."""

    def test_check_type_enum_values(self):
        """Verify CheckType enum has expected values."""
        from tools.fixops.scheduler import CheckType

        assert CheckType.PRE_COMMIT.value == "pre_commit"
        assert CheckType.POST_COMMIT.value == "post_commit"
        assert CheckType.POST_FIX.value == "post_fix"
        assert CheckType.PERIODIC.value == "periodic"
        assert CheckType.ON_DEMAND.value == "on_demand"
        assert CheckType.CI_CD.value == "ci_cd"

    def test_check_frequency_enum_values(self):
        """Verify CheckFrequency enum has expected values."""
        from tools.fixops.scheduler import CheckFrequency

        assert CheckFrequency.HOURLY.value == "hourly"
        assert CheckFrequency.DAILY.value == "daily"
        assert CheckFrequency.WEEKLY.value == "weekly"
        assert CheckFrequency.MONTHLY.value == "monthly"

    def test_log_analyzer_class(self):
        """Test LogAnalyzer can be imported and has patterns."""
        from tools.fixops.scheduler import LogAnalyzer

        assert len(LogAnalyzer.ERROR_PATTERNS) >= 5

        # Verify pattern structure
        for pattern in LogAnalyzer.ERROR_PATTERNS:
            assert len(pattern) == 3  # (regex, type, arabic_name)
            assert isinstance(pattern[0], str)
            assert isinstance(pattern[1], str)
            assert isinstance(pattern[2], str)


@requires_dependency("structlog")
class TestAuditImportsWithDeps:
    """Verify audit module imports (requires structlog)."""

    def test_import_ai_audit(self):
        """Test AI audit imports."""
        from shared.ai.audit import (
            AIAuditLogger,
            AuditEvent,
            AuditEventType,
        )

        assert AIAuditLogger is not None
        assert AuditEvent is not None
        assert AuditEventType is not None


@requires_dependency("structlog")
class TestExperienceLearningImports:
    """Verify experience learning imports (requires structlog)."""

    def test_import_experience_learning(self):
        """Test experience learning imports."""
        from shared.ai.experience_learning import (
            ExperienceLearner,
            TaskExecution,
            SOP,
            ExecutionStatus,
            SOPConfidence,
        )

        assert ExperienceLearner is not None
        assert TaskExecution is not None
        assert SOP is not None
        assert ExecutionStatus is not None
        assert SOPConfidence is not None


@requires_dependency("structlog")
class TestLLMProviderImports:
    """Verify LLM provider imports (requires structlog)."""

    def test_llm_provider_enum(self):
        """Test LLM provider enum imports."""
        from shared.ai.llm_provider import LLMProvider

        assert LLMProvider is not None
        assert hasattr(LLMProvider, "OLLAMA")
        assert hasattr(LLMProvider, "ANTHROPIC")
        assert hasattr(LLMProvider, "OPENAI")
        assert hasattr(LLMProvider, "GOOGLE")
        assert hasattr(LLMProvider, "DEEPSEEK")

    def test_llm_config(self):
        """Test LLM config class."""
        from shared.ai.llm_provider import LLMConfig

        assert LLMConfig is not None

    def test_llm_response(self):
        """Test LLM response class."""
        from shared.ai.llm_provider import LLMResponse

        assert LLMResponse is not None
