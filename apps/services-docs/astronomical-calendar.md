# Astronomical Calendar Service Analysis

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | astronomical-calendar |
| **Arabic Name** | خدمة التقويم الفلكي الزراعي |
| **Type** | Python/FastAPI |
| **Port** | 8111 |
| **Version** | 15.5.0 (16.0.0 in readiness probe) |
| **Description** | Traditional Yemeni astronomical farming calendar combining precise astronomical calculations with traditional agricultural knowledge |

### Core Features

1. **Moon Phase Calculations (مراحل القمر)** - Precise lunar phase calculations with illumination percentage
2. **Lunar Mansions (المنازل القمرية)** - 28 traditional lunar mansions with farming recommendations
3. **Hijri Calendar** - Gregorian to Hijri date conversion
4. **Agricultural Zodiac** - Zodiac signs with farming fertility scores
5. **Yemeni Seasons** - Traditional Yemeni agricultural seasons
6. **Weather Integration** - Integration with weather-service for combined recommendations
7. **Traditional Wisdom** - Extensive collection of Yemeni farming proverbs and techniques

---

## Kong Gateway Configuration

```yaml
host: astronomical-calendar
port: 8111
routes:
  - /api/v1/astronomy
  - /astronomy (strip_path: true)
```

---

## API Endpoints

### Health Endpoints

| Method | Path | Response Model | Description |
|--------|------|----------------|-------------|
| GET | `/healthz` | JSON | Health check - liveness probe |
| GET | `/readyz` | JSON | Kubernetes readiness probe |

#### Health Response Schema
```json
{
  "status": "healthy",
  "service": "astronomical-calendar",
  "version": "15.5.0",
  "timestamp": "2026-01-25T12:00:00.000000"
}
```

---

### Calendar Endpoints

| Method | Path | Response Model | Description |
|--------|------|----------------|-------------|
| GET | `/v1/today` | DailyAstronomicalData | Get today's astronomical data |
| GET | `/v1/date/{date_str}` | DailyAstronomicalData | Get astronomical data for specific date |
| GET | `/v1/week` | WeeklyForecast | Weekly astronomical forecast |
| GET | `/v1/best-days` | JSON | Find best days for specific farming activity |
| GET | `/v1/current-season` | SeasonInfo | Get current Yemeni season |
| GET | `/v1/hijri` | HijriDate | Convert Gregorian to Hijri date |
| GET | `/v1/hijri-months` | JSON | List all Hijri months |

#### GET /v1/today
Returns comprehensive astronomical data for the current date.

**Response Schema (DailyAstronomicalData):**
```json
{
  "date_gregorian": "2026-01-25",
  "date_hijri": {
    "year": 1447,
    "month": 7,
    "day": 15,
    "month_name": "رجب",
    "month_name_en": "Rajab",
    "weekday": "الأحد"
  },
  "moon_phase": {
    "phase_key": "full_moon",
    "name": "البدر",
    "name_en": "Full Moon",
    "icon": "🌕",
    "illumination": 98.5,
    "age_days": 14.75,
    "is_waxing": false,
    "farming_good": true
  },
  "lunar_mansion": {
    "number": 3,
    "name": "الثريا",
    "name_en": "Al-Thuraya",
    "constellation": "الثور",
    "constellation_en": "Taurus",
    "element": "أرض",
    "farming": "ممتازة للزراعة",
    "farming_score": 10,
    "crops": ["جميع المحاصيل"],
    "activities": ["زراعة", "غرس", "تطعيم", "تقليم"],
    "avoid": [],
    "description": "أفضل المنازل للزراعة على الإطلاق - نجم الثريا المبارك"
  },
  "zodiac": {
    "name": "الدلو",
    "name_en": "Aquarius",
    "element": "هواء",
    "fertility": "جافة",
    "score": 4
  },
  "season": {
    "name": "الشتاء",
    "name_en": "Shita (Winter)",
    "description": "موسم زراعة الخضروات الشتوية",
    "main_crops": ["قمح", "شعير", "خضروات"],
    "activities": ["زراعة القمح", "ري"]
  },
  "overall_farming_score": 8,
  "recommendations": [
    {
      "activity": "زراعة",
      "suitability": "ممتازة",
      "suitability_score": 9,
      "reason": "المنزلة والقمر مناسبان",
      "best_time": "الصباح الباكر"
    }
  ]
}
```

