# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the in-memory taxonomy store + release pipeline (ADR-012)."""

from __future__ import annotations

import asyncio
from uuid import UUID

import pytest
from src.store import (
    ReleaseEvent,
    Synonym,
    TaxonomyEdge,
    TaxonomyNode,
    TaxonomyStore,
    TaxonomyValidationError,
    make_default_seed_store,
)

_WHEAT_ID = UUID("11111111-1111-4111-8111-111111111111")
_VAR_ID = UUID("22222222-2222-4222-8222-222222222222")


def _wheat() -> TaxonomyNode:
    return TaxonomyNode(
        id=_WHEAT_ID,
        kind="crop",
        synonyms=(Synonym("en", "wheat", is_preferred=True),),
    )


def _variety() -> TaxonomyNode:
    return TaxonomyNode(
        id=_VAR_ID,
        kind="variety",
        parent_id=_WHEAT_ID,
        synonyms=(Synonym("en", "Sakha 95"),),
    )


@pytest.mark.asyncio
async def test_publish_release_swaps_snapshot_atomically_and_bumps_semver() -> None:
    store = TaxonomyStore()
    store.stage_node(_wheat())
    version = await store.publish_release(bump="minor")
    assert version.semver == "0.1.0"
    snap = store.snapshot()
    assert snap.version.semver == "0.1.0"
    assert len(snap.nodes) == 1
    # Pending must be drained.
    with pytest.raises(TaxonomyValidationError, match="no staged"):
        await store.publish_release()


@pytest.mark.asyncio
async def test_release_rejects_orphan_parent() -> None:
    store = TaxonomyStore()
    store.stage_node(_variety())  # parent never staged
    with pytest.raises(TaxonomyValidationError, match="parent"):
        await store.publish_release()


@pytest.mark.asyncio
async def test_release_rejects_duplicate_synonym_per_node() -> None:
    store = TaxonomyStore()
    store.stage_node(
        TaxonomyNode(
            id=_WHEAT_ID,
            kind="crop",
            synonyms=(
                Synonym("en", "wheat"),
                Synonym("en", "Wheat"),  # case-insensitive duplicate
            ),
        )
    )
    with pytest.raises(TaxonomyValidationError, match="duplicate synonym"):
        await store.publish_release()


@pytest.mark.asyncio
async def test_release_rejects_edge_referencing_unknown_node() -> None:
    store = TaxonomyStore()
    store.stage_node(_wheat())
    store.stage_edge(TaxonomyEdge(parent_id=_WHEAT_ID, child_id=_VAR_ID))
    with pytest.raises(TaxonomyValidationError, match="unknown child"):
        await store.publish_release()


@pytest.mark.asyncio
async def test_checksum_is_stable_across_release_order() -> None:
    """Same logical graph → same SHA-256 regardless of staging order.
    This is what lets clients use the checksum as an ETag.
    """

    store_a = TaxonomyStore()
    store_a.stage_node(_wheat())
    store_a.stage_node(_variety())
    store_a.stage_edge(TaxonomyEdge(parent_id=_WHEAT_ID, child_id=_VAR_ID))
    version_a = await store_a.publish_release()

    store_b = TaxonomyStore()
    store_b.stage_node(_variety())  # reverse order
    store_b.stage_node(_wheat())
    store_b.stage_edge(TaxonomyEdge(parent_id=_WHEAT_ID, child_id=_VAR_ID))
    version_b = await store_b.publish_release()

    assert version_a.checksum_sha256 == version_b.checksum_sha256


@pytest.mark.asyncio
async def test_release_publisher_invoked_with_event_payload() -> None:
    captured: list[ReleaseEvent] = []

    async def publisher(event: ReleaseEvent) -> None:
        captured.append(event)

    store = TaxonomyStore(release_publisher=publisher)
    store.stage_node(_wheat())
    version = await store.publish_release(bump="major")
    assert len(captured) == 1
    event = captured[0]
    assert event.semver == version.semver == "1.0.0"
    assert event.checksum_sha256 == version.checksum_sha256
    assert event.node_count == 1
    assert event.edge_count == 0


@pytest.mark.asyncio
async def test_release_publisher_failure_does_not_roll_back() -> None:
    """A flaky NATS broker must not corrupt the in-memory snapshot."""

    async def publisher(_: ReleaseEvent) -> None:
        raise RuntimeError("nats unreachable")

    store = TaxonomyStore(release_publisher=publisher)
    store.stage_node(_wheat())
    # Must not raise — failure is logged, snapshot is already swapped.
    version = await store.publish_release()
    assert store.snapshot().version.semver == version.semver


@pytest.mark.asyncio
async def test_concurrent_releases_are_serialised() -> None:
    """The release lock prevents two concurrent ``publish_release``
    calls from interleaving and observing the same staged nodes twice.
    """

    store = TaxonomyStore()
    store.stage_node(_wheat())
    # Second release call has nothing pending after the first acquires
    # the lock and drains it.
    results = await asyncio.gather(
        store.publish_release(),
        store.publish_release(),
        return_exceptions=True,
    )
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    assert len(successes) == 1
    assert len(failures) == 1
    assert isinstance(failures[0], TaxonomyValidationError)


@pytest.mark.asyncio
async def test_seeded_store_emits_one_event_per_release() -> None:
    """``make_default_seed_store`` builds a non-trivial graph; releasing
    it once must produce exactly one event with the right counts.
    """

    captured: list[ReleaseEvent] = []

    async def publisher(event: ReleaseEvent) -> None:
        captured.append(event)

    store = make_default_seed_store(publisher=publisher)
    await store.publish_release(bump="minor")
    assert len(captured) == 1
    assert captured[0].node_count == 5
    assert captured[0].edge_count == 1
    # The forbidden flag survived the round-trip.
    forbidden, reason_en, _reason_ar = store.is_forbidden(UUID("44444444-4444-4444-8444-444444444444"))
    assert forbidden is True
    assert reason_en is not None
