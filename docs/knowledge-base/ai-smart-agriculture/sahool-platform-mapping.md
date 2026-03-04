---
title: ربط مفاهيم الذكاء الزراعي بمنصة SAHOOL - Platform Mapping
description: كيف تطبق منصة SAHOOL مفاهيم سلسلة الذكاء الزراعي في خدماتها الفعلية
tags:
  - sahool
  - platform-mapping
  - services
  - architecture
  - implementation
category: ai-smart-agriculture
last_updated: 2026-03-03
version: 2.0.0
---

# ربط سلسلة الذكاء الزراعي بمنصة SAHOOL | Platform Mapping

كيف تطبق منصة **SAHOOL** مفاهيم سلسلة الذكاء الزراعي AI+ في خدماتها الـ 71 الفعلية.

How SAHOOL implements the AI+ Agriculture industry chain concepts across its 71 microservices.

---

## ربط طبقات سلسلة الصناعة بخدمات SAHOOL | Industry Chain → SAHOOL Services

### طبقة جمع البيانات | Data Collection Layer

| مفهوم سلسلة الصناعة | SAHOOL Service | المنفذ | الوصف |
|---------------------|----------------|--------|-------|
| شبكة مستشعرات IoT | `iot-service` | 8117 | إدارة أجهزة إنترنت الأشياء |
| بوابة بروتوكولات IoT | `iot-gateway` | 8106 | بوابة بروتوكولات MQTT/CoAP |
| محور المستشعرات | `iot-sensor-hub` | 8251 | تجميع بيانات المستشعرات |
| المستشعرات الافتراضية | `virtual-sensors` | 8119 | حساب قيم مشتقة من بيانات المستشعرات |
| الاستشعار عن بعد | `vegetation-analysis-service` | 8090 | تحليل صور الأقمار الصناعية (Sentinel) |
| بيانات الطقس | `weather-service` | 8092 | جمع ومعالجة البيانات المناخية |
| معالجة حافة | `edge-orchestrator-service` | 8180 | إدارة أجهزة Jetson Orin الطرفية |

### طبقة معالجة وتخزين البيانات | Data Processing & Storage

| مفهوم سلسلة الصناعة | SAHOOL Component | الوصف |
|---------------------|------------------|-------|
| منصة البيانات الكبرى | PostgreSQL 16 + PostGIS 3.4 | قاعدة بيانات مكانية متقدمة |
| تخزين السلاسل الزمنية | Redis 7.x + PostgreSQL | تخزين وتخبئة البيانات الزمنية |
| نظام الأحداث | NATS JetStream | نقل الأحداث بين الخدمات (4 طبقات) |
| تخزين المتجهات | Qdrant 1.7.x / Milvus 2.3.x | تخزين المتجهات لنظام RAG |
| تتبع النماذج | MLflow 2.15.x | إدارة وتتبع نماذج AI |

### طبقة تحليل الخوارزميات | AI Algorithm Analysis

| نموذج سلسلة الصناعة | SAHOOL Service | المنفذ | الوصف |
|---------------------|----------------|--------|-------|
| نموذج الزراعة الذكية | `advisory-service` | 8093 | توصيات ونصائح زراعية ذكية |
| نموذج تقدير الإنتاج | `yield-prediction-service` | 8152 | تنبؤ بالإنتاجية عبر ML |
| نموذج الآفات والأمراض | `yolo26-vision-service` | 8150 | كشف 22 آفة + 34 مرض + 12 عشب |
| نموذج الآفات (تكميلي) | `pest-detection-service` | 8125 | كشف إضافي للآفات |
| نموذج نمو المحاصيل | `crop-growth-model` | 3023 | محاكاة مراحل نمو المحاصيل |
| تحليل صحة المحاصيل | `crop-intelligence-service` | 8095 | تحليل ذكي لصحة المحاصيل |
| حساب NDVI/LAI | `vegetation-analysis-service` | 8090 | تحليل الغطاء النباتي |
| تقدير LAI | `lai-estimation` | 3022 | تقدير مؤشر مساحة الأوراق |
| تحليل التربة | `soil-analysis-service` | 8134 | تحليل التربة بالذكاء الاصطناعي |
| تحليل التضاريس | `terrain-core-service` | 8185 | تحليل DEM والتضاريس |
| تحليل المياه | `hydrology-service` | 8165 | تحليل الصرف والمياه |
| رؤية أرضية | `ground-vision-service` | 8182 | تحليل الصور الأرضية |

