# SAHOOL Platform - Network Architecture Diagram
## مخطط البنية الشبكية لمنصة صهول

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTERNET / PUBLIC                              │
│                           الإنترنت / الشبكة العامة                          │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               │ HTTPS/HTTP
                               │
                               ▼
                    ┌──────────────────────┐
                    │   REVERSE PROXY      │
                    │   (nginx/Apache)     │
                    │   SSL/TLS Termination│
                    └──────────┬───────────┘
                               │
                               │ HTTP
                               │
                               ▼
                    ┌──────────────────────┐
                    │   KONG API GATEWAY   │
                    │   Port: 8000 (PUBLIC)│◄─── ONLY PUBLIC PORT
                    │   Admin: 8001 (LOCAL)│
                    └──────────┬───────────┘
                               │
                   ┌───────────┴───────────┐
                   │  sahool-network       │
                   │  (Docker Bridge)      │
                   └───────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ INFRASTRUCTURE│    │  NODE.JS SERVICES│    │  PYTHON SERVICES │
│   SERVICES    │    │   (127.0.0.1)    │    │   (127.0.0.1)    │
│ (127.0.0.1)   │    └──────────────────┘    └──────────────────┘
└───────────────┘
```

---

## Detailed Port Mapping
## تفصيل توزيع المنافذ

### Infrastructure Layer (طبقة البنية التحتية)
```
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE SERVICES                    │
│                     الخدمات الأساسية                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PostgreSQL (PostGIS)        127.0.0.1:5432                │
│  └─ Spatial Database         └─ Field data, users, etc.    │
│                                                             │
│  Redis                       127.0.0.1:6379                │
│  └─ Cache & Sessions         └─ Fast data access           │
│                                                             │
│  NATS JetStream              127.0.0.1:4222 (client)       │
│  └─ Message Queue            127.0.0.1:8222 (monitoring)   │
│                                                             │
│  MQTT Broker                 127.0.0.1:1883 (TCP)          │
│  └─ IoT Communication        127.0.0.1:9001 (WebSocket)    │
│                                                             │
│  Qdrant Vector DB            127.0.0.1:6333 (HTTP)         │
│  └─ RAG & Semantic Search    127.0.0.1:6334 (gRPC)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### API Gateway Layer (طبقة بوابة API)
```
┌─────────────────────────────────────────────────────────────┐
│                    KONG API GATEWAY                         │
│                      بوابة Kong                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Proxy (PUBLIC)              0.0.0.0:8000 ◄─── PUBLIC      │
│  └─ Main entry point         └─ Routes to services         │
│                                                             │
│  Admin (INTERNAL)            127.0.0.1:8001 ◄─── LOCAL     │
│  └─ Configuration API        └─ Route management           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Application Services Layer (طبقة خدمات التطبيق)
```
┌─────────────────────────────────────────────────────────────┐
│              NODE.JS SERVICES (3000-3099)                   │
│                   خدمات Node.js                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Field Management            127.0.0.1:3000                │
│  └─ Core field operations    └─ TypeORM, PostGIS           │
│                                                             │
│  Marketplace                 127.0.0.1:3010                │
│  └─ E-commerce & FinTech     └─ Credit scoring, payments   │
│                                                             │
│  Research Core               127.0.0.1:3015                │
│  └─ Scientific research      └─ Experiments, trials        │
│                                                             │
│  Disaster Assessment         127.0.0.1:3020                │
│  └─ Emergency response       └─ Impact assessment          │
│                                                             │
│  Chat Service                127.0.0.1:8114                │
│  └─ Real-time messaging      └─ WebSocket chat             │
│                                                             │
│  IoT Service                 127.0.0.1:8117                │
│  └─ Device management        └─ MQTT integration           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│          PYTHON CORE SERVICES (8080-8099)                   │
│                الخدمات الأساسية بـ Python                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WebSocket Gateway           127.0.0.1:8081                │
│  └─ Real-time connections    └─ NATS to WebSocket bridge   │
│                                                             │
│  Billing Core                127.0.0.1:8089                │
│  └─ Payment processing       └─ Stripe, Tharwatt           │
│                                                             │
│  Field Chat                  127.0.0.1:8099                │
│  └─ Field-specific chat      └─ CQRS pattern               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│      PYTHON DATA & INTELLIGENCE (8090-8098, 8110-8118)      │
│              خدمات البيانات والذكاء الاصطناعي               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Vegetation Analysis         127.0.0.1:8090 ✓ CONSOLIDATED │
│  └─ Satellite imagery        └─ NDVI, LAI, indices         │
│                                                             │
│  Indicators Service          127.0.0.1:8091                │
│  └─ Agricultural metrics     └─ KPIs, analytics            │
│                                                             │
│  Weather Service             127.0.0.1:8092 ✓ CONSOLIDATED │
│  └─ Multi-provider weather   └─ Forecasts, alerts          │
│                                                             │
│  Advisory Service            127.0.0.1:8093 ✓ CONSOLIDATED │
│  └─ Agro recommendations     └─ Fertilizer, irrigation     │
│                                                             │
│  Irrigation Smart            127.0.0.1:8094                │
│  └─ Smart irrigation         └─ ET calculation, scheduling │
│                                                             │
│  Crop Intelligence           127.0.0.1:8095 ✓ CONSOLIDATED │
│  └─ Disease detection        └─ AI/ML models               │
│                                                             │
│  Virtual Sensors             127.0.0.1:8096                │
│  └─ Estimated measurements   └─ Temp, humidity, soil       │
│                                                             │
│  Yield Prediction            127.0.0.1:8098 ✓ CONSOLIDATED │
│  └─ Harvest forecasting      └─ ML-based predictions       │
│                                                             │
│  Notification Service        127.0.0.1:8110                │
│  └─ Multi-channel alerts     └─ Email, SMS, Push           │
│                                                             │
│  Astronomical Calendar       127.0.0.1:8111                │
│  └─ Islamic calendar         └─ Prayer times, seasons      │
│                                                             │
│  AI Advisor                  127.0.0.1:8112                │
│  └─ RAG-based assistant      └─ Claude, GPT, Gemini        │
│                                                             │
│  Alert Service               127.0.0.1:8113                │
│  └─ Alert management         └─ Threshold monitoring       │
│                                                             │
│  Inventory Service           127.0.0.1:8116                │
│  └─ Stock management         └─ Analytics, tracking        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         PYTHON SUPPORT SERVICES (8101-8106)                 │
│                    خدمات الدعم                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Equipment Service           127.0.0.1:8101                │
│  └─ Farm equipment           └─ Maintenance, tracking      │
│                                                             │
│  Task Service                127.0.0.1:8103                │
│  └─ Task scheduling          └─ Assignments, tracking      │
│                                                             │
│  Provider Config             127.0.0.1:8104                │
│  └─ Service configuration    └─ Multi-provider setup       │
│                                                             │
│  IoT Gateway                 127.0.0.1:8106                │
│  └─ MQTT to NATS bridge      └─ Sensor data processing     │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         INTEGRATION SERVICES (8200+)                        │
│                  خدمات التكامل                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MCP Server                  127.0.0.1:8200                │
│  └─ Model Context Protocol   └─ AI assistant integration   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Service Communication Flow
## مسار الاتصال بين الخدمات

