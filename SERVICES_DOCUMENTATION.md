# SAHOOL v15.3 - توثيق الخدمات
# Services Documentation

## نظرة عامة | Overview

منصة سهول الزراعية الذكية - نظام متكامل لإدارة المزارع في اليمن باستخدام الذكاء الاصطناعي والأقمار الصناعية.

SAHOOL Smart Agricultural Platform - An integrated farm management system for Yemen using AI and satellite technology.

---

## مخطط البنية | Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SAHOOL Platform v15.3                              │
│                          منصة سهول الزراعية الذكية                              │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────┐
                                    │   Clients   │
                                    │  العملاء    │
                                    └──────┬──────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
            ┌───────▼───────┐      ┌───────▼───────┐      ┌───────▼───────┐
            │ Flutter App   │      │ Admin Panel   │      │  External API │
            │ تطبيق الموبايل │      │ لوحة التحكم   │      │   APIs خارجية │
            │   (Mobile)    │      │  (Next.js)    │      │               │
            └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
                    │                      │                      │
                    └──────────────────────┼──────────────────────┘
                                           │
                                    ┌──────▼──────┐
                                    │    Kong     │
                                    │ API Gateway │
                                    │   :8000     │
                                    └──────┬──────┘
                                           │
        ┌──────────────────────────────────┼──────────────────────────────────┐
        │                                  │                                  │
        │                    ┌─────────────┼─────────────┐                    │
        │                    │             │             │                    │
┌───────▼───────┐    ┌───────▼───────┐    │    ┌───────▼───────┐    ┌───────▼───────┐
│  field_core   │    │  field_ops    │    │    │  crop_health  │    │   weather     │
│    :3000      │    │    :8080      │    │    │  AI :8095     │    │    :8092      │
│  الحقول       │    │  العمليات     │    │    │  أمراض النبات │    │   الطقس       │
└───────┬───────┘    └───────┬───────┘    │    └───────┬───────┘    └───────┬───────┘
        │                    │            │            │                    │
        │            ┌───────▼───────┐    │    ┌───────▼───────┐            │
        │            │  irrigation   │    │    │virtual_sensors│            │
        │            │    :8094      │    │    │    :8096      │            │
        │            │  الري الذكي   │    │    │ المستشعرات    │            │
        │            └───────┬───────┘    │    └───────┬───────┘            │
        │                    │            │            │                    │
        └────────────────────┼────────────┼────────────┼────────────────────┘
                             │            │            │
                    ┌────────▼────────────▼────────────▼────────┐
                    │              Message Bus                  │
                    │         NATS JetStream :4222              │
                    │            ناقل الرسائل                   │
                    └────────┬────────────┬────────────┬────────┘
                             │            │            │
        ┌────────────────────┼────────────┼────────────┼────────────────────┐
        │                    │            │            │                    │
┌───────▼───────┐    ┌───────▼───────┐    │    ┌───────▼───────┐    ┌───────▼───────┐
│  PostgreSQL   │    │    Redis      │    │    │     MQTT      │    │   Satellite   │
│   (PostGIS)   │    │   Cache       │    │    │  IoT Broker   │    │   Service     │
│    :5432      │    │    :6379      │    │    │    :1883      │    │    :8090      │
│  قاعدة البيانات│    │  التخزين المؤقت│    │    │   أجهزة IoT   │    │  الأقمار      │
└───────────────┘    └───────────────┘    │    └───────────────┘    └───────────────┘
                                          │
                              ┌───────────▼───────────┐
                              │    More Services...   │
                              │   fertilizer :8093    │
                              │   indicators :8091    │
                              │   yield_engine :8098  │
                              │   community_chat:8097 │
                              └───────────────────────┘
```

### تدفق البيانات | Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Disease Diagnosis Flow                                │
│                          تدفق تشخيص أمراض النباتات                              │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  Farmer  │────▶│  Camera  │────▶│ Flutter  │────▶│  Kong    │────▶│ Crop AI  │
  │  المزارع │     │  الكاميرا │     │   App    │     │ Gateway  │     │  :8095   │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                                           │
       ┌───────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │TensorFlow│────▶│ Disease  │────▶│Treatment │────▶│ Response │
  │  Model   │     │   ID     │     │   Plan   │     │ للمزارع  │
  │  النموذج │     │ المرض    │     │  العلاج  │     │          │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│                          Smart Irrigation Flow                                  │
│                           تدفق الري الذكي                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  Field   │────▶│ Weather  │────▶│ Virtual  │────▶│Irrigation│────▶│ Schedule │
  │  Data    │     │  :8092   │     │ Sensors  │     │  Smart   │     │  جدول    │
  │بيانات الحقل│     │  الطقس   │     │  :8096   │     │  :8094   │     │  الري    │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                         │                │                │
                         ▼                ▼                ▼
                   ┌──────────┐     ┌──────────┐     ┌──────────┐
                   │Temperature│    │   ET0    │     │  Water   │
                   │ Humidity  │    │ FAO-56   │     │ Balance  │
                   │  الحرارة  │    │ التبخر   │     │  الميزان │
                   └──────────┘     └──────────┘     └──────────┘
```

