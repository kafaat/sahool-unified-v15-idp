# Irrigation Cycle Engine

**محرك دورات الري - نظام إدارة دورات الري الزراعي**

## Overview | نظرة عامة

SAHOOL Irrigation Cycle Engine is a production-grade FastAPI microservice implementing FAO-56 standard irrigation scheduling with Yemen-specific adaptations. It calculates optimal irrigation cycles, water requirements, and multi-day schedules using scientific formulas for evapotranspiration (ET0 and ETc) with support for crop coefficients, soil profiles, and salinity management.

محرك دورات الري لمنصة سهول هو خدمة FastAPI متقدمة تطبق معايير FAO-56 لجدولة الري مع التكييف مع ظروف اليمن. يحسب دورات الري المثلى ومتطلبات المياه والجداول متعددة الأيام باستخدام صيغ علمية للبخر والنتح (ET0 و ETc) مع دعم معاملات المحاصيل وملفات التربة وإدارة الملوحة.

## Port

```
8250
```

## Features | الميزات

### Core Irrigation Calculations | حسابات الري الأساسية

- **ET0 Calculation (Penman-Monteith FAO-56)**: Reference evapotranspiration from weather data
  - يحسب ET0 (البخر والنتح المرجعي) من بيانات الطقس
- **ETc with Dual Crop Coefficients**: Crop ET using Kcb (basal) and Ke (evaporation)
  - حساب ETc (بخر ونتح المحصول) باستخدام معاملات ثنائية
- **Irrigation Cycle Formula**: T = ((θfc - θmin) × Zr × β) / (ETc × α × γ)
  - دورة الري: T = ((θfc - θmin) × Zr × β) / (ETc × α × γ)
- **Water Requirement Estimation**: Net and gross irrigation depths with efficiency factors
  - تقدير متطلبات المياه بكفاءات مختلفة

### Yemen-Specific Data | البيانات المخصصة لليمن

- **Crop Database**: 25+ Yemen crops with growth stages and Kc values
  - قاعدة بيانات المحاصيل اليمنية مع مراحل النمو
- **Climate Zones**: Regional ET0 data for Yemen (4 zones: High rainfall, Moderate, Arid, Coastal)
  - مناطق مناخية مع بيانات ET0 المحلية
- **Soil Profiles**: Hydraulic properties (θfc, θwp, bulk density) for Yemen soils
  - ملفات التربة اليمنية مع الخصائص الهيدروليكية
- **Salinity Management**: Integrated salinity assessment with Kc adjustment
  - إدارة الملوحة مع تعديل Kc

### Multi-Day Scheduling | جدولة متعددة الأيام

- Automatic irrigation event detection based on soil depletion
  - كشف تلقائي لأحداث الري
- Cumulative water tracking and water use efficiency metrics
  - تتبع استهلاك المياه المتراكم
- Bilingual growth stage tracking (English/Arabic)
  - تتبع مراحل النمو ثنائي اللغة

### Salinity & Water Quality | الملوحة وجودة المياه

- EC (Electrical Conductivity) based salinity assessment
  - تقييم الملوحة بناءً على التوصيل الكهربائي
- Leaching requirement calculation
  - حساب متطلبات الغسيل
- Yield reduction estimation under salinity stress
  - تقدير انخفاض الإنتاجية تحت إجهاد الملوحة
- SAR (Sodium Adsorption Ratio) calculation
  - حساب نسبة امتصاص الصوديوم

### NATS Event Integration | التكامل مع أحداث NATS

- Publishes `sahool.{tenant_id}.irrigation.cycle_calculated` events
  - نشر أحداث حساب دورة الري
- Supports tenant-scoped messaging
  - دعم المراسلة محدودة النطاق بحسب المشروع

## API Endpoints

### Health Checks

```
GET /healthz                   # Service health status
GET /readyz                    # Readiness probe (checks Yemen data loading)
```

### ET0 Calculation

```
POST /api/v1/irrigation/et0
```

Calculate reference evapotranspiration (ET0) using FAO-56 Penman-Monteith method.

