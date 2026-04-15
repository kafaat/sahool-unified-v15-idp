"""
Tests for shared/ai/knowledge/models.py
==========================================
اختبارات نماذج بيانات المعرفة الزراعية

Tests cover:
- All enums: KnowledgeDomain, VerificationStatus, SourceCredibilityLevel, etc.
- Metadata models: FRESHMetadata, GeospatialMetadata, KnowledgeSourceMeta
- Document models: BaseKnowledgeDocument and all subclasses
- to_knowledge_document() conversion
- Default values and field validation
"""

import pytest
from datetime import date, datetime

from shared.ai.knowledge.models import (
    KnowledgeDomain,
    VerificationStatus,
    SourceCredibilityLevel,
    HierarchyLevel,
    Sensitivity,
    SeasonalRelevance,
    FRESHMetadata,
    GeospatialMetadata,
    KnowledgeSourceMeta,
    BaseKnowledgeDocument,
    CropKnowledgeDocument,
    SoilTypeDocument,
    IrrigationKnowledgeDocument,
    FertilizerKnowledgeDocument,
    WeatherPatternDocument,
    RemoteSensingGuideDocument,
    SmartAgricultureDocument,
    PestVisionDocument,
    PrecisionFarmingDocument,
    DigitalTwinDocument,
    BestPracticesDocument,
)


# ─────────────────────────────────────────────────────────────────────────────
# Enum Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeDomain:
    def test_all_values(self):
        expected = {
            "crops", "soil", "irrigation", "fertilizer", "pest_disease",
            "weather", "remote_sensing", "smart_agriculture",
            "precision_farming", "digital_twin", "general",
        }
        actual = {d.value for d in KnowledgeDomain}
        assert actual == expected

    def test_is_str_enum(self):
        assert isinstance(KnowledgeDomain.CROPS, str)
        assert KnowledgeDomain.CROPS == "crops"


class TestVerificationStatus:
    def test_all_values(self):
        expected = {"pending", "approved", "review_required", "rejected"}
        actual = {s.value for s in VerificationStatus}
        assert actual == expected


class TestSourceCredibilityLevel:
    def test_values_are_integers(self):
        assert SourceCredibilityLevel.COMMUNITY == 1
        assert SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION == 5

    def test_ordering(self):
        assert SourceCredibilityLevel.COMMUNITY < SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION
        assert SourceCredibilityLevel.LOCAL_RESEARCH < SourceCredibilityLevel.GOVERNMENT_UNIVERSITY


class TestHierarchyLevel:
    def test_all_values(self):
        assert HierarchyLevel.OVERVIEW == "overview"
        assert HierarchyLevel.DETAILED == "detailed"
        assert HierarchyLevel.EXPERT == "expert"


class TestSensitivity:
    def test_all_values(self):
        assert Sensitivity.PUBLIC == "public"
        assert Sensitivity.INTERNAL == "internal"
        assert Sensitivity.RESTRICTED == "restricted"


class TestSeasonalRelevance:
    def test_all_values(self):
        expected = {"all_year", "winter", "spring", "summer", "fall", "planting", "growing", "harvest"}
        actual = {s.value for s in SeasonalRelevance}
        assert actual == expected


# ─────────────────────────────────────────────────────────────────────────────
# Metadata Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestFRESHMetadata:
    def test_defaults(self):
        m = FRESHMetadata()
        assert m.format == "md"
        assert m.relevance_domains == []
        assert m.expiration_date is None
        assert m.sensitivity == Sensitivity.PUBLIC
        assert m.hierarchy_level == HierarchyLevel.DETAILED
        assert m.seasonal_relevance == SeasonalRelevance.ALL_YEAR

    def test_custom_values(self):
        m = FRESHMetadata(
            format="json",
            relevance_domains=[KnowledgeDomain.CROPS, KnowledgeDomain.SOIL],
            expiration_date=date(2026, 12, 31),
            sensitivity=Sensitivity.RESTRICTED,
            hierarchy_level=HierarchyLevel.EXPERT,
            seasonal_relevance=SeasonalRelevance.WINTER,
        )
        assert m.format == "json"
        assert len(m.relevance_domains) == 2
        assert m.expiration_date == date(2026, 12, 31)

    def test_model_dump(self):
        m = FRESHMetadata()
        d = m.model_dump()
        assert "format" in d
        assert "sensitivity" in d


class TestGeospatialMetadata:
    def test_defaults(self):
        g = GeospatialMetadata()
        assert g.applicable_regions == []
        assert g.climate_zones == []
        assert g.altitude_range_m is None
        assert g.latitude_range is None
        assert g.soil_types == []

    def test_custom_values(self):
        g = GeospatialMetadata(
            applicable_regions=["MENA", "Gulf"],
            climate_zones=["arid", "semi-arid"],
            altitude_range_m=(0, 500),
            latitude_range=(12.0, 25.0),
            soil_types=["sandy", "clay"],
        )
        assert len(g.applicable_regions) == 2
        assert g.altitude_range_m == (0, 500)


