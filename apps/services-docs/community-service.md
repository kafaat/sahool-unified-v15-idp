# Community Service | خدمة المجتمع الزراعي

Community collaboration and knowledge-sharing service for SAHOOL farmers, powered by Rocket.Chat. Provides real-time group messaging, topic-based agricultural channels, expert Q&A, and integration with SAHOOL advisory, weather, and pest detection services.

**Port:** 8135 | **Type:** Python / FastAPI | **Version:** 16.0.0

---

## Overview

The Community Service connects SAHOOL farmers with each other and with agricultural experts through real-time group channels organized by topic. It acts as a bridge between the SAHOOL platform and a self-hosted Rocket.Chat instance, providing:

- Topic-based agricultural channels (irrigation, pest control, market prices, etc.)
- Real-time group messaging with bilingual support (Arabic / English)
- Expert Q&A with advisory-service integration
- Automated weather and pest alert broadcasting to relevant channels
- Farmer-to-farmer knowledge sharing
- Channel moderation and content guidelines enforcement
- JWT-based authentication with per-tenant isolation
- Offline message queueing for low-connectivity environments
- Migration path from the deprecated wechat-service

| Property | Value |
|----------|-------|
| **Service Name** | community-service |
| **Version** | 16.0.0 |
| **Type** | Python (FastAPI) |
| **Description** | Community collaboration and knowledge-sharing for farmers |
| **Arabic Name** | خدمة المجتمع الزراعي |
| **Source Path** | `apps/services/community-service/` |
| **Replaces** | wechat-service (Port 8133) |

---

## Architecture

```
                          +-------------------+
                          |   Kong Gateway    |
                          |    (Port 8000)    |
                          +--------+----------+
                                   |
                                   | /api/v1/community/*
                                   v
+------------------+      +-------------------+      +-------------------+
|  SAHOOL Mobile   |----->| community-service |----->|   Rocket.Chat     |
|  SAHOOL Web      |      |   (Port 8135)     |      |   (Port 3100)     |
|  SAHOOL Admin    |      |   FastAPI + WS    |      |   REST + Realtime |
+------------------+      +--------+----------+      +--------+----------+
                                   |                           |
                    +--------------+--------------+            |
                    |              |              |            |
              +-----v----+  +-----v----+  +------v---+  +----v------+
              |PostgreSQL |  |  Redis   |  |   NATS   |  |  MongoDB  |
              | (PgBouncer|  | (Sessions|  | (Events) |  | (RC Data) |
              |  6432)    |  |  6379)   |  |  4222)   |  |  27017)   |
              +----------+  +----------+  +----------+  +-----------+

Integration with SAHOOL Services:
  +-------------------+     +-------------------+     +------------------------+
  | advisory-service  |     |  weather-service  |     | pest-detection-service  |
  |    (Port 8093)    |     |    (Port 8092)    |     |      (Port 8125)       |
  +-------------------+     +-------------------+     +------------------------+
         |                         |                            |
         +-------------------------+----------------------------+
                                   |
                          NATS Event Subscriptions
                     (advisory, weather, pest alerts)
                                   |
                                   v
                          +-------------------+
                          | community-service |
                          | Auto-broadcasts   |
                          | to relevant       |
                          | channels          |
                          +-------------------+
```

### Component Responsibilities

| Component | Role |
|-----------|------|
| **community-service** | API gateway, authentication, channel management, message routing, NATS integration |
| **Rocket.Chat** | Message persistence, real-time delivery, file sharing, search indexing |
| **MongoDB** | Rocket.Chat data store (messages, channels, user profiles) |
| **PostgreSQL** | SAHOOL user mapping, channel metadata, moderation logs |
| **Redis** | Session cache, rate limit counters, online presence |
| **NATS** | Event-driven integration with advisory, weather, and pest services |

---