#### GET /v1/date/{date_str}
**Path Parameters:**
- `date_str` (string, required): Date in YYYY-MM-DD format

**Response:** Same as `/v1/today`

#### GET /v1/week
**Query Parameters:**
- `start_date` (string, optional): Start date in YYYY-MM-DD format

**Response Schema (WeeklyForecast):**
```json
{
  "start_date": "2026-01-25",
  "end_date": "2026-01-31",
  "days": [/* Array of DailyAstronomicalData */],
  "best_planting_days": ["2026-01-25", "2026-01-27"],
  "best_harvesting_days": ["2026-01-28"],
  "avoid_days": ["2026-01-29"]
}
```

#### GET /v1/best-days
**Query Parameters:**
- `activity` (string, required): Activity type (زراعة, حصاد, ري, تقليم, etc.)
- `days` (integer, optional, default=30): Number of days to search

**Response:**
```json
{
  "activity": "زراعة",
  "search_period_days": 30,
  "best_days": [
    {
      "date": "2026-01-27",
      "score": 9,
      "lunar_mansion": "الثريا",
      "moon_phase": "الهلال المتزايد"
    }
  ],
  "total_found": 5
}
```

---

### Astronomy Endpoints

| Method | Path | Response Model | Description |
|--------|------|----------------|-------------|
| GET | `/v1/moon-phase` | MoonPhase | Get current moon phase |
| GET | `/v1/lunar-mansion` | LunarMansion | Get current lunar mansion |
| GET | `/v1/lunar-mansions` | JSON | List all 28 lunar mansions |
| GET | `/v1/zodiac` | ZodiacInfo | Get current zodiac sign |
| GET | `/v1/zodiac-farming` | JSON | List zodiac signs with fertility info |

#### GET /v1/moon-phase
**Query Parameters:**
- `date_str` (string, optional): Date in YYYY-MM-DD format

**Response Schema (MoonPhase):**
```json
{
  "phase_key": "waxing_crescent",
  "name": "الهلال المتزايد",
  "name_en": "Waxing Crescent",
  "icon": "🌒",
  "illumination": 25.3,
  "age_days": 3.75,
  "is_waxing": true,
  "farming_good": true
}
```

#### GET /v1/lunar-mansion
**Query Parameters:**
- `date_str` (string, optional): Date in YYYY-MM-DD format

**Response Schema (LunarMansion):**
```json
{
  "number": 15,
  "name": "الغفر",
  "name_en": "Al-Ghafr",
  "constellation": "الميزان",
  "constellation_en": "Libra",
  "element": "هواء",
  "farming": "جيدة",
  "farming_score": 6,
  "crops": ["زهور", "نباتات زينة"],
  "activities": ["زراعة الزهور"],
  "avoid": ["غرس أشجار"],
  "description": "مناسبة للنباتات الجمالية"
}
```

#### GET /v1/lunar-mansions
**Response:**
```json
{
  "mansions": [
    {
      "number": 1,
      "name": "الشرطين",
      "name_en": "Al-Sharatain",
      "constellation": "الحمل",
      "element": "نار",
      "farming_score": 9,
      "crops": ["قمح", "شعير", "ذرة"]
    }
    // ... 28 total mansions
  ],
  "total": 28
}
```

---

### Crops Endpoints

| Method | Path | Response Model | Description |
|--------|------|----------------|-------------|
| GET | `/v1/crops` | JSON | List supported crops |
| GET | `/v1/crop-calendar/{crop_name}` | CropCalendar | Get crop-specific planting calendar |
| GET | `/v1/crop-details` | JSON | List detailed crop information |
| GET | `/v1/crop-details/{crop_id}` | JSON | Get full crop details |
| GET | `/v1/crop-details/{crop_id}/planting-guide` | JSON | Get crop planting guide |
| GET | `/v1/what-to-plant` | JSON | Recommend what to plant now |

