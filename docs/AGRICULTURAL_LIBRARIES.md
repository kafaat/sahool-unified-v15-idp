# SAHOOL Agricultural Libraries Documentation

# وثائق المكتبات الزراعية في سهول

**Version**: 16.0.0
**Updated**: January 2026
**Author**: SAHOOL Platform Team

---

## Overview | نظرة عامة

The SAHOOL platform includes 14 specialized agricultural modules in the `shared/` directory, providing comprehensive support for Middle East farming operations. These modules integrate with SAHOOL services and support offline-first, bilingual (Arabic/English) functionality.

تتضمن منصة سهول 14 وحدة زراعية متخصصة في دليل `shared/`، تقدم دعمًا شاملاً للعمليات الزراعية في الشرق الأوسط. تتكامل هذه الوحدات مع خدمات سهول وتدعم العمل دون اتصال مع دعم ثنائي اللغة (العربية/الإنجليزية).

---

## Table of Contents | جدول المحتويات

| # | Module | الوحدة | Lines | Purpose |
|---|--------|--------|-------|---------|
| 1 | [agri_calendar](#1-agri_calendar) | التقويم الزراعي | 1,052 | Islamic calendar with agricultural seasons |
| 2 | [crop_insurance](#2-crop_insurance) | التأمين الزراعي | 1,231 | Parametric crop insurance |
| 3 | [crop_rotation](#3-crop_rotation) | الدورة الزراعية | 1,233 | AI-driven rotation planning |
| 4 | [fertilizer_management](#4-fertilizer_management) | إدارة الأسمدة | 620 | Fertilizer calculations |
| 5 | [field_boundaries](#5-field_boundaries) | حدود الحقول | 2,000+ | PostGIS boundary management |
| 6 | [harvest_quality](#6-harvest_quality) | جودة المحصول | ~800 | Harvest quality assessment |
| 7 | [irrigation](#7-irrigation) | الري التعاوني | ~1,200 | Human-Machine Collaborative irrigation |
| 8 | [ml_irrigation](#8-ml_irrigation) | الري الذكي | ~600 | ML-based irrigation prediction |
| 9 | [pest_scouting](#9-pest_scouting) | مسح الآفات | ~900 | Pest monitoring |
| 10 | [pesticide_compliance](#10-pesticide_compliance) | سلامة المبيدات | ~500 | Pesticide regulation compliance |
| 11 | [soil_sensors](#11-soil_sensors) | مجسات التربة | ~400 | Soil sensor integration |
| 12 | [soil_testing](#12-soil_testing) | تحليل التربة | ~700 | Soil testing protocols |
| 13 | [water_management](#13-water_management) | إدارة المياه | ~800 | Water resource management |
| 14 | [weather_alerts](#14-weather_alerts) | تنبيهات الطقس | ~600 | Weather alert system |

---

## 1. agri_calendar

### التقويم الزراعي | Agricultural Calendar Module

**Location**: `shared/agri_calendar/`
**Version**: 16.0.0
**Files**: `__init__.py`, `islamic.py`, `models.py`, `planting.py`, `seasons.py`

#### Purpose | الغرض

Comprehensive agricultural calendar for Saudi Arabia and Yemen featuring:
- Agricultural season tracking by region (13 regions supported)
- Planting and harvest date recommendations
- Islamic (Hijri) calendar integration
- Traditional Arab farming calendar (Anwa'a - الأنواء)
- Regional climate-based scheduling

تقويم زراعي شامل للمملكة العربية السعودية واليمن يتضمن:
- تتبع المواسم الزراعية حسب المنطقة (13 منطقة مدعومة)
- توصيات مواعيد الزراعة والحصاد
- تكامل التقويم الإسلامي (الهجري)
- تقويم الزراعة العربي التقليدي (الأنواء)
- الجدولة المبنية على المناخ الإقليمي

#### Key Classes | الفئات الرئيسية

```python
# Season Calculations
SeasonCalculator              # Calculate current/upcoming seasons

# Planting Recommendations
PlantingRecommendationEngine  # Generate planting recommendations

# Islamic Calendar
HijriCalendar                 # Hijri-Gregorian date conversion
IslamicEventsManager          # Islamic events affecting agriculture
```

#### Key Enums | التعدادات

| Enum | Purpose | الغرض |
|------|---------|-------|
| `Region` | Saudi/Yemen regions | المناطق السعودية/اليمنية |
| `CropType` | Supported crop types | أنواع المحاصيل |
| `AgriculturalSeason` | Season definitions | تعريفات المواسم |
| `TraditionalSeason` | Anwa'a seasons | مواسم الأنواء |
| `HijriMonth` | Islamic months | الأشهر الهجرية |
| `ClimateZone` | Climate classifications | تصنيفات المناخ |

#### Data Constants | الثوابت

| Constant | Description |
|----------|-------------|
| `REGION_METADATA` | Metadata for all supported regions |
| `TRADITIONAL_SEASONS` | 13 traditional Anwa'a season definitions |
| `PLANTING_WINDOWS` | Optimal planting windows by crop/region |
| `ISLAMIC_EVENTS` | Islamic events with agricultural impact |
| `HIJRI_MONTH_NAMES` | Month names in Arabic |
| `DAY_NAMES` | Day names in Arabic |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.agri_calendar import (
    SeasonCalculator,
    Region,
    get_current_season,
    get_current_traditional_season,
    gregorian_to_hijri,
    get_planting_recommendation,
    CropType,
    get_crops_to_plant_now,
)
from datetime import date

# Get current agricultural season
season = get_current_season(Region.RIYADH)
print(f"Current season: {season.name_ar} ({season.name_en})")
# الموسم الحالي: الشتاء (Winter)

# Get traditional Anwa'a season
trad_season = get_current_traditional_season()
print(f"Traditional: {trad_season.name_ar}")
print(f"Proverb: {trad_season.proverb_ar}")

# Convert to Hijri date
hijri = gregorian_to_hijri(date(2026, 3, 15))
print(f"Hijri: {hijri.day} {hijri.month_name_ar} {hijri.year} هـ")

# Get planting recommendation
recommendation = get_planting_recommendation(CropType.WHEAT, Region.HAIL)
print(f"Plant: {recommendation.recommended_planting_start}")
print(f"Harvest: {recommendation.expected_harvest_start}")

# Get all crops to plant now
crops = get_crops_to_plant_now(Region.RIYADH)
for crop in crops:
    print(f"- {crop['crop_name_ar']}: {crop['urgency']}")
```

#### Integration | التكامل

- **advisory-service**: Seasonal planting advisories
- **astronomical-calendar**: Islamic calendar sync
- **agro-advisor**: Traditional farming knowledge

---

## 2. crop_insurance

### التأمين الزراعي | Crop Insurance Module

**Location**: `shared/crop_insurance/`
**Version**: 16.0.0
**Files**: `__init__.py`, `claims.py`, `models.py`, `risk_assessment.py`

#### Purpose | الغرض

Comprehensive crop insurance functionality:
- Traditional and parametric (index-based) insurance policies
- Claim submission, processing, and tracking
- Risk assessment based on field data, weather, and historical yields
- Weather-indexed insurance support
- Premium calculations with multiple risk factors

وظائف التأمين الزراعي الشاملة:
- وثائق التأمين التقليدية والمعلمية (المبنية على المؤشرات)
- تقديم ومعالجة وتتبع المطالبات
- تقييم المخاطر بناءً على بيانات الحقل والطقس والغلة التاريخية
- دعم التأمين المرتبط بالطقس
- حسابات الأقساط مع عوامل المخاطر المتعددة

#### Key Classes | الفئات الرئيسية

```python
# Risk Assessment
RiskAssessmentEngine          # Main risk assessment orchestrator
RiskCalculator                # Calculate risk scores
WeatherRiskAnalyzer           # Weather-based risk analysis
HistoricalYieldAnalyzer       # Historical yield analysis

# Claims Processing
ClaimProcessor                # Process insurance claims
ClaimValidator                # Validate claim submissions
PayoutCalculator              # Calculate claim payouts
ClaimStorage                  # Claim data persistence
```

#### Key Enums | التعدادات

| Enum | Purpose | الغرض |
|------|---------|-------|
| `InsuranceType` | Traditional vs parametric | تقليدي أو معلمي |
| `PolicyStatus` | Policy lifecycle states | حالات دورة الوثيقة |
| `ClaimStatus` | Claim processing states | حالات معالجة المطالبة |
| `RiskLevel` | Risk severity levels | مستويات شدة المخاطر |
| `WeatherIndexType` | Weather index triggers | محفزات مؤشر الطقس |
| `PayoutTriggerType` | Automatic payout triggers | محفزات الدفع التلقائي |

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `InsurancePolicy` | Complete policy with coverage details |
| `InsuranceClaim` | Claim with evidence and status |
| `FieldRiskProfile` | Field-specific risk assessment |
| `PremiumQuote` | Premium calculation result |
| `ParametricTrigger` | Weather index trigger conditions |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.crop_insurance import (
    RiskAssessmentEngine,
    assess_field_risk,
    calculate_premium_rate,
    submit_claim,
    get_claim_status,
    process_parametric_trigger,
)

# Assess field risk
engine = get_risk_assessment_engine()
risk_profile = await assess_field_risk(
    field_id="FIELD-001",
    crop_type="wheat",
    coverage_amount=50000,
)
print(f"Risk Level: {risk_profile.risk_level.value}")
print(f"Risk Score: {risk_profile.overall_score}/100")

# Calculate premium rate
premium = await calculate_premium_rate(
    risk_profile=risk_profile,
    coverage_type="comprehensive",
    deductible_percent=10,
)
print(f"Annual Premium: {premium.annual_premium} SAR")

# Submit a claim
claim = await submit_claim(
    policy_id="POL-001",
    claim_type="weather_damage",
    description="Frost damage to wheat crop",
    estimated_loss=15000,
    evidence=[...],  # Photos, reports
)

# Process parametric trigger (automatic for indexed insurance)
await process_parametric_trigger(
    policy_id="POL-002",
    trigger_type="frost",
    observed_value=-3.5,  # Temperature in Celsius
)
```

#### Integration | التكامل

- **weather-service**: Weather index triggers
- **field-management-service**: Field data for risk assessment
- **billing-core**: Premium processing

---

## 3. crop_rotation

### الدورة الزراعية | Crop Rotation Planning Module

**Location**: `shared/crop_rotation/`
**Version**: 1.0.0
**Files**: `__init__.py`, `models.py`, `planner.py`, `soil_health.py`

#### Purpose | الغرض

Comprehensive crop rotation planning and soil health management:
- Rotation planning and recommendations
- Soil health improvement tracking
- Pest/disease break recommendations
- Nutrient cycling optimization
- Multi-year planning

تخطيط شامل للدورة الزراعية وإدارة صحة التربة:
- تخطيط الدورة والتوصيات
- تتبع تحسين صحة التربة
- توصيات كسر دورة الآفات/الأمراض
- تحسين دورة المغذيات
- التخطيط متعدد السنوات

#### Supported Crops | المحاصيل المدعومة

| Crop (EN) | المحصول (AR) | Family |
|-----------|--------------|--------|
| Wheat | قمح | Gramineae |
| Barley | شعير | Gramineae |
| Alfalfa | برسيم | Leguminosae |
| Clover | برسيم مصري | Leguminosae |
| Maize | ذرة | Gramineae |
| Sorghum | ذرة رفيعة | Gramineae |
| Tomato | طماطم | Solanaceae |
| Potato | بطاطس | Solanaceae |
| Onion | بصل | Liliaceae |
| Cucumber | خيار | Cucurbitaceae |
| Date Palm | نخيل | Palmae |
| Cotton | قطن | Malvaceae |

#### Key Classes | الفئات الرئيسية

```python
# Rotation Planning
CropRotationPlanner           # Main rotation planner
RotationPlannerConfig         # Planner configuration

# Soil Health
SoilHealthTracker             # Track soil health over time
SoilHealthTrackerConfig       # Tracker configuration
```

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `CropCharacteristics` | Crop attributes and requirements |
| `RotationPlan` | Multi-year rotation plan |
| `RotationRecommendation` | AI-generated rotation advice |
| `SoilHealthReport` | Soil health assessment |
| `PestBreakRecommendation` | Pest cycle break suggestions |
| `NutrientBalance` | Nutrient cycling analysis |

#### Data Constants | الثوابت

| Constant | Description |
|----------|-------------|
| `CROP_DATABASE` | Complete crop characteristics |
| `PEST_DISEASE_DATABASE` | Pest/disease associations |
| `ROTATION_COMPATIBILITY` | Crop sequence compatibility |
| `OPTIMAL_RANGES` | Soil health optimal ranges |
| `CROP_SOIL_IMPACT` | Crop impact on soil health |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.crop_rotation import (
    CropRotationPlanner,
    SoilHealthTracker,
    CropType,
    get_crop_characteristics,
    get_crop_arabic_name,
    calculate_rotation_score,
    assess_soil_health_from_measurement,
)

# Get crop characteristics
wheat = get_crop_characteristics(CropType.WHEAT)
print(f"Wheat ({get_crop_arabic_name(CropType.WHEAT)})")
print(f"  Family: {wheat.family.value}")
print(f"  Nitrogen fixer: {wheat.nitrogen_fixer}")
print(f"  Root depth: {wheat.root_depth_cm} cm")

# Create rotation planner
planner = CropRotationPlanner(
    field_id="FIELD-001",
    field_size_ha=10.5,
)

# Generate rotation plan
plan = planner.generate_plan(
    current_crop=CropType.WHEAT,
    years=5,
    goals=["soil_health", "pest_break", "profitability"],
)

for year, slot in enumerate(plan.sequence, 1):
    print(f"Year {year}: {slot.crop_name_ar} ({slot.crop_type.value})")
    print(f"  Benefits: {[b.value for b in slot.benefits]}")

# Track soil health
tracker = SoilHealthTracker(field_id="FIELD-001")
report = tracker.generate_report(measurements=[...])
print(f"Soil Health Score: {report.overall_score}/100")
print(f"Trend: {report.trend.value}")
```

#### Integration | التكامل

- **advisory-service**: Rotation recommendations
- **soil_testing**: Soil health data
- **pest_scouting**: Pest cycle information

---

## 4. fertilizer_management

### إدارة الأسمدة | Fertilizer Management Module

**Location**: `shared/fertilizer_management/`
**Version**: 1.0.0
**Files**: `__init__.py`, `calculator.py`, `inventory.py`, `models.py`, `recommendations.py`

#### Purpose | الغرض

Comprehensive fertilizer management:
- Fertilizer inventory tracking
- Application recommendations based on soil tests
- Nutrient balance tracking
- Cost optimization
- Environmental compliance

إدارة شاملة للأسمدة:
- تتبع مخزون الأسمدة
- توصيات التسميد بناءً على تحليل التربة
- تتبع توازن العناصر الغذائية
- تحسين التكاليف
- الامتثال البيئي

#### Key Classes | الفئات الرئيسية

```python
# Recommendations
FertilizerRecommendationEngine  # Generate recommendations

# Inventory
FertilizerInventoryManager      # Track fertilizer stock

# Calculator
FertilizerCalculator            # Application rate calculations
```

#### Key Enums | التعدادات

| Enum | Purpose | الغرض |
|------|---------|-------|
| `FertilizerType` | Urea, DAP, NPK, organic | يوريا، داب، مركب، عضوي |
| `FertilizerForm` | Granular, liquid, foliar | حبيبي، سائل، ورقي |
| `ApplicationMethod` | Broadcast, band, fertigation | نثر، تسطير، تسميد بالري |
| `NutrientStatus` | Deficient, adequate, excess | ناقص، كافي، زائد |
| `ComplianceLevel` | Compliant, warning, violation | ملتزم، تحذير، مخالفة |

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `Fertilizer` | Fertilizer product with NPK composition |
| `FertilizerRecommendation` | Crop-specific recommendation |
| `InventoryItem` | Fertilizer stock item |
| `NutrientBalance` | Field nutrient status |
| `CostAnalysis` | Cost-benefit analysis |
| `EnvironmentalCompliance` | Environmental limit checking |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.fertilizer_management import (
    FertilizerRecommendationEngine,
    FertilizerCalculator,
    FertilizerInventoryManager,
    get_crop_requirements,
    calculate_quick_recommendation,
    quick_rate_calculation,
)

# Get crop nutrient requirements
wheat_req = get_crop_requirements("wheat")
print(f"N: {wheat_req.nitrogen_kg_ha} kg/ha")
print(f"P: {wheat_req.phosphorus_kg_ha} kg/ha")
print(f"K: {wheat_req.potassium_kg_ha} kg/ha")

# Quick recommendation based on soil test
recommendation = calculate_quick_recommendation(
    crop="wheat",
    soil_n_ppm=18,
    soil_p_ppm=12,
    soil_k_ppm=150,
    area_ha=10.5,
)
print(f"Recommended: {recommendation.fertilizer_name}")
print(f"Rate: {recommendation.rate_kg_ha} kg/ha")
print(f"Total: {recommendation.total_kg} kg")

# Calculate application rate
rate = quick_rate_calculation(
    target_n_kg_ha=46,
    fertilizer_n_percent=46,  # Urea
)
print(f"Apply {rate.rate_kg_ha} kg/ha of Urea")

# Inventory management
inventory = FertilizerInventoryManager(farm_id="FARM-001")
inventory.add_purchase("urea", quantity_kg=500, price_per_kg=2.5)
summary = inventory.get_summary()
print(f"Total stock: {summary.total_quantity_kg} kg")
print(f"Total value: {summary.total_value} SAR")
```

#### Integration | التكامل

- **soil_testing**: Soil test results for recommendations
- **advisory-service**: Fertilizer advisory delivery
- **billing-core**: Inventory cost tracking

---

## 5. field_boundaries

### حدود الحقول | Field Boundaries Module

**Location**: `shared/field_boundaries/`
**Version**: 16.0.0
**Files**: `__init__.py`, `geometry.py`, `mapping.py`, `models.py`, `sharing.py`

#### Purpose | الغرض

Comprehensive field boundary management:
- Field polygon management with GeoJSON support
- Geodesic and projected area/perimeter calculations
- GPS track to boundary conversion with filtering
- Boundary sharing between users/neighbors
- Conflict detection (overlap, gap, encroachment)
- PostGIS integration patterns

إدارة شاملة لحدود الحقول:
- إدارة مضلعات الحقول مع دعم GeoJSON
- حسابات المساحة والمحيط الجيوديسية والإسقاطية
- تحويل مسار GPS إلى حدود مع التصفية
- مشاركة الحدود بين المستخدمين/الجيران
- اكتشاف التعارضات (التداخل، الفجوات، التعدي)
- أنماط تكامل PostGIS

#### Key Classes | الفئات الرئيسية

```python
# Geometry
GeometryMetrics               # Area, perimeter, centroid calculations

# Mapping
GPSMapper                     # GPS track to boundary conversion
MappingSession                # Active mapping session

# Sharing
BoundarySharingManager        # Boundary sharing workflow
```

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `Point` | Geographic point (lon, lat) |
| `Polygon` | Closed polygon boundary |
| `MultiPolygon` | Multiple polygons |
| `FieldBoundary` | Complete field boundary record |
| `BoundaryConflict` | Detected boundary conflict |
| `BoundaryShareRequest` | Sharing request between users |
| `GPSTrack` | GPS points from field walking |

#### Geometry Constants | ثوابت الهندسة

| Constant | Value | Description |
|----------|-------|-------------|
| `EARTH_RADIUS_M` | 6,371,000 | Earth radius in meters |
| `HECTARES_PER_SQM` | 0.0001 | Conversion factor |
| `DUNAMS_PER_SQM` | 0.001 | Middle East unit |
| `ACRES_PER_SQM` | 0.000247105 | Conversion factor |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.field_boundaries import (
    FieldBoundary,
    Polygon,
    GPSMapper,
    BoundarySharingManager,
    calculate_geometry_metrics,
    generate_postgis_area_query,
    PermissionLevel,
)

# Create boundary from coordinates
boundary = FieldBoundary(
    field_id="FIELD-001",
    tenant_id="tenant-001",
    owner_id="user-001",
    name="North Field",
    name_ar="الحقل الشمالي",
    geometry=Polygon(coordinates=[[
        (46.7, 24.7),
        (46.71, 24.7),
        (46.71, 24.71),
        (46.7, 24.71),
        (46.7, 24.7)  # Closed
    ]])
)

# Calculate metrics
metrics = calculate_geometry_metrics(boundary.geometry.exterior_ring)
print(f"Area: {metrics.area_hectares:.2f} hectares")
print(f"Area: {metrics.area_dunams:.2f} dunams")  # دونم
print(f"Perimeter: {metrics.perimeter_meters:.0f} meters")
print(f"Centroid: {metrics.centroid}")

# GPS mapping session
mapper = GPSMapper()
session = mapper.start_session(
    user_id="user-001",
    field_id="FIELD-002"
)

# Add GPS points while walking field
mapper.add_point(session.id, longitude=46.7, latitude=24.7, accuracy_m=3.0)
mapper.add_point(session.id, longitude=46.71, latitude=24.7, accuracy_m=2.5)
# ... add more points ...

# End session and get boundary
result = mapper.end_session(session.id)
if result.success:
    new_boundary = result.boundary
    print(f"Created boundary: {new_boundary.field_id}")

# Share boundary with neighbor
sharing = BoundarySharingManager()
request = sharing.create_share_request(
    boundary=boundary,
    recipient_id="neighbor-user",
    permission_level=PermissionLevel.VIEW,
)
print(f"Share request: {request.id}")

# Generate PostGIS queries
area_query = generate_postgis_area_query("FIELD-001")
# SELECT ST_Area(geometry::geography) / 10000 AS area_ha FROM fields ...
```

#### Integration | التكامل

- **field-management-service**: Field CRUD operations
- **satellite-service**: Imagery alignment
- **vegetation-analysis-service**: NDVI by boundary

---

## 6. harvest_quality

### جودة المحصول | Harvest Quality Module

**Location**: `shared/harvest_quality/`
**Version**: 1.0.0
**Files**: `__init__.py`, `grading.py`, `models.py`, `pricing.py`

#### Purpose | الغرض

Comprehensive quality tracking for agricultural produce:
- Quality grading standards for grains, dates, and vegetables
- Quality test recording and certification
- Grade-based pricing calculations
- Quality trend analysis
- Buyer requirements matching

تتبع شامل للجودة للمنتجات الزراعية:
- معايير تصنيف الجودة للحبوب والتمور والخضروات
- تسجيل اختبارات الجودة والشهادات
- حسابات التسعير المبنية على الدرجة
- تحليل اتجاهات الجودة
- مطابقة متطلبات المشترين

#### Key Classes | الفئات الرئيسية

```python
# Grading
QualityGradingEngine          # Calculate quality grades
BuyerMatchingEngine           # Match produce to buyers
QualityTrendAnalyzer          # Analyze quality trends

# Pricing
QualityPricingEngine          # Calculate grade-based prices
```

#### Quality Grades | درجات الجودة

| Grade | English | العربية | Description |
|-------|---------|---------|-------------|
| A | Premium | ممتاز | Top export quality |
| B | Standard | جيد | Good local market |
| C | Economy | مقبول | Processing grade |
| D | Substandard | ضعيف | Feed/industrial use |

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `QualityStandard` | Grading criteria for crop type |
| `QualityTestRecord` | Recorded quality test |
| `GradingResult` | Grade calculation result |
| `BuyerRequirement` | Buyer quality specifications |
| `PriceCalculation` | Price with grade adjustments |
| `QualityTrendAnalysis` | Multi-season trend report |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.harvest_quality import (
    QualityGradingEngine,
    QualityPricingEngine,
    QUALITY_STANDARDS,
    PRICE_MATRICES,
    calculate_quick_price,
)

# Grade a wheat sample
engine = QualityGradingEngine()
engine.set_standard(QUALITY_STANDARDS["wheat"])

result = engine.calculate_grade({
    "moisture": 12.5,        # %
    "protein": 13.0,         # %
    "test_weight": 79.0,     # kg/hl
    "foreign_matter": 0.8,   # %
    "damaged_kernels": 1.5,  # %
})

print(f"Grade: {result.overall_grade.value}")  # A, B, C, D
print(f"Score: {result.grade_score:.1f}/100")
print(f"Summary: {result.summary_ar}")

# Calculate price
pricing = QualityPricingEngine()
price_calc = pricing.calculate_price(
    grade=result.overall_grade,
    quantity=1000,  # kg
    test_values={"moisture": 12.5, "protein": 13.0},
    price_matrix=PRICE_MATRICES["wheat"],
)

print(f"Base price: {price_calc.base_price} SAR/kg")
print(f"Adjustments: {price_calc.adjustments}")
print(f"Final price: {price_calc.final_price} SAR")
print(f"Total value: {price_calc.total_value} SAR")

# Quick price calculation
quick = calculate_quick_price(
    crop="wheat",
    grade="A",
    quantity_kg=5000,
)
print(f"Quick estimate: {quick} SAR")
```

#### Integration | التكامل

- **marketplace-service**: Quality-based listings
- **billing-core**: Price calculations
- **yield-engine**: Yield quality correlation

---

## 7. irrigation

### الري التعاوني | Human-Machine Collaborative Irrigation Module

**Location**: `shared/irrigation/`
**Version**: 1.0.0
**Files**: `__init__.py`, `checklist.py`, `collaborative_engine.py`, `dimensions.py`, `integration.py`, `models.py`

#### Purpose | الغرض

Human-Machine Collaborative (HMC) irrigation decision framework:

1. **Goal Anchoring** (ترسيخ الأهداف) - Human defines optimization goals
2. **Experience Injection** (حقن الخبرة) - Human injects local farming knowledge
3. **Supervision Calibration** (معايرة الإشراف) - Testing and validation
4. **Value Upgrade** (ترقية القيمة) - Continuous improvement

إطار قرار الري التعاوني بين الإنسان والآلة:

1. **ترسيخ الأهداف** - الإنسان يحدد أهداف التحسين
2. **حقن الخبرة** - الإنسان يحقن المعرفة الزراعية المحلية
3. **معايرة الإشراف** - الاختبار والتحقق
4. **ترقية القيمة** - التحسين المستمر

#### Key Classes | الفئات الرئيسية

```python
# Main Engine
HMCIrrigationEngine           # Orchestrates HMC workflow

# Dimensions
GoalAnchoringDimension        # Goal setting phase
ExperienceInjectionDimension  # Knowledge injection phase
SupervisionCalibrationDimension  # Calibration phase
ValueUpgradeDimension         # Continuous learning phase

# Checklist
CollaborativeChecklist        # Validation checklist

# Integration
HMCIntegrationManager         # Service integrations
```

#### Key Enums | التعدادات

| Enum | Purpose | الغرض |
|------|---------|-------|
| `IrrigationGoalType` | Water saving, yield max, quality | توفير المياه، تعظيم الغلة، الجودة |
| `ExperienceSource` | Farmer, agronomist, literature | المزارع، المهندس، المراجع |
| `CalibrationMethod` | Simulation, field trial, historical | محاكاة، تجربة حقلية، تاريخي |
| `SessionStatus` | Draft, active, completed, archived | مسودة، نشط، مكتمل، مؤرشف |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.irrigation import (
    HMCIrrigationEngine,
    IrrigationGoal,
    IrrigationGoalType,
    EcologicalConstraint,
    ExperienceRule,
    ExperienceSource,
    quick_start,
)

# Quick start - creates engine with session
engine = quick_start(
    farm_id="FARM-001",
    farmer_id="farmer-123",
)

# Phase 1: Human sets goals
engine.human_sets_goals(
    goals=[
        IrrigationGoal(
            goal_type=IrrigationGoalType.WATER_SAVING,
            priority=1,
            target_value=30,  # 30% reduction
        ),
    ],
    constraints=[
        EcologicalConstraint(
            water_quota_reduction=0.3,
            min_soil_moisture=25,
            max_salinity_ds_m=3.0,
        ),
    ],
)

# Phase 2: AI generates irrigation program
program = await engine.ai_generates_program(
    context={
        "crop_type": "wheat",
        "growth_stage": "tillering",
        "soil_moisture": 35,
        "weather_forecast": {...},
    }
)

# Phase 3: Human reviews and injects experience
engine.human_reviews_program(program)
engine.human_injects_experience([
    ExperienceRule(
        condition="cold_wave",
        action="reduce_irrigation_20%",
        source=ExperienceSource.FARMER,
        rationale="Plants need less water in cold",
        rationale_ar="النباتات تحتاج ماء أقل في البرد",
    ),
])

# Phase 4: Calibration
result = engine.run_calibration_cycle()
print(f"Calibration passed: {result.passed}")

# Phase 5: Approval and execution
if engine.checklist.validate_all().is_complete:
    engine.human_approves_execution()

# Record outcome for learning
engine.record_outcome(
    actual_yield=4.5,  # tons/ha
    water_used=450,    # mm
    issues_encountered=["minor_stress_day_45"],
)
```

#### Integration | التكامل

- **irrigation-smart**: Smart irrigation execution
- **weather-service**: Weather forecasts
- **ml_irrigation**: ML predictions

---

## 8. ml_irrigation

### الري الذكي | ML Irrigation Prediction Module

**Location**: `shared/ml_irrigation/`
**Version**: 1.0.0
**Files**: `__init__.py`, `models.py`, `optimizer.py`, `predictor.py`

#### Purpose | الغرض

ML-based irrigation prediction and optimization:
- Irrigation need prediction based on weather, soil, and crop data
- Water usage optimization recommendations
- Historical pattern analysis
- Anomaly detection for irrigation systems

التنبؤ بالري وتحسينه باستخدام التعلم الآلي:
- التنبؤ باحتياجات الري بناءً على بيانات الطقس والتربة والمحصول
- توصيات تحسين استخدام المياه
- تحليل الأنماط التاريخية
- اكتشاف الشذوذ في أنظمة الري

#### Key Classes | الفئات الرئيسية

```python
# Prediction
IrrigationPredictor           # ML-based irrigation prediction
PredictorConfig               # Prediction configuration

# Optimization
WaterOptimizer                # Water usage optimization
OptimizerConfig               # Optimizer configuration
```

#### Feature Models | نماذج الميزات

| Model | Features |
|-------|----------|
| `WeatherFeatures` | Temperature, humidity, wind, ET0, precipitation |
| `SoilFeatures` | Moisture, field capacity, wilting point, EC, pH |
| `CropFeatures` | Crop type, growth stage, Kc, root depth, NDVI |
| `IrrigationFeatures` | Combined feature set |

#### Key Enums | التعدادات

| Enum | Purpose | الغرض |
|------|---------|-------|
| `IrrigationUrgency` | Critical, high, medium, low | حرج، عالي، متوسط، منخفض |
| `CropStage` | Germination, tillering, heading, etc. | إنبات، تفريع، سنبلة، إلخ |
| `SoilType` | Sandy, loamy, clay, etc. | رملي، طميي، طيني، إلخ |
| `AnomalyType` | Leak, sensor fault, over-irrigation | تسرب، عطل مجس، إفراط ري |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.ml_irrigation import (
    IrrigationPredictor,
    WeatherFeatures,
    SoilFeatures,
    CropFeatures,
    SoilType,
    CropStage,
    predict_irrigation,
    optimize_water_usage,
    detect_irrigation_anomalies,
)

# Create feature objects
weather = WeatherFeatures(
    temperature_current=28.0,
    temperature_max=35.0,
    temperature_min=22.0,
    humidity=45.0,
    precipitation_probability=10.0,
    wind_speed=12.0,
    solar_radiation=800.0,
    et0=5.5,
)

soil = SoilFeatures(
    moisture_current=35.0,
    moisture_field_capacity=45.0,
    moisture_wilting_point=15.0,
    soil_type=SoilType.LOAMY,
    ec=1.2,
    ph=7.2,
)

crop = CropFeatures(
    crop_type="wheat",
    crop_type_ar="قمح",
    growth_stage=CropStage.TILLERING,
    days_after_planting=45,
    kc=0.95,
    root_depth_cm=60.0,
    ndvi=0.72,
)

# Predict irrigation needs
prediction = predict_irrigation(weather, soil, crop)

print(f"Irrigation needed: {prediction.irrigation_needed}")
print(f"Amount: {prediction.recommended_amount_mm} mm")
print(f"Urgency: {prediction.urgency.value}")
print(f"Confidence: {prediction.confidence.value}")
print(f"Recommendation: {prediction.recommendation}")
print(f"التوصية: {prediction.recommendation_ar}")

# Optimize water usage
from shared.ml_irrigation import IrrigationRecord

records = [...]  # Historical irrigation records
optimization = optimize_water_usage(
    records=records,
    area_ha=10.5,
)

print(f"Current efficiency: {optimization.current_efficiency}%")
print(f"Potential savings: {optimization.savings_percent}%")
print(f"Recommendations: {optimization.recommendations}")

# Detect anomalies
anomalies = detect_irrigation_anomalies(
    records=records,
    current_reading=45.0,
)

for anomaly in anomalies:
    print(f"{anomaly.anomaly_type.value}: {anomaly.description}")
    print(f"Severity: {anomaly.severity.value}")
```

#### Integration | التكامل

- **irrigation-smart**: Irrigation execution
- **virtual-sensors**: Sensor data
- **weather-service**: Weather forecasts

---

## 9. pest_scouting

### مسح الآفات | Pest Scouting Module

**Location**: `shared/pest_scouting/`
**Version**: 1.0.0
**Files**: `__init__.py`, `identification.py`, `models.py`, `recommendations.py`, `thresholds.py`

#### Purpose | الغرض

Comprehensive pest scouting and monitoring:
- Pest/disease identification with Middle East pest database
- Scout report management and tracking
- Threshold-based alerts with economic analysis
- Treatment recommendations (chemical, biological, cultural)
- Historical outbreak tracking

مسح ورصد شامل للآفات:
- تعريف الآفات/الأمراض مع قاعدة بيانات آفات الشرق الأوسط
- إدارة وتتبع تقارير المسح
- تنبيهات مبنية على العتبات مع التحليل الاقتصادي
- توصيات العلاج (كيميائي، بيولوجي، زراعي)
- تتبع تاريخ الإصابات

#### Supported Pests | الآفات المدعومة

| Pest (EN) | الآفة (AR) | Scientific Name |
|-----------|------------|-----------------|
| Red Palm Weevil | سوسة النخيل الحمراء | *Rhynchophorus ferrugineus* |
| Dubas Bug | دوباس النخيل | *Ommatissus lybicus* |
| Aphids | المن | *Aphididae* |
| Whiteflies | الذبابة البيضاء | *Aleyrodidae* |
| Spider Mites | العنكبوت الأحمر | *Tetranychidae* |
| Desert Locust | الجراد الصحراوي | *Schistocerca gregaria* |
| Date Moth | فراشة التمر | *Ephestia cautella* |
| Tomato Leafminer | حافرة أنفاق الطماطم | *Tuta absoluta* |
| Thrips | التربس | *Thysanoptera* |
| Fruit Flies | ذباب الفاكهة | *Tephritidae* |

#### Key Classes | الفئات الرئيسية

```python
# Identification
get_pest_by_id()              # Lookup pest by ID
identify_by_symptoms()        # Identify from symptoms
assess_infestation_level()    # Assess severity

# Thresholds
assess_threshold()            # Check against economic threshold
calculate_economic_injury_level()  # Calculate EIL
estimate_yield_loss()         # Estimate yield impact

# Recommendations
generate_treatment_recommendation()  # Get treatment plan
get_ipm_calendar()            # IPM schedule
```

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `PestIdentification` | Complete pest record |
| `ScoutReport` | Field scouting report |
| `PestAlert` | Threshold-triggered alert |
| `EconomicThreshold` | Economic injury threshold |
| `TreatmentRecommendation` | Treatment plan |
| `ChemicalOption` | Pesticide option |
| `BiologicalOption` | Biocontrol option |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.pest_scouting import (
    get_pest_by_id,
    get_pests_by_crop,
    identify_by_symptoms,
    assess_threshold,
    generate_treatment_recommendation,
    get_ipm_calendar,
    PEST_DATABASE,
    CropType,
)

# Get pest information
rpw = get_pest_by_id("rpw")
print(f"Name: {rpw.name_ar} ({rpw.name_en})")
print(f"Scientific: {rpw.scientific_name}")
print(f"Quarantine: {rpw.is_quarantine_pest}")
print(f"Symptoms: {rpw.symptoms_ar}")

# Get pests for a crop
wheat_pests = get_pests_by_crop(CropType.WHEAT)
for pest in wheat_pests:
    print(f"- {pest.name_ar}")

# Identify by symptoms
matches = identify_by_symptoms(
    symptoms=["yellowing_leaves", "honeydew", "sooty_mold"],
    crop_type=CropType.TOMATO,
)
for match in matches:
    print(f"{match.pest.name_ar}: {match.confidence}% match")

# Assess economic threshold
assessment = assess_threshold(
    pest_id="aphid",
    crop_type=CropType.WHEAT,
    population_count=45,  # per plant
    crop_stage="tillering",
    crop_value_per_ha=8000,
)

print(f"Threshold exceeded: {assessment.exceeded}")
print(f"Action needed: {assessment.action_needed}")
print(f"Economic injury level: {assessment.eil}")
print(f"Estimated yield loss: {assessment.yield_loss_percent}%")

# Generate treatment recommendation
if assessment.action_needed:
    treatment = generate_treatment_recommendation(
        pest_id="aphid",
        crop_type=CropType.WHEAT,
        infestation_level="moderate",
    )

    print(f"Urgency: {treatment.urgency.value}")
    print("Chemical options:")
    for chem in treatment.chemical_options:
        print(f"  - {chem.product_name}: {chem.rate}")
    print("Biological options:")
    for bio in treatment.biological_options:
        print(f"  - {bio.agent_name}")

# Get IPM calendar
calendar = get_ipm_calendar(CropType.DATE_PALM)
for month, activities in calendar.items():
    print(f"{month}: {activities}")
```

#### Integration | التكامل

- **crop-intelligence-service**: Disease detection
- **advisory-service**: Treatment advisories
- **pesticide_compliance**: PHI/REI checking

---

## 10. pesticide_compliance

### سلامة المبيدات | Pesticide Compliance Module

**Location**: `shared/pesticide_compliance/`
**Version**: 1.0.0
**Files**: `__init__.py`, `alerts.py`, `checker.py`, `database.py`, `models.py`

#### Purpose | الغرض

Critical food and worker safety module:
- Pre-Harvest Interval (PHI) tracking
- Re-Entry Interval (REI) tracking
- Tank mix compatibility checking
- PPE requirements
- Spray drift risk assessment

وحدة حرجة لسلامة الغذاء والعمال:
- تتبع فترة ما قبل الحصاد (PHI)
- تتبع فترة إعادة الدخول (REI)
- فحص توافق خلطات الخزان
- متطلبات معدات الحماية الشخصية (PPE)
- تقييم مخاطر انجراف الرش

#### Key Classes | الفئات الرئيسية

```python
# Compliance Checking
PesticideComplianceChecker    # Main compliance checker
check_phi_compliance()        # PHI verification
check_rei_compliance()        # REI verification
check_tank_mix_compatibility() # Tank mix check
get_ppe_requirements()        # PPE lookup
assess_spray_drift_risk()     # Drift risk assessment
```

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `Pesticide` | Pesticide product record |
| `PesticideApplication` | Application record |
| `PHIViolation` | PHI violation alert |
| `REIViolation` | REI violation alert |
| `TankMixCompatibility` | Mix compatibility result |
| `PPERequirement` | PPE requirements |
| `SprayDriftRisk` | Drift risk assessment |
| `ComplianceCheck` | Overall compliance status |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.pesticide_compliance import (
    PesticideComplianceChecker,
    check_phi_compliance,
    check_rei_compliance,
    check_tank_mix_compatibility,
    get_ppe_requirements,
    assess_spray_drift_risk,
    get_pesticide,
    PESTICIDE_DATABASE,
)
from datetime import datetime, timedelta

# Check PHI compliance
phi_check = check_phi_compliance(
    pesticide_id="lambda_cyhalothrin",
    application_date=datetime.now() - timedelta(days=5),
    planned_harvest_date=datetime.now() + timedelta(days=10),
    crop_type="tomato",
)

if phi_check.is_violation:
    print(f"PHI VIOLATION: {phi_check.message}")
    print(f"Message (AR): {phi_check.message_ar}")
    print(f"Safe harvest date: {phi_check.safe_harvest_date}")
else:
    print("PHI compliance OK")

# Check REI compliance
rei_check = check_rei_compliance(
    pesticide_id="chlorpyrifos",
    application_datetime=datetime.now() - timedelta(hours=6),
)

if rei_check.is_violation:
    print(f"REI VIOLATION: Workers cannot enter!")
    print(f"Safe re-entry time: {rei_check.safe_entry_time}")

# Check tank mix compatibility
compatibility = check_tank_mix_compatibility(
    pesticide_ids=["lambda_cyhalothrin", "mancozeb", "urea_foliar"],
)

print(f"Compatible: {compatibility.is_compatible}")
if not compatibility.is_compatible:
    for issue in compatibility.issues:
        print(f"  - {issue}")

# Get PPE requirements
ppe = get_ppe_requirements(pesticide_id="paraquat")
print("Required PPE:")
print(f"  Gloves: {ppe.gloves}")
print(f"  Respirator: {ppe.respirator}")
print(f"  Eye protection: {ppe.eye_protection}")
print(f"  Body protection: {ppe.body_protection}")
print(f"  Boots: {ppe.boots}")

# Assess spray drift risk
drift_risk = assess_spray_drift_risk(
    wind_speed_kmh=15,
    temperature_c=28,
    humidity_percent=45,
    distance_to_sensitive_area_m=50,
)

print(f"Drift risk: {drift_risk.risk_level.value}")
print(f"Recommendation: {drift_risk.recommendation}")
print(f"التوصية: {drift_risk.recommendation_ar}")
```

#### Integration | التكامل

- **pest_scouting**: Treatment recommendations
- **weather_alerts**: Spray conditions
- **notification-service**: Violation alerts

---

## 11. soil_sensors

### مجسات التربة | Soil Sensors Module

**Location**: `shared/soil_sensors/`
**Version**: 1.0.0
**Files**: `__init__.py`, `adapters.py`, `models.py`, `processor.py`

#### Purpose | الغرض

IoT sensor integration for soil moisture and health monitoring:
- Multi-protocol support (MQTT, LoRaWAN, HTTP)
- Sensor data normalization
- Alert generation on thresholds
- Historical data aggregation

تكامل أجهزة إنترنت الأشياء لمراقبة رطوبة التربة وصحتها:
- دعم بروتوكولات متعددة (MQTT، LoRaWAN، HTTP)
- تطبيع بيانات المجسات
- توليد التنبيهات عند العتبات
- تجميع البيانات التاريخية

#### Key Classes | الفئات الرئيسية

```python
# Adapters
SensorAdapter                 # Base adapter class
MQTTAdapter                   # MQTT protocol adapter
LoRaWANAdapter               # LoRaWAN protocol adapter
HTTPAdapter                   # HTTP/REST adapter
get_adapter()                 # Factory function

# Processing
SensorDataProcessor           # Data processing and normalization
aggregate_readings()          # Aggregate sensor readings
detect_anomalies()           # Detect sensor anomalies
interpolate_field_moisture() # Spatial interpolation
```

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `SoilSensor` | Sensor device record |
| `SensorReading` | Single sensor reading |
| `SensorAlert` | Threshold-triggered alert |
| `SensorCalibration` | Calibration record |
| `SensorStatus` | Sensor health status |

#### Key Enums | التعدادات

| Enum | Purpose | الغرض |
|------|---------|-------|
| `SensorType` | Moisture, temp, EC, pH | رطوبة، حرارة، توصيل، حموضة |
| `SensorProtocol` | MQTT, LoRaWAN, HTTP | بروتوكولات الاتصال |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.soil_sensors import (
    SensorDataProcessor,
    MQTTAdapter,
    LoRaWANAdapter,
    get_adapter,
    aggregate_readings,
    detect_anomalies,
    interpolate_field_moisture,
    SensorType,
    SensorProtocol,
)

# Connect to sensor via MQTT
mqtt_adapter = get_adapter(SensorProtocol.MQTT)
await mqtt_adapter.connect(
    broker="mqtt.farm.local",
    topic="sensors/soil/+",
)

# Process incoming readings
processor = SensorDataProcessor(field_id="FIELD-001")

async for reading in mqtt_adapter.stream_readings():
    # Normalize and validate
    normalized = processor.normalize(reading)

    # Check for alerts
    alerts = processor.check_thresholds(normalized)
    for alert in alerts:
        print(f"ALERT: {alert.message}")
        print(f"تنبيه: {alert.message_ar}")

# Aggregate readings for period
readings = await processor.get_readings(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
)

aggregated = aggregate_readings(
    readings=readings,
    interval="hourly",
    aggregation="mean",
)

# Detect anomalies
anomalies = detect_anomalies(readings)
for anomaly in anomalies:
    print(f"Anomaly at {anomaly.timestamp}: {anomaly.description}")

# Interpolate field moisture map
moisture_map = interpolate_field_moisture(
    sensor_readings=readings,
    field_boundary=boundary,
    resolution_m=10,
)
# Returns grid of moisture values for visualization
```

#### Integration | التكامل

- **iot-gateway**: Sensor data ingestion
- **virtual-sensors**: Virtual sensor computation
- **irrigation-smart**: Irrigation decisions

---

## 12. soil_testing

### تحليل التربة | Soil Testing Module

**Location**: `shared/soil_testing/`
**Version**: 1.0.0
**Files**: `__init__.py`, `interpreter.py`, `models.py`, `recommendations.py`, `trends.py`

#### Purpose | الغرض

Comprehensive soil testing and analysis:
- Soil test result recording
- Nutrient level interpretation
- Amendment recommendations
- Historical trend tracking
- Lab integration support

تحليل واختبار شامل للتربة:
- تسجيل نتائج تحليل التربة
- تفسير مستويات العناصر الغذائية
- توصيات التعديل والتسميد
- تتبع الاتجاهات التاريخية
- دعم التكامل مع المختبرات

#### Key Classes | الفئات الرئيسية

```python
# Interpretation
SoilTestInterpreter           # Interpret soil test results
interpret_soil_test()         # Quick interpretation

# Recommendations
SoilAmendmentRecommender      # Generate amendment plans
generate_amendment_plan()     # Quick plan generation

# Trends
SoilTrendAnalyzer             # Analyze historical trends
analyze_soil_trends()         # Quick trend analysis
```

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `SoilTestResult` | Complete soil test record |
| `MacronutrientResults` | N, P, K test results |
| `MicronutrientResults` | Fe, Mn, Zn, Cu, B, Mo |
| `SoilProperties` | pH, EC, organic matter |
| `InterpretationReport` | Interpretation with status |
| `AmendmentPlan` | Recommended amendments |
| `TrendReport` | Multi-year trend analysis |

#### Data Constants | الثوابت

| Constant | Description |
|----------|-------------|
| `NUTRIENT_THRESHOLDS` | Crop-specific nutrient thresholds |
| `SOIL_PROPERTY_THRESHOLDS` | pH, EC, OM thresholds |
| `CROP_SENSITIVITY` | Crop sensitivity to conditions |
| `FERTILIZER_PRODUCTS` | Available fertilizer products |
| `CROP_REQUIREMENTS` | Crop nutrient requirements |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.soil_testing import (
    SoilTestResult,
    SoilTestInterpreter,
    SoilAmendmentRecommender,
    SoilTrendAnalyzer,
    MacronutrientResults,
    SoilProperties,
    interpret_soil_test,
    generate_amendment_plan,
)
from datetime import datetime

# Create a soil test result
soil_test = SoilTestResult(
    id="test_001",
    tenant_id="tenant_001",
    field_id="FIELD-001",
    sample_id="sample_001",
    sample_date=datetime.now(),
    macronutrients=MacronutrientResults(
        nitrogen_nitrate_ppm=25,
        phosphorus_ppm=15,
        potassium_ppm=180,
    ),
    soil_properties=SoilProperties(
        ph=7.8,
        ec_ds_m=2.5,
        organic_matter_percent=1.5,
    ),
)

# Interpret results
interpreter = SoilTestInterpreter()
report = interpreter.interpret(soil_test, crop="wheat")

print(f"Summary: {report.summary}")
print(f"الملخص: {report.summary_ar}")

for nutrient, status in report.nutrient_status.items():
    print(f"{nutrient}: {status.level.value} - {status.recommendation_ar}")

# Generate amendment plan
recommender = SoilAmendmentRecommender()
plan = recommender.generate_plan(
    soil_test=soil_test,
    crop="wheat",
    target_yield=5.0,  # tons/ha
)

print(f"Amendment Plan for {plan.crop}")
for amendment in plan.amendments:
    print(f"  - {amendment.product_name}: {amendment.rate_kg_ha} kg/ha")
    print(f"    Timing: {amendment.timing}")
    print(f"    Cost: {amendment.cost_per_ha} SAR/ha")

print(f"Total cost: {plan.total_cost_per_ha} SAR/ha")

# Analyze trends
analyzer = SoilTrendAnalyzer()
trend_report = analyzer.analyze_trends(
    field_id="FIELD-001",
    soil_tests=[soil_test, ...],  # Multiple tests over time
)

print(f"Organic Matter Trend: {trend_report.om_trend.direction.value}")
print(f"pH Trend: {trend_report.ph_trend.direction.value}")
print(f"Management Impact: {trend_report.management_assessment}")
```

#### Integration | التكامل

- **fertilizer_management**: Fertilizer recommendations
- **crop_rotation**: Soil health tracking
- **advisory-service**: Soil management advisories

---

## 13. water_management

### إدارة المياه | Water Management Module

**Location**: `shared/water_management/`
**Version**: 1.0.0
**Files**: `__init__.py`, `efficiency.py`, `models.py`, `monitoring.py`, `reporting.py`

#### Purpose | الغرض

Comprehensive water management compliant with Saudi regulations:
- Water source monitoring (wells, tanks, canals)
- Water rights and allocation tracking
- Irrigation efficiency metrics (FAO guidelines)
- Water quality monitoring
- Regulatory compliance reporting (MEWA, NWC)

إدارة شاملة للمياه متوافقة مع الأنظمة السعودية:
- مراقبة مصادر المياه (الآبار، الخزانات، القنوات)
- تتبع حقوق المياه والتخصيصات
- مقاييس كفاءة الري (إرشادات FAO)
- مراقبة جودة المياه
- تقارير الامتثال التنظيمي (وزارة البيئة والمياه والزراعة، شركة المياه الوطنية)

#### Key Classes | الفئات الرئيسية

```python
# Monitoring
WaterLevelMonitor             # Well/tank level monitoring
WaterQualityMonitor           # Water quality monitoring
GroundwaterMonitor            # Aquifer status monitoring

# Efficiency
IrrigationEfficiencyCalculator  # Efficiency calculations
EfficiencyAlertGenerator      # Efficiency alerts
WaterConservationCalculator   # Conservation opportunities

# Reporting
WaterReportGenerator          # Generate compliance reports
WaterReportScheduler          # Schedule automated reports
```

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `WaterSource` | Well, tank, or canal record |
| `WaterAllocation` | Water rights allocation |
| `WaterMeter` | Water meter readings |
| `WaterQualityTest` | Water quality analysis |
| `IrrigationEfficiencyMetrics` | Efficiency calculations |
| `MEWAComplianceReport` | MEWA compliance report |
| `WellExtractionReport` | Well extraction report |

#### Regulatory Standards | المعايير التنظيمية

| Standard | Description |
|----------|-------------|
| `SaudiWaterStandards` | MEWA and NWC requirements |
| Groundwater limits | Extraction quotas by region |
| Quality parameters | TDS, pH, SAR, Boron limits |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.water_management import (
    WaterSource,
    WaterSourceType,
    WaterLevelMonitor,
    WaterQualityMonitor,
    IrrigationEfficiencyCalculator,
    WaterReportGenerator,
    SaudiWaterStandards,
)

# Define water source
well = WaterSource(
    id="WELL-001",
    name="Main Farm Well",
    name_ar="البئر الرئيسي للمزرعة",
    source_type=WaterSourceType.GROUNDWATER,
    location=GeoLocation(latitude=24.7, longitude=46.7),
    max_extraction_m3_day=500,
    current_depth_m=85,
)

# Monitor water levels
monitor = WaterLevelMonitor(source=well)
trend = monitor.analyze_trend(days=90)

print(f"Current depth: {trend.current_level_m}m")
print(f"Trend: {trend.trend_direction.value}")
print(f"Depletion rate: {trend.depletion_rate_m_year} m/year")

if trend.alert:
    print(f"ALERT: {trend.alert.message}")
    print(f"تنبيه: {trend.alert.message_ar}")

# Calculate irrigation efficiency
calculator = IrrigationEfficiencyCalculator(field_id="FIELD-001")
metrics = calculator.calculate(
    water_applied_m3=450,
    area_ha=10,
    crop_et_mm=45,
    rainfall_mm=5,
)

print(f"Application efficiency: {metrics.application_efficiency}%")
print(f"Distribution uniformity: {metrics.distribution_uniformity}%")
print(f"Water use efficiency: {metrics.wue_kg_m3} kg/m³")

# Check against Saudi standards
standards = SaudiWaterStandards()
if metrics.application_efficiency < standards.min_efficiency:
    print("Below MEWA recommended efficiency!")

# Generate MEWA compliance report
generator = WaterReportGenerator(farm_id="FARM-001")
report = generator.generate_mewa_report(
    period_start=date(2026, 1, 1),
    period_end=date(2026, 3, 31),
)

print(f"Total extraction: {report.total_extraction_m3} m³")
print(f"Quota used: {report.quota_utilization_percent}%")
print(f"Compliance status: {report.compliance_status.value}")

if report.issues:
    for issue in report.issues:
        print(f"Issue: {issue.description}")
        print(f"المشكلة: {issue.description_ar}")
```

#### Integration | التكامل

- **irrigation-smart**: Irrigation scheduling
- **iot-service**: Meter and sensor data
- **billing-core**: Water usage billing

---

## 14. weather_alerts

### تنبيهات الطقس | Weather Alerts Module

**Location**: `shared/weather_alerts/`
**Version**: 16.0.0
**Files**: `__init__.py`, `alerts.py`, `models.py`, `spray_window.py`

#### Purpose | الغرض

Enhanced weather alerts for agricultural operations:
- Severe weather alerts (frost, heat, wind, hail)
- Spray window optimization
- Irrigation scheduling based on forecast
- Harvest timing recommendations

تنبيهات طقس محسنة للعمليات الزراعية:
- تنبيهات الطقس الشديد (الصقيع، الحرارة، الرياح، البَرَد)
- تحسين نوافذ الرش
- جدولة الري بناءً على التوقعات
- توصيات توقيت الحصاد

#### Key Classes | الفئات الرئيسية

```python
# Alert Generation
WeatherAlertGenerator         # Generate weather alerts
AlertGeneratorConfig          # Alert configuration

# Spray Windows
SprayWindowCalculator         # Calculate spray windows
SprayWindowConfig             # Spray window configuration
detect_inversions()           # Detect temperature inversions
find_spray_windows()          # Find optimal spray times
```

#### Key Models | النماذج الرئيسية

| Model | Description |
|-------|-------------|
| `WeatherForecast` | Hourly/daily forecast |
| `WeatherAlert` | Generated weather alert |
| `SprayWindow` | Optimal spray window |
| `IrrigationSchedule` | Weather-based irrigation plan |
| `HarvestWindow` | Optimal harvest timing |
| `AlertThresholds` | Crop-specific thresholds |

#### Alert Types | أنواع التنبيهات

| Alert | English | العربية | Trigger |
|-------|---------|---------|---------|
| FROST | Frost Warning | تحذير صقيع | Temp < crop threshold |
| HEAT | Heat Stress | إجهاد حراري | Temp > crop threshold |
| WIND | High Wind | رياح قوية | Wind > 35 km/h |
| HAIL | Hail Risk | خطر البَرَد | Hail probability > 50% |
| RAIN | Heavy Rain | أمطار غزيرة | Precip > 50mm/day |

#### Usage Examples | أمثلة الاستخدام

```python
from shared.weather_alerts import (
    WeatherAlertGenerator,
    SprayWindowCalculator,
    WeatherForecast,
    CropType,
    generate_weather_alerts,
    find_spray_windows,
    detect_inversions,
)
from datetime import date, datetime

# Create forecast
forecast = WeatherForecast(
    forecast_date=date.today(),
    temperature_min=-2.0,
    temperature_max=15.0,
    humidity=75.0,
    wind_speed=20.0,
    precipitation_probability=10.0,
)

# Generate weather alerts
alerts = generate_weather_alerts(
    forecasts=[forecast],
    crop_type=CropType.WHEAT,
    field_id="FIELD-001",
)

for alert in alerts:
    print(f"{alert.get_priority_icon()} {alert.title}")
    print(f"   {alert.title_ar}")
    print(f"   Severity: {alert.severity.value}")
    for action in alert.recommended_actions:
        print(f"   - {action}")
    for action_ar in alert.recommended_actions_ar:
        print(f"   - {action_ar}")

# Find spray windows
hourly_forecasts = [...]  # List of hourly forecasts
windows = find_spray_windows(
    hourly_forecasts=hourly_forecasts,
    min_duration_hours=2.0,
)

for window in windows:
    print(f"Window: {window.start_time} - {window.end_time}")
    print(f"Duration: {window.duration_hours} hours")
    print(f"Score: {window.score}/100")
    print(f"Condition: {window.overall_condition.value}")
    print(f"Drift Risk: {window.drift_risk}")
    print(f"خطر الانجراف: {window.drift_risk_ar}")

# Detect temperature inversions (dangerous for spraying)
inversions = detect_inversions(hourly_forecasts)
for start, end in inversions:
    print(f"INVERSION: {start} - {end}")
    print("  DO NOT spray during this period!")
    print("  لا ترش خلال هذه الفترة!")

# Generate irrigation schedule
generator = WeatherAlertGenerator()
schedule = generator.generate_irrigation_schedule(
    forecasts=forecasts,
    field_id="FIELD-001",
    crop_type=CropType.WHEAT,
    soil_moisture_current=35.0,
    planned_irrigation_mm=25.0,
)

print(f"Recommendation: {schedule.recommendation.value}")
print(f"Reason: {schedule.reason}")
print(f"السبب: {schedule.reason_ar}")

# Get harvest window
harvest = generator.generate_harvest_window(
    forecasts=forecasts,
    field_id="FIELD-001",
    crop_type=CropType.WHEAT,
)

print(f"Harvest condition: {harvest.overall_condition.value}")
print(f"Optimal date: {harvest.optimal_date}")
print(f"Recommendation: {harvest.recommendation}")
print(f"التوصية: {harvest.recommendation_ar}")
```

#### Integration | التكامل

- **weather-service**: Weather forecasts
- **pesticide_compliance**: Spray timing
- **advisory-service**: Weather-based advisories

---

## Module Dependencies | تبعيات الوحدات

```
                    ┌─────────────────┐
                    │  weather_alerts │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐  ┌───────────────┐  ┌─────────────────┐
│   irrigation    │  │ pest_scouting │  │  ml_irrigation  │
│      (HMC)      │  │               │  │                 │
└────────┬────────┘  └───────┬───────┘  └────────┬────────┘
         │                   │                   │
         │                   ▼                   │
         │           ┌───────────────┐           │
         │           │  pesticide_   │           │
         │           │  compliance   │           │
         │           └───────────────┘           │
         │                                       │
         ▼                                       ▼
┌─────────────────┐                    ┌─────────────────┐
│ water_management│                    │   soil_sensors  │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         └──────────────┬───────────────────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  soil_testing   │
               └────────┬────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│  fertilizer │ │crop_rotation│ │ harvest_quality │
│  management │ │             │ │                 │
└─────────────┘ └─────────────┘ └─────────────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  agri_calendar  │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ field_boundaries│
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  crop_insurance │
               └─────────────────┘
```

---

## Common Patterns | الأنماط الشائعة

### Bilingual Content | المحتوى ثنائي اللغة

All modules provide bilingual support:

```python
# Every model includes Arabic fields
class Alert:
    title: str          # English
    title_ar: str       # العربية
    message: str        # English
    message_ar: str     # العربية

# Recommendations include both languages
recommendation = engine.generate()
print(recommendation.summary)     # English
print(recommendation.summary_ar)  # العربية
```

### Error Handling | معالجة الأخطاء

Each module defines its own exceptions:

```python
from shared.crop_insurance import InsuranceException, InsuranceErrors
from shared.irrigation import HMCEngineError, GoalsNotSetError
from shared.harvest_quality import QualityException, QualityErrors

try:
    result = engine.process()
except InsuranceException as e:
    print(f"Error: {e.message}")
    print(f"خطأ: {e.message_ar}")
```

### Configuration Pattern | نمط التكوين

Most modules use config classes:

```python
from shared.ml_irrigation import PredictorConfig, IrrigationPredictor

config = PredictorConfig(
    confidence_threshold=0.8,
    enable_caching=True,
    model_version="v2.0",
)

predictor = IrrigationPredictor(config)
```

### Factory Functions | دوال المصنع

Quick-start functions for common use cases:

```python
# Quick functions available in most modules
from shared.agri_calendar import get_current_season
from shared.ml_irrigation import predict_irrigation
from shared.soil_testing import interpret_soil_test
from shared.weather_alerts import generate_weather_alerts
```

---

## Testing | الاختبار

All modules include comprehensive tests:

```bash
# Run all agricultural module tests
pytest shared/agri_calendar/ shared/crop_insurance/ shared/crop_rotation/ \
       shared/fertilizer_management/ shared/field_boundaries/ shared/harvest_quality/ \
       shared/irrigation/ shared/ml_irrigation/ shared/pest_scouting/ \
       shared/pesticide_compliance/ shared/soil_sensors/ shared/soil_testing/ \
       shared/water_management/ shared/weather_alerts/ -v

# Run specific module tests
pytest shared/irrigation/ -v

# Run with coverage
pytest shared/ --cov=shared --cov-report=html
```

---

## Version History | تاريخ الإصدارات

| Version | Date | Changes |
|---------|------|---------|
| 16.0.0 | Jan 2026 | Platform version alignment |
| 1.0.0 | Jan 2026 | Initial release of all modules |

---

## References | المراجع

- **FAO Irrigation Guidelines**: Water management calculations
- **Saudi MEWA Regulations**: Water compliance standards
- **Islamic Calendar**: Hijri date calculations
- **Traditional Arab Farming**: Anwa'a seasonal knowledge
- **Middle East Pest Database**: Regional pest information

---

_Last Updated: January 2026_
_SAHOOL Platform - National Agricultural Intelligence Platform_
_منصة سهول - المنصة الوطنية للذكاء الزراعي_
