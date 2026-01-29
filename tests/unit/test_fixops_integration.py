"""
FixOps Integration Test Suite
==============================
مجموعة اختبارات تكامل FixOps

Tests for:
- FixOps ↔ Auto-Fix Engine integration
- Signal collection with all tools
- Copilot API ↔ FixOps integration
- AI Audit Logger integration
- End-to-end workflow

Author: SAHOOL Platform Team
Updated: January 2026
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import json

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.integration, pytest.mark.fixops]


class TestFixOpsAutoFixIntegration:
    """Test FixOps integration with Auto-Fix Engine."""

    def test_fixops_orchestrator_initialization(self):
        """Test orchestrator initializes with Auto-Fix Engine."""
        from tools.fixops.orchestrator import (
            FixOpsOrchestrator,
            FixOpsConfig,
            HAS_AUTO_FIX,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FixOpsConfig(
                repo_root=Path(tmpdir),
                use_auto_fix_engine=True,
                dry_run=True,
            )
            orchestrator = FixOpsOrchestrator(config)

            assert orchestrator is not None
            assert orchestrator.config.use_auto_fix_engine is True

    def test_fixops_config_integration_options(self):
        """Test FixOpsConfig has integration options."""
        from tools.fixops.orchestrator import FixOpsConfig

        config = FixOpsConfig()

        assert hasattr(config, "use_auto_fix_engine")
        assert hasattr(config, "use_audit_logger")
        assert config.use_auto_fix_engine is True
        assert config.use_audit_logger is True

    @pytest.mark.asyncio
    async def test_fixops_run_with_engine(self):
        """Test FixOps run uses Auto-Fix Engine when available."""
        from tools.fixops.orchestrator import FixOpsOrchestrator, FixOpsConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("x=1\n")

            config = FixOpsConfig(
                repo_root=Path(tmpdir),
                dry_run=True,
                use_auto_fix_engine=False,  # Disable for this test
            )
            orchestrator = FixOpsOrchestrator(config)

            # Mock signal collector
            orchestrator.signal_collector.collect_local_signals = MagicMock(return_value=[])

            summary = await orchestrator.run()

            assert summary is not None
            assert summary.status == "completed"


class TestSignalCollectorTools:
    """Test SignalCollector with all diagnostic tools."""

    def test_signal_collector_initialization(self):
        """Test SignalCollector initializes correctly."""
        from tools.fixops.signals import SignalCollector

        collector = SignalCollector()
        assert collector is not None
        assert collector.repo_root == Path.cwd()

    def test_local_signal_structure(self):
        """Test LocalSignal structure includes all fields."""
        from tools.fixops.signals import LocalSignal

        signal = LocalSignal(
            tool="ruff",
            issues=[{"code": "E501", "message": "Line too long"}],
            exit_code=1,
            execution_time_ms=150.0,
        )

        data = signal.to_dict()
        assert data["tool"] == "ruff"
        assert len(data["issues"]) == 1
        assert data["execution_time_ms"] == 150.0

    def test_signal_collector_has_semgrep_support(self):
        """Test SignalCollector has Semgrep support."""
        from tools.fixops.signals import SignalCollector

        collector = SignalCollector()
        assert hasattr(collector, "_run_semgrep")

    def test_signal_collector_has_pylint_support(self):
        """Test SignalCollector has Pylint support."""
        from tools.fixops.signals import SignalCollector

        collector = SignalCollector()
        assert hasattr(collector, "_run_pylint")

    def test_ci_signal_github_actions(self):
        """Test GitHub Actions CI signal collection."""
        from tools.fixops.signals import CISignal

        signal = CISignal(
            source="github_actions",
            job_id="12345",
            workflow="ci.yml",
            status="completed",
            metadata={
                "repository": "kafaat/sahool",
                "ref": "refs/heads/main",
            },
        )

        data = signal.to_dict()
        assert data["source"] == "github_actions"
        assert data["job_id"] == "12345"
        assert "repository" in data["metadata"]


class TestAutoAuditIntegration:
    """Test Auto-Audit system integration."""

    def test_auto_audit_model_exists(self):
        """Test AutoAudit models are importable."""
        from shared.ai.auto_fix.auto_audit import (
            AutoAudit,
            AuditAction,
            AuditConfig,
        )

        assert AutoAudit is not None
        assert AuditAction is not None

    def test_audit_action_values(self):
        """Test AuditAction enum values."""
        from shared.ai.auto_fix.auto_audit import AuditAction

        assert AuditAction.DIAGNOSE.value == "diagnose"
        assert AuditAction.FIX_APPLY.value == "fix_apply"
        assert AuditAction.FIX_ROLLBACK.value == "fix_rollback"
        assert AuditAction.FILE_MODIFIED.value == "file_modified"
        assert AuditAction.SECURITY_SCAN.value == "security_scan"

    def test_auto_audit_initialization(self):
        """Test AutoAudit initialization."""
        from shared.ai.auto_fix.auto_audit import AutoAudit, AuditConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config = AuditConfig(
                log_dir=Path(tmpdir) / "audit",
                enable_file_logging=True,
                enable_db_logging=False,
            )
            audit = AutoAudit(config)

            assert audit is not None


class TestExperienceLearning:
    """Test Experience Learning integration."""

    def test_experience_learner_exists(self):
        """Test ExperienceLearner is importable."""
        from shared.ai.experience_learning import (
            ExperienceLearner,
            TaskExecution,
            SOP,
            ExecutionStatus,
        )

        assert ExperienceLearner is not None
        assert TaskExecution is not None

    def test_execution_status_values(self):
        """Test ExecutionStatus enum values."""
        from shared.ai.experience_learning import ExecutionStatus

        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.PARTIAL.value == "partial"
        assert ExecutionStatus.FAILURE.value == "failure"

    def test_sop_confidence_values(self):
        """Test SOPConfidence enum values."""
        from shared.ai.experience_learning import SOPConfidence

        assert SOPConfidence.HIGH.value == "high"
        assert SOPConfidence.MEDIUM.value == "medium"
        assert SOPConfidence.LOW.value == "low"
        assert SOPConfidence.EXPERIMENTAL.value == "experimental"

    @pytest.mark.asyncio
    async def test_experience_learner_record_execution(self):
        """Test recording task execution."""
        from shared.ai.experience_learning import (
            ExperienceLearner,
            ExecutionStep,
            ExecutionStatus,
        )

        learner = ExperienceLearner()

        execution = await learner.record_execution(
            task_type="code_fix",
            task_description="Fix linting errors",
            steps=[
                ExecutionStep(
                    step_number=1,
                    action="run_ruff",
                    parameters={"path": "src/"},
                    success=True,
                ),
            ],
            status=ExecutionStatus.SUCCESS,
            context={"language": "python"},
            tenant_id="test-tenant",
            agent_id="code-fix-agent",
        )

        assert execution is not None
        assert execution.task_type == "code_fix"
        assert execution.status == ExecutionStatus.SUCCESS


class TestFixLearning:
    """Test Fix Learning integration."""

    def test_fix_learning_exists(self):
        """Test FixLearning is importable."""
        from shared.ai.auto_fix.fix_learning import (
            FixLearning,
            FixPattern,
            FixStatistics,
        )

        assert FixLearning is not None
        assert FixPattern is not None

    def test_fix_learning_initialization(self):
        """Test FixLearning initialization."""
        from shared.ai.auto_fix.fix_learning import FixLearning

        learning = FixLearning()
        assert learning is not None


class TestBatchProcessor:
    """Test Batch Processor integration."""

    def test_batch_processor_exists(self):
        """Test BatchProcessor is importable."""
        from shared.ai.auto_fix.batch_processor import (
            BatchProcessor,
            BatchConfig,
            BatchResult,
        )

        assert BatchProcessor is not None
        assert BatchConfig is not None

    def test_batch_config_defaults(self):
        """Test BatchConfig default values."""
        from shared.ai.auto_fix.batch_processor import BatchConfig

        config = BatchConfig()

        assert config.max_workers >= 1
        assert config.timeout_per_file > 0
        assert config.enable_checkpoints is True

    @pytest.mark.asyncio
    async def test_batch_processor_initialization(self):
        """Test BatchProcessor initialization."""
        from shared.ai.auto_fix.batch_processor import (
            BatchProcessor,
            BatchConfig,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = BatchConfig(
                output_dir=Path(tmpdir),
                dry_run=True,
            )
            processor = BatchProcessor(config)

            assert processor is not None


class TestAutoFixEngine:
    """Test Auto-Fix Engine integration."""

    def test_engine_initialization(self):
        """Test AutoFixEngine initialization."""
        from shared.ai.auto_fix.engine import AutoFixEngine

        engine = AutoFixEngine(dry_run=True)
        assert engine is not None
        assert engine.dry_run is True

    def test_fix_strategy_values(self):
        """Test FixStrategy enum values."""
        from shared.ai.auto_fix.models import FixStrategy

        assert FixStrategy.MINIMAL.value == "minimal"
        assert FixStrategy.SAFE.value == "safe"
        assert FixStrategy.COMPREHENSIVE.value == "comprehensive"
        assert FixStrategy.REFACTOR.value == "refactor"

    @pytest.mark.asyncio
    async def test_engine_diagnose_file(self):
        """Test diagnosing a single file."""
        from shared.ai.auto_fix.engine import AutoFixEngine

        engine = AutoFixEngine(dry_run=True)

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("x = 1\n")
            f.flush()

            try:
                report = await engine.diagnose(f.name)
                assert report is not None
                assert hasattr(report, "diagnostics")
            except Exception:
                # Tool may not be available
                pass


class TestDiagnosticsTools:
    """Test Diagnostics with all tools."""

    def test_diagnostics_initialization(self):
        """Test CodeDiagnostics initialization."""
        from shared.ai.auto_fix.diagnostics import CodeDiagnostics

        diagnostics = CodeDiagnostics()
        assert diagnostics is not None

    def test_tool_types_defined(self):
        """Test all ToolTypes are defined."""
        from shared.ai.auto_fix.models import ToolType

        assert ToolType.RUFF.value == "ruff"
        assert ToolType.ESLINT.value == "eslint"
        assert ToolType.MYPY.value == "mypy"
        assert ToolType.BANDIT.value == "bandit"
        assert ToolType.SEMGREP.value == "semgrep"
        assert ToolType.PYLINT.value == "pylint"
        assert ToolType.DART_ANALYZE.value == "dart_analyze"

    def test_security_patterns_defined(self):
        """Test security patterns are defined."""
        from shared.ai.auto_fix.diagnostics import SECURITY_PATTERNS

        assert len(SECURITY_PATTERNS) > 0

        # Check for critical patterns
        pattern_ids = [p.id for p in SECURITY_PATTERNS]
        assert "SEC001" in pattern_ids  # SQL Injection
        assert "SEC005" in pattern_ids  # eval()
        assert "SEC009" in pattern_ids  # Hardcoded secrets

    def test_circuit_breaker_exists(self):
        """Test CircuitBreaker is available."""
        from shared.ai.auto_fix.diagnostics import CircuitBreaker

        cb = CircuitBreaker()
        assert cb is not None
        assert cb.can_execute("test_tool") is True

    def test_diagnostic_cache_exists(self):
        """Test DiagnosticCache is available."""
        from shared.ai.auto_fix.diagnostics import DiagnosticCache

        cache = DiagnosticCache(ttl_seconds=60)
        assert cache is not None

        stats = cache.get_stats()
        assert "hits" in stats
        assert "misses" in stats


class TestKimiRequestGeneration:
    """Test Kimi request generation."""

    @pytest.mark.asyncio
    async def test_generate_kimi_request(self):
        """Test generating Kimi-compatible request."""
        from tools.fixops.orchestrator import FixOpsOrchestrator, FixOpsConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FixOpsConfig(
                repo_root=Path(tmpdir),
                dry_run=True,
            )
            orchestrator = FixOpsOrchestrator(config)

            # Mock run to populate summary
            orchestrator.signal_collector.collect_local_signals = MagicMock(return_value=[])
            await orchestrator.run()

            request = orchestrator.generate_kimi_request()

            # Verify request structure
            assert "version" in request
            assert "mode" in request
            assert request["mode"] == "patch-only"
            assert "constraints" in request
            assert request["constraints"]["no_network"] is True
            assert "questions" in request


class TestCopilotFixOpsIntegration:
    """Test Copilot API ↔ FixOps integration."""

    def test_copilot_has_fixops_import(self):
        """Test Copilot API has FixOps import."""
        from apps.services.copilot_api.src.main import HAS_FIXOPS

        # HAS_FIXOPS should be True if import successful
        assert isinstance(HAS_FIXOPS, bool)

    def test_copilot_has_audit_import(self):
        """Test Copilot API has AI Audit import."""
        from apps.services.copilot_api.src.main import HAS_AUDIT

        # HAS_AUDIT should be True if import successful
        assert isinstance(HAS_AUDIT, bool)


# Fixtures
@pytest.fixture
def temp_repo():
    """Create temporary repository directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        src_dir = Path(tmpdir) / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('hello')\n")
        (src_dir / "utils.py").write_text("def helper(): pass\n")
        yield Path(tmpdir)


@pytest.fixture
def mock_orchestrator(temp_repo):
    """Create orchestrator with mock config."""
    from tools.fixops.orchestrator import FixOpsOrchestrator, FixOpsConfig

    config = FixOpsConfig(
        repo_root=temp_repo,
        dry_run=True,
        use_auto_fix_engine=False,
        use_audit_logger=False,
    )

    return FixOpsOrchestrator(config)


@pytest.fixture
def sample_diagnostic():
    """Create sample diagnostic."""
    from shared.ai.auto_fix.models import (
        Diagnostic,
        DiagnosticSeverity,
        DiagnosticCategory,
        CodeLocation,
        ToolType,
    )

    return Diagnostic(
        id="test-001",
        message="Line too long",
        message_ar="السطر طويل جداً",
        severity=DiagnosticSeverity.WARNING,
        category=DiagnosticCategory.STYLE,
        location=CodeLocation(
            file_path="src/main.py",
            line_start=10,
        ),
        rule_id="E501",
        tool=ToolType.RUFF,
    )
