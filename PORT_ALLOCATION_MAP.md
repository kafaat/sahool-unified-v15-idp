# خريطة تخصيص المنافذ | Port Allocation Map

**التاريخ | Date**: 2026-02-10
**المنصة | Platform**: SAHOOL v16.0.0
**المرجع الأساسي | Source of Truth**: `governance/services.yaml`, `docker-compose.yml`

---

## 🎯 نظرة عامة | Overview

هذا المستند يوثق جميع تخصيصات المنافذ (Ports) في منصة SAHOOL لتجنب التعارضات وضمان الأمان.

This document provides a comprehensive mapping of all port allocations in the SAHOOL platform to avoid conflicts and ensure security.

> **ملاحظة مهمة**: Kong API Gateway يعمل داخل شبكة Docker ويجب أن يستخدم المنفذ الداخلي للحاوية (Internal Port)، وليس المنفذ المعيّن على المضيف (Host Port).
>
> **Important**: Kong API Gateway runs inside the Docker network and must use the container's internal port, NOT the host-mapped port.

---

## 🏗️ خدمات البنية التحتية | Infrastructure Services

### قاعدة البيانات | Database Services

| الخدمة | Service | المنفذ | Port | النوع | Type |
|--------|---------|--------|------|------|------|
| PostgreSQL (PostGIS) | postgres | 5432 | 5432 | TCP | TCP |
| PgBouncer (Connection Pool) | pgbouncer | 6432 | 6432 | TCP | TCP |

### خدمات التخزين المؤقت والرسائل | Caching & Messaging

| الخدمة | Service | المنفذ | Port | الاستخدام | Usage |
|--------|---------|--------|------|----------|-------|
| Redis (Primary) | redis | 6379 | 6379 | تخزين مؤقت | Caching |
| NATS (Client) | nats | 4222 | 4222 | رسائل | Messaging |
| NATS Monitoring | nats | 8222 | 8222 | مراقبة | Monitoring |
| NATS Cluster | nats | 6222 | 6222 | تجميع | Clustering |
| NATS Prometheus | nats-exporter | 7777 | 7777 | مقاييس | Metrics |
| MQTT (Broker) | mqtt | 1883 | 1883 | IoT | IoT Protocol |
| MQTT WebSocket | mqtt | 9001 | 9001 | WebSocket | WebSocket |

### بوابة API | API Gateway

| الخدمة | Service | المنفذ | Port | الوصول | Access |
|--------|---------|--------|------|--------|--------|
| Kong (HTTP Proxy) | kong | 8000 | 8000 | عام | Public |
| Kong (HTTPS Proxy) | kong | 8443 | 8443 | عام | Public |
| Kong Admin API | kong | 8001 | 8001 | localhost | localhost |

### خدمات التخزين والأمان | Storage & Security

| الخدمة | Service | المنفذ | Port | الاستخدام | Usage |
|--------|---------|--------|------|----------|-------|
| MinIO (S3 API) | minio | 9000 | 9000 | تخزين | Storage |
| MinIO Console | minio | 9090 | 9090 | Web UI | Web UI |
| Qdrant (API) | qdrant | 6333 | 6333 | Vector DB | Vector DB |
| Qdrant (gRPC) | qdrant | 6334 | 6334 | gRPC | gRPC |
| Milvus | milvus | 19530 | 19530 | Vector DB | Vector DB |
| HashiCorp Vault | vault | 8200 | 8200 | أسرار | Secrets |
| MLflow | mlflow | 5000 | 5000 | ML Registry | ML Registry |
| Ollama (LLM) | ollama | 11434 | 11434 | LLM محلي | Local LLM |

---

## 🚀 خدمات التطبيقات | Application Services

### خدمات Node.js (نطاق 3000-3999) | Node.js Services (Range 3000-3999)

