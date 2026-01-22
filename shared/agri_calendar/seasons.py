"""
Agricultural Seasons Calculator - حاسبة المواسم الزراعية

Season calculations for Saudi Arabia and Yemen regions.
Includes traditional Anwa'a (الأنواء) calendar integration.

Supports:
- Regional climate-based seasons
- Traditional Arabic Anwa'a system
- Gregorian and Hijri calendar alignment
- Temperature and rainfall patterns

Author: SAHOOL Platform Team
Updated: January 2026
"""

from datetime import date
from typing import Any

from .models import (
    AgriculturalSeason,
    ClimateZone,
    CropType,
    Region,
    RegionMetadata,
    SeasonDefinition,
    TraditionalSeason,
    TraditionalSeasonInfo,
)


# =============================================================================
# Region Metadata Database - قاعدة بيانات المناطق
# =============================================================================


# Saudi Arabia regions
REGION_METADATA: dict[Region, RegionMetadata] = {
    Region.RIYADH: RegionMetadata(
        region=Region.RIYADH,
        name_ar="الرياض",
        name_en="Riyadh",
        country="Saudi Arabia",
        latitude=24.7136,
        longitude=46.6753,
        altitude_m=612,
        climate_zone=ClimateZone.ARID_HOT,
        avg_annual_rainfall_mm=100,
        avg_annual_temp_c=26.0,
        groundwater_available=True,
        primary_crops=[
            CropType.DATE_PALM, CropType.WHEAT, CropType.ALFALFA,
            CropType.TOMATO, CropType.POTATO,
        ],
        traditional_farming_practices_ar=[
            "زراعة النخيل في الواحات",
            "الري بالآبار الارتوازية",
            "زراعة الخضروات في البيوت المحمية",
        ],
        traditional_farming_practices_en=[
            "Date palm cultivation in oases",
            "Irrigation from artesian wells",
            "Greenhouse vegetable production",
        ],
    ),
    Region.QASSIM: RegionMetadata(
        region=Region.QASSIM,
        name_ar="القصيم",
        name_en="Qassim",
        country="Saudi Arabia",
        latitude=26.3066,
        longitude=43.9733,
        altitude_m=650,
        climate_zone=ClimateZone.ARID_HOT,
        avg_annual_rainfall_mm=125,
        avg_annual_temp_c=24.5,
        groundwater_available=True,
        primary_crops=[
            CropType.DATE_PALM, CropType.WHEAT, CropType.BARLEY,
            CropType.GRAPE, CropType.TOMATO, CropType.WATERMELON,
        ],
        traditional_farming_practices_ar=[
            "منطقة التمور الأشهر في المملكة",
            "زراعة القمح الشتوية",
            "زراعة الفواكه والخضروات",
        ],
        traditional_farming_practices_en=[
            "Most famous date region in the Kingdom",
            "Winter wheat cultivation",
            "Fruit and vegetable farming",
        ],
    ),
    Region.HAIL: RegionMetadata(
        region=Region.HAIL,
        name_ar="حائل",
        name_en="Hail",
        country="Saudi Arabia",
        latitude=27.5214,
        longitude=41.6875,
        altitude_m=1000,
        climate_zone=ClimateZone.ARID_MILD,
        avg_annual_rainfall_mm=140,
        avg_annual_temp_c=22.0,
        groundwater_available=True,
        primary_crops=[
            CropType.WHEAT, CropType.BARLEY, CropType.POTATO,
            CropType.DATE_PALM, CropType.OLIVE,
        ],
        traditional_farming_practices_ar=[
            "سلة الغذاء في المملكة",
            "زراعة الحبوب الموسمية",
            "زراعة البطاطس على نطاق واسع",
        ],
        traditional_farming_practices_en=[
            "Food basket of the Kingdom",
            "Seasonal grain cultivation",
            "Large-scale potato farming",
        ],
    ),
    Region.EASTERN: RegionMetadata(
        region=Region.EASTERN,
        name_ar="الشرقية",
        name_en="Eastern Province",
        country="Saudi Arabia",
        latitude=26.4207,
        longitude=50.0888,
        altitude_m=10,
        climate_zone=ClimateZone.COASTAL,
        avg_annual_rainfall_mm=90,
        avg_annual_temp_c=27.0,
        groundwater_available=True,
        surface_water_available=False,
        desalinated_water_available=True,
        primary_crops=[
            CropType.DATE_PALM, CropType.RICE, CropType.ALFALFA,
            CropType.TOMATO, CropType.CITRUS,
        ],
        traditional_farming_practices_ar=[
            "زراعة الأرز في الأحساء",
            "واحات النخيل التاريخية",
            "الري من عيون المياه",
        ],
        traditional_farming_practices_en=[
            "Rice cultivation in Al-Ahsa",
            "Historic date palm oases",
            "Irrigation from natural springs",
        ],
    ),
    Region.ASIR: RegionMetadata(
        region=Region.ASIR,
        name_ar="عسير",
        name_en="Asir",
        country="Saudi Arabia",
        latitude=18.2164,
        longitude=42.5053,
        altitude_m=2200,
        climate_zone=ClimateZone.HIGHLAND,
        avg_annual_rainfall_mm=350,
        avg_annual_temp_c=18.0,
        groundwater_available=True,
        surface_water_available=True,
        primary_crops=[
            CropType.WHEAT, CropType.BARLEY, CropType.COFFEE,
            CropType.SORGHUM, CropType.POMEGRANATE, CropType.FIG,
        ],
        traditional_farming_practices_ar=[
            "الزراعة المدرجة على الجبال",
            "زراعة البن العربي",
            "حصاد مياه الأمطار",
        ],
        traditional_farming_practices_en=[
            "Terraced mountain farming",
            "Arabica coffee cultivation",
            "Rainwater harvesting",
        ],
    ),
    Region.JAZAN: RegionMetadata(
        region=Region.JAZAN,
        name_ar="جازان",
        name_en="Jazan",
        country="Saudi Arabia",
        latitude=16.8892,
        longitude=42.5611,
        altitude_m=30,
        climate_zone=ClimateZone.SUBTROPICAL,
        avg_annual_rainfall_mm=200,
        avg_annual_temp_c=30.0,
        groundwater_available=True,
        surface_water_available=True,
        primary_crops=[
            CropType.MANGO, CropType.PAPAYA, CropType.BANANA,
            CropType.SORGHUM, CropType.SESAME, CropType.COFFEE,
        ],
        traditional_farming_practices_ar=[
            "زراعة الفواكه الاستوائية",
            "زراعة البن الخولاني",
            "الري من الأودية",
        ],
        traditional_farming_practices_en=[
            "Tropical fruit cultivation",
            "Khawlani coffee farming",
            "Wadi irrigation",
        ],
    ),
    Region.TABUK: RegionMetadata(
        region=Region.TABUK,
        name_ar="تبوك",
        name_en="Tabuk",
        country="Saudi Arabia",
        latitude=28.3838,
        longitude=36.5550,
        altitude_m=770,
        climate_zone=ClimateZone.ARID_MILD,
        avg_annual_rainfall_mm=50,
        avg_annual_temp_c=21.0,
        groundwater_available=True,
        primary_crops=[
            CropType.DATE_PALM, CropType.GRAPE, CropType.CITRUS,
            CropType.OLIVE, CropType.WHEAT,
        ],
        traditional_farming_practices_ar=[
            "زراعة العنب والزيتون",
            "الحمضيات عالية الجودة",
            "زراعة القمح الشتوي",
        ],
        traditional_farming_practices_en=[
            "Grape and olive cultivation",
            "High-quality citrus",
            "Winter wheat farming",
        ],
    ),
    Region.JOUF: RegionMetadata(
        region=Region.JOUF,
        name_ar="الجوف",
        name_en="Al-Jouf",
        country="Saudi Arabia",
        latitude=29.7875,
        longitude=39.8739,
        altitude_m=580,
        climate_zone=ClimateZone.ARID_MILD,
        avg_annual_rainfall_mm=75,
        avg_annual_temp_c=20.0,
        groundwater_available=True,
        primary_crops=[
            CropType.OLIVE, CropType.DATE_PALM, CropType.WHEAT,
            CropType.BARLEY, CropType.TOMATO,
        ],
        traditional_farming_practices_ar=[
            "أكبر منطقة لزراعة الزيتون",
            "زيت الزيتون البكر",
            "زراعة الحبوب",
        ],
        traditional_farming_practices_en=[
            "Largest olive growing region",
            "Extra virgin olive oil production",
            "Grain cultivation",
        ],
    ),
    Region.NAJRAN: RegionMetadata(
        region=Region.NAJRAN,
        name_ar="نجران",
        name_en="Najran",
        country="Saudi Arabia",
        latitude=17.4933,
        longitude=44.1277,
        altitude_m=1300,
        climate_zone=ClimateZone.SEMI_ARID,
        avg_annual_rainfall_mm=150,
        avg_annual_temp_c=23.0,
        groundwater_available=True,
        primary_crops=[
            CropType.DATE_PALM, CropType.CITRUS, CropType.GRAPE,
            CropType.POMEGRANATE, CropType.SORGHUM,
        ],
        traditional_farming_practices_ar=[
            "الواحات الزراعية التقليدية",
            "زراعة الفواكه",
            "تربية النحل",
        ],
        traditional_farming_practices_en=[
            "Traditional agricultural oases",
            "Fruit farming",
            "Beekeeping",
        ],
    ),

    # Yemen regions
    Region.SANA: RegionMetadata(
        region=Region.SANA,
        name_ar="صنعاء",
        name_en="Sana'a",
        country="Yemen",
        latitude=15.3694,
        longitude=44.1910,
        altitude_m=2250,
        climate_zone=ClimateZone.HIGHLAND,
        avg_annual_rainfall_mm=300,
        avg_annual_temp_c=17.5,
        groundwater_available=True,
        surface_water_available=True,
        primary_crops=[
            CropType.WHEAT, CropType.BARLEY, CropType.GRAPE,
            CropType.POTATO, CropType.POMEGRANATE, CropType.QAT,
        ],
        traditional_farming_practices_ar=[
            "الزراعة المدرجة",
            "حصاد مياه الأمطار",
            "زراعة العنب والفواكه",
        ],
        traditional_farming_practices_en=[
            "Terraced agriculture",
            "Rainwater harvesting",
            "Grape and fruit cultivation",
        ],
    ),
    Region.TAIZ: RegionMetadata(
        region=Region.TAIZ,
        name_ar="تعز",
        name_en="Taiz",
        country="Yemen",
        latitude=13.5789,
        longitude=44.0219,
        altitude_m=1400,
        climate_zone=ClimateZone.HIGHLAND,
        avg_annual_rainfall_mm=400,
        avg_annual_temp_c=21.0,
        groundwater_available=True,
        surface_water_available=True,
        primary_crops=[
            CropType.COFFEE, CropType.SORGHUM, CropType.MAIZE,
            CropType.WHEAT, CropType.MANGO, CropType.BANANA,
        ],
        traditional_farming_practices_ar=[
            "منطقة البن اليمني الشهير",
            "الزراعة المطرية",
            "المدرجات الجبلية",
        ],
        traditional_farming_practices_en=[
            "Famous Yemeni coffee region",
            "Rainfed agriculture",
            "Mountain terraces",
        ],
    ),
    Region.ADEN: RegionMetadata(
        region=Region.ADEN,
        name_ar="عدن",
        name_en="Aden",
        country="Yemen",
        latitude=12.7797,
        longitude=45.0095,
        altitude_m=5,
        climate_zone=ClimateZone.COASTAL,
        avg_annual_rainfall_mm=50,
        avg_annual_temp_c=29.0,
        groundwater_available=False,
        surface_water_available=False,
        desalinated_water_available=True,
        primary_crops=[
            CropType.DATE_PALM, CropType.TOMATO, CropType.ONION,
            CropType.CUCUMBER, CropType.WATERMELON,
        ],
        traditional_farming_practices_ar=[
            "الزراعة الساحلية",
            "البيوت المحمية",
            "المياه المحلاة",
        ],
        traditional_farming_practices_en=[
            "Coastal farming",
            "Greenhouse production",
            "Desalinated water use",
        ],
    ),
    Region.HADRAMAUT: RegionMetadata(
        region=Region.HADRAMAUT,
        name_ar="حضرموت",
        name_en="Hadramaut",
        country="Yemen",
        latitude=15.9392,
        longitude=48.7882,
        altitude_m=500,
        climate_zone=ClimateZone.ARID_HOT,
        avg_annual_rainfall_mm=100,
        avg_annual_temp_c=27.0,
        groundwater_available=True,
        primary_crops=[
            CropType.DATE_PALM, CropType.SESAME, CropType.SORGHUM,
            CropType.WHEAT, CropType.ALFALFA,
        ],
        traditional_farming_practices_ar=[
            "زراعة النخيل في الوديان",
            "نظام الري بالغيل",
            "الزراعة السيلية",
        ],
        traditional_farming_practices_en=[
            "Date palm in wadis",
            "Traditional channel irrigation",
            "Spate irrigation",
        ],
    ),
    Region.IBBI: RegionMetadata(
        region=Region.IBBI,
        name_ar="إب",
        name_en="Ibb",
        country="Yemen",
        latitude=13.9594,
        longitude=44.1729,
        altitude_m=2050,
        climate_zone=ClimateZone.HIGHLAND,
        avg_annual_rainfall_mm=1000,
        avg_annual_temp_c=19.0,
        groundwater_available=True,
        surface_water_available=True,
        primary_crops=[
            CropType.COFFEE, CropType.WHEAT, CropType.MAIZE,
            CropType.POTATO, CropType.SORGHUM, CropType.QAT,
        ],
        traditional_farming_practices_ar=[
            "أكثر مناطق اليمن أمطاراً",
            "اللواء الأخضر",
            "الزراعة المطرية المستدامة",
        ],
        traditional_farming_practices_en=[
            "Highest rainfall in Yemen",
            "The Green Province",
            "Sustainable rainfed agriculture",
        ],
    ),
}


