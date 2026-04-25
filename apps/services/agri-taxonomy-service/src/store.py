# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""In-memory taxonomy store + release pipeline (ADR-012, Phase 4).

Why in-memory: Phase-4 ADR-012 keeps the persistence layer pluggable.
The reads served by this service are entirely dominated by ``GET
/api/v1/taxonomy/version`` (snapshot ETag check) and ``GET /nodes``
(client refresh) — both naturally fit a frozen snapshot served from
RAM. A future migration to ``knowledge-graph`` (port 8140) only needs
to swap the store implementation.

Concurrency model
-----------------

* Every successful release builds a brand-new immutable ``Snapshot``.
* The current snapshot reference is published via a single attribute
  swap (``self._current = new``) — readers therefore always observe a
  fully-formed snapshot, no half-updated state.
* Mutations to ``_pending`` (the staging area where ``add_node`` /
  ``add_edge`` accumulate) are guarded by ``asyncio.Lock`` so concurrent
  ``POST /releases`` calls cannot interleave.

Release pipeline
----------------

``publish_release()``:

1. Acquire the release lock.
2. Validate the staged graph (no orphan parents, no duplicate
   synonyms-per-node, no cycles).
3. Compute SHA-256 over a canonical JSON projection so the same graph
   always produces the same checksum across hosts.
4. Bump the SemVer (patch by default, callers can pass ``"minor"`` or
   ``"major"``).
5. Build the new ``Snapshot`` and atomically swap.
6. Notify subscribers via the injected ``release_publisher`` callback —
   production wires this to NATS ``sahool.taxonomy.released.v{N}``,
   tests use an ``asyncio.Queue`` to assert the event payload.

The ``release_publisher`` is async and best-effort: a failure is logged
but does not roll the release back (the snapshot is already swapped and
the next polling tick will refresh clients anyway).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

log = logging.getLogger(__name__)


# ---- Domain value objects (server-side analogues of the client's models) -

NodeKind = Literal["crop", "variety", "disease", "pest", "weed", "fertilizer"]


@dataclass(frozen=True)
class Synonym:
    language: str
    label: str
    is_preferred: bool = False


@dataclass(frozen=True)
class TaxonomyNode:
    id: UUID
    kind: NodeKind
    parent_id: UUID | None = None
    synonyms: tuple[Synonym, ...] = ()
    cross_refs: tuple[tuple[str, str], ...] = ()  # frozen-friendly dict view
    forbidden: bool = False  # only meaningful for fertilizer/pest substances
    forbidden_reason_en: str | None = None
    forbidden_reason_ar: str | None = None


@dataclass(frozen=True)
class TaxonomyEdge:
    parent_id: UUID
    child_id: UUID


@dataclass(frozen=True)
class TaxonomyVersion:
    semver: str
    released_at: datetime
    checksum_sha256: str


@dataclass(frozen=True)
class Snapshot:
    """Immutable, ETag-friendly snapshot of the released taxonomy."""

    version: TaxonomyVersion
    nodes: tuple[TaxonomyNode, ...] = ()
    edges: tuple[TaxonomyEdge, ...] = ()


# ---- Release-event payload + publisher contract --------------------------


@dataclass(frozen=True)
class ReleaseEvent:
    """Payload published on ``sahool.taxonomy.released.v{N}``.

    The major-version suffix in the subject is the SemVer major; minor
    / patch upgrades stay on the same subject and clients just refresh.
    """

    semver: str
    released_at: datetime
    checksum_sha256: str
    node_count: int
    edge_count: int


#: Async callback the store invokes after every successful release.
#: Production wires this to a NATS ``Publish`` on
#: ``sahool.taxonomy.released.v{major}``; tests pass an in-memory queue.
ReleasePublisher = Callable[[ReleaseEvent], Awaitable[None]]


# ---- Pending-graph errors ------------------------------------------------


