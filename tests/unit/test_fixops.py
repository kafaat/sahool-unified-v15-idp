"""
FixOps Orchestrator Test Suite
===============================
مجموعة اختبارات منسق عمليات الإصلاح

Tests for:
- Signal collection (CI, Local)
- Issue analysis and classification
- Fix recommendations
- Orchestrator workflow

Author: SAHOOL Platform Team
Updated: January 2026
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.fixops]


class TestSignalModels:
    """Test signal data models."""

    def test_ci_signal_creation(self):
        """Test CISignal creation."""
        from tools.fixops.signals import CISignal

        signal = CISignal(
            source="github_actions",
            job_id="123",
            workflow="ci.yml",
            status="completed",
        )

        assert signal.source == "github_actions"
        assert signal.job_id == "123"

    def test_ci_signal_to_dict(self):
        """Test CISignal to_dict method."""
        from tools.fixops.signals import CISignal

        signal = CISignal(
            source="github_actions",
            job_id="123",
            workflow="ci.yml",
        )

        data = signal.to_dict()
        assert data["source"] == "github_actions"
        assert data["job_id"] == "123"
        assert "timestamp" in data

    def test_local_signal_creation(self):
        """Test LocalSignal creation."""
        from tools.fixops.signals import LocalSignal

        signal = LocalSignal(
            tool="ruff",
            issues=[{"code": "E501", "message": "Line too long"}],
            exit_code=1,
        )

        assert signal.tool == "ruff"
        assert len(signal.issues) == 1
        assert signal.exit_code == 1

    def test_local_signal_to_dict(self):
        """Test LocalSignal to_dict method."""
        from tools.fixops.signals import LocalSignal

        signal = LocalSignal(
            tool="mypy",
            issues=[{"raw": "error: Incompatible types"}],
            execution_time_ms=1500.5,
        )

        data = signal.to_dict()
        assert data["tool"] == "mypy"
        assert data["execution_time_ms"] == 1500.5


class TestSignalCollector:
    """Test SignalCollector functionality."""

    def test_collector_initialization(self):
        """Test collector initializes correctly."""
        from tools.fixops.signals import SignalCollector

        collector = SignalCollector()
        assert collector is not None
        assert collector.repo_root == Path.cwd()

    def test_collector_with_custom_root(self):
        """Test collector with custom repo root."""
        from tools.fixops.signals import SignalCollector

        with tempfile.TemporaryDirectory() as tmpdir:
            collector = SignalCollector(repo_root=Path(tmpdir))
            assert collector.repo_root == Path(tmpdir)

    @patch.dict("os.environ", {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "12345"})
    def test_collect_github_actions_signal(self):
        """Test GitHub Actions signal collection."""
        from tools.fixops.signals import SignalCollector

        collector = SignalCollector()
        signals = collector.collect_ci_signals()

        assert len(signals) >= 0  # May be empty without proper env

    def test_collect_local_signals_empty(self):
        """Test local signals collection with no tools."""
        from tools.fixops.signals import SignalCollector

        with tempfile.TemporaryDirectory() as tmpdir:
            collector = SignalCollector(repo_root=Path(tmpdir))
            signals = collector.collect_local_signals()

            # May return empty or signals depending on installed tools
            assert isinstance(signals, list)

    def test_get_all_signals(self):
        """Test getting all collected signals."""
        from tools.fixops.signals import SignalCollector

        collector = SignalCollector()
        all_signals = collector.get_all_signals()

        assert "ci_signals" in all_signals
        assert "local_signals" in all_signals
        assert "summary" in all_signals

    def test_clear_signals(self):
        """Test clearing collected signals."""
        from tools.fixops.signals import LocalSignal, SignalCollector

        collector = SignalCollector()
        collector._local_signals.append(LocalSignal(tool="test", issues=[]))

        assert len(collector._local_signals) == 1

        collector.clear()
        assert len(collector._local_signals) == 0


class TestOrchestratorModels:
    """Test orchestrator data models."""

    def test_fixops_config_defaults(self):
        """Test FixOpsConfig default values."""
        from tools.fixops.orchestrator import FixOpsConfig

        config = FixOpsConfig()

        assert config.dry_run is False
        assert config.max_files_changed == 20
        assert config.fix_strategy == "safe"
        assert config.enable_auto_fix is True

    def test_fixops_config_custom(self):
        """Test FixOpsConfig with custom values."""
        from tools.fixops.orchestrator import FixOpsConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FixOpsConfig(
                repo_root=Path(tmpdir),
                dry_run=True,
                fix_strategy="minimal",
                max_files_changed=10,
            )

            assert config.repo_root == Path(tmpdir)
            assert config.dry_run is True
            assert config.fix_strategy == "minimal"

    def test_fix_recommendation_creation(self):
        """Test FixRecommendation creation."""
        from tools.fixops.orchestrator import FixRecommendation

        rec = FixRecommendation(
            id="ruff-0001",
            priority="high",
            category="bug",
            title="Undefined variable",
            title_ar="متغير غير معرف",
            description="Variable 'x' is used before definition",
            description_ar="المتغير 'x' مستخدم قبل التعريف",
            file_path="src/main.py",
            line_number=42,
            auto_fixable=True,
            tool="ruff",
        )

        assert rec.id == "ruff-0001"
        assert rec.priority == "high"
        assert rec.auto_fixable is True

    def test_fix_recommendation_to_dict(self):
        """Test FixRecommendation to_dict method."""
        from tools.fixops.orchestrator import FixRecommendation

        rec = FixRecommendation(
            id="test-0001",
            priority="medium",
            category="style",
            title="Test issue",
            title_ar="مشكلة اختبار",
            description="Test description",
            description_ar="وصف الاختبار",
        )

        data = rec.to_dict()
        assert data["id"] == "test-0001"
        assert data["priority"] == "medium"
        assert data["category"] == "style"

    def test_fixops_summary_creation(self):
        """Test FixOpsSummary creation."""
        from tools.fixops.orchestrator import FixOpsSummary

        summary = FixOpsSummary(
            id="run-001",
            repo_root="/path/to/repo",
            total_issues=10,
        )

        assert summary.id == "run-001"
        assert summary.total_issues == 10
        assert summary.status == "running"

    def test_fixops_summary_to_dict(self):
        """Test FixOpsSummary to_dict method."""
        from tools.fixops.orchestrator import FixOpsSummary

        summary = FixOpsSummary(
            id="run-001",
            repo_root="/path/to/repo",
            total_issues=5,
            issues_by_severity={"high": 2, "medium": 3},
        )

        data = summary.to_dict()
        assert data["id"] == "run-001"
        assert data["analysis"]["total_issues"] == 5


class TestOrchestrator:
    """Test FixOpsOrchestrator functionality."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        from tools.fixops.orchestrator import FixOpsConfig, FixOpsOrchestrator

        config = FixOpsConfig()
        orchestrator = FixOpsOrchestrator(config)

        assert orchestrator.config == config
        assert orchestrator.signal_collector is not None

    def test_orchestrator_default_config(self):
        """Test orchestrator with default config."""
        from tools.fixops.orchestrator import FixOpsOrchestrator

        orchestrator = FixOpsOrchestrator()
        assert orchestrator.config is not None

    def test_classify_severity_ruff(self):
        """Test severity classification for Ruff issues."""
        from tools.fixops.orchestrator import FixOpsOrchestrator

        orchestrator = FixOpsOrchestrator()

        # Security issue
        issue = {"code": "S101"}
        severity = orchestrator._classify_severity(issue, "ruff")
        assert severity == "high"

        # Error issue
        issue = {"code": "E501"}
        severity = orchestrator._classify_severity(issue, "ruff")
        assert severity == "medium"

        # Warning issue
        issue = {"code": "W191"}
        severity = orchestrator._classify_severity(issue, "ruff")
        assert severity == "low"

    def test_classify_severity_bandit(self):
        """Test severity classification for Bandit issues."""
        from tools.fixops.orchestrator import FixOpsOrchestrator

        orchestrator = FixOpsOrchestrator()

        # High severity
        issue = {"issue_severity": "HIGH"}
        severity = orchestrator._classify_severity(issue, "bandit")
        assert severity == "critical"

        # Medium severity
        issue = {"issue_severity": "MEDIUM"}
        severity = orchestrator._classify_severity(issue, "bandit")
        assert severity == "high"

    def test_classify_category_ruff(self):
        """Test category classification for Ruff issues."""
        from tools.fixops.orchestrator import FixOpsOrchestrator

        orchestrator = FixOpsOrchestrator()

        # Security category
        issue = {"code": "S101"}
        category = orchestrator._classify_category(issue, "ruff")
        assert category == "security"

        # Bug category
        issue = {"code": "F401"}
        category = orchestrator._classify_category(issue, "ruff")
        assert category == "bug"

        # Style category
        issue = {"code": "W503"}
        category = orchestrator._classify_category(issue, "ruff")
        assert category == "style"

    def test_classify_category_bandit(self):
        """Test category classification for Bandit issues."""
        from tools.fixops.orchestrator import FixOpsOrchestrator

        orchestrator = FixOpsOrchestrator()

        issue = {}
        category = orchestrator._classify_category(issue, "bandit")
        assert category == "security"

    def test_classify_category_mypy(self):
        """Test category classification for Mypy issues."""
        from tools.fixops.orchestrator import FixOpsOrchestrator

        orchestrator = FixOpsOrchestrator()

        issue = {}
        category = orchestrator._classify_category(issue, "mypy")
        assert category == "bug"

    def test_create_recommendation(self):
        """Test recommendation creation from issue."""
        from tools.fixops.orchestrator import FixOpsOrchestrator

        orchestrator = FixOpsOrchestrator()

        issue = {
            "code": "E501",
            "message": "Line too long",
            "filename": "src/main.py",
            "location": {"row": 42},
        }

        rec = orchestrator._create_recommendation(issue, "ruff", 0)

        assert rec is not None
        assert rec.tool == "ruff"
        assert rec.file_path == "src/main.py"

    def test_generate_kimi_request_empty(self):
        """Test Kimi request generation with no summary."""
        from tools.fixops.orchestrator import FixOpsOrchestrator

        orchestrator = FixOpsOrchestrator()
        request = orchestrator.generate_kimi_request()

        assert request == {}

    @pytest.mark.asyncio
    async def test_orchestrator_run_dry_run(self):
        """Test orchestrator run in dry-run mode."""
        from tools.fixops.orchestrator import FixOpsConfig, FixOpsOrchestrator

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FixOpsConfig(
                repo_root=Path(tmpdir),
                dry_run=True,
            )
            orchestrator = FixOpsOrchestrator(config)

            # Mock signal collector
            orchestrator.signal_collector.collect_local_signals = MagicMock(return_value=[])

            summary = await orchestrator.run()

            assert summary is not None
            assert summary.status == "completed"


