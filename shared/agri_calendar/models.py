"""
Agricultural Calendar Models - نماذج التقويم الزراعي

Data models for agricultural calendar, seasons, planting events,
Islamic calendar integration, and traditional farming calendar.

Supports:
- Saudi Arabia and Yemen regional climates
- Hijri (Islamic) and Gregorian calendars
- Traditional farming seasons (Anwa'a - الأنواء)
- Bilingual Arabic/English content

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from enum import StrEnum
from typing import Any

# =============================================================================
# Enums - التعدادات
# =============================================================================


class CalendarType(StrEnum):
    """Calendar system types"""

    GREGORIAN = "gregorian"  # ميلادي
    HIJRI = "hijri"  # هجري
    BOTH = "both"  # كلاهما


class Region(StrEnum):
    """Agricultural regions in Saudi Arabia and Yemen"""

    # Saudi Arabia regions
    RIYADH = "riyadh"  # الرياض
    QASSIM = "qassim"  # القصيم
    HAIL = "hail"  # حائل
    EASTERN = "eastern"  # الشرقية
    ASIR = "asir"  # عسير
    NAJRAN = "najran"  # نجران
    JAZAN = "jazan"  # جازان
    TABUK = "tabuk"  # تبوك
    JOUF = "jouf"  # الجوف
    MADINAH = "madinah"  # المدينة
    MAKKAH = "makkah"  # مكة
    BAHA = "baha"  # الباحة
    NORTHERN = "northern"  # الحدود الشمالية

    # Yemen regions
    SANA = "sana"  # صنعاء
    TAIZ = "taiz"  # تعز
    ADEN = "aden"  # عدن
    HADRAMAUT = "hadramaut"  # حضرموت
    IBBI = "ibb"  # إب
    DHAMAR = "dhamar"  # ذمار
    HODEIDAH = "hodeidah"  # الحديدة
    MARIB = "marib"  # مأرب
    SHABWA = "shabwa"  # شبوة
    LAHIJ = "lahij"  # لحج


class ClimateZone(StrEnum):
    """Climate zones for agricultural planning"""

    ARID_HOT = "arid_hot"  # جاف حار (Central/Eastern Saudi)
    ARID_MILD = "arid_mild"  # جاف معتدل (Northern Saudi)
    SEMI_ARID = "semi_arid"  # شبه جاف
    SUBTROPICAL = "subtropical"  # شبه استوائي (Jazan, Yemen coastal)
    HIGHLAND = "highland"  # مرتفعات (Asir, Yemen highlands)
    COASTAL = "coastal"  # ساحلي (Red Sea, Gulf coasts)


class AgriculturalSeason(StrEnum):
    """Agricultural seasons in the Middle East"""

    WINTER = "winter"  # الشتاء (Dec-Feb)
    SPRING = "spring"  # الربيع (Mar-May)
    SUMMER = "summer"  # الصيف (Jun-Aug)
    AUTUMN = "autumn"  # الخريف (Sep-Nov)

    # Traditional Arabic seasons based on Anwa'a
    SAIF = "saif"  # الصيف - Hot summer (Jun 21 - Sep 22)
    KHARIF = "kharif"  # الخريف - Autumn (Sep 23 - Dec 21)
    SHITA = "shita"  # الشتاء - Winter (Dec 22 - Mar 20)
    RABI = "rabi"  # الربيع - Spring (Mar 21 - Jun 20)


class TraditionalSeason(StrEnum):
    """
    Traditional Arab seasons based on Anwa'a (الأنواء)
    Each Naw'a lasts approximately 13 days
    """

    # Summer Anwa'a (الصيف)
    THURAYA = "thuraya"  # الثريا (Jun 7)
    DABARAN = "dabaran"  # الدبران (Jun 20)
    HAQAA = "haqaa"  # الهقعة (Jul 3)
    HANAA = "hanaa"  # الهنعة (Jul 16)
    DHIRAA = "dhiraa"  # الذراع (Jul 29)
    NATHRA = "nathra"  # النثرة (Aug 11)
    TARF = "tarf"  # الطرف (Aug 24)

    # Autumn Anwa'a (الخريف)
    JABHA = "jabha"  # الجبهة (Sep 6)
    ZUBRA = "zubra"  # الزبرة (Sep 19)
    SARFA = "sarfa"  # الصرفة (Oct 2)
    AWWA = "awwa"  # العواء (Oct 15)
    SIMAK = "simak"  # السماك (Oct 28)
    GHAFR = "ghafr"  # الغفر (Nov 10)
    ZUBANA = "zubana"  # الزبانا (Nov 23)

    # Winter Anwa'a (الشتاء)
    IKLIL = "iklil"  # الإكليل (Dec 6)
    QALB = "qalb"  # القلب (Dec 19)
    SHAULA = "shaula"  # الشولة (Jan 1)
    NAAYIM = "naayim"  # النعايم (Jan 14)
    BALDA = "balda"  # البلدة (Jan 27)
    SAAD_DHABIH = "saad_dhabih"  # سعد الذابح (Feb 9)
    SAAD_BULAA = "saad_bulaa"  # سعد بلع (Feb 22)

    # Spring Anwa'a (الربيع)
    SAAD_SUUD = "saad_suud"  # سعد السعود (Mar 7)
    SAAD_AKHBIYA = "saad_akhbiya"  # سعد الأخبية (Mar 20)
    MUQADDAM = "muqaddam"  # المقدم (Apr 2)
    MUAKHKHAR = "muakhkhar"  # المؤخر (Apr 15)
    RISHA = "risha"  # الرشا (Apr 28)
    SHARATAIN = "sharatain"  # الشرطين (May 11)
    BUTAIN = "butain"  # البطين (May 24)


class HijriMonth(StrEnum):
    """Islamic (Hijri) calendar months"""

    MUHARRAM = "muharram"  # محرم
    SAFAR = "safar"  # صفر
    RABI_AL_AWWAL = "rabi_al_awwal"  # ربيع الأول
    RABI_AL_THANI = "rabi_al_thani"  # ربيع الثاني
    JUMADA_AL_AWWAL = "jumada_al_awwal"  # جمادى الأولى
    JUMADA_AL_THANI = "jumada_al_thani"  # جمادى الثانية
    RAJAB = "rajab"  # رجب
    SHABAN = "shaban"  # شعبان
    RAMADAN = "ramadan"  # رمضان
    SHAWWAL = "shawwal"  # شوال
    DHU_AL_QIDAH = "dhu_al_qidah"  # ذو القعدة
    DHU_AL_HIJJAH = "dhu_al_hijjah"  # ذو الحجة


class CropType(StrEnum):
    """Common crops in Saudi Arabia and Yemen"""

    # Cereals - الحبوب
    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    SORGHUM = "sorghum"  # ذرة رفيعة
    MILLET = "millet"  # دخن
    MAIZE = "maize"  # ذرة
    RICE = "rice"  # أرز

    # Legumes - البقوليات
    ALFALFA = "alfalfa"  # برسيم
    FABA_BEAN = "faba_bean"  # فول
    CHICKPEA = "chickpea"  # حمص
    LENTIL = "lentil"  # عدس
    COWPEA = "cowpea"  # لوبيا

    # Vegetables - الخضروات
    TOMATO = "tomato"  # طماطم
    POTATO = "potato"  # بطاطس
    ONION = "onion"  # بصل
    GARLIC = "garlic"  # ثوم
    CUCUMBER = "cucumber"  # خيار
    EGGPLANT = "eggplant"  # باذنجان
    PEPPER = "pepper"  # فلفل
    SQUASH = "squash"  # كوسة
    WATERMELON = "watermelon"  # بطيخ
    MELON = "melon"  # شمام
    OKRA = "okra"  # بامية
    CARROT = "carrot"  # جزر
    CABBAGE = "cabbage"  # ملفوف
    LETTUCE = "lettuce"  # خس

    # Fruits - الفواكه
    DATE_PALM = "date_palm"  # نخيل
    GRAPE = "grape"  # عنب
    CITRUS = "citrus"  # حمضيات
    MANGO = "mango"  # مانجو
    PAPAYA = "papaya"  # بابايا
    BANANA = "banana"  # موز
    POMEGRANATE = "pomegranate"  # رمان
    FIG = "fig"  # تين
    OLIVE = "olive"  # زيتون

    # Industrial/Cash crops - المحاصيل النقدية
    COFFEE = "coffee"  # قهوة (Yemen specialty)
    QAT = "qat"  # قات (Yemen)
    COTTON = "cotton"  # قطن
    SESAME = "sesame"  # سمسم

    # Fodder - الأعلاف
    RHODES_GRASS = "rhodes_grass"  # حشيشة رودس
    SUDAN_GRASS = "sudan_grass"  # حشيشة السودان


class PlantingEventType(StrEnum):
    """Types of agricultural calendar events"""

    PLANTING_START = "planting_start"  # بداية الزراعة
    PLANTING_END = "planting_end"  # نهاية الزراعة
    TRANSPLANTING = "transplanting"  # الشتل
    HARVEST_START = "harvest_start"  # بداية الحصاد
    HARVEST_END = "harvest_end"  # نهاية الحصاد
    POLLINATION = "pollination"  # التلقيح (for date palm)
    PRUNING = "pruning"  # التقليم
    FERTILIZATION = "fertilization"  # التسميد
    IRRIGATION_START = "irrigation_start"  # بداية الري
    PEST_CONTROL = "pest_control"  # مكافحة الآفات
    FRUIT_THINNING = "fruit_thinning"  # خف الثمار
    WEEDING = "weeding"  # إزالة الأعشاب


class EventPriority(StrEnum):
    """Priority level for calendar events"""

    CRITICAL = "critical"  # حرج - Must not miss
    HIGH = "high"  # عالي
    MEDIUM = "medium"  # متوسط
    LOW = "low"  # منخفض
    INFORMATIONAL = "informational"  # معلوماتي


class RecommendationConfidence(StrEnum):
    """Confidence level for recommendations"""

    HIGH = "high"  # عالية (>85%)
    MEDIUM = "medium"  # متوسطة (60-85%)
    LOW = "low"  # منخفضة (<60%)


# =============================================================================
# Islamic Calendar Models - نماذج التقويم الهجري
# =============================================================================


@dataclass
class HijriDate:
    """
    Hijri (Islamic) calendar date
    تاريخ هجري
    """

    year: int  # السنة الهجرية
    month: int  # الشهر (1-12)
    day: int  # اليوم (1-30)

    # Month name
    month_name: HijriMonth | None = None
    month_name_ar: str = ""
    month_name_en: str = ""

    # Day of week
    day_of_week: int = 0  # 0=Saturday, 6=Friday
    day_name_ar: str = ""  # السبت, الأحد, etc.
    day_name_en: str = ""  # Saturday, Sunday, etc.

    # Corresponding Gregorian
    gregorian_date: date | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "month_name": self.month_name.value if self.month_name else None,
            "month_name_ar": self.month_name_ar,
            "month_name_en": self.month_name_en,
            "day_of_week": self.day_of_week,
            "day_name_ar": self.day_name_ar,
            "day_name_en": self.day_name_en,
            "gregorian_date": self.gregorian_date.isoformat() if self.gregorian_date else None,
            "formatted_ar": f"{self.day} {self.month_name_ar} {self.year} هـ",
            "formatted_en": f"{self.day} {self.month_name_en} {self.year} AH",
        }

    def __str__(self) -> str:
        return f"{self.day}/{self.month}/{self.year} AH"


@dataclass
class IslamicEvent:
    """
    Islamic calendar event relevant to agriculture
    حدث في التقويم الإسلامي ذو صلة بالزراعة
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Event info
    name_en: str = ""
    name_ar: str = ""
    description_en: str = ""
    description_ar: str = ""

    # Date (Hijri)
    hijri_month: HijriMonth | None = None
    hijri_day: int | None = None  # None if varies (e.g., Ramadan start)

    # Agricultural relevance
    agricultural_significance_en: str = ""
    agricultural_significance_ar: str = ""

    # Market impact (e.g., demand changes during Ramadan)
    affects_market: bool = False
    market_impact_en: str = ""
    market_impact_ar: str = ""

    # Labor availability impact
    affects_labor: bool = False
    labor_impact_en: str = ""
    labor_impact_ar: str = ""

    # Duration in days
    duration_days: int = 1

    # Recurring annually
    is_annual: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "name_en": self.name_en,
            "name_ar": self.name_ar,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "hijri_month": self.hijri_month.value if self.hijri_month else None,
            "hijri_day": self.hijri_day,
            "agricultural_significance_en": self.agricultural_significance_en,
            "agricultural_significance_ar": self.agricultural_significance_ar,
            "affects_market": self.affects_market,
            "market_impact_en": self.market_impact_en,
            "affects_labor": self.affects_labor,
            "duration_days": self.duration_days,
        }


