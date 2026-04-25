# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Full Extended Kalman Filter. Skeleton — see ADR-011."""

from __future__ import annotations

from .models import FusedState, FusionConfig, SensorFrame


class EKF:
    """Extended Kalman Filter with full covariance.

    Distinct from ``shared/digital_twin/assimilation.py`` (Kalman-lite):
    this class computes process / observation Jacobians at each step.
    Phase 4 implementation.
    """

    def __init__(self, config: FusionConfig) -> None:
        self.config = config

    def predict(self, dt_seconds: float) -> None:
        raise NotImplementedError("ADR-011: implemented in Phase 4")

    def update(self, frame: SensorFrame) -> None:
        raise NotImplementedError("ADR-011: implemented in Phase 4")

    def state(self) -> FusedState:
        raise NotImplementedError("ADR-011: implemented in Phase 4")
