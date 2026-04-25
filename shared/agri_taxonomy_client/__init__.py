# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.agri_taxonomy_client — Client for ``agri-taxonomy-service`` (ADR-012)
============================================================================

Phase 4 implementation. Exposes the taxonomy value objects and the
``TaxonomyClient`` polling client with atomic snapshot swap.
"""

from __future__ import annotations

from .client import Snapshot, TaxonomyClient, TaxonomyFetcher, TaxonomyNotifier
from .models import Synonym, TaxonomyEdge, TaxonomyNode, TaxonomyVersion

__all__ = [
    "Snapshot",
    "Synonym",
    "TaxonomyClient",
    "TaxonomyEdge",
    "TaxonomyFetcher",
    "TaxonomyNode",
    "TaxonomyNotifier",
    "TaxonomyVersion",
]
