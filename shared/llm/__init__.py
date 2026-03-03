"""
SAHOOL Local LLM Utilities
==========================
أدوات نماذج اللغة الكبيرة المحلية لسهول

Local LLM utilities for development to save API costs.
Supports Ollama and OpenAI-compatible endpoints for local inference.

Features:
- Multiple provider support (Ollama, vLLM, LM Studio)
- Smart routing based on environment (dev=local, prod=cloud)
- Fallback logic between providers
- Agricultural prompt templates (bilingual Arabic/English)
- Token counting and response parsing utilities

Example Usage:
    from shared.llm import LLMRouter

    router = LLMRouter()

    # Automatically uses Ollama in dev, OpenAI in prod
    response = await router.generate(
        prompt="ما هي أفضل طريقة لري القمح؟",
        model="auto"  # Picks best available
    )
    print(response.text)

    # Use specific model
    response = await router.generate(
        prompt="Explain photosynthesis",
        model="llama3.2"
    )

    # With agricultural prompt template
    from shared.llm.prompts import format_irrigation_advice, PromptLanguage

    system, user = format_irrigation_advice(
        crop_type="wheat",
        area_hectares=5.0,
        soil_moisture=45.0,
        language=PromptLanguage.BILINGUAL
    )
    response = await router.generate(prompt=user, system_prompt=system)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

# Configuration
from .config import (
    CloudConfig,
    Environment,
    LLMConfig,
    ModelCapability,
    OllamaConfig,
    OpenAICompatConfig,
    get_config,
    get_local_models,
    get_model_info,
    get_models_by_capability,
    set_config,
)

# Ollama provider
from .ollama import (
    OllamaError,
    OllamaProvider,
    get_ollama_provider,
)

# OpenAI-compatible provider
from .openai_compat import (
    OpenAICompatError,
    OpenAICompatProvider,
    get_deepseek_vllm_provider,
    get_lm_studio_provider,
    get_openai_compat_provider,
    get_vllm_provider,
)

# Prompts
from .prompts import (
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

# Provider base classes
from .provider import (
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

# Router
from .router import (
    AllProvidersFailedError,
    LLMRouter,
    RouterStats,
    RoutingDecision,
    chat,
    generate,
    get_router,
)

# Utilities
from .utils import (
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

__all__ = [
    # Configuration
    "CloudConfig",
    "Environment",
    "LLMConfig",
    "ModelCapability",
    "OllamaConfig",
    "OpenAICompatConfig",
    "get_config",
    "set_config",
    "get_model_info",
    "get_models_by_capability",
    "get_local_models",
    # Provider base
    "GenerationOptions",
    "GenerationResponse",
    "GenerationStatus",
    "LLMProvider",
    "LLMProviderError",
    "Message",
    "ModelNotFoundError",
    "ProviderType",
    "ProviderUnavailableError",
    "RateLimitError",
    "StreamChunk",
    # Ollama
    "OllamaError",
    "OllamaProvider",
    "get_ollama_provider",
    # OpenAI-compatible
    "OpenAICompatError",
    "OpenAICompatProvider",
    "get_openai_compat_provider",
    "get_vllm_provider",
    "get_deepseek_vllm_provider",
    "get_lm_studio_provider",
    # Router
    "AllProvidersFailedError",
    "LLMRouter",
    "RouterStats",
    "RoutingDecision",
    "get_router",
    "generate",
    "chat",
    # Prompts
    "PromptCategory",
    "PromptLanguage",
    "PromptTemplate",
    "get_prompt_template",
    "list_prompt_templates",
    "get_prompts_by_category",
    "format_crop_advisory",
    "format_disease_diagnosis",
    "format_irrigation_advice",
    "format_general_question",
    # Utilities
    "JSONExtractionResult",
    "estimate_tokens",
    "estimate_tokens_messages",
    "check_context_limit",
    "truncate_to_token_limit",
    "extract_json",
    "extract_json_list",
    "parse_numbered_list",
    "parse_bullet_list",
    "parse_key_value_pairs",
    "extract_code_blocks",
    "clean_response",
    "split_into_sentences",
    "normalize_arabic",
    "detect_language",
    "validate_response_format",
    "ensure_type",
]

__version__ = "1.0.0"