#### GET /v1/crop-calendar/{crop_name}
**Path Parameters:**
- `crop_name` (string, required): Arabic crop name (e.g., "قمح", "بن")

**Response Schema (CropCalendar):**
```json
{
  "crop_name": "قمح",
  "crop_name_en": "Wheat",
  "best_planting_mansions": [1, 3, 4, 13, 14, 24],
  "best_moon_phases": ["waxing_crescent", "first_quarter", "waxing_gibbous"],
  "best_zodiac_signs": ["taurus", "cancer", "virgo", "scorpio", "pisces"],
  "optimal_months": [10, 11, 12, 1],
  "planting_guide": "يُزرع القمح في أوائل الشتاء...",
  "current_suitability": 8
}
```

#### GET /v1/what-to-plant
**Query Parameters:**
- `region` (string, optional): Region ID (tihama, central_highlands, etc.)
- `month` (integer, optional): Month number (1-12)

**Response:**
```json
{
  "date": "2026-01-25",
  "region": "central_highlands",
  "month": 1,
  "recommended_crops": [
    {
      "crop_id": "wheat",
      "name": "قمح",
      "suitability_score": 9,
      "reason": "الشهر المثالي للزراعة في المرتفعات"
    }
  ],
  "astronomical_context": {
    "lunar_mansion": "الثريا",
    "moon_phase": "الهلال المتزايد",
    "overall_score": 8
  }
}
```

---

### Reference Endpoints

| Method | Path | Response Model | Description |
|--------|------|----------------|-------------|
| GET | `/v1/seasons` | JSON | List Yemeni agricultural seasons |
| GET | `/v1/regions` | JSON | List Yemeni agricultural regions |
| GET | `/v1/regions/{region_id}` | JSON | Get region details |
| GET | `/v1/regions/{region_id}/crops` | JSON | Get crops for a region |

#### GET /v1/regions
**Response:**
```json
{
  "total_regions": 5,
  "regions": [
    {
      "id": "tihama",
      "name": "سهل تهامة",
      "name_en": "Tihama Coastal Plain",
      "governorates": ["الحديدة", "تعز", "لحج"],
      "climate_type": "حار رطب"
    }
  ]
}
```

---

### Yemeni Heritage Endpoints

| Method | Path | Response Model | Description |
|--------|------|----------------|-------------|
| GET | `/v1/landmarks` | JSON | List all historical landmarks |
| GET | `/v1/landmarks/{category}` | JSON | Get landmarks by category |
| GET | `/v1/landmarks/{category}/{landmark_name}` | JSON | Get specific landmark |
| GET | `/v1/techniques` | JSON | List traditional techniques |
| GET | `/v1/techniques/{category}` | JSON | Get techniques by category |
| GET | `/v1/techniques/{category}/{technique_id}` | JSON | Get specific technique |

#### Landmark Categories
- `terraces` - Mountain terraces (المدرجات الجبلية)
- `dams` - Historical dams (السدود)
- `water_systems` - Traditional water systems (أنظمة المياه)
- `storage` - Storage facilities (المخازن)

#### Technique Categories
- `plowing` - Plowing techniques (الحراثة)
- `irrigation` - Irrigation methods (الري)
- `fertilization` - Fertilization methods (التسميد)
- `harvesting` - Harvesting techniques (الحصاد)
- `processing` - Processing methods (المعالجة)
- `pest_control` - Pest control methods (مكافحة الآفات)

---

### Yemeni Wisdom Endpoints

| Method | Path | Response Model | Description |
|--------|------|----------------|-------------|
| GET | `/v1/proverbs` | JSON | Get all farming proverbs |
| GET | `/v1/proverbs/today` | JSON | Get proverb of the day |
| GET | `/v1/proverbs/crop/{crop_name}` | JSON | Get proverbs for a crop |
| GET | `/v1/proverbs/mansion/{mansion_name}` | JSON | Get proverbs for a lunar mansion |
| GET | `/v1/stars` | JSON | Get important agricultural stars |
| GET | `/v1/stars/{star_name}` | JSON | Get star information |
| GET | `/v1/wisdom/today` | JSON | Get comprehensive daily wisdom |

