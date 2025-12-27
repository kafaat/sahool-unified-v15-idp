# SAHOOL Platform Deployment Packages | حزم نشر منصة سهول

<div dir="rtl">

## نظرة عامة

تقدم منصة سهول ثلاث حزم نشر رئيسية مصممة لتلبية احتياجات المزارعين والمؤسسات الزراعية على مختلف المستويات. كل حزمة مبنية على سابقتها، مما يوفر قابلية التوسع والمرونة.

</div>

---

## Overview

SAHOOL platform offers three main deployment packages designed to meet the needs of farmers and agricultural organizations at different scales. Each package builds upon the previous one, providing scalability and flexibility.

---

<div dir="rtl">

## 📦 الحزم المتاحة

### 🌱 حزمة المبتدئين (Starter Package)

**مناسبة لـ:** المزارعين الصغار والمزارع العائلية (1-50 هكتار)

**الخدمات المتضمنة:**
- **البنية التحتية:**
  - PostgreSQL/PostGIS - قاعدة بيانات جغرافية مكانية
  - Redis - ذاكرة تخزين مؤقت وجلسات
  - NATS - طابور الرسائل

- **الخدمات الأساسية:**
  - `field_core` - إدارة الحقول الجغرافية والمحاصيل
  - `weather_core` - بيانات الطقس والتنبؤات
  - `astronomical_calendar` - التقويم الفلكي الزراعي اليمني
  - `agro_advisor` - المستشار الزراعي الذكي
  - `notification_service` - خدمة الإشعارات والتنبيهات

**حدود الموارد:**
- CPU: 0.25-1.0 نواة لكل خدمة
- Memory: 128MB-512MB لكل خدمة
- PostgreSQL: 512MB RAM
- Redis: 256MB RAM

**الميزات الرئيسية:**
✅ إدارة الحقول والمحاصيل
✅ توقعات الطقس المحلية
✅ التقويم الزراعي اليمني
✅ نصائح زراعية أساسية
✅ تنبيهات وإشعارات

**السعر المتوقع:** مجاني أو اشتراك شهري بسيط

---

### 🚜 الحزمة الاحترافية (Professional Package)

**مناسبة لـ:** المزارع التجارية والتعاونيات الزراعية (50-500 هكتار)

**تشمل جميع خدمات حزمة المبتدئين بالإضافة إلى:**

- **الاستشعار عن بعد:**
  - `satellite_service` - صور الأقمار الصناعية (Sentinel, NASA)
  - `ndvi_engine` - تحليل NDVI وصحة المحاصيل

- **الذكاء الاصطناعي:**
  - `crop_health_ai` - كشف الأمراض النباتية بالذكاء الاصطناعي
  - `virtual_sensors` - المستشعرات الافتراضية (FAO-56 ET0)

- **الزراعة الذكية:**
  - `irrigation_smart` - إدارة الري الذكي
  - `fertilizer_advisor` - مستشار التسميد
  - `yield_engine` - التنبؤ بالإنتاجية
  - `inventory_service` - إدارة المخزون

**حدود الموارد:**
- CPU: 0.5-2.0 نواة لكل خدمة
- Memory: 512MB-2GB لكل خدمة
- PostgreSQL: 2GB RAM
- Redis: 512MB RAM

**الميزات الإضافية:**
✅ صور الأقمار الصناعية وتحليل NDVI
✅ كشف الأمراض بالذكاء الاصطناعي
✅ توصيات الري المحسّنة
✅ توصيات التسميد الدقيق
✅ التنبؤ بالإنتاجية
✅ إدارة المخزون والمدخلات

**السعر المتوقع:** اشتراك شهري متوسط

---

### 🏢 حزمة المؤسسات (Enterprise Package)

**مناسبة لـ:** المؤسسات الزراعية الكبرى والشركات (500+ هكتار)

**تشمل جميع خدمات الحزمة الاحترافية بالإضافة إلى:**

- **الذكاء الاصطناعي المتقدم:**
  - `ai_advisor` - مستشار ذكي متعدد الوكلاء مع RAG
  - `qdrant` - قاعدة بيانات متجهة للبحث الدلالي

- **إنترنت الأشياء:**
  - `iot_gateway` - بوابة إنترنت الأشياء الزراعية
  - `mqtt` - وسيط رسائل MQTT

- **البحث العلمي:**
  - `research_core` - إدارة التجارب والأبحاث الزراعية
  - `crop_growth_model` - نماذج نمو المحاصيل (WOFOST, DSSAT)
  - `lai_estimation` - تقدير مؤشر مساحة الأوراق
  - `disaster_assessment` - تقييم الكوارث الزراعية

