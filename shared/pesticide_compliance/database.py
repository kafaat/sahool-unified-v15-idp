"""
Pesticide Database - قاعدة بيانات المبيدات
Contains registered pesticides with PHI/REI information
"""

from __future__ import annotations

from .models import (
    MixCompatibility,
    Pesticide,
    PesticideCategory,
    PPELevel,
    PPERequirement,
    ToxicityClass,
)

# Standard PPE configurations
PPE_MINIMAL = PPERequirement(
    level=PPELevel.MINIMAL,
    gloves="Chemical-resistant gloves",
    gloves_ar="قفازات مقاومة للكيماويات",
    respirator="None required for outdoor use",
    respirator_ar="غير مطلوبة للاستخدام الخارجي",
    eye_protection="Safety glasses",
    eye_protection_ar="نظارات واقية",
    clothing="Long sleeves, long pants",
    clothing_ar="أكمام طويلة، بنطلون طويل",
    footwear="Waterproof boots",
    footwear_ar="أحذية مقاومة للماء",
)

PPE_STANDARD = PPERequirement(
    level=PPELevel.STANDARD,
    gloves="Nitrile or neoprene gloves",
    gloves_ar="قفازات نيتريل أو نيوبرين",
    respirator="N95 or dust mask",
    respirator_ar="كمامة N95 أو قناع غبار",
    eye_protection="Goggles or face shield",
    eye_protection_ar="نظارات واقية أو واقي وجه",
    clothing="Coveralls or protective suit",
    clothing_ar="بدلة واقية كاملة",
    footwear="Chemical-resistant boots",
    footwear_ar="أحذية مقاومة للكيماويات",
)

PPE_ENHANCED = PPERequirement(
    level=PPELevel.ENHANCED,
    gloves="Double nitrile gloves",
    gloves_ar="قفازات نيتريل مزدوجة",
    respirator="Half-face respirator with organic vapor cartridge",
    respirator_ar="قناع نصف وجه مع خرطوشة بخار عضوي",
    eye_protection="Tight-fitting goggles",
    eye_protection_ar="نظارات واقية محكمة",
    clothing="Chemical-resistant coveralls",
    clothing_ar="بدلة مقاومة للكيماويات",
    footwear="Chemical-resistant boots with covers",
    footwear_ar="أحذية مقاومة للكيماويات مع أغطية",
    additional=["Chemical-resistant apron", "Head covering"],
    additional_ar=["مريلة مقاومة للكيماويات", "غطاء رأس"],
)

PPE_MAXIMUM = PPERequirement(
    level=PPELevel.MAXIMUM,
    gloves="Double chemical-resistant gloves",
    gloves_ar="قفازات مزدوجة مقاومة للكيماويات",
    respirator="Full-face respirator with combination cartridge",
    respirator_ar="قناع وجه كامل مع خرطوشة مركبة",
    eye_protection="Integrated in full-face respirator",
    eye_protection_ar="مدمجة في قناع الوجه الكامل",
    clothing="Encapsulated chemical suit",
    clothing_ar="بدلة كيميائية مغلقة",
    footwear="Chemical-resistant boots, taped to suit",
    footwear_ar="أحذية مقاومة للكيماويات، ملصقة بالبدلة",
    additional=["Air-supplied if enclosed area", "Decontamination station nearby"],
    additional_ar=["تزويد هواء للأماكن المغلقة", "محطة إزالة التلوث قريبة"],
)


