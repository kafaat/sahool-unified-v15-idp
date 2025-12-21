# 📦 أرشيف الخدمات القديمة (Legacy Services)
## SAHOOL Platform v15.5

---

## ⚠️ تنبيه هام

هذه الخدمات **قديمة ومتوقفة** ولا يجب استخدامها في التطوير الجديد.
تم استبدالها بخدمات حديثة ضمن معمارية Field-First.

```bash
# لتشغيل الخدمات القديمة (للاختبار فقط)
docker compose --profile legacy up -d
```

---

## 📋 قائمة الخدمات القديمة (14 خدمة)

| # | الخدمة القديمة | المنفذ | البديل الحديث | المنفذ الجديد |
|---|---------------|--------|--------------|---------------|
| 1 | field_core | 3000 | field-service | - |
| 2 | field_ops | 8080 | field-service | - |
| 3 | ndvi_engine | 8107 | satellite-service | 8090 |
| 4 | weather_core | 8108 | weather-advanced | 8092 |
| 5 | field_chat | 8099 | community-chat | 8097 |
| 6 | iot_gateway | 8106 | iot-service | - |
| 7 | agro_advisor | 8105 | fertilizer-advisor | 8093 |
| 8 | ws_gateway | 8090 | notification-service | 8110 |
| 9 | crop_health | - | crop-health-ai | 8095 |
| 10 | agro_rules | - | indicators-service | 8091 |
| 11 | task_service | - | field-service | - |
| 12 | equipment_service | - | - | (merged) |
| 13 | community_service | - | community-chat | 8097 |
| 14 | provider_config | - | - | (merged) |

---

## 📂 تفاصيل كل خدمة قديمة

### 1. field_core
```yaml
الخدمة: field_core
المنفذ: 3000
المسار: apps/services/field-service
الحالة: Legacy
البديل: field-service (موحد)
السبب: دمج إدارة الحقول في خدمة واحدة
```

**ملفات الامتداد:**
- `apps/services/field-service/Dockerfile`
- `apps/services/field-service/src/`
- `apps/services/field-service/package.json`

---

### 2. field_ops
```yaml
الخدمة: field_ops
المنفذ: 8080
المسار: apps/services/field-service
الحالة: Legacy
البديل: field-service (موحد)
السبب: دمج عمليات الحقل مع إدارة الحقول
```

**التبعيات:**
- postgres (database)
- nats (events)
- redis (cache)

---

### 3. ndvi_engine
```yaml
الخدمة: ndvi_engine
المنفذ: 8107
المسار: apps/services/ndvi-processor
الحالة: Legacy
البديل: satellite-service (8090)
السبب: توسيع لدعم NDWI, EVI, SAVI
```

**ملفات الامتداد:**
- `apps/services/ndvi-processor/Dockerfile`
- `apps/services/ndvi-processor/src/`
- `apps/services/ndvi-processor/requirements.txt`

**المخرجات القديمة:**
- NDVI only

**المخرجات الجديدة (satellite-service):**
- NDVI, NDWI, EVI, SAVI, LAI

---

### 4. weather_core
```yaml
الخدمة: weather_core
المنفذ: 8108
المسار: apps/services/weather-advanced
الحالة: Legacy
البديل: weather-advanced (8092)
السبب: إضافة تنبؤات متقدمة وتكامل FAO
```

**ملفات الامتداد:**
- `apps/services/weather-advanced/Dockerfile`
- `apps/services/weather-advanced/src/`
- `apps/services/weather-advanced/requirements.txt`

**API Keys المطلوبة:**
- `OPENWEATHER_API_KEY`

---

### 5. field_chat
```yaml
الخدمة: field_chat
المنفذ: 8099
المسار: apps/services/community-chat
الحالة: Legacy
البديل: community-chat (8097)
السبب: إعادة تصميم WebSocket
```

**ملفات الامتداد:**
- `apps/services/community-chat/Dockerfile`
- `apps/services/community-chat/src/`
- `apps/services/community-chat/package.json`

---

### 6. iot_gateway
```yaml
الخدمة: iot_gateway
المنفذ: 8106
المسار: apps/services/iot-service
الحالة: Legacy
البديل: iot-service (قيد التطوير)
السبب: تحسين بروتوكول MQTT
```

**التبعيات:**
- mqtt (broker)
- nats (events)

---

### 7. agro_advisor
```yaml
الخدمة: agro_advisor
المنفذ: 8105
المسار: apps/services/fertilizer-advisor
الحالة: Legacy
البديل: fertilizer-advisor (8093)
السبب: فصل التسميد عن الاستشارات العامة
```

---

### 8. ws_gateway
```yaml
الخدمة: ws_gateway
المنفذ: 8090
المسار: apps/services/notification-service
الحالة: Legacy
البديل: notification-service (8110)
السبب: توحيد قنوات الإشعارات
```

**القنوات القديمة:**
- WebSocket only

