# مخطط معمارية Kong و API Gateway
# Kong & API Gateway Architecture Diagram

**منصة سهول | SAHOOL Platform v16.0.0**

---

## 🏗️ نظرة عامة على البنية | Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         SAHOOL Platform Architecture                         │
│                      منصة سهول - البنية المعمارية                           │
└──────────────────────────────────────────────────────────────────────────────┘

                                  ┌─────────────┐
                                  │   Clients   │
                                  │  العملاء    │
                                  │             │
                                  │ Web │Mobile │
                                  └──────┬──────┘
                                         │
                                         ▼
        ┌────────────────────────────────────────────────────────────┐
        │                     Kong API Gateway                        │
        │                   بوابة API - Kong                         │
        │                                                             │
        │  Port: 8000 (HTTP) | 8443 (HTTPS - Production)            │
        │  Admin: 8001 (localhost only)                              │
        │                                                             │
        │  ┌──────────────────────────────────────────────────────┐  │
        │  │  Global Plugins (الإضافات العامة)                   │  │
        │  │  ├─ CORS (origins: * for dev)                        │  │
        │  │  ├─ Prometheus (metrics)                             │  │
        │  │  ├─ Correlation ID (distributed tracing)             │  │
        │  │  └─ Request Size Limiting (10 MB global)             │  │
        │  └──────────────────────────────────────────────────────┘  │
        │                                                             │
        │  ┌──────────────────────────────────────────────────────┐  │
        │  │  JWT Authentication (مصادقة JWT)                    │  │
        │  │  ├─ Starter (100/min, 5K/hour)                       │  │
        │  │  ├─ Professional (1K/min, 50K/hour)                  │  │
        │  │  ├─ Enterprise (10K/min, 500K/hour)                  │  │
        │  │  ├─ Research (1K/min, 50K/hour)                      │  │
        │  │  └─ Admin (10K/min, unlimited/hour)                  │  │
        │  └──────────────────────────────────────────────────────┘  │
        └────────────────────────┬───────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
        ┌───────────────┐ ┌─────────────┐ ┌──────────────┐
        │Infrastructure │ │  Backend    │ │  AI Agents   │
        │    Services   │ │  Services   │ │   وكلاء AI   │
        │ خدمات البنية  │ │الخدمات الخلفية│ └──────────────┘
        └───────────────┘ └─────────────┘
```

---

## 🏢 Infrastructure Layer (طبقة البنية التحتية)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Infrastructure Services (14)                     │
│                      خدمات البنية التحتية (14)                     │
└─────────────────────────────────────────────────────────────────────┘

Database Layer (طبقة قواعد البيانات)
├─ PostgreSQL:5432          ✅ PostGIS 16-3.4
│   └─ PgBouncer:6432       ✅ Connection Pooling (250 max)
│
Caching Layer (طبقة التخزين المؤقت)
├─ Redis:6379               ✅ Redis 7.4-alpine
│
Message Queue (طابور الرسائل)
├─ NATS:4222                ✅ NATS 2.10.24 + JetStream
│   └─ Exporter:7777        ✅ Prometheus metrics
│
Secrets Management (إدارة الأسرار)
├─ Vault:8200               ✅ HashiCorp Vault 1.17
│
Object Storage (التخزين الكائني)
├─ MinIO:9000               ✅ S3-compatible storage
│
Vector Databases (قواعد بيانات المتجهات)
├─ Qdrant:6333              ✅ Vector search v1.7.4
├─ Milvus:19530             ✅ Vector database v2.5.27
│
Coordination (التنسيق)
├─ etcd:2379                ✅ etcd v3.5.5
│
IoT Messaging (رسائل إنترنت الأشياء)
├─ MQTT:1883                ✅ Eclipse Mosquitto 2
│
ML Platform (منصة التعلم الآلي)
├─ MLflow:5000              ⚠️  pip install errors
│
Local LLM (نماذج اللغة المحلية)
└─ Ollama:11434             🎮 Requires GPU
```

---

## 🤖 AI Agents Layer (طبقة وكلاء الذكاء الاصطناعي)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI Agents Services (6)                        │
│                      خدمات وكلاء الذكاء الاصطناعي (6)               │
└─────────────────────────────────────────────────────────────────────┘