### طبقة مخرجات القرار | Decision Output

| نموذج سلسلة الصناعة | SAHOOL Service | المنفذ | الوصف |
|---------------------|----------------|--------|-------|
| إنذارات مبكرة | `alert-service` | 8113 | نظام التنبيهات والإنذارات |
| نظام القرارات الذكي | `advisory-service` | 8093 | محرك التوصيات الزراعية |
| الري الذكي | `irrigation-smart` | 8094 | جدولة ري ذكية بالذكاء الاصطناعي |
| قواعد زراعية | `agro-rules` | 8151 | محرك القواعد الزراعية |
| حلول مخصصة | `ai-advisor` | 8112 | مستشار AI مخصص |
| تحسين التسوية | `leveling-optimizer-service` | 8170 | تحسين تسوية الحقول |
| تقويم زراعي | `astronomical-calendar` | 8111 | تقويم إسلامي وزراعي |

### طبقة التنفيذ الميداني | Field Execution

| نموذج سلسلة الصناعة | SAHOOL Service | المنفذ | الوصف |
|---------------------|----------------|--------|-------|
| إدارة الحقول | `field-management-service` | 3000 | إدارة الحقول (الخدمة الموحدة) |
| إدارة المعدات | `equipment-service` | 8101 | تتبع وصيانة المعدات |
| إدارة المهام | `task-service` | 8103 | إدارة وتوزيع مهام الحقل |
| تكامل الطائرات | `drone-service` | 8126 | تخطيط رحلات الطائرات |
| تتبع المنتجات | `traceability-service` | 8123 | تتبع سلسلة التوريد |
| السوق الزراعي | `marketplace-service` | 3010 | سوق إلكتروني زراعي |
| إشعارات | `notification-service` | 8110 | إشعارات متعددة القنوات |

---

## ربط بنية IoT بمكونات SAHOOL | IoT Architecture → SAHOOL

### طبقة الأجهزة → SAHOOL

```
المستشعرات الميدانية
    │
    v
┌───────────────────────────────────────────────┐
│  shared/soil_sensors/     ← محولات المستشعرات │
│  shared/irrigation/       ← أجهزة الري        │
│  shared/weather_alerts/   ← محطات الطقس       │
└───────────────────────────────────────────────┘
```

### طبقة الشبكة → SAHOOL

```
بروتوكولات الاتصال
    │
    v
┌───────────────────────────────────────────────┐
│  iot-gateway (8106)       ← MQTT/CoAP بوابة  │
│  ws-gateway (8081)        ← WebSocket         │
│  NATS JetStream           ← أحداث داخلية     │
│  Mosquitto MQTT 2.x       ← وسيط IoT         │
└───────────────────────────────────────────────┘
```

### طبقة المنصة → SAHOOL

```
معالجة وتحليل
    │
    v
┌───────────────────────────────────────────────┐
│  PostgreSQL 16 + PostGIS  ← تخزين مكاني      │
│  Redis 7.x                ← تخبئة وجلسات     │
│  Kong 3.x                 ← بوابة API         │
│  Prometheus + Grafana     ← مراقبة            │
│  OpenTelemetry + Jaeger   ← تتبع موزع        │
│  shared/ai/*              ← نماذج AI          │
│  shared/monitoring/       ← SLI/SLO           │
└───────────────────────────────────────────────┘
```

### طبقة التطبيقات → SAHOOL

```
واجهات المستخدم
    │
    v
┌───────────────────────────────────────────────┐
│  apps/web/                ← لوحة التحكم       │
│  apps/admin/              ← بوابة الإدارة     │
│  apps/mobile/             ← تطبيق الحقل       │
│    sahool_field_app       ← تطبيق الحقل الرئيسي│
│    sahol_atmosphere       ← تطبيق الطقس       │
│  chat-service (8000)      ← دردشة الحقل       │
│  whatsapp-bot (8240)      ← بوت واتساب        │
│  ussd-gateway (8183)      ← بوابة USSD        │
└───────────────────────────────────────────────┘
```

