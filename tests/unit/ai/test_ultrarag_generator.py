"""
Tests for UltraRAG Generator Module
اختبارات وحدة المولد UltraRAG
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.ultrarag.generator import (
    Generator,
    GeneratorConfig,
    OllamaGenerator,
)
from shared.ai.ultrarag.models import (
    GenerationMode,
    GenerationResult,
)


class TestGeneratorConfig:
    """Tests for GeneratorConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = GeneratorConfig()
        assert config.model == "codellama:7b"
        assert config.provider == "ollama"
        assert config.max_tokens == 1024
        assert config.temperature == 0.1
        assert config.top_p == 0.9
        assert config.mode == GenerationMode.STANDARD
        assert config.system_prompt == ""
        assert config.include_sources is True
        assert config.bilingual_output is False

    def test_custom_config(self):
        """Test custom configuration"""
        config = GeneratorConfig(
            model="codellama:13b",
            provider="ollama",
            max_tokens=2048,
            temperature=0.3,
            mode=GenerationMode.CHAIN_OF_THOUGHT,
            bilingual_output=True,
        )
        assert config.model == "codellama:13b"
        assert config.max_tokens == 2048
        assert config.temperature == 0.3
        assert config.mode == GenerationMode.CHAIN_OF_THOUGHT
        assert config.bilingual_output is True

    def test_config_with_system_prompt(self):
        """Test configuration with system prompts"""
        config = GeneratorConfig(
            system_prompt="You are an agricultural assistant.",
            system_prompt_ar="أنت مساعد زراعي متخصص.",
        )
        assert "agricultural" in config.system_prompt
        assert "زراعي" in config.system_prompt_ar


class TestOllamaGenerator:
    """Tests for OllamaGenerator"""

    @pytest.fixture
    def mock_llm_client(self):
        """Create mock LLM client"""
        client = MagicMock()
        client.generate = AsyncMock()
        return client

    @pytest.fixture
    def generator(self, mock_llm_client):
        """Create generator instance"""
        return OllamaGenerator(llm_client=mock_llm_client)

    @pytest.fixture
    def generator_with_config(self, mock_llm_client):
        """Create generator with custom config"""
        config = GeneratorConfig(
            model="codellama:13b",
            temperature=0.2,
            bilingual_output=True,
        )
        return OllamaGenerator(llm_client=mock_llm_client, config=config)

    def test_generator_initialization(self, generator, mock_llm_client):
        """Test generator initialization"""
        assert generator.llm_client == mock_llm_client
        assert generator.config is not None
        assert generator.config.model == "codellama:7b"

    def test_generator_with_custom_config(self, generator_with_config):
        """Test generator with custom configuration"""
        assert generator_with_config.config.model == "codellama:13b"
        assert generator_with_config.config.temperature == 0.2
        assert generator_with_config.config.bilingual_output is True

    @pytest.mark.asyncio
    async def test_generate_standard(self, generator, mock_llm_client):
        """Test standard generation"""
        mock_llm_client.generate.return_value = "The recommended irrigation is 25mm per week."

        result = await generator.generate(
            query="How much water for wheat?",
            context="Wheat requires regular irrigation during growth.",
            mode=GenerationMode.STANDARD,
            language="en",
        )

        assert result is not None
        assert "25mm" in result.answer
        assert result.mode == GenerationMode.STANDARD
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_generate_chain_of_thought(self, generator, mock_llm_client):
        """Test chain-of-thought generation"""
        mock_llm_client.generate.return_value = """
        Reasoning:
        1. Wheat needs water during growth
        2. Summer requires more irrigation

        Final Answer:
        Apply 25mm per week during summer.
        """

        result = await generator.generate(
            query="How to irrigate wheat in summer?",
            context="Wheat cultivation guide...",
            mode=GenerationMode.CHAIN_OF_THOUGHT,
        )

        assert result.mode == GenerationMode.CHAIN_OF_THOUGHT
        mock_llm_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_arabic(self, generator, mock_llm_client):
        """Test generation in Arabic"""
        mock_llm_client.generate.return_value = "الري الموصى به هو 25 ملم أسبوعياً."

        result = await generator.generate(
            query="كيف أروي القمح؟",
            context="القمح يحتاج ري منتظم.",
            language="ar",
        )

        assert result is not None
        assert "ملم" in result.answer or "25" in result.answer

    @pytest.mark.asyncio
    async def test_generate_with_error(self, generator, mock_llm_client):
        """Test generation handles errors gracefully"""
        mock_llm_client.generate.side_effect = Exception("LLM timeout")

        result = await generator.generate(
            query="Test query",
            context="Test context",
        )

        assert "Error" in result.answer
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_generate_respects_max_tokens(self, generator, mock_llm_client):
        """Test that max_tokens is passed to LLM"""
        mock_llm_client.generate.return_value = "Response"

        await generator.generate(
            query="Test",
            context="Context",
            max_tokens=512,
        )

        call_args = mock_llm_client.generate.call_args
        assert call_args.kwargs["max_tokens"] == 512

    def test_standard_prompt_english(self, generator):
        """Test standard prompt generation in English"""
        prompt = generator._standard_prompt(
            query="How to irrigate wheat?",
            context="Wheat requires regular watering.",
            language="en",
        )
        assert "agricultural assistant" in prompt
        assert "How to irrigate wheat?" in prompt
        assert "Wheat requires regular watering" in prompt
        assert "Context:" in prompt

    def test_standard_prompt_arabic(self, generator):
        """Test standard prompt generation in Arabic"""
        prompt = generator._standard_prompt(
            query="كيف أروي القمح؟",
            context="القمح يحتاج ري منتظم",
            language="ar",
        )
        assert "مساعد زراعي" in prompt
        assert "كيف أروي القمح" in prompt
        assert "السياق" in prompt

    def test_cot_prompt_english(self, generator):
        """Test chain-of-thought prompt in English"""
        prompt = generator._cot_prompt(
            query="Test query",
            context="Test context",
            language="en",
        )
        assert "step-by-step" in prompt.lower()
        assert "Reasoning" in prompt
        assert "Final Answer" in prompt

    def test_cot_prompt_arabic(self, generator):
        """Test chain-of-thought prompt in Arabic"""
        prompt = generator._cot_prompt(
            query="سؤال",
            context="السياق",
            language="ar",
        )
        assert "خطوة بخطوة" in prompt
        assert "التفكير" in prompt
        assert "الإجابة النهائية" in prompt

    def test_self_reflective_prompt_english(self, generator):
        """Test self-reflective prompt in English"""
        prompt = generator._self_reflective_prompt(
            query="Test",
            context="Context",
            language="en",
        )
        # Verify it's different from standard
        standard = generator._standard_prompt("Test", "Context", "en")
        assert prompt != standard

    def test_mode_prompts_all_defined(self, generator):
        """Test that all generation modes have prompts"""
        for mode in GenerationMode:
            if mode == GenerationMode.ITERATIVE:
                # Iterative may share with another mode
                continue
            assert mode in generator._mode_prompts


