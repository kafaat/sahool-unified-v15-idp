# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Holdout Validation - التحقق بالاحتجاز
========================================
Evaluate calibrated parameters against a held-out subset of observations.

Computes per-variable RMSE, MAE, and bias to decide whether the
calibrated parameter set is safe for decision-making.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from shared.calibration.types import (
    CalibrationObservation,
    CalibrationTarget,
    TimestampedObservation,
    ValidationMetrics,
)

# Predictor type alias
Predictor = Callable[
    [dict[str, float], list[CalibrationTarget]],
    dict[str, dict[str, float]],
]


def _obs_value_and_date(obs: CalibrationObservation | TimestampedObservation) -> tuple[str, float]:
    if isinstance(obs, TimestampedObservation):
        return obs.t, obs.obs.value
    return obs.t, obs.value


def validate_holdout(
    theta: dict[str, float],
    holdout_targets: list[CalibrationTarget],
    predictor: Predictor,
) -> ValidationMetrics:
    """
    Compute RMSE / MAE / bias on a holdout set.
    حساب RMSE / MAE / الانحياز على مجموعة احتجاز.

    Args:
        theta: Calibrated parameter values.
        holdout_targets: Observations reserved for validation.
        predictor: Same predictor used during calibration.

    Returns:
        ValidationMetrics with per-variable error statistics.
    """
    yhat = predictor(theta, holdout_targets)

    rmse: dict[str, float] = {}
    mae: dict[str, float] = {}
    bias: dict[str, float] = {}

    for tgt in holdout_targets:
        var = tgt.variable
        n = 0
        sum_se = 0.0
        sum_ae = 0.0
        sum_err = 0.0

        for obs in tgt.observations:
            t, y = _obs_value_and_date(obs)
            pred = yhat.get(var, {}).get(t)
            if pred is None:
                continue
            err = pred - y
            sum_se += err * err
            sum_ae += abs(err)
            sum_err += err
            n += 1

        if n == 0:
            rmse[var] = float("nan")
            mae[var] = float("nan")
            bias[var] = float("nan")
        else:
            rmse[var] = math.sqrt(sum_se / n)
            mae[var] = sum_ae / n
            bias[var] = sum_err / n

    return ValidationMetrics(rmse=rmse, mae=mae, bias=bias)
