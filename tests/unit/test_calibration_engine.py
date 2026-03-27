# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Unit tests for the calibration engine and types.
اختبارات وحدة لمحرك المعايرة والأنواع.
"""

from __future__ import annotations

import math

import pytest

from shared.calibration.engine import CalibrationEngine, weighted_rmse
from shared.calibration.types import (
    CalibrationObservation,
    CalibrationResult,
    CalibrationTarget,
    ParameterBound,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _linear_predictor(theta: dict, targets: list[CalibrationTarget]) -> dict[str, dict[str, float]]:
    """Toy predictor: y = a * t_index + b, where theta = {a, b}."""
    a = theta.get("a", 1.0)
    b = theta.get("b", 0.0)
    out: dict[str, dict[str, float]] = {}
    for tgt in targets:
        var_preds = {}
        for i, obs in enumerate(tgt.observations):
            var_preds[obs.t] = a * (i + 1) + b
        out[tgt.variable] = var_preds
    return out


@pytest.fixture
def simple_targets() -> list[CalibrationTarget]:
    """Targets that match y = 2 * index + 1 (a=2, b=1)."""
    return [
        CalibrationTarget(
            variable="LAI",
            observations=[
                CalibrationObservation(t="2026-02-01", value=3.0, uncertainty=0.5),
                CalibrationObservation(t="2026-02-15", value=5.0, uncertainty=0.5),
                CalibrationObservation(t="2026-03-01", value=7.0, uncertainty=0.5),
            ],
            weight=1.0,
        )
    ]


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class TestCalibrationTypes:
    def test_observation_frozen(self):
        obs = CalibrationObservation(t="2026-01-01", value=1.5)
        with pytest.raises(AttributeError):
            obs.value = 2.0  # type: ignore[misc]

    def test_target_weight_default(self):
        tgt = CalibrationTarget(variable="LAI", observations=[])
        assert tgt.weight == 1.0

    def test_result_fields(self):
        res = CalibrationResult(
            success=True,
            best_theta={"a": 1.0},
            best_cost=0.05,
            n_evaluations=100,
        )
        assert res.success
        assert res.best_theta["a"] == 1.0
        assert res.cost_history == []


# ---------------------------------------------------------------------------
# Cost function
# ---------------------------------------------------------------------------


class TestWeightedRMSE:
    def test_perfect_predictions(self, simple_targets):
        preds = {"LAI": {"2026-02-01": 3.0, "2026-02-15": 5.0, "2026-03-01": 7.0}}
        cost = weighted_rmse(preds, simple_targets)
        assert cost == pytest.approx(0.0, abs=1e-9)

    def test_nonzero_error(self, simple_targets):
        preds = {"LAI": {"2026-02-01": 3.5, "2026-02-15": 5.5, "2026-03-01": 7.5}}
        cost = weighted_rmse(preds, simple_targets)
        assert cost > 0.0

    def test_missing_predictions_returns_inf(self, simple_targets):
        preds: dict = {"biomass": {}}
        cost = weighted_rmse(preds, simple_targets)
        assert cost == float("inf")

    def test_empty_targets(self):
        cost = weighted_rmse({"LAI": {"2026-01-01": 1.0}}, [])
        assert cost == float("inf")


# ---------------------------------------------------------------------------
# Calibration Engine
# ---------------------------------------------------------------------------


class TestCalibrationEngine:
    def test_calibrate_linear(self, simple_targets):
        """Engine should find a≈2, b≈1 for y=2i+1."""
        engine = CalibrationEngine(
            predictor=_linear_predictor,
            bounds=[
                ParameterBound("a", 0.0, 5.0, initial=1.0),
                ParameterBound("b", -5.0, 5.0, initial=0.0),
            ],
            seed=42,
        )
        result = engine.calibrate(
            targets=simple_targets,
            max_iter=300,
            n_restarts=5,
        )
        assert result.success
        assert result.best_theta["a"] == pytest.approx(2.0, abs=0.3)
        assert result.best_theta["b"] == pytest.approx(1.0, abs=0.5)
        assert result.n_evaluations > 0

    def test_empty_targets_returns_failure(self):
        engine = CalibrationEngine(
            predictor=_linear_predictor,
            bounds=[ParameterBound("a", 0, 5)],
        )
        result = engine.calibrate(targets=[])
        assert not result.success
        assert result.best_cost == float("inf")

    def test_failing_predictor_does_not_crash(self, simple_targets):
        def bad_predictor(theta, targets):
            raise RuntimeError("Model exploded")

        engine = CalibrationEngine(
            predictor=bad_predictor,
            bounds=[ParameterBound("a", 0, 5)],
        )
        result = engine.calibrate(targets=simple_targets, max_iter=5, n_restarts=1)
        assert result.best_cost == float("inf")

    def test_initial_values_used(self, simple_targets):
        """When initial is close to solution, engine should converge quickly."""
        engine = CalibrationEngine(
            predictor=_linear_predictor,
            bounds=[
                ParameterBound("a", 0.0, 5.0, initial=2.0),
                ParameterBound("b", -5.0, 5.0, initial=1.0),
            ],
            seed=42,
        )
        result = engine.calibrate(targets=simple_targets, max_iter=50, n_restarts=1)
        assert result.success
        assert result.best_cost < 0.5
