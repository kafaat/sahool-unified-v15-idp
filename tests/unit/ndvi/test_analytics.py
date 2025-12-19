"""
SAHOOL NDVI Analytics Tests
Sprint 8: Unit tests for NDVI analytics and trends
"""

import pytest
from datetime import date
import sys
sys.path.insert(0, "archive/kernel-legacy")

# Use absolute imports to avoid import errors
from kernel.services.ndvi_engine.src.analytics import (
    compute_trend,
    compute_linear_trend,
    summarize,
    compare_to_historical_mean,
    NdviSummary,
)


class TestComputeTrend:
    """Test compute_trend function"""

    def test_insufficient_data(self):
        """Less than 4 points returns insufficient"""
        assert compute_trend([0.5, 0.6, 0.7]) == "insufficient"
        assert compute_trend([0.5]) == "insufficient"
        assert compute_trend([]) == "insufficient"

    def test_rising_trend(self):
        """Increasing values detected as rising"""
        values = [0.3, 0.35, 0.5, 0.55, 0.6, 0.65]
        assert compute_trend(values) == "rising"

    def test_falling_trend(self):
        """Decreasing values detected as falling"""
        values = [0.7, 0.65, 0.5, 0.45, 0.4, 0.35]
        assert compute_trend(values) == "falling"

    def test_stable_trend(self):
        """Flat values detected as stable"""
        values = [0.5, 0.52, 0.48, 0.51, 0.49, 0.50]
        assert compute_trend(values) == "stable"

    def test_custom_threshold(self):
        """Custom threshold affects detection"""
        values = [0.5, 0.51, 0.52, 0.53]

        # With default threshold (0.03), should be stable
        assert compute_trend(values) == "stable"

        # With lower threshold, should be rising
        assert compute_trend(values, threshold=0.01) == "rising"


class TestLinearTrend:
    """Test compute_linear_trend function"""

    def test_insufficient_data(self):
        """Less than 3 points returns None"""
        assert compute_linear_trend([0.5, 0.6]) is None
        assert compute_linear_trend([]) is None

    def test_positive_slope(self):
        """Increasing values have positive slope"""
        values = [0.3, 0.4, 0.5, 0.6, 0.7]
        result = compute_linear_trend(values)

        assert result is not None
        slope, r_squared = result
        assert slope > 0

    def test_negative_slope(self):
        """Decreasing values have negative slope"""
        values = [0.7, 0.6, 0.5, 0.4, 0.3]
        result = compute_linear_trend(values)

        assert result is not None
        slope, r_squared = result
        assert slope < 0

    def test_perfect_fit(self):
        """Perfect linear data has R² = 1"""
        values = [0.0, 0.1, 0.2, 0.3, 0.4]
        result = compute_linear_trend(values)

        assert result is not None
        slope, r_squared = result
        assert r_squared == pytest.approx(1.0, abs=0.001)

    def test_flat_line(self):
        """Constant values have zero slope"""
        values = [0.5, 0.5, 0.5, 0.5]
        result = compute_linear_trend(values)

        assert result is not None
        slope, r_squared = result
        assert slope == pytest.approx(0.0, abs=0.001)


class TestHistoricalComparison:
    """Test compare_to_historical_mean function"""

    def test_normal_value(self):
        """Value within 1 std is normal"""
        result = compare_to_historical_mean(
            current_value=0.55,
            historical_mean=0.5,
            historical_std=0.1,
        )

        assert result["status"] == "normal"
        assert -1 < result["z_score"] < 1

    def test_above_normal(self):
        """Value 1-2 std above is above_normal"""
        result = compare_to_historical_mean(
            current_value=0.65,
            historical_mean=0.5,
            historical_std=0.1,
        )

        assert result["status"] == "above_normal"
        assert 1 <= result["z_score"] < 2

    def test_below_normal(self):
        """Value 1-2 std below is below_normal"""
        result = compare_to_historical_mean(
            current_value=0.35,
            historical_mean=0.5,
            historical_std=0.1,
        )

        assert result["status"] == "below_normal"
        assert -2 < result["z_score"] <= -1

    def test_significantly_above(self):
        """Value >2 std above is significantly_above"""
        result = compare_to_historical_mean(
            current_value=0.8,
            historical_mean=0.5,
            historical_std=0.1,
        )

        assert result["status"] == "significantly_above"
        assert result["z_score"] >= 2

    def test_significantly_below(self):
        """Value >2 std below is significantly_below"""
        result = compare_to_historical_mean(
            current_value=0.2,
            historical_mean=0.5,
            historical_std=0.1,
        )

        assert result["status"] == "significantly_below"
        assert result["z_score"] <= -2

    def test_zero_std_handled(self):
        """Zero standard deviation doesn't crash"""
        result = compare_to_historical_mean(
            current_value=0.6,
            historical_mean=0.5,
            historical_std=0.0,
        )

        assert result["z_score"] == 0.0

    def test_deviation_percentage(self):
        """Deviation percentage is calculated correctly"""
        result = compare_to_historical_mean(
            current_value=0.6,
            historical_mean=0.5,
            historical_std=0.1,
        )

        # (0.6 - 0.5) / 0.5 * 100 = 20%
        assert result["deviation_pct"] == pytest.approx(20.0, abs=0.1)


class TestNdviSummary:
    """Test NdviSummary dataclass"""

    def test_summary_to_dict(self):
        """Summary serializes correctly"""
        summary = NdviSummary(
            count=10,
            ndvi_mean=0.55,
            ndvi_min=0.3,
            ndvi_max=0.8,
            ndvi_std=0.15,
            confidence_mean=0.75,
            trend="rising",
            trend_slope=0.01,
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
        )

        data = summary.to_dict()

        assert data["count"] == 10
        assert data["ndvi_mean"] == 0.55
        assert data["trend"] == "rising"
        assert data["date_range"]["start"] == "2024-01-01"
        assert data["date_range"]["end"] == "2024-01-31"

    def test_empty_summary(self):
        """Empty summary has correct defaults"""
        summary = NdviSummary(
            count=0,
            ndvi_mean=0.0,
            ndvi_min=0.0,
            ndvi_max=0.0,
            ndvi_std=None,
            confidence_mean=0.0,
            trend="insufficient",
            trend_slope=None,
            date_range=None,
        )

        data = summary.to_dict()

        assert data["count"] == 0
        assert data["ndvi_std"] is None
        assert data["trend"] == "insufficient"
