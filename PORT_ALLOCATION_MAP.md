# خريطة تخصيص المنافذ | Port Allocation Map

**التاريخ | Date**: 2026-02-04  
**المنصة | Platform**: SAHOOL v16.0.0  
**إجمالي الخدمات | Total Services**: 92

---

## 🎯 نظرة عامة | Overview

هذا المستند يوثق جميع تخصيصات المنافذ (Ports) في منصة SAHOOL لتجنب التعارضات وضمان الأمان.

This document provides a comprehensive mapping of all port allocations in the SAHOOL platform to avoid conflicts and ensure security.

---

## 🏗️ خدمات البنية التحتية | Infrastructure Services

### قاعدة البيانات | Database Services

| الخدمة | Service | المنفذ الخارجي | External Port | المنفذ الداخلي | Internal Port | النوع | Type | الأمان | Security |
|--------|---------|-----------------|---------------|-----------------|---------------|------|------|--------|----------|
| PostgreSQL (PostGIS) | postgres | 127.0.0.1:5432 | 127.0.0.1:5432 | 5432 | 5432 | TCP | TCP | ✅ localhost | ✅ localhost |
| PgBouncer (Connection Pool) | pgbouncer | 127.0.0.1:6432 | 127.0.0.1:6432 | 6432 | 6432 | TCP | TCP | ✅ localhost | ✅ localhost |

**ملاحظات | Notes**:
- PostgreSQL مع PostGIS 3.4 للبيانات الجغرافية | PostgreSQL with PostGIS 3.4 for geospatial data
- PgBouncer للتحكم في الاتصالات (transaction mode) | PgBouncer for connection pooling (transaction mode)
- الوصول محصور على localhost فقط | Access restricted to localhost only

---

### خدمات التخزين المؤقت | Caching Services

| الخدمة | Service | المنفذ الخارجي | External Port | المنفذ الداخلي | Internal Port | النوع | Type | الأمان | Security |
|--------|---------|-----------------|---------------|-----------------|---------------|------|------|--------|----------|
| Redis (Primary) | redis | 127.0.0.1:6379 | 127.0.0.1:6379 | 6379 | 6379 | TCP | TCP | ✅ localhost | ✅ localhost |
| Redis TLS | redis | 127.0.0.1:6380 | 127.0.0.1:6380 | 6380 | 6380 | TCP | TCP | ✅ localhost + TLS | ✅ localhost + TLS |

**ملاحظات | Notes**:
- Redis 7.4-alpine مع سياسة LRU | Redis 7.4-alpine with LRU policy
- MaxMemory: 2GB
- TLS اختياري للإنتاج | TLS optional for production

---

### خدمات الرسائل | Messaging Services

| الخدمة | Service | المنفذ الخارجي | External Port | المنفذ الداخلي | Internal Port | الاستخدام | Usage |
|--------|---------|-----------------|---------------|-----------------|---------------|----------|-----------|
| NATS (Client) | nats | 127.0.0.1:4222 | 127.0.0.1:4222 | 4222 | 4222 | اتصالات العملاء | Client connections |
| NATS TLS | nats | 127.0.0.1:4223 | 127.0.0.1:4223 | 4223 | 4223 | اتصالات آمنة | Secure connections |
| NATS Monitoring | nats | 127.0.0.1:8222 | 127.0.0.1:8222 | 8222 | 8222 | HTTP مراقبة | HTTP monitoring |
| NATS Cluster | nats | 127.0.0.1:6222 | 127.0.0.1:6222 | 6222 | 6222 | تجميع الخوادم | Server clustering |
| NATS Prometheus | nats-exporter | 127.0.0.1:7777 | 127.0.0.1:7777 | 7777 | 7777 | المقاييس | Metrics |
| MQTT (Broker) | mqtt | 127.0.0.1:1883 | 127.0.0.1:1883 | 1883 | 1883 | MQTT بروتوكول | MQTT protocol |
| MQTT WebSocket | mqtt | 127.0.0.1:9001 | 127.0.0.1:9001 | 9001 | 9001 | WebSocket | WebSocket |

**ملاحظات | Notes**:
- NATS 2.10.24 مع دعم Clustering | NATS 2.10.24 with Clustering support
- MQTT Eclipse Mosquitto 2 | MQTT Eclipse Mosquitto 2
- Max payload: 8MB (NATS)

---

### بوابة API | API Gateway

