# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Objective Functions - دوال الهدف للمعايرة
======================================================
Weighted Negative Log-Likelihood (NLL) objective that leverages per-observation
uncertainty (σ) to weight residuals.  Falls back gracefully to the simpler
``CalibrationObservation`` type if ``TimestampedObservation`` is not used.

The NLL formulation is:
    L(θ) = Σ_targets w_t · Σ_obs [ (y - ŷ)² / (2σ²) + log(σ) ]

This naturally down-weights observations with high σ and penalises
over-confident models that report small σ while having large residuals.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

from shared.calibration.types import (
    CalibrationObservation,
    CalibrationTarget,
    TimestampedObservation,
)

# Type alias for the predictor callable
Predictor = Callable[
    [dict[str, float], list[CalibrationTarget]],
    dict[str, dict[str, float]],
]


@dataclass(frozen=True)
class ObjectiveResult:
    """
    Objective evaluation result with per-target breakdown.
    نتيجة تقييم دالة الهدف مع تفصيل لكل هدف.
    """

    value: float
    per_target: dict[str, float]
    n_obs_used: int = 0


def _obs_triple(obs: CalibrationObservation | TimestampedObservation) -> tuple[str, float, float, float]:
    """Extract (date, value, sigma, quality_score) regardless of obs type."""
    if isinstance(obs, TimestampedObservation):
        return obs.t, obs.obs.value, max(obs.obs.std, 1e-6), obs.quality_score
    # Legacy CalibrationObservation
    return obs.t, obs.value, max(obs.uncertainty, 1e-6), 1.0


def build_weighted_nll_objective(
    targets: list[CalibrationTarget],
    predictor: Predictor,
) -> Callable[[dict[str, float]], ObjectiveResult]:
    """
    Build a weighted NLL objective closure.
    بناء دالة هدف NLL المرجّحة.

    The returned callable runs the predictor and computes the NLL.

    Observations with ``quality_score < target.min_quality_score`` are
    pre-filtered at build time (not on every call).

    Args:
        targets: Calibration targets with observations.
        predictor: ``predictor(theta, targets) -> {var: {date: yhat}}``

    Returns:
        ``objective(theta) -> ObjectiveResult``
    """
    # Pre-filter by min_quality_score
    filtered: list[CalibrationTarget] = []
    for tgt in targets:
        kept = [o for o in tgt.observations if _obs_triple(o)[3] >= tgt.min_quality_score]
        if kept:
            filtered.append(
                CalibrationTarget(
                    variable=tgt.variable,
                    observations=kept,
                    weight=tgt.weight,
                    min_quality_score=tgt.min_quality_score,
                )
            )

    def objective(theta: dict[str, float]) -> ObjectiveResult:
        yhat = predictor(theta, filtered)
        total = 0.0
        per_target: dict[str, float] = {}
        n_obs = 0

        for tgt in filtered:
            var = tgt.variable
            nll = 0.0
            count = 0

            for obs in tgt.observations:
                t, y, sigma, _q = _obs_triple(obs)
                pred = yhat.get(var, {}).get(t)
                if pred is None:
                    continue

                residual = y - pred
                nll += (residual * residual) / (2.0 * sigma * sigma) + math.log(sigma)
                count += 1

            component = tgt.weight * nll
            per_target[var] = component
            total += component
            n_obs += count

        return ObjectiveResult(value=total, per_target=per_target, n_obs_used=n_obs)

    return objective