**القنوات الجديدة:**
- Push notifications
- SMS
- In-app
- WebSocket

---

### 9. crop_health
```yaml
الخدمة: crop_health
المنفذ: -
الحالة: Legacy
البديل: crop-health-ai (8095)
السبب: إضافة AI للتشخيص
```

---

### 10. agro_rules
```yaml
الخدمة: agro_rules
المنفذ: -
الحالة: Legacy (NATS Worker)
البديل: indicators-service (8091)
السبب: تحويل Rules إلى Indicators
```

---

### 11. task_service
```yaml
الخدمة: task_service
المنفذ: -
الحالة: Legacy
البديل: field-service
السبب: دمج المهام مع الحقول
```

---

### 12. equipment_service
```yaml
الخدمة: equipment_service
المنفذ: -
الحالة: Legacy
البديل: merged into field-service
السبب: المعدات جزء من الحقل
```

---

### 13. community_service
```yaml
الخدمة: community_service
المنفذ: -
الحالة: Legacy
البديل: community-chat (8097)
السبب: توحيد خدمات المجتمع
```

---

### 14. provider_config
```yaml
الخدمة: provider_config
المنفذ: -
الحالة: Legacy
البديل: merged into billing-core
السبب: إعدادات المزود جزء من الفوترة
```

---

## 🔄 خريطة الترحيل

```
┌────────────────────────────────────────────────────────────────┐
│                    Legacy Services (14)                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  field_core ─────┐                                             │
│  field_ops ──────┼──────► field-service                        │
│  task_service ───┤                                             │
│  equipment_svc ──┘                                             │
│                                                                 │
│  ndvi_engine ────────────► satellite-service (8090)            │
│                                                                 │
│  weather_core ───────────► weather-advanced (8092)             │
│                                                                 │
│  field_chat ─────┐                                             │
│  community_svc ──┴───────► community-chat (8097)               │
│                                                                 │
│  iot_gateway ────────────► iot-service (قيد التطوير)           │
│                                                                 │
│  agro_advisor ───────────► fertilizer-advisor (8093)           │
│                                                                 │
│  ws_gateway ─────────────► notification-service (8110)         │
│                                                                 │
│  crop_health ────────────► crop-health-ai (8095)               │
│                                                                 │
│  agro_rules ─────────────► indicators-service (8091)           │
│                                                                 │
│  provider_config ────────► billing-core (8089)                 │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 📁 هيكل ملفات الخدمات القديمة

```
apps/services/
├── field-service/          # يستخدم بواسطة: field_core, field_ops
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│
├── ndvi-processor/         # يستخدم بواسطة: ndvi_engine
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│
├── weather-advanced/       # يستخدم بواسطة: weather_core
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│
├── community-chat/         # يستخدم بواسطة: field_chat
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│
├── iot-service/           # يستخدم بواسطة: iot_gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│
├── fertilizer-advisor/    # يستخدم بواسطة: agro_advisor
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│
└── notification-service/  # يستخدم بواسطة: ws_gateway
    ├── Dockerfile
    ├── requirements.txt
    └── src/
```

---

## ⚠️ تحذيرات الترحيل

### 1. تغيير المنافذ
```yaml
# القديم → الجديد
8107 (ndvi_engine) → 8090 (satellite-service)
8108 (weather_core) → 8092 (weather-advanced)
8099 (field_chat) → 8097 (community-chat)
8105 (agro_advisor) → 8093 (fertilizer-advisor)
8090 (ws_gateway) → 8110 (notification-service)
```

### 2. تغيير API Endpoints
```yaml
# ndvi_engine → satellite-service
GET /ndvi/{field_id} → GET /v1/satellite/analyze

# weather_core → weather-advanced
GET /forecast → GET /v1/weather/forecast

# agro_advisor → fertilizer-advisor
POST /advise → POST /v1/fertilizer/recommend
```

### 3. تغيير Environment Variables
```yaml
# قديم
DATABASE_URL=postgres://...

# جديد
DB_HOST=postgres
DB_PORT=5432
DB_USER=sahool
DB_PASSWORD=...
DB_NAME=sahool
```

---

## 🗓️ جدول الإيقاف

| المرحلة | التاريخ | الإجراء |
|---------|---------|---------|
| الآن | Dec 2025 | Legacy في profile منفصل |
| Phase 2 | Jan 2026 | إزالة من docker-compose |
| Phase 3 | Feb 2026 | أرشفة الكود |
| Final | Mar 2026 | حذف نهائي |

---

## 📞 الدعم

للترحيل من الخدمات القديمة:
1. راجع `docs/architecture/PRINCIPLES.md`
2. استخدم `config/service-registry.yaml` للتصنيف
3. اختبر مع `docker compose --profile legacy up -d`

---

<p align="center">
  <strong>Legacy Services Archive</strong>
  <br>
  <sub>SAHOOL Platform v15.5</sub>
  <br>
  <sub>December 2025</sub>
</p>
