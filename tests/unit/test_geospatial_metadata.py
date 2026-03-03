"""
Tests for ISO 19115 Geospatial Metadata Module
اختبارات وحدة البيانات الوصفية الجغرافية ISO 19115

Tests cover:
- ISO 19115 model creation and validation
- Factory functions for different data types
- Data quality reports (ISO 19157)
- Lineage tracking
- Geographic extent validation
- ISO-compliant dictionary export
"""

import pytest
from datetime import datetime, UTC

from shared.geospatial_metadata import (
    GeospatialMetadataRecord,
    MD_Metadata,
    MD_DataIdentification,
    MD_ReferenceSystem,
    MD_Resolution,
    MD_Keywords,
    MD_LegalConstraints,
    MD_ScopeCode,
    MD_TopicCategory,
    MD_SpatialRepresentationType,
    CI_Citation,
    CI_ResponsibleParty,
    CI_RoleCode,
    EX_Extent,
    EX_GeographicBoundingBox,
    EX_TemporalExtent,
    DataQualityReport,
    DQ_Scope,
    LI_Lineage,
    LI_ProcessStep,
    LI_Source,
    create_field_metadata,
    create_ndvi_metadata,
    create_terrain_metadata,
    create_satellite_metadata,
    create_iot_sensor_metadata,
)


# =============================================================================
# ISO 19115 Core Models
# =============================================================================


class TestCICitation:
    """Tests for CI_Citation model."""

    def test_create_citation(self):
        citation = CI_Citation(
            title="Test Field Boundary",
            title_ar="حدود الحقل التجريبي",
            date_type="creation",
        )
        assert citation.title == "Test Field Boundary"
        assert citation.title_ar == "حدود الحقل التجريبي"
        assert citation.date_type == "creation"
        assert citation.identifier.startswith("SAHOOL-")

    def test_citation_with_responsible_party(self):
        party = CI_ResponsibleParty(
            individual_name="Test User",
            role=CI_RoleCode.OWNER,
        )
        citation = CI_Citation(
            title="Test",
            cited_responsible_party=[party],
        )
        assert len(citation.cited_responsible_party) == 1
        assert citation.cited_responsible_party[0].role == CI_RoleCode.OWNER


class TestCIResponsibleParty:
    """Tests for CI_ResponsibleParty model."""

    def test_default_party(self):
        party = CI_ResponsibleParty()
        assert party.organisation_name == "KAFAAT - SAHOOL Platform"
        assert party.organisation_name_ar == "كفاءات - منصة سهول"
        assert party.role == CI_RoleCode.POINT_OF_CONTACT


class TestEXGeographicBoundingBox:
    """Tests for EX_GeographicBoundingBox model."""

    def test_valid_bbox(self):
        bbox = EX_GeographicBoundingBox(
            west_bound_longitude=46.7,
            east_bound_longitude=46.8,
            south_bound_latitude=24.7,
            north_bound_latitude=24.8,
        )
        assert bbox.west_bound_longitude == 46.7
        assert bbox.north_bound_latitude == 24.8

    def test_invalid_east_lt_west(self):
        with pytest.raises(ValueError, match="East longitude"):
            EX_GeographicBoundingBox(
                west_bound_longitude=46.8,
                east_bound_longitude=46.7,
                south_bound_latitude=24.7,
                north_bound_latitude=24.8,
            )

    def test_invalid_longitude_range(self):
        with pytest.raises(ValueError):
            EX_GeographicBoundingBox(
                west_bound_longitude=200.0,
                east_bound_longitude=46.8,
                south_bound_latitude=24.7,
                north_bound_latitude=24.8,
            )

    def test_invalid_north_lt_south(self):
        with pytest.raises(ValueError, match="North latitude"):
            EX_GeographicBoundingBox(
                west_bound_longitude=46.7,
                east_bound_longitude=46.8,
                south_bound_latitude=25.0,
                north_bound_latitude=24.0,
            )


class TestEXTemporalExtent:
    """Tests for EX_TemporalExtent model."""

    def test_valid_temporal(self):
        te = EX_TemporalExtent(
            begin_position=datetime(2025, 1, 1, tzinfo=UTC),
            end_position=datetime(2025, 12, 31, tzinfo=UTC),
        )
        assert te.begin_position.year == 2025
        assert te.end_position.year == 2025

    def test_ongoing(self):
        te = EX_TemporalExtent(
            begin_position=datetime(2025, 1, 1, tzinfo=UTC),
        )
        assert te.end_position is None

    def test_end_before_begin(self):
        with pytest.raises(ValueError):
            EX_TemporalExtent(
                begin_position=datetime(2025, 12, 31, tzinfo=UTC),
                end_position=datetime(2025, 1, 1, tzinfo=UTC),
            )