# =============================================================================
# Traditional Seasons (Anwa'a) Database - قاعدة بيانات الأنواء
# =============================================================================


def _create_traditional_seasons() -> dict[TraditionalSeason, TraditionalSeasonInfo]:
    """Create traditional season information database"""
    seasons = {}

    # Summer Anwa'a (الصيف) - Jun 7 to Sep 5
    seasons[TraditionalSeason.THURAYA] = TraditionalSeasonInfo(
        season=TraditionalSeason.THURAYA,
        name_ar="الثريا",
        name_en="Thuraya (Pleiades)",
        start_date_approx=date(2026, 6, 7),
        end_date_approx=date(2026, 6, 19),
        star_name_ar="نجم الثريا",
        star_name_en="Pleiades star cluster",
        weather_description_ar="بداية الصيف الحقيقي، حرارة شديدة",
        weather_description_en="Start of true summer, intense heat",
        typical_temp_min_c=28,
        typical_temp_max_c=45,
        agricultural_activities_ar=[
            "حصاد القمح والشعير",
            "جني التمر المبكر",
            "ري مكثف للنخيل",
        ],
        agricultural_activities_en=[
            "Wheat and barley harvest",
            "Early date harvest",
            "Intensive palm irrigation",
        ],
        recommended_crops=[CropType.DATE_PALM],
        proverb_ar="إذا طلعت الثريا، رفع العشاء من العشية",
        proverb_en="When Thuraya rises, dinner is lifted early (days are long)",
    )

    seasons[TraditionalSeason.DABARAN] = TraditionalSeasonInfo(
        season=TraditionalSeason.DABARAN,
        name_ar="الدبران",
        name_en="Dabaran (Aldebaran)",
        start_date_approx=date(2026, 6, 20),
        end_date_approx=date(2026, 7, 2),
        star_name_ar="عين الثور",
        star_name_en="Eye of Taurus",
        weather_description_ar="حرارة شديدة، رياح سموم",
        weather_description_en="Extreme heat, hot winds (Samum)",
        typical_temp_min_c=30,
        typical_temp_max_c=48,
        agricultural_activities_ar=[
            "الحفاظ على الماشية من الحر",
            "ري صباحي ومسائي",
            "حماية المحاصيل من الحرارة",
        ],
        agricultural_activities_en=[
            "Protect livestock from heat",
            "Morning and evening irrigation",
            "Protect crops from heat stress",
        ],
        recommended_crops=[],
        proverb_ar="الدبران صيف وحر وقيظان",
        proverb_en="Dabaran is summer, heat, and scorching",
    )

    # Winter Anwa'a - Key agricultural period
    seasons[TraditionalSeason.SAAD_DHABIH] = TraditionalSeasonInfo(
        season=TraditionalSeason.SAAD_DHABIH,
        name_ar="سعد الذابح",
        name_en="Saad al-Dhabih",
        start_date_approx=date(2026, 2, 9),
        end_date_approx=date(2026, 2, 21),
        star_name_ar="سعد الذابح",
        star_name_en="Lucky Star of the Slaughterer",
        weather_description_ar="برد شديد، صقيع ليلي",
        weather_description_en="Severe cold, night frost",
        typical_temp_min_c=2,
        typical_temp_max_c=18,
        agricultural_activities_ar=[
            "زراعة البطاطس",
            "تقليم أشجار الفاكهة",
            "حماية المحاصيل من الصقيع",
        ],
        agricultural_activities_en=[
            "Potato planting",
            "Fruit tree pruning",
            "Frost protection for crops",
        ],
        recommended_crops=[CropType.POTATO, CropType.ONION, CropType.GARLIC],
        proverb_ar="سعد الذابح ما ينفع صاحبه إلا الذبائح",
        proverb_en="In Saad al-Dhabih, only slaughtered meat helps (it's too cold to farm)",
    )

    seasons[TraditionalSeason.SAAD_BULAA] = TraditionalSeasonInfo(
        season=TraditionalSeason.SAAD_BULAA,
        name_ar="سعد بلع",
        name_en="Saad Bula",
        start_date_approx=date(2026, 2, 22),
        end_date_approx=date(2026, 3, 6),
        star_name_ar="سعد بلع",
        star_name_en="Lucky Star of the Swallower",
        weather_description_ar="البرد يبدأ بالانحسار، رطوبة",
        weather_description_en="Cold begins to recede, humid",
        typical_temp_min_c=5,
        typical_temp_max_c=22,
        agricultural_activities_ar=[
            "زراعة الخضروات الشتوية",
            "تطعيم الأشجار",
            "بداية موسم زراعة القمح",
        ],
        agricultural_activities_en=[
            "Winter vegetable planting",
            "Tree grafting",
            "Start of wheat planting season",
        ],
        recommended_crops=[CropType.WHEAT, CropType.BARLEY, CropType.LETTUCE],
        proverb_ar="سعد بلع تنبلع الأرض بالماء",
        proverb_en="In Saad Bula, the earth swallows water (moisture returns)",
    )

    # Spring Anwa'a - Important planting period
    seasons[TraditionalSeason.SAAD_SUUD] = TraditionalSeasonInfo(
        season=TraditionalSeason.SAAD_SUUD,
        name_ar="سعد السعود",
        name_en="Saad al-Suud",
        start_date_approx=date(2026, 3, 7),
        end_date_approx=date(2026, 3, 19),
        star_name_ar="سعد السعود",
        star_name_en="Luckiest of the Lucky",
        weather_description_ar="بداية الدفء، الجو معتدل",
        weather_description_en="Beginning of warmth, moderate weather",
        typical_temp_min_c=10,
        typical_temp_max_c=26,
        agricultural_activities_ar=[
            "أفضل وقت للزراعة",
            "زراعة الخضروات الصيفية",
            "تلقيح النخيل",
        ],
        agricultural_activities_en=[
            "Best time for planting",
            "Summer vegetable planting",
            "Date palm pollination",
        ],
        recommended_crops=[
            CropType.TOMATO, CropType.CUCUMBER, CropType.SQUASH,
            CropType.WATERMELON, CropType.MELON,
        ],
        proverb_ar="سعد السعود تدب الحرارة في العود",
        proverb_en="In Saad al-Suud, warmth creeps into the wood (trees wake up)",
    )

    seasons[TraditionalSeason.SAAD_AKHBIYA] = TraditionalSeasonInfo(
        season=TraditionalSeason.SAAD_AKHBIYA,
        name_ar="سعد الأخبية",
        name_en="Saad al-Akhbiya",
        start_date_approx=date(2026, 3, 20),
        end_date_approx=date(2026, 4, 1),
        star_name_ar="سعد الأخبية",
        star_name_en="Lucky Star of Tents",
        weather_description_ar="دفء ربيعي، رياح خفيفة",
        weather_description_en="Spring warmth, light winds",
        typical_temp_min_c=14,
        typical_temp_max_c=30,
        agricultural_activities_ar=[
            "زراعة الذرة",
            "شتل الطماطم والباذنجان",
            "مكافحة الآفات الربيعية",
        ],
        agricultural_activities_en=[
            "Maize planting",
            "Tomato and eggplant transplanting",
            "Spring pest control",
        ],
        recommended_crops=[CropType.MAIZE, CropType.SORGHUM, CropType.OKRA],
        proverb_ar="سعد الأخبية تطلع من جحرها الحشرات الخبية",
        proverb_en="In Saad al-Akhbiya, insects emerge from hiding",
    )

    # Autumn - Preparation for winter crops
    seasons[TraditionalSeason.SARFA] = TraditionalSeasonInfo(
        season=TraditionalSeason.SARFA,
        name_ar="الصرفة",
        name_en="Al-Sarfa",
        start_date_approx=date(2026, 10, 2),
        end_date_approx=date(2026, 10, 14),
        star_name_ar="الصرفة",
        star_name_en="The Averted One",
        weather_description_ar="انصراف الحر، بداية الاعتدال",
        weather_description_en="Heat departs, beginning of moderation",
        typical_temp_min_c=18,
        typical_temp_max_c=35,
        agricultural_activities_ar=[
            "تجهيز الأرض للزراعة الشتوية",
            "حرث التربة",
            "زراعة البرسيم",
        ],
        agricultural_activities_en=[
            "Land preparation for winter crops",
            "Soil plowing",
            "Alfalfa planting",
        ],
        recommended_crops=[CropType.ALFALFA, CropType.WHEAT, CropType.BARLEY],
        proverb_ar="الصرفة تصرف الحر وتقبل البرد",
        proverb_en="Sarfa dismisses heat and welcomes cold",
    )

    seasons[TraditionalSeason.SIMAK] = TraditionalSeasonInfo(
        season=TraditionalSeason.SIMAK,
        name_ar="السماك",
        name_en="Al-Simak",
        start_date_approx=date(2026, 10, 28),
        end_date_approx=date(2026, 11, 9),
        star_name_ar="السماك الأعزل",
        star_name_en="Spica (The Unarmed)",
        weather_description_ar="جو معتدل مائل للبرودة",
        weather_description_en="Moderate weather turning cool",
        typical_temp_min_c=15,
        typical_temp_max_c=30,
        agricultural_activities_ar=[
            "زراعة القمح والشعير",
            "زراعة البصل والثوم",
            "غرس الأشجار",
        ],
        agricultural_activities_en=[
            "Wheat and barley planting",
            "Onion and garlic planting",
            "Tree planting",
        ],
        recommended_crops=[
            CropType.WHEAT, CropType.BARLEY, CropType.ONION, CropType.GARLIC,
        ],
        proverb_ar="السماك يمسك الزرع بالتراب",
        proverb_en="Simak holds the crop in the soil",
    )

    return seasons


