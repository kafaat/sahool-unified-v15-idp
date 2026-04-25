# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Value objects for the agricultural taxonomy. Skeleton — see ADR-012."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class TaxonomyVersion:
    """SemVer release identifier for a taxonomy snapshot."""

    semver: str  # e.g. "3.4.1"
    released_at: datetime
    checksum_sha256: str


@dataclass(frozen=True)
class Synonym:
    """One alias for a taxonomy node, in a given language."""

    language: str  # ISO 639-1, e.g. "ar", "en", "la" (Latin binomial)
    label: str
    is_preferred: bool = False


@dataclass(frozen=True)
class TaxonomyNode:
    """A node in the taxonomy graph (crop, variety, disease, pest, weed, fertilizer).

    Fields:
        id: UUIDv4 — stable identifier (ADR-012 invariant).
        kind: One of ``"crop" | "variety" | "disease" | "pest" | "weed" | "fertilizer"``.
        parent_id: Parent node id (``None`` for roots).
        synonyms: Localised aliases per ISO 639-1 language code.
        cross_refs: External authority codes keyed by registry name.
            Example: ``{"AGROVOC": "c_8389", "EPPO": "TRZAX"}``.
    """

    id: UUID
    kind: str
    parent_id: UUID | None
    synonyms: list[Synonym] = field(default_factory=list)
    cross_refs: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TaxonomyEdge:
    """Edge in the taxonomy graph (e.g., susceptibility, treatment)."""

    source_id: UUID
    target_id: UUID
    relation: str  # e.g. "susceptible_to", "treated_by", "synonym_of"
