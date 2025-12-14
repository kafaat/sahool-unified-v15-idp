"""
Nutrient Deficiency Knowledge Base - SAHOOL Agro Advisor
NPK and micronutrient deficiency identification
"""

NUTRIENT_DEFICIENCIES = {
    # === MACRONUTRIENTS ===
    "nitrogen_deficiency": {
        "nutrient": "N",
        "name_ar": "نقص النيتروجين",
        "name_en": "Nitrogen Deficiency",
        "symptoms_ar": [
            "اصفرار الأوراق السفلية",
            "تقزم النبات",
            "ضعف النمو الخضري",
            "شحوب عام في اللون"
        ],
        "symptoms_en": [
            "Yellowing of lower leaves",
            "Stunted growth",
            "Poor vegetative growth",
            "Overall pale color"
        ],
        "visual_indicators": {
            "leaf_color": "pale_yellow",
            "pattern": "uniform_chlorosis",
            "location": "older_leaves_first",
            "ndvi_impact": "severe_decrease"
        },
        "causes": [
            "poor_soil_fertility",
            "leaching_from_rain",
            "insufficient_fertilization",
            "poor_root_development"
        ],
        "corrections": [
            {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50},
            {"type": "fertilizer", "product": "ammonium_sulfate", "dose_kg_ha": 75},
            {"type": "fertilizer", "product": "npk_balanced", "dose_kg_ha": 100},
            {"type": "practice", "action": "foliar_spray_urea_2pct"}
        ],
        "severity_default": "high",
        "urgency_hours": 48,
    },

    "phosphorus_deficiency": {
        "nutrient": "P",
        "name_ar": "نقص الفوسفور",
        "name_en": "Phosphorus Deficiency",
        "symptoms_ar": [
            "تلون الأوراق باللون الأرجواني",
            "تأخر النضج",
            "ضعف نمو الجذور",
            "صغر حجم الأوراق"
        ],
        "symptoms_en": [
            "Purple coloration of leaves",
            "Delayed maturity",
            "Poor root development",
            "Small leaf size"
        ],
        "visual_indicators": {
            "leaf_color": "purple_bronze",
            "pattern": "purple_veins_undersides",
            "location": "older_leaves_first",
            "ndvi_impact": "moderate_decrease"
        },
        "causes": [
            "low_soil_ph",
            "cold_soil_temperatures",
            "poor_soil_aeration",
            "phosphorus_fixation"
        ],
        "corrections": [
            {"type": "fertilizer", "product": "tsp", "dose_kg_ha": 50},
            {"type": "fertilizer", "product": "dap", "dose_kg_ha": 75},
            {"type": "fertilizer", "product": "npk_high_p", "dose_kg_ha": 100},
            {"type": "practice", "action": "check_soil_ph"}
        ],
        "severity_default": "medium",
        "urgency_hours": 72,
    },

    "potassium_deficiency": {
        "nutrient": "K",
        "name_ar": "نقص البوتاسيوم",
        "name_en": "Potassium Deficiency",
        "symptoms_ar": [
            "احتراق حواف الأوراق",
            "تجعد الأوراق",
            "ضعف مقاومة الأمراض",
            "صغر حجم الثمار"
        ],
        "symptoms_en": [
            "Leaf edge scorching",
            "Leaf curling",
            "Poor disease resistance",
            "Small fruit size"
        ],
        "visual_indicators": {
            "leaf_color": "brown_edges",
            "pattern": "marginal_necrosis",
            "location": "older_leaves_first",
            "ndvi_impact": "moderate_decrease"
        },
        "causes": [
            "sandy_soil",
            "heavy_leaching",
            "high_nitrogen_application",
            "calcium_magnesium_excess"
        ],
        "corrections": [
            {"type": "fertilizer", "product": "potassium_sulfate", "dose_kg_ha": 50},
            {"type": "fertilizer", "product": "potassium_chloride", "dose_kg_ha": 60},
            {"type": "fertilizer", "product": "npk_high_k", "dose_kg_ha": 100},
            {"type": "practice", "action": "foliar_spray_kno3"}
        ],
        "severity_default": "medium",
        "urgency_hours": 72,
    },

    # === SECONDARY NUTRIENTS ===
    "calcium_deficiency": {
        "nutrient": "Ca",
        "name_ar": "نقص الكالسيوم",
        "name_en": "Calcium Deficiency",
        "symptoms_ar": [
            "تعفن الطرف الزهري (الطماطم)",
            "تشوه الأوراق الجديدة",
            "ضعف الجدار الخلوي",
            "تقزم القمم النامية"
        ],
        "symptoms_en": [
            "Blossom end rot (tomato)",
            "Distorted new leaves",
            "Weak cell walls",
            "Stunted growing tips"
        ],
        "visual_indicators": {
            "leaf_color": "distorted_tips",
            "pattern": "tip_burn",
            "location": "new_leaves_first",
            "ndvi_impact": "localized_decrease"
        },
        "causes": [
            "acidic_soil",
            "irregular_watering",
            "high_ammonium_nitrogen",
            "root_damage"
        ],
        "corrections": [
            {"type": "fertilizer", "product": "calcium_nitrate", "dose_kg_ha": 50},
            {"type": "fertilizer", "product": "gypsum", "dose_kg_ha": 200},
            {"type": "practice", "action": "regular_irrigation"},
            {"type": "practice", "action": "foliar_calcium_spray"}
        ],
        "severity_default": "high",
        "urgency_hours": 24,
    },

    "magnesium_deficiency": {
        "nutrient": "Mg",
        "name_ar": "نقص المغنيسيوم",
        "name_en": "Magnesium Deficiency",
        "symptoms_ar": [
            "اصفرار بين العروق",
            "الأوراق السفلية تتأثر أولاً",
            "احمرار أو بنفسجي",
            "تساقط الأوراق المبكر"
        ],
        "symptoms_en": [
            "Interveinal chlorosis",
            "Lower leaves affected first",
            "Reddish or purple tint",
            "Premature leaf drop"
        ],
        "visual_indicators": {
            "leaf_color": "interveinal_yellow",
            "pattern": "green_veins_yellow_between",
            "location": "older_leaves_first",
            "ndvi_impact": "gradual_decrease"
        },
        "causes": [
            "sandy_soil",
            "acidic_conditions",
            "excess_potassium",
            "heavy_leaching"
        ],
        "corrections": [
            {"type": "fertilizer", "product": "magnesium_sulfate", "dose_kg_ha": 25},
            {"type": "fertilizer", "product": "dolomite_lime", "dose_kg_ha": 500},
            {"type": "practice", "action": "foliar_epsom_salt"}
        ],
        "severity_default": "medium",
        "urgency_hours": 72,
    },

    # === MICRONUTRIENTS ===
    "iron_deficiency": {
        "nutrient": "Fe",
        "name_ar": "نقص الحديد",
        "name_en": "Iron Deficiency",
        "symptoms_ar": [
            "اصفرار الأوراق الجديدة مع بقاء العروق خضراء",
            "شحوب النموات الحديثة",
            "ضعف النمو"
        ],
        "symptoms_en": [
            "New leaf yellowing with green veins",
            "Pale new growth",
            "Weak growth"
        ],
        "visual_indicators": {
            "leaf_color": "pale_new_leaves",
            "pattern": "interveinal_chlorosis_new",
            "location": "new_leaves_first",
            "ndvi_impact": "localized_decrease"
        },
        "causes": [
            "high_soil_ph",
            "waterlogged_soil",
            "excess_phosphorus",
            "calcareous_soil"
        ],
        "corrections": [
            {"type": "fertilizer", "product": "iron_sulfate", "dose_kg_ha": 10},
            {"type": "fertilizer", "product": "iron_chelate", "dose_kg_ha": 5},
            {"type": "practice", "action": "acidify_soil"},
            {"type": "practice", "action": "foliar_iron_spray"}
        ],
        "severity_default": "medium",
        "urgency_hours": 72,
    },

    "zinc_deficiency": {
        "nutrient": "Zn",
        "name_ar": "نقص الزنك",
        "name_en": "Zinc Deficiency",
        "symptoms_ar": [
            "صغر حجم الأوراق",
            "تقارب العقد",
            "اصفرار بين العروق",
            "تأخر النضج"
        ],
        "symptoms_en": [
            "Small leaf size",
            "Short internodes",
            "Interveinal chlorosis",
            "Delayed maturity"
        ],
        "visual_indicators": {
            "leaf_color": "mottled_yellow",
            "pattern": "small_clustered_leaves",
            "location": "new_growth",
            "ndvi_impact": "moderate_decrease"
        },
        "causes": [
            "high_soil_ph",
            "high_phosphorus",
            "sandy_soil",
            "organic_matter_deficiency"
        ],
        "corrections": [
            {"type": "fertilizer", "product": "zinc_sulfate", "dose_kg_ha": 10},
            {"type": "fertilizer", "product": "zinc_chelate", "dose_kg_ha": 3},
            {"type": "practice", "action": "foliar_zinc_spray"}
        ],
        "severity_default": "medium",
        "urgency_hours": 72,
    },
}


