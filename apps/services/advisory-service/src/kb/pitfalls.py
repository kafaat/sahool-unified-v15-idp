"""
Agricultural Pitfalls Knowledge Base - SAHOOL Agro Advisor
قاعدة معرفة المزالق الزراعية - مستشار ساحول الزراعي

Common mistakes and pitfalls in agriculture based on 2025 article series.
الأخطاء الشائعة والمزالق في الزراعة بناءً على سلسلة مقالات 2025.
"""

from typing import Optional

# === AGRICULTURAL PITFALLS ===
# المزالق الزراعية
PITFALLS = {
    # === SOIL MANAGEMENT PITFALLS ===
    "over_tillage": {
        "name_ar": "الحراثة المفرطة",
        "name_en": "Over-Tillage",
        "category": "soil",
        "severity": "high",
        "description_ar": "الحراثة العميقة والمتكررة التي تدمر بنية التربة والكائنات الحية فيها",
        "description_en": "Deep and frequent tillage that destroys soil structure and living organisms",
        "symptoms_ar": [
            "تكوين طبقة صلبة تحت السطح",
            "تآكل التربة بسرعة",
            "انخفاض المادة العضوية",
            "ضعف تسرب المياه",
        ],
        "symptoms_en": [
            "Hardpan formation below surface",
            "Rapid soil erosion",
            "Decreased organic matter",
            "Poor water infiltration",
        ],
        "causes_ar": ["الاعتقاد بضرورة الحراثة", "تقليد الممارسات القديمة", "عدم معرفة البدائل"],
        "causes_en": ["Belief that tillage is necessary", "Following old practices", "Not knowing alternatives"],
        "solutions_ar": [
            "تبني الزراعة بدون حراثة",
            "استخدام محاصيل التغطية",
            "تقليل عمق الحراثة",
            "الحراثة فقط عند الضرورة",
        ],
        "solutions_en": [
            "Adopt no-till farming",
            "Use cover crops",
            "Reduce tillage depth",
            "Till only when necessary",
        ],
        "economic_impact": "high",
        "recovery_time_months": 24,
    },
    "soil_compaction": {
        "name_ar": "ضغط التربة",
        "name_en": "Soil Compaction",
        "category": "soil",
        "severity": "high",
        "description_ar": "ضغط التربة بسبب الآلات الثقيلة أو العمل في ظروف رطبة",
        "description_en": "Soil compression from heavy machinery or working in wet conditions",
        "symptoms_ar": [
            "جذور ضحلة ومشوهة",
            "تجمع المياه على السطح",
            "نمو ضعيف للمحاصيل",
            "صعوبة اختراق الجذور",
        ],
        "symptoms_en": [
            "Shallow and deformed roots",
            "Surface water pooling",
            "Poor crop growth",
            "Difficulty in root penetration",
        ],
        "causes_ar": ["استخدام آلات ثقيلة", "العمل في تربة رطبة", "حركة مرور متكررة"],
        "causes_en": ["Heavy machinery use", "Working wet soil", "Frequent traffic"],
        "solutions_ar": [
            "تقليل حركة الآلات",
            "استخدام إطارات عريضة",
            "تجنب العمل في تربة رطبة",
            "زراعة جذور عميقة",
        ],
        "solutions_en": [
            "Reduce machinery traffic",
            "Use wide tires",
            "Avoid working wet soil",
            "Plant deep-rooted crops",
        ],
        "economic_impact": "high",
        "recovery_time_months": 36,
    },
    "ignoring_soil_biology": {
        "name_ar": "تجاهل بيولوجيا التربة",
        "name_en": "Ignoring Soil Biology",
        "category": "soil",
        "severity": "medium",
        "description_ar": "التركيز على الكيمياء فقط وتجاهل الكائنات الحية في التربة",
        "description_en": "Focusing only on chemistry while ignoring living organisms in soil",
        "symptoms_ar": [
            "حاجة متزايدة للأسمدة",
            "أمراض تربة متكررة",
            "تربة ميتة بدون ديدان",
            "تدهور المحصول مع الوقت",
        ],
        "symptoms_en": [
            "Increasing fertilizer needs",
            "Recurring soil diseases",
            "Dead soil without worms",
            "Declining yields over time",
        ],
        "causes_ar": ["المبيدات الكيميائية", "غياب المادة العضوية", "تبخير التربة"],
        "causes_en": ["Chemical pesticides", "Lack of organic matter", "Soil fumigation"],
        "solutions_ar": [
            "إضافة كمبوست بانتظام",
            "تقليل الكيماويات",
            "تنويع المحاصيل",
            "استخدام منشطات حيوية",
        ],
        "solutions_en": [
            "Add compost regularly",
            "Reduce chemicals",
            "Diversify crops",
            "Use biostimulants",
        ],
        "economic_impact": "medium",
        "recovery_time_months": 18,
    },
    # === WATER MANAGEMENT PITFALLS ===
    "over_irrigation": {
        "name_ar": "الري المفرط",
        "name_en": "Over-Irrigation",
        "category": "water",
        "severity": "high",
        "description_ar": "إعطاء المحاصيل ماء أكثر من حاجتها الفعلية",
        "description_en": "Giving crops more water than their actual needs",
        "symptoms_ar": [
            "اصفرار الأوراق",
            "تعفن الجذور",
            "نمو فطري",
            "هدر المياه والطاقة",
        ],
        "symptoms_en": [
            "Leaf yellowing",
            "Root rot",
            "Fungal growth",
            "Waste of water and energy",
        ],
        "causes_ar": ["جدولة ثابتة بدون مراقبة", "خوف من الجفاف", "عدم قياس رطوبة التربة"],
        "causes_en": ["Fixed schedule without monitoring", "Fear of drought", "Not measuring soil moisture"],
        "solutions_ar": [
            "استخدام حساسات رطوبة",
            "الري بالتنقيط",
            "جدولة حسب المحصول والطقس",
            "فحص رطوبة التربة قبل الري",
        ],
        "solutions_en": [
            "Use moisture sensors",
            "Drip irrigation",
            "Schedule by crop and weather",
            "Check soil moisture before irrigating",
        ],
        "economic_impact": "high",
        "recovery_time_months": 1,
    },
    "inefficient_irrigation": {
        "name_ar": "الري غير الكفء",
        "name_en": "Inefficient Irrigation",
        "category": "water",
        "severity": "medium",
        "description_ar": "استخدام طرق ري تهدر الكثير من الماء",
        "description_en": "Using irrigation methods that waste much water",
        "symptoms_ar": [
            "فواتير مياه عالية",
            "بقع جافة في الحقل",
            "تملح التربة",
            "نمو غير متساوي",
        ],
        "symptoms_en": [
            "High water bills",
            "Dry spots in field",
            "Soil salinization",
            "Uneven growth",
        ],
        "causes_ar": ["الري بالغمر", "أنظمة قديمة", "تسربات غير مكتشفة"],
        "causes_en": ["Flood irrigation", "Old systems", "Undetected leaks"],
        "solutions_ar": [
            "التحول للري بالتنقيط",
            "صيانة دورية",
            "تقسيم الحقل لمناطق",
            "استخدام التغطية",
        ],
        "solutions_en": [
            "Switch to drip irrigation",
            "Regular maintenance",
            "Divide field into zones",
            "Use mulching",
        ],
        "economic_impact": "medium",
        "recovery_time_months": 3,
    },
    # === FERTILIZER PITFALLS ===
    "over_fertilization": {
        "name_ar": "التسميد المفرط",
        "name_en": "Over-Fertilization",
        "category": "nutrition",
        "severity": "high",
        "description_ar": "إضافة أسمدة أكثر من حاجة المحصول الفعلية",
        "description_en": "Adding more fertilizer than the crop actually needs",
        "symptoms_ar": [
            "نمو خضري مفرط",
            "حرق الجذور",
            "تلوث المياه الجوفية",
            "تراكم الأملاح",
        ],
        "symptoms_en": [
            "Excessive vegetative growth",
            "Root burn",
            "Groundwater pollution",
            "Salt accumulation",
        ],
        "causes_ar": ["عدم تحليل التربة", "اتباع وصفات عامة", "الاعتقاد بأن الأكثر أفضل"],
        "causes_en": ["No soil analysis", "Following general recipes", "Believing more is better"],
        "solutions_ar": [
            "تحليل التربة قبل التسميد",
            "حساب الاحتياج الفعلي",
            "التسميد على دفعات",
            "استخدام أسمدة بطيئة التحرر",
        ],
        "solutions_en": [
            "Soil analysis before fertilizing",
            "Calculate actual needs",
            "Split fertilizer applications",
            "Use slow-release fertilizers",
        ],
        "economic_impact": "high",
        "recovery_time_months": 6,
    },
    "nutrient_imbalance": {
        "name_ar": "اختلال توازن العناصر",
        "name_en": "Nutrient Imbalance",
        "category": "nutrition",
        "severity": "medium",
        "description_ar": "التركيز على بعض العناصر وإهمال أخرى",
        "description_en": "Focusing on some nutrients while neglecting others",
        "symptoms_ar": [
            "أعراض نقص عناصر صغرى",
            "تثبيت العناصر في التربة",
            "انخفاض جودة المحصول",
            "ضعف المقاومة للأمراض",
        ],
        "symptoms_en": [
            "Micronutrient deficiency symptoms",
            "Nutrient lockup in soil",
            "Reduced crop quality",
            "Poor disease resistance",
        ],
        "causes_ar": ["استخدام NPK فقط", "تجاهل العناصر الصغرى", "عدم فهم التفاعلات"],
        "causes_en": ["Using only NPK", "Ignoring micronutrients", "Not understanding interactions"],
        "solutions_ar": [
            "تحليل شامل للتربة والنبات",
            "برنامج تغذية متكامل",
            "إضافة مادة عضوية",
            "تنويع مصادر التسميد",
        ],
        "solutions_en": [
            "Comprehensive soil and plant analysis",
            "Integrated nutrition program",
            "Add organic matter",
            "Diversify fertilizer sources",
        ],
        "economic_impact": "medium",
        "recovery_time_months": 12,
    },
    # === PEST MANAGEMENT PITFALLS ===
    "pesticide_overuse": {
        "name_ar": "الإفراط في المبيدات",
        "name_en": "Pesticide Overuse",
        "category": "pest_management",
        "severity": "high",
        "description_ar": "الاستخدام المكثف وغير المبرر للمبيدات الكيميائية",
        "description_en": "Intensive and unjustified use of chemical pesticides",
        "symptoms_ar": [
            "مقاومة الآفات للمبيدات",
            "قتل الأعداء الطبيعية",
            "تلوث المنتجات",
            "مشاكل صحية للعمال",
        ],
        "symptoms_en": [
            "Pest resistance to pesticides",
            "Killing natural enemies",
            "Product contamination",
            "Worker health issues",
        ],
        "causes_ar": ["الرش الوقائي الروتيني", "الخوف من الخسارة", "ضغط التجار"],
        "causes_en": ["Routine preventive spraying", "Fear of loss", "Dealer pressure"],
        "solutions_ar": [
            "المكافحة المتكاملة IPM",
            "الرش فقط عند الحاجة",
            "مراقبة عتبة الضرر الاقتصادي",
            "استخدام بدائل حيوية",
        ],
        "solutions_en": [
            "Integrated Pest Management",
            "Spray only when needed",
            "Monitor economic threshold",
            "Use biological alternatives",
        ],
        "economic_impact": "high",
        "recovery_time_months": 24,
    },
    "ignoring_beneficial_insects": {
        "name_ar": "تجاهل الحشرات النافعة",
        "name_en": "Ignoring Beneficial Insects",
        "category": "pest_management",
        "severity": "medium",
        "description_ar": "قتل الحشرات النافعة التي تكافح الآفات طبيعياً",
        "description_en": "Killing beneficial insects that naturally control pests",
        "symptoms_ar": [
            "زيادة تعداد الآفات",
            "حاجة متزايدة للمبيدات",
            "اختفاء الأعداء الطبيعية",
            "دورات تفشي متكررة",
        ],
        "symptoms_en": [
            "Increased pest populations",
            "Growing pesticide needs",
            "Disappearing natural enemies",
            "Recurring outbreak cycles",
        ],
        "causes_ar": ["المبيدات واسعة الطيف", "عدم التعرف على النافعات", "رش في أوقات خاطئة"],
        "causes_en": ["Broad-spectrum pesticides", "Not recognizing beneficials", "Spraying at wrong times"],
        "solutions_ar": [
            "تعلم التعرف على النافعات",
            "استخدام مبيدات انتقائية",
            "توفير موائل للنافعات",
            "تجنب الرش أثناء نشاطها",
        ],
        "solutions_en": [
            "Learn to identify beneficials",
            "Use selective pesticides",
            "Provide habitats for beneficials",
            "Avoid spraying during their activity",
        ],
        "economic_impact": "medium",
        "recovery_time_months": 12,
    },
    # === CROP MANAGEMENT PITFALLS ===
    "monoculture": {
        "name_ar": "الزراعة الأحادية",
        "name_en": "Monoculture",
        "category": "crop_management",
        "severity": "high",
        "description_ar": "زراعة نفس المحصول في نفس الأرض سنة بعد سنة",
        "description_en": "Growing the same crop on the same land year after year",
        "symptoms_ar": [
            "تراكم أمراض التربة",
            "استنزاف عناصر معينة",
            "زيادة الآفات المتخصصة",
            "انخفاض المحصول التدريجي",
        ],
        "symptoms_en": [
            "Soil disease buildup",
            "Depletion of specific nutrients",
            "Increased specialized pests",
            "Gradual yield decline",
        ],
        "causes_ar": ["سهولة الإدارة", "ضمان السوق", "نقص المعرفة بالتناوب"],
        "causes_en": ["Ease of management", "Market certainty", "Lack of rotation knowledge"],
        "solutions_ar": [
            "تناوب المحاصيل 3-4 سنوات",
            "زراعة بقوليات في الدورة",
            "تنويع العائلات النباتية",
            "محاصيل تغطية بين المواسم",
        ],
        "solutions_en": [
            "3-4 year crop rotation",
            "Include legumes in rotation",
            "Diversify plant families",
            "Cover crops between seasons",
        ],
        "economic_impact": "high",
        "recovery_time_months": 36,
    },
    "wrong_variety_selection": {
        "name_ar": "اختيار صنف غير مناسب",
        "name_en": "Wrong Variety Selection",
        "category": "crop_management",
        "severity": "medium",
        "description_ar": "اختيار أصناف غير ملائمة للظروف المحلية",
        "description_en": "Selecting varieties unsuitable for local conditions",
        "symptoms_ar": [
            "إنتاجية أقل من المتوقع",
            "حساسية للأمراض المحلية",
            "عدم تكيف مع الطقس",
            "جودة منخفضة",
        ],
        "symptoms_en": [
            "Lower than expected yield",
            "Sensitivity to local diseases",
            "Weather inadaptability",
            "Low quality",
        ],
        "causes_ar": ["اتباع الموضة", "توصيات غير محلية", "عدم التجربة قبل التوسع"],
        "causes_en": ["Following trends", "Non-local recommendations", "Not testing before scaling"],
        "solutions_ar": [
            "استشارة المختصين المحليين",
            "تجربة الصنف على نطاق صغير",
            "اختيار أصناف مقاومة محلياً",
            "مراعاة متطلبات السوق",
        ],
        "solutions_en": [
            "Consult local specialists",
            "Test variety on small scale",
            "Choose locally resistant varieties",
            "Consider market requirements",
        ],
        "economic_impact": "medium",
        "recovery_time_months": 6,
    },
    # === BUSINESS PITFALLS ===
    "poor_market_timing": {
        "name_ar": "توقيت سوقي خاطئ",
        "name_en": "Poor Market Timing",
        "category": "business",
        "severity": "medium",
        "description_ar": "إنتاج المحاصيل في أوقات تكثر فيها المنافسة",
        "description_en": "Producing crops when competition is high",
        "symptoms_ar": [
            "أسعار منخفضة",
            "صعوبة التسويق",
            "خسائر مالية",
            "تلف المنتجات",
        ],
        "symptoms_en": [
            "Low prices",
            "Marketing difficulty",
            "Financial losses",
            "Product spoilage",
        ],
        "causes_ar": ["عدم دراسة السوق", "التقليد الأعمى", "غياب التخطيط"],
        "causes_en": ["Not studying market", "Blind imitation", "Lack of planning"],
        "solutions_ar": [
            "دراسة دورات السوق",
            "الزراعة المبكرة أو المتأخرة",
            "تنويع المحاصيل",
            "عقود مسبقة",
        ],
        "solutions_en": [
            "Study market cycles",
            "Early or late planting",
            "Diversify crops",
            "Forward contracts",
        ],
        "economic_impact": "high",
        "recovery_time_months": 3,
    },
    "no_record_keeping": {
        "name_ar": "عدم تسجيل البيانات",
        "name_en": "No Record Keeping",
        "category": "business",
        "severity": "medium",
        "description_ar": "عدم توثيق العمليات والتكاليف والإنتاج",
        "description_en": "Not documenting operations, costs, and production",
        "symptoms_ar": [
            "عدم معرفة الربح الحقيقي",
            "تكرار الأخطاء",
            "صعوبة التحسين",
            "عدم أهلية للشهادات",
        ],
        "symptoms_en": [
            "Unknown actual profit",
            "Repeating mistakes",
            "Difficulty improving",
            "Ineligibility for certifications",
        ],
        "causes_ar": ["ضيق الوقت", "عدم الاقتناع بالفائدة", "غياب النظام"],
        "causes_en": ["Time constraints", "Not convinced of benefit", "Lack of system"],
        "solutions_ar": [
            "استخدام تطبيقات بسيطة",
            "تسجيل يومي موجز",
            "توكيل المهمة لشخص",
            "ربط بنظام ساحول",
        ],
        "solutions_en": [
            "Use simple apps",
            "Brief daily recording",
            "Delegate the task",
            "Link to SAHOOL system",
        ],
        "economic_impact": "medium",
        "recovery_time_months": 1,
    },
}


