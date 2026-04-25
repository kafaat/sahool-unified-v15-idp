# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Value objects for edge resilience. Skeleton — see ADR-014."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PowerState(str, Enum):
    """Discrete power-supply states reported by ``PowerMonitor``."""

    NORMAL = "NORMAL"
    SHUTDOWN_SOON = "SHUTDOWN_SOON"  # supercap discharge has begun
    UNKNOWN = "UNKNOWN"  # no GPIO configured (best-effort mode)


class BackpressureLevel(str, Enum):
    """Discrete backpressure states (80 / 60 % hysteresis)."""

    NORMAL = "NORMAL"
    STALLED = "STALLED"


@dataclass(frozen=True)
class WALEntry:
    """One append-only entry in the local WAL."""

    sequence: int
    timestamp: datetime
    payload: bytes
    crc32: int


@dataclass(frozen=True)
class ResilienceConfig:
    """Tunables for the edge resilience controller."""

    wal_path: str = "/var/sahool/wal"
    wal_max_bytes: int = 1 << 30  # 1 GiB
    supercap_gpio: int | None = None
    backpressure_high: float = 0.80
    backpressure_low: float = 0.60
    fsync_batch_size: int = 16
