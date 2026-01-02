"""
SAHOOL Crop Parameters for Yemen
معلمات المحاصيل اليمنية - نظام صحول

This module contains comprehensive crop parameters for Yemen's agricultural regions.
يحتوي هذا الوحدة على معلمات شاملة للمحاصيل في المناطق الزراعية اليمنية.

Regions:
- Tihama (السهول الساحلية - التهامة): Coastal plains, hot climate
- Highlands (المرتفعات الجبلية): Mountain regions, moderate climate
- Hadhramaut (حضرموت): Eastern valleys, arid climate
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class Region(Enum):
    """Yemen agricultural regions - المناطق الزراعية اليمنية"""
    TIHAMA = "tihama"  # التهامة - السهول الساحلية
    HIGHLANDS = "highlands"  # المرتفعات الجبلية
    HADHRAMAUT = "hadhramaut"  # حضرموت
    EASTERN = "eastern"  # المناطق الشرقية
    CENTRAL = "central"  # المناطق الوسطى


class Season(Enum):
    """Agricultural seasons in Yemen - المواسم الزراعية في اليمن"""
    KHARIF = "kharif"  # الخريفي (Summer/Monsoon crops)
    RABI = "rabi"  # الشتوي (Winter crops)
    YEAR_ROUND = "year_round"  # على مدار السنة


class CropCategory(Enum):
    """Crop categories - فئات المحاصيل"""
    CEREAL = "cereal"  # الحبوب
    VEGETABLE = "vegetable"  # الخضروات
    FRUIT = "fruit"  # الفواكه
    LEGUME = "legume"  # البقوليات
    CASH_CROP = "cash_crop"  # المحاصيل النقدية
    FODDER = "fodder"  # الأعلاف


@dataclass
class GrowthParameters:
    """
    Growth parameters for crop modeling
    معلمات النمو لنمذجة المحاصيل
    """
    # Growing Degree Days required - درجات الحرارة التراكمية المطلوبة
    gdd_required: float

    # Base temperature for GDD calculation (°C) - درجة الحرارة الأساسية
    base_temp: float

    # Optimal temperature range (°C) - نطاق درجة الحرارة المثلى
    optimal_temp_min: float
    optimal_temp_max: float

    # Growth duration in days - مدة النمو بالأيام
    growth_days: int

    # Optimal NDVI peak value - قيمة ذروة NDVI المثلى
    optimal_ndvi_peak: float

    # Water requirement (mm) - احتياج المياه
    water_requirement_mm: float

    # Critical growth stages - مراحل النمو الحرجة
    stages: Dict[str, int] = field(default_factory=dict)


@dataclass
class SoilRequirements:
    """
    Soil requirements for crops
    متطلبات التربة للمحاصيل
    """
    # Optimal pH range - نطاق pH المثالي
    ph_min: float
    ph_max: float

    # Soil type preference - تفضيل نوع التربة
    preferred_soil_types: List[str]

    # Electrical conductivity tolerance (dS/m) - تحمل الملوحة
    ec_tolerance: float

    # Nutrient requirements (NPK ratio) - متطلبات العناصر الغذائية
    npk_ratio: str


@dataclass
class RegionalAdjustment:
    """
    Regional yield adjustment factors
    عوامل التعديل الإقليمية للإنتاج
    """
    # Yield multiplier for the region - معامل الإنتاج للمنطقة
    yield_multiplier: float

    # Water availability factor - عامل توفر المياه
    water_availability: float

    # Soil quality factor - عامل جودة التربة
    soil_quality: float

    # Climate suitability (0-1) - ملاءمة المناخ
    climate_suitability: float

    # Common constraints - القيود الشائعة
    constraints: List[str] = field(default_factory=list)


@dataclass
class CropParameters:
    """
    Comprehensive crop parameters
    معلمات شاملة للمحصول
    """
    # Basic information - المعلومات الأساسية
    crop_id: str
    name_en: str
    name_ar: str
    category: CropCategory

    # Base yield (kg/hectare) under optimal conditions - الإنتاج الأساسي
    base_yield_kg_per_ha: float

    # Growth parameters - معلمات النمو
    growth: GrowthParameters

    # Soil requirements - متطلبات التربة
    soil: SoilRequirements

    # Regional adjustments - التعديلات الإقليمية
    regional_adjustments: Dict[Region, RegionalAdjustment]

    # Seasonal factors - العوامل الموسمية
    season: Season
    seasonal_yield_factors: Dict[str, float] = field(default_factory=dict)

    # Economic parameters - المعلمات الاقتصادية
    market_price_per_kg: float = 0.0  # YER (Yemeni Rial)
    labor_hours_per_ha: float = 0.0

    # Disease susceptibility - قابلية الإصابة بالأمراض
    common_diseases: List[str] = field(default_factory=list)

    # Drought tolerance (0-1) - تحمل الجفاف
    drought_tolerance: float = 0.5

    # Heat tolerance (0-1) - تحمل الحرارة
    heat_tolerance: float = 0.5


# معلمات المحاصيل اليمنية الرئيسية
# Main Yemen Crop Parameters Database
YEMEN_CROPS: Dict[str, CropParameters] = {

    # ==================== الحبوب - CEREALS ====================

    "wheat": CropParameters(
        crop_id="wheat",
        name_en="Wheat",
        name_ar="القمح",
        category=CropCategory.CEREAL,
        base_yield_kg_per_ha=2500,
        growth=GrowthParameters(
            gdd_required=2000,
            base_temp=0,
            optimal_temp_min=15,
            optimal_temp_max=25,
            growth_days=120,
            optimal_ndvi_peak=0.75,
            water_requirement_mm=450,
            stages={
                "germination": 10,
                "tillering": 30,
                "stem_extension": 50,
                "heading": 80,
                "grain_filling": 100,
                "maturity": 120
            }
        ),
        soil=SoilRequirements(
            ph_min=6.0,
            ph_max=7.5,
            preferred_soil_types=["loamy", "clay_loam"],
            ec_tolerance=4.0,
            npk_ratio="120:60:40"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.7,
                soil_quality=0.8,
                climate_suitability=0.9,
                constraints=["limited_irrigation", "steep_slopes"]
            ),
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=0.6,
                water_availability=0.5,
                soil_quality=0.6,
                climate_suitability=0.4,
                constraints=["heat_stress", "water_scarcity"]
            ),
            Region.HADHRAMAUT: RegionalAdjustment(
                yield_multiplier=0.8,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.7,
                constraints=["water_scarcity", "soil_salinity"]
            )
        },
        season=Season.RABI,
        seasonal_yield_factors={"winter": 1.0, "summer": 0.3},
        market_price_per_kg=250,
        labor_hours_per_ha=80,
        common_diseases=["wheat_rust", "leaf_blight", "smut"],
        drought_tolerance=0.6,
        heat_tolerance=0.5
    ),

    "barley": CropParameters(
        crop_id="barley",
        name_en="Barley",
        name_ar="الشعير",
        category=CropCategory.CEREAL,
        base_yield_kg_per_ha=2200,
        growth=GrowthParameters(
            gdd_required=1800,
            base_temp=0,
            optimal_temp_min=12,
            optimal_temp_max=22,
            growth_days=100,
            optimal_ndvi_peak=0.72,
            water_requirement_mm=380,
            stages={
                "germination": 8,
                "tillering": 25,
                "stem_extension": 45,
                "heading": 70,
                "grain_filling": 85,
                "maturity": 100
            }
        ),
        soil=SoilRequirements(
            ph_min=6.5,
            ph_max=8.0,
            preferred_soil_types=["loamy", "sandy_loam"],
            ec_tolerance=8.0,
            npk_ratio="90:45:30"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.3,
                water_availability=0.7,
                soil_quality=0.8,
                climate_suitability=0.95,
                constraints=[]
            ),
            Region.HADHRAMAUT: RegionalAdjustment(
                yield_multiplier=0.9,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.8,
                constraints=["water_scarcity"]
            )
        },
        season=Season.RABI,
        seasonal_yield_factors={"winter": 1.0, "summer": 0.4},
        market_price_per_kg=220,
        labor_hours_per_ha=70,
        common_diseases=["barley_stripe", "net_blotch"],
        drought_tolerance=0.8,
        heat_tolerance=0.7
    ),

    "sorghum": CropParameters(
        crop_id="sorghum",
        name_en="Sorghum",
        name_ar="الذرة الرفيعة",
        category=CropCategory.CEREAL,
        base_yield_kg_per_ha=2000,
        growth=GrowthParameters(
            gdd_required=2200,
            base_temp=10,
            optimal_temp_min=25,
            optimal_temp_max=35,
            growth_days=110,
            optimal_ndvi_peak=0.78,
            water_requirement_mm=500,
            stages={
                "germination": 10,
                "vegetative": 35,
                "booting": 60,
                "flowering": 80,
                "grain_filling": 95,
                "maturity": 110
            }
        ),
        soil=SoilRequirements(
            ph_min=5.5,
            ph_max=8.0,
            preferred_soil_types=["loamy", "clay_loam", "sandy_loam"],
            ec_tolerance=5.0,
            npk_ratio="100:50:40"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.1,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.9,
                constraints=["water_scarcity"]
            ),
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=0.9,
                water_availability=0.7,
                soil_quality=0.8,
                climate_suitability=0.7,
                constraints=["cooler_climate"]
            ),
            Region.HADHRAMAUT: RegionalAdjustment(
                yield_multiplier=1.0,
                water_availability=0.5,
                soil_quality=0.7,
                climate_suitability=0.85,
                constraints=["water_scarcity"]
            )
        },
        season=Season.KHARIF,
        seasonal_yield_factors={"summer": 1.0, "winter": 0.5},
        market_price_per_kg=200,
        labor_hours_per_ha=75,
        common_diseases=["grain_mold", "leaf_blight"],
        drought_tolerance=0.9,
        heat_tolerance=0.95
    ),

    "corn": CropParameters(
        crop_id="corn",
        name_en="Corn (Maize)",
        name_ar="الذرة الشامية",
        category=CropCategory.CEREAL,
        base_yield_kg_per_ha=4000,
        growth=GrowthParameters(
            gdd_required=2500,
            base_temp=10,
            optimal_temp_min=20,
            optimal_temp_max=30,
            growth_days=100,
            optimal_ndvi_peak=0.80,
            water_requirement_mm=550,
            stages={
                "germination": 8,
                "vegetative": 40,
                "tasseling": 60,
                "silking": 70,
                "grain_filling": 85,
                "maturity": 100
            }
        ),
        soil=SoilRequirements(
            ph_min=5.8,
            ph_max=7.0,
            preferred_soil_types=["loamy", "clay_loam"],
            ec_tolerance=1.7,
            npk_ratio="150:75:60"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.0,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.8,
                constraints=["water_intensive"]
            ),
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=0.9,
                water_availability=0.7,
                soil_quality=0.8,
                climate_suitability=0.75,
                constraints=["temperature_sensitive"]
            )
        },
        season=Season.KHARIF,
        seasonal_yield_factors={"summer": 1.0, "winter": 0.6},
        market_price_per_kg=230,
        labor_hours_per_ha=85,
        common_diseases=["corn_blight", "rust"],
        drought_tolerance=0.5,
        heat_tolerance=0.7
    ),

    "millet": CropParameters(
        crop_id="millet",
        name_en="Pearl Millet",
        name_ar="الدخن",
        category=CropCategory.CEREAL,
        base_yield_kg_per_ha=1500,
        growth=GrowthParameters(
            gdd_required=1900,
            base_temp=10,
            optimal_temp_min=25,
            optimal_temp_max=35,
            growth_days=90,
            optimal_ndvi_peak=0.70,
            water_requirement_mm=350,
            stages={
                "germination": 7,
                "tillering": 25,
                "stem_extension": 45,
                "flowering": 60,
                "grain_filling": 75,
                "maturity": 90
            }
        ),
        soil=SoilRequirements(
            ph_min=5.0,
            ph_max=8.0,
            preferred_soil_types=["sandy_loam", "loamy"],
            ec_tolerance=6.0,
            npk_ratio="60:30:20"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.5,
                soil_quality=0.6,
                climate_suitability=0.95,
                constraints=[]
            ),
            Region.HADHRAMAUT: RegionalAdjustment(
                yield_multiplier=1.1,
                water_availability=0.5,
                soil_quality=0.6,
                climate_suitability=0.9,
                constraints=[]
            )
        },
        season=Season.KHARIF,
        seasonal_yield_factors={"summer": 1.0, "winter": 0.3},
        market_price_per_kg=180,
        labor_hours_per_ha=60,
        common_diseases=["downy_mildew", "smut"],
        drought_tolerance=0.95,
        heat_tolerance=0.95
    ),

    # ==================== الخضروات - VEGETABLES ====================

    "tomato": CropParameters(
        crop_id="tomato",
        name_en="Tomato",
        name_ar="الطماطم",
        category=CropCategory.VEGETABLE,
        base_yield_kg_per_ha=25000,
        growth=GrowthParameters(
            gdd_required=1500,
            base_temp=10,
            optimal_temp_min=20,
            optimal_temp_max=28,
            growth_days=90,
            optimal_ndvi_peak=0.70,
            water_requirement_mm=600,
            stages={
                "transplant": 0,
                "vegetative": 25,
                "flowering": 45,
                "fruit_set": 60,
                "ripening": 75,
                "harvest": 90
            }
        ),
        soil=SoilRequirements(
            ph_min=6.0,
            ph_max=6.8,
            preferred_soil_types=["loamy", "sandy_loam"],
            ec_tolerance=2.5,
            npk_ratio="150:80:120"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.1,
                water_availability=0.7,
                soil_quality=0.7,
                climate_suitability=0.8,
                constraints=["heat_stress", "pests"]
            ),
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.8,
                soil_quality=0.8,
                climate_suitability=0.95,
                constraints=[]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"winter": 1.0, "summer": 0.85},
        market_price_per_kg=300,
        labor_hours_per_ha=250,
        common_diseases=["tomato_leaf_blight", "bacterial_wilt", "leaf_curl_virus"],
        drought_tolerance=0.4,
        heat_tolerance=0.6
    ),

    "potato": CropParameters(
        crop_id="potato",
        name_en="Potato",
        name_ar="البطاطس",
        category=CropCategory.VEGETABLE,
        base_yield_kg_per_ha=15000,
        growth=GrowthParameters(
            gdd_required=1400,
            base_temp=7,
            optimal_temp_min=15,
            optimal_temp_max=24,
            growth_days=100,
            optimal_ndvi_peak=0.75,
            water_requirement_mm=500,
            stages={
                "planting": 0,
                "emergence": 15,
                "vegetative": 40,
                "tuber_initiation": 50,
                "tuber_bulking": 80,
                "maturity": 100
            }
        ),
        soil=SoilRequirements(
            ph_min=5.0,
            ph_max=6.5,
            preferred_soil_types=["sandy_loam", "loamy"],
            ec_tolerance=1.7,
            npk_ratio="120:80:150"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.3,
                water_availability=0.8,
                soil_quality=0.85,
                climate_suitability=0.95,
                constraints=[]
            ),
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=0.6,
                water_availability=0.6,
                soil_quality=0.6,
                climate_suitability=0.4,
                constraints=["heat_stress", "disease_pressure"]
            )
        },
        season=Season.RABI,
        seasonal_yield_factors={"winter": 1.0, "summer": 0.3},
        market_price_per_kg=200,
        labor_hours_per_ha=200,
        common_diseases=["late_blight", "early_blight", "bacterial_wilt"],
        drought_tolerance=0.5,
        heat_tolerance=0.4
    ),

    "onion": CropParameters(
        crop_id="onion",
        name_en="Onion",
        name_ar="البصل",
        category=CropCategory.VEGETABLE,
        base_yield_kg_per_ha=12000,
        growth=GrowthParameters(
            gdd_required=1300,
            base_temp=6,
            optimal_temp_min=13,
            optimal_temp_max=24,
            growth_days=120,
            optimal_ndvi_peak=0.68,
            water_requirement_mm=450,
            stages={
                "germination": 10,
                "vegetative": 50,
                "bulb_initiation": 80,
                "bulb_development": 105,
                "maturity": 120
            }
        ),
        soil=SoilRequirements(
            ph_min=6.0,
            ph_max=7.5,
            preferred_soil_types=["sandy_loam", "loamy"],
            ec_tolerance=1.2,
            npk_ratio="100:50:120"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.8,
                soil_quality=0.8,
                climate_suitability=0.9,
                constraints=[]
            ),
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=0.9,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.7,
                constraints=["heat_stress"]
            )
        },
        season=Season.RABI,
        seasonal_yield_factors={"winter": 1.0, "summer": 0.6},
        market_price_per_kg=250,
        labor_hours_per_ha=180,
        common_diseases=["purple_blotch", "stemphylium_blight"],
        drought_tolerance=0.6,
        heat_tolerance=0.6
    ),

    "cucumber": CropParameters(
        crop_id="cucumber",
        name_en="Cucumber",
        name_ar="الخيار",
        category=CropCategory.VEGETABLE,
        base_yield_kg_per_ha=28000,
        growth=GrowthParameters(
            gdd_required=1200,
            base_temp=15,
            optimal_temp_min=22,
            optimal_temp_max=28,
            growth_days=60,
            optimal_ndvi_peak=0.72,
            water_requirement_mm=400,
            stages={
                "germination": 5,
                "vegetative": 20,
                "flowering": 30,
                "fruit_set": 40,
                "harvest_begin": 50,
                "harvest_end": 60
            }
        ),
        soil=SoilRequirements(
            ph_min=5.5,
            ph_max=7.0,
            preferred_soil_types=["loamy", "sandy_loam"],
            ec_tolerance=1.3,
            npk_ratio="120:60:100"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.7,
                soil_quality=0.7,
                climate_suitability=0.9,
                constraints=["disease_pressure"]
            ),
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.0,
                water_availability=0.8,
                soil_quality=0.8,
                climate_suitability=0.8,
                constraints=[]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"summer": 1.0, "winter": 0.9},
        market_price_per_kg=280,
        labor_hours_per_ha=150,
        common_diseases=["powdery_mildew", "downy_mildew", "anthracnose"],
        drought_tolerance=0.3,
        heat_tolerance=0.7
    ),

    "pepper": CropParameters(
        crop_id="pepper",
        name_en="Bell Pepper",
        name_ar="الفلفل الحلو",
        category=CropCategory.VEGETABLE,
        base_yield_kg_per_ha=15000,
        growth=GrowthParameters(
            gdd_required=1600,
            base_temp=15,
            optimal_temp_min=21,
            optimal_temp_max=28,
            growth_days=85,
            optimal_ndvi_peak=0.70,
            water_requirement_mm=500,
            stages={
                "transplant": 0,
                "vegetative": 30,
                "flowering": 50,
                "fruit_set": 60,
                "fruit_development": 75,
                "harvest": 85
            }
        ),
        soil=SoilRequirements(
            ph_min=6.0,
            ph_max=7.0,
            preferred_soil_types=["loamy", "sandy_loam"],
            ec_tolerance=1.5,
            npk_ratio="140:70:100"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.1,
                water_availability=0.7,
                soil_quality=0.7,
                climate_suitability=0.85,
                constraints=["heat_stress"]
            ),
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.8,
                soil_quality=0.8,
                climate_suitability=0.9,
                constraints=[]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"spring": 1.0, "summer": 0.85, "winter": 0.9},
        market_price_per_kg=350,
        labor_hours_per_ha=220,
        common_diseases=["bacterial_spot", "anthracnose", "phytophthora_blight"],
        drought_tolerance=0.4,
        heat_tolerance=0.6
    ),

    "eggplant": CropParameters(
        crop_id="eggplant",
        name_en="Eggplant",
        name_ar="الباذنجان",
        category=CropCategory.VEGETABLE,
        base_yield_kg_per_ha=20000,
        growth=GrowthParameters(
            gdd_required=1700,
            base_temp=15,
            optimal_temp_min=22,
            optimal_temp_max=30,
            growth_days=90,
            optimal_ndvi_peak=0.72,
            water_requirement_mm=550,
            stages={
                "transplant": 0,
                "vegetative": 30,
                "flowering": 50,
                "fruit_set": 60,
                "harvest_begin": 75,
                "harvest_end": 90
            }
        ),
        soil=SoilRequirements(
            ph_min=5.5,
            ph_max=6.8,
            preferred_soil_types=["loamy", "clay_loam"],
            ec_tolerance=2.0,
            npk_ratio="150:75:100"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.7,
                soil_quality=0.7,
                climate_suitability=0.9,
                constraints=[]
            ),
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.0,
                water_availability=0.8,
                soil_quality=0.8,
                climate_suitability=0.8,
                constraints=["cooler_nights"]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"summer": 1.0, "winter": 0.8},
        market_price_per_kg=270,
        labor_hours_per_ha=200,
        common_diseases=["bacterial_wilt", "phomopsis_blight", "leaf_spot"],
        drought_tolerance=0.5,
        heat_tolerance=0.8
    ),

    # ==================== الفواكه - FRUITS ====================

    "date_palm": CropParameters(
        crop_id="date_palm",
        name_en="Date Palm",
        name_ar="نخيل التمر",
        category=CropCategory.FRUIT,
        base_yield_kg_per_ha=5000,
        growth=GrowthParameters(
            gdd_required=3500,
            base_temp=18,
            optimal_temp_min=25,
            optimal_temp_max=45,
            growth_days=180,
            optimal_ndvi_peak=0.60,
            water_requirement_mm=1500,
            stages={
                "pollination": 30,
                "fruit_set": 60,
                "kimri": 90,
                "khalal": 120,
                "rutab": 150,
                "tamar": 180
            }
        ),
        soil=SoilRequirements(
            ph_min=7.0,
            ph_max=8.5,
            preferred_soil_types=["sandy_loam", "loamy"],
            ec_tolerance=12.0,
            npk_ratio="200:100:200"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.0,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.95,
                constraints=["water_intensive"]
            ),
            Region.HADHRAMAUT: RegionalAdjustment(
                yield_multiplier=1.3,
                water_availability=0.6,
                soil_quality=0.75,
                climate_suitability=0.98,
                constraints=["water_intensive"]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"year": 1.0},
        market_price_per_kg=600,
        labor_hours_per_ha=150,
        common_diseases=["date_palm_bayoud", "black_scorch", "fruit_rot"],
        drought_tolerance=0.7,
        heat_tolerance=0.98
    ),

    "mango": CropParameters(
        crop_id="mango",
        name_en="Mango",
        name_ar="المانجو",
        category=CropCategory.FRUIT,
        base_yield_kg_per_ha=6000,
        growth=GrowthParameters(
            gdd_required=2800,
            base_temp=15,
            optimal_temp_min=24,
            optimal_temp_max=35,
            growth_days=150,
            optimal_ndvi_peak=0.68,
            water_requirement_mm=1200,
            stages={
                "flowering": 30,
                "fruit_set": 50,
                "fruit_development": 90,
                "fruit_maturation": 130,
                "harvest": 150
            }
        ),
        soil=SoilRequirements(
            ph_min=5.5,
            ph_max=7.5,
            preferred_soil_types=["loamy", "sandy_loam"],
            ec_tolerance=2.0,
            npk_ratio="180:90:120"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.95,
                constraints=["water_requirement"]
            ),
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=0.7,
                water_availability=0.8,
                soil_quality=0.8,
                climate_suitability=0.6,
                constraints=["cooler_climate", "frost_risk"]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"year": 1.0},
        market_price_per_kg=400,
        labor_hours_per_ha=120,
        common_diseases=["mango_anthracnose", "powdery_mildew", "bacterial_black_spot"],
        drought_tolerance=0.6,
        heat_tolerance=0.9
    ),

    "banana": CropParameters(
        crop_id="banana",
        name_en="Banana",
        name_ar="الموز",
        category=CropCategory.FRUIT,
        base_yield_kg_per_ha=20000,
        growth=GrowthParameters(
            gdd_required=3000,
            base_temp=14,
            optimal_temp_min=26,
            optimal_temp_max=30,
            growth_days=270,
            optimal_ndvi_peak=0.75,
            water_requirement_mm=1800,
            stages={
                "vegetative": 90,
                "flowering": 180,
                "fruit_filling": 240,
                "harvest": 270
            }
        ),
        soil=SoilRequirements(
            ph_min=5.5,
            ph_max=7.0,
            preferred_soil_types=["loamy", "clay_loam"],
            ec_tolerance=1.0,
            npk_ratio="200:100:300"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.3,
                water_availability=0.7,
                soil_quality=0.8,
                climate_suitability=0.95,
                constraints=["water_intensive", "disease_pressure"]
            ),
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=0.6,
                water_availability=0.8,
                soil_quality=0.8,
                climate_suitability=0.5,
                constraints=["temperature_sensitive", "wind_damage"]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"year": 1.0},
        market_price_per_kg=300,
        labor_hours_per_ha=200,
        common_diseases=["banana_fusarium", "panama_disease", "sigatoka"],
        drought_tolerance=0.3,
        heat_tolerance=0.8
    ),

    "grape": CropParameters(
        crop_id="grape",
        name_en="Grape",
        name_ar="العنب",
        category=CropCategory.FRUIT,
        base_yield_kg_per_ha=8000,
        growth=GrowthParameters(
            gdd_required=2400,
            base_temp=10,
            optimal_temp_min=20,
            optimal_temp_max=30,
            growth_days=150,
            optimal_ndvi_peak=0.70,
            water_requirement_mm=600,
            stages={
                "bud_break": 15,
                "flowering": 45,
                "fruit_set": 60,
                "veraison": 100,
                "harvest": 150
            }
        ),
        soil=SoilRequirements(
            ph_min=6.0,
            ph_max=7.5,
            preferred_soil_types=["sandy_loam", "loamy"],
            ec_tolerance=1.5,
            npk_ratio="100:50:150"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.3,
                water_availability=0.7,
                soil_quality=0.85,
                climate_suitability=0.95,
                constraints=[]
            ),
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=0.7,
                water_availability=0.6,
                soil_quality=0.6,
                climate_suitability=0.6,
                constraints=["heat_stress", "disease_pressure"]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"year": 1.0},
        market_price_per_kg=450,
        labor_hours_per_ha=180,
        common_diseases=["grape_downy_mildew", "powdery_mildew", "anthracnose"],
        drought_tolerance=0.7,
        heat_tolerance=0.7
    ),

    # ==================== المحاصيل النقدية - CASH CROPS ====================

    "coffee": CropParameters(
        crop_id="coffee",
        name_en="Coffee (Arabica)",
        name_ar="البن",
        category=CropCategory.CASH_CROP,
        base_yield_kg_per_ha=800,
        growth=GrowthParameters(
            gdd_required=2000,
            base_temp=15,
            optimal_temp_min=18,
            optimal_temp_max=24,
            growth_days=270,
            optimal_ndvi_peak=0.65,
            water_requirement_mm=1200,
            stages={
                "flowering": 60,
                "fruit_set": 90,
                "fruit_development": 180,
                "ripening": 240,
                "harvest": 270
            }
        ),
        soil=SoilRequirements(
            ph_min=5.5,
            ph_max=6.5,
            preferred_soil_types=["volcanic", "loamy"],
            ec_tolerance=1.0,
            npk_ratio="120:60:100"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.5,
                water_availability=0.8,
                soil_quality=0.9,
                climate_suitability=0.98,
                constraints=[]
            ),
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=0.3,
                water_availability=0.5,
                soil_quality=0.6,
                climate_suitability=0.3,
                constraints=["heat_stress", "unsuitable_climate"]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"year": 1.0},
        market_price_per_kg=8000,
        labor_hours_per_ha=300,
        common_diseases=["coffee_leaf_rust", "coffee_berry_disease", "anthracnose"],
        drought_tolerance=0.5,
        heat_tolerance=0.4
    ),

    "qat": CropParameters(
        crop_id="qat",
        name_en="Qat (Khat)",
        name_ar="القات",
        category=CropCategory.CASH_CROP,
        base_yield_kg_per_ha=3000,
        growth=GrowthParameters(
            gdd_required=2200,
            base_temp=12,
            optimal_temp_min=18,
            optimal_temp_max=28,
            growth_days=365,
            optimal_ndvi_peak=0.72,
            water_requirement_mm=1400,
            stages={
                "pruning": 30,
                "vegetative": 120,
                "harvest_ready": 180,
                "peak_harvest": 240
            }
        ),
        soil=SoilRequirements(
            ph_min=6.0,
            ph_max=7.5,
            preferred_soil_types=["loamy", "clay_loam"],
            ec_tolerance=2.0,
            npk_ratio="180:90:140"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.4,
                water_availability=0.7,
                soil_quality=0.85,
                climate_suitability=0.95,
                constraints=["water_intensive"]
            ),
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=0.5,
                water_availability=0.5,
                soil_quality=0.6,
                climate_suitability=0.4,
                constraints=["heat_stress", "water_intensive"]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"year": 1.0},
        market_price_per_kg=2000,
        labor_hours_per_ha=400,
        common_diseases=["leaf_spot", "root_rot"],
        drought_tolerance=0.4,
        heat_tolerance=0.6
    ),

    # ==================== البقوليات - LEGUMES ====================

    "lentil": CropParameters(
        crop_id="lentil",
        name_en="Lentil",
        name_ar="العدس",
        category=CropCategory.LEGUME,
        base_yield_kg_per_ha=1200,
        growth=GrowthParameters(
            gdd_required=1600,
            base_temp=5,
            optimal_temp_min=15,
            optimal_temp_max=25,
            growth_days=100,
            optimal_ndvi_peak=0.70,
            water_requirement_mm=350,
            stages={
                "germination": 10,
                "vegetative": 40,
                "flowering": 60,
                "pod_fill": 80,
                "maturity": 100
            }
        ),
        soil=SoilRequirements(
            ph_min=6.0,
            ph_max=8.0,
            preferred_soil_types=["loamy", "clay_loam"],
            ec_tolerance=3.0,
            npk_ratio="20:40:40"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.3,
                water_availability=0.7,
                soil_quality=0.8,
                climate_suitability=0.9,
                constraints=[]
            ),
            Region.HADHRAMAUT: RegionalAdjustment(
                yield_multiplier=0.8,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.7,
                constraints=["heat_stress"]
            )
        },
        season=Season.RABI,
        seasonal_yield_factors={"winter": 1.0, "summer": 0.3},
        market_price_per_kg=500,
        labor_hours_per_ha=60,
        common_diseases=["fusarium_wilt", "rust"],
        drought_tolerance=0.7,
        heat_tolerance=0.6
    ),

    "chickpea": CropParameters(
        crop_id="chickpea",
        name_en="Chickpea",
        name_ar="الحمص",
        category=CropCategory.LEGUME,
        base_yield_kg_per_ha=1400,
        growth=GrowthParameters(
            gdd_required=1700,
            base_temp=5,
            optimal_temp_min=18,
            optimal_temp_max=28,
            growth_days=110,
            optimal_ndvi_peak=0.72,
            water_requirement_mm=400,
            stages={
                "germination": 10,
                "vegetative": 45,
                "flowering": 70,
                "pod_fill": 90,
                "maturity": 110
            }
        ),
        soil=SoilRequirements(
            ph_min=6.0,
            ph_max=8.5,
            preferred_soil_types=["loamy", "sandy_loam"],
            ec_tolerance=4.0,
            npk_ratio="25:50:50"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.7,
                soil_quality=0.8,
                climate_suitability=0.85,
                constraints=[]
            ),
            Region.HADHRAMAUT: RegionalAdjustment(
                yield_multiplier=0.9,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.75,
                constraints=["heat_stress"]
            )
        },
        season=Season.RABI,
        seasonal_yield_factors={"winter": 1.0, "summer": 0.4},
        market_price_per_kg=550,
        labor_hours_per_ha=65,
        common_diseases=["wilt", "blight", "root_rot"],
        drought_tolerance=0.8,
        heat_tolerance=0.7
    ),

    # ==================== الأعلاف - FODDER ====================

    "alfalfa": CropParameters(
        crop_id="alfalfa",
        name_en="Alfalfa (Lucerne)",
        name_ar="البرسيم الحجازي",
        category=CropCategory.FODDER,
        base_yield_kg_per_ha=18000,
        growth=GrowthParameters(
            gdd_required=2000,
            base_temp=5,
            optimal_temp_min=15,
            optimal_temp_max=30,
            growth_days=365,
            optimal_ndvi_peak=0.78,
            water_requirement_mm=900,
            stages={
                "establishment": 30,
                "vegetative": 60,
                "flowering": 90,
                "cutting_1": 45,
                "cutting_2": 90,
                "cutting_3": 135
            }
        ),
        soil=SoilRequirements(
            ph_min=6.5,
            ph_max=8.0,
            preferred_soil_types=["loamy", "sandy_loam"],
            ec_tolerance=2.0,
            npk_ratio="30:60:100"
        ),
        regional_adjustments={
            Region.HIGHLANDS: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.8,
                soil_quality=0.85,
                climate_suitability=0.9,
                constraints=[]
            ),
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.0,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.75,
                constraints=["water_intensive"]
            )
        },
        season=Season.YEAR_ROUND,
        seasonal_yield_factors={"year": 1.0},
        market_price_per_kg=150,
        labor_hours_per_ha=100,
        common_diseases=["leaf_spot", "root_rot", "downy_mildew"],
        drought_tolerance=0.6,
        heat_tolerance=0.7
    ),

    "sesame": CropParameters(
        crop_id="sesame",
        name_en="Sesame",
        name_ar="السمسم",
        category=CropCategory.CASH_CROP,
        base_yield_kg_per_ha=600,
        growth=GrowthParameters(
            gdd_required=2000,
            base_temp=15,
            optimal_temp_min=25,
            optimal_temp_max=35,
            growth_days=90,
            optimal_ndvi_peak=0.68,
            water_requirement_mm=400,
            stages={
                "germination": 8,
                "vegetative": 35,
                "flowering": 55,
                "pod_development": 75,
                "maturity": 90
            }
        ),
        soil=SoilRequirements(
            ph_min=5.5,
            ph_max=8.0,
            preferred_soil_types=["loamy", "sandy_loam"],
            ec_tolerance=3.0,
            npk_ratio="60:40:40"
        ),
        regional_adjustments={
            Region.TIHAMA: RegionalAdjustment(
                yield_multiplier=1.2,
                water_availability=0.6,
                soil_quality=0.7,
                climate_suitability=0.9,
                constraints=[]
            ),
            Region.HADHRAMAUT: RegionalAdjustment(
                yield_multiplier=1.1,
                water_availability=0.5,
                soil_quality=0.7,
                climate_suitability=0.85,
                constraints=["water_scarcity"]
            )
        },
        season=Season.KHARIF,
        seasonal_yield_factors={"summer": 1.0, "winter": 0.5},
        market_price_per_kg=1200,
        labor_hours_per_ha=70,
        common_diseases=["phytophthora_blight", "bacterial_leaf_spot"],
        drought_tolerance=0.9,
        heat_tolerance=0.95
    ),
}


def get_crop_parameters(crop_id: str) -> Optional[CropParameters]:
    """
    Get crop parameters by crop ID
    الحصول على معلمات المحصول باستخدام معرف المحصول

    Args:
        crop_id: Crop identifier - معرف المحصول

    Returns:
        Crop parameters or None - معلمات المحصول أو لا شيء
    """
    return YEMEN_CROPS.get(crop_id)


def get_crops_by_category(category: CropCategory) -> List[CropParameters]:
    """
    Get all crops in a specific category
    الحصول على جميع المحاصيل في فئة معينة

    Args:
        category: Crop category - فئة المحصول

    Returns:
        List of crop parameters - قائمة معلمات المحاصيل
    """
    return [crop for crop in YEMEN_CROPS.values() if crop.category == category]


def get_crops_by_region(region: Region, min_suitability: float = 0.6) -> List[CropParameters]:
    """
    Get suitable crops for a specific region
    الحصول على المحاصيل المناسبة لمنطقة معينة

    Args:
        region: Yemen region - المنطقة اليمنية
        min_suitability: Minimum climate suitability threshold - الحد الأدنى للملاءمة المناخية

    Returns:
        List of suitable crop parameters - قائمة معلمات المحاصيل المناسبة
    """
    suitable_crops = []
    for crop in YEMEN_CROPS.values():
        if region in crop.regional_adjustments:
            adjustment = crop.regional_adjustments[region]
            if adjustment.climate_suitability >= min_suitability:
                suitable_crops.append(crop)
    return suitable_crops


def get_all_crop_ids() -> List[str]:
    """
    Get list of all crop IDs
    الحصول على قائمة جميع معرفات المحاصيل

    Returns:
        List of crop IDs - قائمة معرفات المحاصيل
    """
    return list(YEMEN_CROPS.keys())