class TestEXExtent:
    """Tests for EX_Extent model including vertical extent validation."""

    def test_valid_vertical_extent(self):
        ext = EX_Extent(vertical_min_m=100.0, vertical_max_m=500.0)
        assert ext.vertical_min_m == 100.0
        assert ext.vertical_max_m == 500.0

    def test_invalid_vertical_max_lt_min(self):
        with pytest.raises(ValueError, match="vertical_max_m.*must be >= vertical_min_m"):
            EX_Extent(vertical_min_m=500.0, vertical_max_m=100.0)

    def test_vertical_none_values_ok(self):
        ext = EX_Extent(vertical_min_m=None, vertical_max_m=None)
        assert ext.vertical_min_m is None

    def test_vertical_only_max_ok(self):
        ext = EX_Extent(vertical_max_m=500.0)
        assert ext.vertical_max_m == 500.0


class TestMDReferenceSystem:
    """Tests for MD_ReferenceSystem model."""

    def test_wgs84_preset(self):
        crs = MD_ReferenceSystem.wgs84()
        assert crs.code == "EPSG:4326"
        assert crs.code_space == "EPSG"

    def test_utm38n_preset(self):
        crs = MD_ReferenceSystem.utm_zone_38n()
        assert crs.code == "EPSG:32638"
        assert "Arabian Peninsula" in crs.description

    def test_utm39n_preset(self):
        crs = MD_ReferenceSystem.utm_zone_39n()
        assert crs.code == "EPSG:32639"


# =============================================================================
# Data Quality (ISO 19157)
# =============================================================================


class TestDataQualityReport:
    """Tests for DataQualityReport and DQ_Element models."""

    def test_empty_report(self):
        report = DataQualityReport()
        assert report.scope.level == MD_ScopeCode.DATASET
        assert len(report.report) == 0

    def test_positional_accuracy(self):
        report = DataQualityReport()
        report.add_positional_accuracy(3.5, method="RTK GPS")
        assert len(report.report) == 1
        elem = report.report[0]
        assert elem.quality_type == "positionalAccuracy"
        assert elem.quantitative_result.value == 3.5
        assert elem.quantitative_result.value_unit == "m"

    def test_completeness(self):
        report = DataQualityReport()
        report.add_completeness(95.0)
        elem = report.report[0]
        assert elem.quality_type == "completeness"
        assert elem.quantitative_result.value == 95.0

    def test_thematic_accuracy(self):
        report = DataQualityReport()
        report.add_thematic_accuracy(87.5)
        elem = report.report[0]
        assert elem.quality_type == "thematicAccuracy"

    def test_conformance(self):
        report = DataQualityReport()
        report.add_conformance("GeoJSON RFC 7946", is_conformant=True)
        elem = report.report[0]
        assert elem.conformance_result.is_conformant is True
        assert "GeoJSON" in elem.conformance_result.specification

    def test_logical_consistency(self):
        report = DataQualityReport()
        report.add_logical_consistency(98.5, name="Topological consistency")
        elem = report.report[0]
        assert elem.quality_type == "logicalConsistency"
        assert elem.quantitative_result.value == 98.5
        assert elem.quantitative_result.value_unit == "%"

    def test_overall_quality_score(self):
        report = DataQualityReport()
        report.add_positional_accuracy(5.0)       # 100 - 5 = 95 (weight 0.3)
        report.add_completeness(90.0)              # 90 (weight 0.25)
        report.add_thematic_accuracy(85.0)         # 85 (weight 0.25)
        score = report.overall_quality_score()
        assert score is not None
        assert 85.0 <= score <= 95.0  # Weighted average should be in this range

    def test_overall_quality_score_empty(self):
        report = DataQualityReport()
        assert report.overall_quality_score() is None

    def test_overall_quality_score_conformance_only(self):
        """Conformance elements have no quantitative result, score should be None."""
        report = DataQualityReport()
        report.add_conformance("ISO 19115", is_conformant=True)
        assert report.overall_quality_score() is None

    def test_overall_quality_score_perfect_accuracy(self):
        """0m positional error = 100 score."""
        report = DataQualityReport()
        report.add_positional_accuracy(0.0)
        score = report.overall_quality_score()
        assert score == 100.0


# =============================================================================
# Lineage (ISO 19115 Section 6.6)
# =============================================================================


class TestLineage:
    """Tests for LI_Lineage, LI_ProcessStep, LI_Source."""

    def test_lineage_creation(self):
        lineage = LI_Lineage(
            statement="Data captured via GPS survey",
            statement_ar="بيانات مسح GPS",
        )
        assert lineage.statement == "Data captured via GPS survey"
        assert len(lineage.source) == 0
        assert len(lineage.process_step) == 0

    def test_add_step(self):
        lineage = LI_Lineage(statement="Test lineage")
        step = lineage.add_step(
            description="Processing step 1",
            description_ar="خطوة المعالجة 1",
            software="PostGIS 3.4",
            algorithm="ST_Buffer",
            parameters={"distance": 10.0},
        )
        assert len(lineage.process_step) == 1
        assert step.software_reference == "PostGIS 3.4"
        assert step.parameters == {"distance": 10.0}

    def test_lineage_with_source(self):
        source = LI_Source(
            description="Sentinel-2 L2A imagery",
            source_spatial_resolution=MD_Resolution(distance_m=10.0),
        )
        lineage = LI_Lineage(
            statement="NDVI from satellite",
            source=[source],
        )
        assert len(lineage.source) == 1
        assert lineage.source[0].source_spatial_resolution.distance_m == 10.0


