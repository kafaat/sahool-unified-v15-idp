# Copilot API

**Type:** Python / FastAPI
**Port:** 8088
**Version:** 16.0.0
**Layer:** Business (Event Architecture)

## Overview

The Copilot API is the unified AI-powered assistant for the SAHOOL platform. It provides multi-turn conversational AI, Retrieval-Augmented Generation (RAG) over an agricultural knowledge base, specialized agent routing (agricultural advisory, code analysis), tool execution with security guardrails, and streaming response support. The service operates offline-first using a local Ollama LLM as the primary provider, with optional fallback to Claude, OpenAI, Gemini, and DeepSeek for cloud-connected deployments.

## Architecture

```
FastAPI Application (port 8088)
├── Authentication & Authorization (JWT + tool guardrails)
├── Prompt Guard (injection detection, size limits 12 000 chars)
├── Agent Router (code, advisory, chat, field-ops agents)
├── RAG Module
│   ├── Qdrant vector search (sentence-transformers embeddings)
│   └── Redis-cached search results
├── LLM Provider Router
│   ├── Primary: Ollama (offline, local, codellama:7b default)
│   └── Fallback: Claude / OpenAI / Gemini / DeepSeek (optional)
├── Chat History Store (PostgreSQL, offline-graceful)
└── NATS Event Publisher (copilot.chat.*, copilot.rag.*, copilot.tool.*)
```

### Request Flow

1. JWT authentication → extract user/tenant
2. Prompt injection detection and size validation
3. Rate limiting via Redis
4. Agent intent classification and routing
5. Chat history retrieval from PostgreSQL
6. RAG semantic search in Qdrant
7. LLM inference (Ollama primary, cloud fallback)
8. Response saved to chat history and published to NATS
9. JSON or Server-Sent Events response returned

## API Endpoints

### Health & Info
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Readiness probe (all dependencies) |
| `/health` | GET | Combined health with component status |
| `/metrics` | GET | Prometheus metrics (guard checks, blocked calls) |
| `/info` | GET | Service info and available LLM providers |
| `/docs` | GET | Swagger UI |

### Chat
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Main chat with RAG and agent routing |
| `/api/v1/chat/stream` | POST | Streaming response (Server-Sent Events) |
| `/api/v1/chat/message` | POST | Add message to existing session |
| `/api/v1/chat/{session_id}` | DELETE | Clear chat history for session |

### RAG
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rag/search` | POST | Semantic search across knowledge base |
| `/api/v1/rag/index` | POST | Index documents into Qdrant |
| `/api/v1/rag/index/{collection}` | DELETE | Delete a collection |
| `/api/v1/rag/stats` | GET | Vector database statistics |

### Tools & Guards
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tools/validate` | POST | Validate tool request against guardrails |
| `/api/v1/tools/execute` | POST | Execute tool with guard validation |
| `/api/v1/tools/registry` | GET | List available tools |
| `/api/v1/tools/policies` | GET | Active security policies |

## LLM Providers

| Provider | Type | Model | Use |
|----------|------|-------|-----|
| Ollama | Local (offline-first) | codellama:7b (default) | Primary |
| Claude (Anthropic) | Cloud | claude-3-5-sonnet | Fallback |
| OpenAI | Cloud | gpt-4o-mini | Fallback |
| Gemini (Google) | Cloud | gemini-1.5-pro | Fallback |
| DeepSeek | Cloud | deepseek-coder | Fallback |

## NATS Events

### Publishes
| Subject | Trigger |
|---------|---------|
| `sahool.copilot.chat.started` | Chat session initiated |
| `sahool.copilot.chat.message_received` | User message received |
| `sahool.copilot.chat.response_generated` | Response generated |
| `sahool.copilot.chat.completed` | Chat exchange completed |
| `sahool.copilot.guard.violation` | Security guardrail triggered |
| `sahool.copilot.rag.search_performed` | RAG search executed |
| `sahool.copilot.tool.executed` | Tool executed |

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8088` | No | Service port |
| `JWT_SECRET_KEY` | — | Yes | JWT secret (32+ chars) |
| `COPILOT_MODE` | `offline` | No | `offline` or `online` |
| `ENABLE_EXTERNAL` | `false` | No | Enable cloud LLM providers |
| `MAX_PROMPT_CHARS` | `12000` | No | Maximum prompt length |
| `MAX_ARGS_SIZE` | `20000` | No | Maximum tool arguments size |
| `REQUEST_TIMEOUT_S` | `30.0` | No | LLM inference timeout |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | No | Ollama server URL |
| `OLLAMA_MODEL` | `codellama:7b` | No | Primary local LLM model |
| `ANTHROPIC_API_KEY` | — | No | Claude API key |
| `GOOGLE_API_KEY` | — | No | Gemini API key |
| `DEEPSEEK_API_KEY` | — | No | DeepSeek API key |
| `QDRANT_HOST` | `localhost` | No | Qdrant host |
| `QDRANT_PORT` | `6333` | No | Qdrant port |
| `QDRANT_COLLECTION` | `sahool_copilot_knowledge` | No | Vector collection name |
| `USE_QDRANT` | `true` | No | Enable RAG via Qdrant |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | No | Sentence-transformer model |
| `DATABASE_URL` | — | No | PostgreSQL for chat history |
| `REDIS_URL` | — | No | Redis for caching and rate limiting |
| `NATS_URL` | — | No | NATS server |
| `CODE_FIX_AGENT_URL` | `http://localhost:8161` | No | Code-Fix-Agent URL |
| `AI_ADVISOR_URL` | `http://localhost:8112` | No | AI Advisor URL |

## Security Features

| Feature | Description |
|---------|-------------|
| Prompt Injection Detection | Blocks malicious prompt patterns |
| Request Size Limits | Rejects prompts > 12 000 chars |
| Rate Limiting | Per-user and per-tenant via Redis |
| Tool Guardrails | Policy-based tool access restrictions |
| JWT Authentication | Token-based with configurable expiration |
| Audit Logging | All requests logged with user/tenant context |

## Prometheus Metrics

```
copilot_guard_checks_total      # Total guardrail checks
copilot_guard_allowed_total     # Requests allowed
copilot_guard_blocked_total     # Requests blocked
copilot_chat_duration_seconds   # Chat response latency
copilot_rag_search_latency_ms   # RAG search latency
copilot_llm_token_usage         # Token usage per provider
```

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "copilot-api", "mode": "offline"}
GET /readyz   → {"status": "ok", "components": {"rag": true, "qdrant": true, "redis": true, "nats": true}}
GET /metrics  → Prometheus exposition format
```

## Admin Integration Notes

- The admin portal's AI Copilot panel should connect to `POST /api/v1/chat` for standard queries and `POST /api/v1/chat/stream` for real-time streaming responses.
- RAG knowledge base documents can be indexed by the admin via `POST /api/v1/rag/index`; collection statistics are available at `GET /api/v1/rag/stats`.
- Guard violation events (`sahool.copilot.guard.violation`) should be monitored in the security dashboard for anomaly detection.
- The service degrades gracefully when Qdrant or PostgreSQL are unavailable — chat still works in pure LLM mode without RAG or history persistence.
- Agent routing is automatic; the chat router classifies intents and selects the most appropriate specialized agent without admin configuration.
