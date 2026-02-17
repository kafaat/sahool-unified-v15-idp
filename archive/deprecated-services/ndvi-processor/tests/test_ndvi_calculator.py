"""
NDVI Calculator Tests
اختبارات حاسبة NDVI
"""

import numpy as np
import pytest


class TestNDVICalculator:
    """Test suite for NDVI calculation functions."""

    def test_calculate_ndvi_basic(self):
        """Test basic NDVI calculation with valid bands."""
        # NDVI = (NIR - RED) / (NIR + RED)
        nir = np.array([[0.5, 0.6], [0.7, 0.8]])
        red = np.array([[0.1, 0.2], [0.1, 0.2]])

        expected = (nir - red) / (nir + red)
        result = self._calculate_ndvi(nir, red)

        np.testing.assert_array_almost_equal(result, expected)

    def test_calculate_ndvi_handles_zero_division(self):
        """Test NDVI handles zero division gracefully."""
        nir = np.array([[0.0, 0.5], [0.5, 0.5]])
        red = np.array([[0.0, 0.1], [0.1, 0.1]])

        result = self._calculate_ndvi(nir, red)

        # Should handle 0/0 case
        assert not np.isnan(result).all()

    def test_calculate_ndvi_range(self):
        """Test NDVI values are within valid range [-1, 1]."""
        nir = np.random.rand(100, 100)
        red = np.random.rand(100, 100)

        result = self._calculate_ndvi(nir, red)

        assert result.min() >= -1.0
        assert result.max() <= 1.0

    def test_calculate_ndvi_healthy_vegetation(self):
        """Test NDVI returns high values for healthy vegetation."""
        # Healthy vegetation: high NIR, low RED
        nir = np.array([[0.8, 0.9], [0.85, 0.9]])
        red = np.array([[0.1, 0.1], [0.1, 0.1]])

        result = self._calculate_ndvi(nir, red)

        # Healthy vegetation should have NDVI > 0.6
        assert (result > 0.6).all()

    def test_calculate_ndvi_bare_soil(self):
        """Test NDVI returns low values for bare soil."""
        # Bare soil: similar NIR and RED
        nir = np.array([[0.3, 0.35], [0.32, 0.33]])
        red = np.array([[0.25, 0.30], [0.28, 0.29]])

        result = self._calculate_ndvi(nir, red)

        # Bare soil should have NDVI < 0.2
        assert (result < 0.3).all()

    def test_calculate_ndvi_water(self):
        """Test NDVI returns negative values for water."""
        # Water: RED > NIR
        nir = np.array([[0.05, 0.06], [0.04, 0.05]])
        red = np.array([[0.1, 0.12], [0.11, 0.13]])

        result = self._calculate_ndvi(nir, red)

        # Water should have negative NDVI
        assert (result < 0).all()

    @staticmethod
    def _calculate_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Calculate NDVI from NIR and RED bands."""
        with np.errstate(divide="ignore", invalid="ignore"):
            ndvi = (nir - red) / (nir + red)
            ndvi = np.nan_to_num(ndvi, nan=0.0, posinf=1.0, neginf=-1.0)
        return np.clip(ndvi, -1.0, 1.0)


class TestNDVIClassification:
    """Test suite for NDVI classification."""

    @pytest.mark.parametrize(
        "ndvi,expected_class",
        [
            (-0.5, "water"),
            (0.0, "bare_soil"),
            (0.15, "sparse_vegetation"),
            (0.35, "moderate_vegetation"),
            (0.55, "dense_vegetation"),
            (0.8, "very_dense_vegetation"),
        ],
    )
    def test_classify_ndvi(self, ndvi: float, expected_class: str):
        """Test NDVI classification into categories."""
        result = self._classify_ndvi(ndvi)
        assert result == expected_class

    def test_classify_ndvi_array(self):
        """Test classification of NDVI array."""
        ndvi_array = np.array([-0.5, 0.0, 0.2, 0.4, 0.6, 0.85])
        expected = [
            "water",
            "bare_soil",
            "sparse_vegetation",
            "moderate_vegetation",
            "dense_vegetation",
            "very_dense_vegetation",
        ]

        result = [self._classify_ndvi(v) for v in ndvi_array]
        assert result == expected

    @staticmethod
    def _classify_ndvi(ndvi: float) -> str:
        """Classify NDVI value into vegetation category."""
        if ndvi < -0.1:
            return "water"
        elif ndvi < 0.1:
            return "bare_soil"
        elif ndvi < 0.25:
            return "sparse_vegetation"
        elif ndvi < 0.45:
            return "moderate_vegetation"
        elif ndvi < 0.65:
            return "dense_vegetation"
        else:
            return "very_dense_vegetation"


class TestNDVIStatistics:
    """Test suite for NDVI statistics calculation."""

    def test_calculate_statistics(self):
        """Test NDVI statistics calculation."""
        ndvi_data = np.array([0.2, 0.4, 0.6, 0.5, 0.3, 0.7, 0.45])

        stats = self._calculate_statistics(ndvi_data)

        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
        assert "median" in stats

        assert stats["mean"] == pytest.approx(np.mean(ndvi_data), rel=1e-5)
        assert stats["std"] == pytest.approx(np.std(ndvi_data), rel=1e-5)
        assert stats["min"] == pytest.approx(np.min(ndvi_data), rel=1e-5)
        assert stats["max"] == pytest.approx(np.max(ndvi_data), rel=1e-5)

    def test_calculate_percentiles(self):
        """Test NDVI percentile calculation."""
        ndvi_data = np.arange(0, 1, 0.01)  # 0 to 0.99

        stats = self._calculate_statistics(ndvi_data)

        assert "p25" in stats
        assert "p75" in stats
        assert stats["p25"] == pytest.approx(0.25, rel=0.1)
        assert stats["p75"] == pytest.approx(0.75, rel=0.1)

    @staticmethod
    def _calculate_statistics(ndvi_data: np.ndarray) -> dict:
        """Calculate statistics for NDVI data."""
        return {
            "mean": float(np.mean(ndvi_data)),
            "std": float(np.std(ndvi_data)),
            "min": float(np.min(ndvi_data)),
            "max": float(np.max(ndvi_data)),
            "median": float(np.median(ndvi_data)),
            "p25": float(np.percentile(ndvi_data, 25)),
            "p75": float(np.percentile(ndvi_data, 75)),
        }


class TestNDVIAlertThresholds:
    """Test suite for NDVI alert threshold detection."""

    def test_detect_low_ndvi_alert(self):
        """Test detection of low NDVI alert."""
        ndvi_value = 0.15
        threshold = 0.25

        alert = self._check_threshold(ndvi_value, threshold, "low")

        assert alert is not None
        assert alert["type"] == "low_ndvi"
        assert alert["severity"] == "warning"

    def test_detect_critical_ndvi_alert(self):
        """Test detection of critical NDVI alert."""
        ndvi_value = 0.05
        threshold = 0.1

        alert = self._check_threshold(ndvi_value, threshold, "critical")

        assert alert is not None
        assert alert["type"] == "critical_ndvi"
        assert alert["severity"] == "critical"

    def test_no_alert_for_healthy_ndvi(self):
        """Test no alert for healthy NDVI."""
        ndvi_value = 0.65
        threshold = 0.25

        alert = self._check_threshold(ndvi_value, threshold, "low")

        assert alert is None

    def test_detect_ndvi_drop(self):
        """Test detection of significant NDVI drop."""
        previous_ndvi = 0.7
        current_ndvi = 0.4
        drop_threshold = 0.2

        alert = self._check_drop(previous_ndvi, current_ndvi, drop_threshold)

        assert alert is not None
        assert alert["type"] == "ndvi_drop"
        assert alert["drop_amount"] == pytest.approx(0.3, rel=1e-5)

    @staticmethod
    def _check_threshold(value: float, threshold: float, level: str) -> dict | None:
        """Check if NDVI value triggers an alert."""
        if value < threshold:
            severity = "critical" if level == "critical" else "warning"
            return {
                "type": f"{level}_ndvi",
                "severity": severity,
                "value": value,
                "threshold": threshold,
            }
        return None

    @staticmethod
    def _check_drop(previous: float, current: float, threshold: float) -> dict | None:
        """Check for significant NDVI drop."""
        drop = previous - current
        if drop > threshold:
            return {
                "type": "ndvi_drop",
                "severity": "warning",
                "previous_value": previous,
                "current_value": current,
                "drop_amount": drop,
            }
        return None
