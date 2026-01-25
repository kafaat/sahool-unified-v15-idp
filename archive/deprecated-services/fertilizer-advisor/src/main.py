"""
🧪 SAHOOL Fertilizer Advisor Service v15.3
خدمة مستشار السماد - NPK Recommendations & Soil Analysis

Field-First Architecture:
- كل توصية تُنتج ActionTemplate قابل للتنفيذ بدون اتصال
- التحليل يخدم الميدان، لا العكس
"""

# Field-First: Action Template Support
import os
import sys
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from fastapi import FastAPI

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel, Field

sys.path.insert(0, "/app")
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Context Engineering Integration
try:
    from context_integration import (
        compress_soil_analysis,
        compress_crop_data,
        FertilizerRecommendationMemory,
        evaluate_fertilizer_recommendation,
    )
    CONTEXT_ENGINEERING_AVAILABLE = True
except ImportError:
    CONTEXT_ENGINEERING_AVAILABLE = False

try:
    from shared.contracts.actions import (
        ActionTemplate,
        ActionTemplateFactory,
    )
    from shared.contracts.actions import (
        UrgencyLevel as ActionUrgency,
    )

    ACTION_TEMPLATE_AVAILABLE = True
except ImportError:
    ACTION_TEMPLATE_AVAILABLE = False

def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="SAHOOL Fertilizer Advisor | مستشار السماد",
        version="15.3.0",
        description="Comprehensive NPK recommendations, soil analysis, and fertilization scheduling",
    )

    # Setup unified error handling
    setup_exception_handlers(app)
    add_request_id_middleware(app)

    # Context Engineering: Initialize recommendation memory
    if CONTEXT_ENGINEERING_AVAILABLE:
        try:
            app.state.recommendation_memory = FertilizerRecommendationMemory()
            app.state.context_engineering_enabled = True
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"Failed to initialize recommendation memory: {e}"
            )
            app.state.context_engineering_enabled = False
    else:
        app.state.context_engineering_enabled = False

    return app


app = create_app()


# =============================================================================
# Enums & Models
# =============================================================================


class CropType(str, Enum):
    TOMATO = "tomato"
    WHEAT = "wheat"
    COFFEE = "coffee"
    QAT = "qat"
    BANANA = "banana"
    CUCUMBER = "cucumber"
    PEPPER = "pepper"
    POTATO = "potato"
    CORN = "corn"
    GRAPES = "grapes"
    DATE_PALM = "date_palm"
    MANGO = "mango"


class GrowthStage(str, Enum):
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"


class SoilType(str, Enum):
    SANDY = "sandy"
    CLAY = "clay"
    LOAMY = "loamy"
    SILT = "silt"
    ROCKY = "rocky"


class FertilizerType(str, Enum):
    UREA = "urea"  # 46-0-0
    DAP = "dap"  # 18-46-0
    NPK_15_15_15 = "npk_15_15_15"
    NPK_20_20_20 = "npk_20_20_20"
    POTASSIUM_SULFATE = "potassium_sulfate"  # 0-0-50
    AMMONIUM_NITRATE = "ammonium_nitrate"  # 34-0-0
    SUPERPHOSPHATE = "superphosphate"  # 0-20-0
    ORGANIC_COMPOST = "organic_compost"
    CHICKEN_MANURE = "chicken_manure"
    COW_MANURE = "cow_manure"


class ApplicationMethod(str, Enum):
    BROADCAST = "broadcast"
    SIDE_DRESSING = "side_dressing"
    FERTIGATION = "fertigation"
    FOLIAR = "foliar"
    BAND = "band"


class SoilAnalysis(BaseModel):
    field_id: str
    analysis_date: datetime
    ph: float = Field(..., ge=0, le=14)
    nitrogen_ppm: float = Field(..., ge=0)
    phosphorus_ppm: float = Field(..., ge=0)
    potassium_ppm: float = Field(..., ge=0)
    organic_matter_percent: float = Field(..., ge=0, le=100)
    ec_ds_m: float = Field(..., ge=0, description="Electrical Conductivity")
    calcium_ppm: float = Field(default=0, ge=0)
    magnesium_ppm: float = Field(default=0, ge=0)
    sulfur_ppm: float = Field(default=0, ge=0)
    iron_ppm: float = Field(default=0, ge=0)
    zinc_ppm: float = Field(default=0, ge=0)
    soil_type: SoilType


class FertilizerRecommendation(BaseModel):
    fertilizer_type: FertilizerType
    fertilizer_name_ar: str
    fertilizer_name_en: str
    quantity_kg_per_hectare: float
    quantity_kg_per_donum: float  # 1 donum = 0.1 hectare (Yemen measure)
    application_method: ApplicationMethod
    application_method_ar: str
    timing_ar: str
    timing_en: str
    npk_content: dict[str, float]
    cost_estimate_yer: float
    notes_ar: list[str]
    notes_en: list[str]


class FertilizationPlan(BaseModel):
    plan_id: str
    field_id: str
    crop: CropType
    crop_name_ar: str
    growth_stage: GrowthStage
    growth_stage_ar: str
    area_hectares: float
    soil_analysis: SoilAnalysis | None
    target_yield_kg_ha: float
    recommendations: list[FertilizerRecommendation]
    total_nitrogen_kg: float
    total_phosphorus_kg: float
    total_potassium_kg: float
    total_cost_yer: float
    schedule: list[dict[str, Any]]
    warnings_ar: list[str]
    warnings_en: list[str]
    created_at: datetime


