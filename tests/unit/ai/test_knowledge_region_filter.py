"""
Tests for Region Relevance Filter (AgriRegion Pattern)
=======================================================
اختبارات فلتر الملاءمة الإقليمية (نمط AgriRegion)

Tests for climate compatibility, crop relevance, soil scoring,
and document filtering based on regional applicability.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.models import (
    BaseKnowledgeDocument,
    GeospatialMetadata,
    KnowledgeDomain,
)
from shared.ai.knowledge.verification.region_filter import (
    CLIMATE_ZONES,
    RegionRelevanceFilter,
    RegionRelevanceResult,
)


@pytest.fixture
def region_filter() -> RegionRelevanceFilter:
    """Create a RegionRelevanceFilter with Yemen regions."""
    return RegionRelevanceFilter(target_regions=["yemen_highland", "yemen_coastal"])


@pytest.fixture
def yemen_highland_doc() -> BaseKnowledgeDocument:
    """Create a document specifically for Yemen highlands."""
    return BaseKnowledgeDocument(
        title="Highland Wheat Cultivation",
        title_ar="زراعة القمح في المرتفعات",
        content="Wheat cultivation at 1500-2500m altitude in semi-arid highlands.",
        domain=KnowledgeDomain.CROPS,
        tags=["crop:wheat", "crop:barley"],
        geospatial=GeospatialMetadata(
            applicable_regions=["yemen_highland"],
            climate_zones=["semi_arid_highland"],
            altitude_range_m=(1500, 2500),
            soil_types=["loam", "clay loam"],
        ),
    )


@pytest.fixture
def general_doc() -> BaseKnowledgeDocument:
    """Create a general document with no region info."""
    return BaseKnowledgeDocument(
        title="General Agriculture Principles",
        content="Basic farming principles applicable everywhere.",
        domain=KnowledgeDomain.GENERAL,
    )


@pytest.fixture
def tropical_doc() -> BaseKnowledgeDocument:
    """Create a document for tropical regions (low relevance for Yemen)."""
    return BaseKnowledgeDocument(
        title="Tropical Rice Cultivation",
        content="Rice paddies in tropical monsoon climate.",
        domain=KnowledgeDomain.CROPS,
        tags=["crop:rice"],
        geospatial=GeospatialMetadata(
            applicable_regions=["southeast_asia"],
            climate_zones=["tropical_monsoon"],
            altitude_range_m=(0, 100),
        ),
    )


# ─── Climate Zones Tests ─────────────────────────────────────────────────────


class TestClimateZones:
    """Tests for climate zone definitions."""

    @pytest.mark.unit
    def test_all_zones_defined(self):
        """Test all 15 climate zones are defined."""
        assert len(CLIMATE_ZONES) == 15

    @pytest.mark.unit
    def test_yemen_zones_present(self):
        """Test Yemen zones are defined."""
        yemen_zones = [z for z in CLIMATE_ZONES if z.startswith("yemen_")]
        assert len(yemen_zones) == 5

    @pytest.mark.unit
    def test_gcc_zones_present(self):
        """Test GCC/Saudi zones are defined."""
        gcc_zones = [z for z in CLIMATE_ZONES if z.startswith("saudi_") or z.startswith("gcc_")]
        assert len(gcc_zones) == 3

    @pytest.mark.unit
    def test_zone_has_required_fields(self):
        """Test each zone has required fields."""
        for name, zone in CLIMATE_ZONES.items():
            assert "name_ar" in zone, f"Zone {name} missing name_ar"
            assert "type" in zone, f"Zone {name} missing type"
            assert "temp_range_c" in zone, f"Zone {name} missing temp_range_c"
            assert "rainfall_mm" in zone, f"Zone {name} missing rainfall_mm"
            assert "altitude_m" in zone, f"Zone {name} missing altitude_m"
            assert "similar_zones" in zone, f"Zone {name} missing similar_zones"

    @pytest.mark.unit
    def test_similar_zones_are_lists(self):
        """Test similar_zones are lists."""
        for name, zone in CLIMATE_ZONES.items():
            assert isinstance(zone["similar_zones"], list)

    @pytest.mark.unit
    def test_highland_similarity(self):
        """Test Yemen highland and Saudi Asir are similar."""
        yemen_hl = CLIMATE_ZONES["yemen_highland"]
        assert "saudi_asir" in yemen_hl["similar_zones"]

        saudi_asir = CLIMATE_ZONES["saudi_asir"]
        assert "yemen_highland" in saudi_asir["similar_zones"]


# ─── RegionRelevanceResult Tests ─────────────────────────────────────────────


class TestRegionRelevanceResult:
    """Tests for RegionRelevanceResult dataclass."""

    @pytest.mark.unit
    def test_default_values(self):
        """Test default result values."""
        result = RegionRelevanceResult()
        assert result.overall_score == 0.0
        assert result.is_relevant is False

    @pytest.mark.unit
    def test_is_relevant_threshold(self):
        """Test relevance threshold at 0.3."""
        result = RegionRelevanceResult(overall_score=0.3)
        assert result.is_relevant is True

        result2 = RegionRelevanceResult(overall_score=0.29)
        assert result2.is_relevant is False

    @pytest.mark.unit
    def test_to_metadata(self):
        """Test conversion to metadata dict."""
        result = RegionRelevanceResult(
            overall_score=0.85,
            climate_score=0.9,
            crop_score=0.8,
            applicable_regions=["yemen_highland"],
            adaptations_needed=["Adjust for altitude"],
        )
        metadata = result.to_metadata()
        assert "region_relevance" in metadata
        assert metadata["region_relevance"]["overall_score"] == 0.85
        assert "yemen_highland" in metadata["region_relevance"]["applicable_regions"]


# ─── Climate Compatibility Tests ──────────────────────────────────────────────


class TestClimateCompatibility:
    """Tests for climate compatibility scoring."""

    @pytest.mark.unit
    def test_direct_region_match(self, region_filter: RegionRelevanceFilter, yemen_highland_doc):
        """Test direct region match gets score 1.0."""
        result = region_filter.assess_relevance(yemen_highland_doc, ["yemen_highland"])
        assert result.climate_score == 1.0

    @pytest.mark.unit
    def test_no_geospatial_data(self, region_filter: RegionRelevanceFilter, general_doc):
        """Test document with no geospatial data gets moderate score (0.5)."""
        result = region_filter.assess_relevance(general_doc)
        assert result.climate_score == 0.5

    @pytest.mark.unit
    def test_similar_zone_match(self, region_filter: RegionRelevanceFilter):
        """Test similar zone match gets reduced but positive score."""
        doc = BaseKnowledgeDocument(
            title="Asir Farming",
            content="Agriculture in Asir",
            domain=KnowledgeDomain.CROPS,
            geospatial=GeospatialMetadata(
                applicable_regions=["saudi_asir"],  # Similar to yemen_highland
            ),
        )
        result = region_filter.assess_relevance(doc, ["yemen_highland"])
        assert result.climate_score >= 0.5  # Should get a decent score from similarity

    @pytest.mark.unit
    def test_dissimilar_region_low_score(self, region_filter: RegionRelevanceFilter, tropical_doc):
        """Test dissimilar tropical region gets low score."""
        result = region_filter.assess_relevance(tropical_doc)
        assert result.climate_score < 0.5


# ─── Crop Relevance Tests ───────────────────────────────────────────────────


class TestCropRelevance:
    """Tests for crop relevance scoring."""

    @pytest.mark.unit
    def test_mena_crop_high_score(self, region_filter: RegionRelevanceFilter):
        """Test MENA crops get high relevance score."""
        doc = BaseKnowledgeDocument(
            title="Wheat Guide",
            content="Wheat cultivation",
            domain=KnowledgeDomain.CROPS,
            tags=["crop:wheat", "crop:barley"],
        )
        result = region_filter.assess_relevance(doc)
        assert result.crop_score >= 0.8

    @pytest.mark.unit
    def test_no_crop_tags_moderate_score(self, region_filter: RegionRelevanceFilter):
        """Test document without crop tags gets moderate score."""
        doc = BaseKnowledgeDocument(
            title="Soil Guide",
            content="Soil management",
            domain=KnowledgeDomain.SOIL,
            tags=["soil", "management"],
        )
        result = region_filter.assess_relevance(doc)
        assert result.crop_score == 0.6  # General content default


# ─── Soil Compatibility Tests ────────────────────────────────────────────────


class TestSoilCompatibility:
    """Tests for soil compatibility scoring."""

    @pytest.mark.unit
    def test_regional_soil_types(self, region_filter: RegionRelevanceFilter):
        """Test regional soil types get high score."""
        doc = BaseKnowledgeDocument(
            title="Sandy Soil",
            content="Sandy soil management",
            domain=KnowledgeDomain.SOIL,
            geospatial=GeospatialMetadata(soil_types=["sandy", "calcareous"]),
        )
        result = region_filter.assess_relevance(doc)
        # Sandy and calcareous are regional soils → should score well
        assert result.overall_score > 0

    @pytest.mark.unit
    def test_no_soil_info_moderate(self, region_filter: RegionRelevanceFilter):
        """Test no soil info gives moderate score."""
        doc = BaseKnowledgeDocument(
            title="General",
            content="General content",
            domain=KnowledgeDomain.GENERAL,
        )
        # Soil score for no data should be 0.5
        result = region_filter.assess_relevance(doc)
        # Overall moderate since all scores are moderate for general content
        assert result.overall_score >= 0.3


# ─── Overall Assessment Tests ────────────────────────────────────────────────


class TestOverallAssessment:
    """Tests for overall relevance assessment."""

    @pytest.mark.unit
    def test_yemen_highland_highly_relevant(self, region_filter: RegionRelevanceFilter, yemen_highland_doc):
        """Test Yemen highland document is highly relevant for Yemen regions."""
        result = region_filter.assess_relevance(yemen_highland_doc)
        assert result.is_relevant is True
        assert result.overall_score >= 0.7

    @pytest.mark.unit
    def test_general_doc_relevant(self, region_filter: RegionRelevanceFilter, general_doc):
        """Test general document is moderately relevant everywhere."""
        result = region_filter.assess_relevance(general_doc)
        assert result.is_relevant is True  # 0.5 > 0.3 threshold

    @pytest.mark.unit
    def test_applicable_regions_found(self, region_filter: RegionRelevanceFilter, yemen_highland_doc):
        """Test applicable regions are identified."""
        result = region_filter.assess_relevance(yemen_highland_doc)
        assert "yemen_highland" in result.applicable_regions

    @pytest.mark.unit
    def test_general_doc_applies_everywhere(self, region_filter: RegionRelevanceFilter, general_doc):
        """Test general document applies to all target regions."""
        result = region_filter.assess_relevance(general_doc, ["yemen_highland", "yemen_coastal"])
        assert len(result.applicable_regions) == 2


# ─── Document Filtering Tests ───────────────────────────────────────────────


class TestDocumentFiltering:
    """Tests for batch document filtering."""

    @pytest.mark.unit
    def test_filter_documents(
        self, region_filter: RegionRelevanceFilter, yemen_highland_doc, general_doc, tropical_doc
    ):
        """Test filtering a batch of documents."""
        documents = [yemen_highland_doc, general_doc, tropical_doc]
        results = region_filter.filter_documents(documents)
        # At least yemen and general docs should pass
        assert len(results) >= 2

    @pytest.mark.unit
    def test_filter_sorted_by_score(self, region_filter, yemen_highland_doc, general_doc):
        """Test filtered results are sorted by relevance score descending."""
        documents = [general_doc, yemen_highland_doc]
        results = region_filter.filter_documents(documents)
        if len(results) >= 2:
            scores = [r[1].overall_score for r in results]
            assert scores == sorted(scores, reverse=True)

    @pytest.mark.unit
    def test_filter_empty_list(self, region_filter: RegionRelevanceFilter):
        """Test filtering an empty list."""
        results = region_filter.filter_documents([])
        assert results == []


# ─── Adaptation Suggestion Tests ─────────────────────────────────────────────


class TestAdaptationSuggestions:
    """Tests for adaptation suggestions."""

    @pytest.mark.unit
    def test_no_regions_suggests_verification(self, region_filter: RegionRelevanceFilter, general_doc):
        """Test general doc gets verification suggestion."""
        result = region_filter.assess_relevance(general_doc)
        assert any("Verify" in a or "applicability" in a.lower() for a in result.adaptations_needed)

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_arabic_adaptations(self, region_filter: RegionRelevanceFilter, general_doc):
        """Test Arabic adaptation suggestions | اختبار اقتراحات التكييف العربية"""
        result = region_filter.assess_relevance(general_doc)
        assert len(result.adaptations_needed_ar) > 0
        assert any("تحقق" in a for a in result.adaptations_needed_ar)

    @pytest.mark.unit
    def test_altitude_adaptation(self, region_filter: RegionRelevanceFilter):
        """Test altitude mismatch generates adaptation suggestion."""
        doc = BaseKnowledgeDocument(
            title="Lowland Farming",
            content="Farming at sea level",
            domain=KnowledgeDomain.CROPS,
            geospatial=GeospatialMetadata(
                applicable_regions=["test_region"],
                altitude_range_m=(0, 100),  # Low altitude
            ),
        )
        result = region_filter.assess_relevance(doc, ["yemen_highland"])
        # Yemen highland is 1500-3000m - altitude mismatch should be noted
        altitude_adaptations = [a for a in result.adaptations_needed if "altitude" in a.lower()]
        assert len(altitude_adaptations) > 0
