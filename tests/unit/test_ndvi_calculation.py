"""
Unit Tests for NDVI Calculation Module
اختبارات وحدة حساب NDVI

Tests for the NDVI calculation handler and utility functions.
"""

import numpy as np
import pytest

from apps.kernel.common.queue.tasks.ndvi_calculation import (
    HEALTH_THRESHOLDS,
    NDVI_THRESHOLDS,
    NDVIAlert,
    NDVIStatistics,
    ZoneClassification,
    calculate_health_score,
    calculate_ndvi_from_bands,
    calculate_ndvi_simple,
    calculate_statistics,
    classify_zones,
    generate_alerts,
    get_vegetation_class,
    handle_ndvi_calculation,
    simulate_band_data,
)


class TestNDVICalculation:
    """Tests for NDVI calculation from bands"""

    def test_calculate_ndvi_basic(self):
        """Test basic NDVI calculation"""
        # Create simple test bands
        red = np.array([[0.1, 0.2], [0.15, 0.25]], dtype=np.float32)
        nir = np.array([[0.5, 0.6], [0.55, 0.65]], dtype=np.float32)

        ndvi = calculate_ndvi_from_bands(red, nir)

        # NDVI = (NIR - RED) / (NIR + RED)
        # For [0][0]: (0.5 - 0.1) / (0.5 + 0.1) = 0.4 / 0.6 = 0.6667
        assert ndvi.shape == (2, 2)
        assert -1 <= ndvi[0, 0] <= 1
        assert np.isclose(ndvi[0, 0], 0.6667, atol=0.01)

    def test_calculate_ndvi_zero_division(self):
        """Test NDVI handles zero division"""
        red = np.array([[0.0, 0.1]], dtype=np.float32)
        nir = np.array([[0.0, 0.3]], dtype=np.float32)

        ndvi = calculate_ndvi_from_bands(red, nir)

        # When both are 0, should return 0
        assert ndvi[0, 0] == 0.0
        # Normal calculation for second pixel
        assert ndvi[0, 1] > 0

    def test_calculate_ndvi_clips_values(self):
        """Test NDVI clips values to [-1, 1] range"""
        # Edge case: very high NIR, very low RED
        red = np.array([[0.01]], dtype=np.float32)
        nir = np.array([[0.99]], dtype=np.float32)

        ndvi = calculate_ndvi_from_bands(red, nir)

        assert -1 <= ndvi[0, 0] <= 1

    def test_calculate_ndvi_water_negative(self):
        """Test NDVI returns negative values for water-like pixels"""
        # Water has higher red reflectance than NIR
        red = np.array([[0.3]], dtype=np.float32)
        nir = np.array([[0.1]], dtype=np.float32)

        ndvi = calculate_ndvi_from_bands(red, nir)

        # Should be negative
        assert ndvi[0, 0] < 0

    def test_calculate_ndvi_dense_vegetation(self):
        """Test NDVI returns high values for dense vegetation"""
        # Dense vegetation has high NIR, low RED
        red = np.array([[0.05]], dtype=np.float32)
        nir = np.array([[0.50]], dtype=np.float32)

        ndvi = calculate_ndvi_from_bands(red, nir)

        # Should be high (healthy vegetation typically > 0.6)
        assert ndvi[0, 0] > 0.6


class TestNDVIStatistics:
    """Tests for NDVI statistics calculation"""

    def test_calculate_statistics_basic(self):
        """Test basic statistics calculation"""
        ndvi = np.array([[0.3, 0.4, 0.5], [0.6, 0.7, 0.8]], dtype=np.float32)

        stats = calculate_statistics(ndvi)

        assert isinstance(stats, NDVIStatistics)
        assert stats.mean == pytest.approx(0.55, abs=0.01)
        assert stats.median == pytest.approx(0.55, abs=0.01)
        assert stats.min == pytest.approx(0.3, abs=0.01)
        assert stats.max == pytest.approx(0.8, abs=0.01)
        assert stats.valid_pixels == 6
        assert stats.total_pixels == 6

    def test_calculate_statistics_with_nan(self):
        """Test statistics handles NaN values"""
        ndvi = np.array([[0.5, np.nan], [0.6, 0.7]], dtype=np.float32)

        stats = calculate_statistics(ndvi)

        # Should only count valid pixels
        assert stats.valid_pixels == 3
        assert stats.total_pixels == 4

    def test_calculate_statistics_coverage_percent(self):
        """Test vegetation coverage percentage calculation"""
        # Mix of vegetation (>0.2) and non-vegetation (<0.2)
        ndvi = np.array([[0.1, 0.3, 0.5], [0.15, 0.4, 0.6]], dtype=np.float32)

        stats = calculate_statistics(ndvi)

        # 4 out of 6 pixels have NDVI > 0.2 (sparse_vegetation threshold)
        assert stats.coverage_percent == pytest.approx(66.67, abs=1)

    def test_calculate_statistics_empty_array(self):
        """Test statistics handles empty array"""
        ndvi = np.array([], dtype=np.float32).reshape(0, 0)

        stats = calculate_statistics(ndvi)

        assert stats.mean == 0.0
        assert stats.valid_pixels == 0

    def test_statistics_to_dict(self):
        """Test NDVIStatistics.to_dict() method"""
        stats = NDVIStatistics(
            mean=0.5,
            median=0.52,
            min=0.1,
            max=0.9,
            std_dev=0.15,
            coverage_percent=80.0,
            valid_pixels=100,
            total_pixels=100,
        )

        result = stats.to_dict()

        assert isinstance(result, dict)
        assert result["mean"] == 0.5
        assert result["coverage_percent"] == 80.0
        assert "valid_pixels" in result


