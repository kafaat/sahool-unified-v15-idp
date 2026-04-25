# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Crash-safe append-only WAL on eMMC. Skeleton — see ADR-014."""

from __future__ import annotations

from collections.abc import Iterable

from .models import ResilienceConfig, WALEntry


class WriteAheadLog:
    """Append-only write-ahead log with ``O_DSYNC`` + ``fdatasync`` barriers.

    Crash-safety contract: after ``append()`` returns, the entry survives
    abrupt power-loss. Batched writes amortize fsync cost (see
    ``ResilienceConfig.fsync_batch_size``).
    """

    def __init__(self, config: ResilienceConfig) -> None:
        self.config = config

    async def append(self, payload: bytes) -> WALEntry:
        raise NotImplementedError("ADR-014: implemented in Phase 4")

    async def replay(self) -> Iterable[WALEntry]:
        raise NotImplementedError("ADR-014: implemented in Phase 4")

    async def truncate_to(self, sequence: int) -> None:
        """Discard entries up to and including ``sequence`` (after ack)."""

        raise NotImplementedError("ADR-014: implemented in Phase 4")

    def fill_ratio(self) -> float:
        """Return current WAL utilization in [0.0, 1.0]."""

        raise NotImplementedError("ADR-014: implemented in Phase 4")
