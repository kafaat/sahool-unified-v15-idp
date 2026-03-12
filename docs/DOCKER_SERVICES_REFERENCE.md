# SAHOOL Docker Services Reference

# مرجع خدمات Docker لمنصة سهول

**Version**: 16.0.0
**Last Updated**: January 2026

---

## Table of Contents | جدول المحتويات

1. [Overview | نظرة عامة](#overview)
2. [Infrastructure Services | خدمات البنية التحتية](#infrastructure-services)
3. [Node.js Services | خدمات Node.js](#nodejs-services)
4. [Python Services | خدمات Python](#python-services)
5. [Deprecated Services | الخدمات المهملة](#deprecated-services)
6. [Network Configuration | تكوين الشبكة](#network-configuration)
7. [Volume Configuration | تكوين وحدات التخزين](#volume-configuration)
8. [Service Dependencies | تبعيات الخدمات](#service-dependencies)
9. [Resource Limits Summary | ملخص حدود الموارد](#resource-limits-summary)
10. [Profiles | ملفات التعريف](#profiles)

---

## Overview

## نظرة عامة

The SAHOOL platform runs **39+ services** plus infrastructure components in a containerized environment. This document provides a comprehensive reference for all Docker services defined in `docker-compose.yml`.

تعمل منصة سهول على **39+ خدمة** بالإضافة إلى مكونات البنية التحتية في بيئة حاويات. يوفر هذا المستند مرجعًا شاملاً لجميع خدمات Docker المحددة في `docker-compose.yml`.

### Quick Stats | إحصائيات سريعة

| Category | Count |
|----------|-------|
| Infrastructure Services | 14 |
| Node.js Services | 12 |
| Python Services | 29 |
| **Total Active Services** | **39+** |
| Deprecated Services | 9 |
| Named Volumes | 14 |

---

## Infrastructure Services

## خدمات البنية التحتية

### 1. PostgreSQL with PostGIS

**قاعدة البيانات المكانية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-postgres` |
| **Image** | `postgis/postgis:16-3.4` |
| **Port** | `127.0.0.1:5432:5432` |
| **Network** | `sahool-network` |

**Description**: Primary database with geospatial support for field boundaries and location data.

**الوصف**: قاعدة البيانات الرئيسية مع دعم البيانات المكانية لحدود الحقول وبيانات الموقع.

**Environment Variables**:
- `POSTGRES_USER` (required)
- `POSTGRES_PASSWORD` (required)
- `POSTGRES_DB` (default: `sahool`)

**Volumes**:
```yaml
- postgres_data:/var/lib/postgresql/data
- ./infrastructure/core/postgres/init:/docker-entrypoint-initdb.d:ro
```

**Health Check**:
```yaml
test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-sahool}"]
interval: 30s
timeout: 10s
retries: 3
start_period: 30s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 2 | 0.5 |
| Memory | 2G | 512M |

**Security**:
- `no-new-privileges:true`
- tmpfs for `/tmp` and `/run/postgresql`
- Localhost-only port binding

---

### 2. PgBouncer

**تجميع اتصالات قاعدة البيانات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-pgbouncer` |
| **Image** | `edoburu/pgbouncer:latest` |
| **Port** | `127.0.0.1:6432:6432` |
| **Network** | `sahool-network` |

**Description**: Connection pooler to prevent connection exhaustion with 39+ services.

**الوصف**: مجمع اتصالات لمنع استنفاد الاتصالات مع أكثر من 39 خدمة.

**Key Configuration**:
- Pool Mode: `transaction`
- Max DB Connections: `250`
- Default Pool Size: `30`
- Min Pool Size: `10`
- Max Client Connections: `800`

**Volumes**:
```yaml
- ./infrastructure/core/pgbouncer/entrypoint.sh:/entrypoint-custom.sh
- ./infrastructure/core/pgbouncer/pgbouncer.ini:/etc/pgbouncer/pgbouncer.ini:ro
- ./config/certs:/etc/pgbouncer/certs:ro
```

**Dependencies**: `postgres` (healthy)

**Health Check**:
```yaml
test: ["CMD-SHELL", "pidof pgbouncer || exit 1"]
interval: 30s
timeout: 10s
retries: 5
start_period: 45s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.1 |
| Memory | 256M | 64M |

---

### 3. Redis

**التخزين المؤقت ومخزن الجلسات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-redis` |
| **Image** | `redis:7.4-alpine` |
| **Ports** | `127.0.0.1:6379:6379`, `127.0.0.1:6380:6380` (TLS) |
| **Network** | `sahool-network` |

**Description**: Cache and session store with password authentication and memory limits.

**الوصف**: ذاكرة تخزين مؤقت ومخزن جلسات مع مصادقة بكلمة مرور وحدود للذاكرة.

**Security Features**:
- Password authentication (requirepass)
- Dangerous commands renamed
- AOF persistence
- Memory limit with LRU eviction
- TLS/SSL ready

**Volumes**:
```yaml
- redis_data:/data
- ./infrastructure/redis/redis-secure.conf:/usr/local/etc/redis/redis.conf:ro
- ./config/certs:/etc/redis/certs:ro
```

**Health Check**:
```yaml
test: ["CMD-SHELL", "redis-cli -a ${REDIS_PASSWORD} ping | grep PONG"]
interval: 30s
timeout: 10s
retries: 3
start_period: 30s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 768M | 256M |

---

### 4. NATS JetStream

**قائمة انتظار الرسائل**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-nats` |
| **Image** | `nats:2.10.24-alpine` |
| **Ports** | `127.0.0.1:4222:4222` (Standard), `127.0.0.1:4223:4223` (TLS), `127.0.0.1:8222:8222` (Monitoring), `127.0.0.1:6222:6222` (Cluster) |
| **Network** | `sahool-network` |

**Description**: Message queue with authentication, TLS enforcement, and JetStream for persistence.

**الوصف**: قائمة انتظار الرسائل مع المصادقة وتطبيق TLS وJetStream للثبات.

**Environment Variables**:
- `NATS_USER`, `NATS_PASSWORD` (required)
- `NATS_ADMIN_USER`, `NATS_ADMIN_PASSWORD` (required)
- `NATS_MONITOR_USER`, `NATS_MONITOR_PASSWORD` (required)
- `NATS_CLUSTER_USER`, `NATS_CLUSTER_PASSWORD` (required)
- `NATS_JETSTREAM_KEY` (AES-256 encryption)

**Volumes**:
```yaml
- nats_data:/data
- ./config/nats/nats-secure.conf:/etc/nats/nats-secure.conf:ro
- ./config/nats/nats.conf:/etc/nats/nats.conf:ro
- ./config/certs:/etc/nats/certs:ro
```

**Health Check**:
```yaml
test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
interval: 30s
timeout: 10s
retries: 3
start_period: 30s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 5. NATS Prometheus Exporter

**مصدر مقاييس NATS لـ Prometheus**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-nats-prometheus-exporter` |
| **Image** | `natsio/prometheus-nats-exporter:0.14.0` |
| **Port** | `127.0.0.1:7777:7777` |
| **Network** | `sahool-network` |

**Description**: Exports NATS metrics for Prometheus monitoring including JetStream statistics.

**الوصف**: تصدير مقاييس NATS لمراقبة Prometheus بما في ذلك إحصائيات JetStream.

**Dependencies**: `nats` (healthy)

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.25 | 0.1 |
| Memory | 128M | 64M |

---

### 6. MQTT Broker (Mosquitto)

**وسيط MQTT للاتصالات IoT**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-mqtt` |
| **Image** | `eclipse-mosquitto:2` |
| **Ports** | `127.0.0.1:1883:1883`, `127.0.0.1:9001:9001` |
| **Network** | `sahool-network` |

**Description**: MQTT broker for IoT device communication with agricultural sensors.

**الوصف**: وسيط MQTT للاتصال بأجهزة IoT مع أجهزة الاستشعار الزراعية.

**Volumes**:
```yaml
- ./infrastructure/core/mqtt/mosquitto.conf:/mosquitto/config/mosquitto.conf.orig:ro
- ./infrastructure/core/mqtt/acl:/mosquitto/config/acl.source:ro
- ./infrastructure/core/mqtt/init-mqtt.sh:/init-mqtt.sh:ro
- mqtt_passwd:/mosquitto/config
- mqtt_data:/mosquitto/data
- mqtt_logs:/mosquitto/log
```

**Health Check**:
```yaml
test: ["CMD-SHELL", "pidof mosquitto || exit 1"]
interval: 30s
timeout: 10s
retries: 3
start_period: 15s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.1 |
| Memory | 256M | 64M |

---

### 7. Qdrant Vector Database

**قاعدة البيانات الشعاعية للبحث الدلالي**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-qdrant` |
| **Image** | `qdrant/qdrant:v1.7.4` |
| **Ports** | `127.0.0.1:6333:6333`, `127.0.0.1:6334:6334` (gRPC) |
| **Network** | `sahool-network` |

**Description**: Vector database for RAG (Retrieval Augmented Generation) and semantic search.

**الوصف**: قاعدة بيانات شعاعية لـ RAG والبحث الدلالي.

**Volumes**:
```yaml
- qdrant_data:/qdrant/storage
```

**Health Check**:
```yaml
test: ["CMD", "sh", "-c", "test -f /proc/1/cmdline"]
interval: 30s
timeout: 10s
retries: 3
start_period: 30s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1.0 | 0.25 |
| Memory | 1G | 256M |

---

### 8. Ollama (GPU Profile)

**خادم نماذج الذكاء الاصطناعي المحلي**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-ollama` |
| **Image** | `ollama/ollama:0.5.4` |
| **Port** | `127.0.0.1:11434:11434` |
| **Network** | `sahool-network` |
| **Profile** | `gpu` |

**Description**: Local LLM server for code and log analysis. Requires NVIDIA GPU.

**الوصف**: خادم نماذج لغوية كبيرة محلي لتحليل الكود والسجلات. يتطلب GPU من NVIDIA.

**Key Configuration**:
- Keep Alive: 24h
- Parallel Requests: 24
- Max Loaded Models: 2

**Volumes**:
```yaml
- ollama_data:/root/.ollama
```

**Health Check**:
```yaml
test: ["CMD-SHELL", "ollama list || exit 1"]
interval: 30s
timeout: 10s
retries: 3
start_period: 60s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 4 | 1 |
| Memory | 8G | 2G |
| GPU | All NVIDIA GPUs | - |

---

### 9. Etcd (Milvus Metadata)

**تخزين البيانات الوصفية لـ Milvus**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-etcd` |
| **Image** | `quay.io/coreos/etcd:v3.5.18` |
| **Network** | `sahool-network` |

**Description**: Metadata storage for Milvus vector database with authentication.

**الوصف**: تخزين البيانات الوصفية لقاعدة بيانات Milvus الشعاعية مع المصادقة.

**Volumes**:
```yaml
- etcd_data:/etcd
- ./infrastructure/core/etcd/init-auth.sh:/scripts/init-auth.sh:ro
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.1 |
| Memory | 512M | 128M |

---

### 10. MinIO Object Storage

**تخزين الكائنات لـ Milvus**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-minio` |
| **Image** | `minio/minio:RELEASE.2024-05-28T17-19-04Z` |
| **Ports** | `127.0.0.1:9000:9000` (API), `127.0.0.1:9090:9090` (Console) |
| **Network** | `sahool-network` |

**Description**: S3-compatible object storage with TLS and server-side encryption.

**الوصف**: تخزين كائنات متوافق مع S3 مع TLS والتشفير من جانب الخادم.

**Volumes**:
```yaml
- minio_data:/minio_data
- ./secrets/minio-certs/production/certs:/root/.minio/certs:ro
- ./scripts/security/minio-init.sh:/scripts/minio-init.sh:ro
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 1G | 256M |

---

### 11. Milvus Vector Database

**قاعدة البيانات الشعاعية Milvus**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-milvus` |
| **Image** | `milvusdb/milvus:v2.5.27` |
| **Ports** | `127.0.0.1:19530:19530`, `127.0.0.1:9091:9091` |
| **Network** | `sahool-network` |

**Description**: Alternative vector database to Qdrant for high-performance similarity search.

**الوصف**: قاعدة بيانات شعاعية بديلة لـ Qdrant للبحث عالي الأداء عن التشابه.

**Dependencies**: `etcd` (healthy), `minio` (healthy)

**Volumes**:
```yaml
- milvus_data:/var/lib/milvus
```

**Health Check**:
```yaml
test: ["CMD", "curl", "-f", "http://localhost:9091/healthz"]
interval: 30s
timeout: 10s
retries: 3
start_period: 90s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 2 | 0.5 |
| Memory | 4G | 1G |

---

### 12. Kong API Gateway

**بوابة API**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-kong` |
| **Image** | `kong:3.4` |
| **Ports** | `8000:8000` (Proxy), `127.0.0.1:8001:8001` (Admin) |
| **Network** | `sahool-network` |

**Description**: API Gateway with authentication, rate limiting, and service routing.

**الوصف**: بوابة API مع المصادقة وتحديد المعدل وتوجيه الخدمات.

**Key Configuration**:
- Database: Off (declarative mode)
- Plugins: `bundled,cors,rate-limiting,jwt,acl,prometheus`
- DNS Resolver: `127.0.0.11:53` (Docker internal)
- Worker Processes: Auto
- Keepalive Pool Size: 60

**Volumes**:
```yaml
- ./infrastructure/gateway/kong/kong.yml:/kong/declarative/kong.yml:ro
- ./infrastructure/gateway/kong/ssl:/etc/kong/ssl:ro
- kong_logs:/var/log/kong
```

**Dependencies**: `redis` (healthy)

**Health Check**:
```yaml
test: ["CMD", "kong", "health"]
interval: 30s
timeout: 10s
retries: 3
start_period: 30s
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 2 | 0.25 |
| Memory | 1G | 128M |

---

## Node.js Services

## خدمات Node.js

### 1. Field Management Service

**خدمة إدارة الحقول الموحدة**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-field-management-service` |
| **Port** | `3000:3000` |
| **Network** | `sahool-network` |

**Description**: Unified field operations service. Consolidates: field-core, field-service, field-ops.

**الوصف**: خدمة عمليات الحقول الموحدة. تجمع: field-core، field-service، field-ops.

**Dependencies**: `postgres` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 2. Marketplace Service

**خدمة السوق الزراعي**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-marketplace` |
| **Port** | `3010:3010` |
| **Network** | `sahool-network` |

**Description**: Agricultural marketplace and FinTech integration.

**الوصف**: سوق زراعي وتكامل التقنية المالية.

**Dependencies**: `postgres` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /api/v1/healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 3. Research Core

**إدارة البحوث العلمية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-research-core` |
| **Port** | `3015:3015` |
| **Network** | `sahool-network` |

**Description**: Scientific research trials management.

**الوصف**: إدارة التجارب البحثية العلمية.

**Dependencies**: `postgres` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /api/v1/healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 4. Disaster Assessment

**تقييم الكوارث**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-disaster-assessment` |
| **Port** | `3020:3020` |
| **Network** | `sahool-network` |

**Description**: Disaster risk assessment and response coordination.

**الوصف**: تقييم مخاطر الكوارث وتنسيق الاستجابة.

**Dependencies**: `postgres` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /api/v1/disasters/health`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 5. Yield Prediction (Node.js - Deprecated)

**التنبؤ بالإنتاجية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-yield-prediction` |
| **Port** | `3021:3021` |
| **Network** | `sahool-network` |
| **Status** | DEPRECATED - Migrating to yield-prediction-service (Port 8098) |

**Description**: Yield prediction ML service. Being consolidated into yield-prediction-service.

**الوصف**: خدمة التعلم الآلي للتنبؤ بالإنتاجية. يتم دمجها في yield-prediction-service.

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 6. LAI Estimation (Deprecated)

**تقدير مؤشر مساحة الورقة**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-lai-estimation` |
| **Port** | `3022:3022` |
| **Network** | `sahool-network` |
| **Status** | DEPRECATED - Migrating to vegetation-analysis-service (Port 8090) |

**Description**: Leaf Area Index estimation. Being consolidated into vegetation-analysis-service.

**الوصف**: تقدير مؤشر مساحة الورقة. يتم دمجها في vegetation-analysis-service.

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 7. Crop Growth Model (Deprecated)

**نموذج نمو المحاصيل**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-crop-growth-model` |
| **Port** | `3023:3023` |
| **Network** | `sahool-network` |
| **Status** | DEPRECATED - Migrating to crop-intelligence-service (Port 8095) |

**Description**: Crop growth simulation. Being consolidated into crop-intelligence-service.

**الوصف**: محاكاة نمو المحاصيل. يتم دمجها في crop-intelligence-service.

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 8. Chat Service

**خدمة المحادثة الزراعية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-chat-service` |
| **Port** | `8114:8114` |
| **Network** | `sahool-network` |

**Description**: Agricultural chat and messaging service.

**الوصف**: خدمة المحادثة والرسائل الزراعية.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /api/v1/health`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 9. IoT Service

**خدمة إدارة أجهزة IoT**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-iot-service` |
| **Port** | `8117:8117` |
| **Network** | `sahool-network` |

**Description**: IoT device and sensor management with MQTT integration.

**الوصف**: إدارة أجهزة IoT وأجهزة الاستشعار مع تكامل MQTT.

**Dependencies**: `postgres` (healthy), `redis` (healthy), `nats` (healthy), `mqtt` (healthy)

**Health Check Endpoint**: `GET /api/v1/health`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 10. Community Chat (Deprecated)

**محادثة المجتمع**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-community-chat` |
| **Port** | `8097:8097` |
| **Network** | `sahool-network` |
| **Status** | DEPRECATED - Migrating to chat-service (Port 8114) |

**Description**: Community features and chat. Being consolidated into chat-service.

**الوصف**: ميزات المجتمع والمحادثة. يتم دمجها في chat-service.

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 11. User Service

**خدمة المستخدمين والمصادقة**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-user-service` |
| **Port** | `127.0.0.1:3025:3025` (localhost only) |
| **Network** | `sahool-network` |

**Description**: Authentication and user management. Access via Kong API Gateway only.

**الوصف**: المصادقة وإدارة المستخدمين. الوصول عبر بوابة Kong API فقط.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `notification-service` (healthy)

**Health Check Endpoint**: `GET /api/v1/health`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

## Python Services

## خدمات Python

### 1. WebSocket Gateway

**بوابة WebSocket**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-ws-gateway` |
| **Port** | `8081:8081` |
| **Network** | `sahool-network` |

**Description**: Real-time WebSocket gateway for live updates.

**الوصف**: بوابة WebSocket للتحديثات في الوقت الفعلي.

**Dependencies**: `nats` (healthy), `redis` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 2. Billing Core

**خدمة الفوترة الأساسية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-billing-core` |
| **Port** | `8089:8089` |
| **Network** | `sahool-network` |

**Description**: Billing and invoicing with Stripe and Tharwatt integration.

**الوصف**: الفوترة والفواتير مع تكامل Stripe و Tharwatt.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 3. Vegetation Analysis Service

**خدمة تحليل الغطاء النباتي الموحدة**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-vegetation-analysis-service` |
| **Port** | `8090:8090` |
| **Network** | `sahool-network` |

**Description**: Unified satellite and vegetation analysis. Consolidates: satellite-service, ndvi-processor, ndvi-engine, lai-estimation.

**الوصف**: تحليل موحد للأقمار الصناعية والغطاء النباتي. يجمع: satellite-service، ndvi-processor، ndvi-engine، lai-estimation.

**Satellite Providers**:
- Sentinel Hub
- NASA Earthdata
- Planet

**Dependencies**: `postgres` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 768M | 256M |

---

### 4. Indicators Service

**خدمة المؤشرات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-indicators-service` |
| **Port** | `8091:8091` |
| **Network** | `sahool-network` |

**Description**: Field indicators computation and aggregation.

**الوصف**: حساب وتجميع مؤشرات الحقل.

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 5. Weather Service

**خدمة الطقس الموحدة**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-weather-service` |
| **Port** | `8092:8092` |
| **Network** | `sahool-network` |

**Description**: Unified weather operations. Consolidates: weather-core, weather-advanced.

**الوصف**: عمليات الطقس الموحدة. يجمع: weather-core، weather-advanced.

**Weather Providers**:
- OpenWeatherMap
- WeatherAPI

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 6. Advisory Service

**خدمة الاستشارات الموحدة**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-advisory-service` |
| **Port** | `8093:8093` |
| **Network** | `sahool-network` |

**Description**: Unified agricultural advisory. Consolidates: agro-advisor, fertilizer-advisor.

**الوصف**: الاستشارات الزراعية الموحدة. يجمع: agro-advisor، fertilizer-advisor.

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 7. Irrigation Smart

**الري الذكي**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-irrigation-smart` |
| **Port** | `8094:8094` |
| **Network** | `sahool-network` |

**Description**: Smart irrigation management and scheduling.

**الوصف**: إدارة وجدولة الري الذكي.

**Dependencies**: `postgres` (healthy), `nats` (healthy), `iot-gateway` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 8. Crop Intelligence Service

**خدمة ذكاء المحاصيل الموحدة**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-crop-intelligence-service` |
| **Port** | `8095:8095` |
| **Network** | `sahool-network` |

**Description**: Unified crop analysis and AI. Consolidates: crop-health, crop-health-ai, crop-growth-model.

**الوصف**: تحليل المحاصيل الموحد والذكاء الاصطناعي. يجمع: crop-health، crop-health-ai، crop-growth-model.

**Volumes**:
```yaml
- ./models:/app/models:ro
```

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.5 |
| Memory | 1G | 512M |

---

### 9. Yield Prediction Service (Python)

**خدمة التنبؤ بالإنتاجية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-yield-prediction-service` |
| **Port** | `8098:8098` |
| **Network** | `sahool-network` |

**Description**: Unified yield analysis. Consolidates: yield-engine, yield-prediction.

**الوصف**: تحليل الإنتاجية الموحد. يجمع: yield-engine، yield-prediction.

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /api/v1/yield/health`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.25 |
| Memory | 512M | 128M |

---

### 10. Virtual Sensors

**المستشعرات الافتراضية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-virtual-sensors` |
| **Port** | `8119:8119` |
| **Network** | `sahool-network` |

**Description**: Virtual sensor computation from remote sensing data.

**الوصف**: حساب المستشعرات الافتراضية من بيانات الاستشعار عن بُعد.

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 11. Field Chat

**محادثة الحقل**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-field-chat` |
| **Port** | `8099:8099` |
| **Network** | `sahool-network` |

**Description**: Field-level chat and communication.

**الوصف**: المحادثة والتواصل على مستوى الحقل.

**Dependencies**: `postgres` (healthy), `nats` (healthy), `redis` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 12. Equipment Service

**خدمة المعدات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-equipment-service` |
| **Port** | `8101:8101` |
| **Network** | `sahool-network` |

**Description**: Equipment tracking and maintenance management.

**الوصف**: تتبع المعدات وإدارة الصيانة.

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 13. Task Service

**خدمة المهام**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-task-service` |
| **Port** | `8103:8103` |
| **Network** | `sahool-network` |

**Description**: Task management and scheduling for farm operations.

**الوصف**: إدارة المهام وجدولة عمليات المزرعة.

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 14. Provider Config

**تكوين مزودي الخدمات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-provider-config` |
| **Port** | `8104:8104` |
| **Network** | `sahool-network` |

**Description**: External service provider configuration management.

**الوصف**: إدارة تكوين مزودي الخدمات الخارجيين.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.1 |
| Memory | 512M | 128M |

---

### 15. IoT Gateway

**بوابة IoT**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-iot-gateway` |
| **Port** | `8106:8106` |
| **Network** | `sahool-network` |

**Description**: IoT protocol gateway with MQTT bridge.

**الوصف**: بوابة بروتوكول IoT مع جسر MQTT.

**Dependencies**: `postgres` (healthy), `nats` (healthy), `mqtt` (healthy)

**Health Check Endpoint**: `GET /health`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 512M | 128M |

---

### 16. Notification Service

**خدمة الإشعارات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-notification-service` |
| **Port** | `8110:8110` |
| **Network** | `sahool-network` |

**Description**: Push notifications via Email (SMTP) and Firebase Cloud Messaging.

**الوصف**: إشعارات الدفع عبر البريد الإلكتروني (SMTP) و Firebase Cloud Messaging.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 17. Astronomical Calendar

**التقويم الفلكي**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-astronomical-calendar` |
| **Port** | `8111:8111` |
| **Network** | `sahool-network` |

**Description**: Islamic calendar, prayer times, and astronomical calculations.

**الوصف**: التقويم الإسلامي ومواقيت الصلاة والحسابات الفلكية.

**Dependencies**: `weather-service` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.25 | 0.1 |
| Memory | 256M | 64M |

---

### 18. AI Advisor

**المستشار الذكي**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-ai-advisor` |
| **Port** | `8112:8112` |
| **Network** | `sahool-network` |

**Description**: Multi-provider LLM advisory (Anthropic Claude, OpenAI GPT-4, Google Gemini) with RAG.

**الوصف**: استشارات نماذج لغوية متعددة المزودين (Anthropic Claude، OpenAI GPT-4، Google Gemini) مع RAG.

**LLM Providers**:
- Anthropic (Claude 3.5 Sonnet)
- OpenAI (GPT-4o)
- Google (Gemini 1.5 Pro)

**Dependencies**: `qdrant` (healthy), `nats` (healthy), `crop-intelligence-service` (healthy), `weather-service` (healthy), `advisory-service` (healthy), `vegetation-analysis-service` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 2 | 0.5 |
| Memory | 2G | 512M |

---

### 19. Alert Service

**خدمة التنبيهات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-alert-service` |
| **Port** | `8113:8113` |
| **Network** | `sahool-network` |

**Description**: Alert management and escalation.

**الوصف**: إدارة التنبيهات والتصعيد.

**Dependencies**: `pgbouncer` (healthy), `nats` (healthy), `notification-service` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 20. Field Service (Deprecated)

**خدمة الحقول**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-field-service` |
| **Port** | `8115:8115` |
| **Network** | `sahool-network` |
| **Status** | DEPRECATED - Use field-management-service (Port 3000) |

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 21. Inventory Service

**خدمة المخزون**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-inventory-service` |
| **Port** | `8116:8116` |
| **Network** | `sahool-network` |

**Description**: Inventory management for farm supplies and products.

**الوصف**: إدارة مخزون اللوازم والمنتجات الزراعية.

**Dependencies**: `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 22. NDVI Processor

**معالج NDVI**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-ndvi-processor` |
| **Port** | `8118:8118` |
| **Network** | `sahool-network` |
| **Status** | DEPRECATED - Migrating to vegetation-analysis-service |

**Description**: NDVI processing from satellite imagery.

**الوصف**: معالجة NDVI من صور الأقمار الصناعية.

**Dependencies**: `postgres` (healthy), `nats` (healthy), `vegetation-analysis-service` (healthy)

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 1 | 0.5 |
| Memory | 768M | 256M |

---

### 23. Field Intelligence

**خدمة ذكاء الحقل**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-field-intelligence` |
| **Port** | `8120:8120` |
| **Network** | `sahool-network` |

**Description**: Field analytics and intelligence aggregation.

**الوصف**: تحليلات الحقل وتجميع الذكاء.

**Dependencies**: `task-service` (healthy), `astronomical-calendar` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 512M | 128M |

---

### 24. Skills Service

**خدمة المهارات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-skills-service` |
| **Port** | `8121:8121` |
| **Network** | `sahool-network` |

**Description**: AI model skill compression and memory management.

**الوصف**: ضغط نماذج الذكاء الاصطناعي وإدارة الذاكرة.

**Dependencies**: `redis` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 25. Agro Rules Worker

**عامل القواعد الزراعية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-agro-rules` |
| **Network** | `sahool-network` |

**Description**: NATS event-driven worker for agronomic rules processing.

**الوصف**: عامل مدفوع بأحداث NATS لمعالجة القواعد الزراعية.

**Dependencies**: `nats` (healthy), `field-management-service` (started)

**Health Check**:
```yaml
test: ["CMD", "pgrep", "-f", "python.*worker"]
```

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 26. MCP Server

**خادم بروتوكول سياق النموذج**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-mcp-server` |
| **Port** | `8200:8200` |
| **Network** | `sahool-network` |

**Description**: Model Context Protocol integration for AI assistants (Claude, ChatGPT).

**الوصف**: تكامل بروتوكول سياق النموذج لمساعدي الذكاء الاصطناعي (Claude، ChatGPT).

**Dependencies**: `kong` (healthy), `postgres` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /health`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 512M | 256M |

---

### 27. AI Agents Service

**خدمة الوكلاء الذكية**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-ai-agents-service` |
| **Port** | `8130:8130` |
| **Network** | `sahool-network` |

**Description**: Autonomous AI agents for agricultural intelligence.

**الوصف**: وكلاء ذكاء اصطناعي مستقلون للذكاء الزراعي.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 512M | 256M |

---

### 28. CRM Service

**خدمة إدارة علاقات المزارعين**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-crm-service` |
| **Port** | `8131:8131` |
| **Network** | `sahool-network` |

**Description**: Customer Relationship Management for farmers.

**الوصف**: إدارة علاقات العملاء للمزارعين.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 29. Low-Code Engine

**محرك التطوير منخفض الكود**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-lowcode-engine` |
| **Port** | `8132:8132` |
| **Network** | `sahool-network` |

**Description**: Low-code application development platform.

**الوصف**: منصة تطوير التطبيقات منخفضة الكود.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

### 30. WeChat Service

**خدمة ويتشات**

| Property | Value |
|----------|-------|
| **Container Name** | `sahool-wechat-service` |
| **Port** | `8133:8133` |
| **Network** | `sahool-network` |

**Description**: WeChat integration for farmer communication and engagement.

**الوصف**: تكامل ويتشات للتواصل والتفاعل مع المزارعين.

**Dependencies**: `pgbouncer` (healthy), `redis` (healthy), `nats` (healthy)

**Health Check Endpoint**: `GET /healthz`

**Resource Limits**:
| Resource | Limit | Reservation |
|----------|-------|-------------|
| CPU | 0.5 | 0.25 |
| Memory | 384M | 128M |

---

## Deprecated Services

## الخدمات المهملة

The following services are deprecated and will be removed in future versions. Use the `deprecated` or `legacy` profile to run them.

الخدمات التالية مهملة وسيتم إزالتها في الإصدارات المستقبلية. استخدم ملف تعريف `deprecated` أو `legacy` لتشغيلها.

| Service | Port | Replacement | Sunset Date |
|---------|------|-------------|-------------|
| `field-ops` | 8080 | `field-management-service:3000` | Legacy |
| `agro-advisor` | 8105 | `advisory-service:8093` | v17.0.0 |
| `ndvi-engine` | 8107 | `vegetation-analysis-service:8090` | 2026-06-01 |
| `weather-core` | 8108 | `weather-service:8092` | v17.0.0 |
| `crop-health` | 8100 | `crop-intelligence-service:8095` | 2026-06-01 |
| `yield-prediction` (Node.js) | 3021 | `yield-prediction-service:8098` | TBD |
| `lai-estimation` | 3022 | `vegetation-analysis-service:8090` | TBD |
| `crop-growth-model` | 3023 | `crop-intelligence-service:8095` | TBD |
| `community-chat` | 8097 | `chat-service:8114` | TBD |

### Running Deprecated Services

```bash
# Run with deprecated profile
docker compose --profile deprecated up -d

# Run with legacy profile
docker compose --profile legacy up -d
```

---

## Network Configuration

## تكوين الشبكة

### Network Definition

```yaml
networks:
  sahool-network:
    driver: bridge
    name: sahool-network
```

All services are connected to the `sahool-network` bridge network, enabling:
- Service discovery by container name
- Internal DNS resolution
- Network isolation from host

جميع الخدمات متصلة بشبكة الجسر `sahool-network`، مما يتيح:
- اكتشاف الخدمات بواسطة اسم الحاوية
- حل DNS الداخلي
- عزل الشبكة عن المضيف

### Port Binding Security

Most infrastructure services bind to `127.0.0.1` (localhost only) for security:

| Service | Binding | Reason |
|---------|---------|--------|
| PostgreSQL | `127.0.0.1:5432` | Direct DB access restricted |
| PgBouncer | `127.0.0.1:6432` | Connection pooler restricted |
| Redis | `127.0.0.1:6379` | Cache access restricted |
| NATS | `127.0.0.1:4222` | Message queue restricted |
| Kong Admin | `127.0.0.1:8001` | Admin API restricted |
| User Service | `127.0.0.1:3025` | Auth via Kong only |

**Public Services** (accessible from external network):
- Kong Proxy: `8000:8000`

---

## Volume Configuration

## تكوين وحدات التخزين

### Named Volumes

| Volume Name | Container | Mount Point | Purpose |
|-------------|-----------|-------------|---------|
| `sahool-postgres-data` | postgres | `/var/lib/postgresql/data` | PostgreSQL data |
| `sahool-nats-data` | nats | `/data` | NATS JetStream data |
| `sahool-redis-data` | redis | `/data` | Redis persistence |
| `sahool-qdrant-data` | qdrant | `/qdrant/storage` | Vector database |
| `sahool-mqtt-data` | mqtt | `/mosquitto/data` | MQTT persistence |
| `sahool-mqtt-logs` | mqtt | `/mosquitto/log` | MQTT logs |
| `sahool-mqtt-passwd` | mqtt | `/mosquitto/config` | MQTT credentials |
| `sahool-ollama-data` | ollama | `/root/.ollama` | LLM models |
| `sahool-code-review-logs` | code-review | `/app/logs` | Code review logs |
| `sahool-etcd-data` | etcd | `/etcd` | Etcd metadata |
| `sahool-minio-data` | minio | `/minio_data` | Object storage |
| `sahool-milvus-data` | milvus | `/var/lib/milvus` | Milvus data |
| `sahool-pgbouncer-userlist` | pgbouncer | User list | PgBouncer users |
| `kong_logs` | kong | `/var/log/kong` | Kong access logs |

### Bind Mounts (Configuration)

| Source | Target | Service | Mode |
|--------|--------|---------|------|
| `./infrastructure/core/postgres/init` | `/docker-entrypoint-initdb.d` | postgres | ro |
| `./infrastructure/gateway/kong/kong.yml` | `/kong/declarative/kong.yml` | kong | ro |
| `./config/certs` | Various | Multiple | ro |
| `./models` | `/app/models` | crop-intelligence | ro |

---

## Service Dependencies

## تبعيات الخدمات

### Dependency Graph (Simplified)

```
                    ┌─────────────┐
                    │  PostgreSQL │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  PgBouncer  │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
    │  Redis  │      │   NATS    │     │   Kong    │
    └────┬────┘      └─────┬─────┘     └─────┬─────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
         │ Node.js │  │ Python  │  │   IoT   │
         │Services │  │Services │  │Services │
         └─────────┘  └─────────┘  └─────────┘
```

### Critical Dependencies

| Service | Required Dependencies |
|---------|----------------------|
| All Application Services | `postgres` OR `pgbouncer` |
| All Event-Driven Services | `nats` |
| Caching Services | `redis` |
| AI Services | `qdrant` (vector DB) |
| IoT Services | `mqtt`, `nats` |
| User Service | `notification-service` |

---

## Resource Limits Summary

## ملخص حدود الموارد

### High Resource Services

| Service | CPU Limit | Memory Limit | Purpose |
|---------|-----------|--------------|---------|
| PostgreSQL | 2 | 2G | Primary database |
| Milvus | 2 | 4G | Vector database |
| Ollama | 4 | 8G | LLM inference |
| AI Advisor | 2 | 2G | LLM orchestration |
| Kong | 2 | 1G | API Gateway |

### Standard Services

| Service Type | CPU Limit | Memory Limit |
|--------------|-----------|--------------|
| Most Python Services | 0.5 | 384M |
| Most Node.js Services | 1 | 512M |
| Utility Services | 0.25 | 256M |

### Total Resource Requirements (Estimated)

| Metric | Minimum | Recommended |
|--------|---------|-------------|
| CPU Cores | 16 | 32+ |
| Memory | 32GB | 64GB+ |
| Storage | 100GB | 500GB+ |

---

## Profiles

## ملفات التعريف

Docker Compose profiles allow selective service startup:

| Profile | Description | Command |
|---------|-------------|---------|
| (default) | Core services | `docker compose up -d` |
| `gpu` | GPU-enabled services (Ollama) | `docker compose --profile gpu up -d` |
| `deprecated` | Deprecated services | `docker compose --profile deprecated up -d` |
| `legacy` | Legacy compatibility | `docker compose --profile legacy up -d` |
| `demo` | Demo data service | `docker compose --profile demo up -d` |

### Profile Combinations

```bash
# Full stack with GPU support
docker compose --profile gpu up -d

# Include deprecated services for migration testing
docker compose --profile deprecated up -d

# Demo environment with sample data
docker compose --profile demo up -d

# Everything
docker compose --profile gpu --profile demo up -d
```

---

## Quick Reference

## مرجع سريع

### Common Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f [service-name]

# Check service status
docker compose ps

# Stop all services
docker compose down

# Restart specific service
docker compose restart [service-name]

# Scale a service
docker compose up -d --scale [service-name]=3

# Execute command in container
docker compose exec [service-name] /bin/sh

# View resource usage
docker stats
```

### Health Check URLs

| Service | Health Endpoint |
|---------|-----------------|
| Python Services | `GET /healthz` |
| Node.js Services | `GET /healthz` or `GET /api/v1/health` |
| Kong | `GET /status` (via admin API) |
| NATS | `GET :8222/healthz` |
| Redis | `redis-cli ping` |
| PostgreSQL | `pg_isready` |

---

_Last Updated: January 2026_
_Version: 16.0.0_
