"""
OpenMultiAgent Tools Module
===========================
وحدة أدوات OpenMultiAgent

Provides tool definitions for AI agents including built-in utilities
and agricultural-specific tools for the SAHOOL platform.

توفر تعريفات الأدوات لوكلاء الذكاء الاصطناعي بما في ذلك الأدوات المساعدة
المدمجة والأدوات الزراعية المتخصصة لمنصة سهول.

Components:
    - ToolRegistry: Central registry for discovering and managing tools
    - BuiltinTools: Core utility tools (search, file I/O, HTTP, commands)
    - AgriculturalTools: Domain-specific tools (NDVI, weather, soil, etc.)

Author: SAHOOL Platform Team
Updated: April 2026
"""

from shared.ai.tool_registry import ToolRegistry

from .agricultural import AgriculturalTools
from .builtin import BuiltinTools

__all__ = [
    "ToolRegistry",
    "BuiltinTools",
    "AgriculturalTools",
]
