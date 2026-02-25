# shared/llm

Local LLM Utilities — Provider Config & Intelligent Routing
| أدوات نماذج اللغة الكبيرة المحلية — تكوين المزودين والتوجيه الذكي

**Version**: 1.0.0 | **License**: Proprietary - KAFAAT

---

## Overview

The `shared/llm` module provides a unified interface for running Large Language
Model inference across multiple providers. Its primary design goals are:

- **Cost control in development**: routes to Ollama (local, free) when
  `ENVIRONMENT=development` or `DEVELOPMENT_MODE=true`, and to cloud providers
  (OpenAI, Anthropic) in production.
- **Automatic fallback**: if the primary provider is unavailable, the router
  tries the next provider in the fallback chain transparently.
- **Agricultural domain knowledge**: ready-made bilingual (Arabic/English)
  prompt templates for crop advisory, disease diagnosis, irrigation, pest
  control, fertilizer recommendations, and harvest timing.
- **Offline-first compatibility**: Ollama runs entirely on-premise, supporting
  the platform's offline-first architecture for low-connectivity environments.

---

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package entry point; exports all public symbols |
| `config.py` | `LLMConfig`, `OllamaConfig`, `CloudConfig`, model registry, helper functions |
| `provider.py` | Abstract `LLMProvider` base class, `GenerationOptions`, `GenerationResponse`, error types |
| `ollama.py` | `OllamaProvider` — native Ollama REST API integration |
| `openai_compat.py` | `OpenAICompatProvider` — OpenAI-compatible endpoints (vLLM, LM Studio) |
| `router.py` | `LLMRouter` — intelligent routing, fallback, stats; `get_router()` global singleton |
| `prompts.py` | `PromptTemplate` registry with 7 bilingual agricultural templates |
| `utils.py` | Token estimation, JSON extraction, Arabic normalization, response parsing |

---

## Supported Providers

| Provider | Class | Use Case |
|----------|-------|----------|
| **Ollama** | `OllamaProvider` | Local inference (development, on-premise) |
| **OpenAI-compat** | `OpenAICompatProvider` | vLLM, LM Studio, any `/v1/` endpoint |
| **OpenAI** (cloud) | via `CloudConfig` | Production cloud fallback |
| **Anthropic** (cloud) | via `CloudConfig` | Production cloud fallback |

### Model Registry (selected)

| Model | Provider | Capabilities | Context |
|-------|----------|-------------|---------|
| `llama3.2` | Ollama | CHAT, MULTILINGUAL | 128k |
| `qwen2.5` / `qwen2.5:7b` | Ollama | CHAT, CODE, MULTILINGUAL | 32k |
| `codellama` / `codellama:7b` | Ollama | CODE, CHAT | 16k |
| `mistral` / `mistral:7b` | Ollama | CHAT, CODE | 32k |
| `nomic-embed-text` | Ollama | EMBEDDING | 8k |
| `gpt-4o-mini` | OpenAI | CHAT, CODE, VISION, MULTILINGUAL | 128k |
| `gpt-4o` | OpenAI | CHAT, CODE, VISION, MULTILINGUAL | 128k |

`ModelCapability` values: `CHAT`, `CODE`, `EMBEDDING`, `VISION`, `AGRICULTURAL`, `MULTILINGUAL`.

---

## Routing Logic

The `LLMRouter` selects a provider using the following ordered rules:

1. If a specific `model` name is provided and recognized in the registry, use its assigned provider.
2. If `model="auto"` (default), pick the best model matching the requested `capabilities`.
3. Prefer local (Ollama) when `prefer_local=True` or when the environment is `development`.
4. For multilingual requests, prefer `qwen2.5`; for code requests, prefer `codellama`.
5. If the selected provider is unavailable, fall through the fallback chain:
   `OLLAMA` → `OPENAI_COMPAT` → `OPENAI` (cloud).

---

## Usage Examples

### Simple Text Generation

```python
from shared.llm import generate

# Automatic provider selection based on environment
response = await generate(
    prompt="ما هي أفضل طريقة لري القمح؟",
    model="auto",
)
print(response.text)
print(f"Tokens used: {response.total_tokens}")
print(f"Cost: ${response.cost_usd:.4f}")
```

### Chat Completion

```python
from shared.llm import chat, Message

messages = [
    Message(role="system", content="You are an agricultural advisor."),
    Message(role="user", content="My wheat leaves are turning yellow."),
]
response = await chat(messages, model="llama3.2")
print(response.text)
```

### Streaming Response

```python
from shared.llm import LLMRouter, ModelCapability

router = LLMRouter()
async for chunk in router.generate_stream(
    prompt="Explain nitrogen deficiency in wheat",
    capabilities=[ModelCapability.MULTILINGUAL],
):
    print(chunk.text, end="", flush=True)
await router.close()
```

### Using the Router as a Context Manager

