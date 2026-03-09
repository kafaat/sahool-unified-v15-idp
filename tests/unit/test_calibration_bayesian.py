# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Unit tests for Bayesian calibration, NLL objective, fingerprint, validation,
uncertainty, and quality modules.

اختبارات وحدة للمعايرة البايزية، هدف NLL، البصمة، التحقق، عدم اليقين، والجودة.
"""

from __future__ import annotations

import math

import pytest

from shared.calibration.fingerprint import fingerprint_dataset
from shared.calibration.objective import ObjectiveResult, build_weighted_nll_objective
from shared.calibration.types import (
    CalibrationObservation,
    CalibrationTarget,
    ParameterBound,
    TimestampedObservation,
    ValidationMetrics,
)
from shared.calibration.validation import validate_holdout
from shared.process_models.uncertainty import QualityFlag, ValueWithUncertainty


# ---------------------------------------------------------------------------
# ValueWithUncertainty
# ---------------------------------------------------------------------------


class TestValueWithUncertainty:
    def test_basic(self):
        v = ValueWithUncertainty(value=3.5, std=0.2, quality=QualityFlag.OBSERVED)
        assert v.value == 3.5
        assert v.std == 0.2
        assert v.quality == QualityFlag.OBSERVED

    def test_negative_std_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            ValueWithUncertainty(value=1.0, std=-0.1)

    def test_cv(self):
        v = ValueWithUncertainty(value=10.0, std=2.0)
        assert v.cv == pytest.approx(20.0)

    def test_ci_95(self):
        v = ValueWithUncertainty(value=5.0, std=1.0)
        lo, hi = v.ci_95
        assert lo == pytest.approx(5.0 - 1.96, abs=0.01)
        assert hi == pytest.approx(5.0 + 1.96, abs=0.01)

    def test_frozen(self):
        v = ValueWithUncertainty(value=1.0, std=0.1)
        with pytest.raises(AttributeError):
            v.value = 2.0  # type: ignore[misc]

    def test_default_quality(self):
        v = ValueWithUncertainty(value=1.0, std=0.1)
        assert v.quality == QualityFlag.OBSERVED

    def test_zero_std_allowed(self):
        v = ValueWithUncertainty(value=1.0, std=0.0)
        assert v.std == 0.0


# ---------------------------------------------------------------------------
# Quality scoring (imported lazily to avoid pydantic dependency)
# ---------------------------------------------------------------------------


class TestWeatherQuality:
    @pytest.fixture(autouse=True)
    def _import_quality(self):
        try:
            from shared.digital_twin.quality import QualityLevel, score_weather

            self.score_weather = score_weather
            self.QualityLevel = QualityLevel
        except ImportError:
            pytest.skip("pydantic not available (digital_twin.quality requires it)")

    def test_perfect_record(self):
        q = self.score_weather(
            tmax_c=30.0,
            tmin_c=18.0,
            solar_radiation_mj_m2=20.0,
            relative_humidity_pct=55.0,
        )
        assert q.score >= 0.9
        assert q.level == self.QualityLevel.EXCELLENT
        assert len(q.reasons) == 0

    def test_missing_temperature(self):
        q = self.score_weather(
            tmax_c=None,
            tmin_c=None,
            solar_radiation_mj_m2=20.0,
            relative_humidity_pct=55.0,
        )
        assert q.score < 0.7
        assert "missing_temperature" in q.reasons

    def test_tmax_lt_tmin(self):
        q = self.score_weather(
            tmax_c=10.0,
            tmin_c=20.0,
            solar_radiation_mj_m2=18.0,
            relative_humidity_pct=55.0,
        )
        assert "tmax_lt_tmin" in q.reasons


class TestObservationQuality:
    @pytest.fixture(autouse=True)
    def _import_quality(self):
        try:
            from shared.digital_twin.quality import score_observation

            self.score_observation = score_observation
        except ImportError:
            pytest.skip("pydantic not available")

    def test_high_quality_sentinel(self):
        q = self.score_observation(source="sentinel-2", cloud_pct=5.0, age_hours=1.0)
        assert q.score >= 0.9

    def test_high_cloud_penalty(self):
        q = self.score_observation(source="sentinel-2", cloud_pct=60.0)
        assert "high_cloud_cover" in q.reasons

    def test_manual_penalty(self):
        q = self.score_observation(source="manual")
        assert "manual_estimate" in q.reasons


# ---------------------------------------------------------------------------
# TimestampedObservation
# ---------------------------------------------------------------------------


class TestTimestampedObservation:
    def test_basic(self):
        obs = TimestampedObservation(
            t="2026-02-15",
            variable="LAI",
            obs=ValueWithUncertainty(value=1.2, std=0.15),
            quality_score=0.85,
        )
        assert obs.t == "2026-02-15"
        assert obs.obs.value == 1.2

    def test_invalid_quality_score(self):
        with pytest.raises(ValueError, match="quality_score"):
            TimestampedObservation(
                t="2026-02-15",
                variable="LAI",
                obs=ValueWithUncertainty(value=1.0, std=0.1),
                quality_score=1.5,
            )

    def test_default_quality_score(self):
        obs = TimestampedObservation(
            t="2026-02-15",
            variable="LAI",
            obs=ValueWithUncertainty(value=1.0, std=0.1),
        )
        assert obs.quality_score == 0.7

    def test_frozen(self):
        obs = TimestampedObservation(
            t="2026-02-15",
            variable="LAI",
            obs=ValueWithUncertainty(value=1.0, std=0.1),
        )
        with pytest.raises(AttributeError):
            obs.t = "2026-03-01"  # type: ignore[misc]


class TestCalibrationTarget:
    def test_weight_must_be_positive(self):
        with pytest.raises(ValueError, match="weight"):
            CalibrationTarget(variable="LAI", observations=[], weight=-1.0)

    def test_min_quality_score_range(self):
        with pytest.raises(ValueError, match="min_quality_score"):
            CalibrationTarget(variable="LAI", observations=[], weight=1.0, min_quality_score=2.0)

    def test_default_min_quality(self):
        tgt = CalibrationTarget(variable="LAI", observations=[], weight=1.0)
        assert tgt.min_quality_score == 0.0


# ---------------------------------------------------------------------------
# ParameterBound
# ---------------------------------------------------------------------------


class TestParameterBound:
    def test_log_scale(self):
        pb = ParameterBound(name="rue", lower=0.1, upper=5.0, log_scale=True)
        assert pb.log_scale is True

    def test_default_no_log(self):
        pb = ParameterBound(name="rue", lower=0.1, upper=5.0)
        assert pb.log_scale is False


# ---------------------------------------------------------------------------
# Fingerprint
# ---------------------------------------------------------------------------


class TestFingerprint:
    def test_deterministic(self):
        payload = {"a": 1, "b": [2, 3], "c": "hello"}
        fp1 = fingerprint_dataset(payload)
        fp2 = fingerprint_dataset(payload)
        assert fp1 == fp2
        assert len(fp1) == 64  # SHA-256 hex

    def test_key_order_independent(self):
        fp1 = fingerprint_dataset({"x": 1, "y": 2})
        fp2 = fingerprint_dataset({"y": 2, "x": 1})
        assert fp1 == fp2

    def test_different_data_different_fingerprint(self):
        fp1 = fingerprint_dataset({"a": 1})
        fp2 = fingerprint_dataset({"a": 2})
        assert fp1 != fp2

    def test_handles_nested_structures(self):
        payload = {
            "tenant_id": "abc",
            "targets": [
                {"variable": "LAI", "obs_refs": [{"id": "x"}]},
            ],
        }
        fp = fingerprint_dataset(payload)
        assert isinstance(fp, str)
        assert len(fp) == 64


# ---------------------------------------------------------------------------
# NLL Objective
# ---------------------------------------------------------------------------


def _perfect_predictor(theta: dict, targets: list[CalibrationTarget]) -> dict[str, dict[str, float]]:
    """Return observations as predictions (zero residual)."""
    out: dict[str, dict[str, float]] = {}
    for tgt in targets:
        var_preds = {}
        for obs in tgt.observations:
            if isinstance(obs, TimestampedObservation):
                var_preds[obs.t] = obs.obs.value
            else:
                var_preds[obs.t] = obs.value
        out[tgt.variable] = var_preds
    return out


def _offset_predictor(theta: dict, targets: list[CalibrationTarget]) -> dict[str, dict[str, float]]:
    """Add theta['offset'] to each true value."""
    offset = theta.get("offset", 0.0)
    out: dict[str, dict[str, float]] = {}
    for tgt in targets:
        var_preds = {}
        for obs in tgt.observations:
            if isinstance(obs, TimestampedObservation):
                var_preds[obs.t] = obs.obs.value + offset
            else:
                var_preds[obs.t] = obs.value + offset
        out[tgt.variable] = var_preds
    return out


class TestNLLObjective:
    @pytest.fixture
    def targets_v2(self) -> list[CalibrationTarget]:
        return [
            CalibrationTarget(
                variable="LAI",
                observations=[
                    TimestampedObservation(
                        t="2026-02-15",
                        variable="LAI",
                        obs=ValueWithUncertainty(value=1.2, std=0.15),
                        quality_score=0.9,
                    ),
                    TimestampedObservation(
                        t="2026-03-10",
                        variable="LAI",
                        obs=ValueWithUncertainty(value=3.5, std=0.20),
                        quality_score=0.85,
                    ),
                ],
                weight=1.0,
            )
        ]

    def test_perfect_nll_is_only_penalty(self, targets_v2):
        obj = build_weighted_nll_objective(targets_v2, _perfect_predictor)
        result = obj({"unused": 0})
        # NLL with zero residuals = Σ log(σ)
        expected = math.log(0.15) + math.log(0.20)
        assert result.value == pytest.approx(expected, abs=0.01)
        assert result.n_obs_used == 2

    def test_worse_theta_higher_nll(self, targets_v2):
        obj = build_weighted_nll_objective(targets_v2, _offset_predictor)
        good = obj({"offset": 0.0})
        bad = obj({"offset": 2.0})
        assert bad.value > good.value

    def test_quality_filter(self):
        targets = [
            CalibrationTarget(
                variable="LAI",
                observations=[
                    TimestampedObservation(
                        t="2026-02-15",
                        variable="LAI",
                        obs=ValueWithUncertainty(value=1.0, std=0.1),
                        quality_score=0.3,  # Below threshold
                    ),
                    TimestampedObservation(
                        t="2026-03-10",
                        variable="LAI",
                        obs=ValueWithUncertainty(value=2.0, std=0.1),
                        quality_score=0.8,  # Above threshold
                    ),
                ],
                weight=1.0,
                min_quality_score=0.5,
            )
        ]
        obj = build_weighted_nll_objective(targets, _perfect_predictor)
        result = obj({})
        assert result.n_obs_used == 1

    def test_legacy_observations_work(self):
        targets = [
            CalibrationTarget(
                variable="LAI",
                observations=[
                    CalibrationObservation(t="2026-02-15", value=1.0, uncertainty=0.1),
                ],
                weight=1.0,
            )
        ]
        obj = build_weighted_nll_objective(targets, _perfect_predictor)
        result = obj({})
        assert result.n_obs_used == 1
        assert result.value == pytest.approx(math.log(0.1), abs=0.01)

    def test_per_target_breakdown(self, targets_v2):
        obj = build_weighted_nll_objective(targets_v2, _perfect_predictor)
        result = obj({})
        assert "LAI" in result.per_target

    def test_multi_variable(self):
        targets = [
            CalibrationTarget(
                variable="LAI",
                observations=[CalibrationObservation(t="2026-02-15", value=1.0, uncertainty=0.1)],
                weight=1.0,
            ),
            CalibrationTarget(
                variable="biomass",
                observations=[CalibrationObservation(t="2026-02-15", value=500.0, uncertainty=50.0)],
                weight=2.0,
            ),
        ]
        obj = build_weighted_nll_objective(targets, _perfect_predictor)
        result = obj({})
        assert "LAI" in result.per_target
        assert "biomass" in result.per_target
        assert result.n_obs_used == 2


# ---------------------------------------------------------------------------
# Holdout Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def test_perfect_validation(self):
        targets = [
            CalibrationTarget(
                variable="LAI",
                observations=[
                    CalibrationObservation(t="2026-02-15", value=1.0),
                    CalibrationObservation(t="2026-03-01", value=2.0),
                ],
                weight=1.0,
            )
        ]
        val = validate_holdout({}, targets, _perfect_predictor)
        assert val.rmse["LAI"] == pytest.approx(0.0, abs=1e-9)
        assert val.mae["LAI"] == pytest.approx(0.0, abs=1e-9)
        assert val.bias["LAI"] == pytest.approx(0.0, abs=1e-9)

    def test_constant_offset_bias(self):
        targets = [
            CalibrationTarget(
                variable="LAI",
                observations=[
                    CalibrationObservation(t="2026-02-15", value=1.0),
                    CalibrationObservation(t="2026-03-01", value=2.0),
                ],
                weight=1.0,
            )
        ]
        val = validate_holdout({"offset": 0.5}, targets, _offset_predictor)
        assert val.bias["LAI"] == pytest.approx(0.5, abs=0.01)
        assert val.rmse["LAI"] == pytest.approx(0.5, abs=0.01)

    def test_empty_predictions_return_nan(self):
        def no_preds(theta, targets):
            return {}

        targets = [
            CalibrationTarget(
                variable="LAI",
                observations=[CalibrationObservation(t="2026-02-15", value=1.0)],
                weight=1.0,
            )
        ]
        val = validate_holdout({}, targets, no_preds)
        assert math.isnan(val.rmse["LAI"])

    def test_works_with_timestamped_observations(self):
        targets = [
            CalibrationTarget(
                variable="LAI",
                observations=[
                    TimestampedObservation(
                        t="2026-02-15",
                        variable="LAI",
                        obs=ValueWithUncertainty(value=1.0, std=0.1),
                    ),
                ],
                weight=1.0,
            )
        ]
        val = validate_holdout({}, targets, _perfect_predictor)
        assert val.rmse["LAI"] == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# ValidationMetrics
# ---------------------------------------------------------------------------


class TestValidationMetrics:
    def test_frozen(self):
        vm = ValidationMetrics(rmse={"LAI": 0.5}, mae={"LAI": 0.4}, bias={"LAI": 0.1})
        with pytest.raises(AttributeError):
            vm.rmse = {}  # type: ignore[misc]

    def test_basic(self):
        vm = ValidationMetrics(rmse={"LAI": 0.5}, mae={"LAI": 0.3}, bias={"LAI": 0.1})
        assert vm.rmse["LAI"] == 0.5
        assert vm.mae["LAI"] == 0.3
        assert vm.bias["LAI"] == 0.1
