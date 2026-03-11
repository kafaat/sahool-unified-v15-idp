# Service Dependencies - SAHOOL v16.0.0

**Last Updated:** 2026-01-30  
**Total Services:** 56+

---

## 🔗 Dependency Overview

This document maps all service dependencies to help understand:
- Which services depend on which infrastructure
- Inter-service communication patterns
- Critical paths for service startup
- Impact analysis for service failures

---

## 🏗️ Infrastructure Dependencies

### Tier 0: Core Infrastructure (No Dependencies)

These services have NO dependencies and must start first:

| Service | Port | Purpose |
|---------|------|---------|
| **postgres** | 5432 | Primary database |
| **redis** | 6379 | Cache & sessions |
| **nats** | 4222 | Message queue |
| **vault** | 8200 | Secrets management |
| **mqtt** | 1883 | IoT messaging |
| **etcd** | 2379 | Milvus metadata |
| **minio** | 9000 | Milvus object storage |

### Tier 1: Infrastructure Services (Depend on Tier 0)

| Service | Dependencies | Purpose |
|---------|--------------|---------|
| **pgbouncer** | postgres | Connection pooler |
| **kong** | redis | API Gateway |
| **qdrant** | None | Vector database |
| **milvus** | etcd, minio | Vector database (alt) |
| **mlflow** | postgres | ML model registry |
| **nats-prometheus-exporter** | nats | NATS metrics |
| **ollama** | None (GPU profile) | Local LLM |

---

## 📊 Service Dependency Matrix

### Node.js Services

#### field-management-service (Port 3000)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- agro-rules (calls field-management-service:3000)
- Admin app (field management UI)

**Purpose:** Unified field operations (replaces field-ops, field-service, field-core)

---

#### user-service (Port 3025)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- notification-service:8110

**Dependents:**
- ALL services (authentication)
- Admin app (user management, auth)

**Purpose:** Authentication & user management

**Critical:** This is a critical service - if it fails, authentication fails platform-wide

---

#### marketplace-service (Port 3010)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (marketplace management)

**Purpose:** Agricultural marketplace & FinTech

---

#### research-core (Port 3015)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (research trial management)

**Purpose:** Scientific research management

---

#### disaster-assessment (Port 3020)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (disaster reports)

**Purpose:** Disaster impact assessment

---

#### chat-service (Port 8115)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (chat management)

**Purpose:** Agricultural chat & messaging

---

#### iot-service (Port 8117)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222
- mqtt:1883

**Dependents:**
- Admin app (IoT dashboard)

**Purpose:** IoT device & sensor management

---

#### community-chat (Port 8097) ⚠️ DEPRECATED
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Replacement:** chat-service:8115

---

### Python Services

#### vegetation-analysis-service (Port 8090)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- ai-advisor:8112
- field-intelligence:8120
- ndvi-processor:8118
- Admin app (NDVI analytics)

**Purpose:** Satellite imagery & vegetation indices (NDVI, EVI, NDRE, NDWI)

**External APIs:**
- Sentinel Hub (SENTINEL_HUB_CLIENT_ID, SENTINEL_HUB_CLIENT_SECRET)
- NASA Earthdata (NASA_EARTHDATA_USERNAME, NASA_EARTHDATA_PASSWORD)

---

#### weather-service (Port 8092)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- ai-advisor:8112
- astronomical-calendar:8111
- field-intelligence:8120
- Admin app (weather dashboard)

**Purpose:** Multi-provider weather data

**External APIs:**
- OpenWeatherMap (OPENWEATHERMAP_API_KEY)
- WeatherAPI (WEATHERAPI_KEY)

---

#### advisory-service (Port 8093)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- ai-advisor:8112
- Admin app (advisory management)

**Purpose:** Agricultural advice & fertilizer recommendations

---

#### crop-intelligence-service (Port 8095)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- ai-advisor:8112
- Admin app (crop health monitoring)

**Purpose:** Crop health monitoring & disease detection

**Models Required:**
- `/app/models/plant_disease.tflite`

---

#### irrigation-smart (Port 8094)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222
- iot-gateway:8106

**Dependents:**
- Admin app (irrigation control)

**Purpose:** Smart irrigation management

---

#### ai-advisor (Port 8112)
**Dependencies:**
- qdrant:6333
- nats:4222
- crop-intelligence-service:8095
- weather-service:8092
- advisory-service:8093
- vegetation-analysis-service:8090

**Dependents:**
- Admin app (AI advisor interface)

**Purpose:** Multi-LLM agricultural advisor

