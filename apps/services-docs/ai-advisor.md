# AI Advisor Service Analysis

**Service Name:** ai-advisor
**Type:** Python/FastAPI
**Port:** 8112
**Version:** 1.0.0 (Platform: 16.0.0)
**Description:** Multi-agent AI system for comprehensive agricultural advisory services

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [NATS Events](#nats-events)
5. [AI/ML Model Integration](#aiml-model-integration)
6. [Specialized Agents](#specialized-agents)
7. [External Tools](#external-tools)
8. [RAG System](#rag-system)
9. [Security Features](#security-features)
10. [Dependencies](#dependencies)
11. [Environment Variables](#environment-variables)
12. [Missing Environment Variables](#missing-environment-variables)
13. [Bugs and Recommended Fixes](#bugs-and-recommended-fixes)

---

## Service Overview

The AI Advisor service is a multi-agent AI system for agricultural advisory that provides:

- **Crop Disease Diagnosis**: AI-powered identification and treatment recommendations
- **Field Analysis**: NDVI analysis, satellite imagery interpretation
- **Irrigation Management**: Smart irrigation scheduling and water optimization
- **Yield Prediction**: Data-driven crop yield forecasting
- **RAG Integration**: Knowledge retrieval from agricultural databases
- **Workflow Orchestration**: Complex multi-step agricultural workflows
- **Multi-LLM Support**: Anthropic Claude, OpenAI GPT, Google Gemini, Ollama (local)
- **A2A Protocol Support**: Agent-to-Agent communication for inter-service coordination

### Kong Gateway Routes

| Route | Path | Strip Path |
|-------|------|------------|
| Primary | `/api/v1/ai-advisor` | true |
| Alternate | `/ai-advisor` | true |

---

## Architecture

### Component Diagram

```
+------------------+     +-------------------+     +------------------+
|   API Gateway    |---->|   AI Advisor      |---->| External Tools   |
|     (Kong)       |     |     Service       |     |                  |
+------------------+     +-------------------+     +------------------+
                               |                        |
                               v                        v
                    +-------------------+     +------------------+
                    |   Supervisor      |     | crop-intelligence|
                    |   Orchestration   |     | weather-service  |
                    +-------------------+     | vegetation-      |
                               |              | analysis-service |
                               v              | advisory-service |
                    +-------------------+     +------------------+
                    |   AI Agents       |
                    | - Field Analyst   |
                    | - Disease Expert  |
                    | - Irrigation Adv. |
                    | - Yield Predictor |
                    +-------------------+
                               |
                               v
                    +-------------------+     +------------------+
                    |   RAG System      |---->|     Qdrant       |
                    | - Embeddings      |     | Vector Database  |
                    | - Retriever       |     +------------------+
                    +-------------------+
                               |
                               v
                    +-------------------+
                    | Multi-LLM Provider|
                    | - Anthropic Claude|
                    | - OpenAI GPT      |
                    | - Google Gemini   |
                    | - Ollama (Local)  |
                    +-------------------+
```

### Key Components

| Component | Description |
|-----------|-------------|
| **Supervisor** | Coordinates multiple agents for complex queries |
| **Agents** | Specialized AI agents for different agricultural tasks |
| **RAG System** | Knowledge retrieval with Qdrant vector database |
| **Multi-LLM** | Multi-provider LLM service with automatic fallback |
| **Workflow Manager** | Multi-step workflow orchestration |
| **Context Engineering** | Memory, compression, and evaluation modules |
| **A2A Adapter** | Agent-to-Agent protocol integration |

---

## API Endpoints

### Health Endpoints

#### GET `/healthz`
**Description:** Health check endpoint with dependency validation
**Tags:** Health

**Response:**
```json
{
  "status": "healthy | degraded",
  "service": "ai-advisor",
  "version": "1.0.0",
  "embeddings_ready": true,
  "retriever_ready": true,
  "agents_available": 4
}
```

#### GET `/readyz`
**Description:** Kubernetes readiness probe
**Tags:** Health

**Response:**
```json
{
  "status": "ready",
  "service": "ai-advisor",
  "version": "16.0.0",
  "checks": {
    "service": "ready"
  }
}
```

---

### Advisor Endpoints

#### POST `/v1/advisor/ask`
**Description:** Ask a general question to the AI advisor
**Tags:** Advisor

**Request Schema:**
```json
{
  "question": "string (required)",
  "language": "string (default: 'en', options: 'en' | 'ar')",
  "context": {
    "tenant_id": "string (optional)",
    "field_id": "string (optional)",
    "crop_type": "string (optional)",
    "...": "any additional context"
  }
}
```

**Response Schema (EnhancedAgentResponse):**
```json
{
  "status": "success | error",
  "data": {
    "query": "string",
    "agents_consulted": ["field_analyst", "disease_expert"],
    "agent_responses": { ... },
    "synthesized_answer": "string"
  },
  "error": "string (optional)",
  "compression": {
    "original_tokens": 1000,
    "compressed_tokens": 400,
    "compression_ratio": 0.4,
    "savings_percentage": 60.0,
    "strategy": "hybrid"
  },
  "evaluation": null,
  "memory_stored": true,
  "context_tokens_used": 400
}
```

---

#### POST `/v1/advisor/diagnose`
**Description:** Diagnose crop disease
**Tags:** Advisor

**Request Schema:**
```json
{
  "crop_type": "string (required) - Type of crop (wheat, corn, tomato, etc.)",
  "symptoms": {
    "leaf_color": "string",
    "spots": "boolean",
    "wilting": "boolean",
    "growth_issues": "string",
    "...": "any symptom data"
  },
  "image_path": "string (optional) - Path to crop image for analysis",
  "location": "string (optional) - Field location"
}
```

**Response Schema (AgentResponse):**
```json
{
  "status": "success | error",
  "data": {
    "agent": "disease_expert",
    "role": "Crop Disease Diagnosis and Treatment Specialist",
    "response": "Detailed diagnosis text...",
    "confidence": 0.85
  },
  "error": "string (optional)"
}
```

---

#### POST `/v1/advisor/recommend`
**Description:** Get agricultural recommendations (irrigation, fertilizer, pest control)
**Tags:** Advisor

**Request Schema:**
```json
{
  "crop_type": "string (required) - Type of crop",
  "growth_stage": "string (required) - germination | vegetative | flowering | fruiting | maturity",
  "recommendation_type": "string (required) - irrigation | fertilizer | pest",
  "field_data": {
    "soil": {
      "moisture": 30,
      "type": "clay | loam | sandy",
      "ph": 7.0
    },
    "weather": {
      "temperature": 28,
      "humidity": 65,
      "rainfall_forecast": []
    },
    "tenant_id": "string (optional)",
    "field_id": "string (optional)"
  }
}
```

**Response Schema (EnhancedAgentResponse):**
```json
{
  "status": "success | error",
  "data": { ... },
  "error": null,
  "compression": null,
  "evaluation": {
    "overall_score": 0.85,
    "grade": "GOOD",
    "is_approved": true,
    "feedback": "Recommendation meets quality standards",
    "improvements": ["Consider soil pH levels", "Add timing details"],
    "criteria_scores": {
      "accuracy": 0.9,
      "relevance": 0.85,
      "actionability": 0.8
    }
  },
  "memory_stored": true
}
```

---

#### POST `/v1/advisor/analyze-field`
**Description:** Comprehensive field analysis coordinating multiple agents
**Tags:** Advisor

**Request Schema:**
```json
{
  "field_id": "string (required) - Field identifier",
  "crop_type": "string (required) - Type of crop",
  "include_disease_check": "boolean (default: true)",
  "include_irrigation": "boolean (default: true)",
  "include_yield_prediction": "boolean (default: true)"
}
```

**Response Schema:**
```json
{
  "status": "success",
  "data": {
    "field_id": "FIELD-001",
    "crop_type": "wheat",
    "analysis": {
      "satellite_data": {
        "ndvi": 0.72,
        "data": [...]
      },
      "field_analysis": {
        "agent": "field_analyst",
        "response": "...",
        "confidence": 0.9
      },
      "disease_risk": {
        "agent": "disease_expert",
        "response": "...",
        "confidence": 0.85
      },
      "irrigation_advice": {
        "agent": "irrigation_advisor",
        "response": "...",
        "confidence": 0.88
      },
      "yield_prediction": {
        "agent": "yield_predictor",
        "response": "...",
        "confidence": 0.82
      }
    }
  },
  "compression": { ... },
  "memory_stored": true
}
```

---

#### GET `/v1/advisor/agents`
**Description:** List available AI agents
**Tags:** Advisor

**Response:**
```json
{
  "status": "success",
  "agents": [
    {
      "name": "field_analyst",
      "role": "Field Data Analysis and NDVI Interpretation Expert",
      "has_rag": true,
      "num_tools": 0
    },
    {
      "name": "disease_expert",
      "role": "Crop Disease Diagnosis and Treatment Specialist",
      "has_rag": true,
      "num_tools": 0
    },
    {
      "name": "irrigation_advisor",
      "role": "Irrigation and Water Management Specialist",
      "has_rag": true,
      "num_tools": 0
    },
    {
      "name": "yield_predictor",
      "role": "Crop Yield Prediction and Production Forecasting Specialist",
      "has_rag": true,
      "num_tools": 0
    }
  ],
  "total": 4
}
```

---

#### GET `/v1/advisor/tools`
**Description:** List available external tools
**Tags:** Advisor

**Response:**
```json
{
  "status": "success",
  "tools": ["crop_health", "weather", "satellite", "agro"],
  "total": 4
}
```

---

### RAG Endpoints

#### GET `/v1/advisor/rag/info`
**Description:** Get RAG system information
**Tags:** RAG

**Response:**
```json
{
  "status": "success",
  "collection": {
    "collection_name": "agricultural_knowledge",
    "vectors_count": 1000,
    "points_count": 1000,
    "status": "green"
  },
  "embeddings_model": {
    "model_name": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    "embedding_dimension": 768,
    "device": "cpu",
    "max_sequence_length": 128
  }
}
```

---

### Memory Endpoints

#### GET `/v1/advisor/memory/context`
**Description:** Retrieve relevant context from memory
**Tags:** Memory

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tenant_id` | string (optional) | Tenant identifier |
| `field_id` | string (optional) | Field identifier |
| `query` | string (optional) | Query for relevance matching |
| `max_tokens` | integer (default: 2000) | Maximum tokens to return |

**Response:**
```json
{
  "status": "success",
  "tenant_id": "default",
  "field_id": "FIELD-001",
  "context": "Retrieved memory context...",
  "recent_entries_count": 10,
  "memory_stats": {
    "total_entries": 150,
    "tenants_count": 5,
    "memory_usage_bytes": 50000
  }
}
```

---

### Evaluation Endpoints

#### GET `/v1/advisor/evaluation/stats`
**Description:** Get recommendation evaluation statistics
**Tags:** Evaluation

**Response:**
```json
{
  "status": "success",
  "evaluation_stats": {
    "total_evaluations": 100,
    "approved_count": 85,
    "rejected_count": 15,
    "average_score": 0.82,
    "by_type": {
      "irrigation": { "count": 40, "avg_score": 0.85 },
      "fertilizer": { "count": 30, "avg_score": 0.80 },
      "pest_control": { "count": 30, "avg_score": 0.78 }
    }
  }
}
```

---

### System Endpoints

#### GET `/v1/advisor/context-engineering/status`
**Description:** Get context engineering modules status
**Tags:** System

**Response:**
```json
{
  "status": "success",
  "context_engineering_available": true,
  "modules": {
    "compression": {
      "available": true,
      "type": "ContextCompressor"
    },
    "memory": {
      "available": true,
      "type": "FarmMemory",
      "stats": { ... }
    },
    "evaluation": {
      "available": true,
      "type": "RecommendationEvaluator",
      "stats": { ... }
    }
  }
}
```

---

### Monitoring Endpoints

#### GET `/v1/advisor/cost/usage`
**Description:** Get LLM cost usage statistics
**Tags:** Monitoring

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string (optional) | Filter by user ID |

**Response:**
```json
{
  "status": "success",
  "data": {
    "daily_cost_usd": 15.50,
    "monthly_cost_usd": 350.00,
    "daily_limit_usd": 100.0,
    "monthly_limit_usd": 2000.0,
    "total_requests": 500,
    "daily_remaining_usd": 84.50,
    "monthly_remaining_usd": 1650.00,
    "daily_usage_percent": 15.5,
    "monthly_usage_percent": 17.5
  },
  "user_id": "anonymous"
}
```

---

### A2A Protocol Endpoints (When Available)

#### POST `/a2a/tasks`
**Description:** A2A task endpoint for agent-to-agent communication
**Tags:** A2A

**Capabilities:**
- `crop-disease-diagnosis`
- `irrigation-optimization`
- `yield-prediction`
- `field-analysis`
- `general-agricultural-query`

---

## NATS Events

### Configuration

| Setting | Value |
|---------|-------|
| NATS URL | `nats://nats:4222` |
| Subject Prefix | `sahool.ai-advisor` |

### Events (Planned/Available via Context Engineering)

**Note:** The current implementation has NATS configured but does not actively publish/subscribe to events. The NATS dependency is included for future event-driven capabilities and context engineering memory persistence.

| Event Subject | Direction | Description |
|--------------|-----------|-------------|
| `sahool.ai-advisor.recommendation.created` | Publish | When a recommendation is generated |
| `sahool.ai-advisor.diagnosis.completed` | Publish | When disease diagnosis is completed |
| `sahool.ai-advisor.field.analyzed` | Publish | When field analysis is completed |

---

## AI/ML Model Integration

### Primary LLM Providers

| Provider | Model | Purpose | Status |
|----------|-------|---------|--------|
| **Anthropic Claude** | claude-3-5-sonnet-20241022 | Primary LLM for agent reasoning | Recommended |
| **OpenAI GPT** | gpt-4o | Fallback LLM | Optional |
| **Google Gemini** | gemini-1.5-pro | Alternative | Optional |
| **Ollama** | llama3.2, codellama | Local/Offline deployment | Optional |

### LLM Pricing (per 1K tokens)

| Model | Input | Output |
|-------|-------|--------|
| claude-3-5-sonnet-20241022 | $0.003 | $0.015 |
| claude-3-opus-20240229 | $0.015 | $0.075 |
| gpt-4o | $0.005 | $0.015 |
| gpt-4-turbo | $0.01 | $0.03 |
| gemini-1.5-pro | $0.00125 | $0.005 |
| Ollama (local) | Free | Free |

### Embeddings Model

| Setting | Value |
|---------|-------|
| Model | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` |
| Dimension | 768 |
| Device | CPU (configurable) |
| Purpose | Multilingual embeddings for Arabic/English RAG |

### Multi-Provider Features

- **Automatic Fallback**: If primary provider fails, automatically tries next configured provider
- **Circuit Breaker**: Prevents cascading failures (5 failures = 60s timeout)
- **Retry with Exponential Backoff**: 3 attempts with 2-30s wait
- **Cost Tracking**: Per-request and aggregate cost monitoring
- **Budget Limits**: Daily ($100) and monthly ($2000) configurable limits

---

## Specialized Agents

### 1. Field Analyst Agent

**Name:** `field_analyst`
**Role:** Field Data Analysis and NDVI Interpretation Expert

**Capabilities:**
- NDVI analysis and interpretation
- Satellite imagery assessment
- Field health monitoring
- Temporal trend analysis
- Anomaly detection

**Methods:**
| Method | Description |
|--------|-------------|
| `analyze_field()` | Comprehensive field analysis |
| `interpret_ndvi()` | Interpret NDVI value in context |
| `detect_anomalies()` | Compare current vs baseline data |
| `recommend_monitoring()` | Suggest monitoring strategy |

---

### 2. Disease Expert Agent

**Name:** `disease_expert`
**Role:** Crop Disease Diagnosis and Treatment Specialist

**Capabilities:**
- Disease identification from symptoms
- Image-based disease detection
- Treatment recommendations
- Prevention strategies
- Disease risk assessment

**Methods:**
| Method | Description |
|--------|-------------|
| `diagnose()` | Diagnose disease from symptoms |
| `recommend_treatment()` | Treatment recommendations |
| `assess_risk()` | Disease risk assessment |
| `prevention_strategy()` | Prevention plan development |
| `analyze_progression()` | Disease progression analysis |

---

### 3. Irrigation Advisor Agent

**Name:** `irrigation_advisor`
**Role:** Irrigation and Water Management Specialist

**Capabilities:**
- Irrigation scheduling
- Water requirement calculation
- Soil moisture analysis
- Irrigation system optimization
- Water conservation strategies
- Drought management
- Fertigation advice

**Methods:**
| Method | Description |
|--------|-------------|
| `recommend_irrigation()` | Irrigation schedule and amount |
| `calculate_water_requirement()` | Crop water needs calculation |
| `analyze_soil_moisture()` | Soil moisture sensor analysis |
| `optimize_system()` | System performance optimization |
| `drought_management()` | Drought strategy development |
| `fertigation_advice()` | Fertilizer + irrigation advice |

---

### 4. Yield Predictor Agent

**Name:** `yield_predictor`
**Role:** Crop Yield Prediction and Production Forecasting Specialist

**Capabilities:**
- Yield estimation and forecasting
- Production quality assessment
- Harvest timing recommendations
- Market readiness analysis
- Risk factor identification

**Methods:**
| Method | Description |
|--------|-------------|
| `predict_yield()` | Yield prediction |
| `assess_quality()` | Quality assessment |
| `recommend_harvest_time()` | Optimal harvest timing |
| `analyze_yield_gap()` | Gap analysis |
| `risk_assessment()` | Yield risk assessment |
| `forecast_production()` | Farm production forecast |

---

## External Tools

### 1. Crop Health Tool

**Service:** crop-intelligence-service (Port: 8095)
**Replaces:** Deprecated crop-health-ai

| Method | Endpoint | Description |
|--------|----------|-------------|
| `analyze_image()` | POST `/api/v1/analyze` | Analyze crop image for disease |
| `get_disease_info()` | GET `/api/v1/diseases/{name}` | Get disease information |
| `get_treatment_options()` | GET `/api/v1/diseases/{name}/treatments` | Get treatment options |

---

### 2. Weather Tool

**Service:** weather-service (Port: 8092)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `get_current_weather()` | GET `/api/v1/weather/current` | Current conditions |
| `get_forecast()` | GET `/api/v1/weather/forecast` | Weather forecast |
| `get_historical_weather()` | GET `/api/v1/weather/historical` | Historical data |
| `get_et0()` | GET `/api/v1/weather/et0` | Evapotranspiration |
| `get_alerts()` | GET `/api/v1/weather/alerts` | Weather alerts |

---

### 3. Satellite Tool

**Service:** vegetation-analysis-service (Port: 8090)
**Replaces:** Deprecated satellite-service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `get_ndvi()` | GET `/api/v1/satellite/ndvi` | Get NDVI data |
| `get_field_imagery()` | GET `/api/v1/satellite/imagery` | Satellite imagery |
| `analyze_field_zones()` | POST `/api/v1/satellite/analyze-zones` | Zone analysis |
| `get_time_series()` | GET `/api/v1/satellite/time-series` | Time series data |
| `detect_changes()` | POST `/api/v1/satellite/detect-changes` | Change detection |

---

### 4. Agro Tool

**Service:** advisory-service (Port: 8093)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `get_crop_info()` | GET `/api/v1/crops/{type}` | Crop information |
| `get_growth_stage_info()` | GET `/api/v1/crops/{type}/stages/{stage}` | Growth stage info |
| `get_fertilizer_recommendation()` | POST `/api/v1/fertilizer/recommend` | Fertilizer advice |
| `get_pest_control_advice()` | POST `/api/v1/pest-control/advise` | Pest control |
| `get_best_practices()` | GET `/api/v1/best-practices` | Best practices |
| `get_market_prices()` | GET `/api/v1/market/prices` | Market prices |

---

## RAG System

### Vector Database

**Provider:** Qdrant
**Default Collection:** `agricultural_knowledge`
**Distance Metric:** Cosine

### Components

#### EmbeddingsManager

- Model: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- Supports Arabic and English
- Batch encoding supported
- Similarity calculation methods

#### KnowledgeRetriever

- Document addition with auto-ID generation
- Vector search with score threshold
- Metadata filtering support
- Collection management

### Configuration

| Setting | Default |
|---------|---------|
| `qdrant_host` | `qdrant` |
| `qdrant_port` | 6333 |
| `qdrant_collection` | `agricultural_knowledge` |
| `rag_top_k` | 5 |
| `rag_score_threshold` | 0.7 |

---

## Security Features

### Prompt Injection Guard

**Location:** `src/security/prompt_guard.py`

**Detection Patterns:**
- Ignore/override instructions
- Role manipulation attempts
- System prompt extraction
- Jailbreak attempts
- Code execution attempts
- Data exfiltration attempts
- Arabic injection patterns

**Actions:**
- Input sanitization (null bytes, control characters)
- Whitespace normalization
- Input truncation (max 10,000 characters)
- Warning logging for suspicious inputs
- Optional strict mode rejection

### Rate Limiting

**Location:** `src/middleware/rate_limiter.py`

| Limit | Value |
|-------|-------|
| Requests per minute | 30 |
| Requests per hour | 500 |
| Burst size | 5 |

**Exempt Paths:** `/health`, `/healthz`, `/ready`

### Input Validation Middleware

**Location:** `src/middleware/input_validator.py`

| Limit | Value |
|-------|-------|
| Max body size | 1MB |
| Max query length | 5,000 characters |
| Blocked content types | `application/x-www-form-urlencoded` |

### PII Masking

**Location:** `src/utils/pii_masker.py`

**Masked Patterns:**
- Email addresses
- Phone numbers (including Arabic)
- IP addresses
- Credit card numbers
- SSN
- API keys
- JWT tokens
- Passwords

**Sensitive Fields:**
- password, passwd, pwd
- secret, token, api_key
- authorization, auth, credential
- private_key, access_token, refresh_token
- session_id, cookie, ssn, credit_card

### Token Revocation

- Integration with auth module for token revocation middleware
- Exempt paths for health checks and documentation

---

## Dependencies

### Python Dependencies (requirements.txt)

> **Note:** Exact versions may drift — always refer to
> [`apps/services/ai-advisor/requirements.txt`](../../apps/services/ai-advisor/requirements.txt)
> as the source of truth.

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.135.1 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | 0.41.0 | ASGI server |
| httpx | 0.28.1 | Async HTTP client |
| pydantic | 2.12.5 | Data validation |
| pydantic-settings | 2.13.1 | Settings management |
| langchain | >=0.3.26,<0.4.0 | LLM framework |
| langchain-anthropic | 0.3.22 | Anthropic integration |
| langchain-community | 0.3.31 | Community integrations (CVE fix) |
| langchain-core | 0.3.83 | Core abstractions (CVE fix) |
| anthropic | >=0.41.0,<1.0.0 | Anthropic Claude API |
| openai | >=1.0.0,<2.0.0 | OpenAI GPT API |
| google-generativeai | >=0.3.0 | Google Gemini API |
| sentence-transformers | 5.2.3 | Embeddings |
| qdrant-client | 1.17.0 | Vector database |
| a2a | >=0.1.0 | Agent-to-Agent protocol |
| nats-py | 2.14.0 | NATS messaging |
| python-dotenv | 1.2.2 | Environment loading |
| python-multipart | 0.0.22 | File uploads (CVE fix) |
| aiofiles | 24.1.0 | Async file I/O |
| tenacity | 8.5.0 | Retry logic |
| prometheus-client | 0.24.1 | Metrics |
| structlog | 24.4.0 | Structured logging |
| numpy | >=1.26.0,<2.0.0 | Numerical computing |
| pandas | 2.2.2 | Data processing |
| pytest | 8.4.2 | Testing |
| pytest-asyncio | 0.26.0 | Async testing |
| PyJWT | >=2.10.1,<3.0.0 | JWT authentication |
| cryptography | >=44.0.1,<47.0.0 | Cryptographic operations |
| redis[hiredis] | >=7.1.0,<8.0.0 | Token revocation |

### Internal Dependencies

| Module | Path | Purpose |
|--------|------|---------|
| shared.errors_py | `/app/shared/` | Unified error handling |
| shared.middleware | `/app/shared/` | CORS, logging, tenant context |
| shared.observability | `/app/shared/` | Tracing, metrics |
| shared.ai.context_engineering | `/app/shared/` | Memory, compression, evaluation |
| auth.revocation_middleware | `/app/shared/` | Token revocation |
| a2a.server | `/app/shared/` | A2A protocol support |

---

## Environment Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | None (Required for primary LLM) |

### Service Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_NAME` | Service identifier | `ai-advisor` |
| `SERVICE_PORT` | HTTP port | `8112` |
| `PORT` | Alternative port env | `8112` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SERVICE_BASE_URL` | Base URL for A2A | `http://localhost:8112` |
| `LOG_REQUEST_BODY` | Log request bodies | `false` |

### LLM Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_MULTI_PROVIDER` | Enable multi-provider | `true` |
| `PRIMARY_LLM_PROVIDER` | Primary provider | `anthropic` |
| `ANTHROPIC_API_KEY` | Anthropic API key | None |
| `CLAUDE_MODEL` | Claude model | `claude-3-5-sonnet-20241022` |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `OPENAI_MODEL` | OpenAI model | `gpt-4o` |
| `GOOGLE_API_KEY` | Google API key | None |
| `GEMINI_API_KEY` | Alternative Gemini key | None |
| `GEMINI_MODEL` | Gemini model | `gemini-1.5-pro` |
| `MAX_TOKENS` | Max response tokens | `4096` |
| `TEMPERATURE` | LLM temperature | `0.7` |

### Ollama Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default Ollama model | `llama3.2` |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model | `nomic-embed-text` |

### External Services

| Variable | Description | Default |
|----------|-------------|---------|
| `CROP_HEALTH_AI_URL` | Crop intelligence service | `http://crop-intelligence-service:8095` |
| `WEATHER_CORE_URL` | Weather service | `http://weather-service:8092` |
| `SATELLITE_SERVICE_URL` | Vegetation analysis | `http://vegetation-analysis-service:8090` |
| `AGRO_ADVISOR_URL` | Advisory service | `http://advisory-service:8093` |

### Qdrant Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_HOST` | Qdrant hostname | `qdrant` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `QDRANT_COLLECTION` | Collection name | `agricultural_knowledge` |
| `QDRANT_API_KEY` | Qdrant API key | None |

### NATS Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `NATS_URL` | NATS server URL | `nats://nats:4222` |
| `NATS_SUBJECT_PREFIX` | Event subject prefix | `sahool.ai-advisor` |

### Embeddings Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `EMBEDDINGS_MODEL` | Sentence transformer model | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` |
| `EMBEDDINGS_DEVICE` | Device (cpu/cuda) | `cpu` |

### Agent Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_AGENT_ITERATIONS` | Max agent iterations | `5` |
| `AGENT_TIMEOUT` | Agent timeout (seconds) | `120` |

### RAG Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `RAG_TOP_K` | Documents to retrieve | `5` |
| `RAG_SCORE_THRESHOLD` | Minimum similarity | `0.7` |

### Cache Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_CACHE` | Enable caching | `true` |
| `CACHE_TTL` | Cache TTL (seconds) | `3600` |

---

## Missing Environment Variables

The following environment variables are referenced but may need explicit configuration:

### High Priority (Required for Production)

| Variable | Issue | Recommendation |
|----------|-------|----------------|
| `ANTHROPIC_API_KEY` | Required for primary LLM | Must be set for production |
| `QDRANT_API_KEY` | Optional security | Set if Qdrant requires auth |

### Medium Priority (Recommended for Production)

| Variable | Issue | Recommendation |
|----------|-------|----------------|
| `REDIS_URL` | Required for token revocation | Add to config for Redis connection |
| `DATABASE_URL` | Not used currently | May need for future persistence |

### Low Priority (Nice to Have)

| Variable | Issue | Recommendation |
|----------|-------|----------------|
| `SENTRY_DSN` | Error tracking | Add for production monitoring |
| `OPENTELEMETRY_ENDPOINT` | Distributed tracing | Configure for observability |

---

## Bugs and Recommended Fixes

### 1. CRITICAL: Missing NATS Event Publishing

**Issue:** NATS is configured but no events are published/subscribed.

**Location:** `src/main.py`, `src/config.py`

**Impact:** The service is not participating in the event-driven architecture despite having NATS configured.

**Recommendation:**
```python
# Add NATS connection in lifespan
import nats

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing code ...

    # Initialize NATS
    nats_url = os.getenv("NATS_URL", settings.nats_url)
    if nats_url:
        app.state.nc = await nats.connect(nats_url)
        logger.info("nats_connected", url=nats_url)

    yield

    # Close NATS
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()

# Publish events after recommendations
async def publish_event(subject: str, data: dict):
    if hasattr(app.state, "nc"):
        await app.state.nc.publish(subject, json.dumps(data).encode())
```

---

### 2. MEDIUM: Conversation Memory Not Persisted

**Issue:** `ConversationMemory` in agents uses in-memory storage that is lost on restart.

**Location:** `src/agents/base_agent.py` (lines 24-61)

**Impact:** Conversation context is lost between service restarts.

**Recommendation:**
- Integrate with Redis for persistence
- Use the FarmMemory module from context engineering for persistence

---

### 3. MEDIUM: Missing Error Handling for Tool Failures

**Issue:** External tool calls don't have circuit breaker protection.

**Location:** `src/tools/*.py`

**Impact:** Failed external services can cause cascading failures.

**Recommendation:**
```python
from ..llm.multi_provider import CircuitBreaker

class CropHealthTool:
    def __init__(self):
        self.base_url = settings.crop_health_ai_url
        self.timeout = 30.0
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

    async def analyze_image(self, ...):
        return await self.circuit_breaker.call_async(self._analyze_image_impl, ...)
```

---

### 4. LOW: Hardcoded Growth Stage in Field Analysis

**Issue:** Growth stage is hardcoded as "vegetative" in `analyze_field` endpoint.

**Location:** `src/main.py` (lines 783-788)

**Impact:** Incorrect irrigation and yield predictions for other growth stages.

**Recommendation:**
```python
# Add growth_stage to FieldAnalysisRequest
class FieldAnalysisRequest(BaseModel):
    field_id: str
    crop_type: str
    growth_stage: str = Field(default="vegetative", description="Current growth stage")
    # ... rest of fields
```

---

### 5. LOW: Cost Tracker Not Using User ID Properly

**Issue:** Cost tracking async task doesn't include user_id context.

**Location:** `src/llm/multi_provider.py` (lines 315-321)

**Impact:** Cost tracking is not properly attributed to users.

**Recommendation:**
```python
asyncio.create_task(
    cost_tracker.record_usage(
        model=response.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        user_id=user_context.get("user_id") if user_context else None,
        request_type="chat",
    )
)
```

---

### 6. LOW: Version Mismatch

**Issue:** Service reports version "1.0.0" but platform is 16.0.0.

**Location:** `src/main.py` (lines 203, 341)

**Impact:** Inconsistent version reporting.

**Recommendation:** Update to use a shared version constant:
```python
from .config import settings

# In FastAPI app creation
app = FastAPI(
    title="AI Advisor Service",
    version="16.0.0",  # Match platform version
    ...
)
```

---

### 7. ENHANCEMENT: Add Prometheus Metrics

**Issue:** While `prometheus-client` is installed, no custom metrics are exposed.

**Location:** N/A (missing implementation)

**Recommendation:**
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUESTS_TOTAL = Counter('ai_advisor_requests_total', 'Total requests', ['endpoint', 'status'])
LLM_LATENCY = Histogram('ai_advisor_llm_latency_seconds', 'LLM response latency', ['provider'])
AGENT_TASKS = Counter('ai_advisor_agent_tasks_total', 'Agent tasks executed', ['agent', 'status'])

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

### 8. ENHANCEMENT: Add Input Validation for Crop Types

**Issue:** No validation for valid crop types in requests.

**Location:** `src/main.py`

**Recommendation:**
```python
VALID_CROP_TYPES = ["wheat", "corn", "tomato", "cotton", "rice", "barley", "soybean", ...]

class DiagnoseRequest(BaseModel):
    crop_type: str = Field(..., description="Type of crop")

    @validator('crop_type')
    def validate_crop_type(cls, v):
        if v.lower() not in VALID_CROP_TYPES:
            raise ValueError(f"Invalid crop type. Must be one of: {VALID_CROP_TYPES}")
        return v.lower()
```

---

## Testing

### Test Coverage Structure

```
tests/
├── conftest.py                    # Test fixtures
├── test_api_endpoints.py          # API endpoint tests
├── test_base_agent.py             # Base agent tests
├── test_multi_provider.py         # Multi-LLM provider tests
├── evaluation/
│   ├── conftest.py
│   └── test_golden_dataset.py     # Golden dataset evaluation
├── integration/
│   └── test_api_endpoints.py      # Integration tests
├── mocks/
│   └── test_external_services.py  # Mock service tests
└── unit/
    ├── test_agents.py             # Agent unit tests
    ├── test_base_agent.py
    ├── test_llm_providers.py
    └── test_multi_provider.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py -v
```

---

## File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `src/main.py` | 1117 | FastAPI application, endpoints, middleware |
| `src/config.py` | 84 | Configuration settings |
| `src/agents/base_agent.py` | 329 | Base agent class with Claude integration |
| `src/agents/disease_expert.py` | 258 | Disease diagnosis agent |
| `src/agents/field_analyst.py` | 203 | Field analysis agent |
| `src/agents/irrigation_advisor.py` | 307 | Irrigation advice agent |
| `src/agents/yield_predictor.py` | 319 | Yield prediction agent |
| `src/orchestration/supervisor.py` | 326 | Multi-agent coordination |
| `src/orchestration/workflow.py` | 389 | Workflow orchestration |
| `src/llm/multi_provider.py` | 1045 | Multi-LLM provider with fallback |
| `src/rag/embeddings.py` | 208 | Sentence transformer embeddings |
| `src/rag/retriever.py` | 313 | Qdrant vector retrieval |
| `src/tools/crop_health_tool.py` | 151 | Crop health service integration |
| `src/tools/weather_tool.py` | 260 | Weather service integration |
| `src/tools/satellite_tool.py` | 246 | Satellite/vegetation service integration |
| `src/tools/agro_tool.py` | 266 | Advisory service integration |
| `src/security/prompt_guard.py` | 137 | Prompt injection protection |
| `src/middleware/rate_limiter.py` | 124 | Rate limiting |
| `src/middleware/input_validator.py` | 73 | Input validation |
| `src/monitoring/cost_tracker.py` | 140 | LLM cost tracking |
| `src/utils/pii_masker.py` | 128 | PII masking for logs |
| `src/a2a_adapter.py` | 468 | A2A protocol integration |

---

*Document generated: 2026-01-25*
*Service version: 1.0.0 (Platform: 16.0.0)*