class FertilizerRequest(BaseModel):
    field_id: str
    crop: CropType
    growth_stage: GrowthStage
    area_hectares: float = Field(..., gt=0)
    soil_type: SoilType = SoilType.LOAMY
    target_yield_kg_ha: float | None = None
    budget_yer: float | None = None
    organic_only: bool = False
    soil_analysis: SoilAnalysis | None = None


# =============================================================================
# Crop & Fertilizer Data
# =============================================================================

CROP_TRANSLATIONS = {
    CropType.TOMATO: "طماطم",
    CropType.WHEAT: "قمح",
    CropType.COFFEE: "بن",
    CropType.QAT: "قات",
    CropType.BANANA: "موز",
    CropType.CUCUMBER: "خيار",
    CropType.PEPPER: "فلفل",
    CropType.POTATO: "بطاطس",
    CropType.CORN: "ذرة",
    CropType.GRAPES: "عنب",
    CropType.DATE_PALM: "نخيل",
    CropType.MANGO: "مانجو",
}

STAGE_TRANSLATIONS = {
    GrowthStage.SEEDLING: "شتلة",
    GrowthStage.VEGETATIVE: "نمو خضري",
    GrowthStage.FLOWERING: "إزهار",
    GrowthStage.FRUITING: "إثمار",
    GrowthStage.MATURITY: "نضج",
}

FERTILIZER_TRANSLATIONS = {
    FertilizerType.UREA: ("يوريا", "Urea"),
    FertilizerType.DAP: ("داب", "DAP"),
    FertilizerType.NPK_15_15_15: ("سماد مركب 15-15-15", "NPK 15-15-15"),
    FertilizerType.NPK_20_20_20: ("سماد مركب 20-20-20", "NPK 20-20-20"),
    FertilizerType.POTASSIUM_SULFATE: ("سلفات البوتاسيوم", "Potassium Sulfate"),
    FertilizerType.AMMONIUM_NITRATE: ("نترات الأمونيوم", "Ammonium Nitrate"),
    FertilizerType.SUPERPHOSPHATE: ("سوبر فوسفات", "Superphosphate"),
    FertilizerType.ORGANIC_COMPOST: ("سماد عضوي", "Organic Compost"),
    FertilizerType.CHICKEN_MANURE: ("سماد دجاج", "Chicken Manure"),
    FertilizerType.COW_MANURE: ("سماد بقري", "Cow Manure"),
}

APPLICATION_TRANSLATIONS = {
    ApplicationMethod.BROADCAST: "نثر",
    ApplicationMethod.SIDE_DRESSING: "تسميد جانبي",
    ApplicationMethod.FERTIGATION: "تسميد بالري",
    ApplicationMethod.FOLIAR: "رش ورقي",
    ApplicationMethod.BAND: "تسميد شريطي",
}

# NPK content of fertilizers (N-P-K percentages)
FERTILIZER_NPK = {
    FertilizerType.UREA: {"N": 46, "P": 0, "K": 0},
    FertilizerType.DAP: {"N": 18, "P": 46, "K": 0},
    FertilizerType.NPK_15_15_15: {"N": 15, "P": 15, "K": 15},
    FertilizerType.NPK_20_20_20: {"N": 20, "P": 20, "K": 20},
    FertilizerType.POTASSIUM_SULFATE: {"N": 0, "P": 0, "K": 50},
    FertilizerType.AMMONIUM_NITRATE: {"N": 34, "P": 0, "K": 0},
    FertilizerType.SUPERPHOSPHATE: {"N": 0, "P": 20, "K": 0},
    FertilizerType.ORGANIC_COMPOST: {"N": 2, "P": 1, "K": 1},
    FertilizerType.CHICKEN_MANURE: {"N": 3, "P": 2.5, "K": 1.5},
    FertilizerType.COW_MANURE: {"N": 1.5, "P": 1, "K": 1},
}

# Fertilizer prices (YER per kg) - approximate
FERTILIZER_PRICES = {
    FertilizerType.UREA: 800,
    FertilizerType.DAP: 1200,
    FertilizerType.NPK_15_15_15: 1000,
    FertilizerType.NPK_20_20_20: 1100,
    FertilizerType.POTASSIUM_SULFATE: 1500,
    FertilizerType.AMMONIUM_NITRATE: 900,
    FertilizerType.SUPERPHOSPHATE: 600,
    FertilizerType.ORGANIC_COMPOST: 300,
    FertilizerType.CHICKEN_MANURE: 200,
    FertilizerType.COW_MANURE: 150,
}

