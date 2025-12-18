"""
Soil Analysis Module - SAHOOL Agro Advisor
Comprehensive soil analysis and interpretation
Merged from fertilizer-advisor v15.3
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class SoilType(str, Enum):
    """Soil type classification"""
    SANDY = "sandy"
    CLAY = "clay"
    LOAMY = "loamy"
    SILT = "silt"
    ROCKY = "rocky"
    SANDY_LOAM = "sandy_loam"
    CLAY_LOAM = "clay_loam"


@dataclass
class SoilAnalysisResult:
    """Soil analysis data"""
    field_id: str
    analysis_date: datetime
    ph: float
    nitrogen_ppm: float
    phosphorus_ppm: float
    potassium_ppm: float
    organic_matter_pct: float
    ec_ds_m: float  # Electrical Conductivity
    calcium_ppm: float = 0
    magnesium_ppm: float = 0
    sulfur_ppm: float = 0
    iron_ppm: float = 0
    zinc_ppm: float = 0
    manganese_ppm: float = 0
    boron_ppm: float = 0
    soil_type: SoilType = SoilType.LOAMY


@dataclass
class SoilInterpretation:
    """Soil analysis interpretation result"""
    field_id: str
    overall_fertility: str
    overall_fertility_ar: str
    interpretations_ar: list[str]
    interpretations_en: list[str]
    recommendations_ar: list[str]
    recommendations_en: list[str]
    npk_status: dict
    micronutrient_status: dict


# Optimal ranges for soil parameters
OPTIMAL_RANGES = {
    "ph": {"min": 6.0, "max": 7.5, "optimal": 6.5},
    "nitrogen_ppm": {"min": 20, "max": 60, "optimal": 40},
    "phosphorus_ppm": {"min": 10, "max": 50, "optimal": 25},
    "potassium_ppm": {"min": 80, "max": 250, "optimal": 150},
    "organic_matter_pct": {"min": 1.5, "max": 5.0, "optimal": 3.0},
    "ec_ds_m": {"min": 0, "max": 4.0, "optimal": 1.5},
    "calcium_ppm": {"min": 200, "max": 2000, "optimal": 1000},
    "magnesium_ppm": {"min": 25, "max": 200, "optimal": 100},
    "iron_ppm": {"min": 4, "max": 50, "optimal": 20},
    "zinc_ppm": {"min": 1, "max": 10, "optimal": 4},
}


def interpret_soil_analysis(analysis: SoilAnalysisResult) -> SoilInterpretation:
    """
    Interpret soil analysis results and generate recommendations

    Args:
        analysis: SoilAnalysisResult object

    Returns:
        SoilInterpretation with status and recommendations
    """
    interpretations_ar = []
    interpretations_en = []
    recommendations_ar = []
    recommendations_en = []
    npk_status = {}
    micronutrient_status = {}

    # pH Analysis
    if analysis.ph < 5.5:
        interpretations_ar.append("🔴 التربة حامضية جداً")
        interpretations_en.append("🔴 Soil is too acidic")
        recommendations_ar.append("إضافة جير زراعي لرفع pH")
        recommendations_en.append("Add agricultural lime to raise pH")
        npk_status["ph"] = "very_low"
    elif analysis.ph < 6.0:
        interpretations_ar.append("🟡 التربة حامضية قليلاً")
        interpretations_en.append("🟡 Soil is slightly acidic")
        recommendations_ar.append("مراقبة pH وإضافة الجير إذا لزم")
        recommendations_en.append("Monitor pH and add lime if needed")
        npk_status["ph"] = "low"
    elif analysis.ph > 8.5:
        interpretations_ar.append("🔴 التربة قلوية جداً")
        interpretations_en.append("🔴 Soil is too alkaline")
        recommendations_ar.append("إضافة كبريت زراعي أو سماد حامضي")
        recommendations_en.append("Add agricultural sulfur or acidic fertilizer")
        npk_status["ph"] = "very_high"
    elif analysis.ph > 8.0:
        interpretations_ar.append("🟡 التربة قلوية")
        interpretations_en.append("🟡 Soil is alkaline")
        recommendations_ar.append("استخدام أسمدة حامضية التأثير")
        recommendations_en.append("Use acidifying fertilizers")
        npk_status["ph"] = "high"
    else:
        interpretations_ar.append("🟢 pH التربة مناسب")
        interpretations_en.append("🟢 Soil pH is suitable")
        npk_status["ph"] = "optimal"

    # Nitrogen Analysis
    if analysis.nitrogen_ppm < 15:
        interpretations_ar.append("🔴 نقص حاد في النيتروجين")
        interpretations_en.append("🔴 Severe nitrogen deficiency")
        recommendations_ar.append("إضافة يوريا (46-0-0) أو نترات الأمونيوم فوراً")
        recommendations_en.append("Apply urea (46-0-0) or ammonium nitrate immediately")
        npk_status["N"] = "very_low"
    elif analysis.nitrogen_ppm < 25:
        interpretations_ar.append("🟡 نقص النيتروجين")
        interpretations_en.append("🟡 Nitrogen deficiency")
        recommendations_ar.append("تسميد نيتروجيني منتظم")
        recommendations_en.append("Regular nitrogen fertilization")
        npk_status["N"] = "low"
    elif analysis.nitrogen_ppm > 80:
        interpretations_ar.append("🟡 فائض النيتروجين - خطر تلوث")
        interpretations_en.append("🟡 Nitrogen excess - pollution risk")
        recommendations_ar.append("تقليل التسميد النيتروجيني")
        recommendations_en.append("Reduce nitrogen fertilization")
        npk_status["N"] = "high"
    else:
        interpretations_ar.append("🟢 مستوى النيتروجين جيد")
        interpretations_en.append("🟢 Nitrogen level is good")
        npk_status["N"] = "optimal"

    # Phosphorus Analysis
    if analysis.phosphorus_ppm < 8:
        interpretations_ar.append("🔴 نقص حاد في الفوسفور")
        interpretations_en.append("🔴 Severe phosphorus deficiency")
        recommendations_ar.append("إضافة سوبر فوسفات أو DAP (18-46-0)")
        recommendations_en.append("Add superphosphate or DAP (18-46-0)")
        npk_status["P"] = "very_low"
    elif analysis.phosphorus_ppm < 15:
        interpretations_ar.append("🟡 نقص الفوسفور")
        interpretations_en.append("🟡 Phosphorus deficiency")
        recommendations_ar.append("تسميد فوسفوري قبل الزراعة")
        recommendations_en.append("Phosphorus fertilization before planting")
        npk_status["P"] = "low"
    elif analysis.phosphorus_ppm > 60:
        interpretations_ar.append("🟡 فائض الفوسفور")
        interpretations_en.append("🟡 Phosphorus excess")
        recommendations_ar.append("تقليل الأسمدة الفوسفورية")
        recommendations_en.append("Reduce phosphorus fertilizers")
        npk_status["P"] = "high"
    else:
        interpretations_ar.append("🟢 مستوى الفوسفور جيد")
        interpretations_en.append("🟢 Phosphorus level is good")
        npk_status["P"] = "optimal"

    # Potassium Analysis
    if analysis.potassium_ppm < 60:
        interpretations_ar.append("🔴 نقص حاد في البوتاسيوم")
        interpretations_en.append("🔴 Severe potassium deficiency")
        recommendations_ar.append("إضافة سلفات البوتاسيوم (0-0-50) فوراً")
        recommendations_en.append("Add potassium sulfate (0-0-50) immediately")
        npk_status["K"] = "very_low"
    elif analysis.potassium_ppm < 100:
        interpretations_ar.append("🟡 نقص البوتاسيوم")
        interpretations_en.append("🟡 Potassium deficiency")
        recommendations_ar.append("تسميد بوتاسي منتظم")
        recommendations_en.append("Regular potassium fertilization")
        npk_status["K"] = "low"
    elif analysis.potassium_ppm > 300:
        interpretations_ar.append("🟡 فائض البوتاسيوم")
        interpretations_en.append("🟡 Potassium excess")
        npk_status["K"] = "high"
    else:
        interpretations_ar.append("🟢 مستوى البوتاسيوم جيد")
        interpretations_en.append("🟢 Potassium level is good")
        npk_status["K"] = "optimal"

    # Organic Matter Analysis
    if analysis.organic_matter_pct < 1.0:
        interpretations_ar.append("🔴 نقص حاد في المادة العضوية")
        interpretations_en.append("🔴 Severe organic matter deficiency")
        recommendations_ar.append("إضافة سماد عضوي (5-10 طن/هكتار)")
        recommendations_en.append("Add organic fertilizer (5-10 tons/hectare)")
    elif analysis.organic_matter_pct < 2.0:
        interpretations_ar.append("🟡 نقص المادة العضوية")
        interpretations_en.append("🟡 Low organic matter")
        recommendations_ar.append("إضافة كمبوست أو سماد بقري")
        recommendations_en.append("Add compost or cow manure")
    else:
        interpretations_ar.append("🟢 مستوى المادة العضوية جيد")
        interpretations_en.append("🟢 Organic matter level is good")

    # EC (Salinity) Analysis
    if analysis.ec_ds_m > 8:
        interpretations_ar.append("🔴 ملوحة عالية جداً - غير صالحة للزراعة")
        interpretations_en.append("🔴 Very high salinity - unsuitable for cultivation")
        recommendations_ar.append("غسيل التربة بكميات كبيرة من الماء")
        recommendations_en.append("Leach soil with large amounts of water")
    elif analysis.ec_ds_m > 4:
        interpretations_ar.append("🔴 ملوحة مرتفعة")
        interpretations_en.append("🔴 High salinity")
        recommendations_ar.append("غسيل التربة وتحسين الصرف")
        recommendations_en.append("Leach soil and improve drainage")
    elif analysis.ec_ds_m > 2:
        interpretations_ar.append("🟡 ملوحة متوسطة")
        interpretations_en.append("🟡 Moderate salinity")
        recommendations_ar.append("استخدام محاصيل متحملة للملوحة")
        recommendations_en.append("Use salt-tolerant crops")

    # Micronutrients Analysis
    if analysis.iron_ppm < 4:
        micronutrient_status["Fe"] = "low"
        recommendations_ar.append("رش كيلات الحديد على الأوراق")
        recommendations_en.append("Foliar spray with iron chelate")
    else:
        micronutrient_status["Fe"] = "adequate"

    if analysis.zinc_ppm < 1:
        micronutrient_status["Zn"] = "low"
        recommendations_ar.append("رش كبريتات الزنك (0.5%)")
        recommendations_en.append("Spray zinc sulfate (0.5%)")
    else:
        micronutrient_status["Zn"] = "adequate"

    if analysis.calcium_ppm < 200:
        micronutrient_status["Ca"] = "low"
        recommendations_ar.append("إضافة جبس زراعي")
        recommendations_en.append("Add agricultural gypsum")
    else:
        micronutrient_status["Ca"] = "adequate"

    if analysis.magnesium_ppm < 25:
        micronutrient_status["Mg"] = "low"
        recommendations_ar.append("إضافة كبريتات المغنيسيوم")
        recommendations_en.append("Add magnesium sulfate")
    else:
        micronutrient_status["Mg"] = "adequate"

    # Calculate overall fertility
    optimal_count = sum(1 for v in npk_status.values() if v == "optimal")
    low_count = sum(1 for v in npk_status.values() if "low" in v)

    if optimal_count >= 3 and low_count == 0:
        overall = "excellent"
        overall_ar = "ممتازة"
    elif optimal_count >= 2 and low_count <= 1:
        overall = "good"
        overall_ar = "جيدة"
    elif low_count <= 2:
        overall = "fair"
        overall_ar = "متوسطة"
    else:
        overall = "poor"
        overall_ar = "ضعيفة"

    return SoilInterpretation(
        field_id=analysis.field_id,
        overall_fertility=overall,
        overall_fertility_ar=overall_ar,
        interpretations_ar=interpretations_ar,
        interpretations_en=interpretations_en,
        recommendations_ar=recommendations_ar,
        recommendations_en=recommendations_en,
        npk_status=npk_status,
        micronutrient_status=micronutrient_status,
    )


def get_deficiency_symptoms(crop: str) -> dict:
    """
    Get nutrient deficiency symptoms for a crop

    Args:
        crop: Crop name

    Returns:
        Dictionary of deficiency symptoms
    """
    # Universal symptoms (apply to most crops)
    symptoms = {
        "nitrogen": {
            "nutrient": "N",
            "name_ar": "النيتروجين",
            "name_en": "Nitrogen",
            "symptoms_ar": [
                "اصفرار الأوراق القديمة (يبدأ من الأسفل)",
                "توقف أو بطء النمو",
                "ضعف الساق والأفرع",
                "تساقط الأوراق المبكر",
                "لون أخضر فاتح عام",
            ],
            "symptoms_en": [
                "Yellowing of older leaves (starts from bottom)",
                "Stunted or slow growth",
                "Weak stems and branches",
                "Early leaf drop",
                "General pale green color",
            ],
            "treatment_ar": "تسميد باليوريا (46-0-0) أو نترات الأمونيوم (34-0-0)",
            "treatment_en": "Apply urea (46-0-0) or ammonium nitrate (34-0-0)",
            "dose_kg_ha": "50-100",
        },
        "phosphorus": {
            "nutrient": "P",
            "name_ar": "الفوسفور",
            "name_en": "Phosphorus",
            "symptoms_ar": [
                "تلون الأوراق بالأرجواني أو البنفسجي",
                "ضعف نمو الجذور",
                "تأخر الإزهار والإثمار",
                "قلة المحصول",
                "أوراق صغيرة داكنة",
            ],
            "symptoms_en": [
                "Purple or violet coloration of leaves",
                "Poor root development",
                "Delayed flowering and fruiting",
                "Reduced yield",
                "Small dark leaves",
            ],
            "treatment_ar": "تسميد بالسوبر فوسفات أو DAP (18-46-0)",
            "treatment_en": "Apply superphosphate or DAP (18-46-0)",
            "dose_kg_ha": "100-150",
        },
        "potassium": {
            "nutrient": "K",
            "name_ar": "البوتاسيوم",
            "name_en": "Potassium",
            "symptoms_ar": [
                "احتراق وجفاف حواف الأوراق",
                "ضعف مقاومة الأمراض والجفاف",
                "ثمار صغيرة وسيئة الجودة",
                "ضعف الساق (سهولة الرقاد)",
                "بقع بنية على الأوراق",
            ],
            "symptoms_en": [
                "Leaf edge burn and drying",
                "Weak disease and drought resistance",
                "Small fruits with poor quality",
                "Weak stems (easy lodging)",
                "Brown spots on leaves",
            ],
            "treatment_ar": "تسميد بسلفات البوتاسيوم (0-0-50)",
            "treatment_en": "Apply potassium sulfate (0-0-50)",
            "dose_kg_ha": "100-200",
        },
        "iron": {
            "nutrient": "Fe",
            "name_ar": "الحديد",
            "name_en": "Iron",
            "symptoms_ar": [
                "اصفرار بين عروق الأوراق الجديدة",
                "بقاء العروق خضراء",
                "شحوب الأوراق الحديثة",
                "ضعف النمو العام",
            ],
            "symptoms_en": [
                "Interveinal yellowing of new leaves",
                "Veins remain green",
                "Pale new leaves",
                "Poor overall growth",
            ],
            "treatment_ar": "رش كيلات الحديد (Fe-EDDHA) على الأوراق",
            "treatment_en": "Foliar spray with iron chelate (Fe-EDDHA)",
            "dose_kg_ha": "2-5 (foliar)",
        },
        "zinc": {
            "nutrient": "Zn",
            "name_ar": "الزنك",
            "name_en": "Zinc",
            "symptoms_ar": [
                "تقزم الأوراق الجديدة",
                "تشوه الأوراق (التفاف)",
                "بقع بيضاء أو صفراء",
                "قصر السلاميات",
            ],
            "symptoms_en": [
                "Stunted new leaves",
                "Leaf distortion (curling)",
                "White or yellow spots",
                "Short internodes",
            ],
            "treatment_ar": "رش كبريتات الزنك (0.5%)",
            "treatment_en": "Spray zinc sulfate (0.5%)",
            "dose_kg_ha": "2-4 (foliar)",
        },
        "magnesium": {
            "nutrient": "Mg",
            "name_ar": "المغنيسيوم",
            "name_en": "Magnesium",
            "symptoms_ar": [
                "اصفرار بين العروق في الأوراق القديمة",
                "بقاء العروق خضراء",
                "تساقط الأوراق المبكر",
            ],
            "symptoms_en": [
                "Interveinal yellowing of older leaves",
                "Veins remain green",
                "Early leaf drop",
            ],
            "treatment_ar": "إضافة كبريتات المغنيسيوم (إبسوم)",
            "treatment_en": "Add magnesium sulfate (Epsom salt)",
            "dose_kg_ha": "20-50",
        },
        "calcium": {
            "nutrient": "Ca",
            "name_ar": "الكالسيوم",
            "name_en": "Calcium",
            "symptoms_ar": [
                "موت القمم النامية",
                "تشوه الأوراق الجديدة",
                "عفن الطرف الزهري (في الطماطم)",
                "ضعف جدران الخلايا",
            ],
            "symptoms_en": [
                "Death of growing tips",
                "Distorted new leaves",
                "Blossom end rot (in tomatoes)",
                "Weak cell walls",
            ],
            "treatment_ar": "إضافة نترات الكالسيوم أو جير زراعي",
            "treatment_en": "Add calcium nitrate or agricultural lime",
            "dose_kg_ha": "50-100",
        },
    }

    return {
        "crop": crop,
        "deficiency_symptoms": symptoms,
    }


def calculate_fertilizer_adjustment(
    analysis: SoilAnalysisResult,
    crop: str,
    target_yield_kg_ha: float,
) -> dict:
    """
    Calculate fertilizer adjustments based on soil analysis

    Args:
        analysis: Soil analysis result
        crop: Target crop
        target_yield_kg_ha: Target yield

    Returns:
        Adjusted NPK recommendations
    """
    # Base NPK requirements (kg/ha for average yield)
    base_requirements = {
        "tomato": {"N": 180, "P": 80, "K": 220, "base_yield": 40000},
        "wheat": {"N": 120, "P": 60, "K": 40, "base_yield": 4000},
        "coffee": {"N": 100, "P": 40, "K": 120, "base_yield": 2000},
        "banana": {"N": 200, "P": 60, "K": 400, "base_yield": 35000},
        "potato": {"N": 150, "P": 70, "K": 200, "base_yield": 25000},
        "corn": {"N": 180, "P": 80, "K": 120, "base_yield": 8000},
    }

    # Default to tomato if crop not found
    crop_req = base_requirements.get(crop.lower(), base_requirements["tomato"])

    # Yield adjustment factor
    yield_factor = target_yield_kg_ha / crop_req["base_yield"]

    # Base needs adjusted for yield
    n_need = crop_req["N"] * yield_factor
    p_need = crop_req["P"] * yield_factor
    k_need = crop_req["K"] * yield_factor

    # Soil-based adjustments
    # Nitrogen
    if analysis.nitrogen_ppm > 50:
        n_adjustment = 0.6
        n_note = "تربة غنية بالنيتروجين - تقليل 40%"
    elif analysis.nitrogen_ppm > 30:
        n_adjustment = 0.8
        n_note = "تربة متوسطة النيتروجين - تقليل 20%"
    elif analysis.nitrogen_ppm < 15:
        n_adjustment = 1.3
        n_note = "تربة فقيرة بالنيتروجين - زيادة 30%"
    else:
        n_adjustment = 1.0
        n_note = "مستوى النيتروجين مناسب"

    # Phosphorus
    if analysis.phosphorus_ppm > 40:
        p_adjustment = 0.5
        p_note = "تربة غنية بالفوسفور - تقليل 50%"
    elif analysis.phosphorus_ppm > 20:
        p_adjustment = 0.75
        p_note = "تربة متوسطة الفوسفور - تقليل 25%"
    elif analysis.phosphorus_ppm < 10:
        p_adjustment = 1.4
        p_note = "تربة فقيرة بالفوسفور - زيادة 40%"
    else:
        p_adjustment = 1.0
        p_note = "مستوى الفوسفور مناسب"

    # Potassium
    if analysis.potassium_ppm > 200:
        k_adjustment = 0.5
        k_note = "تربة غنية بالبوتاسيوم - تقليل 50%"
    elif analysis.potassium_ppm > 120:
        k_adjustment = 0.75
        k_note = "تربة متوسطة البوتاسيوم - تقليل 25%"
    elif analysis.potassium_ppm < 80:
        k_adjustment = 1.3
        k_note = "تربة فقيرة بالبوتاسيوم - زيادة 30%"
    else:
        k_adjustment = 1.0
        k_note = "مستوى البوتاسيوم مناسب"

    # Organic matter adjustment
    om_factor = 1.0
    if analysis.organic_matter_pct < 1.5:
        om_factor = 1.2  # Increase all by 20%

    return {
        "crop": crop,
        "target_yield_kg_ha": target_yield_kg_ha,
        "adjusted_npk": {
            "N_kg_ha": round(n_need * n_adjustment * om_factor, 1),
            "P_kg_ha": round(p_need * p_adjustment * om_factor, 1),
            "K_kg_ha": round(k_need * k_adjustment * om_factor, 1),
        },
        "adjustments": {
            "nitrogen": {"factor": n_adjustment, "note_ar": n_note},
            "phosphorus": {"factor": p_adjustment, "note_ar": p_note},
            "potassium": {"factor": k_adjustment, "note_ar": k_note},
        },
        "organic_matter_factor": om_factor,
    }