TRADITIONAL_SEASONS: dict[TraditionalSeason, TraditionalSeasonInfo] = _create_traditional_seasons()


# =============================================================================
# Season Definitions by Region - تعريف المواسم حسب المنطقة
# =============================================================================


def create_season_definitions(region: Region) -> list[SeasonDefinition]:
    """
    Create season definitions for a specific region
    إنشاء تعريفات المواسم لمنطقة محددة
    """
    metadata = REGION_METADATA.get(region)
    if not metadata:
        return []

    climate = metadata.climate_zone
    seasons = []

    # Define seasons based on climate zone
    if climate == ClimateZone.ARID_HOT:
        seasons = _create_arid_hot_seasons(region)
    elif climate == ClimateZone.ARID_MILD:
        seasons = _create_arid_mild_seasons(region)
    elif climate == ClimateZone.HIGHLAND:
        seasons = _create_highland_seasons(region)
    elif climate == ClimateZone.COASTAL:
        seasons = _create_coastal_seasons(region)
    elif climate == ClimateZone.SUBTROPICAL:
        seasons = _create_subtropical_seasons(region)
    elif climate == ClimateZone.SEMI_ARID:
        seasons = _create_semi_arid_seasons(region)

    return seasons


def _create_arid_hot_seasons(region: Region) -> list[SeasonDefinition]:
    """Season definitions for arid hot climate (Central Saudi)"""
    return [
        SeasonDefinition(
            season=AgriculturalSeason.WINTER,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            name_ar="الشتاء",
            name_en="Winter",
            start_month=12,
            start_day=1,
            end_month=2,
            end_day=28,
            avg_temp_min_c=8.0,
            avg_temp_max_c=22.0,
            avg_rainfall_mm=30.0,
            avg_humidity_percent=45.0,
            daylight_hours=10.5,
            frost_risk=True,
            frost_risk_level="low",
            heat_stress_risk=False,
            water_stress_level="low",
            description_ar="موسم البرد المعتدل، مثالي لزراعة القمح والشعير والخضروات الشتوية",
            description_en="Mild cold season, ideal for wheat, barley and winter vegetables",
            agricultural_notes_ar="أفضل موسم للزراعة في المنطقة الوسطى",
            agricultural_notes_en="Best planting season for central region",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.SPRING,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            name_ar="الربيع",
            name_en="Spring",
            start_month=3,
            start_day=1,
            end_month=5,
            end_day=31,
            avg_temp_min_c=16.0,
            avg_temp_max_c=35.0,
            avg_rainfall_mm=20.0,
            avg_humidity_percent=30.0,
            daylight_hours=12.5,
            frost_risk=False,
            heat_stress_risk=False,
            water_stress_level="moderate",
            description_ar="موسم الاعتدال، مناسب لزراعة الخضروات الصيفية المبكرة",
            description_en="Moderate season, suitable for early summer vegetables",
            agricultural_notes_ar="تلقيح النخيل وزراعة البطيخ",
            agricultural_notes_en="Date palm pollination and watermelon planting",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.SUMMER,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            name_ar="الصيف",
            name_en="Summer",
            start_month=6,
            start_day=1,
            end_month=8,
            end_day=31,
            avg_temp_min_c=28.0,
            avg_temp_max_c=48.0,
            avg_rainfall_mm=0.0,
            avg_humidity_percent=15.0,
            daylight_hours=14.0,
            frost_risk=False,
            heat_stress_risk=True,
            heat_stress_level="severe",
            irrigation_critical=True,
            water_stress_level="severe",
            description_ar="حرارة شديدة، الري ضروري للبقاء",
            description_en="Extreme heat, irrigation essential for survival",
            agricultural_notes_ar="التركيز على حصاد التمور وري النخيل",
            agricultural_notes_en="Focus on date harvest and palm irrigation",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.AUTUMN,
            region=region,
            climate_zone=ClimateZone.ARID_HOT,
            name_ar="الخريف",
            name_en="Autumn",
            start_month=9,
            start_day=1,
            end_month=11,
            end_day=30,
            avg_temp_min_c=18.0,
            avg_temp_max_c=38.0,
            avg_rainfall_mm=10.0,
            avg_humidity_percent=25.0,
            daylight_hours=11.5,
            frost_risk=False,
            heat_stress_risk=True,
            heat_stress_level="moderate",
            water_stress_level="moderate",
            description_ar="انحسار الحرارة، تجهيز للموسم الشتوي",
            description_en="Heat receding, preparation for winter season",
            agricultural_notes_ar="تجهيز الأرض وبدء زراعة القمح في نوفمبر",
            agricultural_notes_en="Land preparation and start wheat planting in November",
        ),
    ]


