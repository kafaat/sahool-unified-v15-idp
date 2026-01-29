"""
FixOps Smoke Tests
==================
اختبارات الدخان لـ FixOps

Verifies all FixOps imports and basic initialization work correctly.
يتحقق من صحة جميع الاستيرادات والتهيئة الأساسية.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import pytest

# Smoke test marker
pytestmark = [pytest.mark.smoke, pytest.mark.fixops]


class TestFixOpsImports:
    """Verify all FixOps imports work correctly."""

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


class TestAutoFixImports:
    """Verify Auto-Fix Engine imports work correctly."""

    def test_import_auto_fix_engine(self):
        """Test auto_fix engine imports."""
        from shared.ai.auto_fix.engine import AutoFixEngine

        assert AutoFixEngine is not None

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

    def test_import_auto_audit(self):
        """Test auto_audit imports."""
        from shared.ai.auto_fix.auto_audit import (
            AutoAudit,
            AuditAction,
            AuditConfig,
        )

        assert AutoAudit is not None
        assert AuditAction is not None

    def test_import_fix_learning(self):
        """Test fix_learning imports."""
        from shared.ai.auto_fix.fix_learning import (
            FixLearning,
            FixPattern,
            FixStatistics,
        )

        assert FixLearning is not None
        assert FixPattern is not None

    def test_import_batch_processor(self):
        """Test batch_processor imports."""
        from shared.ai.auto_fix.batch_processor import (
            BatchProcessor,
            BatchConfig,
            BatchResult,
        )

        assert BatchProcessor is not None
        assert BatchConfig is not None


class TestAIModuleImports:
    """Verify AI module imports work correctly."""

    def test_import_llm_provider(self):
        """Test LLM provider imports."""
        from shared.ai.llm_provider import (
            LLMProvider,
            LLMRequest,
            LLMResponse,
            LLMManager,
        )

        assert LLMProvider is not None
        assert LLMManager is not None

    def test_import_code_llm_provider(self):
        """Test code LLM provider imports."""
        from shared.ai.code_llm_provider import (
            CodeLLMProvider,
            CodeTaskType,
            CodeContext,
            CodeCompletionResult,
            CodeReviewResult,
            CodeFixResult,
        )

        assert CodeLLMProvider is not None
        assert CodeTaskType is not None

    def test_import_audit(self):
        """Test AI audit imports."""
        from shared.ai.audit import (
            AIAuditLogger,
            AuditEvent,
            AuditEventType,
        )

        assert AIAuditLogger is not None
        assert AuditEvent is not None

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
        assert SOPConfidence is not None


class TestGuardrailsImports:
    """Verify guardrails module imports work correctly."""

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


class TestCopilotApiImports:
    """Verify Copilot API imports work correctly."""

    def test_import_main(self):
        """Test main app imports."""
        from apps.services.copilot_api.src.main import (
            app,
            create_app,
            HAS_AUDIT,
            HAS_FIXOPS,
        )

        assert app is not None
        assert create_app is not None
        assert isinstance(HAS_AUDIT, bool)
        assert isinstance(HAS_FIXOPS, bool)

    def test_import_config(self):
        """Test config imports."""
        from apps.services.copilot_api.src.core.config import (
            Settings,
            get_settings,
        )

        assert Settings is not None
        assert get_settings is not None

    def test_import_schemas(self):
        """Test schemas imports."""
        from apps.services.copilot_api.src.models.schemas import (
            ChatRequest,
            ChatResponse,
            ChatContext,
        )

        assert ChatRequest is not None
        assert ChatResponse is not None


class TestBasicInitialization:
    """Test basic initialization of key components."""

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

    def test_llm_providers_defined(self):
        """Test all LLM providers are defined."""
        from shared.ai.llm_provider import LLMProvider

        assert hasattr(LLMProvider, "OLLAMA")
        assert hasattr(LLMProvider, "ANTHROPIC")
        assert hasattr(LLMProvider, "OPENAI")
        assert hasattr(LLMProvider, "GOOGLE")
        assert hasattr(LLMProvider, "DEEPSEEK")

    def test_check_types_defined(self):
        """Test all check types are defined."""
        from tools.fixops.scheduler import CheckType

        assert hasattr(CheckType, "PRE_COMMIT")
        assert hasattr(CheckType, "POST_COMMIT")
        assert hasattr(CheckType, "POST_FIX")
        assert hasattr(CheckType, "PERIODIC")
        assert hasattr(CheckType, "ON_DEMAND")
        assert hasattr(CheckType, "CI_CD")
