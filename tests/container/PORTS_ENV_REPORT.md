# SAHOOL Services - Ports and Environment Variables Report

**Generated:** 2026-01-06
**Location:** `/home/user/sahool-unified-v15-idp/tests/container/PORTS_ENV_REPORT.md`

## Executive Summary

This report documents all ports and environment variables for services in `/home/user/sahool-unified-v15-idp/apps/services/`. It cross-references:
- EXPOSE instructions in Dockerfiles
- ENV instructions in Dockerfiles
- Port mappings in docker-compose.yml
- Kong upstream configurations
- Required environment variables from .env.example files

## Port Conflicts Detected

### Critical Port Conflicts

1. **Port 8080 Conflict**
   - `agent-registry` (FROZEN - Dockerfile EXPOSE 8080)
   - `field-ops` (Active - docker-compose.yml maps 8080:8080)
   - **Resolution:** agent-registry suggests port 8121

2. **Port 8095 Conflict**
   - `crop-health-ai` (FROZEN - replaced by crop-intelligence-service)
   - `crop-intelligence-service` (Active - EXPOSE 8095)
   - **Status:** Legacy service frozen, no conflict in production

3. **Port 8096 Conflict**
   - `virtual-sensors` (Dockerfile EXPOSE 8096)
   - `code-review-service` (Active - docker-compose.yml maps 8096:8096)
   - **Resolution:** Investigate virtual-sensors usage

4. **Port 8098 Conflict**
   - `yield-engine` (Dockerfile EXPOSE 8098)
   - `yield-prediction-service` (Dockerfile EXPOSE 8098)
   - **Kong Configuration:** Kong routes to yield-prediction-service:8098 for both services

5. **Port 8120 Conflict**
   - `ai-agents-core` (FROZEN - EXPOSE 8120)
   - `globalgap-compliance` (FROZEN - EXPOSE 8120)
   - `field-intelligence` (Active - docker-compose.yml maps 8120:8120)
   - **Resolution:** ai-agents-core suggests port 8122

6. **Port 3020 Conflict**
   - `disaster-assessment` (docker-compose.yml maps 3020:3020)
   - `user-service` (Dockerfile EXPOSE 3020)
   - **Status:** Needs investigation

## Service Port Inventory

### Starter Package Services (Ports 8090-8119)

| Service | Dockerfile EXPOSE | docker-compose Port | Kong Upstream | Kong Route | Status |
|---------|-------------------|---------------------|---------------|------------|--------|
| **advisory-service** | 8093 | 8093:8093 | advisory-service:8093 | /api/v1/advice, /api/v1/advisory | ✅ Active |
| **agro-advisor** | 8105 | 8105:8105 | (via advisory-service) | /api/v1/agro-advisor (legacy) | ⚠️ Deprecated |
| **astronomical-calendar** | 8111 | 8111:8111 | astronomical-calendar:8111 | /api/v1/astronomical, /api/v1/calendar | ✅ Active |
| **notification-service** | 8110 | 8110:8110 | notification-service:8110 | /api/v1/notifications | ✅ Active |
| **weather-service** | 8092 | 8092:8092 | weather-service:8092 | /api/v1/weather | ✅ Active |
| **weather-advanced** | 8092 | (uses weather-service) | weather-service:8092 | /api/v1/weather/advanced | ⚠️ Consolidated |
| **weather-core** | 8108 | 8108:8108 | Not in Kong | - | ⚠️ Not exposed via Kong |

### Professional Package Services (Ports 8090-8120)