### المكونات الرئيسية | Core Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Technology Stack                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
  │    Frontend     │   │    Backend      │   │  Infrastructure │
  │    الواجهات     │   │   الخلفية       │   │   البنية التحتية │
  ├─────────────────┤   ├─────────────────┤   ├─────────────────┤
  │ • Flutter       │   │ • Python 3.11   │   │ • Docker        │
  │ • Riverpod      │   │ • FastAPI       │   │ • Kong Gateway  │
  │ • Next.js 14    │   │ • Node.js       │   │ • PostgreSQL    │
  │ • Tailwind CSS  │   │ • TensorFlow    │   │ • Redis         │
  │ • Leaflet Maps  │   │ • Socket.io     │   │ • NATS          │
  └─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## البنية التحتية | Infrastructure Services

| الخدمة | المنفذ | الوصف |
|--------|-------|-------|
| PostgreSQL (PostGIS) | 5432 | قاعدة البيانات المكانية |
| Kong API Gateway | 8000, 8001 | بوابة API |
| NATS | 4222, 8222 | نظام الرسائل |
| Redis | 6379 | التخزين المؤقت |
| MQTT (Mosquitto) | 1883, 9001 | IoT messaging |

---

## خدمات النواة القديمة | Legacy Kernel Services

| الخدمة | المنفذ | الوصف |
|--------|-------|-------|
| field_core | 3000 | خدمة الحقول الأساسية |
| field_ops | 8080 | عمليات الحقول |
| ws_gateway | 8089 | بوابة WebSocket |
| crop_health | 8100 | صحة المحاصيل (قديم) |
| equipment_service | 8101 | إدارة المعدات |
| community_service | 8102 | خدمة المجتمع |
| task_service | 8103 | إدارة المهام |
| provider_config | 8104 | تكوين المزودين |
| agro_advisor | 8105 | المستشار الزراعي |
| iot_gateway | 8106 | بوابة IoT |
| ndvi_engine | 8107 | محرك NDVI |
| weather_core | 8108 | خدمة الطقس الأساسية |

---

## خدمات v15.3 الجديدة | New v15.3 Services

### 1. Satellite Service - خدمة الأقمار الصناعية
- **المنفذ:** 8090
- **المسار:** `kernel-services-v15.3/satellite-service`
- **الوصف:** تحليل صور الأقمار الصناعية ومؤشر NDVI
- **Endpoints:**
  - `GET /v1/analyze` - تحليل صورة
  - `GET /v1/timeseries` - السلسلة الزمنية
  - `GET /v1/satellites` - الأقمار المتاحة
  - `GET /healthz` - فحص الصحة

### 2. Indicators Service - خدمة المؤشرات
- **المنفذ:** 8091
- **المسار:** `kernel-services-v15.3/indicators-service`
- **الوصف:** مؤشرات الأداء الزراعية والتحليلات
- **Endpoints:**
  - `GET /v1/indicators/definitions` - تعريفات المؤشرات
  - `GET /v1/indicators/field/{id}` - مؤشرات حقل
  - `GET /v1/dashboard` - لوحة التحكم
  - `GET /healthz` - فحص الصحة

### 3. Weather Advanced - خدمة الطقس المتقدمة
- **المنفذ:** 8092
- **المسار:** `kernel-services-v15.3/weather-advanced`
- **الوصف:** التنبؤ بالطقس الزراعي والتنبيهات
- **Endpoints:**
  - `GET /v1/current` - الطقس الحالي
  - `GET /v1/forecast` - التوقعات
  - `GET /v1/alerts` - التنبيهات
  - `GET /v1/agricultural-calendar` - التقويم الزراعي
  - `GET /healthz` - فحص الصحة

### 4. Fertilizer Advisor - مستشار التسميد
- **المنفذ:** 8093
- **المسار:** `kernel-services-v15.3/fertilizer-advisor`
- **الوصف:** توصيات التسميد الذكية
- **Endpoints:**
  - `GET /v1/crops` - المحاصيل المدعومة
  - `GET /v1/fertilizers` - أنواع الأسمدة
  - `POST /v1/recommend` - الحصول على توصية
  - `POST /v1/soil/interpret` - تفسير تحليل التربة
  - `GET /healthz` - فحص الصحة

