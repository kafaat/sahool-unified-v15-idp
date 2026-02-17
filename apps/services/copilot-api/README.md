# SAHOOL Copilot API | واجهة المساعد الذكي سهول

[![GitHub](https://img.shields.io/badge/SAHOOL-v16.0.0-blue)](https://github.com/KAFAAT/sahool)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0+-blue)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

Unified AI-powered assistant for the SAHOOL Agricultural Intelligence Platform with multi-LLM support, RAG capabilities, and comprehensive security guardrails.

مساعد ذكي موحد للمنصة الزراعية سهول مع دعم نماذج لغوية متعددة وقدرات البحث المتقدم وحماية شاملة.

---

## Description | الوصف

SAHOOL Copilot API is a production-grade FastAPI service that provides a unified interface to multiple Large Language Models (LLMs) optimized for agricultural operations and code assistance. The service implements an offline-first architecture with Retrieval-Augmented Generation (RAG), multi-provider LLM support, and comprehensive security measures.

**مساعد Copilot لـ SAHOOL** هي خدمة FastAPI جاهزة للإنتاج توفر واجهة موحدة لعدة نماذج لغوية كبيرة (LLMs) مُحسَّنة لعمليات الزراعة والمساعدة البرمجية. تطبق الخدمة معمارية "من الأول بدون اتصال" مع توليد بحث معقد، ودعم موفري LLM متعددين، وتدابير أمان شاملة.

### Key Highlights | الميزات الرئيسية

- **Offline-First**: Full functionality without internet connectivity (Ollama primary, fallback to cloud)
- **Multi-LLM Support**: Ollama (primary), Claude, OpenAI, Gemini, DeepSeek (fallback)
- **RAG System**: Qdrant vector search with sentence-transformers embeddings
- **Tool Guardrails**: Prompt injection detection, request size limits, safety checks
- **Agent Routing**: Specialized agents for code review, agricultural advisory, field operations
- **Chat History**: PostgreSQL persistence with optional offline mode
- **Bilingual**: Full Arabic/English support with automatic language detection
- **Production Ready**: Prometheus metrics, structured logging, health checks, NATS events

---

## Features | الميزات

### Core Capabilities | القدرات الأساسية

| Feature | Details | التفاصيل |
|---------|---------|---------|
| **Chat Interface** | Multi-turn conversations with context preservation | محادثات متعددة الأدوار مع الحفاظ على السياق |
| **RAG (Search)** | Semantic search across agricultural knowledge base | البحث الدلالي عبر قاعدة معارف زراعية |
| **Code Analysis** | Pest/disease detection, code fixes, documentation generation | تحليل الآفات/الأمراض، إصلاحات الكود، توليد التوثيق |
| **Agricultural Advisory** | Crop management, irrigation, pest control recommendations | نصائح إدارة المحاصيل والري ومكافحة الآفات |
| **Tool Management** | Guardrails, rate limiting, audit logging | إدارة الأدوات والحماية والتدقيق |

### Security | الأمان

| Feature | Description | الوصف |
|---------|-------------|-------|
| **Prompt Injection Detection** | Detects and blocks malicious prompt patterns | كشف وحجب أنماط الرسائل الخطرة |
| **Request Validation** | Validates prompt size, file limits, argument constraints | التحقق من حجم الرسالة والملفات والمعاملات |
| **Rate Limiting** | Per-user and per-tenant rate limits with Redis backend | حدود معدل استخدام الموارد لكل مستخدم ومستأجر |
| **Tool Guardrails** | Restricts tool access based on security policies | تقييد الوصول للأدوات بناءً على سياسات الأمان |
| **JWT Authentication** | Token-based API security with configurable expiration | حماية API القائمة على التوكنات |
| **Audit Logging** | All requests logged with user, tenant, and operation context | تسجيل جميع الطلبات مع السياق |

### LLM Providers | موفرو LLM

```
┌─────────────────────────────────────────────────────────┐
│ Primary: Ollama (Offline, No Internet Required)         │
│ - Model: codellama:7b (default), configurable variants  │
│ - GPU: CUDA support, CPU fallback                       │
│ - Latency: ~100-300ms per request                       │
├─────────────────────────────────────────────────────────┤
│ Fallback Providers (Cloud, Requires API Keys):          │
│ - Claude 3.5 Sonnet (Anthropic)                         │
│ - GPT-4o mini (OpenAI)                                  │
│ - Gemini 1.5 Pro (Google)                               │
│ - DeepSeek Coder (DeepSeek)                             │
└─────────────────────────────────────────────────────────┘
```

### RAG System | نظام البحث المتقدم

- **Vector Database**: Qdrant (1.7.x+) with multi-vector support
- **Embeddings**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **Indexing**: Automatic UPSERT with tenant isolation
- **Search**: Semantic similarity with configurable similarity thresholds
- **Caching**: Redis-backed result caching for frequent queries

---

## Architecture | الهندسة المعمارية

### High-Level Diagram | الرسم البياني العام

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│        (Web Dashboard, Mobile App, Admin Portal)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              SAHOOL Copilot API (Port 8088)                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Authentication & Authorization (JWT + Guardrails)   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Chat Router │ RAG Module │ Tools Guard │ Agents    │   │
│  └────────────┬──────────────┬──────────────┬──────────┘   │
│               │              │              │                │
│        ┌──────▼──────┐ ┌────▼────┐ ┌──────▼────────┐       │
│        │   LLM       │ │ Qdrant  │ │  Guard Rules  │       │
│        │  Provider   │ │ Vector  │ │  + Security   │       │
│        │  Router     │ │   DB    │ │   Policies    │       │
│        └──────┬──────┘ └────┬────┘ └──────┬────────┘       │
│               │              │            │                  │
│        ┌──────┴──────────────┴────────────┴──────┐          │
│        │ External Integrations                   │          │
│        ├─────────────────────────────────────────┤          │
│        │ • Ollama (local LLM)                    │          │
│        │ • Claude / OpenAI / Gemini / DeepSeek  │          │
│        │ • PostgreSQL Chat History               │          │
│        │ • Redis Caching & Rate Limiting         │          │
│        │ • NATS Events Publishing                │          │
│        │ • Code-Fix-Agent & AI Advisor Services  │          │
│        └─────────────────────────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow | سير الطلب

```
1. CLIENT REQUEST
   ↓
2. AUTHENTICATION → Validate JWT token → Extract user/tenant ID
   ↓
3. REQUEST VALIDATION
   ├─ Check prompt size (<12,000 chars)
   ├─ Detect prompt injection attacks
   ├─ Validate file count and sizes
   └─ Apply rate limiting (Redis backend)
   ↓
4. AGENT ROUTING
   ├─ Classify intent (code, advisory, chat, etc.)
   └─ Route to specialized agent
   ↓
5. CONTEXT BUILDING
   ├─ Retrieve chat history (PostgreSQL)
   ├─ RAG search in Qdrant (if enabled)
   └─ Compile context window
   ↓
6. LLM SELECTION
   ├─ Primary: Ollama (offline, always available)
   └─ Fallback: Claude/OpenAI/Gemini/DeepSeek (if configured)
   ↓
7. INFERENCE
   ├─ Generate response (30s timeout)
   └─ Stream or batch return
   ↓
8. POST-PROCESSING
   ├─ Save to chat history (if DB available)
   ├─ Publish NATS events (copilot.chat.completed)
   └─ Log to audit trail
   ↓
9. RESPONSE
   ├─ JSON (streaming or chunked)
   └─ Include metadata (latency, tokens, provider)
```

### Module Organization | تنظيم الوحدات

```
apps/services/copilot-api/
├── src/
│   ├── main.py                    # FastAPI app factory + lifespan
│   ├── api/
│   │   ├── deps.py               # Dependency injection
│   │   └── v1/
│   │       ├── chat.py           # POST /chat, /chat/stream, /chat/message
│   │       ├── rag.py            # POST /rag/search, /rag/index
│   │       ├── tools.py          # POST /tools/validate, /tools/execute
│   │       └── health.py         # GET /healthz, /readyz, /health, /metrics
│   ├── core/
│   │   ├── config.py             # Settings management
│   │   └── agents.py             # Agent router (code, advisory, etc.)
│   ├── db/
│   │   └── chat_store.py         # Chat history persistence
│   ├── rag/
│   │   ├── embeddings.py         # sentence-transformers wrapper
│   │   ├── search.py             # Qdrant vector search
│   │   └── indexer.py            # Document indexing
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   ├── security/
│   │   ├── guards.py             # Tool guardrails + policy engine
│   │   └── prompt_guard.py       # Prompt injection detection
│   └── events/
│       └── publisher.py          # NATS event publishing
├── tests/
│   ├── test_chat.py
│   ├── test_rag.py
│   ├── test_guards.py
│   └── test_health.py
├── Dockerfile                    # Multi-stage build
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

### Data Flow | تدفق البيانات

```
Chat Message (JSON)
    ↓ (FastAPI)
ChatRequest (Pydantic)
    ↓ (Validation)
GuardResult (Approved/Denied)
    ↓ (Auth)
AuthenticatedUser + Tenant
    ↓ (History Retrieval)
ChatHistory (PostgreSQL)
    ↓ (RAG Search)
RelevantDocuments (Qdrant)
    ↓ (Context Building)
PromptWithContext
    ↓ (LLM Inference)
Response (from Ollama/Claude/etc.)
    ↓ (Postprocessing)
ChatMessage (saved to DB)
    ↓ (NATS Publish)
Event (copilot.chat.completed)
    ↓ (JSON Response)
ChatResponse to Client
```

---

## API Endpoints | نقاط النهاية

All endpoints are versioned under `/api/v1/`.

جميع نقاط النهاية مرقمة تحت `/api/v1/`.

### Health & Monitoring | الصحة والمراقبة

```http
GET /healthz
GET /readyz
GET /health
GET /metrics
GET /info
GET /docs
GET /openapi.json
```

| Endpoint | Method | Description | الوصف |
|----------|--------|-------------|-------|
| `/healthz` | GET | Liveness probe - quick health check | فحص الحياة السريع |
| `/readyz` | GET | Readiness probe - full dependency check | فحص الجاهزية الكامل |
| `/health` | GET | Combined health check (alias to readiness) | فحص صحة مجمع |
| `/metrics` | GET | Prometheus metrics (guard checks, blocked calls) | مقاييس Prometheus |
| `/info` | GET | Service info, features, available LLM providers | معلومات الخدمة |
| `/docs` | GET | Swagger UI interactive documentation | توثيق Swagger التفاعلي |
| `/openapi.json` | GET | OpenAPI 3.0 schema | مخطط OpenAPI |

**Response Example** (health):

```json
{
  "status": "ok",
  "service": "copilot-api",
  "version": "1.0.0",
  "mode": "offline",
  "components": {
    "rag": true,
    "qdrant": true,
    "redis": true,
    "nats": true
  },
  "timestamp": "2026-01-20T10:30:00Z"
}
```

### Chat Endpoints | نقاط المحادثة

```http
POST /api/v1/chat
POST /api/v1/chat/stream
POST /api/v1/chat/message
DELETE /api/v1/chat/{session_id}
```

#### POST /api/v1/chat

Main chat endpoint with RAG integration and agent routing.

نقطة نهاية المحادثة الرئيسية مع البحث المتقدم وتوجيه الوكلاء.

**Request** (JSON):

```json
{
  "message": "كيفية معالجة أوراق القمح الصفراء؟",
  "session_id": "session_uuid",
  "context": {
    "field_id": "FIELD-001",
    "crop_type": "wheat",
    "stage": "tillering"
  },
  "enable_rag": true,
  "language": "ar"
}
```

**Response** (JSON):

```json
{
  "message_id": "msg_uuid",
  "response": "يُشير تلون أوراق القمح بالأصفر إلى نقص النيتروجين. يُنصح بتطبيق اليوريا 46% بمعدل 46 كجم/هـ مع الري الخفيف...",
  "provider": "ollama",
  "model": "codellama:7b",
  "tokens": {
    "input": 245,
    "output": 156
  },
  "rag_results": [
    {
      "score": 0.92,
      "content": "Nitrogen deficiency in wheat causes leaf yellowing...",
      "source": "advisory_kb"
    }
  ],
  "latency_ms": 1234,
  "session_id": "session_uuid",
  "timestamp": "2026-01-20T10:30:00Z"
}
```

#### POST /api/v1/chat/stream

Streaming response endpoint (Server-Sent Events).

نقطة نهاية الاستجابة المتدفقة (SSE).

```bash
curl -N -X POST http://localhost:8088/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"message": "Hello"}'
```

**Response** (text/event-stream):

```
data: {"token": "Hello", "latency_ms": 45}
data: {"token": " how", "latency_ms": 78}
data: {"token": " are", "latency_ms": 65}
data: [DONE]
```

#### POST /api/v1/chat/message

Create a new message in an existing session.

إنشاء رسالة جديدة في جلسة موجودة.

**Request**:

```json
{
  "session_id": "session_uuid",
  "message": "What about watering frequency?",
  "role": "user"
}
```

**Response**: ChatResponse (same as /chat)

#### DELETE /api/v1/chat/{session_id}

Clear chat history for a session.

مسح سجل المحادثات لجلسة معينة.

```bash
curl -X DELETE http://localhost:8088/api/v1/chat/session_uuid \
  -H "Authorization: Bearer TOKEN"
```

### RAG Endpoints | نقاط البحث المتقدم

```http
POST /api/v1/rag/search
POST /api/v1/rag/index
DELETE /api/v1/rag/index/{collection}
GET /api/v1/rag/stats
```

#### POST /api/v1/rag/search

Semantic search across indexed documents.

البحث الدلالي عن المستندات المفهرسة.

**Request**:

```json
{
  "query": "How to manage soil salinity?",
  "top_k": 5,
  "similarity_threshold": 0.7,
  "filters": {
    "crop_type": "wheat",
    "region": "yemen"
  }
}
```

**Response**:

```json
{
  "query": "How to manage soil salinity?",
  "results": [
    {
      "id": "doc_001",
      "content": "Soil salinity management...",
      "similarity": 0.94,
      "metadata": {
        "source": "agricultural_handbook",
        "crop": "wheat",
        "region": "yemen"
      }
    }
  ],
  "execution_time_ms": 245
}
```

#### POST /api/v1/rag/index

Add documents to RAG knowledge base.

إضافة مستندات إلى قاعدة معارف البحث المتقدم.

**Request**:

```json
{
  "documents": [
    {
      "id": "doc_001",
      "content": "Nitrogen deficiency in wheat...",
      "metadata": {
        "crop": "wheat",
        "topic": "fertilizer",
        "source": "advisory"
      }
    }
  ],
  "collection": "sahool_copilot_knowledge"
}
```

**Response**:

```json
{
  "indexed": 1,
  "failed": 0,
  "collection": "sahool_copilot_knowledge"
}
```

#### GET /api/v1/rag/stats

Get RAG system statistics.

الحصول على إحصائيات نظام البحث المتقدم.

```json
{
  "qdrant_available": true,
  "collection_count": 1,
  "collections": {
    "sahool_copilot_knowledge": {
      "vector_count": 2450,
      "vector_size": 384,
      "memory_mb": 125.3
    }
  }
}
```

### Tool & Guard Endpoints | نقاط الأدوات والحماية

```http
POST /api/v1/tools/validate
POST /api/v1/tools/execute
GET /api/v1/tools/registry
GET /api/v1/tools/policies
```

#### POST /api/v1/tools/validate

Validate a tool request against guardrails.

التحقق من طلب أداة مقابل سياسات الحماية.

**Request**:

```json
{
  "tool_name": "run_code_fix",
  "arguments": {
    "files": ["service.py"],
    "rules": ["E501", "F401"]
  }
}
```

**Response**:

```json
{
  "allowed": true,
  "tool_name": "run_code_fix",
  "risk_level": "low",
  "reasons": []
}
```

#### POST /api/v1/tools/execute

Execute a tool with guard validation.

تنفيذ أداة مع التحقق من الحماية.

**Request**: Same as validate + execution parameters

**Response**:

```json
{
  "execution_id": "exec_uuid",
  "status": "success",
  "result": { "fixed_files": 2, "issues": 5 },
  "execution_time_ms": 5432
}
```

#### GET /api/v1/tools/registry

List available tools.

قائمة الأدوات المتاحة.

```json
{
  "tools": [
    {
      "name": "run_code_fix",
      "description": "Run code fixes using auto-fix engine",
      "requires_approval": false,
      "risk_level": "low"
    },
    {
      "name": "generate_documentation",
      "description": "Generate API documentation",
      "requires_approval": false,
      "risk_level": "low"
    }
  ]
}
```

---

## Environment Variables | متغيرات البيئة

All environment variables are loaded from `.env` file or system environment. Default values are provided.

يتم تحميل جميع متغيرات البيئة من ملف `.env` أو متغيرات النظام. يتم توفير القيم الافتراضية.

### Service Configuration | إعدادات الخدمة

```bash
# Service Details
SERVICE_NAME=copilot-api
SERVICE_VERSION=16.0.0
ENVIRONMENT=development|staging|production
DEBUG=false
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR

# Server
HOST=0.0.0.0
PORT=8088
WORKERS=4  # Only in production
```

### Security | الأمان

```bash
# JWT
JWT_SECRET_KEY=your-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# API Key (optional)
API_KEY=your-optional-api-key

# CORS
CORS_ORIGINS_LIST=http://localhost:3000,http://localhost:8080
```

### Copilot Settings | إعدادات المساعد الذكي

```bash
# Mode
COPILOT_MODE=offline|online
ENABLE_EXTERNAL=false|true  # Enable cloud LLM providers

# Limits
MAX_PROMPT_CHARS=12000
MAX_ARGS_SIZE=20000
REQUEST_TIMEOUT_S=30.0
MAX_FILES_CHANGED=20
```

### Ollama (Local LLM) | أولاما (نموذج لغوي محلي)

```bash
# Primary provider (offline-first)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:7b
# Alternative models: codellama:13b, mistral:7b, llama2:7b, deepseek-coder:6.7b
```

### Cloud LLM Providers (Optional) | موفرو LLM السحابيين (اختياري)

```bash
# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Google (Gemini)
GOOGLE_API_KEY=AIzaSy...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# OpenAI (or compatible)
EXTERNAL_LLM_BASE_URL=https://api.openai.com/v1
EXTERNAL_LLM_API_KEY=sk-...
EXTERNAL_LLM_MODEL=gpt-4o-mini
EXTERNAL_LLM_TEMPERATURE=0.2
```

### Qdrant (Vector Database) | قاعدة بيانات المتجهات

```bash
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=sahool_copilot_knowledge
USE_QDRANT=true

# Alternative: Milvus
# MILVUS_HOST=localhost
# MILVUS_PORT=19530
```

### Embeddings | التضمينات

```bash
# Sentence Transformers (local, offline)
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
# Alternative: all-MiniLM-L6-v2, all-mpnet-base-v2
```

### Database (PostgreSQL) | قاعدة البيانات

```bash
# Chat History Persistence (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/sahool?sslmode=require
# Format: postgresql://[user[:password]@][netloc][:port][/dbname]
```

### Redis | ريديس

```bash
# Caching & Rate Limiting
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password  # Optional
```

### NATS | ناتس

```bash
# Event Publishing
NATS_URL=nats://localhost:4222
```

### Internal Service URLs | عناوين الخدمات الداخلية

```bash
# Code-Fix-Agent Service
CODE_FIX_AGENT_URL=http://localhost:8161

# AI Advisor Service
AI_ADVISOR_URL=http://localhost:8112

# Field Management Service
FIELD_MANAGEMENT_URL=http://localhost:3000

# Weather Service
WEATHER_SERVICE_URL=http://localhost:8108
```

### Example .env File | ملف .env النموذجي

```bash
# ═══════════════════════════════════════════════════════════
# SAHOOL Copilot API Configuration
# ═══════════════════════════════════════════════════════════

# Service
ENVIRONMENT=development
LOG_LEVEL=INFO
PORT=8088

# Security
JWT_SECRET_KEY=your-32-character-minimum-secret-key-here
CORS_ORIGINS_LIST=http://localhost:3000,http://localhost:8080

# Copilot
COPILOT_MODE=offline
ENABLE_EXTERNAL=false
MAX_PROMPT_CHARS=12000

# Ollama (Primary Provider)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:7b

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
USE_QDRANT=true

# PostgreSQL (optional)
DATABASE_URL=postgresql://sahool:password@localhost:5432/sahool?sslmode=require

# Redis (optional)
REDIS_URL=redis://localhost:6379

# NATS
NATS_URL=nats://localhost:4222

# Internal Services
CODE_FIX_AGENT_URL=http://localhost:8161
AI_ADVISOR_URL=http://localhost:8112
```

---

## Events (NATS) | الأحداث

The Copilot API publishes events to NATS for integration with other platform services.

تنشر واجهة Copilot الأحداث إلى NATS للتكامل مع خدمات المنصة الأخرى.

### Event Subjects | مواضيع الأحداث

All events follow the pattern: `sahool.{domain}.{action}`

جميع الأحداث تتبع النمط: `sahool.{domain}.{action}`

```yaml
Copilot Events:
  copilot.chat.started:
    description: Chat session initiated
    payload:
      user_id: UUID
      session_id: UUID
      tenant_id: UUID
      timestamp: ISO8601
      mode: "offline|online"

  copilot.chat.message_received:
    description: User message received
    payload:
      message_id: UUID
      session_id: UUID
      user_id: UUID
      message: String
      language: "ar|en"
      token_count: Int

  copilot.chat.response_generated:
    description: Copilot generated response
    payload:
      response_id: UUID
      session_id: UUID
      provider: "ollama|claude|openai|gemini|deepseek"
      model: String
      tokens_used: {input: Int, output: Int}
      latency_ms: Int
      rag_used: Boolean
      agent: String (code|advisory|chat|etc)

  copilot.chat.completed:
    description: Chat exchange completed
    payload:
      session_id: UUID
      message_count: Int
      total_tokens: Int
      duration_ms: Int
      user_id: UUID
      tenant_id: UUID

  copilot.guard.violation:
    description: Security guard violation detected
    payload:
      violation_id: UUID
      violation_type: String
      user_id: UUID
      tenant_id: UUID
      details: Object
      timestamp: ISO8601
      severity: "warning|error|critical"

  copilot.rag.search_performed:
    description: RAG search executed
    payload:
      search_id: UUID
      query: String
      results_count: Int
      execution_time_ms: Int
      collection: String

  copilot.tool.executed:
    description: Tool executed successfully
    payload:
      tool_name: String
      execution_id: UUID
      status: "success|failed"
      duration_ms: Int
      user_id: UUID
      tenant_id: UUID
```

### Publishing Events | نشر الأحداث

Events are automatically published by the service. To subscribe:

```python
import nats

nc = await nats.connect("nats://localhost:4222")

# Subscribe to all copilot events
sub = await nc.subscribe("sahool.copilot.*")

async for msg in sub.messages:
    data = json.loads(msg.data)
    print(f"Event: {msg.subject}, Data: {data}")
```

---

## Docker | دوكر

### Build | البناء

```bash
# Build the image
docker build -f Dockerfile -t sahool-copilot-api:latest .

# Build with Python 3.12
docker build --build-arg PYTHON_VERSION=3.12 \
  -f Dockerfile -t sahool-copilot-api:py312 .
```

### Run | التشغيل

```bash
# Run in offline mode (Ollama only)
docker run -d \
  --name copilot-api \
  -p 8088:8088 \
  -e ENVIRONMENT=development \
  -e COPILOT_MODE=offline \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -e QDRANT_HOST=qdrant \
  -e NATS_URL=nats://nats:4222 \
  sahool-copilot-api:latest

# Run with cloud LLM fallback
docker run -d \
  --name copilot-api \
  -p 8088:8088 \
  -e ENVIRONMENT=production \
  -e COPILOT_MODE=online \
  -e ENABLE_EXTERNAL=true \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -e QDRANT_HOST=qdrant \
  -e DATABASE_URL=postgresql://... \
  sahool-copilot-api:latest
```

### Docker Compose | تركيبة دوكر

```yaml
version: '3.8'

services:
  copilot-api:
    build: ./apps/services/copilot-api
    container_name: copilot-api
    ports:
      - "8088:8088"
    environment:
      ENVIRONMENT: development
      COPILOT_MODE: offline
      OLLAMA_BASE_URL: http://ollama:11434
      QDRANT_HOST: qdrant
      QDRANT_PORT: 6333
      NATS_URL: nats://nats:4222
      REDIS_URL: redis://redis:6379
      DATABASE_URL: postgresql://sahool:password@postgres:5432/sahool?sslmode=disable
    depends_on:
      - ollama
      - qdrant
      - redis
      - nats
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8088/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    # Pre-pull model on startup
    command: serve

  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"

  nats:
    image: nats:latest
    container_name: nats
    ports:
      - "4222:4222"
      - "6222:6222"
      - "8222:8222"

  postgres:
    image: postgres:16-alpine
    container_name: postgres
    environment:
      POSTGRES_USER: sahool
      POSTGRES_PASSWORD: password
      POSTGRES_DB: sahool
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  ollama_data:
  qdrant_data:
  postgres_data:
```

### Health Checks | فحص الصحة

```bash
# Liveness check
curl http://localhost:8088/healthz
# Returns: {"status": "ok", ...}

# Readiness check
curl http://localhost:8088/readyz
# Returns: {"status": "ok|degraded", "components": {...}}

# Service info
curl http://localhost:8088/info
# Returns: Full service configuration and feature status
```

---

## Testing | الاختبار

### Unit Tests | اختبارات الوحدة

```bash
# Run all unit tests
pytest tests/test_*.py -v

# Run specific test file
pytest tests/test_chat.py -v

# With coverage report
pytest tests/ --cov=src --cov-report=html

# Run markers
pytest -m unit
pytest -m integration
```

### Integration Tests | اختبارات التكامل

```bash
# Requires running services (Ollama, Qdrant, Redis, NATS, PostgreSQL)
pytest tests/integration/ -v

# With coverage
pytest tests/integration/ --cov=src
```

### Manual Testing | الاختبار اليدوي

```bash
# Using curl
curl -X POST http://localhost:8088/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "كيفية معالجة أمراض القمح؟",
    "language": "ar"
  }'

# Using Python requests
python
import requests
response = requests.post(
    "http://localhost:8088/api/v1/chat",
    json={"message": "Hello", "language": "en"},
    headers={"Authorization": "Bearer TOKEN"}
)
print(response.json())
```

### Test Coverage Requirements | متطلبات تغطية الاختبار

- **Minimum**: 25% (enforced in CI)
- **Target**: 70%+
- **Critical paths**: 90%+ (auth, guards, RAG)

### Running Tests with Docker | تشغيل الاختبارات مع دوكر

```bash
# Start services
docker-compose -f docker-compose.test.yml up -d

# Run tests
docker-compose -f docker-compose.test.yml run copilot-api pytest tests/

# Cleanup
docker-compose -f docker-compose.test.yml down
```

---

## Development | التطوير

### Setup | الإعداد

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env with your configuration

# 4. Start dependencies (Docker recommended)
docker-compose up -d ollama qdrant redis nats postgres

# 5. Initialize database (if using PostgreSQL)
# Migrations handled by startup script

# 6. Run service
python -m uvicorn src.main:app --reload
```

### Project Structure | هيكل المشروع

```
copilot-api/
├── src/
│   ├── main.py                 # FastAPI app factory
│   ├── __init__.py
│   ├── api/
│   │   ├── deps.py            # Dependency injection (auth, guards)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py        # Chat endpoints
│   │   │   ├── rag.py         # RAG endpoints
│   │   │   ├── tools.py       # Tools & guards
│   │   │   └── health.py      # Health & metrics
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py          # Settings (Pydantic)
│   │   ├── agents.py          # Agent routing
│   │   └── __init__.py
│   ├── db/
│   │   ├── chat_store.py      # Chat history DB ops
│   │   └── __init__.py
│   ├── models/
│   │   ├── schemas.py         # Pydantic models
│   │   └── __init__.py
│   ├── rag/
│   │   ├── embeddings.py      # Embeddings wrapper
│   │   ├── search.py          # Qdrant search
│   │   ├── indexer.py         # Document indexing
│   │   └── __init__.py
│   ├── security/
│   │   ├── guards.py          # Tool guardrails
│   │   ├── prompt_guard.py    # Prompt injection detection
│   │   └── __init__.py
│   └── events/
│       ├── publisher.py       # NATS publisher
│       └── __init__.py
├── tests/
│   ├── test_chat.py
│   ├── test_rag.py
│   ├── test_guards.py
│   ├── test_health.py
│   ├── conftest.py            # Pytest fixtures
│   └── __init__.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

### Common Development Tasks | مهام التطوير الشائعة

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/
mypy src/

# Run service with auto-reload
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8088

# Debug with pdb
python -m pdb -m uvicorn src.main:app

# Interactive shell with app context
python -c "from src.main import app; import asyncio; asyncio.run(...)"
```

### Debugging Tips | نصائح التصحيح

```python
# Enable debug logging
export LOG_LEVEL=DEBUG

# Access app state
from fastapi import Request
@app.get("/debug")
async def debug(request: Request):
    settings = request.app.state.settings
    audit_logger = request.app.state.audit_logger
    return {"settings": settings.dict(), "audit": audit_logger is not None}

# Check RAG stats
from src.rag import get_rag_service
rag = get_rag_service()
stats = await rag.get_stats()
print(f"Qdrant status: {stats}")
```

### Common Issues | المشاكل الشائعة

| Issue | Solution | الحل |
|-------|----------|-----|
| Ollama connection refused | Ensure Ollama running: `ollama serve` | تأكد من تشغيل Ollama |
| Qdrant connection error | Check host/port, ensure service running | تحقق من الخادم والمنفذ |
| Prompt too large error | Reduce message length or increase `MAX_PROMPT_CHARS` | قلل طول الرسالة |
| Token limit exceeded | Check context window, reduce history | قلل النافذة السياقية |
| Import errors | `pip install -r requirements.txt` again | أعد التثبيت |
| JWT token invalid | Generate new token with valid secret | توليد رمز جديد |

---

## Monitoring & Observability | المراقبة والملاحظة

### Metrics | المقاييس

Prometheus metrics available at `GET /metrics`:

```
# HELP copilot_guard_checks_total Total guard validation checks
# TYPE copilot_guard_checks_total counter
copilot_guard_checks_total{service="copilot-api"} 1523

# HELP copilot_guard_allowed_total Total allowed requests
# TYPE copilot_guard_allowed_total counter
copilot_guard_allowed_total{service="copilot-api"} 1501

# HELP copilot_guard_blocked_total Total blocked requests
# TYPE copilot_guard_blocked_total counter
copilot_guard_blocked_total{service="copilot-api"} 22

# Custom metrics can be added:
copilot_chat_duration_seconds{model="ollama", status="success"} 1.234
copilot_rag_search_latency_ms{collection="sahool_copilot_knowledge"} 245
copilot_llm_token_usage{provider="ollama", model="codellama:7b"} 5432
```

### Logging | التسجيل

Structured JSON logging with context:

```json
{
  "timestamp": "2026-01-20T10:30:45.123Z",
  "level": "INFO",
  "logger": "src.api.v1.chat",
  "message": "Chat request processed",
  "request_id": "req_uuid",
  "user_id": "user_uuid",
  "tenant_id": "tenant_uuid",
  "session_id": "session_uuid",
  "provider": "ollama",
  "model": "codellama:7b",
  "tokens_used": {"input": 245, "output": 156},
  "latency_ms": 1234
}
```

### Tracing | التتبع

OpenTelemetry integration (optional):

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

---

## Troubleshooting | استكشاف الأخطاء

### Service Won't Start | الخدمة لن تبدأ

```bash
# Check logs
docker logs copilot-api

# Common causes:
# 1. Port already in use
lsof -i :8088
# Kill process: kill -9 <PID>

# 2. Missing dependencies
pip install -r requirements.txt

# 3. Invalid environment variables
cat .env
# Check syntax: KEY=VALUE (no spaces around =)
```

### Chat Returns No Response | المحادثة لا ترد

```bash
# 1. Check Ollama
curl http://localhost:11434/api/tags
# Should list available models

# 2. Check model is loaded
ollama pull codellama:7b

# 3. Check logs
docker logs ollama

# 4. Check resource usage
docker stats ollama
# If memory/CPU maxed out, reduce model size
```

### RAG Search Returns No Results | البحث لا يرجع نتائج

```bash
# 1. Check Qdrant
curl http://localhost:6333/health

# 2. Check collection exists
curl http://localhost:6333/collections

# 3. Index documents
curl -X POST http://localhost:8088/api/v1/rag/index \
  -H "Authorization: Bearer TOKEN" \
  -d '{...}'

# 4. Check stats
curl http://localhost:8088/api/v1/rag/stats
```

### Guard Violations / Blocked Requests | الطلبات المحجوبة

```bash
# Check guard logs
grep "guard.violation" /var/log/copilot-api.log

# View block statistics
curl http://localhost:8088/metrics | grep guard_blocked

# Temporarily disable (dev only)
ENABLE_GUARDS=false  # In .env

# Common violations:
# - Prompt too large (>12000 chars)
# - Prompt injection detected
# - Rate limit exceeded
# - Invalid tool request
```

---

## Performance Tuning | ضبط الأداء

### Ollama Optimization | تحسين أولاما

```bash
# Use smaller model (faster inference)
OLLAMA_MODEL=codellama:7b  # ~18GB, 300ms latency
OLLAMA_MODEL=mistral:7b    # ~16GB, 250ms latency
OLLAMA_MODEL=neural-chat:7b # ~13GB, 200ms latency

# Enable GPU (if available)
# CUDA: Automatic with NVIDIA GPU
# Metal (Mac): Automatic with Apple Silicon
# AMD (ROCm): docker run -e CUDA_VISIBLE_DEVICES=0 ...

# Increase context window
# In Ollama config: context_size=4096
```

### RAG Optimization | تحسين البحث المتقدم

```bash
# Increase Qdrant resources
docker run -d \
  -p 6333:6333 \
  -e QDRANT_TELEMETRY_DISABLED=true \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Use smaller embeddings model
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Faster, less memory

# Reduce search scope
top_k=5  # Instead of 10
similarity_threshold=0.8  # Higher = stricter
```

### Database Optimization | تحسين قاعدة البيانات

```bash
# PostgreSQL connection pooling (PgBouncer)
# In docker-compose:
pgbouncer:
  image: edoburu/pgbouncer
  environment:
    - DATABASES_HOST=postgres
    - PGBOUNCER_POOL_MODE=transaction
    - PGBOUNCER_DEFAULT_POOL_SIZE=25

# Use connection string
DATABASE_URL=postgresql://user:pass@pgbouncer:6432/sahool
```

### Caching Strategy | استراتيجية التخزين المؤقت

```bash
# Redis caching (if available)
REDIS_URL=redis://localhost:6379

# Cache configurations:
- Chat history: 1 hour TTL
- RAG search results: 30 minutes TTL
- LLM responses: 24 hours TTL (for identical prompts)
```

---

## Contributing | المساهمة

Contributions are welcome! Please follow these guidelines:

1. **Code Style**: Follow PEP 8, use `black` for formatting
2. **Testing**: Write tests for new features (minimum 25% coverage)
3. **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`, etc.)
4. **Documentation**: Update README and inline comments
5. **Security**: Run `bandit` and `safety` before submitting PR

```bash
# Before committing
black src/ tests/
isort src/ tests/
ruff check src/ tests/
mypy src/
pytest tests/ --cov=src
```

---

## License | الترخيص

SAHOOL Copilot API is proprietary software. All rights reserved by KAFAAT.

**واجهة Copilot API** برمجية احتكارية. جميع الحقوق محفوظة لـ KAFAAT.

---

## Support | الدعم

For issues, questions, or feature requests:

- **GitHub Issues**: [SAHOOL Repository](https://github.com/KAFAAT/sahool/issues)
- **Email**: support@sahool.app
- **Documentation**: [SAHOOL Docs](https://docs.sahool.app)
- **Community**: [SAHOOL Community](https://community.sahool.app)

---

## Version History | سجل الإصدارات

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-20 | Initial release with Ollama, Claude, RAG, guardrails |
| 0.9.0 | 2025-12-15 | Beta: Core chat, basic RAG support |
| 0.8.0 | 2025-11-01 | Alpha: FastAPI foundation, health checks |

---

## Additional Resources | موارد إضافية

- [SAHOOL Platform Documentation](https://docs.sahool.app)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Models](https://ollama.ai/library)
- [Qdrant Vector Database](https://qdrant.tech/)
- [Sentence Transformers](https://www.sbert.net/)
- [NATS Documentation](https://docs.nats.io/)
- [PostgreSQL Guide](https://www.postgresql.org/docs/)

---

**Last Updated**: January 2026
**Status**: Production Ready ✅
**Maintainer**: SAHOOL Platform Team