# Crop NPK requirements (kg/ha for target yield)
CROP_NPK_REQUIREMENTS = {
    CropType.TOMATO: {
        "target_yield": 40000,  # kg/ha
        "N": 180,
        "P": 80,
        "K": 220,
        "stages": {
            GrowthStage.SEEDLING: {"N": 0.1, "P": 0.2, "K": 0.1},
            GrowthStage.VEGETATIVE: {"N": 0.3, "P": 0.2, "K": 0.2},
            GrowthStage.FLOWERING: {"N": 0.25, "P": 0.3, "K": 0.25},
            GrowthStage.FRUITING: {"N": 0.25, "P": 0.2, "K": 0.35},
            GrowthStage.MATURITY: {"N": 0.1, "P": 0.1, "K": 0.1},
        },
    },
    CropType.WHEAT: {
        "target_yield": 4000,
        "N": 120,
        "P": 60,
        "K": 40,
        "stages": {
            GrowthStage.SEEDLING: {"N": 0.15, "P": 0.4, "K": 0.2},
            GrowthStage.VEGETATIVE: {"N": 0.4, "P": 0.3, "K": 0.3},
            GrowthStage.FLOWERING: {"N": 0.3, "P": 0.2, "K": 0.3},
            GrowthStage.FRUITING: {"N": 0.1, "P": 0.05, "K": 0.15},
            GrowthStage.MATURITY: {"N": 0.05, "P": 0.05, "K": 0.05},
        },
    },
    CropType.COFFEE: {
        "target_yield": 2000,
        "N": 100,
        "P": 40,
        "K": 120,
        "stages": {
            GrowthStage.SEEDLING: {"N": 0.1, "P": 0.3, "K": 0.1},
            GrowthStage.VEGETATIVE: {"N": 0.35, "P": 0.2, "K": 0.2},
            GrowthStage.FLOWERING: {"N": 0.25, "P": 0.25, "K": 0.25},
            GrowthStage.FRUITING: {"N": 0.2, "P": 0.15, "K": 0.35},
            GrowthStage.MATURITY: {"N": 0.1, "P": 0.1, "K": 0.1},
        },
    },
    CropType.BANANA: {
        "target_yield": 35000,
        "N": 200,
        "P": 60,
        "K": 400,
        "stages": {
            GrowthStage.SEEDLING: {"N": 0.1, "P": 0.25, "K": 0.05},
            GrowthStage.VEGETATIVE: {"N": 0.35, "P": 0.25, "K": 0.2},
            GrowthStage.FLOWERING: {"N": 0.25, "P": 0.25, "K": 0.3},
            GrowthStage.FRUITING: {"N": 0.2, "P": 0.15, "K": 0.35},
            GrowthStage.MATURITY: {"N": 0.1, "P": 0.1, "K": 0.1},
        },
    },
    CropType.QAT: {
        "target_yield": 8000,
        "N": 150,
        "P": 50,
        "K": 100,
        "stages": {
            GrowthStage.SEEDLING: {"N": 0.1, "P": 0.3, "K": 0.1},
            GrowthStage.VEGETATIVE: {"N": 0.5, "P": 0.2, "K": 0.3},
            GrowthStage.FLOWERING: {"N": 0.2, "P": 0.25, "K": 0.3},
            GrowthStage.FRUITING: {"N": 0.15, "P": 0.15, "K": 0.2},
            GrowthStage.MATURITY: {"N": 0.05, "P": 0.1, "K": 0.1},
        },
    },
}

# Add defaults for other crops
for crop in CropType:
    if crop not in CROP_NPK_REQUIREMENTS:
        CROP_NPK_REQUIREMENTS[crop] = CROP_NPK_REQUIREMENTS[CropType.TOMATO].copy()


# =============================================================================
# Calculation Functions
# =============================================================================


def calculate_npk_needs(
    crop: CropType,
    stage: GrowthStage,
    area_ha: float,
    target_yield: float | None,
    soil_analysis: SoilAnalysis | None,
) -> dict[str, float]:
    """Calculate NPK requirements based on crop, stage, and soil"""

    crop_data = CROP_NPK_REQUIREMENTS[crop]
    stage_factors = crop_data["stages"][stage]

    # Base requirements (kg/ha)
    base_n = crop_data["N"]
    base_p = crop_data["P"]
    base_k = crop_data["K"]

    # Adjust for target yield
    if target_yield:
        yield_factor = target_yield / crop_data["target_yield"]
        base_n *= yield_factor
        base_p *= yield_factor
        base_k *= yield_factor

    # Stage-specific needs
    n_need = base_n * stage_factors["N"] * area_ha
    p_need = base_p * stage_factors["P"] * area_ha
    k_need = base_k * stage_factors["K"] * area_ha

    # Adjust based on soil analysis
    if soil_analysis:
        # Reduce N if soil has high nitrogen
        if soil_analysis.nitrogen_ppm > 40:
            n_need *= 0.7
        elif soil_analysis.nitrogen_ppm > 25:
            n_need *= 0.85

        # Adjust P based on soil P
        if soil_analysis.phosphorus_ppm > 30:
            p_need *= 0.6
        elif soil_analysis.phosphorus_ppm > 15:
            p_need *= 0.8

        # Adjust K based on soil K
        if soil_analysis.potassium_ppm > 200:
            k_need *= 0.5
        elif soil_analysis.potassium_ppm > 100:
            k_need *= 0.75

        # Increase if organic matter is low
        if soil_analysis.organic_matter_percent < 1.5:
            n_need *= 1.2

    return {"N": round(n_need, 2), "P": round(p_need, 2), "K": round(k_need, 2)}


