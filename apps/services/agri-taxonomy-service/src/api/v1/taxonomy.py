# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Taxonomy v1 routes — Phase 3.5 scaffold (ADR-012).

Routes return ``501 Not Implemented`` until Phase 4 wires the
``knowledge-graph`` adapter and the release pipeline. The shapes are
stable and match ``shared.agri_taxonomy_client.models``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

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


# ---------------------------------------------------------------------------
# Routes (501 until Phase 4)
# ---------------------------------------------------------------------------


@router.get("/version", response_model=TaxonomyVersionOut)
async def get_version() -> TaxonomyVersionOut:
    """Return the SemVer + checksum of the currently released snapshot."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="ADR-012: implemented in Phase 4",
    )


@router.get("/nodes/{node_id}", response_model=TaxonomyNodeOut)
async def get_node(node_id: UUID) -> TaxonomyNodeOut:
    """Fetch one taxonomy node by stable UUIDv4."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="ADR-012: implemented in Phase 4",
    )


@router.get("/nodes", response_model=list[TaxonomyNodeOut])
async def list_nodes(
    kind: NodeKind | None = Query(None),
    parent_id: UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
) -> list[TaxonomyNodeOut]:
    """List nodes filtered by ``kind`` and / or ``parent_id``."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="ADR-012: implemented in Phase 4",
    )


@router.get("/search", response_model=list[TaxonomyNodeOut])
async def search(
    q: str = Query(..., min_length=2),
    language: str | None = Query(None, description="ISO 639-1 hint"),
) -> list[TaxonomyNodeOut]:
    """Search by synonym across Arabic / English / Latin labels."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="ADR-012: implemented in Phase 4",
    )


@router.get(
    "/fertilizers/{fertilizer_id}/forbidden",
    response_model=ForbiddenCheckOut,
)
async def check_forbidden(fertilizer_id: UUID) -> ForbiddenCheckOut:
    """Forbidden-substance check used by ADR-013 (Prescription Safety Gateway)."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="ADR-012: implemented in Phase 4",
    )


@router.post("/releases", status_code=status.HTTP_202_ACCEPTED)
async def publish_release() -> dict[str, str]:
    """Admin-only: publish a new taxonomy release.

    Triggers the release pipeline (validation → checksum → NATS publish on
    ``sahool.taxonomy.released.v{N}``). Phase 4 implementation.
    """

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="ADR-012: implemented in Phase 4",
    )
