"""
SAHOOL Unified Crop Catalog
كتالوج المحاصيل الموحد لمنصة سهول

Based on:
- FAO FAOSTAT classification
- ICRISAT crop codes
- Yemen agricultural context
- MIAPPE ontology

Last updated: December 2025
"""

from dataclasses import dataclass
from enum import Enum


class CropCategory(str, Enum):
    """تصنيفات المحاصيل الرئيسية"""

    CEREALS = "cereals"  # الحبوب
    LEGUMES = "legumes"  # البقوليات
    VEGETABLES = "vegetables"  # الخضروات
    FRUITS = "fruits"  # الفواكه
    OILSEEDS = "oilseeds"  # البذور الزيتية
    FIBER = "fiber"  # الألياف
    SUGAR = "sugar"  # السكريات
    STIMULANTS = "stimulants"  # المنبهات
    SPICES = "spices"  # التوابل والأعشاب
    FODDER = "fodder"  # الأعلاف
    TUBERS = "tubers"  # الدرنيات


class GrowthHabit(str, Enum):
    """طريقة النمو"""

    ANNUAL = "annual"  # حولي
    PERENNIAL = "perennial"  # معمر
    BIENNIAL = "biennial"  # ثنائي الحول


class WaterRequirement(str, Enum):
    """متطلبات المياه"""

    VERY_LOW = "very_low"  # منخفضة جداً (<300mm)
    LOW = "low"  # منخفضة (300-500mm)
    MEDIUM = "medium"  # متوسطة (500-800mm)
    HIGH = "high"  # عالية (800-1200mm)
    VERY_HIGH = "very_high"  # عالية جداً (>1200mm)


@dataclass
class CropInfo:
    """معلومات المحصول الشاملة"""

    code: str  # رمز المحصول (FAO-based)
    name_en: str  # الاسم بالإنجليزية
    name_ar: str  # الاسم بالعربية
    scientific_name: str  # الاسم العلمي
    category: CropCategory  # التصنيف
    growth_habit: GrowthHabit  # طريقة النمو

    # Growing conditions
    growing_season_days: int  # مدة الموسم (أيام)
    optimal_temp_min: float  # درجة الحرارة المثلى (الصغرى)
    optimal_temp_max: float  # درجة الحرارة المثلى (الكبرى)
    water_requirement: WaterRequirement  # متطلبات المياه

    # Yield data
    base_yield_ton_ha: float  # الإنتاجية الأساسية (طن/هكتار)
    yield_unit: str = "ton/ha"  # وحدة القياس

    # Yemen specific
    yemen_regions: list[str] = None  # المناطق اليمنية المناسبة
    local_varieties: list[str] = None  # الأصناف المحلية

    # FAO Kc coefficients (optional)
    kc_ini: float | None = None  # معامل المحصول الأولي
    kc_mid: float | None = None  # معامل المحصول الأقصى
    kc_end: float | None = None  # معامل المحصول النهائي

    # Economic data (USD/ton)
    price_usd_per_ton: float | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# CEREALS - الحبوب
# ═══════════════════════════════════════════════════════════════════════════════