| Service | Dockerfile EXPOSE | docker-compose Port | Kong Upstream | Kong Route | Status |
|---------|-------------------|---------------------|---------------|------------|--------|
| **crop-intelligence-service** | 8095 | 8095:8095 | crop-intelligence-service:8095 | /api/v1/crop-health | ✅ Active |
| **equipment-service** | 8101 | 8101:8101 | equipment-service:8101 | /api/v1/equipment | ✅ Active |
| **field-intelligence** | 8120 | 8120:8120 | field-intelligence:8120 | /api/v1/field-intelligence | ✅ Active |
| **indicators-service** | 8091 | 8091:8091 | indicators-service:8091 | /api/v1/indicators | ✅ Active |
| **inventory-service** | 8116 | 8116:8116 | inventory-service:8116 | /api/v1/inventory | ✅ Active |
| **irrigation-smart** | 8094 | 8094:8094 | irrigation-smart:8094 | /api/v1/irrigation | ✅ Active |
| **ndvi-engine** | 8107 | 8107:8107 | Not in Kong | - | ⚠️ Not exposed via Kong |
| **ndvi-processor** | 8118 | 8118:8118 | ndvi-processor:8118 | /api/v1/ndvi, /api/v1/ndvi-processor | ✅ Active |
| **satellite-service** | 8090 | Not mapped | vegetation-analysis-service:8090 | /api/v1/satellite | ⚠️ Uses vegetation-analysis |
| **vegetation-analysis-service** | 8090 | 8090:8090 | vegetation-analysis-service:8090 | /api/v1/satellite | ✅ Active |
| **virtual-sensors** | 8096 | Not mapped | virtual-sensors:8119 | /api/v1/sensors/virtual | ⚠️ Port mismatch (8096 vs 8119) |
| **yield-engine** | 8098 | Not mapped | yield-prediction-service:8098 | /api/v1/yield | ⚠️ Uses yield-prediction-service |
| **yield-prediction-service** | 8098 | 8098:8098 | yield-prediction-service:8098 | /api/v1/yield | ✅ Active |

### Enterprise Package Services

| Service | Dockerfile EXPOSE | docker-compose Port | Kong Upstream | Kong Route | Status |
|---------|-------------------|---------------------|---------------|------------|--------|
| **ai-advisor** | 8112 | 8112:8112 | ai-advisor:8112 | /api/v1/ai-advisor | ✅ Active |
| **billing-core** | 8089 | 8089:8089 | billing-core:8089 | /api/v1/billing | ✅ Active |
| **iot-gateway** | 8106 | 8106:8106 | iot-gateway:8106 | /api/v1/iot, /api/v1/agro-rules | ✅ Active |
| **iot-service** | 8117 | 8117:8117 | iot-service:8117 | /api/v1/iot-service | ✅ Active |

### Node.js Services (Ports 3000-3023)

| Service | Dockerfile EXPOSE | docker-compose Port | Kong Upstream | Kong Route | Status |
|---------|-------------------|---------------------|---------------|------------|--------|
| **chat-service** | 8114 | 8114:8114 | chat-service:8114 | /api/v1/chat | ✅ Active |
| **community-chat** | 8097 | 8097:8097 | community-chat:8097 | /api/v1/community/chat | ✅ Active |
| **crop-growth-model** | 3023 | 3023:3023 | crop-growth-model:3023 | /api/v1/crop-model | ✅ Active |
| **disaster-assessment** | 3020 | 3020:3020 | disaster-assessment:3020 | /api/v1/disaster | ✅ Active |
| **field-chat** | 8099 | 8099:8099 | field-chat:8099 | /api/v1/field/chat | ✅ Active |
| **field-core** | 3000 | Not mapped | field-management-service:3000 | /api/v1/fields | ⚠️ Uses field-management-service |
| **field-management-service** | 3000 | 3000:3000 | field-management-service:3000 | /api/v1/fields, /api/v1/field-ops | ✅ Active |
| **lai-estimation** | 3022 | 3022:3022 | lai-estimation:3022 | /api/v1/lai | ✅ Active |
| **marketplace-service** | 3010 | 3010:3010 | marketplace-service:3010 | /api/v1/marketplace | ✅ Active |
| **research-core** | 3015 | 3015:3015 | research-core:3015 | /api/v1/research | ✅ Active |
| **yield-prediction** | 3021 | 3021:3021 | yield-prediction:3021 | /api/v1/yield-prediction | ✅ Active |

### Supporting Services

| Service | Dockerfile EXPOSE | docker-compose Port | Kong Upstream | Kong Route | Status |
|---------|-------------------|---------------------|---------------|------------|--------|
| **alert-service** | 8113 | 8113:8113 | alert-service:8113 | /api/v1/alerts | ✅ Active |
| **code-review-service** | 8096 | 8096:8096 | code-review-service:8096 | /api/v1/code-review | ✅ Active |
| **crop-health** | 8100 | 8100:8100 | Not in Kong | - | ⚠️ Not exposed via Kong |
| **field-ops** | 8080 | 8080:8080 | field-management-service:3000 | /api/v1/field-ops | ⚠️ Port mismatch |
| **field-service** | 8115 | 8115:8115 | field-management-service:3000 | /api/v1/field-service | ⚠️ Port mismatch |
| **mcp-server** | 8200 | 8200:8200 | mcp-server:8200 | /api/v1/mcp | ✅ Active |
| **provider-config** | 8104 | 8104:8104 | provider-config:8104 | /api/v1/providers | ✅ Active |
| **task-service** | 8103 | 8103:8103 | task-service:8103 | /api/v1/tasks | ✅ Active |
| **ws-gateway** | 8081 | 8081:8081 | ws-gateway:8081 | /api/v1/ws | ✅ Active |

