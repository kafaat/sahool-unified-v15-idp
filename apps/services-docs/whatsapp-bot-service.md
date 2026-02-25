# WhatsApp Bot Service | خدمة روبوت واتساب

AI-powered WhatsApp messaging service enabling SAHOOL farmers to receive crop advisory, disease detection, weather forecasts, and irrigation guidance through WhatsApp conversations.

**Port:** 8240 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The WhatsApp Bot Service connects the SAHOOL platform to the Meta WhatsApp Business Cloud API. Farmers with basic WhatsApp accounts can text or send photos to receive instant agricultural intelligence without needing the mobile app. Natural language queries in Arabic or English are forwarded to the LLM Orchestrator Service for response generation. Crop photos are routed to the YOLO Vision Service for disease and pest detection.

Key capabilities:
- Receive and respond to text messages (Arabic / English natural language)
- Image message handling — crop photos sent to YOLO vision for disease/pest detection
- Location messages for weather forecasts and location-based advice
- Interactive button menus (max 3 buttons) and list menus
- Template message sending (pre-approved Meta templates)
- Session management with Redis (1-hour TTL, 10-message context)
- Proactive alert delivery via notification-service integration
- OTP verification via WhatsApp templates

---

## Architecture

```
Meta WhatsApp Cloud API
        |
WhatsApp Bot Service (8240)
├── Webhook Receiver   — Verify + receive Meta webhook events
├── MessageHandler     — Routes message types to handlers
│   ├── Text Handler   → LLM Orchestrator (8164/8220)
│   ├── Image Handler  → YOLO Vision Service (8150)
│   └── Location Handler → Weather/Advisory context
├── SessionManager     — Redis-backed conversation context
├── WhatsAppClient     — Meta Cloud API outbound client
└── Router (api/v1)    — send, send-template, mark-read endpoints

External:
├── Redis       — Session storage (TTL 1h)
├── NATS        — Optional event publishing
├── PostgreSQL  — Optional message persistence
├── LLM Orchestrator (8164) — NLP + advisory generation
└── YOLO Vision (8150)      — Image crop analysis
```

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Readiness probe (Redis, NATS, DB, WhatsApp config) |
| GET | `/` | Service info and endpoint map |

### Webhook (Meta Cloud API)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/webhook` | Webhook verification (Meta hub.verify_token challenge) |
| POST | `/webhook` | Receive incoming messages (text, image, location, interactive) |

### Send Messages

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/send` | Send message (text, image, interactive buttons/lists) |
| POST | `/api/v1/send-template` | Send pre-approved template message |
| POST | `/api/v1/mark-read` | Mark a message as read |

---

## Message Types Supported

### Incoming
- **Text** — Natural language in Arabic or English
- **Image** — Crop photos forwarded to vision service
- **Location** — GPS coordinates for weather and localized advice
- **Interactive** — Button click and list selection responses

### Outgoing
- **Text** — Plain text advisory responses
- **Interactive Buttons** — Quick-reply buttons (max 3)
- **Interactive Lists** — Multi-section selection menus
- **Templates** — Pre-approved Meta templates (OTP, alerts, proactive)

---

## Session Management

Sessions are stored in Redis with the farmer's phone number as key:

| Property | Value |
|----------|-------|
| TTL | 1 hour (configurable via `SESSION_TTL`) |
| Context messages | Last 10 messages |
| Stored data | Language preference, last location, crop context, conversation history |

---

## WhatsApp API Limits

| Limit | Value |
|-------|-------|
| Business-initiated messages | 80 / second |
| Template messages | 1000 / phone number / day |
| New number unique recipients | 250 / 24 hours |

---

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `WHATSAPP_TOKEN` | Meta WhatsApp Business API access token |
| `WHATSAPP_PHONE_ID` | WhatsApp Business phone number ID |
| `WHATSAPP_VERIFY_TOKEN` | Webhook verification token (set in Meta dashboard) |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8240` | Service port |
| `WHATSAPP_API_VERSION` | `v17.0` | Meta API version |
| `LLM_ORCHESTRATOR_URL` | `http://llm-orchestrator-service:8220` | LLM service endpoint |
| `VISION_SERVICE_URL` | `http://yolo26-vision-service:8150` | Vision service endpoint |
| `REDIS_URL` | `redis://localhost:6379` | Redis for session storage |
| `NATS_URL` | - | NATS for event publishing |
| `DATABASE_URL` | - | PostgreSQL for message persistence |
| `SESSION_TTL` | `3600` | Session TTL in seconds |
| `DEFAULT_LANGUAGE` | `ar` | Default response language |
| `DB_POOL_MIN_SIZE` | `2` | asyncpg pool min connections |
| `DB_POOL_MAX_SIZE` | `10` | asyncpg pool max connections |
| `ENVIRONMENT` | `development` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Security

- Webhook verification using `WHATSAPP_VERIFY_TOKEN` prevents spoofed events
- HTTPS required in production (Meta rejects HTTP webhooks)
- Phone numbers masked in all log output (last 4 digits only)
- No persistent storage of message content by default (in-memory only)

---

## Dependencies

- **FastAPI** 0.128.5 — HTTP framework
- **httpx** — Async HTTP client for Meta Cloud API and internal services
- **redis.asyncio** — Session management
- **nats-py** — Optional event publishing
- **asyncpg** — Optional PostgreSQL persistence
- **structlog** — Structured JSON logging
- `shared.errors_py` — Unified error handling

---

## WhatsApp Business API Setup

1. Create a Meta Business Account
2. Create a WhatsApp Business App in Meta Developer Console
3. Add a phone number (production) or use the test number
4. Generate a permanent access token (System User recommended)
5. Set webhook URL: `https://your-domain.com/webhook`
6. Subscribe to webhook fields: `messages`
7. Set `WHATSAPP_VERIFY_TOKEN` to match your Meta dashboard configuration

---

## Related Services

- **ussd-gateway** (8183) — Feature phone (SMS/USSD) channel complement
- **llm-orchestrator-service** (8164) — NLP and advisory generation backend
- **yolo26-vision-service** (8150) — Crop image disease and pest detection
- **notification-service** (8110) — Proactive push alert delivery
- **wechat-service** (8133) — WeChat channel equivalent
