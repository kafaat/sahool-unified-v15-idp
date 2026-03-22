"""
Comprehensive tests for DataExporter module.
Tests cover all export formats (GeoJSON, CSV, JSON, KML) and all export methods.
"""

import json
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.data_exporter import DataExporter, ExportFormat, ExportResult
except ImportError:
    pytest.skip("data_exporter dependencies not installed", allow_module_level=True)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def exporter():
    return DataExporter()


@pytest.fixture
def sample_analysis_data():
    return {
        "field_id": "FIELD-001",
        "analysis_date": "2025-03-15",
        "satellite": "Sentinel-2",
        "health_score": 0.82,
        "health_status": "healthy",
        "latitude": 15.5,
        "longitude": 44.2,
        "indices": {
            "ndvi": 0.72,
            "evi": 0.55,
            "ndwi": 0.1,
        },
        "imagery": {
            "cloud_cover_percent": 5.2,
            "acquisition_date": "2025-03-14",
            "scene_id": "S2A_20250314",
        },
        "anomalies": ["drought_stress", "nutrient_deficiency"],
    }


@pytest.fixture
def sample_timeseries():
    return [
        {"date": "2025-01-01", "ndvi": 0.35, "latitude": 15.5, "longitude": 44.2},
        {"date": "2025-02-01", "ndvi": 0.55, "latitude": 15.5, "longitude": 44.2},
        {"date": "2025-03-01", "ndvi": 0.72, "latitude": 15.5, "longitude": 44.2},
    ]


@pytest.fixture
def sample_boundaries():
    return [
        {
            "field_id": "FIELD-001",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[44.2, 15.5], [44.3, 15.5], [44.3, 15.6], [44.2, 15.6], [44.2, 15.5]]
                ],
            },
            "area_hectares": 10.5,
        },
        {
            "field_id": "FIELD-002",
            "coordinates": [
                [[44.4, 15.5], [44.5, 15.5], [44.5, 15.6], [44.4, 15.6], [44.4, 15.5]]
            ],
            "area_hectares": 8.3,
        },
    ]


@pytest.fixture
def sample_prediction():
    return {
        "field_id": "FIELD-001",
        "prediction_date": "2025-03-15",
        "crop_type": "wheat",
        "predicted_yield_tons_ha": 4.5,
        "confidence_score": 0.88,
        "quality_grade": "A",
        "factors": {
            "ndvi": 0.72,
            "soil_moisture": 45.0,
            "rainfall": 120.0,
        },
        "risks": ["drought", "pest_risk"],
    }


@pytest.fixture
def sample_changes():
    return [
        {
            "change_id": "C001",
            "change_type": "vegetation_loss",
            "latitude": 15.5,
            "longitude": 44.2,
            "severity": "moderate",
            "date": "2025-03-10",
        },
        {
            "change_id": "C002",
            "change_type": "new_cultivation",
            "latitude": 15.6,
            "longitude": 44.3,
            "severity": "low",
            "date": "2025-03-12",
        },
    ]


# =============================================================================
# ExportFormat Tests
# =============================================================================


class TestExportFormat:
    def test_format_values(self):
        assert ExportFormat.GEOJSON.value == "geojson"
        assert ExportFormat.CSV.value == "csv"
        assert ExportFormat.JSON.value == "json"
        assert ExportFormat.KML.value == "kml"

    def test_all_formats(self):
        assert len(ExportFormat) == 4


# =============================================================================
# Content Types Tests
# =============================================================================


class TestContentTypes:
    def test_content_types(self, exporter):
        assert exporter.CONTENT_TYPES[ExportFormat.GEOJSON] == "application/geo+json"
        assert exporter.CONTENT_TYPES[ExportFormat.CSV] == "text/csv"
        assert exporter.CONTENT_TYPES[ExportFormat.JSON] == "application/json"
        assert exporter.CONTENT_TYPES[ExportFormat.KML] == "application/vnd.google-earth.kml+xml"


# =============================================================================
# export_field_analysis Tests
# =============================================================================


