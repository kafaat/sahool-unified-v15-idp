"""
Multi-Agent Infrastructure Module
وحدة البنية التحتية للوكلاء المتعددين

Provides communication and coordination infrastructure for the multi-agent system.
توفر البنية التحتية للاتصال والتنسيق لنظام الوكلاء المتعددين.
"""

from .nats_bridge import (
    AgentNATSBridge,
    AgentMessage,
    MessageType,
    MessagePriority,
)

from .shared_context import (
    FarmContext,
    SharedContextStore,
    SoilAnalysis,
    WeatherData,
    SatelliteIndices,
    FarmAction,
    Issue,
    get_shared_context_store,
)

from .registry_client import (
    AgentCard,
    AgentCapability,
    AgentStatus,
    AgentRegistryClient,
)

__all__ = [
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
]
