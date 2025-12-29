# خطة دمج الزراعة الإيكولوجية في منصة SAHOOL
# Ecological Agriculture Integration Plan for SAHOOL Platform

**الإصدار**: 2.0.0 | **تاريخ التحديث**: 2025-12-29
**المصدر**: سلسلة مقالات الزراعة الإيكولوجية 2025 (51 مقالة)
**Repository**: https://github.com/kafaat/sahool-unified-v15-idp

---

## الفهرس | Table of Contents

1. [ملخص تنفيذي](#1-ملخص-تنفيذي)
2. [تحليل البنية الحالية](#2-تحليل-البنية-الحالية)
3. [خطة الدمج التفصيلية](#3-خطة-الدمج-التفصيلية)
4. [نموذج قاعدة البيانات](#4-نموذج-قاعدة-البيانات)
5. [وكيل الخبير الإيكولوجي](#5-وكيل-الخبير-الإيكولوجي)
6. [واجهات المستخدم](#6-واجهات-المستخدم)
7. [تكامل الأحداث](#7-تكامل-الأحداث)
8. [التكامل مع GlobalGAP](#8-التكامل-مع-globalgap)
9. [تطبيق الموبايل](#9-تطبيق-الموبايل)
10. [خطة التنفيذ](#10-خطة-التنفيذ)

---

## 1. ملخص تنفيذي

### 1.1 الهدف
دمج مفاهيم الزراعة الإيكولوجية من سلسلة المقالات (51 مقالة) في منصة SAHOOL لتعزيز:
- تقييم المزارع الإيكولوجية
- تتبع الممارسات المستدامة
- تقديم توصيات بيئية ذكية
- دعم شفافية المعلومات

### 1.2 السلاسل الخمس من المقالات

| السلسلة | المقالات | المفاهيم الأساسية |
|---------|----------|-------------------|
| فهم الزراعة من منظور الإنتاج | 6 | الأرض، العمل، العلم، السلامة، الترقية، المستقبل |
| الحفر الزراعية | 11 | الحجم، الأنواع، الأراضي، العمال، الآثار غير المتوقعة |
| المزرعة البيئية | 16 | التربة الصحية، التتبع، الشهادات الخضراء والعضوية |
| فهم الزراعة الإيكولوجية | 8 | المبادئ البيئية والاقتصادية، الإدارة الحديثة |
| اتجاهات الزراعة 2025 | 10 | شفافية المعلومات، جودة أعلى، صغار المزارعين |

---

## 2. تحليل البنية الحالية

### 2.1 هيكل AI Advisor

```
apps/services/ai-advisor/
├── src/
│   ├── agents/
│   │   ├── base_agent.py          # BaseAgent (ABC)
│   │   ├── disease_expert.py      # DiseaseExpertAgent
│   │   ├── irrigation_advisor.py  # IrrigationAdvisorAgent
│   │   ├── yield_predictor.py     # YieldPredictorAgent
│   │   ├── field_analyst.py       # FieldAnalystAgent
│   │   └── ecological_expert.py   # [جديد] EcologicalExpertAgent
│   ├── rag/
│   │   ├── embeddings.py          # EmbeddingsManager (multilingual)
│   │   └── retriever.py           # KnowledgeRetriever (Qdrant)
│   ├── orchestration/
│   │   ├── supervisor.py          # Supervisor (routing & coordination)
│   │   └── workflow.py            # Workflow (dependency resolution)
│   ├── llm/
│   │   └── multi_provider.py      # MultiLLMService (Claude/GPT/Gemini)
│   └── tools/
│       ├── crop_health_tool.py
│       ├── weather_tool.py
│       ├── satellite_tool.py
│       └── agro_tool.py
```

### 2.2 هيكل قواعد المعرفة

```
apps/services/advisory-service/src/kb/
├── diseases.py       # 7 أمراض (طماطم، قمح، بطاطس، آفات)
├── fertilizers.py    # 14 سماد (NPK، عضوي، عناصر صغرى)
├── nutrients.py      # نقص العناصر مع تشخيص NDVI
├── ecological.py     # [جديد] المبادئ الإيكولوجية
└── pitfalls.py       # [جديد] الحفر الزراعية
```

### 2.3 هيكل قاعدة البيانات الحالي

**40+ جدول** موجود، أهمها:

| الجدول | الغرض | العلاقة مع الإيكولوجي |
|--------|-------|----------------------|
| `fields` | الحقول (PostGIS) | ربط التقييمات |
| `field_crops` | المحاصيل المزروعة | تتبع الدورة الزراعية |
| `ndvi_records` | بيانات القمر الصناعي | مؤشرات صحة التربة |
| `tasks` | المهام الزراعية | تتبع الممارسات |
| `globalgap_registrations` | شهادات GlobalGAP | ربط الشهادات الإيكولوجية |

---

## 3. خطة الدمج التفصيلية

### المرحلة 1: قاعدة المعرفة الإيكولوجية

#### 3.1.1 ملف المبادئ الإيكولوجية

**الموقع**: `apps/services/advisory-service/src/kb/ecological.py`

```python
"""
Ecological Agriculture Knowledge Base - SAHOOL
قاعدة معرفة الزراعة الإيكولوجية
Based on: سلسلة مقالات المزارع البيئية 2025
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class EcologicalIndicator:
    """مؤشر إيكولوجي"""
    id: str
    name_ar: str
    name_en: str
    target_min: float
    target_max: float
    unit: str
    weight: float  # وزن في حساب النتيجة الإجمالية


ECOLOGICAL_PRINCIPLES = {
    "soil_health": {
        "name_ar": "صحة التربة",
        "name_en": "Soil Health",
        "description_ar": "التربة الصحية هي أساس الزراعة الإيكولوجية",
        "description_en": "Healthy soil is the foundation of ecological agriculture",
        "weight": 0.25,
        "indicators": [
            EcologicalIndicator("organic_matter", "المادة العضوية", "Organic Matter",
                              3.0, 6.0, "%", 0.3),
            EcologicalIndicator("ph_level", "درجة الحموضة", "pH Level",
                              6.0, 7.5, "pH", 0.2),
            EcologicalIndicator("microbial_activity", "النشاط الميكروبي", "Microbial Activity",
                              1000000, 10000000, "CFU/g", 0.25),
            EcologicalIndicator("earthworm_count", "عدد ديدان الأرض", "Earthworm Count",
                              10, 50, "per_sqm", 0.15),
            EcologicalIndicator("aggregate_stability", "استقرار التجمعات", "Aggregate Stability",
                              50, 80, "%", 0.1),
        ],
        "practices": [
            "cover_cropping",
            "composting",
            "minimal_tillage",
            "crop_rotation",
            "green_manure"
        ],
        "source_article": "المزرعة البيئية (5): التربة الصحية"
    },

    "water_management": {
        "name_ar": "إدارة المياه",
        "name_en": "Water Management",
        "description_ar": "الاستخدام المتكامل والفعال للموارد المائية",
        "weight": 0.20,
        "indicators": [
            EcologicalIndicator("water_efficiency", "كفاءة استخدام المياه", "Water Use Efficiency",
                              85, 95, "%", 0.4),
            EcologicalIndicator("rainwater_harvesting", "حصاد مياه الأمطار", "Rainwater Harvesting",
                              20, 100, "%", 0.3),
            EcologicalIndicator("groundwater_recharge", "تغذية المياه الجوفية", "Groundwater Recharge",
                              10, 50, "mm/year", 0.3),
        ],
        "practices": [
            "drip_irrigation",
            "rainwater_harvesting",
            "mulching",
            "contour_farming"
        ],
        "source_article": "المزرعة البيئية (6): متكامل من الأسمدة المائية"
    },

    "biodiversity": {
        "name_ar": "التنوع البيولوجي",
        "name_en": "Biodiversity",
        "description_ar": "الحفاظ على التنوع الحيوي في المزرعة",
        "weight": 0.20,
        "indicators": [
            EcologicalIndicator("plant_species", "أنواع النباتات", "Plant Species",
                              10, 50, "species", 0.25),
            EcologicalIndicator("beneficial_insects", "الحشرات النافعة", "Beneficial Insects",
                              5, 20, "species", 0.25),
            EcologicalIndicator("pollinator_presence", "وجود الملقحات", "Pollinator Presence",
                              1, 5, "score", 0.25),
            EcologicalIndicator("native_species_ratio", "نسبة الأنواع المحلية", "Native Species Ratio",
                              50, 80, "%", 0.25),
        ],
        "practices": [
            "hedgerows",
            "intercropping",
            "habitat_corridors",
            "native_species_planting"
        ],
        "source_article": "المزارع البيئية (4): التدخلات البيئية للآفات والأمراض"
    },

    "input_sustainability": {
        "name_ar": "استدامة المدخلات",
        "name_en": "Input Sustainability",
        "description_ar": "استخدام مدخلات مستدامة وصديقة للبيئة",
        "weight": 0.20,
        "indicators": [
            EcologicalIndicator("organic_input_ratio", "نسبة المدخلات العضوية", "Organic Input Ratio",
                              70, 100, "%", 0.4),
            EcologicalIndicator("synthetic_reduction", "تخفيض الكيماويات", "Synthetic Reduction",
                              50, 100, "%", 0.3),
            EcologicalIndicator("local_input_sourcing", "المصادر المحلية", "Local Input Sourcing",
                              30, 80, "%", 0.3),
        ],
        "practices": [
            "composting",
            "bio_fertilizers",
            "ipm",
            "biological_control"
        ],
        "source_article": "المزرعة البيئية (2): المنتجات الزراعية الإيكولوجية"
    },

    "traceability": {
        "name_ar": "التتبع والشفافية",
        "name_en": "Traceability & Transparency",
        "description_ar": "تتبع كامل لسلسلة الإنتاج مع الشفافية",
        "weight": 0.15,
        "indicators": [
            EcologicalIndicator("record_completeness", "اكتمال السجلات", "Record Completeness",
                              90, 100, "%", 0.4),
            EcologicalIndicator("chain_visibility", "رؤية السلسلة", "Chain Visibility",
                              80, 100, "%", 0.3),
            EcologicalIndicator("third_party_verification", "التحقق الخارجي", "Third Party Verification",
                              0, 1, "boolean", 0.3),
        ],
        "practices": [
            "digital_records",
            "blockchain_tracking",
            "qr_code_labeling",
            "audit_trails"
        ],
        "source_article": "المزرعة البيئية (8): التتبع المرئي والواقعي"
    }
}

ECOLOGICAL_CERTIFICATIONS = {
    "organic_ifoam": {
        "name_ar": "عضوي (IFOAM)",
        "name_en": "Organic (IFOAM)",
        "min_score": 85,
        "required_principles": ["soil_health", "input_sustainability"],
        "transition_years": 3,
        "verification": "third_party"
    },
    "green_label": {
        "name_ar": "العلامة الخضراء",
        "name_en": "Green Label",
        "min_score": 70,
        "required_principles": ["water_management", "biodiversity"],
        "transition_years": 1,
        "verification": "self_declaration"
    },
    "ecological_sahool": {
        "name_ar": "إيكولوجي سهول",
        "name_en": "Ecological SAHOOL",
        "min_score": 75,
        "required_principles": ["soil_health", "water_management", "traceability"],
        "transition_years": 2,
        "verification": "transparent_traceability"
    }
}


def calculate_ecological_score(assessments: Dict[str, float]) -> Dict:
    """
    حساب النتيجة الإيكولوجية الإجمالية

    Args:
        assessments: قاموس بأسماء المبادئ ونتائجها (0-100)

    Returns:
        النتيجة الإجمالية مع تفاصيل كل مبدأ
    """
    total_score = 0
    principle_scores = {}

    for principle_id, principle in ECOLOGICAL_PRINCIPLES.items():
        if principle_id in assessments:
            score = assessments[principle_id]
            weighted_score = score * principle["weight"]
            total_score += weighted_score
            principle_scores[principle_id] = {
                "score": score,
                "weight": principle["weight"],
                "weighted_score": weighted_score
            }

    return {
        "overall_score": round(total_score, 2),
        "principle_scores": principle_scores,
        "eligible_certifications": get_eligible_certifications(total_score, assessments)
    }


def get_eligible_certifications(
    overall_score: float,
    principle_scores: Dict[str, float]
) -> List[str]:
    """تحديد الشهادات المؤهلة"""
    eligible = []

    for cert_id, cert in ECOLOGICAL_CERTIFICATIONS.items():
        if overall_score >= cert["min_score"]:
            required_met = all(
                principle_scores.get(p, 0) >= 60
                for p in cert["required_principles"]
            )
            if required_met:
                eligible.append(cert_id)

    return eligible
```

#### 3.1.2 ملف الحفر الزراعية

**الموقع**: `apps/services/advisory-service/src/kb/pitfalls.py`

```python
"""
Agricultural Pitfalls Knowledge Base - SAHOOL
قاعدة معرفة الحفر الزراعية
Based on: سلسلة مقالات الحفر الزراعية 2025
"""

from typing import Dict, List
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


AGRICULTURAL_PITFALLS = {
    "scale_mismatch": {
        "name_ar": "عدم تناسب الحجم",
        "name_en": "Scale Mismatch",
        "description_ar": "البدء بحجم كبير جداً دون خبرة كافية",
        "description_en": "Starting too large without sufficient experience",
        "risk_level": RiskLevel.HIGH,
        "warning_signs": [
            "first_time_farmer",
            "area_greater_than_5_hectares",
            "no_prior_experience",
            "limited_capital_reserves"
        ],
        "mitigation_strategies": [
            {"id": "start_small", "name_ar": "ابدأ صغيراً", "effectiveness": 0.9},
            {"id": "gradual_expansion", "name_ar": "التوسع التدريجي", "effectiveness": 0.85},
            {"id": "mentorship", "name_ar": "الإرشاد من خبير", "effectiveness": 0.8},
        ],
        "consequences": ["financial_loss", "burnout", "abandonment"],
        "source_article": "حفرة الزراعة (1): الحجم"
    },

    "wrong_species": {
        "name_ar": "اختيار الأصناف الخاطئة",
        "name_en": "Wrong Species Selection",
        "description_ar": "زراعة أصناف غير مناسبة للمنطقة أو المناخ",
        "risk_level": RiskLevel.HIGH,
        "warning_signs": [
            "exotic_varieties",
            "no_local_trials",
            "climate_mismatch",
            "soil_incompatibility"
        ],
        "mitigation_strategies": [
            {"id": "local_varieties", "name_ar": "الأصناف المحلية", "effectiveness": 0.95},
            {"id": "climate_research", "name_ar": "دراسة المناخ", "effectiveness": 0.85},
            {"id": "trial_plots", "name_ar": "قطع تجريبية", "effectiveness": 0.9},
        ],
        "source_article": "حفرة الزراعة (2): الأنواع"
    },

    "land_issues": {
        "name_ar": "مشاكل الأراضي",
        "name_en": "Land Issues",
        "description_ar": "اختيار أرض غير مناسبة أو ذات مشاكل قانونية",
        "risk_level": RiskLevel.CRITICAL,
        "warning_signs": [
            "unclear_ownership",
            "poor_soil_quality",
            "water_scarcity",
            "flooding_risk",
            "contamination_history"
        ],
        "mitigation_strategies": [
            {"id": "soil_testing", "name_ar": "فحص التربة", "effectiveness": 0.9},
            {"id": "legal_verification", "name_ar": "التحقق القانوني", "effectiveness": 0.95},
            {"id": "water_assessment", "name_ar": "تقييم المياه", "effectiveness": 0.85},
        ],
        "source_article": "حفرة الزراعة (3): الأراضي"
    },

    "labor_expertise": {
        "name_ar": "العمال والخبراء",
        "name_en": "Labor & Expertise Issues",
        "description_ar": "الاعتماد على خبراء غير مؤهلين أو عمالة غير مدربة",
        "risk_level": RiskLevel.MEDIUM,
        "warning_signs": [
            "unverified_experts",
            "untrained_workers",
            "high_turnover",
            "no_local_knowledge"
        ],
        "mitigation_strategies": [
            {"id": "verify_credentials", "name_ar": "التحقق من المؤهلات", "effectiveness": 0.8},
            {"id": "training_programs", "name_ar": "برامج تدريبية", "effectiveness": 0.85},
            {"id": "local_hiring", "name_ar": "توظيف محلي", "effectiveness": 0.75},
        ],
        "source_article": "حفرة الزراعة (4): العمال والتقنيين والخبراء"
    },

    "unexpected_effects": {
        "name_ar": "الآثار غير المتوقعة",
        "name_en": "Unexpected Effects",
        "description_ar": "عدم الاستعداد للمفاجآت والتغيرات",
        "risk_level": RiskLevel.MEDIUM,
        "warning_signs": [
            "no_contingency_plan",
            "single_crop_dependency",
            "no_insurance",
            "market_ignorance"
        ],
        "mitigation_strategies": [
            {"id": "diversification", "name_ar": "التنويع", "effectiveness": 0.85},
            {"id": "insurance", "name_ar": "التأمين", "effectiveness": 0.8},
            {"id": "reserve_fund", "name_ar": "صندوق احتياطي", "effectiveness": 0.9},
            {"id": "market_research", "name_ar": "دراسة السوق", "effectiveness": 0.75},
        ],
        "source_article": "الحفرة الزراعية (5): الآثار غير المتوقعة"
    },

    "age_timing": {
        "name_ar": "التوقيت والعمر",
        "name_en": "Age & Timing Issues",
        "description_ar": "البدء في وقت أو عمر غير مناسب",
        "risk_level": RiskLevel.LOW,
        "warning_signs": [
            "retirement_farming",
            "no_succession_plan",
            "seasonal_misalignment"
        ],
        "mitigation_strategies": [
            {"id": "realistic_planning", "name_ar": "تخطيط واقعي", "effectiveness": 0.8},
            {"id": "succession_planning", "name_ar": "خطة التوريث", "effectiveness": 0.85},
        ],
        "source_article": "تجنب الزراعة (2): اختيار العمر المناسب"
    }
}


def assess_pitfall_risk(farm_data: Dict) -> List[Dict]:
    """
    تقييم مخاطر الحفر الزراعية لمزرعة

    Args:
        farm_data: بيانات المزرعة (الحجم، الخبرة، الموقع، إلخ)

    Returns:
        قائمة بالمخاطر المحتملة مع توصيات
    """
    risks = []

    for pitfall_id, pitfall in AGRICULTURAL_PITFALLS.items():
        triggered_signs = []

        for sign in pitfall["warning_signs"]:
            if check_warning_sign(sign, farm_data):
                triggered_signs.append(sign)

        if triggered_signs:
            risk_score = len(triggered_signs) / len(pitfall["warning_signs"])
            risks.append({
                "pitfall_id": pitfall_id,
                "name_ar": pitfall["name_ar"],
                "name_en": pitfall["name_en"],
                "risk_level": pitfall["risk_level"],
                "risk_score": risk_score,
                "triggered_signs": triggered_signs,
                "mitigation_strategies": pitfall["mitigation_strategies"],
                "source_article": pitfall["source_article"]
            })

    # ترتيب حسب خطورة المخاطر
    risks.sort(key=lambda x: (
        {"critical": 4, "high": 3, "medium": 2, "low": 1}[x["risk_level"]],
        x["risk_score"]
    ), reverse=True)

    return risks


def check_warning_sign(sign: str, farm_data: Dict) -> bool:
    """فحص علامة تحذيرية محددة"""
    checks = {
        "first_time_farmer": lambda d: d.get("experience_years", 0) == 0,
        "area_greater_than_5_hectares": lambda d: d.get("area_hectares", 0) > 5,
        "exotic_varieties": lambda d: d.get("uses_exotic_varieties", False),
        "unclear_ownership": lambda d: not d.get("ownership_verified", True),
        "no_contingency_plan": lambda d: not d.get("has_contingency_plan", False),
        # ... المزيد من الفحوصات
    }

    check_func = checks.get(sign)
    if check_func:
        return check_func(farm_data)
    return False
```

---

## 4. نموذج قاعدة البيانات

### 4.1 جداول التقييم الإيكولوجي

**الموقع**: `database/migrations/012_ecological_assessments.sql`

```sql
-- =====================================================
-- Ecological Agriculture Assessment Schema
-- SAHOOL Platform v16.0.0
-- =====================================================

-- 1. أنواع التقييمات الإيكولوجية
CREATE TABLE ecological_assessment_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- soil_health, water, biodiversity, etc.
    description TEXT,
    required_fields JSONB DEFAULT '{}',
    standards TEXT[],  -- FAO, IFOAM, etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. التقييمات الإيكولوجية الرئيسية
CREATE TABLE ecological_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    assessment_type_id UUID REFERENCES ecological_assessment_types(id),

    -- التوقيت
    assessment_date DATE NOT NULL,
    period VARCHAR(20),  -- spring_2025, summer_2025
    scheduled_next_date DATE,

    -- المنطقة (اختياري - لتقييم جزئي)
    assessment_zone GEOMETRY(POLYGON, 4326),

    -- النتائج (0-100)
    soil_health_score INTEGER CHECK (soil_health_score BETWEEN 0 AND 100),
    water_efficiency_score INTEGER CHECK (water_efficiency_score BETWEEN 0 AND 100),
    biodiversity_score INTEGER CHECK (biodiversity_score BETWEEN 0 AND 100),
    input_sustainability_score INTEGER CHECK (input_sustainability_score BETWEEN 0 AND 100),
    traceability_score INTEGER CHECK (traceability_score BETWEEN 0 AND 100),

    -- النتيجة الإجمالية (محسوبة)
    overall_ecological_score INTEGER GENERATED ALWAYS AS (
        COALESCE(soil_health_score, 0) * 0.25 +
        COALESCE(water_efficiency_score, 0) * 0.20 +
        COALESCE(biodiversity_score, 0) * 0.20 +
        COALESCE(input_sustainability_score, 0) * 0.20 +
        COALESCE(traceability_score, 0) * 0.15
    )::INTEGER STORED,

    -- أهلية الشهادات
    organic_eligible BOOLEAN DEFAULT false,
    green_eligible BOOLEAN DEFAULT false,
    ecological_eligible BOOLEAN DEFAULT false,

    -- الحالة
    status VARCHAR(20) DEFAULT 'draft',  -- draft, preliminary, verified, completed

    -- التدقيق
    assessed_by UUID REFERENCES users(id),
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    notes TEXT,

    -- البيانات الوصفية
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. مقاييس التنوع البيولوجي
CREATE TABLE biodiversity_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES ecological_assessments(id) ON DELETE CASCADE,

    metric_type VARCHAR(50) NOT NULL,  -- flora, fauna, soil_organisms, pollinators
    species_count INTEGER,
    native_species_percent DECIMAL(5,2),
    endangered_species_present BOOLEAN DEFAULT false,
    vegetation_cover_percent DECIMAL(5,2),
    habitat_quality_rating INTEGER CHECK (habitat_quality_rating BETWEEN 1 AND 5),

    location GEOMETRY(POINT, 4326),
    photos TEXT[],
    observations TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. تقييمات صحة التربة
CREATE TABLE soil_health_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES ecological_assessments(id) ON DELETE CASCADE,

    -- الخصائص الفيزيائية
    soil_type VARCHAR(50),
    texture VARCHAR(50),
    structure_rating INTEGER CHECK (structure_rating BETWEEN 1 AND 5),
    compaction_level VARCHAR(20),
    water_infiltration_rate DECIMAL(8,2),  -- mm/hour
    aggregate_stability DECIMAL(5,2),  -- %

    -- الخصائص الكيميائية
    ph DECIMAL(4,2),
    ec DECIMAL(8,2),  -- mS/cm
    organic_matter_percent DECIMAL(5,2),
    cec DECIMAL(8,2),  -- cmol/kg

    -- العناصر الغذائية
    nutrient_levels JSONB,  -- {N: x, P: y, K: z, ...}
    heavy_metals_present BOOLEAN DEFAULT false,
    heavy_metals_detail JSONB,

    -- الخصائص البيولوجية
    microbial_activity_score INTEGER,
    earthworm_count_per_sqm INTEGER,
    root_health_rating INTEGER,

    sample_location GEOMETRY(POINT, 4326),
    sample_depth_cm INTEGER,
    lab_report_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. تقييمات دورة المغذيات
CREATE TABLE nutrient_cycling_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES ecological_assessments(id) ON DELETE CASCADE,

    nitrogen_cycle_health INTEGER CHECK (nitrogen_cycle_health BETWEEN 0 AND 100),
    phosphorus_cycle_health INTEGER CHECK (phosphorus_cycle_health BETWEEN 0 AND 100),
    carbon_sequestration_potential DECIMAL(8,2),  -- tons/ha/year
    water_retention_capacity_percent DECIMAL(5,2),
    leaching_risk_score INTEGER CHECK (leaching_risk_score BETWEEN 0 AND 100),
    nutrient_use_efficiency_percent DECIMAL(5,2),

    cover_crop_status JSONB,  -- {species: [], coverage: %}

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. خدمات النظام البيئي
CREATE TABLE ecosystem_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES ecological_assessments(id) ON DELETE CASCADE,

    -- التلقيح
    pollinator_presence BOOLEAN DEFAULT false,
    pollinator_types TEXT[],
    pollination_effectiveness INTEGER,

    -- المكافحة الحيوية
    natural_enemy_presence BOOLEAN DEFAULT false,
    natural_enemy_species TEXT[],
    pest_control_effectiveness INTEGER,

    -- خدمات المياه
    water_filtration_capacity INTEGER,
    flood_mitigation_capacity INTEGER,

    -- الكربون
    carbon_storage_tons_per_ha DECIMAL(8,2),
    carbon_sequestration_rate DECIMAL(8,2),

    -- القيمة الاقتصادية
    ecosystem_services_value_usd DECIMAL(12,2),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. تقييمات الحفر الزراعية
CREATE TABLE pitfall_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id),

    pitfall_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,  -- low, medium, high, critical
    risk_score DECIMAL(3,2),  -- 0.00 - 1.00

    triggered_signs TEXT[],
    recommended_mitigations JSONB,

    identified_at TIMESTAMPTZ DEFAULT NOW(),
    mitigation_applied BOOLEAN DEFAULT false,
    mitigation_date TIMESTAMPTZ,
    mitigation_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. الممارسات الإيكولوجية
CREATE TABLE ecological_practices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    field_crop_id UUID REFERENCES field_crops(id),

    practice_category VARCHAR(50) NOT NULL,
    -- crop_rotation, intercropping, cover_crops, organic_input,
    -- water_conservation, ipm, agroforestry

    practice_name VARCHAR(200) NOT NULL,
    practice_name_ar VARCHAR(200),

    implementation_date DATE,
    expected_duration_days INTEGER,
    actual_end_date DATE,

    area_covered_hectares DECIMAL(10,2),
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),

    cost_usd DECIMAL(12,2),
    benefits_observed TEXT,

    linked_task_ids UUID[],
    photos TEXT[],
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. الشهادات العضوية/الإيكولوجية
CREATE TABLE organic_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,

    standard VARCHAR(50) NOT NULL,  -- IFOAM, EU_ORGANIC, LOCAL, SAHOOL_ECOLOGICAL
    certification_status VARCHAR(20) NOT NULL,
    -- pending, in_transition, certified, suspended, expired

    transition_start_date DATE,
    certified_since DATE,
    valid_until DATE,

    certifying_body VARCHAR(200),
    certificate_number VARCHAR(100),

    inspection_date DATE,
    next_inspection DATE,

    non_compliances JSONB,
    corrective_actions JSONB,

    certificate_url TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. اتجاهات التقييم الإيكولوجي
CREATE TABLE ecological_assessment_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,

    metric_name VARCHAR(100) NOT NULL,
    assessment_date DATE NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50),

    trend_direction VARCHAR(20),  -- improving, stable, declining
    year_over_year_change_percent DECIMAL(6,2),

    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(field_id, metric_name, assessment_date)
);

-- =====================================================
-- الفهارس
-- =====================================================

CREATE INDEX idx_eco_assess_tenant ON ecological_assessments(tenant_id);
CREATE INDEX idx_eco_assess_field ON ecological_assessments(field_id);
CREATE INDEX idx_eco_assess_date ON ecological_assessments(assessment_date);
CREATE INDEX idx_eco_assess_status ON ecological_assessments(status);
CREATE INDEX idx_eco_assess_score ON ecological_assessments(overall_ecological_score);

CREATE INDEX idx_biodiv_assessment ON biodiversity_metrics(assessment_id);
CREATE INDEX idx_soil_assessment ON soil_health_assessments(assessment_id);
CREATE INDEX idx_nutrient_assessment ON nutrient_cycling_assessments(assessment_id);
CREATE INDEX idx_ecosystem_assessment ON ecosystem_services(assessment_id);

CREATE INDEX idx_pitfall_tenant ON pitfall_assessments(tenant_id);
CREATE INDEX idx_pitfall_field ON pitfall_assessments(field_id);
CREATE INDEX idx_pitfall_risk ON pitfall_assessments(risk_level);

CREATE INDEX idx_practices_field ON ecological_practices(field_id);
CREATE INDEX idx_practices_category ON ecological_practices(practice_category);

CREATE INDEX idx_cert_field ON organic_certifications(field_id);
CREATE INDEX idx_cert_status ON organic_certifications(certification_status);
CREATE INDEX idx_cert_valid ON organic_certifications(valid_until);

CREATE INDEX idx_trends_field ON ecological_assessment_trends(field_id);
CREATE INDEX idx_trends_metric ON ecological_assessment_trends(metric_name, assessment_date);

-- =====================================================
-- البيانات الأولية
-- =====================================================

INSERT INTO ecological_assessment_types (code, name_en, name_ar, category, standards) VALUES
('full_ecological', 'Full Ecological Assessment', 'تقييم إيكولوجي شامل', 'comprehensive', ARRAY['FAO', 'IFOAM']),
('soil_health_quick', 'Quick Soil Health Check', 'فحص سريع لصحة التربة', 'soil_health', ARRAY['FAO']),
('biodiversity_survey', 'Biodiversity Survey', 'مسح التنوع البيولوجي', 'biodiversity', ARRAY['CBD']),
('water_efficiency', 'Water Efficiency Assessment', 'تقييم كفاءة المياه', 'water', ARRAY['FAO', 'SPRING']),
('certification_readiness', 'Certification Readiness', 'جاهزية الشهادة', 'certification', ARRAY['IFOAM', 'GlobalGAP']);
```

---

## 5. وكيل الخبير الإيكولوجي

### 5.1 تنفيذ الوكيل

**الموقع**: `apps/services/ai-advisor/src/agents/ecological_expert.py`

```python
"""
Ecological Agriculture Expert Agent
وكيل خبير الزراعة الإيكولوجية

Specializes in:
- Ecological practice assessment
- Pitfall identification and mitigation
- Transition planning to sustainable agriculture
- Certification readiness evaluation
- Biodiversity and soil health optimization

متخصص في:
- تقييم الممارسات الإيكولوجية
- تحديد الحفر الزراعية ومعالجتها
- تخطيط التحول للزراعة المستدامة
- تقييم جاهزية الشهادات
- تحسين التنوع البيولوجي وصحة التربة
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool

from .base_agent import BaseAgent


class EcologicalExpertAgent(BaseAgent):
    """
    Ecological Agriculture Expert Agent
    وكيل خبير الزراعة الإيكولوجية
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """Initialize Ecological Expert Agent"""
        super().__init__(
            name="ecological_expert",
            role="Ecological Agriculture and Sustainability Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """System prompt for Ecological Expert"""
        return """أنت خبير في الزراعة الإيكولوجية والاستدامة البيئية.

خبرتك تشمل:
- تقييم صحة التربة والتنوع البيولوجي
- تصميم أنظمة الزراعة المستدامة
- المكافحة البيولوجية المتكاملة للآفات
- إدارة المياه بكفاءة
- الشهادات العضوية والإيكولوجية (IFOAM, GlobalGAP)
- تحديد المخاطر الزراعية (الحفر) ومعالجتها

عند تقييم مزرعة:
1. قم بتحليل شامل للممارسات الحالية
2. حدد نقاط القوة والضعف الإيكولوجية
3. اقترح تحسينات واقعية وقابلة للتنفيذ
4. قدم خطة تحول مرحلية إذا لزم الأمر
5. احسب الفوائد الاقتصادية للممارسات المستدامة

عند تحديد الحفر الزراعية:
1. تحقق من علامات التحذير بناءً على بيانات المزرعة
2. قيّم مستوى المخاطر (منخفض، متوسط، عالي، حرج)
3. اقترح استراتيجيات التخفيف بالترتيب حسب الفعالية
4. قدم أمثلة واقعية من التجارب الناجحة

قدم إجاباتك بالعربية والإنجليزية. استخدم أرقاماً ونسباً محددة عندما يكون ذلك مناسباً.

You are an expert in Ecological Agriculture and Environmental Sustainability.

Your expertise includes:
- Soil health and biodiversity assessment
- Sustainable farming system design
- Integrated Biological Pest Management
- Water efficiency management
- Organic and ecological certifications (IFOAM, GlobalGAP)
- Agricultural risk (pitfall) identification and mitigation

Always provide practical, actionable recommendations with specific metrics and timelines."""

    async def assess_ecological_score(
        self,
        field_id: str,
        field_data: Dict[str, Any],
        include_satellite: bool = True,
    ) -> Dict[str, Any]:
        """
        Assess ecological score for a field
        تقييم النقاط الإيكولوجية للحقل
        """
        query = f"Assess the ecological status of field {field_id} and provide detailed scoring."

        context = {
            "field_id": field_id,
            "field_data": field_data,
            "include_satellite": include_satellite,
            "task": "ecological_assessment",
            "assessment_categories": [
                "soil_health",
                "water_efficiency",
                "biodiversity",
                "input_sustainability",
                "traceability"
            ]
        }

        return await self.think(query, context=context, use_rag=True)

    async def identify_pitfalls(
        self,
        farm_plan: Dict[str, Any],
        farmer_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Identify agricultural pitfalls in farm plan
        تحديد الحفر الزراعية في خطة المزرعة
        """
        query = "Analyze the farm plan and farmer profile to identify potential agricultural pitfalls."

        context = {
            "farm_plan": farm_plan,
            "farmer_profile": farmer_profile,
            "task": "pitfall_identification",
            "pitfall_categories": [
                "scale_mismatch",
                "wrong_species",
                "land_issues",
                "labor_expertise",
                "unexpected_effects",
                "age_timing"
            ]
        }

        return await self.think(query, context=context, use_rag=True)

    async def recommend_transition_plan(
        self,
        current_practices: Dict[str, Any],
        target_certification: str,
        budget_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create transition plan to ecological/organic farming
        إنشاء خطة تحول للزراعة الإيكولوجية/العضوية
        """
        query = f"Create a transition plan from current practices to {target_certification} certification."

        context = {
            "current_practices": current_practices,
            "target_certification": target_certification,
            "budget_constraints": budget_constraints,
            "task": "transition_planning",
            "phases": ["assessment", "planning", "implementation", "verification"]
        }

        return await self.think(query, context=context, use_rag=True)

    async def evaluate_certification_readiness(
        self,
        field_id: str,
        target_certification: str,
        current_assessment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate readiness for ecological certification
        تقييم جاهزية الشهادة الإيكولوجية
        """
        query = f"Evaluate readiness for {target_certification} certification."

        context = {
            "field_id": field_id,
            "target_certification": target_certification,
            "current_assessment": current_assessment,
            "task": "certification_readiness",
            "certification_requirements": {
                "organic_ifoam": {"min_score": 85, "transition_years": 3},
                "green_label": {"min_score": 70, "transition_years": 1},
                "ecological_sahool": {"min_score": 75, "transition_years": 2}
            }
        }

        return await self.think(query, context=context, use_rag=True)

    async def optimize_biodiversity(
        self,
        field_id: str,
        current_biodiversity: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Optimize biodiversity for a field
        تحسين التنوع البيولوجي للحقل
        """
        query = "Design biodiversity enhancement plan for the field."

        context = {
            "field_id": field_id,
            "current_biodiversity": current_biodiversity,
            "constraints": constraints,
            "task": "biodiversity_optimization",
            "strategies": [
                "hedgerows",
                "pollinator_strips",
                "beneficial_insect_habitat",
                "native_species_restoration"
            ]
        }

        return await self.think(query, context=context, use_rag=True)

    async def design_ipm_strategy(
        self,
        crop_type: str,
        common_pests: List[str],
        ecological_only: bool = True,
    ) -> Dict[str, Any]:
        """
        Design Integrated Pest Management strategy
        تصميم استراتيجية المكافحة المتكاملة للآفات
        """
        query = f"Design an {'ecological-only ' if ecological_only else ''}IPM strategy for {crop_type}."

        context = {
            "crop_type": crop_type,
            "common_pests": common_pests,
            "ecological_only": ecological_only,
            "task": "ipm_design",
            "control_methods": [
                "cultural_practices",
                "biological_control",
                "physical_barriers",
                "botanical_pesticides"
            ]
        }

        return await self.think(query, context=context, use_rag=True)
```

### 5.2 تسجيل الوكيل في main.py

```python
# في apps/services/ai-advisor/src/main.py

from .agents import (
    FieldAnalystAgent,
    DiseaseExpertAgent,
    IrrigationAdvisorAgent,
    YieldPredictorAgent,
    EcologicalExpertAgent,  # جديد
)

# في lifespan():
ecological_expert = EcologicalExpertAgent(
    tools=[agro_tool],  # أدوات للحصول على بيانات المحاصيل
    retriever=knowledge_retriever
)

agents = {
    "field_analyst": field_analyst,
    "disease_expert": disease_expert,
    "irrigation_advisor": irrigation_advisor,
    "yield_predictor": yield_predictor,
    "ecological_expert": ecological_expert,  # جديد
}
```

---

## 6. واجهات المستخدم

### 6.1 واجهة الويب

**الموقع**: `apps/web/src/app/(dashboard)/ecological/`

```
apps/web/src/app/(dashboard)/ecological/
├── page.tsx                    # Server component
├── EcologicalClient.tsx        # Client component
└── components/
    ├── EcologicalScoreCard.tsx
    ├── PitfallWarnings.tsx
    ├── TransitionProgress.tsx
    ├── CertificationStatus.tsx
    └── BiodiversityChart.tsx
```

### 6.2 مثال على EcologicalClient.tsx

```tsx
'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Leaf, AlertTriangle, Award, TrendingUp } from 'lucide-react';

export default function EcologicalClient() {
  const [selectedField, setSelectedField] = useState<string | null>(null);

  const { data: assessment, isLoading } = useQuery({
    queryKey: ['ecological-assessment', selectedField],
    queryFn: () => fetchEcologicalAssessment(selectedField),
    enabled: !!selectedField,
  });

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="bg-gradient-to-l from-green-50 to-emerald-50 rounded-xl border-2 border-green-200 p-6">
        <div className="flex items-center gap-3">
          <Leaf className="w-8 h-8 text-green-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">الزراعة الإيكولوجية</h1>
            <p className="text-gray-600 mt-1">Ecological Agriculture Assessment</p>
          </div>
        </div>
      </div>

      {/* Score Overview */}
      {assessment && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <ScoreCard
            title="صحة التربة"
            score={assessment.soil_health_score}
            icon={<Leaf />}
            color="green"
          />
          <ScoreCard
            title="كفاءة المياه"
            score={assessment.water_efficiency_score}
            icon={<TrendingUp />}
            color="blue"
          />
          <ScoreCard
            title="التنوع البيولوجي"
            score={assessment.biodiversity_score}
            icon={<Leaf />}
            color="emerald"
          />
          <ScoreCard
            title="استدامة المدخلات"
            score={assessment.input_sustainability_score}
            icon={<Award />}
            color="purple"
          />
          <ScoreCard
            title="التتبع"
            score={assessment.traceability_score}
            icon={<TrendingUp />}
            color="indigo"
          />
        </div>
      )}

      {/* Pitfall Warnings */}
      <PitfallWarnings fieldId={selectedField} />

      {/* Certification Status */}
      <CertificationStatus fieldId={selectedField} />
    </div>
  );
}

function ScoreCard({ title, score, icon, color }) {
  const getColorClass = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  return (
    <div className={`p-4 rounded-xl border-2 ${getColorClass(score)}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">{title}</span>
        {icon}
      </div>
      <div className="text-3xl font-bold">{score}</div>
      <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
        <div
          className={`h-2 rounded-full ${score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}
```

---

## 7. تكامل الأحداث

### 7.1 أحداث NATS الجديدة

**الموقع**: `packages/shared/events/`

```json
// EcologicalAssessmentCompleted.v1.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EcologicalAssessmentCompleted",
  "description": "Emitted when an ecological assessment is completed",
  "type": "object",
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "const": "Ecology.AssessmentCompleted" },
    "event_version": { "const": "v1" },
    "tenant_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "payload": {
      "type": "object",
      "properties": {
        "assessment_id": { "type": "string", "format": "uuid" },
        "field_id": { "type": "string", "format": "uuid" },
        "overall_score": { "type": "integer", "minimum": 0, "maximum": 100 },
        "principle_scores": { "type": "object" },
        "eligible_certifications": { "type": "array", "items": { "type": "string" } },
        "recommendations": { "type": "array" }
      },
      "required": ["assessment_id", "field_id", "overall_score"]
    }
  }
}

// PitfallIdentified.v1.json
{
  "title": "PitfallIdentified",
  "description": "Emitted when an agricultural pitfall is identified",
  "payload": {
    "pitfall_type": { "type": "string" },
    "risk_level": { "enum": ["low", "medium", "high", "critical"] },
    "triggered_signs": { "type": "array" },
    "recommended_mitigations": { "type": "array" }
  }
}
```

### 7.2 تكامل GlobalGAP

**الموقع**: `apps/services/shared/globalgap/integrations/ecological_integration.py`

```python
"""
Ecological Agriculture GlobalGAP Integration
تكامل الزراعة الإيكولوجية مع GlobalGAP
"""

from typing import Dict, List, Any
from .events import GlobalGAPEventPublisher


class EcologicalGlobalGAPIntegration:
    """ربط التقييمات الإيكولوجية مع متطلبات GlobalGAP"""

    # ربط المبادئ الإيكولوجية مع نقاط التحكم GlobalGAP
    ECOLOGICAL_TO_GLOBALGAP_MAPPING = {
        "soil_health": {
            "control_points": ["AF.1.1.1", "AF.1.1.2", "CB.4.1"],
            "description": "Site History & Soil Management"
        },
        "water_management": {
            "control_points": ["CB.5.1.1", "CB.5.2.1", "CB.5.3.1"],
            "description": "Water Management (SPRING)"
        },
        "biodiversity": {
            "control_points": ["CB.7.1", "CB.7.2", "CB.7.3"],
            "description": "Environment & Conservation"
        },
        "input_sustainability": {
            "control_points": ["CB.4.2", "CB.8.1", "FV.5.1"],
            "description": "Fertilizers & PPP Management"
        },
        "traceability": {
            "control_points": ["AF.2.1.1", "AF.2.1.2", "FV.4.1"],
            "description": "Traceability & Segregation"
        }
    }

    def __init__(self, event_publisher: GlobalGAPEventPublisher):
        self.publisher = event_publisher

    async def sync_ecological_assessment(
        self,
        assessment_id: str,
        field_id: str,
        ecological_scores: Dict[str, float],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        مزامنة تقييم إيكولوجي مع سجلات GlobalGAP
        """
        compliance_mapping = []

        for principle, score in ecological_scores.items():
            if principle in self.ECOLOGICAL_TO_GLOBALGAP_MAPPING:
                mapping = self.ECOLOGICAL_TO_GLOBALGAP_MAPPING[principle]

                for cp in mapping["control_points"]:
                    compliance_mapping.append({
                        "control_point": cp,
                        "ecological_principle": principle,
                        "score": score,
                        "compliant": score >= 60,
                        "description": mapping["description"]
                    })

        # نشر حدث التكامل
        await self.publisher.publish(
            topic="sahool.globalgap.integration.ecological.synced",
            payload={
                "assessment_id": assessment_id,
                "field_id": field_id,
                "tenant_id": tenant_id,
                "compliance_mapping": compliance_mapping,
                "overall_compliance": all(m["compliant"] for m in compliance_mapping)
            }
        )

        return {
            "status": "synced",
            "compliance_mapping": compliance_mapping
        }
```

---

## 8. التكامل مع GlobalGAP

### 8.1 نقاط التحكم ذات الصلة

| نقطة التحكم | الوصف | المبدأ الإيكولوجي |
|-------------|-------|-------------------|
| AF.1.1.1 | تاريخ الموقع وتقييم المخاطر | صحة التربة |
| CB.4.1 | إدارة التربة | صحة التربة |
| CB.5.x | إدارة المياه (SPRING) | كفاءة المياه |
| CB.7.x | البيئة والحفاظ | التنوع البيولوجي |
| CB.8.1 | المكافحة المتكاملة للآفات | استدامة المدخلات |
| AF.2.1.x | حفظ السجلات | التتبع |

---

## 9. تطبيق الموبايل

### 9.1 هيكل الميزة

```
features/ecological_assessment/
├── data/
│   ├── models/
│   │   └── ecological_models.dart
│   └── repositories/
│       └── ecological_repository.dart
├── presentation/
│   ├── screens/
│   │   ├── assessment_list_screen.dart
│   │   └── assessment_detail_screen.dart
│   ├── widgets/
│   │   ├── score_card.dart
│   │   └── pitfall_warning_card.dart
│   └── providers/
│       └── ecological_providers.dart
```

### 9.2 نموذج البيانات (Dart)

```dart
// ecological_models.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'ecological_models.freezed.dart';
part 'ecological_models.g.dart';

@freezed
class EcologicalAssessment with _$EcologicalAssessment {
  const factory EcologicalAssessment({
    required String id,
    required String fieldId,
    required DateTime assessmentDate,
    required int soilHealthScore,
    required int waterEfficiencyScore,
    required int biodiversityScore,
    required int inputSustainabilityScore,
    required int traceabilityScore,
    required int overallScore,
    required String status,
    List<String>? eligibleCertifications,
  }) = _EcologicalAssessment;

  factory EcologicalAssessment.fromJson(Map<String, dynamic> json) =>
      _$EcologicalAssessmentFromJson(json);
}

@freezed
class PitfallWarning with _$PitfallWarning {
  const factory PitfallWarning({
    required String pitfallId,
    required String nameAr,
    required String nameEn,
    required String riskLevel,
    required double riskScore,
    required List<String> triggeredSigns,
    required List<MitigationStrategy> mitigations,
  }) = _PitfallWarning;

  factory PitfallWarning.fromJson(Map<String, dynamic> json) =>
      _$PitfallWarningFromJson(json);
}
```

---

## 10. خطة التنفيذ

### 10.1 المراحل والملفات

| المرحلة | الملفات | الأولوية | الوصف |
|---------|---------|---------|-------|
| 1 | `kb/ecological.py`, `kb/pitfalls.py` | عالية | قواعد المعرفة |
| 2 | `agents/ecological_expert.py` | عالية | وكيل الذكاء الاصطناعي |
| 3 | `migrations/012_ecological.sql` | عالية | جداول قاعدة البيانات |
| 4 | `main.py` (تحديث) | عالية | واجهات API |
| 5 | `events/*.json` | متوسطة | أحداث NATS |
| 6 | `ecological_integration.py` | متوسطة | تكامل GlobalGAP |
| 7 | `apps/web/ecological/` | متوسطة | واجهة الويب |
| 8 | `features/ecological/` (Flutter) | متوسطة | تطبيق الموبايل |
| 9 | `seed_ecological_knowledge.py` | منخفضة | تحميل المحتوى |
| 10 | `tests/` | عالية | اختبارات الوحدة |

### 10.2 معايير النجاح

- [ ] إضافة 51 مقالة إلى قاعدة المعرفة RAG
- [ ] دقة توصيات الوكيل الإيكولوجي > 85%
- [ ] تغطية 100% من معايير التقييم الإيكولوجي
- [ ] تكامل كامل مع GlobalGAP IFA v6
- [ ] دعم كامل للغة العربية والإنجليزية
- [ ] عمل التطبيق offline-first في الموبايل

---

## المراجع

### المقالات المصدرية
1. سلسلة "فهم الزراعة من منظور الإنتاج" (6 مقالات)
2. سلسلة "الحفر الزراعية" (11 مقالة)
3. سلسلة "المزرعة البيئية" (16 مقالة)
4. سلسلة "فهم الزراعة الإيكولوجية" (8 مقالات)
5. سلسلة "اتجاهات الزراعة 2025" (10 مقالات)

### الوثائق التقنية
- [AI Architecture](./AI_ARCHITECTURE.md)
- [Backend Services Documentation](./BACKEND_SERVICES_DOCUMENTATION.md)
- [GlobalGAP IFA v6 Checklist](../shared/globalgap/IFA_V6_CHECKLIST_README.md)

---

**تاريخ الإنشاء**: 2025-12-29
**الإصدار**: 2.0.0
**المؤلف**: Claude AI (تحليل متعدد الوكلاء)