# =============================================================================
# MD_Metadata Root Entity
# =============================================================================


class TestMDMetadata:
    """Tests for MD_Metadata root entity."""

    def test_minimal_metadata(self):
        md = MD_Metadata(
            identification_info=MD_DataIdentification(
                citation=CI_Citation(title="Test Dataset"),
                abstract="Test abstract",
            )
        )
        assert md.metadata_identifier.startswith("MD-")
        assert md.metadata_standard_name == "ISO 19115-1:2014"
        assert md.hierarchy_level == MD_ScopeCode.DATASET
        assert len(md.metadata_contact) == 1

    def test_to_iso_dict(self):
        md = MD_Metadata(
            identification_info=MD_DataIdentification(
                citation=CI_Citation(title="Export Test"),
                abstract="Testing ISO dict export",
                extent=[
                    EX_Extent(
                        geographic_element=EX_GeographicBoundingBox(
                            west_bound_longitude=46.7,
                            east_bound_longitude=46.8,
                            south_bound_latitude=24.7,
                            north_bound_latitude=24.8,
                        )
                    )
                ],
            )
        )
        iso_dict = md.to_iso_dict()
        assert "MD_Metadata" in iso_dict
        root = iso_dict["MD_Metadata"]
        assert root["metadataStandardName"] == "ISO 19115-1:2014"
        assert "identificationInfo" in root
        assert "referenceSystemInfo" in root


# =============================================================================
# Factory Functions
# =============================================================================


class TestCreateFieldMetadata:
    """Tests for create_field_metadata factory."""

    def test_basic_field(self):
        record = create_field_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            title="North Wheat Field",
            title_ar="الحقل الشمالي للقمح",
            abstract="Boundary of 8.5 ha wheat field",
            bbox=(46.7, 24.7, 46.8, 24.8),
            area_hectares=8.5,
            accuracy_m=3.0,
        )
        assert record.domain == "field"
        assert record.resource_id == "FIELD-001"
        assert record.resource_type == "field_boundary"
        assert record.tenant_id == "tenant-001"
        assert record.metadata.identification_info.citation.title == "North Wheat Field"
        assert MD_TopicCategory.FARMING in record.metadata.identification_info.topic_category
        assert record.metadata.lineage is not None
        assert len(record.metadata.lineage.process_step) >= 1

    def test_field_quality(self):
        record = create_field_metadata(
            field_id="FIELD-002",
            tenant_id="tenant-001",
            title="South Field",
            abstract="Test field",
            bbox=(46.7, 24.7, 46.8, 24.8),
            accuracy_m=2.0,
        )
        quality = record.metadata.data_quality_info
        assert quality is not None
        assert len(quality.report) >= 2  # positional accuracy + conformance


class TestCreateNDVIMetadata:
    """Tests for create_ndvi_metadata factory."""

    def test_ndvi_metadata(self):
        record = create_ndvi_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            bbox=(46.7, 24.7, 46.8, 24.8),
            acquisition_date=datetime(2025, 6, 15, tzinfo=UTC),
            cloud_coverage_pct=5.0,
            mean_ndvi=0.72,
        )
        assert record.domain == "ndvi"
        assert record.resource_type == "ndvi_reading"
        assert "ndvi" in record.tags
        assert record.metadata.lineage is not None
        assert len(record.metadata.lineage.process_step) == 3


class TestCreateTerrainMetadata:
    """Tests for create_terrain_metadata factory."""

    def test_terrain_metadata(self):
        record = create_terrain_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            bbox=(46.7, 24.7, 46.8, 24.8),
            dem_source="SRTM",
            resolution_m=30.0,
            elevation_min_m=500.0,
            elevation_max_m=750.0,
        )
        assert record.domain == "terrain"
        assert record.resource_type == "dem_analysis"
        assert len(record.metadata.reference_system_info) == 2  # WGS84 + UTM
        extent = record.metadata.identification_info.extent[0]
        assert extent.vertical_min_m == 500.0
        assert extent.vertical_max_m == 750.0


class TestCreateSatelliteMetadata:
    """Tests for create_satellite_metadata factory."""

    def test_satellite_metadata(self):
        record = create_satellite_metadata(
            scene_id="S2A_MSIL2A_20250615",
            tenant_id="tenant-001",
            bbox=(46.0, 24.0, 47.0, 25.0),
            acquisition_date=datetime(2025, 6, 15, tzinfo=UTC),
            cloud_coverage_pct=3.0,
        )
        assert record.domain == "satellite"
        assert record.resource_type == "satellite_image"
        assert record.resource_id == "S2A_MSIL2A_20250615"


