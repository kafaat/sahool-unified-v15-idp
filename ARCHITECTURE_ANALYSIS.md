# تقرير تحليل الهيكلية - SAHOOL Platform
## Architecture Analysis Report

**تاريخ التحليل:** 2025-12-22
**الإصدار:** v15.3.2 / v16.0.0

---

## 1. ملخص البنية التحتية

### 1.1 Infrastructure Services ✅

| الخدمة | الصورة | المنفذ | الحالة |
|--------|--------|--------|--------|
| PostgreSQL + PostGIS | postgis/postgis:16-3.4 | 5432 | ✅ موجود |
| Kong API Gateway | kong:3.9 | 8000, 8001 | ✅ موجود |
| NATS JetStream | nats:2.10.24-alpine | 4222, 8222 | ✅ موجود |
| Redis | redis:7.4-alpine | 6379 | ✅ موجود |
| MQTT (Mosquitto) | eclipse-mosquitto:2 | 1883, 9001 | ✅ موجود |
| Prometheus | prom/prometheus:v2.48.0 | 9090 | ✅ موجود |
| Grafana | grafana/grafana:10.2.0 | 3002 | ✅ موجود |

---

## 2. خريطة الخدمات

### 2.1 خدمات Kernel (Legacy) - من archive/

| الخدمة | المنفذ | الوصف | الحالة |
|--------|--------|-------|--------|
| field_core | 3000 | الحقول الجغرافية | 🔴 مسار مفقود |
| field_ops | 8080 | عمليات الحقول | 🔴 مسار مفقود |
| ndvi_engine | 8107 | محرك NDVI | 🔴 مسار مفقود |
| weather_core | 8108 | الطقس الأساسي | 🔴 مسار مفقود |
| field_chat | 8099 | محادثات الحقول | 🔴 مسار مفقود |
| iot_gateway | 8106 | بوابة IoT | 🔴 مسار مفقود |
| agro_advisor | 8105 | المستشار الزراعي | 🔴 مسار مفقود |
| ws_gateway | 8089 | بوابة WebSocket | 🔴 مسار مفقود |
| crop_health | 8100 | صحة المحصول | 🔴 مسار مفقود |
| agro_rules | - | قواعد زراعية (Worker) | 🔴 مسار مفقود |
| task_service | 8103 | إدارة المهام | 🔴 مسار مفقود |
| equipment_service | 8101 | إدارة المعدات | 🔴 مسار مفقود |
| community_service | 8102 | المجتمع | 🔴 مسار مفقود |
| provider_config | 8104 | تكوين المزودين | 🔴 مسار مفقود |

**⚠️ مشكلة حرجة:** جميع هذه الخدمات تشير إلى مسار `./archive/kernel-legacy/kernel/services/` الذي **لا يوجد** في المشروع!

### 2.2 خدمات جديدة (apps/services/) ✅

| الخدمة | المنفذ | الوصف | Dockerfile |
|--------|--------|-------|-----------|
| crop_health_ai | 8095 | تشخيص أمراض المحاصيل (AI) | ✅ |
| virtual_sensors | 8096 | المستشعرات الافتراضية (FAO-56) | ✅ |
| community_chat | 8097 | الدردشة (Socket.io) | ✅ |
| yield_engine | 8098 | محرك التنبؤ بالإنتاج | ✅ |
| irrigation_smart | 8094 | الري الذكي | ✅ |
| fertilizer_advisor | 8093 | مستشار التسميد | ✅ |
| indicators_service | 8091 | المؤشرات الزراعية | ✅ |
| satellite_service | 8090 | الأقمار الصناعية | ✅ |
| weather_advanced | 8092 | الطقس المتقدم | ✅ |
| notification_service | 8110 | الإشعارات | ✅ |
| research_core | 3015 | البحث العلمي (NestJS) | ✅ |
| disaster_assessment | 3020 | تقييم الكوارث (NestJS) | ✅ |
| yield_prediction | 3021 | التنبؤ بالإنتاجية (NestJS) | ✅ |
| lai_estimation | 3022 | تقدير LAI (NestJS) | ✅ |
| crop_growth_model | 3023 | نموذج نمو المحاصيل (NestJS) | ✅ |
| marketplace_service | 3010 | السوق والتمويل (NestJS) | ✅ |

---

## 3. الثغرات الحرجة 🔴

### 3.1 مسارات البناء المفقودة

```yaml
# docker-compose.yml - المسارات التالية غير موجودة:
./archive/kernel-legacy/kernel/services/field_core
./archive/kernel-legacy/kernel/services/field_ops
./archive/kernel-legacy/kernel/services/ndvi_engine
./archive/kernel-legacy/kernel/services/weather_core
./archive/kernel-legacy/kernel/services/field_chat
./archive/kernel-legacy/kernel/services/iot_gateway
./archive/kernel-legacy/kernel/services/agro_advisor
./archive/kernel-legacy/kernel/services/ws_gateway
./archive/kernel-legacy/kernel/services/crop_health
./archive/kernel-legacy/kernel/services/agro_rules
./archive/kernel-legacy/kernel/services/task_service
./archive/kernel-legacy/kernel/services/equipment_service
./archive/kernel-legacy/kernel/services/community_service
./archive/kernel-legacy/kernel/services/provider_config
```

