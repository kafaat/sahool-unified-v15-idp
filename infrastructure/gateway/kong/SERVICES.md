# SAHOOL Platform Services Registry

# سجل خدمات منصة سهول

## Service Overview | نظرة عامة على الخدمات

Total Services: 39 microservices
إجمالي الخدمات: 39 خدمة مصغرة

## Package Distribution | توزيع الباقات

| Package      | Services Count     | Rate Limit | Price (SAR/month) |
| ------------ | ------------------ | ---------- | ----------------- |
| Trial        | 5                  | 50/min     | Free              |
| Starter      | 5                  | 100/min    | 99 SAR            |
| Professional | 13 (+Starter)      | 1000/min   | 399 SAR           |
| Enterprise   | 21 (+Professional) | 10000/min  | 999 SAR           |
| Research     | 14 (+Shared)       | 10000/min  | Custom            |

---

## Starter Package Services | خدمات الباقة الأساسية

**Target Users:** Small farmers and new landowners
**المستخدمون المستهدفون:** المزارعون الصغار وملاك الأراضي الجدد

### 1. Field Core | إدارة الحقول

- **Service Name:** `field-core`
- **Port:** 3000
- **Route:** `/api/v1/starter/fields`
- **Description:** Basic field management (up to 5 fields)
- **الوصف:** إدارة الحقول الأساسية (حتى 5 حقول)
- **Technology:** Node.js/Express
- **Database:** PostgreSQL + PostGIS
- **Features:**
  - Create/update/delete fields
  - Field boundaries (GeoJSON)
  - Crop assignment
  - Basic field statistics

### 2. Weather Core | الطقس الأساسي

- **Service Name:** `weather-core`
- **Port:** 8108
- **Route:** `/api/v1/starter/weather`
- **Description:** 7-day weather forecasts
- **الوصف:** تنبؤات الطقس لـ 7 أيام
- **Technology:** Python/FastAPI
- **Data Sources:** OpenWeatherMap, Met Office
- **Features:**
  - Daily forecasts
  - Temperature, humidity, precipitation
  - Wind speed and direction
  - Basic alerts

### 3. Astronomical Calendar | التقويم الفلكي

- **Service Name:** `astronomical-calendar`
- **Port:** 8111
- **Route:** `/api/v1/starter/calendar`
- **Description:** Yemeni agricultural calendar (Hijri-based)
- **الوصف:** التقويم الزراعي اليمني (قمري)
- **Technology:** Python/FastAPI
- **Features:**
  - Hijri calendar dates
  - Agricultural events
  - Planting seasons
  - Traditional knowledge integration

### 4. Agro Advisor | المستشار الزراعي

- **Service Name:** `agro-advisor`
- **Port:** 8105
- **Route:** `/api/v1/starter/advice`
- **Description:** Basic agricultural advice
- **الوصف:** النصائح الزراعية الأساسية
- **Technology:** Python/FastAPI
- **Features:**
  - Crop recommendations
  - Planting guides
  - Basic pest management
  - Seasonal tips

### 5. Notification Service | خدمة الإشعارات

- **Service Name:** `notification-service`
- **Port:** 8110
- **Route:** `/api/v1/starter/notifications`
- **Description:** SMS and push notifications
- **الوصف:** إشعارات الرسائل النصية والدفع
- **Technology:** Python/FastAPI
- **Providers:** Twilio, Firebase
- **Features:**
  - SMS alerts
  - Push notifications
  - Email notifications
  - Notification preferences

---

## Professional Package Services | خدمات الباقة المتوسطة

**Includes Starter + the following services**
**تشمل الباقة الأساسية + الخدمات التالية**

### 6. Satellite Service | خدمة الأقمار الصناعية

- **Service Name:** `satellite-service`
- **Port:** 8090
- **Route:** `/api/v1/professional/satellite`
- **Description:** Sentinel-2 imagery every 5 days
- **الوصف:** صور Sentinel-2 كل 5 أيام
- **Technology:** Python/FastAPI
- **Data Source:** Copernicus/Sentinel Hub
- **Features:**
  - True color imagery
  - NDVI, NDRE, EVI indices
  - Cloud masking
  - Historical archive

### 7. NDVI Engine | محرك NDVI

- **Service Name:** `ndvi-engine`
- **Port:** 8107
- **Route:** `/api/v1/professional/ndvi`
- **Description:** Vegetation health analysis
- **الوصف:** تحليل صحة النباتات
- **Technology:** Python/FastAPI
- **Features:**
  - NDVI calculation
  - Temporal analysis
  - Zone statistics
  - Health scoring

### 8. Crop Health AI | الذكاء الاصطناعي لصحة المحاصيل