**External APIs:**
- Anthropic (ANTHROPIC_API_KEY) - Claude
- OpenAI (OPENAI_API_KEY) - GPT-4
- Google (GOOGLE_API_KEY) - Gemini
- Ollama (local) - Llama 3.2

**Critical:** This service has the most dependencies - failure of any upstream service affects AI advisor

---

#### field-intelligence (Port 8120)
**Dependencies:**
- task-service:8103
- astronomical-calendar:8111
- notification-service:8110
- weather-service:8092
- vegetation-analysis-service:8090

**Dependents:**
- Admin app (field analytics)

**Purpose:** Field intelligence aggregation

**Critical:** This service aggregates data from 5 other services

---

#### notification-service (Port 8110)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- user-service:3025
- alert-service:8113
- field-intelligence:8120
- Admin app (notification center)

**Purpose:** Multi-channel notifications (Email, SMS, WhatsApp, Push)

**External APIs:**
- SMTP (SMTP_HOST, SMTP_USER, SMTP_PASSWORD)
- Twilio SMS (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
- Twilio WhatsApp (TWILIO_WHATSAPP_NUMBER)
- SendGrid (SENDGRID_API_KEY)
- Firebase (FCM_SERVER_KEY, FIREBASE_CREDENTIALS_JSON)
- Meta WhatsApp (META_WHATSAPP_ACCESS_TOKEN)
- Telegram (TELEGRAM_BOT_TOKEN)

---

#### alert-service (Port 8113)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222
- notification-service:8110

**Dependents:**
- Admin app (alert management)

**Purpose:** Alert management & notifications

---

#### billing-core (Port 8089)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (billing dashboard)

**Purpose:** Billing & payments

**External APIs:**
- Stripe (STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET)
- Tharwatt (THARWATT_API_KEY, THARWATT_MERCHANT_ID)

---

#### iot-gateway (Port 8106)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222
- redis:6379
- mqtt:1883

**Dependents:**
- irrigation-smart:8094
- Admin app (IoT gateway stats)

**Purpose:** MQTT-to-NATS gateway

---

#### astronomical-calendar (Port 8111)
**Dependencies:**
- weather-service:8092

**Dependents:**
- field-intelligence:8120
- Admin app (calendar)

**Purpose:** Astronomical calculations

---

#### task-service (Port 8103)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- field-intelligence:8120
- Admin app (task management)

**Purpose:** Task management

---

#### equipment-service (Port 8101)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- Admin app (equipment tracking)

**Purpose:** Equipment tracking

---

#### inventory-service (Port 8116)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- Admin app (inventory management)

**Purpose:** Inventory management

---

#### provider-config (Port 8104)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (provider configuration)

**Purpose:** Provider configuration management

---

#### virtual-sensors (Port 8119)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- Admin app (virtual sensors)

**Purpose:** Virtual sensor engine

---

#### yield-prediction-service (Port 8152)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (yield forecasts)

**Purpose:** Yield estimation & prediction

---

#### lai-estimation (Port 3022)
**Dependencies:**
- redis:6379
- nats:4222

**Dependents:**
- vegetation-analysis-service
- indicators-service

**Purpose:** Leaf Area Index estimation using LAI-TransNet

---

#### crop-growth-model (Port 3023)
**Dependencies:**
- redis:6379
- nats:4222

**Dependents:**
- yield-prediction-service
- advisory-service

**Purpose:** Crop growth simulation (WOFOST/DSSAT/APSIM)

---

#### field-chat (Port 8099)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222
- redis:6379

**Dependents:**
- Admin app (field chat)

**Purpose:** Field-specific chat

---

#### indicators-service (Port 8091)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- Admin app (indicators dashboard)

**Purpose:** Agricultural indicators

---

#### ws-gateway (Port 8081)
**Dependencies:**
- nats:4222
- redis:6379

**Dependents:**
- Admin app (WebSocket connections)

**Purpose:** WebSocket gateway

---

#### mcp-server (Port 8201)
**Dependencies:**
- kong:8000
- postgres:5432
- nats:4222

**Dependents:**
- AI assistants (Claude, ChatGPT, etc.)

**Purpose:** Model Context Protocol for AI assistants

---

#### skills-service (Port 8121)
**Dependencies:**
- redis:6379

**Dependents:**
- Admin app (skills assessment)

**Purpose:** AI skill compression

---

#### ai-agents-service (Port 8130)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (AI agents)

**Purpose:** Autonomous AI agent orchestration

---

#### ai-agents-core (Port 8161)
**Dependencies:**
- (Not specified in docker-compose)

**Dependents:**
- ai-agents-service:8130

**Purpose:** AI agent infrastructure

---

#### crm-service (Port 8131)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (CRM dashboard)

**Purpose:** Farmer relationship management

---

#### lowcode-engine (Port 8132)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (low-code builder)

**Purpose:** Low-code application development

---

#### wechat-service (Port 8133)
**Dependencies:**
- postgres (via pgbouncer:6432)
- redis:6379
- nats:4222

**Dependents:**
- Admin app (WeChat integration)

**Purpose:** WeChat integration

**External APIs:**
- WeChat (WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_TOKEN)

---

#### ground-vision-service (Port 8182)
**Dependencies:**
- postgres (via pgbouncer:6432)
- nats:4222

**Dependents:**
- Admin app (ground vision monitoring)

**Purpose:** Tower camera agricultural monitoring

**Models Required:**
- `/models/sam_vit_h.pth` (SAM model)
- `/models/yolo_agri_ops.pt` (YOLO model)

**External APIs:**
- Anthropic (ANTHROPIC_API_KEY) or Ollama (local)

---

### Worker Services (No HTTP)

#### agro-rules
**Dependencies:**
- nats:4222
- field-management-service:3000

**Dependents:**
- None (NATS subscriber)

**Purpose:** Event-driven agricultural rules engine

---

#### demo-data (Profile: demo)
**Dependencies:**
- kong:8000
- postgres:5432
- redis:6379
- nats:4222

**Dependents:**
- None (test data generator)

**Purpose:** API data flow simulator

---

#### code-review-service (Profile: gpu)
**Dependencies:**
- ollama:11434

**Dependents:**
- None (autonomous agent)

**Purpose:** Real-time code review with DeepSeek

---

## 🔥 Critical Dependency Paths

### Path 1: Authentication Flow
```
user → kong:8000 → user-service:3025 → pgbouncer:6432 → postgres:5432
                                      → redis:6379
                                      → notification-service:8110
```

### Path 2: AI Advisor Flow
```
user → kong:8000 → ai-advisor:8112 → qdrant:6333
                                   → crop-intelligence-service:8095 → pgbouncer → postgres
                                   → weather-service:8092 → pgbouncer → postgres
                                   → advisory-service:8093 → pgbouncer → postgres
                                   → vegetation-analysis-service:8090 → pgbouncer → postgres
                                   → nats:4222
```

### Path 3: Field Intelligence Flow
```
user → kong:8000 → field-intelligence:8120 → task-service:8103 → pgbouncer → postgres
                                            → astronomical-calendar:8111 → weather-service:8092
                                            → notification-service:8110 → pgbouncer → postgres
                                            → weather-service:8092 → pgbouncer → postgres
                                            → vegetation-analysis-service:8090 → pgbouncer → postgres
```

---

## 🚨 Single Points of Failure

### Critical Infrastructure
1. **postgres** - ALL services depend on it
2. **pgbouncer** - ALL database connections go through it
3. **nats** - Event-driven architecture depends on it
4. **redis** - Session management and caching depend on it
5. **kong** - ALL HTTP traffic goes through it

### Critical Services
1. **user-service** - Authentication fails if this is down
2. **notification-service** - Multiple services depend on it
3. **weather-service** - Multiple services depend on it
4. **vegetation-analysis-service** - Multiple services depend on it

---

## 📈 Startup Order

### Recommended Startup Sequence

1. **Tier 0:** postgres, redis, nats, vault, mqtt, etcd, minio
2. **Tier 1:** pgbouncer, kong, qdrant, milvus, mlflow
3. **Tier 2:** user-service, notification-service, weather-service, vegetation-analysis-service
4. **Tier 3:** All other services (can start in parallel)

### Docker Compose Startup

Docker Compose handles this automatically via `depends_on` with health checks.

```bash
docker-compose up -d
```

---

## 🐛 Dependency Issues

### Missing Dependencies

1. **ai-agents-core** - No dependencies specified in docker-compose
2. **knowledge-graph** - Not in docker-compose but referenced in Kong
3. **yield-engine** - Not in docker-compose but referenced in Kong
4. **agent-registry** - Not in docker-compose but referenced in Kong
5. **globalgap-compliance** - Not in docker-compose but referenced in Kong
6. **logistics-service** - Not in docker-compose but referenced in Kong
7. **ussd-gateway** - Not in docker-compose but referenced in Kong

### Circular Dependencies

None detected.

### Port Conflicts

1. **audit-service** uses port 8114. **chat-service** was moved to port 8115 to resolve the previous conflict.
2. **mcp-server** uses port 8201 (moved from 8200 to avoid conflict with **vault** on 8200).

---

**Last Updated:** 2026-01-30  
**Maintainer:** SAHOOL Platform Team
