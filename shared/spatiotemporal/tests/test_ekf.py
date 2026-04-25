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
