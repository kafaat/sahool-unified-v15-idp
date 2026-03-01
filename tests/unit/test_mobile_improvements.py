"""Tests for mobile improvement tracker."""
import pytest
from shared.mobile_config import (
    MobileImprovementTracker, ImprovementCategory, Priority, MOBILE_IMPROVEMENTS
)

class TestMobileImprovements:
    def setup_method(self):
        self.tracker = MobileImprovementTracker()

    def test_has_20_improvements(self):
        assert len(MOBILE_IMPROVEMENTS) == 20

    def test_list_all(self):
        improvements = self.tracker.list_improvements()
        assert len(improvements) == 20

    def test_filter_by_category(self):
        ui = self.tracker.list_improvements(category=ImprovementCategory.UI_UX)
        assert len(ui) == 8
        perf = self.tracker.list_improvements(category=ImprovementCategory.PERFORMANCE)
        assert len(perf) == 6
        feat = self.tracker.list_improvements(category=ImprovementCategory.NEW_FEATURES)
        assert len(feat) == 6

    def test_filter_by_priority(self):
        p0 = self.tracker.list_improvements(priority=Priority.P0)
        assert len(p0) > 0

    def test_get_summary(self):
        summary = self.tracker.get_summary()
        assert summary["total_improvements"] == 20
        assert summary["message_ar"] != ""

    def test_all_have_arabic(self):
        for imp in self.tracker.list_improvements():
            assert imp.title_ar, f"{imp.improvement_id} missing title_ar"