- **Service Name:** `crop-health-ai`
- **Port:** 8095
- **Route:** `/api/v1/professional/crop-health`
- **Description:** Disease detection from images
- **الوصف:** كشف الأمراض من الصور
- **Technology:** Python/FastAPI + PyTorch
- **AI Model:** ResNet50 + Custom
- **Features:**
  - Disease identification
  - Pest detection
  - Treatment recommendations
  - Confidence scoring

### 9. Irrigation Smart | الري الذكي

- **Service Name:** `irrigation-smart`
- **Port:** 8094
- **Route:** `/api/v1/professional/irrigation`
- **Description:** Smart irrigation scheduling
- **الوصف:** جدولة الري الذكية
- **Technology:** Python/FastAPI
- **Features:**
  - ET0 calculations
  - Crop water requirements
  - Irrigation scheduling
  - Water balance

### 10. Virtual Sensors | المستشعرات الافتراضية

- **Service Name:** `virtual-sensors`
- **Port:** 8096
- **Route:** `/api/v1/professional/sensors/virtual`
- **Description:** ET0 without physical sensors
- **الوصف:** حساب ET0 بدون مستشعرات
- **Technology:** Python/FastAPI
- **Methods:** FAO Penman-Monteith
- **Features:**
  - ET0 estimation
  - Soil moisture modeling
  - Virtual weather stations
  - Data interpolation

### 11. Yield Engine | محرك توقع الإنتاجية

- **Service Name:** `yield-engine`
- **Port:** 8098
- **Route:** `/api/v1/professional/yield`
- **Description:** Seasonal yield prediction
- **الوصف:** توقع الإنتاجية الموسمية
- **Technology:** Python/FastAPI + ML
- **Features:**
  - Yield forecasting
  - Historical comparisons
  - Factor analysis
  - Risk assessment

### 12. Fertilizer Advisor | مستشار التسميد

- **Service Name:** `fertilizer-advisor`
- **Port:** 8093
- **Route:** `/api/v1/professional/fertilizer`
- **Description:** Smart fertilization recommendations
- **الوصف:** توصيات التسميد الذكية
- **Technology:** Python/FastAPI
- **Features:**
  - NPK recommendations
  - Application timing
  - Dosage calculations
  - Cost optimization

### 13. Inventory Service | إدارة المخزون

- **Service Name:** `inventory-service`
- **Port:** 8116
- **Route:** `/api/v1/professional/inventory`
- **Description:** Warehouse and inventory management
- **الوصف:** إدارة المخزون والمستودعات
- **Technology:** Python/FastAPI
- **Features:**
  - Stock tracking
  - Expiry management
  - Reorder alerts
  - Batch tracking

### 14. Equipment Service | خدمة المعدات

- **Service Name:** `equipment-service`
- **Port:** 8101
- **Route:** `/api/v1/professional/equipment`
- **Description:** Farm equipment management
- **الوصف:** إدارة المعدات الزراعية
- **Technology:** Python/FastAPI
- **Features:**
  - Equipment inventory
  - Maintenance scheduling
  - Usage tracking
  - Cost tracking

### 15. Weather Advanced | الطقس المتقدم

- **Service Name:** `weather-advanced`
- **Port:** 8092
- **Route:** `/api/v1/professional/weather/advanced`
- **Description:** Advanced weather analytics
- **الوصف:** التحليلات الجوية المتقدمة
- **Technology:** Python/FastAPI
- **Features:**
  - 14-day forecasts
  - Hourly data
  - Growing degree days
  - Frost predictions

### 16. NDVI Processor | معالج NDVI

- **Service Name:** `ndvi-processor`
- **Port:** 8118
- **Route:** `/api/v1/professional/ndvi-processor`
- **Description:** Batch NDVI processing
- **الوصف:** معالجة NDVI بالدفعات
- **Technology:** Python/FastAPI
- **Features:**
  - Batch processing
  - Change detection
  - Anomaly detection
  - Export capabilities

### 17. Indicators Service | خدمة المؤشرات

- **Service Name:** `indicators-service`
- **Port:** 8091
- **Route:** `/api/v1/professional/indicators`
- **Description:** Agricultural performance indicators
- **الوصف:** مؤشرات الأداء الزراعي
- **Technology:** Python/FastAPI
- **Features:**
  - KPI tracking
  - Benchmarking
  - Trend analysis
  - Custom indicators

### 18. Task Service | خدمة المهام

- **Service Name:** `task-service`
- **Port:** 8103
- **Route:** `/api/v1/professional/tasks`
- **Description:** Farm task management
- **الوصف:** إدارة المهام الزراعية
- **Technology:** Python/FastAPI
- **Features:**
  - Task scheduling
  - Assignment
  - Progress tracking
  - Notifications

---

## Enterprise Package Services | خدمات الباقة المتقدمة

**Includes Professional + the following services**
**تشمل الباقة المتوسطة + الخدمات التالية**