---

## ربط الزراعة الدقيقة بوحدات SAHOOL المشتركة | Precision Farming → Shared Modules

| مرحلة الزراعة الدقيقة | SAHOOL Shared Module | الوصف |
|-----------------------|---------------------|-------|
| تحليل التربة | `shared/soil_testing/` | تفسير نتائج فحص التربة |
| اختيار الأصناف | `shared/crop_rotation/` | تخطيط الدورة الزراعية |
| الري الذكي | `shared/irrigation/` | جدولة ري ذكية |
| الري ML | `shared/ml_irrigation/` | تحسين الري بالتعلم الآلي |
| إدارة المياه | `shared/water_management/` | رصد كفاءة استخدام المياه |
| إدارة الملوحة | `shared/salinity/` | مراقبة ملوحة التربة |
| التسميد | `shared/fertilizer_management/` | توصيات المغذيات |
| رصد الآفات | `shared/pest_scouting/` | مسح ورصد الآفات |
| الامتثال للمبيدات | `shared/pesticide_compliance/` | سلامة المبيدات (PHI) |
| التقويم الزراعي | `shared/agri_calendar/` | مواعيد الزراعة والحصاد |
| حدود الحقول | `shared/field_boundaries/` | عمليات جغرافية مكانية |
| جودة الحصاد | `shared/harvest_quality/` | فرز وتصنيف الجودة |
| تكامل الطائرات | `shared/drone_integration/` | تخطيط VRA |
| التأمين | `shared/crop_insurance/` | تقييم المخاطر |
| السوق | `shared/market_prices/` | تتبع الأسعار |

---

## ربط بنية الأحداث | Event Architecture Mapping

بنية SAHOOL ذات الأربع طبقات تتوافق مباشرة مع سلسلة الصناعة:

| طبقة سلسلة الصناعة | طبقة أحداث SAHOOL | خدمات SAHOOL |
|-------------------|-------------------|-------------|
| **جمع البيانات** | **Acquisition** | vegetation-analysis, iot-service, weather-service, virtual-sensors, iot-gateway, edge-orchestrator |
| **تحليل الخوارزميات** | **Intelligence** | indicators-service, lai-estimation, crop-intelligence, yolo26-vision, terrain-core, field-intelligence |
| **مخرجات القرار** | **Decision** | crop-growth-model, advisory-service, irrigation-smart, yield-prediction, hydrology, leveling-optimizer |
| **التنفيذ الميداني** | **Business** | notification-service, marketplace, billing-core, chat-service, task-service, equipment-service |

### نمط الأحداث | Event Patterns

```
# جمع البيانات → تحليل
sahool.iot.sensor_reading    → indicators-service → sahool.indicator.computed
sahool.satellite.ndvi_ready  → vegetation-analysis → sahool.field.health_updated

# تحليل → قرار
sahool.vision.pest_detected  → advisory-service → sahool.advisory.recommendation_created
sahool.indicator.threshold_exceeded → alert-service → sahool.alert.created

# قرار → تنفيذ
sahool.advisory.irrigation_needed → irrigation-smart → sahool.irrigation.scheduled
sahool.alert.created → notification-service → sahool.notification.sent
```

---

## الخدمات الذكية الإضافية في SAHOOL | Additional AI Services

| الخدمة | Service | الوصف | الربط |
|--------|---------|-------|-------|
| `copilot-api` | 8088 | مساعد AI متعدد LLM مع RAG | مستشار ذكي شامل |
| `ai-chat-assistant` | 8260 | مساعد دردشة AI | تفاعل مع المزارعين |
| `knowledge-graph` | 8140 | رسم بياني للمعرفة | ربط المعلومات الزراعية |
| `llm-orchestrator-service` | 8164 | تنسيق LLM | إدارة نماذج اللغة |
| `agent-registry` | 8160 | سجل الوكلاء | تنسيق وكلاء AI |
| `skills-service` | 8121 | تقييم المهارات | تقييم مهارات المزارعين |
| `digital-twin-engine` | 8253 | التوائم الرقمية | محاكاة افتراضية للحقول |

---

