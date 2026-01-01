"""
Unit Tests for BaseAgent
اختبارات الوحدة للوكيل الأساسي
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# Import after mocking to prevent initialization issues
@pytest.fixture
def base_agent_class(mock_env_vars):
    """Import BaseAgent with mocked environment"""
    with patch("src.agents.base_agent.ChatAnthropic") as mock_claude:
        mock_llm = AsyncMock()
        mock_claude.return_value = mock_llm

        from src.agents.base_agent import BaseAgent

        return BaseAgent


class TestBaseAgent:
    """Test suite for BaseAgent class"""

    def test_agent_initialization(self, base_agent_class, mock_knowledge_retriever):
        """Test agent initialization with required parameters"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "You are a test agent."

        agent = TestAgent(
            name="TestAgent",
            role="Testing Assistant",
            tools=[],
            retriever=mock_knowledge_retriever,
        )

        assert agent.name == "TestAgent"
        assert agent.role == "Testing Assistant"
        assert agent.retriever is mock_knowledge_retriever
        assert len(agent.conversation_history) == 0

    def test_retrieve_context_with_retriever(
        self, base_agent_class, mock_knowledge_retriever
    ):
        """Test context retrieval from RAG system"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "Test prompt"

        agent = TestAgent(
            name="TestAgent", role="Testing", retriever=mock_knowledge_retriever
        )

        context = agent._retrieve_context("wheat farming")

        assert "Agricultural knowledge 1" in context
        assert "Agricultural knowledge 2" in context
        mock_knowledge_retriever.retrieve.assert_called_once()

    def test_retrieve_context_without_retriever(self, base_agent_class):
        """Test context retrieval when no retriever is available"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "Test prompt"

        agent = TestAgent(name="TestAgent", role="Testing", retriever=None)

        context = agent._retrieve_context("wheat farming")

        assert context == ""

    @pytest.mark.asyncio
    async def test_think_basic_query(self, base_agent_class, mock_anthropic_client):
        """Test basic query processing"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "You are a helpful agricultural assistant."

        with patch("src.agents.base_agent.ChatAnthropic") as mock_claude:
            mock_llm = AsyncMock()
            mock_response = AIMessage(content="Wheat should be planted in autumn.")
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_claude.return_value = mock_llm

            agent = TestAgent(
                name="TestAgent", role="Agricultural Advisor", retriever=None
            )

            result = await agent.think(
                query="When should I plant wheat?", use_rag=False
            )

            assert result["agent"] == "TestAgent"
            assert result["role"] == "Agricultural Advisor"
            assert "Wheat should be planted in autumn" in result["response"]
            assert "confidence" in result
            assert 0 <= result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_think_with_rag(self, base_agent_class, mock_knowledge_retriever):
        """Test query processing with RAG retrieval"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "You are a helpful assistant."

        with patch("src.agents.base_agent.ChatAnthropic") as mock_claude:
            mock_llm = AsyncMock()
            mock_response = AIMessage(content="Based on agricultural knowledge...")
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_claude.return_value = mock_llm

            agent = TestAgent(
                name="TestAgent", role="Advisor", retriever=mock_knowledge_retriever
            )

            result = await agent.think(query="How to control pests?", use_rag=True)

            assert result["agent"] == "TestAgent"
            mock_knowledge_retriever.retrieve.assert_called_once()

    def test_format_context(self, base_agent_class):
        """Test context dictionary formatting"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "Test"

        agent = TestAgent(name="Test", role="Test")

        context = {
            "field_id": "field-123",
            "crop_type": "wheat",
            "data": {"temp": 25, "humidity": 60},
        }

        formatted = agent._format_context(context)

        assert "field_id: field-123" in formatted
        assert "crop_type: wheat" in formatted
        assert "temp" in formatted

    def test_calculate_confidence_high(self, base_agent_class):
        """Test confidence calculation for high-confidence responses"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "Test"

        agent = TestAgent(name="Test", role="Test")

        response = AIMessage(content="The answer is definitely yes.")
        confidence = agent._calculate_confidence(response)

        assert confidence >= 0.7

    def test_calculate_confidence_low(self, base_agent_class):
        """Test confidence calculation for uncertain responses"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "Test"

        agent = TestAgent(name="Test", role="Test")

        response = AIMessage(content="I'm not sure, maybe it could be possible.")
        confidence = agent._calculate_confidence(response)

        assert confidence < 0.8

    def test_reset_conversation(self, base_agent_class):
        """Test conversation history reset"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "Test"

        agent = TestAgent(name="Test", role="Test")

        # Add some conversation history
        agent.conversation_history = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there"),
        ]

        assert len(agent.conversation_history) == 2

        agent.reset_conversation()

        assert len(agent.conversation_history) == 0

    def test_get_info(self, base_agent_class, mock_knowledge_retriever):
        """Test agent information retrieval"""

        class TestAgent(base_agent_class):
            def get_system_prompt(self) -> str:
                return "Test"

        mock_tool = Mock()
        mock_tool.name = "test_tool"

        agent = TestAgent(
            name="TestAgent",
            role="Testing",
            tools=[mock_tool],
            retriever=mock_knowledge_retriever,
        )

        info = agent.get_info()

        assert info["name"] == "TestAgent"
        assert info["role"] == "Testing"
        assert "test_tool" in info["tools"]
        assert info["has_rag"] is True
        assert info["conversation_length"] == 0