- **الأعمال:**
  - `marketplace_service` - سوق سهول للمنتجات
  - `billing_core` - نظام الفوترة والمدفوعات

- **المراقبة والأداء:**
  - `prometheus` - جمع المقاييس
  - `grafana` - لوحات المراقبة والتحليلات

**حدود الموارد:**
- CPU: 1.0-4.0 نواة لكل خدمة
- Memory: 1GB-4GB لكل خدمة
- PostgreSQL: 4GB RAM
- Redis: 1GB RAM

**الميزات المتقدمة:**
✅ مستشار ذكي متقدم مع فهم اللغة الطبيعية
✅ دعم أجهزة IoT والمستشعرات
✅ نماذج محاكاة نمو المحاصيل
✅ تقييم الكوارث والمخاطر
✅ سوق إلكتروني متكامل
✅ نظام فوترة ومدفوعات
✅ مراقبة شاملة للأداء
✅ دعم فني مخصص 24/7

**السعر المتوقع:** اشتراك سنوي مع خصومات مخصصة

</div>

---

## 📦 Available Packages

### 🌱 Starter Package

**Suitable for:** Small farmers and family farms (1-50 hectares)

**Included Services:**
- **Infrastructure:**
  - PostgreSQL/PostGIS - Spatial database
  - Redis - Cache and sessions
  - NATS - Message queue

- **Core Services:**
  - `field_core` - Geospatial field and crop management
  - `weather_core` - Weather data and forecasts
  - `astronomical_calendar` - Yemeni agricultural astronomical calendar
  - `agro_advisor` - Smart agricultural advisor
  - `notification_service` - Alerts and notifications

**Resource Limits:**
- CPU: 0.25-1.0 cores per service
- Memory: 128MB-512MB per service
- PostgreSQL: 512MB RAM
- Redis: 256MB RAM

**Key Features:**
✅ Field and crop management
✅ Local weather forecasts
✅ Yemeni agricultural calendar
✅ Basic farming advice
✅ Alerts and notifications

**Expected Price:** Free or basic monthly subscription

---

### 🚜 Professional Package

**Suitable for:** Commercial farms and agricultural cooperatives (50-500 hectares)

**Includes all Starter services plus:**

- **Remote Sensing:**
  - `satellite_service` - Satellite imagery (Sentinel, NASA)
  - `ndvi_engine` - NDVI analysis and crop health

- **AI Services:**
  - `crop_health_ai` - AI-powered plant disease detection
  - `virtual_sensors` - Virtual sensors (FAO-56 ET0)

- **Smart Agriculture:**
  - `irrigation_smart` - Smart irrigation management
  - `fertilizer_advisor` - Fertilization recommendations
  - `yield_engine` - Yield prediction
  - `inventory_service` - Inventory management

**Resource Limits:**
- CPU: 0.5-2.0 cores per service
- Memory: 512MB-2GB per service
- PostgreSQL: 2GB RAM
- Redis: 512MB RAM

**Additional Features:**
✅ Satellite imagery and NDVI analysis
✅ AI-powered disease detection
✅ Optimized irrigation recommendations
✅ Precision fertilization advice
✅ Yield prediction
✅ Input inventory management

**Expected Price:** Medium monthly subscription

---

### 🏢 Enterprise Package

**Suitable for:** Large agricultural enterprises and corporations (500+ hectares)

**Includes all Professional services plus:**

- **Advanced AI:**
  - `ai_advisor` - Multi-agent AI advisor with RAG
  - `qdrant` - Vector database for semantic search

- **IoT:**
  - `iot_gateway` - Agricultural IoT gateway
  - `mqtt` - MQTT message broker

- **Research:**
  - `research_core` - Agricultural research and trials management
  - `crop_growth_model` - Crop growth models (WOFOST, DSSAT)
  - `lai_estimation` - Leaf Area Index estimation
  - `disaster_assessment` - Agricultural disaster assessment

- **Business:**
  - `marketplace_service` - SAHOOL marketplace for products
  - `billing_core` - Billing and payment system

- **Monitoring:**
  - `prometheus` - Metrics collection
  - `grafana` - Monitoring dashboards and analytics

**Resource Limits:**
- CPU: 1.0-4.0 cores per service
- Memory: 1GB-4GB per service
- PostgreSQL: 4GB RAM
- Redis: 1GB RAM

**Advanced Features:**
✅ Advanced AI advisor with natural language understanding
✅ IoT device and sensor support
✅ Crop growth simulation models
✅ Disaster and risk assessment
✅ Integrated e-commerce marketplace
✅ Billing and payment system
✅ Comprehensive performance monitoring
✅ 24/7 dedicated support