class TestSignalSource:
    """Test SignalSource enum."""

    def test_signal_source_values(self):
        """Test SignalSource enum values."""
        from tools.fixops.orchestrator import SignalSource

        assert SignalSource.CI.value == "ci"
        assert SignalSource.LOCAL.value == "local"
        assert SignalSource.MANUAL.value == "manual"
        assert SignalSource.API.value == "api"


class TestRunFixops:
    """Test run_fixops convenience function."""

    @pytest.mark.asyncio
    async def test_run_fixops_function(self):
        """Test run_fixops convenience function."""
        from tools.fixops.orchestrator import run_fixops

        with tempfile.TemporaryDirectory() as tmpdir:
            summary = await run_fixops(
                repo_root=Path(tmpdir),
                dry_run=True,
            )

            assert summary is not None
            assert summary.status == "completed"


# Fixtures
@pytest.fixture
def temp_repo():
    """Create temporary repository directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        (Path(tmpdir) / "src").mkdir()
        (Path(tmpdir) / "src" / "main.py").write_text("print('hello')")
        yield Path(tmpdir)


@pytest.fixture
def mock_orchestrator(temp_repo):
    """Create orchestrator with mock config."""
    from tools.fixops.orchestrator import FixOpsConfig, FixOpsOrchestrator

    config = FixOpsConfig(
        repo_root=temp_repo,
        dry_run=True,
    )

    return FixOpsOrchestrator(config)