def select_fertilizers(
    npk_needs: dict[str, float], organic_only: bool, budget: float | None
) -> list[FertilizerRecommendation]:
    """Select optimal fertilizer mix to meet NPK needs"""

    recommendations = []
    remaining_n = npk_needs["N"]
    remaining_p = npk_needs["P"]
    remaining_k = npk_needs["K"]

    if organic_only:
        # Use organic fertilizers
        fertilizers_to_use = [
            FertilizerType.ORGANIC_COMPOST,
            FertilizerType.CHICKEN_MANURE,
            FertilizerType.COW_MANURE,
        ]
    else:
        fertilizers_to_use = [
            FertilizerType.NPK_20_20_20,
            FertilizerType.UREA,
            FertilizerType.DAP,
            FertilizerType.POTASSIUM_SULFATE,
        ]

    # Calculate quantities for balanced approach
    for fert_type in fertilizers_to_use:
        if remaining_n <= 0 and remaining_p <= 0 and remaining_k <= 0:
            break

        npk = FERTILIZER_NPK[fert_type]
        names = FERTILIZER_TRANSLATIONS[fert_type]
        price = FERTILIZER_PRICES[fert_type]

        # Determine quantity based on limiting nutrient
        qty_for_n = (remaining_n / (npk["N"] / 100)) if npk["N"] > 0 else float("inf")
        qty_for_p = (remaining_p / (npk["P"] / 100)) if npk["P"] > 0 else float("inf")
        qty_for_k = (remaining_k / (npk["K"] / 100)) if npk["K"] > 0 else float("inf")

        quantity = min(qty_for_n, qty_for_p, qty_for_k, 500)  # Cap at 500 kg
        if quantity <= 0 or quantity == float("inf"):
            continue

        quantity = round(quantity, 1)

        # Update remaining needs
        remaining_n -= quantity * npk["N"] / 100
        remaining_p -= quantity * npk["P"] / 100
        remaining_k -= quantity * npk["K"] / 100

        # Determine application method
        if fert_type in [
            FertilizerType.ORGANIC_COMPOST,
            FertilizerType.CHICKEN_MANURE,
            FertilizerType.COW_MANURE,
        ]:
            method = ApplicationMethod.BROADCAST
        elif fert_type == FertilizerType.UREA:
            method = ApplicationMethod.SIDE_DRESSING
        else:
            method = ApplicationMethod.FERTIGATION

        recommendations.append(
            FertilizerRecommendation(
                fertilizer_type=fert_type,
                fertilizer_name_ar=names[0],
                fertilizer_name_en=names[1],
                quantity_kg_per_hectare=quantity,
                quantity_kg_per_donum=round(quantity * 0.1, 2),
                application_method=method,
                application_method_ar=APPLICATION_TRANSLATIONS[method],
                timing_ar="في الصباح الباكر أو المساء",
                timing_en="Early morning or evening",
                npk_content=npk,
                cost_estimate_yer=round(quantity * price, 0),
                notes_ar=get_fertilizer_notes_ar(fert_type),
                notes_en=get_fertilizer_notes_en(fert_type),
            )
        )

    return recommendations


def get_fertilizer_notes_ar(fert_type: FertilizerType) -> list[str]:
    """Get Arabic notes for fertilizer application"""
    notes = {
        FertilizerType.UREA: [
            "لا تضع اليوريا على أوراق مبللة",
            "تجنب الاستخدام في درجات حرارة عالية جداً",
            "الري مباشرة بعد التسميد",
        ],
        FertilizerType.DAP: [
            "مناسب للتسميد الأساسي",
            "يذوب ببطء في التربة",
            "تجنب الخلط مع الأسمدة القلوية",
        ],
        FertilizerType.NPK_20_20_20: [
            "سماد متوازن لجميع المراحل",
            "يمكن استخدامه للرش الورقي بتركيز 0.5%",
            "مناسب للري بالتنقيط",
        ],
        FertilizerType.ORGANIC_COMPOST: [
            "يحسن بنية التربة",
            "إضافة قبل الزراعة بأسبوعين",
            "زيادة الكمية للتربة الرملية",
        ],
        FertilizerType.POTASSIUM_SULFATE: [
            "مهم لجودة الثمار",
            "زيادة الكمية في مرحلة الإثمار",
            "تجنب الإفراط لتجنب الملوحة",
        ],
    }
    return notes.get(fert_type, ["اتبع تعليمات الشركة المصنعة"])


def get_fertilizer_notes_en(fert_type: FertilizerType) -> list[str]:
    """Get English notes for fertilizer application"""
    notes = {
        FertilizerType.UREA: [
            "Don't apply urea on wet leaves",
            "Avoid use in very high temperatures",
            "Irrigate immediately after application",
        ],
        FertilizerType.DAP: [
            "Suitable for basal application",
            "Dissolves slowly in soil",
            "Avoid mixing with alkaline fertilizers",
        ],
        FertilizerType.NPK_20_20_20: [
            "Balanced fertilizer for all stages",
            "Can be used for foliar spray at 0.5%",
            "Suitable for drip irrigation",
        ],
        FertilizerType.ORGANIC_COMPOST: [
            "Improves soil structure",
            "Apply 2 weeks before planting",
            "Increase quantity for sandy soil",
        ],
        FertilizerType.POTASSIUM_SULFATE: [
            "Important for fruit quality",
            "Increase during fruiting stage",
            "Avoid excess to prevent salinity",
        ],
    }
    return notes.get(fert_type, ["Follow manufacturer instructions"])