**Expected Price:** Annual subscription with custom discounts

---

## 🚀 Quick Start | البدء السريع

<div dir="rtl">

### تشغيل حزمة معينة

</div>

### Running a specific package

```bash
# Starter Package | حزمة المبتدئين
cd packages/starter
cp ../.env.example .env
# Edit .env with your configuration
docker-compose up -d

# Professional Package | الحزمة الاحترافية
cd packages/professional
cp ../.env.example .env
# Edit .env with your configuration
docker-compose up -d

# Enterprise Package | حزمة المؤسسات
cd packages/enterprise
cp ../.env.example .env
# Edit .env with your configuration
docker-compose up -d
```

---

## 📊 Comparison Table | جدول المقارنة

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| **Basic Services** | ✅ | ✅ | ✅ |
| **Weather Forecasts** | ✅ | ✅ | ✅ |
| **Agricultural Calendar** | ✅ | ✅ | ✅ |
| **Satellite Imagery** | ❌ | ✅ | ✅ |
| **NDVI Analysis** | ❌ | ✅ | ✅ |
| **AI Disease Detection** | ❌ | ✅ | ✅ |
| **Smart Irrigation** | ❌ | ✅ | ✅ |
| **Yield Prediction** | ❌ | ✅ | ✅ |
| **Advanced AI Advisor** | ❌ | ❌ | ✅ |
| **IoT Integration** | ❌ | ❌ | ✅ |
| **Research Tools** | ❌ | ❌ | ✅ |
| **Marketplace** | ❌ | ❌ | ✅ |
| **Monitoring Stack** | ❌ | ❌ | ✅ |
| **Max Fields** | 10 | 100 | Unlimited |
| **API Calls/hour** | 500 | 2,000 | 50,000 |
| **Support** | Community | Email | 24/7 Dedicated |

---

## 🔧 Configuration | الإعدادات

<div dir="rtl">

### المتغيرات البيئية المطلوبة

راجع ملف `.env.example` في دليل `packages/` للحصول على قائمة كاملة بالمتغيرات البيئية المطلوبة.

**متغيرات إلزامية لجميع الحزم:**
- `POSTGRES_USER` و `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `JWT_SECRET_KEY`

**متغيرات إضافية للحزمة الاحترافية:**
- `SENTINEL_HUB_CLIENT_ID` و `SENTINEL_HUB_CLIENT_SECRET` (اختياري)
- `NASA_EARTHDATA_USERNAME` و `NASA_EARTHDATA_PASSWORD` (اختياري)

**متغيرات إضافية لحزمة المؤسسات:**
- `ANTHROPIC_API_KEY` أو `OPENAI_API_KEY` (للمستشار الذكي)
- `MQTT_PASSWORD` (لإنترنت الأشياء)
- `GRAFANA_ADMIN_PASSWORD` (للمراقبة)

</div>

### Required Environment Variables

See `.env.example` file in `packages/` directory for a complete list of required environment variables.

**Required for all packages:**
- `POSTGRES_USER` and `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `JWT_SECRET_KEY`

**Additional for Professional:**
- `SENTINEL_HUB_CLIENT_ID` and `SENTINEL_HUB_CLIENT_SECRET` (optional)
- `NASA_EARTHDATA_USERNAME` and `NASA_EARTHDATA_PASSWORD` (optional)

**Additional for Enterprise:**
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (for AI advisor)
- `MQTT_PASSWORD` (for IoT)
- `GRAFANA_ADMIN_PASSWORD` (for monitoring)

---

## 📚 Documentation | التوثيق

<div dir="rtl">

لمزيد من المعلومات، راجع:
- [دليل التثبيت](../docs/installation.md)
- [دليل الإعدادات](../docs/configuration.md)
- [مرجع API](../docs/api-reference.md)
- [دليل استكشاف الأخطاء](../docs/troubleshooting.md)

</div>

For more information, see:
- [Installation Guide](../docs/installation.md)
- [Configuration Guide](../docs/configuration.md)
- [API Reference](../docs/api-reference.md)
- [Troubleshooting Guide](../docs/troubleshooting.md)

---

## 📞 Support | الدعم

<div dir="rtl">

- **المجتمع:** [GitHub Discussions](https://github.com/sahool/sahool-platform/discussions)
- **البريد الإلكتروني:** support@sahool.com
- **الموقع:** https://sahool.com

</div>

- **Community:** [GitHub Discussions](https://github.com/sahool/sahool-platform/discussions)
- **Email:** support@sahool.com
- **Website:** https://sahool.com

---

## 📄 License | الترخيص

Copyright © 2025 SAHOOL Platform. All rights reserved.