class TestCreateIoTSensorMetadata:
    """Tests for create_iot_sensor_metadata factory."""

    def test_sensor_metadata(self):
        record = create_iot_sensor_metadata(
            device_id="DEV-001",
            sensor_id="SENSOR-001",
            tenant_id="tenant-001",
            location=(46.75, 24.75),
            sensor_type="soil_moisture",
            accuracy_pct=95.0,
        )
        assert record.domain == "iot"
        assert record.resource_type == "sensor_data"
        assert "iot" in record.tags
        quality = record.metadata.data_quality_info
        assert quality is not None
        assert any(e.quality_type == "thematicAccuracy" for e in quality.report)


# =============================================================================
# GeospatialMetadataRecord
# =============================================================================


class TestGeospatialMetadataRecord:
    """Tests for the SAHOOL convenience wrapper."""

    def test_to_geojson_metadata(self):
        record = create_field_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            title="Test Field",
            abstract="Test abstract",
            bbox=(46.7, 24.7, 46.8, 24.8),
        )
        geojson_meta = record.to_geojson_metadata()
        assert geojson_meta["metadata_standard"] == "ISO 19115-1:2014"
        assert geojson_meta["domain"] == "field"
        assert geojson_meta["resource_id"] == "FIELD-001"
        assert geojson_meta["crs"] == "EPSG:4326"


# =============================================================================
# Extended Edge-Case & Validation Tests
# =============================================================================


class TestBoundaryValidation:
    """Edge-case validation tests for geographic extents."""

    def test_extreme_west_coordinate(self):
        """Test valid extreme western coordinate (dateline)."""
        bbox = EX_GeographicBoundingBox(
            west_bound_longitude=-180.0,
            east_bound_longitude=180.0,
            south_bound_latitude=-90.0,
            north_bound_latitude=90.0,
        )
        assert bbox.west_bound_longitude == -180.0
        assert bbox.north_bound_latitude == 90.0

    def test_zero_crossing_meridian(self):
        """Test bbox crossing the prime meridian."""
        bbox = EX_GeographicBoundingBox(
            west_bound_longitude=-5.0,
            east_bound_longitude=5.0,
            south_bound_latitude=48.0,
            north_bound_latitude=52.0,
        )
        assert bbox.west_bound_longitude == -5.0
        assert bbox.east_bound_longitude == 5.0

    def test_point_extent(self):
        """Test bbox collapsed to a single point."""
        bbox = EX_GeographicBoundingBox(
            west_bound_longitude=46.75,
            east_bound_longitude=46.75,
            south_bound_latitude=24.75,
            north_bound_latitude=24.75,
        )
        assert bbox.west_bound_longitude == bbox.east_bound_longitude

    def test_invalid_latitude_too_high(self):
        with pytest.raises(ValueError):
            EX_GeographicBoundingBox(
                west_bound_longitude=0,
                east_bound_longitude=10,
                south_bound_latitude=0,
                north_bound_latitude=91,
            )

    def test_invalid_latitude_too_low(self):
        with pytest.raises(ValueError):
            EX_GeographicBoundingBox(
                west_bound_longitude=0,
                east_bound_longitude=10,
                south_bound_latitude=-91,
                north_bound_latitude=0,
            )

    def test_arabian_peninsula_bbox(self):
        """Test typical SAHOOL deployment region."""
        bbox = EX_GeographicBoundingBox(
            west_bound_longitude=34.5,
            east_bound_longitude=59.5,
            south_bound_latitude=12.0,
            north_bound_latitude=32.0,
        )
        assert bbox.west_bound_longitude == 34.5
        assert bbox.north_bound_latitude == 32.0

    def test_yemen_bbox(self):
        """Test Yemen-specific region (SAHOOL deployment target)."""
        bbox = EX_GeographicBoundingBox(
            west_bound_longitude=42.5,
            east_bound_longitude=54.0,
            south_bound_latitude=12.5,
            north_bound_latitude=19.0,
        )
        assert bbox.south_bound_latitude == 12.5


class TestTemporalEdgeCases:
    """Edge-case tests for temporal extents."""

    def test_same_start_end(self):
        """Test instantaneous temporal extent (single observation)."""
        t = datetime(2025, 6, 15, 12, 0, 0, tzinfo=UTC)
        te = EX_TemporalExtent(begin_position=t, end_position=t)
        assert te.begin_position == te.end_position

    def test_multi_year_extent(self):
        """Test multi-year crop rotation extent."""
        te = EX_TemporalExtent(
            begin_position=datetime(2023, 1, 1, tzinfo=UTC),
            end_position=datetime(2026, 12, 31, tzinfo=UTC),
        )
        duration = te.end_position - te.begin_position
        assert duration.days > 1400


