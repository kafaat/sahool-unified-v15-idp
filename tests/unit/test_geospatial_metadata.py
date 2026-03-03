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
    DQ_Element,
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
        assert any(
            e.quality_type == "thematicAccuracy"
            for e in quality.report
        )


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
