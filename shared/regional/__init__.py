"""
Regional Agricultural Data Module | وحدة البيانات الزراعية الإقليمية

Provides country-specific agricultural profiles for 6 Middle Eastern countries:
- Yemen (اليمن), Saudi Arabia (السعودية), Oman (عُمان)
- Iraq (العراق), Jordan (الأردن), Egypt (مصر)

Each profile includes:
  name_en, name_ar, climate_zones, major_crops, soil_types,
  water_sources, growing_seasons

يوفر ملفات زراعية لست دول في الشرق الأوسط مع بيانات المناخ والمحاصيل والتربة.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enumerations | التعدادات
# ---------------------------------------------------------------------------


class ClimateZone(StrEnum):
    """Climate zone classification | تصنيف المناطق المناخية"""

    ARID = "arid"
    SEMI_ARID = "semi_arid"
    HIGHLAND = "highland"
    COASTAL = "coastal"
    DESERT = "desert"
    MEDITERRANEAN = "mediterranean"
    SUBTROPICAL = "subtropical"
    TROPICAL_MONSOON = "tropical_monsoon"


class SoilCategory(StrEnum):
    """Soil category | فئة التربة"""

    VOLCANIC = "volcanic"
    ALLUVIAL = "alluvial"
    SANDY = "sandy"
    CALCAREOUS = "calcareous"
    SALINE = "saline"
    CLAY = "clay"
    LOAMY = "loamy"
    GRAVEL = "gravel"
    ROCKY = "rocky"
    MARSH = "marsh"
    DESERT = "desert"
    TERRA_ROSSA = "terra_rossa"
    GYPSIFEROUS = "gypsiferous"


class WaterSourceType(StrEnum):
    """Water source type | نوع مصدر المياه"""

    WELLS = "wells"
    SPRINGS = "springs"
    SPATE = "spate_irrigation"
    TERRACES = "terraces"
    DESALINATION = "desalination"
    GROUNDWATER = "groundwater"
    DAMS = "dams"
    CANALS = "canals"
    RIVER = "river"
    AFLAJ = "aflaj"
    TREATED_WASTEWATER = "treated_wastewater"
    WADI = "wadi"


class GrowingSeason(StrEnum):
    """Growing season | موسم الزراعة"""

    WINTER = "winter"
    SUMMER = "summer"
    YEAR_ROUND = "year_round"


# Arabic translations | الترجمات العربية
CLIMATE_ZONE_AR: dict[ClimateZone, str] = {
    ClimateZone.ARID: "جاف",
    ClimateZone.SEMI_ARID: "شبه جاف",
    ClimateZone.HIGHLAND: "مرتفعات",
    ClimateZone.COASTAL: "ساحلي",
    ClimateZone.DESERT: "صحراوي",
    ClimateZone.MEDITERRANEAN: "متوسطي",
    ClimateZone.SUBTROPICAL: "شبه استوائي",
    ClimateZone.TROPICAL_MONSOON: "استوائي موسمي",
}

SOIL_CATEGORY_AR: dict[SoilCategory, str] = {
    SoilCategory.VOLCANIC: "بركانية",
    SoilCategory.ALLUVIAL: "رسوبية / طميية",
    SoilCategory.SANDY: "رملية",
    SoilCategory.CALCAREOUS: "كلسية",
    SoilCategory.SALINE: "ملحية",
    SoilCategory.CLAY: "طينية",
    SoilCategory.LOAMY: "لومية",
    SoilCategory.GRAVEL: "حصوية",
    SoilCategory.ROCKY: "صخرية",
    SoilCategory.MARSH: "مستنقعية",
    SoilCategory.DESERT: "صحراوية",
    SoilCategory.TERRA_ROSSA: "تراروسا",
    SoilCategory.GYPSIFEROUS: "جبسية",
}

WATER_SOURCE_AR: dict[WaterSourceType, str] = {
    WaterSourceType.WELLS: "آبار",
    WaterSourceType.SPRINGS: "ينابيع",
    WaterSourceType.SPATE: "ري سيول",
    WaterSourceType.TERRACES: "مدرجات",
    WaterSourceType.DESALINATION: "تحلية",
    WaterSourceType.GROUNDWATER: "مياه جوفية",
    WaterSourceType.DAMS: "سدود",
    WaterSourceType.CANALS: "قنوات",
    WaterSourceType.RIVER: "نهر",
    WaterSourceType.AFLAJ: "أفلاج",
    WaterSourceType.TREATED_WASTEWATER: "مياه معالجة",
    WaterSourceType.WADI: "وادي",
}

SEASON_AR: dict[GrowingSeason, str] = {
    GrowingSeason.WINTER: "شتوي",
    GrowingSeason.SUMMER: "صيفي",
    GrowingSeason.YEAR_ROUND: "على مدار السنة",
}


# ---------------------------------------------------------------------------
# Data classes | فئات البيانات
# ---------------------------------------------------------------------------


@dataclass
class CropEntry:
    """A major crop for a country | محصول رئيسي لدولة"""

    name_en: str = ""
    name_ar: str = ""
    area_ha: int = 0
    region: str = ""
    season: GrowingSeason = GrowingSeason.WINTER
    season_ar: str = ""


@dataclass
class SeasonWindow:
    """A growing season window | نافذة موسم زراعي"""

    season: GrowingSeason = GrowingSeason.WINTER
    season_ar: str = ""
    start_month: str = ""
    end_month: str = ""
    crops: list[str] = field(default_factory=list)
    description_en: str = ""
    description_ar: str = ""


@dataclass
class ClimateInfo:
    """Climate summary for a region | ملخص المناخ لمنطقة"""

    zone: ClimateZone = ClimateZone.ARID
    zone_ar: str = ""
    avg_temp_summer_c: float = 0.0
    avg_temp_winter_c: float = 0.0
    annual_rainfall_mm: float = 0.0
    description_en: str = ""
    description_ar: str = ""


@dataclass
class CountryProfile:
    """Agricultural profile for a country | ملف زراعي لدولة"""

    country_code: str = ""
    name_en: str = ""
    name_ar: str = ""
    capital: str = ""
    capital_ar: str = ""
    arable_land_hectares: int = 0
    climate_zones: list[ClimateZone] = field(default_factory=list)
    climate_zones_ar: list[str] = field(default_factory=list)
    major_crops: list[CropEntry] = field(default_factory=list)
    soil_types: list[SoilCategory] = field(default_factory=list)
    soil_types_ar: list[str] = field(default_factory=list)
    water_sources: list[WaterSourceType] = field(default_factory=list)
    water_sources_ar: list[str] = field(default_factory=list)
    growing_seasons: list[SeasonWindow] = field(default_factory=list)
    climate_data: list[ClimateInfo] = field(default_factory=list)
    currency: str = ""
    currency_ar: str = ""
    dialect: str = ""
    dialect_ar: str = ""
    notes_en: str = ""
    notes_ar: str = ""

    # Legacy compat aliases -----------------------------------------------
    @property
    def name(self) -> str:
        """Alias for name_en (backward compat)."""
        return self.name_en

    @property
    def main_crops(self) -> list[dict]:
        """Legacy dict representation of major_crops."""
        return [
            {
                "crop": c.name_en.lower().replace(" ", "_"),
                "crop_ar": c.name_ar,
                "area_ha": c.area_ha,
                "region": c.region,
            }
            for c in self.major_crops
        ]


# ---------------------------------------------------------------------------
# Country data builders | بناة بيانات الدول
# ---------------------------------------------------------------------------


def _build_yemen() -> CountryProfile:
    """Build Yemen profile | بناء ملف اليمن"""
    zones = [ClimateZone.ARID, ClimateZone.SEMI_ARID, ClimateZone.HIGHLAND, ClimateZone.COASTAL]
    soils = [SoilCategory.VOLCANIC, SoilCategory.ALLUVIAL, SoilCategory.SANDY, SoilCategory.CALCAREOUS]
    waters = [WaterSourceType.WELLS, WaterSourceType.SPATE, WaterSourceType.TERRACES, WaterSourceType.SPRINGS]
    return CountryProfile(
        country_code="YE",
        name_en="Yemen",
        name_ar="اليمن",
        capital="Sana'a",
        capital_ar="صنعاء",
        arable_land_hectares=1_600_000,
        climate_zones=zones,
        climate_zones_ar=[CLIMATE_ZONE_AR[z] for z in zones],
        major_crops=[
            CropEntry(
                name_en="Coffee",
                name_ar="بُن",
                area_ha=34_000,
                region="highlands",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Qat",
                name_ar="قات",
                area_ha=167_000,
                region="highlands",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Sorghum",
                name_ar="ذرة رفيعة",
                area_ha=350_000,
                region="highlands",
                season=GrowingSeason.SUMMER,
                season_ar=SEASON_AR[GrowingSeason.SUMMER],
            ),
            CropEntry(
                name_en="Wheat",
                name_ar="قمح",
                area_ha=100_000,
                region="highlands",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Mango",
                name_ar="مانجو",
                area_ha=12_000,
                region="tihama",
                season=GrowingSeason.SUMMER,
                season_ar=SEASON_AR[GrowingSeason.SUMMER],
            ),
            CropEntry(
                name_en="Date Palm",
                name_ar="نخيل",
                area_ha=20_000,
                region="hadramout",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
        ],
        soil_types=soils,
        soil_types_ar=[SOIL_CATEGORY_AR[s] for s in soils],
        water_sources=waters,
        water_sources_ar=[WATER_SOURCE_AR[w] for w in waters],
        growing_seasons=[
            SeasonWindow(
                season=GrowingSeason.WINTER,
                season_ar="شتوي",
                start_month="October",
                end_month="November",
                crops=["wheat", "barley"],
                description_en="Main cereal planting",
                description_ar="زراعة الحبوب الرئيسية",
            ),
            SeasonWindow(
                season=GrowingSeason.SUMMER,
                season_ar="صيفي",
                start_month="March",
                end_month="April",
                crops=["sorghum", "millet"],
                description_en="Summer crops planting",
                description_ar="زراعة المحاصيل الصيفية",
            ),
        ],
        climate_data=[
            ClimateInfo(
                zone=ClimateZone.HIGHLAND,
                zone_ar="مرتفعات",
                avg_temp_summer_c=25.0,
                avg_temp_winter_c=12.0,
                annual_rainfall_mm=500.0,
                description_en="Yemen highlands - coffee region",
                description_ar="مرتفعات اليمن - منطقة البُن",
            ),
            ClimateInfo(
                zone=ClimateZone.COASTAL,
                zone_ar="ساحلي",
                avg_temp_summer_c=38.0,
                avg_temp_winter_c=25.0,
                annual_rainfall_mm=50.0,
                description_en="Tihama coastal plain",
                description_ar="سهل تهامة الساحلي",
            ),
        ],
        currency="YER",
        currency_ar="ريال يمني",
        dialect="yemeni",
        dialect_ar="يمنية",
        notes_en="Water scarcity is a critical challenge. Terraced farming in highlands.",
        notes_ar="شح المياه تحدٍ حرج. الزراعة المدرجة في المرتفعات.",
    )


def _build_saudi() -> CountryProfile:
    """Build Saudi Arabia profile | بناء ملف السعودية"""
    zones = [ClimateZone.DESERT, ClimateZone.ARID, ClimateZone.SEMI_ARID]
    soils = [SoilCategory.SANDY, SoilCategory.SALINE, SoilCategory.CALCAREOUS, SoilCategory.GYPSIFEROUS]
    waters = [
        WaterSourceType.DESALINATION,
        WaterSourceType.GROUNDWATER,
        WaterSourceType.DAMS,
        WaterSourceType.TREATED_WASTEWATER,
    ]
    return CountryProfile(
        country_code="SA",
        name_en="Saudi Arabia",
        name_ar="المملكة العربية السعودية",
        capital="Riyadh",
        capital_ar="الرياض",
        arable_land_hectares=3_500_000,
        climate_zones=zones,
        climate_zones_ar=[CLIMATE_ZONE_AR[z] for z in zones],
        major_crops=[
            CropEntry(
                name_en="Date Palm",
                name_ar="نخيل",
                area_ha=170_000,
                region="qassim",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Wheat",
                name_ar="قمح",
                area_ha=400_000,
                region="central",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Tomato",
                name_ar="طماطم",
                area_ha=15_000,
                region="southwest",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Alfalfa",
                name_ar="برسيم",
                area_ha=200_000,
                region="central",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Cucumber",
                name_ar="خيار",
                area_ha=5_000,
                region="greenhouse",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Watermelon",
                name_ar="بطيخ",
                area_ha=30_000,
                region="southwest",
                season=GrowingSeason.SUMMER,
                season_ar=SEASON_AR[GrowingSeason.SUMMER],
            ),
        ],
        soil_types=soils,
        soil_types_ar=[SOIL_CATEGORY_AR[s] for s in soils],
        water_sources=waters,
        water_sources_ar=[WATER_SOURCE_AR[w] for w in waters],
        growing_seasons=[
            SeasonWindow(
                season=GrowingSeason.WINTER,
                season_ar="شتوي",
                start_month="November",
                end_month="December",
                crops=["wheat", "barley", "vegetables"],
                description_en="Main cereal and vegetable planting",
                description_ar="زراعة الحبوب والخضروات",
            ),
            SeasonWindow(
                season=GrowingSeason.SUMMER,
                season_ar="صيفي",
                start_month="March",
                end_month="April",
                crops=["date_palm_pollination", "watermelon"],
                description_en="Date pollination and summer crops",
                description_ar="تلقيح النخيل ومحاصيل صيفية",
            ),
        ],
        climate_data=[
            ClimateInfo(
                zone=ClimateZone.DESERT,
                zone_ar="صحراوي",
                avg_temp_summer_c=45.0,
                avg_temp_winter_c=15.0,
                annual_rainfall_mm=80.0,
                description_en="Central desert - Najd",
                description_ar="الصحراء الوسطى - نجد",
            ),
        ],
        currency="SAR",
        currency_ar="ريال سعودي",
        dialect="saudi",
        dialect_ar="سعودية",
        notes_en="Relies heavily on non-renewable groundwater. Vision 2030 promotes sustainability.",
        notes_ar="تعتمد على المياه الجوفية غير المتجددة. رؤية 2030 تعزز الاستدامة.",
    )


def _build_oman() -> CountryProfile:
    """Build Oman profile | بناء ملف عُمان"""
    zones = [ClimateZone.ARID, ClimateZone.TROPICAL_MONSOON]
    soils = [SoilCategory.SANDY, SoilCategory.ALLUVIAL, SoilCategory.GRAVEL]
    waters = [WaterSourceType.AFLAJ, WaterSourceType.WELLS, WaterSourceType.DESALINATION, WaterSourceType.DAMS]
    return CountryProfile(
        country_code="OM",
        name_en="Oman",
        name_ar="عُمان",
        capital="Muscat",
        capital_ar="مسقط",
        arable_land_hectares=60_000,
        climate_zones=zones,
        climate_zones_ar=[CLIMATE_ZONE_AR[z] for z in zones],
        major_crops=[
            CropEntry(
                name_en="Date Palm",
                name_ar="نخيل",
                area_ha=32_000,
                region="interior",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Lime",
                name_ar="ليمون",
                area_ha=5_000,
                region="batinah",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Banana",
                name_ar="موز",
                area_ha=3_000,
                region="dhofar",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Alfalfa",
                name_ar="برسيم",
                area_ha=8_000,
                region="interior",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
        ],
        soil_types=soils,
        soil_types_ar=[SOIL_CATEGORY_AR[s] for s in soils],
        water_sources=waters,
        water_sources_ar=[WATER_SOURCE_AR[w] for w in waters],
        growing_seasons=[
            SeasonWindow(
                season=GrowingSeason.WINTER,
                season_ar="شتوي",
                start_month="October",
                end_month="March",
                crops=["alfalfa", "vegetables"],
                description_en="Winter growing season",
                description_ar="موسم الزراعة الشتوي",
            ),
            SeasonWindow(
                season=GrowingSeason.SUMMER,
                season_ar="صيفي",
                start_month="April",
                end_month="September",
                crops=["date_palm"],
                description_en="Date harvest season",
                description_ar="موسم حصاد التمور",
            ),
        ],
        climate_data=[
            ClimateInfo(
                zone=ClimateZone.ARID,
                zone_ar="جاف",
                avg_temp_summer_c=42.0,
                avg_temp_winter_c=20.0,
                annual_rainfall_mm=100.0,
                description_en="Batinah coast - main farming",
                description_ar="ساحل الباطنة - الزراعة الرئيسية",
            ),
        ],
        currency="OMR",
        currency_ar="ريال عماني",
        dialect="omani",
        dialect_ar="عمانية",
        notes_en="Traditional aflaj irrigation system (UNESCO Heritage). Salinity is a major challenge.",
        notes_ar="نظام الأفلاج التقليدي (تراث يونسكو). الملوحة تحدٍ رئيسي.",
    )


def _build_iraq() -> CountryProfile:
    """Build Iraq profile | بناء ملف العراق"""
    zones = [ClimateZone.ARID, ClimateZone.SEMI_ARID, ClimateZone.MEDITERRANEAN]
    soils = [SoilCategory.ALLUVIAL, SoilCategory.SALINE, SoilCategory.MARSH]
    waters = [WaterSourceType.RIVER, WaterSourceType.CANALS, WaterSourceType.GROUNDWATER]
    return CountryProfile(
        country_code="IQ",
        name_en="Iraq",
        name_ar="العراق",
        capital="Baghdad",
        capital_ar="بغداد",
        arable_land_hectares=8_000_000,
        climate_zones=zones,
        climate_zones_ar=[CLIMATE_ZONE_AR[z] for z in zones],
        major_crops=[
            CropEntry(
                name_en="Wheat",
                name_ar="حنطة",
                area_ha=2_500_000,
                region="central",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Barley",
                name_ar="شعير",
                area_ha=1_200_000,
                region="central",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Rice",
                name_ar="تمن",
                area_ha=200_000,
                region="south",
                season=GrowingSeason.SUMMER,
                season_ar=SEASON_AR[GrowingSeason.SUMMER],
            ),
            CropEntry(
                name_en="Date Palm",
                name_ar="نخيل",
                area_ha=160_000,
                region="south",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Tomato",
                name_ar="طماطة",
                area_ha=80_000,
                region="central",
                season=GrowingSeason.SUMMER,
                season_ar=SEASON_AR[GrowingSeason.SUMMER],
            ),
        ],
        soil_types=soils,
        soil_types_ar=[SOIL_CATEGORY_AR[s] for s in soils],
        water_sources=waters,
        water_sources_ar=[WATER_SOURCE_AR[w] for w in waters],
        growing_seasons=[
            SeasonWindow(
                season=GrowingSeason.WINTER,
                season_ar="شتوي",
                start_month="October",
                end_month="April",
                crops=["wheat", "barley"],
                description_en="Rainfed north, irrigated south",
                description_ar="بعلي شمالاً ومروي جنوباً",
            ),
            SeasonWindow(
                season=GrowingSeason.SUMMER,
                season_ar="صيفي",
                start_month="May",
                end_month="September",
                crops=["rice", "cotton", "vegetables"],
                description_en="Rice and summer crops",
                description_ar="الأرز والمحاصيل الصيفية",
            ),
        ],
        climate_data=[
            ClimateInfo(
                zone=ClimateZone.SUBTROPICAL,
                zone_ar="شبه استوائي",
                avg_temp_summer_c=42.0,
                avg_temp_winter_c=10.0,
                annual_rainfall_mm=150.0,
                description_en="Mesopotamian plain - Tigris & Euphrates",
                description_ar="سهل بلاد الرافدين",
            ),
        ],
        currency="IQD",
        currency_ar="دينار عراقي",
        dialect="iraqi",
        dialect_ar="عراقية",
        notes_en="Historically the Fertile Crescent. Salinity from ancient irrigation. Water declining.",
        notes_ar="تاريخياً الهلال الخصيب. ملوحة من الري القديم. تراجع المياه.",
    )


def _build_jordan() -> CountryProfile:
    """Build Jordan profile | بناء ملف الأردن"""
    zones = [ClimateZone.SEMI_ARID, ClimateZone.MEDITERRANEAN, ClimateZone.ARID]
    soils = [SoilCategory.TERRA_ROSSA, SoilCategory.ALLUVIAL, SoilCategory.DESERT]
    waters = [
        WaterSourceType.DAMS,
        WaterSourceType.GROUNDWATER,
        WaterSourceType.TREATED_WASTEWATER,
        WaterSourceType.RIVER,
    ]
    return CountryProfile(
        country_code="JO",
        name_en="Jordan",
        name_ar="الأردن",
        capital="Amman",
        capital_ar="عمّان",
        arable_land_hectares=400_000,
        climate_zones=zones,
        climate_zones_ar=[CLIMATE_ZONE_AR[z] for z in zones],
        major_crops=[
            CropEntry(
                name_en="Tomato",
                name_ar="بندورة",
                area_ha=15_000,
                region="jordan_valley",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Olive",
                name_ar="زيتون",
                area_ha=65_000,
                region="highlands",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Wheat",
                name_ar="قمح",
                area_ha=30_000,
                region="central",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Cucumber",
                name_ar="خيار",
                area_ha=8_000,
                region="jordan_valley",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
        ],
        soil_types=soils,
        soil_types_ar=[SOIL_CATEGORY_AR[s] for s in soils],
        water_sources=waters,
        water_sources_ar=[WATER_SOURCE_AR[w] for w in waters],
        growing_seasons=[
            SeasonWindow(
                season=GrowingSeason.WINTER,
                season_ar="شتوي",
                start_month="October",
                end_month="April",
                crops=["tomato", "cucumber", "wheat"],
                description_en="Main vegetable and cereal season",
                description_ar="موسم الخضروات والحبوب الرئيسي",
            ),
            SeasonWindow(
                season=GrowingSeason.SUMMER,
                season_ar="صيفي",
                start_month="May",
                end_month="September",
                crops=["greenhouse_crops"],
                description_en="Jordan Valley greenhouse crops",
                description_ar="محاصيل بيوت محمية",
            ),
        ],
        climate_data=[
            ClimateInfo(
                zone=ClimateZone.SEMI_ARID,
                zone_ar="شبه جاف",
                avg_temp_summer_c=35.0,
                avg_temp_winter_c=8.0,
                annual_rainfall_mm=250.0,
                description_en="Jordan Valley - irrigated",
                description_ar="وادي الأردن - مروي",
            ),
            ClimateInfo(
                zone=ClimateZone.MEDITERRANEAN,
                zone_ar="متوسطي",
                avg_temp_summer_c=28.0,
                avg_temp_winter_c=5.0,
                annual_rainfall_mm=450.0,
                description_en="Highland plateau - olive growing",
                description_ar="الهضبة - زراعة الزيتون",
            ),
        ],
        currency="JOD",
        currency_ar="دينار أردني",
        dialect="jordanian",
        dialect_ar="أردنية",
        notes_en="One of the most water-scarce countries globally. Jordan Valley is the food basket.",
        notes_ar="من أكثر الدول شحاً بالمياه عالمياً. وادي الأردن سلة الغذاء.",
    )


def _build_egypt() -> CountryProfile:
    """Build Egypt profile | بناء ملف مصر"""
    zones = [ClimateZone.ARID, ClimateZone.MEDITERRANEAN]
    soils = [SoilCategory.ALLUVIAL, SoilCategory.DESERT, SoilCategory.SALINE]
    waters = [WaterSourceType.RIVER, WaterSourceType.CANALS, WaterSourceType.GROUNDWATER]
    return CountryProfile(
        country_code="EG",
        name_en="Egypt",
        name_ar="مصر",
        capital="Cairo",
        capital_ar="القاهرة",
        arable_land_hectares=3_600_000,
        climate_zones=zones,
        climate_zones_ar=[CLIMATE_ZONE_AR[z] for z in zones],
        major_crops=[
            CropEntry(
                name_en="Wheat",
                name_ar="قمح",
                area_ha=1_400_000,
                region="delta",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
            CropEntry(
                name_en="Rice",
                name_ar="أرز",
                area_ha=500_000,
                region="delta",
                season=GrowingSeason.SUMMER,
                season_ar=SEASON_AR[GrowingSeason.SUMMER],
            ),
            CropEntry(
                name_en="Cotton",
                name_ar="قطن",
                area_ha=100_000,
                region="upper_egypt",
                season=GrowingSeason.SUMMER,
                season_ar=SEASON_AR[GrowingSeason.SUMMER],
            ),
            CropEntry(
                name_en="Sugarcane",
                name_ar="قصب سكر",
                area_ha=130_000,
                region="upper_egypt",
                season=GrowingSeason.YEAR_ROUND,
                season_ar=SEASON_AR[GrowingSeason.YEAR_ROUND],
            ),
            CropEntry(
                name_en="Corn",
                name_ar="ذرة",
                area_ha=800_000,
                region="delta",
                season=GrowingSeason.SUMMER,
                season_ar=SEASON_AR[GrowingSeason.SUMMER],
            ),
            CropEntry(
                name_en="Clover",
                name_ar="برسيم",
                area_ha=1_000_000,
                region="delta",
                season=GrowingSeason.WINTER,
                season_ar=SEASON_AR[GrowingSeason.WINTER],
            ),
        ],
        soil_types=soils,
        soil_types_ar=[SOIL_CATEGORY_AR[s] for s in soils],
        water_sources=waters,
        water_sources_ar=[WATER_SOURCE_AR[w] for w in waters],
        growing_seasons=[
            SeasonWindow(
                season=GrowingSeason.WINTER,
                season_ar="شتوي",
                start_month="October",
                end_month="April",
                crops=["wheat", "clover", "vegetables"],
                description_en="Wheat, berseem, vegetables",
                description_ar="قمح وبرسيم وخضروات",
            ),
            SeasonWindow(
                season=GrowingSeason.SUMMER,
                season_ar="صيفي",
                start_month="May",
                end_month="September",
                crops=["rice", "cotton", "corn"],
                description_en="Rice, cotton, maize",
                description_ar="أرز وقطن وذرة",
            ),
        ],
        climate_data=[
            ClimateInfo(
                zone=ClimateZone.SUBTROPICAL,
                zone_ar="شبه استوائي",
                avg_temp_summer_c=35.0,
                avg_temp_winter_c=12.0,
                annual_rainfall_mm=25.0,
                description_en="Nile Valley and Delta",
                description_ar="وادي ودلتا النيل",
            ),
            ClimateInfo(
                zone=ClimateZone.MEDITERRANEAN,
                zone_ar="متوسطي",
                avg_temp_summer_c=30.0,
                avg_temp_winter_c=13.0,
                annual_rainfall_mm=180.0,
                description_en="North coast",
                description_ar="الساحل الشمالي",
            ),
        ],
        currency="EGP",
        currency_ar="جنيه مصري",
        dialect="egyptian",
        dialect_ar="مصرية",
        notes_en="97% of agriculture in Nile Valley & Delta. Aswan High Dam provides regulation.",
        notes_ar="97% من الزراعة في وادي ودلتا النيل. السد العالي ينظم المياه.",
    )


# ---------------------------------------------------------------------------
# All country data (legacy dict kept for backward compat)
# ---------------------------------------------------------------------------
COUNTRY_PROFILES: dict[str, dict] = {
    "YE": {
        "name": "Yemen",
        "name_ar": "اليمن",
        "capital": "Sana'a",
        "capital_ar": "صنعاء",
        "arable_land_hectares": 1_600_000,
        "main_crops": [
            {"crop": "coffee", "crop_ar": "بُن", "area_ha": 34_000, "region": "highlands"},
            {"crop": "qat", "crop_ar": "قات", "area_ha": 167_000, "region": "highlands"},
            {"crop": "sorghum", "crop_ar": "ذرة رفيعة", "area_ha": 350_000, "region": "highlands"},
            {"crop": "wheat", "crop_ar": "قمح", "area_ha": 100_000, "region": "highlands"},
            {"crop": "mango", "crop_ar": "مانجو", "area_ha": 12_000, "region": "tihama"},
            {"crop": "date_palm", "crop_ar": "نخيل", "area_ha": 20_000, "region": "hadramout"},
        ],
        "climate_zones": ["arid", "semi-arid", "highland-temperate"],
        "water_sources": ["wells", "spate_irrigation", "terraces", "springs"],
        "soil_types": ["volcanic", "alluvial", "sandy", "calcareous"],
        "currency": "YER",
        "currency_ar": "ريال يمني",
        "dialect": "yemeni",
        "dialect_ar": "يمنية",
    },
    "SA": {
        "name": "Saudi Arabia",
        "name_ar": "المملكة العربية السعودية",
        "capital": "Riyadh",
        "capital_ar": "الرياض",
        "arable_land_hectares": 3_500_000,
        "main_crops": [
            {"crop": "date_palm", "crop_ar": "نخيل", "area_ha": 170_000, "region": "qassim"},
            {"crop": "wheat", "crop_ar": "قمح", "area_ha": 400_000, "region": "central"},
            {"crop": "tomato", "crop_ar": "طماطم", "area_ha": 15_000, "region": "southwest"},
            {"crop": "alfalfa", "crop_ar": "برسيم", "area_ha": 200_000, "region": "central"},
            {"crop": "cucumber", "crop_ar": "خيار", "area_ha": 5_000, "region": "greenhouse"},
            {"crop": "watermelon", "crop_ar": "بطيخ", "area_ha": 30_000, "region": "southwest"},
        ],
        "climate_zones": ["hyper-arid", "arid", "semi-arid"],
        "water_sources": ["desalination", "groundwater", "dams", "treated_wastewater"],
        "soil_types": ["sandy", "saline", "calcareous", "gypsiferous"],
        "currency": "SAR",
        "currency_ar": "ريال سعودي",
        "dialect": "saudi",
        "dialect_ar": "سعودية",
    },
    "OM": {
        "name": "Oman",
        "name_ar": "عُمان",
        "capital": "Muscat",
        "capital_ar": "مسقط",
        "arable_land_hectares": 60_000,
        "main_crops": [
            {"crop": "date_palm", "crop_ar": "نخيل", "area_ha": 32_000, "region": "interior"},
            {"crop": "lime", "crop_ar": "ليمون", "area_ha": 5_000, "region": "batinah"},
            {"crop": "banana", "crop_ar": "موز", "area_ha": 3_000, "region": "dhofar"},
            {"crop": "alfalfa", "crop_ar": "برسيم", "area_ha": 8_000, "region": "interior"},
        ],
        "climate_zones": ["arid", "tropical-monsoon"],
        "water_sources": ["aflaj", "wells", "desalination", "dams"],
        "soil_types": ["sandy", "alluvial", "gravel"],
        "currency": "OMR",
        "currency_ar": "ريال عماني",
        "dialect": "omani",
        "dialect_ar": "عمانية",
    },
    "IQ": {
        "name": "Iraq",
        "name_ar": "العراق",
        "capital": "Baghdad",
        "capital_ar": "بغداد",
        "arable_land_hectares": 8_000_000,
        "main_crops": [
            {"crop": "wheat", "crop_ar": "حنطة", "area_ha": 2_500_000, "region": "central"},
            {"crop": "barley", "crop_ar": "شعير", "area_ha": 1_200_000, "region": "central"},
            {"crop": "rice", "crop_ar": "تمن", "area_ha": 200_000, "region": "south"},
            {"crop": "date_palm", "crop_ar": "نخيل", "area_ha": 160_000, "region": "south"},
            {"crop": "tomato", "crop_ar": "طماطة", "area_ha": 80_000, "region": "central"},
        ],
        "climate_zones": ["arid", "semi-arid", "mediterranean"],
        "water_sources": ["tigris", "euphrates", "canals", "groundwater"],
        "soil_types": ["alluvial", "saline", "marsh"],
        "currency": "IQD",
        "currency_ar": "دينار عراقي",
        "dialect": "iraqi",
        "dialect_ar": "عراقية",
    },
    "JO": {
        "name": "Jordan",
        "name_ar": "الأردن",
        "capital": "Amman",
        "capital_ar": "عمّان",
        "arable_land_hectares": 400_000,
        "main_crops": [
            {"crop": "tomato", "crop_ar": "بندورة", "area_ha": 15_000, "region": "jordan_valley"},
            {"crop": "olive", "crop_ar": "زيتون", "area_ha": 65_000, "region": "highlands"},
            {"crop": "wheat", "crop_ar": "قمح", "area_ha": 30_000, "region": "central"},
            {"crop": "cucumber", "crop_ar": "خيار", "area_ha": 8_000, "region": "jordan_valley"},
        ],
        "climate_zones": ["semi-arid", "mediterranean", "arid"],
        "water_sources": ["dams", "groundwater", "treated_wastewater", "jordan_river"],
        "soil_types": ["terra_rossa", "alluvial", "desert"],
        "currency": "JOD",
        "currency_ar": "دينار أردني",
        "dialect": "jordanian",
        "dialect_ar": "أردنية",
    },
    "EG": {
        "name": "Egypt",
        "name_ar": "مصر",
        "capital": "Cairo",
        "capital_ar": "القاهرة",
        "arable_land_hectares": 3_600_000,
        "main_crops": [
            {"crop": "wheat", "crop_ar": "قمح", "area_ha": 1_400_000, "region": "delta"},
            {"crop": "rice", "crop_ar": "أرز", "area_ha": 500_000, "region": "delta"},
            {"crop": "cotton", "crop_ar": "قطن", "area_ha": 100_000, "region": "upper_egypt"},
            {"crop": "sugarcane", "crop_ar": "قصب سكر", "area_ha": 130_000, "region": "upper_egypt"},
            {"crop": "corn", "crop_ar": "ذرة", "area_ha": 800_000, "region": "delta"},
            {"crop": "clover", "crop_ar": "برسيم", "area_ha": 1_000_000, "region": "delta"},
        ],
        "climate_zones": ["arid", "mediterranean"],
        "water_sources": ["nile", "canals", "groundwater"],
        "soil_types": ["alluvial_nile", "desert", "saline"],
        "currency": "EGP",
        "currency_ar": "جنيه مصري",
        "dialect": "egyptian",
        "dialect_ar": "مصرية",
    },
}


# Country profile builders
_PROFILE_BUILDERS: dict[str, callable] = {
    "YE": _build_yemen,
    "SA": _build_saudi,
    "OM": _build_oman,
    "IQ": _build_iraq,
    "JO": _build_jordan,
    "EG": _build_egypt,
}


class RegionalDataManager:
    """Manages country-specific agricultural data.

    يدير البيانات الزراعية الخاصة بكل دولة.
    Supports 6 Middle Eastern countries with bilingual data.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, CountryProfile] = {}
        for code, builder in _PROFILE_BUILDERS.items():
            self._profiles[code] = builder()

    # ----- New API (required by specification) -------------------------

    def get_country_profile(self, country_code: str) -> CountryProfile | None:
        """Get a country agricultural profile by ISO 2-letter code.

        الحصول على الملف الزراعي للدولة برمز ISO.

        Args:
            country_code: ISO 3166-1 alpha-2 (e.g. 'YE', 'SA')

        Returns:
            CountryProfile or None if not found.
        """
        return self._profiles.get(country_code.upper())

    def get_suitable_crops(
        self,
        country_code: str,
        season: GrowingSeason | None = None,
    ) -> list[CropEntry]:
        """Get crops suitable for given conditions in a country.

        الحصول على المحاصيل المناسبة للظروف في دولة معينة.

        Args:
            country_code: ISO 2-letter code
            season: Optional filter by growing season

        Returns:
            List of CropEntry matching the filters.
        """
        profile = self.get_country_profile(country_code)
        if not profile:
            return []
        crops = list(profile.major_crops)
        if season is not None:
            crops = [c for c in crops if c.season == season or c.season == GrowingSeason.YEAR_ROUND]
        return crops

    def get_climate_data(
        self,
        country_code: str,
        zone: ClimateZone | None = None,
    ) -> list[ClimateInfo]:
        """Get climate data for a country, optionally by zone.

        الحصول على بيانات المناخ لدولة، مع تصفية حسب المنطقة.

        Args:
            country_code: ISO 2-letter code
            zone: Optional filter by climate zone

        Returns:
            List of ClimateInfo items.
        """
        profile = self.get_country_profile(country_code)
        if not profile:
            return []
        data = list(profile.climate_data)
        if zone is not None:
            data = [d for d in data if d.zone == zone]
        return data

    # ----- Legacy API (backward compatibility) -------------------------

    def get_country(self, code: str) -> CountryProfile | None:
        """Legacy: get country profile by code (alias for get_country_profile)."""
        return self.get_country_profile(code)

    def list_countries(self) -> list[CountryProfile]:
        """List all supported country profiles."""
        return list(self._profiles.values())

    def get_crops_for_country(self, code: str) -> list[dict]:
        """Legacy: get main crops for a country as dicts."""
        data = COUNTRY_PROFILES.get(code, {})
        return data.get("main_crops", [])

    def find_countries_for_crop(self, crop_type: str) -> list[str]:
        """Find countries that grow a specific crop.

        البحث عن الدول التي تزرع محصولاً معيناً.
        """
        countries = []
        for code, data in COUNTRY_PROFILES.items():
            for crop in data.get("main_crops", []):
                if crop["crop"] == crop_type:
                    countries.append(code)
                    break
        return countries
