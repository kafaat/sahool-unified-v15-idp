"""
Tests for Knowledge Source Registry
=====================================
اختبارات سجل مصادر المعرفة الزراعية

Tests for URL matching, credibility scoring, domain/region filtering,
and YAML loading.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from shared.ai.knowledge.models import KnowledgeDomain, SourceCredibilityLevel
from shared.ai.knowledge.sources.registry import (
    KnowledgeSourceRegistry,
    TrustedSource,
)


@pytest.fixture
def registry() -> KnowledgeSourceRegistry:
    """Create a loaded registry from the default sources file."""
    r = KnowledgeSourceRegistry()
    r.load()
    return r


@pytest.fixture
def empty_registry(tmp_path: Path) -> KnowledgeSourceRegistry:
    """Create a registry with a non-existent sources file."""
    r = KnowledgeSourceRegistry(sources_file=tmp_path / "nonexistent.yaml")
    return r


# ─── Loading Tests ────────────────────────────────────────────────────────────


class TestRegistryLoading:
    """Tests for loading trusted sources from YAML."""

    @pytest.mark.unit
    def test_load_default_sources(self, registry: KnowledgeSourceRegistry):
        """Test loading from the default trusted_sources.yaml."""
        sources = registry.list_all_sources()
        assert len(sources) >= 20  # At least 20 sources defined

    @pytest.mark.unit
    def test_load_nonexistent_file(self, empty_registry: KnowledgeSourceRegistry):
        """Test graceful handling of missing sources file."""
        empty_registry.load()
        sources = empty_registry.list_all_sources()
        assert sources == []

    @pytest.mark.unit
    def test_auto_load_on_first_access(self):
        """Test that registry auto-loads on first access."""
        r = KnowledgeSourceRegistry()
        # Accessing list_all_sources should trigger lazy load
        sources = r.list_all_sources()
        assert len(sources) >= 20

    @pytest.mark.unit
    def test_load_empty_yaml(self, tmp_path: Path):
        """Test loading an empty YAML file."""
        empty_yaml = tmp_path / "empty.yaml"
        empty_yaml.write_text("{}")
        r = KnowledgeSourceRegistry(sources_file=empty_yaml)
        r.load()
        assert r.list_all_sources() == []


# ─── Source Credibility Tests ─────────────────────────────────────────────────


class TestSourceCredibility:
    """Tests for source credibility scoring."""

    @pytest.mark.unit
    def test_fao_credibility(self, registry: KnowledgeSourceRegistry):
        """Test FAO has highest credibility."""
        cred = registry.get_source_credibility("https://www.fao.org/some-page")
        assert cred == SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION

    @pytest.mark.unit
    def test_icarda_credibility(self, registry: KnowledgeSourceRegistry):
        """Test ICARDA has highest credibility."""
        cred = registry.get_source_credibility("https://www.icarda.org/research")
        assert cred.value == 5

    @pytest.mark.unit
    def test_unknown_source_returns_community(self, registry: KnowledgeSourceRegistry):
        """Test unknown URL returns COMMUNITY (lowest) credibility."""
        cred = registry.get_source_credibility("https://random-blog.com/agriculture")
        assert cred == SourceCredibilityLevel.COMMUNITY

    @pytest.mark.unit
    def test_empty_url(self, registry: KnowledgeSourceRegistry):
        """Test empty URL returns COMMUNITY credibility."""
        cred = registry.get_source_credibility("")
        assert cred == SourceCredibilityLevel.COMMUNITY


# ─── Trusted Source Check Tests ───────────────────────────────────────────────


class TestIsTrustedSource:
    """Tests for is_trusted_source method."""

    @pytest.mark.unit
    def test_fao_is_trusted(self, registry: KnowledgeSourceRegistry):
        """Test FAO is trusted."""
        assert registry.is_trusted_source("https://www.fao.org/water") is True

    @pytest.mark.unit
    def test_unknown_not_trusted(self, registry: KnowledgeSourceRegistry):
        """Test unknown source is not trusted (default min_credibility=2)."""
        assert registry.is_trusted_source("https://random-blog.com") is False

    @pytest.mark.unit
    def test_custom_min_credibility(self, registry: KnowledgeSourceRegistry):
        """Test custom minimum credibility threshold."""
        # Everything trusted at level 1 (including unknown)
        assert registry.is_trusted_source("https://random-blog.com", min_credibility=1) is True
        # FAO trusted at any level
        assert registry.is_trusted_source("https://fao.org/page", min_credibility=5) is True


# ─── Source Info Tests ────────────────────────────────────────────────────────


class TestGetSourceInfo:
    """Tests for getting full source information."""

    @pytest.mark.unit
    def test_known_source_info(self, registry: KnowledgeSourceRegistry):
        """Test getting info for a known source."""
        info = registry.get_source_info("https://www.fao.org/agriculture")
        assert info is not None
        assert info.name != ""
        assert info.credibility.value == 5

    @pytest.mark.unit
    def test_unknown_source_returns_none(self, registry: KnowledgeSourceRegistry):
        """Test unknown source returns None."""
        info = registry.get_source_info("https://unknown-site.com/page")
        assert info is None


# ─── Domain Filtering Tests ──────────────────────────────────────────────────


class TestSourcesByDomain:
    """Tests for filtering sources by knowledge domain."""

    @pytest.mark.unit
    def test_crop_domain_sources(self, registry: KnowledgeSourceRegistry):
        """Test getting sources for crop domain."""
        sources = registry.get_sources_for_domain(KnowledgeDomain.CROPS)
        assert len(sources) > 0
        for s in sources:
            assert KnowledgeDomain.CROPS in s.domains

    @pytest.mark.unit
    def test_irrigation_domain_sources(self, registry: KnowledgeSourceRegistry):
        """Test getting sources for irrigation domain."""
        sources = registry.get_sources_for_domain(KnowledgeDomain.IRRIGATION)
        assert len(sources) > 0

    @pytest.mark.unit
    def test_all_domains_have_sources(self, registry: KnowledgeSourceRegistry):
        """Test every domain has at least one source."""
        for domain in KnowledgeDomain:
            if domain in (KnowledgeDomain.GENERAL, KnowledgeDomain.PRECISION_FARMING, KnowledgeDomain.DIGITAL_TWIN):
                continue  # These domains may not have specific sources yet
            sources = registry.get_sources_for_domain(domain)
            assert len(sources) > 0, f"No sources for domain {domain.value}"


# ─── Region Filtering Tests ──────────────────────────────────────────────────


class TestSourcesByRegion:
    """Tests for filtering sources by region."""

    @pytest.mark.unit
    def test_global_sources(self, registry: KnowledgeSourceRegistry):
        """Test global sources appear for any region."""
        sources = registry.get_sources_for_region("yemen")
        # Global sources should also match
        global_sources = [s for s in sources if "global" in [r.lower() for r in s.region_coverage]]
        assert len(global_sources) > 0

    @pytest.mark.unit
    def test_mena_region(self, registry: KnowledgeSourceRegistry):
        """Test MENA region sources."""
        sources = registry.get_sources_for_region("mena")
        assert len(sources) > 0


# ─── Dynamic Registration Tests ──────────────────────────────────────────────


class TestDynamicRegistration:
    """Tests for dynamic source registration."""

    @pytest.mark.unit
    def test_register_new_source(self, registry: KnowledgeSourceRegistry):
        """Test registering a new source dynamically."""
        original_count = len(registry.list_all_sources())

        new_source = TrustedSource(
            name="Test Research Center",
            name_ar="مركز أبحاث تجريبي",
            url_patterns=["test-center.org"],
            credibility=SourceCredibilityLevel.LOCAL_RESEARCH,
            domains=[KnowledgeDomain.CROPS],
            languages=["en", "ar"],
            region_coverage=["yemen"],
        )
        registry.register_source(new_source)

        assert len(registry.list_all_sources()) == original_count + 1

        # Verify the new source is matchable
        cred = registry.get_source_credibility("https://test-center.org/paper")
        assert cred == SourceCredibilityLevel.LOCAL_RESEARCH


# ─── Summary Tests ────────────────────────────────────────────────────────────


class TestRegistrySummary:
    """Tests for registry summary."""

    @pytest.mark.unit
    def test_summary_structure(self, registry: KnowledgeSourceRegistry):
        """Test summary has required keys."""
        summary = registry.to_summary()
        assert "total_sources" in summary
        assert "by_credibility" in summary
        assert "domains_covered" in summary
        assert "regions_covered" in summary

    @pytest.mark.unit
    def test_summary_counts(self, registry: KnowledgeSourceRegistry):
        """Test summary total matches source list."""
        summary = registry.to_summary()
        assert summary["total_sources"] == len(registry.list_all_sources())

    @pytest.mark.unit
    def test_summary_has_credibility_distribution(self, registry: KnowledgeSourceRegistry):
        """Test summary includes credibility level distribution."""
        summary = registry.to_summary()
        assert len(summary["by_credibility"]) > 0
        # Should have high credibility sources
        assert 5 in summary["by_credibility"]