#### GET /v1/proverbs/today
**Response:**
```json
{
  "date": "2026-01-25",
  "proverb": {
    "proverb": "الزرع في الثريا، والحصاد في الجوزاء",
    "meaning": "أفضل وقت للزراعة في منزلة الثريا، والحصاد في الجوزاء",
    "application": "توقيت الزراعة والحصاد",
    "mansion": "الثريا"
  },
  "current_context": {
    "lunar_mansion": "الثريا",
    "moon_phase": "البدر",
    "relevance": "هذا المثل مناسب جداً لليوم"
  }
}
```

---

### Integration Endpoints

| Method | Path | Response Model | Description |
|--------|------|----------------|-------------|
| GET | `/v1/integration/weather` | JSON | Integrate with weather service |

#### GET /v1/integration/weather
**Query Parameters:**
- `location_id` (string, optional, default="sanaa"): Location identifier
- `date_str` (string, optional): Date in YYYY-MM-DD format

**Response:**
```json
{
  "date": "2026-01-25",
  "location_id": "sanaa",
  "astronomical": {
    "hijri_date": {/* HijriDate */},
    "moon_phase": {/* MoonPhase */},
    "lunar_mansion": {/* LunarMansion */},
    "zodiac": {/* ZodiacInfo */},
    "season": {/* SeasonInfo */},
    "overall_score": 8
  },
  "weather": {
    "temperature": 22,
    "humidity": 45,
    "condition": "صافي"
  },
  "integrated_recommendations": [
    {
      "activity": "ري",
      "suitability": "جيدة",
      "suitability_score": 7,
      "reason": "المنزلة مناسبة",
      "weather_note": "⚠️ درجة الحرارة مرتفعة - يُنصح بالري في الصباح الباكر أو المساء"
    }
  ],
  "summary_ar": "اليوم في منزلة الثريا، والقمر البدر. درجة ملاءمة الزراعة: 8/10"
}
```

---

## Pydantic Data Models

### MoonPhase
```python
class MoonPhase(BaseModel):
    phase_key: str          # Phase identifier (new_moon, waxing_crescent, etc.)
    name: str               # Arabic name
    name_en: str            # English name
    icon: str               # Emoji icon
    illumination: float     # 0-100 percentage
    age_days: float         # Moon age in days
    is_waxing: bool         # True if waxing, False if waning
    farming_good: bool      # True if good for farming
```

### LunarMansion
```python
class LunarMansion(BaseModel):
    number: int             # 1-28
    name: str               # Arabic name
    name_en: str            # English name
    constellation: str      # Arabic zodiac constellation
    constellation_en: str   # English zodiac constellation
    element: str            # Element (نار, أرض, هواء, ماء)
    farming: str            # Farming status description
    farming_score: int      # 1-10 suitability score
    crops: list[str]        # Recommended crops
    activities: list[str]   # Recommended activities
    avoid: list[str]        # Activities to avoid
    description: str        # Full description
```

### HijriDate
```python
class HijriDate(BaseModel):
    year: int               # Hijri year
    month: int              # 1-12
    day: int                # 1-30
    month_name: str         # Arabic month name
    month_name_en: str      # English month name
    weekday: str            # Arabic weekday name
```

### ZodiacInfo
```python
class ZodiacInfo(BaseModel):
    name: str               # Arabic name
    name_en: str            # English name
    element: str            # Element
    fertility: str          # Fertility description
    score: int              # 1-10 farming suitability
```

### SeasonInfo
```python
class SeasonInfo(BaseModel):
    name: str               # Arabic name
    name_en: str            # English name
    description: str        # Description
    main_crops: list[str]   # Main crops for season
    activities: list[str]   # Recommended activities
```