def _create_arid_mild_seasons(region: Region) -> list[SeasonDefinition]:
    """Season definitions for arid mild climate (Northern Saudi)"""
    return [
        SeasonDefinition(
            season=AgriculturalSeason.WINTER,
            region=region,
            climate_zone=ClimateZone.ARID_MILD,
            name_ar="الشتاء",
            name_en="Winter",
            start_month=12,
            start_day=1,
            end_month=2,
            end_day=28,
            avg_temp_min_c=2.0,
            avg_temp_max_c=16.0,
            avg_rainfall_mm=40.0,
            avg_humidity_percent=55.0,
            daylight_hours=10.0,
            frost_risk=True,
            frost_risk_level="high",
            heat_stress_risk=False,
            water_stress_level="low",
            description_ar="برد شديد مع صقيع، يناسب زراعة الزيتون والحبوب",
            description_en="Severe cold with frost, suitable for olives and grains",
            agricultural_notes_ar="حماية المحاصيل من الصقيع، تقليم الأشجار",
            agricultural_notes_en="Frost protection, tree pruning",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.SPRING,
            region=region,
            climate_zone=ClimateZone.ARID_MILD,
            name_ar="الربيع",
            name_en="Spring",
            start_month=3,
            start_day=1,
            end_month=5,
            end_day=31,
            avg_temp_min_c=10.0,
            avg_temp_max_c=28.0,
            avg_rainfall_mm=25.0,
            avg_humidity_percent=35.0,
            daylight_hours=12.5,
            frost_risk=True,
            frost_risk_level="low",
            heat_stress_risk=False,
            water_stress_level="low",
            description_ar="موسم ذهبي للزراعة",
            description_en="Golden season for agriculture",
            agricultural_notes_ar="زراعة البطاطس والخضروات",
            agricultural_notes_en="Potato and vegetable planting",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.SUMMER,
            region=region,
            climate_zone=ClimateZone.ARID_MILD,
            name_ar="الصيف",
            name_en="Summer",
            start_month=6,
            start_day=1,
            end_month=8,
            end_day=31,
            avg_temp_min_c=22.0,
            avg_temp_max_c=42.0,
            avg_rainfall_mm=0.0,
            avg_humidity_percent=20.0,
            daylight_hours=14.0,
            frost_risk=False,
            heat_stress_risk=True,
            heat_stress_level="high",
            irrigation_critical=True,
            water_stress_level="high",
            description_ar="حرارة مرتفعة، ري مكثف",
            description_en="High heat, intensive irrigation",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.AUTUMN,
            region=region,
            climate_zone=ClimateZone.ARID_MILD,
            name_ar="الخريف",
            name_en="Autumn",
            start_month=9,
            start_day=1,
            end_month=11,
            end_day=30,
            avg_temp_min_c=12.0,
            avg_temp_max_c=32.0,
            avg_rainfall_mm=15.0,
            avg_humidity_percent=30.0,
            daylight_hours=11.5,
            frost_risk=False,
            heat_stress_risk=False,
            water_stress_level="moderate",
            description_ar="موسم حصاد الزيتون والفواكه",
            description_en="Olive and fruit harvest season",
        ),
    ]