class TestGenerationResult:
    """Tests for GenerationResult from generator perspective"""

    def test_result_structure(self):
        """Test generation result structure"""
        result = GenerationResult(
            answer="Test answer",
            answer_ar="إجابة اختبارية",
            confidence=0.85,
            reasoning="Step by step reasoning...",
            mode=GenerationMode.CHAIN_OF_THOUGHT,
            tokens_used=150,
            processing_time_ms=500.0,
        )
        assert result.answer == "Test answer"
        assert result.answer_ar == "إجابة اختبارية"
        assert result.confidence == 0.85
        assert result.reasoning is not None
        assert result.mode == GenerationMode.CHAIN_OF_THOUGHT

    def test_result_serialization(self):
        """Test result to_dict method"""
        result = GenerationResult(
            answer="Answer",
            confidence=0.9,
            mode=GenerationMode.STANDARD,
        )
        d = result.to_dict()
        assert d["answer"] == "Answer"
        assert d["confidence"] == 0.9
        assert d["mode"] == "standard"


class TestGeneratorModes:
    """Tests for different generation modes"""

    @pytest.fixture
    def mock_llm(self):
        client = MagicMock()
        client.generate = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_all_modes_callable(self, mock_llm):
        """Test that all generation modes work"""
        mock_llm.generate.return_value = "Response"
        generator = OllamaGenerator(llm_client=mock_llm)

        for mode in GenerationMode:
            result = await generator.generate(
                query="Test query",
                context="Test context",
                mode=mode,
            )
            assert result is not None
            assert result.mode == mode

    @pytest.mark.asyncio
    async def test_mode_affects_prompt(self, mock_llm):
        """Test that different modes use different prompts"""
        mock_llm.generate.return_value = "Response"
        generator = OllamaGenerator(llm_client=mock_llm)

        prompts_used = []

        for mode in [GenerationMode.STANDARD, GenerationMode.CHAIN_OF_THOUGHT]:
            await generator.generate(
                query="Query",
                context="Context",
                mode=mode,
            )
            call_args = mock_llm.generate.call_args
            prompts_used.append(call_args.kwargs["prompt"])

        # Different modes should use different prompts
        assert prompts_used[0] != prompts_used[1]