### FarmingRecommendation
```python
class FarmingRecommendation(BaseModel):
    activity: str           # Activity name
    suitability: str        # Suitability description
    suitability_score: int  # 1-10
    reason: str             # Reason for recommendation
    best_time: str | None   # Best time of day
```

### DailyAstronomicalData
```python
class DailyAstronomicalData(BaseModel):
    date_gregorian: str
    date_hijri: HijriDate
    moon_phase: MoonPhase
    lunar_mansion: LunarMansion
    zodiac: ZodiacInfo
    season: SeasonInfo
    overall_farming_score: int
    recommendations: list[FarmingRecommendation]
```

### WeeklyForecast
```python
class WeeklyForecast(BaseModel):
    start_date: str
    end_date: str
    days: list[DailyAstronomicalData]
    best_planting_days: list[str]
    best_harvesting_days: list[str]
    avoid_days: list[str]
```

### CropCalendar
```python
class CropCalendar(BaseModel):
    crop_name: str
    crop_name_en: str
    best_planting_mansions: list[int]
    best_moon_phases: list[str]
    best_zodiac_signs: list[str]
    optimal_months: list[int]
    planting_guide: str
    current_suitability: int
```

---

## NATS Events

**This service does not publish or subscribe to any NATS events.**

The astronomical-calendar service operates as a stateless calculation service. It provides astronomical data on-demand via REST API and does not participate in the event-driven architecture.

---

## Islamic Calendar & Prayer Time Calculations

### Hijri Calendar Conversion

The service implements a custom Gregorian-to-Hijri conversion algorithm:

```python
def gregorian_to_hijri(year: int, month: int, day: int) -> HijriDate:
    """
    Converts Gregorian date to Hijri using astronomical calculation.
    Reference: Umm al-Qura calendar approximation.
    """
```

**Algorithm:**
1. Calculate Julian Day Number
2. Use reference point (July 16, 622 CE = 1 Muharram 1 AH)
3. Calculate days since reference
4. Compute Hijri year, month, day using lunar month cycle (29.530588853 days)

### Moon Phase Calculation

Uses the synodic month algorithm:
- **Reference New Moon**: January 6, 2000 at 18:14 UTC
- **Synodic Month**: 29.530588853 days
- **Illumination Formula**: `(1 - cos(2π × moon_age / synodic_month)) / 2 × 100`

### Lunar Mansion Calculation

The 28 lunar mansions divide the sky based on moon position:
- Each mansion spans approximately 12.86 degrees (360° / 28)
- Calculation based on moon age within the synodic cycle

**Note:** This service does not calculate actual prayer times. It focuses on astronomical data for agricultural purposes.

---

## Dependencies

### Python Dependencies (requirements.txt)

```
fastapi==0.126.0
starlette>=0.49.1
uvicorn[standard]>=0.30.0,<1.0.0
pydantic==2.9.2
httpx==0.28.1
python-dotenv==1.0.1
structlog>=24.1.0
```

### Standard Library Dependencies
- `math` - For astronomical calculations
- `os` - Environment variables
- `sys` - System path manipulation
- `datetime` - Date/time handling

### External Service Dependencies
- **weather-service** (optional): For integrated weather recommendations at `http://weather-service:8092`

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CORS_ALLOWED_ORIGINS` | No | `http://localhost:3000,http://localhost:3001,http://localhost:8080` | Comma-separated list of allowed CORS origins |
| `WEATHER_SERVICE_URL` | No | `http://weather-service:8092` | URL of the weather service for integration endpoint |
| `PORT` | No | `8111` | Service port (set in Dockerfile) |

### Missing Environment Variables

The following environment variables are **recommended but not implemented**:

| Variable | Recommended | Purpose |
|----------|-------------|---------|
| `LOG_LEVEL` | Yes | Control logging verbosity |
| `ENVIRONMENT` | Yes | Deployment environment (development, staging, production) |
| `DATABASE_URL` | No | Not needed - service is stateless |
| `NATS_URL` | No | Not needed - service doesn't use events |
| `JWT_SECRET_KEY` | Conditional | If authentication is required in future |

---

## Bugs, Errors & Recommended Fixes

### Critical Issues