def _create_highland_seasons(region: Region) -> list[SeasonDefinition]:
    """Season definitions for highland climate (Asir, Yemen highlands)"""
    return [
        SeasonDefinition(
            season=AgriculturalSeason.WINTER,
            region=region,
            climate_zone=ClimateZone.HIGHLAND,
            name_ar="الشتاء",
            name_en="Winter",
            start_month=12,
            start_day=1,
            end_month=2,
            end_day=28,
            avg_temp_min_c=5.0,
            avg_temp_max_c=18.0,
            avg_rainfall_mm=50.0,
            avg_humidity_percent=60.0,
            daylight_hours=10.5,
            frost_risk=True,
            frost_risk_level="high",
            heat_stress_risk=False,
            water_stress_level="low",
            description_ar="برد جبلي، أمطار معتدلة",
            description_en="Mountain cold, moderate rainfall",
            agricultural_notes_ar="موسم راحة للبن، زراعة الحبوب",
            agricultural_notes_en="Coffee dormant season, grain planting",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.SPRING,
            region=region,
            climate_zone=ClimateZone.HIGHLAND,
            name_ar="الربيع",
            name_en="Spring",
            start_month=3,
            start_day=1,
            end_month=5,
            end_day=31,
            avg_temp_min_c=10.0,
            avg_temp_max_c=24.0,
            avg_rainfall_mm=100.0,
            avg_humidity_percent=55.0,
            daylight_hours=12.5,
            frost_risk=False,
            heat_stress_risk=False,
            water_stress_level="low",
            description_ar="موسم الأمطار الأول، ازدهار القهوة",
            description_en="First rain season, coffee flowering",
            agricultural_notes_ar="إزهار البن، زراعة الذرة",
            agricultural_notes_en="Coffee flowering, sorghum planting",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.SUMMER,
            region=region,
            climate_zone=ClimateZone.HIGHLAND,
            name_ar="الصيف",
            name_en="Summer",
            start_month=6,
            start_day=1,
            end_month=8,
            end_day=31,
            avg_temp_min_c=15.0,
            avg_temp_max_c=28.0,
            avg_rainfall_mm=150.0,
            avg_humidity_percent=65.0,
            daylight_hours=13.5,
            frost_risk=False,
            heat_stress_risk=False,
            water_stress_level="low",
            description_ar="موسم الأمطار الرئيسي (الخريف اليمني)",
            description_en="Main rain season (Yemeni Kharif)",
            agricultural_notes_ar="نمو المحاصيل، مكافحة الآفات",
            agricultural_notes_en="Crop growth, pest management",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.AUTUMN,
            region=region,
            climate_zone=ClimateZone.HIGHLAND,
            name_ar="الخريف",
            name_en="Autumn",
            start_month=9,
            start_day=1,
            end_month=11,
            end_day=30,
            avg_temp_min_c=10.0,
            avg_temp_max_c=22.0,
            avg_rainfall_mm=50.0,
            avg_humidity_percent=50.0,
            daylight_hours=11.5,
            frost_risk=False,
            heat_stress_risk=False,
            water_stress_level="low",
            description_ar="موسم الحصاد الرئيسي",
            description_en="Main harvest season",
            agricultural_notes_ar="حصاد البن والحبوب",
            agricultural_notes_en="Coffee and grain harvest",
        ),
    ]


