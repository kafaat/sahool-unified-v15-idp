# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Value objects for spatio-temporal fusion. Skeleton — see ADR-011."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SensorFrame:
    """Single observation from one sensor stream.

    Attributes:
        sensor_id:   Stable identifier of the source sensor / device.
        timestamp:   UTC timestamp of the observation.
        position:    (lat, lon, alt_m) tuple. ``alt_m`` may be ``None``.
        values:      Sensor-specific payload (e.g., ``{"ndvi": 0.72}``).
        covariance:  Diagonal covariance for the values, in the same order
                     as ``values``. Empty dict means "unknown — use prior".
        tenant_id:   UUID string from JWT ``tid`` claim.
    """

    sensor_id: str
    timestamp: datetime
    position: tuple[float, float, float | None]
    values: dict[str, float]
    covariance: dict[str, float] = field(default_factory=dict)
    tenant_id: str = ""


@dataclass(frozen=True)
class FusedState:
    """Output of one fusion step."""

    timestamp: datetime
    state: dict[str, float]
    covariance: dict[tuple[str, str], float]
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FusionConfig:
    """Configuration for a fusion run.

    ``mode`` is ``"lite"`` (Kalman-lite fallback) or ``"full"`` (EKF).
    ``alignment_window_ms`` is fixed at 500 ms by ADR-011.
    """

    mode: str = "full"
    alignment_window_ms: int = 500
    process_noise: dict[str, float] = field(default_factory=dict)
    max_iters: int = 25
