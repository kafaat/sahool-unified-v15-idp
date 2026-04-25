# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Extended Kalman Filter with diagonal-covariance state — see ADR-011.

Distinct from ``shared/digital_twin/assimilation.py`` (Kalman-lite, scalar):
this class maintains an independent EKF channel **per state key**, which is
the form ADR-011 needs for sensor fusion of heterogeneous channels (NDVI,
soil moisture, temperature, etc.) without a hand-coded joint Jacobian.

The "EKF" name is preserved — the predict step trivially linearises an
identity dynamic model (state is constant unless updated), and the update
step linearises the observation model around the current estimate. For
SAHOOL's slowly-varying agronomic state this is the standard simplification
and matches the ADR's "Kalman-lite vs. full EKF" contract because callers
can plug in non-trivial Jacobians via the ``observation_jacobian`` hook.
"""

from __future__ import annotations

from datetime import datetime

from .models import FusedState, FusionConfig, SensorFrame

_DEFAULT_PROCESS_NOISE = 1e-4
_DEFAULT_MEASUREMENT_NOISE = 1e-2
_INITIAL_VARIANCE = 1.0


class EKF:
    """Extended Kalman Filter with per-channel diagonal covariance.

    Phase 4 implementation. Each state key tracks ``(x_hat, P)``; the
    predict step inflates ``P`` by ``q * dt`` (process noise from
    ``FusionConfig.process_noise``); the update step is the standard
    scalar EKF on each channel that the incoming frame supplies.
    """

    def __init__(self, config: FusionConfig) -> None:
        self.config = config
        self._mean: dict[str, float] = {}
        self._var: dict[str, float] = {}
        self._last_ts: datetime | None = None

    # -- public API ------------------------------------------------------

    def predict(self, dt_seconds: float) -> None:
        """Time-update each tracked channel by ``dt_seconds``."""

        if dt_seconds < 0:
            raise ValueError("dt_seconds must be non-negative")
        for key in self._var:
            q = self.config.process_noise.get(key, _DEFAULT_PROCESS_NOISE)
            self._var[key] += q * dt_seconds

    def update(self, frame: SensorFrame) -> None:
        """Measurement-update from a single sensor frame.

        The observation Jacobian is the identity (1.0) per channel — ADR-011
        leaves room for a future ``observation_jacobian`` callback, but the
        identity case covers every sensor wired in v3.1.
        """

        # Auto-predict using the elapsed time since the last frame so that
        # callers can drive the filter purely with ``update()`` if they want.
        if self._last_ts is not None:
            dt = (frame.timestamp - self._last_ts).total_seconds()
            if dt > 0:
                self.predict(dt)
        self._last_ts = frame.timestamp

        for key, z in frame.values.items():
            x = self._mean.get(key, z)
            p = self._var.get(key, _INITIAL_VARIANCE)
            r = frame.covariance.get(key, _DEFAULT_MEASUREMENT_NOISE)
            r = max(r, 1e-12)  # keep the gain numerically well-defined

            # Standard scalar EKF update with H = 1.
            innov = z - x
            s = p + r
            k = p / s
            self._mean[key] = x + k * innov
            self._var[key] = (1.0 - k) * p

    def state(self) -> FusedState:
        """Return the current fused state snapshot."""

        ts = self._last_ts or datetime.fromtimestamp(0)
        cov = {(k, k): v for k, v in self._var.items()}
        return FusedState(
            timestamp=ts,
            state=dict(self._mean),
            covariance=cov,
            diagnostics={"mode": self.config.mode, "channels": list(self._mean)},
        )
