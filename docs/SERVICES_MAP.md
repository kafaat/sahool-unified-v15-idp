# SAHOOL Services Architecture Map v16.0.0

# خريطة بنية خدمات سهول

---

## نظرة عامة | Overview

**72 active services** across 4 event architecture layers, plus 4 applications and 15 archived services.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          SAHOOL Platform v16.0.0                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Mobile    │  │    Web      │  │   Admin     │  │  External   │         │
│  │  (Flutter)  │  │  Dashboard  │  │  Dashboard  │  │   APIs      │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         └────────────────┴────────────────┴────────────────┘                 │
│                                  │                                            │
│                         ┌────────▼────────┐                                  │
│                         │   Kong Gateway  │ :8000                            │
│                         │ (Auth & Rate)   │                                  │
│                         └────────┬────────┘                                  │
│    ┌─────────────────────────────┼─────────────────────────────┐             │
│    │            4-Layer Event Architecture (NATS)               │             │
│    ├───────────────────────────────────────────────────────────┤             │
│    │  Acquisition → Intelligence → Decision → Business         │             │
│    └───────────────────────────────────────────────────────────┘             │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                        Infrastructure                                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ PostGIS  │ │  Redis   │ │   NATS   │ │  Qdrant  │ │  MinIO   │   │   │
│  │  │  :5432   │ │  :6379   │ │  :4222   │ │  :6333   │ │  :9000   │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                        Observability                                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                 │   │
│  │  │Prometheus│ │ Grafana  │ │  Jaeger  │ │  OTel    │                 │   │
│  │  │  :9090   │ │  :3002   │ │  :16686  │ │ Collector│                 │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘                 │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## طبقات الخدمات | Service Layers (4-Layer Event Architecture)

### Layer 1: Acquisition (اكتساب البيانات)

Data ingestion and normalization.

| Service | Port | Type | Description |
|---------|------|------|-------------|
| iot-service | 8117 | Node.js | IoT device management |
| iot-gateway | 8106 | Python | IoT protocol gateway |
| iot-sensor-hub | 8251 | Python | IoT sensor hub |
| weather-service | 8092 | Python | Weather data; Prometheus `/metrics`, enhanced `/readyz` with DB/NATS checks, NATS event publishing |
| virtual-sensors | 8119 | Python | Virtual sensor computation; input validation (Pydantic v2), Prometheus `/metrics`, Helm chart |
| ground-vision-service | 8182 | Python | Ground-level vision analysis |
| edge-orchestrator-service | 8180 | Python | Edge device management (Jetson Orin) |

### Layer 2: Intelligence (الذكاء)

Feature extraction and AI.

| Service | Port | Type | Description |
|---------|------|------|-------------|
| vegetation-analysis-service | 8090 | Python | Satellite imagery, NDVI, VRA; Prometheus `/metrics`, NDVI anomaly NATS events, tenant isolation |
| indicators-service | 8091 | Python | Field indicators computation; Kong routes, Helm chart, DB integration (asyncpg), JWT auth |
| lai-estimation | 3022 | Node.js | Leaf Area Index estimation |
| crop-intelligence-service | 8095 | Python | Crop health AI |
| field-intelligence | 8120 | Python | Field analytics |
| skills-service | 8121 | Python | Farmer skills assessment |
| yolo26-vision-service | 8150 | Python | YOLO26 computer vision |
| terrain-core-service | 8185 | Python | DEM processing & terrain analysis |
| hydrology-service | 8165 | Python | Hydrology & drainage analysis |
| agro-rules | — | Python | Agronomic rules engine (NATS worker, no HTTP port) |
| pest-detection-service | 8125 | Python | Pest detection AI |
| soil-analysis-service | 8134 | Python | Soil analysis |
| digital-twin-engine | 8253 | Python | Digital twin simulation |

### Layer 3: Decision (القرار)

Recommendations and planning.

| Service | Port | Type | Description |
|---------|------|------|-------------|
| crop-growth-model | 3023 | Node.js | Crop growth simulation (WOFOST) |
| advisory-service | 8093 | Python | Advisory & recommendations; tenant isolation, rate limiting, NATS subscriptions |
| irrigation-smart | 8094 | Python | Smart irrigation (FAO-56); input validation (Pydantic v2), Prometheus `/metrics`, NATS events, Helm chart |
| yield-prediction | 3021 | Node.js | Yield prediction **(deprecated — use yield-prediction-service)** |
| yield-prediction-service | 8152 | Node.js | Yield prediction ML |
| leveling-optimizer-service | 8170 | Python | Field leveling optimization |
| irrigation-cycle-engine | 8250 | Python | Irrigation cycle optimization |
| fertigation-engine | 8252 | Python | Fertigation management |

### Layer 4: Business (الأعمال)

User-facing operations.

