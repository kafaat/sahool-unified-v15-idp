# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""NATS adapter for taxonomy release events (ADR-012, Phase 4).

The adapter is intentionally tiny:

* ``build_release_publisher(nats_url)`` returns a ``ReleasePublisher``
  callable matching :data:`store.ReleasePublisher`.
* If ``nats_url`` is empty / ``None``, returns a no-op publisher so the
  service still boots cleanly in dev / unit-test environments without
  a NATS broker.
* The connection is lazy — established on the first publish attempt —
  so service startup never blocks on NATS being reachable.

Subject convention (ADR-012):

    sahool.taxonomy.released.v{major}

where ``major`` is the SemVer major of the new release. Clients
subscribe per-major to avoid being woken up by patch / minor releases
they're already compatible with.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import asdict

from .store import ReleaseEvent

log = logging.getLogger(__name__)

#: Public alias matches ``store.ReleasePublisher``.
ReleasePublisher = Callable[[ReleaseEvent], Awaitable[None]]


def build_release_publisher(nats_url: str | None) -> ReleasePublisher:
    """Return a publisher bound to ``nats_url`` (or a no-op when unset)."""

    if not nats_url:
        return _noop_publisher

    state: dict[str, object] = {"connection": None}

    async def publish(event: ReleaseEvent) -> None:
        try:
            import nats  # type: ignore[import-not-found]
        except ImportError:  # pragma: no cover - defensive: optional dep
            log.warning("taxonomy.nats_unavailable_skipping_publish")
            return

        connection = state.get("connection")
        if connection is None:
            connection = await nats.connect(nats_url)
            state["connection"] = connection

        major = event.semver.split(".", 1)[0]
        subject = f"sahool.taxonomy.released.v{major}"
        payload = json.dumps(_serialize(event)).encode()
        await connection.publish(subject, payload)

    return publish


async def _noop_publisher(event: ReleaseEvent) -> None:  # noqa: ARG001
    """Drops the event; used when NATS isn't configured."""

    return None


def _serialize(event: ReleaseEvent) -> dict[str, object]:
    payload = asdict(event)
    # ``released_at`` is a datetime — make the JSON shape explicit.
    payload["released_at"] = event.released_at.isoformat()
    return payload