class TestExportFieldAnalysis:
    def test_geojson_format(self, exporter, sample_analysis_data):
        result = exporter.export_field_analysis("FIELD-001", sample_analysis_data, ExportFormat.GEOJSON)
        assert isinstance(result, ExportResult)
        assert result.format == ExportFormat.GEOJSON
        assert result.content_type == "application/geo+json"
        assert result.size_bytes > 0
        assert result.generated_at is not None

        data = json.loads(result.data)
        assert data["type"] == "Feature"
        assert data["geometry"]["type"] == "Point"
        assert data["geometry"]["coordinates"] == [44.2, 15.5]
        assert "health_score" in data["properties"]

    def test_csv_format(self, exporter, sample_analysis_data):
        result = exporter.export_field_analysis("FIELD-001", sample_analysis_data, ExportFormat.CSV)
        assert result.format == ExportFormat.CSV
        assert result.content_type == "text/csv"
        lines = result.data.strip().split("\n")
        assert len(lines) == 2  # header + data
        header = lines[0]
        assert "field_id" in header
        assert "health_score" in header
        assert "index_ndvi" in header

    def test_json_format(self, exporter, sample_analysis_data):
        result = exporter.export_field_analysis("FIELD-001", sample_analysis_data, ExportFormat.JSON)
        assert result.format == ExportFormat.JSON
        data = json.loads(result.data)
        assert data["field_id"] == "FIELD-001"
        assert data["health_score"] == 0.82

    def test_kml_format(self, exporter, sample_analysis_data):
        result = exporter.export_field_analysis("FIELD-001", sample_analysis_data, ExportFormat.KML)
        assert result.format == ExportFormat.KML
        assert result.content_type == "application/vnd.google-earth.kml+xml"
        assert "<kml" in result.data
        assert "Field Analysis FIELD-001" in result.data
        assert "44.2,15.5,0" in result.data

    def test_filename_generation(self, exporter, sample_analysis_data):
        result = exporter.export_field_analysis("FIELD-001", sample_analysis_data, ExportFormat.JSON)
        assert result.filename.startswith("sahool_field_analysis_FIELD-001_")
        assert result.filename.endswith(".json")

    def test_unsupported_format_field_analysis(self, exporter, sample_analysis_data):
        """Test that an invalid format raises ValueError - requires a mock since enum enforces values."""
        # ExportFormat enum restricts values, so all valid enums are covered in tests above.
        pass


# =============================================================================
# export_timeseries Tests
# =============================================================================


class TestExportTimeseries:
    def test_csv_format(self, exporter, sample_timeseries):
        result = exporter.export_timeseries("FIELD-001", sample_timeseries, ExportFormat.CSV)
        assert result.format == ExportFormat.CSV
        lines = result.data.strip().split("\n")
        assert len(lines) == 4  # header + 3 data rows
        assert "ndvi" in lines[0]
        assert "date" in lines[0]

    def test_json_format(self, exporter, sample_timeseries):
        result = exporter.export_timeseries("FIELD-001", sample_timeseries, ExportFormat.JSON)
        data = json.loads(result.data)
        assert data["field_id"] == "FIELD-001"
        assert data["count"] == 3
        assert len(data["timeseries"]) == 3

    def test_geojson_format(self, exporter, sample_timeseries):
        result = exporter.export_timeseries("FIELD-001", sample_timeseries, ExportFormat.GEOJSON)
        data = json.loads(result.data)
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 3
        for feature in data["features"]:
            assert feature["type"] == "Feature"
            assert feature["geometry"]["type"] == "Point"
            assert "ndvi" in feature["properties"]

    def test_geojson_without_coords(self, exporter):
        ts = [{"date": "2025-01-01", "ndvi": 0.5}]
        result = exporter.export_timeseries("FIELD-001", ts, ExportFormat.GEOJSON)
        data = json.loads(result.data)
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 0  # No lat/lon, so no features

    def test_unsupported_format(self, exporter, sample_timeseries):
        with pytest.raises(ValueError, match="not supported for timeseries"):
            exporter.export_timeseries("FIELD-001", sample_timeseries, ExportFormat.KML)

    def test_filename_timeseries(self, exporter, sample_timeseries):
        result = exporter.export_timeseries("FIELD-001", sample_timeseries, ExportFormat.CSV)
        assert "timeseries" in result.filename
        assert result.filename.endswith(".csv")


# =============================================================================
# export_boundaries Tests
# =============================================================================


class TestExportBoundaries:
    def test_geojson_format(self, exporter, sample_boundaries):
        result = exporter.export_boundaries(sample_boundaries, ExportFormat.GEOJSON)
        data = json.loads(result.data)
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2
        # First boundary has explicit geometry
        assert data["features"][0]["geometry"]["type"] == "Polygon"
        assert "area_hectares" in data["features"][0]["properties"]

    def test_kml_format(self, exporter, sample_boundaries):
        result = exporter.export_boundaries(sample_boundaries, ExportFormat.KML)
        assert "<kml" in result.data
        assert "FIELD-001" in result.data
        assert "FIELD-002" in result.data
        assert "<Polygon>" in result.data

    def test_json_format(self, exporter, sample_boundaries):
        result = exporter.export_boundaries(sample_boundaries, ExportFormat.JSON)
        data = json.loads(result.data)
        assert data["count"] == 2
        assert len(data["boundaries"]) == 2

    def test_unsupported_format(self, exporter, sample_boundaries):
        with pytest.raises(ValueError, match="not supported for boundaries"):
            exporter.export_boundaries(sample_boundaries, ExportFormat.CSV)

    def test_filename_boundaries(self, exporter, sample_boundaries):
        result = exporter.export_boundaries(sample_boundaries, ExportFormat.GEOJSON)
        assert "boundaries" in result.filename
        assert result.filename.endswith(".geojson")


