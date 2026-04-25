# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.edge_resilience — Edge Hardware Resilience (ADR-014)
============================================================

Phase 4 implementation. Exposes value objects, the WAL, the power monitor,
and the backpressure controller.
"""

from __future__ import annotations

from .backpressure import BackpressureController
from .models import (
    BackpressureLevel,
    PowerState,
    ResilienceConfig,
    WALEntry,
)
from .power_monitor import DEFAULT_POLL_INTERVAL_S, PowerMonitor
from .wal import WriteAheadLog

__all__ = [
    "DEFAULT_POLL_INTERVAL_S",
    "BackpressureController",
    "BackpressureLevel",
    "PowerMonitor",
    "PowerState",
    "ResilienceConfig",
    "WALEntry",
    "WriteAheadLog",
]