def get_pitfall(pitfall_id: str) -> Optional[dict]:
    """
    Get pitfall by ID
    الحصول على المزلق بالمعرف
    """
    return PITFALLS.get(pitfall_id)


def get_pitfalls_by_category(category: str) -> list[dict]:
    """
    Get all pitfalls in a category
    الحصول على جميع المزالق في فئة معينة
    """
    return [
        {"id": k, **v}
        for k, v in PITFALLS.items()
        if v["category"] == category
    ]


def get_pitfalls_by_severity(severity: str) -> list[dict]:
    """
    Get all pitfalls of a specific severity
    الحصول على جميع المزالق بمستوى خطورة معين
    """
    return [
        {"id": k, **v}
        for k, v in PITFALLS.items()
        if v["severity"] == severity
    ]


def search_pitfalls(query: str, lang: str = "ar") -> list[dict]:
    """
    Search pitfalls by name, symptoms, or solutions
    البحث في المزالق بالاسم أو الأعراض أو الحلول
    """
    results = []
    query_lower = query.lower()

    for pitfall_id, pitfall in PITFALLS.items():
        name_field = "name_ar" if lang == "ar" else "name_en"
        symptoms_field = "symptoms_ar" if lang == "ar" else "symptoms_en"
        solutions_field = "solutions_ar" if lang == "ar" else "solutions_en"

        if query_lower in pitfall[name_field].lower():
            results.append({"id": pitfall_id, **pitfall, "match": "name"})
        elif any(query_lower in s.lower() for s in pitfall[symptoms_field]):
            results.append({"id": pitfall_id, **pitfall, "match": "symptom"})
        elif any(query_lower in s.lower() for s in pitfall[solutions_field]):
            results.append({"id": pitfall_id, **pitfall, "match": "solution"})

    return results


