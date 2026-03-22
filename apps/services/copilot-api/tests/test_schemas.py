"""
Tests for Copilot API Pydantic schemas (models/schemas.py)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pydantic import ValidationError

pytestmark = [pytest.mark.unit]


class TestMessageRole:
    def test_all_roles_exist(self):
        from src.models.schemas import MessageRole

        assert MessageRole.SYSTEM == "system"
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.TOOL == "tool"


class TestCopilotMode:
    def test_all_modes_exist(self):
        from src.models.schemas import CopilotMode

        assert CopilotMode.OFFLINE == "offline"
        assert CopilotMode.HYBRID == "hybrid"
        assert CopilotMode.ONLINE == "online"


class TestChatMessage:
    def test_valid_message(self):
        from src.models.schemas import ChatMessage, MessageRole

        msg = ChatMessage(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
        assert msg.name is None
        assert msg.tool_call_id is None

    def test_empty_content_rejected(self):
        from src.models.schemas import ChatMessage, MessageRole

        with pytest.raises(ValidationError):
            ChatMessage(role=MessageRole.USER, content="")

    def test_content_over_max_length_rejected(self):
        from src.models.schemas import ChatMessage, MessageRole

        with pytest.raises(ValidationError):
            ChatMessage(role=MessageRole.USER, content="x" * 50001)

    def test_optional_fields(self):
        from src.models.schemas import ChatMessage, MessageRole

        msg = ChatMessage(role=MessageRole.TOOL, content="result", name="my_tool", tool_call_id="tc_123")
        assert msg.name == "my_tool"
        assert msg.tool_call_id == "tc_123"


class TestChatRequest:
    def test_valid_request(self):
        from src.models.schemas import ChatMessage, ChatRequest, MessageRole

        req = ChatRequest(
            session_id="sess-1",
            messages=[ChatMessage(role=MessageRole.USER, content="Hi")],
        )
        assert req.session_id == "sess-1"
        assert req.allow_tools is True
        assert req.stream is False
        assert req.context is None

    def test_empty_messages_rejected(self):
        from src.models.schemas import ChatRequest

        with pytest.raises(ValidationError):
            ChatRequest(session_id="s", messages=[])

    def test_last_message_must_be_user_or_tool(self):
        from src.models.schemas import ChatMessage, ChatRequest, MessageRole

        with pytest.raises(ValidationError):
            ChatRequest(
                session_id="s",
                messages=[ChatMessage(role=MessageRole.ASSISTANT, content="Hi")],
            )

    def test_last_message_tool_is_allowed(self):
        from src.models.schemas import ChatMessage, ChatRequest, MessageRole

        req = ChatRequest(
            session_id="s",
            messages=[
                ChatMessage(role=MessageRole.USER, content="call tool"),
                ChatMessage(role=MessageRole.TOOL, content="tool result", tool_call_id="tc1"),
            ],
        )
        assert len(req.messages) == 2

    def test_context_dict_accepted(self):
        from src.models.schemas import ChatMessage, ChatRequest, MessageRole

        req = ChatRequest(
            session_id="s",
            messages=[ChatMessage(role=MessageRole.USER, content="q")],
            context={"field_id": "F001"},
        )
        assert req.context["field_id"] == "F001"


class TestToolCallRequest:
    def test_valid_tool_name(self):
        from src.models.schemas import ToolCallRequest

        req = ToolCallRequest(tool="rag.search", args={"query": "test"})
        assert req.tool == "rag.search"

    def test_tool_name_starting_with_number_rejected(self):
        from src.models.schemas import ToolCallRequest

        with pytest.raises(ValidationError):
            ToolCallRequest(tool="1invalid", args={})

    def test_tool_name_with_special_chars_rejected(self):
        from src.models.schemas import ToolCallRequest

        with pytest.raises(ValidationError):
            ToolCallRequest(tool="tool@name", args={})

    def test_empty_tool_name_rejected(self):
        from src.models.schemas import ToolCallRequest

        with pytest.raises(ValidationError):
            ToolCallRequest(tool="", args={})

    def test_tool_name_underscores_and_dots_allowed(self):
        from src.models.schemas import ToolCallRequest

        req = ToolCallRequest(tool="code.analyze_fix", args={})
        assert req.tool == "code.analyze_fix"

    def test_default_args_empty_dict(self):
        from src.models.schemas import ToolCallRequest

        req = ToolCallRequest(tool="rag.list")
        assert req.args == {}

    def test_session_id_optional(self):
        from src.models.schemas import ToolCallRequest

        req = ToolCallRequest(tool="rag.list")
        assert req.session_id is None


class TestToolCallResponse:
    def test_success_response(self):
        from src.models.schemas import ToolCallResponse

        resp = ToolCallResponse(
            tool="rag.search",
            success=True,
            result=[{"id": "1"}],
            execution_time_ms=12.5,
        )
        assert resp.success is True
        assert resp.error is None

    def test_failure_response(self):
        from src.models.schemas import ToolCallResponse

        resp = ToolCallResponse(
            tool="rag.search",
            success=False,
            error="Connection failed",
            execution_time_ms=5.0,
        )
        assert resp.success is False
        assert resp.error == "Connection failed"


class TestGuardDecision:
    def test_allowed_decision(self):
        from src.models.schemas import GuardDecision

        d = GuardDecision(allowed=True, reason="Allowed")
        assert d.allowed is True

    def test_blocked_decision_with_details(self):
        from src.models.schemas import GuardDecision

        d = GuardDecision(allowed=False, reason="Blocked", details={"layer": "allowlist"})
        assert d.details["layer"] == "allowlist"


class TestRAGDocument:
    def test_basic_creation(self):
        from src.models.schemas import RAGDocument

        doc = RAGDocument(id="d1", text="hello")
        assert doc.id == "d1"
        assert doc.text_ar is None
        assert doc.metadata == {}
        assert doc.embedding is None

    def test_with_arabic_text(self):
        from src.models.schemas import RAGDocument

        doc = RAGDocument(id="d2", text="hello", text_ar="مرحبا")
        assert doc.text_ar == "مرحبا"


class TestRAGSearchResult:
    def test_creation(self):
        from src.models.schemas import RAGSearchResult

        result = RAGSearchResult(
            documents=[], query="test", total_found=0, search_time_ms=1.0
        )
        assert result.total_found == 0


class TestHealthResponse:
    def test_defaults(self):
        from src.models.schemas import HealthResponse

        hr = HealthResponse()
        assert hr.status == "ok"
        assert hr.service == "copilot-api"
        assert hr.version == "16.0.0"
        assert hr.components == {}

    def test_with_components(self):
        from src.models.schemas import HealthResponse

        hr = HealthResponse(components={"rag": True, "nats": False})
        assert hr.components["rag"] is True
        assert hr.components["nats"] is False


class TestChatResponse:
    def test_creation(self):
        from src.models.schemas import ChatMessage, ChatResponse, CopilotMode, MessageRole

        resp = ChatResponse(
            session_id="s1",
            mode=CopilotMode.HYBRID,
            message=ChatMessage(role=MessageRole.ASSISTANT, content="reply"),
        )
        assert resp.mode == CopilotMode.HYBRID
        assert resp.rag_context is None
        assert resp.tool_calls is None
        assert resp.usage is None
        assert resp.timestamp is not None