# =============================================================================
# Traditional Calendar Models - نماذج التقويم التقليدي
# =============================================================================


@dataclass
class TraditionalSeasonInfo:
    """
    Traditional Arabic agricultural season (Naw'a - نوء)
    معلومات الموسم الزراعي التقليدي
    """

    season: TraditionalSeason

    # Names
    name_ar: str = ""
    name_en: str = ""

    # Timing (approximate Gregorian dates)
    start_date_approx: date | None = None
    end_date_approx: date | None = None
    duration_days: int = 13  # Traditional naw'a duration

    # Star/constellation associated
    star_name_ar: str = ""
    star_name_en: str = ""

    # Weather characteristics
    weather_description_ar: str = ""
    weather_description_en: str = ""
    typical_temp_min_c: float = 0.0
    typical_temp_max_c: float = 0.0

    # Agricultural guidance
    agricultural_activities_ar: list[str] = field(default_factory=list)
    agricultural_activities_en: list[str] = field(default_factory=list)

    # Recommended crops
    recommended_crops: list[CropType] = field(default_factory=list)

    # Traditional sayings/proverbs
    proverb_ar: str = ""
    proverb_en: str = ""  # Translation/explanation

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "season": self.season.value,
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "start_date_approx": self.start_date_approx.isoformat() if self.start_date_approx else None,
            "end_date_approx": self.end_date_approx.isoformat() if self.end_date_approx else None,
            "duration_days": self.duration_days,
            "star_name_ar": self.star_name_ar,
            "star_name_en": self.star_name_en,
            "weather_description_ar": self.weather_description_ar,
            "weather_description_en": self.weather_description_en,
            "typical_temp_range": {
                "min_c": self.typical_temp_min_c,
                "max_c": self.typical_temp_max_c,
            },
            "agricultural_activities_ar": self.agricultural_activities_ar,
            "agricultural_activities_en": self.agricultural_activities_en,
            "recommended_crops": [c.value for c in self.recommended_crops],
            "proverb_ar": self.proverb_ar,
            "proverb_en": self.proverb_en,
        }