## API Endpoints

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/healthz` | No | Kubernetes liveness probe |
| `GET` | `/readyz` | No | Kubernetes readiness probe (checks Rocket.Chat, DB, NATS) |
| `GET` | `/metrics` | No | Prometheus metrics |

### Channels

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/community/channels` | JWT | List all available channels for tenant |
| `GET` | `/api/v1/community/channels/:id` | JWT | Get channel details with member count |
| `POST` | `/api/v1/community/channels` | JWT (Admin) | Create a new channel |
| `PUT` | `/api/v1/community/channels/:id` | JWT (Admin) | Update channel settings |
| `DELETE` | `/api/v1/community/channels/:id` | JWT (Admin) | Archive a channel |
| `POST` | `/api/v1/community/channels/:id/join` | JWT | Join a channel |
| `POST` | `/api/v1/community/channels/:id/leave` | JWT | Leave a channel |
| `GET` | `/api/v1/community/channels/:id/members` | JWT | List channel members |

### Messages

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/community/channels/:id/messages` | JWT | Get channel message history (paginated) |
| `POST` | `/api/v1/community/channels/:id/messages` | JWT | Send a message to a channel |
| `PUT` | `/api/v1/community/messages/:id` | JWT | Edit own message |
| `DELETE` | `/api/v1/community/messages/:id` | JWT | Delete own message |
| `POST` | `/api/v1/community/messages/:id/react` | JWT | Add reaction to a message |
| `POST` | `/api/v1/community/messages/:id/pin` | JWT (Mod) | Pin a message in channel |

### Expert Q&A

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/community/questions` | JWT | Ask an expert question |
| `GET` | `/api/v1/community/questions` | JWT | List questions with filters |
| `POST` | `/api/v1/community/questions/:id/answer` | JWT (Expert) | Answer a question |
| `POST` | `/api/v1/community/questions/:id/accept` | JWT | Accept an answer |

### User Profile

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/community/profile` | JWT | Get community profile |
| `PUT` | `/api/v1/community/profile` | JWT | Update display name, avatar, bio |
| `GET` | `/api/v1/community/profile/:userId` | JWT | View another user's profile |

### Moderation

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/community/moderation/report` | JWT | Report inappropriate content |
| `GET` | `/api/v1/community/moderation/reports` | JWT (Admin) | List moderation reports |
| `POST` | `/api/v1/community/moderation/reports/:id/action` | JWT (Admin) | Take moderation action |
| `POST` | `/api/v1/community/moderation/mute` | JWT (Mod) | Mute a user in a channel |

---

## Default Agricultural Channels

The following channels are auto-created per tenant on first initialization:

| Channel ID | Name (EN) | Name (AR) | Description | Auto-Broadcast Source |
|------------|-----------|-----------|-------------|-----------------------|
| `general` | General | عام | General farming discussion | - |
| `irrigation` | Irrigation & Water | الري والمياه | Irrigation scheduling, water management | weather-service (rain alerts) |
| `pest-control` | Pest Control | مكافحة الآفات | Pest identification, IPM strategies | pest-detection-service |
| `crop-health` | Crop Health | صحة المحاصيل | Disease detection, nutrient deficiency | advisory-service |
| `market-prices` | Market Prices | أسعار السوق | Market price updates, trading | marketplace-service |
| `weather` | Weather Updates | تحديثات الطقس | Weather forecasts, alerts | weather-service |
| `equipment` | Equipment & Tools | المعدات والأدوات | Equipment maintenance, sharing | - |
| `harvest` | Harvest & Post-Harvest | الحصاد وما بعده | Harvest timing, storage, quality | advisory-service |
| `soil` | Soil Management | إدارة التربة | Soil testing, amendments, salinity | - |
| `livestock` | Livestock | الثروة الحيوانية | Animal husbandry (regional) | - |
| `announcements` | Announcements | إعلانات | Official platform announcements (read-only) | admin broadcast |
| `expert-qa` | Expert Q&A | أسئلة وأجوبة الخبراء | Expert questions and answers | - |

---

## NATS Events

### Published Events

