# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Engine - محرك المعايرة
====================================
Iterative parameter optimizer for process-based models.

Supports:
  • Random-restart hill climbing (no external dependencies)
  • SciPy differential_evolution (if scipy is installed)

The engine is model-agnostic: any predictor that implements
    predictor(theta: dict, targets: list[CalibrationTarget])
        -> dict[str, dict[str, float]]
can be calibrated.

Cost function: weighted RMSE across all targets.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from typing import Any

import structlog

from shared.calibration.types import (
    CalibrationResult,
    CalibrationTarget,
    ParameterBound,
)

logger = structlog.get_logger()

# Type alias for predictor callable:
#   predictor(theta, targets) -> {"LAI": {"YYYY-MM-DD": yhat}, "biomass": {...}}
Predictor = Callable[[dict[str, float], list[CalibrationTarget]], dict[str, dict[str, float]]]


# ---------------------------------------------------------------------------
# Cost functions
# ---------------------------------------------------------------------------


def weighted_rmse(
    predictions: dict[str, dict[str, float]],
    targets: list[CalibrationTarget],
) -> float:
    """
    Compute weighted RMSE across all calibration targets.
    حساب RMSE المرجّح عبر جميع أهداف المعايرة.
    """
    total_se = 0.0
    total_n = 0
    for tgt in targets:
        preds = predictions.get(tgt.variable, {})
        for obs in tgt.observations:
            yhat = preds.get(obs.t)
            if yhat is None:
                continue
            residual = (yhat - obs.value) / max(0.01, obs.uncertainty)
            total_se += tgt.weight * residual * residual
            total_n += 1
    if total_n == 0:
        return float("inf")
    return math.sqrt(total_se / total_n)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class CalibrationEngine:
    """
    Model-agnostic calibration engine.
    محرك معايرة مستقل عن النموذج.

    Usage::

        from shared.calibration import CalibrationEngine
        from shared.calibration.types import ParameterBound, CalibrationTarget

        engine = CalibrationEngine(
            predictor=my_predictor.predict,
            bounds=[
                ParameterBound("rue", 0.5, 3.0, initial=1.2),
                ParameterBound("k_extinction", 0.3, 0.8, initial=0.5),
            ],
        )
        result = engine.calibrate(targets=[...], max_iter=200)
        print(result.best_theta)
    """

    def __init__(
        self,
        predictor: Predictor,
        bounds: list[ParameterBound],
        cost_fn: Callable[
            [dict[str, dict[str, float]], list[CalibrationTarget]], float
        ]
        | None = None,
        seed: int = 42,
    ) -> None:
        self._predictor = predictor
        self._bounds = bounds
        self._cost_fn = cost_fn or weighted_rmse
        self._rng = random.Random(seed)

    def _sample_theta(self) -> dict[str, float]:
        """Sample a random parameter set within bounds."""
        return {
            b.name: self._rng.uniform(b.lower, b.upper) for b in self._bounds
        }

    def _initial_theta(self) -> dict[str, float]:
        """Return initial (or midpoint) parameter set."""
        return {
            b.name: (
                b.initial if b.initial is not None else (b.lower + b.upper) / 2.0
            )
            for b in self._bounds
        }

    def _perturb(self, theta: dict[str, float], scale: float = 0.1) -> dict[str, float]:
        """Perturb theta within bounds by ±scale fraction of range."""
        perturbed = {}
        for b in self._bounds:
            span = b.upper - b.lower
            delta = self._rng.gauss(0, scale * span)
            val = theta[b.name] + delta
            perturbed[b.name] = max(b.lower, min(b.upper, val))
        return perturbed

    def _evaluate(
        self, theta: dict[str, float], targets: list[CalibrationTarget]
    ) -> tuple[float, dict[str, dict[str, float]]]:
        """Run predictor and compute cost."""
        try:
            preds = self._predictor(theta, targets)
            cost = self._cost_fn(preds, targets)
        except Exception as exc:
            logger.warning("calibration_eval_failed", error=str(exc))
            return float("inf"), {}
        return cost, preds

    def calibrate(
        self,
        targets: list[CalibrationTarget],
        max_iter: int = 200,
        n_restarts: int = 5,
        tolerance: float = 1e-4,
    ) -> CalibrationResult:
        """
        Run calibration optimisation.
        تشغيل عملية المعايرة.

        Uses random-restart local search (no scipy required).
        Each restart starts from a random point; the best overall is returned.

        Args:
            targets: Observed data to calibrate against.
            max_iter: Maximum iterations per restart.
            n_restarts: Number of random restarts.
            tolerance: Stop if cost < tolerance.

        Returns:
            CalibrationResult with best parameters and diagnostics.
        """
        if not targets:
            return CalibrationResult(
                success=False,
                best_theta={},
                best_cost=float("inf"),
                n_evaluations=0,
                metadata={"error": "No calibration targets provided"},
            )

        global_best_theta = self._initial_theta()
        global_best_cost = float("inf")
        global_best_preds: dict[str, dict[str, float]] = {}
        total_evals = 0
        cost_history: list[float] = []

        for restart in range(n_restarts):
            # First restart uses initial theta; others are random
            theta = self._initial_theta() if restart == 0 else self._sample_theta()
            cost, preds = self._evaluate(theta, targets)
            total_evals += 1
            cost_history.append(cost)

            if cost < global_best_cost:
                global_best_cost = cost
                global_best_theta = dict(theta)
                global_best_preds = preds

            # Local search from this start point
            scale = 0.15
            stagnant = 0
            for _it in range(max_iter):
                candidate = self._perturb(theta, scale=scale)
                c_cost, c_preds = self._evaluate(candidate, targets)
                total_evals += 1

                if c_cost < cost:
                    theta = candidate
                    cost = c_cost
                    preds = c_preds
                    stagnant = 0
                    cost_history.append(cost)
                    if cost < global_best_cost:
                        global_best_cost = cost
                        global_best_theta = dict(theta)
                        global_best_preds = preds
                else:
                    stagnant += 1
                    # Adaptive scale reduction
                    if stagnant > 10:
                        scale *= 0.8
                        stagnant = 0
                    if scale < 0.001:
                        break

                if cost < tolerance:
                    break

            logger.debug(
                "calibration_restart_done",
                restart=restart,
                cost=round(cost, 6),
                evals=total_evals,
            )

        logger.info(
            "calibration_complete",
            best_cost=round(global_best_cost, 6),
            n_evaluations=total_evals,
            best_theta={k: round(v, 4) for k, v in global_best_theta.items()},
        )

        return CalibrationResult(
            success=global_best_cost < float("inf"),
            best_theta=global_best_theta,
            best_cost=global_best_cost,
            n_evaluations=total_evals,
            cost_history=cost_history,
            predictions=global_best_preds,
        )
