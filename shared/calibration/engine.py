# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Engine - محرك المعايرة
====================================
Iterative parameter optimizer for process-based models.

Two optimization strategies:
  1. CalibrationEngine     – Random-restart hill climbing (no external deps)
  2. BayesianCalibration   – Optuna TPE + weighted NLL + holdout validation

Both are model-agnostic: any predictor implementing::

    predictor(theta: dict, targets: list[CalibrationTarget])
        -> dict[str, dict[str, float]]

can be calibrated.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass

import structlog

from shared.calibration.objective import build_weighted_nll_objective
from shared.calibration.types import (
    CalibrationResult,
    CalibrationTarget,
    ParameterBound,
    ValidationMetrics,
)
from shared.calibration.validation import validate_holdout

logger = structlog.get_logger()

# Type alias for predictor callable:
#   predictor(theta, targets) -> {"LAI": {"YYYY-MM-DD": yhat}, "biomass": {...}}
Predictor = Callable[[dict[str, float], list[CalibrationTarget]], dict[str, dict[str, float]]]


# ---------------------------------------------------------------------------
# Cost functions (legacy support)
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
            uncertainty = getattr(obs, "uncertainty", 0.1)
            if hasattr(obs, "obs"):
                uncertainty = max(obs.obs.std, 0.01)
            else:
                uncertainty = max(uncertainty, 0.01)
            residual = (yhat - obs.value) / uncertainty
            total_se += tgt.weight * residual * residual
            total_n += 1
    if total_n == 0:
        return float("inf")
    return math.sqrt(total_se / total_n)


# ---------------------------------------------------------------------------
# Legacy Engine (random-restart hill climbing)
# ---------------------------------------------------------------------------


class CalibrationEngine:
    """
    Model-agnostic calibration engine (random-restart hill climbing).
    محرك معايرة مستقل عن النموذج (تسلق تلال مع إعادة تشغيل عشوائية).

    Usage::

        engine = CalibrationEngine(
            predictor=my_predictor.predict,
            bounds=[
                ParameterBound("rue", 0.5, 3.0, initial=1.2),
                ParameterBound("k_extinction", 0.3, 0.8, initial=0.5),
            ],
        )
        result = engine.calibrate(targets=[...], max_iter=200)
    """

    def __init__(
        self,
        predictor: Predictor,
        bounds: list[ParameterBound],
        cost_fn: Callable[[dict[str, dict[str, float]], list[CalibrationTarget]], float] | None = None,
        seed: int = 42,
    ) -> None:
        self._predictor = predictor
        self._bounds = bounds
        self._cost_fn = cost_fn or weighted_rmse
        self._rng = random.Random(seed)

    def _sample_theta(self) -> dict[str, float]:
        return {b.name: self._rng.uniform(b.lower, b.upper) for b in self._bounds}

    def _initial_theta(self) -> dict[str, float]:
        return {b.name: (b.initial if b.initial is not None else (b.lower + b.upper) / 2.0) for b in self._bounds}

    def _perturb(self, theta: dict[str, float], scale: float = 0.1) -> dict[str, float]:
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
            theta = self._initial_theta() if restart == 0 else self._sample_theta()
            cost, preds = self._evaluate(theta, targets)
            total_evals += 1
            cost_history.append(cost)

            if cost < global_best_cost:
                global_best_cost = cost
                global_best_theta = dict(theta)
                global_best_preds = preds

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


# ---------------------------------------------------------------------------
# Bayesian Calibration (Optuna + NLL + holdout validation)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CalibrationConfig:
    """
    Configuration for BayesianCalibration.
    إعدادات المعايرة البايزية.
    """

    n_trials: int = 60
    seed: int = 42
    timeout_s: float | None = None
    # Quality gates for safe_for_decision
    max_rmse_lai: float = 0.8
    max_rmse_biomass: float = 500.0  # kg/ha


@dataclass(frozen=True)
class CalibrationOutput:
    """
    Rich output from BayesianCalibration.calibrate().
    مخرجات غنية من المعايرة البايزية.
    """

    best_params: dict[str, float]
    best_objective: float
    n_trials: int
    objective_breakdown: dict[str, float]
    validation: ValidationMetrics
    safe_for_decision: bool
    gate_violations: dict[str, str]


class BayesianCalibration:
    """
    End-to-end Bayesian calibration with NLL objective and holdout validation.
    معايرة بايزية شاملة مع هدف NLL وتحقق بالاحتجاز.

    Usage::

        cal = BayesianCalibration(
            predictor=my_predictor.predict,
            param_space=[ParameterBound("rue", 0.8, 2.5), ...],
            config=CalibrationConfig(n_trials=80),
        )
        output = cal.calibrate(targets=train, holdout_targets=test)
        if output.safe_for_decision:
            print("Safe to activate:", output.best_params)
    """

    def __init__(
        self,
        predictor: Predictor,
        param_space: list[ParameterBound],
        config: CalibrationConfig | None = None,
    ) -> None:
        self._predictor = predictor
        self._param_space = param_space
        self._config = config or CalibrationConfig()

    def calibrate(
        self,
        targets: list[CalibrationTarget],
        holdout_targets: list[CalibrationTarget] | None = None,
    ) -> CalibrationOutput:
        """
        Run Bayesian optimization + holdout validation.
        تشغيل التحسين البايزي + التحقق بالاحتجاز.
        """
        from shared.calibration.optimizer import BayesianOptimizer

        obj_fn = build_weighted_nll_objective(targets, self._predictor)

        optimizer = BayesianOptimizer(
            param_space=self._param_space,
            n_trials=self._config.n_trials,
            seed=self._config.seed,
            timeout_s=self._config.timeout_s,
        )

        # Evaluate objective to get per-target breakdown
        def scalar_obj(theta: dict[str, float]) -> float:
            return obj_fn(theta).value

        result = optimizer.optimize(scalar_obj)

        # Get per-target breakdown for the best params
        best_obj = obj_fn(result.best_params)

        # Holdout validation
        holdout = holdout_targets or []
        if holdout:
            val = validate_holdout(result.best_params, holdout, self._predictor)
        else:
            val = ValidationMetrics(rmse={}, mae={}, bias={})

        # Quality gates
        safe = True
        violations: dict[str, str] = {}

        rmse_lai = val.rmse.get("LAI")
        if rmse_lai is not None and rmse_lai == rmse_lai:  # NaN check
            if rmse_lai > self._config.max_rmse_lai:
                safe = False
                violations["LAI"] = f"RMSE {rmse_lai:.3f} > threshold {self._config.max_rmse_lai}"

        rmse_bio = val.rmse.get("biomass")
        if rmse_bio is not None and rmse_bio == rmse_bio:
            if rmse_bio > self._config.max_rmse_biomass:
                safe = False
                violations["biomass"] = f"RMSE {rmse_bio:.1f} > threshold {self._config.max_rmse_biomass}"

        logger.info(
            "bayesian_calibration_complete",
            best_objective=round(result.best_value, 4),
            n_trials=result.n_trials,
            safe_for_decision=safe,
            validation_rmse={k: round(v, 4) for k, v in val.rmse.items() if v == v},
        )

        return CalibrationOutput(
            best_params=result.best_params,
            best_objective=result.best_value,
            n_trials=result.n_trials,
            objective_breakdown=best_obj.per_target,
            validation=val,
            safe_for_decision=safe,
            gate_violations=violations,
        )
