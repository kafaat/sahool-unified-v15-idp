"""
Fertilizer Knowledge Base - SAHOOL Agro Advisor
Fertilizer products and application guidelines for Yemen
"""

FERTILIZERS = {
    # === NITROGEN FERTILIZERS ===
    "urea": {
        "name_ar": "يوريا",
        "name_en": "Urea",
        "formula": "CO(NH2)2",
        "analysis": {"N": 46, "P": 0, "K": 0},
        "type": "nitrogen",
        "form": "granular",
        "solubility": "high",
        "application_methods": ["broadcast", "side_dress", "foliar"],
        "precautions_ar": ["لا تخلط مع الجير", "تطبيق قبل الري"],
        "precautions_en": ["Do not mix with lime", "Apply before irrigation"],
        "price_tier": "low",
    },
    "ammonium_sulfate": {
        "name_ar": "سلفات الأمونيوم",
        "name_en": "Ammonium Sulfate",
        "formula": "(NH4)2SO4",
        "analysis": {"N": 21, "P": 0, "K": 0, "S": 24},
        "type": "nitrogen",
        "form": "crystalline",
        "solubility": "high",
        "application_methods": ["broadcast", "side_dress"],
        "precautions_ar": ["حمضي - يخفض pH التربة"],
        "precautions_en": ["Acidic - lowers soil pH"],
        "price_tier": "low",
    },
    "calcium_nitrate": {
        "name_ar": "نترات الكالسيوم",
        "name_en": "Calcium Nitrate",
        "formula": "Ca(NO3)2",
        "analysis": {"N": 15.5, "P": 0, "K": 0, "Ca": 19},
        "type": "nitrogen_calcium",
        "form": "granular",
        "solubility": "high",
        "application_methods": ["fertigation", "foliar", "side_dress"],
        "precautions_ar": ["يمتص الرطوبة - يخزن جاف"],
        "precautions_en": ["Hygroscopic - store dry"],
        "price_tier": "medium",
    },
    # === PHOSPHORUS FERTILIZERS ===
    "tsp": {
        "name_ar": "سوبر فوسفات ثلاثي",
        "name_en": "Triple Super Phosphate (TSP)",
        "formula": "Ca(H2PO4)2",
        "analysis": {"N": 0, "P": 46, "K": 0},
        "type": "phosphorus",
        "form": "granular",
        "solubility": "medium",
        "application_methods": ["broadcast", "banding"],
        "precautions_ar": ["تطبيق قبل الزراعة"],
        "precautions_en": ["Apply before planting"],
        "price_tier": "medium",
    },
    "dap": {
        "name_ar": "داي أمونيوم فوسفات",
        "name_en": "Di-Ammonium Phosphate (DAP)",
        "formula": "(NH4)2HPO4",
        "analysis": {"N": 18, "P": 46, "K": 0},
        "type": "nitrogen_phosphorus",
        "form": "granular",
        "solubility": "high",
        "application_methods": ["broadcast", "banding", "starter"],
        "precautions_ar": ["لا تضع قريب من البذور"],
        "precautions_en": ["Do not place near seeds"],
        "price_tier": "medium",
    },
    # === POTASSIUM FERTILIZERS ===
    "potassium_sulfate": {
        "name_ar": "سلفات البوتاسيوم",
        "name_en": "Potassium Sulfate (SOP)",
        "formula": "K2SO4",
        "analysis": {"N": 0, "P": 0, "K": 50, "S": 18},
        "type": "potassium",
        "form": "granular",
        "solubility": "medium",
        "application_methods": ["broadcast", "side_dress", "fertigation"],
        "precautions_ar": ["مناسب للمحاصيل الحساسة للكلور"],
        "precautions_en": ["Suitable for chloride-sensitive crops"],
        "price_tier": "high",
    },
    "potassium_chloride": {
        "name_ar": "كلوريد البوتاسيوم",
        "name_en": "Potassium Chloride (MOP)",
        "formula": "KCl",
        "analysis": {"N": 0, "P": 0, "K": 60},
        "type": "potassium",
        "form": "granular",
        "solubility": "high",
        "application_methods": ["broadcast", "banding"],
        "precautions_ar": ["تجنب للطماطم والخضار"],
        "precautions_en": ["Avoid for tomatoes and vegetables"],
        "price_tier": "low",
    },
    # === NPK COMPOUND ===
    "npk_20_20_20": {
        "name_ar": "NPK متوازن",
        "name_en": "NPK 20-20-20 Balanced",
        "formula": "Compound",
        "analysis": {"N": 20, "P": 20, "K": 20},
        "type": "compound",
        "form": "soluble",
        "solubility": "high",
        "application_methods": ["fertigation", "foliar"],
        "precautions_ar": ["للري بالتنقيط"],
        "precautions_en": ["For drip irrigation"],
        "price_tier": "high",
    },
    "npk_15_15_15": {
        "name_ar": "NPK 15-15-15",
        "name_en": "NPK 15-15-15",
        "formula": "Compound",
        "analysis": {"N": 15, "P": 15, "K": 15},
        "type": "compound",
        "form": "granular",
        "solubility": "medium",
        "application_methods": ["broadcast", "banding"],
        "precautions_ar": ["سماد عام متعدد الاستخدام"],
        "precautions_en": ["General purpose fertilizer"],
        "price_tier": "medium",
    },
    "npk_12_12_36": {
        "name_ar": "NPK عالي البوتاسيوم",
        "name_en": "NPK 12-12-36 High-K",
        "formula": "Compound",
        "analysis": {"N": 12, "P": 12, "K": 36},
        "type": "compound",
        "form": "soluble",
        "solubility": "high",
        "application_methods": ["fertigation", "foliar"],
        "precautions_ar": ["لمرحلة الإثمار"],
        "precautions_en": ["For fruiting stage"],
        "price_tier": "high",
    },
    # === MICRONUTRIENTS ===
    "iron_chelate": {
        "name_ar": "حديد مخلبي",
        "name_en": "Iron Chelate (EDDHA)",
        "formula": "Fe-EDDHA",
        "analysis": {"Fe": 6},
        "type": "micronutrient",
        "form": "granular",
        "solubility": "high",
        "application_methods": ["soil_drench", "fertigation"],
        "precautions_ar": ["للتربة القلوية"],
        "precautions_en": ["For alkaline soils"],
        "price_tier": "high",
    },
    "zinc_sulfate": {
        "name_ar": "سلفات الزنك",
        "name_en": "Zinc Sulfate",
        "formula": "ZnSO4",
        "analysis": {"Zn": 23, "S": 11},
        "type": "micronutrient",
        "form": "crystalline",
        "solubility": "high",
        "application_methods": ["foliar", "soil"],
        "precautions_ar": ["رش ورقي 0.5%"],
        "precautions_en": ["Foliar spray 0.5%"],
        "price_tier": "low",
    },
    "magnesium_sulfate": {
        "name_ar": "سلفات المغنيسيوم (ملح إبسوم)",
        "name_en": "Magnesium Sulfate (Epsom Salt)",
        "formula": "MgSO4",
        "analysis": {"Mg": 10, "S": 13},
        "type": "secondary",
        "form": "crystalline",
        "solubility": "high",
        "application_methods": ["foliar", "fertigation"],
        "precautions_ar": ["رش ورقي 2%"],
        "precautions_en": ["Foliar spray 2%"],
        "price_tier": "low",
    },
    # === ORGANIC ===
    "compost": {
        "name_ar": "كمبوست",
        "name_en": "Compost",
        "formula": "Organic",
        "analysis": {"N": 1.5, "P": 1, "K": 1, "OM": 30},
        "type": "organic",
        "form": "bulk",
        "solubility": "na",
        "application_methods": ["broadcast", "incorporate"],
        "precautions_ar": ["يحسن بنية التربة"],
        "precautions_en": ["Improves soil structure"],
        "price_tier": "low",
    },
}