def generate_schedule(
    crop: CropType, stage: GrowthStage, recommendations: list[FertilizerRecommendation]
) -> list[dict[str, Any]]:
    """Generate application schedule"""
    schedule = []
    now = datetime.utcnow()

    # Split applications based on stage
    if stage == GrowthStage.SEEDLING:
        intervals = [0, 14]  # Apply now and after 2 weeks
    elif stage == GrowthStage.VEGETATIVE:
        intervals = [0, 10, 20]  # Every 10 days
    elif stage == GrowthStage.FLOWERING:
        intervals = [0, 7, 14, 21]  # Weekly
    elif stage == GrowthStage.FRUITING:
        intervals = [0, 7, 14]
    else:
        intervals = [0]

    for i, day_offset in enumerate(intervals):
        application_date = now + timedelta(days=day_offset)
        split_factor = 1.0 / len(intervals)

        schedule.append(
            {
                "application_number": i + 1,
                "date": application_date.date().isoformat(),
                "fertilizers": [
                    {
                        "name_ar": rec.fertilizer_name_ar,
                        "quantity_kg": round(rec.quantity_kg_per_hectare * split_factor, 1),
                        "method_ar": rec.application_method_ar,
                    }
                    for rec in recommendations
                ],
                "notes_ar": f"التطبيق رقم {i + 1} من {len(intervals)}",
            }
        )

    return schedule


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "service": "fertilizer-advisor",
        "version": "15.3.0",
        "crops_supported": len(CROP_NPK_REQUIREMENTS),
    }


@app.get("/readyz")
def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    return {
        "status": "ready",
        "service": "fertilizer-advisor",
        "version": "16.0.0",
        "checks": {
            "service": "ready",
        },
    }


@app.get("/v1/crops")
def list_crops():
    """قائمة المحاصيل المدعومة"""
    return {
        "crops": [
            {
                "id": crop.value,
                "name_ar": CROP_TRANSLATIONS[crop],
                "target_yield_kg_ha": CROP_NPK_REQUIREMENTS[crop]["target_yield"],
                "npk_requirements": {
                    "N": CROP_NPK_REQUIREMENTS[crop]["N"],
                    "P": CROP_NPK_REQUIREMENTS[crop]["P"],
                    "K": CROP_NPK_REQUIREMENTS[crop]["K"],
                },
            }
            for crop in CropType
        ]
    }


@app.get("/v1/fertilizers")
def list_fertilizers():
    """قائمة الأسمدة المتاحة"""
    return {
        "fertilizers": [
            {
                "id": fert.value,
                "name_ar": FERTILIZER_TRANSLATIONS[fert][0],
                "name_en": FERTILIZER_TRANSLATIONS[fert][1],
                "npk_content": FERTILIZER_NPK[fert],
                "price_yer_per_kg": FERTILIZER_PRICES[fert],
                "is_organic": fert
                in [
                    FertilizerType.ORGANIC_COMPOST,
                    FertilizerType.CHICKEN_MANURE,
                    FertilizerType.COW_MANURE,
                ],
            }
            for fert in FertilizerType
        ]
    }


@app.post("/v1/recommend", response_model=FertilizationPlan)
def get_recommendation(request: FertilizerRequest):
    """الحصول على توصيات التسميد - مع دعم هندسة السياق"""

    # Context Engineering: Compress soil and crop data before LLM processing
    compression_metadata = None
    if CONTEXT_ENGINEERING_AVAILABLE and request.soil_analysis:
        try:
            compression_metadata = compress_soil_analysis(request.soil_analysis)
            compress_crop_data(request.crop, request.area_hectares, request.target_yield_kg_ha)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Context compression failed: {e}")

    # Calculate NPK needs
    npk_needs = calculate_npk_needs(
        request.crop,
        request.growth_stage,
        request.area_hectares,
        request.target_yield_kg_ha,
        request.soil_analysis,
    )

    # Select fertilizers
    recommendations = select_fertilizers(npk_needs, request.organic_only, request.budget_yer)

    # Generate schedule
    schedule = generate_schedule(request.crop, request.growth_stage, recommendations)

    # Calculate totals
    total_n = sum(
        rec.quantity_kg_per_hectare * rec.npk_content["N"] / 100 for rec in recommendations
    )
    total_p = sum(
        rec.quantity_kg_per_hectare * rec.npk_content["P"] / 100 for rec in recommendations
    )
    total_k = sum(
        rec.quantity_kg_per_hectare * rec.npk_content["K"] / 100 for rec in recommendations
    )
    total_cost = sum(rec.cost_estimate_yer for rec in recommendations)

    # Generate warnings
    warnings_ar = []
    warnings_en = []

    if total_n > 200 * request.area_hectares:
        warnings_ar.append("⚠️ كمية النيتروجين مرتفعة - خطر حرق النباتات")
        warnings_en.append("⚠️ High nitrogen amount - risk of plant burn")

    if request.soil_analysis and request.soil_analysis.ec_ds_m > 4:
        warnings_ar.append("⚠️ ملوحة التربة مرتفعة - تقليل الأسمدة الكيميائية")
        warnings_en.append("⚠️ High soil salinity - reduce chemical fertilizers")

    if request.soil_analysis and request.soil_analysis.ph > 8:
        warnings_ar.append("⚠️ التربة قلوية - استخدم أسمدة حامضية")
        warnings_en.append("⚠️ Alkaline soil - use acidifying fertilizers")

    plan = FertilizationPlan(
        plan_id=str(uuid.uuid4()),
        field_id=request.field_id,
        crop=request.crop,
        crop_name_ar=CROP_TRANSLATIONS[request.crop],
        growth_stage=request.growth_stage,
        growth_stage_ar=STAGE_TRANSLATIONS[request.growth_stage],
        area_hectares=request.area_hectares,
        soil_analysis=request.soil_analysis,
        target_yield_kg_ha=request.target_yield_kg_ha
        or CROP_NPK_REQUIREMENTS[request.crop]["target_yield"],
        recommendations=recommendations,
        total_nitrogen_kg=round(total_n, 2),
        total_phosphorus_kg=round(total_p, 2),
        total_potassium_kg=round(total_k, 2),
        total_cost_yer=round(total_cost, 0),
        schedule=schedule,
        warnings_ar=warnings_ar,
        warnings_en=warnings_en,
        created_at=datetime.utcnow(),
    )

    # Context Engineering: Store plan in memory and evaluate quality
    if CONTEXT_ENGINEERING_AVAILABLE and app.state.context_engineering_enabled:
        try:
            app.state.recommendation_memory.store_plan(plan, compression_metadata)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to store recommendation in memory: {e}")

    return plan