## ربط الأنماط المعمارية الجديدة (2025) بخدمات SAHOOL | New Architecture Patterns Mapping

### نمط الاندماج الثلاثي (Triple Fusion) — مستوحى من iMAP

```
خدمات SAHOOL الحالية التي تحقق هذا النمط:

آلية المحصول (Crop Mechanism)         ←→ crop-growth-model (3023)
                                          + shared/agri_calendar/
                                          + shared/crop_rotation/
        ×
نموذج لغوي كبير (LLM)                ←→ llm-orchestrator-service (8164)
                                          + copilot-api (8088)
                                          + shared/ai/llm_provider.py
        ×
نظام وكلاء (Agent System)            ←→ agent-registry (8160)
                                          + ai-agents-core (8161)
                                          + shared/agents/ (CrewAI)
```

### نمط LLM + نموذج صغير + قاعدة معرفة — مستوحى من 农科小智

```
LLM كبير                              ←→ Ollama (codellama/mistral)
                                          + shared/ai/ollama_client.py
        +
نموذج صغير متخصص                     ←→ yolo26-vision-service (8150)
                                          + shared/ai/crop_vision.py
                                          + pest-detection-service (8125)
        +
قاعدة معرفة محلية                     ←→ shared/ai/knowledge/ (63+ وثيقة)
                                          + shared/ai/ultrarag/
                                          + shared/ai/vector_store.py
```

### نمط RAG + Tool Calling — مستوحى من CropWizard

```
RAG ضخم                               ←→ shared/ai/ultrarag/ (AgriRAGProvider)
                                          + Qdrant/Milvus vector stores
        +
Tool Calling                          ←→ mcp-server (8201)
                                          + shared/mcp/
                                          + shared/ai/tool_registry.py
```

---

## ربط قنوات الوصول الميسّر | Accessible Access Channels Mapping

| قناة الوصول | Access Channel | خدمة SAHOOL | المنفذ | الحالة |
|------------|---------------|-------------|--------|--------|
| **WhatsApp Bot** | Super App messaging | `whatsapp-bot-service` | 8240 | متوفر ✓ |
| **USSD Gateway** | أي هاتف بدون إنترنت | `ussd-gateway` | 8183 | متوفر ✓ |
| **واجهة صوتية** | تفاعل صوتي عربي | `shared/nlp/` (AraBERT) | - | جزئي |
| **دردشة AI** | مساعد ذكي تفاعلي | `ai-chat-assistant` | 8260 | متوفر ✓ |
| **تطبيق موبايل** | تطبيق كامل الميزات | `sahool_field_app` | - | متوفر ✓ |
| **لوحة ويب** | إدارة عبر المتصفح | `apps/web/` | - | متوفر ✓ |

---

## ربط نماذج الأعمال بخدمات SAHOOL | Business Models Mapping

| نموذج الأعمال | Business Model | خدمات SAHOOL | الحالة |
|-------------|---------------|-------------|--------|
| **AIaaS (اشتراك)** | `billing-core` (8089) + `user-service` (3025) | متوفر ✓ |
| **منصة مفتوحة** | `mcp-server` (8201) + Kong API Gateway | جزئي |
| **أونلاين + ميداني** | `advisory-service` (8093) + `task-service` (8103) | بنية جاهزة |
| **أجهزة + خدمة** | `iot-service` (8117) + `edge-orchestrator` (8180) | متوفر ✓ |
| **وصول ميسّر** | `ussd-gateway` (8183) + `whatsapp-bot` (8240) | متوفر ✓ |
| **بيانات كأصل** | `knowledge-graph` (8140) + analytics (kernel) | مخطط |

---

> **ملاحظة**: منصة SAHOOL تطبق بالفعل جميع طبقات سلسلة الذكاء الزراعي عبر بنيتها الخدمية المصغرة (71 خدمة). مع تحديثات 2025، أصبحت المنصة مؤهلة لتطبيق الأنماط المعمارية الجديدة (Triple Fusion, Multi-Agent RAG, Tool Calling) وقنوات الوصول الميسّر (USSD, WhatsApp, صوت) — مما يسد الفجوة بين "80% يعترفون بالفائدة و20% فقط تبنوا".

*آخر تحديث: مارس 2026*