**Request Body**:
```json
{
  "latitude": 15.5,
  "elevation_m": 150,
  "weather": [
    {
      "date": "2025-02-16",
      "temp_min_c": 12.0,
      "temp_max_c": 28.0,
      "humidity_min_pct": 30,
      "humidity_max_pct": 70,
      "wind_speed_2m_ms": 2.0,
      "solar_radiation_mjm2": 20.0,
      "rainfall_mm": 0.0
    }
  ]
}
```

**Response**:
```json
[
  {
    "date": "2025-02-16",
    "et0_mm": 5.23,
    "method": "penman_monteith_fao56"
  }
]
```

### Irrigation Cycle Calculation

```
POST /api/v1/irrigation/cycle
```

Calculate optimal irrigation cycle period and water requirements using the SAHOOL cycle formula.

**Request Body**:
```json
{
  "crop": "wheat",
  "growth_stage": "tillering",
  "field_capacity": 0.28,
  "wilting_point": 0.12,
  "root_depth_m": 1.0,
  "bulk_density": 1.4,
  "depletion_fraction": 0.5,
  "et0_mm_day": 5.0,
  "kc": null,
  "ec_water": null,
  "ec_soil": null,
  "alpha": 1.0,
  "beta": 1.0,
  "gamma": 1.0
}
```

**Response**:
```json
{
  "cycle_days": 6.5,
  "net_irrigation_mm": 80.0,
  "gross_irrigation_mm": 94.1,
  "etc_mm_day": 5.0,
  "kc_used": 1.0,
  "kc_adjusted": null,
  "leaching_fraction": null,
  "total_water_mm": 94.1,
  "available_water_mm": 160.0,
  "readily_available_mm": 80.0,
  "next_irrigation_date": "2025-02-22",
  "crop_name": "wheat",
  "crop_name_ar": "القمح",
  "recommendations": [
    "Long cycle. Monitor soil moisture to verify schedule accuracy."
  ],
  "recommendations_ar": [
    "دورة طويلة. راقب رطوبة التربة للتحقق من دقة الجدول."
  ]
}
```

### Multi-Day Schedule Generation

```
POST /api/v1/irrigation/schedule
```

Generate a complete irrigation schedule for a specified period using Yemen crop/climate/soil data.

**Request Body**:
```json
{
  "crop": "wheat",
  "soil_profile": "sandy_loam",
  "climate_zone": "moderate_rainfall",
  "start_date": "2025-02-01",
  "days": 30,
  "field_area_ha": 5.0,
  "irrigation_efficiency": 0.85,
  "ec_water": null
}
```

**Response**:
```json
{
  "crop": "wheat",
  "crop_ar": "القمح",
  "soil_profile": "sandy_loam",
  "climate_zone": "moderate_rainfall",
  "schedule": [
    {
      "date": "2025-02-01",
      "day_of_season": 1,
      "growth_stage": "Germination",
      "kc": 0.3,
      "et0_mm": 4.5,
      "etc_mm": 1.35,
      "soil_moisture_pct": 100.0,
      "irrigate": false,
      "irrigation_mm": 0.0,
      "cumulative_water_mm": 0.0
    },
    {
      "date": "2025-02-06",
      "day_of_season": 6,
      "growth_stage": "Germination",
      "kc": 0.3,
      "et0_mm": 4.5,
      "etc_mm": 1.35,
      "soil_moisture_pct": 45.2,
      "irrigate": true,
      "irrigation_mm": 94.1,
      "cumulative_water_mm": 94.1
    }
  ],
  "total_water_mm": 280.5,
  "total_water_m3_per_ha": 2805.0,
  "irrigation_events": 4,
  "average_cycle_days": 7.5,
  "water_use_efficiency": "2805 m³/ha over 30 days"
}
```

### Yemen Crops Database

```
GET /api/v1/yemen/crops
GET /api/v1/yemen/crops/{crop_name}
```

List available Yemen crops and retrieve detailed crop parameters.

