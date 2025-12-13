# SAHOOL Kernel Services v15.3

## 🚀 الخدمات المتقدمة | Advanced Services

### 🛰️ Satellite Service (خدمة الأقمار الصناعية)
**Port:** 8090

| Endpoint | Description |
|----------|-------------|
| `GET /v1/satellites` | قائمة الأقمار المتاحة |
| `GET /v1/regions` | المناطق المراقبة |
| `POST /v1/imagery/request` | طلب صور الأقمار |
| `POST /v1/analyze` | تحليل شامل للحقل |
| `GET /v1/timeseries/{field_id}` | السلسلة الزمنية |

**Features:**
- Sentinel-2, Landsat-8/9, MODIS integration
- NDVI, NDWI, EVI, SAVI, LAI calculations
- Vegetation health scoring
- Anomaly detection

---

### 📊 Indicators Service (خدمة المؤشرات الزراعية)
**Port:** 8091

| Endpoint | Description |
|----------|-------------|
| `GET /v1/indicators/definitions` | تعريفات المؤشرات |
| `GET /v1/field/{field_id}/indicators` | مؤشرات الحقل |
| `GET /v1/dashboard/{tenant_id}` | لوحة المعلومات |
| `GET /v1/alerts/{tenant_id}` | التنبيهات |
| `GET /v1/trends/{field_id}/{indicator_id}` | الاتجاهات |

**Features:**
- 20+ agricultural indicators
- Real-time dashboard
- Alert system
- Trend analysis

---

### 🌤️ Weather Advanced (خدمة الطقس المتقدمة)
**Port:** 8092

| Endpoint | Description |
|----------|-------------|
| `GET /v1/locations` | المواقع المتاحة |
| `GET /v1/current/{location_id}` | الطقس الحالي |
| `GET /v1/forecast/{location_id}` | التنبؤات (7 أيام) |
| `GET /v1/alerts/{location_id}` | تنبيهات الطقس |
| `GET /v1/agricultural-calendar/{location_id}` | التقويم الزراعي |

**Features:**
- 7-day forecasting
- Agricultural weather alerts
- Evapotranspiration calculation
- Spray window identification
- Crop-specific calendar

---

### 🧪 Fertilizer Advisor (مستشار السماد)
**Port:** 8093

| Endpoint | Description |
|----------|-------------|
| `GET /v1/crops` | المحاصيل المدعومة |
| `GET /v1/fertilizers` | الأسمدة المتاحة |
| `POST /v1/recommend` | توصيات التسميد |
| `POST /v1/soil-analysis/interpret` | تفسير تحليل التربة |
| `GET /v1/deficiency-symptoms/{crop}` | أعراض نقص العناصر |

**Features:**
- NPK recommendations
- 12+ crops supported
- Soil analysis interpretation
- Cost estimation
- Organic fertilizer options

---

### 💧 Smart Irrigation (الري الذكي)
**Port:** 8094

| Endpoint | Description |
|----------|-------------|
| `GET /v1/crops` | المحاصيل المدعومة |
| `GET /v1/methods` | طرق الري |
| `POST /v1/calculate` | حساب احتياجات الري |
| `GET /v1/water-balance/{field_id}` | الميزان المائي |
| `POST /v1/sensor-reading` | قراءة المستشعرات |
| `GET /v1/efficiency-report/{field_id}` | تقرير الكفاءة |

**Features:**
- AI-powered scheduling
- Water conservation
- 5 irrigation methods
- Sensor integration
- Efficiency comparison

---

## 🏃 Quick Start

```bash
# Start all services
cd kernel-services-v15.3
docker compose up -d

# Check health
curl http://localhost:8090/healthz  # Satellite
curl http://localhost:8091/healthz  # Indicators
curl http://localhost:8092/healthz  # Weather
curl http://localhost:8093/healthz  # Fertilizer
curl http://localhost:8094/healthz  # Irrigation
```

## 📊 Service Ports

| Service | Port | Arabic Name |
|---------|------|-------------|
| Satellite | 8090 | الأقمار الصناعية |
| Indicators | 8091 | المؤشرات الزراعية |
| Weather | 8092 | الطقس المتقدم |
| Fertilizer | 8093 | مستشار السماد |
| Irrigation | 8094 | الري الذكي |

## 🔗 Dependencies

- PostgreSQL 15
- NATS JetStream
- Redis 7

## 📁 Structure

```
kernel-services-v15.3/
├── satellite-service/
│   └── src/main.py
├── indicators-service/
│   └── src/main.py
├── weather-advanced/
│   └── src/main.py
├── fertilizer-advisor/
│   └── src/main.py
├── irrigation-smart/
│   └── src/main.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```
