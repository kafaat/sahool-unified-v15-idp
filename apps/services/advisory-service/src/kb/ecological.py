"""
Ecological Agriculture Knowledge Base - SAHOOL Agro Advisor
قاعدة معرفة الزراعة الإيكولوجية - مستشار ساحول الزراعي

Based on ecological agriculture article series 2025.
مبني على سلسلة مقالات الزراعة الإيكولوجية 2025.
"""

from typing import Optional

# === ECOLOGICAL PRINCIPLES ===
# المبادئ الإيكولوجية
ECOLOGICAL_PRINCIPLES = {
    "biodiversity_enhancement": {
        "name_ar": "تعزيز التنوع البيولوجي",
        "name_en": "Biodiversity Enhancement",
        "category": "foundation",
        "description_ar": "زيادة تنوع الأنواع في المزرعة لتحقيق توازن بيئي طبيعي",
        "description_en": "Increasing species diversity on farm to achieve natural ecological balance",
        "practices": [
            "polyculture",
            "cover_crops",
            "hedgerows",
            "insect_hotels",
            "wildflower_strips",
        ],
        "benefits_ar": [
            "مكافحة طبيعية للآفات",
            "تحسين التلقيح",
            "زيادة خصوبة التربة",
            "مرونة المحاصيل",
        ],
        "benefits_en": [
            "Natural pest control",
            "Improved pollination",
            "Increased soil fertility",
            "Crop resilience",
        ],
        "difficulty": "medium",
        "time_to_benefit_months": 12,
        "globalgap_cp": ["CB.1.1", "CB.7.1"],
    },
    "soil_health_management": {
        "name_ar": "إدارة صحة التربة",
        "name_en": "Soil Health Management",
        "category": "foundation",
        "description_ar": "بناء تربة صحية وحية من خلال ممارسات طبيعية",
        "description_en": "Building healthy living soil through natural practices",
        "practices": [
            "composting",
            "no_till",
            "mulching",
            "crop_rotation",
            "green_manure",
        ],
        "benefits_ar": [
            "زيادة المادة العضوية",
            "تحسين بنية التربة",
            "احتفاظ أفضل بالماء",
            "نشاط بيولوجي",
        ],
        "benefits_en": [
            "Increased organic matter",
            "Improved soil structure",
            "Better water retention",
            "Biological activity",
        ],
        "difficulty": "easy",
        "time_to_benefit_months": 6,
        "globalgap_cp": ["CB.3.1", "CB.3.2", "CB.3.4"],
    },
    "water_conservation": {
        "name_ar": "الحفاظ على المياه",
        "name_en": "Water Conservation",
        "category": "resource",
        "description_ar": "استخدام أمثل للموارد المائية وحمايتها من التلوث",
        "description_en": "Optimal use of water resources and protection from pollution",
        "practices": [
            "drip_irrigation",
            "rainwater_harvesting",
            "swales",
            "mulching",
            "drought_resistant_varieties",
        ],
        "benefits_ar": [
            "توفير 40-60% من المياه",
            "تقليل الملوحة",
            "حماية المياه الجوفية",
            "استدامة طويلة المدى",
        ],
        "benefits_en": [
            "Save 40-60% water",
            "Reduce salinity",
            "Protect groundwater",
            "Long-term sustainability",
        ],
        "difficulty": "medium",
        "time_to_benefit_months": 3,
        "globalgap_cp": ["CB.5.1", "CB.5.2", "CB.5.3"],
    },
    "natural_pest_management": {
        "name_ar": "المكافحة الطبيعية للآفات",
        "name_en": "Natural Pest Management",
        "category": "protection",
        "description_ar": "استخدام الأعداء الطبيعية والممارسات الوقائية بدل المبيدات الكيميائية",
        "description_en": "Using natural enemies and preventive practices instead of chemical pesticides",
        "practices": [
            "biological_control",
            "companion_planting",
            "trap_crops",
            "pheromone_traps",
            "beneficial_insects",
        ],
        "benefits_ar": [
            "تقليل التكاليف",
            "سلامة المنتجات",
            "توازن بيئي",
            "صحة العمال",
        ],
        "benefits_en": [
            "Reduced costs",
            "Product safety",
            "Ecological balance",
            "Worker health",
        ],
        "difficulty": "hard",
        "time_to_benefit_months": 18,
        "globalgap_cp": ["CB.7.1", "CB.7.5", "CB.7.6"],
    },
    "closed_loop_systems": {
        "name_ar": "أنظمة الحلقة المغلقة",
        "name_en": "Closed Loop Systems",
        "category": "efficiency",
        "description_ar": "إعادة تدوير المخلفات والموارد داخل المزرعة",
        "description_en": "Recycling waste and resources within the farm",
        "practices": [
            "composting",
            "biogas",
            "animal_integration",
            "agroforestry",
            "vermiculture",
        ],
        "benefits_ar": [
            "تقليل المدخلات الخارجية",
            "خفض التكاليف",
            "إدارة المخلفات",
            "استقلالية المزرعة",
        ],
        "benefits_en": [
            "Reduced external inputs",
            "Lower costs",
            "Waste management",
            "Farm autonomy",
        ],
        "difficulty": "hard",
        "time_to_benefit_months": 24,
        "globalgap_cp": ["CB.6.2", "AF.4.1"],
    },
    "climate_adaptation": {
        "name_ar": "التكيف مع المناخ",
        "name_en": "Climate Adaptation",
        "category": "resilience",
        "description_ar": "تصميم أنظمة زراعية مرنة تتكيف مع تغير المناخ",
        "description_en": "Designing flexible farming systems that adapt to climate change",
        "practices": [
            "agroforestry",
            "microclimate_design",
            "heat_tolerant_varieties",
            "shade_structures",
            "windbreaks",
        ],
        "benefits_ar": [
            "حماية من الحرارة المرتفعة",
            "تقليل مخاطر الجفاف",
            "استقرار الإنتاج",
            "تحسين ظروف العمل",
        ],
        "benefits_en": [
            "Heat protection",
            "Reduced drought risk",
            "Production stability",
            "Improved working conditions",
        ],
        "difficulty": "medium",
        "time_to_benefit_months": 12,
        "globalgap_cp": ["AF.1.1", "CB.1.1"],
    },
}