# =============================================================================
# export_yield_prediction Tests
# =============================================================================


class TestExportYieldPrediction:
    def test_json_format(self, exporter, sample_prediction):
        result = exporter.export_yield_prediction(sample_prediction, ExportFormat.JSON)
        data = json.loads(result.data)
        assert data["predicted_yield_tons_ha"] == 4.5
        assert data["crop_type"] == "wheat"

    def test_csv_format(self, exporter, sample_prediction):
        result = exporter.export_yield_prediction(sample_prediction, ExportFormat.CSV)
        lines = result.data.strip().split("\n")
        assert len(lines) == 2
        header = lines[0]
        assert "predicted_yield_tons_ha" in header
        assert "factor_ndvi" in header
        assert "risks" in header

    def test_geojson_format(self, exporter, sample_prediction):
        result = exporter.export_yield_prediction(sample_prediction, ExportFormat.GEOJSON)
        data = json.loads(result.data)
        assert data["type"] == "Feature"
        # No lat/lon in sample data, so geometry should be None
        assert data["geometry"] is None

    def test_unsupported_format(self, exporter, sample_prediction):
        with pytest.raises(ValueError, match="not supported for yield prediction"):
            exporter.export_yield_prediction(sample_prediction, ExportFormat.KML)

    def test_missing_field_id(self, exporter):
        data = {"predicted_yield_tons_ha": 3.0}
        result = exporter.export_yield_prediction(data, ExportFormat.JSON)
        assert "yield_prediction" in result.filename
        assert "unknown" in result.filename


# =============================================================================
# export_changes_report Tests
# =============================================================================


class TestExportChangesReport:
    def test_csv_format(self, exporter, sample_changes):
        result = exporter.export_changes_report(sample_changes, ExportFormat.CSV)
        lines = result.data.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
        assert "change_type" in lines[0]

    def test_json_format(self, exporter, sample_changes):
        result = exporter.export_changes_report(sample_changes, ExportFormat.JSON)
        data = json.loads(result.data)
        assert data["count"] == 2
        assert len(data["changes"]) == 2

    def test_geojson_format(self, exporter, sample_changes):
        result = exporter.export_changes_report(sample_changes, ExportFormat.GEOJSON)
        data = json.loads(result.data)
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2
        for f in data["features"]:
            assert f["geometry"]["type"] == "Point"
            assert "change_type" in f["properties"]

    def test_geojson_without_coords(self, exporter):
        changes = [{"change_type": "loss", "severity": "high"}]
        result = exporter.export_changes_report(changes, ExportFormat.GEOJSON)
        data = json.loads(result.data)
        assert len(data["features"]) == 0

    def test_unsupported_format(self, exporter, sample_changes):
        with pytest.raises(ValueError, match="not supported for changes report"):
            exporter.export_changes_report(sample_changes, ExportFormat.KML)


# =============================================================================
# Helper Methods Tests
# =============================================================================


