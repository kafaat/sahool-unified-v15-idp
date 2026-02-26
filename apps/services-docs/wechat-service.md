# WeChat Service | خدمة تكامل ويتشات

WeChat messaging and social integration service providing message management, contact operations, Moments publishing, and AI-powered chat analysis for SAHOOL farmers using WeChat.

**Port:** 8133 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The WeChat Service integrates the SAHOOL platform with the WeChat ecosystem, enabling Chinese-language or WeChat-native farmers and agricultural stakeholders to interact with platform data through a familiar interface. It provides bidirectional messaging, group and contact management, Moments publishing for market announcements, and AI-powered chat intelligence (summarization and insight extraction).

Key capabilities:
- Fetch and send messages across individual chats and group chats
- Contact management: add friends, join groups, follow official accounts
- Post to WeChat Moments with visibility controls
- AI-powered conversation summarization
- Chat insight extraction: sentiment, key topics, action items, decisions
- JWT-based authentication with per-tenant isolation
- Rate limiting (slowapi) to respect WeChat API quotas
- Bilingual error messages and responses (Arabic / English)
- Redis session caching

---

## Architecture

```
WeChat Service (8133)
├── src/main.py    — FastAPI app, all endpoints, Pydantic models
└── External APIs:
    ├── WeChat Open Platform API  — Message, contact, Moments operations
    ├── PostgreSQL                — User and session persistence
    ├── Redis                     — Session cache and rate limit counters
    └── NATS                      — Event publishing

Authentication: JWT via shared.auth.dependencies (Bearer token)
Rate limiting: slowapi (Limiter) on per-endpoint basis
```

The service initialises asyncpg, NATS, and Redis connections on startup via the lifespan manager.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Kubernetes readiness probe |
| GET | `/health` | Detailed health status with dependency checks |
| GET | `/metrics` | Prometheus metrics |

### Messages

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| POST | `/api/v1/messages/fetch` | 60/min | Fetch messages from a chat or group |
| POST | `/api/v1/messages/send` | 30/min | Send a message to a chat or group |

### Contacts

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| POST | `/api/v1/contacts/add` | 20/min | Add a new contact or join group |

### Moments

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| POST | `/api/v1/moments/publish` | 10/min | Publish a Moment post |

### Chat Analysis

| Method | Path | Rate Limit | Description |
|--------|------|-----------|-------------|
| POST | `/api/v1/chat/summarize` | 10/min | Generate AI summary of a conversation |
| POST | `/api/v1/chat/insights` | 10/min | Extract sentiment, topics, action items, decisions |

---

## NATS Events Published

All subjects follow the pattern `sahool.{tenant_id}.wechat.{entity}.{action}`:

| Subject | Trigger |
|---------|---------|
| `sahool.{tenant_id}.wechat.messages.fetched` | Messages fetched from a chat |
| `sahool.{tenant_id}.wechat.message.sent` | Message sent successfully |
| `sahool.{tenant_id}.wechat.contact.added` | New contact added |
| `sahool.{tenant_id}.wechat.moment.published` | Moment published |
| `sahool.{tenant_id}.wechat.chat.summarized` | Chat summary generated |
| `sahool.{tenant_id}.wechat.chat.insights_extracted` | Chat insights extracted |

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `SERVICE_PORT` | `8133` | No | Service port |
| `ENVIRONMENT` | `development` | No | Environment name |
| `DATABASE_URL` | - | Yes | PostgreSQL connection string |
| `REDIS_URL` | - | Yes | Redis connection URL |
| `NATS_URL` | - | No | NATS server URL |
| `WECHAT_APP_ID` | - | Yes | WeChat Open Platform App ID |
| `WECHAT_APP_SECRET` | - | Yes | WeChat Open Platform App Secret |
| `JWT_SECRET_KEY` | - | Yes | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | No | JWT algorithm |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,...` | No | Allowed CORS origins |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity |

---

## Error Codes

| Code | Description (EN) | Description (AR) |
|------|------------------|------------------|
| `VALIDATION_ERROR` | Validation error | خطأ في التحقق |
| `NOT_FOUND` | Resource not found | المورد غير موجود |
| `FORBIDDEN` | Access denied | تم رفض الوصول |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | تم تجاوز الحد الأقصى للطلبات |
| `WECHAT_*` | WeChat API error | خطأ في واجهة ويتشات |
| `INVALID_INPUT` | Invalid input | إدخال غير صالح |
| `SERVICE_UNAVAILABLE` | Service unavailable | الخدمة غير متاحة |

---

## Security

- JWT Bearer token required on all `/api/v1/*` endpoints
- Non-root Docker container (user: `sahool`, UID 1000)
- Rate limiting on all endpoints to prevent WeChat API quota exhaustion
- Tenant isolation: all queries scoped to `tenant_id` from JWT

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **asyncpg** — PostgreSQL async driver
- **redis.asyncio** — Redis session cache
- **nats-py** — NATS event publishing
- **structlog** — Structured JSON logging
- **slowapi** — Rate limiting middleware
- `shared.auth.dependencies` — JWT authentication

---

## Related Services

- **chat-service** (8000) — Primary platform messaging (internal)
- **whatsapp-bot-service** (8240) — WhatsApp channel equivalent
- **notification-service** (8110) — Cross-channel notification routing
- **llm-orchestrator-service** (8164) — AI backend for summarization and insights
