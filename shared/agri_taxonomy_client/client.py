# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Polling client for ``agri-taxonomy-service``. Skeleton — see ADR-012."""

from __future__ import annotations

from uuid import UUID

from .models import TaxonomyNode, TaxonomyVersion


class TaxonomyClient:
    """In-process client with a 30 s refresh window and atomic snapshot swap.

    Phase 4 implements the polling loop, NATS subscription
    (``sahool.taxonomy.released.v{N}``), and the LRU lookup cache.
    """

    def __init__(self, base_url: str, refresh_seconds: int = 30) -> None:
        self.base_url = base_url
        self.refresh_seconds = refresh_seconds
        self._snapshot: TaxonomyVersion | None = None

    async def start(self) -> None:
        raise NotImplementedError("ADR-012: implemented in Phase 4")

    async def stop(self) -> None:
        raise NotImplementedError("ADR-012: implemented in Phase 4")

    def get_node(self, node_id: UUID) -> TaxonomyNode | None:
        raise NotImplementedError("ADR-012: implemented in Phase 4")

    def is_forbidden_substance(self, fertilizer_id: UUID) -> bool:
        """Used by ``shared/prescription_safety`` (ADR-013) for blacklist check."""

        raise NotImplementedError("ADR-012: implemented in Phase 4")

    def version(self) -> TaxonomyVersion | None:
        return self._snapshot