class TestZoneClassification:
    """Tests for zone classification"""

    def test_classify_zones_healthy_vegetation(self):
        """Test classification of healthy vegetation"""
        # All high NDVI values (healthy)
        ndvi = np.array([[0.5, 0.6, 0.7], [0.55, 0.65, 0.75]], dtype=np.float32)

        zones = classify_zones(ndvi)

        assert isinstance(zones, ZoneClassification)
        assert zones.healthy_percent > 80
        assert zones.critical_percent < 5
        assert zones.water_percent == 0

    def test_classify_zones_mixed(self):
        """Test classification of mixed zones"""
        # Mix of different zone types
        ndvi = np.array(
            [
                [-0.2, 0.05, 0.15],  # water, bare_soil, critical
                [0.3, 0.5, 0.7],  # stressed, healthy, healthy
            ],
            dtype=np.float32,
        )

        zones = classify_zones(ndvi)

        # Check all zones are accounted for
        total = (
            zones.water_percent
            + zones.bare_soil_percent
            + zones.critical_percent
            + zones.stressed_percent
            + zones.healthy_percent
        )
        assert total == pytest.approx(100, abs=0.1)

    def test_classify_zones_water_detection(self):
        """Test water zone detection"""
        # Negative NDVI (water)
        ndvi = np.array([[-0.3, -0.2, -0.15]], dtype=np.float32)

        zones = classify_zones(ndvi)

        assert zones.water_percent == pytest.approx(100, abs=0.1)

    def test_zones_to_dict(self):
        """Test ZoneClassification.to_dict() method"""
        zones = ZoneClassification(
            healthy_percent=70.0,
            stressed_percent=15.0,
            critical_percent=8.0,
            bare_soil_percent=5.0,
            water_percent=2.0,
        )

        result = zones.to_dict()

        assert isinstance(result, dict)
        assert result["healthy"] == 70.0
        assert result["stressed"] == 15.0


class TestHealthScore:
    """Tests for health score calculation"""

    def test_calculate_health_score_healthy(self):
        """Test health score for healthy vegetation"""
        stats = NDVIStatistics(
            mean=0.6,
            median=0.62,
            min=0.4,
            max=0.8,
            std_dev=0.1,
            coverage_percent=95.0,
            valid_pixels=1000,
            total_pixels=1000,
        )
        zones = ZoneClassification(
            healthy_percent=85.0,
            stressed_percent=10.0,
            critical_percent=3.0,
            bare_soil_percent=2.0,
            water_percent=0.0,
        )

        score = calculate_health_score(stats, zones)

        # Should be high score (>7)
        assert score >= 7.0
        assert score <= 10.0

    def test_calculate_health_score_poor(self):
        """Test health score for poor vegetation"""
        stats = NDVIStatistics(
            mean=0.2,
            median=0.18,
            min=0.05,
            max=0.35,
            std_dev=0.25,
            coverage_percent=30.0,
            valid_pixels=1000,
            total_pixels=1000,
        )
        zones = ZoneClassification(
            healthy_percent=10.0,
            stressed_percent=25.0,
            critical_percent=40.0,
            bare_soil_percent=20.0,
            water_percent=5.0,
        )

        score = calculate_health_score(stats, zones)

        # Should be low score (<5)
        assert score < 5.0
        assert score >= 0.0

    def test_health_score_bounds(self):
        """Test health score stays within 0-10 bounds"""
        # Extreme cases
        stats_good = NDVIStatistics(
            mean=0.9, median=0.9, min=0.8, max=1.0, std_dev=0.05,
            coverage_percent=100.0, valid_pixels=100, total_pixels=100
        )
        zones_good = ZoneClassification(
            healthy_percent=100.0, stressed_percent=0.0,
            critical_percent=0.0, bare_soil_percent=0.0, water_percent=0.0
        )

        stats_bad = NDVIStatistics(
            mean=-0.5, median=-0.5, min=-1.0, max=0.0, std_dev=0.4,
            coverage_percent=0.0, valid_pixels=100, total_pixels=100
        )
        zones_bad = ZoneClassification(
            healthy_percent=0.0, stressed_percent=0.0,
            critical_percent=100.0, bare_soil_percent=0.0, water_percent=0.0
        )

        score_good = calculate_health_score(stats_good, zones_good)
        score_bad = calculate_health_score(stats_bad, zones_bad)

        assert 0.0 <= score_good <= 10.0
        assert 0.0 <= score_bad <= 10.0


