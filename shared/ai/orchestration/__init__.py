"""
Agent Orchestration Framework
=============================
إطار عمل تنسيق الوكلاء

Multi-agent orchestration framework inspired by Claude-Flow architecture.
Provides intelligent routing, swarm coordination, consensus protocols,
and collective memory for distributed AI agent systems.

إطار تنسيق متعدد الوكلاء مستوحى من هندسة Claude-Flow.
يوفر التوجيه الذكي، وتنسيق السرب، وبروتوكولات الإجماع،
والذاكرة الجماعية لأنظمة وكلاء الذكاء الاصطناعي الموزعة.

Components:
    - router: Q-Learning inspired agent routing
    - swarm: Multi-agent swarm coordination
    - consensus: Distributed consensus protocols
    - memory: Collective memory with LRU cache

المكونات:
    - الموجه: توجيه الوكلاء المستوحى من Q-Learning
    - السرب: تنسيق سرب متعدد الوكلاء
    - الإجماع: بروتوكولات الإجماع الموزع
    - الذاكرة: الذاكرة الجماعية مع ذاكرة LRU

Example:
    >>> from shared.ai.orchestration import (
    ...     AgentRouter,
    ...     SwarmCoordinator,
    ...     MajorityVoting,
    ...     CollectiveMemory,
    ... )
    >>>
    >>> # Create router with Q-Learning
    >>> router = AgentRouter()
    >>> router.register_agent(AgentProfile(
    ...     agent_id="crop_analyzer",
    ...     name="Crop Analyzer",
    ...     name_ar="محلل المحاصيل",
    ...     capabilities=[AgentCapability.CROP_ANALYSIS],
    ... ))
    >>>
    >>> # Route a task
    >>> task = Task(
    ...     description="Analyze wheat health",
    ...     description_ar="تحليل صحة القمح",
    ... )
    >>> decision = await router.route_task(task)
    >>>
    >>> # Or use swarm for distributed execution
    >>> coordinator = SwarmCoordinator()
    >>> result = await coordinator.execute(
    ...     config=SwarmConfig(
    ...         name="Analysis Swarm",
    ...         name_ar="سرب التحليل",
    ...         topology=SwarmTopology.STAR,
    ...     ),
    ...     task=task,
    ... )

Author: SAHOOL Platform Team
Updated: January 2026
"""

__version__ = "1.0.0"

# Models
from .models import (
    # Enums
    AgentCapability,
    ConsensusType,
    MemoryNamespace,
    SwarmTopology,
    TaskPriority,
    TaskStatus,
    # Agent Models
    AgentProfile,
    AgentScore,
    AgentState,
    # Task Models
    Task,
    TaskResult,
    # Swarm Models
    SwarmConfig,
    SwarmResult,
    SwarmState,
    # Consensus Models
    ConsensusResult,
    Vote,
    # Memory Models
    MemoryEntry,
    MemoryStats,
    PatternMatch,
    # Routing Models
    RoutingDecision,
    RouterStats,
)

# Router
from .router import (
    AgentRouter,
    get_router,
    reset_router,
)

# Swarm Coordination
from .swarm import (
    SwarmCoordinator,
    AggregationStrategy,
    MajorityVoteAggregation,
    WeightedAverageAggregation,
    ConcatenateAggregation,
    BestResultAggregation,
    get_swarm_coordinator,
    reset_swarm_coordinator,
)

# Consensus Protocols
from .consensus import (
    ConsensusProtocol,
    MajorityVoting,
    WeightedVoting,
    RaftConsensus,
    UnanimousConsensus,
    QuorumConsensus,
    ConsensusManager,
    get_consensus_manager,
    reach_consensus,
)

# Collective Memory
from .memory import (
    CollectiveMemory,
    LRUCache,
    cosine_similarity,
    jaccard_similarity,
    text_similarity,
    get_collective_memory,
    reset_collective_memory,
)

__all__ = [
    # Version
    "__version__",
    # === Enums ===
    "AgentCapability",
    "ConsensusType",
    "MemoryNamespace",
    "SwarmTopology",
    "TaskPriority",
    "TaskStatus",
    # === Agent Models ===
    "AgentProfile",
    "AgentScore",
    "AgentState",
    # === Task Models ===
    "Task",
    "TaskResult",
    # === Swarm Models ===
    "SwarmConfig",
    "SwarmResult",
    "SwarmState",
    # === Consensus Models ===
    "ConsensusResult",
    "Vote",
    # === Memory Models ===
    "MemoryEntry",
    "MemoryStats",
    "PatternMatch",
    # === Routing Models ===
    "RoutingDecision",
    "RouterStats",
    # === Router ===
    "AgentRouter",
    "get_router",
    "reset_router",
    # === Swarm Coordination ===
    "SwarmCoordinator",
    "AggregationStrategy",
    "MajorityVoteAggregation",
    "WeightedAverageAggregation",
    "ConcatenateAggregation",
    "BestResultAggregation",
    "get_swarm_coordinator",
    "reset_swarm_coordinator",
    # === Consensus Protocols ===
    "ConsensusProtocol",
    "MajorityVoting",
    "WeightedVoting",
    "RaftConsensus",
    "UnanimousConsensus",
    "QuorumConsensus",
    "ConsensusManager",
    "get_consensus_manager",
    "reach_consensus",
    # === Collective Memory ===
    "CollectiveMemory",
    "LRUCache",
    "cosine_similarity",
    "jaccard_similarity",
    "text_similarity",
    "get_collective_memory",
    "reset_collective_memory",
]