CEREALS = {
    "WHEAT": CropInfo(
        code="WHEAT",
        name_en="Wheat",
        name_ar="قمح",
        scientific_name="Triticum aestivum",
        category=CropCategory.CEREALS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=120,
        optimal_temp_min=15,
        optimal_temp_max=25,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=2.5,
        yemen_regions=["تهامة", "الجوف", "مأرب", "صعدة"],
        local_varieties=["بلدي", "شامي"],
        kc_ini=0.3,
        kc_mid=1.15,
        kc_end=0.25,
        price_usd_per_ton=350,
    ),
    "BARLEY": CropInfo(
        code="BARLEY",
        name_en="Barley",
        name_ar="شعير",
        scientific_name="Hordeum vulgare",
        category=CropCategory.CEREALS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=12,
        optimal_temp_max=22,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=2.0,
        yemen_regions=["المرتفعات", "صعدة", "عمران"],
        local_varieties=["بلدي", "أبيض"],
        kc_ini=0.3,
        kc_mid=1.15,
        kc_end=0.25,
        price_usd_per_ton=280,
    ),
    "CORN": CropInfo(
        code="CORN",
        name_en="Corn/Maize",
        name_ar="ذرة شامية",
        scientific_name="Zea mays",
        category=CropCategory.CEREALS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=20,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=4.0,
        yemen_regions=["تهامة", "وادي حضرموت"],
        local_varieties=["أصفر", "أبيض"],
        kc_ini=0.3,
        kc_mid=1.20,
        kc_end=0.35,
        price_usd_per_ton=280,
    ),
    "SORGHUM": CropInfo(
        code="SORGHUM",
        name_en="Sorghum",
        name_ar="ذرة رفيعة",
        scientific_name="Sorghum bicolor",
        category=CropCategory.CEREALS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=110,
        optimal_temp_min=25,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=2.0,
        yemen_regions=["تهامة", "الحديدة", "لحج"],
        local_varieties=["بيضاء", "حمراء", "ذهبية"],
        kc_ini=0.3,
        kc_mid=1.0,
        kc_end=0.55,
        price_usd_per_ton=250,
    ),
    "MILLET": CropInfo(
        code="MILLET",
        name_en="Pearl Millet",
        name_ar="دخن",
        scientific_name="Pennisetum glaucum",
        category=CropCategory.CEREALS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=90,
        optimal_temp_min=25,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.VERY_LOW,
        base_yield_ton_ha=1.5,
        yemen_regions=["تهامة", "الحديدة"],
        local_varieties=["بلدي"],
        kc_ini=0.3,
        kc_mid=1.0,
        kc_end=0.30,
        price_usd_per_ton=300,
    ),
    "RICE": CropInfo(
        code="RICE",
        name_en="Rice",
        name_ar="أرز",
        scientific_name="Oryza sativa",
        category=CropCategory.CEREALS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=120,
        optimal_temp_min=22,
        optimal_temp_max=32,
        water_requirement=WaterRequirement.VERY_HIGH,
        base_yield_ton_ha=4.0,
        yemen_regions=["وادي حضرموت"],
        kc_ini=1.05,
        kc_mid=1.20,
        kc_end=0.90,
        price_usd_per_ton=500,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# LEGUMES - البقوليات
# ═══════════════════════════════════════════════════════════════════════════════

LEGUMES = {
    "FABA_BEAN": CropInfo(
        code="FABA_BEAN",
        name_en="Faba Bean",
        name_ar="فول",
        scientific_name="Vicia faba",
        category=CropCategory.LEGUMES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=120,
        optimal_temp_min=15,
        optimal_temp_max=22,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=2.5,
        yemen_regions=["المرتفعات", "إب", "ذمار"],
        local_varieties=["بلدي", "مصري"],
        kc_ini=0.5,
        kc_mid=1.15,
        kc_end=1.10,
        price_usd_per_ton=600,
    ),
    "LENTIL": CropInfo(
        code="LENTIL",
        name_en="Lentil",
        name_ar="عدس",
        scientific_name="Lens culinaris",
        category=CropCategory.LEGUMES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=10,
        optimal_temp_max=20,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=1.0,
        yemen_regions=["المرتفعات", "صعدة"],
        kc_ini=0.4,
        kc_mid=1.1,
        kc_end=0.3,
        price_usd_per_ton=800,
    ),
    "CHICKPEA": CropInfo(
        code="CHICKPEA",
        name_en="Chickpea",
        name_ar="حمص",
        scientific_name="Cicer arietinum",
        category=CropCategory.LEGUMES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=15,
        optimal_temp_max=25,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=1.2,
        yemen_regions=["المرتفعات"],
        kc_ini=0.4,
        kc_mid=1.0,
        kc_end=0.35,
        price_usd_per_ton=900,
    ),
    "COWPEA": CropInfo(
        code="COWPEA",
        name_en="Cowpea",
        name_ar="لوبيا",
        scientific_name="Vigna unguiculata",
        category=CropCategory.LEGUMES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=80,
        optimal_temp_min=25,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=1.5,
        yemen_regions=["تهامة", "لحج"],
        kc_ini=0.4,
        kc_mid=1.05,
        kc_end=0.60,
        price_usd_per_ton=700,
    ),
    "GREEN_BEAN": CropInfo(
        code="GREEN_BEAN",
        name_en="Green Bean",
        name_ar="فاصوليا خضراء",
        scientific_name="Phaseolus vulgaris",
        category=CropCategory.LEGUMES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=70,
        optimal_temp_min=18,
        optimal_temp_max=28,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=12.0,
        yemen_regions=["المرتفعات", "إب"],
        kc_ini=0.4,
        kc_mid=1.15,
        kc_end=0.35,
        price_usd_per_ton=500,
    ),
    "PEANUT": CropInfo(
        code="PEANUT",
        name_en="Peanut/Groundnut",
        name_ar="فول سوداني",
        scientific_name="Arachis hypogaea",
        category=CropCategory.LEGUMES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=120,
        optimal_temp_min=25,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=2.0,
        yemen_regions=["تهامة", "لحج"],
        kc_ini=0.4,
        kc_mid=1.15,
        kc_end=0.60,
        price_usd_per_ton=1000,
    ),
    "FENUGREEK": CropInfo(
        code="FENUGREEK",
        name_en="Fenugreek",
        name_ar="حلبة",
        scientific_name="Trigonella foenum-graecum",
        category=CropCategory.LEGUMES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=90,
        optimal_temp_min=10,
        optimal_temp_max=25,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=1.5,
        yemen_regions=["المرتفعات", "صنعاء", "ذمار"],
        local_varieties=["بلدي يمني"],
        kc_ini=0.4,
        kc_mid=1.0,
        kc_end=0.35,
        price_usd_per_ton=1500,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# VEGETABLES - الخضروات
# ═══════════════════════════════════════════════════════════════════════════════

VEGETABLES = {
    "TOMATO": CropInfo(
        code="TOMATO",
        name_en="Tomato",
        name_ar="طماطم",
        scientific_name="Solanum lycopersicum",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=90,
        optimal_temp_min=18,
        optimal_temp_max=28,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=35.0,
        yemen_regions=["المرتفعات", "تهامة", "وادي حضرموت"],
        local_varieties=["بلدي", "هجين"],
        kc_ini=0.6,
        kc_mid=1.15,
        kc_end=0.80,
        price_usd_per_ton=400,
    ),
    "POTATO": CropInfo(
        code="POTATO",
        name_en="Potato",
        name_ar="بطاطس",
        scientific_name="Solanum tuberosum",
        category=CropCategory.TUBERS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=15,
        optimal_temp_max=22,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=20.0,
        yemen_regions=["المرتفعات", "ذمار", "إب"],
        local_varieties=["سبونتا", "دايمونت"],
        kc_ini=0.5,
        kc_mid=1.15,
        kc_end=0.75,
        price_usd_per_ton=320,
    ),
    "ONION": CropInfo(
        code="ONION",
        name_en="Onion",
        name_ar="بصل",
        scientific_name="Allium cepa",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.BIENNIAL,
        growing_season_days=120,
        optimal_temp_min=13,
        optimal_temp_max=25,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=25.0,
        yemen_regions=["المرتفعات", "تهامة"],
        local_varieties=["أحمر يمني", "أبيض"],
        kc_ini=0.7,
        kc_mid=1.05,
        kc_end=0.75,
        price_usd_per_ton=350,
    ),
    "GARLIC": CropInfo(
        code="GARLIC",
        name_en="Garlic",
        name_ar="ثوم",
        scientific_name="Allium sativum",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=150,
        optimal_temp_min=10,
        optimal_temp_max=20,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=8.0,
        yemen_regions=["المرتفعات", "صعدة"],
        local_varieties=["بلدي"],
        kc_ini=0.7,
        kc_mid=1.0,
        kc_end=0.70,
        price_usd_per_ton=1500,
    ),
    "PEPPER": CropInfo(
        code="PEPPER",
        name_en="Bell Pepper",
        name_ar="فلفل حلو",
        scientific_name="Capsicum annuum",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=90,
        optimal_temp_min=18,
        optimal_temp_max=28,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=25.0,
        yemen_regions=["المرتفعات", "تهامة"],
        kc_ini=0.6,
        kc_mid=1.05,
        kc_end=0.90,
        price_usd_per_ton=600,
    ),
    "CHILI": CropInfo(
        code="CHILI",
        name_en="Chili Pepper",
        name_ar="فلفل حار",
        scientific_name="Capsicum frutescens",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=20,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=15.0,
        yemen_regions=["تهامة", "لحج"],
        local_varieties=["يمني حار"],
        kc_ini=0.6,
        kc_mid=1.05,
        kc_end=0.90,
        price_usd_per_ton=800,
    ),
    "EGGPLANT": CropInfo(
        code="EGGPLANT",
        name_en="Eggplant",
        name_ar="باذنجان",
        scientific_name="Solanum melongena",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=22,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=30.0,
        yemen_regions=["المرتفعات", "تهامة"],
        kc_ini=0.6,
        kc_mid=1.05,
        kc_end=0.90,
        price_usd_per_ton=350,
    ),
    "CUCUMBER": CropInfo(
        code="CUCUMBER",
        name_en="Cucumber",
        name_ar="خيار",
        scientific_name="Cucumis sativus",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=60,
        optimal_temp_min=20,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=40.0,
        yemen_regions=["المرتفعات", "تهامة"],
        kc_ini=0.6,
        kc_mid=1.0,
        kc_end=0.75,
        price_usd_per_ton=300,
    ),
    "ZUCCHINI": CropInfo(
        code="ZUCCHINI",
        name_en="Zucchini/Squash",
        name_ar="كوسا",
        scientific_name="Cucurbita pepo",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=50,
        optimal_temp_min=18,
        optimal_temp_max=28,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=30.0,
        yemen_regions=["المرتفعات"],
        kc_ini=0.5,
        kc_mid=1.0,
        kc_end=0.80,
        price_usd_per_ton=280,
    ),
    "WATERMELON": CropInfo(
        code="WATERMELON",
        name_en="Watermelon",
        name_ar="بطيخ",
        scientific_name="Citrullus lanatus",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=90,
        optimal_temp_min=22,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=35.0,
        yemen_regions=["تهامة", "لحج"],
        kc_ini=0.4,
        kc_mid=1.0,
        kc_end=0.75,
        price_usd_per_ton=200,
    ),
    "CARROT": CropInfo(
        code="CARROT",
        name_en="Carrot",
        name_ar="جزر",
        scientific_name="Daucus carota",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.BIENNIAL,
        growing_season_days=100,
        optimal_temp_min=15,
        optimal_temp_max=22,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=35.0,
        yemen_regions=["المرتفعات"],
        kc_ini=0.7,
        kc_mid=1.05,
        kc_end=0.95,
        price_usd_per_ton=400,
    ),
    "CABBAGE": CropInfo(
        code="CABBAGE",
        name_en="Cabbage",
        name_ar="ملفوف",
        scientific_name="Brassica oleracea var. capitata",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.BIENNIAL,
        growing_season_days=90,
        optimal_temp_min=15,
        optimal_temp_max=22,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=40.0,
        yemen_regions=["المرتفعات"],
        kc_ini=0.7,
        kc_mid=1.05,
        kc_end=0.95,
        price_usd_per_ton=250,
    ),
    "LETTUCE": CropInfo(
        code="LETTUCE",
        name_en="Lettuce",
        name_ar="خس",
        scientific_name="Lactuca sativa",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=60,
        optimal_temp_min=12,
        optimal_temp_max=20,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=25.0,
        yemen_regions=["المرتفعات"],
        kc_ini=0.7,
        kc_mid=1.0,
        kc_end=0.95,
        price_usd_per_ton=400,
    ),
    "OKRA": CropInfo(
        code="OKRA",
        name_en="Okra",
        name_ar="بامية",
        scientific_name="Abelmoschus esculentus",
        category=CropCategory.VEGETABLES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=90,
        optimal_temp_min=25,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=12.0,
        yemen_regions=["تهامة", "لحج", "أبين"],
        local_varieties=["بلدي"],
        kc_ini=0.5,
        kc_mid=1.0,
        kc_end=0.90,
        price_usd_per_ton=600,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# FRUITS - الفواكه
# ═══════════════════════════════════════════════════════════════════════════════

FRUITS = {
    "DATE_PALM": CropInfo(
        code="DATE_PALM",
        name_en="Date Palm",
        name_ar="نخيل تمر",
        scientific_name="Phoenix dactylifera",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=180,
        optimal_temp_min=25,
        optimal_temp_max=40,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=8.0,
        yemen_regions=["وادي حضرموت", "شبوة", "المهرة"],
        local_varieties=["مدهول", "برحي", "خلاص", "سكري"],
        kc_ini=0.9,
        kc_mid=0.95,
        kc_end=0.95,
        price_usd_per_ton=1500,
    ),
    "MANGO": CropInfo(
        code="MANGO",
        name_en="Mango",
        name_ar="مانجو",
        scientific_name="Mangifera indica",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=150,
        optimal_temp_min=24,
        optimal_temp_max=32,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=10.0,
        yemen_regions=["تهامة", "لحج", "أبين"],
        local_varieties=["عويس", "زبدة", "هندي"],
        kc_ini=0.8,
        kc_mid=0.9,
        kc_end=0.85,
        price_usd_per_ton=800,
    ),
    "BANANA": CropInfo(
        code="BANANA",
        name_en="Banana",
        name_ar="موز",
        scientific_name="Musa acuminata",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=300,
        optimal_temp_min=22,
        optimal_temp_max=32,
        water_requirement=WaterRequirement.VERY_HIGH,
        base_yield_ton_ha=30.0,
        yemen_regions=["تهامة", "لحج"],
        local_varieties=["بلدي", "كافنديش"],
        kc_ini=0.5,
        kc_mid=1.1,
        kc_end=1.0,
        price_usd_per_ton=500,
    ),
    "GRAPE": CropInfo(
        code="GRAPE",
        name_en="Grape",
        name_ar="عنب",
        scientific_name="Vitis vinifera",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=170,
        optimal_temp_min=18,
        optimal_temp_max=28,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=12.0,
        yemen_regions=["المرتفعات", "صعدة", "عمران"],
        local_varieties=["بلدي", "رازقي", "عسيلي"],
        kc_ini=0.3,
        kc_mid=0.85,
        kc_end=0.45,
        price_usd_per_ton=700,
    ),
    "PAPAYA": CropInfo(
        code="PAPAYA",
        name_en="Papaya",
        name_ar="باباي",
        scientific_name="Carica papaya",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=270,
        optimal_temp_min=22,
        optimal_temp_max=32,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=40.0,
        yemen_regions=["تهامة", "لحج"],
        kc_ini=0.6,
        kc_mid=1.0,
        kc_end=0.80,
        price_usd_per_ton=400,
    ),
    "CITRUS_ORANGE": CropInfo(
        code="CITRUS_ORANGE",
        name_en="Orange",
        name_ar="برتقال",
        scientific_name="Citrus sinensis",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=300,
        optimal_temp_min=18,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=20.0,
        yemen_regions=["المرتفعات", "تهامة"],
        kc_ini=0.7,
        kc_mid=0.65,
        kc_end=0.65,
        price_usd_per_ton=450,
    ),
    "CITRUS_LEMON": CropInfo(
        code="CITRUS_LEMON",
        name_en="Lemon",
        name_ar="ليمون",
        scientific_name="Citrus limon",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=300,
        optimal_temp_min=18,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=15.0,
        yemen_regions=["المرتفعات", "تهامة"],
        kc_ini=0.7,
        kc_mid=0.65,
        kc_end=0.65,
        price_usd_per_ton=500,
    ),
    "POMEGRANATE": CropInfo(
        code="POMEGRANATE",
        name_en="Pomegranate",
        name_ar="رمان",
        scientific_name="Punica granatum",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=180,
        optimal_temp_min=18,
        optimal_temp_max=32,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=12.0,
        yemen_regions=["المرتفعات", "صعدة"],
        local_varieties=["بلدي يمني"],
        kc_ini=0.6,
        kc_mid=0.85,
        kc_end=0.65,
        price_usd_per_ton=700,
    ),
    "FIG": CropInfo(
        code="FIG",
        name_en="Fig",
        name_ar="تين",
        scientific_name="Ficus carica",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=150,
        optimal_temp_min=18,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=8.0,
        yemen_regions=["المرتفعات"],
        kc_ini=0.5,
        kc_mid=0.85,
        kc_end=0.75,
        price_usd_per_ton=800,
    ),
    "GUAVA": CropInfo(
        code="GUAVA",
        name_en="Guava",
        name_ar="جوافة",
        scientific_name="Psidium guajava",
        category=CropCategory.FRUITS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=180,
        optimal_temp_min=23,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=25.0,
        yemen_regions=["تهامة", "لحج"],
        kc_ini=0.6,
        kc_mid=0.85,
        kc_end=0.75,
        price_usd_per_ton=500,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# STIMULANTS & BEVERAGES - المنبهات والمشروبات
# ═══════════════════════════════════════════════════════════════════════════════

STIMULANTS = {
    "COFFEE": CropInfo(
        code="COFFEE",
        name_en="Yemeni Coffee",
        name_ar="بن يمني",
        scientific_name="Coffea arabica",
        category=CropCategory.STIMULANTS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=270,
        optimal_temp_min=18,
        optimal_temp_max=25,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=0.8,
        yemen_regions=["بني مطر", "حراز", "يافع", "حيمة", "برع"],
        local_varieties=["مخا", "متري", "برعي", "عديني", "حيمي", "يافعي"],
        kc_ini=0.9,
        kc_mid=0.95,
        kc_end=0.95,
        price_usd_per_ton=8000,
    ),
    "QAT": CropInfo(
        code="QAT",
        name_en="Qat/Khat",
        name_ar="قات",
        scientific_name="Catha edulis",
        category=CropCategory.STIMULANTS,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=365,
        optimal_temp_min=18,
        optimal_temp_max=28,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=4.0,
        yemen_regions=["صنعاء", "تعز", "إب", "ذمار"],
        local_varieties=["شامي", "بلدي", "مطري"],
        kc_ini=0.95,
        kc_mid=1.0,
        kc_end=0.95,
        price_usd_per_ton=3000,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# OILSEEDS - البذور الزيتية
# ═══════════════════════════════════════════════════════════════════════════════

OILSEEDS = {
    "SESAME": CropInfo(
        code="SESAME",
        name_en="Sesame",
        name_ar="سمسم",
        scientific_name="Sesamum indicum",
        category=CropCategory.OILSEEDS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=25,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=0.8,
        yemen_regions=["تهامة", "لحج"],
        local_varieties=["أبيض", "أحمر"],
        kc_ini=0.35,
        kc_mid=1.1,
        kc_end=0.25,
        price_usd_per_ton=2000,
    ),
    "SUNFLOWER": CropInfo(
        code="SUNFLOWER",
        name_en="Sunflower",
        name_ar="دوار الشمس",
        scientific_name="Helianthus annuus",
        category=CropCategory.OILSEEDS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=20,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=2.0,
        yemen_regions=["المرتفعات", "تهامة"],
        kc_ini=0.35,
        kc_mid=1.1,
        kc_end=0.35,
        price_usd_per_ton=600,
    ),
    "SOYBEAN": CropInfo(
        code="SOYBEAN",
        name_en="Soybean",
        name_ar="فول الصويا",
        scientific_name="Glycine max",
        category=CropCategory.OILSEEDS,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=120,
        optimal_temp_min=20,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=2.5,
        yemen_regions=["المرتفعات"],
        kc_ini=0.4,
        kc_mid=1.15,
        kc_end=0.50,
        price_usd_per_ton=450,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# FODDER - الأعلاف
# ═══════════════════════════════════════════════════════════════════════════════

FODDER = {
    "ALFALFA": CropInfo(
        code="ALFALFA",
        name_en="Alfalfa",
        name_ar="برسيم حجازي",
        scientific_name="Medicago sativa",
        category=CropCategory.FODDER,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=365,
        optimal_temp_min=15,
        optimal_temp_max=30,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=15.0,
        yield_unit="ton/ha/cut",
        yemen_regions=["وادي حضرموت", "المرتفعات"],
        kc_ini=0.4,
        kc_mid=1.2,
        kc_end=1.15,
        price_usd_per_ton=200,
    ),
    "CLOVER": CropInfo(
        code="CLOVER",
        name_en="Egyptian Clover",
        name_ar="برسيم مصري",
        scientific_name="Trifolium alexandrinum",
        category=CropCategory.FODDER,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=120,
        optimal_temp_min=15,
        optimal_temp_max=25,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=60.0,
        yield_unit="ton/ha (fresh)",
        yemen_regions=["المرتفعات", "تهامة"],
        kc_ini=0.4,
        kc_mid=1.05,
        kc_end=1.05,
        price_usd_per_ton=80,
    ),
    "RHODES_GRASS": CropInfo(
        code="RHODES_GRASS",
        name_en="Rhodes Grass",
        name_ar="جت (حشيشة رودس)",
        scientific_name="Chloris gayana",
        category=CropCategory.FODDER,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=365,
        optimal_temp_min=25,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=12.0,
        yield_unit="ton/ha/cut",
        yemen_regions=["تهامة", "لحج"],
        kc_ini=0.5,
        kc_mid=0.95,
        kc_end=0.85,
        price_usd_per_ton=150,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# SPICES - التوابل والأعشاب
# ═══════════════════════════════════════════════════════════════════════════════

SPICES = {
    "CORIANDER": CropInfo(
        code="CORIANDER",
        name_en="Coriander",
        name_ar="كزبرة",
        scientific_name="Coriandrum sativum",
        category=CropCategory.SPICES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=90,
        optimal_temp_min=15,
        optimal_temp_max=25,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=1.0,
        yemen_regions=["المرتفعات"],
        kc_ini=0.5,
        kc_mid=0.95,
        kc_end=0.70,
        price_usd_per_ton=2000,
    ),
    "CUMIN": CropInfo(
        code="CUMIN",
        name_en="Cumin",
        name_ar="كمون",
        scientific_name="Cuminum cyminum",
        category=CropCategory.SPICES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=100,
        optimal_temp_min=15,
        optimal_temp_max=25,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=0.5,
        yemen_regions=["المرتفعات", "صعدة"],
        kc_ini=0.35,
        kc_mid=0.95,
        kc_end=0.60,
        price_usd_per_ton=3500,
    ),
    "HENNA": CropInfo(
        code="HENNA",
        name_en="Henna",
        name_ar="حناء",
        scientific_name="Lawsonia inermis",
        category=CropCategory.SPICES,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=180,
        optimal_temp_min=25,
        optimal_temp_max=40,
        water_requirement=WaterRequirement.LOW,
        base_yield_ton_ha=3.0,
        yemen_regions=["تهامة", "وادي حضرموت"],
        local_varieties=["يمني بلدي"],
        kc_ini=0.5,
        kc_mid=0.85,
        kc_end=0.70,
        price_usd_per_ton=1000,
    ),
    "BASIL": CropInfo(
        code="BASIL",
        name_en="Basil",
        name_ar="ريحان",
        scientific_name="Ocimum basilicum",
        category=CropCategory.SPICES,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=90,
        optimal_temp_min=18,
        optimal_temp_max=28,
        water_requirement=WaterRequirement.MEDIUM,
        base_yield_ton_ha=15.0,
        yield_unit="ton/ha (fresh)",
        yemen_regions=["المرتفعات"],
        kc_ini=0.6,
        kc_mid=1.0,
        kc_end=0.90,
        price_usd_per_ton=500,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# FIBER CROPS - محاصيل الألياف
# ═══════════════════════════════════════════════════════════════════════════════

FIBER = {
    "COTTON": CropInfo(
        code="COTTON",
        name_en="Cotton",
        name_ar="قطن",
        scientific_name="Gossypium hirsutum",
        category=CropCategory.FIBER,
        growth_habit=GrowthHabit.ANNUAL,
        growing_season_days=150,
        optimal_temp_min=22,
        optimal_temp_max=32,
        water_requirement=WaterRequirement.HIGH,
        base_yield_ton_ha=2.5,
        yemen_regions=["تهامة", "لحج", "أبين"],
        local_varieties=["يمني طويل التيلة"],
        kc_ini=0.35,
        kc_mid=1.2,
        kc_end=0.60,
        price_usd_per_ton=1800,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# SUGAR CROPS - محاصيل السكر
# ═══════════════════════════════════════════════════════════════════════════════

SUGAR = {
    "SUGARCANE": CropInfo(
        code="SUGARCANE",
        name_en="Sugarcane",
        name_ar="قصب السكر",
        scientific_name="Saccharum officinarum",
        category=CropCategory.SUGAR,
        growth_habit=GrowthHabit.PERENNIAL,
        growing_season_days=360,
        optimal_temp_min=25,
        optimal_temp_max=35,
        water_requirement=WaterRequirement.VERY_HIGH,
        base_yield_ton_ha=80.0,
        yemen_regions=["تهامة", "لحج"],
        kc_ini=0.40,
        kc_mid=1.25,
        kc_end=0.75,
        price_usd_per_ton=50,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED CROP CATALOG
# ═══════════════════════════════════════════════════════════════════════════════

ALL_CROPS: dict[str, CropInfo] = {
    **CEREALS,
    **LEGUMES,
    **VEGETABLES,
    **FRUITS,
    **STIMULANTS,
    **OILSEEDS,
    **FODDER,
    **SPICES,
    **FIBER,
    **SUGAR,
}


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def get_crop(code: str) -> CropInfo | None:
    """Get crop by code"""
    return ALL_CROPS.get(code.upper())


def get_crops_by_category(category: CropCategory) -> list[CropInfo]:
    """Get all crops in a category"""
    return [crop for crop in ALL_CROPS.values() if crop.category == category]


def get_crops_by_water_requirement(requirement: WaterRequirement) -> list[CropInfo]:
    """Get crops by water requirement"""
    return [crop for crop in ALL_CROPS.values() if crop.water_requirement == requirement]


def get_crops_for_region(region: str) -> list[CropInfo]:
    """Get crops suitable for a Yemen region"""
    return [
        crop for crop in ALL_CROPS.values() if crop.yemen_regions and region in crop.yemen_regions
    ]


def search_crops(query: str) -> list[CropInfo]:
    """Search crops by name (English or Arabic)"""
    query_lower = query.lower()
    return [
        crop
        for crop in ALL_CROPS.values()
        if query_lower in crop.name_en.lower() or query in crop.name_ar
    ]


def get_crop_codes() -> list[str]:
    """Get all crop codes"""
    return list(ALL_CROPS.keys())


def get_crop_names_ar() -> dict[str, str]:
    """Get mapping of code to Arabic name"""
    return {code: crop.name_ar for code, crop in ALL_CROPS.items()}


def get_crop_names_en() -> dict[str, str]:
    """Get mapping of code to English name"""
    return {code: crop.name_en for code, crop in ALL_CROPS.items()}


# Statistics
TOTAL_CROPS = len(ALL_CROPS)
CATEGORIES_COUNT = {cat.value: len(get_crops_by_category(cat)) for cat in CropCategory}


if __name__ == "__main__":
    print(f"SAHOOL Crop Catalog: {TOTAL_CROPS} crops")
    print("\nBy Category:")
    for cat, count in CATEGORIES_COUNT.items():
        print(f"  - {cat}: {count}")
    print("\nYemen-specific crops:")
    for crop in ALL_CROPS.values():
        if crop.local_varieties:
            print(f"  - {crop.name_ar} ({crop.name_en}): {', '.join(crop.local_varieties)}")