# Pesticide Database - قاعدة بيانات المبيدات المسجلة
PESTICIDE_DATABASE: dict[str, Pesticide] = {
    # ============== INSECTICIDES - مبيدات حشرية ==============
    "imidacloprid_200sl": Pesticide(
        id="imidacloprid_200sl",
        trade_name="Confidor 200 SL",
        trade_name_ar="كونفيدور 200 إس إل",
        active_ingredient="Imidacloprid",
        active_ingredient_ar="إيميداكلوبريد",
        category=PesticideCategory.INSECTICIDE,
        toxicity_class=ToxicityClass.II,
        phi_days=21,
        rei_hours=12,
        max_applications_per_season=3,
        min_days_between_applications=7,
        registered_crops=["tomato", "cucumber", "pepper", "wheat", "cotton"],
        ppe_requirements=PPE_STANDARD,
        registration_number="SA-INS-001",
        formulation="Soluble Liquid (SL)",
        manufacturer="Bayer",
        notes="Systemic insecticide for sucking insects",
        notes_ar="مبيد حشري جهازي للحشرات الماصة",
    ),
    "lambda_cyhalothrin_5ec": Pesticide(
        id="lambda_cyhalothrin_5ec",
        trade_name="Karate Zeon 5 EC",
        trade_name_ar="كاراتيه زيون 5 إي سي",
        active_ingredient="Lambda-cyhalothrin",
        active_ingredient_ar="لامبدا-سايهالوثرين",
        category=PesticideCategory.INSECTICIDE,
        toxicity_class=ToxicityClass.II,
        phi_days=7,
        rei_hours=24,
        max_applications_per_season=4,
        min_days_between_applications=7,
        registered_crops=["wheat", "barley", "cotton", "vegetables"],
        ppe_requirements=PPE_ENHANCED,
        registration_number="SA-INS-002",
        formulation="Emulsifiable Concentrate (EC)",
        manufacturer="Syngenta",
        notes="Contact and stomach poison for lepidopteran pests",
        notes_ar="سم تلامسي ومعدي لآفات حرشفية الأجنحة",
    ),
    "chlorpyrifos_48ec": Pesticide(
        id="chlorpyrifos_48ec",
        trade_name="Dursban 48 EC",
        trade_name_ar="دورسبان 48 إي سي",
        active_ingredient="Chlorpyrifos",
        active_ingredient_ar="كلوربيريفوس",
        category=PesticideCategory.INSECTICIDE,
        toxicity_class=ToxicityClass.II,
        phi_days=21,
        rei_hours=24,
        max_applications_per_season=2,
        min_days_between_applications=14,
        registered_crops=["citrus", "cotton", "corn"],
        ppe_requirements=PPE_ENHANCED,
        registration_number="SA-INS-003",
        is_restricted=True,
        formulation="Emulsifiable Concentrate (EC)",
        manufacturer="Corteva",
        notes="Organophosphate - restricted use",
        notes_ar="مركب فسفوري عضوي - مقيد الاستخدام",
    ),
    "emamectin_benzoate_5sg": Pesticide(
        id="emamectin_benzoate_5sg",
        trade_name="Proclaim 5 SG",
        trade_name_ar="بروكليم 5 إس جي",
        active_ingredient="Emamectin benzoate",
        active_ingredient_ar="إمامكتين بنزوات",
        category=PesticideCategory.INSECTICIDE,
        toxicity_class=ToxicityClass.III,
        phi_days=7,
        rei_hours=12,
        max_applications_per_season=4,
        min_days_between_applications=7,
        registered_crops=["tomato", "pepper", "cotton", "cabbage"],
        ppe_requirements=PPE_STANDARD,
        registration_number="SA-INS-004",
        formulation="Soluble Granule (SG)",
        manufacturer="Syngenta",
        notes="For caterpillars and leaf miners",
        notes_ar="ليرقات وصانعات الأنفاق",
    ),
    "spinosad_480sc": Pesticide(
        id="spinosad_480sc",
        trade_name="Tracer 480 SC",
        trade_name_ar="تريسر 480 إس سي",
        active_ingredient="Spinosad",
        active_ingredient_ar="سبينوساد",
        category=PesticideCategory.INSECTICIDE,
        toxicity_class=ToxicityClass.III,
        phi_days=3,
        rei_hours=4,
        max_applications_per_season=6,
        min_days_between_applications=5,
        registered_crops=["tomato", "pepper", "grape", "citrus", "vegetables"],
        ppe_requirements=PPE_MINIMAL,
        registration_number="SA-INS-005",
        is_organic_approved=True,
        formulation="Suspension Concentrate (SC)",
        manufacturer="Corteva",
        notes="OMRI approved for organic farming",
        notes_ar="معتمد للزراعة العضوية",
    ),
    # ============== FUNGICIDES - مبيدات فطرية ==============
    "mancozeb_80wp": Pesticide(
        id="mancozeb_80wp",
        trade_name="Dithane M-45",
        trade_name_ar="ديثان إم-45",
        active_ingredient="Mancozeb",
        active_ingredient_ar="مانكوزيب",
        category=PesticideCategory.FUNGICIDE,
        toxicity_class=ToxicityClass.U,
        phi_days=7,
        rei_hours=24,
        max_applications_per_season=8,
        min_days_between_applications=7,
        registered_crops=["tomato", "potato", "grape", "wheat", "vegetables"],
        ppe_requirements=PPE_STANDARD,
        registration_number="SA-FUN-001",
        formulation="Wettable Powder (WP)",
        manufacturer="UPL",
        notes="Protectant fungicide, multi-site activity",
        notes_ar="مبيد فطري وقائي، متعدد مواقع التأثير",
    ),
    "azoxystrobin_250sc": Pesticide(
        id="azoxystrobin_250sc",
        trade_name="Amistar 250 SC",
        trade_name_ar="أميستار 250 إس سي",
        active_ingredient="Azoxystrobin",
        active_ingredient_ar="أزوكسيستروبين",
        category=PesticideCategory.FUNGICIDE,
        toxicity_class=ToxicityClass.U,
        phi_days=14,
        rei_hours=4,
        max_applications_per_season=4,
        min_days_between_applications=10,
        registered_crops=["wheat", "barley", "grape", "vegetables", "rice"],
        ppe_requirements=PPE_MINIMAL,
        registration_number="SA-FUN-002",
        formulation="Suspension Concentrate (SC)",
        manufacturer="Syngenta",
        notes="Strobilurin fungicide, systemic and translaminar",
        notes_ar="مبيد فطري ستروبيلورين، جهازي وعابر للأوراق",
    ),
    "tebuconazole_250ew": Pesticide(
        id="tebuconazole_250ew",
        trade_name="Folicur 250 EW",
        trade_name_ar="فوليكور 250 إي دبليو",
        active_ingredient="Tebuconazole",
        active_ingredient_ar="تيبوكونازول",
        category=PesticideCategory.FUNGICIDE,
        toxicity_class=ToxicityClass.III,
        phi_days=21,
        rei_hours=12,
        max_applications_per_season=3,
        min_days_between_applications=14,
        registered_crops=["wheat", "barley", "grape", "banana", "vegetables"],
        ppe_requirements=PPE_STANDARD,
        registration_number="SA-FUN-003",
        formulation="Emulsion Water (EW)",
        manufacturer="Bayer",
        notes="Triazole fungicide, curative and protectant",
        notes_ar="مبيد فطري ترايازول، علاجي ووقائي",
    ),
    "copper_hydroxide_50wp": Pesticide(
        id="copper_hydroxide_50wp",
        trade_name="Kocide 3000",
        trade_name_ar="كوسايد 3000",
        active_ingredient="Copper hydroxide",
        active_ingredient_ar="هيدروكسيد النحاس",
        category=PesticideCategory.FUNGICIDE,
        toxicity_class=ToxicityClass.III,
        phi_days=1,
        rei_hours=24,
        max_applications_per_season=10,
        min_days_between_applications=7,
        registered_crops=["tomato", "potato", "citrus", "grape", "vegetables"],
        ppe_requirements=PPE_STANDARD,
        registration_number="SA-FUN-004",
        is_organic_approved=True,
        formulation="Wettable Powder (WP)",
        manufacturer="Certis",
        notes="OMRI approved copper fungicide",
        notes_ar="مبيد فطري نحاسي معتمد للزراعة العضوية",
    ),
    # ============== HERBICIDES - مبيدات أعشاب ==============
    "glyphosate_480sl": Pesticide(
        id="glyphosate_480sl",
        trade_name="Roundup 480 SL",
        trade_name_ar="راوند أب 480 إس إل",
        active_ingredient="Glyphosate",
        active_ingredient_ar="غليفوسات",
        category=PesticideCategory.HERBICIDE,
        toxicity_class=ToxicityClass.III,
        phi_days=14,
        rei_hours=4,
        max_applications_per_season=2,
        min_days_between_applications=30,
        registered_crops=["non-crop", "orchards", "vineyards"],
        ppe_requirements=PPE_MINIMAL,
        registration_number="SA-HER-001",
        formulation="Soluble Liquid (SL)",
        manufacturer="Bayer",
        notes="Non-selective post-emergence herbicide",
        notes_ar="مبيد أعشاب غير انتقائي بعد الإنبات",
    ),
    "2_4_d_amine_720sl": Pesticide(
        id="2_4_d_amine_720sl",
        trade_name="Weedar 64",
        trade_name_ar="ويدار 64",
        active_ingredient="2,4-D amine",
        active_ingredient_ar="2,4-د أمين",
        category=PesticideCategory.HERBICIDE,
        toxicity_class=ToxicityClass.II,
        phi_days=14,
        rei_hours=48,
        max_applications_per_season=2,
        min_days_between_applications=21,
        registered_crops=["wheat", "barley", "corn", "pasture"],
        ppe_requirements=PPE_STANDARD,
        registration_number="SA-HER-002",
        formulation="Soluble Liquid (SL)",
        manufacturer="Nufarm",
        notes="Selective broadleaf herbicide for cereals",
        notes_ar="مبيد أعشاب عريضة الأوراق انتقائي للحبوب",
    ),
    "pendimethalin_455cs": Pesticide(
        id="pendimethalin_455cs",
        trade_name="Prowl H2O",
        trade_name_ar="براول إتش 2 أو",
        active_ingredient="Pendimethalin",
        active_ingredient_ar="بنديميثالين",
        category=PesticideCategory.HERBICIDE,
        toxicity_class=ToxicityClass.III,
        phi_days=60,
        rei_hours=24,
        max_applications_per_season=2,
        min_days_between_applications=30,
        registered_crops=["cotton", "corn", "wheat", "vegetables"],
        ppe_requirements=PPE_STANDARD,
        registration_number="SA-HER-003",
        formulation="Capsule Suspension (CS)",
        manufacturer="BASF",
        notes="Pre-emergence grass and broadleaf control",
        notes_ar="مبيد ما قبل الإنبات للحشائش والأعشاب العريضة",
    ),
    # ============== ACARICIDES - مبيدات عناكب ==============
    "abamectin_18ec": Pesticide(
        id="abamectin_18ec",
        trade_name="Vertimec 1.8 EC",
        trade_name_ar="فيرتيميك 1.8 إي سي",
        active_ingredient="Abamectin",
        active_ingredient_ar="أباميكتين",
        category=PesticideCategory.ACARICIDE,
        toxicity_class=ToxicityClass.II,
        phi_days=7,
        rei_hours=12,
        max_applications_per_season=3,
        min_days_between_applications=7,
        registered_crops=["tomato", "cucumber", "pepper", "citrus", "cotton"],
        ppe_requirements=PPE_ENHANCED,
        registration_number="SA-ACA-001",
        formulation="Emulsifiable Concentrate (EC)",
        manufacturer="Syngenta",
        notes="For mites and leaf miners",
        notes_ar="للعناكب وصانعات الأنفاق",
    ),
    "spiromesifen_240sc": Pesticide(
        id="spiromesifen_240sc",
        trade_name="Oberon 240 SC",
        trade_name_ar="أوبيرون 240 إس سي",
        active_ingredient="Spiromesifen",
        active_ingredient_ar="سبيروميسيفين",
        category=PesticideCategory.ACARICIDE,
        toxicity_class=ToxicityClass.U,
        phi_days=3,
        rei_hours=12,
        max_applications_per_season=3,
        min_days_between_applications=7,
        registered_crops=["tomato", "cucumber", "pepper", "strawberry"],
        ppe_requirements=PPE_MINIMAL,
        registration_number="SA-ACA-002",
        formulation="Suspension Concentrate (SC)",
        manufacturer="Bayer",
        notes="For mites and whiteflies, lipid biosynthesis inhibitor",
        notes_ar="للعناكب والذبابة البيضاء، مثبط تخليق الدهون",
    ),
}


