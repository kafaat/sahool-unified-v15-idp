"""
Agricultural Encyclopedia — الموسوعة الزراعية
Provides crop-specific knowledge from SAHOOL knowledge base.
Phase 4 of Component Unification Plan (PR #1344)
"""

import structlog
from fastapi import APIRouter, Query

logger = structlog.get_logger()
router = APIRouter(prefix="/encyclopedia", tags=["encyclopedia"])

# Crop knowledge database (bilingual)
CROP_KNOWLEDGE = {
    "wheat": {
        "name": "Wheat",
        "name_ar": "القمح",
        "family": "Poaceae",
        "family_ar": "النجيليات",
        "growth_stages": [
            "Germination",
            "Tillering",
            "Stem elongation",
            "Heading",
            "Flowering",
            "Grain filling",
            "Maturity",
        ],
        "growth_stages_ar": ["الإنبات", "التفريع", "استطالة الساق", "طرد السنابل", "الإزهار", "امتلاء الحبوب", "النضج"],
        "water_need_mm": {"min": 450, "max": 650},
        "optimal_temp": {"min": 15, "max": 25},
        "soil_ph": {"min": 6.0, "max": 7.5},
        "common_diseases": [
            {"name": "Leaf Rust", "name_ar": "صدأ الأوراق", "ndvi_indicator": "drop > 0.15 in 10 days"},
            {"name": "Powdery Mildew", "name_ar": "البياض الدقيقي", "ndvi_indicator": "gradual decline"},
        ],
        "common_pests": [
            {"name": "Aphids", "name_ar": "المن", "threshold": "10 per tiller"},
            {"name": "Hessian Fly", "name_ar": "ذبابة هسيان", "threshold": "1 per 10 plants"},
        ],
        "fertilizer_guide": {
            "nitrogen": {"base_kg_ha": 120, "split": ["1/3 at sowing", "1/3 at tillering", "1/3 at heading"]},
            "phosphorus": {"base_kg_ha": 60, "timing": "all at sowing"},
            "potassium": {"base_kg_ha": 40, "timing": "all at sowing"},
        },
        "yemen_notes": "يُزرع في المرتفعات (1500-2500م). الموسم: أكتوبر-مايو. أصناف محلية: صنعاني، حيمي.",
    },
    "date_palm": {
        "name": "Date Palm",
        "name_ar": "النخيل",
        "family": "Arecaceae",
        "family_ar": "النخيليات",
        "growth_stages": ["Dormancy", "Spathe emergence", "Pollination", "Fruit set", "Khalal", "Rutab", "Tamar"],
        "growth_stages_ar": ["السكون", "ظهور الطلع", "التلقيح", "العقد", "الخلال", "الرطب", "التمر"],
        "water_need_mm": {"min": 1200, "max": 1800},
        "optimal_temp": {"min": 25, "max": 45},
        "soil_ph": {"min": 7.0, "max": 8.5},
        "common_pests": [
            {"name": "Red Palm Weevil", "name_ar": "سوسة النخيل الحمراء", "threshold": "CRITICAL - immediate action"},
            {"name": "Dubas Bug", "name_ar": "حشرة الدوباس", "threshold": "5 per frond"},
        ],
        "yemen_notes": "أكثر من 30 صنف يمني. حضرموت وشبوة أهم المناطق. الحصاد: يوليو-أكتوبر.",
    },
    "tomato": {
        "name": "Tomato",
        "name_ar": "الطماطم",
        "family": "Solanaceae",
        "family_ar": "الباذنجانيات",
        "growth_stages": ["Seedling", "Vegetative", "Flowering", "Fruit set", "Ripening", "Harvest"],
        "growth_stages_ar": ["شتلة", "نمو خضري", "إزهار", "عقد الثمار", "النضج", "الحصاد"],
        "water_need_mm": {"min": 400, "max": 800},
        "optimal_temp": {"min": 20, "max": 30},
        "soil_ph": {"min": 6.0, "max": 7.0},
        "common_diseases": [
            {"name": "Early Blight", "name_ar": "اللفحة المبكرة", "ndvi_indicator": "localized drops"},
            {
                "name": "Tomato Yellow Leaf Curl",
                "name_ar": "تجعد أوراق الطماطم",
                "ndvi_indicator": "severe NDVI decline",
            },
        ],
        "yemen_notes": "تُزرع في تهامة والمرتفعات. موسمان: شتوي وصيفي.",
    },
    "barley": {
        "name": "Barley",
        "name_ar": "الشعير",
        "family": "Poaceae",
        "family_ar": "النجيليات",
        "growth_stages": ["Germination", "Tillering", "Stem elongation", "Heading", "Ripening"],
        "growth_stages_ar": ["الإنبات", "التفريع", "استطالة الساق", "طرد السنابل", "النضج"],
        "water_need_mm": {"min": 300, "max": 500},
        "optimal_temp": {"min": 12, "max": 22},
        "soil_ph": {"min": 6.0, "max": 8.0},
        "yemen_notes": "أكثر تحملاً للجفاف من القمح. يُزرع في المناطق الجافة والهامشية.",
    },
}


@router.get("/search")
async def search_encyclopedia(q: str = Query(..., min_length=2), lang: str = Query("ar", regex="^(ar|en)$")):
    results = []
    q_lower = q.lower()
    for crop_type, data in CROP_KNOWLEDGE.items():
        name = data["name_ar"] if lang == "ar" else data["name"]
        if q_lower in name.lower() or q_lower in crop_type:
            results.append({"crop_type": crop_type, "name": name, "name_ar": data["name_ar"], "name_en": data["name"]})
            continue
        # Search in diseases
        for d in data.get("common_diseases", []):
            if q_lower in d.get("name", "").lower() or q_lower in d.get("name_ar", ""):
                results.append(
                    {
                        "crop_type": crop_type,
                        "match_type": "disease",
                        "match": d["name_ar"] if lang == "ar" else d["name"],
                    }
                )
        # Search in pests
        for p in data.get("common_pests", []):
            if q_lower in p.get("name", "").lower() or q_lower in p.get("name_ar", ""):
                results.append(
                    {"crop_type": crop_type, "match_type": "pest", "match": p["name_ar"] if lang == "ar" else p["name"]}
                )
    return {"query": q, "language": lang, "results": results, "count": len(results)}


@router.get("/{crop_type}")
async def get_crop_encyclopedia(crop_type: str):
    crop = CROP_KNOWLEDGE.get(crop_type.lower())
    if not crop:
        available = list(CROP_KNOWLEDGE.keys())
        return {
            "error": f"Crop '{crop_type}' not found",
            "error_ar": f"المحصول '{crop_type}' غير موجود",
            "available_crops": available,
        }
    return {"crop": crop_type, "data": crop}


@router.get("/")
async def list_crops():
    crops = [
        {"crop_type": k, "name": v["name"], "name_ar": v["name_ar"], "family_ar": v["family_ar"]}
        for k, v in CROP_KNOWLEDGE.items()
    ]
    return {"crops": crops, "count": len(crops)}
