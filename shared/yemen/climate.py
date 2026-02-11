"""
Yemen climate zone data for SAHOOL platform.

Provides ET0 ranges, temperature profiles, rainfall patterns, and
groundwater data for Yemen's major agro-ecological zones.

Sources:
- FAO Yemen AQUASTAT
- MDPI Agricultural Water Deficit Yemen (2023)
- Yemen Meteorological Authority historical data
- UNDP climate risk assessments
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class YemenClimateZone(str, Enum):
    """Major agro-ecological zones of Yemen."""

    TIHAMA = "tihama"  # Coastal plain (Red Sea)
    HIGHLANDS = "highlands"  # Central highlands (Sana'a, Ibb)
    NORTHERN_HIGHLANDS = "northern_highlands"  # Sa'dah, Amran
    EASTERN_PLATEAU = "eastern_plateau"  # Marib, Al-Jawf
    HADHRAMAUT = "hadhramaut"  # Wadi Hadhramaut
    SOUTHERN_COAST = "southern_coast"  # Aden, Lahj
    SOCOTRA = "socotra"  # Socotra Island


@dataclass
class MonthlyClimate:
    """Monthly climate data."""

    month: int  # 1-12
    temp_min_c: float
    temp_max_c: float
    rainfall_mm: float
    et0_mm_day: float  # Reference ET (Penman-Monteith)
    humidity_pct: float
    wind_speed_ms: float  # m/s at 2m height
    solar_radiation_mjm2: float  # MJ/m²/day


@dataclass
class YemenClimateData:
    """Complete climate data for a Yemen zone."""

    zone: YemenClimateZone
    name: str
    name_ar: str
    elevation_m: tuple[int, int]  # min, max elevation
    annual_rainfall_mm: tuple[float, float]  # min, max range
    et0_range_mm_day: tuple[float, float]  # min, max daily ET0
    groundwater_decline_m_year: float  # Annual decline rate
    ec_groundwater_dsm: tuple[float, float]  # EC range of groundwater
    major_crops: list[str] = field(default_factory=list)
    monthly_data: list[MonthlyClimate] = field(default_factory=list)
    notes: str = ""
    notes_ar: str = ""


# Yemen Climate Zone Database
YEMEN_CLIMATE_ZONES: dict[str, YemenClimateData] = {
    "tihama": YemenClimateData(
        zone=YemenClimateZone.TIHAMA,
        name="Tihama Coastal Plain",
        name_ar="سهل تهامة الساحلي",
        elevation_m=(0, 500),
        annual_rainfall_mm=(50, 200),
        et0_range_mm_day=(5.0, 8.0),
        groundwater_decline_m_year=1.5,
        ec_groundwater_dsm=(1.5, 8.0),
        major_crops=["sorghum", "millet", "date_palm", "mango", "banana", "cotton", "sesame"],
        monthly_data=[
            MonthlyClimate(1, 18, 30, 5, 5.0, 70, 2.5, 16.0),
            MonthlyClimate(2, 19, 31, 3, 5.5, 68, 2.5, 18.0),
            MonthlyClimate(3, 21, 33, 8, 6.2, 65, 2.8, 20.5),
            MonthlyClimate(4, 23, 36, 10, 7.0, 60, 3.0, 22.0),
            MonthlyClimate(5, 26, 39, 5, 7.5, 55, 3.2, 23.0),
            MonthlyClimate(6, 28, 40, 2, 8.0, 50, 3.5, 24.0),
            MonthlyClimate(7, 28, 39, 15, 7.5, 55, 3.5, 22.5),
            MonthlyClimate(8, 27, 38, 20, 7.0, 60, 3.0, 21.0),
            MonthlyClimate(9, 26, 37, 15, 6.8, 62, 2.8, 20.0),
            MonthlyClimate(10, 23, 35, 8, 6.5, 58, 2.5, 19.0),
            MonthlyClimate(11, 21, 32, 5, 5.5, 65, 2.5, 17.0),
            MonthlyClimate(12, 19, 30, 5, 5.0, 70, 2.5, 15.5),
        ],
        notes="Hottest zone. Severe salinity from seawater intrusion. Spate irrigation traditional.",
        notes_ar="أشد المناطق حرارة. ملوحة شديدة من تسرب مياه البحر. الري بالسيول تقليدي.",
    ),
    "highlands": YemenClimateData(
        zone=YemenClimateZone.HIGHLANDS,
        name="Central Highlands (Sana'a, Ibb, Taiz)",
        name_ar="المرتفعات الوسطى (صنعاء، إب، تعز)",
        elevation_m=(1500, 3000),
        annual_rainfall_mm=(200, 800),
        et0_range_mm_day=(3.5, 6.0),
        groundwater_decline_m_year=4.0,
        ec_groundwater_dsm=(0.5, 2.5),
        major_crops=[
            "wheat",
            "barley",
            "qat",
            "coffee_arabica",
            "grape",
            "alfalfa",
            "tomato",
            "onion",
        ],
        monthly_data=[
            MonthlyClimate(1, 3, 22, 5, 3.5, 45, 1.5, 16.0),
            MonthlyClimate(2, 4, 23, 8, 4.0, 42, 1.8, 18.0),
            MonthlyClimate(3, 7, 25, 25, 4.5, 40, 2.0, 20.0),
            MonthlyClimate(4, 10, 27, 40, 5.0, 38, 2.0, 22.0),
            MonthlyClimate(5, 12, 28, 20, 5.5, 35, 2.2, 23.5),
            MonthlyClimate(6, 13, 29, 5, 6.0, 30, 2.5, 24.0),
            MonthlyClimate(7, 13, 27, 60, 5.0, 50, 2.0, 21.0),
            MonthlyClimate(8, 13, 27, 70, 5.0, 55, 1.8, 20.5),
            MonthlyClimate(9, 11, 27, 25, 5.0, 40, 1.8, 20.0),
            MonthlyClimate(10, 8, 25, 10, 4.5, 35, 1.5, 18.5),
            MonthlyClimate(11, 5, 23, 8, 3.8, 40, 1.5, 16.5),
            MonthlyClimate(12, 3, 22, 5, 3.5, 45, 1.5, 15.0),
        ],
        notes="Most productive zone. Severe groundwater depletion (2-6 m/year in Sana'a basin). "
        "Qat consumes 30% of Sana'a basin water.",
        notes_ar="أكثر المناطق إنتاجية. استنزاف شديد للمياه الجوفية (2-6 م/سنة في حوض صنعاء). "
        "القات يستهلك 30% من مياه حوض صنعاء.",
    ),
    "northern_highlands": YemenClimateData(
        zone=YemenClimateZone.NORTHERN_HIGHLANDS,
        name="Northern Highlands (Sa'dah, Amran)",
        name_ar="المرتفعات الشمالية (صعدة، عمران)",
        elevation_m=(1200, 2800),
        annual_rainfall_mm=(150, 400),
        et0_range_mm_day=(3.5, 5.5),
        groundwater_decline_m_year=3.0,
        ec_groundwater_dsm=(0.5, 2.0),
        major_crops=["wheat", "barley", "qat", "grape", "pomegranate", "alfalfa"],
        monthly_data=[
            MonthlyClimate(1, 2, 20, 5, 3.5, 40, 1.5, 15.5),
            MonthlyClimate(2, 3, 21, 8, 3.8, 38, 1.8, 17.5),
            MonthlyClimate(3, 6, 24, 25, 4.5, 35, 2.0, 19.5),
            MonthlyClimate(4, 9, 26, 30, 5.0, 33, 2.0, 21.5),
            MonthlyClimate(5, 11, 28, 15, 5.5, 30, 2.2, 23.0),
            MonthlyClimate(6, 13, 30, 3, 5.5, 28, 2.5, 24.0),
            MonthlyClimate(7, 13, 28, 45, 5.0, 45, 2.0, 21.0),
            MonthlyClimate(8, 13, 28, 55, 5.0, 50, 1.8, 20.0),
            MonthlyClimate(9, 10, 27, 20, 4.8, 38, 1.8, 19.5),
            MonthlyClimate(10, 7, 25, 8, 4.2, 33, 1.5, 18.0),
            MonthlyClimate(11, 4, 22, 5, 3.5, 38, 1.5, 16.0),
            MonthlyClimate(12, 2, 20, 3, 3.5, 42, 1.5, 15.0),
        ],
        notes="Conflict-affected area. Good groundwater quality but declining levels.",
        notes_ar="منطقة متأثرة بالنزاع. جودة مياه جوفية جيدة لكن المستويات في انخفاض.",
    ),
    "eastern_plateau": YemenClimateData(
        zone=YemenClimateZone.EASTERN_PLATEAU,
        name="Eastern Plateau (Marib, Al-Jawf)",
        name_ar="الهضبة الشرقية (مأرب، الجوف)",
        elevation_m=(600, 1500),
        annual_rainfall_mm=(50, 150),
        et0_range_mm_day=(5.0, 7.5),
        groundwater_decline_m_year=2.0,
        ec_groundwater_dsm=(1.0, 4.0),
        major_crops=["sorghum", "millet", "date_palm", "alfalfa", "cotton"],
        monthly_data=[
            MonthlyClimate(1, 8, 25, 3, 5.0, 40, 2.0, 16.5),
            MonthlyClimate(2, 9, 27, 5, 5.5, 38, 2.2, 18.5),
            MonthlyClimate(3, 12, 30, 10, 6.0, 35, 2.5, 20.5),
            MonthlyClimate(4, 16, 33, 15, 6.5, 30, 2.8, 22.0),
            MonthlyClimate(5, 20, 36, 8, 7.0, 25, 3.0, 23.5),
            MonthlyClimate(6, 22, 38, 2, 7.5, 22, 3.5, 24.0),
            MonthlyClimate(7, 22, 37, 15, 7.0, 30, 3.0, 22.5),
            MonthlyClimate(8, 22, 36, 20, 6.8, 35, 2.8, 21.5),
            MonthlyClimate(9, 19, 35, 8, 6.5, 30, 2.5, 20.5),
            MonthlyClimate(10, 15, 32, 5, 6.0, 28, 2.2, 19.0),
            MonthlyClimate(11, 11, 28, 3, 5.5, 35, 2.0, 17.0),
            MonthlyClimate(12, 9, 25, 3, 5.0, 40, 2.0, 15.5),
        ],
        notes="Semi-arid desert margin. Ancient Marib dam area. Spate irrigation.",
        notes_ar="هامش صحراوي شبه جاف. منطقة سد مأرب القديم. ري بالسيول.",
    ),
    "hadhramaut": YemenClimateData(
        zone=YemenClimateZone.HADHRAMAUT,
        name="Wadi Hadhramaut",
        name_ar="وادي حضرموت",
        elevation_m=(200, 800),
        annual_rainfall_mm=(30, 100),
        et0_range_mm_day=(5.0, 7.0),
        groundwater_decline_m_year=1.0,
        ec_groundwater_dsm=(1.0, 5.0),
        major_crops=["date_palm", "mango", "sesame", "alfalfa"],
        monthly_data=[
            MonthlyClimate(1, 12, 28, 3, 5.0, 45, 2.0, 16.5),
            MonthlyClimate(2, 14, 30, 3, 5.5, 42, 2.0, 18.5),
            MonthlyClimate(3, 17, 33, 5, 6.0, 38, 2.2, 20.5),
            MonthlyClimate(4, 20, 36, 8, 6.5, 35, 2.5, 22.0),
            MonthlyClimate(5, 23, 38, 5, 7.0, 30, 2.8, 23.0),
            MonthlyClimate(6, 25, 40, 1, 7.0, 28, 3.0, 24.0),
            MonthlyClimate(7, 25, 39, 5, 6.8, 35, 3.0, 22.5),
            MonthlyClimate(8, 25, 38, 5, 6.5, 38, 2.8, 21.5),
            MonthlyClimate(9, 23, 37, 5, 6.5, 35, 2.5, 20.5),
            MonthlyClimate(10, 19, 34, 3, 6.0, 32, 2.2, 19.0),
            MonthlyClimate(11, 15, 30, 3, 5.5, 40, 2.0, 17.0),
            MonthlyClimate(12, 13, 28, 2, 5.0, 45, 2.0, 15.5),
        ],
        notes="Major date palm region. UNDP SIERY drip trials: 40-60% water savings. "
        "5,456m pipes installed for 31 farms in Tarim.",
        notes_ar="منطقة رئيسية لزراعة النخيل. تجارب UNDP للتنقيط: 40-60% توفير مياه. "
        "5,456م أنابيب مُركبة لـ 31 مزرعة في تريم.",
    ),
    "southern_coast": YemenClimateData(
        zone=YemenClimateZone.SOUTHERN_COAST,
        name="Southern Coast (Aden, Lahj, Abyan)",
        name_ar="الساحل الجنوبي (عدن، لحج، أبين)",
        elevation_m=(0, 300),
        annual_rainfall_mm=(20, 80),
        et0_range_mm_day=(5.5, 7.5),
        groundwater_decline_m_year=2.0,
        ec_groundwater_dsm=(2.0, 10.0),
        major_crops=["date_palm", "cotton", "sorghum", "sesame", "tomato"],
        monthly_data=[
            MonthlyClimate(1, 20, 28, 2, 5.5, 65, 3.0, 16.5),
            MonthlyClimate(2, 20, 29, 2, 5.8, 63, 3.0, 18.5),
            MonthlyClimate(3, 22, 31, 5, 6.5, 60, 3.2, 20.5),
            MonthlyClimate(4, 24, 33, 5, 7.0, 55, 3.5, 22.0),
            MonthlyClimate(5, 26, 35, 3, 7.5, 50, 4.0, 23.0),
            MonthlyClimate(6, 27, 37, 1, 7.5, 48, 4.5, 23.5),
            MonthlyClimate(7, 27, 36, 3, 7.0, 55, 4.0, 22.0),
            MonthlyClimate(8, 27, 35, 3, 6.8, 58, 3.5, 21.5),
            MonthlyClimate(9, 26, 34, 3, 6.5, 55, 3.2, 20.5),
            MonthlyClimate(10, 23, 32, 3, 6.2, 52, 3.0, 19.0),
            MonthlyClimate(11, 21, 30, 3, 5.8, 60, 3.0, 17.0),
            MonthlyClimate(12, 20, 28, 2, 5.5, 65, 3.0, 15.5),
        ],
        notes="Severe seawater intrusion. Highest EC values in Yemen. Critical salinity management needed.",
        notes_ar="تسرب شديد لمياه البحر. أعلى قيم ملوحة في اليمن. إدارة ملوحة حرجة مطلوبة.",
    ),
}


def get_climate_zone(zone: str) -> YemenClimateData | None:
    """Get climate data by zone name (case-insensitive)."""
    return YEMEN_CLIMATE_ZONES.get(zone.lower())


def get_et0_range(zone: str) -> tuple[float, float] | None:
    """Get ET0 range for a climate zone."""
    data = get_climate_zone(zone)
    return data.et0_range_mm_day if data else None
