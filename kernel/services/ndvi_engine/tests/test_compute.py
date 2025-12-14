"""
Tests for NDVI Compute Module
"""

import pytest
from datetime import date

from src.compute import (
    compute_ndvi_mock,
    compute_vegetation_indices,
    detect_ndvi_anomaly,
    NdviResult,
)


class TestComputeNdviMock:
    """Tests for mock NDVI computation"""

    def test_compute_ndvi_returns_result(self):
        """Test that compute_ndvi_mock returns a valid result"""
        result = compute_ndvi_mock("field-123")

        assert isinstance(result, NdviResult)
        assert result.field_id == "field-123"
        assert -1 <= result.ndvi_mean <= 1
        assert -1 <= result.ndvi_min <= 1
        assert -1 <= result.ndvi_max <= 1
        assert result.ndvi_min <= result.ndvi_mean <= result.ndvi_max
        assert result.data_source == "mock"

    def test_compute_ndvi_with_custom_date(self):
        """Test compute with custom scene date"""
        custom_date = date(2024, 6, 15)
        result = compute_ndvi_mock("field-456", scene_date=custom_date)

        assert result.scene_date == "2024-06-15"
        assert result.field_id == "field-456"

    def test_compute_ndvi_quality_range(self):
        """Test quality score is in valid range"""
        result = compute_ndvi_mock("field-789")

        assert 0 <= result.quality_score <= 1
        assert 0 <= result.cloud_cover_pct <= 100


class TestVegetationIndices:
    """Tests for vegetation indices calculation"""

    def test_compute_all_indices(self):
        """Test computation of all vegetation indices"""
        # Typical healthy vegetation values
        nir = 0.8
        red = 0.1
        green = 0.2
        blue = 0.1
        swir = 0.3

        indices = compute_vegetation_indices(nir, red, green, blue, swir)

        assert "ndvi" in indices
        assert "ndwi" in indices
        assert "evi" in indices
        assert "savi" in indices
        assert "gndvi" in indices

    def test_ndvi_calculation(self):
        """Test NDVI calculation formula"""
        # NIR = 0.8, Red = 0.2 -> NDVI = (0.8-0.2)/(0.8+0.2) = 0.6
        indices = compute_vegetation_indices(0.8, 0.2, 0.3, 0.1, 0.4)

        assert indices["ndvi"] == pytest.approx(0.6, rel=0.01)

    def test_ndvi_range(self):
        """Test NDVI values are in valid range"""
        indices = compute_vegetation_indices(0.9, 0.1, 0.2, 0.1, 0.3)

        assert -1 <= indices["ndvi"] <= 1
        assert -1 <= indices["ndwi"] <= 1


class TestAnomalyDetection:
    """Tests for NDVI anomaly detection"""

    def test_no_anomaly_normal_data(self):
        """Test no anomaly detected for normal NDVI pattern"""
        history = [0.65, 0.67, 0.66, 0.68, 0.65, 0.66, 0.67]
        current = 0.66

        anomaly = detect_ndvi_anomaly("field-123", current, history)

        assert anomaly is None

    def test_anomaly_sudden_drop(self):
        """Test anomaly detected for sudden NDVI drop"""
        history = [0.65, 0.67, 0.66, 0.68, 0.65, 0.66, 0.67]
        current = 0.35  # Significant drop

        anomaly = detect_ndvi_anomaly("field-123", current, history)

        assert anomaly is not None
        assert anomaly["anomaly_type"] == "sudden_drop"
        assert anomaly["severity"] in ["medium", "high"]

    def test_anomaly_empty_history(self):
        """Test no anomaly with empty history"""
        anomaly = detect_ndvi_anomaly("field-123", 0.5, [])

        assert anomaly is None

    def test_anomaly_short_history(self):
        """Test no anomaly with insufficient history"""
        history = [0.65, 0.67]
        anomaly = detect_ndvi_anomaly("field-123", 0.35, history)

        assert anomaly is None
