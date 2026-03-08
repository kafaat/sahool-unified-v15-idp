# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Bayesian Optimizer - المحسّن البايزي
======================================
Optuna-backed TPE (Tree-structured Parzen Estimator) optimizer.

Falls back to random-restart hill-climbing if optuna is not installed,
keeping the calibration module dependency-light for unit tests and
minimal deployments.

Usage::

    optimizer = BayesianOptimizer(
        param_space=[
            ParamSpec("rue", 0.8, 2.5),
            ParamSpec("lai_max", 2.0, 8.0, log=True),
        ],
        n_trials=60,
    )
    result = optimizer.optimize(lambda theta: cost(theta))
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import structlog

from shared.calibration.types import ParameterBound

logger = structlog.get_logger()

# Optuna is optional — soft-import
try:
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    _HAS_OPTUNA = True
except ImportError:  # pragma: no cover
    optuna = None  # type: ignore[assignment]
    _HAS_OPTUNA = False


# ParamSpec alias for the Bayesian optimizer
ParamSpec = ParameterBound


@dataclass(frozen=True)
class OptimizerResult:
    """
    Output of the optimizer.
    مخرجات المحسّن.
    """

    best_params: dict[str, float]
    best_value: float
    n_trials: int
    all_values: list[float]


class BayesianOptimizer:
    """
    Optuna TPE-based Bayesian optimiser.
    محسّن بايزي قائم على Optuna TPE.

    Raises ``RuntimeError`` at init if optuna is not installed.
    """

    def __init__(
        self,
        param_space: list[ParamSpec],
        n_trials: int = 60,
        seed: int = 42,
        timeout_s: float | None = None,
    ) -> None:
        if not _HAS_OPTUNA:
            raise RuntimeError(
                "optuna is not installed; run `pip install optuna` or fall back to CalibrationEngine (random-restart)."
            )
        if not param_space:
            raise ValueError("param_space must contain at least one parameter")
        if n_trials < 1:
            raise ValueError("n_trials must be >= 1")

        self._param_space = param_space
        self._n_trials = n_trials
        self._seed = seed
        self._timeout_s = timeout_s

    def optimize(self, objective: Callable[[dict[str, float]], float]) -> OptimizerResult:
        """
        Run Bayesian optimisation (minimize).
        تشغيل التحسين البايزي (تصغير).

        Args:
            objective: ``f(theta) -> scalar cost`` (lower is better).

        Returns:
            OptimizerResult with best parameters and convergence trace.
        """
        sampler = optuna.samplers.TPESampler(seed=self._seed)
        study = optuna.create_study(direction="minimize", sampler=sampler)

        values: list[float] = []

        def _trial_fn(trial: optuna.Trial) -> float:
            theta: dict[str, float] = {}
            for p in self._param_space:
                if p.log_scale:
                    low = max(p.lower, 1e-10)  # Optuna requires low > 0 for log
                    theta[p.name] = trial.suggest_float(p.name, low, p.upper, log=True)
                else:
                    theta[p.name] = trial.suggest_float(p.name, p.lower, p.upper)
            val = float(objective(theta))
            values.append(val)
            return val

        study.optimize(
            _trial_fn,
            n_trials=self._n_trials,
            timeout=self._timeout_s,
        )

        best = dict(study.best_params)
        logger.info(
            "bayesian_optimization_complete",
            best_value=round(study.best_value, 6),
            n_trials=len(study.trials),
            best_params={k: round(v, 4) for k, v in best.items()},
        )

        return OptimizerResult(
            best_params=best,
            best_value=float(study.best_value),
            n_trials=len(study.trials),
            all_values=values,
        )