# === ECOLOGICAL PRACTICES ===
# الممارسات الإيكولوجية
ECOLOGICAL_PRACTICES = {
    "composting": {
        "name_ar": "التسميد العضوي (الكمبوست)",
        "name_en": "Composting",
        "category": "soil",
        "description_ar": "تحويل المخلفات العضوية إلى سماد غني بالمغذيات",
        "description_en": "Converting organic waste into nutrient-rich fertilizer",
        "materials_ar": ["مخلفات نباتية", "روث الحيوانات", "بقايا المطبخ", "قش"],
        "materials_en": ["Plant residues", "Animal manure", "Kitchen scraps", "Straw"],
        "steps_ar": [
            "جمع المواد العضوية بنسبة 3 كربون : 1 نيتروجين",
            "إنشاء كومة بارتفاع 1-1.5 متر",
            "الحفاظ على الرطوبة 50-60%",
            "تقليب كل 2-3 أسابيع",
            "الجاهزية خلال 2-4 أشهر",
        ],
        "steps_en": [
            "Collect organic materials at 3 carbon : 1 nitrogen ratio",
            "Build pile 1-1.5m high",
            "Maintain 50-60% moisture",
            "Turn every 2-3 weeks",
            "Ready in 2-4 months",
        ],
        "application_rate": "5-10 tons/ha",
        "timing": "before_planting",
        "cost_level": "low",
        "labor_intensity": "medium",
    },
    "no_till": {
        "name_ar": "الزراعة بدون حراثة",
        "name_en": "No-Till Farming",
        "category": "soil",
        "description_ar": "تقليل اضطراب التربة للحفاظ على بنيتها وكائناتها الحية",
        "description_en": "Minimizing soil disturbance to preserve structure and living organisms",
        "materials_ar": ["أداة زراعة مباشرة", "غطاء نباتي", "مبيد أعشاب عضوي اختياري"],
        "materials_en": ["Direct seeding tool", "Cover crop", "Optional organic herbicide"],
        "steps_ar": [
            "زراعة غطاء نباتي كثيف",
            "قص أو ضغط الغطاء النباتي",
            "زراعة مباشرة في الغطاء",
            "إدارة الأعشاب ميكانيكياً",
        ],
        "steps_en": [
            "Plant dense cover crop",
            "Mow or roll cover",
            "Direct seed into cover",
            "Manage weeds mechanically",
        ],
        "application_rate": "N/A",
        "timing": "continuous",
        "cost_level": "low",
        "labor_intensity": "low",
    },
    "companion_planting": {
        "name_ar": "الزراعة التصاحبية",
        "name_en": "Companion Planting",
        "category": "biodiversity",
        "description_ar": "زراعة نباتات متكاملة معاً للحماية المتبادلة وتحسين النمو",
        "description_en": "Growing complementary plants together for mutual protection and improved growth",
        "materials_ar": ["بذور متنوعة", "خريطة تخطيط", "معرفة بالتوافقات"],
        "materials_en": ["Diverse seeds", "Planning map", "Compatibility knowledge"],
        "steps_ar": [
            "دراسة التوافقات بين المحاصيل",
            "تصميم خريطة الزراعة",
            "مراعاة ارتفاع النباتات",
            "التوقيت المناسب للزراعة",
        ],
        "steps_en": [
            "Study crop compatibilities",
            "Design planting map",
            "Consider plant heights",
            "Proper planting timing",
        ],
        "application_rate": "N/A",
        "timing": "planting",
        "cost_level": "low",
        "labor_intensity": "medium",
    },
    "biological_control": {
        "name_ar": "المكافحة البيولوجية",
        "name_en": "Biological Control",
        "category": "pest_management",
        "description_ar": "استخدام الكائنات الحية للسيطرة على الآفات",
        "description_en": "Using living organisms to control pests",
        "materials_ar": [
            "حشرات مفترسة (أبو العيد)",
            "طفيليات (ترايكوجراما)",
            "مبيدات حيوية (Bt)",
        ],
        "materials_en": [
            "Predatory insects (ladybugs)",
            "Parasitoids (Trichogramma)",
            "Biopesticides (Bt)",
        ],
        "steps_ar": [
            "تحديد الآفة المستهدفة",
            "اختيار العدو الطبيعي المناسب",
            "إطلاق في الوقت والكمية المناسبة",
            "مراقبة النتائج",
        ],
        "steps_en": [
            "Identify target pest",
            "Select appropriate natural enemy",
            "Release at right time and quantity",
            "Monitor results",
        ],
        "application_rate": "varies_by_agent",
        "timing": "early_infestation",
        "cost_level": "medium",
        "labor_intensity": "medium",
    },
    "agroforestry": {
        "name_ar": "الزراعة الحراجية",
        "name_en": "Agroforestry",
        "category": "system_design",
        "description_ar": "دمج الأشجار مع المحاصيل أو الحيوانات في نظام واحد",
        "description_en": "Integrating trees with crops or animals in one system",
        "materials_ar": ["شتلات أشجار", "محاصيل تحتية", "تصميم نظام متكامل"],
        "materials_en": ["Tree seedlings", "Understory crops", "Integrated system design"],
        "steps_ar": [
            "اختيار أنواع الأشجار المناسبة",
            "تصميم تخطيط الصفوف",
            "زراعة الأشجار أولاً",
            "إضافة المحاصيل بعد التأسيس",
        ],
        "steps_en": [
            "Select appropriate tree species",
            "Design row layout",
            "Plant trees first",
            "Add crops after establishment",
        ],
        "application_rate": "50-200 trees/ha",
        "timing": "rainy_season",
        "cost_level": "high",
        "labor_intensity": "high",
    },
    "drip_irrigation": {
        "name_ar": "الري بالتنقيط",
        "name_en": "Drip Irrigation",
        "category": "water",
        "description_ar": "توصيل المياه مباشرة لجذور النبات بكفاءة عالية",
        "description_en": "Delivering water directly to plant roots with high efficiency",
        "materials_ar": ["أنابيب رئيسية", "خطوط تنقيط", "فلاتر", "مؤقتات"],
        "materials_en": ["Main pipes", "Drip lines", "Filters", "Timers"],
        "steps_ar": [
            "تصميم شبكة الري",
            "تركيب المضخة والفلاتر",
            "مد خطوط التنقيط",
            "ضبط جدول الري",
        ],
        "steps_en": [
            "Design irrigation network",
            "Install pump and filters",
            "Lay drip lines",
            "Set irrigation schedule",
        ],
        "application_rate": "2-4 L/h per emitter",
        "timing": "continuous",
        "cost_level": "medium",
        "labor_intensity": "low",
    },
    "cover_crops": {
        "name_ar": "محاصيل التغطية",
        "name_en": "Cover Crops",
        "category": "soil",
        "description_ar": "زراعة محاصيل غير منتجة لحماية وتحسين التربة",
        "description_en": "Growing non-harvested crops to protect and improve soil",
        "materials_ar": ["بذور بقوليات (برسيم، فول)", "بذور نجيليات (شعير، شوفان)"],
        "materials_en": ["Legume seeds (clover, fava)", "Grass seeds (barley, oats)"],
        "steps_ar": [
            "اختيار النوع حسب الهدف",
            "زراعة بعد الحصاد",
            "ترك للنمو 2-3 أشهر",
            "قص أو دمج في التربة",
        ],
        "steps_en": [
            "Select type based on goal",
            "Plant after harvest",
            "Allow 2-3 months growth",
            "Mow or incorporate into soil",
        ],
        "application_rate": "20-50 kg/ha",
        "timing": "off_season",
        "cost_level": "low",
        "labor_intensity": "low",
    },
    "mulching": {
        "name_ar": "التغطية العضوية",
        "name_en": "Mulching",
        "category": "soil",
        "description_ar": "تغطية التربة بمواد عضوية للحفاظ على الرطوبة ومنع الأعشاب",
        "description_en": "Covering soil with organic materials to retain moisture and prevent weeds",
        "materials_ar": ["قش", "نشارة خشب", "أوراق جافة", "مخلفات المحاصيل"],
        "materials_en": ["Straw", "Wood chips", "Dry leaves", "Crop residues"],
        "steps_ar": [
            "جمع المواد المتاحة",
            "فرش طبقة 10-15 سم",
            "ترك مسافة حول الساق",
            "تجديد عند التحلل",
        ],
        "steps_en": [
            "Collect available materials",
            "Spread 10-15cm layer",
            "Leave space around stem",
            "Renew when decomposed",
        ],
        "application_rate": "5-10 tons/ha",
        "timing": "after_planting",
        "cost_level": "low",
        "labor_intensity": "medium",
    },
}