# Tank Mix Compatibility Matrix - مصفوفة توافق الخلط
# Format: (product_a, product_b) -> (compatibility, warnings_en, warnings_ar, mixing_order)
TANK_MIX_COMPATIBILITY: dict[tuple[str, str], tuple[MixCompatibility, list[str], list[str], list[str]]] = {
    # Fungicide + Insecticide combinations
    ("mancozeb_80wp", "imidacloprid_200sl"): (
        MixCompatibility.COMPATIBLE,
        ["Add mancozeb first, mix well, then add imidacloprid"],
        ["أضف مانكوزيب أولاً، امزج جيداً، ثم أضف إيميداكلوبريد"],
        ["mancozeb_80wp", "imidacloprid_200sl"],
    ),
    ("azoxystrobin_250sc", "lambda_cyhalothrin_5ec"): (
        MixCompatibility.COMPATIBLE,
        ["Compatible, standard mixing order"],
        ["متوافق، ترتيب خلط قياسي"],
        ["azoxystrobin_250sc", "lambda_cyhalothrin_5ec"],
    ),
    ("tebuconazole_250ew", "emamectin_benzoate_5sg"): (
        MixCompatibility.COMPATIBLE,
        ["Good compatibility"],
        ["توافق جيد"],
        ["tebuconazole_250ew", "emamectin_benzoate_5sg"],
    ),
    # Problematic combinations
    ("copper_hydroxide_50wp", "mancozeb_80wp"): (
        MixCompatibility.CAUTION,
        ["May increase phytotoxicity risk in hot weather", "Reduce rates by 20%"],
        ["قد يزيد خطر السمية النباتية في الطقس الحار", "خفض المعدلات بنسبة 20%"],
        ["copper_hydroxide_50wp", "mancozeb_80wp"],
    ),
    ("glyphosate_480sl", "2_4_d_amine_720sl"): (
        MixCompatibility.CAUTION,
        ["May reduce glyphosate efficacy", "Apply in sequence if possible"],
        ["قد يقلل من فعالية الغليفوسات", "طبق بالتتابع إن أمكن"],
        ["2_4_d_amine_720sl", "glyphosate_480sl"],
    ),
    # Incompatible combinations
    ("copper_hydroxide_50wp", "chlorpyrifos_48ec"): (
        MixCompatibility.INCOMPATIBLE,
        [
            "Copper products are incompatible with most organophosphates",
            "May cause chemical breakdown",
        ],
        ["منتجات النحاس غير متوافقة مع معظم المركبات الفسفورية العضوية", "قد يسبب تحلل كيميائي"],
        [],
    ),
    ("abamectin_18ec", "copper_hydroxide_50wp"): (
        MixCompatibility.INCOMPATIBLE,
        ["Abamectin is unstable with copper compounds", "Increased risk of phytotoxicity"],
        ["أباميكتين غير مستقر مع مركبات النحاس", "زيادة خطر السمية النباتية"],
        [],
    ),
    ("pendimethalin_455cs", "glyphosate_480sl"): (
        MixCompatibility.INCOMPATIBLE,
        ["Physical incompatibility - forms precipitate", "Apply separately with 24h interval"],
        ["عدم توافق فيزيائي - يكون راسب", "طبق بشكل منفصل مع فاصل 24 ساعة"],
        [],
    ),
}


