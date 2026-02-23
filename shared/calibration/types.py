# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Types - أنواع بيانات المعايرة
==========================================
Value objects shared between CalibrationEngine and model adapters.

v16.1 additions:
  - TimestampedObservation   – quality-scored observation with source ref
  - CalibrationTarget.min_quality_score  – gate for low-quality data
  - ValidationMetrics        – holdout-set evaluation results
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from shared.process_models.uncertainty import ValueWithUncertainty

# Type alias for supported calibration variables
VariableName = Literal["LAI", "biomass", "soil_moisture"]


# ---------------------------------------------------------------------------
# Original types (backward-compatible)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CalibrationObservation:
    """
    A single observed data point for calibration.
    نقطة بيانات مرصودة واحدة للمعايرة.
    """

    t: str  # ISO date "YYYY-MM-DD" | تاريخ الرصد
    value: float  # Observed value | القيمة المرصودة
    uncertainty: float = 0.1  # Observation uncertainty (std dev) | عدم اليقين


@dataclass(frozen=True)
class ParameterBound:
    """
    Bounds for a single calibration parameter.
    حدود معامل واحد للمعايرة.
    """

    name: str
    lower: float
    upper: float
    initial: float | None = None  # Starting value (default: midpoint) | القيمة الابتدائية
    log_scale: bool = False  # Sample in log-space (Optuna) | عينة لوغاريتمية


@dataclass
class CalibrationResult:
    """
    Output of the calibration engine.
    مخرجات محرك المعايرة.
    """

    success: bool
    best_theta: dict[str, float]  # Calibrated parameters | المعاملات المعايرة
    best_cost: float  # Final cost (RMSE or NLL) | قيمة دالة التكلفة النهائية
    n_evaluations: int  # Number of model runs | عدد تشغيلات النموذج
    cost_history: list[float] = field(default_factory=list)
    predictions: dict[str, dict[str, float]] = field(
        default_factory=dict
    )  # Final predictions | التنبؤات النهائية
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# v16.1: Uncertainty-aware types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TimestampedObservation:
    """
    An observation enriched with uncertainty, quality score, and source reference.
    رصد مُثرى بعدم اليقين ودرجة الجودة ومرجع المصدر.

    Example::

        TimestampedObservation(
            t="2026-02-15",
            variable="LAI",
            obs=ValueWithUncertainty(value=1.2, std=0.15, quality=QualityFlag.OBSERVED),
            source_ref={"ndvi_result_id": "abc-123"},
            quality_score=0.85,
        )
    """

    t: str  # ISO date "YYYY-MM-DD" | تاريخ الرصد
    variable: VariableName  # type: ignore[assignment]
    obs: ValueWithUncertainty
    source_ref: dict[str, Any] = field(default_factory=dict)  # Provenance link | رابط المصدر
    quality_score: float = 0.7  # 0..1 aggregate quality | الجودة الكلية

    def __post_init__(self) -> None:
        if not (0.0 <= self.quality_score <= 1.0):
            raise ValueError(f"quality_score must be in [0, 1], got {self.quality_score}")


@dataclass(frozen=True)
class CalibrationTarget:
    """
    A variable to calibrate against, with its observations.
    متغير للمعايرة مقابله مع أرصاده.

    Supports both legacy ``CalibrationObservation`` and new ``TimestampedObservation``.

    Example (v16.1)::

        CalibrationTarget(
            variable="LAI",
            observations=[obs1, obs2],
            weight=1.0,
            min_quality_score=0.5,
        )

    Example (legacy, still works)::

        CalibrationTarget(
            variable="LAI",
            observations=[
                CalibrationObservation(t="2026-02-15", value=1.2, uncertainty=0.15),
            ],
            weight=1.0,
        )
    """

    variable: str  # Variable name: "LAI", "biomass", "soil_moisture" | اسم المتغير
    observations: list[CalibrationObservation] | list[TimestampedObservation]
    weight: float = 1.0  # Relative weight in cost function | الوزن النسبي
    min_quality_score: float = 0.0  # Gate low-quality obs (0 = accept all) | حد أدنى

    def __post_init__(self) -> None:
        if self.weight <= 0:
            raise ValueError(f"CalibrationTarget.weight must be > 0, got {self.weight}")
        if not (0.0 <= self.min_quality_score <= 1.0):
            raise ValueError(f"min_quality_score must be in [0, 1], got {self.min_quality_score}")


# ---------------------------------------------------------------------------
# Validation metrics (holdout evaluation)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValidationMetrics:
    """
    Per-variable error metrics from holdout evaluation.
    مقاييس الخطأ لكل متغير من التقييم بالاحتجاز.
    """

    rmse: dict[str, float]
    mae: dict[str, float]
    bias: dict[str, float]