# =============================================================================
# Season Models - نماذج المواسم
# =============================================================================


@dataclass
class SeasonDefinition:
    """
    Agricultural season definition for a specific region
    تعريف الموسم الزراعي لمنطقة محددة
    """

    # Required fields (no defaults) - must come first
    season: AgriculturalSeason
    region: Region
    climate_zone: ClimateZone

    # Optional fields with defaults
    season_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Names
    name_ar: str = ""
    name_en: str = ""

    # Date range (Gregorian)
    start_month: int = 1  # 1-12
    start_day: int = 1
    end_month: int = 12
    end_day: int = 31

    # Climate characteristics
    avg_temp_min_c: float = 0.0
    avg_temp_max_c: float = 0.0
    avg_rainfall_mm: float = 0.0
    avg_humidity_percent: float = 0.0
    daylight_hours: float = 12.0

    # Growing conditions
    frost_risk: bool = False
    frost_risk_level: str = "none"  # none, low, medium, high
    heat_stress_risk: bool = False
    heat_stress_level: str = "none"

    # Water availability
    irrigation_critical: bool = False
    water_stress_level: str = "low"  # low, moderate, high, severe

    # Description
    description_ar: str = ""
    description_en: str = ""

    # Agricultural notes
    agricultural_notes_ar: str = ""
    agricultural_notes_en: str = ""

    def get_date_range(self, year: int) -> tuple[date, date]:
        """Get the date range for this season in a specific year"""
        start = date(year, self.start_month, self.start_day)

        # Handle seasons that span year boundaries
        end_year = year if self.end_month >= self.start_month else year + 1
        end = date(end_year, self.end_month, self.end_day)

        return start, end

    def is_date_in_season(self, check_date: date) -> bool:
        """Check if a date falls within this season"""
        start, end = self.get_date_range(check_date.year)

        # Handle year boundary
        if start > end:
            return check_date >= start or check_date <= end
        return start <= check_date <= end

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "season_id": self.season_id,
            "season": self.season.value,
            "region": self.region.value,
            "climate_zone": self.climate_zone.value,
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "date_range": {
                "start_month": self.start_month,
                "start_day": self.start_day,
                "end_month": self.end_month,
                "end_day": self.end_day,
            },
            "climate": {
                "avg_temp_min_c": self.avg_temp_min_c,
                "avg_temp_max_c": self.avg_temp_max_c,
                "avg_rainfall_mm": self.avg_rainfall_mm,
                "avg_humidity_percent": self.avg_humidity_percent,
                "daylight_hours": self.daylight_hours,
            },
            "risks": {
                "frost_risk": self.frost_risk,
                "frost_risk_level": self.frost_risk_level,
                "heat_stress_risk": self.heat_stress_risk,
                "heat_stress_level": self.heat_stress_level,
                "water_stress_level": self.water_stress_level,
            },
            "description_ar": self.description_ar,
            "description_en": self.description_en,
        }


