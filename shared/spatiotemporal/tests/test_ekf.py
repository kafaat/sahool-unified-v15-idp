# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the EKF channel-fusion filter (ADR-011)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from shared.spatiotemporal import EKF, FusionConfig, SensorFrame


def _frame(ms: int, ndvi: float, var: float = 0.01) -> SensorFrame:
    return SensorFrame(
        sensor_id="s",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(milliseconds=ms),
        position=(0.0, 0.0, None),
        values={"ndvi": ndvi},
        covariance={"ndvi": var},
    )


def test_first_observation_initialises_state() -> None:
    ekf = EKF(FusionConfig())
    ekf.update(_frame(0, 0.6))
    state = ekf.state()
    assert state.state["ndvi"] == pytest.approx(0.6, abs=1e-6)


def test_repeated_consistent_observations_reduce_variance() -> None:
    ekf = EKF(FusionConfig())
    for i in range(5):
        ekf.update(_frame(i * 1, 0.5, var=0.01))
    final = ekf.state()
    assert final.state["ndvi"] == pytest.approx(0.5, abs=1e-3)
    # Variance must shrink monotonically with more measurements.
    assert final.covariance[("ndvi", "ndvi")] < 0.01


def test_predict_inflates_variance_with_dt() -> None:
    ekf = EKF(FusionConfig(process_noise={"ndvi": 0.05}))
    ekf.update(_frame(0, 0.6, var=0.01))
    before = ekf.state().covariance[("ndvi", "ndvi")]
    ekf.predict(dt_seconds=2.0)
    after = ekf.state().covariance[("ndvi", "ndvi")]
    assert after == pytest.approx(before + 0.05 * 2.0, abs=1e-9)


def test_negative_dt_rejected() -> None:
    ekf = EKF(FusionConfig())
    with pytest.raises(ValueError):
        ekf.predict(-0.1)


def test_observation_jacobian_scales_kalman_gain() -> None:
    """A Jacobian H = 2 should converge twice as fast as H = 1 on the same data.

    Sensor reports z = 2x + noise, so we estimate x by inverting the
    observation model. With variance r = 0.01 and prior P0 = 1, the
    closed-form posterior mean after one update is
    ``x* = (H * z) / (H^2 + r)`` ≈ 1.0/4.01 = 0.2494 for z = 1.0.
    """

    ekf = EKF(
        FusionConfig(),
        observation_jacobian=lambda key, x: 2.0,
        observation_model=lambda key, x: 2.0 * x,
    )
    # Initial prior x0 = 0, P0 = 1.0 (set by first update auto-init).
    # Force prior init by seeding once with the model at x=0:
    f0 = SensorFrame(
        sensor_id="s",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        position=(0.0, 0.0, None),
        values={"x": 0.0},
        covariance={"x": 1e-12},  # near-perfect to lock the prior at 0
    )
    ekf.update(f0)
    # Now feed a measurement z = 1.0 with R = 0.01.
    f1 = SensorFrame(
        sensor_id="s",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(milliseconds=1),
        position=(0.0, 0.0, None),
        values={"x": 1.0},
        covariance={"x": 0.01},
    )
    ekf.update(f1)
    state = ekf.state()
    # Estimate must move toward 0.5 (the "true" x given z = 2x = 1).
    assert 0.0 < state.state["x"] < 0.5


def test_observation_jacobian_falls_back_to_identity() -> None:
    """Default behaviour (no Jacobian) is preserved for callers that don't pass one."""

    ekf_default = EKF(FusionConfig())
    ekf_explicit_identity = EKF(FusionConfig(), observation_jacobian=lambda k, x: 1.0)
    f = _frame(0, 0.6, var=0.01)
    ekf_default.update(f)
    ekf_explicit_identity.update(f)
    assert ekf_default.state().state["ndvi"] == pytest.approx(ekf_explicit_identity.state().state["ndvi"], abs=1e-12)
    assert ekf_default.state().covariance[("ndvi", "ndvi")] == pytest.approx(
        ekf_explicit_identity.state().covariance[("ndvi", "ndvi")], abs=1e-12
    )


def test_handles_multiple_independent_channels() -> None:
    ekf = EKF(FusionConfig())
    f = SensorFrame(
        sensor_id="s",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        position=(0.0, 0.0, None),
        values={"ndvi": 0.7, "soil_moisture": 0.32},
        covariance={"ndvi": 0.01, "soil_moisture": 0.04},
    )
    ekf.update(f)
    state = ekf.state()
    assert state.state["ndvi"] == pytest.approx(0.7)
    assert state.state["soil_moisture"] == pytest.approx(0.32)
    # Independent channels mean only diagonal covariance entries are set.
    assert ("ndvi", "soil_moisture") not in state.covariance