| المنفذ | Port | الخدمة | Service | الحالة | Status |
|--------|------|---------|---------|--------|--------|
| 3000 | 3000 | field-management-service | Field Management | ✅ نشط | ✅ Active |
| 3010 | 3010 | marketplace-service | Marketplace | ✅ نشط | ✅ Active |
| 3015 | 3015 | research-core | Research Trials | ✅ نشط | ✅ Active |
| 3020 | 3020 | disaster-assessment | Disaster Risk | ✅ نشط | ✅ Active |
| 3021 | 3021 | yield-prediction | Yield Prediction | ✅ نشط | ✅ Active |
| 3022 | 3022 | lai-estimation | LAI Estimation | ✅ نشط | ✅ Active |
| 3023 | 3023 | crop-growth-model | Crop Growth | ✅ نشط | ✅ Active |
| 3025 | 3025 | user-service | User Management | ✅ نشط | ✅ Active |

### خدمات Python الأساسية (نطاق 8000-8127) | Python Core Services (Range 8000-8127)

| المنفذ الداخلي | Internal Port | المنفذ الخارجي | Host Port | الخدمة | Service | الحالة | Status |
|----------------|---------------|----------------|-----------|---------|---------|--------|--------|
| 8000 | 8000 | 8115 | 8115 | chat-service | Chat Service | ✅ نشط | ✅ Active |
| 8081 | 8081 | 8081 | 8081 | ws-gateway | WebSocket Gateway | ✅ نشط | ✅ Active |
| 8088 | 8088 | 8163 | 8163 | copilot-api | Copilot API | ✅ نشط | ✅ Active |
| 8089 | 8089 | 8089 | 8089 | billing-core | Billing & Invoicing | ✅ نشط | ✅ Active |
| 8090 | 8090 | 8090 | 8090 | vegetation-analysis-service | Satellite Analysis | ✅ نشط | ✅ Active |
| 8091 | 8091 | 8091 | 8091 | indicators-service | Field Indicators | ✅ نشط | ✅ Active |
| 8092 | 8092 | 8092 | 8092 | weather-service | Weather Data | ✅ نشط | ✅ Active |
| 8093 | 8093 | 8093 | 8093 | advisory-service | Agricultural Advisory | ✅ نشط | ✅ Active |
| 8094 | 8094 | 8094 | 8094 | irrigation-smart | Smart Irrigation | ✅ نشط | ✅ Active |
| 8095 | 8095 | 8095 | 8095 | crop-intelligence-service | Crop Health AI | ✅ نشط | ✅ Active |
| 8097 | 8097 | 8097 | 8097 | community-chat | Community Chat | ✅ نشط | ✅ Active |
| 8098 | 8098 | 8098 | 8098 | yield-engine | Yield Estimation | ✅ نشط | ✅ Active |
| 8099 | 8099 | 8099 | 8099 | field-chat | Field Chat | ✅ نشط | ✅ Active |
| 8101 | 8101 | 8101 | 8101 | equipment-service | Equipment Tracking | ✅ نشط | ✅ Active |
| 8102 | 8102 | 8102 | 8102 | code-review-service | Code Review | ✅ نشط | ✅ Active |
| 8103 | 8103 | 8103 | 8103 | task-service | Task Management | ✅ نشط | ✅ Active |
| 8104 | 8104 | 8104 | 8104 | provider-config | Provider Config | ✅ نشط | ✅ Active |
| 8105 | 8105 | 8105 | 8105 | agro-advisor | Agro Advisory | ✅ نشط | ✅ Active |
| 8106 | 8106 | 8106 | 8106 | iot-gateway | IoT Protocol Gateway | ✅ نشط | ✅ Active |
| 8107 | 8107 | 8107 | 8107 | ndvi-engine | NDVI Engine | ⚠️ منتهي | ⚠️ Deprecated |
| 8108 | 8108 | 8108 | 8108 | weather-core | Weather Core | ⚠️ منتهي | ⚠️ Deprecated |
| 8110 | 8110 | 8110 | 8110 | notification-service | Notifications | ✅ نشط | ✅ Active |
| 8111 | 8111 | 8111 | 8111 | astronomical-calendar | Islamic Calendar | ✅ نشط | ✅ Active |
| 8112 | 8112 | 8112 | 8112 | ai-advisor | AI Advisor | ✅ نشط | ✅ Active |
| 8113 | 8113 | 8113 | 8113 | alert-service | Alerts | ✅ نشط | ✅ Active |
| 8114 | 8114 | 8114 | 8114 | audit-service | Audit Logging | ✅ نشط | ✅ Active |
| 8116 | 8116 | 8116 | 8116 | inventory-service | Inventory | ✅ نشط | ✅ Active |
| 8117 | 8117 | 8117 | 8117 | iot-service | IoT Device Management | ✅ نشط | ✅ Active |
| 8118 | 8118 | 8118 | 8118 | ndvi-processor | NDVI Processor | ✅ نشط | ✅ Active |
| 8119 | 8119 | 8119 | 8119 | virtual-sensors | Virtual Sensors | ✅ نشط | ✅ Active |
| 8120 | 8120 | 8120 | 8120 | field-intelligence | Field Analytics | ✅ نشط | ✅ Active |
| 8121 | 8121 | 8121 | 8121 | skills-service | Skills Assessment | ✅ نشط | ✅ Active |
| 8123 | 8123 | 8123 | 8123 | traceability-service | Traceability | ✅ نشط | ✅ Active |
| 8124 | 8124 | 8124 | 8124 | soil-analysis-service | Soil Analysis | ✅ نشط | ✅ Active |
| 8125 | 8125 | 8125 | 8125 | pest-detection-service | Pest Detection | ✅ نشط | ✅ Active |
| 8126 | 8126 | 8126 | 8126 | drone-service | Drone Integration | ✅ نشط | ✅ Active |
| 8127 | 8127 | 8127 | 8127 | cooperative-service | Cooperative Management | ✅ نشط | ✅ Active |