class TestKnowledgeSourceMeta:
    def test_defaults(self):
        s = KnowledgeSourceMeta()
        assert s.source_name == ""
        assert s.credibility == SourceCredibilityLevel.SPECIALIZED_WEBSITE
        assert s.language == "both"
        assert s.agrovoc_concepts == []

    def test_custom_values(self):
        s = KnowledgeSourceMeta(
            source_name="FAO",
            source_name_ar="منظمة الأغذية والزراعة",
            credibility=SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION,
            doi="10.1234/example",
        )
        assert s.source_name == "FAO"
        assert s.credibility == SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION
        assert s.doi == "10.1234/example"


# ─────────────────────────────────────────────────────────────────────────────
# Document Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestBaseKnowledgeDocument:
    def test_minimal_creation(self):
        doc = BaseKnowledgeDocument(
            title="Test Document",
            domain=KnowledgeDomain.GENERAL,
        )
        assert doc.title == "Test Document"
        assert doc.domain == KnowledgeDomain.GENERAL
        assert doc.id.startswith("kb_")
        assert doc.version == "1.0.0"
        assert doc.verification_status == VerificationStatus.PENDING

    def test_id_auto_generated(self):
        doc1 = BaseKnowledgeDocument(title="A", domain=KnowledgeDomain.CROPS)
        doc2 = BaseKnowledgeDocument(title="B", domain=KnowledgeDomain.CROPS)
        assert doc1.id != doc2.id

    def test_defaults(self):
        doc = BaseKnowledgeDocument(title="T", domain=KnowledgeDomain.SOIL)
        assert doc.title_ar == ""
        assert doc.content == ""
        assert doc.content_ar == ""
        assert doc.tags == []
        assert isinstance(doc.fresh, FRESHMetadata)
        assert isinstance(doc.geospatial, GeospatialMetadata)
        assert isinstance(doc.source, KnowledgeSourceMeta)
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.updated_at, datetime)

    def test_to_knowledge_document(self):
        doc = BaseKnowledgeDocument(
            title="Wheat Guide",
            title_ar="دليل القمح",
            content="Wheat growing guide",
            domain=KnowledgeDomain.CROPS,
            tags=["wheat", "guide"],
            version="2.0.0",
        )
        result = doc.to_knowledge_document()
        assert result["id"] == doc.id
        assert result["title"] == "Wheat Guide"
        assert result["title_ar"] == "دليل القمح"
        assert result["collection"] == "crop_knowledge"
        assert result["metadata"]["domain"] == "crops"
        assert result["metadata"]["tags"] == ["wheat", "guide"]
        assert result["metadata"]["version"] == "2.0.0"

    def test_get_collection_mapping(self):
        """Test that each domain maps to the correct collection."""
        mappings = {
            KnowledgeDomain.CROPS: "crop_knowledge",
            KnowledgeDomain.SOIL: "soil_knowledge",
            KnowledgeDomain.IRRIGATION: "irrigation_practices",
            KnowledgeDomain.FERTILIZER: "fertilizer_knowledge",
            KnowledgeDomain.PEST_DISEASE: "pest_knowledge",
            KnowledgeDomain.WEATHER: "weather_knowledge",
            KnowledgeDomain.REMOTE_SENSING: "remote_sensing_knowledge",
            KnowledgeDomain.SMART_AGRICULTURE: "smart_agriculture_knowledge",
            KnowledgeDomain.PRECISION_FARMING: "precision_farming_knowledge",
            KnowledgeDomain.DIGITAL_TWIN: "digital_twin_knowledge",
            KnowledgeDomain.GENERAL: "general_agriculture",
        }
        for domain, expected_collection in mappings.items():
            doc = BaseKnowledgeDocument(title="T", domain=domain)
            result = doc.to_knowledge_document()
            assert result["collection"] == expected_collection, f"Failed for {domain}"


class TestCropKnowledgeDocument:
    def test_default_domain(self):
        doc = CropKnowledgeDocument(title="Wheat")
        assert doc.domain == KnowledgeDomain.CROPS

    def test_crop_specific_fields(self):
        doc = CropKnowledgeDocument(
            title="Wheat",
            scientific_name="Triticum aestivum",
            family="Poaceae",
            varieties=["Sakha 95", "Giza 171"],
            harvest_days=150,
            optimal_temperature_c=(15.0, 25.0),
            kc_values={"initial": 0.3, "mid": 1.15},
        )
        assert doc.scientific_name == "Triticum aestivum"
        assert len(doc.varieties) == 2
        assert doc.harvest_days == 150
        assert doc.optimal_temperature_c == (15.0, 25.0)
        assert doc.kc_values["mid"] == 1.15

    def test_defaults(self):
        doc = CropKnowledgeDocument(title="T")
        assert doc.scientific_name == ""
        assert doc.varieties == []
        assert doc.growth_stages == []
        assert doc.kc_values == {}
        assert doc.optimal_temperature_c is None
        assert doc.water_requirement_mm_season is None
        assert doc.harvest_days is None