```
External Request                   Internal Communication
  (الطلب الخارجي)                    (الاتصال الداخلي)

     Internet                            Services
        │                                    │
        │ HTTPS                              │
        ▼                                    │
   ┌─────────┐                               │
   │ Reverse │                               │
   │  Proxy  │                               │
   └────┬────┘                               │
        │ HTTP                               │
        ▼                                    │
   ┌─────────┐                               │
   │  Kong   │                               │
   │  :8000  │◄──────────────────────────────┤
   └────┬────┘                               │
        │                                    │
        │ Route to service                   │
        │ (via Docker network)               │
        │                                    │
        ├─────────────────► Field Mgmt (3000)│
        │                         │          │
        │                         ├──► PostgreSQL (5432)
        │                         │          │
        │                         ├──► Redis (6379)
        │                         │          │
        │                         └──► NATS (4222)
        │                                    │
        ├─────────────────► Weather (8092)  │
        │                         │          │
        │                         ├──► External Weather API
        │                         │          │
        │                         └──► NATS (4222)
        │                                    │
        ├─────────────────► AI Advisor (8112)│
        │                         │          │
        │                         ├──► Qdrant (6333)
        │                         │          │
        │                         ├──► Claude API
        │                         │          │
        │                         ├──► Veg Analysis (8090)
        │                         │          │
        │                         ├──► Weather (8092)
        │                         │          │
        │                         └──► NATS (4222)
        │                                    │
        └─────────────────► IoT Service (8117)
                                  │          │
                                  ├──► MQTT (1883)
                                  │          │
                                  ├──► IoT Gateway (8106)
                                  │          │
                                  └──► NATS (4222)
```

