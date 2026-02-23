# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Data Quality Scoring - تسجيل جودة البيانات
=============================================
Score weather and observation inputs to gate calibration / assimilation.

Quality scores are used by CalibrationEngine to filter low-quality
observations (via ``min_quality_score``) and by AssimilationEngine
to weight the Kalman gain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class QualityLevel(StrEnum):
    """Coarse quality band. مستوى الجودة."""

    EXCELLENT = "excellent"  # score ≥ 0.9
    GOOD = "good"  # score ≥ 0.7
    FAIR = "fair"  # score ≥ 0.5
    POOR = "poor"  # score ≥ 0.25
    UNKNOWN = "unknown"  # score < 0.25 or not assessed


def _level_from_score(score: float) -> QualityLevel:
    if score >= 0.9:
        return QualityLevel.EXCELLENT
    if score >= 0.7:
        return QualityLevel.GOOD
    if score >= 0.5:
        return QualityLevel.FAIR
    if score >= 0.25:
        return QualityLevel.POOR
    return QualityLevel.UNKNOWN


@dataclass(frozen=True)
class WeatherQualityScore:
    """
    Quality assessment for a day's weather record.
    تقييم جودة سجل الطقس اليومي.

    Typical penalty reasons:
      - "missing_radiation"  – solar_radiation_mj_m2 is zero or absent
      - "tmax_lt_tmin"       – tmax < tmin
      - "implausible_rh"    – RH outside [5, 100]
      - "gap_filled"        – record was spatially interpolated
    """

    score: float  # 0..1 aggregate quality | الجودة الكلية
    level: QualityLevel
    reasons: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"WeatherQualityScore.score must be in [0, 1], got {self.score}")


@dataclass(frozen=True)
class ObservationQualityScore:
    """
    Quality assessment for a single field observation.
    تقييم جودة رصد ميداني واحد.

    Typical penalty reasons:
      - "high_cloud_cover"  – cloud pct > 50% (satellite imagery)
      - "stale_sensor"      – last reading > 6h old
      - "low_spatial_res"   – pixel > 30m
      - "manual_estimate"   – subjective visual estimate
    """

    score: float  # 0..1 | الجودة الكلية
    level: QualityLevel
    reasons: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"ObservationQualityScore.score must be in [0, 1], got {self.score}")


def score_weather(
    *,
    tmax_c: float | None,
    tmin_c: float | None,
    solar_radiation_mj_m2: float | None,
    relative_humidity_pct: float | None,
    gap_filled: bool = False,
) -> WeatherQualityScore:
    """
    Heuristic quality scorer for a daily weather record.
    مسجّل جودة تجريبي لسجل الطقس اليومي.
    """
    score = 1.0
    reasons: list[str] = []

    if tmax_c is None or tmin_c is None:
        score -= 0.4
        reasons.append("missing_temperature")
    elif tmax_c < tmin_c:
        score -= 0.3
        reasons.append("tmax_lt_tmin")

    if solar_radiation_mj_m2 is None or solar_radiation_mj_m2 <= 0.0:
        score -= 0.25
        reasons.append("missing_radiation")

    if relative_humidity_pct is not None and not (5.0 <= relative_humidity_pct <= 100.0):
        score -= 0.15
        reasons.append("implausible_rh")

    if gap_filled:
        score -= 0.10
        reasons.append("gap_filled")

    score = max(0.0, min(1.0, score))
    return WeatherQualityScore(
        score=score,
        level=_level_from_score(score),
        reasons=reasons,
    )


def score_observation(
    *,
    source: str,
    cloud_pct: float = 0.0,
    age_hours: float = 0.0,
    spatial_res_m: float = 10.0,
) -> ObservationQualityScore:
    """
    Heuristic quality scorer for a field observation.
    مسجّل جودة تجريبي لرصد ميداني.
    """
    score = 1.0
    reasons: list[str] = []

    if cloud_pct > 50.0:
        score -= 0.3
        reasons.append("high_cloud_cover")
    elif cloud_pct > 20.0:
        score -= 0.1
        reasons.append("moderate_cloud_cover")

    if age_hours > 48.0:
        score -= 0.3
        reasons.append("stale_sensor")
    elif age_hours > 6.0:
        score -= 0.1
        reasons.append("slightly_stale")

    if spatial_res_m > 30.0:
        score -= 0.15
        reasons.append("low_spatial_res")

    if source == "manual":
        score -= 0.15
        reasons.append("manual_estimate")

    score = max(0.0, min(1.0, score))
    return ObservationQualityScore(
        score=score,
        level=_level_from_score(score),
        reasons=reasons,
    )
