# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the agri-taxonomy polling client (ADR-012)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from shared.agri_taxonomy_client import (
    Snapshot,
    Synonym,
    TaxonomyClient,
    TaxonomyNode,
    TaxonomyVersion,
)


def _node(kind: str = "fertilizer") -> TaxonomyNode:
    return TaxonomyNode(
        id=uuid4(),
        kind=kind,
        parent_id=None,
        synonyms=[Synonym(language="en", label="Test", is_preferred=True)],
    )


def _snapshot(
    nodes: list[TaxonomyNode],
    forbidden: frozenset[UUID] = frozenset(),
    semver: str = "1.0.0",
) -> Snapshot:
    version = TaxonomyVersion(
        semver=semver,
        released_at=datetime(2026, 1, 1, tzinfo=UTC),
        checksum_sha256="0" * 64,
    )
    return Snapshot(
        version=version,
        nodes={n.id: n for n in nodes},
        forbidden_substances=forbidden,
    )


@pytest.mark.asyncio
async def test_start_requires_fetcher() -> None:
    client = TaxonomyClient("http://taxonomy.local")
    with pytest.raises(RuntimeError, match="fetcher"):
        await client.start()


@pytest.mark.asyncio
async def test_start_loads_initial_snapshot_synchronously() -> None:
    node = _node()
    snap = _snapshot([node])

    async def fetcher() -> Snapshot:
        return snap

    client = TaxonomyClient("http://t", refresh_seconds=60, fetcher=fetcher)
    try:
        await client.start()
        assert client.version() is not None
        assert client.version().semver == "1.0.0"
        assert client.get_node(node.id) == node
    finally:
        await client.stop()


@pytest.mark.asyncio
async def test_unknown_node_returns_none_before_and_after_start() -> None:
    snap = _snapshot([_node()])

    async def fetcher() -> Snapshot:
        return snap

    client = TaxonomyClient("http://t", refresh_seconds=60, fetcher=fetcher)
    assert client.get_node(uuid4()) is None  # before start
    try:
        await client.start()
        assert client.get_node(uuid4()) is None  # after start, unknown id
    finally:
        await client.stop()


@pytest.mark.asyncio
async def test_is_forbidden_substance_uses_snapshot_set() -> None:
    forbidden_id = uuid4()
    safe_id = uuid4()
    snap = _snapshot(
        [
            TaxonomyNode(id=forbidden_id, kind="fertilizer", parent_id=None),
            TaxonomyNode(id=safe_id, kind="fertilizer", parent_id=None),
        ],
        forbidden=frozenset({forbidden_id}),
    )

    async def fetcher() -> Snapshot:
        return snap

    client = TaxonomyClient("http://t", refresh_seconds=60, fetcher=fetcher)
    try:
        await client.start()
        assert client.is_forbidden_substance(forbidden_id) is True
        assert client.is_forbidden_substance(safe_id) is False
    finally:
        await client.stop()


@pytest.mark.asyncio
async def test_is_forbidden_substance_returns_false_before_start() -> None:
    # Fail-open for "unknown" — the prescription gateway has its own
    # authoritative checker until the taxonomy snapshot is loaded.
    client = TaxonomyClient("http://t", refresh_seconds=60, fetcher=None)
    assert client.is_forbidden_substance(uuid4()) is False


@pytest.mark.asyncio
async def test_refresh_loop_swaps_snapshot_atomically() -> None:
    versions = ["1.0.0", "1.0.1", "1.0.2"]
    counter = {"i": 0}
    fetched = asyncio.Event()

    async def fetcher() -> Snapshot:
        i = counter["i"]
        counter["i"] = min(i + 1, len(versions) - 1)
        snap = _snapshot([_node()], semver=versions[i])
        if i > 0:
            fetched.set()
        return snap

    # Sub-second refresh interval keeps the test fast.
    client = TaxonomyClient("http://t", refresh_seconds=1, fetcher=fetcher)
    try:
        await client.start()
        assert client.version().semver == "1.0.0"
        # Wait for the second fetch to occur.
        await asyncio.wait_for(fetched.wait(), timeout=3.0)
        assert client.version().semver in {"1.0.1", "1.0.2"}
    finally:
        await client.stop()


@pytest.mark.asyncio
async def test_stop_is_idempotent_and_safe_before_start() -> None:
    client = TaxonomyClient("http://t", refresh_seconds=60)
    await client.stop()  # never started — must not raise
    await client.stop()  # second call — must not raise


def test_invalid_refresh_seconds_rejected() -> None:
    with pytest.raises(ValueError):
        TaxonomyClient("http://t", refresh_seconds=0)


@pytest.mark.asyncio
async def test_notifier_triggers_immediate_refresh() -> None:
    """A notifier event must wake the polling loop and refresh the
    snapshot in well under ``refresh_seconds`` — that is the whole
    point of subscribing to ``sahool.taxonomy.released.v{N}``.
    """

    versions = ["1.0.0", "1.0.1", "1.0.2"]
    counter = {"i": 0}

    async def fetcher() -> Snapshot:
        i = counter["i"]
        counter["i"] = min(i + 1, len(versions) - 1)
        return _snapshot([_node()], semver=versions[i])

    queue: asyncio.Queue[str] = asyncio.Queue()

    async def notifier():
        # Yields whatever ``queue`` produces until cancellation.
        while True:
            event = await queue.get()
            yield event

    # Long polling interval means only the notifier can drive the refresh.
    client = TaxonomyClient(
        "http://t", refresh_seconds=3600, fetcher=fetcher, notifier=notifier
    )
    try:
        await client.start()
        assert client.version().semver == "1.0.0"
        # Push a release event; the polling loop must wake up and refresh.
        await queue.put("released")
        # Spin briefly — the refresh has to complete on the event loop.
        for _ in range(50):
            await asyncio.sleep(0.01)
            if client.version().semver != "1.0.0":
                break
        assert client.version().semver in {"1.0.1", "1.0.2"}
    finally:
        await client.stop()


@pytest.mark.asyncio
async def test_notifier_is_optional() -> None:
    """Passing no notifier must keep the v3.1 polling-only behaviour."""

    snap = _snapshot([_node()])

    async def fetcher() -> Snapshot:
        return snap

    client = TaxonomyClient("http://t", refresh_seconds=60, fetcher=fetcher)
    try:
        await client.start()
        # No notifier task should have been spawned.
        assert client._notifier_task is None  # type: ignore[attr-defined]
    finally:
        await client.stop()


@pytest.mark.asyncio
async def test_notifier_does_not_break_normal_polling() -> None:
    """With a quiet notifier, the polling cadence still drives refreshes."""

    versions = ["1.0.0", "1.0.1"]
    counter = {"i": 0}
    fetched = asyncio.Event()

    async def fetcher() -> Snapshot:
        i = counter["i"]
        counter["i"] = min(i + 1, len(versions) - 1)
        snap = _snapshot([_node()], semver=versions[i])
        if i > 0:
            fetched.set()
        return snap

    async def notifier():
        # Quiet — never yields. Polling must still tick the refresh.
        await asyncio.Event().wait()
        if False:  # pragma: no cover
            yield None

    client = TaxonomyClient(
        "http://t", refresh_seconds=1, fetcher=fetcher, notifier=notifier
    )
    try:
        await client.start()
        await asyncio.wait_for(fetched.wait(), timeout=3.0)
        assert client.version().semver == "1.0.1"
    finally:
        await client.stop()