| Event Subject | Trigger | Payload |
|---------------|---------|---------|
| `sahool.{tenant_id}.community.message.sent` | Message sent to channel | `{ channel_id, message_id, sender_id, content_preview, timestamp }` |
| `sahool.{tenant_id}.community.channel.created` | New channel created | `{ channel_id, name, name_ar, created_by, timestamp }` |
| `sahool.{tenant_id}.community.member.joined` | User joins channel | `{ channel_id, user_id, timestamp }` |
| `sahool.{tenant_id}.community.member.left` | User leaves channel | `{ channel_id, user_id, timestamp }` |
| `sahool.{tenant_id}.community.question.asked` | Expert question posted | `{ question_id, channel_id, user_id, topic, timestamp }` |
| `sahool.{tenant_id}.community.question.answered` | Expert answers question | `{ question_id, answer_id, expert_id, timestamp }` |
| `sahool.{tenant_id}.community.moderation.action` | Moderation action taken | `{ report_id, action, moderator_id, target_user_id, timestamp }` |

### Subscribed Events

| Event Subject | Source Service | Action |
|---------------|----------------|--------|
| `sahool.{tenant_id}.advisory.recommendation.created` | advisory-service | Broadcast summary to `crop-health` channel |
| `sahool.{tenant_id}.weather.alert.issued` | weather-service | Broadcast alert to `weather` and `irrigation` channels |
| `sahool.{tenant_id}.pest.detection.confirmed` | pest-detection-service | Broadcast alert to `pest-control` channel |
| `sahool.{tenant_id}.marketplace.price.updated` | marketplace-service | Broadcast price update to `market-prices` channel |
| `sahool.{tenant_id}.notification.broadcast` | notification-service | Broadcast to `announcements` channel |

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL via PgBouncer | `postgresql://user:pass@pgbouncer:6432/sahool` |
| `NATS_URL` | NATS connection URL | `nats://user:pass@nats:4222` |
| `REDIS_URL` | Redis connection URL | `redis://:pass@redis:6379/0` |
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | `your-32-char-minimum-secret-key` |
| `ROCKETCHAT_URL` | Rocket.Chat server URL | `http://rocketchat:3100` |
| `ROCKETCHAT_ADMIN_USER` | Rocket.Chat admin username | `sahool-admin` |
| `ROCKETCHAT_ADMIN_PASSWORD` | Rocket.Chat admin password | `<secure_password>` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8135` |
| `HOST` | Bind address | `0.0.0.0` |
| `ENVIRONMENT` | Environment mode | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MONGODB_URL` | MongoDB URL (for direct queries) | `mongodb://mongo:27017/rocketchat` |
| `ROCKETCHAT_BOT_USER` | Bot username for auto-broadcasts | `sahool-bot` |
| `ROCKETCHAT_BOT_PASSWORD` | Bot password | `<secure_password>` |
| `MAX_MESSAGE_LENGTH` | Maximum message length | `5000` |
| `DEFAULT_PAGE_SIZE` | Default pagination size | `50` |
| `OFFLINE_QUEUE_TTL` | Offline message queue TTL (seconds) | `86400` |
| `MODERATION_ENABLED` | Enable content moderation | `true` |

---

## Docker Deployment

### docker-compose.yml

