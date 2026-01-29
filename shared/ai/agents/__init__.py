"""
SAHOOL AI Agents
================
وكلاء الذكاء الاصطناعي لسهول

Autonomous agricultural agents inspired by:
- Dexter: Task decomposition and self-validation
- OpenCode: Dual-agent pattern (Plan/Execute)
- Claude Code: Tool use and streaming
- ReAct: Reasoning + Acting pattern
- Tree-of-Thoughts: Complex problem solving

Enhanced Features (v3):
- Sub-agent spawning and collaboration
- Memory integration for learning from feedback
- Consensus-based multi-agent decision making
- Multi-source research with citation tracking
- Seasonal planning and resource optimization
- ReAct pattern with explicit reasoning traces
- Multi-level memory (episodic, semantic, procedural)
- Tree-of-Thoughts for solution exploration

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

# ReAct Agent - Reasoning + Acting pattern
from .react_agent import (
    ReActAgent,
    ReActStep,
    ReActThought,
    ReActAction,
    ReActObservation,
    ReActReflection,
    ReActTrace,
    ReActStepType,
    # Helper functions
    create_thought,
    create_action,
    create_reflection,
)

# Tree Search Agent - Tree-of-Thoughts pattern
from .tree_search_agent import (
    TreeSearchAgent,
    ThoughtNode,
    ThoughtPath,
    ThoughtTree,
    SearchStrategy,
    NodeStatus,
    create_thought_node,
)

# Multi-level Memory System
from .memory_system import (
    AgentMemorySystem,
    MemoryStore,
    MemoryEntry as MultiLevelMemoryEntry,
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
    WorkingMemory,
    MemoryType as MultiLevelMemoryType,
    MemoryPriority,
    RetrievalStrategy,
    create_memory_system,
)

# Structured Feedback Loop with LLM-as-Judge
from .feedback_loop import (
    AgentFeedbackLoop,
    LLMJudge,
    FeedbackRecord,
    JudgeEvaluation,
    HumanFeedback,
    OutcomeFeedback,
    DimensionScore,
    QualityRubric,
    FeedbackType,
    QualityDimension,
    OutcomeStatus,
    EscalationLevel,
    create_feedback_loop,
    get_code_fix_rubric,
    get_advisory_rubric,
    CODE_FIX_RUBRIC,
    ADVISORY_RUBRIC,
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

    # ========================================
    # REACT AGENT (Reasoning + Acting)
    # ========================================
    "ReActAgent",
    "ReActStep",
    "ReActThought",
    "ReActAction",
    "ReActObservation",
    "ReActReflection",
    "ReActTrace",
    "ReActStepType",
    "create_thought",
    "create_action",
    "create_reflection",

    # ========================================
    # TREE SEARCH AGENT (Tree-of-Thoughts)
    # ========================================
    "TreeSearchAgent",
    "ThoughtNode",
    "ThoughtPath",
    "ThoughtTree",
    "SearchStrategy",
    "NodeStatus",
    "create_thought_node",

    # ========================================
    # MULTI-LEVEL MEMORY SYSTEM
    # ========================================
    "AgentMemorySystem",
    "MemoryStore",
    "MultiLevelMemoryEntry",
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",
    "WorkingMemory",
    "MultiLevelMemoryType",
    "MemoryPriority",
    "RetrievalStrategy",
    "create_memory_system",

    # ========================================
    # FEEDBACK LOOP (LLM-as-Judge)
    # ========================================
    "AgentFeedbackLoop",
    "LLMJudge",
    "FeedbackRecord",
    "JudgeEvaluation",
    "HumanFeedback",
    "OutcomeFeedback",
    "DimensionScore",
    "QualityRubric",
    "FeedbackType",
    "QualityDimension",
    "OutcomeStatus",
    "EscalationLevel",
    "create_feedback_loop",
    "get_code_fix_rubric",
    "get_advisory_rubric",
    "CODE_FIX_RUBRIC",
    "ADVISORY_RUBRIC",
]
