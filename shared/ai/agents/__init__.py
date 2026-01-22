"""
SAHOOL AI Agents
================
وكلاء الذكاء الاصطناعي لسهول

Autonomous agricultural agents inspired by:
- Dexter: Task decomposition and self-validation
- OpenCode: Dual-agent pattern (Plan/Execute)
- Claude Code: Tool use and streaming

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .base import (
    AgentMode,
    AgentState,
    AgentStep,
    AgentTool,
    BaseAutonomousAgent,
    StepResult,
    ToolResult,
)
from .agricultural_research import AgriculturalResearchAgent
from .farm_advisor import FarmAdvisorAgent
from .planner import PlannerAgent

__all__ = [
    # Base classes
    "AgentMode",
    "AgentState",
    "AgentStep",
    "AgentTool",
    "BaseAutonomousAgent",
    "StepResult",
    "ToolResult",
    # Specialized agents
    "AgriculturalResearchAgent",
    "FarmAdvisorAgent",
    "PlannerAgent",
]