```yaml
services:
  community-service:
    build:
      context: .
      dockerfile: apps/services/community-service/Dockerfile
    container_name: sahool-community-service
    ports:
      - "8135:8135"
    environment:
      - PORT=8135
      - ENVIRONMENT=${ENVIRONMENT:-development}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
      - NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ROCKETCHAT_URL=http://rocketchat:3100
      - ROCKETCHAT_ADMIN_USER=${ROCKETCHAT_ADMIN_USER}
      - ROCKETCHAT_ADMIN_PASSWORD=${ROCKETCHAT_ADMIN_PASSWORD}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    depends_on:
      pgbouncer:
        condition: service_healthy
      redis:
        condition: service_healthy
      nats:
        condition: service_healthy
      rocketchat:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8135/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    security_opt:
      - no-new-privileges:true
    networks:
      - sahool-network

  rocketchat:
    image: rocket.chat:6.12
    container_name: sahool-rocketchat
    ports:
      - "3100:3000"
    environment:
      - ROOT_URL=http://localhost:3100
      - MONGO_URL=mongodb://mongo:27017/rocketchat
      - MONGO_OPLOG_URL=mongodb://mongo:27017/local?replicaSet=rs0
      - OVERWRITE_SETTING_Show_Setup_Wizard=completed
    depends_on:
      mongo:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    networks:
      - sahool-network

  mongo:
    image: mongo:7.0
    container_name: sahool-mongo-rc
    command: ["--replSet", "rs0", "--bind_ip_all"]
    volumes:
      - mongo-rc-data:/data/db
    healthcheck:
      test: echo "try { rs.status() } catch (err) { rs.initiate({_id:'rs0',members:[{_id:0,host:'mongo:27017'}]}) }" | mongosh --quiet
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - sahool-network

volumes:
  mongo-rc-data:

networks:
  sahool-network:
    external: true
```

### Dockerfile

```dockerfile
FROM python:3.11-slim-bookworm AS base

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base AS builder

COPY apps/services/community-service/requirements.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -r requirements.txt

FROM base AS production

RUN groupadd -r sahool && useradd -r -g sahool -u 1000 sahool

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY apps/services/community-service/src /app/src
COPY shared /app/shared

RUN chown -R sahool:sahool /app
USER sahool

EXPOSE 8135

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8135/healthz || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8135"]
```

---

## Helm Deployment

### values.yaml

```yaml
community-service:
  replicaCount: 2
  image:
    repository: ghcr.io/kafaat/sahool-community-service
    tag: "16.0.0"
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8135
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  env:
    - name: PORT
      value: "8135"
    - name: ENVIRONMENT
      value: "production"
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: sahool-db-credentials
          key: connection-string
    - name: NATS_URL
      valueFrom:
        secretKeyRef:
          name: sahool-nats-credentials
          key: url
    - name: REDIS_URL
      valueFrom:
        secretKeyRef:
          name: sahool-redis-credentials
          key: url
    - name: JWT_SECRET_KEY
      valueFrom:
        secretKeyRef:
          name: sahool-jwt
          key: secret-key
    - name: ROCKETCHAT_URL
      value: "http://rocketchat:3100"
    - name: ROCKETCHAT_ADMIN_USER
      valueFrom:
        secretKeyRef:
          name: sahool-rocketchat-credentials
          key: admin-user
    - name: ROCKETCHAT_ADMIN_PASSWORD
      valueFrom:
        secretKeyRef:
          name: sahool-rocketchat-credentials
          key: admin-password
  probes:
    liveness:
      path: /healthz
      port: 8135
      initialDelaySeconds: 15
      periodSeconds: 30
    readiness:
      path: /readyz
      port: 8135
      initialDelaySeconds: 10
      periodSeconds: 10
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70
  podAnnotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8135"
    prometheus.io/path: "/metrics"

rocketchat:
  replicaCount: 1
  image:
    repository: rocket.chat
    tag: "6.12"
  service:
    type: ClusterIP
    port: 3100
  mongodb:
    enabled: true
    replicaSet:
      enabled: true
    persistence:
      enabled: true
      size: 20Gi
```

### Kong Route Configuration

```yaml
services:
  - name: community-service
    url: http://sahool-community-service:8135
    routes:
      - name: community-route
        paths:
          - /api/v1/community
        strip_path: false
        protocols:
          - http
          - https
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 60
          hour: 2000
          policy: redis
```

---

## Integration with SAHOOL Services

### advisory-service (Port 8093)

The community-service subscribes to advisory recommendation events and auto-broadcasts summaries to the `crop-health` channel. When a farmer asks a question in the `expert-qa` channel, the service can optionally forward it to the advisory-service for AI-generated responses.

```
advisory-service --[NATS: sahool.{tid}.advisory.recommendation.created]--> community-service
                                                                             |
                                                                             v
                                                                      #crop-health channel
                                                                      "New advisory: ..."
```