```python
from shared.llm import LLMRouter, ModelCapability

async with LLMRouter() as router:
    response = await router.generate(
        prompt="Recommend a pest control schedule for dates",
        capabilities=[ModelCapability.AGRICULTURAL],
        prefer_local=True,
        enable_fallback=True,
    )
    print(router.get_status())  # provider availability + stats
```

### Agricultural Prompt Templates

```python
from shared.llm import LLMRouter
from shared.llm.prompts import format_irrigation_advice, PromptLanguage

system_prompt, user_prompt = format_irrigation_advice(
    crop_type="wheat",
    area_hectares=8.5,
    soil_moisture=38.0,
    soil_type="sandy_loam",
    irrigation_type="drip",
    growth_stage="tillering",
    eto=5.5,
    language=PromptLanguage.BILINGUAL,
)

async with LLMRouter() as router:
    response = await router.generate(
        prompt=user_prompt,
        system_prompt=system_prompt,
    )
```

### Disease Diagnosis Template

```python
from shared.llm.prompts import format_disease_diagnosis, PromptLanguage

system, user = format_disease_diagnosis(
    crop_type="wheat",
    symptoms="Yellow-orange pustules on leaf surface, early flag leaf stage",
    growth_stage="tillering",
    temperature=18.0,
    humidity=75.0,
    recent_weather="fog and dew for 3 days",
    language=PromptLanguage.ENGLISH,
)
```

### Token Management Utilities

```python
from shared.llm import (
    estimate_tokens,
    check_context_limit,
    truncate_to_token_limit,
    extract_json,
    normalize_arabic,
)

# Estimate token count (handles Arabic at ~2 chars/token)
count = estimate_tokens("متى أسقي القمح؟")

# Check and truncate to model context window
text, truncated = truncate_to_token_limit(long_text, max_tokens=4096)

# Extract JSON from freeform LLM output
result = extract_json('Here is the data: {"ndvi": 0.72, "status": "healthy"}')
if result.success:
    print(result.data)  # {"ndvi": 0.72, "status": "healthy"}

# Normalize Arabic text before sending to model
clean_text = normalize_arabic("مَرحَبًا")  # removes diacritics, normalizes alef
```

---

## Available Prompt Templates

| Template Key | Category | Description |
|--------------|----------|-------------|
| `crop_advisor` | CROP_ADVISORY | General crop management questions |
| `disease_diagnosis` | DISEASE_DIAGNOSIS | Symptom-based disease identification |
| `irrigation_advice` | IRRIGATION | Smart irrigation scheduling |
| `fertilizer_recommendation` | FERTILIZER | Soil-test-based fertilizer plans |
| `pest_control` | PEST_CONTROL | IPM-based pest management |
| `harvest_timing` | HARVEST | Optimal harvest timing |
| `general` | GENERAL | Open-ended agricultural questions |

All templates provide bilingual system and user prompts via `PromptLanguage.ENGLISH`,
`PromptLanguage.ARABIC`, or `PromptLanguage.BILINGUAL`.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Controls routing: `development` prefers local, `production` uses cloud |
| `DEVELOPMENT_MODE` | `true` | Force local models even outside development environment |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_DEFAULT_MODEL` | `llama3.2` | Default model when `model="auto"` in development |
| `OPENAI_COMPAT_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible endpoint URL |
| `OPENAI_COMPAT_MODEL` | `llama3.2` | Model for OpenAI-compatible endpoint |
| `OPENAI_API_KEY` | — | Enables OpenAI cloud fallback |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model for production |
| `ANTHROPIC_API_KEY` | — | Enables Anthropic cloud fallback |
| `ANTHROPIC_MODEL` | `claude-3-haiku-20240307` | Anthropic model for production |

---

## Error Types

| Exception | Trigger |
|-----------|---------|
| `LLMProviderError` | Base error for all provider failures |
| `ProviderUnavailableError` | Provider cannot be reached (timeout, not running) |
| `ModelNotFoundError` | Requested model is not available on the provider |
| `RateLimitError` | API rate limit exceeded |
| `AllProvidersFailedError` | Every provider in the fallback chain failed; includes per-provider error list |
| `OllamaError` | Ollama-specific failures |
| `OpenAICompatError` | OpenAI-compatible endpoint failures |

---

## Integration Points

- **copilot-api** (port 8088): Primary consumer; uses `LLMRouter` for multi-LLM advisory.
- **llm-orchestrator-service** (port 8164): Orchestrates multi-provider routing at the service level.
- **ai-advisor** (port 8112): Agricultural AI advisory powered by prompt templates from this module.
- **shared/ai/ollama_client.py**: Separate Ollama client for the Auto-Fix Engine; uses the same Ollama server.
- **shared/nlp/**: Arabic NLP module; uses `normalize_arabic()` and `detect_language()` from `utils.py`.
