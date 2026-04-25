# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.edge_resilience — Edge Hardware Resilience (ADR-014)
============================================================

Skeleton package. See ``README.md`` and
``docs/adr/ADR-014-edge-hardware-resilience.md``.
"""

from __future__ import annotations

from .models import (
    BackpressureLevel,
    PowerState,
    ResilienceConfig,
    WALEntry,
)

__all__ = ["BackpressureLevel", "PowerState", "ResilienceConfig", "WALEntry"]