### 19. AI Advisor | المستشار الذكي

- **Service Name:** `ai-advisor`
- **Port:** 8112
- **Route:** `/api/v1/enterprise/ai-advisor`
- **Description:** Multi-agent AI advisor
- **الوصف:** المستشار الذكي متعدد الوكلاء
- **Technology:** Python/FastAPI + LangChain
- **AI Models:** GPT-4, Claude, Llama
- **Features:**
  - Natural language queries
  - Multi-modal analysis
  - Expert recommendations
  - Decision support

### 20. IoT Gateway | بوابة إنترنت الأشياء

- **Service Name:** `iot-gateway`
- **Port:** 8106
- **Route:** `/api/v1/enterprise/iot`
- **Description:** Real IoT sensor integration
- **الوصف:** ربط مستشعرات IoT حقيقية
- **Technology:** Python/FastAPI + MQTT
- **Protocols:** MQTT, CoAP, LoRaWAN
- **Features:**
  - Device management
  - Real-time data streaming
  - Protocol translation
  - Edge computing

### 21. Research Core | إدارة الأبحاث

- **Service Name:** `research-core`
- **Port:** 3015
- **Route:** `/api/v1/enterprise/research`
- **Description:** Research trials management
- **الوصف:** إدارة التجارب البحثية
- **Technology:** Node.js/Express
- **Features:**
  - Trial design
  - Plot management
  - Data collection
  - Statistical analysis

### 22. Marketplace Service | السوق الزراعي

- **Service Name:** `marketplace-service`
- **Port:** 3010
- **Route:** `/api/v1/enterprise/marketplace`
- **Description:** Agricultural marketplace
- **الوصف:** السوق الزراعي
- **Technology:** Node.js/Express
- **Features:**
  - Product listings
  - Buyer-seller matching
  - Price discovery
  - Transaction management

### 23. Billing Core | الفوترة والمدفوعات

- **Service Name:** `billing-core`
- **Port:** 8089
- **Route:** `/api/v1/enterprise/billing`
- **Description:** Billing and payments
- **الوصف:** الفوترة والمدفوعات
- **Technology:** Python/FastAPI
- **Payment Gateways:** Stripe, Moyasar
- **Features:**
  - Subscription management
  - Invoice generation
  - Payment processing
  - Usage tracking

### 24. Disaster Assessment | تقييم الكوارث

- **Service Name:** `disaster-assessment`
- **Port:** 3020
- **Route:** `/api/v1/enterprise/disaster`
- **Description:** Agricultural disaster assessment
- **الوصف:** تقييم الكوارث الزراعية
- **Technology:** Node.js/Express
- **Features:**
  - Damage assessment
  - Satellite imagery analysis
  - Loss estimation
  - Recovery planning

### 25. Crop Growth Model | نماذج نمو المحاصيل

- **Service Name:** `crop-growth-model`
- **Port:** 3023
- **Route:** `/api/v1/enterprise/crop-model`
- **Description:** WOFOST/DSSAT simulation
- **الوصف:** محاكاة نماذج WOFOST/DSSAT
- **Technology:** Node.js + Python
- **Models:** WOFOST, DSSAT, APSIM
- **Features:**
  - Growth simulation
  - Yield prediction
  - Scenario analysis
  - Climate impact

### 26. LAI Estimation | تقدير مؤشر مساحة الورق

- **Service Name:** `lai-estimation`
- **Port:** 3022
- **Route:** `/api/v1/enterprise/lai`
- **Description:** Leaf Area Index estimation
- **الوصف:** تقدير مؤشر مساحة الورق
- **Technology:** Node.js/Python
- **Features:**
  - LAI calculation
  - Temporal trends
  - Growth stage detection
  - Biomass estimation

### 27. Yield Prediction | توقع الإنتاجية المتقدم

- **Service Name:** `yield-prediction`
- **Port:** 3021
- **Route:** `/api/v1/enterprise/yield-prediction`
- **Description:** Advanced yield prediction
- **الوصف:** توقع الإنتاجية المتقدم
- **Technology:** Node.js + ML
- **Features:**
  - ML-based predictions
  - Multi-factor analysis
  - Confidence intervals
  - What-if scenarios

### 28. IoT Service | خدمة IoT

- **Service Name:** `iot-service`
- **Port:** 8117
- **Route:** `/api/v1/enterprise/iot-service`
- **Description:** IoT data processing
- **الوصف:** معالجة بيانات IoT
- **Technology:** Python/FastAPI
- **Features:**
  - Data ingestion
  - Time-series storage
  - Anomaly detection
  - Alerts

---

## Shared Services | الخدمات المشتركة

**Available to all package tiers**
**متاحة لجميع مستويات الباقات**

### 29. Field Operations | عمليات الحقول