# =============================================================================
# Planting/Event Models - نماذج الزراعة والأحداث
# =============================================================================


@dataclass
class PlantingWindow:
    """
    Optimal planting window for a crop in a region
    نافذة الزراعة المثلى لمحصول في منطقة
    """

    # Required fields (no defaults) - must come first
    crop_type: CropType
    region: Region

    # Optional fields with defaults
    window_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    crop_variety: str | None = None
    climate_zone: ClimateZone | None = None

    # Planting window
    optimal_start_month: int = 1
    optimal_start_day: int = 1
    optimal_end_month: int = 12
    optimal_end_day: int = 31

    # Extended window (acceptable but not optimal)
    extended_start_month: int | None = None
    extended_start_day: int | None = None
    extended_end_month: int | None = None
    extended_end_day: int | None = None

    # Days to maturity
    days_to_germination: int = 7
    days_to_maturity_min: int = 60
    days_to_maturity_max: int = 120

    # Expected harvest window
    harvest_start_month: int | None = None
    harvest_end_month: int | None = None

    # Growing conditions
    min_soil_temp_c: float = 10.0
    optimal_soil_temp_c: float = 20.0
    max_soil_temp_c: float = 35.0

    # Water requirements
    water_requirement_mm_season: float = 400.0
    irrigation_frequency_days: int = 7

    # Yield expectations
    expected_yield_tons_ha_min: float = 0.0
    expected_yield_tons_ha_max: float = 0.0
    expected_yield_tons_ha_avg: float = 0.0

    # Traditional timing (Naw'a based)
    traditional_season: TraditionalSeason | None = None
    traditional_guidance_ar: str = ""
    traditional_guidance_en: str = ""

    # Confidence
    confidence: RecommendationConfidence = RecommendationConfidence.MEDIUM

    # Notes
    notes_ar: str = ""
    notes_en: str = ""

    def get_optimal_window(self, year: int) -> tuple[date, date]:
        """Get optimal planting dates for a specific year"""
        start = date(year, self.optimal_start_month, self.optimal_start_day)

        end_year = year if self.optimal_end_month >= self.optimal_start_month else year + 1
        end = date(end_year, self.optimal_end_month, self.optimal_end_day)

        return start, end

    def is_date_optimal(self, plant_date: date) -> bool:
        """Check if a planting date is within optimal window"""
        start, end = self.get_optimal_window(plant_date.year)
        return start <= plant_date <= end

    def calculate_harvest_date(self, plant_date: date) -> tuple[date, date]:
        """Calculate expected harvest date range from planting date"""
        harvest_start = plant_date + timedelta(days=self.days_to_maturity_min)
        harvest_end = plant_date + timedelta(days=self.days_to_maturity_max)
        return harvest_start, harvest_end

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "window_id": self.window_id,
            "crop_type": self.crop_type.value,
            "crop_variety": self.crop_variety,
            "region": self.region.value,
            "climate_zone": self.climate_zone.value if self.climate_zone else None,
            "optimal_window": {
                "start_month": self.optimal_start_month,
                "start_day": self.optimal_start_day,
                "end_month": self.optimal_end_month,
                "end_day": self.optimal_end_day,
            },
            "extended_window": {
                "start_month": self.extended_start_month,
                "start_day": self.extended_start_day,
                "end_month": self.extended_end_month,
                "end_day": self.extended_end_day,
            }
            if self.extended_start_month
            else None,
            "maturity": {
                "days_to_germination": self.days_to_germination,
                "days_to_maturity_min": self.days_to_maturity_min,
                "days_to_maturity_max": self.days_to_maturity_max,
            },
            "soil_temp": {
                "min_c": self.min_soil_temp_c,
                "optimal_c": self.optimal_soil_temp_c,
                "max_c": self.max_soil_temp_c,
            },
            "water_requirement_mm_season": self.water_requirement_mm_season,
            "expected_yield_tons_ha": {
                "min": self.expected_yield_tons_ha_min,
                "max": self.expected_yield_tons_ha_max,
                "avg": self.expected_yield_tons_ha_avg,
            },
            "traditional_season": self.traditional_season.value if self.traditional_season else None,
            "traditional_guidance_ar": self.traditional_guidance_ar,
            "confidence": self.confidence.value,
            "notes_ar": self.notes_ar,
            "notes_en": self.notes_en,
        }