class TestDataQualityEdgeCases:
    """Edge-case tests for data quality reports."""

    def test_multiple_quality_elements(self):
        report = DataQualityReport()
        report.add_positional_accuracy(2.5, method="RTK GPS")
        report.add_completeness(98.0)
        report.add_thematic_accuracy(92.0)
        report.add_temporal_accuracy(0.5)
        report.add_conformance("ISO 19115-1:2014", is_conformant=True)
        assert len(report.report) == 5

    def test_perfect_accuracy(self):
        report = DataQualityReport()
        report.add_positional_accuracy(0.01, method="Survey-grade RTK")
        assert report.report[0].quantitative_result.value == 0.01

    def test_zero_completeness(self):
        report = DataQualityReport()
        report.add_completeness(0.0, name="Cloud-covered area")
        assert report.report[0].quantitative_result.value == 0.0

    def test_conformance_failure(self):
        report = DataQualityReport()
        report.add_conformance(
            "ISO 19131:2022",
            is_conformant=False,
            explanation="Data product specification not yet defined",
        )
        assert report.report[0].conformance_result.is_conformant is False

    def test_custom_scope(self):
        report = DataQualityReport(scope=DQ_Scope(level=MD_ScopeCode.FEATURE))
        assert report.scope.level == MD_ScopeCode.FEATURE


class TestLineageEdgeCases:
    """Edge-case tests for lineage tracking."""

    def test_multi_step_pipeline(self):
        """Test complex multi-step processing pipeline."""
        lineage = LI_Lineage(
            statement="Multi-step NDVI pipeline",
        )
        lineage.add_step(
            description="Download Sentinel-2 L1C from CDSE",
            software="sentinelhub-py 3.10",
        )
        lineage.add_step(
            description="Atmospheric correction to L2A",
            software="Sen2Cor 2.11",
            algorithm="Scene Classification + Atmospheric Correction",
        )
        lineage.add_step(
            description="NDVI calculation (B8-B4)/(B8+B4)",
            software="rasterio 1.3",
            algorithm="NDVI",
            parameters={"nir_band": "B8", "red_band": "B4"},
        )
        lineage.add_step(
            description="Zonal statistics per field polygon",
            software="PostGIS 3.4",
            algorithm="ST_SummaryStatsAgg",
        )
        assert len(lineage.process_step) == 4
        assert lineage.process_step[2].parameters == {"nir_band": "B8", "red_band": "B4"}

    def test_multi_source_lineage(self):
        """Test lineage with multiple data sources."""
        lineage = LI_Lineage(
            statement="Fusion of satellite and IoT data",
            source=[
                LI_Source(
                    description="Sentinel-2 NDVI raster",
                    source_spatial_resolution=MD_Resolution(distance_m=10.0),
                ),
                LI_Source(
                    description="IoT soil moisture sensors",
                    source_spatial_resolution=MD_Resolution(distance_m=0.0),
                ),
                LI_Source(
                    description="Weather station observations",
                ),
            ],
        )
        assert len(lineage.source) == 3

    def test_lineage_process_step_with_processor(self):
        """Test process step with identified processor."""
        step = LI_ProcessStep(
            description="Field boundary digitization",
            processor=CI_ResponsibleParty(
                individual_name="Ahmad Farmer",
                role=CI_RoleCode.ORIGINATOR,
            ),
            software_reference="SAHOOL Field App v16.0.0",
        )
        assert step.processor.individual_name == "Ahmad Farmer"
        assert step.processor.role == CI_RoleCode.ORIGINATOR


