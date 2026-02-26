# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Uncertainty Value Objects - كائنات القيم مع عدم اليقين
=======================================================
Attach measurement uncertainty and quality provenance to any numeric value.

Used by:
  calibration/ – observation uncertainties drive NLL objective weighting
  digital_twin/ – state confidence propagation
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class QualityFlag(StrEnum):
    """
    Provenance tag for a numeric value.
    علامة مصدر لقيمة رقمية.
    """

    OBSERVED = "observed"  # Direct measurement | قياس مباشر
    INTERPOLATED = "interpolated"  # Spatially/temporally filled | استيفاء
    SIMULATED = "simulated"  # Process-model output | ناتج نموذج
    CALIBRATED = "calibrated"  # Post-calibration output | ناتج بعد المعايرة
    UNCALIBRATED = "uncalibrated"  # Pre-calibration default | قبل المعايرة


@dataclass(frozen=True)
class ValueWithUncertainty:
    """
    A numeric value paired with its standard deviation and quality flag.
    قيمة رقمية مع انحرافها المعياري وعلامة الجودة.

    Example::

        obs = ValueWithUncertainty(value=3.5, std=0.2, quality=QualityFlag.OBSERVED)
    """

    value: float
    std: float  # Standard deviation (σ ≥ 0) | الانحراف المعياري
    quality: QualityFlag = QualityFlag.OBSERVED

    def __post_init__(self) -> None:
        if self.std < 0:
            raise ValueError(f"std must be non-negative, got {self.std}")

    @property
    def cv(self) -> float:
        """Coefficient of variation (%). معامل الاختلاف."""
        if abs(self.value) < 1e-12:
            return 0.0
        return abs(self.std / self.value) * 100.0

    @property
    def ci_95(self) -> tuple[float, float]:
        """Approximate 95% confidence interval. فترة الثقة 95%."""
        margin = 1.96 * self.std
        return (self.value - margin, self.value + margin)