#### 1. Version Mismatch
**Location:** Lines 14, 56, 3204, 3215
**Issue:** Version inconsistency between health endpoints
- `/healthz` returns version `15.5.0`
- `/readyz` returns version `16.0.0`
- FastAPI app declares version `15.5.0`

**Recommendation:**
```python
VERSION = "16.0.0"
# Use VERSION constant throughout the application
```

#### 2. Broken Error Handler Import
**Location:** Lines 44-46 (inside docstring)
**Issue:** The error handling setup code appears inside the FastAPI description docstring:
```python
description="""
    ...
# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)
    ...
"""
```

**Impact:** The unified error handlers and request ID middleware are NOT being applied.

**Recommendation:** Move these lines outside the docstring:
```python
app = FastAPI(...)

# Setup unified error handling
from shared.errors_py import add_request_id_middleware, setup_exception_handlers
setup_exception_handlers(app)
add_request_id_middleware(app)
```

### Medium Priority Issues

#### 3. Missing Input Validation for Region IDs
**Location:** `/v1/regions/{region_id}`, `/v1/regions/{region_id}/crops`
**Issue:** Region IDs are validated but error messages could be more informative.

**Recommendation:** Add Enum or list validation for region IDs.

#### 4. Unhandled Weather Service Timeout
**Location:** Line 3831
**Issue:** Generic exception handling masks connection issues:
```python
except Exception:
    weather_data = {"note": "خدمة الطقس غير متاحة حالياً"}
```

**Recommendation:**
```python
except httpx.TimeoutException:
    weather_data = {"error": "timeout", "note": "انتهت مهلة الاتصال بخدمة الطقس"}
except httpx.ConnectError:
    weather_data = {"error": "connection_error", "note": "لا يمكن الاتصال بخدمة الطقس"}
except Exception as e:
    logger.warning(f"Weather service error: {e}")
    weather_data = {"error": "unknown", "note": "خدمة الطقس غير متاحة حالياً"}
```

#### 5. UTC Time Usage Without Timezone
**Location:** Multiple endpoints using `datetime.utcnow()`
**Issue:** `datetime.utcnow()` is deprecated in Python 3.12+

**Recommendation:**
```python
from datetime import datetime, timezone
datetime.now(timezone.utc)
```

### Low Priority Issues

#### 6. Missing Structured Logging
**Issue:** Service imports `structlog` but doesn't use it.

**Recommendation:** Add structured logging throughout:
```python
import structlog
logger = structlog.get_logger()

@app.get("/v1/today")
def get_today():
    logger.info("get_today_requested", timestamp=datetime.now(timezone.utc).isoformat())
    return get_daily_astronomical_data(datetime.now(timezone.utc))
```

#### 7. Missing Metrics Endpoint
**Issue:** No `/metrics` endpoint for Prometheus monitoring.

**Recommendation:** Add prometheus metrics:
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('astronomical_requests_total', 'Total requests', ['endpoint'])
REQUEST_LATENCY = Histogram('astronomical_request_latency_seconds', 'Request latency')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### 8. Large In-Memory Data Structures
**Issue:** The service loads extensive static data (proverbs, techniques, landmarks, crops) into memory. This is not a bug but could impact container memory in resource-constrained environments.

**Recommendation:** Consider lazy loading or database storage if memory becomes an issue.

#### 9. Missing Rate Limiting
**Issue:** No rate limiting on endpoints.

**Recommendation:** Implement rate limiting via Kong Gateway or FastAPI middleware.

