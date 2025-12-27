# SAHOOL Platform - API Documentation

## واجهات برمجة منصة سهول - دليل التوثيق

> Unified OpenAPI documentation for all 39 microservices across Starter, Professional, and Enterprise packages.

> توثيق موحد لواجهات OpenAPI لجميع الخدمات الـ 39 عبر باقات المبتدئة والاحترافية والمؤسسية.

---

## 📋 Table of Contents - جدول المحتويات

- [English Documentation](#english-documentation)
  - [Quick Start](#quick-start)
  - [Architecture Overview](#architecture-overview)
  - [Usage Guide](#usage-guide)
  - [API Reference](#api-reference)
  - [Development](#development)
  - [Troubleshooting](#troubleshooting)

- [التوثيق العربي](#التوثيق-العربي)
  - [البدء السريع](#البدء-السريع)
  - [نظرة عامة على البنية](#نظرة-عامة-على-البنية)
  - [دليل الاستخدام](#دليل-الاستخدام)
  - [مرجع واجهات البرمجة](#مرجع-واجهات-البرمجة)
  - [التطوير](#التطوير)
  - [حل المشاكل](#حل-المشاكل)

---

# English Documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (for the aggregator script)
- Docker & Docker Compose (for the documentation server)
- Running SAHOOL services (at least one package tier)

### Step 1: Generate Unified API Spec

Run the aggregator script to fetch OpenAPI specs from all running services:

```bash
# Navigate to the docs/api directory
cd /home/user/sahool-unified-v15-idp/docs/api

# Install Python dependencies
pip install requests pyyaml

# Run the aggregator
python openapi-aggregator.py
```

This will create:
- `openapi-unified.yaml` - YAML format specification
- `openapi-unified.json` - JSON format specification

### Step 2: Start Documentation Server

```bash
# Start the documentation server
docker-compose -f docker-compose.docs.yml up -d

# Check if it's running
docker-compose -f docker-compose.docs.yml ps

# View logs
docker-compose -f docker-compose.docs.yml logs -f api-docs
```

### Step 3: Access Documentation

Open your browser and navigate to:
- **Local**: http://localhost:8888
- **Network**: http://YOUR_SERVER_IP:8888

---

## 🏗️ Architecture Overview

### Service Organization

The SAHOOL platform consists of **39 microservices** organized into **3 package tiers**:

#### 🌱 Starter Package (5 services)
Essential services for small farms:
- **field_core** (Port 3000) - Field management and boundaries
- **weather_core** (Port 8108) - Weather data and forecasts
- **astronomical_calendar** (Port 8111) - Yemeni agricultural calendar
- **agro_advisor** (Port 8105) - Basic agricultural advisory
- **notification_service** (Port 8110) - Email/SMS notifications

#### 🚜 Professional Package (13 services)
Includes all Starter services plus:
- **satellite_service** (Port 8090) - Satellite imagery integration
- **ndvi_engine** (Port 8107) - Vegetation index analysis
- **crop_health_ai** (Port 8095) - AI-powered disease detection
- **irrigation_smart** (Port 8094) - Smart irrigation scheduling
- **virtual_sensors** (Port 8096) - ML-based sensor predictions
- **yield_engine** (Port 8098) - Yield forecasting
- **fertilizer_advisor** (Port 8093) - NPK recommendations
- **inventory_service** (Port 8113) - Inventory management
- Plus: crop_health, field_ops, task_service, equipment_service, field_chat, indicators_service

#### 🏢 Enterprise Package (21 services)
Complete platform including all Professional services plus:
- **ai_advisor** (Port 8112) - Multi-agent AI with RAG
- **iot_gateway** (Port 8106) - IoT device integration
- **research_core** (Port 3015) - Research and trials management
- **marketplace_service** (Port 3010) - Agricultural marketplace
- **billing_core** (Port 8089) - Subscription and billing
- **disaster_assessment** (Port 3020) - Disaster impact evaluation
- **crop_growth_model** (Port 3023) - WOFOST-based crop simulation
- **lai_estimation** (Port 3022) - Leaf Area Index calculation
- Plus: weather_advanced, provider_config, ws_gateway, community_chat, iot_service, field_service, alert_service, ndvi_processor, yield_prediction, agro_rules, chat_service

### Technology Stack

- **Python Services**: FastAPI framework, OpenAPI at `/openapi.json`
- **NestJS Services**: NestJS framework, OpenAPI at `/api-json`
- **Documentation**: Swagger UI & ReDoc
- **Server**: Nginx (Alpine)
- **Aggregation**: Python script with requests & PyYAML

---

## 📖 Usage Guide

### Viewing API Documentation

The documentation interface provides two viewing modes:

1. **Swagger UI** (Default)
   - Interactive API explorer
   - Try out endpoints directly
   - Request/response examples

2. **ReDoc**
   - Clean, three-panel layout
   - Better for reading and printing
   - Comprehensive overview

Toggle between viewers using the buttons in the header.

### Filtering by Package Tier

Use the tab navigation to view services by package:
- **All Services**: Complete unified documentation
- **Starter**: Only starter package services
- **Professional**: Only professional package services
- **Enterprise**: Only enterprise package services

### Language Support

Click the language toggle (🌐) to switch between:
- **English** (LTR) - Default
- **العربية** (RTL) - Arabic with right-to-left layout

### Downloading Specifications

Download the unified spec in your preferred format:
- **YAML**: Click "Download YAML" button
- **JSON**: Click "Download JSON" button

---

## 🔌 API Reference

### Authentication

Most endpoints require JWT authentication. Include the token in requests:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:3000/api/v1/fields
```

### Base URLs by Service Type

#### Starter Services
```
http://localhost:3000  - field_core (NestJS)
http://localhost:8108  - weather_core (Python)
http://localhost:8111  - astronomical_calendar (Python)
http://localhost:8105  - agro_advisor (Python)
http://localhost:8110  - notification_service (Python)
```

#### Professional Services
```
http://localhost:8090  - satellite_service (Python)
http://localhost:8107  - ndvi_engine (Python)
http://localhost:8095  - crop_health_ai (Python)
http://localhost:8094  - irrigation_smart (Python)
http://localhost:8096  - virtual_sensors (Python)
http://localhost:8098  - yield_engine (Python)
http://localhost:8093  - fertilizer_advisor (Python)
http://localhost:8113  - inventory_service (Python)
```

#### Enterprise Services
```
http://localhost:8112  - ai_advisor (Python)
http://localhost:8106  - iot_gateway (Python)
http://localhost:3015  - research_core (NestJS)
http://localhost:3010  - marketplace_service (NestJS)
http://localhost:8089  - billing_core (Python)
http://localhost:3020  - disaster_assessment (NestJS)
http://localhost:3023  - crop_growth_model (NestJS)
http://localhost:3022  - lai_estimation (NestJS)
```

### Common Response Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## 💻 Development

### Regenerating Documentation

After service changes, regenerate the unified spec:

```bash
# Stop any running services you want to exclude
# Then run the aggregator
python openapi-aggregator.py

# The script will:
# 1. Fetch specs from all running services
# 2. Merge them into a unified document
# 3. Save as openapi-unified.yaml and .json
# 4. Show a summary of successes/failures
```

### Adding New Services

1. Add service configuration to `openapi-aggregator.py`:

```python
ServiceConfig(
    name="my_new_service",
    port=8200,
    tier="professional",  # or "starter" or "enterprise"
    type="python",  # or "nestjs"
    description_en="English description",
    description_ar="الوصف بالعربية"
)
```

2. Ensure the service exposes OpenAPI spec at:
   - Python/FastAPI: `http://localhost:PORT/openapi.json`
   - NestJS: `http://localhost:PORT/api-json`

3. Regenerate the unified spec:
```bash
python openapi-aggregator.py
```

### Customizing the UI

Edit `index.html` to customize:
- Colors and themes (CSS variables in `:root`)
- Header content
- Package descriptions
- Feature lists

### Auto-refresh Mode

To enable automatic spec regeneration, uncomment the `api-aggregator` service in `docker-compose.docs.yml`:

```yaml
  api-aggregator:
    image: python:3.11-slim
    # ... (see file for full config)
```

This will regenerate the spec every 5 minutes.

---

## 🔧 Troubleshooting

### Issue: "Failed to fetch any OpenAPI specs"

**Cause**: Services are not running or not accessible.

**Solution**:
```bash
# Check which services are running
docker ps

# Start the desired package tier
cd packages/starter  # or professional, enterprise
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Then regenerate docs
cd ../../docs/api
python openapi-aggregator.py
```

### Issue: "Connection refused for service_name"

**Cause**: Specific service is down or port is incorrect.

**Solution**:
1. Check service status:
   ```bash
   docker-compose -f packages/starter/docker-compose.yml ps
   ```

2. Check service logs:
   ```bash
   docker logs sahool-starter-service-name
   ```

3. Verify port mapping in docker-compose file

### Issue: "Documentation page is blank"

**Cause**: YAML/JSON spec file missing or malformed.

**Solution**:
```bash
# Check if files exist
ls -lh openapi-unified.*

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('openapi-unified.yaml'))"

# Regenerate if needed
python openapi-aggregator.py
```

### Issue: "CORS errors in browser console"

**Cause**: Browser blocking requests due to CORS policy.

**Solution**:
The nginx configuration includes CORS headers. If issues persist:
1. Clear browser cache
2. Try a different browser
3. Check nginx.conf is properly mounted

### Issue: "Services show in docs but endpoints fail"

**Cause**: Services may have changed ports or be in different Docker network.

**Solution**:
1. Verify service is accessible:
   ```bash
   curl http://localhost:PORT/healthz
   ```

2. Check Docker networks:
   ```bash
   docker network ls
   docker network inspect sahool-starter-network
   ```

3. Ensure services expose ports correctly in docker-compose

---

## 📚 Additional Resources

- **Main Documentation**: See `/docs` directory
- **Service README**: Each service has its own README
- **OpenAPI Specification**: https://swagger.io/specification/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **NestJS Docs**: https://docs.nestjs.com/

---

# التوثيق العربي

## 🚀 البدء السريع

### المتطلبات الأساسية

- Python 3.8+ (لسكريبت التجميع)
- Docker & Docker Compose (لخادم التوثيق)
- خدمات سهول قيد التشغيل (على الأقل باقة واحدة)

### الخطوة 1: توليد مواصفات API الموحدة

قم بتشغيل سكريبت التجميع لجلب مواصفات OpenAPI من جميع الخدمات:

```bash
# انتقل إلى مجلد التوثيق
cd /home/user/sahool-unified-v15-idp/docs/api

# تثبيت مكتبات Python
pip install requests pyyaml

# تشغيل سكريبت التجميع
python openapi-aggregator.py
```

سيتم إنشاء:
- `openapi-unified.yaml` - المواصفات بصيغة YAML
- `openapi-unified.json` - المواصفات بصيغة JSON

### الخطوة 2: تشغيل خادم التوثيق

```bash
# تشغيل خادم التوثيق
docker-compose -f docker-compose.docs.yml up -d

# التحقق من التشغيل
docker-compose -f docker-compose.docs.yml ps

# عرض السجلات
docker-compose -f docker-compose.docs.yml logs -f api-docs
```

### الخطوة 3: الوصول إلى التوثيق

افتح المتصفح وانتقل إلى:
- **محلي**: http://localhost:8888
- **الشبكة**: http://عنوان_الخادم:8888

---

## 🏗️ نظرة عامة على البنية

### تنظيم الخدمات

تتكون منصة سهول من **39 خدمة دقيقة** منظمة في **3 مستويات للباقات**:

#### 🌱 الباقة المبتدئة (5 خدمات)
خدمات أساسية للمزارع الصغيرة:
- **field_core** (المنفذ 3000) - إدارة الحقول والحدود
- **weather_core** (المنفذ 8108) - بيانات الطقس والتنبؤات
- **astronomical_calendar** (المنفذ 8111) - التقويم الزراعي اليمني
- **agro_advisor** (المنفذ 8105) - الإرشاد الزراعي الأساسي
- **notification_service** (المنفذ 8110) - إشعارات البريد والرسائل

#### 🚜 الباقة الاحترافية (13 خدمة)
تشمل جميع خدمات الباقة المبتدئة بالإضافة إلى:
- **satellite_service** (المنفذ 8090) - تكامل صور الأقمار الصناعية
- **ndvi_engine** (المنفذ 8107) - تحليل مؤشر الغطاء النباتي
- **crop_health_ai** (المنفذ 8095) - كشف الأمراض بالذكاء الاصطناعي
- **irrigation_smart** (المنفذ 8094) - جدولة الري الذكي
- **virtual_sensors** (المنفذ 8096) - التنبؤ بالمستشعرات
- **yield_engine** (المنفذ 8098) - التنبؤ بالإنتاجية
- **fertilizer_advisor** (المنفذ 8093) - توصيات التسميد
- **inventory_service** (المنفذ 8113) - إدارة المخزون
- بالإضافة إلى: crop_health, field_ops, task_service, equipment_service, field_chat, indicators_service

#### 🏢 الباقة المؤسسية (21 خدمة)
المنصة الكاملة تشمل جميع خدمات الباقة الاحترافية بالإضافة إلى:
- **ai_advisor** (المنفذ 8112) - الذكاء الاصطناعي متعدد الوكلاء
- **iot_gateway** (المنفذ 8106) - تكامل أجهزة IoT
- **research_core** (المنفذ 3015) - إدارة البحوث والتجارب
- **marketplace_service** (المنفذ 3010) - السوق الزراعي
- **billing_core** (المنفذ 8089) - نظام الفوترة
- **disaster_assessment** (المنفذ 3020) - تقييم تأثير الكوارث
- **crop_growth_model** (المنفذ 3023) - محاكاة نمو المحاصيل
- **lai_estimation** (المنفذ 3022) - حساب مؤشر مساحة الأوراق
- بالإضافة إلى: weather_advanced, provider_config, ws_gateway, community_chat, iot_service, field_service, alert_service, ndvi_processor, yield_prediction, agro_rules, chat_service

---

## 📖 دليل الاستخدام

### عرض توثيق API

توفر واجهة التوثيق وضعين للعرض:

1. **Swagger UI** (افتراضي)
   - مستكشف API تفاعلي
   - تجربة نقاط النهاية مباشرة
   - أمثلة الطلبات والاستجابات

2. **ReDoc**
   - تخطيط نظيف بثلاث لوحات
   - أفضل للقراءة والطباعة
   - نظرة شاملة

التبديل بين العارضين باستخدام الأزرار في الرأس.

### الترشيح حسب مستوى الباقة

استخدم علامات التبويب لعرض الخدمات حسب الباقة:
- **جميع الخدمات**: التوثيق الموحد الكامل
- **المبتدئة**: خدمات الباقة المبتدئة فقط
- **الاحترافية**: خدمات الباقة الاحترافية فقط
- **المؤسسية**: خدمات الباقة المؤسسية فقط

### دعم اللغة

انقر على زر اللغة (🌐) للتبديل بين:
- **English** (من اليسار لليمين) - افتراضي
- **العربية** (من اليمين لليسار)

### تحميل المواصفات

تحميل المواصفات الموحدة بالصيغة المفضلة:
- **YAML**: انقر على زر "Download YAML"
- **JSON**: انقر على زر "Download JSON"

---

## 🔌 مرجع واجهات البرمجة

### المصادقة

معظم نقاط النهاية تتطلب مصادقة JWT. قم بتضمين الرمز في الطلبات:

```bash
curl -H "Authorization: Bearer رمز_JWT_الخاص_بك" \
  http://localhost:3000/api/v1/fields
```

### عناوين URL الأساسية حسب نوع الخدمة

#### خدمات الباقة المبتدئة
```
http://localhost:3000  - field_core (NestJS)
http://localhost:8108  - weather_core (Python)
http://localhost:8111  - astronomical_calendar (Python)
http://localhost:8105  - agro_advisor (Python)
http://localhost:8110  - notification_service (Python)
```

#### خدمات الباقة الاحترافية
```
http://localhost:8090  - satellite_service (Python)
http://localhost:8107  - ndvi_engine (Python)
http://localhost:8095  - crop_health_ai (Python)
http://localhost:8094  - irrigation_smart (Python)
http://localhost:8096  - virtual_sensors (Python)
http://localhost:8098  - yield_engine (Python)
http://localhost:8093  - fertilizer_advisor (Python)
http://localhost:8113  - inventory_service (Python)
```

#### خدمات الباقة المؤسسية
```
http://localhost:8112  - ai_advisor (Python)
http://localhost:8106  - iot_gateway (Python)
http://localhost:3015  - research_core (NestJS)
http://localhost:3010  - marketplace_service (NestJS)
http://localhost:8089  - billing_core (Python)
http://localhost:3020  - disaster_assessment (NestJS)
http://localhost:3023  - crop_growth_model (NestJS)
http://localhost:3022  - lai_estimation (NestJS)
```

### رموز الاستجابة الشائعة

- `200 OK` - طلب ناجح
- `201 Created` - تم إنشاء المورد بنجاح
- `400 Bad Request` - معاملات طلب غير صالحة
- `401 Unauthorized` - مصادقة مفقودة أو غير صالحة
- `403 Forbidden` - صلاحيات غير كافية
- `404 Not Found` - المورد غير موجود
- `422 Unprocessable Entity` - خطأ في التحقق من الصحة
- `500 Internal Server Error` - خطأ في الخادم

---

## 💻 التطوير

### إعادة توليد التوثيق

بعد تغييرات الخدمة، أعد توليد المواصفات الموحدة:

```bash
# أوقف أي خدمات تريد استبعادها
# ثم قم بتشغيل سكريبت التجميع
python openapi-aggregator.py

# سيقوم السكريبت بـ:
# 1. جلب المواصفات من جميع الخدمات قيد التشغيل
# 2. دمجها في وثيقة موحدة
# 3. الحفظ بصيغة YAML و JSON
# 4. عرض ملخص للنجاحات/الإخفاقات
```

### إضافة خدمات جديدة

1. أضف تكوين الخدمة إلى `openapi-aggregator.py`:

```python
ServiceConfig(
    name="my_new_service",
    port=8200,
    tier="professional",  # أو "starter" أو "enterprise"
    type="python",  # أو "nestjs"
    description_en="English description",
    description_ar="الوصف بالعربية"
)
```

2. تأكد من أن الخدمة تعرض مواصفات OpenAPI في:
   - Python/FastAPI: `http://localhost:PORT/openapi.json`
   - NestJS: `http://localhost:PORT/api-json`

3. أعد توليد المواصفات الموحدة:
```bash
python openapi-aggregator.py
```

---

## 🔧 حل المشاكل

### المشكلة: "فشل جلب أي مواصفات OpenAPI"

**السبب**: الخدمات غير قيد التشغيل أو غير قابلة للوصول.

**الحل**:
```bash
# تحقق من الخدمات قيد التشغيل
docker ps

# ابدأ مستوى الباقة المطلوب
cd packages/starter  # أو professional أو enterprise
docker-compose up -d

# انتظر حتى تصبح الخدمات جاهزة
docker-compose ps

# ثم أعد توليد التوثيق
cd ../../docs/api
python openapi-aggregator.py
```

### المشكلة: "رفض الاتصال للخدمة"

**السبب**: خدمة معينة متوقفة أو المنفذ غير صحيح.

**الحل**:
1. تحقق من حالة الخدمة:
   ```bash
   docker-compose -f packages/starter/docker-compose.yml ps
   ```

2. تحقق من سجلات الخدمة:
   ```bash
   docker logs sahool-starter-service-name
   ```

3. تحقق من تعيين المنفذ في ملف docker-compose

### المشكلة: "صفحة التوثيق فارغة"

**السبب**: ملف YAML/JSON المواصفات مفقود أو تالف.

**الحل**:
```bash
# تحقق من وجود الملفات
ls -lh openapi-unified.*

# تحقق من صحة YAML
python -c "import yaml; yaml.safe_load(open('openapi-unified.yaml'))"

# أعد التوليد إذا لزم الأمر
python openapi-aggregator.py
```

---

## 📞 الدعم والمساعدة

للحصول على المساعدة:
- **البريد الإلكتروني**: support@sahool.com
- **الموقع**: https://sahool.com
- **التوثيق الكامل**: راجع مجلد `/docs`

---

## 📄 الترخيص

© 2025 SAHOOL Platform. جميع الحقوق محفوظة.

---

**Built with ❤️ for Yemen's Farmers**

**بُني بحب ❤️ لمزارعي اليمن**
