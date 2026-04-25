# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Power-good monitor. Skeleton — see ADR-014."""

from __future__ import annotations

from collections.abc import AsyncIterator

from .models import PowerState, ResilienceConfig


class PowerMonitor:
    """Subscribes to a GPIO / sysfs power-good line.

    When supercap discharge starts, transitions to ``SHUTDOWN_SOON`` and
    the orchestrator has at least 5 s to flush WAL + close NATS cleanly.
    Devices without a configured GPIO operate in best-effort mode and
    only ever report ``UNKNOWN`` / ``NORMAL``.
    """

    def __init__(self, config: ResilienceConfig) -> None:
        self.config = config

    async def states(self) -> AsyncIterator[PowerState]:
        """Async generator yielding power-state transitions.

        Phase 4 implementation.
        """

        raise NotImplementedError("ADR-014: implemented in Phase 4")
