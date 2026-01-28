"""
SAHOOL AI Agents
================
وكلاء الذكاء الاصطناعي لسهول

Autonomous agricultural agents inspired by:
- Dexter: Task decomposition and self-validation
- OpenCode: Dual-agent pattern (Plan/Execute)
- Claude Code: Tool use and streaming

Enhanced Features (v2):
- Sub-agent spawning and collaboration
- Memory integration for learning from feedback
- Consensus-based multi-agent decision making
- Multi-source research with citation tracking
- Seasonal planning and resource optimization

Author: SAHOOL Platform Team
Updated: January 2026
"""

# Base classes and enums
from .base import (
    # Enums
    AgentMode,
    AgentState,
    CollaborationRole,
    ConsensusType,
    MemoryType,
    # Data classes
    AgentCapability,
    AgentStep,
    AgentTool,
    ConsensusProposal,
    DelegatedTask,
    HelpRequest,
    MemoryEntry,
    StepResult,
    ToolResult,
    # Base agent class
    BaseAutonomousAgent,
)

# Research agent with multi-source support
from .agricultural_research import (
    AgriculturalResearchAgent,
    # Research types
    Citation,
    ConfidenceAssessment,
    ResearchFinding,
    ResearchQuery,
    ResearchSourceType,
)

# Farm advisor with specialized sub-agents
from .farm_advisor import (
    FarmAdvisorAgent,
    FarmContext,
    CollaborativeDecision,
    # Specialized sub-agents
    IrrigationSubAgent,
    FertilizerSubAgent,
    PestControlSubAgent,
    HarvestPlannerSubAgent,
)

# Planner with seasonal and collaborative features
from .planner import (
    PlannerAgent,
    ExecutionPlan,
    # Seasonal planning
    Season,
    SeasonalPlan,
    ResourceAllocation,
    # Risk assessment
    RiskCategory,
    RiskAssessment,
    # Collaborative planning
    CollaborativePlan,
)

__all__ = [
    # ========================================
    # BASE CLASSES AND ENUMS
    # ========================================
    # Enums
    "AgentMode",
    "AgentState",
    "CollaborationRole",
    "ConsensusType",
    "MemoryType",
    # Core data classes
    "AgentCapability",
    "AgentStep",
    "AgentTool",
    "ConsensusProposal",
    "DelegatedTask",
    "HelpRequest",
    "MemoryEntry",
    "StepResult",
    "ToolResult",
    # Base agent
    "BaseAutonomousAgent",

    # ========================================
    # RESEARCH AGENT
    # ========================================
    "AgriculturalResearchAgent",
    "Citation",
    "ConfidenceAssessment",
    "ResearchFinding",
    "ResearchQuery",
    "ResearchSourceType",

    # ========================================
    # FARM ADVISOR AGENT
    # ========================================
    "FarmAdvisorAgent",
    "FarmContext",
    "CollaborativeDecision",
    # Specialized sub-agents
    "IrrigationSubAgent",
    "FertilizerSubAgent",
    "PestControlSubAgent",
    "HarvestPlannerSubAgent",

    # ========================================
    # PLANNER AGENT
    # ========================================
    "PlannerAgent",
    "ExecutionPlan",
    # Seasonal planning
    "Season",
    "SeasonalPlan",
    "ResourceAllocation",
    # Risk assessment
    "RiskCategory",
    "RiskAssessment",
    # Collaborative planning
    "CollaborativePlan",
]
