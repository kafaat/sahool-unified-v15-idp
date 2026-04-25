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
from dataclasses import asdict, dataclass

from .store import ReleaseEvent

log = logging.getLogger(__name__)

#: Public alias matches ``store.ReleasePublisher``.
ReleasePublisher = Callable[[ReleaseEvent], Awaitable[None]]


@dataclass
class PublisherHandle:
    """Bundle of (publish callable, close callable) returned from the factory.

    The lifespan owns both handles so the cached connection can be drained
    cleanly during shutdown. ``close`` is always safe to call (idempotent
    and a no-op when no connection was ever established).
    """

    publish: ReleasePublisher
    close: Callable[[], Awaitable[None]]


def build_release_publisher(nats_url: str | None) -> PublisherHandle:
    """Return a (publish, close) pair bound to ``nats_url``.

    When ``nats_url`` is empty/``None`` the publisher drops events and the
    closer is a no-op.
    """

    if not nats_url:
        return PublisherHandle(publish=_noop_publisher, close=_noop_close)

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

    async def close() -> None:
        connection = state.get("connection")
        if connection is None:
            return
        # Drain flushes pending publishes then closes the socket — preferred
        # over `.close()` to avoid losing buffered taxonomy release events.
        try:
            drain = getattr(connection, "drain", None)
            if drain is not None:
                await drain()
            else:  # pragma: no cover - older nats-py without drain()
                await connection.close()
        except Exception:  # pragma: no cover - shutdown best-effort
            log.exception("taxonomy.nats_close_failed")
        finally:
            state["connection"] = None

    return PublisherHandle(publish=publish, close=close)


async def _noop_publisher(event: ReleaseEvent) -> None:  # noqa: ARG001
    """Drops the event; used when NATS isn't configured."""

    return None


async def _noop_close() -> None:
    return None


def _serialize(event: ReleaseEvent) -> dict[str, object]:
    payload = asdict(event)
    # ``released_at`` is a datetime — make the JSON shape explicit.
    payload["released_at"] = event.released_at.isoformat()
    return payload
