# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Extended Kalman Filter with diagonal-covariance state — see ADR-011.

Distinct from ``shared/digital_twin/assimilation.py`` (Kalman-lite, scalar):
this class maintains an independent EKF channel **per state key**, which is
the form ADR-011 needs for sensor fusion of heterogeneous channels (NDVI,
soil moisture, temperature, etc.) without a hand-coded joint Jacobian.

The "EKF" name is preserved — the predict step trivially linearises an
identity dynamic model (state is constant unless updated), and the update
step linearises the observation model around the current estimate.
Non-identity sensors plug a non-trivial scalar Jacobian via
``observation_jacobian`` (and an optional non-linear ``observation_model``)
which is exactly the EKF generalisation point ADR-011 reserved.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from .models import FusedState, FusionConfig, SensorFrame

_DEFAULT_PROCESS_NOISE = 1e-4
_DEFAULT_MEASUREMENT_NOISE = 1e-2
_INITIAL_VARIANCE = 1.0

#: Signature of the observation-Jacobian callback. Receives
#: ``(channel_key, current_estimate)`` and returns the scalar
#: ``H = ∂h/∂x`` for that channel at that operating point.
ObservationJacobian = Callable[[str, float], float]


class EKF:
    """Extended Kalman Filter with per-channel diagonal covariance.

    Phase 4 implementation. Each state key tracks ``(x_hat, P)``; the
    predict step inflates ``P`` by ``q * dt`` (process noise from
    ``FusionConfig.process_noise``); the update step is the standard
    scalar EKF on each channel that the incoming frame supplies.

    Non-identity sensors (e.g. radiance → reflectance, raw ADC → SI
    units) inject an ``observation_jacobian`` callback that returns the
    scalar Jacobian ``H = ∂h/∂x`` per channel; the default ``H = 1``
    keeps the original direct-observation behaviour.
    """

    def __init__(
        self,
        config: FusionConfig,
        *,
        observation_jacobian: ObservationJacobian | None = None,
        observation_model: Callable[[str, float], float] | None = None,
    ) -> None:
        self.config = config
        self._mean: dict[str, float] = {}
        self._var: dict[str, float] = {}
        self._last_ts: datetime | None = None
        self._jac = observation_jacobian
        self._h = observation_model

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

        For each channel the scalar EKF is::

            innov = z - h(x_hat)             # h defaults to identity
            H     = observation_jacobian(k, x_hat)   # default 1.0
            S     = H * P * H + R
            K     = P * H / S
            x_hat = x_hat + K * innov
            P     = (1 - K * H) * P

        With ``observation_jacobian=None`` and ``observation_model=None``
        the recursion collapses to the identity-Jacobian update used by
        the v3.1 sensors (NDVI, soil moisture, temperature, ...).
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

            h_jac = self._jac(key, x) if self._jac is not None else 1.0
            predicted = self._h(key, x) if self._h is not None else x

            # Scalar EKF update with non-identity Jacobian.
            innov = z - predicted
            s = h_jac * p * h_jac + r
            k = (p * h_jac) / s
            self._mean[key] = x + k * innov
            self._var[key] = (1.0 - k * h_jac) * p

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
