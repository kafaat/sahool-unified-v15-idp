"""
SAHOOL NDVI Cloud Cover Tests
Sprint 8: Unit tests for cloud coverage estimation
"""

import pytest
import sys

sys.path.insert(0, "archive/kernel-legacy/kernel/services/ndvi_engine/src")

from cloud_cover import (
    estimate_cloud_coverage_from_mask,
    estimate_cloud_coverage_from_scl,
    estimate_cloud_coverage_from_qa,
    is_scene_usable,
    cloud_coverage_grade,
    SCLClass,
    CLOUD_CLASSES,
)


class TestCloudMaskEstimation:
    """Test estimate_cloud_coverage_from_mask"""

    def test_no_clouds(self):
        """All clear pixels returns 0"""
        mask = [0, 0, 0, 0]
        assert estimate_cloud_coverage_from_mask(mask) == 0.0

    def test_all_clouds(self):
        """All cloud pixels returns 1"""
        mask = [1, 1, 1, 1]
        assert estimate_cloud_coverage_from_mask(mask) == 1.0

    def test_partial_clouds(self):
        """Mixed pixels return correct fraction"""
        mask = [0, 0, 0, 1]  # 25% cloud
        assert estimate_cloud_coverage_from_mask(mask) == 0.25

    def test_empty_mask(self):
        """Empty mask returns 0"""
        assert estimate_cloud_coverage_from_mask([]) == 0.0

    def test_custom_cloud_value(self):
        """Custom cloud value is respected"""
        mask = [0, 0, 2, 2]  # 2 = cloud
        coverage = estimate_cloud_coverage_from_mask(mask, cloud_value=2)
        assert coverage == 0.5


class TestSCLEstimation:
    """Test estimate_cloud_coverage_from_scl"""

    def test_clear_scene(self):
        """Scene with vegetation is clear"""
        scl = [SCLClass.VEGETATION] * 10
        result = estimate_cloud_coverage_from_scl(scl)

        assert result.cloud_fraction == 0.0
        assert result.usable_fraction == 1.0
        assert result.cloud_pixels == 0
        assert result.usable_pixels == 10

    def test_cloudy_scene(self):
        """Scene with high probability clouds"""
        scl = [SCLClass.CLOUD_HIGH_PROB] * 10
        result = estimate_cloud_coverage_from_scl(scl)

        assert result.cloud_fraction == 1.0
        assert result.cloud_pixels == 10

    def test_mixed_scene(self):
        """Mixed scene with various classes"""
        scl = [
            SCLClass.VEGETATION,
            SCLClass.VEGETATION,
            SCLClass.NOT_VEGETATED,
            SCLClass.CLOUD_MEDIUM_PROB,
            SCLClass.CLOUD_HIGH_PROB,
        ]
        result = estimate_cloud_coverage_from_scl(scl)

        assert result.cloud_fraction == 0.4  # 2 cloud out of 5
        assert result.total_pixels == 5

    def test_empty_scl(self):
        """Empty SCL returns zeros"""
        result = estimate_cloud_coverage_from_scl([])

        assert result.cloud_fraction == 0.0
        assert result.total_pixels == 0


class TestQAEstimation:
    """Test estimate_cloud_coverage_from_qa"""

    def test_clear_qa(self):
        """No cloud bits set returns 0"""
        # Bit 10 and 11 not set
        qa = [0, 0, 0, 0]
        assert estimate_cloud_coverage_from_qa(qa) == 0.0

    def test_cloud_bit_set(self):
        """Cloud bit (10) set is detected"""
        # Bit 10 = 1024
        qa = [1024, 0, 0, 0]
        coverage = estimate_cloud_coverage_from_qa(qa)
        assert coverage == 0.25

    def test_cirrus_bit_set(self):
        """Cirrus bit (11) set is detected"""
        # Bit 11 = 2048
        qa = [2048, 0, 0, 0]
        coverage = estimate_cloud_coverage_from_qa(qa)
        assert coverage == 0.25

    def test_both_bits_set(self):
        """Both cloud and cirrus bits are detected"""
        # Bit 10 + Bit 11 = 1024 + 2048 = 3072
        qa = [3072, 0, 0, 0]
        coverage = estimate_cloud_coverage_from_qa(qa)
        assert coverage == 0.25

    def test_empty_qa(self):
        """Empty QA returns 0"""
        assert estimate_cloud_coverage_from_qa([]) == 0.0


class TestSceneUsability:
    """Test is_scene_usable function"""

    def test_clear_scene_usable(self):
        """Clear scene is usable"""
        assert is_scene_usable(0.1) is True

    def test_cloudy_scene_not_usable(self):
        """Very cloudy scene is not usable"""
        assert is_scene_usable(0.5) is False

    def test_custom_max_cloud(self):
        """Custom max_cloud threshold is respected"""
        assert is_scene_usable(0.4, max_cloud=0.5) is True
        assert is_scene_usable(0.6, max_cloud=0.5) is False

    def test_low_usable_fraction_rejected(self):
        """Low usable fraction is rejected"""
        assert is_scene_usable(0.1, usable_fraction=0.3, min_usable=0.5) is False

    def test_high_usable_fraction_accepted(self):
        """High usable fraction is accepted"""
        assert is_scene_usable(0.1, usable_fraction=0.8, min_usable=0.5) is True


class TestCloudGrade:
    """Test cloud_coverage_grade function"""

    def test_clear_grade(self):
        """Coverage <= 0.1 is clear"""
        grade_en, grade_ar = cloud_coverage_grade(0.05)
        assert grade_en == "clear"
        assert grade_ar == "صافي"

    def test_mostly_clear_grade(self):
        """Coverage <= 0.3 is mostly clear"""
        grade_en, _ = cloud_coverage_grade(0.2)
        assert grade_en == "mostly_clear"

    def test_partly_cloudy_grade(self):
        """Coverage <= 0.5 is partly cloudy"""
        grade_en, _ = cloud_coverage_grade(0.4)
        assert grade_en == "partly_cloudy"

    def test_mostly_cloudy_grade(self):
        """Coverage <= 0.7 is mostly cloudy"""
        grade_en, _ = cloud_coverage_grade(0.6)
        assert grade_en == "mostly_cloudy"

    def test_cloudy_grade(self):
        """Coverage > 0.7 is cloudy"""
        grade_en, grade_ar = cloud_coverage_grade(0.8)
        assert grade_en == "cloudy"
        assert grade_ar == "غائم"