### 3.2 خدمة المصادقة (Auth) مفقودة

**المشكلة:** لا يوجد خدمة مصادقة مستقلة!
- جميع الخدمات تستخدم `JWT_SECRET_KEY` لكن لا يوجد من يُولّد الـ tokens
- Kong لديه JWT plugin لكن بدون خدمة auth فعلية

**الحل المقترح:**
```yaml
auth_service:
  build: ./apps/services/auth
  ports:
    - "8000:8000"
  environment:
    - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    - DATABASE_URL=...
```

### 3.3 Frontend Web الرئيسي مفقود

**المشكلة:** `admin_dashboard` موجود لكن **تطبيق web الرئيسي للمزارعين غير موجود** في docker-compose.

**ملاحظة:** يوجد في `apps/web` لكنه غير مضمن في docker-compose.

### 3.4 مسار خاطئ (Backslash)

```yaml
# خطأ في docker-compose.yml:
admin_dashboard:
  build:
    context: ./archive\frontend-legacy\frontend\dashboard  # ❌ Backslash!
```

يجب أن يكون:
```yaml
context: ./archive/frontend-legacy/frontend/dashboard
```

---

## 4. تكرار الخدمات 🟡

| الوظيفة | الخدمات المكررة | التوصية |
|---------|-----------------|---------|
| الطقس | weather_core, weather_advanced | دمج أو حذف أحدهما |
| المجتمع | community_service, community_chat | توضيح الفرق أو دمج |
| الإنتاج | yield_engine, yield_prediction | توضيح الفرق |

---

## 5. Kong API Gateway Analysis

### 5.1 Upstreams المعرّفة ✅

| Upstream | Target | Health Check |
|----------|--------|--------------|
| field-ops-upstream | sahool-field-ops:8080 | ✅ /healthz |
| ndvi-engine-upstream | sahool-ndvi-engine:8107 | ✅ /health |
| weather-upstream | sahool-weather-core:8108 | ✅ /health |
| chat-upstream | sahool-field-chat:8099 | ✅ /health |
| iot-upstream | sahool-iot-gateway:8106 | ✅ /health |
| advisor-upstream | sahool-agro-advisor:8105 | ✅ /health |
| ws-gateway-upstream | sahool-ws-gateway:8089 | ✅ /health |
| crop-health-upstream | sahool-crop-health:8100 | ✅ /health |
| satellite-upstream | sahool-satellite-service:8090 | ✅ /health |
| ... (20+ more) | ... | ... |

### 5.2 Routes المعرّفة

| Route | Paths | Rate Limit |
|-------|-------|------------|
| field-ops-route | /api/v1/fields, /tasks, /assignments | 60/min, 2000/hr |
| ndvi-route | /api/v1/ndvi, /satellite | 30/min, 500/hr |
| weather-route | /api/v1/weather, /forecast | - |
| chat-route | /api/v1/chat, /messages | 120/min |
| iot-route | /api/v1/iot, /sensors, /devices | 200/min |
| advisor-route | /api/v1/advisor, /recommendations | 30/min |
| ws-route | /ws, /api/v1/realtime | - |
| ... | ... | ... |

### 5.3 مشاكل Kong

1. **Port غير صحيح في crop-growth-upstream:**
   ```yaml
   target: sahool-crop-growth-model:3000  # يجب أن يكون 3023
   ```

2. **Health check paths غير متسقة:**
   - بعضها `/healthz` والبعض الآخر `/health`

---

## 6. NATS Subjects Analysis

### 6.1 Pattern المستخدم
```
sahool.events.{event_type}
```

### 6.2 الخدمات المتصلة بـ NATS

| الخدمة | NATS_URL | الاستخدام |
|--------|----------|-----------|
| field_ops | ✅ | Publisher/Consumer |
| ndvi_engine | ✅ | Publisher |
| weather_core | ✅ | Publisher |
| field_chat | ✅ | Publisher |
| iot_gateway | ✅ | Publisher |
| agro_advisor | ✅ | Publisher |
| ws_gateway | ✅ | Consumer (للـ WebSocket) |
| agro_rules | ✅ | Consumer (Worker) |
| notification_service | ✅ | Consumer |

### 6.3 الخدمات **غير** متصلة بـ NATS

- crop_health_ai ❌
- virtual_sensors ❌
- irrigation_smart ❌
- fertilizer_advisor ❌
- indicators_service ❌
- satellite_service ❌
- weather_advanced ❌
- yield_engine ❌
- community_chat ❌

**تأثير:** هذه الخدمات لا يمكنها إرسال/استقبال أحداث في الوقت الحقيقي.

---

## 7. Frontend Integration

### 7.1 apps/web

