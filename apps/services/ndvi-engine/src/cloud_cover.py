"""
SAHOOL Cloud Cover Detection
Generic cloud coverage estimation utilities

Sprint 8: Provider-agnostic cloud detection
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import IntEnum


class SCLClass(IntEnum):
    """
    Sentinel-2 Scene Classification Layer (SCL) classes.

    Used for cloud masking in Sentinel-2 imagery.
    """

    NO_DATA = 0
    SATURATED_DEFECTIVE = 1
    DARK_AREA_SHADOW = 2
    CLOUD_SHADOW = 3
    VEGETATION = 4
    NOT_VEGETATED = 5
    WATER = 6
    UNCLASSIFIED = 7
    CLOUD_MEDIUM_PROB = 8
    CLOUD_HIGH_PROB = 9
    THIN_CIRRUS = 10
    SNOW_ICE = 11


# SCL classes considered as cloud/unusable
CLOUD_CLASSES = {
    SCLClass.CLOUD_SHADOW,
    SCLClass.CLOUD_MEDIUM_PROB,
    SCLClass.CLOUD_HIGH_PROB,
    SCLClass.THIN_CIRRUS,
}

UNUSABLE_CLASSES = {
    SCLClass.NO_DATA,
    SCLClass.SATURATED_DEFECTIVE,
    SCLClass.CLOUD_SHADOW,
    SCLClass.CLOUD_MEDIUM_PROB,
    SCLClass.CLOUD_HIGH_PROB,
    SCLClass.THIN_CIRRUS,
    SCLClass.SNOW_ICE,
}


@dataclass
class CloudCoverResult:
    """Result of cloud coverage estimation"""

    cloud_fraction: float  # 0.0 to 1.0
    usable_fraction: float  # Fraction of usable pixels
    total_pixels: int
    cloud_pixels: int
    usable_pixels: int


def estimate_cloud_coverage_from_mask(
    mask_values: Sequence[int],
    cloud_value: int = 1,
) -> float:
    """
    Estimate cloud coverage from a binary mask.

    Generic approach for any provider that supplies a binary cloud mask.

    Args:
        mask_values: List/array of pixel classifications (0=clear, 1=cloud)
        cloud_value: Value representing cloud pixels

    Returns:
        Cloud coverage fraction (0.0 to 1.0)
    """
    if not mask_values:
        return 0.0

    cloud_count = sum(1 for v in mask_values if v == cloud_value)
    return cloud_count / len(mask_values)


def estimate_cloud_coverage_from_scl(
    scl_values: Sequence[int],
) -> CloudCoverResult:
    """
    Estimate cloud coverage from Sentinel-2 SCL band.

    Args:
        scl_values: List/array of SCL class values

    Returns:
        CloudCoverResult with detailed statistics
    """
    if not scl_values:
        return CloudCoverResult(
            cloud_fraction=0.0,
            usable_fraction=0.0,
            total_pixels=0,
            cloud_pixels=0,
            usable_pixels=0,
        )

    total = len(scl_values)
    cloud_pixels = sum(1 for v in scl_values if v in CLOUD_CLASSES)
    unusable_pixels = sum(1 for v in scl_values if v in UNUSABLE_CLASSES)
    usable_pixels = total - unusable_pixels

    return CloudCoverResult(
        cloud_fraction=cloud_pixels / total if total > 0 else 0.0,
        usable_fraction=usable_pixels / total if total > 0 else 0.0,
        total_pixels=total,
        cloud_pixels=cloud_pixels,
        usable_pixels=usable_pixels,
    )


def estimate_cloud_coverage_from_qa(
    qa_values: Sequence[int],
    cloud_bit: int = 10,
    cirrus_bit: int = 11,
) -> float:
    """
    Estimate cloud coverage from QA60 band (Sentinel-2 / Landsat style).

    Args:
        qa_values: List/array of QA band values
        cloud_bit: Bit position for cloud flag (default: 10 for Sentinel-2)
        cirrus_bit: Bit position for cirrus flag (default: 11 for Sentinel-2)

    Returns:
        Cloud coverage fraction (0.0 to 1.0)
    """
    if not qa_values:
        return 0.0

    cloud_mask = 1 << cloud_bit
    cirrus_mask = 1 << cirrus_bit
    combined_mask = cloud_mask | cirrus_mask

    cloud_count = sum(1 for v in qa_values if (v & combined_mask) != 0)
    return cloud_count / len(qa_values)


def is_scene_usable(
    cloud_coverage: float,
    max_cloud: float = 0.3,
    min_usable: float = 0.5,
    usable_fraction: float | None = None,
) -> bool:
    """
    Determine if a scene is usable for NDVI analysis.

    Args:
        cloud_coverage: Cloud coverage fraction
        max_cloud: Maximum acceptable cloud coverage
        min_usable: Minimum acceptable usable pixel fraction
        usable_fraction: Usable pixel fraction (if available)

    Returns:
        True if scene meets quality criteria
    """
    if cloud_coverage > max_cloud:
        return False

    return not (usable_fraction is not None and usable_fraction < min_usable)


def cloud_coverage_grade(coverage: float) -> tuple[str, str]:
    """
    Convert cloud coverage to human-readable grade.

    Args:
        coverage: Cloud coverage fraction (0.0 to 1.0)

    Returns:
        Tuple of (grade_en, grade_ar)
    """
    if coverage <= 0.1:
        return ("clear", "صافي")
    elif coverage <= 0.3:
        return ("mostly_clear", "صافي جزئياً")
    elif coverage <= 0.5:
        return ("partly_cloudy", "غائم جزئياً")
    elif coverage <= 0.7:
        return ("mostly_cloudy", "غائم في الغالب")
    else:
        return ("cloudy", "غائم")