def get_fertilizer(fertilizer_id: str) -> dict | None:
    """Get fertilizer by ID"""
    return FERTILIZERS.get(fertilizer_id)


def get_fertilizers_by_type(fert_type: str) -> list[dict]:
    """Get all fertilizers of a specific type"""
    return [{"id": k, **v} for k, v in FERTILIZERS.items() if v["type"] == fert_type]


def get_fertilizers_for_nutrient(nutrient: str) -> list[dict]:
    """Get fertilizers that provide a specific nutrient"""
    results = []
    for fert_id, fert in FERTILIZERS.items():
        if nutrient in fert["analysis"] and fert["analysis"][nutrient] > 0:
            results.append(
                {"id": fert_id, **fert, "nutrient_content": fert["analysis"][nutrient]}
            )
    # Sort by nutrient content descending
    return sorted(results, key=lambda x: x["nutrient_content"], reverse=True)


def calculate_dose(
    fertilizer_id: str, nutrient: str, target_kg_ha: float
) -> float | None:
    """
    Calculate fertilizer dose needed to supply target kg/ha of nutrient
    Returns kg/ha of fertilizer needed
    """
    fert = FERTILIZERS.get(fertilizer_id)
    if not fert or nutrient not in fert["analysis"]:
        return None

    nutrient_pct = fert["analysis"][nutrient]
    if nutrient_pct == 0:
        return None

    return (target_kg_ha / nutrient_pct) * 100
