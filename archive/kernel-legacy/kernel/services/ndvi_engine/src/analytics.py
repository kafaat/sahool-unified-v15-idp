"""
SAHOOL NDVI Analytics
Time-series analysis, trends, and comparisons

Sprint 8: Trend detection, summary statistics, and anomaly detection
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from statistics import mean, stdev

from .models import NdviObservation

# ─────────────────────────────────────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class NdviSummary:
    """Summary statistics for NDVI time series"""

    count: int
    ndvi_mean: float
    ndvi_min: float
    ndvi_max: float
    ndvi_std: float | None
    confidence_mean: float
    trend: str  # rising, falling, stable, insufficient
    trend_slope: float | None
    date_range: tuple[date, date] | None

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "ndvi_mean": round(self.ndvi_mean, 4),
            "ndvi_min": round(self.ndvi_min, 4),
            "ndvi_max": round(self.ndvi_max, 4),
            "ndvi_std": round(self.ndvi_std, 4) if self.ndvi_std else None,
            "confidence_mean": round(self.confidence_mean, 4),
            "trend": self.trend,
            "trend_slope": round(self.trend_slope, 6) if self.trend_slope else None,
            "date_range": {
                "start": self.date_range[0].isoformat() if self.date_range else None,
                "end": self.date_range[1].isoformat() if self.date_range else None,
            },
        }


@dataclass(frozen=True)
class TrendAnalysis:
    """Detailed trend analysis result"""

    direction: str  # rising, falling, stable, volatile
    strength: str  # strong, moderate, weak
    slope: float  # Units per day
    r_squared: float  # Fit quality (0-1)
    change_pct: float  # Total change percentage
    message: str
    message_ar: str


@dataclass(frozen=True)
class Comparison:
    """Comparison between two time periods"""

    current_mean: float
    previous_mean: float
    change: float
    change_pct: float
    trend: str  # improved, declined, stable
    significance: str  # significant, marginal, none


# ─────────────────────────────────────────────────────────────────────────────
# Trend Detection
# ─────────────────────────────────────────────────────────────────────────────


def compute_trend(values: Sequence[float], threshold: float = 0.03) -> str:
    """
    Compute trend direction from a sequence of values.

    Simple approach: compare average of first two points vs last two points.

    Args:
        values: Sequence of NDVI values in chronological order
        threshold: Minimum change to consider significant

    Returns:
        Trend direction: "rising", "falling", "stable", or "insufficient"
    """
    if len(values) < 4:
        return "insufficient"

    first_avg = mean(values[:2])
    last_avg = mean(values[-2:])
    delta = last_avg - first_avg

    if delta > threshold:
        return "rising"
    elif delta < -threshold:
        return "falling"
    else:
        return "stable"


def compute_linear_trend(
    values: Sequence[float],
) -> tuple[float, float] | None:
    """
    Compute linear trend slope using simple linear regression.

    Args:
        values: Sequence of values (assumed equally spaced in time)

    Returns:
        Tuple of (slope, r_squared) or None if insufficient data
    """
    n = len(values)
    if n < 3:
        return None

    # Simple linear regression: y = mx + b
    # x = indices 0, 1, 2, ...
    x_mean = (n - 1) / 2
    y_mean = mean(values)

    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return None

    slope = numerator / denominator

    # Calculate R-squared
    y_pred = [slope * i + (y_mean - slope * x_mean) for i in range(n)]
    ss_res = sum((v - p) ** 2 for v, p in zip(values, y_pred, strict=False))
    ss_tot = sum((v - y_mean) ** 2 for v in values)

    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    return slope, r_squared


def analyze_trend(
    series: Sequence[NdviObservation],
) -> TrendAnalysis | None:
    """
    Perform detailed trend analysis on NDVI series.

    Args:
        series: Sequence of observations in chronological order

    Returns:
        TrendAnalysis or None if insufficient data
    """
    if len(series) < 4:
        return None

    values = [obs.ndvi_mean for obs in series]
    result = compute_linear_trend(values)

    if result is None:
        return None

    slope, r_squared = result

    # Determine direction
    if abs(slope) < 0.001:
        direction = "stable"
    elif slope > 0:
        direction = "rising"
    else:
        direction = "falling"

    # Check for volatility
    if len(values) >= 5:
        val_std = stdev(values)
        if val_std > 0.15:
            direction = "volatile"

    # Determine strength
    if r_squared >= 0.7:
        strength = "strong"
    elif r_squared >= 0.4:
        strength = "moderate"
    else:
        strength = "weak"

    # Calculate change percentage
    first_val = values[0]
    last_val = values[-1]
    change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0

    # Generate messages
    messages = _generate_trend_messages(direction, strength, change_pct)

    return TrendAnalysis(
        direction=direction,
        strength=strength,
        slope=slope,
        r_squared=r_squared,
        change_pct=change_pct,
        message=messages[0],
        message_ar=messages[1],
    )


def _generate_trend_messages(
    direction: str,
    strength: str,
    change_pct: float,
) -> tuple[str, str]:
    """Generate human-readable trend messages"""
    change_str = f"{abs(change_pct):.1f}%"

    if direction == "rising":
        en = f"Vegetation health is improving ({strength} trend, +{change_str})"
        ar = f"صحة النباتات تتحسن (اتجاه {_strength_ar(strength)}، +{change_str})"
    elif direction == "falling":
        en = f"Vegetation health is declining ({strength} trend, -{change_str})"
        ar = f"صحة النباتات تتراجع (اتجاه {_strength_ar(strength)}، -{change_str})"
    elif direction == "volatile":
        en = "Vegetation health is unstable (high variability)"
        ar = "صحة النباتات غير مستقرة (تقلبات عالية)"
    else:
        en = "Vegetation health is stable"
        ar = "صحة النباتات مستقرة"

    return en, ar


def _strength_ar(strength: str) -> str:
    return {"strong": "قوي", "moderate": "متوسط", "weak": "ضعيف"}.get(
        strength, strength
    )


# ─────────────────────────────────────────────────────────────────────────────
# Summary Statistics
# ─────────────────────────────────────────────────────────────────────────────


def summarize(series: Sequence[NdviObservation]) -> NdviSummary:
    """
    Compute summary statistics for NDVI time series.

    Args:
        series: Sequence of observations

    Returns:
        NdviSummary with statistics
    """
    if not series:
        return NdviSummary(
            count=0,
            ndvi_mean=0.0,
            ndvi_min=0.0,
            ndvi_max=0.0,
            ndvi_std=None,
            confidence_mean=0.0,
            trend="insufficient",
            trend_slope=None,
            date_range=None,
        )

    ndvi_values = [obs.ndvi_mean for obs in series]
    confidence_values = [obs.confidence for obs in series]

    # Calculate std if enough data
    ndvi_std = stdev(ndvi_values) if len(ndvi_values) >= 2 else None

    # Calculate trend
    trend = compute_trend(ndvi_values)
    trend_result = compute_linear_trend(ndvi_values)
    trend_slope = trend_result[0] if trend_result else None

    # Get date range
    dates = [obs.obs_date for obs in series]
    date_range = (min(dates), max(dates)) if dates else None

    return NdviSummary(
        count=len(series),
        ndvi_mean=mean(ndvi_values),
        ndvi_min=min(ndvi_values),
        ndvi_max=max(ndvi_values),
        ndvi_std=ndvi_std,
        confidence_mean=mean(confidence_values),
        trend=trend,
        trend_slope=trend_slope,
        date_range=date_range,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Period Comparison
# ─────────────────────────────────────────────────────────────────────────────


def compare_periods(
    current: Sequence[NdviObservation],
    previous: Sequence[NdviObservation],
    significance_threshold: float = 0.05,
) -> Comparison | None:
    """
    Compare NDVI between two time periods.

    Useful for year-over-year or month-over-month comparisons.

    Args:
        current: Current period observations
        previous: Previous period observations
        significance_threshold: Minimum change to consider significant

    Returns:
        Comparison result or None if insufficient data
    """
    if not current or not previous:
        return None

    current_mean = mean(obs.ndvi_mean for obs in current)
    previous_mean = mean(obs.ndvi_mean for obs in previous)

    change = current_mean - previous_mean
    change_pct = (change / previous_mean * 100) if previous_mean != 0 else 0

    # Determine trend
    if abs(change) < significance_threshold:
        trend = "stable"
        significance = "none"
    elif change > 0:
        trend = "improved"
        significance = "significant" if change > 0.1 else "marginal"
    else:
        trend = "declined"
        significance = "significant" if change < -0.1 else "marginal"

    return Comparison(
        current_mean=current_mean,
        previous_mean=previous_mean,
        change=change,
        change_pct=change_pct,
        trend=trend,
        significance=significance,
    )


def compare_to_historical_mean(
    current_value: float,
    historical_mean: float,
    historical_std: float,
) -> dict:
    """
    Compare current NDVI to historical statistics.

    Args:
        current_value: Current NDVI value
        historical_mean: Historical mean
        historical_std: Historical standard deviation

    Returns:
        Comparison dictionary with z-score and interpretation
    """
    if historical_std == 0:
        z_score = 0.0
    else:
        z_score = (current_value - historical_mean) / historical_std

    deviation_pct = (
        ((current_value - historical_mean) / historical_mean * 100)
        if historical_mean != 0
        else 0
    )

    # Interpret z-score
    if abs(z_score) < 1:
        status = "normal"
        status_ar = "طبيعي"
    elif abs(z_score) < 2:
        status = "above_normal" if z_score > 0 else "below_normal"
        status_ar = "أعلى من المعتاد" if z_score > 0 else "أقل من المعتاد"
    else:
        status = "significantly_above" if z_score > 0 else "significantly_below"
        status_ar = "أعلى بكثير من المعتاد" if z_score > 0 else "أقل بكثير من المعتاد"

    return {
        "current_value": current_value,
        "historical_mean": historical_mean,
        "z_score": round(z_score, 2),
        "deviation_pct": round(deviation_pct, 1),
        "status": status,
        "status_ar": status_ar,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Seasonal Analysis
# ─────────────────────────────────────────────────────────────────────────────


def get_seasonal_baseline(
    series: Sequence[NdviObservation],
    target_month: int,
) -> dict | None:
    """
    Calculate baseline statistics for a specific month across years.

    Args:
        series: Multi-year observation series
        target_month: Month (1-12) to analyze

    Returns:
        Baseline statistics or None if insufficient data
    """
    monthly_values = [
        obs.ndvi_mean for obs in series if obs.obs_date.month == target_month
    ]

    if len(monthly_values) < 3:
        return None

    return {
        "month": target_month,
        "sample_size": len(monthly_values),
        "mean": mean(monthly_values),
        "std": stdev(monthly_values) if len(monthly_values) >= 2 else None,
        "min": min(monthly_values),
        "max": max(monthly_values),
    }