class TestMDMetadataEdgeCases:
    """Edge-case tests for the root MD_Metadata entity."""

    def test_full_metadata_record(self):
        """Test creating a complete metadata record with all optional fields."""
        from shared.geospatial_metadata.iso19115 import (
            MD_Distribution,
            MD_DistributionFormat,
            MD_DigitalTransferOptions,
            CI_OnlineResource,
            MD_BrowseGraphic,
            MD_AggregateInformation,
        )

        md = MD_Metadata(
            hierarchy_level=MD_ScopeCode.DATASET,
            identification_info=MD_DataIdentification(
                citation=CI_Citation(
                    title="Full Test",
                    title_ar="اختبار كامل",
                    edition="v2.0",
                    presentation_form="mapDigital",
                ),
                abstract="Complete metadata test with all optional fields",
                abstract_ar="اختبار كامل للبيانات الوصفية",
                purpose="Testing completeness of ISO 19115 implementation",
                purpose_ar="اختبار اكتمال تنفيذ ISO 19115",
                topic_category=[
                    MD_TopicCategory.FARMING,
                    MD_TopicCategory.ENVIRONMENT,
                    MD_TopicCategory.INLAND_WATERS,
                ],
                descriptive_keywords=[
                    MD_Keywords(
                        keyword=["irrigation", "wheat", "NDVI"],
                        keyword_ar=["ري", "قمح", "NDVI"],
                        type="theme",
                        thesaurus_name="SAHOOL Agricultural Vocabulary",
                    ),
                    MD_Keywords(
                        keyword=["Saudi Arabia", "Riyadh"],
                        keyword_ar=["السعودية", "الرياض"],
                        type="place",
                    ),
                ],
                spatial_representation_type=[
                    MD_SpatialRepresentationType.VECTOR,
                    MD_SpatialRepresentationType.GRID,
                ],
                spatial_resolution=[
                    MD_Resolution(distance_m=10.0, level_of_detail="10m Sentinel-2"),
                    MD_Resolution(equivalent_scale=50000),
                ],
                extent=[
                    EX_Extent(
                        description="Saudi Arabia - Central Region",
                        description_ar="السعودية - المنطقة الوسطى",
                        geographic_element=EX_GeographicBoundingBox(
                            west_bound_longitude=46.0,
                            east_bound_longitude=47.0,
                            south_bound_latitude=24.0,
                            north_bound_latitude=25.0,
                        ),
                        temporal_element=EX_TemporalExtent(
                            begin_position=datetime(2025, 1, 1, tzinfo=UTC),
                            end_position=datetime(2025, 12, 31, tzinfo=UTC),
                        ),
                        vertical_min_m=400.0,
                        vertical_max_m=800.0,
                    ),
                ],
                resource_constraints=[MD_LegalConstraints()],
                graphic_overview=[
                    MD_BrowseGraphic(
                        file_name="/thumbnails/field-001.png",
                        file_description="Field boundary preview",
                        file_type="image/png",
                    ),
                ],
                aggregation_info=[
                    MD_AggregateInformation(
                        aggregate_dataset_name="SAHOOL Field Collection 2025",
                        association_type="largerWorkCitation",
                    ),
                ],
                tenant_id="tenant-001",
                domain="field",
            ),
            reference_system_info=[
                MD_ReferenceSystem.wgs84(),
                MD_ReferenceSystem.utm_zone_38n(),
            ],
            distribution_info=MD_Distribution(
                distribution_format=[
                    MD_DistributionFormat(name="GeoJSON", version="RFC 7946"),
                    MD_DistributionFormat(name="GeoPackage", version="1.3"),
                ],
                transfer_options=[
                    MD_DigitalTransferOptions(
                        transfer_size_mb=2.5,
                        online_resource=[
                            CI_OnlineResource(
                                linkage="https://api.sahool.app/v1/fields/FIELD-001",
                                protocol="HTTPS",
                                name="SAHOOL API",
                            ),
                        ],
                    ),
                ],
            ),
            data_quality_info=DataQualityReport(),
            lineage=LI_Lineage(statement="Full test lineage"),
        )

        assert len(md.identification_info.topic_category) == 3
        assert len(md.reference_system_info) == 2
        assert md.distribution_info is not None
        assert len(md.distribution_info.distribution_format) == 2
        assert md.identification_info.graphic_overview[0].file_type == "image/png"
        assert md.identification_info.aggregation_info[0].association_type == "largerWorkCitation"

        # Test ISO dict export
        iso_dict = md.to_iso_dict()
        assert iso_dict["MD_Metadata"]["metadataStandardVersion"] == "2014"
        assert len(iso_dict["MD_Metadata"]["referenceSystemInfo"]) == 2

    def test_metadata_unique_identifiers(self):
        """Test that each metadata record gets a unique identifier."""
        md1 = MD_Metadata(
            identification_info=MD_DataIdentification(
                citation=CI_Citation(title="Record 1"),
                abstract="First record",
            ),
        )
        md2 = MD_Metadata(
            identification_info=MD_DataIdentification(
                citation=CI_Citation(title="Record 2"),
                abstract="Second record",
            ),
        )
        assert md1.metadata_identifier != md2.metadata_identifier

    def test_metadata_with_feature_scope(self):
        """Test metadata with feature-level hierarchy."""
        md = MD_Metadata(
            hierarchy_level=MD_ScopeCode.FEATURE,
            identification_info=MD_DataIdentification(
                citation=CI_Citation(title="Single Feature"),
                abstract="Feature-level metadata",
            ),
        )
        assert md.hierarchy_level == MD_ScopeCode.FEATURE


