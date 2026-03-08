"""
Treatment Recommendations API
واجهة برمجة توصيات العلاج

Endpoints for treatment recommendations and IPM calendar.
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}


logger = structlog.get_logger(__name__)

router = APIRouter()


# ============================================================================
# Enums
# ============================================================================


class TreatmentType(StrEnum):
    """Treatment type."""

    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    CULTURAL = "cultural"
    MECHANICAL = "mechanical"
    PHEROMONE = "pheromone"


class SafetyLevel(StrEnum):
    """Safety classification."""

    LOW_RISK = "low_risk"
    MODERATE = "moderate"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"


# ============================================================================
# Models
# ============================================================================


class TreatmentOption(BaseModel):
    """Single treatment option."""

    id: str
    type: TreatmentType
    name_en: str
    name_ar: str
    active_ingredient: str | None = None
    active_ingredient_ar: str | None = None
    application_rate: str
    application_rate_ar: str
    application_method_en: str
    application_method_ar: str
    phi_days: int | None = Field(None, description="Pre-Harvest Interval in days")
    rei_hours: int | None = Field(None, description="Restricted Entry Interval in hours")
    safety_level: SafetyLevel = SafetyLevel.MODERATE
    ppe_required_en: list[str] = []
    ppe_required_ar: list[str] = []
    effectiveness_rating: float = Field(..., ge=0, le=5)
    environmental_impact: str
    environmental_impact_ar: str
    cost_level: str  # low, medium, high
    notes_en: str | None = None
    notes_ar: str | None = None


class TreatmentProtocol(BaseModel):
    """Treatment protocol for a pest."""

    pest_id: str
    pest_name_en: str
    pest_name_ar: str
    crop: str | None = None
    chemical_options: list[TreatmentOption] = []
    biological_options: list[TreatmentOption] = []
    cultural_options: list[TreatmentOption] = []
    ipm_strategy_en: str
    ipm_strategy_ar: str
    rotation_recommendation_en: str
    rotation_recommendation_ar: str


class RecommendationRequest(BaseModel):
    """Request for treatment recommendation."""

    pest_id: str
    crop: str
    severity: str  # low, medium, high, critical
    growth_stage: str | None = None
    organic_only: bool = False
    budget_constraint: str | None = None  # low, medium, high


class IPMCalendarEntry(BaseModel):
    """IPM calendar entry."""

    month: int
    month_name_en: str
    month_name_ar: str
    activities_en: list[str]
    activities_ar: list[str]
    target_pests: list[str]
    monitoring_frequency: str


# ============================================================================
# Treatment Database
# ============================================================================

TREATMENT_DATABASE: dict[str, TreatmentProtocol] = {
    "rpw": TreatmentProtocol(
        pest_id="rpw",
        pest_name_en="Red Palm Weevil",
        pest_name_ar="سوسة النخيل الحمراء",
        crop="date_palm",
        chemical_options=[
            TreatmentOption(
                id="rpw_chem_1",
                type=TreatmentType.CHEMICAL,
                name_en="Emamectin benzoate injection",
                name_ar="حقن إيمامكتين بنزوات",
                active_ingredient="Emamectin benzoate 5%",
                active_ingredient_ar="إيمامكتين بنزوات 5%",
                application_rate="50-100ml per injection point",
                application_rate_ar="50-100 مل لكل نقطة حقن",
                application_method_en="Trunk injection at 4-6 points, 45° angle, 15-20cm depth",
                application_method_ar="حقن الجذع في 4-6 نقاط، زاوية 45°، عمق 15-20 سم",
                phi_days=60,
                rei_hours=24,
                safety_level=SafetyLevel.CAUTION,
                ppe_required_en=["Gloves", "Eye protection", "Long sleeves"],
                ppe_required_ar=["قفازات", "حماية العين", "أكمام طويلة"],
                effectiveness_rating=4.5,
                environmental_impact="Low - targeted application",
                environmental_impact_ar="منخفض - تطبيق موجه",
                cost_level="high",
            ),
            TreatmentOption(
                id="rpw_chem_2",
                type=TreatmentType.CHEMICAL,
                name_en="Imidacloprid soil drench",
                name_ar="غمر التربة بإيميداكلوبريد",
                active_ingredient="Imidacloprid 35%",
                active_ingredient_ar="إيميداكلوبريد 35%",
                application_rate="2ml/liter water, 5-10L per tree",
                application_rate_ar="2 مل/لتر ماء، 5-10 لتر لكل شجرة",
                application_method_en="Soil drench around trunk base",
                application_method_ar="غمر التربة حول قاعدة الجذع",
                phi_days=90,
                rei_hours=48,
                safety_level=SafetyLevel.WARNING,
                ppe_required_en=["Gloves", "Eye protection", "Respirator"],
                ppe_required_ar=["قفازات", "حماية العين", "كمامة"],
                effectiveness_rating=4.0,
                environmental_impact="Moderate - systemic",
                environmental_impact_ar="متوسط - جهازي",
                cost_level="medium",
            ),
        ],
        biological_options=[
            TreatmentOption(
                id="rpw_bio_1",
                type=TreatmentType.BIOLOGICAL,
                name_en="Beauveria bassiana",
                name_ar="بوفيريا باسيانا",
                active_ingredient="Beauveria bassiana spores",
                active_ingredient_ar="أبواغ بوفيريا باسيانا",
                application_rate="10^8 spores/ml, 2L per tree",
                application_rate_ar="10^8 بوغ/مل، 2 لتر لكل شجرة",
                application_method_en="Spray on trunk and leaf bases, evening application",
                application_method_ar="رش على الجذع وقواعد الأوراق، تطبيق مسائي",
                phi_days=0,
                rei_hours=0,
                safety_level=SafetyLevel.LOW_RISK,
                ppe_required_en=["Dust mask"],
                ppe_required_ar=["قناع غبار"],
                effectiveness_rating=3.5,
                environmental_impact="Negligible - natural fungus",
                environmental_impact_ar="ضئيل - فطر طبيعي",
                cost_level="medium",
            ),
        ],
        cultural_options=[
            TreatmentOption(
                id="rpw_cult_1",
                type=TreatmentType.CULTURAL,
                name_en="Sanitation and pruning",
                name_ar="النظافة والتقليم",
                application_rate="As needed",
                application_rate_ar="حسب الحاجة",
                application_method_en="Remove and destroy infested trees, burn debris",
                application_method_ar="إزالة وتدمير الأشجار المصابة، حرق المخلفات",
                safety_level=SafetyLevel.LOW_RISK,
                ppe_required_en=["Work gloves"],
                ppe_required_ar=["قفازات عمل"],
                effectiveness_rating=4.0,
                environmental_impact="Positive - removes pest reservoir",
                environmental_impact_ar="إيجابي - يزيل مصدر الآفة",
                cost_level="low",
            ),
        ],
        ipm_strategy_en=(
            "1) Pheromone trapping for monitoring, "
            "2) Preventive injection for healthy trees, "
            "3) Curative treatment for infested, "
            "4) Remove severely infested trees"
        ),
        ipm_strategy_ar=(
            "1) مصائد الفرمون للمراقبة، 2) حقن وقائي للأشجار السليمة، 3) علاج للمصابة، 4) إزالة الأشجار المصابة بشدة"
        ),
        rotation_recommendation_en=("Rotate between emamectin and imidacloprid to prevent resistance"),
        rotation_recommendation_ar="تناوب بين إيمامكتين وإيميداكلوبريد لمنع المقاومة",
    ),
    "aphids": TreatmentProtocol(
        pest_id="aphids",
        pest_name_en="Aphids",
        pest_name_ar="المن",
        chemical_options=[
            TreatmentOption(
                id="aphid_chem_1",
                type=TreatmentType.CHEMICAL,
                name_en="Acetamiprid",
                name_ar="أسيتاميبريد",
                active_ingredient="Acetamiprid 20%",
                active_ingredient_ar="أسيتاميبريد 20%",
                application_rate="25g/100L water",
                application_rate_ar="25غ/100 لتر ماء",
                application_method_en="Foliar spray, ensure coverage of leaf undersides",
                application_method_ar="رش ورقي، ضمان تغطية أسفل الأوراق",
                phi_days=7,
                rei_hours=12,
                safety_level=SafetyLevel.CAUTION,
                ppe_required_en=["Gloves", "Eye protection"],
                ppe_required_ar=["قفازات", "حماية العين"],
                effectiveness_rating=4.5,
                environmental_impact="Moderate",
                environmental_impact_ar="متوسط",
                cost_level="low",
            ),
        ],
        biological_options=[
            TreatmentOption(
                id="aphid_bio_1",
                type=TreatmentType.BIOLOGICAL,
                name_en="Ladybird beetles release",
                name_ar="إطلاق خنافس أبو العيد",
                application_rate="1000 adults/hectare",
                application_rate_ar="1000 بالغ/هكتار",
                application_method_en="Release at dusk near infested plants",
                application_method_ar="إطلاق عند الغسق بالقرب من النباتات المصابة",
                safety_level=SafetyLevel.LOW_RISK,
                ppe_required_en=[],
                ppe_required_ar=[],
                effectiveness_rating=3.5,
                environmental_impact="Positive - natural predator",
                environmental_impact_ar="إيجابي - مفترس طبيعي",
                cost_level="medium",
            ),
            TreatmentOption(
                id="aphid_bio_2",
                type=TreatmentType.BIOLOGICAL,
                name_en="Neem oil spray",
                name_ar="رش زيت النيم",
                active_ingredient="Azadirachtin",
                active_ingredient_ar="أزاديراكتين",
                application_rate="5ml/L water",
                application_rate_ar="5 مل/لتر ماء",
                application_method_en="Spray in early morning or evening",
                application_method_ar="رش في الصباح الباكر أو المساء",
                phi_days=1,
                rei_hours=4,
                safety_level=SafetyLevel.LOW_RISK,
                ppe_required_en=["Gloves"],
                ppe_required_ar=["قفازات"],
                effectiveness_rating=3.0,
                environmental_impact="Low",
                environmental_impact_ar="منخفض",
                cost_level="low",
            ),
        ],
        cultural_options=[
            TreatmentOption(
                id="aphid_cult_1",
                type=TreatmentType.CULTURAL,
                name_en="Water spray",
                name_ar="رش الماء",
                application_rate="Strong jet",
                application_rate_ar="نفاث قوي",
                application_method_en="Dislodge aphids with strong water spray",
                application_method_ar="إزاحة المن برش ماء قوي",
                safety_level=SafetyLevel.LOW_RISK,
                ppe_required_en=[],
                ppe_required_ar=[],
                effectiveness_rating=2.5,
                environmental_impact="None",
                environmental_impact_ar="لا يوجد",
                cost_level="low",
            ),
        ],
        ipm_strategy_en=(
            "1) Monitor with yellow sticky traps, "
            "2) Encourage natural enemies, "
            "3) Use neem oil for early infestations, "
            "4) Chemical control as last resort"
        ),
        ipm_strategy_ar=(
            "1) مراقبة بمصائد صفراء لاصقة، "
            "2) تشجيع الأعداء الطبيعية، "
            "3) استخدام زيت النيم للإصابات المبكرة، "
            "4) المكافحة الكيميائية كملاذ أخير"
        ),
        rotation_recommendation_en="Rotate between neonicotinoids and pyrethroids",
        rotation_recommendation_ar="تناوب بين النيونيكوتينويدات والبيرثرويدات",
    ),
}


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/treatments/recommend")
async def get_recommendations(request: RecommendationRequest, _user=Depends(get_current_user)):
    """
    Get treatment recommendations for a pest.
    الحصول على توصيات العلاج لآفة.
    """
    protocol = TREATMENT_DATABASE.get(request.pest_id)

    if not protocol:
        raise HTTPException(
            status_code=404,
            detail=f"No treatment protocol for pest: {request.pest_id}",
        )

    # Filter options based on request
    recommendations = {
        "pest_id": request.pest_id,
        "pest_name_en": protocol.pest_name_en,
        "pest_name_ar": protocol.pest_name_ar,
        "crop": request.crop,
        "severity": request.severity,
        "ipm_strategy_en": protocol.ipm_strategy_en,
        "ipm_strategy_ar": protocol.ipm_strategy_ar,
        "recommended_options": [],
    }

    # Prioritize based on severity
    if request.organic_only:
        options = protocol.biological_options + protocol.cultural_options
    elif request.severity == "critical":
        options = protocol.chemical_options + protocol.biological_options
    elif request.severity == "high":
        options = protocol.chemical_options + protocol.biological_options + protocol.cultural_options
    else:
        options = protocol.biological_options + protocol.cultural_options + protocol.chemical_options

    # Filter by budget if specified
    if request.budget_constraint:
        budget_order = {"low": 1, "medium": 2, "high": 3}
        max_budget = budget_order.get(request.budget_constraint, 3)
        options = [o for o in options if budget_order.get(o.cost_level, 2) <= max_budget]

    recommendations["recommended_options"] = options[:5]  # Top 5

    logger.info(
        "treatment_recommended",
        pest_id=request.pest_id,
        severity=request.severity,
        options_count=len(recommendations["recommended_options"]),
    )

    return recommendations


@router.get("/treatments/protocols/{pest_id}", response_model=TreatmentProtocol)
async def get_protocol(pest_id: str):
    """
    Get full treatment protocol for pest.
    الحصول على بروتوكول العلاج الكامل للآفة.
    """
    protocol = TREATMENT_DATABASE.get(pest_id)

    if not protocol:
        raise HTTPException(
            status_code=404,
            detail=f"No protocol found for pest: {pest_id}",
        )

    return protocol


@router.get("/treatments/ipm-calendar")
async def get_ipm_calendar(
    crop: str = Query(..., description="Crop type"),
    region: str = Query("middle_east", description="Region"),
):
    """
    Get IPM calendar for crop.
    الحصول على تقويم المكافحة المتكاملة للمحصول.
    """
    # Simplified IPM calendar - would be crop-specific in production
    months_en = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    months_ar = [
        "يناير",
        "فبراير",
        "مارس",
        "أبريل",
        "مايو",
        "يونيو",
        "يوليو",
        "أغسطس",
        "سبتمبر",
        "أكتوبر",
        "نوفمبر",
        "ديسمبر",
    ]

    calendar = []

    for i in range(12):
        month = i + 1

        if crop.lower() == "date_palm":
            if month in [3, 4, 5]:  # Spring
                activities_en = [
                    "RPW pheromone trap check weekly",
                    "Preventive trunk injection",
                    "Dubas monitoring",
                ]
                activities_ar = [
                    "فحص مصائد سوسة النخيل أسبوعياً",
                    "حقن الجذع الوقائي",
                    "مراقبة الدوباس",
                ]
                target_pests = ["rpw", "dubas"]
            elif month in [6, 7, 8]:  # Summer
                activities_en = [
                    "Increase trap monitoring",
                    "Spray for dubas if needed",
                    "Date moth monitoring in storage",
                ]
                activities_ar = [
                    "زيادة مراقبة المصائد",
                    "رش للدوباس إذا لزم",
                    "مراقبة فراشة التمر في المخازن",
                ]
                target_pests = ["rpw", "dubas", "date_moth"]
            elif month in [9, 10, 11]:  # Fall
                activities_en = [
                    "Post-harvest sanitation",
                    "Remove infested fruits",
                    "Fall dubas generation control",
                ]
                activities_ar = [
                    "تنظيف ما بعد الحصاد",
                    "إزالة الثمار المصابة",
                    "مكافحة جيل الدوباس الخريفي",
                ]
                target_pests = ["dubas", "date_moth"]
            else:  # Winter
                activities_en = [
                    "Pruning and sanitation",
                    "Trap maintenance",
                    "Plan next season treatments",
                ]
                activities_ar = [
                    "التقليم والتنظيف",
                    "صيانة المصائد",
                    "تخطيط علاجات الموسم القادم",
                ]
                target_pests = ["rpw"]
        else:
            # Generic calendar
            if month in [3, 4, 5]:
                activities_en = [
                    "Monitor for aphids and thrips",
                    "Yellow sticky trap installation",
                    "Biological control release",
                ]
                activities_ar = [
                    "مراقبة المن والتربس",
                    "تركيب مصائد صفراء لاصقة",
                    "إطلاق المكافحة الحيوية",
                ]
                target_pests = ["aphids", "thrips"]
            elif month in [6, 7, 8]:
                activities_en = [
                    "Spider mite monitoring",
                    "Whitefly control",
                    "Increase irrigation to reduce mite stress",
                ]
                activities_ar = [
                    "مراقبة العنكبوت الأحمر",
                    "مكافحة الذبابة البيضاء",
                    "زيادة الري لتقليل إجهاد العث",
                ]
                target_pests = ["spider_mite", "whitefly"]
            elif month in [9, 10, 11]:
                activities_en = [
                    "End-of-season cleanup",
                    "Remove crop residues",
                    "Soil treatment if needed",
                ]
                activities_ar = [
                    "تنظيف نهاية الموسم",
                    "إزالة بقايا المحصول",
                    "معالجة التربة إذا لزم",
                ]
                target_pests = ["whitefly", "thrips"]
            else:
                activities_en = [
                    "Plan crop rotation",
                    "Order biological control agents",
                    "Equipment maintenance",
                ]
                activities_ar = [
                    "تخطيط الدورة الزراعية",
                    "طلب عوامل المكافحة الحيوية",
                    "صيانة المعدات",
                ]
                target_pests = []

        calendar.append(
            IPMCalendarEntry(
                month=month,
                month_name_en=months_en[i],
                month_name_ar=months_ar[i],
                activities_en=activities_en,
                activities_ar=activities_ar,
                target_pests=target_pests,
                monitoring_frequency="weekly" if month in [3, 4, 5, 6, 7, 8] else "bi-weekly",
            )
        )

    return {
        "crop": crop,
        "region": region,
        "calendar": calendar,
    }


@router.get("/treatments/rotation")
async def get_rotation_plan(
    pest_id: str = Query(..., description="Pest ID"),
    seasons: int = Query(4, ge=1, le=8, description="Number of seasons to plan"),
):
    """
    Get pesticide rotation plan.
    الحصول على خطة تناوب المبيدات.
    """
    protocol = TREATMENT_DATABASE.get(pest_id)

    if not protocol:
        raise HTTPException(
            status_code=404,
            detail=f"No protocol found for pest: {pest_id}",
        )

    # Get all chemical options
    chemicals = protocol.chemical_options

    if not chemicals:
        return {
            "pest_id": pest_id,
            "message": "No chemical options - use biological/cultural methods",
            "message_ar": "لا خيارات كيميائية - استخدم الطرق الحيوية/الزراعية",
        }

    # Create rotation plan
    rotation = []
    for i in range(seasons):
        chemical = chemicals[i % len(chemicals)]
        rotation.append(
            {
                "season": i + 1,
                "treatment": chemical.name_en,
                "treatment_ar": chemical.name_ar,
                "active_ingredient": chemical.active_ingredient,
                "reason_en": "Rotation to prevent resistance buildup",
                "reason_ar": "تناوب لمنع تراكم المقاومة",
            }
        )

    return {
        "pest_id": pest_id,
        "pest_name_en": protocol.pest_name_en,
        "pest_name_ar": protocol.pest_name_ar,
        "rotation_plan": rotation,
        "recommendation_en": protocol.rotation_recommendation_en,
        "recommendation_ar": protocol.rotation_recommendation_ar,
    }
