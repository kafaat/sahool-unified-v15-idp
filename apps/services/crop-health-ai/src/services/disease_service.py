"""
Sahool Vision - Disease Service
خدمة معلومات الأمراض

هذه الخدمة مسؤولة عن:
- قاعدة بيانات الأمراض
- معلومات المحاصيل المدعومة
- تفاصيل العلاج
"""

from typing import Any

# Fixed relative import - إصلاح الاستيراد النسبي
from ..models.disease import (
    CropType,
    DiseaseSeverity,
    Treatment,
    TreatmentType,
)


class DiseaseService:
    """
    خدمة إدارة معلومات الأمراض
    Disease Information Management Service
    """

    # قاعدة بيانات الأمراض (Yemen-focused crops)
    DISEASE_DATABASE: dict[str, dict[str, Any]] = {
        "wheat_leaf_rust": {
            "name": "Wheat Leaf Rust",
            "name_ar": "صدأ أوراق القمح",
            "description": "Fungal disease causing orange-brown pustules on leaves",
            "description_ar": "مرض فطري يسبب بثور برتقالية-بنية على الأوراق",
            "crop": CropType.WHEAT,
            "severity_default": DiseaseSeverity.MEDIUM,
            "treatments": [
                Treatment(
                    treatment_type=TreatmentType.FUNGICIDE,
                    product_name="Propiconazole 25% EC",
                    product_name_ar="بروبيكونازول 25%",
                    dosage="0.5 L/hectare",
                    dosage_ar="0.5 لتر/هكتار",
                    application_method="Foliar spray",
                    application_method_ar="رش ورقي",
                    frequency="Every 14 days if infection persists",
                    frequency_ar="كل 14 يوم إذا استمرت الإصابة",
                    precautions=["Wear protective equipment", "Avoid spraying in wind"],
                    precautions_ar=["ارتداء معدات الحماية", "تجنب الرش في الرياح"],
                )
            ],
            "prevention": [
                "Use resistant varieties",
                "Crop rotation",
                "Remove crop residues",
            ],
            "prevention_ar": [
                "استخدام أصناف مقاومة",
                "الدورة الزراعية",
                "إزالة بقايا المحصول",
            ],
        },
        "tomato_late_blight": {
            "name": "Tomato Late Blight",
            "name_ar": "اللفحة المتأخرة للطماطم",
            "description": "Devastating fungal disease causing dark lesions and rapid plant death",
            "description_ar": "مرض فطري مدمر يسبب آفات داكنة وموت سريع للنبات",
            "crop": CropType.TOMATO,
            "severity_default": DiseaseSeverity.HIGH,
            "treatments": [
                Treatment(
                    treatment_type=TreatmentType.FUNGICIDE,
                    product_name="Copper Hydroxide",
                    product_name_ar="هيدروكسيد النحاس",
                    dosage="2-3 kg/hectare",
                    dosage_ar="2-3 كجم/هكتار",
                    application_method="Foliar spray before infection",
                    application_method_ar="رش ورقي قبل الإصابة",
                    frequency="Every 7-10 days during humid conditions",
                    frequency_ar="كل 7-10 أيام في الظروف الرطبة",
                    precautions=["Apply before rain", "Ensure complete coverage"],
                    precautions_ar=["التطبيق قبل المطر", "ضمان التغطية الكاملة"],
                )
            ],
            "prevention": [
                "Avoid overhead irrigation",
                "Improve air circulation",
                "Plant resistant varieties",
            ],
            "prevention_ar": [
                "تجنب الري العلوي",
                "تحسين دوران الهواء",
                "زراعة أصناف مقاومة",
            ],
        },
        "coffee_leaf_rust": {
            "name": "Coffee Leaf Rust",
            "name_ar": "صدأ أوراق البن",
            "description": "Major fungal disease affecting coffee plants, causing yellow-orange spots",
            "description_ar": "مرض فطري رئيسي يصيب نباتات البن، يسبب بقع صفراء-برتقالية",
            "crop": CropType.COFFEE,
            "severity_default": DiseaseSeverity.HIGH,
            "treatments": [
                Treatment(
                    treatment_type=TreatmentType.FUNGICIDE,
                    product_name="Bordeaux Mixture",
                    product_name_ar="خليط بوردو",
                    dosage="1% solution",
                    dosage_ar="محلول 1%",
                    application_method="Spray on leaves",
                    application_method_ar="رش على الأوراق",
                    frequency="Monthly during rainy season",
                    frequency_ar="شهرياً خلال موسم الأمطار",
                    precautions=["Test on small area first"],
                    precautions_ar=["اختبار على منطقة صغيرة أولاً"],
                )
            ],
            "prevention": [
                "Shade management",
                "Proper nutrition",
                "Resistant varieties",
            ],
            "prevention_ar": ["إدارة الظل", "التغذية السليمة", "الأصناف المقاومة"],
        },
        "date_palm_bayoud": {
            "name": "Date Palm Bayoud Disease",
            "name_ar": "مرض البيوض في النخيل",
            "description": "Lethal fungal disease causing wilting and death of date palms",
            "description_ar": "مرض فطري قاتل يسبب ذبول وموت النخيل",
            "crop": CropType.DATE_PALM,
            "severity_default": DiseaseSeverity.CRITICAL,
            "treatments": [
                Treatment(
                    treatment_type=TreatmentType.FUNGICIDE,
                    product_name="Carbendazim",
                    product_name_ar="كاربندازيم",
                    dosage="Soil drench application",
                    dosage_ar="تطبيق غمر التربة",
                    application_method="Apply to soil around trunk",
                    application_method_ar="تطبيق على التربة حول الجذع",
                    frequency="At first signs of infection",
                    frequency_ar="عند أول علامات الإصابة",
                    precautions=[
                        "Remove and burn infected trees",
                        "Quarantine affected area",
                    ],
                    precautions_ar=[
                        "إزالة وحرق الأشجار المصابة",
                        "عزل المنطقة المصابة",
                    ],
                )
            ],
            "prevention": [
                "Use certified disease-free offshoots",
                "Avoid moving soil",
                "Monitor regularly",
            ],
            "prevention_ar": [
                "استخدام فسائل معتمدة خالية من المرض",
                "تجنب نقل التربة",
                "المراقبة المنتظمة",
            ],
        },
        "mango_anthracnose": {
            "name": "Mango Anthracnose",
            "name_ar": "أنثراكنوز المانجو",
            "description": "Fungal disease causing black spots on leaves and fruits",
            "description_ar": "مرض فطري يسبب بقع سوداء على الأوراق والثمار",
            "crop": CropType.MANGO,
            "severity_default": DiseaseSeverity.MEDIUM,
            "treatments": [
                Treatment(
                    treatment_type=TreatmentType.FUNGICIDE,
                    product_name="Mancozeb 75% WP",
                    product_name_ar="مانكوزيب 75%",
                    dosage="2.5 g/L water",
                    dosage_ar="2.5 جم/لتر ماء",
                    application_method="Spray during flowering and fruit set",
                    application_method_ar="رش أثناء الإزهار وعقد الثمار",
                    frequency="Every 15 days during humid season",
                    frequency_ar="كل 15 يوم خلال الموسم الرطب",
                    precautions=["Avoid application during hot midday"],
                    precautions_ar=["تجنب التطبيق في منتصف النهار الحار"],
                )
            ],
            "prevention": [
                "Prune dead branches",
                "Good drainage",
                "Avoid wetting foliage",
            ],
            "prevention_ar": ["تقليم الفروع الميتة", "صرف جيد", "تجنب تبليل الأوراق"],
        },
        "healthy": {
            "name": "Healthy Plant",
            "name_ar": "نبات سليم",
            "description": "No disease detected. Plant appears healthy.",
            "description_ar": "لم يتم اكتشاف مرض. النبات يبدو سليماً.",
            "crop": CropType.UNKNOWN,
            "severity_default": DiseaseSeverity.HEALTHY,
            "treatments": [],
            "prevention": [
                "Continue good agricultural practices",
                "Regular monitoring",
            ],
            "prevention_ar": ["استمرار الممارسات الزراعية الجيدة", "المراقبة المنتظمة"],
        },
    }

    # معلومات المحاصيل المدعومة
    CROPS_INFO = {
        CropType.WHEAT: {"name_ar": "قمح", "icon": "🌾"},
        CropType.TOMATO: {"name_ar": "طماطم", "icon": "🍅"},
        CropType.POTATO: {"name_ar": "بطاطس", "icon": "🥔"},
        CropType.CORN: {"name_ar": "ذرة", "icon": "🌽"},
        CropType.GRAPE: {"name_ar": "عنب", "icon": "🍇"},
        CropType.APPLE: {"name_ar": "تفاح", "icon": "🍎"},
        CropType.COFFEE: {"name_ar": "بن", "icon": "☕"},
        CropType.DATE_PALM: {"name_ar": "نخيل", "icon": "🌴"},
        CropType.MANGO: {"name_ar": "مانجو", "icon": "🥭"},
        CropType.CITRUS: {"name_ar": "حمضيات", "icon": "🍊"},
        CropType.COTTON: {"name_ar": "قطن", "icon": "🌿"},
        CropType.SORGHUM: {"name_ar": "ذرة رفيعة", "icon": "🌾"},
    }

    def get_disease(self, disease_id: str) -> dict[str, Any] | None:
        """الحصول على معلومات مرض معين"""
        return self.DISEASE_DATABASE.get(disease_id)

    def get_all_diseases(self, crop_type: CropType | None = None) -> list[dict[str, Any]]:
        """الحصول على قائمة جميع الأمراض"""
        diseases = []
        for key, info in self.DISEASE_DATABASE.items():
            if key == "healthy":
                continue
            if crop_type and info.get("crop") != crop_type:
                continue
            diseases.append(
                {
                    "disease_id": key,
                    "name": info["name"],
                    "name_ar": info["name_ar"],
                    "crop": info.get("crop", CropType.UNKNOWN).value,
                    "severity": info["severity_default"].value,
                }
            )
        return diseases

    def get_treatment_details(self, disease_id: str) -> dict[str, Any] | None:
        """الحصول على تفاصيل العلاج"""
        disease = self.DISEASE_DATABASE.get(disease_id)
        if not disease:
            return None

        return {
            "disease_id": disease_id,
            "disease_name": disease["name"],
            "disease_name_ar": disease["name_ar"],
            "treatments": [t.model_dump() for t in disease.get("treatments", [])],
            "prevention": disease.get("prevention", []),
            "prevention_ar": disease.get("prevention_ar", []),
            "severity": disease["severity_default"].value,
        }

    def get_supported_crops(self) -> list[dict[str, Any]]:
        """الحصول على قائمة المحاصيل المدعومة"""
        return [
            {
                "crop_id": crop.value,
                "name": crop.value.replace("_", " ").title(),
                "name_ar": info["name_ar"],
                "icon": info["icon"],
                "diseases_count": sum(
                    1 for d in self.DISEASE_DATABASE.values() if d.get("crop") == crop
                ),
            }
            for crop, info in self.CROPS_INFO.items()
        ]

    def get_disease_names(self) -> list[str]:
        """الحصول على قائمة أسماء الأمراض للنموذج"""
        return list(self.DISEASE_DATABASE.keys())


# Singleton instance
disease_service = DiseaseService()
