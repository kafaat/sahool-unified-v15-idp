"""
Auto Crop Classifier — مصنّف المحاصيل التلقائي
Classifies crop types from satellite NDVI time-series without user input.

Approach: Uses NDVI temporal signature matching against known crop profiles.
Each crop has a distinctive growth curve (phenological signature).

Inspired by OneSoil (F1=0.96 for 12 crops) and EOS Data Analytics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CropSignature:
    """Known phenological NDVI signature for a crop type.

    توقيع النمو المعروف لنوع المحصول بناءً على مؤشر الغطاء النباتي
    """

    crop_type: str
    crop_name_ar: str
    peak_ndvi: float
    peak_month: int  # 1-12
    growing_season_months: list[int]
    ndvi_profile: list[float]  # 12 monthly values (Jan-Dec)
    min_area_ha: float
    common_regions: list[str]  # Yemen governorates


@dataclass
class ClassificationResult:
    """Result of crop type classification.

    نتيجة تصنيف نوع المحصول
    """

    crop_type: str
    crop_name_ar: str
    confidence: float  # 0-1
    match_score: float
    alternative_crops: list[tuple[str, float]] = field(default_factory=list)  # (crop, confidence)
    season: str = "unknown"  # "winter" | "summer" | "year-round" | "unknown"
    method: str = "correlation"


# ---------------------------------------------------------------------------
# Yemen-specific crop profiles
# ---------------------------------------------------------------------------

_YEMEN_PROFILES: list[CropSignature] = [
    CropSignature(
        crop_type="wheat",
        crop_name_ar="قمح",
        peak_ndvi=0.65,
        peak_month=1,  # Jan
        growing_season_months=[10, 11, 12, 1, 2, 3],
        ndvi_profile=[
            0.65, 0.55, 0.35, 0.15, 0.10, 0.10,
            0.10, 0.10, 0.12, 0.25, 0.45, 0.60,
        ],
        min_area_ha=0.5,
        common_regions=["Ibb", "Dhamar", "Sana'a", "Amran", "Al Bayda"],
    ),
    CropSignature(
        crop_type="barley",
        crop_name_ar="شعير",
        peak_ndvi=0.55,
        peak_month=12,  # Dec
        growing_season_months=[9, 10, 11, 12, 1, 2],
        ndvi_profile=[
            0.50, 0.35, 0.18, 0.10, 0.10, 0.10,
            0.10, 0.10, 0.15, 0.30, 0.45, 0.55,
        ],
        min_area_ha=0.3,
        common_regions=["Dhamar", "Sana'a", "Amran", "Sa'dah", "Hajjah"],
    ),
    CropSignature(
        crop_type="sorghum",
        crop_name_ar="ذرة رفيعة",
        peak_ndvi=0.70,
        peak_month=9,  # Sep
        growing_season_months=[6, 7, 8, 9, 10, 11],
        ndvi_profile=[
            0.10, 0.10, 0.10, 0.10, 0.12, 0.15,
            0.30, 0.50, 0.70, 0.65, 0.40, 0.15,
        ],
        min_area_ha=0.3,
        common_regions=["Ibb", "Taiz", "Dhamar", "Al Bayda", "Al Hudaydah"],
    ),
    CropSignature(
        crop_type="qat",
        crop_name_ar="قات",
        peak_ndvi=0.75,
        peak_month=8,  # Aug (peak flush)
        growing_season_months=list(range(1, 13)),
        ndvi_profile=[
            0.60, 0.60, 0.62, 0.65, 0.68, 0.70,
            0.73, 0.75, 0.73, 0.70, 0.65, 0.62,
        ],
        min_area_ha=0.1,
        common_regions=["Sana'a", "Ibb", "Taiz", "Dhamar", "Sa'dah"],
    ),
    CropSignature(
        crop_type="date_palm",
        crop_name_ar="نخيل",
        peak_ndvi=0.45,
        peak_month=7,  # Jul
        growing_season_months=list(range(1, 13)),
        ndvi_profile=[
            0.32, 0.33, 0.35, 0.38, 0.40, 0.43,
            0.45, 0.44, 0.42, 0.40, 0.36, 0.33,
        ],
        min_area_ha=0.2,
        common_regions=["Hadramaut", "Shabwah", "Al Mahra", "Al Hudaydah", "Lahij"],
    ),
    CropSignature(
        crop_type="coffee",
        crop_name_ar="بن",
        peak_ndvi=0.65,
        peak_month=9,  # Sep
        growing_season_months=list(range(1, 13)),
        ndvi_profile=[
            0.52, 0.50, 0.52, 0.55, 0.58, 0.60,
            0.62, 0.63, 0.65, 0.62, 0.58, 0.54,
        ],
        min_area_ha=0.2,
        common_regions=["Ibb", "Taiz", "Raymah", "Al Mahwit", "Haraz"],
    ),
    CropSignature(
        crop_type="tomato",
        crop_name_ar="طماطم",
        peak_ndvi=0.60,
        peak_month=5,  # May
        growing_season_months=[2, 3, 4, 5, 6, 7],
        ndvi_profile=[
            0.10, 0.20, 0.35, 0.50, 0.60, 0.55,
            0.40, 0.15, 0.10, 0.10, 0.10, 0.10,
        ],
        min_area_ha=0.1,
        common_regions=["Al Hudaydah", "Lahij", "Abyan", "Taiz", "Ibb"],
    ),
    CropSignature(
        crop_type="onion",
        crop_name_ar="بصل",
        peak_ndvi=0.45,
        peak_month=4,  # Apr
        growing_season_months=[1, 2, 3, 4, 5],
        ndvi_profile=[
            0.20, 0.30, 0.40, 0.45, 0.38, 0.15,
            0.10, 0.10, 0.10, 0.10, 0.10, 0.12,
        ],
        min_area_ha=0.1,
        common_regions=["Al Hudaydah", "Dhamar", "Ibb", "Lahij", "Abyan"],
    ),
    CropSignature(
        crop_type="banana",
        crop_name_ar="موز",
        peak_ndvi=0.75,
        peak_month=8,  # Aug
        growing_season_months=list(range(1, 13)),
        ndvi_profile=[
            0.60, 0.62, 0.65, 0.68, 0.70, 0.72,
            0.74, 0.75, 0.73, 0.70, 0.65, 0.62,
        ],
        min_area_ha=0.2,
        common_regions=["Al Hudaydah", "Lahij", "Abyan", "Hadramaut"],
    ),
    CropSignature(
        crop_type="mango",
        crop_name_ar="مانجو",
        peak_ndvi=0.65,
        peak_month=7,  # Jul
        growing_season_months=[4, 5, 6, 7, 8, 9],
        ndvi_profile=[
            0.40, 0.40, 0.42, 0.48, 0.55, 0.62,
            0.65, 0.60, 0.50, 0.42, 0.40, 0.40,
        ],
        min_area_ha=0.3,
        common_regions=["Al Hudaydah", "Lahij", "Abyan", "Hadramaut"],
    ),
    CropSignature(
        crop_type="sesame",
        crop_name_ar="سمسم",
        peak_ndvi=0.50,
        peak_month=8,  # Aug
        growing_season_months=[6, 7, 8, 9, 10],
        ndvi_profile=[
            0.10, 0.10, 0.10, 0.10, 0.10, 0.12,
            0.25, 0.45, 0.50, 0.35, 0.15, 0.10,
        ],
        min_area_ha=0.3,
        common_regions=["Al Hudaydah", "Hajjah", "Lahij", "Abyan"],
    ),
    CropSignature(
        crop_type="cotton",
        crop_name_ar="قطن",
        peak_ndvi=0.60,
        peak_month=9,  # Sep
        growing_season_months=[5, 6, 7, 8, 9, 10, 11],
        ndvi_profile=[
            0.10, 0.10, 0.10, 0.10, 0.15, 0.25,
            0.40, 0.55, 0.60, 0.55, 0.30, 0.12,
        ],
        min_area_ha=0.5,
        common_regions=["Abyan", "Lahij", "Al Hudaydah", "Hadramaut"],
    ),
]

_WINTER_MONTHS = {10, 11, 12, 1, 2, 3}
_SUMMER_MONTHS = {4, 5, 6, 7, 8, 9}


def _season_for_months(months: list[int]) -> str:
    """Determine season label from a growing-season month list."""
    month_set = set(months)
    if month_set == set(range(1, 13)):
        return "year-round"
    winter_overlap = len(month_set & _WINTER_MONTHS)
    summer_overlap = len(month_set & _SUMMER_MONTHS)
    if winter_overlap > summer_overlap:
        return "winter"
    if summer_overlap > winter_overlap:
        return "summer"
    return "year-round"


def _pearson_correlation(x: list[float], y: list[float]) -> float:
    """Compute Pearson correlation coefficient between two equal-length sequences.

    Returns 0.0 when standard deviation of either sequence is zero.
    """
    n = len(x)
    if n == 0:
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

    if std_x == 0.0 or std_y == 0.0:
        return 0.0

    return cov / (std_x * std_y)


def _interpolate_to_monthly(ndvi_timeseries: list[float], months: list[int]) -> list[float]:
    """Map sparse (value, month) pairs onto a full 12-month array.

    Months not covered by observations are linearly interpolated from their
    neighbours.  If only one observation exists, it is broadcast to all months.
    """
    if len(ndvi_timeseries) != len(months):
        raise ValueError(
            f"ndvi_timeseries length ({len(ndvi_timeseries)}) must equal "
            f"months length ({len(months)})"
        )

    monthly: dict[int, list[float]] = {}
    for val, m in zip(ndvi_timeseries, months):
        monthly.setdefault(m, []).append(val)

    # Average duplicate months
    averaged: dict[int, float] = {m: sum(v) / len(v) for m, v in monthly.items()}

    if not averaged:
        return [0.0] * 12

    # Build sorted list of known (month_index, value) for interpolation
    known = sorted(averaged.items())

    result = [0.0] * 12
    for month_idx in range(1, 13):
        if month_idx in averaged:
            result[month_idx - 1] = averaged[month_idx]
        else:
            # Linear interpolation between nearest known months
            lower = upper = None
            for m, v in known:
                if m <= month_idx:
                    lower = (m, v)
            for m, v in known:
                if m >= month_idx:
                    upper = (m, v)
                    break
            if lower is None and upper is not None:
                result[month_idx - 1] = upper[1]
            elif upper is None and lower is not None:
                result[month_idx - 1] = lower[1]
            elif lower is not None and upper is not None:
                if lower[0] == upper[0]:
                    result[month_idx - 1] = lower[1]
                else:
                    frac = (month_idx - lower[0]) / (upper[0] - lower[0])
                    result[month_idx - 1] = lower[1] + frac * (upper[1] - lower[1])

    return result


class CropClassifier:
    """Classify crop types from NDVI time-series using phenological signature matching.

    مصنّف المحاصيل التلقائي — يحدد نوع المحصول من السلسلة الزمنية لمؤشر NDVI
    باستخدام مطابقة التوقيع الفينولوجي.

    Example::

        classifier = CropClassifier()
        result = classifier.classify(
            ndvi_timeseries=[0.12, 0.25, 0.45, 0.60, 0.65, 0.55, 0.35, 0.15],
            months=[10, 11, 12, 1, 2, 3, 4, 5],
        )
        print(result.crop_type)      # "wheat"
        print(result.crop_name_ar)   # "قمح"
        print(result.confidence)     # 0.93
    """

    HIGH_CONFIDENCE_THRESHOLD = 0.7
    MODERATE_CONFIDENCE_THRESHOLD = 0.4
    MAX_ALTERNATIVES = 3

    def __init__(self, profiles: list[CropSignature] | None = None) -> None:
        self._profiles = list(profiles) if profiles is not None else list(_YEMEN_PROFILES)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(
        self,
        ndvi_timeseries: list[float],
        months: list[int],
    ) -> ClassificationResult:
        """Classify crop type from an NDVI time-series.

        تصنيف نوع المحصول من السلسلة الزمنية لمؤشر NDVI

        Args:
            ndvi_timeseries: Observed NDVI values (0-1 range).
            months: Corresponding month numbers (1-12) for each observation.

        Returns:
            ClassificationResult with best-matching crop and alternatives.

        Raises:
            ValueError: If inputs are empty or have mismatched lengths.
        """
        if not ndvi_timeseries or not months:
            raise ValueError("ndvi_timeseries and months must not be empty")

        monthly_values = _interpolate_to_monthly(ndvi_timeseries, months)

        scores: list[tuple[CropSignature, float]] = []
        for profile in self._profiles:
            corr = _pearson_correlation(monthly_values, profile.ndvi_profile)
            # Clamp to [0, 1] — negative correlation means poor match
            score = max(0.0, corr)
            scores.append((profile, score))

        scores.sort(key=lambda t: t[1], reverse=True)

        best_profile, best_score = scores[0]
        confidence = self._score_to_confidence(best_score)

        alternatives: list[tuple[str, float]] = []
        for profile, score in scores[1 : 1 + self.MAX_ALTERNATIVES]:
            alt_confidence = self._score_to_confidence(score)
            if alt_confidence > 0.0:
                alternatives.append((profile.crop_type, round(alt_confidence, 3)))

        return ClassificationResult(
            crop_type=best_profile.crop_type,
            crop_name_ar=best_profile.crop_name_ar,
            confidence=round(confidence, 3),
            match_score=round(best_score, 4),
            alternative_crops=alternatives,
            season=_season_for_months(best_profile.growing_season_months),
            method="correlation",
        )

    def classify_from_peak(
        self,
        peak_ndvi: float,
        peak_month: int,
    ) -> ClassificationResult:
        """Quick classification from a single peak NDVI observation.

        تصنيف سريع من ملاحظة واحدة لقمة مؤشر NDVI

        Args:
            peak_ndvi: Observed peak NDVI value.
            peak_month: Month (1-12) when the peak was observed.

        Returns:
            ClassificationResult with best match and alternatives.
        """
        if not 1 <= peak_month <= 12:
            raise ValueError(f"peak_month must be 1-12, got {peak_month}")
        if not 0.0 <= peak_ndvi <= 1.0:
            raise ValueError(f"peak_ndvi must be 0-1, got {peak_ndvi}")

        scores: list[tuple[CropSignature, float]] = []
        for profile in self._profiles:
            # Distance in months on a circular calendar
            month_dist = min(
                abs(peak_month - profile.peak_month),
                12 - abs(peak_month - profile.peak_month),
            )
            month_score = max(0.0, 1.0 - month_dist / 6.0)

            ndvi_diff = abs(peak_ndvi - profile.peak_ndvi)
            ndvi_score = max(0.0, 1.0 - ndvi_diff / 0.5)

            combined = 0.6 * month_score + 0.4 * ndvi_score
            scores.append((profile, combined))

        scores.sort(key=lambda t: t[1], reverse=True)

        best_profile, best_score = scores[0]
        confidence = self._score_to_confidence(best_score)

        alternatives: list[tuple[str, float]] = []
        for profile, score in scores[1 : 1 + self.MAX_ALTERNATIVES]:
            alt_confidence = self._score_to_confidence(score)
            if alt_confidence > 0.0:
                alternatives.append((profile.crop_type, round(alt_confidence, 3)))

        return ClassificationResult(
            crop_type=best_profile.crop_type,
            crop_name_ar=best_profile.crop_name_ar,
            confidence=round(confidence, 3),
            match_score=round(best_score, 4),
            alternative_crops=alternatives,
            season=_season_for_months(best_profile.growing_season_months),
            method="peak_matching",
        )

    def get_all_profiles(self) -> list[CropSignature]:
        """Return all registered crop phenological profiles.

        إرجاع جميع التوقيعات الفينولوجية المسجلة للمحاصيل
        """
        return list(self._profiles)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _score_to_confidence(self, score: float) -> float:
        """Convert a raw match score (0-1) to a calibrated confidence value."""
        if score >= self.HIGH_CONFIDENCE_THRESHOLD:
            # High-confidence band: map [0.7, 1.0] -> [0.70, 1.0]
            return 0.70 + 0.30 * ((score - 0.70) / 0.30)
        if score >= self.MODERATE_CONFIDENCE_THRESHOLD:
            # Moderate band: map [0.4, 0.7] -> [0.30, 0.70]
            return 0.30 + 0.40 * ((score - 0.40) / 0.30)
        if score > 0.0:
            # Low band: map (0, 0.4] -> (0, 0.30]
            return 0.30 * (score / 0.40)
        return 0.0