class TaxonomyValidationError(ValueError):
    """Raised by ``publish_release()`` when the staged graph is invalid."""


# ---- Store ---------------------------------------------------------------


@dataclass
class _Pending:
    """Mutable staging area: callers add nodes/edges before releasing."""

    nodes: dict[UUID, TaxonomyNode] = field(default_factory=dict)
    edges: list[TaxonomyEdge] = field(default_factory=list)


class TaxonomyStore:
    """In-memory store + release pipeline. Single instance per process."""

    def __init__(
        self,
        *,
        release_publisher: ReleasePublisher | None = None,
        initial_version: str = "0.0.0",
    ) -> None:
        self._pending = _Pending()
        empty_version = TaxonomyVersion(
            semver=initial_version,
            released_at=datetime.now(UTC),
            checksum_sha256=hashlib.sha256(b"{}").hexdigest(),
        )
        self._current = Snapshot(version=empty_version)
        self._release_lock = asyncio.Lock()
        self._publisher = release_publisher
        # Lazy O(1) lookup index, rebuilt the first time we observe a new
        # snapshot (atomic identity check). Avoids paying the index cost
        # for tests that never touch ``get_node``.
        self._indexed_snapshot: Snapshot | None = None
        self._node_index: dict[UUID, TaxonomyNode] = {}

    # -- read API (synchronous; backed by an immutable snapshot) ---------

    def snapshot(self) -> Snapshot:
        return self._current

    def _current_node_index(self) -> dict[UUID, TaxonomyNode]:
        snapshot = self._current
        if self._indexed_snapshot is not snapshot:
            self._node_index = {node.id: node for node in snapshot.nodes}
            self._indexed_snapshot = snapshot
        return self._node_index

    def get_node(self, node_id: UUID) -> TaxonomyNode | None:
        return self._current_node_index().get(node_id)

    def list_nodes(
        self,
        *,
        kind: NodeKind | None = None,
        parent_id: UUID | None = None,
        limit: int = 50,
    ) -> list[TaxonomyNode]:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        results: list[TaxonomyNode] = []
        for node in self._current.nodes:
            if kind is not None and node.kind != kind:
                continue
            if parent_id is not None and node.parent_id != parent_id:
                continue
            results.append(node)
            if len(results) >= limit:
                break
        return results

    def search(
        self,
        q: str,
        *,
        language: str | None = None,
    ) -> list[TaxonomyNode]:
        needle = q.strip().lower()
        if len(needle) < 2:
            return []
        results: list[TaxonomyNode] = []
        for node in self._current.nodes:
            for syn in node.synonyms:
                if language is not None and syn.language != language:
                    continue
                if needle in syn.label.lower():
                    results.append(node)
                    break
        return results

    def is_forbidden(self, fertilizer_id: UUID) -> tuple[bool, str | None, str | None]:
        node = self.get_node(fertilizer_id)
        if node is None:
            return (False, None, None)
        return (
            node.forbidden,
            node.forbidden_reason_en,
            node.forbidden_reason_ar,
        )

    # -- write API (staging; not visible to readers until release) -------

    def stage_node(self, node: TaxonomyNode) -> None:
        if node.id in self._pending.nodes:
            raise TaxonomyValidationError(f"duplicate node id: {node.id}")
        self._pending.nodes[node.id] = node

    def stage_edge(self, edge: TaxonomyEdge) -> None:
        self._pending.edges.append(edge)

    def reset_pending(self) -> None:
        self._pending = _Pending()

    # -- release pipeline -----------------------------------------------

    async def publish_release(
        self,
        bump: Literal["major", "minor", "patch"] = "patch",
    ) -> TaxonomyVersion:
        """Validate the staged graph and atomically swap a new snapshot."""

        async with self._release_lock:
            self._validate_pending()
            # Sort nodes/edges deterministically so a given set of staged
            # mutations always produces the same released snapshot ordering
            # (and the same ``/nodes`` response order), regardless of the
            # order callers staged them in.
            new_nodes = tuple(sorted(self._pending.nodes.values(), key=lambda n: n.id))
            new_edges = tuple(sorted(self._pending.edges, key=lambda e: (e.parent_id, e.child_id)))
            checksum = self._checksum(new_nodes, new_edges)
            semver = self._bump(self._current.version.semver, bump)
            version = TaxonomyVersion(
                semver=semver,
                released_at=datetime.now(UTC),
                checksum_sha256=checksum,
            )
            new_snapshot = Snapshot(version=version, nodes=new_nodes, edges=new_edges)
            # Atomic single-attribute swap — readers either observe the
            # old snapshot or the new one, never a half-built state.
            self._current = new_snapshot
            self.reset_pending()

        # Publish the release event after we drop the lock so a slow
        # subscriber cannot hold up subsequent reads. Failure is logged
        # but never rolls the release back.
        if self._publisher is not None:
            event = ReleaseEvent(
                semver=version.semver,
                released_at=version.released_at,
                checksum_sha256=version.checksum_sha256,
                node_count=len(new_nodes),
                edge_count=len(new_edges),
            )
            try:
                await self._publisher(event)
            except Exception:  # pragma: no cover - defensive
                log.exception("taxonomy.release_publisher_failed")
        return version

    # -- internals -------------------------------------------------------

    def _validate_pending(self) -> None:
        if not self._pending.nodes:
            raise TaxonomyValidationError("no staged nodes — refusing empty release")
        node_ids = set(self._pending.nodes)
        # 1. No edge references an unknown node.
        for edge in self._pending.edges:
            if edge.parent_id not in node_ids:
                raise TaxonomyValidationError(f"edge references unknown parent: {edge.parent_id}")
            if edge.child_id not in node_ids:
                raise TaxonomyValidationError(f"edge references unknown child: {edge.child_id}")
        # 2. No node has a parent that isn't staged.
        for node in self._pending.nodes.values():
            if node.parent_id is not None and node.parent_id not in node_ids:
                raise TaxonomyValidationError(f"node {node.id} parent {node.parent_id} not staged")
        # 3. No duplicate (language, label) synonym per node.
        for node in self._pending.nodes.values():
            seen: set[tuple[str, str]] = set()
            for syn in node.synonyms:
                key = (syn.language, syn.label.lower())
                if key in seen:
                    raise TaxonomyValidationError(f"duplicate synonym {syn.label!r} ({syn.language}) on node {node.id}")
                seen.add(key)
        # 4. No cycles in the parent_id chain.
        self._assert_acyclic()

    def _assert_acyclic(self) -> None:
        # Walk parent chain from each node up to the root or a cycle.
        for start in self._pending.nodes.values():
            seen: set[UUID] = set()
            node: TaxonomyNode | None = start
            while node is not None and node.parent_id is not None:
                if node.id in seen:
                    raise TaxonomyValidationError(f"cycle detected at node {node.id}")
                seen.add(node.id)
                node = self._pending.nodes.get(node.parent_id)

    @staticmethod
    def _checksum(nodes: Iterable[TaxonomyNode], edges: Iterable[TaxonomyEdge]) -> str:
        # Canonical JSON: stable key order + sorted node / edge lists so
        # the same graph always produces the same checksum.
        def node_dict(n: TaxonomyNode) -> dict:
            return {
                "id": str(n.id),
                "kind": n.kind,
                "parent_id": str(n.parent_id) if n.parent_id else None,
                "synonyms": sorted(
                    [{"language": s.language, "label": s.label, "preferred": s.is_preferred} for s in n.synonyms],
                    key=lambda s: (s["language"], s["label"]),
                ),
                "cross_refs": sorted(n.cross_refs),
                "forbidden": n.forbidden,
                # Include the user-visible reason fields so two snapshots
                # that differ only in their reason text produce different
                # checksums (clients use the checksum as an ETag and would
                # otherwise skip a real refresh).
                "forbidden_reason_en": n.forbidden_reason_en,
                "forbidden_reason_ar": n.forbidden_reason_ar,
            }

        payload = {
            "nodes": sorted([node_dict(n) for n in nodes], key=lambda n: n["id"]),
            "edges": sorted(
                [{"parent": str(e.parent_id), "child": str(e.child_id)} for e in edges],
                key=lambda e: (e["parent"], e["child"]),
            ),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    @staticmethod
    def _bump(semver: str, kind: Literal["major", "minor", "patch"]) -> str:
        try:
            major, minor, patch = (int(x) for x in semver.split("."))
        except ValueError as exc:
            raise TaxonomyValidationError(f"invalid SemVer: {semver!r}") from exc
        if kind == "major":
            return f"{major + 1}.0.0"
        if kind == "minor":
            return f"{major}.{minor + 1}.0"
        return f"{major}.{minor}.{patch + 1}"


# ---- Helpers used by the FastAPI router ---------------------------------


def node_to_response(node: TaxonomyNode) -> dict:
    """Render a :class:`TaxonomyNode` for the v1 API."""

    return {
        "id": str(node.id),
        "kind": node.kind,
        "parent_id": str(node.parent_id) if node.parent_id else None,
        "synonyms": [{"language": s.language, "label": s.label, "is_preferred": s.is_preferred} for s in node.synonyms],
        "cross_refs": dict(node.cross_refs),
    }


def make_default_seed_store(
    publisher: ReleasePublisher | None = None,
) -> TaxonomyStore:
    """Build a store seeded with a small but realistic taxonomy.

    Used at service startup so the API is immediately useful without
    requiring an admin call to ``POST /releases``. Production swaps
    this for a load from ``knowledge-graph`` (port 8140) — see ADR-012.
    """

    store = TaxonomyStore(release_publisher=publisher)
    # A handful of canonical nodes representative of every kind.
    wheat = TaxonomyNode(
        id=UUID("11111111-1111-4111-8111-111111111111"),
        kind="crop",
        synonyms=(
            Synonym("en", "wheat", is_preferred=True),
            Synonym("ar", "قمح", is_preferred=True),
            Synonym("la", "Triticum aestivum"),
        ),
        cross_refs=(("AGROVOC", "c_8373"),),
    )
    sakha = TaxonomyNode(
        id=UUID("22222222-2222-4222-8222-222222222222"),
        kind="variety",
        parent_id=wheat.id,
        synonyms=(Synonym("en", "Sakha 95", is_preferred=True),),
    )
    rust = TaxonomyNode(
        id=UUID("33333333-3333-4333-8333-333333333333"),
        kind="disease",
        synonyms=(
            Synonym("en", "leaf rust", is_preferred=True),
            Synonym("ar", "صدأ الأوراق", is_preferred=True),
        ),
    )
    paraquat = TaxonomyNode(
        id=UUID("44444444-4444-4444-8444-444444444444"),
        kind="fertilizer",
        synonyms=(Synonym("en", "paraquat", is_preferred=True),),
        forbidden=True,
        forbidden_reason_en="Class I acutely toxic herbicide; banned for use on food crops.",
        forbidden_reason_ar="مبيد عشبي شديد السمية من الفئة الأولى؛ محظور على المحاصيل الغذائية.",
    )
    urea = TaxonomyNode(
        id=UUID("55555555-5555-4555-8555-555555555555"),
        kind="fertilizer",
        synonyms=(
            Synonym("en", "urea 46%", is_preferred=True),
            Synonym("ar", "يوريا 46%", is_preferred=True),
        ),
    )
    for node in (wheat, sakha, rust, paraquat, urea):
        store.stage_node(node)
    store.stage_edge(TaxonomyEdge(parent_id=wheat.id, child_id=sakha.id))
    return store