**Example Request**:
```
GET /api/v1/yemen/crops?crop_type=cereal&region=highlands
GET /api/v1/yemen/crops/wheat
```

**Response**:
```json
{
  "name": "Wheat",
  "name_ar": "القمح",
  "crop_type": "cereal",
  "root_depth_m": 1.0,
  "depletion_fraction": 0.5,
  "growth_stages": [
    {
      "name": "Germination",
      "name_ar": "الإنبات",
      "duration_days": 15,
      "kc": 0.3
    },
    {
      "name": "Tillering",
      "name_ar": "التفريع",
      "duration_days": 30,
      "kc": 0.7
    },
    {
      "name": "Heading",
      "name_ar": "طلوع السنابل",
      "duration_days": 15,
      "kc": 1.0
    },
    {
      "name": "Grain Filling",
      "name_ar": "امتلاء الحبوب",
      "duration_days": 30,
      "kc": 0.85
    }
  ],
  "salinity_threshold_dsm": 6.0,
  "regions": ["highlands", "coastal_plains"]
}
```

### Yemen Climate Zones

```
GET /api/v1/yemen/climate-zones
```

List Yemen climate zones with key parameters.

**Response**:
```json
{
  "zones": [
    {
      "zone": "high_rainfall",
      "name": "High Rainfall",
      "name_ar": "هطول مرتفع",
      "et0_range_mm_day": "3.0-5.0",
      "annual_rainfall_mm": 600,
      "groundwater_decline_m_year": 0.5,
      "major_crops": ["wheat", "barley", "maize"]
    }
  ],
  "total": 4
}
```

### Yemen Soil Profiles

```
GET /api/v1/yemen/soils
```

List Yemen soil profiles with hydraulic properties.

**Response**:
```json
{
  "profiles": [
    {
      "name": "Sandy Loam",
      "name_ar": "رمل طيني",
      "soil_type": "sandy_loam",
      "region": "Central Yemen",
      "field_capacity": 0.28,
      "wilting_point": 0.12,
      "bulk_density": 1.4,
      "available_water_mm_m": 160.0,
      "ec_natural": 0.5
    }
  ],
  "total": 6
}
```

### Salinity Assessment

```
POST /api/v1/irrigation/salinity-assessment
```

Assess salinity impact on irrigation water and crop yield.

**Query Parameters**:
```
ec_water=2.5              # EC of irrigation water (dS/m)
crop=wheat                # Crop name
kc=1.0                    # Current Kc (optional)
ec_soil=4.0               # Soil EC (optional)
na=14.0                   # Sodium (meq/L, optional)
ca=2.5                    # Calcium (meq/L, optional)
mg=1.5                    # Magnesium (meq/L, optional)
```

**Response**:
```json
{
  "ec_water": 2.5,
  "ec_soil": 4.0,
  "sar": 2.1,
  "risk": "moderate",
  "risk_ar": "معتدل",
  "yield_reduction_pct": 8.5,
  "leaching_fraction": 0.12,
  "kc_original": 1.0,
  "kc_adjusted": 0.92,
  "recommendations": [
    "Maintain adequate irrigation to prevent salt accumulation",
    "Monitor soil EC monthly, target <3 dS/m for wheat"
  ],
  "recommendations_ar": [
    "حافظ على ري كافٍ لمنع تراكم الأملاح",
    "راقب التوصيل الكهربائي للتربة شهرياً"
  ]
}
```

## Core Formula Breakdown

### Irrigation Cycle Formula

```
T = ((θfc - θmin) × Zr × β) / (ETc × α × γ)
```

Where:
- **T**: Irrigation cycle (days) | دورة الري (أيام)
- **θfc**: Field capacity (cm³/cm³) | السعة الحقلية (سم³/سم³)
- **θmin**: Minimum soil moisture threshold (cm³/cm³) | الحد الأدنى لرطوبة التربة
- **Zr**: Effective root depth (mm) | عمق الجذور الفعال (ملم)
- **β**: Soil correction factor (0.8-1.2) | معامل تصحيح التربة
- **ETc**: Crop evapotranspiration (mm/day) | البخر والنتح للمحصول (ملم/يوم)
- **α**: ET correction factor (0.7-1.3) | معامل تصحيح البخر والنتح
- **γ**: Stress/management correction factor (0.8-1.0) | معامل التصحيح الإجهادي

