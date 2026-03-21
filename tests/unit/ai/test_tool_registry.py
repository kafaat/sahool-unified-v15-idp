"""
Tool Registry Tests - اختبارات سجل الأدوات
=============================================

Tests for tool registration, discovery, capability querying,
and configuration management.
"""

import pytest

pytest.importorskip("structlog")

from shared.ai.tool_registry import (
    Language,
    QualityConfig,
    ToolCapability,
    ToolCategory,
    ToolInfo,
    ToolMetrics,
    ToolRegistry,
    ToolResult,
    ToolStatus,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    """Tests for tool registry enums."""

    def test_tool_category_values(self):
        assert ToolCategory.LINTER == "linter"
        assert ToolCategory.FORMATTER == "formatter"
        assert ToolCategory.TYPE_CHECKER == "type_checker"
        assert ToolCategory.SECURITY == "security"
        assert ToolCategory.TESTING == "testing"

    def test_tool_capability_values(self):
        assert ToolCapability.AUTO_FIX == "auto_fix"
        assert ToolCapability.INCREMENTAL == "incremental"
        assert ToolCapability.PARALLEL == "parallel"
        assert ToolCapability.JSON_OUTPUT == "json_output"

    def test_tool_status_values(self):
        assert ToolStatus.AVAILABLE == "available"
        assert ToolStatus.UNAVAILABLE == "unavailable"
        assert ToolStatus.DISABLED == "disabled"
        assert ToolStatus.CIRCUIT_OPEN == "circuit_open"

    def test_language_values(self):
        assert Language.PYTHON == "python"
        assert Language.TYPESCRIPT == "typescript"
        assert Language.DART == "dart"


# =============================================================================
# ToolInfo Tests
# =============================================================================


class TestToolInfo:
    """Tests for ToolInfo dataclass."""

    def test_create_tool_info(self):
        tool = ToolInfo(
            id="ruff",
            name="Ruff",
            name_ar="راف",
            category=ToolCategory.LINTER,
            languages=[Language.PYTHON],
            command="ruff check",
            version_command="ruff --version",
            capabilities=[ToolCapability.AUTO_FIX, ToolCapability.JSON_OUTPUT],
        )
        assert tool.id == "ruff"
        assert tool.name == "Ruff"
        assert tool.name_ar == "راف"
        assert tool.category == ToolCategory.LINTER
        assert Language.PYTHON in tool.languages
        assert ToolCapability.AUTO_FIX in tool.capabilities
        assert tool.status == ToolStatus.UNAVAILABLE
        assert tool.priority == 100

    def test_tool_info_defaults(self):
        tool = ToolInfo(
            id="test",
            name="Test Tool",
            name_ar="أداة اختبار",
            category=ToolCategory.TESTING,
            languages=[Language.PYTHON],
            command="test",
            version_command="test --version",
            capabilities=[],
        )
        assert tool.default_args == []
        assert tool.config_file is None
        assert tool.version is None
        assert tool.timeout_seconds == 60
        assert tool.description == ""
        assert tool.description_ar == ""


# =============================================================================
# ToolResult Tests
# =============================================================================


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_create_tool_result(self):
        result = ToolResult(
            tool_id="ruff",
            success=True,
            exit_code=0,
            stdout="All checks passed",
            stderr="",
            duration_ms=150.0,
            issues_count=0,
            fixed_count=0,
        )
        assert result.tool_id == "ruff"
        assert result.success is True
        assert result.exit_code == 0
        assert result.issues_count == 0
        assert result.duration_ms == 150.0

    def test_failed_result(self):
        result = ToolResult(
            tool_id="mypy",
            success=False,
            exit_code=1,
            stdout="",
            stderr="Module not found",
            duration_ms=500.0,
            issues_count=5,
            error_message="Mypy failed",
        )
        assert result.success is False
        assert result.error_message == "Mypy failed"
        assert result.issues_count == 5


# =============================================================================
# ToolMetrics Tests
# =============================================================================


class TestToolMetrics:
    """Tests for ToolMetrics dataclass."""

    def test_default_metrics(self):
        metrics = ToolMetrics(tool_id="ruff")
        assert metrics.tool_id == "ruff"
        assert metrics.total_runs == 0
        assert metrics.successful_runs == 0
        assert metrics.failed_runs == 0
        assert metrics.avg_duration_ms == 0.0

    def test_metrics_with_values(self):
        metrics = ToolMetrics(
            tool_id="ruff",
            total_runs=100,
            successful_runs=95,
            failed_runs=5,
            avg_duration_ms=200.0,
            issues_found=50,
            issues_fixed=30,
        )
        assert metrics.total_runs == 100
        assert metrics.successful_runs == 95
        assert metrics.failed_runs == 5
        assert metrics.issues_found == 50
        assert metrics.issues_fixed == 30


# =============================================================================
# QualityConfig Tests
# =============================================================================


class TestQualityConfig:
    """Tests for QualityConfig dataclass."""

    def test_default_config(self):
        config = QualityConfig()
        assert "ruff" in config.python_tools
        assert "mypy" in config.python_tools
        assert "bandit" in config.python_tools
        assert "eslint" in config.typescript_tools
        assert "tsc" in config.typescript_tools
        assert "dart_analyze" in config.dart_tools

    def test_default_settings(self):
        config = QualityConfig()
        assert config.fail_on_warning is False
        assert config.auto_fix is True
        assert config.parallel_execution is True
        assert config.max_parallel_tools == 4
        assert config.cache_enabled is True
        assert config.cache_ttl_seconds == 300

    def test_exclude_patterns(self):
        config = QualityConfig()
        assert "**/node_modules/**" in config.exclude_patterns
        assert "**/.git/**" in config.exclude_patterns
        assert "**/*.g.dart" in config.exclude_patterns

    def test_custom_config(self):
        config = QualityConfig(
            python_tools=["ruff"],
            auto_fix=False,
            max_parallel_tools=2,
        )
        assert config.python_tools == ["ruff"]
        assert config.auto_fix is False
        assert config.max_parallel_tools == 2

    def test_from_yaml_missing_file_returns_defaults(self):
        config = QualityConfig.from_yaml("/nonexistent/path/config.yaml")
        assert "ruff" in config.python_tools
        assert config.auto_fix is True


# =============================================================================
# ToolRegistry Tests
# =============================================================================


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_registry_initialization(self):
        registry = ToolRegistry()
        assert registry is not None

    def test_register_tool(self):
        registry = ToolRegistry()
        tool = ToolInfo(
            id="custom-tool",
            name="Custom Tool",
            name_ar="أداة مخصصة",
            category=ToolCategory.LINTER,
            languages=[Language.PYTHON],
            command="custom-tool check",
            version_command="custom-tool --version",
            capabilities=[ToolCapability.AUTO_FIX],
        )
        registry.register(tool)
        assert registry.get_tool("custom-tool") is not None

    def test_get_nonexistent_tool_returns_none(self):
        registry = ToolRegistry()
        assert registry.get_tool("nonexistent-xyz") is None

    def test_default_tools_registered(self):
        """Registry should have default tools pre-registered."""
        registry = ToolRegistry()
        ruff = registry.get_tool("ruff")
        assert ruff is not None
        assert ruff.name == "Ruff"
        assert Language.PYTHON in ruff.languages

    def test_get_tools_for_language(self):
        registry = ToolRegistry()
        python_tools = registry.get_tools_for_language(Language.PYTHON)
        tool_ids = [t.id for t in python_tools]
        assert "ruff" in tool_ids
        assert "mypy" in tool_ids
        assert "bandit" in tool_ids

    def test_get_tools_for_typescript(self):
        registry = ToolRegistry()
        ts_tools = registry.get_tools_for_language(Language.TYPESCRIPT)
        tool_ids = [t.id for t in ts_tools]
        assert "eslint" in tool_ids
        assert "tsc" in tool_ids

    def test_get_tools_by_category(self):
        """Filter tools by category using get_all_tools."""
        registry = ToolRegistry()
        all_tools = registry.get_all_tools()
        linters = [t for t in all_tools if t.category == ToolCategory.LINTER]
        assert any(t.id == "ruff" for t in linters)

        security = [t for t in all_tools if t.category == ToolCategory.SECURITY]
        assert any(t.id == "bandit" for t in security)

    def test_get_all_tools(self):
        registry = ToolRegistry()
        all_tools = registry.get_all_tools()
        assert len(all_tools) >= 5  # Should have at least the default tools

    def test_tool_status_change(self):
        """Test changing tool status directly."""
        registry = ToolRegistry()
        ruff = registry.get_tool("ruff")
        assert ruff is not None
        ruff.status = ToolStatus.AVAILABLE
        assert ruff.status == ToolStatus.AVAILABLE

        ruff.status = ToolStatus.DISABLED
        ruff_after = registry.get_tool("ruff")
        assert ruff_after is not None
        assert ruff_after.status == ToolStatus.DISABLED

    def test_get_enabled_tools(self):
        """Test getting enabled tools for a language."""
        registry = ToolRegistry()
        # Mark ruff as available
        ruff = registry.get_tool("ruff")
        assert ruff is not None
        ruff.status = ToolStatus.AVAILABLE

        enabled = registry.get_enabled_tools(Language.PYTHON)
        assert any(t.id == "ruff" for t in enabled)

    def test_get_tools_with_autofix_capability(self):
        """Filter tools by capability using get_all_tools."""
        registry = ToolRegistry()
        all_tools = registry.get_all_tools()
        auto_fix_tools = [
            t for t in all_tools if ToolCapability.AUTO_FIX in t.capabilities
        ]
        assert any(t.id == "ruff" for t in auto_fix_tools)
