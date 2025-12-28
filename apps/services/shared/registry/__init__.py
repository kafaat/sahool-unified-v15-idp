"""
SAHOOL Agent Registry Package
حزمة سجل وكلاء سهول

Agent-to-Agent (A2A) Protocol Implementation
تطبيق بروتوكول الوكيل-إلى-وكيل

This package provides a comprehensive agent registry system following
the A2A protocol specifications for agent discovery, invocation, and management.

توفر هذه الحزمة نظام سجل شامل للوكلاء يتبع
مواصفات بروتوكول A2A لاكتشاف الوكلاء واستدعائهم وإدارتهم.
"""

from .agent_card import (
    AgentCard,
    AgentCapability,
    AgentSkill,
    SecurityScheme,
    InputMode,
    OutputMode,
    AgentMetadata,
    AgentEndpoint,
)

from .registry import (
    AgentRegistry,
    RegistryConfig,
    HealthStatus,
)

from .client import (
    RegistryClient,
    AgentInvocationRequest,
    AgentInvocationResponse,
)

__version__ = "1.0.0"
__all__ = [
    # Agent Card models
    "AgentCard",
    "AgentCapability",
    "AgentSkill",
    "SecurityScheme",
    "InputMode",
    "OutputMode",
    "AgentMetadata",
    "AgentEndpoint",
    # Registry
    "AgentRegistry",
    "RegistryConfig",
    "HealthStatus",
    # Client
    "RegistryClient",
    "AgentInvocationRequest",
    "AgentInvocationResponse",
]
