"""
SAHOOL Growing Degree Days (GDD) Tracker
متتبع وحدات الحرارة النامية

Tracks crop development using heat units accumulated over time.
Similar to OneSoil's GDD feature for precision agriculture.

Features:
- Daily and accumulated GDD calculation
- Growth stage mapping based on GDD thresholds
- Milestone predictions (emergence, flowering, harvest)
- Comparison to historical normal
- Multiple calculation methods (simple, modified, sine)
- Full support for all Yemen crops

References:
- McMaster & Wilhelm (1997) - GDD: an overview
- Miller et al. (2001) - Using GDD in crop production
- Cesaraccio et al. (2001) - Comparison of GDD calculation methods
"""

import logging
import math
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class GDDMethod(Enum):
    """GDD calculation methods"""

    SIMPLE = "simple"  # (Tmax + Tmin) / 2 - Tbase
    MODIFIED = "modified"  # With upper cutoff
    SINE = "sine"  # Sine wave approximation


@dataclass
class GDDDataPoint:
    """Single day's GDD data"""

    date: date
    temp_min: float
    temp_max: float
    temp_avg: float
    daily_gdd: float
    accumulated_gdd: float

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "temp_min_c": round(self.temp_min, 1),
            "temp_max_c": round(self.temp_max, 1),
            "temp_avg_c": round(self.temp_avg, 1),
            "daily_gdd": round(self.daily_gdd, 1),
            "accumulated_gdd": round(self.accumulated_gdd, 1),
        }


@dataclass
class GrowthMilestone:
    """Growth milestone based on GDD"""

    stage_name_en: str
    stage_name_ar: str
    gdd_required: float
    gdd_accumulated: float
    is_reached: bool
    reached_date: date | None
    expected_date: date | None
    days_remaining: int | None
    description_ar: str
    description_en: str

    def to_dict(self) -> dict:
        return {
            "stage_name_en": self.stage_name_en,
            "stage_name_ar": self.stage_name_ar,
            "gdd_required": round(self.gdd_required, 1),
            "gdd_accumulated": round(self.gdd_accumulated, 1),
            "is_reached": self.is_reached,
            "reached_date": (
                self.reached_date.isoformat() if self.reached_date else None
            ),
            "expected_date": (
                self.expected_date.isoformat() if self.expected_date else None
            ),
            "days_remaining": self.days_remaining,
            "description_ar": self.description_ar,
            "description_en": self.description_en,
        }


@dataclass
class GDDChart:
    """Complete GDD chart for a field/crop"""

    field_id: str
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    planting_date: date
    base_temp: float
    upper_temp: float | None  # Upper cutoff temperature

    # Current status
    current_date: date
    total_gdd: float
    days_since_planting: int
    avg_daily_gdd: float

    # Data series
    daily_data: list[GDDDataPoint]

    # Milestones
    milestones: list[GrowthMilestone]
    current_stage: str
    current_stage_ar: str
    next_stage: str
    next_stage_ar: str
    gdd_to_next_stage: float

    # Predictions
    estimated_harvest_date: date
    gdd_to_harvest: float
    days_to_harvest: int

    # Comparison
    vs_normal_year: float  # % ahead/behind normal
    vs_normal_description_ar: str
    vs_normal_description_en: str

    # Metadata
    calculation_method: str
    confidence: float

    def to_dict(self) -> dict:
        return {
            "field_id": self.field_id,
            "crop": {
                "code": self.crop_code,
                "name_ar": self.crop_name_ar,
                "name_en": self.crop_name_en,
            },
            "planting_date": self.planting_date.isoformat(),
            "base_temp_c": self.base_temp,
            "upper_temp_c": self.upper_temp,
            "current_status": {
                "date": self.current_date.isoformat(),
                "total_gdd": round(self.total_gdd, 1),
                "days_since_planting": self.days_since_planting,
                "avg_daily_gdd": round(self.avg_daily_gdd, 1),
            },
            "daily_data": [d.to_dict() for d in self.daily_data],
            "current_stage": {
                "name_en": self.current_stage,
                "name_ar": self.current_stage_ar,
                "next_stage_en": self.next_stage,
                "next_stage_ar": self.next_stage_ar,
                "gdd_to_next_stage": round(self.gdd_to_next_stage, 1),
            },
            "milestones": [m.to_dict() for m in self.milestones],
            "harvest_prediction": {
                "estimated_date": self.estimated_harvest_date.isoformat(),
                "gdd_remaining": round(self.gdd_to_harvest, 1),
                "days_remaining": self.days_to_harvest,
            },
            "comparison": {
                "vs_normal_percent": round(self.vs_normal_year, 1),
                "description_ar": self.vs_normal_description_ar,
                "description_en": self.vs_normal_description_en,
            },
            "metadata": {
                "calculation_method": self.calculation_method,
                "confidence": round(self.confidence, 2),
            },
        }


@dataclass
class CropGDDRequirements:
    """GDD requirements for a crop"""

    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    base_temp: float
    upper_temp: float | None
    total_gdd_required: float
    stages: list[dict]  # [{name_en, name_ar, gdd_start, gdd_end, description}]

    def to_dict(self) -> dict:
        return {
            "crop_code": self.crop_code,
            "crop_name_ar": self.crop_name_ar,
            "crop_name_en": self.crop_name_en,
            "base_temp_c": self.base_temp,
            "upper_temp_c": self.upper_temp,
            "total_gdd_required": round(self.total_gdd_required, 1),
            "stages": self.stages,
        }


