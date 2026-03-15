# Environment Variables Reference - SAHOOL v16.0.0

**Last Updated:** 2026-01-30  
**Total Services:** 56+

---

## 🔐 Required Environment Variables

These variables **MUST** be set for the platform to function.

### Core Infrastructure

```bash
# PostgreSQL Database
POSTGRES_USER=sahool
POSTGRES_PASSWORD=<secure-password-min-16-chars>
POSTGRES_DB=sahool
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# PgBouncer Connection Pooler
PGBOUNCER_POOL_MODE=transaction
PGBOUNCER_MAX_CLIENT_CONN=1000
PGBOUNCER_DEFAULT_POOL_SIZE=250
PGBOUNCER_MIN_POOL_SIZE=50
PGBOUNCER_RESERVE_POOL_SIZE=25
PGBOUNCER_MAX_DB_CONNECTIONS=250

# Redis Cache
REDIS_PASSWORD=<secure-password-min-16-chars>
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# NATS Message Queue
NATS_USER=<nats-user>
NATS_PASSWORD=<secure-password-min-16-chars>
NATS_ADMIN_USER=<admin-user>
NATS_ADMIN_PASSWORD=<secure-password-min-16-chars>
NATS_MONITOR_USER=<monitor-user>
NATS_MONITOR_PASSWORD=<secure-password-min-16-chars>
NATS_CLUSTER_USER=<cluster-user>
NATS_CLUSTER_PASSWORD=<secure-password-min-16-chars>
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222

# JWT Authentication
JWT_SECRET_KEY=<min-32-chars-secret-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# MQTT (IoT Devices)
MQTT_PASSWORD=<secure-password-min-16-chars>
MQTT_HOST=mqtt
MQTT_PORT=1883
MQTT_WS_PORT=9001

# Vault (Secrets Management)
VAULT_DEV_ROOT_TOKEN_ID=dev-only-token
VAULT_ADDR=http://vault:8200

# Etcd (Milvus Metadata)
ETCD_ROOT_USERNAME=<etcd-user>
ETCD_ROOT_PASSWORD=<secure-password-min-16-chars>

# MinIO (Milvus Object Storage)
MINIO_ROOT_USER=<min-16-chars>
MINIO_ROOT_PASSWORD=<min-16-chars>
MINIO_BUCKET=milvus
```

### General Configuration

```bash
# Environment
ENVIRONMENT=development  # development | staging | production
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR | CRITICAL

# Application
APP_NAME=SAHOOL
APP_VERSION=16.0.0
API_VERSION=v1

# Timezone
TZ=UTC
```

---

## 🌐 External API Keys

### Satellite Imagery Services

```bash
# Sentinel Hub (vegetation-analysis-service)
SENTINEL_HUB_CLIENT_ID=<your-client-id>
SENTINEL_HUB_CLIENT_SECRET=<your-client-secret>
SENTINEL_HUB_INSTANCE_ID=<your-instance-id>

# NASA Earthdata (vegetation-analysis-service)
NASA_EARTHDATA_USERNAME=<your-username>
NASA_EARTHDATA_PASSWORD=<your-password>

# Planet Labs (vegetation-analysis-service) - OPTIONAL
PLANET_API_KEY=<your-api-key>
```

### Weather Services

```bash
# OpenWeatherMap (weather-service)
OPENWEATHERMAP_API_KEY=<your-api-key>

# WeatherAPI (weather-service)
WEATHERAPI_KEY=<your-api-key>

# Visual Crossing (weather-service) - OPTIONAL
VISUAL_CROSSING_API_KEY=<your-api-key>
```

### AI/LLM Services

```bash
# Anthropic Claude (ai-advisor, ground-vision-service)
ANTHROPIC_API_KEY=<your-api-key>
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# OpenAI (ai-advisor)
OPENAI_API_KEY=<your-api-key>
OPENAI_MODEL=gpt-4o

# Google Gemini (ai-advisor)
GOOGLE_API_KEY=<your-api-key>
GEMINI_MODEL=gemini-1.5-pro

# Ollama (Local LLM - ai-advisor, code-review-service)
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2

# HuggingFace (huggingface_provider - embeddings, Arabic NLP)
HF_TOKEN=<your-hf-token>
HUGGINGFACE_API_TOKEN=<your-hf-token>
HUGGINGFACE_CACHE_DIR=/tmp/huggingface
HUGGINGFACE_MODEL_DIR=/tmp/huggingface/models
HUGGINGFACE_MODEL_REVISION=main  # Pin model revision for reproducibility (default: main)
```

### Notification Services