class TestAlertGeneration:
    """Tests for alert generation"""

    def test_generate_alerts_critical_zone(self):
        """Test alert generation for critical zones"""
        stats = NDVIStatistics(
            mean=0.3, median=0.3, min=0.1, max=0.5, std_dev=0.1,
            coverage_percent=50.0, valid_pixels=100, total_pixels=100
        )
        zones = ZoneClassification(
            healthy_percent=20.0, stressed_percent=30.0,
            critical_percent=35.0, bare_soil_percent=10.0, water_percent=5.0
        )

        alerts = generate_alerts(stats, zones)

        # Should have critical zone alert
        critical_alerts = [a for a in alerts if a.alert_type == "critical_vegetation"]
        assert len(critical_alerts) > 0
        assert critical_alerts[0].severity in ["high", "critical"]

    def test_generate_alerts_healthy_field(self):
        """Test minimal alerts for healthy field"""
        stats = NDVIStatistics(
            mean=0.65, median=0.66, min=0.5, max=0.8, std_dev=0.08,
            coverage_percent=95.0, valid_pixels=100, total_pixels=100
        )
        zones = ZoneClassification(
            healthy_percent=90.0, stressed_percent=8.0,
            critical_percent=2.0, bare_soil_percent=0.0, water_percent=0.0
        )

        alerts = generate_alerts(stats, zones)

        # Should have no or few alerts
        assert len(alerts) < 2

    def test_generate_alerts_high_variance(self):
        """Test alert generation for high variance"""
        stats = NDVIStatistics(
            mean=0.5, median=0.5, min=0.1, max=0.9, std_dev=0.3,
            coverage_percent=70.0, valid_pixels=100, total_pixels=100
        )
        zones = ZoneClassification(
            healthy_percent=50.0, stressed_percent=30.0,
            critical_percent=10.0, bare_soil_percent=5.0, water_percent=5.0
        )

        alerts = generate_alerts(stats, zones)

        # Should have non-uniform growth alert
        variance_alerts = [a for a in alerts if a.alert_type == "non_uniform_growth"]
        assert len(variance_alerts) > 0

    def test_alert_to_dict(self):
        """Test NDVIAlert.to_dict() method"""
        alert = NDVIAlert(
            alert_type="critical_vegetation",
            severity="high",
            location={"lat": 24.5, "lon": 46.3},
            area_percent=25.0,
            message_ar="منطقة حرجة",
            message_en="Critical zone detected",
        )

        result = alert.to_dict()

        assert isinstance(result, dict)
        assert result["type"] == "critical_vegetation"
        assert result["severity"] == "high"
        assert result["area_percent"] == 25.0


class TestSimulateBandData:
    """Tests for band data simulation"""

    def test_simulate_band_data_shape(self):
        """Test simulated band data has correct shape"""
        red, nir = simulate_band_data("field-123", "http://example.com/image.tif")

        assert red.shape == (100, 100)
        assert nir.shape == (100, 100)
        assert red.dtype == np.float32
        assert nir.dtype == np.float32

    def test_simulate_band_data_range(self):
        """Test simulated band data is in valid range"""
        red, nir = simulate_band_data("field-456", "http://example.com/image.tif")

        assert np.all(red >= 0) and np.all(red <= 1)
        assert np.all(nir >= 0) and np.all(nir <= 1)

    def test_simulate_band_data_reproducible(self):
        """Test simulated data is reproducible for same field_id"""
        red1, nir1 = simulate_band_data("field-789", "http://example.com/img1.tif")
        red2, nir2 = simulate_band_data("field-789", "http://example.com/img2.tif")

        # Same field_id should produce same data (regardless of image_url)
        np.testing.assert_array_equal(red1, red2)
        np.testing.assert_array_equal(nir1, nir2)

    def test_simulate_band_data_different_fields(self):
        """Test different fields produce different data"""
        red1, _ = simulate_band_data("field-aaa", "http://example.com/image.tif")
        red2, _ = simulate_band_data("field-bbb", "http://example.com/image.tif")

        # Different field_ids should produce different data
        assert not np.array_equal(red1, red2)


