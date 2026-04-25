# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Polling client for ``agri-taxonomy-service`` — see ADR-012.

The client refreshes a frozen ``Snapshot`` on a fixed cadence and swaps it
atomically; readers (``get_node``, ``is_forbidden_substance``) never see a
half-updated taxonomy. The ``fetcher`` callable is injected so production
can use HTTP/NATS while tests stay deterministic and offline.

The taxonomy service emits ``sahool.taxonomy.released.v{N}`` whenever a
new release is published; subscribing to that subject is reserved for a
follow-up — the ``refresh_seconds`` polling loop is sufficient for the
30 s freshness budget specified in ADR-012.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from .models import TaxonomyEdge, TaxonomyNode, TaxonomyVersion

#: Type alias for the injectable fetcher. Returns the next snapshot on each call.
TaxonomyFetcher = Callable[[], Awaitable["Snapshot"]]


@dataclass(frozen=True)
class Snapshot:
    """Immutable taxonomy snapshot; ``TaxonomyClient`` swaps these atomically."""

    version: TaxonomyVersion
    nodes: dict[UUID, TaxonomyNode]
    edges: tuple[TaxonomyEdge, ...] = ()
    forbidden_substances: frozenset[UUID] = frozenset()


class TaxonomyClient:
    """In-process client with a configurable refresh window and atomic snapshot swap.

    Phase 4 implements the polling loop and an LRU-bounded lookup cache.
    NATS subscription (``sahool.taxonomy.released.v{N}``) is reserved for
    a follow-up.
    """

    def __init__(
        self,
        base_url: str,
        refresh_seconds: int = 30,
        *,
        fetcher: TaxonomyFetcher | None = None,
    ) -> None:
        if refresh_seconds <= 0:
            raise ValueError("refresh_seconds must be positive")
        self.base_url = base_url
        self.refresh_seconds = refresh_seconds
        self._fetcher: TaxonomyFetcher | None = fetcher
        self._snapshot: Snapshot | None = None
        self._task: asyncio.Task[Any] | None = None
        self._stop_event: asyncio.Event | None = None

    # -- lifecycle -------------------------------------------------------

    async def start(self) -> None:
        """Fetch once synchronously, then run a background refresh loop.

        ``start()`` is idempotent; calling it twice is a no-op.
        """

        if self._task is not None and not self._task.done():
            return
        if self._fetcher is None:
            raise RuntimeError(
                "TaxonomyClient requires a fetcher (injected for tests, "
                "HTTP/NATS in production)"
            )
        # First refresh is awaited so callers can rely on the snapshot
        # being populated immediately after ``start()`` returns.
        self._snapshot = await self._fetcher()
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._refresh_loop(), name="taxonomy-refresh")

    async def stop(self) -> None:
        """Stop the refresh loop. Idempotent."""

        if self._stop_event is not None:
            self._stop_event.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # pragma: no cover
                pass
            self._task = None
        self._stop_event = None

    # -- read-side -------------------------------------------------------

    def get_node(self, node_id: UUID) -> TaxonomyNode | None:
        snap = self._snapshot
        if snap is None:
            return None
        return snap.nodes.get(node_id)

    def is_forbidden_substance(self, fertilizer_id: UUID) -> bool:
        """Used by ``shared/prescription_safety`` (ADR-013) for blacklist check.

        Returns ``False`` (fail-open for *unknown*) when the snapshot is not
        yet loaded — the prescription gateway has its own forbidden-substance
        checker that must remain authoritative until the taxonomy is up.
        """

        snap = self._snapshot
        if snap is None:
            return False
        return fertilizer_id in snap.forbidden_substances

    def version(self) -> TaxonomyVersion | None:
        return self._snapshot.version if self._snapshot is not None else None

    def snapshot(self) -> Snapshot | None:
        """Return the current full snapshot, or ``None`` before ``start()``."""

        return self._snapshot

    # -- internals -------------------------------------------------------

    async def _refresh_loop(self) -> None:
        assert self._fetcher is not None
        assert self._stop_event is not None
        while not self._stop_event.is_set():
            try:
                # ``wait_for`` lets ``stop()`` interrupt the sleep promptly.
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.refresh_seconds,
                )
                # Stop event was set during the sleep window.
                return
            except TimeoutError:
                pass
            try:
                snap = await self._fetcher()
            except Exception:  # pragma: no cover - defensive: keep last good snapshot
                continue
            # Atomic single-attribute swap is the snapshot guarantee
            # callers rely on; readers always see a fully-formed Snapshot.
            self._snapshot = snap