| Service | Port | Type | Description |
|---------|------|------|-------------|
| field-management-service | 3000 | Node.js | Field management (consolidated); FieldEventsService, PostGIS health check in `/readyz`, Helm chart |
| user-service | 3025 | Node.js | Authentication & user management; JWT validation hardened, bcrypt standardization, security config |
| notification-service | 8110 | Python | Push notifications; JWT auth on 7 endpoints, retry logic, Prometheus `/metrics` |
| billing-core | 8089 | Python | Billing & invoicing; input validation (Pydantic v2), Prometheus `/metrics`, NetworkPolicy |
| task-service | 8103 | Python | Task management |
| equipment-service | 8101 | Python | Equipment tracking |
| alert-service | 8113 | Python | Alert management |
| provider-config | 8104 | Python | Provider configuration |
| audit-service | 8114 | Python | Audit logging |
| marketplace-service | 3010 | Node.js | Agricultural marketplace; JwtAuthGuard on all fintech endpoints, Helm chart |
| chat-service | 8115 | Node.js | Real-time messaging |
| research-core | 3015 | Node.js | Research trials |
| disaster-assessment | 3020 | Node.js | Disaster risk assessment |
| inventory-service | 8116 | Python | Inventory management |
| cooperative-service | 8127 | Python | Cooperative management |
| crm-service | 8131 | Python | Farmer CRM |
| logistics-service | 8167 | Python | Logistics management |
| supply-chain-service | 8230 | Python | Supply chain management |
| traceability-service | 8123 | Python | Product traceability |
| globalgap-compliance | 8128 | Python | GlobalGAP compliance |
| wechat-service | 8133 | Python | WeChat integration |
| astronomical-calendar | 8111 | Python | Islamic calendar & timings |
| ws-gateway | 8081 | Python | WebSocket gateway |
| whatsapp-bot-service | 8240 | Python | WhatsApp bot |
| ussd-gateway | 8183 | Python | USSD gateway |
| drone-service | 8126 | Python | Drone integration |

### AI & Agent Services

| Service | Port | Type | Description |
|---------|------|------|-------------|
| agent-registry | 8160 | Python | Agent registry service |
| ai-advisor | 8112 | Python | AI advisory service |
| ai-agents-core | 8161 | Python | AI agents core module |
| ai-agents-service | 8130 | Python | AI agents service |
| ai-chat-assistant | 8260 | Python | AI chat assistant |
| llm-orchestrator-service | 8164 | Python | LLM orchestration |
| copilot-api | 8088 | Python | AI copilot (multi-LLM, RAG) |
| knowledge-graph | 8140 | Python | Knowledge graph service |
| code-fix-agent | 8162 | Python | Code fix AI agent |
| code-review-agent | 8145 | Node.js | Code review agent |
| code-review-service | 8102 | Python | Code review service |
| mcp-server | 8201 | Python | Model Context Protocol |
| vllm-deepseek | 8270 | Python | vLLM DeepSeek inference server (GPU-accelerated) |

### Specialized Services

| Service | Port | Type | Description |
|---------|------|------|-------------|
| lowcode-engine | 8132 | Python | Low-code workflow automation |
| demo-data | 8261 | Python | Demo data generator |
| ndvi-processor | 8118 | Python | NDVI processing (deprecating) |

---

## التبعيات | Dependencies

```
field-management-service ──► postgres (PostGIS), redis, nats (FieldEventsService)
user-service ──────────────► postgres, redis (JWT sessions, bcrypt)
billing-core ──────────────► postgres, redis, nats, prometheus
notification-service ──────► postgres, redis, nats (retry logic), prometheus
marketplace-service ───────► postgres, redis, nats (JwtAuthGuard)
vegetation-analysis-service► postgres, nats (NDVI anomaly events), sentinel-hub, prometheus
indicators-service ────────► postgres (asyncpg), nats, kong (routes), prometheus
advisory-service ──────────► postgres, nats (subscriptions), redis (rate limiting)
irrigation-smart ──────────► postgres, nats (events), prometheus
weather-service ───────────► postgres, nats (events), prometheus
virtual-sensors ───────────► postgres, nats, prometheus
yolo26-vision-service ─────► gpu (cuda), redis, nats
copilot-api ───────────────► qdrant, ollama, redis, nats
```

---

## نقاط النهاية الصحية | Health Endpoints

All services provide:

```bash
GET /healthz       # Liveness probe
GET /readyz        # Readiness probe
GET /health        # Comprehensive status (some services)
GET /metrics       # Prometheus metrics (some services)
```

---

## الأمان | Security (March 2026)

- All DELETE endpoints require JWT authentication (`get_current_user`)
- All services use unified error handling (`shared.errors_py`)
- Multi-tenant isolation via `tenant_id` scoping (enforced in advisory-service, vegetation-analysis-service)
- Kong gateway handles external auth and rate limiting (routes added for indicators-service)
- **marketplace-service**: JwtAuthGuard enforced on all fintech endpoints (payments, wallets, transactions)
- **notification-service**: JWT auth added to 7 previously unprotected endpoints, retry logic for delivery
- **user-service**: JWT validation hardened, bcrypt standardized for password hashing, security config tightened
- **billing-core**: Input validation via Pydantic v2, Kubernetes NetworkPolicy for network isolation
- **advisory-service**: Rate limiting on advisory generation, NATS subscription-based event consumption
- Prometheus `/metrics` endpoints added to: weather-service, vegetation-analysis-service, irrigation-smart, notification-service, billing-core, virtual-sensors
- Helm charts added for: field-management-service, marketplace-service, indicators-service, irrigation-smart, virtual-sensors

---

## الخدمات المؤرشفة | Archived Services (15)

See `apps/services/DEPRECATION_SUMMARY.md` for full list and migration guides.

| Deprecated | Replaced By | Sunset |
|------------|------------|--------|
| satellite-service | vegetation-analysis-service | 2025-06 |
| crop-health-ai | crop-intelligence-service | 2025-06 |
| fertilizer-advisor | advisory-service | 2025-06 |
| field-ops, field-core, field-service | field-management-service | v17.0.0 |
| ndvi-engine, ndvi-processor | vegetation-analysis-service | 2026-02 |
| community-chat, field-chat | chat-service | 2026-02 |
| yield-engine | yield-prediction-service | 2026-02 |

---

<p align="center">
  <strong>SAHOOL Platform v16.0.0</strong>
  <br>
  <sub>Architecture Map - March 2026</sub>
</p>