#### 10. sys.path Manipulation
**Location:** Line 26
**Issue:** Direct `sys.path` manipulation is fragile:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
```

**Recommendation:** Use proper Python packaging with `pyproject.toml` or `setup.py`.

---

## Data Content Summary

### Lunar Mansions (28 total)
Each mansion includes:
- Arabic and English names
- Associated constellation
- Element (fire, earth, air, water)
- Farming score (1-10)
- Recommended crops and activities
- Activities to avoid

**Best Mansions for Farming:**
| Rank | Mansion | Score | Element |
|------|---------|-------|---------|
| 1 | الثريا (Al-Thuraya) | 10 | Earth |
| 2 | سعد السعود (Sa'd al-Su'ud) | 10 | Air |
| 3 | الشرطين (Al-Sharatain) | 9 | Fire |
| 4 | السماك (Al-Simak) | 9 | Earth |

**Worst Mansions:**
| Rank | Mansion | Score | Element |
|------|---------|-------|---------|
| 1 | الشولة (Al-Shaulah) | 2 | Water |
| 2 | الطرف (Al-Tarf) | 2 | Fire |

### Moon Phases (8 phases)
- New Moon (المحاق) - farming_good: false
- Waxing Crescent (الهلال المتزايد) - farming_good: true
- First Quarter (التربيع الأول) - farming_good: true
- Waxing Gibbous (الأحدب المتزايد) - farming_good: true
- Full Moon (البدر) - farming_good: true
- Waning Gibbous (الأحدب المتناقص) - farming_good: false
- Last Quarter (التربيع الأخير) - farming_good: false
- Waning Crescent (الهلال المتناقص) - farming_good: false

### Zodiac Signs
12 signs with fertility scores (1-10):
- Cancer (السرطان): 10 - Most fertile
- Taurus (الثور): 9
- Scorpio (العقرب): 9
- Pisces (الحوت): 9
- Leo (الأسد): 2 - Least fertile

### Yemeni Regions
- Tihama (سهل تهامة) - Hot coastal plain
- Central Highlands (المرتفعات الوسطى) - Coffee country
- Hadramaut (حضرموت) - Date palm region
- Eastern Plateau (الهضبة الشرقية)
- Northern Highlands (المرتفعات الشمالية)

### Traditional Content
- **Proverbs:** 100+ Yemeni farming proverbs organized by:
  - General wisdom
  - By crop type
  - By season
  - By region
  - By activity
- **Techniques:** Traditional farming methods for:
  - Plowing (ox, manual, iron plow)
  - Irrigation (channels, flood, drip, bucket)
  - Fertilization (organic, ash, coffee grounds, green manure)
  - Harvesting (grains, coffee, honey, dates)
  - Processing (drying, milling, storage)
  - Pest control (ash, fumigation, scarecrows, clay traps)
- **Landmarks:** Historical sites including:
  - Ancient Marib Dam
  - Mountain terraces (UNESCO heritage)
  - Traditional water systems (ghayls)
  - Storage facilities

---

## Testing

### Test File
**Location:** `/home/user/sahool-unified-v15-idp/apps/services/astronomical-calendar/tests/test_calendar.py`

The test file uses a mock FastAPI app with hardcoded responses. Tests cover:
- Health endpoint
- Moon phase endpoint
- Lunar mansion endpoint
- Hijri date conversion
- Agricultural zodiac
- Planting calendar
- Yemeni seasons
- Today's comprehensive info

**Note:** Tests mock the app instead of testing the actual implementation. Consider adding integration tests against the real service.

---

## Deployment

### Docker
```bash
# Build
docker build -t sahool-astronomical-calendar .

# Run
docker run -p 8111:8111 sahool-astronomical-calendar
```

### Health Checks
```bash
# Liveness
curl http://localhost:8111/healthz

# Readiness
curl http://localhost:8111/readyz
```

### Kubernetes
The Dockerfile includes a health check configuration:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8111/healthz').raise_for_status()" || exit 1
```

---

## File Locations

| File | Path |
|------|------|
| Main Source | `/home/user/sahool-unified-v15-idp/apps/services/astronomical-calendar/src/main.py` |
| Requirements | `/home/user/sahool-unified-v15-idp/apps/services/astronomical-calendar/requirements.txt` |
| Dockerfile | `/home/user/sahool-unified-v15-idp/apps/services/astronomical-calendar/Dockerfile` |
| Tests | `/home/user/sahool-unified-v15-idp/apps/services/astronomical-calendar/tests/test_calendar.py` |
| README | `/home/user/sahool-unified-v15-idp/apps/services/astronomical-calendar/README.md` |