### خدمات متقدمة (نطاق 8128-8253) | Advanced Services (Range 8128-8253)

| المنفذ | Port | الخدمة | Service | الفئة | Category | الحالة | Status |
|--------|------|---------|---------|-------|----------|--------|--------|
| 8128 | 8128 | globalgap-compliance | GlobalGAP Compliance | امتثال | Compliance | ✅ نشط | ✅ Active |
| 8130 | 8130 | ai-agents-service | AI Agents Service | ذكاء اصطناعي | AI | ✅ نشط | ✅ Active |
| 8131 | 8131 | crm-service | CRM Service | أعمال | Business | ✅ نشط | ✅ Active |
| 8132 | 8132 | lowcode-engine | Low-Code Engine | أدوات | Tools | ✅ نشط | ✅ Active |
| 8133 | 8133 | wechat-service | WeChat Service | اتصالات | Communication | ✅ نشط | ✅ Active |
| 8140 | 8140 | knowledge-graph | Knowledge Graph | ذكاء اصطناعي | AI | ✅ نشط | ✅ Active |
| 8150 | 8150 | yolo26-vision-service | YOLO26 Vision | رؤية حاسوبية | Computer Vision | ✅ GPU |
| 8151 | 8151 | agro-rules | Agronomic Rules | قواعد زراعية | Agro Rules | ✅ NATS Worker |
| 8160 | 8160 | agent-registry | Agent Registry | وكلاء | Agents | ✅ نشط | ✅ Active |
| 8161 | 8161 | ai-agents-core | AI Agents Core | وكلاء | Agents | ✅ نشط | ✅ Active |
| 8162 | 8162 | code-fix-agent | Code Fix Agent | وكلاء | Agents | ✅ نشط | ✅ Active |
| 8164 | 8164 | llm-orchestrator-service | LLM Orchestration | ذكاء اصطناعي | AI | ✅ نشط | ✅ Active |
| 8165 | 8165 | hydrology-service | Hydrology Analysis | تضاريس | Terrain | ✅ نشط | ✅ Active |
| 8167 | 8167 | logistics-service | Logistics | لوجستيات | Logistics | ✅ نشط | ✅ Active |
| 8170 | 8170 | leveling-optimizer-service | Leveling Optimization | تضاريس | Terrain | ✅ نشط | ✅ Active |
| 8180 | 8180 | edge-orchestrator-service | Edge Device Management | حافة | Edge | ✅ نشط | ✅ Active |
| 8182 | 8182 | ground-vision-service | Ground Vision | رؤية حاسوبية | Computer Vision | ✅ GPU |
| 8183 | 8183 | ussd-gateway | USSD Gateway | اتصالات | Communication | ✅ نشط | ✅ Active |
| 8185 | 8185 | terrain-core-service | Terrain Analysis | تضاريس | Terrain | ✅ نشط | ✅ Active |
| 8200 | 8200 | mcp-server | Model Context Protocol | أدوات | Tools | ✅ نشط | ✅ Active |
| 8230 | 8230 | supply-chain-service | Supply Chain | سلسلة توريد | Supply Chain | ✅ نشط | ✅ Active |
| 8250 | 8250 | irrigation-cycle-engine | Irrigation Cycle | ري | Irrigation | ✅ v3.0 |
| 8251 | 8251 | iot-sensor-hub | IoT Sensor Hub | IoT | IoT | ✅ v3.0 |
| 8252 | 8252 | fertigation-engine | Fertigation | تسميد | Fertigation | ✅ v3.0 |
| 8253 | 8253 | digital-twin-engine | Digital Twin | توأم رقمي | Digital Twin | ✅ v3.0 |

