# Fertigation Engine | محرك التسميد بالري

**Service Name:** fertigation-engine
**Type:** Python/FastAPI
**Port:** 8252
**Version:** 16.0.0
**Status:** Active

**Arabic Name:** محرك التسميد بالري
**Arabic Description:** محرك متكامل لإدارة التسميد والري مع قاعدة بيانات NPK حسب المحصول والمرحلة النموية، وإدارة الملوحة الواعية للموصلية الكهربائية وتقييم المخاطر البيئية.

---

## Table of Contents | جدول المحتويات

1. [Overview](#overview) | [نظرة عامة](#نظرة-عامة)
2. [Architecture](#architecture) | [البنية المعمارية](#البنية-المعمارية)
3. [API Endpoints](#api-endpoints) | [نقاط نهاية الـ API](#نقاط-نهاية-الـ-api)
4. [Supported Crops](#supported-crops) | [المحاصيل المدعومة](#المحاصيل-المدعومة)
5. [Fertilizer Database](#fertilizer-database) | [قاعدة بيانات الأسمدة](#قاعدة-بيانات-الأسمدة)
6. [Growth Phases](#growth-phases) | [المراحل النموية](#المراحل-النموية)
7. [Algorithms](#algorithms) | [الخوارزميات](#الخوارزميات)
8. [NATS Events](#nats-events) | [أحداث NATS](#أحداث-nats)
9. [Dependencies](#dependencies) | [المتطلبات](#المتطلبات)
10. [Environment Variables](#environment-variables) | [متغيرات البيئة](#متغيرات-البيئة)
11. [Usage Examples](#usage-examples) | [أمثلة الاستخدام](#أمثلة-الاستخدام)
12. [Error Handling](#error-handling) | [معالجة الأخطاء](#معالجة-الأخطاء)

---

## Overview | نظرة عامة

### English

The **Fertigation Engine** is an integrated fertilizer + irrigation management service for the SAHOOL platform, providing:

- **NPK Database by Crop × Growth Stage**: Comprehensive nitrogen, phosphorus, and potassium requirements for 8 supported crops across 8 growth phases
- **Fertigation Scheduling**: Calculates optimal fertilizer injection rates and application timing
- **Nutrient Balance Tracking**: Monitors cumulative nutrient application and removal (harvest, erosion)
- **Salinity-Aware EC Management**: Computes electrical conductivity (EC) contribution of fertilizers and manages solution salinity within crop tolerance limits
- **Environmental Risk Assessment**: Evaluates nitrogen and phosphorus leaching risks based on application rates
- **11 Fertilizer Types with Arabic Nomenclature**: Urea, DAP, MAP, KCl, SOP, Ammonium Nitrate, Calcium Nitrate, Potassium Nitrate, and NPK blends
- **Bilingual Output**: All recommendations and alerts in Arabic and English

**Key Features:**
- WOFOST-compatible crop growth simulation interface
- Soil nutrient credit calculations (30-50% utilization efficiency)
- Fertilizer preference system (user-selectable sources for N, P, K)
- Cost tracking (SAR/hectare) for economic analysis
- Integrated NATS event publishing for downstream services

### العربية

**محرك التسميد بالري** هو خدمة متكاملة لإدارة التسميد والري في منصة سهول، توفر:

- **قاعدة بيانات NPK حسب المحصول والمرحلة النموية**: متطلبات شاملة للنيتروجين والفوسفور والبوتاسيوم لـ 8 محاصيل مدعومة عبر 8 مراحل نموية
- **جدولة التسميد بالري**: حساب معدلات حقن الأسمدة المثلى وتوقيت التطبيق
- **تتبع توازن المغذيات**: مراقبة التطبيق التراكمي للمغذيات والإزالة (الحصاد، الانجراف)
- **إدارة الملوحة الواعية للموصلية الكهربائية**: حساب مساهمة الموصلية الكهربائية للأسمدة وإدارة ملوحة المحلول ضمن حدود تحمل المحصول
- **تقييم المخاطر البيئية**: تقييم مخاطر تسرب النيتروجين والفوسفور بناءً على معدلات التطبيق
- **11 نوع سماد بالأسماء العربية**: يوريا، DAP، MAP، كلوريد البوتاسيوم، سلفات البوتاسيوم، ونترات الأمونيوم والكالسيوم والبوتاسيوم والمخاليط
- **مخرجات ثنائية اللغة**: جميع التوصيات والتنبيهات بالعربية والإنجليزية

---

## Architecture | البنية المعمارية

### Directory Structure | هيكل المجلدات

```
apps/services/fertigation-engine/
├── Dockerfile                    # Container configuration
├── requirements.txt              # Python dependencies
├── README.md                     # Service documentation
├── src/
│   ├── __init__.py
│   └── main.py                   # FastAPI application with FertigationEngine
└── tests/
    ├── __init__.py
    ├── test_health.py            # Health check tests
    └── ...                        # Additional test files
```

### Core Components | المكونات الأساسية

**FertigationEngine Class** - Main calculation engine:
- `calculate_fertigation(req)` - Generate complete fertigation plan with NPK, EC, cost, and recommendations
- `_select_fertilizers()` - Greedy optimizer for fertilizer combination selection
- `_assess_n_loss_risk()` - Evaluate nitrogen leaching potential
- `_assess_p_loss_risk()` - Evaluate phosphorus leaching potential
- `_generate_recommendations()` - Bilingual advisory generation

**Data Models (Pydantic):**
- `FertigationRequest` - Input parameters for plan calculation
- `FertigationPlan` - Complete output with fertilizer schedule and recommendations
- `NutrientBalanceRequest` - Historical nutrient tracking input
- `NutrientBalance` - Balance analysis with efficiency metrics

---

## API Endpoints | نقاط نهاية الـ API

### Health Check Endpoints | نقاط التحقق من الصحة

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/healthz` | Liveness probe | `{"status": "ok", "service": "fertigation-engine", "version": "16.0.0"}` |
| GET | `/readyz` | Readiness probe | `{"status": "ok", "crops_with_npk": 8, "fertilizers_available": 11, "nats": true}` |

### Fertigation Planning | تخطيط التسميد بالري

#### POST /api/v1/fertigation/plan

**Purpose:** Calculate complete fertigation plan with NPK requirements, fertilizer recommendations, EC management, and environmental risk assessment.

**الغرض:** حساب خطة التسميد بالري الكاملة مع متطلبات NPK وتوصيات الأسمدة وإدارة الموصلية وتقييم المخاطر البيئية.

**Request Schema:**
```json
{
  "crop": "wheat",
  "growth_phase": "tillering",
  "field_area_ha": 5.2,
  "soil_n_ppm": 18.0,
  "soil_p_ppm": 12.5,
  "soil_k_ppm": 85.0,
  "irrigation_volume_m3": 100.0,
  "ec_water": 0.6,
  "max_ec_solution": 2.5,
  "target_yield_tha": 5.0,
  "preferred_fertilizers": ["urea", "dap", "sop"]
}
```

**Field Descriptions:**
- `crop` (string, required): Crop name (e.g., "wheat", "tomato", "date_palm")
- `growth_phase` (enum, required): Current growth phase (germination|seedling|vegetative|tillering|flowering|fruit_development|ripening|harvest)
- `field_area_ha` (float, default=1.0): Field area in hectares (≥0.01 ha)
- `soil_n_ppm` (float, optional): Current soil nitrogen in ppm (for nutrient credit calculation)
- `soil_p_ppm` (float, optional): Current soil phosphorus in ppm
- `soil_k_ppm` (float, optional): Current soil potassium in ppm
- `irrigation_volume_m3` (float, required): Irrigation volume per event in cubic meters
- `ec_water` (float, default=0.5): EC of irrigation water (dS/m, electrical conductivity units)
- `max_ec_solution` (float, default=2.5): Maximum tolerable EC of fertigation solution (dS/m)
- `target_yield_tha` (float, optional): Target yield in tonnes/hectare (for future yield prediction models)
- `preferred_fertilizers` (array, optional): User-preferred fertilizer types (see FertilizerType enum)

**Response Schema:**
```json
{
  "crop": "wheat",
  "crop_ar": "القمح",
  "growth_phase": "tillering",
  "field_area_ha": 5.2,
  "n_required_kg_ha": 60.0,
  "p_required_kg_ha": 15.0,
  "k_required_kg_ha": 20.0,
  "n_adjusted_kg_ha": 45.2,
  "p_adjusted_kg_ha": 12.0,
  "k_adjusted_kg_ha": 18.0,
  "fertilizer_plan": [
    {
      "fertilizer": "map",
      "name": "Mono-Ammonium Phosphate",
      "name_ar": "فوسفات أحادي الأمونيوم",
      "amount_kg": 23.08,
      "n_supplied_kg": 2.54,
      "p_supplied_kg": 12.00,
      "k_supplied_kg": 0.0,
      "ec_contribution": 0.005,
      "cost_sar": 80.78
    },
    {
      "fertilizer": "urea",
      "name": "Urea",
      "name_ar": "يوريا",
      "amount_kg": 98.26,
      "n_supplied_kg": 45.2,
      "p_supplied_kg": 0.0,
      "k_supplied_kg": 0.0,
      "ec_contribution": 0.108,
      "cost_sar": 245.65
    },
    {
      "fertilizer": "sop",
      "name": "Potassium Sulfate (SOP)",
      "name_ar": "سلفات البوتاسيوم",
      "amount_kg": 36.00,
      "n_supplied_kg": 0.0,
      "p_supplied_kg": 0.0,
      "k_supplied_kg": 18.0,
      "ec_contribution": 0.043,
      "cost_sar": 144.00
    }
  ],
  "ec_water": 0.6,
  "ec_fertilizer_contribution": 0.156,
  "ec_total": 0.756,
  "ec_within_limit": true,
  "total_cost_sar": 470.43,
  "cost_per_ha_sar": 90.47,
  "n_loss_risk": "moderate",
  "n_loss_risk_ar": "متوسط",
  "p_loss_risk": "low",
  "p_loss_risk_ar": "منخفض",
  "recommendations": [
    "Apply nitrogen early morning to reduce volatilization losses.",
    "Monitor soil moisture during fruit development."
  ],
  "recommendations_ar": [
    "طبّق النيتروجين في الصباح الباكر لتقليل فقد التطاير.",
    "راقب رطوبة التربة أثناء نمو الثمار."
  ]
}
```

**HTTP Responses:**
- `200 OK` - Fertigation plan successfully calculated
- `400 Bad Request` - Invalid input parameters (missing crop data, out-of-range values)
- `500 Internal Server Error` - Calculation failure

---

### Nutrient Balance Tracking | تتبع توازن المغذيات

#### POST /api/v1/fertigation/nutrient-balance

**Purpose:** Calculate cumulative nutrient balance (applied vs. removed) and efficiency metrics for a field.

**الغرض:** حساب توازن المغذيات التراكمي (المطبق مقابل المزال) ومؤشرات الكفاءة للحقل.

**Request Schema:**
```json
{
  "field_id": "FIELD-003",
  "crop": "wheat",
  "entries": [
    {
      "date": "2025-01-10",
      "type": "applied",
      "n_kg": 120.0,
      "p_kg": 60.0,
      "k_kg": 75.0
    },
    {
      "date": "2025-03-20",
      "type": "removed",
      "n_kg": 95.0,
      "p_kg": 52.0,
      "k_kg": 68.0
    }
  ]
}
```

**Field Descriptions:**
- `field_id` (string, required): Unique field identifier
- `crop` (string, required): Crop name for context
- `entries` (array, required): List of nutrient transactions
  - `date` (string): Transaction date (ISO 8601)
  - `type` (string): "applied" (fertilizer) or "removed" (harvest/erosion)
  - `n_kg`, `p_kg`, `k_kg` (floats): Nutrient amounts in kg

**Response Schema:**
```json
{
  "field_id": "FIELD-003",
  "crop": "wheat",
  "n_balance_kg_ha": 25.0,
  "p_balance_kg_ha": 8.0,
  "k_balance_kg_ha": 7.0,
  "n_efficiency_pct": 79.2,
  "p_efficiency_pct": 86.7,
  "k_efficiency_pct": 90.7,
  "surplus_alert": false,
  "deficit_alert": false,
  "recommendations": [
    "N balance stable. Continue current application rates.",
    "P efficiency good. No adjustments needed."
  ],
  "recommendations_ar": [
    "توازن النيتروجين مستقر. استمر في معدلات التطبيق الحالية.",
    "كفاءة الفوسفور جيدة. لا حاجة لتعديلات."
  ]
}
```

**Interpretation:**
- **Balance = Applied - Removed**
  - Positive: Nutrient accumulation (may increase risk of leaching)
  - Negative: Nutrient depletion (risk of deficiency)
- **Efficiency = (Removed / Applied) × 100%**
  - >80%: Excellent (crop and soil uptake efficient)
  - 60-80%: Good (acceptable loss from leaching/erosion)
  - <60%: Poor (excess losses, review application strategy)

---

### Reference Data Endpoints | نقاط نهاية البيانات المرجعية

#### GET /api/v1/fertigation/fertilizers

**Purpose:** List all available fertilizers with NPK content and pricing.

**الغرض:** عرض قائمة بجميع الأسمدة المتاحة مع محتوى NPK والتسعير.

**Response:**
```json
{
  "fertilizers": [
    {
      "type": "urea",
      "name": "Urea",
      "name_ar": "يوريا",
      "n": 46.0,
      "p": 0.0,
      "k": 0.0,
      "ec_per_gl": 1.1,
      "solubility_gl": 1080,
      "price_sar_kg": 2.5
    },
    {
      "type": "dap",
      "name": "Di-Ammonium Phosphate",
      "name_ar": "فوسفات ثنائي الأمونيوم",
      "n": 18.0,
      "p": 46.0,
      "k": 0.0,
      "ec_per_gl": 0.86,
      "solubility_gl": 575,
      "price_sar_kg": 3.0
    }
  ],
  "total": 11
}
```

#### GET /api/v1/fertigation/crops/{crop_name}/npk

**Purpose:** Get NPK requirements by growth phase for a specific crop.

**الغرض:** الحصول على متطلبات NPK حسب المرحلة النموية لمحصول معين.

**Response Example (Wheat):**
```json
{
  "crop": "wheat",
  "total_requirements_kg_ha": {
    "n": 120,
    "p": 60,
    "k": 75
  },
  "by_phase": {
    "seedling": {
      "n": 20,
      "p": 30,
      "k": 15,
      "pct_of_total": 15
    },
    "tillering": {
      "n": 60,
      "p": 15,
      "k": 20,
      "pct_of_total": 35
    }
  }
}
```

#### GET /api/v1/fertigation/crops

**Purpose:** List all crops with NPK requirements.

**الغرض:** عرض قائمة بجميع المحاصيل ومتطلبات NPK.

**Response:**
```json
{
  "crops": [
    {
      "name": "wheat",
      "total_n": 120,
      "total_p": 60,
      "total_k": 75,
      "phases": 5
    },
    {
      "name": "tomato",
      "total_n": 180,
      "total_p": 100,
      "total_k": 190,
      "phases": 5
    }
  ],
  "total": 8
}
```

#### GET /api/v1/fertigation/growth-phases

**Purpose:** List all supported growth phases.

**الغرض:** عرض قائمة بجميع المراحل النموية المدعومة.

**Response:**
```json
{
  "phases": [
    "germination",
    "seedling",
    "vegetative",
    "tillering",
    "flowering",
    "fruit_development",
    "ripening",
    "harvest"
  ]
}
```

---

## Supported Crops | المحاصيل المدعومة

| Crop Name | Arabic Name | Total N | Total P | Total K | Phases | Notes |
|-----------|-------------|---------|---------|---------|--------|-------|
| **wheat** | القمح | 120 kg/ha | 60 kg/ha | 75 kg/ha | 5 | Winter cereal, high N at tillering |
| **barley** | الشعير | 100 kg/ha | 50 kg/ha | 60 kg/ha | 4 | Drought-tolerant, similar to wheat |
| **date_palm** | النخيل | 130 kg/ha | 65 kg/ha | 210 kg/ha | 4 | High K requirement, perennial |
| **tomato** | الطماطم | 180 kg/ha | 100 kg/ha | 190 kg/ha | 5 | Intensive cultivation, heavy feeder |
| **sorghum** | الذرة الرفيعة | 85 kg/ha | 43 kg/ha | 60 kg/ha | 4 | Drought-tolerant grain |
| **qat** | القات | 130 kg/ha | 45 kg/ha | 95 kg/ha | 3 | Yemen-specific, continuous harvest |
| **coffee_arabica** | القهوة العربية | 120 kg/ha | 55 kg/ha | 125 kg/ha | 4 | Perennial crop, high K for quality |
| **alfalfa** | الجت/البرسيم | 20 kg/ha | 55 kg/ha | 110 kg/ha | 3 | Legume, N-fixing, fodder crop |

### Crop-Specific Notes | ملاحظات خاصة بالمحصول

**Wheat/Barley**: Require maximum N during tillering (35% of total). Reduce N during flowering to prevent excessive vegetative growth.

**Date Palm**: High K demand (210 kg/ha total) for fruit quality. Potassium sulfate (SOP) recommended for saline soils to avoid Cl⁻ accumulation.

**Tomato**: Highest N and K demand. Split applications critical due to continuous fruiting. EC management crucial for greenhouse cultivation.

**Sorghum**: Drought-tolerant but responsive to N in vegetative stage. Conservative P recommendations due to limited availability in arid soils.

**Qat**: Yemen-endemic crop with high N requirement for vegetative growth. Three growth phases: vegetative, flowering, and harvest (harvesting removes significant N).

**Alfalfa**: Nitrogen-fixing legume (Rhizobium symbiosis) requires minimal N but high P for nodulation and K for forage quality.

---

## Fertilizer Database | قاعدة بيانات الأسمدة

### 11 Fertilizer Types | أنواع الأسمدة الـ 11

| Type | Name | Arabic | N% | P% | K% | EC (dS/m per g/L) | Price (SAR/kg) | Solubility (g/L) | Notes |
|------|------|--------|----|----|----|--------------------|-----------------|------------------|-------|
| **urea** | Urea | يوريا | 46 | 0 | 0 | 1.10 | 2.50 | 1080 | Highest N, volatile, apply early morning |
| **dap** | Di-Ammonium Phosphate | فوسفات ثنائي الأمونيوم | 18 | 46 | 0 | 0.86 | 3.00 | 575 | Preferred P source for deficiency |
| **map** | Mono-Ammonium Phosphate | فوسفات أحادي الأمونيوم | 11 | 52 | 0 | 0.80 | 3.50 | 370 | Higher P%, acid-forming |
| **kcl** | K Chloride (MOP) | كلوريد البوتاسيوم | 0 | 0 | 60 | 1.87 | 2.80 | 340 | High EC, avoid in saline soils |
| **sop** | K Sulfate (SOP) | سلفات البوتاسيوم | 0 | 0 | 50 | 1.20 | 4.00 | 110 | Preferred for saline conditions |
| **ammonium_nitrate** | Ammonium Nitrate | نترات الأمونيوم | 34 | 0 | 0 | 1.50 | 2.00 | 1870 | Soluble, fast-acting N |
| **calcium_nitrate** | Calcium Nitrate | نترات الكالسيوم | 15.5 | 0 | 0 | 1.00 | 3.50 | 1290 | Provides Ca²⁺, prevents blossom-end rot |
| **potassium_nitrate** | Potassium Nitrate | نترات البوتاسيوم | 13 | 0 | 46 | 1.20 | 5.00 | 316 | Balanced N+K, premium price |
| **npk_20_20_20** | NPK 20-20-20 | سماد مركب 20-20-20 | 20 | 20 | 20 | 1.30 | 6.00 | 500 | Balanced general purpose |
| **npk_15_15_15** | NPK 15-15-15 | سماد مركب 15-15-15 | 15 | 15 | 15 | 1.10 | 5.00 | 450 | Lower analysis, cost-effective |
| **phosphoric_acid** | Phosphoric Acid (85%) | حمض الفوسفوريك | 0 | 52 | 0 | 0.60 | 4.50 | 5480 | Highly soluble, for P deficiency, acidifying |

### Fertilizer Selection Strategy | استراتيجية اختيار الأسمدة

The engine uses a **greedy optimizer** to select the optimal fertilizer combination:

1. **Phosphorus First**: P sources are limited and expensive; prioritize P deficit
2. **Nitrogen Second**: Address remaining N requirement after P source supplies N as byproduct
3. **Potassium Last**: K selection depends on soil EC:
   - **EC > 1.5 dS/m (saline)**: Use SOP (sulfate) to avoid Cl⁻ accumulation
   - **EC ≤ 1.5 dS/m (normal)**: Use KCl (chloride) for cost savings

**User Preferences**: If `preferred_fertilizers` list is provided, the engine will select from that list before falling back to defaults.

**EC Management**: Total solution EC = Water EC + Fertilizer EC contribution. Must not exceed `max_ec_solution` to prevent osmotic stress.

---

## Growth Phases | المراحل النموية

The engine recognizes **8 growth phases** aligned with crop phenology:

| Phase | Duration (Days) | Characteristics | N Demand | K Demand | Management Notes |
|-------|-----------------|-----------------|----------|----------|------------------|
| **GERMINATION** | 7-14 | Seed imbibition, radicle emergence | Low | Low | Establish root system, minimal nutrient demand |
| **SEEDLING** | 14-28 | True leaves appear, tap root develops | Low-Moderate | Low-Moderate | Phosphorus critical for root development |
| **VEGETATIVE** | 21-45 | Leaf area expansion, stolon/runner formation | High | Moderate-High | Peak N demand for leaf production |
| **TILLERING** | 14-35 | Shoot multiplication (cereals), branch development (others) | Very High | Moderate | Maximum N application (critical period) |
| **FLOWERING** | 7-21 | Flower bud initiation, floret development | Moderate | High | Reduce N to prevent excessive vegetative growth; increase K for flower retention |
| **FRUIT_DEVELOPMENT** | 21-45 | Cell division, seed development, fruit enlargement | Moderate-High | Very High | K critical for fruit size and quality; reduce N to prevent cracking |
| **RIPENING** | 14-28 | Color development, TSS accumulation, senescence | Low | Moderate | Minimal N; K supports quality and shelf-life |
| **HARVEST** | 0+ | Ready for harvest | None | None | No nutrient applications |

### Phase-Specific Examples | أمثلة خاصة بالمرحلة

**Example 1: Wheat at Tillering (Maximum N)**
- Growth Phase: TILLERING
- NPK Allocation: 60% N (of total 120 kg/ha = 60 kg/ha N)
- Reason: Shoot multiplication critical; maximum dry matter accumulation
- Application Method: Split into 2-3 fertigations (mid-morning to reduce volatilization)

**Example 2: Tomato at Flowering (Balanced NPK)**
- Growth Phase: FLOWERING
- NPK: 40% N, 30% P, 50% K
- Reason: Reduce N to prevent excessive vegetative growth and fruit cracking
- EC Management: Total EC should stay <1.8 dS/m for fruit quality

**Example 3: Date Palm at Fruit Development (K-Rich)**
- Growth Phase: FRUIT_DEVELOPMENT
- NPK: 50% N, 15% P, 80% K (high K-to-N ratio)
- Reason: Large fruit development requires sustained K supply
- Application: Fertigate 3-4 times during this 45-day phase

---

## Algorithms | الخوارزميات

### 1. Soil Nutrient Credit System | نظام ائتمان المغذيات في التربة

The engine adjusts NPK requirements based on existing soil nutrient content:

```
N Credit = soil_n_ppm × 2.0 kg/ha per ppm
N Adjusted = max(0, N_required - N_credit × 0.30)  // Use 30% of soil N

P Credit = soil_p_ppm × 1.5 kg/ha per ppm
P Adjusted = max(0, P_required - P_credit × 0.20)  // Use 20% of soil P

K Credit = soil_k_ppm × 1.2 kg/ha per ppm
K Adjusted = max(0, K_required - K_credit × 0.20)  // Use 20% of soil K
```

**Rationale**: Soil nutrient availability depends on soil pH, organic matter, and clay content. These conservative multipliers (20-30% utilization) account for:
- Sorption/fixation of nutrients
- Microbial immobilization
- Rhizosphere depletion zones
- Seasonal moisture availability

### 2. Fertilizer Selection (Greedy Optimization) | اختيار الأسمدة (التحسين الجشع)

```python
# Step 1: Select P source (highest P% available)
p_amount_needed_kg = p_adjusted_kg_ha × field_area_ha
selected_p_fertilizer = user_preferred("p") or "map"  # Default: MAP (52% P)
p_amount_kg = p_amount_needed_kg / (p_fertilizer.p_content / 100)

# Step 2: Calculate N from P source byproduct
n_from_p_source = p_amount_kg × (p_fertilizer.n_content / 100)
remaining_n_kg = (n_adjusted_kg_ha × field_area_ha) - n_from_p_source

# Step 3: Select N source if remaining N > 0
if remaining_n_kg > 0:
    selected_n_fertilizer = user_preferred("n") or "urea"  # Default: Urea (46% N)
    n_amount_kg = remaining_n_kg / (n_fertilizer.n_content / 100)

# Step 4: Select K source based on soil EC
if ec_water > 1.5:  # Saline soil
    selected_k_fertilizer = "sop"  # Sulfate avoids Cl⁻
else:
    selected_k_fertilizer = "kcl"  # Chloride (cheaper)

k_amount_needed_kg = k_adjusted_kg_ha × field_area_ha
k_amount_kg = k_amount_needed_kg / (k_fertilizer.k_content / 100)
```

**Why Greedy?** This approach:
- Minimizes fertilizer cost (fewest items to source)
- Reduces EC contribution (fewer salts)
- Respects user preferences
- Handles multi-nutrient sources (e.g., DAP supplies both N and P)

### 3. Electrical Conductivity (EC) Management | إدارة الموصلية الكهربائية

EC is critical for crop health and relates to osmotic potential:

```
EC_total = EC_water + EC_fertilizer_contribution

EC_fertilizer_contribution = Σ (fertilizer_amount_kg / irrigation_volume_m³) × ec_per_gl
                            = Σ (kg / 1000L) × ec_per_gl

Example:
  - 50 kg Urea dissolved in 100 m³ (100,000 L)
  - EC contribution = (50 / 100,000) × 1.1 = 0.00055 dS/m ≈ 0.0005 dS/m
  - Total EC = 0.6 (water) + 0.156 (all fertilizers) = 0.756 dS/m
```

**Crop EC Tolerance Ranges** (general guidelines, 2.5 dS/m is conservative maximum):
- Wheat/Barley: <2.0 dS/m
- Tomato: <1.8 dS/m (sensitive to salt stress)
- Date Palm: <2.5-3.0 dS/m (salt-tolerant)

**Recommendation**: If EC exceeds limit, the engine recommends splitting the fertigation into multiple lower-concentration applications.

### 4. Nitrogen Loss Risk Assessment | تقييم مخاطر فقد النيتروجين

```
N Loss Risk Classification:
  - High   (n_kg_ha > 80): >80% risk of leaching, immediate mitigation needed
  - Moderate (40-80 kg/ha): 40-80% risk, implement best practices
  - Low    (<40 kg/ha): <40% risk, standard practices acceptable

Risk Mitigation:
  - Apply N early morning (reduce volatilization by ~30%)
  - Split applications (reduce leaching by ~20% per split)
  - Reduce N during flowering (crop uptake low)
  - Monitor rainfall (>25 mm may cause leaching)
```

### 5. Phosphorus Loss Risk Assessment | تقييم مخاطر فقد الفوسفور

```
P Loss Risk Classification:
  - High   (p_kg_ha > 50): Risk of eutrophication, limit applications
  - Moderate (25-50 kg/ha): Monitor runoff and soil test before reapplication
  - Low    (<25 kg/ha): Safe for most soils
```

**Note**: P mobility is lower than N (binds to soil minerals); risk is primarily runoff-based rather than leaching.

---

## NATS Events | أحداث NATS

The service publishes NATS events for downstream consumers (advisory, notification, data pipeline services):

| Event Subject | Trigger | Payload | Purpose |
|---------------|---------|---------|---------|
| `sahool.{tenant_id}.fertigation.plan_created` | Successful plan calculation | `{crop, phase, n_kg, ec_total, timestamp}` | Log plan creation, trigger notifications |
| (Future) `sahool.{tenant_id}.fertigation.high_ec_alert` | EC > max_ec_solution | `{field_id, ec_total, max_ec, recommendation}` | Alert operator to split applications |
| (Future) `sahool.{tenant_id}.fertigation.n_loss_risk` | N loss risk HIGH | `{field_id, n_kg_ha, risk_level, mitigation}` | Trigger environmental advisory |

**Event Publishing Code:**
```python
if nc:  # NATS connection available
    await nc.publish(
        f"sahool.{tenant_id}.fertigation.plan_created",
        json.dumps({
            "crop": req.crop,
            "phase": req.growth_phase.value,
            "n_kg": result.n_adjusted_kg_ha,
            "ec_total": result.ec_total,
            "timestamp": datetime.utcnow().isoformat(),
        }).encode()
    )
```

---

## Dependencies | المتطلبات

### Python Dependencies | متطلبات Python

See `requirements.txt`:

```
# Core
fastapi==0.128.5
starlette>=0.49.1
uvicorn[standard]>=0.30.0,<1.0.0
pydantic==2.13.1
httpx==0.28.1
python-dotenv==1.2.1

# Scientific computing
numpy>=1.26.0,<2.5.0

# Messaging & Cache
nats-py==2.13.1
redis>=7.1.0,<8.0.0

# Observability
structlog>=24.1.0
prometheus-client>=0.21.0

# Testing
pytest==8.4.2
pytest-asyncio==0.26.0
pytest-cov==4.1.0
pytest-mock==3.15.1
```

### Shared Modules (Optional) | الوحدات المشتركة (اختيارية)

The service attempts to import from `shared/` for enhanced functionality:

- `shared.errors_py` - Unified error handling (FastAPI exception handling)
- `shared.yemen.crops` - Yemen-specific crop data (YEMEN_CROPS registry)
- `shared.auth.dependencies` - JWT authentication (future enhancement for protected endpoints)

**Graceful Degradation**: If shared modules are unavailable, the service continues with built-in fallbacks.

---

## Environment Variables | متغيرات البيئة

| Variable | Type | Default | Description | مثال |
|----------|------|---------|-------------|-------|
| `PORT` | int | 8252 | HTTP listening port | `8252` |
| `HOST` | string | 0.0.0.0 | HTTP listening host | `0.0.0.0` or `127.0.0.1` |
| `ENVIRONMENT` | enum | development | Deployment environment | `development`, `staging`, `production` |
| `LOG_LEVEL` | string | INFO | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `NATS_URL` | string | (none) | NATS cluster connection URL | `nats://nats:4222` |
| `TENANT_ID` | string | default | Tenant identifier for NATS event scoping | `farm-001` |
| `REDIS_URL` | string | (none) | Redis cache URL (future use) | `redis://redis:6379` |

### Configuration Examples | أمثلة التكوين

**Development (Docker Compose):**
```bash
PORT=8252
ENVIRONMENT=development
LOG_LEVEL=DEBUG
NATS_URL=nats://nats:4222
TENANT_ID=sahool-demo
```

**Production (K8s):**
```bash
PORT=8252
ENVIRONMENT=production
LOG_LEVEL=WARNING
NATS_URL=nats://nats-cluster:4222
TENANT_ID=${TENANT_ID}  # From ConfigMap
```

---

## Usage Examples | أمثلة الاستخدام

### Example 1: Wheat Fertigation at Tillering | مثال 1: تسميد القمح أثناء الإشطاء

**Scenario**: Farmer has 5.2 ha of wheat (Sakha 95) in the tillering phase. Soil test shows 18 ppm N, 12.5 ppm P, 85 ppm K. Irrigation planned with 100 m³/event from a well (EC 0.6 dS/m).

**Request:**
```bash
curl -X POST http://localhost:8252/api/v1/fertigation/plan \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "wheat",
    "growth_phase": "tillering",
    "field_area_ha": 5.2,
    "soil_n_ppm": 18.0,
    "soil_p_ppm": 12.5,
    "soil_k_ppm": 85.0,
    "irrigation_volume_m3": 100.0,
    "ec_water": 0.6,
    "max_ec_solution": 2.5
  }'
```

**Response Summary**:
- Total Cost: 470 SAR (~90 SAR/ha)
- Fertilizers: MAP (23 kg) + Urea (98 kg) + SOP (36 kg)
- EC: 0.76 dS/m (safe, <2.5)
- N Loss Risk: Moderate → Recommend early morning application

**Farmer Action**: Dissolve 312 kg fertilizer (23+98+36+155 for other splits) into 400 m³ total irrigation volume across 4 events.

---

### Example 2: Tomato Fertigation at Flowering | مثال 2: تسميد الطماطم أثناء الإزهار

**Scenario**: Greenhouse tomato, 2 ha, flowering stage, soil test shows 25 ppm N (adequate). Drip irrigation with 50 m³/event from treated water (EC 0.4 dS/m).

**Request:**
```bash
curl -X POST http://localhost:8252/api/v1/fertigation/plan \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "tomato",
    "growth_phase": "flowering",
    "field_area_ha": 2.0,
    "soil_n_ppm": 25.0,
    "soil_p_ppm": null,
    "soil_k_ppm": null,
    "irrigation_volume_m3": 50.0,
    "ec_water": 0.4,
    "max_ec_solution": 1.8,
    "preferred_fertilizers": ["calcium_nitrate", "dap", "potassium_nitrate"]
  }'
```

**Expected Response**:
- Adjusted N: 32 kg/ha (reduced from 40 due to soil N credit)
- Phosphorus: 30 kg/ha (P critical for flower retention)
- Potassium: 50 kg/ha (high K for flower quality)
- Recommendation: "Reduce N during flowering to prevent excessive vegetative growth. Increase K during fruit development for quality and size."
- EC: ~1.5 dS/m (within greenhouse tolerance <1.8)

---

### Example 3: Nutrient Balance Tracking | مثال 3: تتبع توازن المغذيات

**Scenario**: End-of-season nutrient audit for a wheat field. Track all fertigations and harvest removal.

**Request:**
```bash
curl -X POST http://localhost:8252/api/v1/fertigation/nutrient-balance \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FIELD-WEST-03",
    "crop": "wheat",
    "entries": [
      {"date": "2025-01-10", "type": "applied", "n_kg": 30, "p_kg": 30, "k_kg": 15},
      {"date": "2025-02-15", "type": "applied", "n_kg": 60, "p_kg": 15, "k_kg": 20},
      {"date": "2025-03-20", "type": "applied", "n_kg": 30, "p_kg": 10, "k_kg": 25},
      {"date": "2025-05-10", "type": "removed", "n_kg": 95, "p_kg": 52, "k_kg": 68}
    ]
  }'
```

**Expected Response**:
- N Balance: 25 kg/ha (applied 120, removed 95)
- N Efficiency: 79% (good uptake)
- P Balance: 3 kg/ha (applied 55, removed 52)
- P Efficiency: 95% (excellent)
- K Balance: -8 kg/ha (applied 60, removed 68) ← Deficit
- Recommendation: "Potassium deficit. Consider soil K test before next season. Apply 20-30 kg K/ha in residue or next pre-plant."

**Insight**: Field is mining K slightly; need to increase K application or apply crop residue for next cycle.

---

### Example 4: Accessing Fertilizer Database | مثال 4: الوصول إلى قاعدة بيانات الأسمدة

**Request:**
```bash
curl http://localhost:8252/api/v1/fertigation/fertilizers
```

**Use Case**: Farmer wants to select preferred fertilizers based on price or availability in local market.

---

## Error Handling | معالجة الأخطاء

### HTTP Status Codes | رموز حالة HTTP

| Code | Condition | Example |
|------|-----------|---------|
| **200** | OK | Successful plan calculation or data retrieval |
| **400** | Bad Request | Missing crop, invalid growth phase, negative area |
| **404** | Not Found | Crop name not in database (e.g., `/crops/maize/npk` if maize not supported) |
| **500** | Internal Server Error | Engine calculation failure (rare, indicates bug) |

### Validation Rules | قواعد التحقق

1. **Crop Validation**: Must be in CROP_NPK_REQUIREMENTS (case-insensitive)
2. **Growth Phase Validation**: Must be valid GrowthPhase enum value
3. **Area Validation**: Must be ≥0.01 ha (minimum feasible field)
4. **Irrigation Volume**: Must be >0 m³
5. **EC Values**: Must be positive floats
6. **Soil Nutrients**: Must be non-negative if provided

### Error Response Example | مثال استجابة الخطأ

```json
{
  "detail": "NPK data not found for: maize"
}
```

```json
{
  "detail": "field_area_ha must be >= 0.01"
}
```

---

## Testing | الاختبار

### Test Structure | هيكل الاختبار

```
tests/
├── __init__.py
├── test_health.py          # Health endpoint tests
└── (additional test files)
```

### Running Tests | تشغيل الاختبارات

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_health.py -v
```

### Test Markers | علامات الاختبار

```python
@pytest.mark.unit       # Fast, no I/O
@pytest.mark.integration # Database, API calls
```

---

## Integration with Other Services | التكامل مع الخدمات الأخرى

### Downstream Consumers | المستهلكون التاليون

**Advisory Service** (`advisory-service`, port 8093):
- Consumes: Fertigation plans
- Action: Cross-reference with disease/pest advice
- Integration: NATS event: `sahool.{tenant_id}.fertigation.plan_created`

**Notification Service** (`notification-service`, port 8110):
- Consumes: High EC alerts, N loss risk alerts
- Action: Send farmer notifications
- Integration: NATS event publishing (future)

**Field Intelligence** (`field-intelligence`, port 8120):
- Consumes: Nutrient balance records
- Action: Aggregate field-season metrics for yield prediction
- Integration: Nutrient balance tracking via API

**YOLO26 Vision Service** (`yolo26-vision-service`, port 8150):
- Produces: Disease/pest detection
- Consumed By: Fertigation Engine (contextual recommendations)
- Example: "Pest detected → apply fungicide instead of N"

### Event Flow | تدفق الأحداث

```
Farmer Input (soil test, field data)
    ↓
Fertigation Engine (POST /api/v1/fertigation/plan)
    ↓
NATS Event: sahool.{tenant_id}.fertigation.plan_created
    ↓
Notification Service (send SMS/app notification)
Advisory Service (cross-check with disease risk)
Field Intelligence (store for yield model)
```

---

## Troubleshooting | استكشاف الأخطاء

### Service Won't Start | الخدمة لن تبدأ

**Issue**: `ConnectionRefusedError` on NATS connection
**Solution**: NATS is optional; service starts without it (graceful degradation). Check logs for warnings.

### EC Exceeds Limit | الموصلية تتجاوز الحد

**Issue**: Response shows `ec_within_limit: false`
**Solution**: Recommendation in response: "Split fertigation into multiple applications" (e.g., 2-4 fertigations instead of 1)

### Missing Crop Data | بيانات المحصول مفقودة

**Issue**: `{"detail": "NPK data not found for: xyz"}`
**Solution**: Check supported crops via `GET /api/v1/fertigation/crops`. If crop needed, submit request to extend CROP_NPK_REQUIREMENTS.

### Unrealistic Fertilizer Amounts | كميات الأسمدة غير واقعية

**Issue**: Calculated 500 kg urea for 1 ha (seems excessive)
**Possible Causes**:
- Soil nutrient test values invalid (e.g., 0 ppm, unrealistic)
- `max_ec_solution` too high (allows excessive salt)
- Preferred fertilizers missing critical nutrients (forces less efficient combinations)

**Solution**: Validate soil test. Reduce `max_ec_solution` to 2.0-2.2 for conservative approach.

---

## Performance Characteristics | خصائص الأداء

- **Calculation Time**: <50 ms per plan
- **Memory Usage**: ~15 MB resident set (Python + FastAPI)
- **Throughput**: ~1000 plans/min on single thread (I/O limited by NATS)
- **Scaling**: Horizontal scaling via load balancer (stateless)

---

## Version History | سجل الإصدارات

| Version | Date | Changes |
|---------|------|---------|
| **16.0.0** | 2026-02 | Bilingual README, initial release |

---

## Support & Contributions | الدعم والمساهمات

**Service Owner**: KAFAAT Agricultural Intelligence
**Documentation**: This README + service code
**Issues**: Submit via platform issue tracker
**Contributions**: Follow SAHOOL contribution guidelines (Python 3.11+, FastAPI conventions, Pydantic v2 models)

---

## License | الترخيص

**Proprietary** - SAHOOL Platform v16.0.0
©2026 KAFAAT. All rights reserved.

---

**Last Updated**: February 2026
**Maintainer**: SAHOOL Engineering Team