| الخدمة | Service | المنفذ الخارجي | External Port | المنفذ الداخلي | Internal Port | الوصول | Access |
|--------|---------|-----------------|---------------|-----------------|---------------|--------|--------|
| Kong (HTTP Proxy) | kong | 0.0.0.0:8000 | 0.0.0.0:8000 | 8000 | 8000 | 🌐 عام | 🌐 Public |
| Kong (HTTPS Proxy) | kong | 0.0.0.0:8443 | 0.0.0.0:8443 | 8443 | 8443 | 🌐 عام | 🌐 Public |
| Kong Admin API | kong | 127.0.0.1:8001 | 127.0.0.1:8001 | 8001 | 8001 | ✅ localhost | ✅ localhost |
| Kong Admin HTTPS | kong | 127.0.0.1:8444 | 127.0.0.1:8444 | 8444 | 8444 | ✅ localhost | ✅ localhost |

**ملاحظات | Notes**:
- Kong 3.4 - بوابة API الرئيسية | Kong 3.4 - Main API Gateway
- ⚠️ Admin API يجب أن يكون localhost فقط | ⚠️ Admin API should be localhost only
- توصية: استخدام TLS في الإنتاج | Recommendation: Use TLS in production

---

### خدمات التخزين | Storage Services

| الخدمة | Service | المنفذ الخارجي | External Port | المنفذ الداخلي | Internal Port | النوع | Type |
|--------|---------|-----------------|---------------|-----------------|---------------|------|------|
| MinIO (S3 API) | minio | 127.0.0.1:9000 | 127.0.0.1:9000 | 9000 | 9000 | S3-compatible |
| MinIO Console | minio | 127.0.0.1:9090 | 127.0.0.1:9090 | 9090 | 9090 | Web UI |
| Qdrant (API) | qdrant | 127.0.0.1:6333 | 127.0.0.1:6333 | 6333 | 6333 | Vector DB API |
| Qdrant (gRPC) | qdrant | 127.0.0.1:6334 | 127.0.0.1:6334 | 6334 | 6334 | gRPC |
| Milvus (Service) | milvus | 127.0.0.1:19530 | 127.0.0.1:19530 | 19530 | 19530 | Vector DB |
| Milvus (Metrics) | milvus | 127.0.0.1:9091 | 127.0.0.1:9091 | 9091 | 9091 | Health/Metrics |

**ملاحظات | Notes**:
- MinIO لتخزين الصور والنماذج | MinIO for images and model storage
- Qdrant & Milvus لقواعد البيانات المتجهة (AI) | Qdrant & Milvus for vector databases (AI)

---

### خدمات الأمان والإدارة | Security & Management Services

| الخدمة | Service | المنفذ الخارجي | External Port | المنفذ الداخلي | Internal Port | الاستخدام | Usage |
|--------|---------|-----------------|---------------|-----------------|---------------|----------|-----------|
| HashiCorp Vault | vault | 127.0.0.1:8200 | 127.0.0.1:8200 | 8200 | 8200 | إدارة الأسرار | Secrets management |
| Vault (Additional) | vault | 127.0.0.1:8201-8203 | 127.0.0.1:8201-8203 | 8201-8203 | 8201-8203 | HA Cluster | HA Cluster |
| MLflow | mlflow | 127.0.0.1:5000 | 127.0.0.1:5000 | 5000 | 5000 | سجل نماذج ML | ML Model Registry |
| Ollama (LLM) | ollama | 127.0.0.1:11434 | 127.0.0.1:11434 | 11434 | 11434 | خادم LLM محلي | Local LLM Server |

**ملاحظات | Notes**:
- Vault لتخزين الأسرار بأمان | Vault for secure secrets storage
- Ollama للنماذج اللغوية الكبيرة المحلية | Ollama for local Large Language Models
- MLflow لتتبع تجارب ML | MLflow for ML experiment tracking

---

## 🚀 خدمات التطبيقات | Application Services

### نطاق 3000-3999 (خدمات Node.js) | Range 3000-3999 (Node.js Services)