---

## ⚠️ الخدمات المنتهية | Deprecated Services

| الخدمة المنتهية | Deprecated Service | البديل | Replacement | تاريخ الإيقاف | Date |
|-----------------|-------------------|--------|-------------|---------------|------|
| satellite-service | satellite-service | vegetation-analysis-service | vegetation-analysis-service | 2026-01-11 |
| weather-advanced | weather-advanced | weather-service | weather-service | 2026-01-11 |
| crop-health-ai | crop-health-ai | crop-intelligence-service | crop-intelligence-service | 2026-01-11 |
| fertilizer-advisor | fertilizer-advisor | advisory-service | advisory-service | 2026-01-11 |
| field-ops | field-ops | field-management-service | field-management-service | قديم | Legacy |
| field-core | field-core | field-management-service | field-management-service | قديم | Legacy |
| field-service | field-service | field-management-service | field-management-service | قديم | Legacy |
| ndvi-engine | ndvi-engine | vegetation-analysis-service | vegetation-analysis-service | ⚠️ قيد الإزالة |
| weather-core | weather-core | weather-service | weather-service | ⚠️ قيد الإزالة |

---

## 🔒 سياسات الأمان | Security Policies

### منافذ Localhost فقط | Localhost-Only Ports

هذه المنافذ **يجب** أن تكون محمية على localhost (127.0.0.1) فقط:

- **قواعد البيانات | Databases**: 5432, 6432
- **التخزين المؤقت | Caching**: 6379
- **الرسائل | Messaging**: 4222, 8222, 1883
- **الأسرار | Secrets**: 8200 (Vault)
- **التخزين | Storage**: 9000, 9090, 6333, 6334, 19530
- **الأدوات | Tools**: 5000 (MLflow), 11434 (Ollama)
- **الإدارة | Admin**: 8001 (Kong Admin)

### منافذ عامة | Public Ports

- **Kong API Gateway**: 8000 (HTTP), 8443 (HTTPS)
- يجب استخدام TLS في الإنتاج | Must use TLS in production
- يجب تفعيل Rate Limiting | Must enable Rate Limiting

---

## 📝 ملاحظات تقنية | Technical Notes

### قاعدة Kong للمنافذ | Kong Port Rule

Kong يعمل داخل شبكة Docker. عند تعريف خدمة في `kong.yml`:

```yaml
# ✅ صحيح - المنفذ الداخلي للحاوية
- name: copilot-api
  host: copilot-api
  port: 8088  # Container internal port

# ❌ خطأ - المنفذ المعيّن على المضيف
- name: copilot-api
  host: copilot-api
  port: 8163  # This is the HOST port, won't work!
```

### المراجع | References

- **سجل الخدمات | Service Registry**: `governance/services.yaml`
- **Docker Compose**: `docker-compose.yml`
- **بوابة Kong | Kong Gateway**: `infrastructure/gateway/kong/kong.yml`

---

**آخر تحديث | Last Updated**: 2026-02-10
**الإصدار | Version**: 2.0