class TestHandleNDVICalculation:
    """Tests for the main handler function"""

    def test_handle_ndvi_calculation_basic(self):
        """Test basic NDVI calculation handler"""
        payload = {
            "image_url": "s3://sahool-images/field-test/sentinel2.tif",
            "field_id": "test-field-001",
        }

        result = handle_ndvi_calculation(payload)

        assert "ndvi_map_url" in result
        assert "statistics" in result
        assert "health_score" in result
        assert "alerts" in result
        assert "zones" in result
        assert result["field_id"] == "test-field-001"

    def test_handle_ndvi_calculation_with_band_data(self):
        """Test handler with provided band data"""
        red = np.random.rand(50, 50) * 0.2
        nir = np.random.rand(50, 50) * 0.6 + 0.3

        payload = {
            "image_url": "s3://test/image.tif",
            "field_id": "test-field-002",
            "red_band_data": red.tolist(),
            "nir_band_data": nir.tolist(),
        }

        result = handle_ndvi_calculation(payload)

        assert "statistics" in result
        assert result["metadata"]["image_dimensions"]["height"] == 50
        assert result["metadata"]["image_dimensions"]["width"] == 50

    def test_handle_ndvi_calculation_missing_fields(self):
        """Test handler raises error for missing required fields"""
        payload = {"image_url": "s3://test/image.tif"}  # Missing field_id

        with pytest.raises(ValueError) as exc_info:
            handle_ndvi_calculation(payload)

        assert "required" in str(exc_info.value).lower()

    def test_handle_ndvi_calculation_include_array(self):
        """Test handler can include NDVI array in result"""
        payload = {
            "image_url": "s3://test/image.tif",
            "field_id": "test-field-003",
            "include_array": True,
        }

        result = handle_ndvi_calculation(payload)

        assert "ndvi_array" in result
        assert isinstance(result["ndvi_array"], list)


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_calculate_ndvi_simple(self):
        """Test simplified NDVI calculation interface"""
        red = [[0.1, 0.2], [0.15, 0.25]]
        nir = [[0.5, 0.6], [0.55, 0.65]]

        result = calculate_ndvi_simple(red, nir)

        assert "ndvi_array" in result
        assert "statistics" in result
        assert "zones" in result
        assert "health_score" in result
        assert "alerts" in result

    def test_get_vegetation_class_water(self):
        """Test vegetation class for water"""
        assert get_vegetation_class(-0.3) == "water"

    def test_get_vegetation_class_bare_soil(self):
        """Test vegetation class for bare soil"""
        assert get_vegetation_class(0.05) == "bare_soil"

    def test_get_vegetation_class_sparse(self):
        """Test vegetation class for sparse vegetation"""
        assert get_vegetation_class(0.15) == "sparse_vegetation"

    def test_get_vegetation_class_moderate(self):
        """Test vegetation class for moderate vegetation"""
        assert get_vegetation_class(0.35) == "moderate_vegetation"

    def test_get_vegetation_class_dense(self):
        """Test vegetation class for dense vegetation"""
        assert get_vegetation_class(0.55) == "dense_vegetation"

    def test_get_vegetation_class_very_dense(self):
        """Test vegetation class for very dense vegetation"""
        assert get_vegetation_class(0.85) == "very_dense_vegetation"


class TestThresholds:
    """Tests for threshold constants"""

    def test_ndvi_thresholds_ordering(self):
        """Test NDVI thresholds are properly ordered"""
        assert NDVI_THRESHOLDS["water"] < NDVI_THRESHOLDS["bare_soil"]
        assert NDVI_THRESHOLDS["bare_soil"] < NDVI_THRESHOLDS["sparse_vegetation"]
        assert NDVI_THRESHOLDS["sparse_vegetation"] < NDVI_THRESHOLDS["moderate_vegetation"]
        assert NDVI_THRESHOLDS["moderate_vegetation"] < NDVI_THRESHOLDS["dense_vegetation"]
        assert NDVI_THRESHOLDS["dense_vegetation"] < NDVI_THRESHOLDS["very_dense"]

    def test_health_thresholds_ordering(self):
        """Test health thresholds are properly ordered"""
        assert HEALTH_THRESHOLDS["critical"] < HEALTH_THRESHOLDS["poor"]
        assert HEALTH_THRESHOLDS["poor"] < HEALTH_THRESHOLDS["fair"]
        assert HEALTH_THRESHOLDS["fair"] < HEALTH_THRESHOLDS["good"]
        assert HEALTH_THRESHOLDS["good"] < HEALTH_THRESHOLDS["excellent"]
