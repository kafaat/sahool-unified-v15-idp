"""
Agent-to-Agent (A2A) Protocol Implementation
تطبيق بروتوكول Agent-to-Agent

Implements the Linux Foundation A2A specification for agent communication.
ينفذ مواصفات Linux Foundation A2A لاتصال الوكلاء.

This package provides:
- Protocol message types and state management
- Base agent class with agent card generation
- Client for discovering and communicating with agents
- Server implementation with FastAPI and WebSocket support

يوفر هذا الحزمة:
- أنواع رسائل البروتوكول وإدارة الحالة
- فئة الوكيل الأساسية مع توليد بطاقة الوكيل
- العميل لاكتشاف والتواصل مع الوكلاء
- تنفيذ الخادم مع FastAPI ودعم WebSocket
"""

from .protocol import (
    A2AMessage,
    TaskMessage,
    TaskResultMessage,
    ErrorMessage,
    TaskState,
    ConversationContext,
)

from .agent import (
    A2AAgent,
    AgentCard,
    AgentCapability,
)

from .client import (
    A2AClient,
    AgentDiscovery,
)

from .server import (
    A2AServer,
    create_a2a_router,
)

__all__ = [
    # Protocol
    "A2AMessage",
    "TaskMessage",
    "TaskResultMessage",
    "ErrorMessage",
    "TaskState",
    "ConversationContext",
    # Agent
    "A2AAgent",
    "AgentCard",
    "AgentCapability",
    # Client
    "A2AClient",
    "AgentDiscovery",
    # Server
    "A2AServer",
    "create_a2a_router",
]

__version__ = "1.0.0"