def _create_coastal_seasons(region: Region) -> list[SeasonDefinition]:
    """Season definitions for coastal climate"""
    return [
        SeasonDefinition(
            season=AgriculturalSeason.WINTER,
            region=region,
            climate_zone=ClimateZone.COASTAL,
            name_ar="الشتاء",
            name_en="Winter",
            start_month=12,
            start_day=1,
            end_month=2,
            end_day=28,
            avg_temp_min_c=15.0,
            avg_temp_max_c=26.0,
            avg_rainfall_mm=20.0,
            avg_humidity_percent=70.0,
            daylight_hours=10.5,
            frost_risk=False,
            heat_stress_risk=False,
            water_stress_level="moderate",
            description_ar="جو معتدل رطب",
            description_en="Moderate humid weather",
            agricultural_notes_ar="موسم زراعة الخضروات",
            agricultural_notes_en="Vegetable planting season",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.SUMMER,
            region=region,
            climate_zone=ClimateZone.COASTAL,
            name_ar="الصيف",
            name_en="Summer",
            start_month=6,
            start_day=1,
            end_month=8,
            end_day=31,
            avg_temp_min_c=28.0,
            avg_temp_max_c=42.0,
            avg_rainfall_mm=0.0,
            avg_humidity_percent=75.0,
            daylight_hours=13.5,
            frost_risk=False,
            heat_stress_risk=True,
            heat_stress_level="high",
            irrigation_critical=True,
            water_stress_level="high",
            description_ar="حرارة ورطوبة عالية",
            description_en="High heat and humidity",
            agricultural_notes_ar="الزراعة المحمية، ري مكثف",
            agricultural_notes_en="Protected farming, intensive irrigation",
        ),
    ]


