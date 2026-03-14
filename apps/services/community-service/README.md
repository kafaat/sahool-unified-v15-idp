# SAHOOL Community Service

## خدمة المجتمع الزراعي

Rocket.Chat integration service for farmer community messaging, cooperative group management, and AI-powered advisory bots.

خدمة تكامل روكيت شات للمراسلة المجتمعية للمزارعين وإدارة مجموعات التعاونيات وبوتات الاستشارات الذكية.

---

## Features | الميزات

- **Agricultural Channels** | القنوات الزراعية
  - Pre-configured topic channels (irrigation, diseases, market prices, weather, pests, equipment)
  - Tenant-scoped channel isolation
  - Bilingual channel metadata (Arabic/English)

- **Cooperative Group Management** | إدارة مجموعات التعاونيات
  - Create and manage community channels per cooperative
  - Member join/leave management
  - Channel history and search

- **AI Advisory Bots** | بوتات الاستشارات الذكية
  - Route advisory messages to relevant agricultural channels
  - Weather and pest alert broadcasting
  - Bilingual advisory content with severity levels

- **User Synchronization** | مزامنة المستخدمين
  - Sync SAHOOL users to Rocket.Chat
  - Role-based access provisioning
  - Avatar synchronization

- **Multi-Tenant Support** | دعم تعدد المستأجرين
  - Tenant workspace initialization with default channels
  - Tenant-prefixed channel naming
  - Admin user provisioning

---

## API Endpoints | نقاط الوصول

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe |
| GET | `/health` | Combined health status |
| GET | `/metrics` | Prometheus metrics |

### Tenant Setup

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/community/setup-tenant` | Initialize tenant workspace |

### Channels

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/community/channels` | Create channel |
| GET | `/api/v1/community/channels` | List channels |
| POST | `/api/v1/community/channels/{id}/join` | Join channel |
| POST | `/api/v1/community/channels/{id}/leave` | Leave channel |
| GET | `/api/v1/community/channels/{id}/members` | Get members |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/community/messages` | Post message |
| GET | `/api/v1/community/channels/{id}/history` | Get history |
| POST | `/api/v1/community/messages/search` | Search messages |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/community/users/sync` | Sync user to Rocket.Chat |

### Bots

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/community/bots/advisory` | Post advisory message |
| POST | `/api/v1/community/bots/alert` | Post alert message |

---

## Environment Variables | متغيرات البيئة

| Variable | Default | Description |
|----------|---------|-------------|
| `ROCKETCHAT_URL` | `http://rocketchat:3000` | Rocket.Chat server URL |
| `ROCKETCHAT_ADMIN_USER` | - | Admin username for API access |
| `ROCKETCHAT_ADMIN_PASSWORD` | - | Admin password |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `REDIS_URL` | - | Redis connection string |
| `NATS_URL` | - | NATS connection string |
| `PORT` | `8133` | Service port |
| `ENVIRONMENT` | `development` | Environment name |
| `CORS_ORIGINS` | `https://sahool.app,...` | Allowed CORS origins |

---

## NATS Events | أحداث NATS

| Subject | Trigger |
|---------|---------|
| `sahool.community.channel_created` | New channel created |
| `sahool.community.user_joined` | User joined a channel |
| `sahool.community.message_posted` | Message posted |
| `sahool.community.advisory_posted` | Advisory bot message posted |
| `sahool.community.alert_posted` | Alert posted |
| `sahool.community.tenant_setup` | Tenant workspace initialized |

---

## Default Agricultural Channels | القنوات الزراعية الافتراضية

| Channel | Arabic | Topic |
|---------|--------|-------|
| irrigation | الري | Irrigation scheduling and water management |
| crop-diseases | أمراض-المحاصيل | Crop disease identification and treatment |
| market-prices | أسعار-السوق | Agricultural market prices and trading |
| weather-alerts | تنبيهات-الطقس | Weather forecasts and alerts |
| pest-management | إدارة-الآفات | Pest identification and IPM strategies |
| equipment | المعدات | Equipment sharing and maintenance tips |
| best-practices | أفضل-الممارسات | Agricultural best practices and knowledge sharing |
| announcements | الإعلانات | Platform announcements (read-only) |

---

## Development | التطوير

```bash
# Run locally
uvicorn src.main:app --host 0.0.0.0 --port 8133 --reload

# Run tests
pytest tests/ -v

# Docker build
docker build -f Dockerfile -t sahool-community-service:latest ../../..
```

---

## Port | المنفذ

**8133** (reusing deprecated wechat-service port)

## Version | الإصدار

16.0.0
