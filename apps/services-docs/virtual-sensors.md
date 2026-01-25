# Virtual Sensors Service Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | virtual-sensors |
| **Arabic Name** | محرك المستشعرات الافتراضية |
| **Version** | 15.5.0 (code) / 16.0.0 (readiness endpoint) |
| **Type** | Python/FastAPI |
| **Port** | 8119 |
| **Layer** | Acquisition |
| **Category** | Analytics |
| **Status** | Active |

### Description

Software-based sensor calculations for smart irrigation management without physical hardware. The service calculates evapotranspiration (ET0), soil moisture estimation, and irrigation recommendations using weather data, crop coefficients, and soil characteristics based on **FAO-56 Penman-Monteith methodology**.

**Key Features:**
- Reference evapotranspiration (ET0) calculation using Penman-Monteith equation
- Crop coefficient (Kc) database with 15 crops adapted for Yemen/Middle East
- Soil moisture estimation using water balance method
- Irrigation scheduling and recommendations
- Virtual sensor ActionTemplate generation for mobile app integration
- Bilingual support (Arabic/English)
- Offline-first architecture support

---

## API Endpoints

### Health & System Endpoints

#### GET /healthz
Health check endpoint with dependency status.

**Response:**
```json
{
  "status": "healthy|degraded",
  "service": "virtual-sensors",
  "version": "15.5.0",
  "nats_connected": true|false,
  "timestamp": "2025-01-25T10:00:00Z"
}
```

#### GET /readyz
Kubernetes readiness probe.

**Response:**
```json
{
  "status": "ready",
  "service": "virtual-sensors",
  "version": "16.0.0",
  "checks": {
    "service": "ready"
  }
}
```

#### GET /v1/info
Get service information and capabilities.

**Response:**
```json
{
  "service": "virtual-sensors",
  "service_ar": "محرك المستشعرات الافتراضية",
  "version": "15.5.0",
  "description": "Software-based irrigation sensors using weather and crop data",
  "description_ar": "مستشعرات ري برمجية باستخدام بيانات الطقس والمحاصيل",
  "capabilities": [
    "ET0 calculation (Penman-Monteith)",
    "Crop water requirements (ETc)",
    "Virtual soil moisture estimation",
    "Irrigation scheduling",
    "Water balance tracking"
  ],
  "supported_crops": 15,
  "supported_soils": 6
}
```

---

### ET0 Calculation Endpoints

#### POST /v1/et0/calculate
Calculate reference evapotranspiration (ET0) using Penman-Monteith equation.