class TestFactoryBilingual:
    """Tests for bilingual (Arabic/English) content in factory output."""

    def test_field_metadata_arabic_content(self):
        record = create_field_metadata(
            field_id="FIELD-AR",
            tenant_id="tenant-ar",
            title="حقل القمح الشمالي",
            title_ar="حقل القمح الشمالي",
            abstract="حدود حقل القمح",
            abstract_ar="حدود حقل القمح الشمالي بمساحة 8.5 هكتار",
            bbox=(46.7, 24.7, 46.8, 24.8),
            area_hectares=8.5,
        )
        assert record.metadata.identification_info.citation.title_ar == "حقل القمح الشمالي"
        assert record.metadata.identification_info.abstract_ar is not None
        assert "هكتار" in record.metadata.identification_info.abstract_ar

    def test_ndvi_metadata_arabic_lineage(self):
        record = create_ndvi_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            bbox=(46.7, 24.7, 46.8, 24.8),
            acquisition_date=datetime(2025, 6, 15, tzinfo=UTC),
        )
        assert record.metadata.lineage is not None
        assert record.metadata.lineage.statement_ar is not None
        assert "NDVI" in record.metadata.lineage.statement_ar

    def test_terrain_metadata_arabic_keywords(self):
        record = create_terrain_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            bbox=(46.7, 24.7, 46.8, 24.8),
        )
        keywords = record.metadata.identification_info.descriptive_keywords
        assert len(keywords) > 0
        arabic_kw = keywords[0].keyword_ar
        assert len(arabic_kw) > 0
        assert any("تضاريس" in kw for kw in arabic_kw)

    def test_iot_sensor_arabic_type(self):
        record = create_iot_sensor_metadata(
            device_id="DEV-001",
            sensor_id="SENSOR-001",
            tenant_id="tenant-001",
            location=(46.75, 24.75),
            sensor_type="soil_moisture",
        )
        title_ar = record.metadata.identification_info.citation.title_ar
        assert "رطوبة التربة" in title_ar


class TestFactoryWithCustomCRS:
    """Tests for factory functions with non-default CRS."""

    def test_field_with_utm38n(self):
        record = create_field_metadata(
            field_id="FIELD-UTM",
            tenant_id="tenant-001",
            title="UTM Field",
            abstract="Field with UTM CRS",
            bbox=(46.7, 24.7, 46.8, 24.8),
            crs="EPSG:32638",
        )
        assert record.metadata.reference_system_info[0].code == "EPSG:32638"

    def test_terrain_has_dual_crs(self):
        """Terrain analysis should include both WGS84 and UTM."""
        record = create_terrain_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            bbox=(46.7, 24.7, 46.8, 24.8),
        )
        crs_codes = [rs.code for rs in record.metadata.reference_system_info]
        assert "EPSG:4326" in crs_codes
        assert "EPSG:32638" in crs_codes


class TestModelSerialization:
    """Test model serialization/deserialization roundtrips."""

    def test_field_metadata_json_roundtrip(self):
        record = create_field_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            title="Roundtrip Test",
            abstract="Testing JSON serialization",
            bbox=(46.7, 24.7, 46.8, 24.8),
        )
        json_str = record.model_dump_json()
        restored = GeospatialMetadataRecord.model_validate_json(json_str)
        assert restored.resource_id == record.resource_id
        assert restored.domain == record.domain
        assert restored.metadata.identification_info.citation.title == "Roundtrip Test"

    def test_metadata_dict_roundtrip(self):
        record = create_ndvi_metadata(
            field_id="FIELD-002",
            tenant_id="tenant-002",
            bbox=(46.7, 24.7, 46.8, 24.8),
            acquisition_date=datetime(2025, 6, 15, tzinfo=UTC),
            mean_ndvi=0.65,
        )
        data = record.model_dump()
        restored = GeospatialMetadataRecord.model_validate(data)
        assert restored.resource_type == "ndvi_reading"
        assert restored.metadata.lineage.statement is not None

    def test_iso_dict_structure(self):
        """Verify ISO dict output has expected structure for external tools."""
        record = create_field_metadata(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            title="Structure Test",
            abstract="Testing ISO dict structure",
            bbox=(46.7, 24.7, 46.8, 24.8),
        )
        iso_dict = record.metadata.to_iso_dict()
        root = iso_dict["MD_Metadata"]

        # Check mandatory elements
        assert "fileIdentifier" in root
        assert "language" in root
        assert "characterSet" in root
        assert "hierarchyLevel" in root
        assert "contact" in root
        assert "dateStamp" in root
        assert "metadataStandardName" in root
        assert "identificationInfo" in root
        assert "referenceSystemInfo" in root

        # Check nested structure
        ident = root["identificationInfo"]["MD_DataIdentification"]
        assert "citation" in ident
        assert "abstract" in ident
        assert "topicCategory" in ident
        assert "farming" in ident["topicCategory"]

    def test_geojson_metadata_export(self):
        """Test GeoJSON metadata export for map integration."""
        record = create_satellite_metadata(
            scene_id="S2A_TEST",
            tenant_id="tenant-001",
            bbox=(46.0, 24.0, 47.0, 25.0),
            acquisition_date=datetime(2025, 6, 15, tzinfo=UTC),
        )
        meta = record.to_geojson_metadata()
        assert "metadata_id" in meta
        assert "metadata_standard" in meta
        assert meta["resource_type"] == "satellite_image"
        assert "created_at" in meta


