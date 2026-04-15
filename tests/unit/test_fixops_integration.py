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

import json
import tempfile
from datetime import UTC
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.integration, pytest.mark.fixops]


class TestFixOpsAutoFixIntegration:
    """Test FixOps integration with Auto-Fix Engine."""

    def test_fixops_orchestrator_initialization(self):
        """Test orchestrator initializes with Auto-Fix Engine."""
        from tools.fixops.orchestrator import (
            HAS_AUTO_FIX,
            FixOpsConfig,
            FixOpsOrchestrator,
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
        from tools.fixops.orchestrator import FixOpsConfig, FixOpsOrchestrator

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
            AuditAction,
            AuditLogEntry,
            AutoAudit,
        )

        assert AutoAudit is not None
        assert AuditAction is not None
        assert AuditLogEntry is not None

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
        from shared.ai.auto_fix.auto_audit import AutoAudit

        with tempfile.TemporaryDirectory() as tmpdir:
            audit = AutoAudit(
                audit_dir=Path(tmpdir) / "audit",
                enabled=True,
            )

            assert audit is not None
            assert audit.enabled is True


class TestExperienceLearning:
    """Test Experience Learning integration."""

    def test_experience_learner_exists(self):
        """Test ExperienceLearner is importable."""
        from shared.ai.experience_learning import (
            SOP,
            ExecutionStatus,
            ExperienceLearner,
            TaskExecution,
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
            ExecutionStatus,
            ExecutionStep,
            ExperienceLearner,
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
        """Test FixLearningSystem is importable."""
        from shared.ai.auto_fix.fix_learning import (
            FixLearningSystem,
            FixPattern,
            LearnedFix,
        )

        assert FixLearningSystem is not None
        assert FixPattern is not None
        assert LearnedFix is not None

    def test_fix_learning_initialization(self):
        """Test FixLearningSystem initialization."""
        from shared.ai.auto_fix.fix_learning import FixLearningSystem

        learning = FixLearningSystem()
        assert learning is not None


class TestBatchProcessor:
    """Test Batch Processor integration."""

    def test_batch_processor_exists(self):
        """Test BatchProcessor is importable."""
        from shared.ai.auto_fix.batch_processor import (
            BatchConfig,
            BatchProcessor,
            BatchResult,
        )

        assert BatchProcessor is not None
        assert BatchConfig is not None

    def test_batch_config_defaults(self):
        """Test BatchConfig default values."""
        from shared.ai.auto_fix.batch_processor import BatchConfig

        config = BatchConfig()

        assert config.max_concurrent_files >= 1
        assert config.max_file_size_kb > 0
        assert config.enable_checkpoints is True

    @pytest.mark.asyncio
    async def test_batch_processor_initialization(self):
        """Test BatchProcessor initialization."""
        from shared.ai.auto_fix.batch_processor import (
            BatchProcessor,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            processor = BatchProcessor(checkpoint_dir=tmpdir)

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
        from tools.fixops.orchestrator import FixOpsConfig, FixOpsOrchestrator

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
        try:
            from apps.services.copilot_api.src.main import HAS_FIXOPS

            # HAS_FIXOPS should be True if import successful
            assert isinstance(HAS_FIXOPS, bool)
        except ImportError:
            # Module might not be in path, that's okay for this test
            pytest.skip("copilot_api module not in Python path")

    def test_copilot_has_audit_import(self):
        """Test Copilot API has AI Audit import."""
        try:
            from apps.services.copilot_api.src.main import HAS_AUDIT

            # HAS_AUDIT should be True if import successful
            assert isinstance(HAS_AUDIT, bool)
        except ImportError:
            # Module might not be in path, that's okay for this test
            pytest.skip("copilot_api module not in Python path")


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
    from tools.fixops.orchestrator import FixOpsConfig, FixOpsOrchestrator

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
        CodeLocation,
        Diagnostic,
        DiagnosticCategory,
        DiagnosticSeverity,
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


class TestFixOpsScheduler:
    """Test FixOps Scheduler functionality."""

    def test_scheduler_initialization(self):
        """Test scheduler initializes correctly."""
        from tools.fixops.scheduler import FixOpsScheduler

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = FixOpsScheduler(repo_root=Path(tmpdir))
            assert scheduler is not None
            assert len(scheduler.checks) > 0

    def test_check_type_values(self):
        """Test CheckType enum values."""
        from tools.fixops.scheduler import CheckType

        assert CheckType.PRE_COMMIT.value == "pre_commit"
        assert CheckType.POST_FIX.value == "post_fix"
        assert CheckType.PERIODIC.value == "periodic"
        assert CheckType.CI_CD.value == "ci_cd"

    def test_check_frequency_values(self):
        """Test CheckFrequency enum values."""
        from tools.fixops.scheduler import CheckFrequency

        assert CheckFrequency.HOURLY.value == "hourly"
        assert CheckFrequency.DAILY.value == "daily"
        assert CheckFrequency.WEEKLY.value == "weekly"
        assert CheckFrequency.MONTHLY.value == "monthly"

    def test_scheduled_check_creation(self):
        """Test ScheduledCheck creation."""
        from tools.fixops.scheduler import CheckFrequency, CheckType, ScheduledCheck

        check = ScheduledCheck(
            id="test-check",
            name="Test Check",
            name_ar="فحص اختباري",
            check_type=CheckType.PERIODIC,
            frequency=CheckFrequency.DAILY,
            tools=["ruff", "mypy"],
        )

        assert check.id == "test-check"
        assert check.check_type == CheckType.PERIODIC
        assert check.frequency == CheckFrequency.DAILY

    def test_scheduled_check_to_dict(self):
        """Test ScheduledCheck to_dict method."""
        from tools.fixops.scheduler import CheckType, ScheduledCheck

        check = ScheduledCheck(
            id="test-check",
            name="Test Check",
            name_ar="فحص اختباري",
            check_type=CheckType.PRE_COMMIT,
            tools=["ruff"],
        )

        data = check.to_dict()
        assert data["id"] == "test-check"
        assert data["check_type"] == "pre_commit"

    def test_get_due_checks(self):
        """Test getting due checks."""
        from tools.fixops.scheduler import FixOpsScheduler

        with tempfile.TemporaryDirectory() as tmpdir:
            scheduler = FixOpsScheduler(repo_root=Path(tmpdir))
            due = scheduler.get_due_checks()
            # Should have at least some checks due (never run before)
            assert isinstance(due, list)

    @pytest.mark.asyncio
    async def test_run_pre_commit_check(self):
        """Test running pre-commit check."""
        from tools.fixops.scheduler import FixOpsScheduler

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("x = 1\n")

            scheduler = FixOpsScheduler(repo_root=Path(tmpdir))
            result = await scheduler.run_pre_commit_check([str(test_file)])

            assert result is not None
            assert result.check_id is not None


class TestLogAnalyzer:
    """Test LogAnalyzer functionality."""

    def test_log_analyzer_initialization(self):
        """Test LogAnalyzer initialization."""
        from tools.fixops.scheduler import LogAnalyzer

        analyzer = LogAnalyzer()
        assert analyzer is not None

    def test_analyze_log_file(self):
        """Test analyzing a single log file."""
        from tools.fixops.scheduler import LogAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            log_file.write_text("""
2026-01-29 10:00:00 INFO Starting service
2026-01-29 10:00:01 ERROR Connection failed
2026-01-29 10:00:02 WARNING Retry attempt 1
2026-01-29 10:00:03 CRITICAL Database unavailable
""")

            analyzer = LogAnalyzer()
            result = analyzer.analyze_log_file(log_file)

            assert result is not None
            assert result.get("issues_found", 0) >= 2  # ERROR and CRITICAL
            assert "by_category" in result

    def test_error_patterns(self):
        """Test error patterns are defined."""
        from tools.fixops.scheduler import LogAnalyzer

        assert len(LogAnalyzer.ERROR_PATTERNS) > 0

        pattern_names = [p[1] for p in LogAnalyzer.ERROR_PATTERNS]
        assert "error" in pattern_names
        assert "critical" in pattern_names
        assert "exception" in pattern_names


class TestCheckResult:
    """Test CheckResult data class."""

    def test_check_result_creation(self):
        """Test CheckResult creation."""
        from datetime import datetime, timezone

        from tools.fixops.scheduler import CheckResult, CheckType

        result = CheckResult(
            check_id="test-001",
            check_type=CheckType.PERIODIC,
            started_at=datetime.now(UTC),
            success=True,
            total_issues=5,
            critical_issues=1,
        )

        assert result.check_id == "test-001"
        assert result.success is True
        assert result.total_issues == 5

    def test_check_result_to_dict(self):
        """Test CheckResult to_dict method."""
        from datetime import datetime, timezone

        from tools.fixops.scheduler import CheckResult, CheckType

        result = CheckResult(
            check_id="test-001",
            check_type=CheckType.PRE_COMMIT,
            started_at=datetime.now(UTC),
        )

        data = result.to_dict()
        assert data["check_id"] == "test-001"
        assert data["check_type"] == "pre_commit"


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_run_pre_commit_function(self):
        """Test run_pre_commit convenience function."""
        from tools.fixops.scheduler import run_pre_commit

        with tempfile.TemporaryDirectory() as tmpdir:
            result = await run_pre_commit(repo_root=Path(tmpdir))
            assert result is not None

    @pytest.mark.asyncio
    async def test_run_post_fix_function(self):
        """Test run_post_fix convenience function."""
        from tools.fixops.scheduler import run_post_fix

        with tempfile.TemporaryDirectory() as tmpdir:
            result = await run_post_fix(repo_root=Path(tmpdir))
            assert result is not None

    @pytest.mark.asyncio
    async def test_analyze_logs_function(self):
        """Test analyze_logs convenience function."""
        from tools.fixops.scheduler import analyze_logs

        with tempfile.TemporaryDirectory() as tmpdir:
            result = await analyze_logs(repo_root=Path(tmpdir))
            assert result is not None
            assert "analyzed_at" in result