def _create_subtropical_seasons(region: Region) -> list[SeasonDefinition]:
    """Season definitions for subtropical climate (Jazan)"""
    return [
        SeasonDefinition(
            season=AgriculturalSeason.WINTER,
            region=region,
            climate_zone=ClimateZone.SUBTROPICAL,
            name_ar="الشتاء",
            name_en="Winter",
            start_month=11,
            start_day=1,
            end_month=2,
            end_day=28,
            avg_temp_min_c=20.0,
            avg_temp_max_c=32.0,
            avg_rainfall_mm=60.0,
            avg_humidity_percent=65.0,
            daylight_hours=11.0,
            frost_risk=False,
            heat_stress_risk=False,
            water_stress_level="low",
            description_ar="موسم الأمطار الرئيسي",
            description_en="Main rain season",
            agricultural_notes_ar="زراعة المانجو والبابايا",
            agricultural_notes_en="Mango and papaya cultivation",
        ),
        SeasonDefinition(
            season=AgriculturalSeason.SUMMER,
            region=region,
            climate_zone=ClimateZone.SUBTROPICAL,
            name_ar="الصيف",
            name_en="Summer",
            start_month=5,
            start_day=1,
            end_month=9,
            end_day=30,
            avg_temp_min_c=28.0,
            avg_temp_max_c=40.0,
            avg_rainfall_mm=100.0,
            avg_humidity_percent=70.0,
            daylight_hours=13.0,
            frost_risk=False,
            heat_stress_risk=True,
            heat_stress_level="moderate",
            water_stress_level="low",
            description_ar="حار ورطب، أمطار موسمية",
            description_en="Hot and humid, monsoon rains",
            agricultural_notes_ar="نمو الفواكه الاستوائية",
            agricultural_notes_en="Tropical fruit growth",
        ),
    ]


def _create_semi_arid_seasons(region: Region) -> list[SeasonDefinition]:
    """Season definitions for semi-arid climate"""
    return _create_arid_mild_seasons(region)


# =============================================================================
# Season Calculator Class - فئة حاسبة المواسم
# =============================================================================


