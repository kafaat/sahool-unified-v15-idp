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
)
from shared.ai.auto_fix.models import DiagnosticReport


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
        assert MobileTool.FLUTTER_TEST.value == "flutter_test"


# ═══════════════════════════════════════════════════════════════════════════
# Test FrontendDiagnosticConfig
# ═══════════════════════════════════════════════════════════════════════════


class TestFrontendDiagnosticConfig:
    """Tests for FrontendDiagnosticConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = FrontendDiagnosticConfig()

        assert config.web_path == "apps/web"
        assert config.admin_path == "apps/admin"
        assert FrontendTool.ESLINT in config.tools
        assert FrontendTool.TYPESCRIPT in config.tools
        assert config.auto_fix is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = FrontendDiagnosticConfig(
            web_path="custom/web",
            tools=[FrontendTool.BIOME],
            auto_fix=True,
        )

        assert config.web_path == "custom/web"
        assert config.tools == [FrontendTool.BIOME]
        assert config.auto_fix is True


# ═══════════════════════════════════════════════════════════════════════════
# Test MobileDiagnosticConfig
# ═══════════════════════════════════════════════════════════════════════════


class TestMobileDiagnosticConfig:
    """Tests for MobileDiagnosticConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MobileDiagnosticConfig()

        assert config.mobile_path == "apps/mobile"
        assert MobileTool.DART_ANALYZE in config.tools
        assert MobileTool.DART_FORMAT in config.tools
        assert config.auto_fix is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = MobileDiagnosticConfig(
            mobile_path="custom/flutter",
            tools=[MobileTool.FLUTTER_TEST],
            auto_fix=True,
        )

        assert config.mobile_path == "custom/flutter"
        assert config.tools == [MobileTool.FLUTTER_TEST]
        assert config.auto_fix is True


# ═══════════════════════════════════════════════════════════════════════════
# Test FrontendDiagnosticRunner
# ═══════════════════════════════════════════════════════════════════════════


class TestFrontendDiagnosticRunner:
    """Tests for FrontendDiagnosticRunner class."""

    def test_create_runner(self):
        """Test creating a frontend diagnostic runner."""
        config = FrontendDiagnosticConfig()
        runner = FrontendDiagnosticRunner(config=config)

        assert runner.config == config
        assert runner.working_dir == Path.cwd()

    def test_create_runner_default_config(self):
        """Test creating runner with default config."""
        runner = FrontendDiagnosticRunner()

        assert runner.config is not None
        assert runner.config.web_path == "apps/web"

    @pytest.mark.asyncio
    async def test_run_eslint(self):
        """Test running ESLint diagnostics."""
        runner = FrontendDiagnosticRunner()

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_proc:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(return_value=(b'[{"filePath":"/test.js","messages":[]}]', b""))
            mock_process.returncode = 0
            mock_proc.return_value = mock_process

            diagnostics = await runner.run_eslint("apps/web")

            assert isinstance(diagnostics, list)

    @pytest.mark.asyncio
    async def test_run_typescript(self):
        """Test running TypeScript diagnostics."""
        runner = FrontendDiagnosticRunner()

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_proc:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_process.returncode = 0
            mock_proc.return_value = mock_process

            diagnostics = await runner.run_typescript("apps/web")

            assert isinstance(diagnostics, list)


# ═══════════════════════════════════════════════════════════════════════════
# Test MobileDiagnosticRunner
# ═══════════════════════════════════════════════════════════════════════════


class TestMobileDiagnosticRunner:
    """Tests for MobileDiagnosticRunner class."""

    def test_create_runner(self):
        """Test creating a mobile diagnostic runner."""
        config = MobileDiagnosticConfig()
        runner = MobileDiagnosticRunner(config=config)

        assert runner.config == config
        assert runner.working_dir == Path.cwd()

    def test_create_runner_default_config(self):
        """Test creating runner with default config."""
        runner = MobileDiagnosticRunner()

        assert runner.config is not None
        assert runner.config.mobile_path == "apps/mobile"

    @pytest.mark.asyncio
    async def test_run_dart_analyze(self):
        """Test running Dart analyze."""
        runner = MobileDiagnosticRunner()

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_proc:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_process.returncode = 0
            mock_proc.return_value = mock_process

            diagnostics = await runner.run_dart_analyze("apps/mobile")

            assert isinstance(diagnostics, list)


# ═══════════════════════════════════════════════════════════════════════════
# Test UnifiedDiagnosticRunner
# ═══════════════════════════════════════════════════════════════════════════


class TestUnifiedDiagnosticRunner:
    """Tests for UnifiedDiagnosticRunner class."""

    def test_create_unified_runner(self):
        """Test creating a unified diagnostic runner."""
        runner = UnifiedDiagnosticRunner()

        assert runner.frontend_runner is not None
        assert runner.mobile_runner is not None

    @pytest.mark.asyncio
    async def test_diagnose_frontend(self):
        """Test running frontend diagnostics only."""
        runner = UnifiedDiagnosticRunner()

        with patch.object(runner.frontend_runner, "diagnose", new_callable=AsyncMock) as mock_diagnose:
            mock_diagnose.return_value = DiagnosticReport(
                id="frontend",
                target="apps/web",
                diagnostics=[],
            )

            result = await runner.diagnose_frontend()

            assert result is not None
            mock_diagnose.assert_called_once()

    @pytest.mark.asyncio
    async def test_diagnose_mobile(self):
        """Test running mobile diagnostics only."""
        runner = UnifiedDiagnosticRunner()

        with patch.object(runner.mobile_runner, "diagnose", new_callable=AsyncMock) as mock_diagnose:
            mock_diagnose.return_value = DiagnosticReport(
                id="mobile",
                target="apps/mobile",
                diagnostics=[],
            )

            result = await runner.diagnose_mobile()

            assert result is not None
            mock_diagnose.assert_called_once()

    @pytest.mark.asyncio
    async def test_diagnose_all(self):
        """Test running all diagnostics."""
        runner = UnifiedDiagnosticRunner()

        with patch.object(runner.frontend_runner, "diagnose", new_callable=AsyncMock) as mock_frontend:
            with patch.object(runner.mobile_runner, "diagnose", new_callable=AsyncMock) as mock_mobile:
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

                result = await runner.diagnose_all()

                assert "frontend" in result
                assert "mobile" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