### Reference Evapotranspiration (ET0)

Uses **FAO-56 Penman-Monteith** equation:

```
ET0 = (0.408 × Δ × (Rn - G) + γ × (900/(T+273)) × u₂ × (eₛ - eₐ)) / (Δ + γ × (1 + 0.34 × u₂))
```

Where:
- **Δ**: Slope of saturation vapor pressure curve (kPa/°C)
- **Rn**: Net radiation (MJ/m²/day)
- **G**: Soil heat flux (MJ/m²/day)
- **γ**: Psychrometric constant (kPa/°C)
- **T**: Mean temperature (°C)
- **u₂**: Wind speed at 2m height (m/s)
- **eₛ**: Saturation vapor pressure (kPa)
- **eₐ**: Actual vapor pressure (kPa)

### Crop Evapotranspiration (ETc)

```
ETc = ET0 × Kc
```

Where:
- **ET0**: Reference evapotranspiration
- **Kc**: Crop coefficient (growth stage dependent)

## Environment Variables

| Variable      | Default | Description                                 |
| ------------- | ------- | ------------------------------------------- |
| `PORT`        | 8250    | Service port                                |
| `NATS_URL`    | -       | NATS server URL (optional, for events)      |
| `TENANT_ID`   | default | Tenant ID for event scoping                 |
| `LOG_LEVEL`   | INFO    | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENVIRONMENT` | dev     | Environment (development, staging, prod)    |
| `DATABASE_URL`| -       | PostgreSQL connection (optional)            |

## Dependencies

| Package         | Version    | Purpose                                   |
| --------------- | ---------- | ----------------------------------------- |
| FastAPI         | 0.128.5    | Web framework                             |
| Pydantic        | 2.12.5     | Data validation                           |
| pyfao56         | >=1.4.0    | FAO-56 ET calculations                    |
| NumPy           | >=1.26.0   | Numerical computations                    |
| nats-py         | 2.13.1     | NATS messaging                            |
| Redis           | >=7.1.0    | Caching (optional)                        |
| structlog       | >=24.1.0   | Structured logging                        |
| prometheus-client | >=0.21.0 | Prometheus metrics                        |

## Docker

```bash
# Build image
docker build -t irrigation-cycle-engine .

# Run container
docker run -p 8250:8250 \
  -e PORT=8250 \
  -e NATS_URL=nats://nats:4222 \
  -e TENANT_ID=sahool \
  irrigation-cycle-engine

# Run with environment file
docker run -p 8250:8250 --env-file .env irrigation-cycle-engine
```

## Development

```bash
# Install dependencies
cd apps/services/irrigation-cycle-engine
pip install -r requirements.txt

# Run development server with auto-reload
python -m uvicorn src.main:app --reload --port 8250

# Run with environment variables
PORT=8250 NATS_URL=nats://localhost:4222 \
python -m uvicorn src.main:app --reload --port 8250
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_health.py -v

# Run with verbose output
pytest tests/ -vv
```

## Example Usage

### Python

```python
import httpx
import json
from datetime import date

# Initialize client
client = httpx.Client(base_url="http://localhost:8250")

# Calculate ET0
et0_request = {
    "latitude": 15.5,
    "elevation_m": 150,
    "weather": [
        {
            "date": "2025-02-16",
            "temp_min_c": 12.0,
            "temp_max_c": 28.0,
            "humidity_min_pct": 30,
            "humidity_max_pct": 70,
            "wind_speed_2m_ms": 2.0,
            "solar_radiation_mjm2": 20.0,
            "rainfall_mm": 0.0
        }
    ]
}
response = client.post("/api/v1/irrigation/et0", json=et0_request)
et0_result = response.json()
print(f"ET0: {et0_result[0]['et0_mm']} mm/day")