@app.post("/v1/soil-analysis/interpret")
def interpret_soil_analysis(analysis: SoilAnalysis):
    """تفسير نتائج تحليل التربة"""

    interpretations_ar = []
    interpretations_en = []
    recommendations_ar = []
    recommendations_en = []

    # pH interpretation
    if analysis.ph < 5.5:
        interpretations_ar.append("🔴 التربة حامضية جداً")
        interpretations_en.append("🔴 Soil is too acidic")
        recommendations_ar.append("إضافة جير زراعي لرفع pH")
        recommendations_en.append("Add agricultural lime to raise pH")
    elif analysis.ph > 8.0:
        interpretations_ar.append("🔴 التربة قلوية جداً")
        interpretations_en.append("🔴 Soil is too alkaline")
        recommendations_ar.append("إضافة كبريت أو سماد حامضي")
        recommendations_en.append("Add sulfur or acidic fertilizer")
    else:
        interpretations_ar.append("🟢 pH التربة مناسب")
        interpretations_en.append("🟢 Soil pH is suitable")

    # Nitrogen
    if analysis.nitrogen_ppm < 20:
        interpretations_ar.append("🔴 نقص النيتروجين")
        interpretations_en.append("🔴 Nitrogen deficiency")
        recommendations_ar.append("إضافة يوريا أو نترات الأمونيوم")
        recommendations_en.append("Add urea or ammonium nitrate")
    elif analysis.nitrogen_ppm > 60:
        interpretations_ar.append("🟡 فائض النيتروجين")
        interpretations_en.append("🟡 Nitrogen excess")
        recommendations_ar.append("تقليل التسميد النيتروجيني")
        recommendations_en.append("Reduce nitrogen fertilization")
    else:
        interpretations_ar.append("🟢 مستوى النيتروجين جيد")
        interpretations_en.append("🟢 Nitrogen level is good")

    # Phosphorus
    if analysis.phosphorus_ppm < 10:
        interpretations_ar.append("🔴 نقص الفوسفور")
        interpretations_en.append("🔴 Phosphorus deficiency")
        recommendations_ar.append("إضافة سوبر فوسفات أو DAP")
        recommendations_en.append("Add superphosphate or DAP")
    elif analysis.phosphorus_ppm > 50:
        interpretations_ar.append("🟡 فائض الفوسفور")
        interpretations_en.append("🟡 Phosphorus excess")
    else:
        interpretations_ar.append("🟢 مستوى الفوسفور جيد")
        interpretations_en.append("🟢 Phosphorus level is good")

    # Potassium
    if analysis.potassium_ppm < 80:
        interpretations_ar.append("🔴 نقص البوتاسيوم")
        interpretations_en.append("🔴 Potassium deficiency")
        recommendations_ar.append("إضافة سلفات البوتاسيوم")
        recommendations_en.append("Add potassium sulfate")
    elif analysis.potassium_ppm > 250:
        interpretations_ar.append("🟡 فائض البوتاسيوم")
        interpretations_en.append("🟡 Potassium excess")
    else:
        interpretations_ar.append("🟢 مستوى البوتاسيوم جيد")
        interpretations_en.append("🟢 Potassium level is good")

    # Organic matter
    if analysis.organic_matter_percent < 1.5:
        interpretations_ar.append("🔴 نقص المادة العضوية")
        interpretations_en.append("🔴 Low organic matter")
        recommendations_ar.append("إضافة سماد عضوي أو كمبوست")
        recommendations_en.append("Add organic fertilizer or compost")

    # EC (Salinity)
    if analysis.ec_ds_m > 4:
        interpretations_ar.append("🔴 ملوحة مرتفعة")
        interpretations_en.append("🔴 High salinity")
        recommendations_ar.append("غسيل التربة وتحسين الصرف")
        recommendations_en.append("Leach soil and improve drainage")

    return {
        "field_id": analysis.field_id,
        "analysis_date": analysis.analysis_date.isoformat(),
        "interpretations_ar": interpretations_ar,
        "interpretations_en": interpretations_en,
        "recommendations_ar": recommendations_ar,
        "recommendations_en": recommendations_en,
        "overall_fertility": (
            "جيدة"
            if len([i for i in interpretations_ar if "🟢" in i]) > 3
            else ("متوسطة" if len([i for i in interpretations_ar if "🔴" in i]) < 2 else "ضعيفة")
        ),
    }