class TestSoilTypeDocument:
    def test_default_domain(self):
        doc = SoilTypeDocument(title="Clay Soil")
        assert doc.domain == KnowledgeDomain.SOIL

    def test_soil_fields(self):
        doc = SoilTypeDocument(
            title="Sandy Loam",
            soil_classification="Entisol",
            texture="sandy loam",
            ph_range=(6.0, 7.5),
            suitable_crops=["wheat", "barley"],
        )
        assert doc.soil_classification == "Entisol"
        assert doc.ph_range == (6.0, 7.5)
        assert len(doc.suitable_crops) == 2


class TestIrrigationKnowledgeDocument:
    def test_default_domain(self):
        doc = IrrigationKnowledgeDocument(title="Drip Irrigation")
        assert doc.domain == KnowledgeDomain.IRRIGATION

    def test_fields(self):
        doc = IrrigationKnowledgeDocument(
            title="Drip",
            method="drip",
            efficiency_percent=(85.0, 95.0),
            advantages=["water saving", "precise"],
        )
        assert doc.efficiency_percent == (85.0, 95.0)
        assert len(doc.advantages) == 2


class TestFertilizerKnowledgeDocument:
    def test_default_domain(self):
        doc = FertilizerKnowledgeDocument(title="Urea")
        assert doc.domain == KnowledgeDomain.FERTILIZER

    def test_fields(self):
        doc = FertilizerKnowledgeDocument(
            title="Urea",
            npk_ratio="46-0-0",
            nutrient_content_percent={"N": 46.0},
        )
        assert doc.npk_ratio == "46-0-0"
        assert doc.nutrient_content_percent["N"] == 46.0


class TestWeatherPatternDocument:
    def test_default_domain(self):
        doc = WeatherPatternDocument(title="Arid Climate")
        assert doc.domain == KnowledgeDomain.WEATHER


class TestRemoteSensingGuideDocument:
    def test_default_domain(self):
        doc = RemoteSensingGuideDocument(title="NDVI Guide")
        assert doc.domain == KnowledgeDomain.REMOTE_SENSING

    def test_fields(self):
        doc = RemoteSensingGuideDocument(
            title="NDVI",
            index_name="NDVI",
            formula="(NIR-RED)/(NIR+RED)",
            value_range=(-1.0, 1.0),
            spatial_resolution_m=10.0,
        )
        assert doc.formula == "(NIR-RED)/(NIR+RED)"
        assert doc.spatial_resolution_m == 10.0


class TestSmartAgricultureDocument:
    def test_default_domain(self):
        doc = SmartAgricultureDocument(title="IoT Sensors")
        assert doc.domain == KnowledgeDomain.SMART_AGRICULTURE

    def test_fields(self):
        doc = SmartAgricultureDocument(
            title="IoT",
            technology_type="iot",
            connectivity_requirement="low",
            integration_protocols=["MQTT", "NATS"],
        )
        assert doc.technology_type == "iot"
        assert len(doc.integration_protocols) == 2


class TestPestVisionDocument:
    def test_default_domain(self):
        doc = PestVisionDocument(title="RPW Detection")
        assert doc.domain == KnowledgeDomain.PEST_DISEASE

    def test_fields(self):
        doc = PestVisionDocument(
            title="RPW",
            detection_model="yolo26",
            target_classes=["red_palm_weevil"],
            map_score=0.96,
            image_size_px=640,
            min_confidence=0.25,
        )
        assert doc.map_score == 0.96
        assert doc.image_size_px == 640
        assert doc.min_confidence == 0.25


class TestPrecisionFarmingDocument:
    def test_default_domain(self):
        doc = PrecisionFarmingDocument(title="VRA")
        assert doc.domain == KnowledgeDomain.PRECISION_FARMING

    def test_fields(self):
        doc = PrecisionFarmingDocument(
            title="RTK Guidance",
            guidance_type="rtk",
            gps_accuracy_cm=2.5,
            soil_sampling_grid_m=25.0,
        )
        assert doc.gps_accuracy_cm == 2.5


class TestDigitalTwinDocument:
    def test_default_domain(self):
        doc = DigitalTwinDocument(title="Crop Twin")
        assert doc.domain == KnowledgeDomain.DIGITAL_TWIN

    def test_fields(self):
        doc = DigitalTwinDocument(
            title="AquaCrop Twin",
            simulation_type="crop_growth",
            model_engine="aquacrop",
            update_frequency_minutes=60,
            supported_crops=["wheat", "barley"],
        )
        assert doc.model_engine == "aquacrop"
        assert doc.update_frequency_minutes == 60


class TestBestPracticesDocument:
    def test_default_domain(self):
        doc = BestPracticesDocument(title="GAP Guide")
        assert doc.domain == KnowledgeDomain.GENERAL

    def test_fields(self):
        doc = BestPracticesDocument(
            title="IPM",
            practice_category="ipm",
            success_rate_percent=85.0,
            applicable_crops=["wheat"],
            compliance_standards=["GlobalGAP"],
        )
        assert doc.success_rate_percent == 85.0
        assert "GlobalGAP" in doc.compliance_standards
