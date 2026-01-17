"""
SAHOOL Nutrient Deficiency Detection Module
وحدة كشف نقص العناصر الغذائية

Comprehensive nutrient deficiency detection from vegetation indices.
Based on agricultural research and spectral analysis for Yemen crops.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class NutrientType(str, Enum):
    """أنواع العناصر الغذائية"""

    # Macronutrients - العناصر الكبرى
    NITROGEN = "nitrogen"  # نيتروجين (N)
    PHOSPHORUS = "phosphorus"  # فوسفور (P)
    POTASSIUM = "potassium"  # بوتاسيوم (K)
    CALCIUM = "calcium"  # كالسيوم (Ca)
    MAGNESIUM = "magnesium"  # مغنيسيوم (Mg)
    SULFUR = "sulfur"  # كبريت (S)

    # Micronutrients - العناصر الصغرى
    IRON = "iron"  # حديد (Fe)
    ZINC = "zinc"  # زنك (Zn)
    MANGANESE = "manganese"  # منجنيز (Mn)
    COPPER = "copper"  # نحاس (Cu)
    BORON = "boron"  # بورون (B)
    MOLYBDENUM = "molybdenum"  # موليبدنوم (Mo)


class DeficiencySeverity(str, Enum):
    """مستوى نقص العنصر"""

    OPTIMAL = "optimal"  # مثالي
    MARGINAL = "marginal"  # هامشي (حدّي)
    DEFICIENT = "deficient"  # ناقص
    SEVERELY_DEFICIENT = "severely_deficient"  # نقص شديد
    TOXIC = "toxic"  # سام (زيادة)


@dataclass
class FertilizerRecommendation:
    """توصية السماد"""

    product_name: str
    product_name_ar: str
    npk_ratio: str  # e.g., "20-20-20"
    dosage_kg_per_hectare: float
    dosage_ar: str
    application_method: str
    application_method_ar: str
    timing: str
    timing_ar: str
    cost_estimate_usd: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_name": self.product_name,
            "product_name_ar": self.product_name_ar,
            "npk_ratio": self.npk_ratio,
            "dosage_kg_per_hectare": self.dosage_kg_per_hectare,
            "dosage_ar": self.dosage_ar,
            "application_method": self.application_method,
            "application_method_ar": self.application_method_ar,
            "timing": self.timing,
            "timing_ar": self.timing_ar,
            "cost_estimate_usd": self.cost_estimate_usd,
        }


@dataclass
class NutrientDeficiency:
    """نتيجة كشف نقص العنصر"""

    nutrient: NutrientType
    severity: DeficiencySeverity
    confidence: float
    name_en: str
    name_ar: str
    symptoms_en: list[str]
    symptoms_ar: list[str]
    affected_indicator: str
    evidence: dict[str, Any]
    recommendations: list[FertilizerRecommendation]
    prevention_en: list[str]
    prevention_ar: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nutrient": self.nutrient.value,
            "severity": self.severity.value,
            "confidence": round(self.confidence, 2),
            "name_en": self.name_en,
            "name_ar": self.name_ar,
            "symptoms_en": self.symptoms_en,
            "symptoms_ar": self.symptoms_ar,
            "affected_indicator": self.affected_indicator,
            "evidence": self.evidence,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "prevention_en": self.prevention_en,
            "prevention_ar": self.prevention_ar,
        }


# Nutrient deficiency signatures based on vegetation indices
NUTRIENT_SIGNATURES = {
    NutrientType.NITROGEN: {
        "indicators": {
            "ndre_max": 0.22,  # Low NDRE indicates N deficiency
            "lci_max": 0.20,  # Low chlorophyll
            "ndvi_decline_threshold": 0.15,  # Gradual NDVI decline
        },
        "name_ar": "نقص النيتروجين",
        "name_en": "Nitrogen Deficiency",
        "symptoms_en": [
            "Yellowing of older (lower) leaves first",
            "Pale green color overall",
            "Stunted growth",
            "Reduced tillering in cereals",
        ],
        "symptoms_ar": [
            "اصفرار الأوراق القديمة (السفلية) أولاً",
            "لون أخضر باهت عام",
            "تقزم النمو",
            "قلة التفريع في الحبوب",
        ],
        "recommendations": [
            FertilizerRecommendation(
                product_name="Urea (46-0-0)",
                product_name_ar="يوريا",
                npk_ratio="46-0-0",
                dosage_kg_per_hectare=100,
                dosage_ar="100 كجم/هكتار",
                application_method="Broadcast or band application",
                application_method_ar="نثر أو وضع على شكل شرائط",
                timing="Split application: 50% at planting, 50% at tillering",
                timing_ar="جرعة مقسمة: 50% عند الزراعة، 50% عند التفريع",
                cost_estimate_usd=45,
            ),
            FertilizerRecommendation(
                product_name="Ammonium Sulfate (21-0-0)",
                product_name_ar="سلفات الأمونيوم",
                npk_ratio="21-0-0",
                dosage_kg_per_hectare=150,
                dosage_ar="150 كجم/هكتار",
                application_method="Soil application",
                application_method_ar="تطبيق تربة",
                timing="Pre-planting or sidedress",
                timing_ar="قبل الزراعة أو تسميد جانبي",
                cost_estimate_usd=40,
            ),
        ],
        "prevention_en": [
            "Regular soil testing",
            "Crop rotation with legumes",
            "Use organic matter amendments",
            "Apply nitrogen based on crop needs",
        ],
        "prevention_ar": [
            "تحليل تربة منتظم",
            "تناوب محاصيل مع بقوليات",
            "إضافة مادة عضوية",
            "تطبيق النيتروجين حسب احتياجات المحصول",
        ],
    },
    NutrientType.PHOSPHORUS: {
        "indicators": {
            "ndvi_range": (0.3, 0.5),  # Moderate NDVI
            "evi_max": 0.35,  # Low EVI
            "savi_max": 0.40,  # Low SAVI indicates poor root development
        },
        "name_ar": "نقص الفوسفور",
        "name_en": "Phosphorus Deficiency",
        "symptoms_en": [
            "Purple or reddish coloration on leaves",
            "Dark green foliage",
            "Delayed maturity",
            "Poor root development",
            "Reduced flowering",
        ],
        "symptoms_ar": [
            "تلون بنفسجي أو محمر على الأوراق",
            "أوراق خضراء داكنة",
            "تأخر النضج",
            "ضعف نمو الجذور",
            "قلة الإزهار",
        ],
        "recommendations": [
            FertilizerRecommendation(
                product_name="Triple Super Phosphate (0-46-0)",
                product_name_ar="سوبر فوسفات ثلاثي",
                npk_ratio="0-46-0",
                dosage_kg_per_hectare=80,
                dosage_ar="80 كجم/هكتار",
                application_method="Band application at planting",
                application_method_ar="وضع على شكل شرائط عند الزراعة",
                timing="Before planting or at planting",
                timing_ar="قبل الزراعة أو أثناءها",
                cost_estimate_usd=55,
            ),
            FertilizerRecommendation(
                product_name="DAP (18-46-0)",
                product_name_ar="دي أي بي",
                npk_ratio="18-46-0",
                dosage_kg_per_hectare=100,
                dosage_ar="100 كجم/هكتار",
                application_method="Broadcast and incorporate",
                application_method_ar="نثر وخلط بالتربة",
                timing="Pre-planting",
                timing_ar="قبل الزراعة",
                cost_estimate_usd=60,
            ),
        ],
        "prevention_en": [
            "Maintain soil pH between 6.0-7.0",
            "Apply phosphorus fertilizers at planting",
            "Use mycorrhizal inoculants",
            "Avoid over-liming",
        ],
        "prevention_ar": [
            "حافظ على حموضة التربة بين 6.0-7.0",
            "طبق أسمدة الفوسفور عند الزراعة",
            "استخدم ملقحات الميكوريزا",
            "تجنب الإفراط في الجير",
        ],
    },
    NutrientType.POTASSIUM: {
        "indicators": {
            "ndwi_max": 0.0,  # Low water content (K regulates water)
            "ndvi_edge_decline": True,  # Leaf edge effects
            "evi_decline_rate": 0.1,
        },
        "name_ar": "نقص البوتاسيوم",
        "name_en": "Potassium Deficiency",
        "symptoms_en": [
            "Brown scorching on leaf margins",
            "Weak stems (lodging)",
            "Poor fruit quality",
            "Increased disease susceptibility",
            "Reduced drought tolerance",
        ],
        "symptoms_ar": [
            "احتراق بني على حواف الأوراق",
            "سيقان ضعيفة (رقاد)",
            "جودة ثمار ضعيفة",
            "زيادة قابلية الإصابة بالأمراض",
            "قلة تحمل الجفاف",
        ],
        "recommendations": [
            FertilizerRecommendation(
                product_name="Potassium Chloride (0-0-60)",
                product_name_ar="كلوريد البوتاسيوم",
                npk_ratio="0-0-60",
                dosage_kg_per_hectare=100,
                dosage_ar="100 كجم/هكتار",
                application_method="Broadcast or band",
                application_method_ar="نثر أو شرائط",
                timing="Pre-planting or sidedress",
                timing_ar="قبل الزراعة أو تسميد جانبي",
                cost_estimate_usd=50,
            ),
            FertilizerRecommendation(
                product_name="Potassium Sulfate (0-0-50)",
                product_name_ar="سلفات البوتاسيوم",
                npk_ratio="0-0-50",
                dosage_kg_per_hectare=120,
                dosage_ar="120 كجم/هكتار",
                application_method="Soil or foliar application",
                application_method_ar="تطبيق تربة أو ورقي",
                timing="At flowering and fruiting",
                timing_ar="عند الإزهار والإثمار",
                cost_estimate_usd=65,
            ),
        ],
        "prevention_en": [
            "Regular soil testing for K levels",
            "Avoid excessive nitrogen application",
            "Apply potassium based on crop removal rates",
            "Use crop residue recycling",
        ],
        "prevention_ar": [
            "تحليل تربة منتظم لمستوى البوتاسيوم",
            "تجنب الإفراط في النيتروجين",
            "طبق البوتاسيوم حسب معدلات استهلاك المحصول",
            "أعد تدوير مخلفات المحصول",
        ],
    },
    NutrientType.IRON: {
        "indicators": {
            "lci_max": 0.15,  # Very low chlorophyll
            "ndre_max": 0.18,  # Low red edge
            "ndvi_min": 0.35,  # Maintain green but chlorotic
        },
        "name_ar": "نقص الحديد",
        "name_en": "Iron Deficiency",
        "symptoms_en": [
            "Interveinal chlorosis on young leaves",
            "Green veins with yellow tissue",
            "Severe cases: white leaves",
            "Stunted growth",
        ],
        "symptoms_ar": [
            "اصفرار بين العروق في الأوراق الفتية",
            "عروق خضراء مع نسيج أصفر",
            "الحالات الشديدة: أوراق بيضاء",
            "تقزم النمو",
        ],
        "recommendations": [
            FertilizerRecommendation(
                product_name="Iron Chelate (Fe-EDDHA 6%)",
                product_name_ar="شيلات الحديد",
                npk_ratio="Fe-6%",
                dosage_kg_per_hectare=4,
                dosage_ar="4 كجم/هكتار",
                application_method="Soil drench or fertigation",
                application_method_ar="غمر تربة أو تسميد بالري",
                timing="At first symptoms or preventively",
                timing_ar="عند أول الأعراض أو وقائياً",
                cost_estimate_usd=120,
            ),
            FertilizerRecommendation(
                product_name="Ferrous Sulfate",
                product_name_ar="كبريتات الحديدوز",
                npk_ratio="Fe-20%",
                dosage_kg_per_hectare=20,
                dosage_ar="20 كجم/هكتار",
                application_method="Foliar spray (0.5% solution)",
                application_method_ar="رش ورقي (محلول 0.5%)",
                timing="Every 2 weeks until recovery",
                timing_ar="كل أسبوعين حتى التعافي",
                cost_estimate_usd=25,
            ),
        ],
        "prevention_en": [
            "Maintain soil pH below 7.5",
            "Avoid over-irrigation in calcareous soils",
            "Use acidifying fertilizers",
            "Apply organic matter",
        ],
        "prevention_ar": [
            "حافظ على حموضة التربة أقل من 7.5",
            "تجنب الري الزائد في التربة الجيرية",
            "استخدم أسمدة محمّضة",
            "أضف مادة عضوية",
        ],
    },
    NutrientType.MAGNESIUM: {
        "indicators": {
            "lci_range": (0.10, 0.20),  # Moderate chlorophyll loss
            "ndvi_range": (0.35, 0.55),  # Maintained structure
        },
        "name_ar": "نقص المغنيسيوم",
        "name_en": "Magnesium Deficiency",
        "symptoms_en": [
            "Interveinal chlorosis on older leaves",
            "Leaf margins stay green initially",
            "Reddish-purple coloration in some crops",
            "Premature leaf drop",
        ],
        "symptoms_ar": [
            "اصفرار بين العروق في الأوراق القديمة",
            "حواف الأوراق تبقى خضراء أولاً",
            "تلون أحمر-بنفسجي في بعض المحاصيل",
            "سقوط أوراق مبكر",
        ],
        "recommendations": [
            FertilizerRecommendation(
                product_name="Magnesium Sulfate (Epsom Salt)",
                product_name_ar="كبريتات المغنيسيوم",
                npk_ratio="Mg-10%",
                dosage_kg_per_hectare=50,
                dosage_ar="50 كجم/هكتار",
                application_method="Soil or foliar (2% solution)",
                application_method_ar="تربة أو ورقي (محلول 2%)",
                timing="At early symptoms",
                timing_ar="عند أول الأعراض",
                cost_estimate_usd=30,
            ),
            FertilizerRecommendation(
                product_name="Dolomitic Lime",
                product_name_ar="الجير الدولوميتي",
                npk_ratio="Ca-Mg",
                dosage_kg_per_hectare=500,
                dosage_ar="500 كجم/هكتار",
                application_method="Broadcast and incorporate",
                application_method_ar="نثر وخلط بالتربة",
                timing="Pre-planting",
                timing_ar="قبل الزراعة",
                cost_estimate_usd=35,
            ),
        ],
        "prevention_en": [
            "Use dolomitic lime for pH correction",
            "Avoid excessive potassium application",
            "Regular soil testing",
            "Include magnesium in fertigation programs",
        ],
        "prevention_ar": [
            "استخدم الجير الدولوميتي لتصحيح الحموضة",
            "تجنب الإفراط في البوتاسيوم",
            "تحليل تربة منتظم",
            "أدرج المغنيسيوم في برامج التسميد بالري",
        ],
    },
    NutrientType.ZINC: {
        "indicators": {
            "ndvi_range": (0.4, 0.6),  # Moderate
            "evi_max": 0.40,
            "growth_stunting": True,
        },
        "name_ar": "نقص الزنك",
        "name_en": "Zinc Deficiency",
        "symptoms_en": [
            "Small, narrow leaves (little leaf)",
            "Interveinal chlorosis",
            "Shortened internodes (rosetting)",
            "Delayed maturity",
            "Poor fruit set",
        ],
        "symptoms_ar": [
            "أوراق صغيرة ضيقة",
            "اصفرار بين العروق",
            "قصر السلاميات (تورّد)",
            "تأخر النضج",
            "ضعف عقد الثمار",
        ],
        "recommendations": [
            FertilizerRecommendation(
                product_name="Zinc Sulfate",
                product_name_ar="كبريتات الزنك",
                npk_ratio="Zn-35%",
                dosage_kg_per_hectare=10,
                dosage_ar="10 كجم/هكتار",
                application_method="Soil or foliar (0.5%)",
                application_method_ar="تربة أو ورقي (0.5%)",
                timing="At planting or early growth",
                timing_ar="عند الزراعة أو النمو المبكر",
                cost_estimate_usd=35,
            ),
            FertilizerRecommendation(
                product_name="Zinc Chelate (Zn-EDTA)",
                product_name_ar="شيلات الزنك",
                npk_ratio="Zn-14%",
                dosage_kg_per_hectare=3,
                dosage_ar="3 كجم/هكتار",
                application_method="Foliar spray",
                application_method_ar="رش ورقي",
                timing="Every 2-3 weeks as needed",
                timing_ar="كل 2-3 أسابيع حسب الحاجة",
                cost_estimate_usd=50,
            ),
        ],
        "prevention_en": [
            "Maintain soil pH between 5.5-7.0",
            "Avoid excessive phosphorus application",
            "Use zinc-enriched fertilizers",
            "Apply organic matter",
        ],
        "prevention_ar": [
            "حافظ على حموضة التربة بين 5.5-7.0",
            "تجنب الإفراط في الفوسفور",
            "استخدم أسمدة غنية بالزنك",
            "أضف مادة عضوية",
        ],
    },
}


def detect_nutrient_deficiencies(
    ndvi: float,
    evi: float,
    ndre: float,
    ndwi: float,
    lci: float,
    savi: float,
    growth_stage: str = "vegetative",
) -> list[NutrientDeficiency]:
    """
    كشف نقص العناصر الغذائية من المؤشرات النباتية
    Detect nutrient deficiencies from vegetation indices

    Args:
        ndvi: Normalized Difference Vegetation Index
        evi: Enhanced Vegetation Index
        ndre: Normalized Difference Red Edge (nitrogen/chlorophyll indicator)
        ndwi: Normalized Difference Water Index
        lci: Leaf Chlorophyll Index
        savi: Soil-Adjusted Vegetation Index
        growth_stage: Current growth stage (vegetative, flowering, fruiting)

    Returns:
        List of detected nutrient deficiencies with recommendations
    """
    deficiencies = []

    # Nitrogen deficiency detection
    if ndre <= 0.22 and lci <= 0.20:
        severity = _get_n_severity(ndre, lci)
        confidence = min(1.0, (0.22 - ndre) * 8 + (0.20 - lci) * 5)

        sig = NUTRIENT_SIGNATURES[NutrientType.NITROGEN]
        deficiencies.append(
            NutrientDeficiency(
                nutrient=NutrientType.NITROGEN,
                severity=severity,
                confidence=min(0.95, confidence),
                name_en=sig["name_en"],
                name_ar=sig["name_ar"],
                symptoms_en=sig["symptoms_en"],
                symptoms_ar=sig["symptoms_ar"],
                affected_indicator="NDRE + LCI",
                evidence={"ndre": ndre, "lci": lci, "ndvi": ndvi},
                recommendations=sig["recommendations"],
                prevention_en=sig["prevention_en"],
                prevention_ar=sig["prevention_ar"],
            )
        )

    # Phosphorus deficiency detection
    if evi <= 0.35 and savi <= 0.40 and 0.3 <= ndvi <= 0.5:
        severity = DeficiencySeverity.DEFICIENT if evi <= 0.25 else DeficiencySeverity.MARGINAL
        confidence = min(0.85, (0.35 - evi) * 4 + (0.40 - savi) * 3)

        sig = NUTRIENT_SIGNATURES[NutrientType.PHOSPHORUS]
        deficiencies.append(
            NutrientDeficiency(
                nutrient=NutrientType.PHOSPHORUS,
                severity=severity,
                confidence=max(0.4, confidence),
                name_en=sig["name_en"],
                name_ar=sig["name_ar"],
                symptoms_en=sig["symptoms_en"],
                symptoms_ar=sig["symptoms_ar"],
                affected_indicator="EVI + SAVI",
                evidence={"evi": evi, "savi": savi, "ndvi": ndvi},
                recommendations=sig["recommendations"],
                prevention_en=sig["prevention_en"],
                prevention_ar=sig["prevention_ar"],
            )
        )

    # Potassium deficiency detection (water stress correlation)
    if ndwi <= 0.0 and ndvi >= 0.35:
        severity = (
            DeficiencySeverity.SEVERELY_DEFICIENT
            if ndwi <= -0.15
            else DeficiencySeverity.DEFICIENT
            if ndwi <= -0.05
            else DeficiencySeverity.MARGINAL
        )
        confidence = min(0.8, abs(ndwi) * 4)

        sig = NUTRIENT_SIGNATURES[NutrientType.POTASSIUM]
        deficiencies.append(
            NutrientDeficiency(
                nutrient=NutrientType.POTASSIUM,
                severity=severity,
                confidence=max(0.35, confidence),
                name_en=sig["name_en"],
                name_ar=sig["name_ar"],
                symptoms_en=sig["symptoms_en"],
                symptoms_ar=sig["symptoms_ar"],
                affected_indicator="NDWI",
                evidence={"ndwi": ndwi, "ndvi": ndvi},
                recommendations=sig["recommendations"],
                prevention_en=sig["prevention_en"],
                prevention_ar=sig["prevention_ar"],
            )
        )

    # Iron deficiency detection
    if lci <= 0.15 and ndre <= 0.18 and ndvi >= 0.35:
        severity = (
            DeficiencySeverity.SEVERELY_DEFICIENT
            if lci <= 0.08
            else DeficiencySeverity.DEFICIENT
            if lci <= 0.12
            else DeficiencySeverity.MARGINAL
        )
        confidence = min(0.9, (0.15 - lci) * 10)

        sig = NUTRIENT_SIGNATURES[NutrientType.IRON]
        deficiencies.append(
            NutrientDeficiency(
                nutrient=NutrientType.IRON,
                severity=severity,
                confidence=max(0.5, confidence),
                name_en=sig["name_en"],
                name_ar=sig["name_ar"],
                symptoms_en=sig["symptoms_en"],
                symptoms_ar=sig["symptoms_ar"],
                affected_indicator="LCI + NDRE",
                evidence={"lci": lci, "ndre": ndre, "ndvi": ndvi},
                recommendations=sig["recommendations"],
                prevention_en=sig["prevention_en"],
                prevention_ar=sig["prevention_ar"],
            )
        )

    # Magnesium deficiency detection
    if 0.10 <= lci <= 0.20 and 0.35 <= ndvi <= 0.55 and ndre > 0.20:
        severity = DeficiencySeverity.MARGINAL if lci >= 0.15 else DeficiencySeverity.DEFICIENT
        confidence = 0.55  # Lower confidence - needs visual confirmation

        sig = NUTRIENT_SIGNATURES[NutrientType.MAGNESIUM]
        deficiencies.append(
            NutrientDeficiency(
                nutrient=NutrientType.MAGNESIUM,
                severity=severity,
                confidence=confidence,
                name_en=sig["name_en"],
                name_ar=sig["name_ar"],
                symptoms_en=sig["symptoms_en"],
                symptoms_ar=sig["symptoms_ar"],
                affected_indicator="LCI pattern",
                evidence={"lci": lci, "ndvi": ndvi, "ndre": ndre},
                recommendations=sig["recommendations"],
                prevention_en=sig["prevention_en"],
                prevention_ar=sig["prevention_ar"],
            )
        )

    # Zinc deficiency detection
    if evi <= 0.40 and 0.4 <= ndvi <= 0.6:
        severity = DeficiencySeverity.MARGINAL
        confidence = 0.45  # Low confidence - needs visual confirmation

        sig = NUTRIENT_SIGNATURES[NutrientType.ZINC]
        deficiencies.append(
            NutrientDeficiency(
                nutrient=NutrientType.ZINC,
                severity=severity,
                confidence=confidence,
                name_en=sig["name_en"],
                name_ar=sig["name_ar"],
                symptoms_en=sig["symptoms_en"],
                symptoms_ar=sig["symptoms_ar"],
                affected_indicator="EVI + growth pattern",
                evidence={"evi": evi, "ndvi": ndvi},
                recommendations=sig["recommendations"],
                prevention_en=sig["prevention_en"],
                prevention_ar=sig["prevention_ar"],
            )
        )

    # Sort by severity and confidence
    severity_order = {
        DeficiencySeverity.SEVERELY_DEFICIENT: 0,
        DeficiencySeverity.DEFICIENT: 1,
        DeficiencySeverity.MARGINAL: 2,
        DeficiencySeverity.OPTIMAL: 3,
        DeficiencySeverity.TOXIC: 4,
    }
    deficiencies.sort(key=lambda d: (severity_order.get(d.severity, 5), -d.confidence))

    return deficiencies


def _get_n_severity(ndre: float, lci: float) -> DeficiencySeverity:
    """Determine nitrogen deficiency severity"""
    if ndre <= 0.10 or lci <= 0.08:
        return DeficiencySeverity.SEVERELY_DEFICIENT
    elif ndre <= 0.15 or lci <= 0.12:
        return DeficiencySeverity.DEFICIENT
    elif ndre <= 0.20 or lci <= 0.18:
        return DeficiencySeverity.MARGINAL
    else:
        return DeficiencySeverity.OPTIMAL


def get_nutrient_status_summary(deficiencies: list[NutrientDeficiency]) -> dict[str, Any]:
    """
    ملخص حالة العناصر الغذائية
    Get overall nutrient status summary

    Returns:
        Dictionary with overall status and details
    """
    if not deficiencies:
        return {
            "overall_status_en": "Optimal",
            "overall_status_ar": "مثالي",
            "action_required": False,
            "priority_nutrients": [],
            "estimated_cost_usd": 0,
        }

    # Find highest priority deficiencies
    priority = []
    total_cost = 0

    for d in deficiencies:
        if d.severity in [DeficiencySeverity.SEVERELY_DEFICIENT, DeficiencySeverity.DEFICIENT]:
            priority.append(d.nutrient.value)
            if d.recommendations:
                total_cost += d.recommendations[0].cost_estimate_usd or 0

    if any(d.severity == DeficiencySeverity.SEVERELY_DEFICIENT for d in deficiencies):
        status_en, status_ar = "Critical", "حرج"
    elif any(d.severity == DeficiencySeverity.DEFICIENT for d in deficiencies):
        status_en, status_ar = "Deficient", "ناقص"
    elif any(d.severity == DeficiencySeverity.MARGINAL for d in deficiencies):
        status_en, status_ar = "Marginal", "هامشي"
    else:
        status_en, status_ar = "Optimal", "مثالي"

    return {
        "overall_status_en": status_en,
        "overall_status_ar": status_ar,
        "action_required": len(priority) > 0,
        "priority_nutrients": priority,
        "deficiency_count": len(deficiencies),
        "estimated_cost_usd": round(total_cost, 2),
    }


def generate_fertilizer_plan(
    deficiencies: list[NutrientDeficiency],
    field_area_hectares: float = 1.0,
    budget_usd: float | None = None,
) -> dict[str, Any]:
    """
    إنشاء خطة تسميد
    Generate a fertilizer application plan

    Args:
        deficiencies: List of detected deficiencies
        field_area_hectares: Field area in hectares
        budget_usd: Optional budget limit

    Returns:
        Fertilizer plan with products, quantities, and schedule
    """
    plan = {
        "field_area_hectares": field_area_hectares,
        "applications": [],
        "total_cost_usd": 0,
        "schedule": [],
        "notes_en": [],
        "notes_ar": [],
    }

    # Sort by priority (severity)
    priority_deficiencies = sorted(
        deficiencies,
        key=lambda d: (
            0
            if d.severity == DeficiencySeverity.SEVERELY_DEFICIENT
            else 1
            if d.severity == DeficiencySeverity.DEFICIENT
            else 2
        ),
    )

    running_cost = 0
    for deficiency in priority_deficiencies:
        if not deficiency.recommendations:
            continue

        rec = deficiency.recommendations[0]  # Primary recommendation
        product_cost = (rec.cost_estimate_usd or 0) * field_area_hectares

        # Check budget
        if budget_usd and running_cost + product_cost > budget_usd:
            plan["notes_en"].append(f"Skipped {rec.product_name} due to budget constraints")
            plan["notes_ar"].append(f"تم تخطي {rec.product_name_ar} بسبب قيود الميزانية")
            continue

        running_cost += product_cost

        plan["applications"].append(
            {
                "nutrient": deficiency.nutrient.value,
                "product": rec.product_name,
                "product_ar": rec.product_name_ar,
                "quantity_kg": round(rec.dosage_kg_per_hectare * field_area_hectares, 1),
                "application_method": rec.application_method,
                "application_method_ar": rec.application_method_ar,
                "timing": rec.timing,
                "timing_ar": rec.timing_ar,
                "cost_usd": round(product_cost, 2),
            }
        )

    plan["total_cost_usd"] = round(running_cost, 2)

    # Generate schedule
    if plan["applications"]:
        plan["schedule"] = [
            {
                "week": 1,
                "action_en": "Apply nitrogen and phosphorus fertilizers",
                "action_ar": "تطبيق أسمدة النيتروجين والفوسفور",
            },
            {
                "week": 2,
                "action_en": "Apply micronutrients (foliar)",
                "action_ar": "تطبيق العناصر الصغرى (ورقي)",
            },
            {
                "week": 4,
                "action_en": "Re-evaluate and apply potassium if needed",
                "action_ar": "إعادة تقييم وتطبيق البوتاسيوم إذا لزم",
            },
        ]

    return plan