# === COMPANION PLANTING GUIDE ===
# دليل الزراعة التصاحبية
COMPANION_PLANTING = {
    "tomato": {
        "name_ar": "الطماطم",
        "name_en": "Tomato",
        "good_companions": ["basil", "carrot", "onion", "parsley", "marigold"],
        "good_companions_ar": ["ريحان", "جزر", "بصل", "بقدونس", "قطيفة"],
        "bad_companions": ["cabbage", "fennel", "potato", "corn"],
        "bad_companions_ar": ["كرنب", "شمر", "بطاطس", "ذرة"],
        "benefits_ar": "الريحان يطرد الذباب الأبيض، القطيفة تجذب الملقحات",
        "benefits_en": "Basil repels whiteflies, marigold attracts pollinators",
    },
    "cucumber": {
        "name_ar": "الخيار",
        "name_en": "Cucumber",
        "good_companions": ["bean", "pea", "sunflower", "lettuce", "dill"],
        "good_companions_ar": ["فاصوليا", "بازلاء", "دوار الشمس", "خس", "شبت"],
        "bad_companions": ["potato", "aromatic_herbs"],
        "bad_companions_ar": ["بطاطس", "أعشاب عطرية قوية"],
        "benefits_ar": "البقوليات تثبت النيتروجين، دوار الشمس يوفر ظل جزئي",
        "benefits_en": "Legumes fix nitrogen, sunflower provides partial shade",
    },
    "pepper": {
        "name_ar": "الفلفل",
        "name_en": "Pepper",
        "good_companions": ["basil", "tomato", "carrot", "onion", "spinach"],
        "good_companions_ar": ["ريحان", "طماطم", "جزر", "بصل", "سبانخ"],
        "bad_companions": ["fennel", "kohlrabi"],
        "bad_companions_ar": ["شمر", "كرنب ساق"],
        "benefits_ar": "الريحان يحسن النكهة ويطرد الحشرات",
        "benefits_en": "Basil improves flavor and repels insects",
    },
    "beans": {
        "name_ar": "الفاصوليا",
        "name_en": "Beans",
        "good_companions": ["corn", "squash", "cucumber", "potato"],
        "good_companions_ar": ["ذرة", "قرع", "خيار", "بطاطس"],
        "bad_companions": ["onion", "garlic", "fennel"],
        "bad_companions_ar": ["بصل", "ثوم", "شمر"],
        "benefits_ar": "تثبيت النيتروجين للمحاصيل المجاورة",
        "benefits_en": "Fixes nitrogen for neighboring crops",
    },
    "carrot": {
        "name_ar": "الجزر",
        "name_en": "Carrot",
        "good_companions": ["onion", "leek", "tomato", "lettuce", "rosemary"],
        "good_companions_ar": ["بصل", "كراث", "طماطم", "خس", "إكليل الجبل"],
        "bad_companions": ["dill", "celery"],
        "bad_companions_ar": ["شبت", "كرفس"],
        "benefits_ar": "البصل يطرد ذبابة الجزر",
        "benefits_en": "Onion repels carrot fly",
    },
}


