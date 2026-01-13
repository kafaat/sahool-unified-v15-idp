"""
SAHOOL Disease Detection Module
وحدة كشف الأمراض النباتية

Rule-based disease detection from vegetation indices and environmental conditions.
Based on agricultural research for Yemen crops.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CropType(str, Enum):
    """أنواع المحاصيل المدعومة في اليمن"""

    WHEAT = "wheat"  # قمح
    SORGHUM = "sorghum"  # ذرة رفيعة
    MILLET = "millet"  # دخن
    TOMATO = "tomato"  # طماطم
    POTATO = "potato"  # بطاطس
    CORN = "corn"  # ذرة
    COFFEE = "coffee"  # قهوة (بن يمني)
    DATE_PALM = "date_palm"  # نخيل
    MANGO = "mango"  # مانجو
    CITRUS = "citrus"  # حمضيات
    GRAPE = "grape"  # عنب
    COTTON = "cotton"  # قطن
    QAT = "qat"  # قات
    SESAME = "sesame"  # سمسم
    ALFALFA = "alfalfa"  # برسيم
    UNKNOWN = "unknown"


class DiseaseSeverity(str, Enum):
    """مستوى خطورة المرض"""

    HEALTHY = "healthy"  # سليم
    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # مرتفع
    CRITICAL = "critical"  # حرج


class DiseaseType(str, Enum):
    """أنواع الأمراض الشائعة"""

    # Fungal diseases - أمراض فطرية
    POWDERY_MILDEW = "powdery_mildew"  # البياض الدقيقي
    DOWNY_MILDEW = "downy_mildew"  # البياض الزغبي
    RUST = "rust"  # الصدأ
    LEAF_SPOT = "leaf_spot"  # تبقع الأوراق
    BLIGHT = "blight"  # اللفحة
    ROOT_ROT = "root_rot"  # عفن الجذور

    # Bacterial diseases - أمراض بكتيرية
    BACTERIAL_WILT = "bacterial_wilt"  # الذبول البكتيري
    BACTERIAL_SPOT = "bacterial_spot"  # التبقع البكتيري

    # Viral diseases - أمراض فيروسية
    MOSAIC_VIRUS = "mosaic_virus"  # فيروس الموزايك
    LEAF_CURL = "leaf_curl"  # تجعد الأوراق

    # Deficiencies - نقص عناصر
    NITROGEN_DEFICIENCY = "nitrogen_deficiency"  # نقص نيتروجين
    IRON_DEFICIENCY = "iron_deficiency"  # نقص حديد
    POTASSIUM_DEFICIENCY = "potassium_deficiency"  # نقص بوتاسيوم

    # Stress conditions - إجهاد
    WATER_STRESS = "water_stress"  # إجهاد مائي
    HEAT_STRESS = "heat_stress"  # إجهاد حراري
    SALT_STRESS = "salt_stress"  # إجهاد ملحي

    UNKNOWN = "unknown"


class TreatmentType(str, Enum):
    """نوع العلاج المقترح"""

    FUNGICIDE = "fungicide"  # مبيد فطري
    BACTERICIDE = "bactericide"  # مبيد بكتيري
    INSECTICIDE = "insecticide"  # مبيد حشري
    FERTILIZER = "fertilizer"  # سماد
    IRRIGATION = "irrigation"  # ري
    PRUNING = "pruning"  # تقليم
    SOIL_AMENDMENT = "soil_amendment"  # تحسين التربة
    SHADE = "shade"  # تظليل
    NONE = "none"  # لا يحتاج علاج


@dataclass
class Treatment:
    """معلومات العلاج المقترح"""

    treatment_type: TreatmentType
    product_name: str
    product_name_ar: str
    dosage: str
    dosage_ar: str
    application_method: str
    application_method_ar: str
    urgency_days: int
    precautions: list[str]
    precautions_ar: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "treatment_type": self.treatment_type.value,
            "product_name": self.product_name,
            "product_name_ar": self.product_name_ar,
            "dosage": self.dosage,
            "dosage_ar": self.dosage_ar,
            "application_method": self.application_method,
            "application_method_ar": self.application_method_ar,
            "urgency_days": self.urgency_days,
            "precautions": self.precautions,
            "precautions_ar": self.precautions_ar,
        }


@dataclass
class DiseaseDetection:
    """نتيجة كشف المرض"""

    disease_type: DiseaseType
    severity: DiseaseSeverity
    confidence: float  # 0-1
    name_en: str
    name_ar: str
    description_en: str
    description_ar: str
    affected_indicator: str  # Which index indicated the problem
    evidence: dict[str, Any]
    treatments: list[Treatment]
    prevention: list[str]
    prevention_ar: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "disease_type": self.disease_type.value,
            "severity": self.severity.value,
            "confidence": round(self.confidence, 2),
            "name_en": self.name_en,
            "name_ar": self.name_ar,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "affected_indicator": self.affected_indicator,
            "evidence": self.evidence,
            "treatments": [t.to_dict() for t in self.treatments],
            "prevention": self.prevention,
            "prevention_ar": self.prevention_ar,
        }


# Disease detection rules database
DISEASE_RULES = {
    # Fungal disease patterns
    "powdery_mildew": {
        "conditions": {
            "ndvi_range": (0.3, 0.6),
            "humidity_min": 60,
            "temp_range": (15, 28),
        },
        "name_ar": "البياض الدقيقي",
        "name_en": "Powdery Mildew",
        "description_ar": "مرض فطري يظهر كبقع بيضاء دقيقية على الأوراق",
        "description_en": "Fungal disease appearing as white powdery spots on leaves",
        "treatments": [
            Treatment(
                treatment_type=TreatmentType.FUNGICIDE,
                product_name="Sulfur-based fungicide",
                product_name_ar="مبيد كبريتي",
                dosage="2-3 kg/hectare",
                dosage_ar="2-3 كجم/هكتار",
                application_method="Foliar spray",
                application_method_ar="رش ورقي",
                urgency_days=7,
                precautions=["Avoid spraying in hot weather", "Use protective equipment"],
                precautions_ar=["تجنب الرش في الطقس الحار", "استخدم معدات الوقاية"],
            )
        ],
        "prevention": ["Ensure good air circulation", "Avoid overhead irrigation"],
        "prevention_ar": ["ضمان تهوية جيدة", "تجنب الري العلوي"],
    },
    "rust": {
        "conditions": {
            "ndvi_range": (0.25, 0.55),
            "ndre_max": 0.25,
            "humidity_min": 70,
        },
        "name_ar": "الصدأ",
        "name_en": "Rust Disease",
        "description_ar": "مرض فطري يظهر كبثور صدئية على الأوراق والسيقان",
        "description_en": "Fungal disease showing rusty pustules on leaves and stems",
        "treatments": [
            Treatment(
                treatment_type=TreatmentType.FUNGICIDE,
                product_name="Triazole fungicide",
                product_name_ar="مبيد ترايازول",
                dosage="0.5-1 L/hectare",
                dosage_ar="0.5-1 لتر/هكتار",
                application_method="Foliar spray at early symptoms",
                application_method_ar="رش ورقي عند أول الأعراض",
                urgency_days=5,
                precautions=["Apply at early infection stage"],
                precautions_ar=["طبق في مرحلة الإصابة المبكرة"],
            )
        ],
        "prevention": ["Use resistant varieties", "Remove infected debris"],
        "prevention_ar": ["استخدم أصناف مقاومة", "أزل المخلفات المصابة"],
    },
    "nitrogen_deficiency": {
        "conditions": {
            "ndre_max": 0.22,
            "ndvi_min": 0.4,
            "lci_max": 0.2,
        },
        "name_ar": "نقص النيتروجين",
        "name_en": "Nitrogen Deficiency",
        "description_ar": "اصفرار الأوراق القديمة وضعف النمو بسبب نقص النيتروجين",
        "description_en": "Yellowing of older leaves and stunted growth due to nitrogen deficiency",
        "treatments": [
            Treatment(
                treatment_type=TreatmentType.FERTILIZER,
                product_name="Urea or Ammonium Sulfate",
                product_name_ar="يوريا أو سلفات الأمونيوم",
                dosage="50-100 kg/hectare",
                dosage_ar="50-100 كجم/هكتار",
                application_method="Soil application or fertigation",
                application_method_ar="تطبيق تربة أو تسميد بالري",
                urgency_days=14,
                precautions=["Don't apply in hot midday", "Water after application"],
                precautions_ar=["لا تطبق في منتصف النهار الحار", "اروِ بعد التطبيق"],
            )
        ],
        "prevention": ["Regular soil testing", "Crop rotation with legumes"],
        "prevention_ar": ["تحليل تربة منتظم", "تناوب محاصيل مع بقوليات"],
    },
    "water_stress": {
        "conditions": {
            "ndwi_max": -0.1,
            "ndvi_declining": True,
        },
        "name_ar": "إجهاد مائي",
        "name_en": "Water Stress",
        "description_ar": "نقص المياه يؤدي إلى ذبول وتراجع نمو النبات",
        "description_en": "Water shortage causing wilting and reduced plant growth",
        "treatments": [
            Treatment(
                treatment_type=TreatmentType.IRRIGATION,
                product_name="Irrigation",
                product_name_ar="ري",
                dosage="Based on crop ET requirements",
                dosage_ar="حسب احتياجات التبخر-نتح",
                application_method="Drip or furrow irrigation",
                application_method_ar="ري بالتنقيط أو الأخاديد",
                urgency_days=2,
                precautions=["Irrigate in early morning or evening"],
                precautions_ar=["اروِ في الصباح الباكر أو المساء"],
            )
        ],
        "prevention": ["Install moisture sensors", "Use mulching"],
        "prevention_ar": ["ركب حساسات رطوبة", "استخدم التغطية"],
    },
}


def detect_diseases(
    ndvi: float,
    evi: float,
    ndre: float,
    ndwi: float,
    lci: float,
    savi: float,
    crop_type: CropType = CropType.UNKNOWN,
    humidity_pct: float | None = None,
    temp_c: float | None = None,
) -> list[DiseaseDetection]:
    """
    كشف الأمراض المحتملة من المؤشرات النباتية
    Detect potential diseases from vegetation indices

    Args:
        ndvi: Normalized Difference Vegetation Index
        evi: Enhanced Vegetation Index
        ndre: Normalized Difference Red Edge (nitrogen indicator)
        ndwi: Normalized Difference Water Index
        lci: Leaf Chlorophyll Index
        savi: Soil-Adjusted Vegetation Index
        crop_type: Type of crop (for specific disease patterns)
        humidity_pct: Optional humidity percentage
        temp_c: Optional temperature in Celsius

    Returns:
        List of detected diseases with treatments
    """
    detections = []

    # Water stress detection
    if ndwi <= -0.1:
        severity = (
            DiseaseSeverity.CRITICAL
            if ndwi <= -0.2
            else DiseaseSeverity.HIGH
            if ndwi <= -0.15
            else DiseaseSeverity.MEDIUM
        )
        confidence = min(1.0, abs(ndwi + 0.1) * 5)  # Scale confidence

        rule = DISEASE_RULES["water_stress"]
        detections.append(
            DiseaseDetection(
                disease_type=DiseaseType.WATER_STRESS,
                severity=severity,
                confidence=confidence,
                name_en=rule["name_en"],
                name_ar=rule["name_ar"],
                description_en=rule["description_en"],
                description_ar=rule["description_ar"],
                affected_indicator="NDWI",
                evidence={"ndwi": ndwi, "threshold": -0.1},
                treatments=rule["treatments"],
                prevention=rule["prevention"],
                prevention_ar=rule["prevention_ar"],
            )
        )

    # Nitrogen deficiency detection
    if ndre <= 0.22 and ndvi >= 0.4:
        severity = (
            DiseaseSeverity.HIGH
            if ndre <= 0.15
            else DiseaseSeverity.MEDIUM
            if ndre <= 0.18
            else DiseaseSeverity.LOW
        )
        confidence = min(1.0, (0.22 - ndre) * 10)

        rule = DISEASE_RULES["nitrogen_deficiency"]
        detections.append(
            DiseaseDetection(
                disease_type=DiseaseType.NITROGEN_DEFICIENCY,
                severity=severity,
                confidence=confidence,
                name_en=rule["name_en"],
                name_ar=rule["name_ar"],
                description_en=rule["description_en"],
                description_ar=rule["description_ar"],
                affected_indicator="NDRE",
                evidence={"ndre": ndre, "ndvi": ndvi, "lci": lci},
                treatments=rule["treatments"],
                prevention=rule["prevention"],
                prevention_ar=rule["prevention_ar"],
            )
        )

    # Rust detection (with humidity consideration)
    if ndvi >= 0.25 and ndvi <= 0.55 and ndre <= 0.25:
        if humidity_pct is None or humidity_pct >= 70:
            severity = DiseaseSeverity.MEDIUM if ndre <= 0.20 else DiseaseSeverity.LOW
            confidence = 0.6 if humidity_pct is None else 0.8

            rule = DISEASE_RULES["rust"]
            detections.append(
                DiseaseDetection(
                    disease_type=DiseaseType.RUST,
                    severity=severity,
                    confidence=confidence,
                    name_en=rule["name_en"],
                    name_ar=rule["name_ar"],
                    description_en=rule["description_en"],
                    description_ar=rule["description_ar"],
                    affected_indicator="NDRE + humidity",
                    evidence={"ndvi": ndvi, "ndre": ndre, "humidity": humidity_pct},
                    treatments=rule["treatments"],
                    prevention=rule["prevention"],
                    prevention_ar=rule["prevention_ar"],
                )
            )

    # Powdery mildew detection
    if humidity_pct and temp_c:
        if humidity_pct >= 60 and 15 <= temp_c <= 28 and 0.3 <= ndvi <= 0.6:
            rule = DISEASE_RULES["powdery_mildew"]
            detections.append(
                DiseaseDetection(
                    disease_type=DiseaseType.POWDERY_MILDEW,
                    severity=DiseaseSeverity.LOW,
                    confidence=0.5,  # Lower confidence without visual confirmation
                    name_en=rule["name_en"],
                    name_ar=rule["name_ar"],
                    description_en=rule["description_en"],
                    description_ar=rule["description_ar"],
                    affected_indicator="Environmental conditions",
                    evidence={"humidity": humidity_pct, "temp_c": temp_c, "ndvi": ndvi},
                    treatments=rule["treatments"],
                    prevention=rule["prevention"],
                    prevention_ar=rule["prevention_ar"],
                )
            )

    # Low chlorophyll detection (general stress indicator)
    if lci < 0.15 and ndvi >= 0.35:
        detections.append(
            DiseaseDetection(
                disease_type=DiseaseType.IRON_DEFICIENCY,
                severity=DiseaseSeverity.MEDIUM if lci < 0.10 else DiseaseSeverity.LOW,
                confidence=0.6,
                name_en="Iron/Chlorophyll Deficiency",
                name_ar="نقص حديد/كلوروفيل",
                description_en="Low chlorophyll content indicating possible iron or micronutrient deficiency",
                description_ar="انخفاض محتوى الكلوروفيل يشير لنقص محتمل في الحديد أو العناصر الصغرى",
                affected_indicator="LCI",
                evidence={"lci": lci, "ndvi": ndvi},
                treatments=[
                    Treatment(
                        treatment_type=TreatmentType.FERTILIZER,
                        product_name="Iron chelate (Fe-EDDHA)",
                        product_name_ar="شيلات الحديد",
                        dosage="2-4 kg/hectare",
                        dosage_ar="2-4 كجم/هكتار",
                        application_method="Foliar spray or soil application",
                        application_method_ar="رش ورقي أو تطبيق تربة",
                        urgency_days=14,
                        precautions=["Check soil pH"],
                        precautions_ar=["افحص حموضة التربة"],
                    )
                ],
                prevention=["Regular soil testing", "Maintain proper soil pH"],
                prevention_ar=["تحليل تربة منتظم", "حافظ على حموضة تربة مناسبة"],
            )
        )

    # Sort by severity and confidence
    severity_order = {
        DiseaseSeverity.CRITICAL: 0,
        DiseaseSeverity.HIGH: 1,
        DiseaseSeverity.MEDIUM: 2,
        DiseaseSeverity.LOW: 3,
        DiseaseSeverity.HEALTHY: 4,
    }
    detections.sort(key=lambda d: (severity_order.get(d.severity, 5), -d.confidence))

    return detections


def get_overall_health_status(detections: list[DiseaseDetection]) -> tuple[str, str]:
    """
    تحديد الحالة الصحية العامة من قائمة الكشوفات
    Determine overall health status from detection list

    Returns:
        Tuple of (status_en, status_ar)
    """
    if not detections:
        return ("healthy", "سليم")

    severities = [d.severity for d in detections]

    if DiseaseSeverity.CRITICAL in severities:
        return ("critical", "حرج")
    elif DiseaseSeverity.HIGH in severities:
        return ("poor", "ضعيف")
    elif DiseaseSeverity.MEDIUM in severities:
        return ("fair", "متوسط")
    elif DiseaseSeverity.LOW in severities:
        return ("good", "جيد")
    else:
        return ("healthy", "سليم")