```bash
# SMTP Email (notification-service)
SMTP_HOST=<smtp-server>
SMTP_PORT=587
SMTP_USER=<smtp-username>
SMTP_PASSWORD=<smtp-password>
SMTP_FROM_EMAIL=noreply@sahool.com
SMTP_FROM_NAME=SAHOOL Platform

# SendGrid (notification-service) - OPTIONAL
SENDGRID_API_KEY=<your-api-key>

# Twilio SMS (notification-service)
TWILIO_ACCOUNT_SID=<your-account-sid>
TWILIO_AUTH_TOKEN=<your-auth-token>
TWILIO_PHONE_NUMBER=<your-phone-number>

# Twilio WhatsApp (notification-service)
TWILIO_WHATSAPP_NUMBER=<your-whatsapp-number>

# Meta WhatsApp Business (notification-service) - OPTIONAL
META_WHATSAPP_ACCESS_TOKEN=<your-access-token>
META_WHATSAPP_PHONE_NUMBER_ID=<your-phone-number-id>

# Firebase Cloud Messaging (notification-service)
FCM_SERVER_KEY=<your-server-key>
FIREBASE_CREDENTIALS_JSON=<base64-encoded-credentials>

# Telegram Bot (notification-service)
TELEGRAM_BOT_TOKEN=<your-bot-token>
```

### Payment Services

```bash
# Stripe (billing-core)
STRIPE_API_KEY=<your-api-key>
STRIPE_WEBHOOK_SECRET=<your-webhook-secret>
STRIPE_PUBLISHABLE_KEY=<your-publishable-key>

# Tharwatt (billing-core)
THARWATT_API_KEY=<your-api-key>
THARWATT_MERCHANT_ID=<your-merchant-id>
THARWATT_WEBHOOK_SECRET=<your-webhook-secret>
```

### Social Media Integration

```bash
# WeChat (wechat-service)
WECHAT_APP_ID=<your-app-id>
WECHAT_APP_SECRET=<your-app-secret>
WECHAT_TOKEN=<your-token>
WECHAT_ENCODING_AES_KEY=<your-aes-key>
```

---

## 📦 Service-Specific Variables

### user-service (Port 3025)

```bash
PORT=3025
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=${JWT_ALGORITHM}
NOTIFICATION_SERVICE_URL=http://notification-service:8110
```

### field-management-service (Port 3000)

```bash
PORT=3000
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
JWT_SECRET_KEY=${JWT_SECRET_KEY}
```

### vegetation-analysis-service (Port 8090)

```bash
PORT=8090
LOG_LEVEL=${LOG_LEVEL}
ENVIRONMENT=${ENVIRONMENT}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
SENTINEL_HUB_CLIENT_ID=${SENTINEL_HUB_CLIENT_ID}
SENTINEL_HUB_CLIENT_SECRET=${SENTINEL_HUB_CLIENT_SECRET}
SENTINEL_HUB_INSTANCE_ID=${SENTINEL_HUB_INSTANCE_ID}
NASA_EARTHDATA_USERNAME=${NASA_EARTHDATA_USERNAME}
NASA_EARTHDATA_PASSWORD=${NASA_EARTHDATA_PASSWORD}
```

### weather-service (Port 8092)

```bash
PORT=8092
LOG_LEVEL=${LOG_LEVEL}
ENVIRONMENT=${ENVIRONMENT}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
OPENWEATHERMAP_API_KEY=${OPENWEATHERMAP_API_KEY}
WEATHERAPI_KEY=${WEATHERAPI_KEY}
```

### ai-advisor (Port 8112)

```bash
SERVICE_PORT=8112
LOG_LEVEL=${LOG_LEVEL}
ENVIRONMENT=${ENVIRONMENT}
USE_MULTI_PROVIDER=true
PRIMARY_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
CLAUDE_MODEL=${CLAUDE_MODEL}
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_MODEL=${OPENAI_MODEL}
GOOGLE_API_KEY=${GOOGLE_API_KEY}
GEMINI_MODEL=${GEMINI_MODEL}
OLLAMA_BASE_URL=${OLLAMA_URL}
OLLAMA_MODEL=${OLLAMA_MODEL}
MAX_TOKENS=4096
TEMPERATURE=0.7
CROP_HEALTH_URL=http://crop-intelligence-service:8095
WEATHER_URL=http://weather-service:8092
SATELLITE_URL=http://vegetation-analysis-service:8090
AGRO_ADVISOR_URL=http://advisory-service:8093
NDVI_URL=http://vegetation-analysis-service:8090
QDRANT_HOST=qdrant
QDRANT_PORT=6333
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
```

### notification-service (Port 8110)

```bash
PORT=8110
LOG_LEVEL=${LOG_LEVEL}
ENVIRONMENT=${ENVIRONMENT}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=${SMTP_PORT}
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
SMTP_FROM_EMAIL=${SMTP_FROM_EMAIL}
SMTP_FROM_NAME=${SMTP_FROM_NAME}
TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
TWILIO_WHATSAPP_NUMBER=${TWILIO_WHATSAPP_NUMBER}
FCM_SERVER_KEY=${FCM_SERVER_KEY}
FIREBASE_CREDENTIALS_JSON=${FIREBASE_CREDENTIALS_JSON}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
```

### billing-core (Port 8089)

```bash
PORT=8089
LOG_LEVEL=${LOG_LEVEL}
ENVIRONMENT=${ENVIRONMENT}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
STRIPE_API_KEY=${STRIPE_API_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
THARWATT_API_KEY=${THARWATT_API_KEY}
THARWATT_MERCHANT_ID=${THARWATT_MERCHANT_ID}
```

### ground-vision-service (Port 8182)

