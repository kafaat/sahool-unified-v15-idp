"""
Tests for Mobile Improvement Tracker | اختبارات متتبع تحسينات الهاتف

Tests cover tracker initialization, filtering by category/status/priority,
completion statistics, and bilingual content.
"""

from __future__ import annotations

import pytest

from shared.mobile_config import (
    CATEGORY_AR,
    MOBILE_IMPROVEMENTS,
    ImprovementCategory,
    ImprovementStatus,
    MobileImprovement,
    MobileImprovementTracker,
    Priority,
)


class TestImprovementsData:
    """Tests for the MOBILE_IMPROVEMENTS data list | اختبارات بيانات التحسينات"""

    def test_has_20_improvements(self) -> None:
        """There should be exactly 20 improvement definitions."""
        assert len(MOBILE_IMPROVEMENTS) == 20

    def test_all_have_id(self) -> None:
        """Every improvement has a unique ID."""
        ids = [imp["id"] for imp in MOBILE_IMPROVEMENTS]
        assert len(ids) == len(set(ids))

    def test_all_have_arabic_title(self) -> None:
        """Every improvement has an Arabic title | كل تحسين له عنوان عربي"""
        for imp in MOBILE_IMPROVEMENTS:
            assert imp.get("title_ar", "") != "", f"{imp['id']} missing title_ar"


class TestTrackerInit:
    """Tests for MobileImprovementTracker initialization | اختبارات تهيئة المتتبع"""

    def setup_method(self) -> None:
        self.tracker = MobileImprovementTracker()

    def test_tracker_loads_all_improvements(self) -> None:
        """Tracker loads all 20 improvements."""
        assert len(self.tracker._improvements) == 20

    def test_improvements_are_dataclass_instances(self) -> None:
        """All loaded items are MobileImprovement dataclass instances."""
        for imp in self.tracker._improvements:
            assert isinstance(imp, MobileImprovement)


class TestGetImprovements:
    """Tests for get_improvements() | اختبارات الحصول على التحسينات"""

    def setup_method(self) -> None:
        self.tracker = MobileImprovementTracker()

    def test_get_all_improvements(self) -> None:
        """get_improvements() without filter returns all 20."""
        all_imps = self.tracker.get_improvements()
        assert len(all_imps) == 20

    def test_filter_by_planned_status(self) -> None:
        """Filter by PLANNED status returns planned items only."""
        planned = self.tracker.get_improvements(status=ImprovementStatus.PLANNED)
        for imp in planned:
            assert imp.status == ImprovementStatus.PLANNED

    def test_filter_by_completed_status(self) -> None:
        """Filter by COMPLETED status returns completed items."""
        completed = self.tracker.get_improvements(status=ImprovementStatus.COMPLETED)
        assert len(completed) > 0
        for imp in completed:
            assert imp.status == ImprovementStatus.COMPLETED

    def test_filter_by_in_progress_status(self) -> None:
        """Filter by IN_PROGRESS status returns in-progress items."""
        in_progress = self.tracker.get_improvements(status=ImprovementStatus.IN_PROGRESS)
        assert len(in_progress) > 0
        for imp in in_progress:
            assert imp.status == ImprovementStatus.IN_PROGRESS


class TestGetByCategory:
    """Tests for get_by_category() | اختبارات التصفية حسب الفئة"""

    def setup_method(self) -> None:
        self.tracker = MobileImprovementTracker()

    def test_performance_category(self) -> None:
        """Filter by performance category returns 4 items."""
        items = self.tracker.get_by_category(ImprovementCategory.PERFORMANCE)
        assert len(items) == 4
        for imp in items:
            assert imp.category == ImprovementCategory.PERFORMANCE

    def test_ux_category(self) -> None:
        """Filter by UX category returns 4 items."""
        items = self.tracker.get_by_category(ImprovementCategory.UX)
        assert len(items) == 4
        for imp in items:
            assert imp.category == ImprovementCategory.UX

    def test_offline_category(self) -> None:
        """Filter by offline category returns 4 items."""
        items = self.tracker.get_by_category(ImprovementCategory.OFFLINE)
        assert len(items) == 4

    def test_security_category(self) -> None:
        """Filter by security category returns 4 items."""
        items = self.tracker.get_by_category(ImprovementCategory.SECURITY)
        assert len(items) == 4

    def test_features_category(self) -> None:
        """Filter by features category returns 4 items."""
        items = self.tracker.get_by_category(ImprovementCategory.FEATURES)
        assert len(items) == 4

    def test_all_categories_sum_to_20(self) -> None:
        """Sum of items across all 5 categories should be 20."""
        total = 0
        for cat in (
            ImprovementCategory.PERFORMANCE,
            ImprovementCategory.UX,
            ImprovementCategory.OFFLINE,
            ImprovementCategory.SECURITY,
            ImprovementCategory.FEATURES,
        ):
            total += len(self.tracker.get_by_category(cat))
        assert total == 20


