# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
shared.agri_taxonomy_client — Client for ``agri-taxonomy-service`` (ADR-012)
============================================================================

Skeleton package. See ``README.md`` and
``docs/adr/ADR-012-agri-taxonomy-service.md``.
"""

from __future__ import annotations

from .models import Synonym, TaxonomyEdge, TaxonomyNode, TaxonomyVersion

__all__ = ["Synonym", "TaxonomyEdge", "TaxonomyNode", "TaxonomyVersion"]
