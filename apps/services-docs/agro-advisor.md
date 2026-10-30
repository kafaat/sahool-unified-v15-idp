> **⚠️ DEPRECATED**: This service has been replaced by `advisory-service`. See [advisory-service.md](advisory-service.md) for current documentation.

---

# Agro Advisor Service - Comprehensive Analysis

> **DEPRECATED SERVICE** - This service has been deprecated and merged into `advisory-service`.
>
> - **Deprecation Date**: 2025-01-06
> - **Removal Target**: v17.0.0
> - **Replacement**: advisory-service (Port 8093)

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Deprecation Status](#deprecation-status)
3. [API Endpoints](#api-endpoints)
4. [NATS Events](#nats-events)
5. [Request/Response Schemas](#requestresponse-schemas)
6. [Knowledge Base](#knowledge-base)
7. [Dependencies](#dependencies)
8. [Environment Variables](#environment-variables)
9. [Migration Guide](#migration-guide)
10. [Source Files](#source-files)

---

## Service Overview

| Attribute | Value |
|-----------|-------|
| **Service Name** | agro-advisor |
| **Arabic Name** | مستشار الزراعة |
| **Type** | Python / FastAPI |
| **Port** | 8105 (internal), 8095 (legacy in code) |
| **Version** | 16.0.0 (15.3.3 in code) |
| **Status** | DEPRECATED |
| **Layer** | Decision Layer |
| **Category** | Crop Advisory |

### Description

The Agro Advisor service provides intelligent agricultural advisory services for Yemen agriculture including:

- **Disease Diagnosis**: Image-based and symptom-based disease assessment
- **Nutrient Assessment**: NDVI-based and visual deficiency detection
- **Fertilizer Planning**: Stage-based fertilizer recommendations
- **Crop Information**: Growth stages, requirements, and Yemen-specific varieties

### Key Features

1. **Disease Diagnosis (تشخيص الامراض)**
   - Image classification result processing
   - Symptom-based diagnosis matching
   - Weather-adjusted severity recommendations
   - Treatment action recommendations

2. **Nutrient Assessment (تقييم المغذيات)**
   - NDVI-based deficiency detection
   - Visual symptom analysis
   - Soil test result interpretation
   - Correction plan generation

3. **Fertilizer Planning (تخطيط التسميد)**
   - Crop and growth stage-based plans
   - Field size calculations
   - Soil fertility adjustments
   - Irrigation type optimization (drip/surface)

4. **Task Automation Hook**
   - Automatic task creation in FieldOps
   - Event-driven recommendation processing
   - Priority-based due date calculation

---

## Deprecation Status

### Warning

```
DEPRECATED: This service is scheduled for removal in v17.0.0
Use advisory-service:8093 instead
```

### Docker Compose Labels

```yaml
labels:
  - "com.sahool.deprecated=true"
  - "com.sahool.replacement=advisory-service"
  - "com.sahool.replacement.port=8093"
  - "com.sahool.deprecation.reason=Consolidated into unified advisory-service"
  - "com.sahool.deprecation.date=2025-01-06"
  - "com.sahool.removal.version=v17.0.0"
```

### Docker Profiles

The service is only available under the `deprecated` and `legacy` profiles:

```bash
# To run deprecated services
docker compose --profile deprecated up agro-advisor
docker compose --profile legacy up agro-advisor
```

### Functionality Migration

All functionality has been moved to `advisory-service`:

| Agro Advisor | Advisory Service |
|--------------|------------------|
| `/disease/*` | `advisory-service:8093/disease/*` |
| `/nutrient/*` | `advisory-service:8093/nutrient/*` |
| `/fertilizer/*` | `advisory-service:8093/fertilizer/*` |
| `/crops/*` | `advisory-service:8093/crops/*` |

---

## API Endpoints

### Health Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe |

#### Response: `/healthz`

```json
{
  "status": "ok",
  "service": "agro_advisor",
  "version": "15.3.3"
}
```

#### Response: `/readyz`

```json
{
  "status": "ready",
  "service": "agro-advisor",
  "version": "16.0.0",
  "checks": {
    "service": "ready"
  }
}
```

---

### Disease Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/disease/assess` | Assess disease from image classification |
| POST | `/disease/symptoms` | Assess from reported symptoms |
| GET | `/disease/search?q=` | Search diseases by name/symptoms |
| GET | `/disease/crop/{crop}` | Get all diseases for a crop |
| GET | `/disease/{disease_id}` | Get disease information |

#### POST `/disease/assess`

Assess disease from image classification result.

**Request Body:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "condition_id": "string",
  "confidence": 0.85,
  "crop": "tomato",
  "weather": {
    "humidity": 80,
    "temperature": 22,
    "precipitation": 5
  },
  "correlation_id": "uuid"
}
```

**Response:**
```json
{
  "field_id": "field_001",
  "result": {
    "disease_id": "tomato_late_blight",
    "category": "disease",
    "severity": "high",
    "title_ar": "اشتباه اللفحة المتأخرة",
    "title_en": "Suspected Late Blight",
    "actions": ["spray_copper", "spray_mancozeb", "remove_infected_parts"],
    "confidence": 0.85,
    "urgency_hours": 24,
    "details": {
      "symptoms_ar": ["بقع مائية على الاوراق", "..."],
      "symptoms_en": ["Water-soaked lesions on leaves", "..."],
      "pathogen": "Phytophthora infestans"
    }
  },
  "event_id": "uuid",
  "published": true
}
```

#### POST `/disease/symptoms`

Assess possible diseases from reported symptoms.

**Request Body:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "crop": "wheat",
  "symptoms": ["yellow_leaves", "wilting"],
  "lang": "ar",
  "correlation_id": "uuid"
}
```

**Response:**
```json
{
  "field_id": "field_001",
  "results": [
    {
      "disease_id": "wheat_rust",
      "category": "disease",
      "severity": "high",
      "title_ar": "اشتباه صدا القمح",
      "title_en": "Suspected Wheat Rust",
      "actions": ["spray_propiconazole", "spray_tebuconazole"],
      "confidence": 0.75,
      "urgency_hours": 24,
      "details": {
        "matched_symptoms": 2,
        "total_symptoms": 3
      }
    }
  ],
  "event_id": "uuid"
}
```

#### GET `/disease/search?q={query}&lang={ar|en}`

**Response:**
```json
{
  "query": "لفحة",
  "results": [
    {
      "id": "tomato_late_blight",
      "name_ar": "اللفحة المتاخرة",
      "name_en": "Late Blight",
      "crop": "tomato",
      "match": "name"
    }
  ],
  "count": 1
}
```

#### GET `/disease/crop/{crop}`

**Response:**
```json
{
  "crop": "tomato",
  "diseases": [
    {
      "id": "tomato_late_blight",
      "name_ar": "اللفحة المتاخرة",
      "name_en": "Late Blight",
      "crop": "tomato",
      "pathogen": "Phytophthora infestans",
      "severity_default": "high",
      "urgency_hours": 24
    }
  ],
  "count": 3
}
```

#### GET `/disease/{disease_id}?lang={ar|en}`

**Response:**
```json
{
  "id": "tomato_late_blight",
  "name_ar": "اللفحة المتاخرة",
  "name_en": "Late Blight",
  "crop": "tomato",
  "pathogen": "Phytophthora infestans",
  "symptoms_ar": ["بقع مائية على الاوراق", "بقع بنية داكنة"],
  "symptoms_en": ["Water-soaked lesions on leaves", "Dark brown spots"],
  "conditions": {
    "humidity_min": 80,
    "temp_range": [15, 25],
    "spread": "rain_splash"
  },
  "actions": ["spray_copper", "spray_mancozeb"],
  "severity_default": "high",
  "urgency_hours": 24,
  "actions_details": [
    {
      "name_ar": "رش بالنحاس",
      "name_en": "Copper Spray",
      "instructions_ar": "رش بمبيد نحاسي...",
      "instructions_en": "Spray with copper fungicide...",
      "task_type": "spray",
      "priority": "high"
    }
  ]
}
```

---

### Nutrient Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/nutrient/ndvi` | Assess from NDVI data |
| POST | `/nutrient/visual` | Assess from visual indicators |
| GET | `/nutrient/{deficiency_id}` | Get deficiency information |

#### POST `/nutrient/ndvi`

Assess nutrient deficiency from NDVI data.

**Request Body:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "ndvi": 0.35,
  "ndvi_history": [0.65, 0.55, 0.45, 0.35],
  "crop": "wheat",
  "stage": "tillering",
  "correlation_id": "uuid"
}
```

**Response:**
```json
{
  "field_id": "field_001",
  "ndvi": 0.35,
  "results": [
    {
      "deficiency_id": "nitrogen_deficiency",
      "nutrient": "N",
      "category": "nutrient_deficiency",
      "severity": "high",
      "title_ar": "نقص النيتروجين",
      "title_en": "Nitrogen Deficiency",
      "corrections": [
        {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50}
      ],
      "confidence": 0.7,
      "urgency_hours": 48,
      "details": {
        "diagnosis_reason": "severe_ndvi_drop",
        "ndvi_value": 0.35,
        "symptoms_ar": ["اصفرار الاوراق السفلية"]
      }
    }
  ],
  "event_id": "uuid"
}
```

#### POST `/nutrient/visual`

Assess nutrient deficiency from visual indicators.

**Request Body:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "leaf_color": "pale_yellow",
  "pattern": "uniform_chlorosis",
  "location": "older_leaves_first",
  "crop": "tomato",
  "lang": "ar",
  "correlation_id": "uuid"
}
```

**Response:**
```json
{
  "field_id": "field_001",
  "indicators": {
    "leaf_color": "pale_yellow",
    "pattern": "uniform_chlorosis",
    "location": "older_leaves_first"
  },
  "results": [
    {
      "deficiency_id": "nitrogen_deficiency",
      "nutrient": "N",
      "severity": "high",
      "title_ar": "نقص النيتروجين",
      "confidence": 0.7,
      "details": {
        "matched_indicators": ["leaf_color", "pattern", "location"],
        "match_score": 7
      }
    }
  ],
  "event_id": "uuid"
}
```

#### GET `/nutrient/{deficiency_id}`

**Response:**
```json
{
  "id": "nitrogen_deficiency",
  "nutrient": "N",
  "name_ar": "نقص النيتروجين",
  "name_en": "Nitrogen Deficiency",
  "symptoms_ar": ["اصفرار الاوراق السفلية", "تقزم النبات"],
  "symptoms_en": ["Yellowing of lower leaves", "Stunted growth"],
  "visual_indicators": {
    "leaf_color": "pale_yellow",
    "pattern": "uniform_chlorosis",
    "location": "older_leaves_first",
    "ndvi_impact": "severe_decrease"
  },
  "causes": ["poor_soil_fertility", "leaching_from_rain"],
  "corrections": [
    {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50}
  ],
  "severity_default": "high",
  "urgency_hours": 48
}
```

---

### Fertilizer Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/fertilizer/plan` | Generate fertilizer plan |
| GET | `/fertilizer/{fertilizer_id}` | Get fertilizer information |
| GET | `/fertilizer/nutrient/{nutrient}` | Get fertilizers by nutrient |

#### POST `/fertilizer/plan`

Generate fertilizer plan for crop and stage.

**Request Body:**
```json
{
  "tenant_id": "string",
  "field_id": "string",
  "crop": "tomato",
  "stage": "vegetative",
  "field_size_ha": 2.5,
  "soil_fertility": "medium",
  "irrigation_type": "drip",
  "correlation_id": "uuid"
}
```

**Response:**
```json
{
  "field_id": "field_001",
  "crop": "tomato",
  "stage": "vegetative",
  "field_size_ha": 2.5,
  "applications": [
    {
      "product": "Calcium Nitrate",
      "product_ar": "نترات الكالسيوم",
      "dose_kg_per_ha": 97.0,
      "total_kg": 242.5,
      "timing_days": 0,
      "method": "fertigation"
    }
  ],
  "total_cost_estimate": null,
  "notes": [
    "يفضل تقسيم الجرعة على 2-3 ريات",
    "Divide dose over 2-3 irrigations"
  ],
  "event_id": "uuid",
  "published": true
}
```

#### GET `/fertilizer/{fertilizer_id}`

**Response:**
```json
{
  "id": "urea",
  "name_ar": "يوريا",
  "name_en": "Urea",
  "formula": "CO(NH2)2",
  "analysis": {"N": 46, "P": 0, "K": 0},
  "type": "nitrogen",
  "form": "granular",
  "solubility": "high",
  "application_methods": ["broadcast", "side_dress", "foliar"],
  "precautions_ar": ["لا تخلط مع الجير", "تطبيق قبل الري"],
  "precautions_en": ["Do not mix with lime", "Apply before irrigation"],
  "price_tier": "low"
}
```

#### GET `/fertilizer/nutrient/{nutrient}`

**Response:**
```json
{
  "nutrient": "N",
  "fertilizers": [
    {
      "id": "urea",
      "name_ar": "يوريا",
      "name_en": "Urea",
      "analysis": {"N": 46, "P": 0, "K": 0},
      "nutrient_content": 46
    },
    {
      "id": "ammonium_sulfate",
      "name_ar": "سلفات الامونيوم",
      "name_en": "Ammonium Sulfate",
      "analysis": {"N": 21, "P": 0, "K": 0, "S": 24},
      "nutrient_content": 21
    }
  ],
  "count": 5
}
```

---

### Crop Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/crops` | List all crops by category |
| GET | `/crops/categories` | List crop categories with counts |
| GET | `/crops/search?q=` | Search crops by name |
| GET | `/crops/{crop_code}` | Get single crop details |
| GET | `/crops/{crop_code}/varieties` | Get Yemen-specific varieties |
| GET | `/crops/{crop}/stages` | Get growth stages |
| GET | `/crops/{crop}/requirements` | Get nutrient requirements |

#### GET `/crops`

**Response:**
```json
{
  "crops_by_category": {
    "cereals": [
      {
        "code": "wheat",
        "name_en": "Wheat",
        "name_ar": "قمح",
        "scientific_name": "Triticum aestivum",
        "growing_season_days": 120,
        "base_yield_ton_ha": 5.0,
        "water_requirement": "medium",
        "yemen_regions": ["Highlands"],
        "has_local_varieties": true
      }
    ]
  },
  "total_crops": 50,
  "category_counts": {"cereals": 8, "vegetables": 20, "fruits": 12}
}
```

#### GET `/crops/{crop_code}`

**Response:**
```json
{
  "code": "wheat",
  "name_en": "Wheat",
  "name_ar": "قمح",
  "scientific_name": "Triticum aestivum",
  "category": "cereals",
  "growth_habit": "annual",
  "growing_conditions": {
    "growing_season_days": 120,
    "optimal_temp_min": 15,
    "optimal_temp_max": 25,
    "water_requirement": "medium"
  },
  "yield_data": {
    "base_yield_ton_ha": 5.0,
    "yield_unit": "ton"
  },
  "yemen_specific": {
    "suitable_regions": ["Highlands"],
    "local_varieties": ["Sakha 95", "Gemmeiza 11"],
    "variety_count": 5
  },
  "coefficients": {
    "kc_ini": 0.3,
    "kc_mid": 1.15,
    "kc_end": 0.25
  },
  "economics": {
    "price_usd_per_ton": 350
  },
  "varieties_available": 5
}
```

#### GET `/crops/{crop}/stages`

**Response:**
```json
{
  "crop": "tomato",
  "stages": [
    {
      "stage": "transplant",
      "start_day": 0,
      "duration_days": 14,
      "nutrient_focus": ["N", "P", "K"]
    },
    {
      "stage": "vegetative",
      "start_day": 14,
      "duration_days": 30,
      "nutrient_focus": ["N", "P", "K"]
    }
  ]
}
```

#### GET `/crops/{crop}/requirements`

**Response:**
```json
{
  "crop": "tomato",
  "yield_target_ton_ha": 40,
  "total_needs": {"N": 150, "P": 60, "K": 200, "Ca": 80},
  "stages": {
    "transplant": {"N": 0.10, "P": 0.30, "K": 0.10},
    "vegetative": {"N": 0.30, "P": 0.20, "K": 0.20},
    "flowering": {"N": 0.25, "P": 0.25, "K": 0.25},
    "fruiting": {"N": 0.25, "P": 0.15, "K": 0.35}
  }
}
```

---

### Action Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/actions/{action_id}?lang=` | Get detailed action instructions |

#### GET `/actions/{action_id}?lang={ar|en}`

**Response:**
```json
{
  "id": "spray_copper",
  "name_ar": "رش بالنحاس",
  "name_en": "Copper Spray",
  "instructions_ar": "رش بمبيد نحاسي (هيدروكسيد النحاس) بمعدل 2-3 جم/لتر",
  "instructions_en": "Spray with copper fungicide (copper hydroxide) at 2-3 g/L",
  "task_type": "spray",
  "priority": "high"
}
```

---

## NATS Events

### Subject Namespace

All events use the `sahool.advisor` subject prefix.

### Events Published

| Event Type | Subject | Version | Description |
|------------|---------|---------|-------------|
| `recommendation_issued` | `sahool.advisor.recommendation_issued` | 1 | Disease/pest recommendation created |
| `fertilizer_plan_issued` | `sahool.advisor.fertilizer_plan_issued` | 1 | Fertilizer plan generated |
| `nutrient_assessment_issued` | `sahool.advisor.nutrient_assessment_issued` | 1 | Nutrient deficiency assessment |
| `disease_detected` | `sahool.advisor.disease_detected` | 1 | Disease detection event |

### Event Envelope Schema

All events are wrapped in a standard envelope:

```json
{
  "event_id": "uuid",
  "event_type": "recommendation_issued",
  "version": 1,
  "aggregate_id": "field_001",
  "tenant_id": "tenant_001",
  "correlation_id": "uuid",
  "timestamp": "2026-01-25T10:30:00Z",
  "payload": { }
}
```

### Event Payloads

#### recommendation_issued

```json
{
  "field_id": "field_001",
  "category": "disease",
  "severity": "high",
  "title_ar": "اشتباه اللفحة المتاخرة",
  "title_en": "Suspected Late Blight",
  "actions": ["spray_copper", "spray_mancozeb"],
  "confidence": 0.85,
  "details": {
    "symptoms_ar": ["..."],
    "symptoms_en": ["..."],
    "pathogen": "Phytophthora infestans"
  }
}
```

#### fertilizer_plan_issued

```json
{
  "field_id": "field_001",
  "crop": "tomato",
  "stage": "vegetative",
  "plan": [
    {
      "product": "Calcium Nitrate",
      "product_ar": "نترات الكالسيوم",
      "dose_kg_per_ha": 97.0,
      "total_kg": 242.5,
      "timing_days": 0,
      "method": "fertigation"
    }
  ],
  "notes": ["يفضل تقسيم الجرعة على 2-3 ريات"]
}
```

#### nutrient_assessment_issued

```json
{
  "field_id": "field_001",
  "deficiency_id": "nitrogen_deficiency",
  "nutrient": "N",
  "severity": "high",
  "title_ar": "نقص النيتروجين",
  "title_en": "Nitrogen Deficiency",
  "corrections": [
    {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50}
  ],
  "confidence": 0.7
}
```

### Events Subscribed (Task Automation Hook)

The Task Automation Hook subscribes to the following events to create FieldOps tasks:

| Subject | Action |
|---------|--------|
| `advisor.recommendation_issued` | Creates spray/manual tasks |
| `advisor.fertilizer_plan_issued` | Creates fertilization tasks |
| `advisor.nutrient_assessment_issued` | Creates inspection and correction tasks |

---

## Request/Response Schemas

### Request Models

#### DiseaseAssessRequest

```python
class DiseaseAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    condition_id: str
    confidence: float = Field(ge=0, le=1)
    crop: str | None = None
    weather: dict | None = None
    correlation_id: str | None = None
```

#### SymptomAssessRequest

```python
class SymptomAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    symptoms: list[str]
    lang: str = "ar"
    correlation_id: str | None = None
```

#### NDVIAssessRequest

```python
class NDVIAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    ndvi: float = Field(ge=-1, le=1)
    ndvi_history: list[float] | None = None
    crop: str | None = None
    stage: str | None = None
    correlation_id: str | None = None
```

#### VisualAssessRequest

```python
class VisualAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    leaf_color: str | None = None
    pattern: str | None = None
    location: str | None = None
    crop: str | None = None
    lang: str = "ar"
    correlation_id: str | None = None
```

#### FertilizerPlanRequest

```python
class FertilizerPlanRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    stage: str
    field_size_ha: float = 1.0
    soil_fertility: str = "medium"  # low, medium, high
    irrigation_type: str = "drip"   # drip, surface, sprinkler
    correlation_id: str | None = None
```

---

## Knowledge Base

### Supported Crops (24 crops)

| Crop | Arabic | Yield Target (t/ha) | Key Stages |
|------|--------|---------------------|------------|
| tomato | طماطم | 40 | transplant, vegetative, flowering, fruiting, harvest |
| wheat | قمح | 5 | planting, tillering, booting, heading |
| potato | بطاطس | 30 | planting, vegetative, tuber_init, bulking, maturation |
| maize | ذرة | 8 | planting, v6, v12, tasseling, grain_fill |
| onion | بصل | 35 | transplant, vegetative, bulb_init, bulbing, maturation |
| coffee | قهوة | 1.5 | dormant, flowering, fruit_dev, ripening, post_harvest |
| qat | قات | 4 | pruning, flush_1, flush_2, flush_3 |
| barley | شعير | 3.5 | planting, tillering, booting, heading |
| sorghum | ذرة رفيعة | 3.0 | planting, vegetative, boot, heading |
| millet | دخن | 2.0 | planting, tillering, boot, heading |
| faba_bean | فول | 3.0 | planting, vegetative, flowering, pod_fill |
| lentil | عدس | 1.5 | planting, vegetative, flowering, pod_fill |
| chickpea | حمص | 1.8 | planting, vegetative, flowering, pod_fill |
| pepper | فلفل | 30 | transplant, vegetative, flowering, fruiting, harvest |
| eggplant | باذنجان | 35 | transplant, vegetative, flowering, fruiting, harvest |
| cucumber | خيار | 45 | transplant, vegetative, flowering, fruiting |
| garlic | ثوم | 10 | planting, vegetative, bulb_init, bulbing, maturation |
| grape | عنب | 15 | dormant, bud_break, flowering, fruit_set, ripening |
| date_palm | نخيل | 10 | dormant, flowering, fruit_dev, ripening, post_harvest |
| banana | موز | 35 | planting, vegetative, flowering, bunch_dev, harvest |
| mango | مانجو | 12 | dormant, flowering, fruit_set, fruit_dev, ripening |
| sesame | سمسم | 1.0 | planting, vegetative, flowering, pod_fill |
| alfalfa | برسيم | 20 | establishment, growth, pre_cut, post_cut |

### Disease Database

| Disease ID | Crop | Severity | Urgency (hrs) |
|------------|------|----------|---------------|
| tomato_late_blight | tomato | high | 24 |
| tomato_early_blight | tomato | medium | 48 |
| tomato_powdery_mildew | tomato | medium | 72 |
| wheat_rust | wheat | high | 24 |
| potato_late_blight | potato | high | 24 |
| aphid_infestation | general | medium | 48 |
| whitefly_infestation | general | high | 24 |

### Nutrient Deficiencies

| Deficiency ID | Nutrient | Severity | Urgency (hrs) |
|---------------|----------|----------|---------------|
| nitrogen_deficiency | N | high | 48 |
| phosphorus_deficiency | P | medium | 72 |
| potassium_deficiency | K | medium | 72 |
| calcium_deficiency | Ca | high | 24 |
| magnesium_deficiency | Mg | medium | 72 |
| iron_deficiency | Fe | medium | 72 |
| zinc_deficiency | Zn | medium | 72 |

### Fertilizer Database

| Fertilizer ID | Type | N% | P% | K% |
|---------------|------|----|----|-----|
| urea | nitrogen | 46 | 0 | 0 |
| ammonium_sulfate | nitrogen | 21 | 0 | 0 |
| calcium_nitrate | nitrogen_calcium | 15.5 | 0 | 0 |
| tsp | phosphorus | 0 | 46 | 0 |
| dap | nitrogen_phosphorus | 18 | 46 | 0 |
| potassium_sulfate | potassium | 0 | 0 | 50 |
| potassium_chloride | potassium | 0 | 0 | 60 |
| npk_20_20_20 | compound | 20 | 20 | 20 |
| npk_15_15_15 | compound | 15 | 15 | 15 |
| npk_12_12_36 | compound | 12 | 12 | 36 |
| iron_chelate | micronutrient | - | - | - |
| zinc_sulfate | micronutrient | - | - | - |
| magnesium_sulfate | secondary | - | - | - |
| compost | organic | 1.5 | 1 | 1 |

---

## Dependencies

### Python Dependencies (requirements.txt)

```
# Base requirements
fastapi==0.126.0
starlette>=0.49.1
uvicorn[standard]>=0.30.0,<1.0.0
pydantic==2.9.2
httpx==0.28.1
python-dotenv==1.0.1

# Testing
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==4.1.0
pytest-mock==3.12.0

# Service-specific
nats-py==2.9.0
structlog>=24.1.0
```

### Internal Dependencies

- `shared/errors_py/` - Unified error handling
- `apps/services/shared/crops.py` - Crop catalog
- `apps/services/shared/yemen_varieties.py` - Yemen crop varieties

### Infrastructure Dependencies

| Service | Purpose |
|---------|---------|
| PostgreSQL | Data storage (via DATABASE_URL) |
| NATS | Event publishing |
| FieldOps | Task creation (via hooks) |

---

## Environment Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NATS_URL` | NATS server connection URL | `nats://nats:4222` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8105` |
| `DATABASE_URL` | PostgreSQL connection | - |
| `JWT_SECRET_KEY` | JWT secret for auth | - |
| `JWT_ALGORITHM` | JWT algorithm | `RS256` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Runtime environment | `development` |
| `FIELDOPS_URL` | FieldOps service URL | `http://fieldops:8080` |

### Missing Environment Variables

The following environment variables are configured in docker-compose but not used in code:

1. `DATABASE_URL` - Configured but not actively used (no database operations)
2. `JWT_SECRET_KEY` - Configured but no authentication implemented
3. `JWT_ALGORITHM` - Configured but no authentication implemented

---

## Migration Guide

### Step 1: Update Service URLs

Replace all references to `agro-advisor:8105` with `advisory-service:8093`:

```bash
# Old
curl http://agro-advisor:8105/disease/assess

# New
curl http://advisory-service:8093/disease/assess
```

### Step 2: Update Kong Routes

Kong already routes `/api/v1/agro-advisor` to `advisory-service` for backwards compatibility.

For new implementations, use:
- `/api/v1/advisory` - Primary route
- `/api/v1/advice` - Alternative route

### Step 3: Update NATS Subscriptions

Event subjects remain the same (`sahool.advisor.*`).

### Step 4: Update Docker Compose

Remove agro-advisor from your deployment:

```yaml
# Remove from profiles
profiles:
  - deprecated  # Remove
  - legacy      # Remove
```

### Step 5: Verify Migration

```bash
# Test advisory-service endpoints
curl http://advisory-service:8093/healthz
curl http://advisory-service:8093/disease/tomato_late_blight
curl -X POST http://advisory-service:8093/fertilizer/plan \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"test","field_id":"f1","crop":"wheat","stage":"tillering"}'
```

---

## Source Files

### Main Application

| File | Purpose |
|------|---------|
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/main.py` | FastAPI application, all endpoints |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/Dockerfile` | Container definition |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/requirements.txt` | Python dependencies |

### Engine Modules

| File | Purpose |
|------|---------|
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/engine/__init__.py` | Engine exports |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/engine/disease_rules.py` | Disease assessment logic |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/engine/nutrient_rules.py` | Nutrient assessment logic |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/engine/planner.py` | Fertilizer planning |

### Knowledge Base

| File | Purpose |
|------|---------|
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/kb/__init__.py` | KB exports |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/kb/diseases.py` | Disease database |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/kb/fertilizers.py` | Fertilizer database |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/kb/nutrients.py` | Nutrient deficiencies |

### Events

| File | Purpose |
|------|---------|
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/events/__init__.py` | Events exports |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/events/publish.py` | NATS event publisher |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/events/types.py` | Event type definitions |

### Hooks

| File | Purpose |
|------|---------|
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/hooks/__init__.py` | Hooks exports |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/src/hooks/task_automation.py` | Task automation hook |

### Tests

| File | Purpose |
|------|---------|
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/tests/test_health.py` | Health and endpoint tests |
| `/home/user/sahool-unified-v15-idp/apps/services/agro-advisor/tests/test_planner.py` | Fertilizer planner tests |

---

## Kong Gateway Configuration

### Current Routes (kong.yml)

```yaml
- name: agro-advisor
  url: http://agro-advisor:8105
  routes:
    - name: agro-advisor-route
      paths:
        - /api/v1/agro-advisor
        - /api/v1/agro-rules
        - /agro-advisor
        - /agro-advisor-legacy
      strip_path: true
  plugins:
    - name: rate-limiting
      config:
        minute: 500
        hour: 25000
```

### Rate Limiting

| Tier | Requests/min | Requests/hour |
|------|--------------|---------------|
| Default | 500 | 25,000 |

---

## Architecture Position

### Event Layer: Decision

The agro-advisor service is positioned in the **Decision Layer** of SAHOOL's 4-layer event architecture:

```
Acquisition -> Intelligence -> Decision -> Business
                                  |
                            agro-advisor
                                  |
                     Produces recommendations
```

### Events Consumed From

- `FieldIndicatorsComputed.v1` (from Intelligence layer)
- `WeatherForecastReady.v1` (from Acquisition layer)

### Events Produced To

- `AgroAdviceGenerated.v1` (to Business layer)

---

*Last Updated: 2026-01-25*
*Generated by: Claude Code Analysis*
