"""
Tests for Frontend Diagnostics Module
======================================
اختبارات وحدة تشخيص الواجهة

Comprehensive tests for frontend and mobile diagnostics.

Author: SAHOOL Platform Team
Created: January 2026
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.auto_fix.frontend_diagnostics import (
    FrontendDiagnosticConfig,
    FrontendDiagnosticRunner,
    FrontendTool,
    MobileDiagnosticConfig,
    MobileDiagnosticRunner,
    MobileTool,
    UnifiedDiagnosticRunner,
    diagnose_all_platforms,
    diagnose_frontend,
    diagnose_mobile,
)
from shared.ai.auto_fix.models import DiagnosticReport, DiagnosticSeverity


# ═══════════════════════════════════════════════════════════════════════════
# Test FrontendTool Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestFrontendTool:
    """Tests for FrontendTool enum."""

    def test_tool_values(self):
        """Test all frontend tool values."""
        assert FrontendTool.ESLINT.value == "eslint"
        assert FrontendTool.TYPESCRIPT.value == "typescript"
        assert FrontendTool.BIOME.value == "biome"
        assert FrontendTool.OXLINT.value == "oxlint"


# ═══════════════════════════════════════════════════════════════════════════
# Test MobileTool Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestMobileTool:
    """Tests for MobileTool enum."""

    def test_tool_values(self):
        """Test all mobile tool values."""
        assert MobileTool.DART_ANALYZE.value == "dart_analyze"
        assert MobileTool.DART_FORMAT.value == "dart_format"
        assert MobileTool.FLUTTER_ANALYZE.value == "flutter_analyze"


# ═══════════════════════════════════════════════════════════════════════════
# Test FrontendDiagnosticConfig
# ═══════════════════════════════════════════════════════════════════════════


class TestFrontendDiagnosticConfig:
    """Tests for FrontendDiagnosticConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = FrontendDiagnosticConfig()

        assert "apps/web" in config.paths
        assert "apps/admin" in config.paths
        assert FrontendTool.ESLINT in config.tools
        assert FrontendTool.TYPESCRIPT in config.tools
        assert config.fix is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = FrontendDiagnosticConfig(
            paths=["custom/path"],
            tools=[FrontendTool.BIOME],
            fix=True,
        )

        assert config.paths == ["custom/path"]
        assert config.tools == [FrontendTool.BIOME]
        assert config.fix is True


# ═══════════════════════════════════════════════════════════════════════════
# Test MobileDiagnosticConfig
# ═══════════════════════════════════════════════════════════════════════════