def diagnose_pitfalls(
    symptoms: list[str],
    category: Optional[str] = None,
    lang: str = "ar",
) -> list[dict]:
    """
    Diagnose potential pitfalls based on observed symptoms
    تشخيص المزالق المحتملة بناءً على الأعراض الملاحظة
    """
    results = []
    symptoms_lower = [s.lower() for s in symptoms]

    for pitfall_id, pitfall in PITFALLS.items():
        if category and pitfall["category"] != category:
            continue

        symptoms_field = "symptoms_ar" if lang == "ar" else "symptoms_en"
        pitfall_symptoms = [s.lower() for s in pitfall[symptoms_field]]

        # Calculate match score
        matches = sum(1 for s in symptoms_lower if any(s in ps for ps in pitfall_symptoms))

        if matches > 0:
            score = matches / len(pitfall_symptoms)
            results.append({
                "id": pitfall_id,
                **pitfall,
                "match_score": score,
                "matched_symptoms": matches,
            })

    # Sort by match score descending
    return sorted(results, key=lambda x: x["match_score"], reverse=True)


def get_recovery_plan(pitfall_id: str, lang: str = "ar") -> Optional[dict]:
    """
    Get recovery plan for a specific pitfall
    الحصول على خطة التعافي من مزلق معين
    """
    pitfall = PITFALLS.get(pitfall_id)
    if not pitfall:
        return None

    solutions_field = "solutions_ar" if lang == "ar" else "solutions_en"

    return {
        "pitfall_id": pitfall_id,
        "name": pitfall["name_ar" if lang == "ar" else "name_en"],
        "solutions": pitfall[solutions_field],
        "recovery_time_months": pitfall["recovery_time_months"],
        "economic_impact": pitfall["economic_impact"],
        "priority": "high" if pitfall["severity"] == "high" else "medium",
    }


