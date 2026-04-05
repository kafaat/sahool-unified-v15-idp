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
    # === NPK SPECIALIZED ===
    "npk_balanced": {
        "name_ar": "NPK متوازن عام",
        "name_en": "NPK Balanced (General Purpose)",
        "formula": "Compound",
        "analysis": {"N": 16, "P": 16, "K": 16},
        "type": "compound",
        "form": "granular",
        "solubility": "medium",
        "application_methods": ["broadcast", "banding", "fertigation"],
        "precautions_ar": ["سماد متوازن للاستخدام العام"],
        "precautions_en": ["Balanced fertilizer for general use"],
        "price_tier": "medium",
    },
    "npk_high_p": {
        "name_ar": "NPK عالي الفسفور",
        "name_en": "NPK High-P (10-30-10)",
        "formula": "Compound",
        "analysis": {"N": 10, "P": 30, "K": 10},
        "type": "compound",
        "form": "granular",
        "solubility": "medium",
        "application_methods": ["banding", "starter", "broadcast"],
        "precautions_ar": ["مناسب لمرحلة التأسيس والجذور"],
        "precautions_en": ["Suitable for establishment and root development"],
        "price_tier": "medium",
    },
    "npk_high_k": {
        "name_ar": "NPK عالي البوتاسيوم",
        "name_en": "NPK High-K (10-10-30)",
        "formula": "Compound",
        "analysis": {"N": 10, "P": 10, "K": 30},
        "type": "compound",
        "form": "soluble",
        "solubility": "high",
        "application_methods": ["fertigation", "foliar"],
        "precautions_ar": ["لمراحل الإثمار والنضج"],
        "precautions_en": ["For fruiting and ripening stages"],
        "price_tier": "high",
    },
    # === SOIL AMENDMENTS ===
    "gypsum": {
        "name_ar": "جبس زراعي",
        "name_en": "Agricultural Gypsum",
        "formula": "CaSO4·2H2O",
        "analysis": {"Ca": 23, "S": 19},
        "type": "amendment",
        "form": "powder",
        "solubility": "low",
        "application_methods": ["broadcast", "incorporate"],
        "precautions_ar": ["يُحسن التربة الملحية والصودية", "خلط مع التربة قبل الري"],
        "precautions_en": ["Improves saline-sodic soils", "Incorporate into soil before irrigation"],
        "price_tier": "low",
    },
    "dolomite_lime": {
        "name_ar": "دولوميت (جير دولوميتي)",
        "name_en": "Dolomite Lime",
        "formula": "CaMg(CO3)2",
        "analysis": {"Ca": 22, "Mg": 12},
        "type": "amendment",
        "form": "powder",
        "solubility": "low",
        "application_methods": ["broadcast", "incorporate"],
        "precautions_ar": ["يرفع pH التربة الحامضية", "يُضاف قبل الزراعة بأسبوعين"],
        "precautions_en": ["Raises pH of acidic soils", "Apply 2 weeks before planting"],
        "price_tier": "low",
    },
    # === ADDITIONAL MICRONUTRIENTS ===
    "iron_sulfate": {
        "name_ar": "سلفات الحديد",
        "name_en": "Iron Sulfate (Ferrous Sulfate)",
        "formula": "FeSO4·7H2O",
        "analysis": {"Fe": 20, "S": 11},
        "type": "micronutrient",
        "form": "crystalline",
        "solubility": "high",
        "application_methods": ["soil", "foliar", "fertigation"],
        "precautions_ar": ["رش ورقي 0.5%", "فعال في التربة الحامضية"],
        "precautions_en": ["Foliar spray 0.5%", "Effective in acidic soils"],
        "price_tier": "low",
    },
    "zinc_chelate": {
        "name_ar": "زنك مخلبي",
        "name_en": "Zinc Chelate (Zn-EDTA)",
        "formula": "Zn-EDTA",
        "analysis": {"Zn": 14},
        "type": "micronutrient",
        "form": "soluble",
        "solubility": "high",
        "application_methods": ["foliar", "fertigation"],
        "precautions_ar": ["رش ورقي 0.2%", "لعلاج نقص الزنك في التربة القلوية"],
        "precautions_en": ["Foliar spray 0.2%", "For zinc deficiency in alkaline soils"],
        "price_tier": "medium",
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
    """Get fertilizer by ID. Returns None if fertilizer_id is empty or not found."""
    if not fertilizer_id or not isinstance(fertilizer_id, str):
        return None
    return FERTILIZERS.get(fertilizer_id.strip())


def get_fertilizers_by_type(fert_type: str) -> list[dict]:
    """Get all fertilizers of a specific type. Returns empty list if type is missing or not found."""
    if not fert_type or not isinstance(fert_type, str):
        return []
    fert_type = fert_type.strip()
    return [{"id": k, **v} for k, v in FERTILIZERS.items() if v.get("type") == fert_type]


def get_fertilizers_for_nutrient(nutrient: str) -> list[dict]:
    """Get fertilizers that provide a specific nutrient. Returns empty list if nutrient is missing."""
    if not nutrient or not isinstance(nutrient, str):
        return []
    nutrient = nutrient.strip()
    results = []
    for fert_id, fert in FERTILIZERS.items():
        analysis = fert.get("analysis", {})
        if nutrient in analysis and analysis[nutrient] > 0:
            results.append({"id": fert_id, **fert, "nutrient_content": analysis[nutrient]})
    # Sort by nutrient content descending
    return sorted(results, key=lambda x: x["nutrient_content"], reverse=True)


def calculate_dose(fertilizer_id: str, nutrient: str, target_kg_ha: float) -> float | None:
    """
    Calculate fertilizer dose needed to supply target kg/ha of nutrient.
    Returns kg/ha of fertilizer needed, or None if inputs are invalid.
    """
    if not fertilizer_id or not nutrient:
        return None
    if target_kg_ha <= 0:
        return None

    fert = FERTILIZERS.get(fertilizer_id)
    if not fert:
        return None

    analysis = fert.get("analysis", {})
    if nutrient not in analysis:
        return None

    nutrient_pct = analysis[nutrient]
    if nutrient_pct == 0:
        return None

    return (target_kg_ha / nutrient_pct) * 100