### Worker Services (No HTTP Port)

| Service | Dockerfile EXPOSE | docker-compose Port | Kong Upstream | Status |
|---------|-------------------|---------------------|---------------|--------|
| **agro-rules** | None (NATS worker) | - | - | ✅ Worker only |
| **demo-data** | None (data loader) | - | - | ✅ Init container |

### Frozen/Deprecated Services

| Service | Dockerfile EXPOSE | Reason | Suggested Port |
|---------|-------------------|--------|----------------|
| **agent-registry** | 8080 | Port conflict with field-ops | 8121 |
| **ai-agents-core** | 8120 | Port conflict with field-intelligence | 8122 |
| **crop-health-ai** | 8095 | Replaced by crop-intelligence-service | - |
| **fertilizer-advisor** | 8093 | Consolidated into advisory-service | - |
| **globalgap-compliance** | 8120 | Port conflict | - |
| **user-service** | 3020 | Port conflict with disaster-assessment | - |

## Environment Variables

### Common Environment Variables (All Services)

#### Database Connection
- `DATABASE_URL` - PostgreSQL connection string
- `DB_HOST` - Database host (default: postgres)
- `DB_PORT` - Database port (default: 5432)
- `DB_USER` - Database user (default: sahool)
- `DB_PASSWORD` - Database password (required)
- `DB_NAME` - Database name (default: sahool)