| المنفذ | Port | الخدمة | Service | النوع | Type | الحالة | Status |
|--------|------|---------|---------|------|------|--------|--------|
| 3000 | 3000 | field-management-service | Field Management | Node.js | Node.js | ✅ نشط | ✅ Active |
| 3010 | 3010 | marketplace-service | Marketplace | Node.js | Node.js | ✅ نشط | ✅ Active |
| 3015 | 3015 | research-core | Research Trials | Node.js | Node.js | ✅ نشط | ✅ Active |
| 3020 | 3020 | disaster-assessment | Disaster Risk | Node.js | Node.js | ✅ نشط | ✅ Active |
| 3021 | 3021 | yield-prediction | Yield Prediction | Node.js | Node.js | ⚠️ منتهي | ⚠️ Deprecated |
| 3022 | 3022 | lai-estimation | LAI Estimation | Node.js | Node.js | ⚠️ منتهي | ⚠️ Deprecated |
| 3023 | 3023 | crop-growth-model | Crop Growth | Node.js | Node.js | ⚠️ منتهي | ⚠️ Deprecated |
| 3025 | 3025 | user-service | User Management | Node.js | Node.js | ✅ نشط (localhost) | ✅ Active (localhost) |

**ملاحظات | Notes**:
- خدمات منتهية الصلاحية سيتم دمجها في الخدمات الجديدة | Deprecated services to be consolidated
- user-service محمي على localhost فقط | user-service protected on localhost only

---

### نطاق 8000-8199 (خدمات Python - النواة) | Range 8000-8199 (Python Services - Core)

| المنفذ | Port | الخدمة | Service | النوع | Type | الفئة | Category |
|--------|------|---------|---------|------|------|-------|----------|
| 8080 | 8080 | field-ops | Field Operations | Python | Python | ⚠️ منتهي | ⚠️ Deprecated |
| 8081 | 8081 | ws-gateway | WebSocket Gateway | Python | Python | ✅ اتصالات | ✅ Connections |
| 8089 | 8089 | billing-core | Billing & Invoicing | Python | Python | ✅ أعمال | ✅ Business |
| 8090 | 8090 | vegetation-analysis-service | Satellite Analysis | Python | Python | ✅ ذكاء | ✅ Intelligence |
| 8091 | 8091 | indicators-service | Field Indicators | Python | Python | ✅ ذكاء | ✅ Intelligence |
| 8092 | 8092 | weather-service | Weather Data | Python | Python | ✅ بيانات | ✅ Data |
| 8093 | 8093 | advisory-service | Agricultural Advisory | Python | Python | ✅ استشارات | ✅ Advisory |
| 8094 | 8094 | irrigation-smart | Smart Irrigation | Python | Python | ✅ قرارات | ✅ Decisions |
| 8095 | 8095 | crop-intelligence-service | Crop Health AI | Python | Python | ✅ ذكاء | ✅ Intelligence |
| 8096 | 8096 | crop-health | Crop Health (Old) | Python | Python | ⚠️ منتهي | ⚠️ Deprecated |
| 8097 | 8097 | community-chat | Community Chat | Python | Python | ⚠️ منتهي | ⚠️ Deprecated |
| 8098 | 8098 | yield-engine | Yield Estimation | Python | Python | ✅ قرارات | ✅ Decisions |
| 8099 | 8099 | field-chat | Field Chat | Python | Python | ✅ اتصالات | ✅ Communication |
| 8100 | 8100 | provider-config | Provider Config | Python | Python | ✅ إعدادات | ✅ Config |
| 8101 | 8101 | equipment-service | Equipment Tracking | Python | Python | ✅ عمليات | ✅ Operations |
| 8102 | 8102 | code-review-service | Code Review Agent | Python | Python | 🔧 أدوات | 🔧 Tools |
| 8103 | 8103 | task-service | Task Management | Python | Python | ✅ عمليات | ✅ Operations |
| 8104 | 8104 | ai-agents-service | AI Agents | Python | Python | 🤖 ذكاء اصطناعي | 🤖 AI |
| 8105 | 8105 | agro-advisor | Agro Advisory | Python | Python | ✅ استشارات | ✅ Advisory |
| 8106 | 8106 | iot-gateway | IoT Protocol Gateway | Python | Python | ✅ IoT | ✅ IoT |
| 8107 | 8107 | crm-service | CRM Service | Python | Python | ✅ أعمال | ✅ Business |
| 8108 | 8108 | lowcode-engine | Low-Code Engine | Python | Python | 🔧 أدوات | 🔧 Tools |
| 8109 | 8109 | wechat-service | WeChat Service | Python | Python | ✅ اتصالات | ✅ Communication |
| 8110 | 8110 | notification-service | Notifications | Python | Python | ✅ اتصالات | ✅ Communication |
| 8111 | 8111 | astronomical-calendar | Islamic Calendar | Python | Python | ✅ أدوات | ✅ Tools |
| 8112 | 8112 | virtual-sensors | Virtual Sensors | Python | Python | ✅ IoT | ✅ IoT |
| 8113 | 8113 | alert-service | Alerts | Python | Python | ✅ اتصالات | ✅ Communication |
| 8114 | 8114 | chat-service | Chat Service | Python | Python | ✅ اتصالات | ✅ Communication |
| 8115 | 8115 | inventory-service | Inventory | Python | Python | ✅ أعمال | ✅ Business |
| 8116 | 8116 | ndvi-engine | NDVI Processing | Python | Python | ✅ ذكاء | ✅ Intelligence |
| 8117 | 8117 | iot-service | IoT Device Management | Python | Python | ✅ IoT | ✅ IoT |
| 8118 | 8118 | ndvi-processor | NDVI Processor | Python | Python | ✅ ذكاء | ✅ Intelligence |
| 8119 | 8119 | weather-core | Weather Core | Python | Python | ✅ بيانات | ✅ Data |
| 8120 | 8120 | field-intelligence | Field Analytics | Python | Python | ✅ ذكاء | ✅ Intelligence |
| 8121 | 8121 | skills-service | Skills Assessment | Python | Python | ✅ أدوات | ✅ Tools |
| 8122 | 8122 | copilot-api | Copilot API | Python | Python | 🤖 ذكاء اصطناعي | 🤖 AI |
| 8123 | 8123 | demo-data | Demo Data Service | Python | Python | 🔧 أدوات | 🔧 Tools |
| 8124 | 8124 | soil-analysis-service | Soil Analysis | Python | Python | ✅ ذكاء | ✅ Intelligence |
| 8125 | 8125 | pest-detection-service | Pest Detection | Python | Python | ✅ ذكاء | ✅ Intelligence |
| 8126 | 8126 | drone-service | Drone Integration | Python | Python | ✅ IoT | ✅ IoT |
| 8127 | 8127 | cooperative-service | Cooperative Management | Python | Python | ✅ أعمال | ✅ Business |