def get_principle(principle_id: str) -> Optional[dict]:
    """
    Get ecological principle by ID
    الحصول على المبدأ الإيكولوجي بالمعرف
    """
    return ECOLOGICAL_PRINCIPLES.get(principle_id)


def get_principles_by_category(category: str) -> list[dict]:
    """
    Get all principles in a category
    الحصول على جميع المبادئ في فئة معينة
    """
    return [
        {"id": k, **v}
        for k, v in ECOLOGICAL_PRINCIPLES.items()
        if v["category"] == category
    ]


def get_practice(practice_id: str) -> Optional[dict]:
    """
    Get ecological practice by ID
    الحصول على الممارسة الإيكولوجية بالمعرف
    """
    return ECOLOGICAL_PRACTICES.get(practice_id)


def get_practices_by_category(category: str) -> list[dict]:
    """
    Get all practices in a category
    الحصول على جميع الممارسات في فئة معينة
    """
    return [
        {"id": k, **v}
        for k, v in ECOLOGICAL_PRACTICES.items()
        if v["category"] == category
    ]


def get_companions(crop_id: str) -> Optional[dict]:
    """
    Get companion planting info for a crop
    الحصول على معلومات الزراعة التصاحبية لمحصول معين
    """
    return COMPANION_PLANTING.get(crop_id)