Agent Registry & Core (سجل الوكلاء والنواة)
┌──────────────────────────────────────────────────────────────┐
│  agent-registry:8160          ✅ Central agent registry      │
│    Kong: /api/v1/agents                                      │
│    ├─ Agent registration & discovery                         │
│    ├─ Capability management                                  │
│    ├─ Skills tracking                                        │
│    └─ A2A protocol compliance                                │
│                                                               │
│  ai-agents-core:8161          ✅ Agent orchestration         │
│    Kong: /api/v1/ai-agents                                   │
│    ├─ Multi-agent coordination                               │
│    ├─ Task distribution                                      │
│    ├─ Context sharing                                        │
│    └─ Depends on: agent-registry:8160                        │
└──────────────────────────────────────────────────────────────┘

Code Intelligence (ذكاء الكود)
┌──────────────────────────────────────────────────────────────┐
│  code-fix-agent:8162          ✅ Automated code fixing       │
│    Kong: /api/v1/code-fix                                    │
│    ├─ Multi-tool analysis (Ruff, ESLint, Mypy, Bandit)      │
│    ├─ Auto-fix strategies (MINIMAL, SAFE, COMPREHENSIVE)    │
│    ├─ Audit trail integration                                │
│    ├─ Security vulnerability detection                       │
│    └─ Depends on: agent-registry:8160                        │
│                                                               │
│  code-review-agent           ⚠️  Under development           │
│    Kong: /api/v1/code-review (defined but not implemented)   │
└──────────────────────────────────────────────────────────────┘

Copilot & LLM (المساعد الذكي ونماذج اللغة)
┌──────────────────────────────────────────────────────────────┐
│  copilot-api:8163            ✅ Agricultural AI copilot      │
│    Kong: /api/v1/copilot                                     │
│    ├─ Natural language queries                               │
│    ├─ Context-aware recommendations                          │
│    ├─ Bilingual support (AR/EN)                              │
│    ├─ Depends on: agent-registry:8160                        │
│    └─ Depends on: llm-orchestrator:8164                      │
│                                                               │
│  llm-orchestrator:8164       ✅ Multi-provider LLM           │
│    Kong: /api/v1/llm                                         │
│    ├─ Anthropic (Claude)                                     │
│    ├─ OpenAI (GPT)                                           │
│    ├─ Ollama (Local) - can be connected                      │
│    ├─ Request routing                                        │
│    ├─ Response caching                                       │
│    └─ Cost tracking                                          │
└──────────────────────────────────────────────────────────────┘

Additional AI Services (خدمات ذكاء إضافية)
┌──────────────────────────────────────────────────────────────┐
│  ai-agents-service:8130      ✅ Additional AI services       │
│    Kong: /api/v1/ai-agents-service                           │
│    └─ Depends on: agent-registry:8160                        │
│                                                               │
│  mcp-server:8201            ⚠️  Defined in Kong, needs impl  │
│    Kong: /api/v1/mcp                                         │
│    Config: mcp.json                                          │
│    ├─ Tools: weather, field_health, irrigation               │
│    ├─ Transport: STDIO & HTTP                                │
│    └─ Status: Config exists, needs docker-compose entry      │
└──────────────────────────────────────────────────────────────┘
```

---

## 🌐 Backend Services Layer (طبقة الخدمات الخلفية)

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Node.js Services (12)                          │
│                        خدمات Node.js (12)                           │
└─────────────────────────────────────────────────────────────────────┘

Core Services (الخدمات الأساسية)
├─ field-management:3000    ✅ Unified field operations
├─ user-service:3025        ✅ Authentication & users
├─ marketplace:3010         ✅ Agricultural marketplace
├─ research-core:3015       ✅ Research trials
├─ disaster-assessment:3020 ⚠️  Prisma errors
├─ chat-service:8114        ✅ Community chat
├─ iot-service:8117         ✅ IoT device management
└─ ground-vision:8182       🎮 GPU required

┌─────────────────────────────────────────────────────────────────────┐
│                       Python Services (48)                           │
│                        خدمات Python (48)                            │
└─────────────────────────────────────────────────────────────────────┘

Intelligence Services (خدمات الذكاء)
├─ vegetation-analysis:8090  ✅ Satellite imagery & NDVI
├─ indicators-service:8091   ✅ Field indicators
├─ weather-service:8092      ✅ Weather data & forecasts
├─ advisory-service:8093     ✅ Agricultural advisory
├─ irrigation-smart:8094     ✅ Smart irrigation
├─ crop-intelligence:8095    ✅ Crop health AI
├─ field-intelligence:8120   ✅ Field analytics
├─ pest-detection:8125       ✅ Pest detection AI
├─ soil-analysis:8124        ✅ Soil analysis
├─ yield-prediction:8152     ✅ Yield forecasting
└─ skills-service:8121       ✅ Farmer skills assessment

Vision & Terrain (الرؤية والتضاريس)
├─ yolo26-vision:8150        🎮 YOLOv26m object detection
├─ terrain-core:8185         ✅ DEM processing
├─ hydrology:8165            ✅ Hydrology analysis
├─ leveling-optimizer:8170   ✅ Field leveling
└─ edge-orchestrator:8180    ✅ Edge device management (Jetson Orin)

Integration Services (خدمات التكامل)
├─ ws-gateway:8081           ✅ WebSocket gateway
├─ iot-gateway:8106          ✅ IoT protocol gateway
├─ virtual-sensors:8119      ✅ Virtual sensor computation
├─ drone-service:8126        ✅ Drone integration
└─ wechat-service:8133       ✅ WeChat integration

Business Services (الخدمات التجارية)
├─ billing-core:8089         ✅ Billing & invoicing
├─ task-service:8103         ✅ Task management
├─ equipment-service:8101    ⚠️  Migration error
├─ notification-service:8110 ✅ Push notifications
├─ alert-service:8113        ✅ Alert management
├─ inventory-service:8116    ✅ Inventory tracking
├─ crm-service:8131          ✅ Customer relationship
├─ cooperative-service:8127  ✅ Cooperative management
└─ lowcode-engine:8132       ✅ Low-code platform

Compliance & Traceability (الامتثال والتتبع)
├─ globalgap-compliance:8120 ✅ GlobalGAP compliance
├─ audit-service:8122        ✅ Audit logging
└─ traceability-service:8123 ✅ Product traceability

Specialized Services (خدمات متخصصة)
├─ astronomical-calendar:8111 ✅ Islamic calendar
├─ field-chat:8099           ⚠️  DB schema error
└─ provider-config:8104      ✅ Provider configuration
```