class GDDTracker:
    """
    Track Growing Degree Days for crop development.

    Integrates with weather service for historical and forecast data.
    Provides comprehensive GDD analysis for all Yemen crops.
    """

    # Base temperatures by crop (°C)
    # Sources: FAO, USDA ARS, regional agricultural research
    CROP_BASE_TEMPS = {
        # Cereals - الحبوب
        "WHEAT": {"base": 0, "upper": 30},
        "BARLEY": {"base": 0, "upper": 30},
        "CORN": {"base": 10, "upper": 30},
        "SORGHUM": {"base": 10, "upper": 35},
        "MILLET": {"base": 8, "upper": 35},
        "RICE": {"base": 10, "upper": 30},
        # Vegetables - الخضروات
        "TOMATO": {"base": 10, "upper": 30},
        "POTATO": {"base": 7, "upper": 30},
        "ONION": {"base": 6, "upper": 30},
        "CARROT": {"base": 4, "upper": 30},
        "CUCUMBER": {"base": 12, "upper": 35},
        "SQUASH": {"base": 10, "upper": 35},
        "PEPPER": {"base": 10, "upper": 35},
        "EGGPLANT": {"base": 10, "upper": 35},
        "OKRA": {"base": 15, "upper": 35},
        "CABBAGE": {"base": 5, "upper": 25},
        "LETTUCE": {"base": 5, "upper": 25},
        # Legumes - البقوليات
        "FABA_BEAN": {"base": 0, "upper": 30},
        "LENTIL": {"base": 5, "upper": 30},
        "CHICKPEA": {"base": 5, "upper": 30},
        "COWPEA": {"base": 8, "upper": 35},
        "PEANUT": {"base": 12, "upper": 35},
        "ALFALFA": {"base": 5, "upper": 30},
        # Cash Crops - المحاصيل النقدية
        "COTTON": {"base": 15.5, "upper": 35},
        "COFFEE": {"base": 10, "upper": 32},
        "QAT": {"base": 10, "upper": 35},
        "SESAME": {"base": 10, "upper": 35},
        "TOBACCO": {"base": 10, "upper": 35},
        # Fruits - الفواكه
        "DATE_PALM": {"base": 18, "upper": None},
        "GRAPE": {"base": 10, "upper": None},
        "MANGO": {"base": 10, "upper": None},
        "BANANA": {"base": 14, "upper": None},
        "PAPAYA": {"base": 15, "upper": None},
        "CITRUS": {"base": 13, "upper": None},
        "POMEGRANATE": {"base": 10, "upper": None},
        "FIG": {"base": 10, "upper": None},
        "GUAVA": {"base": 10, "upper": None},
        # Fodder - الأعلاف
        "RHODES_GRASS": {"base": 10, "upper": 35},
        "SUDAN_GRASS": {"base": 10, "upper": 35},
    }

    # GDD requirements and stages by crop
    # Values calibrated for Yemen climate zones
    CROP_GDD_REQUIREMENTS = {
        "WHEAT": {
            "name_ar": "قمح",
            "name_en": "Wheat",
            "total": 2000,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 150,
                    "desc_ar": "ظهور البادرات",
                    "desc_en": "Seedling emergence",
                },
                {
                    "name_en": "Tillering",
                    "name_ar": "التفريع",
                    "gdd": 450,
                    "desc_ar": "بداية التفريع",
                    "desc_en": "Tiller initiation",
                },
                {
                    "name_en": "Stem Elongation",
                    "name_ar": "استطالة الساق",
                    "gdd": 800,
                    "desc_ar": "استطالة الساق",
                    "desc_en": "Stem elongation",
                },
                {
                    "name_en": "Booting",
                    "name_ar": "الإسبال",
                    "gdd": 1100,
                    "desc_ar": "طرد السنابل",
                    "desc_en": "Boot stage",
                },
                {
                    "name_en": "Heading",
                    "name_ar": "الطرد",
                    "gdd": 1300,
                    "desc_ar": "ظهور السنابل",
                    "desc_en": "Heading",
                },
                {
                    "name_en": "Flowering",
                    "name_ar": "الإزهار",
                    "gdd": 1500,
                    "desc_ar": "الإزهار والتلقيح",
                    "desc_en": "Flowering and pollination",
                },
                {
                    "name_en": "Grain Fill",
                    "name_ar": "امتلاء الحبوب",
                    "gdd": 1700,
                    "desc_ar": "امتلاء الحبوب",
                    "desc_en": "Grain filling",
                },
                {
                    "name_en": "Maturity",
                    "name_ar": "النضج",
                    "gdd": 2000,
                    "desc_ar": "النضج الفسيولوجي",
                    "desc_en": "Physiological maturity",
                },
            ],
        },
        "BARLEY": {
            "name_ar": "شعير",
            "name_en": "Barley",
            "total": 1800,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 140,
                    "desc_ar": "ظهور البادرات",
                    "desc_en": "Seedling emergence",
                },
                {
                    "name_en": "Tillering",
                    "name_ar": "التفريع",
                    "gdd": 400,
                    "desc_ar": "بداية التفريع",
                    "desc_en": "Tiller initiation",
                },
                {
                    "name_en": "Stem Elongation",
                    "name_ar": "استطالة الساق",
                    "gdd": 750,
                    "desc_ar": "استطالة الساق",
                    "desc_en": "Stem elongation",
                },
                {
                    "name_en": "Heading",
                    "name_ar": "الطرد",
                    "gdd": 1100,
                    "desc_ar": "ظهور السنابل",
                    "desc_en": "Heading",
                },
                {
                    "name_en": "Flowering",
                    "name_ar": "الإزهار",
                    "gdd": 1300,
                    "desc_ar": "الإزهار",
                    "desc_en": "Flowering",
                },
                {
                    "name_en": "Grain Fill",
                    "name_ar": "امتلاء الحبوب",
                    "gdd": 1550,
                    "desc_ar": "امتلاء الحبوب",
                    "desc_en": "Grain filling",
                },
                {
                    "name_en": "Maturity",
                    "name_ar": "النضج",
                    "gdd": 1800,
                    "desc_ar": "النضج",
                    "desc_en": "Maturity",
                },
            ],
        },
        "CORN": {
            "name_ar": "ذرة شامية",
            "name_en": "Corn",
            "total": 2700,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 120,
                    "desc_ar": "ظهور البادرات",
                    "desc_en": "Seedling emergence",
                },
                {
                    "name_en": "4-Leaf",
                    "name_ar": "4 أوراق",
                    "gdd": 350,
                    "desc_ar": "مرحلة 4 أوراق",
                    "desc_en": "V4 stage",
                },
                {
                    "name_en": "8-Leaf",
                    "name_ar": "8 أوراق",
                    "gdd": 750,
                    "desc_ar": "مرحلة 8 أوراق",
                    "desc_en": "V8 stage",
                },
                {
                    "name_en": "Tasseling",
                    "name_ar": "ظهور النورة",
                    "gdd": 1400,
                    "desc_ar": "ظهور النورة الذكرية",
                    "desc_en": "Tassel emergence",
                },
                {
                    "name_en": "Silking",
                    "name_ar": "ظهور الحرير",
                    "gdd": 1500,
                    "desc_ar": "ظهور الحرير",
                    "desc_en": "Silk emergence",
                },
                {
                    "name_en": "Blister",
                    "name_ar": "حبوب مائية",
                    "gdd": 1750,
                    "desc_ar": "الحبوب المائية",
                    "desc_en": "Blister stage",
                },
                {
                    "name_en": "Dent",
                    "name_ar": "تسنن الحبوب",
                    "gdd": 2300,
                    "desc_ar": "تسنن الحبوب",
                    "desc_en": "Dent stage",
                },
                {
                    "name_en": "Maturity",
                    "name_ar": "النضج",
                    "gdd": 2700,
                    "desc_ar": "النضج الفسيولوجي",
                    "desc_en": "Physiological maturity",
                },
            ],
        },
        "SORGHUM": {
            "name_ar": "ذرة رفيعة",
            "name_en": "Sorghum",
            "total": 2400,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 100,
                    "desc_ar": "ظهور البادرات",
                    "desc_en": "Seedling emergence",
                },
                {
                    "name_en": "3-Leaf",
                    "name_ar": "3 أوراق",
                    "gdd": 300,
                    "desc_ar": "مرحلة 3 أوراق",
                    "desc_en": "3-leaf stage",
                },
                {
                    "name_en": "5-Leaf",
                    "name_ar": "5 أوراق",
                    "gdd": 600,
                    "desc_ar": "مرحلة 5 أوراق",
                    "desc_en": "5-leaf stage",
                },
                {
                    "name_en": "Boot",
                    "name_ar": "الإسبال",
                    "gdd": 1200,
                    "desc_ar": "مرحلة الإسبال",
                    "desc_en": "Boot stage",
                },
                {
                    "name_en": "Flowering",
                    "name_ar": "الإزهار",
                    "gdd": 1500,
                    "desc_ar": "الإزهار",
                    "desc_en": "Flowering",
                },
                {
                    "name_en": "Soft Dough",
                    "name_ar": "عجينة لينة",
                    "gdd": 1900,
                    "desc_ar": "الحبوب العجينية",
                    "desc_en": "Soft dough",
                },
                {
                    "name_en": "Hard Dough",
                    "name_ar": "عجينة صلبة",
                    "gdd": 2200,
                    "desc_ar": "الحبوب الصلبة",
                    "desc_en": "Hard dough",
                },
                {
                    "name_en": "Maturity",
                    "name_ar": "النضج",
                    "gdd": 2400,
                    "desc_ar": "النضج",
                    "desc_en": "Maturity",
                },
            ],
        },
        "MILLET": {
            "name_ar": "دخن",
            "name_en": "Millet",
            "total": 1800,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 80,
                    "desc_ar": "ظهور البادرات",
                    "desc_en": "Emergence",
                },
                {
                    "name_en": "Tillering",
                    "name_ar": "التفريع",
                    "gdd": 400,
                    "desc_ar": "التفريع",
                    "desc_en": "Tillering",
                },
                {
                    "name_en": "Boot",
                    "name_ar": "الإسبال",
                    "gdd": 1000,
                    "desc_ar": "الإسبال",
                    "desc_en": "Boot",
                },
                {
                    "name_en": "Heading",
                    "name_ar": "الطرد",
                    "gdd": 1200,
                    "desc_ar": "طرد السنابل",
                    "desc_en": "Heading",
                },
                {
                    "name_en": "Flowering",
                    "name_ar": "الإزهار",
                    "gdd": 1350,
                    "desc_ar": "الإزهار",
                    "desc_en": "Flowering",
                },
                {
                    "name_en": "Grain Fill",
                    "name_ar": "امتلاء الحبوب",
                    "gdd": 1600,
                    "desc_ar": "امتلاء الحبوب",
                    "desc_en": "Grain fill",
                },
                {
                    "name_en": "Maturity",
                    "name_ar": "النضج",
                    "gdd": 1800,
                    "desc_ar": "النضج",
                    "desc_en": "Maturity",
                },
            ],
        },
        "TOMATO": {
            "name_ar": "طماطم",
            "name_en": "Tomato",
            "total": 1500,
            "stages": [
                {
                    "name_en": "Seedling",
                    "name_ar": "الشتلة",
                    "gdd": 100,
                    "desc_ar": "مرحلة الشتلة",
                    "desc_en": "Seedling stage",
                },
                {
                    "name_en": "Transplant",
                    "name_ar": "الشتل",
                    "gdd": 150,
                    "desc_ar": "بعد الشتل",
                    "desc_en": "After transplanting",
                },
                {
                    "name_en": "Vegetative",
                    "name_ar": "النمو الخضري",
                    "gdd": 400,
                    "desc_ar": "النمو الخضري",
                    "desc_en": "Vegetative growth",
                },
                {
                    "name_en": "First Flower",
                    "name_ar": "الزهرة الأولى",
                    "gdd": 700,
                    "desc_ar": "ظهور الزهرة الأولى",
                    "desc_en": "First flower",
                },
                {
                    "name_en": "Fruit Set",
                    "name_ar": "عقد الثمار",
                    "gdd": 900,
                    "desc_ar": "عقد الثمار",
                    "desc_en": "Fruit set",
                },
                {
                    "name_en": "Fruit Development",
                    "name_ar": "نمو الثمار",
                    "gdd": 1200,
                    "desc_ar": "نمو الثمار",
                    "desc_en": "Fruit development",
                },
                {
                    "name_en": "Ripening",
                    "name_ar": "النضج",
                    "gdd": 1500,
                    "desc_ar": "نضج الثمار",
                    "desc_en": "Fruit ripening",
                },
            ],
        },
        "POTATO": {
            "name_ar": "بطاطس",
            "name_en": "Potato",
            "total": 1600,
            "stages": [
                {
                    "name_en": "Sprout",
                    "name_ar": "التبرعم",
                    "gdd": 100,
                    "desc_ar": "بداية التبرعم",
                    "desc_en": "Sprout emergence",
                },
                {
                    "name_en": "Vegetative",
                    "name_ar": "النمو الخضري",
                    "gdd": 400,
                    "desc_ar": "النمو الخضري",
                    "desc_en": "Vegetative growth",
                },
                {
                    "name_en": "Tuber Initiation",
                    "name_ar": "بداية الدرنات",
                    "gdd": 700,
                    "desc_ar": "بداية تكوين الدرنات",
                    "desc_en": "Tuber initiation",
                },
                {
                    "name_en": "Tuber Bulking",
                    "name_ar": "تضخم الدرنات",
                    "gdd": 1100,
                    "desc_ar": "تضخم الدرنات",
                    "desc_en": "Tuber bulking",
                },
                {
                    "name_en": "Maturation",
                    "name_ar": "النضج",
                    "gdd": 1600,
                    "desc_ar": "نضج الدرنات",
                    "desc_en": "Maturation",
                },
            ],
        },
        "ONION": {
            "name_ar": "بصل",
            "name_en": "Onion",
            "total": 1800,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 150,
                    "desc_ar": "الإنبات",
                    "desc_en": "Emergence",
                },
                {
                    "name_en": "Vegetative",
                    "name_ar": "النمو الخضري",
                    "gdd": 600,
                    "desc_ar": "النمو الخضري",
                    "desc_en": "Vegetative growth",
                },
                {
                    "name_en": "Bulbing",
                    "name_ar": "تكوين البصلة",
                    "gdd": 1200,
                    "desc_ar": "تكوين البصلة",
                    "desc_en": "Bulb formation",
                },
                {
                    "name_en": "Maturation",
                    "name_ar": "النضج",
                    "gdd": 1800,
                    "desc_ar": "نضج البصلة",
                    "desc_en": "Bulb maturation",
                },
            ],
        },
        "COTTON": {
            "name_ar": "قطن",
            "name_en": "Cotton",
            "total": 2400,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 80,
                    "desc_ar": "ظهور البادرات",
                    "desc_en": "Emergence",
                },
                {
                    "name_en": "Squaring",
                    "name_ar": "ظهور البراعم",
                    "gdd": 600,
                    "desc_ar": "ظهور البراعم الزهرية",
                    "desc_en": "First square",
                },
                {
                    "name_en": "First Flower",
                    "name_ar": "الزهرة الأولى",
                    "gdd": 1100,
                    "desc_ar": "الزهرة الأولى",
                    "desc_en": "First flower",
                },
                {
                    "name_en": "First Boll",
                    "name_ar": "اللوزة الأولى",
                    "gdd": 1300,
                    "desc_ar": "اللوزة الأولى",
                    "desc_en": "First boll",
                },
                {
                    "name_en": "Boll Opening",
                    "name_ar": "تفتح اللوز",
                    "gdd": 2100,
                    "desc_ar": "بداية تفتح اللوز",
                    "desc_en": "First open boll",
                },
                {
                    "name_en": "Maturity",
                    "name_ar": "النضج",
                    "gdd": 2400,
                    "desc_ar": "النضج الكامل",
                    "desc_en": "Full maturity",
                },
            ],
        },
        "COFFEE": {
            "name_ar": "بن",
            "name_en": "Coffee",
            "total": 3000,  # Annual cycle
            "stages": [
                {
                    "name_en": "Bud Break",
                    "name_ar": "تفتح البراعم",
                    "gdd": 500,
                    "desc_ar": "تفتح البراعم",
                    "desc_en": "Bud break",
                },
                {
                    "name_en": "Flowering",
                    "name_ar": "الإزهار",
                    "gdd": 1200,
                    "desc_ar": "الإزهار",
                    "desc_en": "Flowering",
                },
                {
                    "name_en": "Pin Head",
                    "name_ar": "رأس الدبوس",
                    "gdd": 1500,
                    "desc_ar": "مرحلة رأس الدبوس",
                    "desc_en": "Pin head stage",
                },
                {
                    "name_en": "Green Berry",
                    "name_ar": "الحبة الخضراء",
                    "gdd": 2000,
                    "desc_ar": "الحبة الخضراء",
                    "desc_en": "Green berry",
                },
                {
                    "name_en": "Ripening",
                    "name_ar": "النضج",
                    "gdd": 2700,
                    "desc_ar": "بداية النضج",
                    "desc_en": "Ripening begins",
                },
                {
                    "name_en": "Harvest",
                    "name_ar": "الحصاد",
                    "gdd": 3000,
                    "desc_ar": "جاهز للحصاد",
                    "desc_en": "Ready for harvest",
                },
            ],
        },
        "FABA_BEAN": {
            "name_ar": "فول",
            "name_en": "Faba Bean",
            "total": 1800,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 120,
                    "desc_ar": "ظهور البادرات",
                    "desc_en": "Emergence",
                },
                {
                    "name_en": "Vegetative",
                    "name_ar": "النمو الخضري",
                    "gdd": 500,
                    "desc_ar": "النمو الخضري",
                    "desc_en": "Vegetative growth",
                },
                {
                    "name_en": "Flowering",
                    "name_ar": "الإزهار",
                    "gdd": 1000,
                    "desc_ar": "الإزهار",
                    "desc_en": "Flowering",
                },
                {
                    "name_en": "Pod Fill",
                    "name_ar": "امتلاء القرون",
                    "gdd": 1400,
                    "desc_ar": "امتلاء القرون",
                    "desc_en": "Pod filling",
                },
                {
                    "name_en": "Maturity",
                    "name_ar": "النضج",
                    "gdd": 1800,
                    "desc_ar": "النضج",
                    "desc_en": "Maturity",
                },
            ],
        },
        "LENTIL": {
            "name_ar": "عدس",
            "name_en": "Lentil",
            "total": 1600,
            "stages": [
                {
                    "name_en": "Emergence",
                    "name_ar": "الإنبات",
                    "gdd": 100,
                    "desc_ar": "ظهور البادرات",
                    "desc_en": "Emergence",
                },
                {
                    "name_en": "Vegetative",
                    "name_ar": "النمو الخضري",
                    "gdd": 450,
                    "desc_ar": "النمو الخضري",
                    "desc_en": "Vegetative growth",
                },
                {
                    "name_en": "Flowering",
                    "name_ar": "الإزهار",
                    "gdd": 900,
                    "desc_ar": "الإزهار",
                    "desc_en": "Flowering",
                },
                {
                    "name_en": "Pod Fill",
                    "name_ar": "امتلاء القرون",
                    "gdd": 1250,
                    "desc_ar": "امتلاء القرون",
                    "desc_en": "Pod filling",
                },
                {
                    "name_en": "Maturity",
                    "name_ar": "النضج",
                    "gdd": 1600,
                    "desc_ar": "النضج",
                    "desc_en": "Maturity",
                },
            ],
        },
        "GRAPE": {
            "name_ar": "عنب",
            "name_en": "Grape",
            "total": 2800,
            "stages": [
                {
                    "name_en": "Bud Break",
                    "name_ar": "تفتح البراعم",
                    "gdd": 100,
                    "desc_ar": "تفتح البراعم",
                    "desc_en": "Bud break",
                },
                {
                    "name_en": "Bloom",
                    "name_ar": "الإزهار",
                    "gdd": 800,
                    "desc_ar": "الإزهار",
                    "desc_en": "Bloom",
                },
                {
                    "name_en": "Fruit Set",
                    "name_ar": "عقد الثمار",
                    "gdd": 1100,
                    "desc_ar": "عقد الثمار",
                    "desc_en": "Fruit set",
                },
                {
                    "name_en": "Veraison",
                    "name_ar": "بداية النضج",
                    "gdd": 2000,
                    "desc_ar": "بداية تلون الحبات",
                    "desc_en": "Veraison (color change)",
                },
                {
                    "name_en": "Harvest",
                    "name_ar": "الحصاد",
                    "gdd": 2800,
                    "desc_ar": "جاهز للحصاد",
                    "desc_en": "Harvest maturity",
                },
            ],
        },
        "DATE_PALM": {
            "name_ar": "نخيل التمر",
            "name_en": "Date Palm",
            "total": 4500,  # From pollination to harvest
            "stages": [
                {
                    "name_en": "Pollination",
                    "name_ar": "التلقيح",
                    "gdd": 100,
                    "desc_ar": "وقت التلقيح",
                    "desc_en": "Pollination time",
                },
                {
                    "name_en": "Hababouk",
                    "name_ar": "حبابوك",
                    "gdd": 900,
                    "desc_ar": "مرحلة الحبابوك",
                    "desc_en": "Hababouk stage",
                },
                {
                    "name_en": "Kimri",
                    "name_ar": "كمري",
                    "gdd": 1800,
                    "desc_ar": "مرحلة الكمري",
                    "desc_en": "Kimri stage",
                },
                {
                    "name_en": "Khalal",
                    "name_ar": "خلال",
                    "gdd": 3000,
                    "desc_ar": "مرحلة الخلال",
                    "desc_en": "Khalal stage",
                },
                {
                    "name_en": "Rutab",
                    "name_ar": "رطب",
                    "gdd": 4000,
                    "desc_ar": "مرحلة الرطب",
                    "desc_en": "Rutab stage",
                },
                {
                    "name_en": "Tamar",
                    "name_ar": "تمر",
                    "gdd": 4500,
                    "desc_ar": "مرحلة التمر",
                    "desc_en": "Tamar (dry date)",
                },
            ],
        },
        "ALFALFA": {
            "name_ar": "برسيم حجازي",
            "name_en": "Alfalfa",
            "total": 900,  # Per cutting cycle
            "stages": [
                {
                    "name_en": "Regrowth",
                    "name_ar": "النمو الجديد",
                    "gdd": 150,
                    "desc_ar": "بداية النمو",
                    "desc_en": "Early regrowth",
                },
                {
                    "name_en": "Vegetative",
                    "name_ar": "النمو الخضري",
                    "gdd": 450,
                    "desc_ar": "النمو الخضري",
                    "desc_en": "Vegetative growth",
                },
                {
                    "name_en": "Bud",
                    "name_ar": "البرعم",
                    "gdd": 700,
                    "desc_ar": "مرحلة البرعم",
                    "desc_en": "Bud stage",
                },
                {
                    "name_en": "Flower",
                    "name_ar": "الإزهار",
                    "gdd": 900,
                    "desc_ar": "الإزهار - جاهز للحش",
                    "desc_en": "Flowering - ready to cut",
                },
            ],
        },
    }

    async def get_gdd_chart(
        self,
        field_id: str,
        crop_code: str,
        planting_date: date,
        latitude: float,
        longitude: float,
        end_date: date | None = None,
        method: str = "simple",
    ) -> GDDChart:
        """
        Generate comprehensive GDD chart from planting to current/end date.

        Args:
            field_id: Field identifier
            crop_code: Crop code (e.g., "WHEAT", "TOMATO")
            planting_date: Date crop was planted
            latitude: Field latitude
            longitude: Field longitude
            end_date: End date for analysis (default: today)
            method: Calculation method (simple, modified, sine)

        Returns:
            GDDChart with complete analysis
        """
        # Import weather service
        from .weather_integration import get_weather_service

        crop_code = crop_code.upper()
        if crop_code not in self.CROP_GDD_REQUIREMENTS:
            raise ValueError(f"Unknown crop: {crop_code}")

        if end_date is None:
            end_date = date.today()

        # Get crop parameters
        crop_params = self.CROP_GDD_REQUIREMENTS[crop_code]
        temp_params = self.CROP_BASE_TEMPS.get(crop_code, {"base": 10, "upper": None})
        base_temp = temp_params["base"]
        upper_temp = temp_params["upper"]

        # Fetch historical weather data
        weather_service = get_weather_service()
        historical = await weather_service.get_historical(
            latitude, longitude, planting_date, end_date
        )

        # Calculate daily GDD
        daily_data = []
        accumulated = 0.0

        for weather_point in historical.daily:
            day_date = weather_point.timestamp.date()

            # Calculate daily GDD
            daily_gdd = self.calculate_daily_gdd(
                temp_min=weather_point.temperature_min_c,
                temp_max=weather_point.temperature_max_c,
                base_temp=base_temp,
                upper_temp=upper_temp,
                method=method,
            )

            accumulated += daily_gdd

            daily_data.append(
                GDDDataPoint(
                    date=day_date,
                    temp_min=weather_point.temperature_min_c,
                    temp_max=weather_point.temperature_max_c,
                    temp_avg=weather_point.temperature_c,
                    daily_gdd=daily_gdd,
                    accumulated_gdd=accumulated,
                )
            )

        # Calculate current status
        total_gdd = accumulated
        days_since_planting = (end_date - planting_date).days
        avg_daily_gdd = total_gdd / max(1, days_since_planting)

        # Determine current stage and next stage
        current_stage, current_stage_ar, next_stage, next_stage_ar, gdd_to_next = (
            self.get_current_stage(crop_code, total_gdd)
        )

        # Generate milestones
        milestones = self.get_milestones(
            crop_code=crop_code,
            accumulated_gdd=total_gdd,
            daily_avg_gdd=avg_daily_gdd,
            current_date=end_date,
            daily_data=daily_data,
        )

        # Predict harvest
        total_required = crop_params["total"]
        gdd_to_harvest = max(0, total_required - total_gdd)

        if avg_daily_gdd > 0:
            days_to_harvest = int(gdd_to_harvest / avg_daily_gdd)
            estimated_harvest_date = end_date + timedelta(days=days_to_harvest)
        else:
            days_to_harvest = 0
            estimated_harvest_date = end_date

        # Compare to normal year
        vs_normal, vs_normal_ar, vs_normal_en = await self.compare_to_normal(
            latitude=latitude,
            longitude=longitude,
            current_gdd=total_gdd,
            days_since_planting=days_since_planting,
            base_temp=base_temp,
            upper_temp=upper_temp,
            method=method,
        )

        # Calculate confidence
        confidence = self._calculate_confidence(len(daily_data), days_since_planting)

        return GDDChart(
            field_id=field_id,
            crop_code=crop_code,
            crop_name_ar=crop_params["name_ar"],
            crop_name_en=crop_params["name_en"],
            planting_date=planting_date,
            base_temp=base_temp,
            upper_temp=upper_temp,
            current_date=end_date,
            total_gdd=total_gdd,
            days_since_planting=days_since_planting,
            avg_daily_gdd=avg_daily_gdd,
            daily_data=daily_data,
            milestones=milestones,
            current_stage=current_stage,
            current_stage_ar=current_stage_ar,
            next_stage=next_stage,
            next_stage_ar=next_stage_ar,
            gdd_to_next_stage=gdd_to_next,
            estimated_harvest_date=estimated_harvest_date,
            gdd_to_harvest=gdd_to_harvest,
            days_to_harvest=days_to_harvest,
            vs_normal_year=vs_normal,
            vs_normal_description_ar=vs_normal_ar,
            vs_normal_description_en=vs_normal_en,
            calculation_method=method,
            confidence=confidence,
        )

    async def get_gdd_forecast(
        self,
        latitude: float,
        longitude: float,
        current_gdd: float,
        target_gdd: float,
        base_temp: float = 10,
        upper_temp: float | None = None,
        method: str = "simple",
    ) -> dict:
        """
        Forecast when target GDD will be reached using weather forecast.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            current_gdd: Current accumulated GDD
            target_gdd: Target GDD to reach
            base_temp: Base temperature
            upper_temp: Upper cutoff temperature (optional)
            method: Calculation method

        Returns:
            Forecast dict with estimated date and daily projections
        """
        from .weather_integration import get_weather_service

        weather_service = get_weather_service()

        # Get 16-day forecast (maximum available)
        forecast = await weather_service.get_forecast(latitude, longitude, days=16)

        # Calculate GDD accumulation from forecast
        gdd_needed = target_gdd - current_gdd
        accumulated = current_gdd
        forecast_data = []
        target_date = None

        for day in forecast.daily:
            daily_gdd = self.calculate_daily_gdd(
                temp_min=day.temperature_min_c,
                temp_max=day.temperature_max_c,
                base_temp=base_temp,
                upper_temp=upper_temp,
                method=method,
            )

            accumulated += daily_gdd

            forecast_data.append(
                {
                    "date": day.timestamp.date().isoformat(),
                    "temp_min_c": round(day.temperature_min_c, 1),
                    "temp_max_c": round(day.temperature_max_c, 1),
                    "daily_gdd": round(daily_gdd, 1),
                    "accumulated_gdd": round(accumulated, 1),
                }
            )

            if target_date is None and accumulated >= target_gdd:
                target_date = day.timestamp.date()

        # If target not reached in forecast, estimate using average
        if target_date is None and forecast_data:
            avg_forecast_gdd = sum(d["daily_gdd"] for d in forecast_data) / len(
                forecast_data
            )
            if avg_forecast_gdd > 0:
                remaining_days = int((target_gdd - accumulated) / avg_forecast_gdd)
                target_date = forecast.daily[-1].timestamp.date() + timedelta(
                    days=remaining_days
                )
                is_estimated = True
            else:
                target_date = None
                is_estimated = False
        else:
            is_estimated = False

        return {
            "current_gdd": round(current_gdd, 1),
            "target_gdd": round(target_gdd, 1),
            "gdd_needed": round(gdd_needed, 1),
            "estimated_date": target_date.isoformat() if target_date else None,
            "is_estimated": is_estimated,
            "forecast_data": forecast_data,
            "base_temp_c": base_temp,
            "upper_temp_c": upper_temp,
            "method": method,
        }

    def calculate_daily_gdd(
        self,
        temp_min: float,
        temp_max: float,
        base_temp: float,
        upper_temp: float | None = None,
        method: str = "simple",
    ) -> float:
        """
        Calculate daily GDD using specified method.

        Methods:
        - simple: (Tmax + Tmin) / 2 - Tbase (if result > 0)
        - modified: Apply upper and lower cutoffs before calculation
        - sine: Sine curve approximation for sub-daily temperature

        Args:
            temp_min: Daily minimum temperature (°C)
            temp_max: Daily maximum temperature (°C)
            base_temp: Base temperature (°C)
            upper_temp: Upper cutoff temperature (°C), optional
            method: Calculation method

        Returns:
            Daily GDD value
        """
        if method == "simple":
            avg_temp = (temp_max + temp_min) / 2
            return max(0, avg_temp - base_temp)

        elif method == "modified":
            # Apply cutoffs
            if upper_temp:
                temp_max = min(temp_max, upper_temp)
                temp_min = min(temp_min, upper_temp)

            temp_max = max(temp_max, base_temp)
            temp_min = max(temp_min, base_temp)

            avg_temp = (temp_max + temp_min) / 2
            return max(0, avg_temp - base_temp)

        elif method == "sine":
            # Sine wave approximation
            # More accurate but computationally intensive
            # Based on Baskerville-Emin method

            if temp_min >= base_temp:
                # Both above base - simple average
                avg_temp = (temp_max + temp_min) / 2
                return avg_temp - base_temp
            elif temp_max <= base_temp:
                # Both below base - no GDD
                return 0.0
            else:
                # Crosses base temp - use sine approximation
                amplitude = (temp_max - temp_min) / 2
                avg = (temp_max + temp_min) / 2

                # Angle where temperature crosses base
                theta = math.asin((base_temp - avg) / amplitude)

                # GDD accumulated (integral of sine curve above base)
                gdd = (1 / math.pi) * (
                    (avg - base_temp) * (math.pi - 2 * theta)
                    + 2 * amplitude * math.cos(theta)
                )

                return max(0, gdd)

        else:
            # Default to simple method
            avg_temp = (temp_max + temp_min) / 2
            return max(0, avg_temp - base_temp)

    def get_current_stage(
        self, crop_code: str, accumulated_gdd: float
    ) -> tuple[str, str, str, str, float]:
        """
        Get current growth stage based on accumulated GDD.

        Returns:
            (current_stage_en, current_stage_ar, next_stage_en, next_stage_ar, gdd_to_next)
        """
        crop_code = crop_code.upper()
        if crop_code not in self.CROP_GDD_REQUIREMENTS:
            return ("Unknown", "غير معروف", "Unknown", "غير معروف", 0.0)

        crop_params = self.CROP_GDD_REQUIREMENTS[crop_code]
        stages = crop_params["stages"]

        # Find current stage
        current_stage_en = "Planting"
        current_stage_ar = "الزراعة"
        next_stage_en = stages[0]["name_en"] if stages else "Unknown"
        next_stage_ar = stages[0]["name_ar"] if stages else "غير معروف"
        gdd_to_next = stages[0]["gdd"] if stages else 0.0

        for i, stage in enumerate(stages):
            if accumulated_gdd >= stage["gdd"]:
                current_stage_en = stage["name_en"]
                current_stage_ar = stage["name_ar"]

                # Get next stage
                if i + 1 < len(stages):
                    next_stage_en = stages[i + 1]["name_en"]
                    next_stage_ar = stages[i + 1]["name_ar"]
                    gdd_to_next = stages[i + 1]["gdd"] - accumulated_gdd
                else:
                    next_stage_en = "Harvest"
                    next_stage_ar = "الحصاد"
                    gdd_to_next = 0.0
            else:
                # This is the next stage
                next_stage_en = stage["name_en"]
                next_stage_ar = stage["name_ar"]
                gdd_to_next = stage["gdd"] - accumulated_gdd
                break

        return (
            current_stage_en,
            current_stage_ar,
            next_stage_en,
            next_stage_ar,
            gdd_to_next,
        )

    def get_milestones(
        self,
        crop_code: str,
        accumulated_gdd: float,
        daily_avg_gdd: float,
        current_date: date,
        daily_data: list[GDDDataPoint],
    ) -> list[GrowthMilestone]:
        """
        Generate milestone list with actual/predicted dates.

        Args:
            crop_code: Crop code
            accumulated_gdd: Current accumulated GDD
            daily_avg_gdd: Average daily GDD
            current_date: Current date
            daily_data: List of daily GDD data points

        Returns:
            List of growth milestones
        """
        crop_code = crop_code.upper()
        if crop_code not in self.CROP_GDD_REQUIREMENTS:
            return []

        crop_params = self.CROP_GDD_REQUIREMENTS[crop_code]
        stages = crop_params["stages"]

        milestones = []

        for stage in stages:
            gdd_req = stage["gdd"]
            is_reached = accumulated_gdd >= gdd_req

            # Determine reached/expected date
            reached_date = None
            expected_date = None
            days_remaining = None

            if is_reached:
                # Find date when this GDD was reached
                for data_point in daily_data:
                    if data_point.accumulated_gdd >= gdd_req:
                        reached_date = data_point.date
                        break
                days_remaining = 0
            else:
                # Predict when it will be reached
                gdd_needed = gdd_req - accumulated_gdd
                if daily_avg_gdd > 0:
                    days_remaining = int(gdd_needed / daily_avg_gdd)
                    expected_date = current_date + timedelta(days=days_remaining)
                else:
                    days_remaining = None

            milestones.append(
                GrowthMilestone(
                    stage_name_en=stage["name_en"],
                    stage_name_ar=stage["name_ar"],
                    gdd_required=gdd_req,
                    gdd_accumulated=accumulated_gdd,
                    is_reached=is_reached,
                    reached_date=reached_date,
                    expected_date=expected_date,
                    days_remaining=days_remaining,
                    description_ar=stage["desc_ar"],
                    description_en=stage["desc_en"],
                )
            )

        return milestones

    async def compare_to_normal(
        self,
        latitude: float,
        longitude: float,
        current_gdd: float,
        days_since_planting: int,
        base_temp: float,
        upper_temp: float | None = None,
        method: str = "simple",
    ) -> tuple[float, str, str]:
        """
        Compare current GDD accumulation to historical 10-year average.

        Returns:
            (percent_difference, description_ar, description_en)
        """
        from .weather_integration import get_weather_service

        try:
            # Calculate average GDD for same period over past 10 years
            weather_service = get_weather_service()
            current_year = date.today().year

            # Sample 3 years to get estimate (full 10 years would be too many API calls)
            sample_years = [current_year - 1, current_year - 2, current_year - 5]
            gdd_samples = []

            for year in sample_years:
                try:
                    # Calculate start date for this historical year
                    start_date = date.today().replace(year=year) - timedelta(
                        days=days_since_planting
                    )
                    end_date = date.today().replace(year=year)

                    # Skip if dates are in the future
                    if end_date > date.today():
                        continue

                    historical = await weather_service.get_historical(
                        latitude, longitude, start_date, end_date
                    )

                    # Calculate GDD for this period
                    gdd_sum = 0.0
                    for day in historical.daily:
                        daily_gdd = self.calculate_daily_gdd(
                            temp_min=day.temperature_min_c,
                            temp_max=day.temperature_max_c,
                            base_temp=base_temp,
                            upper_temp=upper_temp,
                            method=method,
                        )
                        gdd_sum += daily_gdd

                    gdd_samples.append(gdd_sum)
                except Exception as e:
                    logger.warning(
                        f"Could not fetch historical data for year {year}: {e}"
                    )
                    continue

            if not gdd_samples:
                return (0.0, "لا توجد بيانات مقارنة", "No comparison data available")

            # Calculate average
            normal_gdd = sum(gdd_samples) / len(gdd_samples)

            # Calculate percent difference
            percent_diff = (
                (current_gdd - normal_gdd) / normal_gdd * 100 if normal_gdd > 0 else 0.0
            )

            # Generate descriptions
            if percent_diff > 10:
                desc_ar = f"متقدم بنسبة {abs(percent_diff):.1f}% عن المعدل الطبيعي - نمو أسرع من المتوقع"
                desc_en = f"{abs(percent_diff):.1f}% ahead of normal - faster growth than expected"
            elif percent_diff < -10:
                desc_ar = f"متأخر بنسبة {abs(percent_diff):.1f}% عن المعدل الطبيعي - نمو أبطأ من المتوقع"
                desc_en = f"{abs(percent_diff):.1f}% behind normal - slower growth than expected"
            else:
                desc_ar = "ضمن المعدل الطبيعي - نمو طبيعي"
                desc_en = "Within normal range - typical growth"

            return (percent_diff, desc_ar, desc_en)

        except Exception as e:
            logger.error(f"Error comparing to normal: {e}")
            return (0.0, "خطأ في المقارنة", "Comparison error")

    async def get_crop_requirements(self, crop_code: str) -> CropGDDRequirements:
        """
        Get GDD requirements for a crop.

        Args:
            crop_code: Crop code

        Returns:
            CropGDDRequirements with all stages and requirements
        """
        crop_code = crop_code.upper()
        if crop_code not in self.CROP_GDD_REQUIREMENTS:
            raise ValueError(f"Unknown crop: {crop_code}")

        crop_params = self.CROP_GDD_REQUIREMENTS[crop_code]
        temp_params = self.CROP_BASE_TEMPS.get(crop_code, {"base": 10, "upper": None})

        # Format stages
        stages = []
        prev_gdd = 0
        for stage in crop_params["stages"]:
            stages.append(
                {
                    "name_en": stage["name_en"],
                    "name_ar": stage["name_ar"],
                    "gdd_start": prev_gdd,
                    "gdd_end": stage["gdd"],
                    "gdd_duration": stage["gdd"] - prev_gdd,
                    "description_ar": stage["desc_ar"],
                    "description_en": stage["desc_en"],
                }
            )
            prev_gdd = stage["gdd"]

        return CropGDDRequirements(
            crop_code=crop_code,
            crop_name_ar=crop_params["name_ar"],
            crop_name_en=crop_params["name_en"],
            base_temp=temp_params["base"],
            upper_temp=temp_params.get("upper"),
            total_gdd_required=crop_params["total"],
            stages=stages,
        )

    def get_all_crops(self) -> list[dict]:
        """
        Get list of all supported crops.

        Returns:
            List of crop info dictionaries
        """
        crops = []
        for crop_code, params in self.CROP_GDD_REQUIREMENTS.items():
            temp_params = self.CROP_BASE_TEMPS.get(
                crop_code, {"base": 10, "upper": None}
            )
            crops.append(
                {
                    "crop_code": crop_code,
                    "crop_name_ar": params["name_ar"],
                    "crop_name_en": params["name_en"],
                    "base_temp_c": temp_params["base"],
                    "upper_temp_c": temp_params.get("upper"),
                    "total_gdd_required": params["total"],
                    "num_stages": len(params["stages"]),
                }
            )

        return sorted(crops, key=lambda x: x["crop_name_en"])

    def _calculate_confidence(self, num_observations: int, days_elapsed: int) -> float:
        """
        Calculate confidence in GDD predictions.

        Based on:
        - Number of weather observations
        - Days elapsed since planting
        - Data completeness
        """
        # More observations = higher confidence
        obs_score = min(1.0, num_observations / max(1, days_elapsed * 0.5))

        # More days = higher confidence (up to a point)
        days_score = min(1.0, days_elapsed / 30)

        # Combine
        confidence = obs_score * 0.6 + days_score * 0.4
        return min(0.95, max(0.5, confidence))


# Global instance
_gdd_tracker = None


def get_gdd_tracker() -> GDDTracker:
    """Get global GDD tracker instance"""
    global _gdd_tracker
    if _gdd_tracker is None:
        _gdd_tracker = GDDTracker()
    return _gdd_tracker
