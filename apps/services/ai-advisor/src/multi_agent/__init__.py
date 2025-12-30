"""
Multi-Agent System Module
وحدة نظام الوكلاء المتعددين

Implements a multi-agent system for collaborative agricultural intelligence.
ينفذ نظام وكلاء متعددين للذكاء الزراعي التعاوني.
"""

from .infrastructure import (
    AgentNATSBridge,
    AgentMessage,
    MessageType,
    MessagePriority,
    FarmContext,
    SharedContextStore,
    SoilAnalysis,
    WeatherData,
    SatelliteIndices,
    FarmAction,
    Issue,
    get_shared_context_store,
    AgentCard,
    AgentCapability,
    AgentStatus,
    AgentRegistryClient,
)

from .orchestration import (
    MasterAdvisor,
    AgentRegistry,
    NATSBridge,
    ContextStore,
    QueryType,
    ExecutionMode,
    FarmerQuery,
    QueryAnalysis,
    AgentResponse,
    AdvisoryResponse,
    CouncilManager,
    CouncilType,
    CouncilDecision,
    AgentOpinion,
    Conflict,
    ConsensusEngine,
    ConsensusStrategy,
)

__all__ = [
    # Infrastructure components | مكونات البنية التحتية
    "AgentNATSBridge",
    "AgentMessage",
    "MessageType",
    "MessagePriority",
    "FarmContext",
    "SharedContextStore",
    "SoilAnalysis",
    "WeatherData",
    "SatelliteIndices",
    "FarmAction",
    "Issue",
    "get_shared_context_store",
    "AgentCard",
    "AgentCapability",
    "AgentStatus",
    "AgentRegistryClient",

    # Orchestration components | مكونات التنسيق
    "MasterAdvisor",
    "AgentRegistry",
    "NATSBridge",
    "ContextStore",
    "QueryType",
    "ExecutionMode",
    "FarmerQuery",
    "QueryAnalysis",
    "AgentResponse",
    "AdvisoryResponse",

    # Council and Consensus | المجلس والإجماع
    "CouncilManager",
    "CouncilType",
    "CouncilDecision",
    "AgentOpinion",
    "Conflict",
    "ConsensusEngine",
    "ConsensusStrategy",
]