class SeasonCalculator:
    """
    Calculator for agricultural seasons and traditional calendar
    حاسبة المواسم الزراعية والتقويم التقليدي
    """

    def __init__(self, region: Region | None = None):
        """Initialize with optional default region"""
        self.default_region = region
        self._season_cache: dict[Region, list[SeasonDefinition]] = {}

    def get_current_season(
        self,
        region: Region | None = None,
        check_date: date | None = None,
    ) -> SeasonDefinition | None:
        """
        Get the current agricultural season for a region
        الحصول على الموسم الزراعي الحالي لمنطقة
        """
        region = region or self.default_region
        if not region:
            return None

        if check_date is None:
            check_date = date.today()

        seasons = self._get_seasons(region)
        for season in seasons:
            if season.is_date_in_season(check_date):
                return season

        return None

    def get_current_traditional_season(
        self,
        check_date: date | None = None,
    ) -> TraditionalSeasonInfo | None:
        """
        Get the current traditional season (Naw'a)
        الحصول على النوء الحالي
        """
        if check_date is None:
            check_date = date.today()

        # Adjust to current year
        for season_info in TRADITIONAL_SEASONS.values():
            if season_info.start_date_approx and season_info.end_date_approx:
                start = season_info.start_date_approx.replace(year=check_date.year)
                end = season_info.end_date_approx.replace(year=check_date.year)

                if start <= check_date <= end:
                    return season_info

        return None

    def get_season_for_date(
        self,
        region: Region,
        check_date: date,
    ) -> tuple[SeasonDefinition | None, TraditionalSeasonInfo | None]:
        """
        Get both agricultural and traditional seasons for a date
        الحصول على الموسم الزراعي والتقليدي لتاريخ
        """
        agri_season = self.get_current_season(region, check_date)
        trad_season = self.get_current_traditional_season(check_date)
        return agri_season, trad_season

    def get_all_seasons(self, region: Region) -> list[SeasonDefinition]:
        """
        Get all season definitions for a region
        الحصول على جميع تعريفات المواسم لمنطقة
        """
        return self._get_seasons(region)

    def get_all_traditional_seasons(self) -> list[TraditionalSeasonInfo]:
        """
        Get all traditional season information
        الحصول على معلومات جميع الأنواء
        """
        return list(TRADITIONAL_SEASONS.values())

    def get_traditional_season(
        self,
        season: TraditionalSeason,
    ) -> TraditionalSeasonInfo | None:
        """
        Get information for a specific traditional season
        الحصول على معلومات نوء محدد
        """
        return TRADITIONAL_SEASONS.get(season)

    def get_region_metadata(self, region: Region) -> RegionMetadata | None:
        """
        Get metadata for a region
        الحصول على بيانات المنطقة
        """
        return REGION_METADATA.get(region)

    def get_all_regions(self, country: str | None = None) -> list[RegionMetadata]:
        """
        Get all region metadata, optionally filtered by country
        الحصول على بيانات جميع المناطق
        """
        if country:
            return [r for r in REGION_METADATA.values() if r.country == country]
        return list(REGION_METADATA.values())

    def get_season_transition_dates(
        self,
        region: Region,
        year: int,
    ) -> list[dict[str, Any]]:
        """
        Get season transition dates for a year
        الحصول على تواريخ انتقال المواسم في سنة
        """
        seasons = self._get_seasons(region)
        transitions = []

        for season in seasons:
            start, end = season.get_date_range(year)
            transitions.append({
                "season": season.season.value,
                "season_name_ar": season.name_ar,
                "season_name_en": season.name_en,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "description_ar": season.description_ar,
                "description_en": season.description_en,
            })

        return sorted(transitions, key=lambda x: x["start_date"])

    def get_upcoming_traditional_seasons(
        self,
        count: int = 5,
        from_date: date | None = None,
    ) -> list[TraditionalSeasonInfo]:
        """
        Get upcoming traditional seasons
        الحصول على الأنواء القادمة
        """
        if from_date is None:
            from_date = date.today()

        upcoming = []
        current_year = from_date.year

        # Check seasons in current and next year
        for year in [current_year, current_year + 1]:
            for season_info in TRADITIONAL_SEASONS.values():
                if season_info.start_date_approx:
                    start = season_info.start_date_approx.replace(year=year)
                    if start >= from_date:
                        # Create a copy with adjusted dates
                        adjusted = TraditionalSeasonInfo(
                            season=season_info.season,
                            name_ar=season_info.name_ar,
                            name_en=season_info.name_en,
                            start_date_approx=start,
                            end_date_approx=season_info.end_date_approx.replace(year=year)
                            if season_info.end_date_approx else None,
                            duration_days=season_info.duration_days,
                            star_name_ar=season_info.star_name_ar,
                            star_name_en=season_info.star_name_en,
                            weather_description_ar=season_info.weather_description_ar,
                            weather_description_en=season_info.weather_description_en,
                            typical_temp_min_c=season_info.typical_temp_min_c,
                            typical_temp_max_c=season_info.typical_temp_max_c,
                            agricultural_activities_ar=season_info.agricultural_activities_ar,
                            agricultural_activities_en=season_info.agricultural_activities_en,
                            recommended_crops=season_info.recommended_crops,
                            proverb_ar=season_info.proverb_ar,
                            proverb_en=season_info.proverb_en,
                        )
                        upcoming.append(adjusted)

        # Sort by start date and return requested count
        upcoming.sort(key=lambda x: x.start_date_approx or date.max)
        return upcoming[:count]

    def _get_seasons(self, region: Region) -> list[SeasonDefinition]:
        """Get or create cached season definitions for region"""
        if region not in self._season_cache:
            self._season_cache[region] = create_season_definitions(region)
        return self._season_cache[region]


# =============================================================================
# Helper Functions - الدوال المساعدة
# =============================================================================


def get_current_season(region: Region) -> SeasonDefinition | None:
    """
    Quick helper to get current season
    دالة مساعدة للحصول على الموسم الحالي
    """
    calculator = SeasonCalculator()
    return calculator.get_current_season(region)


def get_current_traditional_season() -> TraditionalSeasonInfo | None:
    """
    Quick helper to get current traditional season
    دالة مساعدة للحصول على النوء الحالي
    """
    calculator = SeasonCalculator()
    return calculator.get_current_traditional_season()


def get_region_info(region: Region) -> RegionMetadata | None:
    """
    Quick helper to get region metadata
    دالة مساعدة للحصول على بيانات المنطقة
    """
    return REGION_METADATA.get(region)


def list_saudi_regions() -> list[RegionMetadata]:
    """
    List all Saudi Arabia regions
    قائمة مناطق المملكة العربية السعودية
    """
    calculator = SeasonCalculator()
    return calculator.get_all_regions("Saudi Arabia")


def list_yemen_regions() -> list[RegionMetadata]:
    """
    List all Yemen regions
    قائمة مناطق اليمن
    """
    calculator = SeasonCalculator()
    return calculator.get_all_regions("Yemen")