class TestMobileDiagnosticConfig:
    """Tests for MobileDiagnosticConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MobileDiagnosticConfig()

        assert "apps/mobile" in config.paths
        assert MobileTool.DART_ANALYZE in config.tools
        assert MobileTool.DART_FORMAT in config.tools
        assert config.fix is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = MobileDiagnosticConfig(
            paths=["custom/flutter/path"],
            tools=[MobileTool.FLUTTER_ANALYZE],
            fix=True,
        )

        assert config.paths == ["custom/flutter/path"]
        assert config.tools == [MobileTool.FLUTTER_ANALYZE]
        assert config.fix is True


# ═══════════════════════════════════════════════════════════════════════════
# Test FrontendDiagnosticRunner
# ═══════════════════════════════════════════════════════════════════════════


class TestFrontendDiagnosticRunner:
    """Tests for FrontendDiagnosticRunner class."""

    @pytest.fixture
    def temp_working_dir(self):
        """Create a temporary working directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock frontend structure
            web_dir = Path(tmpdir) / "apps" / "web"
            web_dir.mkdir(parents=True)
            (web_dir / "package.json").write_text('{"name": "web"}')

            admin_dir = Path(tmpdir) / "apps" / "admin"
            admin_dir.mkdir(parents=True)
            (admin_dir / "package.json").write_text('{"name": "admin"}')

            yield tmpdir

    def test_create_runner(self, temp_working_dir):
        """Test creating a frontend diagnostic runner."""
        config = FrontendDiagnosticConfig()
        runner = FrontendDiagnosticRunner(
            config=config,
            working_dir=temp_working_dir,
        )

        assert runner.working_dir == temp_working_dir
        assert runner.config == config

    @pytest.mark.asyncio
    async def test_check_tool_available(self, temp_working_dir):
        """Test checking tool availability."""
        config = FrontendDiagnosticConfig()
        runner = FrontendDiagnosticRunner(
            config=config,
            working_dir=temp_working_dir,
        )

        with patch("asyncio.create_subprocess_shell", new_callable=AsyncMock) as mock_proc:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_process.returncode = 0
            mock_proc.return_value = mock_process

            available = await runner._check_tool_available("eslint")
            assert available is True

    @pytest.mark.asyncio
    async def test_check_tool_not_available(self, temp_working_dir):
        """Test checking tool not available."""
        config = FrontendDiagnosticConfig()
        runner = FrontendDiagnosticRunner(
            config=config,
            working_dir=temp_working_dir,
        )

        with patch("asyncio.create_subprocess_shell", new_callable=AsyncMock) as mock_proc:
            mock_proc.side_effect = FileNotFoundError()

            available = await runner._check_tool_available("nonexistent")
            assert available is False

    @pytest.mark.asyncio
    async def test_run_eslint(self, temp_working_dir):
        """Test running ESLint diagnostics."""
        config = FrontendDiagnosticConfig(tools=[FrontendTool.ESLINT])
        runner = FrontendDiagnosticRunner(
            config=config,
            working_dir=temp_working_dir,
        )

        with patch.object(runner, "_run_tool", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = []

            report = await runner.run()

            assert report is not None

    @pytest.mark.asyncio
    async def test_run_with_fix(self, temp_working_dir):
        """Test running with fix enabled."""
        config = FrontendDiagnosticConfig(
            tools=[FrontendTool.ESLINT],
            fix=True,
        )
        runner = FrontendDiagnosticRunner(
            config=config,
            working_dir=temp_working_dir,
        )

        with patch.object(runner, "_run_tool", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = []

            report = await runner.run()

            assert report is not None


# ═══════════════════════════════════════════════════════════════════════════
# Test MobileDiagnosticRunner
# ═══════════════════════════════════════════════════════════════════════════


class TestMobileDiagnosticRunner:
    """Tests for MobileDiagnosticRunner class."""

    @pytest.fixture
    def temp_flutter_dir(self):
        """Create a temporary Flutter project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock Flutter structure
            mobile_dir = Path(tmpdir) / "apps" / "mobile"
            mobile_dir.mkdir(parents=True)
            (mobile_dir / "pubspec.yaml").write_text("name: sahool_mobile")
            (mobile_dir / "lib").mkdir()

            yield tmpdir

    def test_create_runner(self, temp_flutter_dir):
        """Test creating a mobile diagnostic runner."""
        config = MobileDiagnosticConfig()
        runner = MobileDiagnosticRunner(
            config=config,
            working_dir=temp_flutter_dir,
        )

        assert runner.working_dir == temp_flutter_dir
        assert runner.config == config

    @pytest.mark.asyncio
    async def test_check_flutter_available(self, temp_flutter_dir):
        """Test checking Flutter availability."""
        config = MobileDiagnosticConfig()
        runner = MobileDiagnosticRunner(
            config=config,
            working_dir=temp_flutter_dir,
        )

        with patch("asyncio.create_subprocess_shell", new_callable=AsyncMock) as mock_proc:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(return_value=(b"Flutter 3.27.0", b""))
            mock_process.returncode = 0
            mock_proc.return_value = mock_process

            available = await runner._check_tool_available("flutter")
            assert available is True

    @pytest.mark.asyncio
    async def test_run_dart_analyze(self, temp_flutter_dir):
        """Test running Dart analyze."""
        config = MobileDiagnosticConfig(tools=[MobileTool.DART_ANALYZE])
        runner = MobileDiagnosticRunner(
            config=config,
            working_dir=temp_flutter_dir,
        )

        with patch.object(runner, "_run_tool", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = []

            report = await runner.run()

            assert report is not None


# ═══════════════════════════════════════════════════════════════════════════
# Test UnifiedDiagnosticRunner
# ═══════════════════════════════════════════════════════════════════════════


class TestUnifiedDiagnosticRunner:
    """Tests for UnifiedDiagnosticRunner class."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock project structure
            (Path(tmpdir) / "apps" / "web").mkdir(parents=True)
            (Path(tmpdir) / "apps" / "admin").mkdir(parents=True)
            (Path(tmpdir) / "apps" / "mobile" / "lib").mkdir(parents=True)
            (Path(tmpdir) / "apps" / "services").mkdir(parents=True)
            (Path(tmpdir) / "shared").mkdir(parents=True)

            yield tmpdir

    def test_create_unified_runner(self, temp_project_dir):
        """Test creating a unified diagnostic runner."""
        runner = UnifiedDiagnosticRunner(working_dir=temp_project_dir)

        assert runner.working_dir == temp_project_dir

    @pytest.mark.asyncio
    async def test_run_all_platforms(self, temp_project_dir):
        """Test running diagnostics on all platforms."""
        runner = UnifiedDiagnosticRunner(working_dir=temp_project_dir)

        with patch.object(
            runner.frontend_runner, "run", new_callable=AsyncMock
        ) as mock_frontend:
            with patch.object(
                runner.mobile_runner, "run", new_callable=AsyncMock
            ) as mock_mobile:
                mock_frontend.return_value = DiagnosticReport(
                    id="frontend",
                    target="apps/web",
                    diagnostics=[],
                )
                mock_mobile.return_value = DiagnosticReport(
                    id="mobile",
                    target="apps/mobile",
                    diagnostics=[],
                )

                result = await runner.run_all()

                assert "frontend" in result
                assert "mobile" in result

    @pytest.mark.asyncio
    async def test_run_frontend_only(self, temp_project_dir):
        """Test running frontend diagnostics only."""
        runner = UnifiedDiagnosticRunner(working_dir=temp_project_dir)

        with patch.object(
            runner.frontend_runner, "run", new_callable=AsyncMock
        ) as mock_frontend:
            mock_frontend.return_value = DiagnosticReport(
                id="frontend",
                target="apps/web",
                diagnostics=[],
            )

            result = await runner.run_frontend()

            assert result is not None

    @pytest.mark.asyncio
    async def test_run_mobile_only(self, temp_project_dir):
        """Test running mobile diagnostics only."""
        runner = UnifiedDiagnosticRunner(working_dir=temp_project_dir)

        with patch.object(
            runner.mobile_runner, "run", new_callable=AsyncMock
        ) as mock_mobile:
            mock_mobile.return_value = DiagnosticReport(
                id="mobile",
                target="apps/mobile",
                diagnostics=[],
            )

            result = await runner.run_mobile()

            assert result is not None


# ═══════════════════════════════════════════════════════════════════════════
# Test Convenience Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_diagnose_frontend(self):
        """Test diagnose_frontend function."""
        with patch.object(
            FrontendDiagnosticRunner, "run", new_callable=AsyncMock
        ) as mock_run:
            mock_run.return_value = DiagnosticReport(
                id="test",
                target="apps/web",
                diagnostics=[],
            )

            report = await diagnose_frontend(working_dir="/tmp")

            assert report is not None

    @pytest.mark.asyncio
    async def test_diagnose_mobile(self):
        """Test diagnose_mobile function."""
        with patch.object(
            MobileDiagnosticRunner, "run", new_callable=AsyncMock
        ) as mock_run:
            mock_run.return_value = DiagnosticReport(
                id="test",
                target="apps/mobile",
                diagnostics=[],
            )

            report = await diagnose_mobile(working_dir="/tmp")

            assert report is not None

    @pytest.mark.asyncio
    async def test_diagnose_all_platforms(self):
        """Test diagnose_all_platforms function."""
        with patch.object(
            UnifiedDiagnosticRunner, "run_all", new_callable=AsyncMock
        ) as mock_run:
            mock_run.return_value = {
                "frontend": DiagnosticReport(
                    id="frontend",
                    target="apps/web",
                    diagnostics=[],
                ),
                "mobile": DiagnosticReport(
                    id="mobile",
                    target="apps/mobile",
                    diagnostics=[],
                ),
            }

            result = await diagnose_all_platforms(working_dir="/tmp")

            assert "frontend" in result
            assert "mobile" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
