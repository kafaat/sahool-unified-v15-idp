"""
Tests for shared/llm/ module
==============================

Tests cover:
- Enums: Environment, ModelCapability, ProviderType, GenerationStatus,
  PromptLanguage, PromptCategory
- Configuration: OllamaConfig, OpenAICompatConfig, CloudConfig, LLMConfig
- Provider base: Message, GenerationOptions, GenerationResponse, StreamChunk
- Error hierarchy: LLMProviderError, ModelNotFoundError, ProviderUnavailableError,
  RateLimitError, OllamaError, OpenAICompatError, AllProvidersFailedError
- Prompt templates: PromptTemplate, registry, convenience functions
- Router: RoutingDecision, RouterStats, LLMRouter model selection & routing
- Utilities: token estimation, JSON extraction, text parsing, Arabic processing
- Config global state: get_config, set_config
- Model registry: get_model_info, get_models_by_capability, get_local_models
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from shared.llm.config import (
    CloudConfig,
    Environment,
    LLMConfig,
    ModelCapability,
    MODEL_REGISTRY,
    OllamaConfig,
    OpenAICompatConfig,
    get_config,
    get_local_models,
    get_model_info,
    get_models_by_capability,
    set_config,
)
from shared.llm.provider import (
    GenerationOptions,
    GenerationResponse,
    GenerationStatus,
    LLMProvider,
    LLMProviderError,
    Message,
    ModelNotFoundError,
    ProviderType,
    ProviderUnavailableError,
    RateLimitError,
    StreamChunk,
)
from shared.llm.prompts import (
    PROMPT_TEMPLATES,
    PromptCategory,
    PromptLanguage,
    PromptTemplate,
    format_crop_advisory,
    format_disease_diagnosis,
    format_general_question,
    format_irrigation_advice,
    get_prompt_template,
    get_prompts_by_category,
    list_prompt_templates,
)
from shared.llm.router import (
    AllProvidersFailedError,
    LLMRouter,
    RouterStats,
    RoutingDecision,
)
from shared.llm.utils import (
    JSONExtractionResult,
    check_context_limit,
    clean_response,
    detect_language,
    ensure_type,
    estimate_tokens,
    estimate_tokens_messages,
    extract_code_blocks,
    extract_json,
    extract_json_list,
    normalize_arabic,
    parse_bullet_list,
    parse_key_value_pairs,
    parse_numbered_list,
    split_into_sentences,
    truncate_to_token_limit,
    validate_response_format,
)
from shared.llm.ollama import OllamaError
from shared.llm.openai_compat import OpenAICompatError


# ─────────────────────────────────────────────────────────────────────────────
# Enum Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestEnvironmentEnum:
    @pytest.mark.unit
    def test_all_values(self):
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TEST.value == "test"

    @pytest.mark.unit
    def test_member_count(self):
        assert len(Environment) == 4


class TestModelCapabilityEnum:
    @pytest.mark.unit
    def test_all_values(self):
        assert ModelCapability.CHAT.value == "chat"
        assert ModelCapability.CODE.value == "code"
        assert ModelCapability.EMBEDDING.value == "embedding"
        assert ModelCapability.VISION.value == "vision"
        assert ModelCapability.AGRICULTURAL.value == "agricultural"
        assert ModelCapability.MULTILINGUAL.value == "multilingual"

    @pytest.mark.unit
    def test_member_count(self):
        assert len(ModelCapability) == 6


class TestProviderTypeEnum:
    @pytest.mark.unit
    def test_all_values(self):
        assert ProviderType.OLLAMA.value == "ollama"
        assert ProviderType.OPENAI_COMPAT.value == "openai_compat"
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.ANTHROPIC.value == "anthropic"
        assert ProviderType.LOCAL.value == "local"

    @pytest.mark.unit
    def test_member_count(self):
        assert len(ProviderType) == 5


class TestGenerationStatusEnum:
    @pytest.mark.unit
    def test_all_values(self):
        assert GenerationStatus.SUCCESS.value == "success"
        assert GenerationStatus.ERROR.value == "error"
        assert GenerationStatus.TIMEOUT.value == "timeout"
        assert GenerationStatus.RATE_LIMITED.value == "rate_limited"
        assert GenerationStatus.MODEL_NOT_FOUND.value == "model_not_found"

    @pytest.mark.unit
    def test_member_count(self):
        assert len(GenerationStatus) == 5


class TestPromptLanguageEnum:
    @pytest.mark.unit
    def test_all_values(self):
        assert PromptLanguage.ENGLISH.value == "en"
        assert PromptLanguage.ARABIC.value == "ar"
        assert PromptLanguage.BILINGUAL.value == "both"

    @pytest.mark.unit
    def test_member_count(self):
        assert len(PromptLanguage) == 3


class TestPromptCategoryEnum:
    @pytest.mark.unit
    def test_all_values(self):
        assert PromptCategory.CROP_ADVISORY.value == "crop_advisory"
        assert PromptCategory.DISEASE_DIAGNOSIS.value == "disease_diagnosis"
        assert PromptCategory.IRRIGATION.value == "irrigation"
        assert PromptCategory.FERTILIZER.value == "fertilizer"
        assert PromptCategory.PEST_CONTROL.value == "pest_control"
        assert PromptCategory.HARVEST.value == "harvest"
        assert PromptCategory.GENERAL.value == "general"

    @pytest.mark.unit
    def test_member_count(self):
        assert len(PromptCategory) == 7


# ─────────────────────────────────────────────────────────────────────────────
# Configuration Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestOllamaConfig:
    @pytest.mark.unit
    def test_defaults(self):
        config = OllamaConfig()
        assert "localhost" in config.base_url or "11434" in config.base_url
        assert config.timeout == 120.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.stream_timeout == 300.0


class TestOpenAICompatConfig:
    @pytest.mark.unit
    def test_defaults(self):
        config = OpenAICompatConfig()
        assert config.timeout == 120.0
        assert config.organization is None


class TestCloudConfig:
    @pytest.mark.unit
    def test_defaults(self):
        config = CloudConfig()
        assert config.openai_base_url == "https://api.openai.com/v1"
        assert config.timeout == 120.0


class TestLLMConfig:
    @pytest.mark.unit
    def test_defaults(self):
        config = LLMConfig(
            environment=Environment.DEVELOPMENT,
            development_mode=True,
        )
        assert config.default_temperature == 0.7
        assert config.default_max_tokens == 4096
        assert config.enable_fallback is True
        assert config.enable_cost_tracking is True
        assert config.enable_metrics is True

    @pytest.mark.unit
    def test_is_development(self):
        config = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=False)
        assert config.is_development is True

        config2 = LLMConfig(environment=Environment.PRODUCTION, development_mode=True)
        assert config2.is_development is True

    @pytest.mark.unit
    def test_is_production(self):
        config = LLMConfig(environment=Environment.PRODUCTION, development_mode=False)
        assert config.is_production is True

        config2 = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=False)
        assert config2.is_production is False

    @pytest.mark.unit
    def test_prefer_local(self):
        config = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=False)
        assert config.prefer_local is True

        config2 = LLMConfig(environment=Environment.PRODUCTION, development_mode=False)
        assert config2.prefer_local is False

    @pytest.mark.unit
    def test_to_dict(self):
        config = LLMConfig(
            environment=Environment.TEST,
            development_mode=False,
        )
        d = config.to_dict()
        assert d["environment"] == "test"
        assert "ollama" in d
        assert "openai_compat" in d
        assert "cloud" in d
        assert "defaults" in d
        assert d["defaults"]["temperature"] == 0.7
        assert d["defaults"]["max_tokens"] == 4096

    @pytest.mark.unit
    def test_from_env(self):
        config = LLMConfig.from_env()
        assert isinstance(config, LLMConfig)


# ─────────────────────────────────────────────────────────────────────────────
# Global Config Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestGlobalConfig:
    @pytest.mark.unit
    def test_set_and_get_config(self):
        custom = LLMConfig(environment=Environment.TEST, development_mode=False)
        set_config(custom)
        retrieved = get_config()
        assert retrieved.environment == Environment.TEST
        # Reset to avoid side effects
        set_config(LLMConfig(environment=Environment.DEVELOPMENT, development_mode=True))


# ─────────────────────────────────────────────────────────────────────────────
# Model Registry Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestModelRegistry:
    @pytest.mark.unit
    def test_get_model_info_known(self):
        info = get_model_info("llama3.2")
        assert info is not None
        assert info["provider"] == "ollama"
        assert ModelCapability.CHAT in info["capabilities"]

    @pytest.mark.unit
    def test_get_model_info_unknown(self):
        info = get_model_info("nonexistent-model-xyz")
        assert info is None

    @pytest.mark.unit
    def test_get_models_by_capability_chat(self):
        models = get_models_by_capability(ModelCapability.CHAT)
        assert len(models) > 0
        assert "llama3.2" in models

    @pytest.mark.unit
    def test_get_models_by_capability_embedding(self):
        models = get_models_by_capability(ModelCapability.EMBEDDING)
        assert "nomic-embed-text" in models

    @pytest.mark.unit
    def test_get_models_by_capability_code(self):
        models = get_models_by_capability(ModelCapability.CODE)
        assert "codellama" in models

    @pytest.mark.unit
    def test_get_local_models(self):
        local = get_local_models()
        assert len(local) > 0
        # All local models should have provider=ollama
        for model_name in local:
            info = get_model_info(model_name)
            assert info is not None
            assert info["provider"] == "ollama"
        # OpenAI models should not be in local
        assert "gpt-4o" not in local
        assert "gpt-4o-mini" not in local


# ─────────────────────────────────────────────────────────────────────────────
# Provider Base Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestMessage:
    @pytest.mark.unit
    def test_system_factory(self):
        msg = Message.system("You are a helper")
        assert msg.role == "system"
        assert msg.content == "You are a helper"

    @pytest.mark.unit
    def test_user_factory(self):
        msg = Message.user("Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    @pytest.mark.unit
    def test_assistant_factory(self):
        msg = Message.assistant("Hi there")
        assert msg.role == "assistant"
        assert msg.content == "Hi there"

    @pytest.mark.unit
    def test_to_dict_without_name(self):
        msg = Message(role="user", content="test")
        d = msg.to_dict()
        assert d == {"role": "user", "content": "test"}
        assert "name" not in d

    @pytest.mark.unit
    def test_to_dict_with_name(self):
        msg = Message(role="user", content="test", name="farmer1")
        d = msg.to_dict()
        assert d["name"] == "farmer1"


class TestGenerationOptions:
    @pytest.mark.unit
    def test_defaults(self):
        opts = GenerationOptions()
        assert opts.temperature == 0.7
        assert opts.max_tokens == 4096
        assert opts.top_p == 1.0
        assert opts.top_k is None
        assert opts.stop is None
        assert opts.presence_penalty == 0.0
        assert opts.frequency_penalty == 0.0
        assert opts.seed is None
        assert opts.json_mode is False
        assert opts.stream is False

    @pytest.mark.unit
    def test_to_dict_minimal(self):
        opts = GenerationOptions()
        d = opts.to_dict()
        assert "temperature" in d
        assert "max_tokens" in d
        assert "top_p" in d
        # Optional fields should not be present with default values
        assert "top_k" not in d
        assert "stop" not in d
        assert "presence_penalty" not in d
        assert "seed" not in d

    @pytest.mark.unit
    def test_to_dict_with_optionals(self):
        opts = GenerationOptions(
            top_k=40,
            stop=["END"],
            presence_penalty=0.5,
            frequency_penalty=0.3,
            seed=42,
        )
        d = opts.to_dict()
        assert d["top_k"] == 40
        assert d["stop"] == ["END"]
        assert d["presence_penalty"] == 0.5
        assert d["frequency_penalty"] == 0.3
        assert d["seed"] == 42


class TestGenerationResponse:
    @pytest.mark.unit
    def test_total_tokens(self):
        resp = GenerationResponse(
            text="hello",
            model="llama3.2",
            provider=ProviderType.OLLAMA,
            tokens_input=10,
            tokens_output=5,
        )
        assert resp.total_tokens == 15

    @pytest.mark.unit
    def test_is_success(self):
        resp = GenerationResponse(
            text="ok",
            model="llama3.2",
            provider=ProviderType.OLLAMA,
            status=GenerationStatus.SUCCESS,
        )
        assert resp.is_success is True

        resp2 = GenerationResponse(
            text="",
            model="llama3.2",
            provider=ProviderType.OLLAMA,
            status=GenerationStatus.ERROR,
        )
        assert resp2.is_success is False

    @pytest.mark.unit
    def test_to_dict(self):
        resp = GenerationResponse(
            text="result",
            model="llama3.2",
            provider=ProviderType.OLLAMA,
            tokens_input=10,
            tokens_output=20,
            latency_ms=150.0,
            cost_usd=0.0,
        )
        d = resp.to_dict()
        assert d["text"] == "result"
        assert d["model"] == "llama3.2"
        assert d["provider"] == "ollama"
        assert d["status"] == "success"
        assert d["total_tokens"] == 30
        assert d["latency_ms"] == 150.0


class TestStreamChunk:
    @pytest.mark.unit
    def test_defaults(self):
        chunk = StreamChunk(text="hello")
        assert chunk.text == "hello"
        assert chunk.is_final is False
        assert chunk.tokens == 0
        assert chunk.finish_reason is None

    @pytest.mark.unit
    def test_final_chunk(self):
        chunk = StreamChunk(text="", is_final=True, finish_reason="stop")
        assert chunk.is_final is True
        assert chunk.finish_reason == "stop"


# ─────────────────────────────────────────────────────────────────────────────
# Error Hierarchy Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestErrors:
    @pytest.mark.unit
    def test_llm_provider_error(self):
        err = LLMProviderError("Something broke", provider=ProviderType.OLLAMA)
        assert str(err) == "Something broke"
        assert err.provider == ProviderType.OLLAMA
        assert err.status == GenerationStatus.ERROR

    @pytest.mark.unit
    def test_model_not_found_error(self):
        err = ModelNotFoundError("badmodel", provider=ProviderType.OLLAMA)
        assert "badmodel" in str(err)
        assert err.model == "badmodel"
        assert err.status == GenerationStatus.MODEL_NOT_FOUND

    @pytest.mark.unit
    def test_provider_unavailable_error(self):
        err = ProviderUnavailableError("Server down")
        assert str(err) == "Server down"
        assert isinstance(err, LLMProviderError)

    @pytest.mark.unit
    def test_rate_limit_error(self):
        err = RateLimitError("Too many requests", retry_after=30.0)
        assert err.retry_after == 30.0
        assert err.status == GenerationStatus.RATE_LIMITED

    @pytest.mark.unit
    def test_ollama_error(self):
        err = OllamaError("Ollama issue")
        assert err.provider == ProviderType.OLLAMA
        assert isinstance(err, LLMProviderError)

    @pytest.mark.unit
    def test_openai_compat_error(self):
        err = OpenAICompatError("OpenAI compat issue")
        assert err.provider == ProviderType.OPENAI_COMPAT
        assert isinstance(err, LLMProviderError)

    @pytest.mark.unit
    def test_all_providers_failed_error(self):
        errors = [
            (ProviderType.OLLAMA, "timeout"),
            (ProviderType.OPENAI_COMPAT, "connection refused"),
        ]
        err = AllProvidersFailedError(errors)
        assert err.errors == errors
        assert "All LLM providers failed" in str(err)
        assert "timeout" in str(err)
        assert "connection refused" in str(err)


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Template Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestPromptTemplate:
    @pytest.mark.unit
    def test_get_system_prompt_english(self):
        template = PromptTemplate(
            name="Test",
            name_ar="اختبار",
            category=PromptCategory.GENERAL,
            system_en="English system",
            system_ar="نظام عربي",
            user_template_en="Question: {question}",
            user_template_ar="السؤال: {question}",
        )
        assert template.get_system_prompt(PromptLanguage.ENGLISH) == "English system"

    @pytest.mark.unit
    def test_get_system_prompt_arabic(self):
        template = PromptTemplate(
            name="Test",
            name_ar="اختبار",
            category=PromptCategory.GENERAL,
            system_en="English system",
            system_ar="نظام عربي",
            user_template_en="{question}",
            user_template_ar="{question}",
        )
        assert template.get_system_prompt(PromptLanguage.ARABIC) == "نظام عربي"

    @pytest.mark.unit
    def test_get_system_prompt_bilingual(self):
        template = PromptTemplate(
            name="Test",
            name_ar="اختبار",
            category=PromptCategory.GENERAL,
            system_en="English",
            system_ar="عربي",
            user_template_en="{question}",
            user_template_ar="{question}",
        )
        result = template.get_system_prompt(PromptLanguage.BILINGUAL)
        assert "English" in result
        assert "عربي" in result

    @pytest.mark.unit
    def test_get_user_prompt_with_variables(self):
        template = PromptTemplate(
            name="Test",
            name_ar="اختبار",
            category=PromptCategory.GENERAL,
            system_en="sys",
            system_ar="نظام",
            user_template_en="Crop: {crop_type}, Area: {area}",
            user_template_ar="المحصول: {crop_type}, المساحة: {area}",
        )
        result = template.get_user_prompt(
            PromptLanguage.ENGLISH, crop_type="wheat", area="5ha"
        )
        assert "wheat" in result
        assert "5ha" in result

    @pytest.mark.unit
    def test_format_returns_tuple(self):
        template = PromptTemplate(
            name="Test",
            name_ar="اختبار",
            category=PromptCategory.GENERAL,
            system_en="sys",
            system_ar="نظام",
            user_template_en="{question}",
            user_template_ar="{question}",
        )
        system, user = template.format(
            language=PromptLanguage.ENGLISH, question="How to irrigate?"
        )
        assert system == "sys"
        assert "How to irrigate?" in user


class TestPromptRegistry:
    @pytest.mark.unit
    def test_all_templates_registered(self):
        assert "crop_advisor" in PROMPT_TEMPLATES
        assert "disease_diagnosis" in PROMPT_TEMPLATES
        assert "irrigation_advice" in PROMPT_TEMPLATES
        assert "fertilizer_recommendation" in PROMPT_TEMPLATES
        assert "pest_control" in PROMPT_TEMPLATES
        assert "harvest_timing" in PROMPT_TEMPLATES
        assert "general" in PROMPT_TEMPLATES

    @pytest.mark.unit
    def test_get_prompt_template(self):
        t = get_prompt_template("crop_advisor")
        assert t is not None
        assert t.category == PromptCategory.CROP_ADVISORY

        assert get_prompt_template("nonexistent") is None

    @pytest.mark.unit
    def test_list_prompt_templates(self):
        templates = list_prompt_templates()
        assert len(templates) == len(PROMPT_TEMPLATES)
        for item in templates:
            assert "name" in item
            assert "name_ar" in item
            assert "category" in item

    @pytest.mark.unit
    def test_get_prompts_by_category(self):
        irrigation = get_prompts_by_category(PromptCategory.IRRIGATION)
        assert len(irrigation) >= 1
        assert all(t.category == PromptCategory.IRRIGATION for t in irrigation)


class TestConvenienceFunctions:
    @pytest.mark.unit
    def test_format_crop_advisory(self):
        system, user = format_crop_advisory(
            crop_type="wheat",
            question="When to harvest?",
            area_hectares=10.0,
            growth_stage="heading",
            location="Yemen",
            conditions="dry",
        )
        assert isinstance(system, str)
        assert "wheat" in user

    @pytest.mark.unit
    def test_format_disease_diagnosis(self):
        system, user = format_disease_diagnosis(
            crop_type="tomato",
            symptoms="yellowing leaves",
            growth_stage="fruiting",
            temperature=30.0,
            humidity=80.0,
            recent_weather="rainy",
        )
        assert isinstance(system, str)
        assert "tomato" in user
        assert "yellowing leaves" in user

    @pytest.mark.unit
    def test_format_irrigation_advice(self):
        system, user = format_irrigation_advice(
            crop_type="wheat",
            area_hectares=5.0,
            soil_moisture=45.0,
            language=PromptLanguage.ENGLISH,
        )
        assert isinstance(system, str)
        assert "wheat" in user
        assert "45" in user

    @pytest.mark.unit
    def test_format_general_question(self):
        system, user = format_general_question(
            question="What is NDVI?",
            language=PromptLanguage.ENGLISH,
        )
        assert isinstance(system, str)
        assert "What is NDVI?" in user


# ─────────────────────────────────────────────────────────────────────────────
# Utility Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestEstimateTokens:
    @pytest.mark.unit
    def test_empty_text(self):
        assert estimate_tokens("") == 0

    @pytest.mark.unit
    def test_english_text(self):
        text = "Hello world, this is a test sentence."
        tokens = estimate_tokens(text)
        assert tokens > 0
        # ~4 chars per token for English
        assert tokens == len(text) // 4

    @pytest.mark.unit
    def test_arabic_text(self):
        text = "مرحبا بالعالم هذا اختبار"
        tokens = estimate_tokens(text)
        assert tokens > 0
        # Arabic uses ~2 chars per token, should give more tokens than English ratio
        assert tokens == len(text) // 2

    @pytest.mark.unit
    def test_minimum_one_token(self):
        assert estimate_tokens("a") == 1


class TestEstimateTokensMessages:
    @pytest.mark.unit
    def test_message_overhead(self):
        messages = [{"role": "user", "content": ""}]
        # Should include 4-token overhead per message
        assert estimate_tokens_messages(messages) == 4


class TestCheckContextLimit:
    @pytest.mark.unit
    def test_fits(self):
        fits, estimated = check_context_limit("short", max_tokens=4096)
        assert fits is True
        assert estimated > 0

    @pytest.mark.unit
    def test_does_not_fit(self):
        long_text = "x" * 100000
        fits, estimated = check_context_limit(long_text, max_tokens=100)
        assert fits is False


class TestTruncateToTokenLimit:
    @pytest.mark.unit
    def test_no_truncation_needed(self):
        text = "short text"
        result = truncate_to_token_limit(text, max_tokens=4096)
        assert result == text

    @pytest.mark.unit
    def test_truncation_from_end(self):
        text = "x" * 100000
        result = truncate_to_token_limit(text, max_tokens=100, reserved_output_tokens=50)
        assert result.endswith("...")
        assert len(result) < len(text)

    @pytest.mark.unit
    def test_truncation_from_start(self):
        text = "x" * 100000
        result = truncate_to_token_limit(
            text, max_tokens=100, reserved_output_tokens=50, truncate_from="start"
        )
        assert result.startswith("...")


class TestExtractJson:
    @pytest.mark.unit
    def test_pure_json(self):
        result = extract_json('{"key": "value"}')
        assert result.success is True
        assert result.data == {"key": "value"}

    @pytest.mark.unit
    def test_json_in_code_block(self):
        text = 'Here is the result:\n```json\n{"name": "wheat"}\n```'
        result = extract_json(text)
        assert result.success is True
        assert result.data["name"] == "wheat"

    @pytest.mark.unit
    def test_json_mixed_with_text(self):
        text = 'The response is {"count": 42} which means...'
        result = extract_json(text)
        assert result.success is True
        assert result.data["count"] == 42

    @pytest.mark.unit
    def test_empty_text(self):
        result = extract_json("")
        assert result.success is False
        assert result.error == "Empty text"

    @pytest.mark.unit
    def test_no_json(self):
        result = extract_json("This is plain text with no JSON at all.")
        assert result.success is False


class TestExtractJsonList:
    @pytest.mark.unit
    def test_multiple_objects(self):
        text = 'First: {"a": 1} and second: {"b": 2}'
        results = extract_json_list(text)
        assert len(results) >= 1


class TestParseNumberedList:
    @pytest.mark.unit
    def test_standard_numbered_list(self):
        text = "1. First item\n2. Second item\n3. Third item"
        items = parse_numbered_list(text)
        assert items == ["First item", "Second item", "Third item"]

    @pytest.mark.unit
    def test_empty_text(self):
        assert parse_numbered_list("") == []


class TestParseBulletList:
    @pytest.mark.unit
    def test_dash_bullets(self):
        text = "- Apple\n- Banana\n- Cherry"
        items = parse_bullet_list(text)
        assert items == ["Apple", "Banana", "Cherry"]

    @pytest.mark.unit
    def test_star_bullets(self):
        text = "* Item one\n* Item two"
        items = parse_bullet_list(text)
        assert items == ["Item one", "Item two"]


class TestParseKeyValuePairs:
    @pytest.mark.unit
    def test_colon_separated(self):
        text = "Name: Wheat\nType: Grain\nArea: 5 hectares"
        pairs = parse_key_value_pairs(text)
        assert pairs["Name"] == "Wheat"
        assert pairs["Type"] == "Grain"
        assert pairs["Area"] == "5 hectares"


class TestExtractCodeBlocks:
    @pytest.mark.unit
    def test_python_block(self):
        text = "```python\nprint('hello')\n```"
        blocks = extract_code_blocks(text, language="python")
        assert len(blocks) == 1
        assert "print('hello')" in blocks[0]

    @pytest.mark.unit
    def test_any_language(self):
        text = "```js\nconsole.log('hi')\n```"
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1


class TestCleanResponse:
    @pytest.mark.unit
    def test_removes_prefix(self):
        assert clean_response("Sure, here is the answer") == "here is the answer"
        assert clean_response("Of course! the data") == "the data"

    @pytest.mark.unit
    def test_normalizes_whitespace(self):
        assert clean_response("hello   world\n\ntest") == "hello world test"

    @pytest.mark.unit
    def test_empty(self):
        assert clean_response("") == ""


class TestSplitIntoSentences:
    @pytest.mark.unit
    def test_english(self):
        text = "First sentence. Second sentence! Third?"
        sentences = split_into_sentences(text)
        assert len(sentences) == 3

    @pytest.mark.unit
    def test_arabic_question_mark(self):
        text = "هل هذا سؤال؟ نعم هذا جواب."
        sentences = split_into_sentences(text)
        assert len(sentences) == 2


class TestNormalizeArabic:
    @pytest.mark.unit
    def test_alef_normalization(self):
        # All alef variants should normalize to plain alef
        assert normalize_arabic("أحمد") == "احمد"
        assert normalize_arabic("إبراهيم") == "ابراهيم"

    @pytest.mark.unit
    def test_remove_tatweel(self):
        assert normalize_arabic("كتـــاب") == "كتاب"

    @pytest.mark.unit
    def test_empty(self):
        assert normalize_arabic("") == ""


class TestDetectLanguage:
    @pytest.mark.unit
    def test_english(self):
        assert detect_language("Hello world, this is English text") == "en"

    @pytest.mark.unit
    def test_arabic(self):
        assert detect_language("مرحبا بالعالم هذا نص عربي كامل") == "ar"

    @pytest.mark.unit
    def test_mixed(self):
        result = detect_language("Hello مرحبا world عالم")
        assert result in ("mixed", "ar", "en")

    @pytest.mark.unit
    def test_empty(self):
        assert detect_language("") == "en"


class TestValidateResponseFormat:
    @pytest.mark.unit
    def test_json_valid(self):
        valid, error = validate_response_format('{"key": "val"}', "json")
        assert valid is True
        assert error is None

    @pytest.mark.unit
    def test_json_invalid(self):
        valid, error = validate_response_format("not json", "json")
        assert valid is False
        assert error is not None

    @pytest.mark.unit
    def test_list_valid(self):
        valid, error = validate_response_format("1. First\n2. Second", "list")
        assert valid is True

    @pytest.mark.unit
    def test_text_valid(self):
        valid, error = validate_response_format("some text", "text")
        assert valid is True

    @pytest.mark.unit
    def test_text_empty(self):
        valid, error = validate_response_format("   ", "text")
        assert valid is False


class TestEnsureType:
    @pytest.mark.unit
    def test_correct_type(self):
        assert ensure_type(42, int, 0) == 42

    @pytest.mark.unit
    def test_convertible(self):
        assert ensure_type("42", int, 0) == 42

    @pytest.mark.unit
    def test_not_convertible(self):
        assert ensure_type("abc", int, -1) == -1


# ─────────────────────────────────────────────────────────────────────────────
# Router Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestRoutingDecision:
    @pytest.mark.unit
    def test_creation(self):
        decision = RoutingDecision(
            provider_type=ProviderType.OLLAMA,
            model="llama3.2",
            reason="development mode",
        )
        assert decision.provider_type == ProviderType.OLLAMA
        assert decision.model == "llama3.2"
        assert decision.fallbacks == []


class TestRouterStats:
    @pytest.mark.unit
    def test_defaults(self):
        stats = RouterStats()
        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0
        assert stats.fallback_count == 0
        assert stats.total_tokens == 0
        assert stats.total_cost_usd == 0.0
        assert stats.last_request is None


class TestLLMRouter:
    @pytest.mark.unit
    def test_init_with_config(self):
        config = LLMConfig(environment=Environment.TEST, development_mode=False)
        router = LLMRouter(config=config)
        assert router.config.environment == Environment.TEST

    @pytest.mark.unit
    def test_select_model_specific(self):
        config = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=True)
        router = LLMRouter(config=config)
        model, provider = router._select_model("codellama", None, True)
        assert model == "codellama"
        assert provider == ProviderType.OLLAMA

    @pytest.mark.unit
    def test_select_model_unknown_defaults_to_ollama(self):
        config = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=True)
        router = LLMRouter(config=config)
        model, provider = router._select_model("some-custom-model", None, True)
        assert model == "some-custom-model"
        assert provider == ProviderType.OLLAMA

    @pytest.mark.unit
    def test_select_model_auto_dev(self):
        config = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=True)
        router = LLMRouter(config=config)
        model, provider = router._select_model("auto", None, True)
        assert provider == ProviderType.OLLAMA

    @pytest.mark.unit
    def test_select_model_auto_prod(self):
        config = LLMConfig(environment=Environment.PRODUCTION, development_mode=False)
        router = LLMRouter(config=config)
        model, provider = router._select_model("auto", None, False)
        assert provider == ProviderType.OPENAI

    @pytest.mark.unit
    def test_select_model_with_code_capability(self):
        config = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=True)
        router = LLMRouter(config=config)
        model, provider = router._select_model(
            None, [ModelCapability.CODE], True
        )
        # Should prefer codellama for code capability
        assert provider == ProviderType.OLLAMA

    @pytest.mark.unit
    def test_select_model_with_multilingual_capability(self):
        config = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=True)
        router = LLMRouter(config=config)
        model, provider = router._select_model(
            None, [ModelCapability.MULTILINGUAL], True
        )
        assert provider == ProviderType.OLLAMA

    @pytest.mark.unit
    def test_get_status(self):
        config = LLMConfig(environment=Environment.TEST, development_mode=False)
        router = LLMRouter(config=config)
        status = router.get_status()
        assert "config" in status
        assert "providers" in status
        assert "stats" in status
        assert status["config"]["environment"] == "test"
        assert status["stats"]["total_requests"] == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_decide_routing_development(self):
        config = LLMConfig(environment=Environment.DEVELOPMENT, development_mode=True)
        router = LLMRouter(config=config)
        decision = await router.decide_routing(model="auto")
        assert decision.provider_type == ProviderType.OLLAMA
        assert len(decision.reason) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_close(self):
        config = LLMConfig(environment=Environment.TEST, development_mode=False)
        router = LLMRouter(config=config)
        # Should not raise even with no providers
        await router.close()
        assert len(router._providers) == 0


class TestJSONExtractionResult:
    @pytest.mark.unit
    def test_success(self):
        result = JSONExtractionResult(
            success=True, data={"key": "val"}, raw_text='{"key":"val"}'
        )
        assert result.success is True
        assert result.data == {"key": "val"}
        assert result.error is None

    @pytest.mark.unit
    def test_failure(self):
        result = JSONExtractionResult(
            success=False, data=None, raw_text="bad", error="No JSON"
        )
        assert result.success is False
        assert result.error == "No JSON"