---

### نطاق 8130-8199 (خدمات الذكاء الاصطناعي المتقدمة) | Range 8130-8199 (Advanced AI Services)

| المنفذ | Port | الخدمة | Service | النوع | Type | GPU |
|--------|------|---------|---------|------|------|-----|
| 8130 | 8130 | llm-orchestrator-service | LLM Orchestration | Python | Python | - |
| 8140 | 8140 | knowledge-graph | Knowledge Graph | Python | Python | - |
| 8150 | 8150 | yolo26-vision-service | YOLO26 Vision | Python | Python | ✅ CUDA |
| 8160 | 8160 | agent-registry | Agent Registry | Python | Python | - |
| 8161 | 8161 | code-fix-agent | Code Fix Agent | Python | Python | - |
| 8162 | 8162 | ai-agents-core | AI Agents Core | Python | Python | - |
| 8163 | 8163 | audit-service | Audit Service | Python | Python | - |
| 8164 | 8164 | traceability-service | Traceability | Python | Python | - |
| 8165 | 8165 | globalgap-compliance | GlobalGAP | Python | Python | - |
| 8170 | 8170 | leveling-optimizer-service | Leveling Optimization | Python | Python | - |
| 8175 | 8175 | hydrology-service | Hydrology Analysis | Python | Python | - |
| 8180 | 8180 | edge-orchestrator-service | Edge Device Management | Python | Python | - |
| 8182 | 8182 | ground-vision-service | Ground Vision | Python | Python | ✅ GPU |
| 8185 | 8185 | terrain-core-service | Terrain Analysis | Python | Python | - |
| 8190 | 8190 | supply-chain-service | Supply Chain | Python | Python | - |
| 8195 | 8195 | logistics-service | Logistics | Python | Python | - |

---

### خدمات خاصة | Special Services

| المنفذ | Port | الخدمة | Service | الملاحظات | Notes |
|--------|------|---------|---------|----------|--------|
| 8200 | 8200 | mcp-server | Model Context Protocol | MCP Server |
| 8201 | 8201 | yield-prediction-service | Yield Prediction | Python (New) |
| 8151 | 8151 | agro-rules | Agronomic Rules Engine | Rules Engine |

---

## 📊 إحصائيات تخصيص المنافذ | Port Allocation Statistics