**Integration points:**
- Subscribe to `sahool.{tenant_id}.advisory.recommendation.created`
- Format bilingual advisory summary (EN/AR) for channel broadcast
- Link back to full advisory in mobile/web app

### weather-service (Port 8092)

Weather alerts are broadcast to both `weather` and `irrigation` channels. Critical alerts (frost, hail, sandstorm) trigger push notifications to all channel members.

```
weather-service --[NATS: sahool.{tid}.weather.alert.issued]--> community-service
                                                                  |
                                                                  v
                                                           #weather channel
                                                           #irrigation channel
                                                           "[!!] Weather Alert: ..."
```

**Integration points:**
- Subscribe to `sahool.{tenant_id}.weather.alert.issued`
- Use alert priority encoding (`[!!!]`, `[!!]`, `[!]`, `[.]`)
- Critical alerts trigger notification-service push

### pest-detection-service (Port 8125)

Confirmed pest detections are broadcast to the `pest-control` channel with identification details, severity, and recommended IPM actions.

```
pest-detection-service --[NATS: sahool.{tid}.pest.detection.confirmed]--> community-service
                                                                             |
                                                                             v
                                                                      #pest-control channel
                                                                      "[!!] Pest Alert: RPW ..."
```

**Integration points:**
- Subscribe to `sahool.{tenant_id}.pest.detection.confirmed`
- Include pest species (EN/AR), severity level, affected area
- Link to pest-detection-service detailed report
- Critical pests (RPW, locust) escalated to `[!!!]` alert level

---

## Migration from wechat-service

The community-service replaces the deprecated `wechat-service` (Port 8133). The migration involves switching from the WeChat Open Platform API to self-hosted Rocket.Chat for messaging.

### Migration Timeline

| Phase | Date | Action |
|-------|------|--------|
| **Phase 1** | 2026-03-01 | community-service deployed alongside wechat-service |
| **Phase 2** | 2026-04-01 | User migration begins, dual-write to both services |
| **Phase 3** | 2026-05-01 | wechat-service marked as deprecated (sunset headers) |
| **Phase 4** | 2026-06-01 | wechat-service fully decommissioned |

### Key Differences

| Feature | wechat-service | community-service |
|---------|---------------|-------------------|
| **Backend** | WeChat Open Platform API | Self-hosted Rocket.Chat |
| **Data Store** | PostgreSQL + WeChat servers | PostgreSQL + MongoDB (local) |
| **Port** | 8133 | 8135 |
| **Language Focus** | Chinese (WeChat-native) | Arabic/English (bilingual) |
| **Offline Support** | No | Yes (message queueing) |
| **Data Sovereignty** | WeChat servers (China) | Self-hosted (on-premise/cloud) |
| **AI Features** | Chat summarization (WeChat) | Expert Q&A + advisory integration |
| **Channel Model** | WeChat groups | Topic-based agricultural channels |
| **File Sharing** | WeChat Moments | Rocket.Chat file uploads |

### API Mapping

| wechat-service Endpoint | community-service Equivalent |
|--------------------------|------------------------------|
| `GET /api/v1/wechat/messages` | `GET /api/v1/community/channels/:id/messages` |
| `POST /api/v1/wechat/messages/send` | `POST /api/v1/community/channels/:id/messages` |
| `GET /api/v1/wechat/contacts` | `GET /api/v1/community/channels/:id/members` |
| `POST /api/v1/wechat/contacts/add-friend` | `POST /api/v1/community/channels/:id/join` |
| `POST /api/v1/wechat/groups/join` | `POST /api/v1/community/channels/:id/join` |
| `GET /api/v1/wechat/groups` | `GET /api/v1/community/channels` |
| `POST /api/v1/wechat/moments/post` | `POST /api/v1/community/channels/announcements/messages` |
| `POST /api/v1/wechat/ai/summarize` | Expert Q&A + advisory-service integration |
| `POST /api/v1/wechat/ai/insights` | NATS event subscriptions (automated) |

### Migration Steps

