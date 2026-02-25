# AI Chat Assistant Service

**Port**: 8260 | **Type**: Python (FastAPI) | **Version**: 1.0.0

Lightweight AI assistant integration for SAHOOL chat services. Delivers intelligent, real-time agricultural advisory through chat interfaces with bilingual Arabic and English support and a 70%+ cache hit rate via semantic Redis caching.

---

## Overview

`ai-chat-assistant` bridges the `chat-service` and the `llm-orchestrator-service` using NATS event subscriptions. When a user mentions `@ai` in a chat message, the chat service publishes a NATS event; this service processes it asynchronously, checks the semantic cache, routes to the LLM orchestrator if needed, and publishes the response back. It never modifies the chat-service protocol.

---

## Architecture

```
User Message (@ai mention)
    → chat-service (Socket.IO)
        → NATS: sahool.chat.ai_query
            → ai-chat-assistant
                ├── Cache Manager (Redis, exact + semantic match)
                │       Hit (70%) → return cached response
                │       Miss (30%) → LLM Orchestrator Client
                │                       → llm-orchestrator-service (8164)
                │                           → AI Agents
                └── NATS: sahool.chat.ai_response
                    → chat-service → User
```

---

## API Endpoints

This service is primarily event-driven via NATS and does not expose domain REST endpoints. HTTP endpoints are limited to health and observability.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe (Redis + NATS + LLM orchestrator) |
| GET | `/health` | Combined status with cache statistics |
| GET | `/metrics` | Prometheus metrics (plaintext) |

---

## NATS Events

### Subscribed

**Subject**: `sahool.chat.ai_query`

```json
{
  "query": "متى أسقي القمح؟",
  "language": "ar",
  "user_id": "user_123",
  "field_id": "field_456",
  "conversation_id": "conv_789",
  "context": {"crop_type": "wheat", "location": "Yemen"}
}
```

### Published

**Subject**: `sahool.chat.ai_response`

```json
{
  "conversation_id": "conv_789",
  "answer": "الري الأمثل للقمح...",
  "answer_en": "Optimal irrigation for wheat...",
  "metadata": {
    "confidence": 0.92,
    "agents_used": ["ai-advisor", "weather-service"],
    "processing_time_ms": 1200,
    "cached": false,
    "intent": "irrigation_query"
  }
}
```

---

## Caching Strategy

| Layer | Type | Estimated Hit Rate | Latency |
|-------|------|-------------------|---------|
| Exact match | Redis hash | 30% | < 10 ms |
| Semantic similarity | Embedding comparison | 40% | < 100 ms |
| LLM call | Claude / Ollama via orchestrator | 30% | 1–3 s |

**Overall**: 70% cache hit rate, < 500 ms average response time.

Cache namespace in Redis: `ai-chat:*`. TTL defaults to 7 days (`CACHE_TTL_SECONDS`).

---

## Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `ai_chat_queries_total` | counter | Total AI queries processed |
| `ai_chat_cache_hits` | counter | Cache hit count |
| `ai_chat_cache_misses` | counter | Cache miss count |
| `ai_chat_response_time_seconds` | histogram | End-to-end response time |
| `ai_chat_confidence_score` | gauge | Distribution of confidence scores |
| `ai_chat_errors_total` | counter | Errors by type |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8260` | HTTP listen port |
| `ENVIRONMENT` | `development` | `development`, `staging`, `production` |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `NATS_URL` | `nats://localhost:4222` | NATS connection URL |
| `REDIS_URL` | `redis://localhost:6379` | Redis cache URL |
| `LLM_ORCHESTRATOR_URL` | `http://localhost:8164` | LLM orchestrator base URL |
| `CACHE_TTL_SECONDS` | `604800` | Cache entry TTL (7 days) |
| `CACHE_SIMILARITY_THRESHOLD` | `0.9` | Minimum cosine similarity for semantic cache hit |
| `MIN_CONFIDENCE_THRESHOLD` | `0.6` | Confidence required for auto-send (else disclaimer) |
| `RATE_LIMIT_PER_USER_HOUR` | `10` | Maximum AI queries per user per hour |

---

## Security

- Query sanitization (XSS prevention), max 1,000 characters
- Confidence thresholds: responses below 60% confidence include a disclaimer
- Human-in-the-loop flag for critical topics (pesticide advice)
- No PII stored in cache; Redis connections are TLS-encrypted in production
- Audit logging for all queries

---

## Dependencies

- `nats-py` for NATS pub/sub
- `redis.asyncio` for semantic caching
- `httpx` (async) for LLM orchestrator client
- `shared.errors_py` for exception handling

---

## Health Endpoints

```
GET /healthz → {"status": "ok", "service": "ai-chat-assistant", "version": "1.0.0"}
GET /readyz  → {"status": "ready|not_ready", "checks": {"redis": "connected", "nats": "connected", "llm_orchestrator": "healthy"}}
```

---

## Related Services

- **chat-service** (8000) - produces `sahool.chat.ai_query` events
- **llm-orchestrator-service** (8164) - routes to AI agents
- **redis** - shared caching infrastructure