#### Message Queue
- `NATS_URL` - NATS connection URL (default: nats://nats:4222)
- `NATS_USER` - NATS username
- `NATS_PASSWORD` - NATS password

#### Caching
- `REDIS_URL` - Redis connection URL (default: redis://redis:6379/0)
- `REDIS_HOST` - Redis host (default: redis)
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_PASSWORD` - Redis password (required)

#### Service Configuration
- `PORT` - Service HTTP port
- `NODE_ENV` - Node.js environment (production/development)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/ERROR)
- `ENVIRONMENT` - Application environment (production/staging/development)

#### Authentication & Security
- `JWT_SECRET_KEY` - JWT signing secret (required)
- `JWT_EXPIRES_IN` - JWT expiration time (default: 7d)
- `CORS_ALLOWED_ORIGINS` - CORS allowed origins

### Service-Specific Environment Variables

#### advisory-service (Port 8093)
```bash
PORT=8093
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
```
**Environment Variable Count:** 5 vars

#### agro-advisor (Port 8105) [DEPRECATED]
```bash
PORT=8105
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
LOG_LEVEL=INFO
ENVIRONMENT=production
REDIS_URL=redis://:password@redis:6379/0
OLLAMA_URL=http://ollama:11434
```
**Environment Variable Count:** 7 vars

#### agro-rules (NATS Worker)
```bash
NATS_URL=nats://nats:4222
FIELDOPS_URL=http://field-ops:8080
LOG_LEVEL=INFO
ENVIRONMENT=production
```
**Environment Variable Count:** 4 vars

#### ai-advisor (Port 8112)
```bash
SERVICE_PORT=8112
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
REDIS_URL=redis://:password@redis:6379/0
NATS_URL=nats://nats:4222
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=${QDRANT_API_KEY}
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b
# Plus 10 more AI-related variables
```
**Environment Variable Count:** 20 vars

#### alert-service (Port 8113)
```bash
PORT=8113
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
```
**Environment Variable Count:** 6 vars

#### astronomical-calendar (Port 8111)
```bash
PORT=8111
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
```
**Environment Variable Count:** 4 vars

#### billing-core (Port 8089)
```bash
PORT=8089
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
REDIS_URL=redis://:password@redis:6379/0
NATS_URL=nats://nats:4222
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
PAYMENT_GATEWAY=stripe
CURRENCY=USD
# Plus 2 more payment-related variables
```
**Environment Variable Count:** 12 vars

#### chat-service (Port 8114)
```bash
PORT=8114
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool_chat
JWT_SECRET=${JWT_SECRET_KEY}
JWT_EXPIRES_IN=7d
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
CDN_URL=https://cdn.sahool.com
MAX_FILE_SIZE=10485760
MARKETPLACE_SERVICE_URL=http://marketplace-service:3010
USER_SERVICE_URL=http://user-service:3020
NOTIFICATION_SERVICE_URL=http://notification-service:8110
CORS_ALLOWED_ORIGINS=https://sahool.com,https://app.sahool.com
```
**Environment Variable Count:** 7 vars (from docker-compose)
**Additional from .env.example:** 14+ vars

#### code-review-service (Port 8096)
```bash
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=codellama:7b
WATCH_PATHS=/app/repos
MAX_FILE_SIZE=10485760
SUPPORTED_LANGUAGES=python,javascript,typescript,go
LOG_LEVEL=INFO
ENVIRONMENT=production
PROMETHEUS_PORT=9090
```
**Environment Variable Count:** 8 vars

#### community-chat (Port 8097)
```bash
PORT=8097
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
REDIS_URL=redis://:password@redis:6379/0
NATS_URL=nats://nats:4222
JWT_SECRET=${JWT_SECRET_KEY}
```
**Environment Variable Count:** 6 vars

#### crop-growth-model (Port 3023)
```bash
PORT=3023
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
WOFOST_DATA_PATH=/app/data/wofost
DSSAT_DATA_PATH=/app/data/dssat
WEATHER_SERVICE_URL=http://weather-service:8092
SOIL_SERVICE_URL=http://satellite-service:8090
# Plus 2 more model-related variables
```
**Environment Variable Count:** 9 vars

#### crop-health (Port 8100)
```bash
PORT=8100
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
```
**Environment Variable Count:** 4 vars

#### crop-intelligence-service (Port 8095)
```bash
PORT=8095
MODEL_PATH=/app/models
LOG_LEVEL=INFO
ENVIRONMENT=production
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=${MINIO_ROOT_USER}
```
**Environment Variable Count:** 6 vars

#### disaster-assessment (Port 3020)
```bash
PORT=3020
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
SATELLITE_SERVICE_URL=http://vegetation-analysis-service:8090
WEATHER_SERVICE_URL=http://weather-service:8092
# Plus 4 more disaster-related variables
```
**Environment Variable Count:** 9 vars

#### equipment-service (Port 8101)
```bash
PORT=8101
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
LOG_LEVEL=INFO
```
**Environment Variable Count:** 4 vars

#### field-chat (Port 8099)
```bash
PORT=8099
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
JWT_SECRET=${JWT_SECRET_KEY}
# Plus 3 more chat-related variables
```
**Environment Variable Count:** 8 vars

#### field-intelligence (Port 8120)
```bash
PORT=8120
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
OLLAMA_URL=http://ollama:11434
QDRANT_URL=http://qdrant:6333
# Plus 2 more AI-related variables
```
**Environment Variable Count:** 8 vars

#### field-management-service (Port 3000)
```bash
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
DB_HOST=postgres
DB_PORT=5432
DB_USER=sahool
DB_PASSWORD=${POSTGRES_PASSWORD}
DB_NAME=sahool
REDIS_URL=redis://:password@redis:6379/0
NATS_URL=nats://nats:4222
JWT_SECRET_KEY=${JWT_SECRET_KEY}
```
**Environment Variable Count:** 11 vars

#### field-ops (Port 8080)
```bash
PORT=8080
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
# Plus 4 more operations-related variables
```
**Environment Variable Count:** 8 vars

#### field-service (Port 8115)
```bash
PORT=8115
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
```
**Environment Variable Count:** 6 vars

#### indicators-service (Port 8091)
```bash
PORT=8091
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
```
**Environment Variable Count:** 5 vars

#### inventory-service (Port 8116)
```bash
PORT=8116
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
```
**Environment Variable Count:** 5 vars
**From .env.example:**
- `SERVICE_NAME=inventory-service`

#### iot-gateway (Port 8106)
```bash
PORT=8106
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
MQTT_URL=mqtt://mqtt:1883
MQTT_USER=${MQTT_USER}
MQTT_PASSWORD=${MQTT_PASSWORD}
# Plus 5 more IoT-related variables
```
**Environment Variable Count:** 12 vars

#### iot-service (Port 8117)
```bash
PORT=8117
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
MQTT_URL=mqtt://mqtt:1883
MQTT_USER=${MQTT_USER}
MQTT_PASSWORD=${MQTT_PASSWORD}
NATS_URL=nats://nats:4222
# Plus 4 more IoT-related variables
```
**Environment Variable Count:** 11 vars

#### irrigation-smart (Port 8094)
```bash
PORT=8094
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
WEATHER_SERVICE_URL=http://weather-service:8092
SENSOR_SERVICE_URL=http://virtual-sensors:8119
```
**Environment Variable Count:** 6 vars

#### lai-estimation (Port 3022)
```bash
PORT=3022
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
SATELLITE_SERVICE_URL=http://vegetation-analysis-service:8090
MODEL_PATH=/app/models
# Plus 4 more estimation-related variables
```
**Environment Variable Count:** 9 vars

#### marketplace-service (Port 3010)
```bash
PORT=3010
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
REDIS_URL=redis://:password@redis:6379/0
NATS_URL=nats://nats:4222
JWT_SECRET=${JWT_SECRET_KEY}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
```
**Environment Variable Count:** 7 vars

#### mcp-server (Port 8200)
```bash
SAHOOL_API_URL=http://kong:8000
MCP_SERVER_PORT=8200
MCP_SERVER_HOST=0.0.0.0
LOG_LEVEL=INFO
ENVIRONMENT=production
```
**Environment Variable Count:** 5 vars

#### ndvi-engine (Port 8107)
```bash
PORT=8107
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
MINIO_URL=http://minio:9000
# Plus 3 more processing-related variables
```
**Environment Variable Count:** 7 vars

#### ndvi-processor (Port 8118)
```bash
PORT=8118
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=${MINIO_ROOT_USER}
```
**Environment Variable Count:** 6 vars

#### notification-service (Port 8110)
```bash
PORT=8110
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
# Plus 6 more notification provider variables
```
**Environment Variable Count:** 12 vars
**From .env.example:**
- `SERVICE_NAME=notification-service`
- `SERVICE_VERSION=15.4.0`
- `SERVICE_PORT=8110`
- `NATS_SUBJECT=sahool.notifications.*`
- `FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json`
- `TWILIO_ACCOUNT_SID=your_account_sid_here`
- `TWILIO_AUTH_TOKEN=your_auth_token_here`
- `TWILIO_FROM_NUMBER=+1234567890`
- `SENDGRID_API_KEY=your_sendgrid_api_key_here`
- `SENDGRID_FROM_EMAIL=notifications@sahool.app`
- `SENDGRID_FROM_NAME=SAHOOL Agriculture Platform`
- `CREATE_DB_SCHEMA=false` (dev only)

#### provider-config (Port 8104)
```bash
PORT=8104
LOG_LEVEL=INFO
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
```
**Environment Variable Count:** 5 vars

#### research-core (Port 3015)
```bash
PORT=3015
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
REDIS_URL=redis://:password@redis:6379/0
NATS_URL=nats://nats:4222
MINIO_URL=http://minio:9000
# Plus 4 more research-related variables
```
**Environment Variable Count:** 10 vars

#### task-service (Port 8103)
```bash
PORT=8103
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
```
**Environment Variable Count:** 4 vars

#### vegetation-analysis-service (Port 8090)
```bash
PORT=8090
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=${MINIO_ROOT_USER}
MINIO_SECRET_KEY=${MINIO_ROOT_PASSWORD}
SENTINEL_API_USER=${SENTINEL_API_USER}
SENTINEL_API_PASSWORD=${SENTINEL_API_PASSWORD}
# Plus 3 more satellite-related variables
```
**Environment Variable Count:** 13 vars

#### virtual-sensors (Port 8119)
```bash
PORT=8119
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
WEATHER_SERVICE_URL=http://weather-service:8092
```
**Environment Variable Count:** 5 vars
**Note:** Dockerfile EXPOSE 8096 but Kong routes to :8119

#### weather-core (Port 8108)
```bash
PORT=8108
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
WEATHERSTACK_API_KEY=${WEATHERSTACK_API_KEY}
# Plus 6 more weather provider variables
```
**Environment Variable Count:** 11 vars

#### weather-service (Port 8092)
```bash
PORT=8092
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
NATS_URL=nats://nats:4222
OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
REDIS_URL=redis://:password@redis:6379/0
```
**Environment Variable Count:** 7 vars

#### ws-gateway (Port 8081)
```bash
PORT=8081
NATS_URL=nats://nats:4222
REDIS_URL=redis://:password@redis:6379/0
JWT_SECRET=${JWT_SECRET_KEY}
CORS_ALLOWED_ORIGINS=*
# Plus 3 more WebSocket-related variables
```
**Environment Variable Count:** 8 vars

#### yield-prediction (Port 3021)
```bash
PORT=3021
NODE_ENV=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
MODEL_PATH=/app/models
WEATHER_SERVICE_URL=http://weather-service:8092
SATELLITE_SERVICE_URL=http://vegetation-analysis-service:8090
# Plus 3 more prediction-related variables
```
**Environment Variable Count:** 9 vars

#### yield-prediction-service (Port 8098)
```bash
PORT=8098
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
MODEL_PATH=/app/models
```
**Environment Variable Count:** 5 vars

## Critical Mismatches

### 1. virtual-sensors Port Mismatch
- **Dockerfile EXPOSE:** 8096
- **Kong Upstream:** virtual-sensors:8119
- **Impact:** Service will not be reachable via Kong
- **Recommendation:** Update Dockerfile to EXPOSE 8119 OR update Kong upstream to :8096

### 2. field-ops Port Mismatch
- **Dockerfile EXPOSE:** 8080
- **docker-compose Port:** 8080:8080
- **Kong Route:** Points to field-management-service:3000
- **Impact:** Kong route does not match actual service
- **Recommendation:** Update Kong to route to field-ops:8080 OR clarify service consolidation

### 3. field-service Port Mismatch
- **Dockerfile EXPOSE:** 8115
- **docker-compose Port:** 8115:8115
- **Kong Route:** Points to field-management-service:3000
- **Impact:** Kong route does not match actual service
- **Recommendation:** Update Kong to route to field-service:8115 OR clarify service consolidation

### 4. satellite-service Indirect Routing
- **Dockerfile EXPOSE:** 8090
- **docker-compose:** No direct mapping
- **Kong Route:** Points to vegetation-analysis-service:8090
- **Status:** Appears to be consolidated service
- **Recommendation:** Document that satellite-service is served by vegetation-analysis-service

### 5. yield-engine Indirect Routing
- **Dockerfile EXPOSE:** 8098
- **docker-compose:** No direct mapping
- **Kong Route:** Points to yield-prediction-service:8098
- **Status:** Appears to be consolidated service
- **Recommendation:** Document that yield-engine is served by yield-prediction-service

## Undocumented Required Environment Variables

### High Priority (Service will fail without these)

1. **JWT_SECRET_KEY** - Required by: all authenticated services
2. **REDIS_PASSWORD** - Required by: all services using Redis
3. **POSTGRES_PASSWORD** - Required by: all services using database
4. **NATS_PASSWORD** - Required by: all services using NATS
5. **QDRANT_API_KEY** - Required by: ai-advisor, field-intelligence
6. **OPENWEATHER_API_KEY** - Required by: weather-service, weather-core
7. **STRIPE_SECRET_KEY** - Required by: billing-core, marketplace-service
8. **STRIPE_WEBHOOK_SECRET** - Required by: billing-core
9. **MINIO_ROOT_USER** - Required by: services using MinIO storage
10. **MINIO_ROOT_PASSWORD** - Required by: services using MinIO storage
11. **SENTINEL_API_USER** - Required by: vegetation-analysis-service
12. **SENTINEL_API_PASSWORD** - Required by: vegetation-analysis-service

### Medium Priority (Graceful degradation)

1. **FIREBASE_CREDENTIALS_PATH** - For push notifications
2. **TWILIO_ACCOUNT_SID** - For SMS notifications
3. **TWILIO_AUTH_TOKEN** - For SMS notifications
4. **TWILIO_FROM_NUMBER** - For SMS notifications
5. **SENDGRID_API_KEY** - For email notifications
6. **SENDGRID_FROM_EMAIL** - For email notifications
7. **OLLAMA_MODEL** - AI model selection (has defaults)
8. **WEATHERSTACK_API_KEY** - Alternative weather provider

## Kong Configuration Summary

### Port Mappings from Kong to Services

| Kong Route | Service:Port | Health Check Path |
|------------|--------------|-------------------|
| /api/v1/fields | field-management-service:3000 | /healthz |
| /api/v1/weather | weather-service:8092 | /healthz |
| /api/v1/satellite | vegetation-analysis-service:8090 | /healthz |
| /api/v1/ai-advisor | ai-advisor:8112 | /healthz |
| /api/v1/crop-health | crop-intelligence-service:8095 | /healthz |
| /api/v1/advisory | advisory-service:8093 | /healthz |
| /api/v1/iot | iot-gateway:8106 | /healthz |
| /api/v1/iot-service | iot-service:8117 | /healthz |
| /api/v1/sensors/virtual | virtual-sensors:8119 | /healthz |
| /api/v1/marketplace | marketplace-service:3010 | /healthz |
| /api/v1/billing | billing-core:8089 | /healthz |
| /api/v1/notifications | notification-service:8110 | /healthz |
| /api/v1/research | research-core:3015 | /healthz |
| /api/v1/disaster | disaster-assessment:3020 | /healthz |
| /api/v1/field-intelligence | field-intelligence:8120 | /healthz |
| /api/v1/mcp | mcp-server:8200 | /health |
| /api/v1/code-review | code-review-service:8096 | /health |

## Recommendations

### Immediate Actions Required

1. **Fix virtual-sensors port mismatch**
   - Update Dockerfile EXPOSE from 8096 to 8119
   - OR update Kong upstream from :8119 to :8096

2. **Resolve port conflicts**
   - Disable agent-registry or reassign to port 8121
   - Disable ai-agents-core or reassign to port 8122
   - Clarify user-service vs disaster-assessment on port 3020

3. **Document service consolidations**
   - Create migration guide for deprecated services
   - Update Kong comments to reflect service consolidation
   - Remove or clearly mark frozen services

4. **Create master .env.example**
   - Consolidate all required environment variables
   - Document which variables are required vs optional
   - Provide default values where applicable

5. **Verify Kong routes**
   - Test all Kong routes match actual services
   - Fix field-ops and field-service routing
   - Add health checks for services missing them

### Medium Priority

1. **Standardize environment variable names**
   - Some services use `PORT`, others use `SERVICE_PORT`
   - Standardize on `PORT` for all services

2. **Add missing health checks**
   - crop-health service not exposed via Kong but has port mapped
   - ndvi-engine service not exposed via Kong but has port mapped
   - weather-core service not exposed via Kong but has port mapped

3. **Document service dependencies**
   - Create dependency graph showing which services call which
   - Document required external services (Redis, NATS, PostgreSQL)

4. **Create port allocation policy**
   - 3000-3023: Node.js services
   - 8089-8120: Python services
   - 8200+: Special services (MCP, etc.)

## Port Range Allocation

### Current Allocation
- **3000-3023:** Node.js services (field-management, marketplace, research, disaster, lai, crop-growth, yield-prediction)
- **8080-8120:** Python services (majority of microservices)
- **8200+:** Integration services (mcp-server)

### Reserved Ports
- **8080:** field-ops (conflicts with deprecated agent-registry)
- **8095:** crop-intelligence-service (conflicts with deprecated crop-health-ai)
- **8096:** code-review-service (conflicts with virtual-sensors Dockerfile)
- **8098:** yield-prediction-service (shared with yield-engine)
- **8119:** virtual-sensors Kong route (conflicts with Dockerfile 8096)
- **8120:** field-intelligence (conflicts with deprecated ai-agents-core and globalgap-compliance)

### Available Ports for New Services
- 8121-8199 (except 8200 reserved for mcp-server)
- 3024-3099

## Testing Checklist

- [ ] Verify all services start with documented environment variables
- [ ] Test Kong routes reach correct service ports
- [ ] Confirm health checks work for all services
- [ ] Validate JWT authentication across all authenticated endpoints
- [ ] Test NATS message passing between services
- [ ] Verify Redis caching works across all services
- [ ] Confirm database connections for all services
- [ ] Test service-to-service communication (internal APIs)
- [ ] Validate MinIO storage access for file-handling services
- [ ] Test Qdrant vector search for AI services
- [ ] Verify Ollama AI model access for AI services
- [ ] Test MQTT broker for IoT services
- [ ] Validate weather API integrations
- [ ] Test Sentinel Hub satellite data access
- [ ] Verify payment gateway integrations (Stripe)
- [ ] Test notification providers (Firebase, Twilio, SendGrid)

---

**Report Generated:** 2026-01-06
**Total Services Analyzed:** 52
**Active Services:** 37
**Deprecated Services:** 6
**Worker Services:** 2
**Port Conflicts:** 6
**Port Mismatches:** 5