```bash
PORT=8182
LOG_LEVEL=${LOG_LEVEL}
ENVIRONMENT=${ENVIRONMENT}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OLLAMA_URL=${OLLAMA_URL}
USE_OLLAMA=false
SAM_MODEL_PATH=/models/sam_vit_h.pth
YOLO_MODEL_PATH=/models/yolo_agri_ops.pt
```

---

## ⚠️ Missing Environment Variables

### Services with Incomplete Configuration

The following services are missing critical environment variables:

#### 1. marketplace-service (Port 3010)
**Missing:**
- Payment gateway credentials (if using payments)
- Third-party marketplace integrations

#### 2. research-core (Port 3015)
**Missing:**
- External research database credentials (if applicable)

#### 3. disaster-assessment (Port 3020)
**Missing:**
- Disaster data API keys (if using external sources)

#### 4. iot-service (Port 8117)
**Missing:**
- IoT platform credentials (if using third-party platforms)

#### 5. chat-service (Port 8114)
**Missing:**
- File upload storage credentials (S3/MinIO)

#### 6. community-chat (Port 8097) ⚠️ DEPRECATED
**Missing:**
- Complete configuration (service is deprecated)

#### 7. crop-intelligence-service (Port 8095)
**Missing:**
- ML model API keys (if using external models)

#### 8. irrigation-smart (Port 8094)
**Missing:**
- Irrigation hardware API credentials (if applicable)

#### 9. indicators-service (Port 8091)
**Missing:**
- External indicator data sources (if applicable)

#### 10. virtual-sensors (Port 8119)
**Missing:**
- Sensor calibration parameters

---

## 🔒 Security Best Practices

### 1. Never Commit Secrets
- Use `.env` files (add to `.gitignore`)
- Use environment-specific files (`.env.development`, `.env.production`)
- Use secrets management (Vault, AWS Secrets Manager, etc.)

### 2. Rotate Credentials Regularly
- Database passwords: Every 90 days
- API keys: Every 180 days
- JWT secrets: Every 365 days

### 3. Use Strong Passwords
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- Use password generators

### 4. Limit Access
- Use role-based access control (RBAC)
- Principle of least privilege
- Separate production and development credentials

---

## 📝 .env Template

Create a `.env` file in the project root with the following template:

```bash
# ============================================================================
# SAHOOL v16.0.0 Environment Configuration
# ============================================================================

# ----------------------------------------------------------------------------
# Core Infrastructure
# ----------------------------------------------------------------------------
POSTGRES_USER=sahool
POSTGRES_PASSWORD=
POSTGRES_DB=sahool

REDIS_PASSWORD=

NATS_USER=
NATS_PASSWORD=
NATS_ADMIN_USER=
NATS_ADMIN_PASSWORD=
NATS_MONITOR_USER=
NATS_MONITOR_PASSWORD=
NATS_CLUSTER_USER=
NATS_CLUSTER_PASSWORD=

JWT_SECRET_KEY=

MQTT_PASSWORD=

ETCD_ROOT_USERNAME=
ETCD_ROOT_PASSWORD=

MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=

# ----------------------------------------------------------------------------
# General Configuration
# ----------------------------------------------------------------------------
ENVIRONMENT=development
LOG_LEVEL=INFO

# ----------------------------------------------------------------------------
# External APIs - Satellite Imagery
# ----------------------------------------------------------------------------
SENTINEL_HUB_CLIENT_ID=
SENTINEL_HUB_CLIENT_SECRET=
SENTINEL_HUB_INSTANCE_ID=

NASA_EARTHDATA_USERNAME=
NASA_EARTHDATA_PASSWORD=

# ----------------------------------------------------------------------------
# External APIs - Weather
# ----------------------------------------------------------------------------
OPENWEATHERMAP_API_KEY=
WEATHERAPI_KEY=

# ----------------------------------------------------------------------------
# External APIs - AI/LLM
# ----------------------------------------------------------------------------
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=

# ----------------------------------------------------------------------------
# External APIs - Notifications
# ----------------------------------------------------------------------------
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@sahool.com

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
TWILIO_WHATSAPP_NUMBER=

FCM_SERVER_KEY=
FIREBASE_CREDENTIALS_JSON=

TELEGRAM_BOT_TOKEN=

# ----------------------------------------------------------------------------
# External APIs - Payments
# ----------------------------------------------------------------------------
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=

THARWATT_API_KEY=
THARWATT_MERCHANT_ID=

# ----------------------------------------------------------------------------
# External APIs - Social Media
# ----------------------------------------------------------------------------
WECHAT_APP_ID=
WECHAT_APP_SECRET=
WECHAT_TOKEN=
WECHAT_ENCODING_AES_KEY=
```

---

## 🚀 Quick Start

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Fill in required values:**
   - Core infrastructure passwords
   - JWT secret key
   - External API keys (as needed)

3. **Validate configuration:**
   ```bash
   docker-compose config
   ```

4. **Start services:**
   ```bash
   docker-compose up -d
   ```

---

**Last Updated:** 2026-01-30  
**Maintainer:** SAHOOL Platform Team