def get_pesticide(pesticide_id: str) -> Pesticide | None:
    """Get pesticide by ID"""
    return PESTICIDE_DATABASE.get(pesticide_id)


def search_pesticides(
    query: str,
    category: PesticideCategory | None = None,
    crop: str | None = None,
    organic_only: bool = False,
) -> list[Pesticide]:
    """Search pesticides by name, active ingredient, or crop"""
    results = []
    query_lower = query.lower()

    for pesticide in PESTICIDE_DATABASE.values():
        # Filter by category
        if category and pesticide.category != category:
            continue

        # Filter by crop
        if crop and crop.lower() not in [c.lower() for c in pesticide.registered_crops]:
            continue

        # Filter by organic
        if organic_only and not pesticide.is_organic_approved:
            continue

        # Search by name or active ingredient
        if (
            query_lower in pesticide.trade_name.lower()
            or query_lower in pesticide.trade_name_ar
            or query_lower in pesticide.active_ingredient.lower()
            or query_lower in pesticide.active_ingredient_ar
        ):
            results.append(pesticide)

    return results


def get_tank_mix_compatibility(
    product_a_id: str, product_b_id: str
) -> tuple[MixCompatibility, list[str], list[str], list[str]]:
    """Get tank mix compatibility between two products"""
    # Check both orders
    key1 = (product_a_id, product_b_id)
    key2 = (product_b_id, product_a_id)

    if key1 in TANK_MIX_COMPATIBILITY:
        return TANK_MIX_COMPATIBILITY[key1]
    elif key2 in TANK_MIX_COMPATIBILITY:
        result = TANK_MIX_COMPATIBILITY[key2]
        # Reverse mixing order if needed
        return (result[0], result[1], result[2], result[3][::-1] if result[3] else [])
    else:
        # Unknown combination
        return (
            MixCompatibility.UNKNOWN,
            ["Compatibility not tested - conduct jar test before mixing"],
            ["التوافق غير مختبر - أجرِ اختبار الجرة قبل الخلط"],
            [],
        )
