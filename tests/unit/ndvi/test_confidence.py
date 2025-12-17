"""
SAHOOL NDVI Confidence Score Tests
Sprint 8: Unit tests for confidence scoring
"""

import pytest
import sys
sys.path.insert(0, "kernel/services/ndvi_engine/src")

from confidence import (
    clamp01,
    confidence_score,
    confidence_grade,
    should_use_observation,
    weighted_average_ndvi,
    ConfidenceWeights,
    DEFAULT_WEIGHTS,
)


class TestClamp:
    """Test clamp01 utility"""

    def test_clamp_within_range(self):
        """Values in range are unchanged"""
        assert clamp01(0.5) == 0.5
        assert clamp01(0.0) == 0.0
        assert clamp01(1.0) == 1.0

    def test_clamp_below_zero(self):
        """Values below 0 are clamped to 0"""
        assert clamp01(-0.1) == 0.0
        assert clamp01(-100) == 0.0

    def test_clamp_above_one(self):
        """Values above 1 are clamped to 1"""
        assert clamp01(1.1) == 1.0
        assert clamp01(100) == 1.0


class TestConfidenceScore:
    """Test confidence_score function"""

    def test_perfect_score(self):
        """Perfect conditions yield score of 1.0"""
        score = confidence_score(
            cloud_coverage=0.0,
            age_days=0,
            has_percentiles=True,
            has_std=True,
        )
        assert score == 1.0

    def test_cloud_decreases_confidence(self):
        """Higher cloud coverage decreases confidence"""
        clear = confidence_score(cloud_coverage=0.0, age_days=0, has_percentiles=True)
        cloudy = confidence_score(cloud_coverage=0.6, age_days=0, has_percentiles=True)

        assert cloudy < clear

    def test_age_decreases_confidence(self):
        """Older data has lower confidence"""
        fresh = confidence_score(cloud_coverage=0.0, age_days=0, has_percentiles=True)
        old = confidence_score(cloud_coverage=0.0, age_days=14, has_percentiles=True)

        assert old < fresh

    def test_missing_percentiles_decreases_confidence(self):
        """Missing percentiles reduces confidence"""
        complete = confidence_score(
            cloud_coverage=0.0, age_days=0, has_percentiles=True, has_std=True
        )
        incomplete = confidence_score(
            cloud_coverage=0.0, age_days=0, has_percentiles=False, has_std=False
        )

        assert incomplete < complete

    def test_age_penalty_maxes_at_14_days(self):
        """Age penalty doesn't increase beyond 14 days"""
        day_14 = confidence_score(cloud_coverage=0.0, age_days=14, has_percentiles=True)
        day_30 = confidence_score(cloud_coverage=0.0, age_days=30, has_percentiles=True)

        assert day_14 == day_30

    def test_pixel_count_penalty(self):
        """Low pixel count reduces confidence"""
        high_pixels = confidence_score(
            cloud_coverage=0.0,
            age_days=0,
            has_percentiles=True,
            pixel_count=1000,
            min_pixels=100,
        )
        low_pixels = confidence_score(
            cloud_coverage=0.0,
            age_days=0,
            has_percentiles=True,
            pixel_count=50,
            min_pixels=100,
        )

        assert low_pixels < high_pixels

    def test_score_never_negative(self):
        """Score is always >= 0 even with worst conditions"""
        score = confidence_score(
            cloud_coverage=1.0,
            age_days=30,
            has_percentiles=False,
            has_std=False,
        )
        assert score >= 0.0

    def test_custom_weights(self):
        """Custom weights are applied correctly"""
        custom = ConfidenceWeights(
            cloud_penalty=0.8,
            age_penalty=0.1,
            missing_pctl_penalty=0.1,
        )

        score = confidence_score(
            cloud_coverage=0.5,
            age_days=0,
            has_percentiles=True,
            weights=custom,
        )

        # With 0.5 cloud and 0.8 penalty = 0.4 penalty
        # Score should be 1.0 - 0.4 = 0.6
        assert 0.5 <= score <= 0.7


class TestConfidenceGrade:
    """Test confidence_grade function"""

    def test_excellent_grade(self):
        """Score >= 0.9 is excellent"""
        grade_en, grade_ar = confidence_grade(0.95)
        assert grade_en == "excellent"
        assert grade_ar == "ممتاز"

    def test_good_grade(self):
        """Score >= 0.75 is good"""
        grade_en, _ = confidence_grade(0.8)
        assert grade_en == "good"

    def test_moderate_grade(self):
        """Score >= 0.5 is moderate"""
        grade_en, _ = confidence_grade(0.6)
        assert grade_en == "moderate"

    def test_low_grade(self):
        """Score >= 0.25 is low"""
        grade_en, _ = confidence_grade(0.3)
        assert grade_en == "low"

    def test_poor_grade(self):
        """Score < 0.25 is poor"""
        grade_en, grade_ar = confidence_grade(0.1)
        assert grade_en == "poor"
        assert grade_ar == "ضعيف"


class TestShouldUseObservation:
    """Test should_use_observation function"""

    def test_high_confidence_accepted(self):
        """High confidence observations are accepted"""
        assert should_use_observation(0.8) is True

    def test_low_confidence_rejected(self):
        """Low confidence observations are rejected"""
        assert should_use_observation(0.1) is False

    def test_custom_threshold(self):
        """Custom threshold is respected"""
        assert should_use_observation(0.4, min_confidence=0.5) is False
        assert should_use_observation(0.6, min_confidence=0.5) is True


class TestWeightedAverageNdvi:
    """Test weighted_average_ndvi function"""

    def test_simple_average(self):
        """Equal weights give simple average"""
        observations = [(0.5, 1.0), (0.7, 1.0)]
        avg = weighted_average_ndvi(observations)
        assert avg == pytest.approx(0.6, abs=0.001)

    def test_weighted_average(self):
        """Higher confidence has more weight"""
        observations = [(0.5, 0.5), (0.7, 1.0)]
        avg = weighted_average_ndvi(observations)

        # 0.5 contributes less than 0.7
        assert avg is not None
        assert avg > 0.6  # Biased towards 0.7

    def test_empty_returns_none(self):
        """Empty list returns None"""
        assert weighted_average_ndvi([]) is None

    def test_very_low_confidence_filtered(self):
        """Very low confidence observations are filtered"""
        observations = [(0.3, 0.05), (0.7, 0.8)]
        avg = weighted_average_ndvi(observations)

        # Only 0.7 should contribute
        assert avg is not None
        assert avg > 0.65