@dataclass
class CalendarEvent:
    """
    Agricultural calendar event
    حدث في التقويم الزراعي
    """

    # Required fields (no defaults) - must come first
    event_type: PlantingEventType

    # Optional fields with defaults
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    crop_type: CropType | None = None
    field_id: str | None = None

    # Region
    region: Region | None = None

    # Title and description
    title_en: str = ""
    title_ar: str = ""
    description_en: str = ""
    description_ar: str = ""

    # Date/Time
    date_gregorian: date | None = None
    date_hijri: HijriDate | None = None
    start_time: str | None = None  # HH:MM format
    end_time: str | None = None
    all_day: bool = True

    # Duration
    duration_days: int = 1

    # Date range (for events spanning multiple days)
    end_date_gregorian: date | None = None

    # Priority
    priority: EventPriority = EventPriority.MEDIUM

    # Traditional calendar
    traditional_season: TraditionalSeason | None = None
    traditional_note_ar: str = ""
    traditional_note_en: str = ""

    # Actions/Recommendations
    recommended_actions_en: list[str] = field(default_factory=list)
    recommended_actions_ar: list[str] = field(default_factory=list)

    # Reminders
    reminder_days_before: list[int] = field(default_factory=lambda: [7, 3, 1])

    # Recurring
    is_recurring: bool = False
    recurrence_pattern: str | None = None  # annual, monthly, etc.

    # Status
    is_completed: bool = False
    completed_at: datetime | None = None

    # Weather considerations
    weather_dependent: bool = False
    weather_conditions_required_en: str = ""
    weather_conditions_required_ar: str = ""

    # Notes
    notes: str = ""
    notes_ar: str = ""

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""

    def get_priority_icon(self) -> str:
        """Get priority icon for display"""
        icons = {
            EventPriority.CRITICAL: "[!!!]",
            EventPriority.HIGH: "[!!]",
            EventPriority.MEDIUM: "[!]",
            EventPriority.LOW: "[.]",
            EventPriority.INFORMATIONAL: "[i]",
        }
        return icons.get(self.priority, "[.]")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "crop_type": self.crop_type.value if self.crop_type else None,
            "field_id": self.field_id,
            "region": self.region.value if self.region else None,
            "title_en": self.title_en,
            "title_ar": self.title_ar,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "date_gregorian": self.date_gregorian.isoformat() if self.date_gregorian else None,
            "date_hijri": self.date_hijri.to_dict() if self.date_hijri else None,
            "end_date_gregorian": self.end_date_gregorian.isoformat() if self.end_date_gregorian else None,
            "duration_days": self.duration_days,
            "priority": self.priority.value,
            "priority_icon": self.get_priority_icon(),
            "traditional_season": self.traditional_season.value if self.traditional_season else None,
            "recommended_actions_en": self.recommended_actions_en,
            "recommended_actions_ar": self.recommended_actions_ar,
            "reminder_days_before": self.reminder_days_before,
            "is_recurring": self.is_recurring,
            "is_completed": self.is_completed,
            "weather_dependent": self.weather_dependent,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Recommendation Models - نماذج التوصيات