def search_practices(query: str, lang: str = "ar") -> list[dict]:
    """
    Search practices by name or description
    البحث في الممارسات بالاسم أو الوصف
    """
    results = []
    query_lower = query.lower()

    for practice_id, practice in ECOLOGICAL_PRACTICES.items():
        name_field = "name_ar" if lang == "ar" else "name_en"
        desc_field = "description_ar" if lang == "ar" else "description_en"

        if query_lower in practice[name_field].lower():
            results.append({"id": practice_id, **practice, "match": "name"})
        elif query_lower in practice[desc_field].lower():
            results.append({"id": practice_id, **practice, "match": "description"})

    return results


def get_globalgap_practices(control_point: str) -> list[dict]:
    """
    Get practices that fulfill a specific GlobalGAP control point
    الحصول على الممارسات التي تحقق نقطة تحكم GlobalGAP معينة
    """
    results = []
    for principle_id, principle in ECOLOGICAL_PRINCIPLES.items():
        if control_point in principle.get("globalgap_cp", []):
            results.append({"id": principle_id, **principle, "type": "principle"})

    return results


def calculate_transition_timeline(
    current_practices: list[str],
    target_practices: list[str],
) -> dict:
    """
    Calculate estimated timeline for ecological transition
    حساب الجدول الزمني المقدر للتحول الإيكولوجي
    """
    total_months = 0
    timeline = []

    for practice_id in target_practices:
        if practice_id in current_practices:
            continue

        practice = ECOLOGICAL_PRACTICES.get(practice_id)
        if not practice:
            continue

        # Estimate based on difficulty
        difficulty_months = {
            "easy": 1,
            "medium": 3,
            "hard": 6,
        }
        setup_months = difficulty_months.get(practice.get("difficulty", "medium"), 3)

        timeline.append({
            "practice_id": practice_id,
            "name_ar": practice["name_ar"],
            "name_en": practice["name_en"],
            "start_month": total_months,
            "setup_duration": setup_months,
        })

        total_months += setup_months

    return {
        "total_months": total_months,
        "timeline": timeline,
        "new_practices_count": len(timeline),
    }
