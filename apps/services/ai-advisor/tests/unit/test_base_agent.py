"""
Unit Tests for Base Agent
اختبارات الوحدة للوكيل الأساسي

Tests the base agent functionality including:
- Agent initialization
- RAG integration
- Conversation management
- Tool usage
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage, AIMessage


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing"""

    def get_system_prompt(self) -> str:
        return "You are a test agricultural advisor."


class TestBaseAgent:
    """Test suite for BaseAgent class"""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Agricultural Advisor",
            tools=[],
            retriever=None
        )

        assert agent.name == "test_agent"
        assert agent.role == "Test Agricultural Advisor"
        assert agent.tools == []
        assert agent.retriever is None
        assert agent.conversation_history == []
        assert agent.llm is not None

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_get_system_prompt(self):
        """Test get_system_prompt returns correct prompt"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
        )

        prompt = agent.get_system_prompt()
        assert prompt == "You are a test agricultural advisor."

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_retrieve_context_without_retriever(self):
        """Test context retrieval without RAG retriever"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
            retriever=None
        )

        context = agent._retrieve_context("test query")
        assert context == ""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_retrieve_context_with_retriever(self, mock_knowledge_retriever):
        """Test context retrieval with RAG retriever"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
            retriever=mock_knowledge_retriever
        )

        context = agent._retrieve_context("wheat fertilizer")
        assert "nitrogen" in context.lower()
        assert mock_knowledge_retriever.retrieve.called

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_retrieve_context_handles_error(self):
        """Test context retrieval handles errors gracefully"""
        mock_retriever = MagicMock()
        mock_retriever.retrieve.side_effect = Exception("RAG error")

        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
            retriever=mock_retriever
        )

        context = agent._retrieve_context("test query")
        assert context == ""

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_think_basic(self, mock_anthropic_client):
        """Test basic think functionality"""
        with patch("agents.base_agent.ChatAnthropic") as mock_class:
            mock_llm = AsyncMock()
            mock_llm.ainvoke = AsyncMock(return_value=AIMessage(
                content="I recommend using nitrogen fertilizer."
            ))
            mock_class.return_value = mock_llm

            agent = ConcreteAgent(
                name="test_agent",
                role="Test Advisor"
            )

            response = await agent.think(
                query="What fertilizer for wheat?",
                use_rag=False
            )

            assert response["agent"] == "test_agent"
            assert response["role"] == "Test Advisor"
            assert "nitrogen" in response["response"].lower()
            assert 0 <= response["confidence"] <= 1
            assert len(agent.conversation_history) == 2  # User message + AI response

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_think_with_rag(self, mock_knowledge_retriever):
        """Test think with RAG context"""
        with patch("agents.base_agent.ChatAnthropic") as mock_class:
            mock_llm = AsyncMock()
            mock_llm.ainvoke = AsyncMock(return_value=AIMessage(
                content="Based on the knowledge base, use NPK fertilizer."
            ))
            mock_class.return_value = mock_llm

            agent = ConcreteAgent(
                name="test_agent",
                role="Test Advisor",
                retriever=mock_knowledge_retriever
            )

            response = await agent.think(
                query="What fertilizer for wheat?",
                use_rag=True
            )

            assert response["agent"] == "test_agent"
            assert "fertilizer" in response["response"].lower()
            assert mock_knowledge_retriever.retrieve.called

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_think_with_context(self):
        """Test think with additional context"""
        with patch("agents.base_agent.ChatAnthropic") as mock_class:
            mock_llm = AsyncMock()
            mock_llm.ainvoke = AsyncMock(return_value=AIMessage(
                content="For clay soil, use slow-release fertilizer."
            ))
            mock_class.return_value = mock_llm

            agent = ConcreteAgent(
                name="test_agent",
                role="Test Advisor"
            )

            context = {
                "soil_type": "clay",
                "crop": "wheat",
                "stage": "tillering"
            }

            response = await agent.think(
                query="What fertilizer?",
                context=context,
                use_rag=False
            )

            assert response["agent"] == "test_agent"
            assert mock_llm.ainvoke.called

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_think_handles_error(self):
        """Test think handles LLM errors"""
        with patch("agents.base_agent.ChatAnthropic") as mock_class:
            mock_llm = AsyncMock()
            mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM API error"))
            mock_class.return_value = mock_llm

            agent = ConcreteAgent(
                name="test_agent",
                role="Test Advisor"
            )

            with pytest.raises(Exception) as exc_info:
                await agent.think(query="test", use_rag=False)

            assert "LLM API error" in str(exc_info.value)

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_format_context_simple(self):
        """Test context formatting with simple data"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor"
        )

        context = {
            "temperature": 25,
            "humidity": 0.6,
            "location": "field_001"
        }

        formatted = agent._format_context(context)
        assert "temperature: 25" in formatted
        assert "humidity: 0.6" in formatted
        assert "location: field_001" in formatted

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_format_context_complex(self):
        """Test context formatting with complex nested data"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor"
        )

        context = {
            "weather": {"temp": 25, "humidity": 0.6},
            "crops": ["wheat", "corn"],
        }

        formatted = agent._format_context(context)
        assert "weather:" in formatted
        assert "crops:" in formatted

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_calculate_confidence_high(self):
        """Test confidence calculation for certain response"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor"
        )

        response = AIMessage(content="I recommend using nitrogen fertilizer at 100 kg/ha.")
        confidence = agent._calculate_confidence(response)

        assert confidence == 0.8  # Default high confidence

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_calculate_confidence_low(self):
        """Test confidence calculation for uncertain response"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor"
        )

        response = AIMessage(content="I'm not sure, but maybe nitrogen might help.")
        confidence = agent._calculate_confidence(response)

        assert confidence < 0.8  # Lower confidence due to uncertainty markers

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_use_tool_success(self):
        """Test successful tool execution"""
        mock_tool = MagicMock()
        mock_tool.name = "weather_tool"
        mock_tool.arun = AsyncMock(return_value={"temp": 25})

        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
            tools=[mock_tool]
        )

        result = await agent.use_tool("weather_tool", location="field_001")

        assert result == {"temp": 25}
        assert mock_tool.arun.called

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_use_tool_not_found(self):
        """Test tool execution when tool doesn't exist"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
            tools=[]
        )

        with pytest.raises(ValueError) as exc_info:
            await agent.use_tool("nonexistent_tool")

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_use_tool_execution_error(self):
        """Test tool execution when tool fails"""
        mock_tool = MagicMock()
        mock_tool.name = "failing_tool"
        mock_tool.arun = AsyncMock(side_effect=Exception("Tool failed"))

        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
            tools=[mock_tool]
        )

        with pytest.raises(Exception) as exc_info:
            await agent.use_tool("failing_tool")

        assert "Tool failed" in str(exc_info.value)

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_reset_conversation(self):
        """Test conversation history reset"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor"
        )

        # Add some history
        agent.conversation_history = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there")
        ]

        assert len(agent.conversation_history) == 2

        agent.reset_conversation()

        assert len(agent.conversation_history) == 0

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_get_info(self):
        """Test getting agent information"""
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"

        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
            tools=[mock_tool],
            retriever=MagicMock()
        )

        info = agent.get_info()

        assert info["name"] == "test_agent"
        assert info["role"] == "Test Advisor"
        assert "test_tool" in info["tools"]
        assert info["has_rag"] is True
        assert info["conversation_length"] == 0

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_get_info_no_retriever(self):
        """Test agent info when no RAG retriever"""
        agent = ConcreteAgent(
            name="test_agent",
            role="Test Advisor",
            retriever=None
        )

        info = agent.get_info()

        assert info["has_rag"] is False
