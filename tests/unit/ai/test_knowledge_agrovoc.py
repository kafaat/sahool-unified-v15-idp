"""
Tests for FAO AGROVOC Integration
===================================
اختبارات تكامل مفردات الفاو الزراعية (AGROVOC)

Tests for AgrovocDomain, AgrovocConcept, and AgrovocLookup.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.agrovoc import (
    AgrovocConcept,
    AgrovocDomain,
    AgrovocLookup,
)


# ─── Enum Tests ──────────────────────────────────────────────────────────────


class TestAgrovocDomain:
    """Tests for AgrovocDomain enum."""

    @pytest.mark.unit
    def test_domain_values(self):
        """Test all AGROVOC domain values."""
        assert AgrovocDomain.CROPS == "crops"
        assert AgrovocDomain.SOIL == "soil"
        assert AgrovocDomain.WATER == "water"
        assert AgrovocDomain.PESTS == "pests"
        assert AgrovocDomain.DISEASES == "diseases"
        assert AgrovocDomain.FERTILIZERS == "fertilizers"
        assert AgrovocDomain.CLIMATE == "climate"
        assert AgrovocDomain.EQUIPMENT == "equipment"

    @pytest.mark.unit
    def test_domain_count(self):
        """Test total number of domains."""
        assert len(AgrovocDomain) == 10

    @pytest.mark.unit
    def test_domain_is_str_enum(self):
        """Test domains can be used as strings."""
        assert f"domain:{AgrovocDomain.CROPS}" == "domain:crops"


# ─── Concept Tests ───────────────────────────────────────────────────────────


class TestAgrovocConcept:
    """Tests for AgrovocConcept dataclass."""

    @pytest.mark.unit
    def test_basic_concept(self):
        """Test creating a basic AGROVOC concept."""
        concept = AgrovocConcept(
            uri="c_7951",
            pref_label_en="Triticum aestivum",
            pref_label_ar="قمح طري",
        )
        assert concept.uri == "c_7951"
        assert concept.pref_label_en == "Triticum aestivum"
        assert concept.pref_label_ar == "قمح طري"

    @pytest.mark.unit
    def test_concept_defaults(self):
        """Test default empty collections."""
        concept = AgrovocConcept(uri="c_test", pref_label_en="Test")
        assert concept.alt_labels_en == []
        assert concept.alt_labels_ar == []
        assert concept.broader == []
        assert concept.narrower == []
        assert concept.related == []
        assert concept.domain is None
        assert concept.definition_en == ""
        assert concept.definition_ar == ""

    @pytest.mark.unit
    def test_concept_with_hierarchy(self):
        """Test concept with SKOS hierarchy links."""
        concept = AgrovocConcept(
            uri="c_7951",
            pref_label_en="Triticum aestivum",
            broader=["c_7950"],
            narrower=["c_36832"],
            related=["c_898"],
            domain=AgrovocDomain.CROPS,
        )
        assert "c_7950" in concept.broader
        assert "c_36832" in concept.narrower
        assert "c_898" in concept.related
        assert concept.domain == AgrovocDomain.CROPS

    @pytest.mark.unit
    def test_concept_alt_labels(self):
        """Test concept with alternative labels."""
        concept = AgrovocConcept(
            uri="c_7951",
            pref_label_en="Triticum aestivum",
            pref_label_ar="قمح طري",
            alt_labels_en=["bread wheat", "common wheat", "wheat"],
            alt_labels_ar=["قمح", "قمح خبز", "حنطة"],
        )
        assert "wheat" in concept.alt_labels_en
        assert "قمح" in concept.alt_labels_ar


# ─── Lookup Tests ────────────────────────────────────────────────────────────


class TestAgrovocLookup:
    """Tests for AgrovocLookup service."""

    @pytest.fixture
    def lookup(self) -> AgrovocLookup:
        return AgrovocLookup()

    @pytest.mark.unit
    def test_find_wheat_english(self, lookup: AgrovocLookup):
        """Test finding wheat by English name."""
        concept = lookup.find("wheat")
        assert concept is not None
        assert "c_7951" == concept.uri

    @pytest.mark.unit
    def test_find_wheat_arabic(self, lookup: AgrovocLookup):
        """Test finding wheat by Arabic name | البحث بالعربية"""
        concept = lookup.find("قمح")
        assert concept is not None
        assert concept.uri == "c_7951"

    @pytest.mark.unit
    def test_find_barley(self, lookup: AgrovocLookup):
        """Test finding barley."""
        concept = lookup.find("barley")
        assert concept is not None
        assert concept.uri == "c_898"

    @pytest.mark.unit
    def test_find_date_palm(self, lookup: AgrovocLookup):
        """Test finding date palm."""
        concept = lookup.find("date palm")
        assert concept is not None
        assert concept.uri == "c_5744"

    @pytest.mark.unit
    def test_find_nonexistent_returns_none(self, lookup: AgrovocLookup):
        """Test that non-existent term returns None."""
        concept = lookup.find("xyloflux")
        assert concept is None

    @pytest.mark.unit
    def test_find_case_insensitive(self, lookup: AgrovocLookup):
        """Test case-insensitive English lookup."""
        concept = lookup.find("WHEAT")
        assert concept is not None

    @pytest.mark.unit
    def test_find_all_wheat(self, lookup: AgrovocLookup):
        """Test finding all matches for wheat."""
        results = lookup.find_all("wheat")
        assert len(results) >= 1
        uris = {c.uri for c in results}
        assert "c_7951" in uris

    @pytest.mark.unit
    def test_find_all_nonexistent(self, lookup: AgrovocLookup):
        """Test find_all returns empty for non-existent term."""
        results = lookup.find_all("xyloflux_nonexistent")
        assert results == []

    @pytest.mark.unit
    def test_translate_en_to_ar(self, lookup: AgrovocLookup):
        """Test English to Arabic translation."""
        ar = lookup.translate("wheat", to_lang="ar")
        assert ar is not None
        assert ar != ""

    @pytest.mark.unit
    def test_translate_ar_to_en(self, lookup: AgrovocLookup):
        """Test Arabic to English translation."""
        en = lookup.translate("قمح", to_lang="en")
        assert en is not None
        assert en != ""

    @pytest.mark.unit
    def test_translate_nonexistent(self, lookup: AgrovocLookup):
        """Test translate returns original term for unknown terms."""
        result = lookup.translate("xyloflux", to_lang="ar")
        assert result == "xyloflux"

    @pytest.mark.unit
    def test_get_concept_by_uri(self, lookup: AgrovocLookup):
        """Test direct URI lookup."""
        concept = lookup.get_by_uri("c_7951")
        assert concept is not None
        assert concept.pref_label_en == "Triticum aestivum"

    @pytest.mark.unit
    def test_get_concept_by_invalid_uri(self, lookup: AgrovocLookup):
        """Test invalid URI returns None."""
        concept = lookup.get_by_uri("c_invalid_99999")
        assert concept is None

    @pytest.mark.unit
    def test_get_by_domain(self, lookup: AgrovocLookup):
        """Test getting concepts by domain."""
        crops = lookup.get_by_domain(AgrovocDomain.CROPS)
        assert len(crops) >= 5
        assert all(c.domain == AgrovocDomain.CROPS for c in crops)