def calculate_risk_score(
    current_practices: dict,
) -> dict:
    """
    Calculate overall pitfall risk score based on current practices
    حساب درجة المخاطر الإجمالية بناءً على الممارسات الحالية
    """
    risk_factors = []
    total_score = 0

    # Check tillage practices
    if current_practices.get("tillage_frequency", 0) > 2:
        risk_factors.append({
            "pitfall_id": "over_tillage",
            "risk_level": "high",
            "points": 15,
        })
        total_score += 15

    # Check irrigation method
    if current_practices.get("irrigation_method") == "flood":
        risk_factors.append({
            "pitfall_id": "inefficient_irrigation",
            "risk_level": "medium",
            "points": 10,
        })
        total_score += 10

    # Check rotation
    if not current_practices.get("uses_rotation", True):
        risk_factors.append({
            "pitfall_id": "monoculture",
            "risk_level": "high",
            "points": 15,
        })
        total_score += 15

    # Check pesticide usage
    if current_practices.get("pesticide_applications_per_season", 0) > 5:
        risk_factors.append({
            "pitfall_id": "pesticide_overuse",
            "risk_level": "high",
            "points": 15,
        })
        total_score += 15

    # Check soil testing
    if not current_practices.get("does_soil_testing", False):
        risk_factors.append({
            "pitfall_id": "over_fertilization",
            "risk_level": "medium",
            "points": 10,
        })
        total_score += 10

    # Check record keeping
    if not current_practices.get("keeps_records", False):
        risk_factors.append({
            "pitfall_id": "no_record_keeping",
            "risk_level": "medium",
            "points": 8,
        })
        total_score += 8

    # Calculate overall risk level
    if total_score >= 40:
        overall_risk = "high"
    elif total_score >= 20:
        overall_risk = "medium"
    else:
        overall_risk = "low"

    return {
        "total_score": total_score,
        "max_score": 100,
        "overall_risk": overall_risk,
        "risk_factors": risk_factors,
        "recommendations_count": len(risk_factors),
    }
