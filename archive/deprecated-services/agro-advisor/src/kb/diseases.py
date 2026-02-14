"""
Disease Knowledge Base - SAHOOL Agro Advisor
Structured disease database for Yemen agricultural context
"""

DISEASES = {
    # === TOMATO DISEASES ===
    "tomato_late_blight": {
        "name_ar": "اللفحة المتأخرة",
        "name_en": "Late Blight",
        "crop": "tomato",
        "pathogen": "Phytophthora infestans",
        "symptoms_ar": [
            "بقع مائية على الأوراق",
            "بقع بنية داكنة",
            "عفن أبيض على السطح السفلي",
            "تعفن الثمار",
        ],
        "symptoms_en": [
            "Water-soaked lesions on leaves",
            "Dark brown spots",
            "White mold on leaf undersides",
            "Fruit rot",
        ],
        "conditions": {
            "humidity_min": 80,
            "temp_range": [15, 25],
            "spread": "rain_splash",
        },
        "actions": [
            "spray_copper",
            "spray_mancozeb",
            "remove_infected_parts",
            "avoid_overhead_irrigation",
            "improve_air_circulation",
        ],
        "severity_default": "high",
        "urgency_hours": 24,
    },
    "tomato_early_blight": {
        "name_ar": "اللفحة المبكرة",
        "name_en": "Early Blight",
        "crop": "tomato",
        "pathogen": "Alternaria solani",
        "symptoms_ar": [
            "بقع بنية دائرية مع حلقات متحدة المركز",
            "اصفرار الأوراق",
            "تساقط الأوراق السفلية",
        ],
        "symptoms_en": [
            "Brown circular spots with concentric rings",
            "Leaf yellowing",
            "Lower leaf drop",
        ],
        "conditions": {
            "humidity_min": 60,
            "temp_range": [24, 29],
            "spread": "wind_rain",
        },
        "actions": [
            "spray_chlorothalonil",
            "remove_lower_leaves",
            "mulching",
            "crop_rotation",
        ],
        "severity_default": "medium",
        "urgency_hours": 48,
    },
    "tomato_powdery_mildew": {
        "name_ar": "البياض الدقيقي",
        "name_en": "Powdery Mildew",
        "crop": "tomato",
        "pathogen": "Oidium neolycopersici",
        "symptoms_ar": ["بقع بيضاء دقيقية على الأوراق", "تجعد الأوراق", "ضعف النمو"],
        "symptoms_en": [
            "White powdery spots on leaves",
            "Leaf curling",
            "Stunted growth",
        ],
        "conditions": {"humidity_min": 50, "temp_range": [20, 30], "spread": "wind"},
        "actions": [
            "spray_sulfur",
            "spray_potassium_bicarbonate",
            "improve_ventilation",
        ],
        "severity_default": "medium",
        "urgency_hours": 72,
    },
    # === WHEAT DISEASES ===
    "wheat_rust": {
        "name_ar": "صدأ القمح",
        "name_en": "Wheat Rust",
        "crop": "wheat",
        "pathogen": "Puccinia spp.",
        "symptoms_ar": [
            "بثرات برتقالية أو بنية على الأوراق",
            "اصفرار الأوراق",
            "ضعف الحبوب",
        ],
        "symptoms_en": [
            "Orange or brown pustules on leaves",
            "Leaf yellowing",
            "Poor grain fill",
        ],
        "conditions": {"humidity_min": 70, "temp_range": [15, 25], "spread": "wind"},
        "actions": [
            "spray_propiconazole",
            "spray_tebuconazole",
            "use_resistant_varieties",
        ],
        "severity_default": "high",
        "urgency_hours": 24,
    },
    # === POTATO DISEASES ===
    "potato_late_blight": {
        "name_ar": "اللفحة المتأخرة للبطاطس",
        "name_en": "Potato Late Blight",
        "crop": "potato",
        "pathogen": "Phytophthora infestans",
        "symptoms_ar": ["بقع مائية داكنة على الأوراق", "عفن الدرنات", "رائحة كريهة"],
        "symptoms_en": ["Dark water-soaked leaf spots", "Tuber rot", "Foul smell"],
        "conditions": {
            "humidity_min": 80,
            "temp_range": [12, 22],
            "spread": "rain_splash",
        },
        "actions": [
            "spray_copper",
            "spray_mancozeb",
            "destroy_infected_plants",
            "improve_drainage",
        ],
        "severity_default": "high",
        "urgency_hours": 24,
    },
    # === GENERAL PESTS ===
    "aphid_infestation": {
        "name_ar": "إصابة المن",
        "name_en": "Aphid Infestation",
        "crop": "general",
        "pathogen": "Aphidoidea",
        "symptoms_ar": [
            "حشرات صغيرة خضراء أو سوداء",
            "تجعد الأوراق",
            "إفرازات لزجة (الندوة العسلية)",
            "نمو فطري أسود",
        ],
        "symptoms_en": [
            "Small green or black insects",
            "Leaf curling",
            "Sticky secretions (honeydew)",
            "Black sooty mold",
        ],
        "conditions": {"humidity_min": 40, "temp_range": [18, 28], "spread": "flight"},
        "actions": [
            "spray_neem_oil",
            "spray_insecticidal_soap",
            "introduce_ladybugs",
            "remove_heavily_infested_parts",
        ],
        "severity_default": "medium",
        "urgency_hours": 48,
    },
    "whitefly_infestation": {
        "name_ar": "إصابة الذبابة البيضاء",
        "name_en": "Whitefly Infestation",
        "crop": "general",
        "pathogen": "Bemisia tabaci",
        "symptoms_ar": [
            "حشرات بيضاء صغيرة طائرة",
            "اصفرار الأوراق",
            "ندوة عسلية",
            "انتقال الفيروسات",
        ],
        "symptoms_en": [
            "Small white flying insects",
            "Leaf yellowing",
            "Honeydew",
            "Virus transmission",
        ],
        "conditions": {"humidity_min": 50, "temp_range": [20, 35], "spread": "flight"},
        "actions": [
            "use_yellow_sticky_traps",
            "spray_neem_oil",
            "spray_pyriproxyfen",
            "remove_weeds",
        ],
        "severity_default": "high",
        "urgency_hours": 24,
    },
}


def get_disease(disease_id: str) -> dict | None:
    """Get disease by ID"""
    return DISEASES.get(disease_id)


def get_diseases_by_crop(crop: str) -> list[dict]:
    """Get all diseases for a specific crop"""
    return [
        {"id": k, **v} for k, v in DISEASES.items() if v["crop"] == crop or v["crop"] == "general"
    ]


def search_diseases(query: str, lang: str = "ar") -> list[dict]:
    """Search diseases by name or symptoms"""
    results = []
    query_lower = query.lower()

    for disease_id, disease in DISEASES.items():
        name_field = "name_ar" if lang == "ar" else "name_en"
        symptoms_field = "symptoms_ar" if lang == "ar" else "symptoms_en"

        if query_lower in disease[name_field].lower():
            results.append({"id": disease_id, **disease, "match": "name"})
        elif any(query_lower in s.lower() for s in disease[symptoms_field]):
            results.append({"id": disease_id, **disease, "match": "symptom"})

    return results