| الملف | الخدمة المستهدفة | الـ Route |
|-------|-----------------|-----------|
| ndvi/api.ts | ❓ غير محدد | /api/v1/ndvi |
| alerts/api.ts | ❓ غير محدد | /api/v1/alerts |
| advisor/api.ts | ❓ غير محدد | /api/v1/advisor |
| field-map/api.ts | ❓ غير محدد | /api/v1/fields |
| reports/api.ts | ❓ غير محدد | /api/v1/reports |

**مشكلة:** يستخدم `NEXT_PUBLIC_API_URL || '/api'` - يتوقع Kong proxy.

### 7.2 apps/admin

| الخدمة | المنفذ في api.ts | المنفذ الفعلي | التطابق |
|--------|-----------------|---------------|---------|
| fieldCore | 3000 | 3000 | ✅ |
| satellite | 8090 | 8090 | ✅ |
| indicators | 8091 | 8091 | ✅ |
| weather | 8092 | 8092 | ✅ |
| fertilizer | 8093 | 8093 | ✅ |
| irrigation | 8094 | 8094 | ✅ |
| cropHealth | 8095 | 8095 | ✅ |
| virtualSensors | 8096 | 8096 | ✅ |
| communityChat | 8097 | 8097 | ✅ |
| yieldEngine | 8098 | 8098 | ✅ |
| equipment | 8101 | 8101 | ✅ |
| community | 8102 | 8102 | ✅ |
| task | 8103 | 8103 | ✅ |
| providerConfig | 8104 | 8104 | ✅ |
| notifications | 8110 | 8110 | ✅ |
| wsGateway | 8090 | 8089 | ❌ خطأ! |

---

## 8. قائمة الأولويات

### 🔴 الأولوية القصوى (يجب إصلاحها فوراً)

1. **إنشاء/استعادة Kernel Services**
   - إما إنشاء `archive/kernel-legacy/` أو تعديل docker-compose لاستخدام apps/services/

2. **إضافة Auth Service**
   - إنشاء خدمة مصادقة مستقلة
   - أو استخدام خدمة موجودة وتوثيقها

3. **إصلاح wsGateway port** في apps/admin/src/lib/api.ts
   ```typescript
   wsGateway: 8089,  // وليس 8090
   ```

4. **إصلاح crop-growth-model port** في kong.yml
   ```yaml
   target: sahool-crop-growth-model:3023  # وليس 3000
   ```

### 🟡 الأولوية المتوسطة

5. **إضافة web app** إلى docker-compose
6. **توحيد Health check paths** (`/healthz` أو `/health`)
7. **ربط الخدمات الجديدة بـ NATS**

### 🟢 الأولوية المنخفضة

8. **توضيح تكرار الخدمات**
9. **تحديث التوثيق**

---

## 9. المرحلة التالية المقترحة

### اليوم الثاني: مراجعة الخدمات الحرجة

بناءً على التحليل، الخدمات الأكثر أهمية للمراجعة:

1. **crop_health_ai** (8095) - الميزة الفريدة (AI)
2. **satellite_service** (8090) - NDVI والأقمار الصناعية
3. **irrigation_smart** (8094) - الري الذكي (FAO-56)
4. **marketplace_service** (3010) - السوق والتمويل

---

## 10. الرسم البياني للهيكلية

```
┌─────────────────────────────────────────────────────────────────┐
│                        SAHOOL Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Web App  │    │  Admin   │    │ Mobile   │    │ Flutter  │  │
│  │ (Next.js)│    │(Next.js) │    │  (TBD)   │    │  (TBD)   │  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│       │               │               │               │        │
│       └───────────────┴───────────────┴───────────────┘        │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │    Kong     │                              │
│                    │ API Gateway │                              │
│                    │   :8000     │                              │
│                    └──────┬──────┘                              │
│                           │                                     │
│    ┌──────────────────────┼──────────────────────┐             │
│    │                      │                      │             │
│    ▼                      ▼                      ▼             │
│ ┌──────────┐      ┌──────────────┐      ┌──────────────┐      │
│ │ Legacy   │      │ New Services │      │ NestJS       │      │
│ │ Kernel   │      │ (Python)     │      │ Services     │      │
│ │ Services │      │              │      │              │      │
│ │ (🔴 N/A) │      │ :8090-8098   │      │ :3010-3023   │      │
│ └────┬─────┘      └──────┬───────┘      └──────┬───────┘      │
│      │                   │                      │              │
│      └───────────────────┴──────────────────────┘              │
│                          │                                      │
│         ┌────────────────┼────────────────┐                    │
│         ▼                ▼                ▼                    │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐                │
│   │PostgreSQL│    │   NATS   │    │  Redis   │                │
│   │ +PostGIS │    │JetStream │    │  Cache   │                │
│   │  :5432   │    │  :4222   │    │  :6379   │                │
│   └──────────┘    └──────────┘    └──────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**انتهى التقرير**

*تم إنشاؤه بواسطة Claude Code*