@app.get("/v1/deficiency-symptoms/{crop}")
def get_deficiency_symptoms(crop: CropType):
    """أعراض نقص العناصر الغذائية"""

    symptoms = {
        "nitrogen": {
            "name_ar": "النيتروجين (N)",
            "symptoms_ar": [
                "اصفرار الأوراق القديمة",
                "توقف النمو",
                "ضعف الساق",
                "تساقط الأوراق المبكر",
            ],
            "symptoms_en": [
                "Yellowing of older leaves",
                "Stunted growth",
                "Weak stems",
                "Early leaf drop",
            ],
            "treatment_ar": "تسميد باليوريا أو نترات الأمونيوم",
            "treatment_en": "Apply urea or ammonium nitrate",
        },
        "phosphorus": {
            "name_ar": "الفوسفور (P)",
            "symptoms_ar": [
                "تلون الأوراق بالأرجواني",
                "ضعف الجذور",
                "تأخر الإزهار",
                "قلة الإنتاج",
            ],
            "symptoms_en": [
                "Purple coloration of leaves",
                "Weak roots",
                "Delayed flowering",
                "Low yield",
            ],
            "treatment_ar": "تسميد بالسوبر فوسفات أو DAP",
            "treatment_en": "Apply superphosphate or DAP",
        },
        "potassium": {
            "name_ar": "البوتاسيوم (K)",
            "symptoms_ar": [
                "احتراق حواف الأوراق",
                "ضعف مقاومة الأمراض",
                "ثمار صغيرة",
                "سوء جودة المحصول",
            ],
            "symptoms_en": [
                "Leaf edge burn",
                "Weak disease resistance",
                "Small fruits",
                "Poor crop quality",
            ],
            "treatment_ar": "تسميد بسلفات البوتاسيوم",
            "treatment_en": "Apply potassium sulfate",
        },
        "iron": {
            "name_ar": "الحديد (Fe)",
            "symptoms_ar": [
                "اصفرار بين عروق الأوراق الجديدة",
                "شحوب الأوراق",
                "ضعف النمو",
            ],
            "symptoms_en": [
                "Interveinal yellowing of new leaves",
                "Pale leaves",
                "Weak growth",
            ],
            "treatment_ar": "رش كيلات الحديد على الأوراق",
            "treatment_en": "Foliar spray with iron chelate",
        },
        "zinc": {
            "name_ar": "الزنك (Zn)",
            "symptoms_ar": ["تقزم الأوراق الجديدة", "تشوه الأوراق", "بقع بيضاء"],
            "symptoms_en": ["Stunted new leaves", "Leaf distortion", "White spots"],
            "treatment_ar": "رش كبريتات الزنك",
            "treatment_en": "Spray zinc sulfate",
        },
    }

    return {
        "crop": crop.value,
        "crop_name_ar": CROP_TRANSLATIONS[crop],
        "deficiency_symptoms": symptoms,
    }


# =============================================================================
# Field-First: Action Template Endpoints
# =============================================================================


@app.post("/v1/recommend-with-action")
def get_recommendation_with_action(request: FertilizerRequest):
    """
    الحصول على توصيات التسميد مع ActionTemplate

    Field-First: هذا الـ endpoint يُنتج قالب إجراء قابل للتنفيذ
    بدون اتصال، مع خطوات واضحة وموارد محددة.
    """
    # Get the regular fertilization plan
    plan = get_recommendation(request)

    # If ActionTemplate not available, return plan only
    if not ACTION_TEMPLATE_AVAILABLE:
        return {
            "plan": plan,
            "action_template": None,
            "action_template_available": False,
        }

    # Create ActionTemplate for the first recommendation
    if plan.recommendations:
        rec = plan.recommendations[0]

        # Determine urgency based on growth stage
        urgency_map = {
            GrowthStage.SEEDLING: ActionUrgency.MEDIUM,
            GrowthStage.VEGETATIVE: ActionUrgency.MEDIUM,
            GrowthStage.FLOWERING: ActionUrgency.HIGH,
            GrowthStage.FRUITING: ActionUrgency.HIGH,
            GrowthStage.MATURITY: ActionUrgency.LOW,
        }
        urgency = urgency_map.get(request.growth_stage, ActionUrgency.MEDIUM)

        # Create ActionTemplate using factory
        action = ActionTemplateFactory.create_fertilization_action(
            field_id=request.field_id,
            fertilizer_type=rec.fertilizer_type.value,
            quantity_kg=rec.quantity_kg_per_hectare * request.area_hectares,
            urgency=urgency,
            confidence=0.88,
            application_method=rec.application_method.value,
            npk_ratio=f"{rec.npk_content['N']}-{rec.npk_content['P']}-{rec.npk_content['K']}",
            source_analysis_id=plan.plan_id,
        )

        # Calculate priority
        action.calculate_priority_score()

        # Add all fertilizers as metadata
        action.metadata["all_fertilizers"] = [
            {
                "type": r.fertilizer_type.value,
                "name_ar": r.fertilizer_name_ar,
                "quantity_kg": r.quantity_kg_per_hectare * request.area_hectares,
                "method": r.application_method.value,
            }
            for r in plan.recommendations
        ]

        return {
            "plan": plan,
            "action_template": action.model_dump(),
            "action_template_available": True,
            "task_card": action.to_task_card(),
            "notification_payload": action.to_notification_payload(),
        }

    return {
        "plan": plan,
        "action_template": None,
        "action_template_available": True,
        "message": "No fertilization needed at this time",
    }