# =============================================================================


@dataclass
class PlantingRecommendation:
    """
    Planting date recommendation for a specific crop and location
    توصية بتاريخ الزراعة لمحصول ومكان محدد
    """

    # Required fields (no defaults) - must come first
    crop_type: CropType

    # Optional fields with defaults
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    field_id: str | None = None
    region: Region | None = None
    crop_variety: str | None = None
    crop_name_ar: str = ""

    # Recommended dates
    recommended_planting_start: date | None = None
    recommended_planting_end: date | None = None
    recommended_planting_optimal: date | None = None  # Best single date

    # Expected harvest
    expected_harvest_start: date | None = None
    expected_harvest_end: date | None = None

    # Alternative windows
    alternative_windows: list[dict[str, Any]] = field(default_factory=list)

    # Confidence
    confidence: RecommendationConfidence = RecommendationConfidence.MEDIUM
    confidence_score: float = 0.75  # 0-1

    # Reasoning
    reasoning_en: str = ""
    reasoning_ar: str = ""

    # Factors considered
    factors_en: list[str] = field(default_factory=list)
    factors_ar: list[str] = field(default_factory=list)

    # Traditional guidance
    traditional_season: TraditionalSeason | None = None
    traditional_guidance_ar: str = ""
    traditional_guidance_en: str = ""

    # Hijri date equivalents
    planting_start_hijri: HijriDate | None = None
    planting_end_hijri: HijriDate | None = None

    # Weather-based adjustments
    weather_adjusted: bool = False
    weather_adjustment_reason_en: str = ""
    weather_adjustment_reason_ar: str = ""

    # Expected outcomes
    expected_yield_tons_ha: float | None = None
    expected_growing_days: int | None = None

    # Warnings
    warnings_en: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    # Tips
    tips_en: list[str] = field(default_factory=list)
    tips_ar: list[str] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    model_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "recommendation_id": self.recommendation_id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "region": self.region.value if self.region else None,
            "crop_type": self.crop_type.value,
            "crop_variety": self.crop_variety,
            "crop_name_ar": self.crop_name_ar,
            "recommended_planting": {
                "start": self.recommended_planting_start.isoformat() if self.recommended_planting_start else None,
                "end": self.recommended_planting_end.isoformat() if self.recommended_planting_end else None,
                "optimal": self.recommended_planting_optimal.isoformat() if self.recommended_planting_optimal else None,
            },
            "expected_harvest": {
                "start": self.expected_harvest_start.isoformat() if self.expected_harvest_start else None,
                "end": self.expected_harvest_end.isoformat() if self.expected_harvest_end else None,
            },
            "alternative_windows": self.alternative_windows,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "reasoning_en": self.reasoning_en,
            "reasoning_ar": self.reasoning_ar,
            "factors_en": self.factors_en,
            "factors_ar": self.factors_ar,
            "traditional_season": self.traditional_season.value if self.traditional_season else None,
            "traditional_guidance_ar": self.traditional_guidance_ar,
            "planting_start_hijri": self.planting_start_hijri.to_dict() if self.planting_start_hijri else None,
            "planting_end_hijri": self.planting_end_hijri.to_dict() if self.planting_end_hijri else None,
            "weather_adjusted": self.weather_adjusted,
            "expected_yield_tons_ha": self.expected_yield_tons_ha,
            "expected_growing_days": self.expected_growing_days,
            "warnings_en": self.warnings_en,
            "warnings_ar": self.warnings_ar,
            "tips_en": self.tips_en,
            "tips_ar": self.tips_ar,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class SeasonalCalendar:
    """
    Complete seasonal agricultural calendar for a region
    التقويم الزراعي الموسمي الكامل لمنطقة
    """

    # Required fields (no defaults) - must come first
    region: Region

    # Optional fields with defaults
    calendar_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    region_name_ar: str = ""
    region_name_en: str = ""
    climate_zone: ClimateZone | None = None

    # Time period
    year: int = 2026

    # Season definitions
    seasons: list[SeasonDefinition] = field(default_factory=list)

    # Current season
    current_season: AgriculturalSeason | None = None
    current_traditional_season: TraditionalSeason | None = None

    # Planting windows by crop
    planting_windows: list[PlantingWindow] = field(default_factory=list)

    # Upcoming events
    upcoming_events: list[CalendarEvent] = field(default_factory=list)

    # Islamic calendar events affecting agriculture
    islamic_events: list[IslamicEvent] = field(default_factory=list)

    # Traditional season info
    traditional_seasons: list[TraditionalSeasonInfo] = field(default_factory=list)

    # Active crops by month
    active_crops_by_month: dict[int, list[CropType]] = field(default_factory=dict)

    # Key dates
    key_dates: list[dict[str, Any]] = field(default_factory=list)

    # Summary
    summary_ar: str = ""
    summary_en: str = ""

    # Notes
    notes_ar: str = ""
    notes_en: str = ""

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get_current_season(self, check_date: date | None = None) -> SeasonDefinition | None:
        """Get the season for a specific date"""
        if check_date is None:
            check_date = date.today()

        for season in self.seasons:
            if season.is_date_in_season(check_date):
                return season
        return None

    def get_planting_windows_for_crop(self, crop_type: CropType) -> list[PlantingWindow]:
        """Get all planting windows for a specific crop"""
        return [w for w in self.planting_windows if w.crop_type == crop_type]

    def get_upcoming_events(self, days_ahead: int = 30) -> list[CalendarEvent]:
        """Get events within the next N days"""
        today = date.today()
        end_date = today + timedelta(days=days_ahead)

        return [e for e in self.upcoming_events if e.date_gregorian and today <= e.date_gregorian <= end_date]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "calendar_id": self.calendar_id,
            "region": self.region.value,
            "region_name_ar": self.region_name_ar,
            "region_name_en": self.region_name_en,
            "climate_zone": self.climate_zone.value if self.climate_zone else None,
            "year": self.year,
            "seasons": [s.to_dict() for s in self.seasons],
            "current_season": self.current_season.value if self.current_season else None,
            "current_traditional_season": self.current_traditional_season.value
            if self.current_traditional_season
            else None,
            "planting_windows": [w.to_dict() for w in self.planting_windows],
            "upcoming_events": [e.to_dict() for e in self.upcoming_events],
            "islamic_events": [e.to_dict() for e in self.islamic_events],
            "traditional_seasons": [t.to_dict() for t in self.traditional_seasons],
            "active_crops_by_month": {k: [c.value for c in v] for k, v in self.active_crops_by_month.items()},
            "key_dates": self.key_dates,
            "summary_ar": self.summary_ar,
            "summary_en": self.summary_en,
            "generated_at": self.generated_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


