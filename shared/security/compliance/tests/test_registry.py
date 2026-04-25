# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for ``ComplianceRegistry`` (ADR-016)."""

from __future__ import annotations

from shared.security.compliance import (
    ComplianceRegistry,
    DefaultPlugin,
    FIPSPlugin,
    GDPRPlugin,
    NESAPlugin,
    TenantContext,
    build_default_registry,
)


class _FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def test_default_registry_registers_default_plugin() -> None:
    registry = ComplianceRegistry()
    assert "default" in registry.available()


def test_resolve_returns_registered_plugin() -> None:
    registry = build_default_registry()
    ctx = TenantContext(tenant_id="t1", region="EU", compliance_profile="gdpr")
    plugin = registry.resolve(ctx)
    assert isinstance(plugin, GDPRPlugin)


def test_resolve_falls_back_to_default_for_unknown_profile() -> None:
    registry = build_default_registry()
    ctx = TenantContext(tenant_id="t2", region="GLOBAL", compliance_profile="unknown-xyz")
    plugin = registry.resolve(ctx)
    assert isinstance(plugin, DefaultPlugin)


def test_resolve_uses_cache_within_ttl() -> None:
    clock = _FakeClock()
    registry = ComplianceRegistry(ttl_seconds=60.0, clock=clock)
    registry.register(FIPSPlugin())
    ctx = TenantContext(tenant_id="t3", region="US", compliance_profile="fips")

    p1 = registry.resolve(ctx)
    # Swap the underlying plug-in *behind the registry's back* so we can
    # observe whether resolve serves the cache (it should within TTL).
    new_fips = FIPSPlugin()
    registry._plugins["fips"] = new_fips  # type: ignore[attr-defined]
    clock.advance(30.0)
    p2 = registry.resolve(ctx)
    assert p1 is p2  # served from cache


def test_resolve_refreshes_cache_after_ttl() -> None:
    clock = _FakeClock()
    registry = ComplianceRegistry(ttl_seconds=60.0, clock=clock)
    registry.register(FIPSPlugin())
    ctx = TenantContext(tenant_id="t4", region="US", compliance_profile="fips")

    p1 = registry.resolve(ctx)
    new_fips = FIPSPlugin()
    registry._plugins["fips"] = new_fips  # type: ignore[attr-defined]
    clock.advance(61.0)
    p2 = registry.resolve(ctx)
    assert p2 is new_fips
    assert p1 is not p2


def test_register_replaces_and_invalidates_cache() -> None:
    registry = build_default_registry()
    ctx = TenantContext(tenant_id="t5", region="SA", compliance_profile="nesa")
    p1 = registry.resolve(ctx)
    assert isinstance(p1, NESAPlugin)

    new_nesa = NESAPlugin()
    registry.register(new_nesa)
    p2 = registry.resolve(ctx)
    assert p2 is new_nesa


def test_invalidate_clears_specific_tenant_only() -> None:
    registry = build_default_registry()
    ctx_a = TenantContext(tenant_id="tA", region="EU", compliance_profile="gdpr")
    ctx_b = TenantContext(tenant_id="tB", region="EU", compliance_profile="gdpr")
    registry.resolve(ctx_a)
    registry.resolve(ctx_b)
    assert len(registry._cache) == 2  # type: ignore[attr-defined]

    registry.invalidate(tenant_id="tA")
    cache_keys = list(registry._cache.keys())  # type: ignore[attr-defined]
    assert ("tA", "gdpr") not in cache_keys
    assert ("tB", "gdpr") in cache_keys


def test_invalidate_all_clears_cache() -> None:
    registry = build_default_registry()
    ctx = TenantContext(tenant_id="tC", region="EU", compliance_profile="gdpr")
    registry.resolve(ctx)
    registry.invalidate()
    assert registry._cache == {}  # type: ignore[attr-defined]


def test_available_lists_all_registered() -> None:
    registry = build_default_registry()
    assert set(registry.available()) == {"default", "fips", "gdpr", "nesa"}
