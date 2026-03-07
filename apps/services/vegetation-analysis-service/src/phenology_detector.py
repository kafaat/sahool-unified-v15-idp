"""
SAHOOL Crop Phenology Detection
كشف مراحل نمو المحاصيل من بيانات الأقمار الصناعية

Detects crop growth stages from NDVI time series using phenological metrics:
- SOS (Start of Season) - بداية الموسم
- POS (Peak of Season) - ذروة الموسم
- EOS (End of Season) - نهاية الموسم
- LOS (Length of Season) - طول الموسم

References:
- BBCH Scale (Biologische Bundesanstalt, Bundessortenamt and CHemical industry)
- Bolton & Friedl (2013) - Forecasting crop yield using remotely sensed vegetation indices
- Reed et al. (1994) - Measuring phenological variability from satellite imagery
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum


class GrowthStage(Enum):
    """Crop growth stages based on BBCH scale"""

    BARE_SOIL = "bare_soil"  # Before planting / BBCH 00
    GERMINATION = "germination"  # BBCH 00-09
    EMERGENCE = "emergence"  # BBCH 10-19
    LEAF_DEVELOPMENT = "leaf_dev"  # BBCH 20-29
    TILLERING = "tillering"  # BBCH 30-39 (cereals)
    STEM_ELONGATION = "stem_elong"  # BBCH 40-49
    BOOTING = "booting"  # BBCH 50-59 (cereals)
    FLOWERING = "flowering"  # BBCH 60-69
    FRUIT_DEVELOPMENT = "fruit_dev"  # BBCH 70-79
    RIPENING = "ripening"  # BBCH 80-89
    SENESCENCE = "senescence"  # BBCH 90-99
    HARVESTED = "harvested"  # Post-harvest

    @property
    def label_ar(self) -> str:
        """Arabic label for growth stage"""
        labels = {
            "bare_soil": "تربة عارية",
            "germination": "إنبات",
            "emergence": "بزوغ",
            "leaf_dev": "تطور الأوراق",
            "tillering": "التفريع",
            "stem_elong": "استطالة الساق",
            "booting": "طور الإسبال",
            "flowering": "إزهار",
            "fruit_dev": "تطور الثمار",
            "ripening": "نضج",
            "senescence": "شيخوخة",
            "harvested": "محصود",
        }
        return labels.get(self.value, self.value)

    @property
    def label_en(self) -> str:
        """English label for growth stage"""
        labels = {
            "bare_soil": "Bare Soil",
            "germination": "Germination",
            "emergence": "Emergence",
            "leaf_dev": "Leaf Development",
            "tillering": "Tillering",
            "stem_elong": "Stem Elongation",
            "booting": "Booting",
            "flowering": "Flowering",
            "fruit_dev": "Fruit Development",
            "ripening": "Ripening",
            "senescence": "Senescence",
            "harvested": "Harvested",
        }
        return labels.get(self.value, self.value)


@dataclass
class PhenologyResult:
    """Result of phenology detection for a field"""

    field_id: str
    crop_type: str
    current_stage: GrowthStage
    stage_start_date: date
    days_in_stage: int
    expected_next_stage: GrowthStage
    days_to_next_stage: int
    season_progress_percent: float
    ndvi_at_detection: float
    confidence: float
    recommendations_ar: list[str]
    recommendations_en: list[str]

    # Additional metrics
    sos_date: date | None = None  # Start of Season
    pos_date: date | None = None  # Peak of Season
    eos_date: date | None = None  # End of Season
    estimated_harvest_date: date | None = None


@dataclass
class PhenologyTimeline:
    """Expected phenology timeline for crop planning"""

    field_id: str
    crop_type: str
    planting_date: date
    stages: list[dict]  # [{stage, start_date, end_date, duration_days, ndvi_range}]
    harvest_estimate: date
    season_length_days: int
    critical_periods: list[dict]  # [{period, dates, reason_ar, reason_en}]


class PhenologyDetector:
    """
    Detect crop growth stages from NDVI time series.

    Algorithm:
    1. Smooth NDVI time series using Savitzky-Golay filter
    2. Detect phenological events:
       - SOS: NDVI crosses emergence threshold with sustained increase
       - POS: Maximum NDVI in season
       - EOS: NDVI drops below senescence threshold
    3. Map relative position in season to BBCH growth stages
    4. Generate stage-specific recommendations

    Yemen-specific calibrations for major crops.
    """

    # NDVI thresholds for phenological event detection
    NDVI_THRESHOLDS = {
        "bare_soil": 0.10,  # Bare soil baseline
        "emergence": 0.20,  # Green-up begins (SOS)
        "active_growth": 0.35,  # Active vegetative growth
        "peak": 0.65,  # Maximum greenness (POS)
        "senescence_start": 0.45,  # Decline begins
        "harvest_ready": 0.25,  # Ready for harvest (EOS)
    }

    # Yemen crop-specific phenology parameters
    # Based on Yemen agricultural practices and climate zones
    YEMEN_CROP_SEASONS = {
        # Cereals (الحبوب)
        "wheat": {
            "name_ar": "قمح",
            "season_length_days": 120,
            "stages": {
                "germination": {
                    "duration_days": 10,
                    "ndvi_start": 0.15,
                    "ndvi_end": 0.25,
                },
                "emergence": {
                    "duration_days": 15,
                    "ndvi_start": 0.25,
                    "ndvi_end": 0.35,
                },
                "tillering": {
                    "duration_days": 30,
                    "ndvi_start": 0.35,
                    "ndvi_end": 0.55,
                },
                "stem_elongation": {
                    "duration_days": 20,
                    "ndvi_start": 0.55,
                    "ndvi_end": 0.70,
                },
                "booting": {"duration_days": 10, "ndvi_start": 0.70, "ndvi_end": 0.75},
                "flowering": {
                    "duration_days": 12,
                    "ndvi_start": 0.75,
                    "ndvi_end": 0.72,
                },
                "ripening": {"duration_days": 18, "ndvi_start": 0.72, "ndvi_end": 0.45},
                "senescence": {
                    "duration_days": 5,
                    "ndvi_start": 0.45,
                    "ndvi_end": 0.25,
                },
            },
            "critical_periods": [
                {
                    "stage": "tillering",
                    "reason_ar": "فترة حرجة للتسميد",
                    "reason_en": "Critical fertilization period",
                },
                {
                    "stage": "flowering",
                    "reason_ar": "حساس للإجهاد المائي",
                    "reason_en": "Sensitive to water stress",
                },
            ],
        },
        "sorghum": {
            "name_ar": "ذرة رفيعة",
            "season_length_days": 110,
            "stages": {
                "germination": {
                    "duration_days": 7,
                    "ndvi_start": 0.15,
                    "ndvi_end": 0.25,
                },
                "emergence": {
                    "duration_days": 12,
                    "ndvi_start": 0.25,
                    "ndvi_end": 0.35,
                },
                "leaf_development": {
                    "duration_days": 35,
                    "ndvi_start": 0.35,
                    "ndvi_end": 0.60,
                },
                "stem_elongation": {
                    "duration_days": 20,
                    "ndvi_start": 0.60,
                    "ndvi_end": 0.75,
                },
                "flowering": {
                    "duration_days": 15,
                    "ndvi_start": 0.75,
                    "ndvi_end": 0.70,
                },
                "fruit_development": {
                    "duration_days": 15,
                    "ndvi_start": 0.70,
                    "ndvi_end": 0.55,
                },
                "ripening": {"duration_days": 20, "ndvi_start": 0.55, "ndvi_end": 0.30},
                "senescence": {
                    "duration_days": 6,
                    "ndvi_start": 0.30,
                    "ndvi_end": 0.20,
                },
            },
            "critical_periods": [
                {
                    "stage": "flowering",
                    "reason_ar": "حساس جداً للحرارة",
                    "reason_en": "Very sensitive to heat",
                },
                {
                    "stage": "fruit_development",
                    "reason_ar": "احتياجات مائية عالية",
                    "reason_en": "High water requirements",
                },
            ],
        },
        "millet": {
            "name_ar": "دخن",
            "season_length_days": 90,
            "stages": {
                "germination": {
                    "duration_days": 5,
                    "ndvi_start": 0.15,
                    "ndvi_end": 0.22,
                },
                "emergence": {
                    "duration_days": 10,
                    "ndvi_start": 0.22,
                    "ndvi_end": 0.32,
                },
                "leaf_development": {
                    "duration_days": 25,
                    "ndvi_start": 0.32,
                    "ndvi_end": 0.55,
                },
                "stem_elongation": {
                    "duration_days": 15,
                    "ndvi_start": 0.55,
                    "ndvi_end": 0.65,
                },
                "flowering": {
                    "duration_days": 12,
                    "ndvi_start": 0.65,
                    "ndvi_end": 0.62,
                },
                "fruit_development": {
                    "duration_days": 15,
                    "ndvi_start": 0.62,
                    "ndvi_end": 0.45,
                },
                "ripening": {"duration_days": 8, "ndvi_start": 0.45, "ndvi_end": 0.25},
            },
            "critical_periods": [
                {
                    "stage": "flowering",
                    "reason_ar": "حساس للرياح",
                    "reason_en": "Sensitive to wind",
                },
            ],
        },
        # Vegetables (الخضروات)
        "tomato": {
            "name_ar": "طماطم",
            "season_length_days": 105,
            "stages": {
                "germination": {
                    "duration_days": 8,
                    "ndvi_start": 0.15,
                    "ndvi_end": 0.25,
                },
                "emergence": {
                    "duration_days": 12,
                    "ndvi_start": 0.25,
                    "ndvi_end": 0.35,
                },
                "leaf_development": {
                    "duration_days": 25,
                    "ndvi_start": 0.35,
                    "ndvi_end": 0.60,
                },
                "flowering": {
                    "duration_days": 15,
                    "ndvi_start": 0.60,
                    "ndvi_end": 0.70,
                },
                "fruit_development": {
                    "duration_days": 30,
                    "ndvi_start": 0.70,
                    "ndvi_end": 0.65,
                },
                "ripening": {"duration_days": 15, "ndvi_start": 0.65, "ndvi_end": 0.55},
            },
            "critical_periods": [
                {
                    "stage": "flowering",
                    "reason_ar": "التلقيح الحرج",
                    "reason_en": "Critical pollination",
                },
                {
                    "stage": "fruit_development",
                    "reason_ar": "احتياجات غذائية عالية",
                    "reason_en": "High nutrient demand",
                },
            ],
        },
        "potato": {
            "name_ar": "بطاطس",
            "season_length_days": 100,
            "stages": {
                "germination": {
                    "duration_days": 12,
                    "ndvi_start": 0.12,
                    "ndvi_end": 0.22,
                },
                "emergence": {
                    "duration_days": 15,
                    "ndvi_start": 0.22,
                    "ndvi_end": 0.35,
                },
                "leaf_development": {
                    "duration_days": 30,
                    "ndvi_start": 0.35,
                    "ndvi_end": 0.65,
                },
                "flowering": {
                    "duration_days": 10,
                    "ndvi_start": 0.65,
                    "ndvi_end": 0.68,
                },
                "fruit_development": {
                    "duration_days": 25,
                    "ndvi_start": 0.68,
                    "ndvi_end": 0.55,
                },
                "ripening": {"duration_days": 8, "ndvi_start": 0.55, "ndvi_end": 0.30},
            },
            "critical_periods": [
                {
                    "stage": "fruit_development",
                    "reason_ar": "تكوين الدرنات",
                    "reason_en": "Tuber formation",
                },
            ],
        },
        "onion": {
            "name_ar": "بصل",
            "season_length_days": 120,
            "stages": {
                "germination": {
                    "duration_days": 10,
                    "ndvi_start": 0.15,
                    "ndvi_end": 0.22,
                },
                "emergence": {
                    "duration_days": 18,
                    "ndvi_start": 0.22,
                    "ndvi_end": 0.30,
                },
                "leaf_development": {
                    "duration_days": 50,
                    "ndvi_start": 0.30,
                    "ndvi_end": 0.55,
                },
                "fruit_development": {
                    "duration_days": 30,
                    "ndvi_start": 0.55,
                    "ndvi_end": 0.50,
                },
                "ripening": {"duration_days": 12, "ndvi_start": 0.50, "ndvi_end": 0.25},
            },
            "critical_periods": [
                {
                    "stage": "fruit_development",
                    "reason_ar": "تكوين البصلة",
                    "reason_en": "Bulb formation",
                },
            ],
        },
        # Cash Crops (المحاصيل النقدية)
        "coffee": {
            "name_ar": "بن",
            "season_length_days": 365,  # Perennial, one harvest cycle
            "stages": {
                "emergence": {
                    "duration_days": 45,
                    "ndvi_start": 0.30,
                    "ndvi_end": 0.40,
                },
                "leaf_development": {
                    "duration_days": 120,
                    "ndvi_start": 0.40,
                    "ndvi_end": 0.60,
                },
                "flowering": {
                    "duration_days": 60,
                    "ndvi_start": 0.60,
                    "ndvi_end": 0.70,
                },
                "fruit_development": {
                    "duration_days": 90,
                    "ndvi_start": 0.70,
                    "ndvi_end": 0.65,
                },
                "ripening": {"duration_days": 50, "ndvi_start": 0.65, "ndvi_end": 0.55},
            },
            "critical_periods": [
                {
                    "stage": "flowering",
                    "reason_ar": "التلقيح والعقد",
                    "reason_en": "Pollination and fruit set",
                },
                {
                    "stage": "fruit_development",
                    "reason_ar": "نمو الحبوب",
                    "reason_en": "Bean development",
                },
            ],
        },
        "qat": {
            "name_ar": "قات",
            "season_length_days": 90,  # Harvest cycle for leaves
            "stages": {
                "leaf_development": {
                    "duration_days": 60,
                    "ndvi_start": 0.40,
                    "ndvi_end": 0.65,
                },
                "ripening": {"duration_days": 30, "ndvi_start": 0.65, "ndvi_end": 0.60},
            },
            "critical_periods": [
                {
                    "stage": "leaf_development",
                    "reason_ar": "جودة الأوراق",
                    "reason_en": "Leaf quality",
                },
            ],
        },
        # Legumes (البقوليات)
        "faba_bean": {
            "name_ar": "فول",
            "season_length_days": 130,
            "stages": {
                "germination": {
                    "duration_days": 8,
                    "ndvi_start": 0.15,
                    "ndvi_end": 0.25,
                },
                "emergence": {
                    "duration_days": 15,
                    "ndvi_start": 0.25,
                    "ndvi_end": 0.35,
                },
                "leaf_development": {
                    "duration_days": 40,
                    "ndvi_start": 0.35,
                    "ndvi_end": 0.60,
                },
                "flowering": {
                    "duration_days": 20,
                    "ndvi_start": 0.60,
                    "ndvi_end": 0.70,
                },
                "fruit_development": {
                    "duration_days": 30,
                    "ndvi_start": 0.70,
                    "ndvi_end": 0.55,
                },
                "ripening": {"duration_days": 17, "ndvi_start": 0.55, "ndvi_end": 0.30},
            },
            "critical_periods": [
                {
                    "stage": "flowering",
                    "reason_ar": "تثبيت النيتروجين",
                    "reason_en": "Nitrogen fixation",
                },
            ],
        },
        "lentil": {
            "name_ar": "عدس",
            "season_length_days": 110,
            "stages": {
                "germination": {
                    "duration_days": 7,
                    "ndvi_start": 0.15,
                    "ndvi_end": 0.23,
                },
                "emergence": {
                    "duration_days": 12,
                    "ndvi_start": 0.23,
                    "ndvi_end": 0.32,
                },
                "leaf_development": {
                    "duration_days": 35,
                    "ndvi_start": 0.32,
                    "ndvi_end": 0.55,
                },
                "flowering": {
                    "duration_days": 18,
                    "ndvi_start": 0.55,
                    "ndvi_end": 0.65,
                },
                "fruit_development": {
                    "duration_days": 25,
                    "ndvi_start": 0.65,
                    "ndvi_end": 0.45,
                },
                "ripening": {"duration_days": 13, "ndvi_start": 0.45, "ndvi_end": 0.25},
            },
            "critical_periods": [
                {
                    "stage": "flowering",
                    "reason_ar": "حساس للحرارة",
                    "reason_en": "Heat sensitive",
                },
            ],
        },
        # Fruits (الفواكه)
        "mango": {
            "name_ar": "مانجو",
            "season_length_days": 180,  # Fruiting cycle
            "stages": {
                "flowering": {
                    "duration_days": 30,
                    "ndvi_start": 0.50,
                    "ndvi_end": 0.60,
                },
                "fruit_development": {
                    "duration_days": 90,
                    "ndvi_start": 0.60,
                    "ndvi_end": 0.70,
                },
                "ripening": {"duration_days": 60, "ndvi_start": 0.70, "ndvi_end": 0.65},
            },
            "critical_periods": [
                {
                    "stage": "flowering",
                    "reason_ar": "التلقيح",
                    "reason_en": "Pollination",
                },
            ],
        },
        "grape": {
            "name_ar": "عنب",
            "season_length_days": 150,
            "stages": {
                "leaf_development": {
                    "duration_days": 40,
                    "ndvi_start": 0.30,
                    "ndvi_end": 0.50,
                },
                "flowering": {
                    "duration_days": 20,
                    "ndvi_start": 0.50,
                    "ndvi_end": 0.60,
                },
                "fruit_development": {
                    "duration_days": 60,
                    "ndvi_start": 0.60,
                    "ndvi_end": 0.70,
                },
                "ripening": {"duration_days": 30, "ndvi_start": 0.70, "ndvi_end": 0.60},
            },
            "critical_periods": [
                {
                    "stage": "fruit_development",
                    "reason_ar": "حجم وجودة الثمار",
                    "reason_en": "Berry size and quality",
                },
            ],
        },
    }

    def detect_current_stage(
        self,
        field_id: str,
        crop_type: str,
        ndvi_series: list[dict],  # [{date, value}]
        planting_date: date | None = None,
    ) -> PhenologyResult:
        """
        Detect current growth stage from NDVI pattern.

        Algorithm:
        1. Smooth NDVI time series (Savitzky-Golay filter)
        2. Detect Start of Season (SOS) - NDVI crosses emergence threshold
        3. Detect Peak of Season (POS) - Maximum NDVI
        4. Detect End of Season (EOS) - NDVI drops below senescence threshold
        5. Map to BBCH growth stage based on relative position

        Args:
            field_id: Field identifier
            crop_type: Crop type (must be in YEMEN_CROP_SEASONS)
            ndvi_series: List of {date, value} dictionaries
            planting_date: Optional planting date for better accuracy

        Returns:
            PhenologyResult with current stage and recommendations
        """
        if not ndvi_series:
            raise ValueError("NDVI series cannot be empty")

        crop_type = crop_type.lower()
        if crop_type not in self.YEMEN_CROP_SEASONS:
            raise ValueError(f"Unknown crop type: {crop_type}. Must be one of {list(self.YEMEN_CROP_SEASONS.keys())}")

        crop_params = self.YEMEN_CROP_SEASONS[crop_type]

        # Sort by date
        ndvi_series = sorted(
            ndvi_series,
            key=lambda x: x["date"] if isinstance(x["date"], date) else datetime.fromisoformat(x["date"]).date(),
        )

        # Smooth the series
        smoothed = self._smooth_ndvi_series([x["value"] for x in ndvi_series])
        ndvi_smooth = [{"date": ndvi_series[i]["date"], "value": smoothed[i]} for i in range(len(ndvi_series))]

        # Detect phenological events
        sos_date = self._detect_sos(ndvi_smooth, planting_date)
        pos_date = self._detect_pos(ndvi_smooth)
        eos_date = self._detect_eos(ndvi_smooth, pos_date)

        # Current values
        current_date = ndvi_series[-1]["date"]
        if isinstance(current_date, str):
            current_date = datetime.fromisoformat(current_date).date()
        current_ndvi = ndvi_series[-1]["value"]

        # Determine current stage
        stage, stage_start, days_in_stage = self._determine_stage(
            current_date, current_ndvi, sos_date, pos_date, eos_date, crop_params
        )

        # Predict next stage
        next_stage, days_to_next = self._predict_next_stage(stage, days_in_stage, crop_params)

        # Calculate season progress
        if sos_date and current_date:
            days_since_sos = (current_date - sos_date).days
            season_progress = min(100, (days_since_sos / crop_params["season_length_days"]) * 100)
        else:
            season_progress = 0

        # Estimate harvest date
        if sos_date:
            harvest_date = sos_date + timedelta(days=crop_params["season_length_days"])
        else:
            harvest_date = None

        # Calculate confidence
        confidence = self._calculate_confidence(ndvi_series, stage, crop_params)

        # Generate recommendations
        recommendations_ar, recommendations_en = self._get_stage_recommendations(
            crop_type, stage, days_to_next, current_ndvi, crop_params
        )

        return PhenologyResult(
            field_id=field_id,
            crop_type=crop_type,
            current_stage=stage,
            stage_start_date=stage_start,
            days_in_stage=days_in_stage,
            expected_next_stage=next_stage,
            days_to_next_stage=days_to_next,
            season_progress_percent=round(season_progress, 1),
            ndvi_at_detection=round(current_ndvi, 4),
            confidence=round(confidence, 2),
            recommendations_ar=recommendations_ar,
            recommendations_en=recommendations_en,
            sos_date=sos_date,
            pos_date=pos_date,
            eos_date=eos_date,
            estimated_harvest_date=harvest_date,
        )

    def get_phenology_timeline(self, field_id: str, crop_type: str, planting_date: date) -> PhenologyTimeline:
        """
        Generate expected phenology timeline for planning.

        Args:
            field_id: Field identifier
            crop_type: Crop type
            planting_date: Planned or actual planting date

        Returns:
            PhenologyTimeline with expected stage dates
        """
        crop_type = crop_type.lower()
        if crop_type not in self.YEMEN_CROP_SEASONS:
            raise ValueError(f"Unknown crop type: {crop_type}")

        crop_params = self.YEMEN_CROP_SEASONS[crop_type]

        stages = []
        current_date = planting_date

        for stage_name, stage_params in crop_params["stages"].items():
            duration = stage_params["duration_days"]
            end_date = current_date + timedelta(days=duration)

            stages.append(
                {
                    "stage": stage_name,
                    "stage_ar": self._stage_name_to_enum(stage_name).label_ar,
                    "stage_en": self._stage_name_to_enum(stage_name).label_en,
                    "start_date": current_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "duration_days": duration,
                    "ndvi_range": {
                        "min": stage_params["ndvi_start"],
                        "max": stage_params["ndvi_end"],
                    },
                }
            )

            current_date = end_date

        harvest_date = planting_date + timedelta(days=crop_params["season_length_days"])

        # Format critical periods
        critical_periods = []
        for cp in crop_params.get("critical_periods", []):
            # Find the stage dates
            stage_info = next((s for s in stages if s["stage"] == cp["stage"]), None)
            if stage_info:
                critical_periods.append(
                    {
                        "stage": cp["stage"],
                        "stage_ar": stage_info["stage_ar"],
                        "stage_en": stage_info["stage_en"],
                        "start_date": stage_info["start_date"],
                        "end_date": stage_info["end_date"],
                        "reason_ar": cp["reason_ar"],
                        "reason_en": cp["reason_en"],
                    }
                )

        return PhenologyTimeline(
            field_id=field_id,
            crop_type=crop_type,
            planting_date=planting_date,
            stages=stages,
            harvest_estimate=harvest_date,
            season_length_days=crop_params["season_length_days"],
            critical_periods=critical_periods,
        )

    def _smooth_ndvi_series(self, ndvi_values: list[float], window_size: int = 5) -> list[float]:
        """
        Apply simple moving average smoothing to remove noise.

        For production, could use Savitzky-Golay filter or Whittaker smoother.
        """
        if len(ndvi_values) < window_size:
            return ndvi_values

        smoothed = []
        half_window = window_size // 2

        for i in range(len(ndvi_values)):
            start = max(0, i - half_window)
            end = min(len(ndvi_values), i + half_window + 1)
            window = ndvi_values[start:end]
            smoothed.append(sum(window) / len(window))

        return smoothed

    def _detect_sos(self, ndvi_series: list[dict], planting_date: date | None = None) -> date | None:
        """
        Detect Start of Season (SOS).

        SOS is when NDVI crosses emergence threshold with sustained increase.
        """
        threshold = self.NDVI_THRESHOLDS["emergence"]

        # If planting date is known, search after it
        if planting_date:
            ndvi_series = [
                x
                for x in ndvi_series
                if (x["date"] if isinstance(x["date"], date) else datetime.fromisoformat(x["date"]).date())
                >= planting_date
            ]

        for i in range(len(ndvi_series) - 2):
            current = ndvi_series[i]["value"]
            next1 = ndvi_series[i + 1]["value"]
            next2 = ndvi_series[i + 2]["value"]

            # Check if NDVI crosses threshold with sustained increase
            if current < threshold <= next1 and next2 > next1:
                dt = ndvi_series[i + 1]["date"]
                return dt if isinstance(dt, date) else datetime.fromisoformat(dt).date()

        # Fallback: first time NDVI > threshold
        for point in ndvi_series:
            if point["value"] > threshold:
                dt = point["date"]
                return dt if isinstance(dt, date) else datetime.fromisoformat(dt).date()

        return None

    def _detect_pos(self, ndvi_series: list[dict]) -> date | None:
        """
        Detect Peak of Season (POS).

        POS is the date of maximum NDVI.
        """
        if not ndvi_series:
            return None

        max_point = max(ndvi_series, key=lambda x: x["value"])
        dt = max_point["date"]
        return dt if isinstance(dt, date) else datetime.fromisoformat(dt).date()

    def _detect_eos(self, ndvi_series: list[dict], pos_date: date | None) -> date | None:
        """
        Detect End of Season (EOS).

        EOS is when NDVI drops below harvest threshold after POS.
        """
        threshold = self.NDVI_THRESHOLDS["harvest_ready"]

        # Search after POS
        if pos_date:
            ndvi_series = [
                x
                for x in ndvi_series
                if (x["date"] if isinstance(x["date"], date) else datetime.fromisoformat(x["date"]).date()) > pos_date
            ]

        for point in ndvi_series:
            if point["value"] < threshold:
                dt = point["date"]
                return dt if isinstance(dt, date) else datetime.fromisoformat(dt).date()

        return None

    def _determine_stage(
        self,
        current_date: date,
        current_ndvi: float,
        sos_date: date | None,
        pos_date: date | None,
        eos_date: date | None,
        crop_params: dict,
    ) -> tuple[GrowthStage, date, int]:
        """
        Determine current growth stage based on dates and NDVI.

        Returns: (stage, stage_start_date, days_in_stage)
        """
        # If no SOS detected, assume bare soil or early germination
        if not sos_date:
            if current_ndvi < self.NDVI_THRESHOLDS["emergence"]:
                return GrowthStage.BARE_SOIL, current_date, 0
            else:
                return GrowthStage.GERMINATION, current_date, 0

        # After EOS
        if eos_date and current_date > eos_date:
            if current_ndvi < self.NDVI_THRESHOLDS["bare_soil"]:
                return GrowthStage.HARVESTED, eos_date, (current_date - eos_date).days
            else:
                return GrowthStage.SENESCENCE, eos_date, (current_date - eos_date).days

        # Calculate days since SOS
        days_since_sos = (current_date - sos_date).days

        # Map to stages based on cumulative duration
        cumulative_days = 0
        stage_start = sos_date

        for stage_name, stage_params in crop_params["stages"].items():
            duration = stage_params["duration_days"]
            cumulative_days += duration

            if days_since_sos < cumulative_days:
                # We're in this stage
                days_in_stage = days_since_sos - (cumulative_days - duration)
                return self._stage_name_to_enum(stage_name), stage_start, days_in_stage

            stage_start = sos_date + timedelta(days=cumulative_days)

        # Beyond all defined stages
        return GrowthStage.SENESCENCE, stage_start, (current_date - stage_start).days

    def _predict_next_stage(
        self, current_stage: GrowthStage, days_in_stage: int, crop_params: dict
    ) -> tuple[GrowthStage, int]:
        """
        Predict next growth stage and days remaining.

        Returns: (next_stage, days_to_next_stage)
        """
        stage_order = list(crop_params["stages"].keys())
        current_stage_name = current_stage.value

        # Find current stage in order
        try:
            current_idx = stage_order.index(current_stage_name)
        except ValueError:
            # Stage not in normal sequence
            if current_stage == GrowthStage.BARE_SOIL:
                return GrowthStage.GERMINATION, 7
            elif current_stage == GrowthStage.SENESCENCE:
                return GrowthStage.HARVESTED, 5
            else:
                return current_stage, 0

        # Get current stage duration
        current_duration = crop_params["stages"][current_stage_name]["duration_days"]
        days_remaining = max(0, current_duration - days_in_stage)

        # Next stage
        if current_idx + 1 < len(stage_order):
            next_stage_name = stage_order[current_idx + 1]
            next_stage = self._stage_name_to_enum(next_stage_name)
        else:
            next_stage = GrowthStage.HARVESTED

        return next_stage, days_remaining

    def _calculate_confidence(self, ndvi_series: list[dict], detected_stage: GrowthStage, crop_params: dict) -> float:
        """
        Calculate confidence in stage detection.

        Based on:
        - Number of observations
        - NDVI consistency with expected range
        - Temporal spacing of observations
        """
        if len(ndvi_series) < 3:
            return 0.5  # Low confidence with few observations

        current_ndvi = ndvi_series[-1]["value"]

        # Check if NDVI matches expected range for stage
        stage_name = detected_stage.value
        if stage_name in crop_params.get("stages", {}):
            expected_range = crop_params["stages"][stage_name]
            ndvi_min = expected_range["ndvi_start"]
            ndvi_max = expected_range["ndvi_end"]

            if ndvi_min <= current_ndvi <= ndvi_max:
                ndvi_match = 1.0
            else:
                # How far outside range?
                deviation = min(abs(current_ndvi - ndvi_min), abs(current_ndvi - ndvi_max))
                ndvi_match = max(0.3, 1.0 - deviation)
        else:
            ndvi_match = 0.6

        # More observations = higher confidence
        obs_score = min(1.0, len(ndvi_series) / 10)

        # Combine
        confidence = ndvi_match * 0.6 + obs_score * 0.4
        return min(0.95, max(0.4, confidence))

    def _get_stage_recommendations(
        self,
        crop_type: str,
        stage: GrowthStage,
        days_to_next: int,
        current_ndvi: float,
        crop_params: dict,
    ) -> tuple[list[str], list[str]]:
        """
        Get Arabic and English recommendations for current stage.

        Returns: (recommendations_ar, recommendations_en)
        """
        ar, en = [], []
        crop_name_ar = crop_params["name_ar"]
        stage_ar = stage.label_ar
        stage_en = stage.label_en

        # General stage info
        ar.append(f"🌱 المحصول ({crop_name_ar}) في مرحلة {stage_ar}")
        en.append(f"🌱 Crop ({crop_type}) is in {stage_en} stage")

        # Stage-specific recommendations
        stage_name = stage.value

        if stage == GrowthStage.BARE_SOIL:
            ar.append("📅 جهز الأرض للزراعة - حرث وتسوية")
            en.append("📅 Prepare land for planting - tillage and leveling")
            ar.append("💧 تأكد من توفر مياه الري")
            en.append("💧 Ensure irrigation water availability")

        elif stage == GrowthStage.GERMINATION:
            ar.append("💧 حافظ على رطوبة التربة - ري خفيف يومي")
            en.append("💧 Maintain soil moisture - light daily irrigation")
            ar.append("🔍 راقب ظهور البادرات")
            en.append("🔍 Monitor seedling emergence")

        elif stage == GrowthStage.EMERGENCE:
            ar.append("🌿 تأكد من كثافة النباتات المناسبة")
            en.append("🌿 Ensure proper plant density")
            ar.append("🦗 راقب الآفات المبكرة")
            en.append("🦗 Monitor for early pests")

        elif stage == GrowthStage.LEAF_DEVELOPMENT or stage == GrowthStage.TILLERING:
            ar.append("🥗 قم بالتسميد النيتروجيني لتعزيز النمو الخضري")
            en.append("🥗 Apply nitrogen fertilizer to boost vegetative growth")
            ar.append("💧 زد الري تدريجياً مع نمو النبات")
            en.append("💧 Gradually increase irrigation with plant growth")
            ar.append("🌾 راقب الأعشاب الضارة وقم بمكافحتها")
            en.append("🌾 Monitor and control weeds")

        elif stage == GrowthStage.FLOWERING:
            ar.append("💐 مرحلة حرجة - تجنب الإجهاد المائي")
            en.append("💐 Critical period - avoid water stress")
            ar.append("🐝 تأكد من وجود الملقحات إن أمكن")
            en.append("🐝 Ensure pollinators presence if applicable")
            ar.append("🌡️ تجنب درجات الحرارة المرتفعة جداً")
            en.append("🌡️ Avoid extreme heat stress")

        elif stage == GrowthStage.FRUIT_DEVELOPMENT:
            ar.append("🥗 قم بالتسميد المتوازن (NPK)")
            en.append("🥗 Apply balanced fertilization (NPK)")
            ar.append("💧 حافظ على ري منتظم ومتواصل")
            en.append("💧 Maintain regular and consistent irrigation")
            ar.append("🔍 راقب جودة الثمار")
            en.append("🔍 Monitor fruit quality")

        elif stage == GrowthStage.RIPENING:
            ar.append(f"⏱️ تحضير للحصاد خلال {days_to_next} يوم")
            en.append(f"⏱️ Prepare for harvest in {days_to_next} days")
            ar.append("💧 قلل الري تدريجياً")
            en.append("💧 Gradually reduce irrigation")
            ar.append("📊 راقب مؤشرات النضج")
            en.append("📊 Monitor maturity indicators")

        elif stage == GrowthStage.SENESCENCE:
            ar.append("✂️ الحصاد مستحق - خطط لجمع المحصول")
            en.append("✂️ Harvest due - plan crop collection")
            ar.append("🚜 جهز معدات الحصاد")
            en.append("🚜 Prepare harvesting equipment")

        elif stage == GrowthStage.HARVESTED:
            ar.append("📦 تخزين المحصول بشكل صحيح")
            en.append("📦 Store harvest properly")
            ar.append("🔄 خطط للموسم القادم")
            en.append("🔄 Plan for next season")

        # NDVI-based alerts
        if current_ndvi < 0.3 and stage in [
            GrowthStage.LEAF_DEVELOPMENT,
            GrowthStage.TILLERING,
            GrowthStage.FLOWERING,
        ]:
            ar.append("⚠️ NDVI منخفض - تحقق من صحة النباتات")
            en.append("⚠️ Low NDVI - check plant health")

        # Check critical periods
        for cp in crop_params.get("critical_periods", []):
            if cp["stage"] == stage_name:
                ar.append(f"⚠️ فترة حرجة: {cp['reason_ar']}")
                en.append(f"⚠️ Critical period: {cp['reason_en']}")

        return ar, en

    def _stage_name_to_enum(self, stage_name: str) -> GrowthStage:
        """Convert stage name string to GrowthStage enum"""
        mapping = {
            "germination": GrowthStage.GERMINATION,
            "emergence": GrowthStage.EMERGENCE,
            "leaf_development": GrowthStage.LEAF_DEVELOPMENT,
            "tillering": GrowthStage.TILLERING,
            "stem_elongation": GrowthStage.STEM_ELONGATION,
            "booting": GrowthStage.BOOTING,
            "flowering": GrowthStage.FLOWERING,
            "fruit_development": GrowthStage.FRUIT_DEVELOPMENT,
            "ripening": GrowthStage.RIPENING,
            "senescence": GrowthStage.SENESCENCE,
        }
        return mapping.get(stage_name, GrowthStage.LEAF_DEVELOPMENT)

    def get_supported_crops(self) -> list[dict[str, str]]:
        """Get list of supported crops"""
        return [
            {
                "id": crop_id,
                "name_ar": params["name_ar"],
                "name_en": crop_id.replace("_", " ").title(),
                "season_length_days": params["season_length_days"],
            }
            for crop_id, params in self.YEMEN_CROP_SEASONS.items()
        ]