# =============================================================================
# Region Metadata - بيانات المنطقة
# =============================================================================


@dataclass
class RegionMetadata:
    """
    Metadata for an agricultural region
    بيانات وصفية لمنطقة زراعية
    """

    region: Region

    # Names
    name_ar: str = ""
    name_en: str = ""

    # Geography
    country: str = "Saudi Arabia"  # or "Yemen"
    latitude: float = 0.0
    longitude: float = 0.0
    altitude_m: float = 0.0

    # Climate
    climate_zone: ClimateZone = ClimateZone.ARID_HOT
    avg_annual_rainfall_mm: float = 100.0
    avg_annual_temp_c: float = 28.0

    # Water resources
    groundwater_available: bool = True
    surface_water_available: bool = False
    desalinated_water_available: bool = False

    # Primary crops
    primary_crops: list[CropType] = field(default_factory=list)

    # Traditional farming
    traditional_farming_practices_ar: list[str] = field(default_factory=list)
    traditional_farming_practices_en: list[str] = field(default_factory=list)

    # Notes
    notes_ar: str = ""
    notes_en: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "region": self.region.value,
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "country": self.country,
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude_m": self.altitude_m,
            },
            "climate": {
                "zone": self.climate_zone.value,
                "avg_annual_rainfall_mm": self.avg_annual_rainfall_mm,
                "avg_annual_temp_c": self.avg_annual_temp_c,
            },
            "water_resources": {
                "groundwater": self.groundwater_available,
                "surface_water": self.surface_water_available,
                "desalinated_water": self.desalinated_water_available,
            },
            "primary_crops": [c.value for c in self.primary_crops],
            "traditional_farming_practices_ar": self.traditional_farming_practices_ar,
            "traditional_farming_practices_en": self.traditional_farming_practices_en,
        }
