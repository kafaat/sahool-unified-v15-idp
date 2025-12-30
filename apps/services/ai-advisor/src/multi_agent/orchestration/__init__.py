"""
Multi-Agent Orchestration Module
وحدة تنسيق الوكلاء المتعددين

Central orchestration components for SAHOOL multi-agent system.
مكونات التنسيق المركزية لنظام SAHOOL متعدد الوكلاء.
"""

from .master_advisor import (
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
)

from .council_manager import (
    CouncilManager,
    CouncilType,
    CouncilDecision,
    AgentOpinion,
    Conflict,
)

from .consensus_engine import (
    ConsensusEngine,
    ConsensusStrategy,
)

__all__ = [
    # Main orchestrator | المنسق الرئيسي
    "MasterAdvisor",

    # Supporting components | المكونات الداعمة
    "AgentRegistry",
    "NATSBridge",
    "ContextStore",

    # Council and Consensus | المجلس والإجماع
    "CouncilManager",
    "ConsensusEngine",

    # Enums | التعدادات
    "QueryType",
    "ExecutionMode",
    "CouncilType",
    "ConsensusStrategy",

    # Data models | نماذج البيانات
    "FarmerQuery",
    "QueryAnalysis",
    "AgentResponse",
    "AdvisoryResponse",
    "CouncilDecision",
    "AgentOpinion",
    "Conflict",
]
