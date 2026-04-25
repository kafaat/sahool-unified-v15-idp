# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""TTL-cached registry resolving ``TenantContext`` → ``CompliancePlugin``.

Skeleton — see ADR-016.
"""

from __future__ import annotations

from .models import TenantContext
from .protocol import CompliancePlugin


class ComplianceRegistry:
    """Resolves the active plug-in for a tenant.

    Cache TTL is 60 s, keyed by ``(tenant_id, profile)``. Phase 4 implements
    the cache, plug-in loading, and fallback to ``default``.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, CompliancePlugin] = {}

    def register(self, plugin: CompliancePlugin) -> None:
        self._plugins[plugin.name] = plugin

    def resolve(self, ctx: TenantContext) -> CompliancePlugin:
        raise NotImplementedError("ADR-016: implemented in Phase 4")
