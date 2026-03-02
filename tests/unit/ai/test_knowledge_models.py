"""
Tests for Knowledge Domain Models
==================================
اختبارات نماذج بيانات المعرفة الزراعية

Comprehensive tests for Pydantic v2 domain models, enums,
FRESH metadata, geospatial metadata, and UltraRAG conversion.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from shared.ai.knowledge.models import (
    BaseKnowledgeDocument,
    CropKnowledgeDocument,
    FertilizerKnowledgeDocument,
    FRESHMetadata,
    GeospatialMetadata,
    HierarchyLevel,
    IrrigationKnowledgeDocument,
    KnowledgeDomain,
    KnowledgeSourceMeta,
    RemoteSensingGuideDocument,
    Sensitivity,
    SoilTypeDocument,
    SourceCredibilityLevel,
    VerificationStatus,
    WeatherPatternDocument,
)


# ─── Enum Tests ───────────────────────────────────────────────────────────────


class TestKnowledgeDomain:
    """Tests for KnowledgeDomain enum | اختبارات مجالات المعرفة"""

    @pytest.mark.unit
    def test_all_domains_defined(self):
        """Test that all 8 knowledge domains are defined."""
        assert len(KnowledgeDomain) == 8

    @pytest.mark.unit
    def test_domain_values(self):
        """Test domain string values."""
        assert KnowledgeDomain.CROPS == "crops"
        assert KnowledgeDomain.SOIL == "soil"
        assert KnowledgeDomain.IRRIGATION == "irrigation"
        assert KnowledgeDomain.FERTILIZER == "fertilizer"
        assert KnowledgeDomain.PEST_DISEASE == "pest_disease"
        assert KnowledgeDomain.WEATHER == "weather"
        assert KnowledgeDomain.REMOTE_SENSING == "remote_sensing"
        assert KnowledgeDomain.GENERAL == "general"

    @pytest.mark.unit
    def test_domain_is_str_enum(self):
        """Test that domains can be used as strings."""
        assert f"Domain: {KnowledgeDomain.CROPS}" == "Domain: crops"


class TestVerificationStatus:
    """Tests for VerificationStatus enum."""

    @pytest.mark.unit
    def test_all_statuses(self):
        """Test all verification statuses."""
        assert VerificationStatus.PENDING == "pending"
        assert VerificationStatus.APPROVED == "approved"
        assert VerificationStatus.REVIEW_REQUIRED == "review_required"
        assert VerificationStatus.REJECTED == "rejected"


class TestSourceCredibilityLevel:
    """Tests for SourceCredibilityLevel enum."""

    @pytest.mark.unit
    def test_credibility_values(self):
        """Test credibility level integer values."""
        assert SourceCredibilityLevel.COMMUNITY.value == 1
        assert SourceCredibilityLevel.SPECIALIZED_WEBSITE.value == 2
        assert SourceCredibilityLevel.LOCAL_RESEARCH.value == 3
        assert SourceCredibilityLevel.GOVERNMENT_UNIVERSITY.value == 4
        assert SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION.value == 5

    @pytest.mark.unit
    def test_credibility_comparison(self):
        """Test that credibility levels can be compared."""
        assert SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION.value > SourceCredibilityLevel.COMMUNITY.value
        assert SourceCredibilityLevel.GOVERNMENT_UNIVERSITY.value >= 4


class TestHierarchyLevel:
    """Tests for HierarchyLevel enum."""

    @pytest.mark.unit
    def test_hierarchy_values(self):
        """Test hierarchy level values."""
        assert HierarchyLevel.OVERVIEW == "overview"
        assert HierarchyLevel.DETAILED == "detailed"
        assert HierarchyLevel.EXPERT == "expert"


class TestSensitivity:
    """Tests for Sensitivity enum."""

    @pytest.mark.unit
    def test_sensitivity_values(self):
        """Test sensitivity values."""
        assert Sensitivity.PUBLIC == "public"
        assert Sensitivity.INTERNAL == "internal"
        assert Sensitivity.RESTRICTED == "restricted"


# ─── Metadata Model Tests ─────────────────────────────────────────────────────


class TestFRESHMetadata:
    """Tests for FRESH framework metadata model."""

    @pytest.mark.unit
    def test_defaults(self):
        """Test default FRESH metadata values."""
        fresh = FRESHMetadata()
        assert fresh.format == "md"
        assert fresh.relevance_domains == []
        assert fresh.expiration_date is None
        assert fresh.sensitivity == Sensitivity.PUBLIC
        assert fresh.hierarchy_level == HierarchyLevel.DETAILED

    @pytest.mark.unit
    def test_custom_values(self):
        """Test FRESH metadata with custom values."""
        fresh = FRESHMetadata(
            format="pdf",
            relevance_domains=[KnowledgeDomain.CROPS, KnowledgeDomain.IRRIGATION],
            expiration_date=date(2027, 1, 1),
            sensitivity=Sensitivity.RESTRICTED,
            hierarchy_level=HierarchyLevel.EXPERT,
        )
        assert fresh.format == "pdf"
        assert len(fresh.relevance_domains) == 2
        assert fresh.expiration_date == date(2027, 1, 1)
        assert fresh.sensitivity == Sensitivity.RESTRICTED

    @pytest.mark.unit
    def test_model_dump(self):
        """Test serialization to dict."""
        fresh = FRESHMetadata(format="html")
        d = fresh.model_dump()
        assert d["format"] == "html"
        assert d["sensitivity"] == "public"


class TestGeospatialMetadata:
    """Tests for GeospatialMetadata model."""

    @pytest.mark.unit
    def test_defaults(self):
        """Test default geospatial metadata."""
        geo = GeospatialMetadata()
        assert geo.applicable_regions == []
        assert geo.climate_zones == []
        assert geo.altitude_range_m is None
        assert geo.latitude_range is None
        assert geo.soil_types == []

    @pytest.mark.unit
    def test_with_regions(self):
        """Test geospatial metadata with regions."""
        geo = GeospatialMetadata(
            applicable_regions=["yemen_highland", "saudi_asir"],
            climate_zones=["semi_arid_highland"],
            altitude_range_m=(1500, 3000),
            latitude_range=(13.0, 17.0),
            soil_types=["loam", "clay loam"],
        )
        assert len(geo.applicable_regions) == 2
        assert geo.altitude_range_m == (1500, 3000)
        assert "loam" in geo.soil_types


class TestKnowledgeSourceMeta:
    """Tests for KnowledgeSourceMeta model."""

    @pytest.mark.unit
    def test_defaults(self):
        """Test default source metadata."""
        source = KnowledgeSourceMeta()
        assert source.source_name == ""
        assert source.credibility == SourceCredibilityLevel.SPECIALIZED_WEBSITE
        assert source.language == "both"
        assert source.agrovoc_concepts == []

    @pytest.mark.unit
    def test_fao_source(self):
        """Test creating an FAO source."""
        source = KnowledgeSourceMeta(
            source_name="FAO Water Productivity",
            source_name_ar="إنتاجية المياه - الفاو",
            source_url="https://www.fao.org/aquastat",
            credibility=SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION,
            agrovoc_concepts=["c_3693", "c_7951"],
        )
        assert source.credibility.value == 5
        assert "c_3693" in source.agrovoc_concepts


# ─── Document Model Tests ─────────────────────────────────────────────────────


class TestBaseKnowledgeDocument:
    """Tests for BaseKnowledgeDocument model."""

    @pytest.mark.unit
    def test_auto_generated_id(self):
        """Test that document IDs are auto-generated."""
        doc = BaseKnowledgeDocument(title="Test", domain=KnowledgeDomain.GENERAL)
        assert doc.id.startswith("kb_")
        assert len(doc.id) == 15  # "kb_" + 12 hex chars

    @pytest.mark.unit
    def test_unique_ids(self):
        """Test that each document gets a unique ID."""
        doc1 = BaseKnowledgeDocument(title="A", domain=KnowledgeDomain.GENERAL)
        doc2 = BaseKnowledgeDocument(title="B", domain=KnowledgeDomain.GENERAL)
        assert doc1.id != doc2.id

    @pytest.mark.unit
    def test_default_values(self):
        """Test default field values."""
        doc = BaseKnowledgeDocument(title="Test Doc", domain=KnowledgeDomain.CROPS)
        assert doc.title == "Test Doc"
        assert doc.title_ar == ""
        assert doc.content == ""
        assert doc.content_ar == ""
        assert doc.verification_status == VerificationStatus.PENDING
        assert doc.version == "1.0.0"
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.fresh, FRESHMetadata)
        assert isinstance(doc.geospatial, GeospatialMetadata)
        assert isinstance(doc.source, KnowledgeSourceMeta)

    @pytest.mark.unit
    def test_bilingual_content(self):
        """Test bilingual content support | اختبار ثنائية اللغة"""
        doc = BaseKnowledgeDocument(
            title="Wheat Irrigation",
            title_ar="ري القمح",
            content="Wheat requires 450-650mm of water per season",
            content_ar="يحتاج القمح 450-650 ملم من المياه في الموسم",
            domain=KnowledgeDomain.IRRIGATION,
        )
        assert doc.title == "Wheat Irrigation"
        assert doc.title_ar == "ري القمح"
        assert "450-650mm" in doc.content
        assert "450-650 ملم" in doc.content_ar

    @pytest.mark.unit
    def test_to_knowledge_document(self):
        """Test conversion to UltraRAG-compatible dict."""
        doc = BaseKnowledgeDocument(
            title="Test",
            title_ar="اختبار",
            content="English content",
            content_ar="محتوى عربي",
            domain=KnowledgeDomain.CROPS,
            tags=["wheat", "irrigation"],
            source=KnowledgeSourceMeta(
                source_url="https://fao.org",
                credibility=SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION,
            ),
            verification_status=VerificationStatus.APPROVED,
        )
        result = doc.to_knowledge_document()
        assert result["id"] == doc.id
        assert result["title"] == "Test"
        assert result["title_ar"] == "اختبار"
        assert result["source"] == "https://fao.org"
        assert result["collection"] == "crop_knowledge"
        assert result["metadata"]["domain"] == "crops"
        assert result["metadata"]["tags"] == ["wheat", "irrigation"]
        assert result["metadata"]["source_credibility"] == 5
        assert result["metadata"]["verification_status"] == "approved"

    @pytest.mark.unit
    def test_get_collection_mapping(self):
        """Test domain-to-collection mapping for all domains."""
        mappings = {
            KnowledgeDomain.CROPS: "crop_knowledge",
            KnowledgeDomain.SOIL: "soil_knowledge",
            KnowledgeDomain.IRRIGATION: "irrigation_practices",
            KnowledgeDomain.FERTILIZER: "fertilizer_knowledge",
            KnowledgeDomain.PEST_DISEASE: "pest_knowledge",
            KnowledgeDomain.WEATHER: "weather_knowledge",
            KnowledgeDomain.REMOTE_SENSING: "remote_sensing_knowledge",
            KnowledgeDomain.GENERAL: "general_agriculture",
        }
        for domain, expected_collection in mappings.items():
            doc = BaseKnowledgeDocument(title="Test", domain=domain)
            assert doc._get_collection() == expected_collection


class TestCropKnowledgeDocument:
    """Tests for CropKnowledgeDocument model."""

    @pytest.mark.unit
    def test_defaults(self):
        """Test crop document defaults."""
        doc = CropKnowledgeDocument(title="Wheat")
        assert doc.domain == KnowledgeDomain.CROPS
        assert doc.scientific_name == ""
        assert doc.varieties == []
        assert doc.kc_values == {}

    @pytest.mark.unit
    def test_wheat_document(self):
        """Test creating a wheat knowledge document."""
        doc = CropKnowledgeDocument(
            title="Wheat (Triticum aestivum)",
            title_ar="القمح",
            scientific_name="Triticum aestivum",
            family="Poaceae",
            family_ar="النجيلية",
            kc_values={"initial": 0.3, "mid_season": 1.15, "late_season": 0.4},
            optimal_temperature_c=(15.0, 25.0),
            water_requirement_mm_season=(450.0, 650.0),
            harvest_days=120,
        )
        assert doc.scientific_name == "Triticum aestivum"
        assert doc.kc_values["mid_season"] == 1.15
        assert doc.optimal_temperature_c == (15.0, 25.0)
        assert doc.harvest_days == 120

    @pytest.mark.unit
    def test_collection_mapping(self):
        """Test crop documents map to crop_knowledge collection."""
        doc = CropKnowledgeDocument(title="Barley")
        assert doc._get_collection() == "crop_knowledge"


class TestSoilTypeDocument:
    """Tests for SoilTypeDocument model."""

    @pytest.mark.unit
    def test_soil_document(self):
        """Test creating a soil knowledge document."""
        doc = SoilTypeDocument(
            title="Sandy Soil",
            title_ar="التربة الرملية",
            soil_classification="Aridisol",
            texture="sandy",
            texture_ar="رملية",
            ph_range=(7.0, 8.5),
            ec_range_ds_m=(0.5, 4.0),
            organic_matter_percent=(0.3, 1.5),
            suitable_crops=["dates", "watermelon"],
        )
        assert doc.domain == KnowledgeDomain.SOIL
        assert doc.ph_range == (7.0, 8.5)
        assert "dates" in doc.suitable_crops


class TestIrrigationKnowledgeDocument:
    """Tests for IrrigationKnowledgeDocument model."""

    @pytest.mark.unit
    def test_drip_irrigation(self):
        """Test creating drip irrigation document."""
        doc = IrrigationKnowledgeDocument(
            title="Drip Irrigation",
            title_ar="الري بالتنقيط",
            method="drip",
            method_ar="تنقيط",
            efficiency_percent=(85.0, 95.0),
            suitable_crops=["tomato", "cucumber", "dates"],
        )
        assert doc.domain == KnowledgeDomain.IRRIGATION
        assert doc.efficiency_percent == (85.0, 95.0)


class TestFertilizerKnowledgeDocument:
    """Tests for FertilizerKnowledgeDocument model."""

    @pytest.mark.unit
    def test_urea_document(self):
        """Test creating urea fertilizer document."""
        doc = FertilizerKnowledgeDocument(
            title="Urea",
            title_ar="اليوريا",
            fertilizer_type="nitrogen",
            npk_ratio="46-0-0",
            nutrient_content_percent={"N": 46.0},
            safety_notes=["Avoid application before heavy rain"],
        )
        assert doc.domain == KnowledgeDomain.FERTILIZER
        assert doc.nutrient_content_percent["N"] == 46.0


class TestWeatherPatternDocument:
    """Tests for WeatherPatternDocument model."""

    @pytest.mark.unit
    def test_climate_zone(self):
        """Test creating a climate zone document."""
        doc = WeatherPatternDocument(
            title="Yemen Highland Climate",
            title_ar="مناخ المرتفعات اليمنية",
            climate_zone="semi_arid_highland",
            temperature_range_c={"summer": (18.0, 28.0), "winter": (5.0, 15.0)},
            annual_rainfall_mm=(300.0, 800.0),
            weather_risks=["frost", "drought"],
        )
        assert doc.domain == KnowledgeDomain.WEATHER
        assert doc.annual_rainfall_mm == (300.0, 800.0)


class TestRemoteSensingGuideDocument:
    """Tests for RemoteSensingGuideDocument model."""

    @pytest.mark.unit
    def test_ndvi_guide(self):
        """Test creating NDVI guide document."""
        doc = RemoteSensingGuideDocument(
            title="NDVI Interpretation Guide",
            title_ar="دليل تفسير NDVI",
            index_name="NDVI",
            index_name_ar="مؤشر الاختلاف الطبيعي للغطاء النباتي",
            formula="(NIR - Red) / (NIR + Red)",
            value_range=(-1.0, 1.0),
            data_source="Sentinel-2",
            spatial_resolution_m=10.0,
            temporal_resolution_days=5,
        )
        assert doc.domain == KnowledgeDomain.REMOTE_SENSING
        assert doc.formula == "(NIR - Red) / (NIR + Red)"
        assert doc.spatial_resolution_m == 10.0
