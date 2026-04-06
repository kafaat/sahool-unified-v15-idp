"""
Tests for shared/ai/auto_fix/engine.py fixes
اختبارات إصلاحات محرك الإصلاح التلقائي

Validates:
- get_available_tools() checks ALL ToolType entries (not just 5)
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
os.environ.setdefault("ENVIRONMENT", "test")


class TestGetAvailableToolsExpansion:
    """Test that get_available_tools checks all defined tools."""

    def test_tooltype_has_more_than_5_entries(self):
        """ToolType enum should have 22 entries."""
        from shared.ai.auto_fix.models import ToolType

        tools = list(ToolType)
        assert len(tools) >= 20, (
            f"Expected at least 20 ToolType entries, got {len(tools)}. "
            "New tools may have been added."
        )

    def test_engine_get_available_tools_checks_all(self):
        """get_available_tools should iterate all ToolType, not a hardcoded subset."""
        import inspect
        from shared.ai.auto_fix.engine import AutoFixEngine

        source = inspect.getsource(AutoFixEngine.get_available_tools)

        # Should NOT contain a hardcoded list of specific tools
        assert "ToolType.RUFF," not in source or "for tool in ToolType" in source, (
            "get_available_tools should iterate ToolType enum, not hardcode specific tools"
        )

        # Should iterate all ToolType
        assert "for tool in ToolType" in source, (
            "get_available_tools should use 'for tool in ToolType' to check all tools"
        )

    def test_all_tooltype_values_are_strings(self):
        """Each ToolType value should be a non-empty string."""
        from shared.ai.auto_fix.models import ToolType

        for tool in ToolType:
            assert isinstance(tool.value, str), f"ToolType.{tool.name} value is not a string"
            assert len(tool.value) > 0, f"ToolType.{tool.name} has empty value"

    def test_key_tools_present_in_tooltype(self):
        """Essential tools must exist in ToolType enum."""
        from shared.ai.auto_fix.models import ToolType

        required = [
            "ruff", "eslint", "mypy", "bandit", "dart_analyze",
            "biome", "semgrep", "trivy", "hadolint", "detect_secrets",
        ]
        tool_values = {t.value for t in ToolType}

        for tool_name in required:
            assert tool_name in tool_values, (
                f"ToolType missing required tool: {tool_name}"
            )
