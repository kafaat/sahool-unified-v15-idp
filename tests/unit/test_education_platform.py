"""Tests for farmer education platform."""
import pytest
from shared.learning_marketplace.education_platform import (
    EducationPlatform,
    LEARNING_PATHS,
    FARMER_LEVELS,
)

class TestEducationPlatform:
    def setup_method(self):
        self.platform = EducationPlatform()

    def test_get_all_paths(self):
        paths = self.platform.get_paths()
        assert len(paths) >= 4

    def test_get_wheat_paths(self):
        paths = self.platform.get_paths(crop_type="wheat")
        assert len(paths) > 0

    def test_complete_module(self):
        progress = self.platform.complete_module("farmer-001", "M01")
        assert progress.total_points > 0
        assert progress.completed_modules == 1

    def test_farmer_level_progression(self):
        level, title, ar = self.platform.get_farmer_level(0)
        assert level == 1
        level, title, ar = self.platform.get_farmer_level(1500)
        assert level >= 6

    def test_issue_certificate(self):
        cert = self.platform.issue_certificate("farmer-001", "LP-WHEAT-BASIC")
        assert cert.certificate_id != ""
        assert cert.verification_code != ""

    def test_all_paths_have_arabic(self):
        for path in self.platform.get_paths():
            assert path.title_ar, f"Path {path.path_id} missing title_ar"
