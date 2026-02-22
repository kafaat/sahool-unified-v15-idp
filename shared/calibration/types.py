# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Types - أنواع بيانات المعايرة
==========================================
Value objects shared between CalibrationEngine and model adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
class CalibrationTarget:
    """
    A variable to calibrate against, with its observations.
    متغير للمعايرة مقابله مع أرصاده.

    Example::

        CalibrationTarget(
            variable="LAI",
            observations=[
                CalibrationObservation(t="2026-02-15", value=1.2, uncertainty=0.15),
                CalibrationObservation(t="2026-03-10", value=3.5, uncertainty=0.20),
            ],
            weight=1.0,
        )
    """

    variable: str  # Variable name: "LAI", "biomass", "soil_moisture" | اسم المتغير
    observations: list[CalibrationObservation]
    weight: float = 1.0  # Relative weight in cost function | الوزن النسبي


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


@dataclass
class CalibrationResult:
    """
    Output of the calibration engine.
    مخرجات محرك المعايرة.
    """

    success: bool
    best_theta: dict[str, float]  # Calibrated parameters | المعاملات المعايرة
    best_cost: float  # Final cost (RMSE) | قيمة دالة التكلفة النهائية
    n_evaluations: int  # Number of model runs | عدد تشغيلات النموذج
    cost_history: list[float] = field(default_factory=list)
    predictions: dict[str, dict[str, float]] = field(
        default_factory=dict
    )  # Final predictions | التنبؤات النهائية
    metadata: dict[str, Any] = field(default_factory=dict)
