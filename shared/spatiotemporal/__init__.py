# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.spatiotemporal — Spatio-Temporal Sensor Fusion (ADR-011)
================================================================

Phase 4 implementation. Exposes value objects, time alignment, cubic
resampling, an EKF, and a factor-graph batch optimizer.
"""

from __future__ import annotations

from .alignment import align_streams
from .ekf import EKF, ObservationJacobian
from .factor_graph import FactorGraph
from .interpolation import resample_cubic
from .models import FusedState, FusionConfig, SensorFrame

__all__ = [
    "EKF",
    "FactorGraph",
    "FusedState",
    "FusionConfig",
    "ObservationJacobian",
    "SensorFrame",
    "align_streams",
    "resample_cubic",
]