### 5. Irrigation Smart - الري الذكي
- **المنفذ:** 8094
- **المسار:** `kernel-services-v15.3/irrigation-smart`
- **الوصف:** جدولة الري الذكية باستخدام FAO-56 Penman-Monteith
- **Endpoints:**
  - `GET /v1/crops` - المحاصيل المدعومة
  - `GET /v1/methods` - طرق الري
  - `POST /v1/calculate` - حساب احتياجات الري
  - `GET /v1/water-balance/{id}` - الميزان المائي
  - `POST /v1/sensor-reading` - قراءة المستشعر
  - `GET /v1/efficiency-report/{id}` - تقرير الكفاءة
  - `GET /healthz` - فحص الصحة

### 6. Crop Health AI - سهول فيجن
- **المنفذ:** 8095
- **المسار:** `kernel-services-v15.3/crop-health-ai`
- **الوصف:** الذكاء الاصطناعي للكشف عن أمراض النباتات
- **Endpoints:**
  - `POST /v1/diagnose` - تشخيص صورة
  - `POST /v1/diagnose/batch` - تشخيص دفعة
  - `GET /v1/crops` - المحاصيل المدعومة
  - `GET /v1/diseases` - قائمة الأمراض
  - `GET /v1/treatment/{id}` - تفاصيل العلاج
  - `GET /healthz` - فحص الصحة

### 7. Virtual Sensors - المستشعرات الافتراضية
- **المنفذ:** 8096
- **المسار:** `kernel-services-v15.3/virtual-sensors`
- **الوصف:** محرك حساب ET0 وETc بدون أجهزة استشعار
- **Endpoints:**
  - `POST /v1/et0/calculate` - حساب ET0
  - `GET /v1/crops` - المحاصيل ومعاملات Kc
  - `POST /v1/etc/calculate` - حساب ETc
  - `GET /v1/soils` - أنواع التربة
  - `POST /v1/soil-moisture/estimate` - تقدير رطوبة التربة
  - `POST /v1/irrigation/recommend` - توصية الري
  - `GET /healthz` - فحص الصحة

### 8. Community Chat - الدردشة المجتمعية
- **المنفذ:** 8097
- **المسار:** `kernel-services-v15.3/community-chat`
- **الوصف:** خدمة الدردشة في الوقت الفعلي مع الخبراء
- **التقنية:** Node.js + Socket.io
- **Endpoints:**
  - `GET /v1/requests` - طلبات الدردشة
  - `GET /v1/rooms/{id}/messages` - رسائل الغرفة
  - `GET /v1/experts/online` - الخبراء المتاحين
  - `GET /v1/stats` - إحصائيات
  - `GET /healthz` - فحص الصحة

### 9. Yield Engine - محرك الإنتاجية
- **المنفذ:** 8098
- **المسار:** `kernel-services-v15.3/yield-engine`
- **الوصف:** التنبؤ بإنتاجية المحاصيل بالذكاء الاصطناعي
- **Endpoints:**
  - `GET /v1/crops` - المحاصيل المدعومة
  - `POST /v1/predict` - التنبؤ بالإنتاجية
  - `GET /v1/factors` - عوامل التأثير
  - `GET /v1/historical/{crop}` - البيانات التاريخية
  - `GET /healthz` - فحص الصحة

---

## لوحة تحكم المشرفين | Admin Dashboard

- **المنفذ:** 3001
- **التقنية:** Next.js 14 + TypeScript + Tailwind CSS
- **المسار:** `web_admin/`

### الصفحات المتاحة:
| المسار | الوصف |
|--------|-------|
| `/dashboard` | لوحة التحكم الرئيسية |
| `/farms` | إدارة المزارع |
| `/epidemic` | مركز رصد الأوبئة |
| `/diseases` | إدارة الأمراض |
| `/yield` | حاسبة الإنتاجية |
| `/irrigation` | الري الذكي |
| `/sensors` | المستشعرات الافتراضية |
| `/alerts` | الطقس والتنبيهات |
| `/support` | الدعم الفني |
| `/settings` | الإعدادات |

---

## تطبيق Flutter المحمول | Mobile Flutter App

- **المسار:** `mobile/sahool_field_app/`
- **التقنية:** Flutter + Riverpod + Freezed

### الميزات:
- تشخيص أمراض النباتات بالكاميرا
- عرض خرائط الحقول مع NDVI
- جدولة الري الذكية
- توصيات التسميد
- التنبيهات الزراعية
- الدردشة مع الخبراء
- العمل بدون إنترنت (Offline-first)