---

## 🔄 Data Flow (تدفق البيانات)

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Request Flow                                 │
│                         تدفق الطلبات                                 │
└──────────────────────────────────────────────────────────────────────┘

1. Client Request (طلب العميل)
   │
   ├─ Web App → Kong:8000
   ├─ Mobile App → Kong:8000
   └─ Admin Dashboard → Kong:8000
                │
                ▼
2. Kong API Gateway Processing (معالجة Kong)
   │
   ├─ CORS Check (فحص CORS)
   ├─ JWT Validation (التحقق من JWT)
   ├─ Rate Limiting (تحديد المعدل)
   ├─ Request Size Check (فحص حجم الطلب)
   └─ Correlation ID Injection (إضافة معرف الارتباط)
                │
                ▼
3. Route Matching (مطابقة المسار)
   │
   ├─ /api/v1/agents → agent-registry:8160
   ├─ /api/v1/ai-agents → ai-agents-core:8161
   ├─ /api/v1/code-fix → code-fix-agent:8162
   ├─ /api/v1/copilot → copilot-api:8163
   ├─ /api/v1/llm → llm-orchestrator:8164
   ├─ /api/v1/fields → field-management:3000
   ├─ /auth/* → user-service:3025
   └─ ... (77 routes total)
                │
                ▼
4. Upstream Service (الخدمة النهائية)
   │
   ├─ Database Access → PgBouncer:6432 → PostgreSQL:5432
   ├─ Cache Access → Redis:6379
   ├─ Event Publishing → NATS:4222
   └─ Secret Retrieval → Vault:8200
                │
                ▼
5. Response (الاستجابة)
   │
   ├─ Add Headers (Correlation ID, Rate Limit)
   ├─ Prometheus Metrics
   └─ Return to Client
```

---

## 🛡️ Security Layers (طبقات الأمان)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Security Architecture                          │
│                        البنية الأمنية                                │
└──────────────────────────────────────────────────────────────────────┘

Layer 1: Network Security (أمان الشبكة)
┌────────────────────────────────────────────────────┐
│  ✅ Docker Network Isolation                       │
│  ✅ Localhost-only ports (admin APIs)              │
│  ⚠️  TLS/SSL (disabled for dev, required for prod) │
└────────────────────────────────────────────────────┘

Layer 2: API Gateway Security (أمان بوابة API)
┌────────────────────────────────────────────────────┐
│  ✅ JWT Authentication (5 tiers)                   │
│  ✅ Rate Limiting (Redis-based)                    │
│  ✅ Request Size Limiting (10 MB global)           │
│  ⚠️  CORS (wildcard for dev, restrict for prod)    │
│  ⚠️  Security Headers (not configured)             │
└────────────────────────────────────────────────────┘

Layer 3: Service Security (أمان الخدمات)
┌────────────────────────────────────────────────────┐
│  ✅ Container Isolation (no-new-privileges)        │
│  ✅ Resource Limits (CPU, Memory)                  │
│  ✅ Health Checks                                  │
│  ✅ Secret Management (Vault)                      │
│  ✅ Database SSL (disabled for dev via PgBouncer)  │
└────────────────────────────────────────────────────┘

Layer 4: Data Security (أمان البيانات)
┌────────────────────────────────────────────────────┐
│  ✅ PostgreSQL Authentication                      │
│  ✅ Redis Authentication                           │
│  ✅ NATS Authentication                            │
│  ✅ Environment Variable Protection                │
│  ✅ PgBouncer userlist.txt dynamic generation      │
└────────────────────────────────────────────────────┘
```

---

## 📊 Performance Optimization (تحسين الأداء)

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Performance Architecture                           │
│                    معمارية الأداء                                    │
└──────────────────────────────────────────────────────────────────────┘

Kong Gateway Optimization
┌────────────────────────────────────────────────────┐
│  Worker Processes:      auto (all CPU cores)       │
│  Worker Connections:    4096                       │
│  Upstream Keepalive:    60 connections             │
│  Keepalive Timeout:     60s                        │
│  Keepalive Requests:    100                        │
│  Memory Cache:          128m                       │
└────────────────────────────────────────────────────┘

PgBouncer Connection Pooling
┌────────────────────────────────────────────────────┐
│  Pool Mode:             transaction                │
│  Max DB Connections:    250                        │
│  Default Pool Size:     30                         │
│  Min Pool Size:         10                         │
│  Reserve Pool:          10                         │
│  Max Client Conn:       800                        │
│  Client Idle Timeout:   900s (15 min)              │
│  Server Idle Timeout:   600s (10 min)              │
└────────────────────────────────────────────────────┘

DNS Resolution
┌────────────────────────────────────────────────────┐
│  DNS Resolver:          127.0.0.11:53 (Docker)     │
│  Cache TTL:             300s (5 min)               │
│  Stale TTL:             30s                        │
│  Error TTL:             30s                        │
│  Order:                 LAST,A,CNAME               │
└────────────────────────────────────────────────────┘

Caching Strategy
┌────────────────────────────────────────────────────┐
│  Redis:                 Shared cache for all       │
│  Kong Memory Cache:     128m for routes/plugins    │
│  DNS Cache:             300s TTL                   │
│  LLM Response Cache:    Redis-based                │
└────────────────────────────────────────────────────┘
```

---

## 🔌 Service Dependencies (تبعيات الخدمات)

```
┌──────────────────────────────────────────────────────────────────────┐
│                      AI Agents Dependencies                           │
│                     تبعيات وكلاء الذكاء الاصطناعي                    │
└──────────────────────────────────────────────────────────────────────┘

agent-registry:8160
  └─ Dependencies:
      ├─ PostgreSQL (via PgBouncer)
      ├─ NATS
      └─ Redis

ai-agents-core:8161
  └─ Dependencies:
      ├─ agent-registry:8160        ⭐ Core dependency
      ├─ PostgreSQL (via PgBouncer)
      ├─ NATS
      └─ Redis

code-fix-agent:8162
  └─ Dependencies:
      ├─ agent-registry:8160        ⭐ Core dependency
      ├─ PostgreSQL (via PgBouncer)
      ├─ NATS
      └─ Redis

copilot-api:8163
  └─ Dependencies:
      ├─ agent-registry:8160        ⭐ Core dependency
      ├─ llm-orchestrator:8164      ⭐ Core dependency
      ├─ PostgreSQL (via PgBouncer)
      ├─ NATS
      └─ Redis

llm-orchestrator:8164
  └─ Dependencies:
      ├─ PostgreSQL (via PgBouncer)
      ├─ NATS
      ├─ Redis
      └─ External APIs:
          ├─ Anthropic (Claude)
          ├─ OpenAI (GPT)
          └─ Ollama (Local) - can be connected

ai-agents-service:8130
  └─ Dependencies:
      ├─ agent-registry:8160        ⭐ Core dependency
      ├─ PostgreSQL (via PgBouncer)
      ├─ NATS
      └─ Redis
```

---

## 📈 Monitoring & Observability (المراقبة والرصد)

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Monitoring Architecture                            │
│                    معمارية المراقبة                                  │
└──────────────────────────────────────────────────────────────────────┘

Metrics Collection (جمع المقاييس)
┌────────────────────────────────────────────────────┐
│  Kong:                                              │
│    ├─ Prometheus Plugin (global)                   │
│    ├─ Metrics endpoint: /metrics                   │
│    └─ Request rate, latency, status codes          │
│                                                     │
│  NATS:                                              │
│    ├─ Prometheus Exporter:7777                     │
│    └─ JetStream metrics                            │
│                                                     │
│  Services:                                          │
│    ├─ Health endpoints: /healthz                   │
│    ├─ OpenTelemetry (some services)                │
│    └─ Custom metrics                               │
└────────────────────────────────────────────────────┘

Health Checks (فحوصات الصحة)
┌────────────────────────────────────────────────────┐
│  All Services:                                      │
│    ├─ Endpoint: /healthz or /health                │
│    ├─ Interval: 30s                                │
│    ├─ Timeout: 10s                                 │
│    ├─ Retries: 3                                   │
│    └─ Start period: 15-90s (varies)                │
└────────────────────────────────────────────────────┘

Logging (التسجيل)
┌────────────────────────────────────────────────────┐
│  Kong:                                              │
│    ├─ Access logs: /dev/stdout                     │
│    ├─ Error logs: /dev/stderr                      │
│    └─ Volume: kong_logs                            │
│                                                     │
│  Services:                                          │
│    ├─ Structured JSON logs                         │
│    ├─ LOG_LEVEL: INFO (configurable)               │
│    └─ Correlation ID tracing                       │
└────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Topology (طوبولوجيا النشر)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Docker Compose Setup                           │
│                        إعداد Docker Compose                          │
└──────────────────────────────────────────────────────────────────────┘

Network: sahool-network (bridge)
┌────────────────────────────────────────────────────┐
│  All services connected to single network          │
│  DNS: Docker internal (127.0.0.11:53)              │
│  Service discovery: By service name                │
└────────────────────────────────────────────────────┘

Volumes (التخزين الدائم)
┌────────────────────────────────────────────────────┐
│  ├─ postgres_data      (Database)                  │
│  ├─ redis_data         (Cache)                     │
│  ├─ vault_data         (Secrets)                   │
│  ├─ nats_data          (JetStream)                 │
│  ├─ kong_logs          (Gateway logs)              │
│  ├─ ollama-models      (LLM models)                │
│  ├─ yolo26-models      (Vision models)             │
│  └─ minio_data         (Object storage)            │
└────────────────────────────────────────────────────┘

Resource Allocation (تخصيص الموارد)
┌────────────────────────────────────────────────────┐
│  Infrastructure Services:                          │
│    ├─ PostgreSQL: 2 CPU, 2G RAM                    │
│    ├─ PgBouncer: 1 CPU, 512M RAM                   │
│    ├─ Redis: 1 CPU, 512M RAM                       │
│    ├─ NATS: 1 CPU, 512M RAM                        │
│    └─ Kong: 2 CPU, 1G RAM                          │
│                                                     │
│  AI Services:                                       │
│    ├─ copilot-api: 1 CPU, 512M RAM                 │
│    ├─ llm-orchestrator: 2 CPU, 1G RAM              │
│    ├─ code-fix-agent: 0.5 CPU, 384M RAM            │
│    └─ yolo26-vision: GPU required                  │
│                                                     │
│  Backend Services:                                  │
│    └─ Average: 0.5 CPU, 512M RAM each              │
└────────────────────────────────────────────────────┘
```

---

## 📋 Summary (الملخص)

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Platform Statistics                               │
│                     إحصائيات المنصة                                  │
└──────────────────────────────────────────────────────────────────────┘

Total Services:             80
  ├─ Infrastructure:        14 (17.5%)
  ├─ Python Services:       48 (60.0%)
  ├─ Node.js Services:      12 (15.0%)
  └─ AI Agents:              6 (7.5%)

Kong Routes:                77
  ├─ Public routes:         ~20
  ├─ JWT-protected:         ~50
  └─ Internal only:         ~7

Port Ranges:
  ├─ 1000-2000:              2 services
  ├─ 3000-3999:             12 services
  ├─ 4000-5000:              3 services
  ├─ 6000-6999:              4 services
  ├─ 8000-8199:             51 services
  └─ 9000+:                  8 services

Dependencies:
  ✅ PostgreSQL users:      ~70 services
  ✅ Redis users:           ~60 services
  ✅ NATS users:            ~50 services
  ✅ Agent Registry users:   4 services

Health Status:
  ✅ Active & Healthy:      73 services (91%)
  ⚠️  With Warnings:         5 services (6%)
  🎮 GPU Required:           2 services (3%)

Overall Rating:             8.4/10 🟢
```

---

**© 2026 KAFAAT - SAHOOL Platform**
**Created: 2026-02-04**
