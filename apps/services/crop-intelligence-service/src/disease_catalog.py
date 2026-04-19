"""
Named-disease catalog ported from the archived crop-health-ai service.

crop-intelligence-service already hosts:
  * rule-based disease *detection* from NDVI / environmental signals
    (``disease_detection.py`` — returns ``DiseaseType`` enum values)
  * a bare-bones ``/api/v1/disease/types`` endpoint that dumps enum
    entries (category-level, not disease-level)

The archived crop-health-ai had something different: a curated dictionary
of *named* Yemeni crop diseases (e.g. ``wheat_leaf_rust``,
``date_palm_bayoud``) with specific treatment products, dosages,
precautions and preventive measures. That's the data this module ports
over so the old farmer-facing ``/v1/crops``, ``/v1/treatment/{id}`` and
diseases-catalog endpoints keep working against
crop-intelligence-service.

This is a pure data module — no persistence, no ML inference. If you're
looking for image-based or NDVI-based diagnosis, use
``disease_detection.py`` instead.
"""

from __future__ import annotations

from typing import Any

from .disease_detection import CropType, DiseaseSeverity

# ---------------------------------------------------------------------------
# Treatment + disease catalog (ported verbatim from crop-health-ai)
# ---------------------------------------------------------------------------
#
# Shape note: the archive's ``Treatment`` dataclass carried a human-readable
# ``frequency`` string rather than the ``urgency_days: int`` field that the
# rule-based detector in this service uses. Clients of the old endpoints
# expect the string form (e.g. "Every 14 days if infection persists"), so we
# store catalog entries as plain dicts rather than coercing them into the
# detector's Treatment dataclass. Diagnostic responses from
# ``/api/v1/diagnose`` etc. continue to use the typed Treatment class.

DISEASE_CATALOG: dict[str, dict[str, Any]] = {
    "wheat_leaf_rust": {
        "name": "Wheat Leaf Rust",
        "name_ar": "صدأ أوراق القمح",
        "description": "Fungal disease causing orange-brown pustules on leaves",
        "description_ar": "مرض فطري يسبب بثور برتقالية-بنية على الأوراق",
        "crop": CropType.WHEAT,
        "severity_default": DiseaseSeverity.MEDIUM,
        "treatments": [
            {
                "treatment_type": "fungicide",
                "product_name": "Propiconazole 25% EC",
                "product_name_ar": "بروبيكونازول 25%",
                "dosage": "0.5 L/hectare",
                "dosage_ar": "0.5 لتر/هكتار",
                "application_method": "Foliar spray",
                "application_method_ar": "رش ورقي",
                "frequency": "Every 14 days if infection persists",
                "frequency_ar": "كل 14 يوم إذا استمرت الإصابة",
                "precautions": ["Wear protective equipment", "Avoid spraying in wind"],
                "precautions_ar": ["ارتداء معدات الحماية", "تجنب الرش في الرياح"],
            }
        ],
        "prevention": ["Use resistant varieties", "Crop rotation", "Remove crop residues"],
        "prevention_ar": ["استخدام أصناف مقاومة", "الدورة الزراعية", "إزالة بقايا المحصول"],
    },
    "tomato_late_blight": {
        "name": "Tomato Late Blight",
        "name_ar": "اللفحة المتأخرة للطماطم",
        "description": "Devastating fungal disease causing dark lesions and rapid plant death",
        "description_ar": "مرض فطري مدمر يسبب آفات داكنة وموت سريع للنبات",
        "crop": CropType.TOMATO,
        "severity_default": DiseaseSeverity.HIGH,
        "treatments": [
            {
                "treatment_type": "fungicide",
                "product_name": "Copper Hydroxide",
                "product_name_ar": "هيدروكسيد النحاس",
                "dosage": "2-3 kg/hectare",
                "dosage_ar": "2-3 كجم/هكتار",
                "application_method": "Foliar spray before infection",
                "application_method_ar": "رش ورقي قبل الإصابة",
                "frequency": "Every 7-10 days during humid conditions",
                "frequency_ar": "كل 7-10 أيام في الظروف الرطبة",
                "precautions": ["Apply before rain", "Ensure complete coverage"],
                "precautions_ar": ["التطبيق قبل المطر", "ضمان التغطية الكاملة"],
            }
        ],
        "prevention": [
            "Avoid overhead irrigation",
            "Improve air circulation",
            "Plant resistant varieties",
        ],
        "prevention_ar": ["تجنب الري العلوي", "تحسين دوران الهواء", "زراعة أصناف مقاومة"],
    },
    "coffee_leaf_rust": {
        "name": "Coffee Leaf Rust",
        "name_ar": "صدأ أوراق البن",
        "description": "Major fungal disease affecting coffee plants, causing yellow-orange spots",
        "description_ar": "مرض فطري رئيسي يصيب نباتات البن، يسبب بقع صفراء-برتقالية",
        "crop": CropType.COFFEE,
        "severity_default": DiseaseSeverity.HIGH,
        "treatments": [
            {
                "treatment_type": "fungicide",
                "product_name": "Bordeaux Mixture",
                "product_name_ar": "خليط بوردو",
                "dosage": "1% solution",
                "dosage_ar": "محلول 1%",
                "application_method": "Spray on leaves",
                "application_method_ar": "رش على الأوراق",
                "frequency": "Monthly during rainy season",
                "frequency_ar": "شهرياً خلال موسم الأمطار",
                "precautions": ["Test on small area first"],
                "precautions_ar": ["اختبار على منطقة صغيرة أولاً"],
            }
        ],
        "prevention": ["Shade management", "Proper nutrition", "Resistant varieties"],
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
            {
                "treatment_type": "fungicide",
                "product_name": "Carbendazim",
                "product_name_ar": "كاربندازيم",
                "dosage": "Soil drench application",
                "dosage_ar": "تطبيق غمر التربة",
                "application_method": "Apply to soil around trunk",
                "application_method_ar": "تطبيق على التربة حول الجذع",
                "frequency": "At first signs of infection",
                "frequency_ar": "عند أول علامات الإصابة",
                "precautions": ["Remove and burn infected trees", "Quarantine affected area"],
                "precautions_ar": ["إزالة وحرق الأشجار المصابة", "عزل المنطقة المصابة"],
            }
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
            {
                "treatment_type": "fungicide",
                "product_name": "Mancozeb 75% WP",
                "product_name_ar": "مانكوزيب 75%",
                "dosage": "2.5 g/L water",
                "dosage_ar": "2.5 جم/لتر ماء",
                "application_method": "Spray during flowering and fruit set",
                "application_method_ar": "رش أثناء الإزهار وعقد الثمار",
                "frequency": "Every 15 days during humid season",
                "frequency_ar": "كل 15 يوم خلال الموسم الرطب",
                "precautions": ["Avoid application during hot midday"],
                "precautions_ar": ["تجنب التطبيق في منتصف النهار الحار"],
            }
        ],
        "prevention": ["Prune dead branches", "Good drainage", "Avoid wetting foliage"],
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
        "prevention": ["Continue good agricultural practices", "Regular monitoring"],
        "prevention_ar": ["استمرار الممارسات الزراعية الجيدة", "المراقبة المنتظمة"],
    },
}