class TestCompletionStats:
    """Tests for get_completion_stats() | اختبارات إحصائيات الإنجاز"""

    def setup_method(self) -> None:
        self.tracker = MobileImprovementTracker()

    def test_stats_total(self) -> None:
        """Total should be 20."""
        stats = self.tracker.get_completion_stats()
        assert stats["total"] == 20

    def test_stats_sum_matches_total(self) -> None:
        """planned + in_progress + completed should equal total."""
        stats = self.tracker.get_completion_stats()
        assert stats["planned"] + stats["in_progress"] + stats["completed"] == stats["total"]

    def test_stats_has_completion_percent(self) -> None:
        """Stats include completion_percent."""
        stats = self.tracker.get_completion_stats()
        assert "completion_percent" in stats
        assert 0.0 <= stats["completion_percent"] <= 100.0

    def test_stats_by_category(self) -> None:
        """Stats include by_category breakdown."""
        stats = self.tracker.get_completion_stats()
        by_cat = stats["by_category"]
        assert "performance" in by_cat
        assert "ux" in by_cat
        assert "offline" in by_cat
        assert "security" in by_cat
        assert "features" in by_cat

    def test_stats_by_category_has_total_weeks(self) -> None:
        """Each category stats includes total_weeks."""
        stats = self.tracker.get_completion_stats()
        for cat_data in stats["by_category"].values():
            assert "total_weeks" in cat_data
            assert cat_data["total_weeks"] >= 0

    def test_stats_bilingual_message(self) -> None:
        """Stats has bilingual message | رسالة ثنائية اللغة"""
        stats = self.tracker.get_completion_stats()
        assert stats["message"] != ""
        assert stats["message_ar"] != ""
        assert "مكتمل" in stats["message_ar"]

    def test_completed_count_positive(self) -> None:
        """There should be some completed items (security items are completed)."""
        stats = self.tracker.get_completion_stats()
        assert stats["completed"] > 0


class TestLegacyAPI:
    """Tests for legacy list_improvements and get_summary | اختبارات التوافق القديم"""

    def setup_method(self) -> None:
        self.tracker = MobileImprovementTracker()

    def test_list_all(self) -> None:
        """list_improvements() returns all 20."""
        all_imps = self.tracker.list_improvements()
        assert len(all_imps) == 20

    def test_list_by_priority_p0(self) -> None:
        """filter by P0 priority returns items."""
        p0 = self.tracker.list_improvements(priority=Priority.P0)
        assert len(p0) > 0
        for imp in p0:
            assert imp.priority == Priority.P0

    def test_get_summary(self) -> None:
        """get_summary() returns expected structure."""
        summary = self.tracker.get_summary()
        assert summary["total_improvements"] == 20
        assert summary["message_ar"] != ""
        assert "p0_count" in summary
        assert "total_effort_weeks" in summary
        assert summary["total_effort_weeks"] > 0


class TestBilingualContent:
    """Tests for bilingual content completeness | اختبارات اكتمال المحتوى الثنائي"""

    def setup_method(self) -> None:
        self.tracker = MobileImprovementTracker()

    def test_all_improvements_have_arabic_title(self) -> None:
        """Every improvement has a non-empty Arabic title | كل تحسين له عنوان عربي"""
        for imp in self.tracker.get_improvements():
            assert imp.title_ar != "", f"{imp.id} missing title_ar"

    def test_all_improvements_have_category_arabic(self) -> None:
        """Every improvement has Arabic category label."""
        for imp in self.tracker.get_improvements():
            assert imp.category_ar != "", f"{imp.id} missing category_ar"

    def test_all_improvements_have_priority_arabic(self) -> None:
        """Every improvement has Arabic priority label."""
        for imp in self.tracker.get_improvements():
            assert imp.priority_ar != "", f"{imp.id} missing priority_ar"

    def test_all_improvements_have_status_arabic(self) -> None:
        """Every improvement has Arabic status label."""
        for imp in self.tracker.get_improvements():
            assert imp.status_ar != "", f"{imp.id} missing status_ar"

    def test_improvement_id_alias(self) -> None:
        """improvement_id property returns same as id."""
        imp = self.tracker.get_improvements()[0]
        assert imp.improvement_id == imp.id

    def test_title_alias(self) -> None:
        """title property returns same as title_en."""
        imp = self.tracker.get_improvements()[0]
        assert imp.title == imp.title_en