**Request Body (WeatherInput):**
```json
{
  "temperature_max": 35.0,
  "temperature_min": 22.0,
  "humidity": 45.0,
  "wind_speed": 2.5,
  "solar_radiation": 22.5,
  "sunshine_hours": 10.0,
  "latitude": 15.35,
  "altitude": 2200,
  "calculation_date": "2025-01-25"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `temperature_max` | float | Yes | - | Maximum temperature (C) |
| `temperature_min` | float | Yes | - | Minimum temperature (C) |
| `humidity` | float | Yes | 0-100 | Relative humidity (%) |
| `wind_speed` | float | Yes | >= 0 | Wind speed at 2m height (m/s) |
| `solar_radiation` | float | No | - | Solar radiation (MJ/m2/day) |
| `sunshine_hours` | float | No | 0-24 | Sunshine hours |
| `latitude` | float | Yes | -90 to 90 | Latitude (degrees) |
| `altitude` | float | No | default: 0 | Altitude above sea level (m) |
| `calculation_date` | date | No | default: today | Date for calculation |

**Response (ET0Response):**
```json
{
  "et0": 5.82,
  "et0_ar": "5.82 مم/يوم",
  "method": "FAO-56 Penman-Monteith",
  "weather_summary": {
    "temp_max": 35.0,
    "temp_min": 22.0,
    "temp_mean": 28.5,
    "humidity": 45.0,
    "wind_speed": 2.5,
    "latitude": 15.35,
    "altitude": 2200
  },
  "calculation_date": "2025-01-25"
}
```

---

### Crop Management Endpoints

#### GET /v1/crops
Get list of supported crops with Kc values.

**Response:**
```json
{
  "crops": [
    {
      "crop_id": "wheat",
      "name": "Wheat",
      "name_ar": "القمح",
      "kc_initial": 0.3,
      "kc_mid": 1.15,
      "kc_end": 0.25,
      "root_depth_max": 1.5,
      "critical_periods": ["flowering", "grain_filling"]
    }
  ],
  "total": 15
}
```

**Supported Crops:**

| Crop ID | Arabic Name | Kc Initial | Kc Mid | Kc End | Max Root Depth (m) |
|---------|-------------|------------|--------|--------|-------------------|
| wheat | القمح | 0.30 | 1.15 | 0.25 | 1.5 |
| barley | الشعير | 0.30 | 1.15 | 0.25 | 1.2 |
| sorghum | الذرة الرفيعة | 0.30 | 1.10 | 0.55 | 1.5 |
| maize | الذرة | 0.30 | 1.20 | 0.35 | 1.5 |
| tomato | الطماطم | 0.60 | 1.15 | 0.80 | 1.0 |
| potato | البطاطس | 0.50 | 1.15 | 0.75 | 0.6 |
| onion | البصل | 0.70 | 1.05 | 0.75 | 0.4 |
| coffee | البن اليمني | 0.90 | 0.95 | 0.90 | 1.5 |
| date_palm | النخيل | 0.90 | 1.00 | 0.90 | 2.5 |
| mango | المانجو | 0.75 | 0.90 | 0.80 | 2.0 |
| grape | العنب | 0.30 | 0.85 | 0.45 | 1.5 |
| alfalfa | البرسيم | 0.40 | 1.20 | 1.15 | 1.5 |
| qat | القات | 0.85 | 1.00 | 0.90 | 1.5 |
| banana | الموز | 0.50 | 1.10 | 1.00 | 0.6 |
| sesame | السمسم | 0.35 | 1.10 | 0.25 | 1.0 |

#### GET /v1/crops/{crop_type}/kc
Get Kc values for a specific crop.

**Path Parameters:**
- `crop_type` (string): Crop type identifier

**Query Parameters:**
- `growth_stage` (optional): GrowthStage enum value
- `days_in_stage` (optional): Days in current growth stage for interpolation

**Response (with growth_stage):**
```json
{
  "crop_type": "wheat",
  "crop_name_ar": "القمح",
  "growth_stage": "mid_season",
  "kc": 1.15,
  "days_in_stage": 30
}
```

**Response (without growth_stage):**
```json
{
  "crop_type": "wheat",
  "crop_name_ar": "القمح",
  "kc_initial": 0.3,
  "kc_mid": 1.15,
  "kc_end": 0.25,
  "stages_days": {
    "initial": 20,
    "development": 30,
    "mid_season": 60,
    "late_season": 30
  },
  "root_depth_max": 1.5,
  "depletion_fraction": 0.55
}
```

#### POST /v1/etc/calculate
Calculate crop evapotranspiration (ETc = ET0 x Kc).

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `crop_type` | string | Yes | Crop type identifier |
| `growth_stage` | GrowthStage | Yes | Current growth stage |
| `field_area_hectares` | float | No (default: 1.0) | Field area in hectares |
| `days_in_stage` | int | No | Days in current growth stage |

**Request Body:** `WeatherInput` (same as ET0 calculation)

**Response (CropETcResponse):**
```json
{
  "crop_type": "wheat",
  "crop_name_ar": "القمح",
  "growth_stage": "mid_season",
  "kc": 1.15,
  "et0": 5.82,
  "etc": 6.69,
  "daily_water_need_liters": 66900,
  "daily_water_need_m3": 66.9,
  "weekly_water_need_m3": 468.3,
  "critical_period": true,
  "notes": "Crop is in mid_season stage with Kc=1.15. Critical growth period - maintain optimal irrigation.",
  "notes_ar": "المحصول في مرحلة mid_season مع معامل Kc=1.15. فترة نمو حرجة - حافظ على الري المثالي."
}
```

---

### Soil Management Endpoints

#### GET /v1/soils
Get list of supported soil types with properties.

**Response:**
```json
{
  "soils": [
    {
      "soil_type": "loam",
      "name_ar": "طميي",
      "field_capacity": 0.27,
      "wilting_point": 0.12,
      "available_water_capacity": 0.15,
      "infiltration_rate_mm_hr": 13
    }
  ],
  "total": 6
}
```

**Supported Soil Types:**

| Soil Type | Arabic Name | Field Capacity | Wilting Point | AWC | Infiltration (mm/hr) |
|-----------|-------------|----------------|---------------|-----|---------------------|
| sandy | رملي | 0.12 | 0.04 | 0.08 | 50 |
| sandy_loam | رملي طميي | 0.20 | 0.08 | 0.12 | 25 |
| loam | طميي | 0.27 | 0.12 | 0.15 | 13 |
| clay_loam | طيني طميي | 0.32 | 0.18 | 0.14 | 8 |
| clay | طيني | 0.38 | 0.25 | 0.13 | 3 |
| silty_clay | طيني غريني | 0.35 | 0.22 | 0.13 | 5 |

#### POST /v1/soil-moisture/estimate
Estimate soil moisture using water balance method.

**Request Body (SoilMoistureInput):**
```json
{
  "soil_type": "loam",
  "root_depth": 0.6,
  "last_irrigation_date": "2025-01-20",
  "last_irrigation_amount": 30.0,
  "rainfall_since": 5.0,
  "daily_etc": 5.5
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `soil_type` | SoilType | Yes | enum | Soil type |
| `root_depth` | float | No (default: 0.6) | 0 < x <= 3.0 | Root depth (m) |
| `last_irrigation_date` | date | Yes | - | Date of last irrigation |
| `last_irrigation_amount` | float | Yes | - | Irrigation amount (mm) |
| `rainfall_since` | float | No (default: 0) | >= 0 | Rainfall since last irrigation (mm) |
| `daily_etc` | float | Yes | - | Daily crop ET (mm/day) |

**Response (VirtualSoilMoistureResponse):**
```json
{
  "calculation_id": "uuid-string",
  "estimated_moisture": 0.185,
  "moisture_percentage": 62.5,
  "days_since_irrigation": 5,
  "total_et_loss": 27.5,
  "available_water": 56.5,
  "total_available_water": 90.0,
  "status": "moderate_stress",
  "status_ar": "إجهاد متوسط",
  "urgency": "medium"
}
```

**Urgency Levels:**

| Depletion % | Status | Arabic | Urgency |
|-------------|--------|--------|---------|
| < 30% | optimal | مثالي | none |
| 30-50% | adequate | كافي | low |
| 50-70% | moderate_stress | إجهاد متوسط | medium |
| 70-85% | high_stress | إجهاد عالي | high |
| > 85% | critical | حرج | critical |

---

### Irrigation Recommendation Endpoints

#### GET /v1/irrigation-methods
Get irrigation methods with efficiencies.

**Response:**
```json
{
  "methods": [
    {"method": "drip", "efficiency": 0.9, "efficiency_percent": "90%"},
    {"method": "sprinkler", "efficiency": 0.75, "efficiency_percent": "75%"},
    {"method": "surface", "efficiency": 0.6, "efficiency_percent": "60%"},
    {"method": "flood", "efficiency": 0.5, "efficiency_percent": "50%"},
    {"method": "furrow", "efficiency": 0.55, "efficiency_percent": "55%"}
  ]
}
```

#### POST /v1/irrigation/recommend
Get complete irrigation recommendation.

**Request Body (IrrigationRecommendationInput):**
```json
{
  "crop_type": "wheat",
  "growth_stage": "mid_season",
  "soil_type": "loam",
  "irrigation_method": "drip",
  "field_area_hectares": 5.0,
  "last_irrigation_date": "2025-01-20",
  "last_irrigation_amount": 30.0,
  "current_soil_moisture": null,
  "weather": {
    "temperature_max": 35.0,
    "temperature_min": 22.0,
    "humidity": 45.0,
    "wind_speed": 2.5,
    "latitude": 15.35,
    "altitude": 2200,
    "calculation_date": "2025-01-25"
  }
}
```

**Response (IrrigationRecommendation):**
```json
{
  "recommendation_id": "uuid-string",
  "timestamp": "2025-01-25T10:00:00Z",
  "crop_type": "wheat",
  "crop_name_ar": "القمح",
  "growth_stage": "mid_season",
  "field_area_hectares": 5.0,
  "et0": 5.82,
  "kc": 1.15,
  "etc": 6.69,
  "soil_type": "loam",
  "soil_type_ar": "طميي",
  "estimated_moisture": 0.175,
  "moisture_depletion_percent": 58.5,
  "irrigation_needed": true,
  "urgency": "medium",
  "urgency_ar": "متوسط",
  "recommended_amount_mm": 35.2,
  "recommended_amount_liters": 1760000,
  "recommended_amount_m3": 1760.0,
  "gross_irrigation_mm": 39.1,
  "optimal_time": "Early morning (6-8 AM) or late evening (6-8 PM)",
  "optimal_time_ar": "الصباح الباكر (6-8 صباحاً) أو المساء (6-8 مساءً)",
  "next_irrigation_days": 3,
  "advice": "Irrigation recommended. Apply 39.1 mm (1760.0 m3) using drip method.",
  "advice_ar": "يُنصح بالري. أضف 39.1 مم (1760.0 متر مكعب) باستخدام طريقة drip.",
  "warnings": ["Critical growth stage - avoid water stress"],
  "warnings_ar": ["مرحلة نمو حرجة - تجنب إجهاد الماء"]
}
```

#### GET /v1/irrigation/quick-check
Quick irrigation check without full weather data (simplified ET0 estimation).

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `crop_type` | string | Yes | Crop type identifier |
| `growth_stage` | GrowthStage | Yes | Current growth stage |
| `soil_type` | SoilType | No (default: loam) | Soil type |
| `days_since_irrigation` | int | Yes | Days since last irrigation |
| `temperature` | float | Yes | Average temperature (C) |
| `humidity` | float | No (default: 50) | Relative humidity (%) |

**Response:**
```json
{
  "crop_type": "wheat",
  "crop_name_ar": "القمح",
  "growth_stage": "mid_season",
  "days_since_irrigation": 5,
  "estimated_et0": 4.5,
  "kc": 1.15,
  "estimated_etc": 5.18,
  "estimated_water_loss_mm": 25.9,
  "estimated_depletion_percent": 86,
  "status": "irrigate_now",
  "status_ar": "ري الآن",
  "needs_irrigation": true,
  "recommendation": "Irrigate now",
  "recommendation_ar": "قم بالري الآن"
}
```

---

### Field-First ActionTemplate Endpoints

#### POST /v1/irrigation/recommend-with-action
Get irrigation recommendation with ActionTemplate for mobile app integration.

**Request Body (VirtualSensorActionRequest):**
```json
{
  "field_id": "field-001",
  "farmer_id": "farmer-001",
  "tenant_id": "tenant-001",
  "crop_type": "wheat",
  "growth_stage": "mid_season",
  "soil_type": "loam",
  "irrigation_method": "drip",
  "field_area_hectares": 5.0,
  "last_irrigation_date": "2025-01-20",
  "last_irrigation_amount": 30.0,
  "weather": { /* WeatherInput */ },
  "publish_event": true
}
```

**Response:**
```json
{
  "recommendation": {
    "recommendation_id": "uuid",
    "crop_type": "wheat",
    "crop_name_ar": "القمح",
    "et0": 5.82,
    "kc": 1.15,
    "etc": 6.69,
    "moisture_depletion_percent": 58.5,
    "irrigation_needed": true,
    "urgency": "medium",
    "urgency_ar": "متوسط",
    "recommended_amount_mm": 35.2,
    "recommended_amount_m3": 1760.0,
    "optimal_time_ar": "الصباح الباكر (6-8 صباحاً) أو المساء (6-8 مساءً)",
    "next_irrigation_days": 3,
    "advice_ar": "يُنصح بالري...",
    "warnings_ar": ["مرحلة نمو حرجة..."]
  },
  "action_template": {
    "action_id": "uuid",
    "action_type": "irrigation",
    "title_ar": "ري تقديري - متوسط",
    "title_en": "Virtual Irrigation - medium",
    "description_ar": "...",
    "description_en": "...",
    "summary_ar": "رطوبة التربة: 42% | ET: 6.7 مم/يوم",
    "source_service": "virtual-sensors",
    "source_analysis_type": "virtual_soil_moisture",
    "confidence": 0.75,
    "urgency": "medium",
    "field_id": "field-001",
    "farmer_id": "farmer-001",
    "tenant_id": "tenant-001",
    "offline_executable": true,
    "fallback_instructions_ar": "في حال عدم توفر البيانات، قم بفحص رطوبة التربة يدوياً بعمق 15 سم",
    "fallback_instructions_en": "If data unavailable, manually check soil moisture at 15cm depth",
    "estimated_duration_minutes": 78,
    "data": {
      "et0": 5.82,
      "kc": 1.15,
      "etc": 6.69,
      "is_virtual": true
    },
    "badge": {
      "type": "virtual_estimate",
      "label_ar": "تقدير افتراضي",
      "label_en": "Virtual Estimate",
      "color": "#6366F1"
    },
    "created_at": "2025-01-25T10:00:00Z"
  },
  "task_card": {
    "id": "uuid",
    "type": "irrigation",
    "title_ar": "ري تقديري - متوسط",
    "title_en": "Virtual Irrigation - medium",
    "urgency": {
      "level": "medium",
      "label_ar": "متوسط",
      "color": "#EAB308"
    },
    "field_id": "field-001",
    "confidence_percent": 75,
    "offline_ready": true,
    "badge": { /* badge object */ },
    "irrigation_needed": true,
    "water_m3": 1760.0
  },
  "is_virtual": true,
  "nats_published": true
}
```

#### GET /v1/quick-check-with-action
Quick check with ActionTemplate for rural environments without IoT.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `field_id` | string | Yes | Field identifier |
| `farmer_id` | string | No | Farmer identifier |
| `crop_type` | string | Yes | Crop type |
| `growth_stage` | GrowthStage | Yes | Growth stage |
| `soil_type` | SoilType | No (default: loam) | Soil type |
| `days_since_irrigation` | int | Yes | Days since last irrigation |
| `temperature` | float | Yes | Temperature (C) |
| `humidity` | float | No (default: 50) | Humidity (%) |

**Response:**
```json
{
  "quick_check": { /* quick check result */ },
  "action_template": {
    "action_id": "uuid",
    "action_type": "irrigation|monitoring",
    "title_ar": "...",
    "title_en": "...",
    "source_service": "virtual-sensors",
    "confidence": 0.70,
    "urgency": "medium",
    "field_id": "field-001",
    "offline_executable": true,
    "badge": {
      "type": "virtual_quick",
      "label_ar": "فحص سريع",
      "label_en": "Quick Check",
      "color": "#8B5CF6"
    },
    "data": { /* quick check data */ }
  },
  "is_virtual": true
}
```

---

## NATS Events

### Events Published

| Event Type | Subject | Trigger | Description |
|------------|---------|---------|-------------|
| `virtual_sensor.irrigation_needed` | `sahool.analysis.virtual_sensor_irrigation_needed` | POST /v1/irrigation/recommend-with-action | Published when irrigation is needed and `publish_event: true` |

**Event Payload (AnalysisEvent):**
```json
{
  "event_id": "uuid",
  "event_type": "virtual_sensor.irrigation_needed",
  "source_service": "virtual-sensors",
  "timestamp": "2025-01-25T10:00:00Z",
  "tenant_id": "tenant-001",
  "field_id": "field-001",
  "farmer_id": "farmer-001",
  "data": {
    "et0": 5.82,
    "kc": 1.15,
    "etc": 6.69,
    "soil_type": "loam",
    "moisture_depletion_percent": 58.5,
    "recommended_amount_mm": 35.2,
    "recommended_amount_m3": 1760.0,
    "next_irrigation_days": 3,
    "is_virtual": true
  },
  "action_template": { /* ActionTemplate object */ },
  "notification_priority": "medium",
  "notification_channels": ["in_app"]
}
```

### Events Consumed

According to `governance/services.yaml`:

| Event | Source | Description |
|-------|--------|-------------|
| `SensorReadingIngested.v1` | iot-service | IoT sensor readings for calibration |
| `WeatherObserved.v1` | weather-service | Weather data updates |
| `IndexTileReady.v1` | vegetation-analysis-service | NDVI/vegetation index data |

**Note:** The current implementation does not have explicit NATS subscription handlers. Event consumption is expected but not implemented.

---

## Data Models (Enums)

### GrowthStage
```python
class GrowthStage(str, Enum):
    INITIAL = "initial"        # المرحلة الأولية
    DEVELOPMENT = "development" # مرحلة النمو
    MID_SEASON = "mid_season"   # منتصف الموسم
    LATE_SEASON = "late_season" # نهاية الموسم
```

### SoilType
```python
class SoilType(str, Enum):
    SANDY = "sandy"            # رملي
    SANDY_LOAM = "sandy_loam"  # رملي طميي
    LOAM = "loam"              # طميي
    CLAY_LOAM = "clay_loam"    # طيني طميي
    CLAY = "clay"              # طيني
    SILTY_CLAY = "silty_clay"  # طيني غريني
```

### IrrigationMethod
```python
class IrrigationMethod(str, Enum):
    DRIP = "drip"           # تنقيط
    SPRINKLER = "sprinkler" # رش
    SURFACE = "surface"     # سطحي
    FLOOD = "flood"         # غمر
    FURROW = "furrow"       # أخاديد
```

### UrgencyLevel
```python
class UrgencyLevel(str, Enum):
    NONE = "none"         # لا حاجة
    LOW = "low"           # منخفض
    MEDIUM = "medium"     # متوسط
    HIGH = "high"         # عالي
    CRITICAL = "critical" # حرج
```

---

## Algorithms

### FAO-56 Penman-Monteith ET0 Calculation

The service implements the full FAO-56 Penman-Monteith equation:

```
ET0 = [0.408 * Delta * (Rn - G) + gamma * (900/(T+273)) * u2 * (es - ea)] / [Delta + gamma * (1 + 0.34 * u2)]
```

**Key Calculations:**
1. **Saturation Vapor Pressure (es):** Using Magnus formula
2. **Actual Vapor Pressure (ea):** From relative humidity
3. **Slope of Saturation Curve (Delta)**
4. **Psychrometric Constant (gamma):** Adjusted for altitude
5. **Net Radiation (Rn):** From solar radiation or estimated from temperature range
6. **Solar Radiation Estimation:** Angstrom formula or Hargreaves method

### Crop Coefficient (Kc) Interpolation

- **Initial Stage:** Uses `kc_initial`
- **Development Stage:** Linear interpolation from `kc_initial` to `kc_mid`
- **Mid-Season Stage:** Uses `kc_mid`
- **Late Season Stage:** Linear decline from `kc_mid` to `kc_end`

### Soil Moisture Estimation (Water Balance Method)

```
Remaining Available Water = Input Water - Total ET Loss
Depletion % = (TAW - Remaining AW) / TAW * 100
```

Where:
- **Total Available Water (TAW)** = (Field Capacity - Wilting Point) * Root Depth * 1000
- **Effective Rainfall** = Rainfall * 0.80 (80% efficiency)
- **Total ET Loss** = Daily ETc * Days Since Irrigation

### Irrigation Recommendation Algorithm

1. Calculate Management Allowed Depletion (MAD) = Depletion Fraction * 100
2. Irrigation needed if: Depletion > (MAD - 10%)
3. Required irrigation = Deficit * 1.1 (10% for distribution uniformity)
4. Gross irrigation = Required / Irrigation Efficiency
5. Days until next irrigation = Remaining Allowable Depletion / Daily ETc

---

## Dependencies

### Python Dependencies (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.126.0 | Web framework |
| starlette | >=0.49.1 | ASGI framework |
| uvicorn[standard] | >=0.30.0,<1.0.0 | ASGI server |
| python-multipart | 0.0.18 | Form data parsing |
| pydantic | 2.9.2 | Data validation |
| pydantic-settings | 2.7.1 | Settings management |
| httpx | 0.28.1 | HTTP client |
| aiohttp | >=3.11.12 | Async HTTP (security fix) |
| python-dateutil | 2.8.2 | Date utilities |
| numpy | >=1.26.0,<2.1.0 | Numerical calculations |
| pytest | 8.3.4 | Testing |
| pytest-asyncio | 0.24.0 | Async testing |
| python-dotenv | 1.0.1 | Environment variables |
| structlog | >=24.1.0 | Structured logging |

### Service Dependencies

| Service | Purpose |
|---------|---------|
| postgres | Database storage (configured but not actively used in current implementation) |
| nats | Event publishing |
| weather-service | Weather data source |
| vegetation-analysis-service | NDVI/vegetation index data |

### Shared Modules

| Module | Path | Purpose |
|--------|------|---------|
| errors_py | shared/errors_py.py | Unified error handling |
| nats_publisher | shared/libs/events/nats_publisher.py | NATS event publishing |

---

## Environment Variables

### Configured in docker-compose.yml

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | 8119 | No | Service port |
| `LOG_LEVEL` | INFO | No | Logging level |
| `ENVIRONMENT` | development | No | Environment name |
| `DATABASE_URL` | - | Yes | PostgreSQL connection string |
| `NATS_URL` | - | Yes | NATS connection URL |

### Used in Code

| Variable | Default | Used In | Description |
|----------|---------|---------|-------------|
| `PORT` | 8119 | main.py | Service port |
| `CORS_ALLOWED_ORIGINS` | localhost:3000,3001,8080 | main.py | CORS origins |

### Missing Environment Variables

The following environment variables are referenced in README.md but NOT used in code:

| Variable | Purpose | Status |
|----------|---------|--------|
| `HOST` | Server host binding | **NOT IMPLEMENTED** (hardcoded to 0.0.0.0) |
| `SATELLITE_SERVICE_URL` | Satellite service integration | **NOT IMPLEMENTED** |
| `WEATHER_SERVICE_URL` | Weather service integration | **NOT IMPLEMENTED** |
| `MODEL_UPDATE_INTERVAL_HOURS` | Model refresh interval | **NOT IMPLEMENTED** |

---

## Bugs, Errors, and Recommended Fixes

### Critical Issues

#### 1. Version Mismatch
**Location:** `/apps/services/virtual-sensors/src/main.py`
**Issue:** Inconsistent version numbers across the service.
- `SERVICE_VERSION = "15.5.0"` (line 55)
- `/readyz` returns `"version": "16.0.0"` (line 1017)
- Dockerfile label: `version="2.0.0"` (line 41)
- README.md states: `15.4.0`

**Recommendation:** Standardize to `16.0.0` across all files.

#### 2. Database Connection Not Used
**Location:** `/apps/services/virtual-sensors/src/main.py`
**Issue:** `DATABASE_URL` is configured in docker-compose but there is no database connection or persistence in the service. All data is computed in-memory.

**Impact:** No historical data storage, no calibration persistence.

**Recommendation:** Either:
- Remove DATABASE_URL from docker-compose if not needed
- Implement database storage for calculations and calibration data

#### 3. NATS Subscription Not Implemented
**Location:** `/apps/services/virtual-sensors/src/main.py`
**Issue:** According to `governance/services.yaml`, the service should consume events:
- `SensorReadingIngested.v1`
- `WeatherObserved.v1`
- `IndexTileReady.v1`

But there are no NATS subscription handlers implemented.

**Recommendation:** Implement NATS subscription handlers in the lifespan context or add a note that this is not yet implemented.

### Medium Issues

#### 4. Unused Variable
**Location:** `/apps/services/virtual-sensors/src/main.py`, line 840
**Issue:** `SOIL_PROPERTIES[soil_type]` is called but the result is not assigned to any variable.
```python
def calculate_irrigation_recommendation(...):
    ...
    SOIL_PROPERTIES[soil_type]  # Line 840 - result not used
    efficiency = IRRIGATION_EFFICIENCY[irrigation_method]
```

**Recommendation:** Remove the line or assign to variable if needed.

#### 5. Unused Variable in Quick Check
**Location:** `/apps/services/virtual-sensors/src/main.py`, line 1374
**Issue:** `remaining_water` is calculated but never used.
```python
typical_irrigation - total_et_loss  # Line 1374 - result not assigned/used
depletion = (total_et_loss / typical_irrigation) * 100
```

**Recommendation:** Remove the line or use the calculated value.

#### 6. Port Mismatch in README
**Location:** `/apps/services/virtual-sensors/README.md`, line 9
**Issue:** README states `Port: 8096` but actual port is `8119`.

**Recommendation:** Update README to reflect correct port 8119.

#### 7. Health Endpoint Mismatch
**Location:** `governance/services.yaml`
**Issue:** Services.yaml defines `health_endpoint: "/health"` but the service implements `/healthz`.

**Recommendation:** Either update services.yaml to `/healthz` or add a `/health` alias endpoint.

### Minor Issues

#### 8. NATS Connection State Never Set
**Location:** `/apps/services/virtual-sensors/src/main.py`, line 1000
**Issue:** Health check references `app.state.nats_client` but this is never set in the lifespan handler.

```python
nats_connected = hasattr(app.state, "nats_client") and app.state.nats_client is not None
```

**Recommendation:** Add NATS connection setup in lifespan handler or remove from health check.

#### 9. Deprecated asyncio.get_event_loop() Usage
**Location:** `/shared/libs/events/nats_publisher.py`, line 293
**Issue:** Using deprecated `asyncio.get_event_loop()` pattern.

**Recommendation:** Use `asyncio.get_running_loop()` or handle DeprecationWarning.

#### 10. Missing Test Coverage
**Location:** `/apps/services/virtual-sensors/tests/test_virtual_sensors.py`
**Issue:** Tests use a mocked FastAPI app instead of testing the actual implementation. None of the actual endpoints are tested.

**Recommendation:** Update tests to use the actual `src/main.py` app with TestClient.

### Recommendations

#### 1. Add Database Persistence
Implement database storage for:
- Historical ET0/ETc calculations
- Irrigation recommendations history
- Field-specific calibration data

#### 2. Implement Weather Service Integration
Add actual integration with weather-service to fetch real-time weather data instead of requiring manual input.

#### 3. Add NATS Event Subscriptions
Implement handlers for the events listed in governance/services.yaml.

#### 4. Add API Rate Limiting
Consider adding rate limiting middleware for public endpoints.

#### 5. Add Request Validation
Add validation for crop_type against CROP_COEFFICIENTS dictionary in all endpoints.

---

## Kong Gateway Configuration

```yaml
- name: virtual-sensors
  host: virtual-sensors
  port: 8119
  protocol: http
  routes:
    - name: virtual-sensors-route
      paths: ["/api/v1/virtual-sensors", "/virtual-sensors"]
      strip_path: true
      protocols: ["http", "https"]
```

**Gateway URLs:**
- `http://kong:8000/api/v1/virtual-sensors/*`
- `http://kong:8000/virtual-sensors/*`

---

## Docker Configuration

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 384M
    reservations:
      cpus: '0.25'
      memory: 128M
```

### Health Check

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8119/healthz')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 15s
```

---

## File Structure

```
apps/services/virtual-sensors/
├── Dockerfile              # Multi-stage Docker build
├── .dockerignore           # Docker ignore patterns
├── README.md               # Service documentation (outdated port)
├── requirements.txt        # Python dependencies
├── src/
│   └── main.py             # Main FastAPI application (1691 lines)
└── tests/
    ├── __init__.py
    └── test_virtual_sensors.py  # Unit tests (mocked)
```

---

## Related Services

| Service | Relationship |
|---------|--------------|
| weather-service | Provides weather data for ET0 calculations |
| vegetation-analysis-service | Provides NDVI data for virtual sensor calibration |
| iot-service | Provides real sensor data for comparison/calibration |
| notification-service | Receives NATS events for farmer notifications |
| irrigation-smart | Complementary irrigation service in Decision layer |

---

## Changelog Notes

- **v15.5.0**: Current implementation with FAO-56 Penman-Monteith
- **v15.4.0**: Previous version mentioned in README
- **v16.0.0**: Target version for unified platform

---

*Generated: 2026-01-25*
*Service Path: /home/user/sahool-unified-v15-idp/apps/services/virtual-sensors/*