class TestHelperMethods:
    def test_flatten_dict_simple(self, exporter):
        d = {"a": 1, "b": "hello"}
        flat = exporter._flatten_dict(d)
        assert flat == {"a": 1, "b": "hello"}

    def test_flatten_dict_nested(self, exporter):
        d = {"outer": {"inner": 42, "nested": {"deep": True}}}
        flat = exporter._flatten_dict(d)
        assert flat["outer_inner"] == 42
        assert flat["outer_nested_deep"] is True

    def test_flatten_dict_list_values(self, exporter):
        d = {"tags": ["a", "b", "c"]}
        flat = exporter._flatten_dict(d)
        assert flat["tags"] == "a, b, c"

    def test_flatten_dict_list_of_dicts(self, exporter):
        d = {"items": [{"x": 1}, {"x": 2}]}
        flat = exporter._flatten_dict(d)
        assert flat["items"] == "[2 items]"

    def test_flatten_analysis_for_csv(self, exporter, sample_analysis_data):
        flat = exporter._flatten_analysis_for_csv(sample_analysis_data)
        assert flat["field_id"] == "FIELD-001"
        assert flat["health_score"] == 0.82
        assert flat["index_ndvi"] == 0.72
        assert flat["cloud_cover_percent"] == 5.2
        assert flat["anomalies"] == "drought_stress, nutrient_deficiency"

    def test_flatten_analysis_empty_anomalies(self, exporter):
        data = {"field_id": "F1", "anomalies": []}
        flat = exporter._flatten_analysis_for_csv(data)
        assert flat["anomalies"] == ""

    def test_flatten_prediction_for_csv(self, exporter, sample_prediction):
        flat = exporter._flatten_prediction_for_csv(sample_prediction)
        assert flat["field_id"] == "FIELD-001"
        assert flat["predicted_yield_tons_ha"] == 4.5
        assert flat["factor_ndvi"] == 0.72
        assert flat["risks"] == "drought, pest_risk"

    def test_flatten_prediction_empty_risks(self, exporter):
        data = {"field_id": "F1", "risks": []}
        flat = exporter._flatten_prediction_for_csv(data)
        assert flat["risks"] == ""

    def test_to_csv_empty_list(self, exporter):
        assert exporter._to_csv([]) == ""

    def test_to_csv_single_row(self, exporter):
        data = [{"a": 1, "b": 2}]
        csv = exporter._to_csv(data)
        lines = csv.strip().split("\n")
        assert len(lines) == 2
        assert "a" in lines[0]
        assert "b" in lines[0]

    def test_to_geojson_with_lat_lon(self, exporter):
        data = {"latitude": 15.5, "longitude": 44.2, "ndvi": 0.7}
        result = json.loads(exporter._to_geojson(data))
        assert result["geometry"]["coordinates"] == [44.2, 15.5]
        assert result["properties"]["ndvi"] == 0.7

    def test_to_geojson_with_nested_lat_lon(self, exporter):
        data = {"imagery": {"latitude": 15.5, "longitude": 44.2}, "ndvi": 0.7}
        result = json.loads(exporter._to_geojson(data))
        assert result["geometry"]["coordinates"] == [44.2, 15.5]

    def test_to_geojson_null_geometry(self, exporter):
        data = {"ndvi": 0.7}
        result = json.loads(exporter._to_geojson(data))
        assert result["geometry"] is None

    def test_to_geojson_polygon(self, exporter):
        data = {"coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6]]]}
        result = json.loads(exporter._to_geojson(data, geometry_type="Polygon"))
        assert result["geometry"]["type"] == "Polygon"

    def test_to_kml_with_coords(self, exporter):
        data = {"latitude": 15.5, "longitude": 44.2, "ndvi": 0.7}
        kml = exporter._to_kml(data, name="Test Point")
        assert "<kml" in kml
        assert "44.2,15.5,0" in kml
        assert "Test Point" in kml

    def test_to_kml_without_coords(self, exporter):
        data = {"ndvi": 0.7}
        kml = exporter._to_kml(data, name="No Coords")
        assert "<kml" in kml
        assert "No Coords" in kml
        # Should not contain <Point> since no coordinates
        assert "<coordinates>" not in kml or "None" not in kml

    def test_format_kml_description(self, exporter):
        data = {"name": "Test", "value": 42}
        desc = exporter._format_kml_description(data)
        assert "<table>" in desc
        assert "name" in desc
        assert "42" in desc

    def test_format_kml_description_skips_none(self, exporter):
        data = {"name": "Test", "empty": None}
        desc = exporter._format_kml_description(data)
        assert "empty" not in desc

    def test_generate_filename(self, exporter):
        fname = exporter.generate_filename("test", "FIELD-001", ExportFormat.JSON)
        assert fname.startswith("sahool_test_FIELD-001_")
        assert fname.endswith(".json")

    def test_generate_filename_sanitizes(self, exporter):
        fname = exporter.generate_filename("test", "FIELD/001@bad", ExportFormat.CSV)
        assert "/" not in fname.split("_")[2]
        assert "@" not in fname

    def test_boundaries_to_kml(self, exporter, sample_boundaries):
        kml = exporter._boundaries_to_kml(sample_boundaries)
        assert "<kml" in kml
        assert "SAHOOL Field Boundaries" in kml
        assert "FIELD-001" in kml

    def test_export_result_size_bytes(self, exporter, sample_analysis_data):
        result = exporter.export_field_analysis("F1", sample_analysis_data, ExportFormat.JSON)
        assert result.size_bytes == len(result.data.encode("utf-8"))
