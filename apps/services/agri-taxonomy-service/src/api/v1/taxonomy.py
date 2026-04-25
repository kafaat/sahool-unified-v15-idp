# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Taxonomy v1 routes — Phase 4 implementation (ADR-012).

The router is deliberately thin: it translates HTTP into store calls
and back, and owns no taxonomy state of its own. The store reference
is resolved at request time via ``app.state.taxonomy_store`` so tests
can inject a fixture-built store without monkey-patching globals.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from ...store import TaxonomyStore, TaxonomyValidationError, node_to_response

router = APIRouter()

NodeKind = Literal["crop", "variety", "disease", "pest", "weed", "fertilizer"]


# ---------------------------------------------------------------------------
# Response schemas (mirror shared.agri_taxonomy_client.models)
# ---------------------------------------------------------------------------


class SynonymOut(BaseModel):
    language: str = Field(..., description="ISO 639-1 (or 'la' for Latin)")
    label: str
    is_preferred: bool = False


class TaxonomyNodeOut(BaseModel):
    id: UUID
    kind: NodeKind
    parent_id: UUID | None = None
    synonyms: list[SynonymOut] = Field(default_factory=list)
    cross_refs: dict[str, str] = Field(
        default_factory=dict,
        description="External vocabulary IDs (AGROVOC, EPPO, Wikidata, ...)",
    )


class TaxonomyVersionOut(BaseModel):
    semver: str
    released_at: datetime
    checksum_sha256: str


class ForbiddenCheckOut(BaseModel):
    fertilizer_id: UUID
    forbidden: bool
    reason_en: str | None = None
    reason_ar: str | None = None


class PublishReleaseIn(BaseModel):
    bump: Literal["major", "minor", "patch"] = "patch"


class PublishReleaseOut(BaseModel):
    semver: str
    released_at: datetime
    checksum_sha256: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _store(request: Request) -> TaxonomyStore:
    store = getattr(request.app.state, "taxonomy_store", None)
    if store is None:
        # Defensive: lifespan must populate this. Surfacing 503 keeps
        # the failure mode out of 500 / "internal" land.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="taxonomy store not initialised",
        )
    return store


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/version", response_model=TaxonomyVersionOut)
async def get_version(request: Request) -> TaxonomyVersionOut:
    """Return the SemVer + checksum of the currently released snapshot."""

    snapshot = _store(request).snapshot()
    return TaxonomyVersionOut(
        semver=snapshot.version.semver,
        released_at=snapshot.version.released_at,
        checksum_sha256=snapshot.version.checksum_sha256,
    )


@router.get("/nodes/{node_id}", response_model=TaxonomyNodeOut)
async def get_node(node_id: UUID, request: Request) -> TaxonomyNodeOut:
    """Fetch one taxonomy node by stable UUIDv4."""

    node = _store(request).get_node(node_id)
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"taxonomy node not found: {node_id}",
        )
    return TaxonomyNodeOut.model_validate(node_to_response(node))


@router.get("/nodes", response_model=list[TaxonomyNodeOut])
async def list_nodes(
    request: Request,
    kind: NodeKind | None = Query(None),
    parent_id: UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
) -> list[TaxonomyNodeOut]:
    """List nodes filtered by ``kind`` and / or ``parent_id``."""

    nodes = _store(request).list_nodes(kind=kind, parent_id=parent_id, limit=limit)
    return [TaxonomyNodeOut.model_validate(node_to_response(n)) for n in nodes]


@router.get("/search", response_model=list[TaxonomyNodeOut])
async def search(
    request: Request,
    q: str = Query(..., min_length=2),
    language: str | None = Query(None, description="ISO 639-1 hint"),
) -> list[TaxonomyNodeOut]:
    """Search by synonym across Arabic / English / Latin labels."""

    nodes = _store(request).search(q, language=language)
    return [TaxonomyNodeOut.model_validate(node_to_response(n)) for n in nodes]


@router.get(
    "/fertilizers/{fertilizer_id}/forbidden",
    response_model=ForbiddenCheckOut,
)
async def check_forbidden(
    fertilizer_id: UUID, request: Request
) -> ForbiddenCheckOut:
    """Forbidden-substance check used by ADR-013 (Prescription Safety Gateway)."""

    forbidden, reason_en, reason_ar = _store(request).is_forbidden(fertilizer_id)
    return ForbiddenCheckOut(
        fertilizer_id=fertilizer_id,
        forbidden=forbidden,
        reason_en=reason_en,
        reason_ar=reason_ar,
    )


@router.post(
    "/releases",
    response_model=PublishReleaseOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def publish_release(
    request: Request,
    body: PublishReleaseIn | None = None,
) -> PublishReleaseOut:
    """Admin-only: publish a new taxonomy release.

    Triggers the release pipeline (validation → checksum → NATS publish on
    ``sahool.taxonomy.released.v{major}``).
    """

    bump = (body or PublishReleaseIn()).bump
    try:
        version = await _store(request).publish_release(bump=bump)
    except TaxonomyValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return PublishReleaseOut(
        semver=version.semver,
        released_at=version.released_at,
        checksum_sha256=version.checksum_sha256,
    )