# Calculate irrigation cycle
cycle_request = {
    "crop": "wheat",
    "growth_stage": "tillering",
    "field_capacity": 0.28,
    "wilting_point": 0.12,
    "root_depth_m": 1.0,
    "depletion_fraction": 0.5,
    "et0_mm_day": et0_result[0]['et0_mm'],
    "ec_water": None
}
response = client.post("/api/v1/irrigation/cycle", json=cycle_request)
cycle_result = response.json()
print(f"Irrigation cycle: {cycle_result['cycle_days']} days")
print(f"Water requirement: {cycle_result['gross_irrigation_mm']} mm")

# Generate schedule
schedule_request = {
    "crop": "wheat",
    "soil_profile": "sandy_loam",
    "climate_zone": "moderate_rainfall",
    "start_date": "2025-02-01",
    "days": 30,
    "field_area_ha": 5.0,
    "irrigation_efficiency": 0.85
}
response = client.post("/api/v1/irrigation/schedule", json=schedule_request)
schedule_result = response.json()
print(f"Total water needed: {schedule_result['total_water_m3_per_ha']} m³/ha")
print(f"Irrigation events: {schedule_result['irrigation_events']}")
```

### cURL

```bash
# Health check
curl http://localhost:8250/healthz

# Calculate ET0
curl -X POST http://localhost:8250/api/v1/irrigation/et0 \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 15.5,
    "elevation_m": 150,
    "weather": [
      {
        "date": "2025-02-16",
        "temp_min_c": 12,
        "temp_max_c": 28,
        "humidity_min_pct": 30,
        "humidity_max_pct": 70,
        "wind_speed_2m_ms": 2,
        "solar_radiation_mjm2": 20,
        "rainfall_mm": 0
      }
    ]
  }'

# Calculate irrigation cycle
curl -X POST http://localhost:8250/api/v1/irrigation/cycle \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "wheat",
    "field_capacity": 0.28,
    "wilting_point": 0.12,
    "root_depth_m": 1.0,
    "depletion_fraction": 0.5,
    "et0_mm_day": 5.0
  }'

# Get Yemen crops
curl http://localhost:8250/api/v1/yemen/crops

# Salinity assessment
curl "http://localhost:8250/api/v1/irrigation/salinity-assessment?ec_water=2.5&crop=wheat"
```

## Integration with SAHOOL Platform

This service integrates with:

- **weather-service** (Port 8108): Provides weather data for ET0 calculations
- **field-management-service** (Port 3000): Field and crop information
- **vegetation-analysis-service** (Port 8090): NDVI and crop health monitoring
- **notification-service** (Port 8110): Irrigation alerts and recommendations

## Notes for Yemen Implementation

- All formulas follow **FAO-56** standard (Allen et al., 1998)
- Yemen climate zones based on rainfall, elevation, and groundwater availability
- Salinity thresholds calibrated for major Yemen crops (wheat, barley, date palm)
- Soil profiles represent typical Yemen soil types (sandy loam, clay loam, calcareous)
- Growth stage durations vary by elevation and rainfall zone

## References

1. **Allen, R.G., Pereira, L.S., Raes, D., Smith, M., 1998**. Crop evapotranspiration - Guidelines for computing crop water requirements. FAO Irrigation and Drainage Paper 56. Rome.

2. **Ayers, R.S., Westcot, D.W., 1985**. Water quality for agriculture. FAO Irrigation and Drainage Paper 29. Rome.

3. **Maas, E.V., Hoffman, G.J., 1977**. Crop salt tolerance - Current assessment. Journal of Irrigation and Drainage Engineering, 103(2), 115-134.

## Support

For issues, feature requests, or documentation improvements:

- **GitHub Issues**: [SAHOOL Platform Issues](https://github.com/kafaat/sahool-unified-v15-idp)
- **Documentation**: `/docs/services-docs/irrigation-cycle-engine.md`
- **Slack**: #irrigation-services
- **Email**: support@sahool.app