---

## التشغيل | Running the Platform

### المتطلبات:
- Docker & Docker Compose
- Node.js 18+ (للتطوير)
- Python 3.11+ (للتطوير)

### بدء التشغيل:
```bash
# إنشاء ملف .env من المثال
cp .env.example .env

# تشغيل جميع الخدمات
docker-compose up -d

# عرض حالة الخدمات
docker-compose ps

# عرض logs
docker-compose logs -f [service_name]
```

### فحص صحة الخدمات:
```bash
# فحص جميع الخدمات
curl http://localhost:8095/healthz  # crop_health_ai
curl http://localhost:8096/healthz  # virtual_sensors
curl http://localhost:8097/healthz  # community_chat
curl http://localhost:8098/healthz  # yield_engine
curl http://localhost:8094/healthz  # irrigation_smart
curl http://localhost:8093/healthz  # fertilizer_advisor
curl http://localhost:8091/healthz  # indicators_service
curl http://localhost:8090/healthz  # satellite_service
curl http://localhost:8092/healthz  # weather_advanced
```

---

## خريطة المنافذ | Port Map

```
┌─────────────────────────────────────────────────────────────┐
│                    SAHOOL v15.3 Port Map                    │
├─────────────────────────────────────────────────────────────┤
│ Infrastructure                                              │
│   5432  │ PostgreSQL (PostGIS)                              │
│   4222  │ NATS                                              │
│   6379  │ Redis                                             │
│   1883  │ MQTT                                              │
│   8000  │ Kong Gateway                                      │
├─────────────────────────────────────────────────────────────┤
│ Legacy Kernel                                               │
│   3000  │ Field Core                                        │
│   8080  │ Field Ops                                         │
│   8089  │ WebSocket Gateway                                 │
│   8100  │ Crop Health (legacy)                              │
│   8101  │ Equipment Service                                 │
│   8102  │ Community Service                                 │
│   8103  │ Task Service                                      │
│   8104  │ Provider Config                                   │
│   8105  │ Agro Advisor                                      │
│   8106  │ IoT Gateway                                       │
│   8107  │ NDVI Engine                                       │
│   8108  │ Weather Core                                      │
├─────────────────────────────────────────────────────────────┤
│ New v15.3 Services                                          │
│   8090  │ Satellite Service    (NDVI/Imagery)               │
│   8091  │ Indicators Service   (KPIs/Analytics)             │
│   8092  │ Weather Advanced     (Forecasting)                │
│   8093  │ Fertilizer Advisor   (Smart Fertilization)        │
│   8094  │ Irrigation Smart     (FAO-56)                     │
│   8095  │ Crop Health AI       (Disease Detection)          │
│   8096  │ Virtual Sensors      (ET0/ETc)                    │
│   8097  │ Community Chat       (Socket.io)                  │
│   8098  │ Yield Engine         (ML Prediction)              │
├─────────────────────────────────────────────────────────────┤
│ Frontend                                                    │
│   3001  │ Admin Dashboard (Next.js)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## المحافظات المدعومة | Supported Governorates

اليمن - 22 محافظة:
- صنعاء (Sanaa)
- عدن (Aden)
- تعز (Taiz)
- الحديدة (Hodeidah)
- إب (Ibb)
- ذمار (Dhamar)
- حضرموت (Hadramaut)
- البيضاء (Al-Bayda)
- لحج (Lahj)
- أبين (Abyan)
- شبوة (Shabwa)
- المهرة (Al-Mahrah)
- صعدة (Saada)
- حجة (Hajjah)
- المحويت (Al-Mahwit)
- عمران (Amran)
- الجوف (Al-Jawf)
- مأرب (Marib)
- ريمة (Raymah)
- الضالع (Al-Dhale'e)
- سقطرى (Socotra)
- أمانة العاصمة (Amanat Al-Asimah)

---

## المحاصيل المدعومة | Supported Crops

| المحصول | الاسم الإنجليزي |
|---------|----------------|
| طماطم | Tomato |
| قمح | Wheat |
| بن | Coffee |
| قات | Qat |
| موز | Banana |
| خيار | Cucumber |
| فلفل | Pepper |
| بطاطس | Potato |
| ذرة | Corn |
| عنب | Grapes |
| نخيل | Date Palm |
| مانجو | Mango |
| بصل | Onion |
| ثوم | Garlic |
| برسيم | Alfalfa |

---

## الترخيص | License

© 2024 SAHOOL Agricultural Platform - جميع الحقوق محفوظة

---

## التواصل | Contact

- الموقع: https://sahool.io
- البريد: support@sahool.io