- **Service Name:** `field-ops`
- **Port:** 8080
- **Route:** `/api/v1/shared/field-ops`
- **Technology:** Python/FastAPI

### 30. WebSocket Gateway | بوابة WebSocket

- **Service Name:** `ws-gateway`
- **Port:** 8081
- **Route:** `/api/v1/shared/ws`
- **Technology:** Python/FastAPI
- **Features:** Real-time updates

### 31. Community Chat | محادثة المجتمع

- **Service Name:** `community-chat`
- **Port:** 8097
- **Route:** `/api/v1/shared/community/chat`
- **Technology:** Python/FastAPI

### 32. Field Chat | محادثة الحقل

- **Service Name:** `field-chat`
- **Port:** 8099
- **Route:** `/api/v1/shared/field/chat`
- **Technology:** Python/FastAPI

### 33. Provider Config | تكوين المزودين

- **Service Name:** `provider-config`
- **Port:** 8104
- **Route:** `/api/v1/shared/providers`
- **Technology:** Python/FastAPI

### 34. Alert Service | خدمة التنبيهات

- **Service Name:** `alert-service`
- **Port:** 8113
- **Route:** `/api/v1/shared/alerts`
- **Technology:** Python/FastAPI

### 35. Chat Service | خدمة المحادثة

- **Service Name:** `chat-service`
- **Port:** 8114
- **Route:** `/api/v1/shared/chat`
- **Technology:** Python/FastAPI

### 36. Field Service | خدمة الحقول

- **Service Name:** `field-service`
- **Port:** 8115
- **Route:** `/api/v1/shared/field-service`
- **Technology:** Python/FastAPI

---

## Administrative Services | الخدمات الإدارية

### 37. Admin Dashboard | لوحة التحكم

- **Service Name:** `admin-dashboard`
- **Port:** 3001
- **Route:** `/api/v1/admin`
- **Technology:** Node.js/React
- **Access:** Admin users only

---

## Infrastructure Services | الخدمات الأساسية

### 38. PostgreSQL Database

- **Port:** 5432
- **Version:** 16 with PostGIS
- **Purpose:** Main data storage

### 39. Redis Cache

- **Port:** 6379
- **Version:** 7
- **Purpose:** Caching and sessions

### NATS Event Bus

- **Port:** 4222
- **Version:** 2.10
- **Purpose:** Event-driven messaging

### Kong API Gateway

- **Proxy:** 8000 (HTTP), 8443 (HTTPS)
- **Admin:** 8001
- **Purpose:** API Gateway and routing

---

## Service Health Endpoints | نقاط فحص صحة الخدمات

All services expose the following health endpoints:

```
GET /health          # Basic health check
GET /health/ready    # Readiness probe
GET /health/live     # Liveness probe
GET /metrics         # Prometheus metrics
```

---

## Package Access Matrix | مصفوفة الوصول حسب الباقات

| Service               | Trial | Starter | Professional | Enterprise | Research |
| --------------------- | ----- | ------- | ------------ | ---------- | -------- |
| Field Core            | ✓     | ✓       | ✓            | ✓          | ✓        |
| Weather Core          | ✓     | ✓       | ✓            | ✓          | ✓        |
| Astronomical Calendar | ✓     | ✓       | ✓            | ✓          | ✓        |
| Agro Advisor          | ✓     | ✓       | ✓            | ✓          | ✓        |
| Notification Service  | ✓     | ✓       | ✓            | ✓          | ✓        |
| Satellite Service     | -     | -       | ✓            | ✓          | ✓        |
| NDVI Engine           | -     | -       | ✓            | ✓          | ✓        |
| Crop Health AI        | -     | -       | ✓            | ✓          | ✓        |
| Irrigation Smart      | -     | -       | ✓            | ✓          | ✓        |
| Virtual Sensors       | -     | -       | ✓            | ✓          | ✓        |
| Yield Engine          | -     | -       | ✓            | ✓          | ✓        |
| Fertilizer Advisor    | -     | -       | ✓            | ✓          | ✓        |
| Inventory Service     | -     | -       | ✓            | ✓          | ✓        |
| AI Advisor            | -     | -       | -            | ✓          | ✓        |
| IoT Gateway           | -     | -       | -            | ✓          | -        |
| Research Core         | -     | -       | -            | ✓          | ✓        |
| Marketplace Service   | -     | -       | -            | ✓          | -        |
| Billing Core          | -     | -       | -            | ✓          | -        |
| Disaster Assessment   | -     | -       | -            | ✓          | ✓        |
| Crop Growth Model     | -     | -       | -            | ✓          | ✓        |
| LAI Estimation        | -     | -       | -            | ✓          | ✓        |

---

**Last Updated:** 2025-12-25
**Version:** 1.0.0
