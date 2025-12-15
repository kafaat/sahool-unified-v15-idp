"""
Tests for NDVI Compute Module
"""

from datetime import date

import pytest
from src.compute import (
    NdviResult,
    compute_mock,
    calculate_vegetation_indices,
    detect_anomalies,
)


class TestComputeNdviMock:
    """Tests for mock NDVI computation"""

    def test_compute_ndvi_returns_result(self):
        """Test that compute_mock returns a valid result"""
        result = compute_mock("field-123")

        assert isinstance(result, NdviResult)
        assert result.field_id == "field-123"
        assert -1 <= result.ndvi_mean <= 1
        assert -1 <= result.ndvi_min <= 1
        assert -1 <= result.ndvi_max <= 1
        assert result.ndvi_min <= result.ndvi_mean <= result.ndvi_max
        assert result.data_source == "mock"

    def test_compute_ndvi_with_historical(self):
        """Test compute with historical flag"""
        result = compute_mock("field-456", historical=True)

        assert result.field_id == "field-456"

    def test_compute_ndvi_quality_range(self):
        """Test quality score is in valid range"""
        result = compute_mock("field-789")

        assert 0 <= result.quality_score <= 1
        assert 0 <= result.cloud_cover_pct <= 100


class TestVegetationIndices:
    """Tests for vegetation indices calculation"""

    def test_compute_all_indices(self):
        """Test computation of all vegetation indices"""
        # Typical healthy vegetation values
        red = 0.1
        nir = 0.8
        green = 0.2
        blue = 0.1
        swir = 0.3

        indices = calculate_vegetation_indices(red, nir, blue, green, swir)

        assert "ndvi" in indices
        assert "ndwi" in indices
        assert "evi" in indices
        assert "savi" in indices

    def test_ndvi_calculation(self):
        """Test NDVI calculation formula"""
        # NIR = 0.8, Red = 0.2 -> NDVI = (0.8-0.2)/(0.8+0.2) = 0.6
        indices = calculate_vegetation_indices(0.2, 0.8, 0.1, 0.3, 0.4)

        assert indices["ndvi"] == pytest.approx(0.6, rel=0.01)

    def test_ndvi_range(self):
        """Test NDVI values are in valid range"""
        indices = calculate_vegetation_indices(0.1, 0.9, 0.1, 0.2, 0.3)

        assert -1 <= indices["ndvi"] <= 1
        assert -1 <= indices["ndwi"] <= 1


class TestAnomalyDetection:
    """Tests for NDVI anomaly detection"""

    def test_no_anomaly_normal_data(self):
        """Test no anomaly detected for normal NDVI pattern"""
        historical_mean = 0.66
        historical_std = 0.02
        current = 0.67

        anomaly = detect_anomalies(current, historical_mean, historical_std)

        assert anomaly is None

    def test_anomaly_sudden_drop(self):
        """Test anomaly detected for sudden NDVI drop"""
        historical_mean = 0.66
        historical_std = 0.02
        current = 0.35  # Significant drop (>2 sigma away)

        anomaly = detect_anomalies(current, historical_mean, historical_std, threshold_sigma=2.0)

        assert anomaly is not None
        assert anomaly["type"] == "negative"
        assert anomaly["severity"] in ["medium", "high"]

    def test_anomaly_zero_std(self):
        """Test no anomaly with zero standard deviation"""
        anomaly = detect_anomalies(0.5, 0.6, 0.0)

        assert anomaly is None

    def test_anomaly_positive_deviation(self):
        """Test positive anomaly detection"""
        historical_mean = 0.5
        historical_std = 0.05
        current = 0.65  # 3 sigma above mean

        anomaly = detect_anomalies(current, historical_mean, historical_std, threshold_sigma=2.0)

        assert anomaly is not None
        assert anomaly["type"] == "positive"