1. **Deploy community-service** alongside wechat-service using `docker-compose --profile community up`
2. **Provision Rocket.Chat** with default agricultural channels (auto-created on first startup)
3. **Map existing users** from wechat-service user table to community-service profiles
4. **Enable dual-write** in notification-service to broadcast to both services during transition
5. **Redirect API clients** from `/api/v1/wechat/*` to `/api/v1/community/*` via Kong route update
6. **Decommission wechat-service** after confirming zero traffic for 30 days

---

## Rate Limiting

| Tier | Messages/min | API Requests/min | API Requests/hour |
|------|--------------|------------------|-------------------|
| Starter | 10 | 30 | 500 |
| Professional | 30 | 60 | 2000 |
| Enterprise | 60 | 120 | 5000 |

---

## Security

- **JWT Authentication**: All endpoints except health probes require valid JWT Bearer token
- **Tenant Isolation**: Channel and message data scoped by `tenant_id` from JWT `tid` claim
- **Content Moderation**: Automated profanity filtering and manual report-based moderation
- **Rate Limiting**: Per-user and per-tenant limits via slowapi
- **Input Sanitization**: HTML stripping, control character removal on all message content
- **Non-root Container**: Runs as user `sahool` (UID 1000)
- **No-new-privileges**: Docker security option enabled

---

## Related Services

| Service | Relationship | Port |
|---------|--------------|------|
| **chat-service** | Marketplace 1:1 messaging (separate scope) | 8115 |
| **wechat-service** | Deprecated predecessor | 8133 |
| **advisory-service** | Advisory broadcast source | 8093 |
| **weather-service** | Weather alert broadcast source | 8092 |
| **pest-detection-service** | Pest alert broadcast source | 8125 |
| **marketplace-service** | Market price broadcast source | 3010 |
| **notification-service** | Push notification integration | 8110 |
| **user-service** | User authentication and profiles | 3025 |

---

## File Structure

```
apps/services/community-service/
├── Dockerfile
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point, lifespan
│   ├── api/
│   │   └── v1/
│   │       ├── channels.py      # Channel CRUD endpoints
│   │       ├── messages.py      # Message endpoints
│   │       ├── questions.py     # Expert Q&A endpoints
│   │       ├── moderation.py    # Moderation endpoints
│   │       └── profile.py       # Community profile endpoints
│   ├── events/
│   │   ├── publishers.py        # NATS event publishers
│   │   └── subscribers.py       # NATS event subscribers (advisory, weather, pest)
│   ├── rocketchat/
│   │   ├── client.py            # Rocket.Chat REST API client
│   │   └── realtime.py          # Rocket.Chat Realtime API (WebSocket)
│   ├── services/
│   │   ├── channel_service.py   # Channel business logic
│   │   ├── message_service.py   # Message routing and formatting
│   │   ├── broadcast_service.py # Auto-broadcast from NATS events
│   │   └── moderation_service.py # Content moderation logic
│   └── models/
│       ├── channel.py           # Channel metadata models
│       ├── message.py           # Message models
│       └── question.py          # Q&A models
└── tests/
    ├── test_channels.py
    ├── test_messages.py
    ├── test_broadcasts.py
    └── test_moderation.py
```

---

## Monitoring

### Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `community_messages_total` | Counter | Total messages sent (by channel, tenant) |
| `community_active_users` | Gauge | Currently active users |
| `community_channels_total` | Gauge | Total active channels |
| `community_rocketchat_latency_seconds` | Histogram | Rocket.Chat API response time |
| `community_broadcast_total` | Counter | Auto-broadcast messages (by source service) |
| `community_moderation_actions_total` | Counter | Moderation actions taken |

### Grafana Dashboard

Included in `infrastructure/monitoring/grafana/dashboards/community-service.json`:
- Messages per hour by channel
- Active users over time
- Rocket.Chat latency P50/P95/P99
- Auto-broadcast delivery success rate
- Moderation reports and actions

---

*Document generated: 2026-03-13*
*Service Version: 16.0.0*
*Replaces: wechat-service (Port 8133)*
