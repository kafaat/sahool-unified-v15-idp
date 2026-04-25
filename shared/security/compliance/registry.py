# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""TTL-cached registry resolving ``TenantContext`` → ``CompliancePlugin`` (ADR-016).

The registry is intentionally tiny:

* Plug-ins register themselves once at startup (no I/O).
* ``resolve(ctx)`` looks up by ``ctx.compliance_profile`` and falls back
  to ``"default"`` when the requested profile is unknown.
* Results are cached for ``ttl_seconds`` per ``(tenant_id, profile)`` key
  so repeated lookups across a request lifecycle are free.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from .models import TenantContext
from .protocol import CompliancePlugin

DEFAULT_TTL_SECONDS = 60.0


@dataclass
class _CacheEntry:
    plugin: CompliancePlugin
    expires_at: float


class ComplianceRegistry:
    """Resolves the active plug-in for a tenant.

    Parameters
    ----------
    ttl_seconds:
        Cache lifetime per ``(tenant_id, profile)`` lookup. Defaults to 60 s.
    clock:
        Injectable monotonic clock for deterministic tests. Defaults to
        :func:`time.monotonic`.

    The registry registers a permissive ``DefaultPlugin`` automatically so
    callers always have a valid fallback.
    """

    def __init__(
        self,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        clock=time.monotonic,  # type: ignore[assignment]
    ) -> None:
        self._plugins: dict[str, CompliancePlugin] = {}
        self._cache: dict[tuple[str, str], _CacheEntry] = {}
        self._ttl = ttl_seconds
        self._clock = clock
        # Auto-register the permissive default plug-in. Imported lazily to
        # avoid a circular import (plugins/* import from ..models).
        from .plugins.default import DefaultPlugin

        self.register(DefaultPlugin())

    # -- public API ------------------------------------------------------

    def register(self, plugin: CompliancePlugin) -> None:
        """Register or replace a plug-in by ``plugin.name``.

        Replacing an existing plug-in invalidates any cached entries that
        pointed at it so callers see the new plug-in on the next resolve.
        """

        previous = self._plugins.get(plugin.name)
        self._plugins[plugin.name] = plugin
        if previous is not None and previous is not plugin:
            self._cache = {k: v for k, v in self._cache.items() if v.plugin is not previous}

    def available(self) -> list[str]:
        """Return the names of currently registered plug-ins (sorted)."""

        return sorted(self._plugins.keys())

    def resolve(self, ctx: TenantContext) -> CompliancePlugin:
        """Resolve the active plug-in for ``ctx`` with TTL caching.

        Falls back to the ``default`` plug-in when ``ctx.compliance_profile``
        is unknown so callers always get a valid plug-in.
        """

        key = (ctx.tenant_id, ctx.compliance_profile)
        now = self._clock()
        cached = self._cache.get(key)
        if cached is not None and cached.expires_at > now:
            return cached.plugin

        plugin = self._plugins.get(ctx.compliance_profile) or self._plugins["default"]
        self._cache[key] = _CacheEntry(plugin=plugin, expires_at=now + self._ttl)
        return plugin

    def invalidate(self, tenant_id: str | None = None) -> None:
        """Invalidate cache entries.

        ``tenant_id=None`` clears the whole cache; otherwise only entries
        for the given tenant are removed. Useful when a tenant's compliance
        profile changes mid-flight.
        """

        if tenant_id is None:
            self._cache.clear()
            return
        self._cache = {k: v for k, v in self._cache.items() if k[0] != tenant_id}


def build_default_registry(ttl_seconds: float = DEFAULT_TTL_SECONDS) -> ComplianceRegistry:
    """Convenience factory: registry pre-loaded with all four plug-ins."""

    # Lazy imports keep the registry module decoupled from concrete plug-ins
    # so a caller can build a registry with only the plug-ins they need.
    from .plugins.fips import FIPSPlugin
    from .plugins.gdpr import GDPRPlugin
    from .plugins.nesa import NESAPlugin

    registry = ComplianceRegistry(ttl_seconds=ttl_seconds)
    registry.register(FIPSPlugin())
    registry.register(NESAPlugin())
    registry.register(GDPRPlugin())
    return registry