# ---------------------------------------------------------------------------
# Supported crops metadata (archive's CROPS_INFO, kept as a CropType-keyed dict)
# ---------------------------------------------------------------------------

CROPS_INFO: dict[CropType, dict[str, str]] = {
    CropType.WHEAT: {"name_ar": "قمح", "icon": "🌾"},
    CropType.TOMATO: {"name_ar": "طماطم", "icon": "🍅"},
    CropType.POTATO: {"name_ar": "بطاطس", "icon": "🥔"},
    CropType.CORN: {"name_ar": "ذرة", "icon": "🌽"},
    CropType.GRAPE: {"name_ar": "عنب", "icon": "🍇"},
    CropType.COFFEE: {"name_ar": "بن", "icon": "☕"},
    CropType.DATE_PALM: {"name_ar": "نخيل", "icon": "🌴"},
    CropType.MANGO: {"name_ar": "مانجو", "icon": "🥭"},
    CropType.CITRUS: {"name_ar": "حمضيات", "icon": "🍊"},
    CropType.COTTON: {"name_ar": "قطن", "icon": "🌿"},
    CropType.SORGHUM: {"name_ar": "ذرة رفيعة", "icon": "🌾"},
}

# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def list_named_diseases(crop_type: CropType | None = None) -> list[dict[str, Any]]:
    """Return the curated named diseases (excluding ``healthy``).

    When ``crop_type`` is given, filter to diseases affecting that crop.
    """
    diseases: list[dict[str, Any]] = []
    for key, info in DISEASE_CATALOG.items():
        if key == "healthy":
            continue
        if crop_type and info.get("crop") != crop_type:
            continue
        diseases.append(
            {
                "disease_id": key,
                "name": info["name"],
                "name_ar": info["name_ar"],
                "crop": info["crop"].value,
                "severity": info["severity_default"].value,
            }
        )
    return diseases


def get_treatment_details(disease_id: str) -> dict[str, Any] | None:
    """Return the full treatment + prevention record for one named disease."""
    disease = DISEASE_CATALOG.get(disease_id)
    if not disease:
        return None
    return {
        "disease_id": disease_id,
        "disease_name": disease["name"],
        "disease_name_ar": disease["name_ar"],
        "treatments": disease.get("treatments", []),
        "prevention": disease.get("prevention", []),
        "prevention_ar": disease.get("prevention_ar", []),
        "severity": disease["severity_default"].value,
    }


def list_supported_crops() -> list[dict[str, Any]]:
    """Return supported crops with Arabic labels and per-crop disease counts."""
    return [
        {
            "crop_id": crop.value,
            "name": crop.value.replace("_", " ").title(),
            "name_ar": info["name_ar"],
            "icon": info["icon"],
            "diseases_count": sum(
                1 for d in DISEASE_CATALOG.values() if d.get("crop") == crop and d is not DISEASE_CATALOG["healthy"]
            ),
        }
        for crop, info in CROPS_INFO.items()
    ]
