"""
SAHOOL NDVI Confidence Score
Computes confidence score based on data quality factors

Sprint 8: Configurable confidence scoring
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceWeights:
    """
    Configurable weights for confidence score calculation.

    Each weight determines how much that factor affects the final score.
    Sum of weights should be <= 1.0 for interpretable results.
    """

    cloud_penalty: float = 0.55  # Heavy penalty for cloud cover
    age_penalty: float = 0.35  # Penalty for old data
    missing_pctl_penalty: float = 0.10  # Penalty for missing percentiles

    def __post_init__(self):
        total = self.cloud_penalty + self.age_penalty + self.missing_pctl_penalty
        if total > 1.0:
            raise ValueError(f"Total weights ({total}) exceed 1.0")


# Default weights used across the system
DEFAULT_WEIGHTS = ConfidenceWeights()


def clamp01(x: float) -> float:
    """Clamp value to [0, 1] range"""
    return max(0.0, min(1.0, x))


def confidence_score(
    *,
    cloud_coverage: float,
    age_days: int,
    has_percentiles: bool = True,
    has_std: bool = True,
    pixel_count: int | None = None,
    min_pixels: int = 100,
    weights: ConfidenceWeights = DEFAULT_WEIGHTS,
) -> float:
    """
    Calculate confidence score for an NDVI observation.

    The score represents how reliable the NDVI reading is, based on:
    - Cloud coverage (higher cloud = lower confidence)
    - Data age (older data = lower confidence)
    - Data completeness (missing percentiles/std = lower confidence)
    - Pixel count (too few pixels = lower confidence)

    Args:
        cloud_coverage: Cloud coverage fraction (0.0 to 1.0)
        age_days: Days since observation
        has_percentiles: Whether P10/P90 are available
        has_std: Whether standard deviation is available
        pixel_count: Number of valid pixels (optional)
        min_pixels: Minimum acceptable pixel count
        weights: Configurable weight factors

    Returns:
        Confidence score in [0.0, 1.0] range
        - 1.0 = Perfect confidence
        - 0.0 = No confidence
    """
    score = 1.0

    # Cloud penalty: higher cloud coverage = lower confidence
    cloud = clamp01(cloud_coverage)
    score -= weights.cloud_penalty * cloud

    # Age penalty: older data = lower confidence
    # Linear decay from 0 days (no penalty) to 14 days (full penalty)
    age = max(age_days, 0)
    age_factor = min(age / 14.0, 1.0)
    score -= weights.age_penalty * age_factor

    # Completeness penalty: missing statistics = lower confidence
    if not has_percentiles:
        score -= weights.missing_pctl_penalty * 0.6
    if not has_std:
        score -= weights.missing_pctl_penalty * 0.4

    # Pixel count penalty (if provided)
    if pixel_count is not None and pixel_count < min_pixels:
        pixel_factor = pixel_count / min_pixels
        score *= pixel_factor

    return clamp01(score)


def confidence_grade(score: float) -> tuple[str, str]:
    """
    Convert confidence score to human-readable grade.

    Args:
        score: Confidence score (0.0 to 1.0)

    Returns:
        Tuple of (grade_en, grade_ar)
    """
    if score >= 0.9:
        return ("excellent", "ممتاز")
    elif score >= 0.75:
        return ("good", "جيد")
    elif score >= 0.5:
        return ("moderate", "متوسط")
    elif score >= 0.25:
        return ("low", "منخفض")
    else:
        return ("poor", "ضعيف")


def should_use_observation(
    confidence: float,
    min_confidence: float = 0.3,
) -> bool:
    """
    Determine if an observation should be used in analysis.

    Args:
        confidence: Observation confidence score
        min_confidence: Minimum acceptable confidence

    Returns:
        True if observation meets quality threshold
    """
    return confidence >= min_confidence


def weighted_average_ndvi(
    observations: list[tuple[float, float]],
) -> float | None:
    """
    Calculate weighted average NDVI using confidence scores.

    Args:
        observations: List of (ndvi_value, confidence_score) tuples

    Returns:
        Weighted average NDVI, or None if no valid observations
    """
    if not observations:
        return None

    # Filter out low confidence observations
    valid = [(ndvi, conf) for ndvi, conf in observations if conf > 0.1]

    if not valid:
        return None

    total_weight = sum(conf for _, conf in valid)
    if total_weight == 0:
        return None

    weighted_sum = sum(ndvi * conf for ndvi, conf in valid)
    return weighted_sum / total_weight
