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
from .base import (
    # Data classes
    AgentCapability,
    # Enums
    AgentMode,
    AgentState,
    AgentStep,
    AgentTool,
    # Base agent class
    BaseAutonomousAgent,
    CollaborationRole,
    ConsensusProposal,
    ConsensusType,
    DelegatedTask,
    HelpRequest,
    MemoryEntry,
    MemoryType,
    StepResult,
    ToolResult,
)

# Farm advisor with specialized sub-agents
from .farm_advisor import (
    CollaborativeDecision,
    FarmAdvisorAgent,
    FarmContext,
    FertilizerSubAgent,
    HarvestPlannerSubAgent,
    # Specialized sub-agents
    IrrigationSubAgent,
    PestControlSubAgent,
)

# Structured Feedback Loop with LLM-as-Judge
from .feedback_loop import (
    ADVISORY_RUBRIC,
    CODE_FIX_RUBRIC,
    AgentFeedbackLoop,
    DimensionScore,
    EscalationLevel,
    FeedbackRecord,
    FeedbackType,
    HumanFeedback,
    JudgeEvaluation,
    LLMJudge,
    OutcomeFeedback,
    OutcomeStatus,
    QualityDimension,
    QualityRubric,
    create_feedback_loop,
    get_advisory_rubric,
    get_code_fix_rubric,
)

# Multi-level Memory System
from .memory_system import (
    AgentMemorySystem,
    EpisodicMemory,
    MemoryPriority,
    MemoryStore,
    ProceduralMemory,
    RetrievalStrategy,
    SemanticMemory,
    WorkingMemory,
    create_memory_system,
)
from .memory_system import (
    MemoryEntry as MultiLevelMemoryEntry,
)
from .memory_system import (
    MemoryType as MultiLevelMemoryType,
)

# Planner with seasonal and collaborative features
from .planner import (
    # Collaborative planning
    CollaborativePlan,
    ExecutionPlan,
    PlannerAgent,
    ResourceAllocation,
    RiskAssessment,
    # Risk assessment
    RiskCategory,
    # Seasonal planning
    Season,
    SeasonalPlan,
)

# ReAct Agent - Reasoning + Acting pattern
from .react_agent import (
    ReActAction,
    ReActAgent,
    ReActObservation,
    ReActReflection,
    ReActStep,
    ReActStepType,
    ReActThought,
    ReActTrace,
    create_action,
    create_reflection,
    # Helper functions
    create_thought,
)

# Tree Search Agent - Tree-of-Thoughts pattern
from .tree_search_agent import (
    NodeStatus,
    SearchStrategy,
    ThoughtNode,
    ThoughtPath,
    ThoughtTree,
    TreeSearchAgent,
    create_thought_node,
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