class TestEnumCoverage:
    """Test that all enum values are valid and accessible."""

    def test_scope_codes(self):
        assert MD_ScopeCode.DATASET == "dataset"
        assert MD_ScopeCode.FEATURE == "feature"
        assert MD_ScopeCode.SERIES == "series"

    def test_topic_categories(self):
        assert MD_TopicCategory.FARMING == "farming"
        assert MD_TopicCategory.ELEVATION == "elevation"
        assert MD_TopicCategory.IMAGERY_BASE_MAPS == "imageryBaseMapsEarthCover"
        assert MD_TopicCategory.CLIMATOLOGY_METEOROLOGY == "climatologyMeteorologyAtmosphere"

    def test_spatial_representation_types(self):
        assert MD_SpatialRepresentationType.VECTOR == "vector"
        assert MD_SpatialRepresentationType.GRID == "grid"
        assert MD_SpatialRepresentationType.TIN == "tin"

    def test_role_codes(self):
        assert CI_RoleCode.OWNER == "owner"
        assert CI_RoleCode.AUTHOR == "author"
        assert CI_RoleCode.PROCESSOR == "processor"

    def test_restriction_codes(self):
        from shared.geospatial_metadata.iso19115 import MD_RestrictionCode

        assert MD_RestrictionCode.RESTRICTED == "restricted"
        assert MD_RestrictionCode.COPYRIGHT == "copyright"

    def test_maintenance_frequency(self):
        from shared.geospatial_metadata.iso19115 import MD_MaintenanceFrequencyCode

        assert MD_MaintenanceFrequencyCode.DAILY == "daily"
        assert MD_MaintenanceFrequencyCode.CONTINUAL == "continual"
        assert MD_MaintenanceFrequencyCode.AS_NEEDED == "asNeeded"

    def test_progress_codes(self):
        from shared.geospatial_metadata.iso19115 import MD_ProgressCode

        assert MD_ProgressCode.ON_GOING == "onGoing"
        assert MD_ProgressCode.COMPLETED == "completed"


# =============================================================================
# Bbox Validation Tests
# =============================================================================


class TestBboxValidation:
    """Tests for _validate_bbox function and factory bbox validation."""

    def test_valid_bbox_passes(self):
        """Valid bbox should not raise."""
        from shared.geospatial_metadata.factory import _validate_bbox

        result = _validate_bbox((46.7, 24.7, 46.8, 24.8))
        assert result == (46.7, 24.7, 46.8, 24.8)

    def test_bbox_west_out_of_range(self):
        from shared.geospatial_metadata.factory import _validate_bbox

        with pytest.raises(ValueError, match="west_longitude.*out of range"):
            _validate_bbox((-200, 24.7, 46.8, 24.8))

    def test_bbox_east_out_of_range(self):
        from shared.geospatial_metadata.factory import _validate_bbox

        with pytest.raises(ValueError, match="east_longitude.*out of range"):
            _validate_bbox((46.7, 24.7, 200, 24.8))

    def test_bbox_south_out_of_range(self):
        from shared.geospatial_metadata.factory import _validate_bbox

        with pytest.raises(ValueError, match="south_latitude.*out of range"):
            _validate_bbox((46.7, -100, 46.8, 24.8))

    def test_bbox_north_out_of_range(self):
        from shared.geospatial_metadata.factory import _validate_bbox

        with pytest.raises(ValueError, match="north_latitude.*out of range"):
            _validate_bbox((46.7, 24.7, 46.8, 100))

    def test_bbox_east_lt_west_rejected(self):
        from shared.geospatial_metadata.factory import _validate_bbox

        with pytest.raises(ValueError, match="east_longitude.*must be >= west"):
            _validate_bbox((46.8, 24.7, 46.7, 24.8))

    def test_bbox_north_lt_south_rejected(self):
        from shared.geospatial_metadata.factory import _validate_bbox

        with pytest.raises(ValueError, match="north_latitude.*must be >= south"):
            _validate_bbox((46.7, 24.8, 46.8, 24.7))

    def test_factory_rejects_invalid_bbox(self):
        """Factory functions should reject invalid bbox coordinates."""
        with pytest.raises(ValueError, match="east_longitude.*must be >= west"):
            create_field_metadata(
                field_id="F-BAD",
                tenant_id="00000000-0000-0000-0000-000000000001",
                title="Bad bbox",
                abstract="Inverted coordinates",
                bbox=(47.0, 24.0, 46.0, 25.0),  # west > east
            )

    def test_factory_rejects_latlon_swap(self):
        """Detect when latitude values > 90 are passed as latitude."""
        from shared.geospatial_metadata.factory import _validate_bbox

        # If someone passes latitude > 90, it should fail
        with pytest.raises(ValueError, match="south_latitude.*out of range"):
            _validate_bbox((46.0, 91.0, 47.0, 92.0))  # lat=91 is invalid