@app.post("/v1/soil-analysis/interpret-with-action")
def interpret_soil_analysis_with_action(analysis: SoilAnalysis):
    """
    تفسير نتائج تحليل التربة مع ActionTemplate

    Field-First: إذا كان هناك نقص، يُنتج إجراء تسميد
    """
    # Get the regular interpretation
    result = interpret_soil_analysis(analysis)

    # If ActionTemplate not available or no deficiency, return as-is
    if not ACTION_TEMPLATE_AVAILABLE:
        return {
            **result,
            "action_template": None,
        }

    # Check if there's a deficiency that needs action
    deficiencies = [i for i in result["interpretations_ar"] if "🔴" in i]

    if not deficiencies:
        return {
            **result,
            "action_template": None,
            "message": "No action needed - soil is healthy",
        }

    # Create action for the most critical deficiency
    if "النيتروجين" in str(deficiencies):
        fert_type = "urea"
        quantity = 50  # kg/ha base
    elif "الفوسفور" in str(deficiencies):
        fert_type = "dap"
        quantity = 40
    elif "البوتاسيوم" in str(deficiencies):
        fert_type = "potassium_sulfate"
        quantity = 35
    else:
        fert_type = "npk_15_15_15"
        quantity = 45

    action = ActionTemplateFactory.create_fertilization_action(
        field_id=analysis.field_id,
        fertilizer_type=fert_type,
        quantity_kg=quantity,
        urgency=ActionUrgency.HIGH if len(deficiencies) > 2 else ActionUrgency.MEDIUM,
        confidence=0.90,  # High confidence from soil analysis
        application_method="broadcast",
        source_analysis_id=f"soil_{analysis.field_id}_{analysis.analysis_date.isoformat()}",
    )

    action.calculate_priority_score()

    return {
        **result,
        "action_template": action.model_dump(),
        "task_card": action.to_task_card(),
    }


# =============================================================================
# Context Engineering Endpoints
# =============================================================================


@app.post("/v1/recommend/evaluate")
def evaluate_recommendation(plan: FertilizationPlan):
    """
    Evaluate quality of a fertilization recommendation.
    تقييم جودة توصية التسميد

    Uses LLM-as-Judge pattern to evaluate across multiple criteria:
    - Accuracy: Is the NPK calculation correct?
    - Actionability: Can the farmer implement it?
    - Safety: Are warnings adequate?
    - Relevance: Does it match the context?
    - Completeness: All nutrients covered?
    - Clarity: Understandable in Arabic/English?

    Returns:
        dict: Evaluation result with approval status and feedback
    """
    if not CONTEXT_ENGINEERING_AVAILABLE:
        return {
            "error": "Context engineering not available",
            "message": "AI evaluation disabled in this environment",
            "status": "disabled",
        }

    try:
        evaluation = evaluate_fertilizer_recommendation(plan)
        return {
            **evaluation,
            "status": "success",
            "context_engineering_enabled": True,
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Recommendation evaluation failed: {e}")
        return {
            "error": "Recommendation evaluation failed",
            "status": "failed",
            "context_engineering_enabled": True,
        }


@app.get("/v1/recommendations/recent")
def get_recent_recommendations(field_id: str | None = None, limit: int = 5):
    """
    Retrieve recent fertilization recommendations from memory.
    استرجاع التوصيات الأخيرة من الذاكرة

    Args:
        field_id: Optional field ID to filter by
        limit: Maximum number of recommendations (default: 5, max: 20)

    Returns:
        dict: List of recent recommendations with metadata
    """
    if not CONTEXT_ENGINEERING_AVAILABLE or not app.state.context_engineering_enabled:
        return {
            "error": "Context engineering not available",
            "recommendations": [],
        }

    try:
        # Limit maximum to 20
        limit = min(limit, 20)

        recommendations = app.state.recommendation_memory.retrieve_recent_plans(
            field_id=field_id,
            limit=limit,
        )

        return {
            "status": "success",
            "field_id": field_id,
            "count": len(recommendations),
            "recommendations": recommendations,
            "context_engineering_enabled": True,
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to retrieve recommendations: {e}")
        return {
            "error": "Failed to retrieve recommendations",
            "status": "failed",
            "recommendations": [],
            "context_engineering_enabled": True,
        }


@app.post("/v1/soil-analysis/compress")
def compress_soil_endpoint(analysis: SoilAnalysis):
    """
    Compress soil analysis data for LLM context.
    ضغط بيانات تحليل التربة لسياق نموذج اللغة

    Useful for understanding token optimization in AI interactions.

    Returns:
        dict: Compression metrics and compressed data
    """
    if not CONTEXT_ENGINEERING_AVAILABLE:
        return {
            "error": "Context engineering not available",
            "status": "disabled",
        }

    try:
        result = compress_soil_analysis(analysis)
        return {
            "status": "success",
            "field_id": analysis.field_id,
            **result,
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Soil compression failed: {e}")
        return {
            "error": "Soil compression failed",
            "status": "failed",
            "context_engineering_enabled": True,
        }


@app.get("/v1/context-engineering/status")
def get_context_engineering_status():
    """
    Check if context engineering is enabled and available.
    التحقق من توفر هندسة السياق

    Returns:
        dict: Status information about context engineering
    """
    return {
        "context_engineering_available": CONTEXT_ENGINEERING_AVAILABLE,
        "context_engineering_enabled": (
            app.state.context_engineering_enabled if CONTEXT_ENGINEERING_AVAILABLE else False
        ),
        "features": {
            "compression": CONTEXT_ENGINEERING_AVAILABLE,
            "memory_storage": CONTEXT_ENGINEERING_AVAILABLE,
            "recommendation_evaluation": CONTEXT_ENGINEERING_AVAILABLE,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8093)