| النطاق | Range | العدد | Count | الاستخدام | Usage |
|--------|-------|------|-------|----------|-----------|
| 1000-2999 | 1000-2999 | 3 | 3 | MQTT, NATS | MQTT, NATS |
| 3000-3999 | 3000-3999 | 8 | 8 | Node.js Services | Node.js Services |
| 4000-5999 | 4000-5999 | 4 | 4 | NATS, MLflow | NATS, MLflow |
| 6000-6999 | 6000-6999 | 5 | 5 | DB, Redis, Qdrant, NATS | DB, Redis, Qdrant, NATS |
| 7000-7999 | 7000-7999 | 1 | 1 | NATS Exporter | NATS Exporter |
| 8000-8199 | 8000-8199 | 52 | 52 | Python Services (Core) | Python Services (Core) |
| 8200-8300 | 8200-8300 | 3 | 3 | Vault, MCP | Vault, MCP |
| 9000-9999 | 9000-9999 | 3 | 3 | MinIO, MQTT WS, Milvus | MinIO, MQTT WS, Milvus |
| 11000+ | 11000+ | 1 | 1 | Ollama LLM | Ollama LLM |
| 19000+ | 19000+ | 1 | 1 | Milvus | Milvus |

**إجمالي المنافذ المستخدمة | Total Ports Used**: 81

---

## 🔒 سياسات الأمان | Security Policies

### منافذ Localhost فقط | Localhost-Only Ports

هذه المنافذ **يجب** أن تكون محمية على localhost (127.0.0.1) فقط:
These ports **must** be protected on localhost (127.0.0.1) only:

- ✅ **قواعد البيانات | Databases**: 5432, 6432
- ✅ **التخزين المؤقت | Caching**: 6379, 6380
- ✅ **الرسائل | Messaging**: 4222, 4223, 8222, 1883
- ✅ **الأسرار | Secrets**: 8200-8203 (Vault)
- ✅ **التخزين | Storage**: 9000, 9090, 6333, 6334, 19530
- ✅ **الأدوات | Tools**: 5000 (MLflow), 11434 (Ollama)
- ✅ **الإدارة | Admin**: 8001, 8444 (Kong Admin)

### منافذ عامة | Public Ports

- 🌐 **Kong API Gateway**: 8000 (HTTP), 8443 (HTTPS)
- ⚠️ يجب استخدام TLS في الإنتاج | Must use TLS in production
- ⚠️ يجب تفعيل Rate Limiting | Must enable Rate Limiting

---

## ⚠️ تعارضات محتملة | Potential Conflicts

### تم اكتشافها | Identified

1. **notification-service & virtual-sensors**: كلاهما على منفذ 8110 ❌  
   **Both on port 8110 ❌**
   - الحل: نقل virtual-sensors إلى 8112 | Solution: Move virtual-sensors to 8112

2. **خدمات منتهية الصلاحية | Deprecated Services**:
   - field-ops (8080) → يجب إزالته | Should be removed
   - crop-health (8096) → يجب إزالته | Should be removed
   - community-chat (8097) → يجب إزالته | Should be removed

---

## 📝 توصيات | Recommendations

### فورية | Immediate

1. ✅ إصلاح تعارض المنفذ 8110 | Fix port 8110 conflict
2. ✅ إزالة الخدمات المنتهية الصلاحية | Remove deprecated services
3. ✅ التأكد من جميع المنافذ الحساسة على localhost | Ensure all sensitive ports on localhost

### قصيرة المدى | Short-term

1. 📝 توحيد نطاقات المنافذ | Standardize port ranges:
   - 3000-3999: Node.js services
   - 8000-8199: Python core services
   - 8200-8299: Tools & utilities
   - 9000-9999: Storage services

2. 🔒 تفعيل TLS لجميع المنافذ العامة | Enable TLS for all public ports

3. 📊 إضافة مراقبة للمنافذ | Add port monitoring

### طويلة المدى | Long-term

1. 🔄 النظر في استخدام Service Mesh (Istio/Linkerd)
2. 🔐 تنفيذ mTLS بين الخدمات | Implement mTLS between services
3. 📈 إضافة تتبع استخدام المنافذ | Add port usage tracking

---

## 🆘 دعم واستفسارات | Support & Inquiries

لأي استفسارات حول تخصيصات المنافذ:  
For any inquiries about port allocations:

- **الوثائق | Documentation**: `docs/`
- **سجل الخدمات | Service Registry**: `governance/services.yaml`
- **Docker Compose**: `docker-compose.yml`

---

**آخر تحديث | Last Updated**: 2026-02-04  
**الإصدار | Version**: 1.0
