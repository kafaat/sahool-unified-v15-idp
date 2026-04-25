# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Polling client for ``agri-taxonomy-service`` — see ADR-012.

The client refreshes a frozen ``Snapshot`` on a fixed cadence and swaps it
atomically; readers (``get_node``, ``is_forbidden_substance``) never see a
half-updated taxonomy. The ``fetcher`` callable is injected so production
can use HTTP/NATS while tests stay deterministic and offline.

The taxonomy service emits ``sahool.taxonomy.released.v{N}`` whenever a
new release is published. The client can either:

* Poll on ``refresh_seconds`` cadence (always-on path, default).
* **And/or** wake up the polling loop early when a NATS notification
  arrives, via the optional ``notifier`` injected at construction. The
  notifier is a generic async iterator of "release" events so production
  can plug NATS while tests use a plain ``asyncio.Queue``.

Both paths are belt-and-braces — the polling cadence remains the
authoritative freshness budget, the notifier just lets clients react
within milliseconds instead of seconds when the release is broadcast.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from .models import TaxonomyEdge, TaxonomyNode, TaxonomyVersion

log = logging.getLogger(__name__)

#: Type alias for the injectable fetcher. Returns the next snapshot on each call.
TaxonomyFetcher = Callable[[], Awaitable["Snapshot"]]

#: Type alias for the optional release-notifier. Production wires this to a
#: NATS subscription on ``sahool.taxonomy.released.v{N}``; tests pass a
#: plain async generator. Yielded values are opaque — the client treats
#: every event as "refresh now".
TaxonomyNotifier = Callable[[], AsyncIterator[Any]]


@dataclass(frozen=True)
class Snapshot:
    """Immutable taxonomy snapshot; ``TaxonomyClient`` swaps these atomically."""

    version: TaxonomyVersion
    nodes: dict[UUID, TaxonomyNode]
    edges: tuple[TaxonomyEdge, ...] = ()
    forbidden_substances: frozenset[UUID] = frozenset()


class TaxonomyClient:
    """In-process client with a configurable refresh window and atomic snapshot swap.

    Phase 4 implements the polling loop and an optional NATS-style
    ``notifier`` that triggers an immediate refresh on
    ``sahool.taxonomy.released.v{N}`` events. Lookups read directly from
    the latest snapshot — there is no separate LRU cache because the
    snapshot itself is the cache and is swapped atomically on refresh.
    """

    def __init__(
        self,
        base_url: str,
        refresh_seconds: int = 30,
        *,
        fetcher: TaxonomyFetcher | None = None,
        notifier: TaxonomyNotifier | None = None,
    ) -> None:
        if refresh_seconds <= 0:
            raise ValueError("refresh_seconds must be positive")
        self.base_url = base_url
        self.refresh_seconds = refresh_seconds
        self._fetcher: TaxonomyFetcher | None = fetcher
        self._notifier: TaxonomyNotifier | None = notifier
        self._snapshot: Snapshot | None = None
        self._task: asyncio.Task[Any] | None = None
        self._notifier_task: asyncio.Task[Any] | None = None
        self._stop_event: asyncio.Event | None = None
        self._wake_event: asyncio.Event | None = None
        self._fetch_lock: asyncio.Lock | None = None

    # -- lifecycle -------------------------------------------------------

    async def start(self) -> None:
        """Fetch once synchronously, then run a background refresh loop.

        ``start()`` is idempotent; calling it twice is a no-op.
        """

        if self._task is not None and not self._task.done():
            return
        if self._fetcher is None:
            raise RuntimeError("TaxonomyClient requires a fetcher (injected for tests, HTTP/NATS in production)")
        # First refresh is awaited so callers can rely on the snapshot
        # being populated immediately after ``start()`` returns.
        self._snapshot = await self._fetcher()
        self._stop_event = asyncio.Event()
        self._wake_event = asyncio.Event()
        self._fetch_lock = asyncio.Lock()
        self._task = asyncio.create_task(self._refresh_loop(), name="taxonomy-refresh")
        if self._notifier is not None:
            self._notifier_task = asyncio.create_task(self._notifier_loop(), name="taxonomy-notifier")

    async def stop(self) -> None:
        """Stop the refresh loop and the optional notifier loop. Idempotent."""

        if self._stop_event is not None:
            self._stop_event.set()
        if self._wake_event is not None:
            # Unblock any pending wait in the polling loop so it can exit.
            self._wake_event.set()
        for task_attr in ("_task", "_notifier_task"):
            task = getattr(self, task_attr)
            if task is None:
                continue
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):  # pragma: no cover
                pass
            setattr(self, task_attr, None)
        self._stop_event = None
        self._wake_event = None
        self._fetch_lock = None

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
        assert self._wake_event is not None
        while not self._stop_event.is_set():
            # Wait for either the refresh interval to elapse or the
            # notifier to fire (``_wake_event`` is set by
            # ``_notifier_loop``). ``stop()`` also sets the wake event,
            # which lets us exit promptly.
            try:
                await asyncio.wait_for(
                    self._wake_event.wait(),
                    timeout=self.refresh_seconds,
                )
            except TimeoutError:
                pass
            if self._stop_event.is_set():
                return
            self._wake_event.clear()
            await self._fetch_and_swap()

    async def _notifier_loop(self) -> None:
        assert self._notifier is not None
        assert self._wake_event is not None
        assert self._stop_event is not None
        try:
            async for _event in self._notifier():
                if self._stop_event.is_set():
                    return
                # Wake the polling loop. The actual fetch happens there
                # so we never have two concurrent fetches racing on the
                # snapshot swap.
                self._wake_event.set()
        except (asyncio.CancelledError, Exception):  # pragma: no cover
            return

    async def _fetch_and_swap(self) -> None:
        assert self._fetcher is not None
        assert self._fetch_lock is not None
        async with self._fetch_lock:
            try:
                snap = await self._fetcher()
            except Exception:
                # Keep the last good snapshot but surface the failure so
                # operators can tell when the taxonomy has stopped
                # refreshing. Silent failure here masks staleness in
                # production (review feedback #10).
                log.warning(
                    "taxonomy_client.fetch_failed",
                    extra={"base_url": self.base_url},
                    exc_info=True,
                )
                return
            # Atomic single-attribute swap is the snapshot guarantee
            # callers rely on; readers always see a fully-formed Snapshot.
            self._snapshot = snap