---

## Security Layers
## طبقات الأمان

```
┌───────────────────────────────────────────────────────────┐
│ Layer 1: Network Firewall                                │
│ الطبقة 1: جدار الحماية الشبكي                            │
├───────────────────────────────────────────────────────────┤
│ • Allow: Port 8000 (Kong Proxy) from Internet            │
│ • Allow: Port 443 (HTTPS) from Internet (if using nginx) │
│ • Deny: All other ports from Internet                    │
└───────────────────────────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────┐
│ Layer 2: Reverse Proxy (Optional)                        │
│ الطبقة 2: الخادم الوكيل العكسي                           │
├───────────────────────────────────────────────────────────┤
│ • SSL/TLS Termination                                     │
│ • DDoS Protection                                         │
│ • Rate Limiting                                           │
│ • Request Filtering                                       │
└───────────────────────────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────┐
│ Layer 3: API Gateway (Kong)                              │
│ الطبقة 3: بوابة API                                       │
├───────────────────────────────────────────────────────────┤
│ • Authentication (JWT)                                    │
│ • Authorization (RBAC)                                    │
│ • Rate Limiting (per user/tier)                           │
│ • Request Validation                                      │
│ • Route Management                                        │
│ • Service Discovery                                       │
└───────────────────────────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────┐
│ Layer 4: Docker Network Isolation                        │
│ الطبقة 4: عزل شبكة Docker                                │
├───────────────────────────────────────────────────────────┤
│ • Services on isolated bridge network                     │
│ • Port binding to 127.0.0.1 (localhost only)             │
│ • No direct external access                               │
│ • Internal DNS resolution                                 │
└───────────────────────────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────┐
│ Layer 5: Application Security                            │
│ الطبقة 5: أمان التطبيق                                   │
├───────────────────────────────────────────────────────────┤
│ • Input Validation                                        │
│ • SQL Injection Prevention                                │
│ • XSS Protection                                          │
│ • CSRF Protection                                         │
│ • Secure Password Hashing (Argon2)                        │
└───────────────────────────────────────────────────────────┘
```

---

## Port Accessibility Matrix
## مصفوفة إمكانية الوصول للمنافذ

| Port  | Service              | Internet | Local Host | Docker Network |
|-------|----------------------|----------|------------|----------------|
| 8000  | Kong Proxy           | ✅ Yes   | ✅ Yes     | ✅ Yes         |
| 8001  | Kong Admin           | ❌ No    | ✅ Yes     | ✅ Yes         |
| 3000  | Field Management     | ❌ No    | ✅ Yes     | ✅ Yes         |
| 3010  | Marketplace          | ❌ No    | ✅ Yes     | ✅ Yes         |
| 8090  | Vegetation Analysis  | ❌ No    | ✅ Yes     | ✅ Yes         |
| 8092  | Weather Service      | ❌ No    | ✅ Yes     | ✅ Yes         |
| 8112  | AI Advisor           | ❌ No    | ✅ Yes     | ✅ Yes         |
| 5432  | PostgreSQL           | ❌ No    | ✅ Yes     | ✅ Yes         |
| 6379  | Redis                | ❌ No    | ✅ Yes     | ✅ Yes         |
| 4222  | NATS                 | ❌ No    | ✅ Yes     | ✅ Yes         |
| 1883  | MQTT                 | ❌ No    | ✅ Yes     | ✅ Yes         |
| 6333  | Qdrant               | ❌ No    | ✅ Yes     | ✅ Yes         |
| ...   | All other services   | ❌ No    | ✅ Yes     | ✅ Yes         |

**Legend**:
- ✅ Accessible
- ❌ Not Accessible

---

**Created**: 2025-12-28  
**Version**: v16.0.0  
**See Also**: 
- `docs/PORT_MAPPING.md` - Detailed port reference
- `docs/PORT_UNIFICATION_SUMMARY.md` - Change summary
- `docker-compose.yml` - Actual configuration
