"""
Copilot API Schemas
مخططات بيانات Copilot API

Pydantic models for request/response validation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from ..core.config import SERVICE_VERSION


class MessageRole(StrEnum):
    """Message roles | أدوار الرسائل"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class CopilotMode(StrEnum):
    """Copilot operation mode | وضع تشغيل Copilot"""

    OFFLINE = "offline"
    HYBRID = "hybrid"
    ONLINE = "online"


class ChatMessage(BaseModel):
    """Single chat message | رسالة محادثة واحدة"""

    role: MessageRole
    content: str = Field(..., min_length=1, max_length=50000)
    name: str | None = None
    tool_call_id: str | None = None

    model_config = {"json_schema_extra": {"example": {"role": "user", "content": "ما هي حالة الحقول اليوم؟"}}}


class ChatRequest(BaseModel):
    """Chat request payload | حمولة طلب المحادثة"""

    session_id: str = Field(..., description="Client-side session identifier")
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=100)
    allow_tools: bool = Field(default=True, description="Allow tool calls")
    stream: bool = Field(default=False, description="Stream response")
    context: dict[str, Any] | None = Field(default=None, description="Additional context")

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: list[ChatMessage]) -> list[ChatMessage]:
        """Validate message sequence"""
        if not v:
            raise ValueError("At least one message is required")
        # Last message should typically be from user
        if v[-1].role not in (MessageRole.USER, MessageRole.TOOL):
            raise ValueError("Last message should be from user or tool")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session-abc-123",
                "messages": [{"role": "user", "content": "مرحبا، ما هي خدماتك؟"}],
                "allow_tools": True,
            }
        }
    }


class ChatResponse(BaseModel):
    """Chat response payload | حمولة رد المحادثة"""

    session_id: str
    mode: CopilotMode
    message: ChatMessage
    rag_context: list[dict[str, Any]] | None = None
    tool_calls: list[dict[str, Any]] | None = None
    usage: dict[str, int] | None = None
    intent: str | None = None
    sources: list[dict] = Field(default_factory=list)
    services_used: list[str] = Field(default_factory=list)
    confidence: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session-abc-123",
                "mode": "offline",
                "message": {"role": "assistant", "content": "مرحباً! أنا مساعد سهول الذكي..."},
                "timestamp": "2026-01-29T10:30:00Z",
            }
        }
    }


class UnifiedQueryRequest(BaseModel):
    """Unified query from any channel (Phase 2) | استعلام موحد من أي قناة"""

    message: str
    channel: str = "web"  # whatsapp | ussd | wechat | web | mobile
    field_id: str | None = None
    tenant_id: str | None = None
    language: str = "ar"
    image_base64: str | None = None
    location: dict | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "ما حالة حقل القمح؟",
                "channel": "mobile",
                "field_id": "FIELD-003",
                "language": "ar",
            }
        }
    }


class ToolCallRequest(BaseModel):
    """Tool call request | طلب استدعاء أداة"""

    tool: str = Field(..., description="Tool identifier (e.g., 'rag.search')")
    args: dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    session_id: str | None = None

    @field_validator("tool")
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """Validate tool name format"""
        if not v or len(v) > 100:
            raise ValueError("Invalid tool name")
        # Allow alphanumeric, dots, underscores
        import re

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9._]*$", v):
            raise ValueError("Tool name must start with letter and contain only alphanumeric, dots, underscores")
        return v

    model_config = {
        "json_schema_extra": {"example": {"tool": "rag.search", "args": {"query": "irrigation schedule", "k": 5}}}
    }


class ToolCallResponse(BaseModel):
    """Tool call response | رد استدعاء أداة"""

    tool: str
    success: bool
    result: Any | None = None
    error: str | None = None
    execution_time_ms: float

    model_config = {
        "json_schema_extra": {
            "example": {
                "tool": "rag.search",
                "success": True,
                "result": [{"id": "doc-1", "text": "..."}],
                "execution_time_ms": 45.2,
            }
        }
    }


class GuardDecision(BaseModel):
    """Guard decision result | نتيجة قرار الحماية"""

    allowed: bool
    reason: str
    details: dict[str, Any] | None = None

    model_config = {"json_schema_extra": {"example": {"allowed": True, "reason": "Tool is in allowlist"}}}


class RAGDocument(BaseModel):
    """RAG document | وثيقة RAG"""

    id: str
    text: str
    text_ar: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "doc-irrigation-001",
                "text": "Wheat irrigation schedule...",
                "text_ar": "جدول ري القمح...",
                "metadata": {"category": "irrigation", "crop": "wheat"},
            }
        }
    }


class RAGSearchResult(BaseModel):
    """RAG search result | نتيجة بحث RAG"""

    documents: list[RAGDocument]
    query: str
    total_found: int
    search_time_ms: float

    model_config = {
        "json_schema_extra": {
            "example": {
                "documents": [],
                "query": "irrigation",
                "total_found": 5,
                "search_time_ms": 23.5,
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response | رد فحص الصحة"""

    status: str = "ok"
    service: str = "copilot-api"
    version: str = SERVICE_VERSION
    mode: CopilotMode = CopilotMode.OFFLINE
    components: dict[str, bool] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "service": "copilot-api",
                "version": "1.0.0",
                "mode": "offline",
                "components": {"qdrant": True, "redis": True, "nats": True},
            }
        }
    }
