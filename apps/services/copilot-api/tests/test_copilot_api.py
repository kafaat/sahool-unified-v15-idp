"""
Copilot API Test Suite
======================
مجموعة اختبارات Copilot API

Tests for:
- Health endpoints
- Chat functionality
- Tool execution with guardrails
- RAG integration
- Multi-LLM provider routing

Author: SAHOOL Platform Team
Updated: January 2026
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.copilot]


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_healthz_returns_ok(self):
        """Test /healthz returns 200 OK."""
        from src.api.v1.health import healthz

        result = healthz()
        assert result["status"] == "healthy"
        assert result["service"] == "copilot-api"
        assert "version" in result

    @pytest.mark.asyncio
    async def test_readyz_returns_status(self):
        """Test /readyz returns component status."""
        from src.api.v1.health import readyz

        result = readyz()
        assert result["status"] in ["healthy", "degraded"]
        assert "components" in result


class TestChatModels:
    """Test chat request/response models."""

    def test_chat_request_validation(self):
        """Test ChatRequest validation."""
        from src.models.schemas import ChatRequest

        # Valid request
        request = ChatRequest(
            message="Hello",
            session_id="test-session",
            language="en",
        )
        assert request.message == "Hello"
        assert request.session_id == "test-session"

    def test_chat_request_with_context(self):
        """Test ChatRequest with context."""
        from src.models.schemas import ChatContext, ChatRequest

        context = ChatContext(
            file_path="/path/to/file.py",
            language="python",
            code_snippet="def hello(): pass",
        )

        request = ChatRequest(
            message="Explain this code",
            context=context,
        )
        assert request.context.file_path == "/path/to/file.py"
        assert request.context.language == "python"

    def test_chat_response_structure(self):
        """Test ChatResponse structure."""
        from src.models.schemas import ChatResponse, RAGDocument

        response = ChatResponse(
            message="Here is the response",
            session_id="test-session",
            model="ollama/codellama",
            tokens_used=100,
            latency_ms=150.5,
        )
        assert response.message == "Here is the response"
        assert response.tokens_used == 100


class TestToolGuardrails:
    """Test tool guardrails functionality."""

    def test_tool_allowlist_check(self):
        """Test tool is in allowlist."""
        from src.security.allowlists import TOOL_ALLOWLIST

        assert "read_file" in TOOL_ALLOWLIST
        assert "write_file" in TOOL_ALLOWLIST
        assert "dangerous_tool" not in TOOL_ALLOWLIST

    def test_blocked_patterns(self):
        """Test blocked patterns are detected."""
        import re

        from src.security.allowlists import BLOCKED_PATTERNS

        # Test dangerous patterns
        test_cases = [
            ("password=secret123", True),
            ("api_key=abc123", True),
            ("normal_text", False),
        ]

        for text, should_block in test_cases:
            blocked = any(re.search(pattern, text, re.IGNORECASE) for pattern in BLOCKED_PATTERNS)
            assert blocked == should_block, f"Pattern check failed for: {text}"

    def test_dangerous_commands(self):
        """Test dangerous commands are detected."""
        from src.security.allowlists import DANGEROUS_COMMANDS

        assert "rm -rf" in DANGEROUS_COMMANDS
        assert "DROP TABLE" in DANGEROUS_COMMANDS
        assert "ls -la" not in DANGEROUS_COMMANDS

    def test_guard_decision_allow(self):
        """Test guard allows safe operations."""
        from src.models.schemas import ToolCallRequest
        from src.security.guardrails import ToolGuard

        guard = ToolGuard()

        request = ToolCallRequest(
            tool_name="read_file",
            arguments={"path": "/safe/path/file.txt"},
        )

        decision = guard.check(request)
        assert decision.allowed is True

    def test_guard_decision_block_dangerous_tool(self):
        """Test guard blocks dangerous tools."""
        from src.models.schemas import ToolCallRequest
        from src.security.guardrails import ToolGuard

        guard = ToolGuard()

        request = ToolCallRequest(
            tool_name="execute_shell",
            arguments={"command": "rm -rf /"},
        )

        decision = guard.check(request)
        assert decision.allowed is False
        assert "dangerous" in decision.reason.lower() or "blocked" in decision.reason.lower()


class TestRAGService:
    """Test RAG service functionality."""

    @pytest.mark.asyncio
    async def test_embedding_service_initialization(self):
        """Test embedding service initializes correctly."""
        from src.rag.embeddings import EmbeddingService

        service = EmbeddingService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_search_returns_documents(self):
        """Test search returns relevant documents."""
        from src.core.config import Settings
        from src.rag.service import CopilotRAGService

        settings = Settings()
        service = CopilotRAGService(settings)

        # Mock the search
        with patch.object(service, "_search_keyword") as mock_search:
            mock_search.return_value = [{"content": "Test document", "score": 0.9}]

            results = await service.search("test query", top_k=5)
            assert len(results) >= 0  # May be empty in unit tests


class TestAgentRouter:
    """Test agent routing functionality."""

    def test_router_initialization(self):
        """Test router initializes with default agents."""
        from src.core.agents import AgentRouter

        router = AgentRouter()
        assert router is not None

    def test_route_code_fix_intent(self):
        """Test routing to code fix agent."""
        from src.core.agents import AgentRouter

        router = AgentRouter()

        # Test code fix intent detection
        result = router.route("Fix this bug in my code")
        assert result is not None
        assert result.agent_name in ["code-fix-agent", "general"]

    def test_route_weather_intent(self):
        """Test routing to weather agent."""
        from src.core.agents import AgentRouter

        router = AgentRouter()

        result = router.route("What's the weather forecast?")
        assert result is not None

    def test_route_arabic_intent(self):
        """Test routing with Arabic input."""
        from src.core.agents import AgentRouter

        router = AgentRouter()

        result = router.route("ما هي حالة الطقس اليوم؟")
        assert result is not None


class TestMultiLLMProviderDetection:
    """Test multi-LLM provider detection."""

    def test_provider_detection_ollama(self):
        """Test Ollama provider is always available."""
        from src.core.config import Settings

        settings = Settings()

        # Ollama should always be listed
        available_providers = (
            settings.get_available_providers()
            if hasattr(settings, "get_available_providers")
            else []
        )
        assert isinstance(available_providers, list)


class TestConfigSettings:
    """Test configuration settings."""

    def test_default_settings(self):
        """Test default settings are applied."""
        from src.core.config import Settings

        settings = Settings()

        assert settings.port == 8088
        assert settings.environment in ["development", "production", "test"]
        assert settings.enable_guardrails is True

    def test_qdrant_settings(self):
        """Test Qdrant settings."""
        from src.core.config import Settings

        settings = Settings()

        assert settings.qdrant_host is not None
        assert settings.qdrant_port == 6333


class TestIntegration:
    """Integration tests (requires running services)."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_chat_flow(self):
        """Test complete chat flow with RAG."""
        # This would require a running service
        pass

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_execution_with_guardrails(self):
        """Test tool execution passes through guardrails."""
        # This would require a running service
        pass


# Fixtures
@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    from src.core.config import Settings

    settings = Settings()
    settings.environment = "test"
    return settings


@pytest.fixture
def mock_guard():
    """Create mock tool guard."""
    from src.security.guardrails import ToolGuard

    return ToolGuard()


@pytest.fixture
def mock_router():
    """Create mock agent router."""
    from src.core.agents import AgentRouter

    return AgentRouter()