def get_deficiency(deficiency_id: str) -> dict | None:
    """Get nutrient deficiency by ID"""
    return NUTRIENT_DEFICIENCIES.get(deficiency_id)


def get_deficiency_by_nutrient(nutrient: str) -> dict | None:
    """Get deficiency info by nutrient symbol (N, P, K, etc.)"""
    for def_id, deficiency in NUTRIENT_DEFICIENCIES.items():
        if deficiency["nutrient"] == nutrient:
            return {"id": def_id, **deficiency}
    return None


def diagnose_from_ndvi(ndvi: float, ndvi_history: list[float] = None) -> list[dict]:
    """
    Diagnose potential nutrient issues from NDVI readings
    Returns list of possible deficiencies ordered by likelihood
    """
    diagnoses = []

    if ndvi < 0.3:
        # Severe stress - likely nitrogen
        diagnoses.append({
            "id": "nitrogen_deficiency",
            "confidence": 0.7,
            "reason": "severe_ndvi_drop"
        })
    elif ndvi < 0.5:
        # Moderate stress - could be multiple
        diagnoses.extend([
            {"id": "nitrogen_deficiency", "confidence": 0.5, "reason": "moderate_ndvi"},
            {"id": "potassium_deficiency", "confidence": 0.3, "reason": "moderate_ndvi"},
        ])

    # Check for declining trend
    if ndvi_history and len(ndvi_history) >= 3:
        trend = ndvi_history[-1] - ndvi_history[0]
        if trend < -0.1:
            diagnoses.append({
                "id": "phosphorus_deficiency",
                "confidence": 0.4,
                "reason": "declining_ndvi_trend"
            })

    return diagnoses
