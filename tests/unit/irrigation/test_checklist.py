"""
SAHOOL HMC Irrigation Decision Framework - Checklist Tests
اختبارات قائمة التحقق لإطار قرارات الري التعاوني

Tests the validation checklist:
- Goal anchoring checklist items
- Experience injection checklist items
- Supervision checklist items
- Value upgrade checklist items
- Validation of complete/incomplete checklists
- Getting incomplete items
- Arabic labels and bilingual support
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Checklist Class for Testing
# ═══════════════════════════════════════════════════════════════════════════════


class HMCChecklist:
    """
    HMC Validation Checklist
    قائمة التحقق من التعاون بين الإنسان والآلة
    """

    # Standard checklist items by category
    CHECKLIST_ITEMS = {
        "goal_anchoring": [
            {
                "order": 1,
                "title_en": "Water savings goal defined",
                "title_ar": "تم تحديد هدف توفير المياه",
                "description_en": "Target water savings percentage has been specified",
                "description_ar": "تم تحديد النسبة المستهدفة لتوفير المياه",
                "is_required": True,
            },
            {
                "order": 2,
                "title_en": "Yield threshold defined",
                "title_ar": "تم تحديد عتبة الإنتاج",
                "description_en": "Minimum acceptable yield threshold has been set",
                "description_ar": "تم تحديد الحد الأدنى المقبول للإنتاج",
                "is_required": True,
            },
            {
                "order": 3,
                "title_en": "Ecological constraints reviewed",
                "title_ar": "تمت مراجعة القيود البيئية",
                "description_en": "All applicable ecological constraints have been reviewed",
                "description_ar": "تمت مراجعة جميع القيود البيئية المطبقة",
                "is_required": True,
            },
            {
                "order": 4,
                "title_en": "Responsibilities defined",
                "title_ar": "تم تحديد المسؤوليات",
                "description_en": "Human and AI responsibilities have been clearly defined",
                "description_ar": "تم تحديد مسؤوليات الإنسان والذكاء الاصطناعي بوضوح",
                "is_required": False,
            },
        ],
        "experience_injection": [
            {
                "order": 5,
                "title_en": "Farmer experience documented",
                "title_ar": "تم توثيق خبرة المزارع",
                "description_en": "Relevant farmer experience has been captured",
                "description_ar": "تم تسجيل خبرة المزارع ذات الصلة",
                "is_required": False,
            },
            {
                "order": 6,
                "title_en": "Historical rules reviewed",
                "title_ar": "تمت مراجعة القواعد التاريخية",
                "description_en": "Historical irrigation rules have been reviewed",
                "description_ar": "تمت مراجعة قواعد الري التاريخية",
                "is_required": True,
            },
            {
                "order": 7,
                "title_en": "Reward function calibrated",
                "title_ar": "تمت معايرة دالة المكافأة",
                "description_en": "AI reward function has been calibrated to farmer preferences",
                "description_ar": "تمت معايرة دالة مكافأة الذكاء الاصطناعي وفقاً لتفضيلات المزارع",
                "is_required": True,
            },
        ],
        "supervision": [
            {
                "order": 8,
                "title_en": "Simulation verification passed",
                "title_ar": "اجتاز التحقق بالمحاكاة",
                "description_en": "Program has been verified through simulation",
                "description_ar": "تم التحقق من البرنامج من خلال المحاكاة",
                "is_required": True,
            },
            {
                "order": 9,
                "title_en": "Emergency strategy defined",
                "title_ar": "تم تحديد استراتيجية الطوارئ",
                "description_en": "Emergency fallback strategy has been defined",
                "description_ar": "تم تحديد استراتيجية الطوارئ الاحتياطية",
                "is_required": True,
            },
            {
                "order": 10,
                "title_en": "Sensor failure plan reviewed",
                "title_ar": "تمت مراجعة خطة فشل المستشعر",
                "description_en": "Plan for handling sensor failures has been reviewed",
                "description_ar": "تمت مراجعة خطة التعامل مع فشل المستشعرات",
                "is_required": True,
            },
        ],
        "value_upgrade": [
            {
                "order": 11,
                "title_en": "Weather integration configured",
                "title_ar": "تم تكوين تكامل الطقس",
                "description_en": "Weather forecast integration is configured",
                "description_ar": "تم تكوين تكامل توقعات الطقس",
                "is_required": True,
            },
            {
                "order": 12,
                "title_en": "Fertilization sync reviewed",
                "title_ar": "تمت مراجعة مزامنة التسميد",
                "description_en": "Fertilization schedule synchronization reviewed",
                "description_ar": "تمت مراجعة مزامنة جدول التسميد",
                "is_required": False,
            },
            {
                "order": 13,
                "title_en": "Carbon impact calculated",
                "title_ar": "تم حساب أثر الكربون",
                "description_en": "Carbon reduction impact has been calculated",
                "description_ar": "تم حساب تأثير تقليل الكربون",
                "is_required": False,
            },
        ],
    }

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.items: list[dict[str, Any]] = []
        self._initialize_items()

    def _initialize_items(self):
        """Initialize checklist items for session"""
        for category, items in self.CHECKLIST_ITEMS.items():
            for item in items:
                self.items.append(
                    {
                        "item_id": str(uuid.uuid4()),
                        "session_id": self.session_id,
                        "category": category,
                        "order": item["order"],
                        "title_en": item["title_en"],
                        "title_ar": item["title_ar"],
                        "description_en": item.get("description_en"),
                        "description_ar": item.get("description_ar"),
                        "is_required": item["is_required"],
                        "is_completed": False,
                        "completed_at": None,
                        "completed_by": None,
                        "validation_data": None,
                    }
                )

    def get_items_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get checklist items by category"""
        return [item for item in self.items if item["category"] == category]

    def complete_item(
        self,
        item_id: str,
        completed_by: str,
        validation_data: dict[str, Any] | None = None,
    ) -> bool:
        """Mark an item as completed"""
        for item in self.items:
            if item["item_id"] == item_id:
                item["is_completed"] = True
                item["completed_at"] = datetime.now(UTC).isoformat()
                item["completed_by"] = completed_by
                item["validation_data"] = validation_data
                return True
        return False

    def is_complete(self) -> bool:
        """Check if all required items are completed"""
        required_items = [item for item in self.items if item["is_required"]]
        return all(item["is_completed"] for item in required_items)

    def get_incomplete_items(self, required_only: bool = True) -> list[dict[str, Any]]:
        """Get list of incomplete items"""
        if required_only:
            return [item for item in self.items if item["is_required"] and not item["is_completed"]]
        return [item for item in self.items if not item["is_completed"]]

    def get_completion_status(self) -> dict[str, Any]:
        """Get overall completion status"""
        total = len(self.items)
        completed = len([item for item in self.items if item["is_completed"]])
        required_total = len([item for item in self.items if item["is_required"]])
        required_completed = len([item for item in self.items if item["is_required"] and item["is_completed"]])

        return {
            "total_items": total,
            "completed_items": completed,
            "completion_percent": (completed / total * 100) if total > 0 else 0,
            "required_items": required_total,
            "required_completed": required_completed,
            "required_completion_percent": ((required_completed / required_total * 100) if required_total > 0 else 0),
            "is_complete": self.is_complete(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Goal Anchoring Checklist Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestGoalAnchoringChecklistItems:
    """
    Test Goal Anchoring Checklist Items
    اختبار عناصر قائمة تحقق تثبيت الهدف
    """

    def test_goal_anchoring_items_exist(self):
        """Test that goal anchoring items are defined"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("goal_anchoring")

        assert len(items) > 0
        assert len(items) == 4

    def test_goal_anchoring_has_water_savings_item(self):
        """Test goal anchoring includes water savings goal item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("goal_anchoring")

        water_savings_items = [item for item in items if "water savings" in item["title_en"].lower()]
        assert len(water_savings_items) == 1
        assert water_savings_items[0]["is_required"] is True

    def test_goal_anchoring_has_yield_threshold_item(self):
        """Test goal anchoring includes yield threshold item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("goal_anchoring")

        yield_items = [item for item in items if "yield threshold" in item["title_en"].lower()]
        assert len(yield_items) == 1
        assert yield_items[0]["is_required"] is True

    def test_goal_anchoring_has_ecological_constraints_item(self):
        """Test goal anchoring includes ecological constraints item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("goal_anchoring")

        ecological_items = [item for item in items if "ecological" in item["title_en"].lower()]
        assert len(ecological_items) == 1

    def test_goal_anchoring_items_have_arabic_titles(self):
        """Test all goal anchoring items have Arabic titles"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("goal_anchoring")

        for item in items:
            assert item["title_ar"] is not None
            assert len(item["title_ar"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Experience Injection Checklist Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestExperienceInjectionChecklistItems:
    """
    Test Experience Injection Checklist Items
    اختبار عناصر قائمة تحقق حقن الخبرة
    """

    def test_experience_injection_items_exist(self):
        """Test that experience injection items are defined"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("experience_injection")

        assert len(items) > 0
        assert len(items) == 3

    def test_experience_injection_has_farmer_experience_item(self):
        """Test experience injection includes farmer experience item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("experience_injection")

        farmer_exp_items = [item for item in items if "farmer experience" in item["title_en"].lower()]
        assert len(farmer_exp_items) == 1

    def test_experience_injection_has_reward_calibration_item(self):
        """Test experience injection includes reward function calibration item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("experience_injection")

        reward_items = [item for item in items if "reward" in item["title_en"].lower()]
        assert len(reward_items) == 1
        assert reward_items[0]["is_required"] is True

    def test_experience_injection_items_have_descriptions(self):
        """Test all experience injection items have descriptions"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("experience_injection")

        for item in items:
            assert item["description_en"] is not None
            assert item["description_ar"] is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Supervision Checklist Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSupervisionChecklistItems:
    """
    Test Supervision Checklist Items
    اختبار عناصر قائمة تحقق الإشراف
    """

    def test_supervision_items_exist(self):
        """Test that supervision items are defined"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("supervision")

        assert len(items) > 0
        assert len(items) == 3

    def test_supervision_has_simulation_item(self):
        """Test supervision includes simulation verification item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("supervision")

        simulation_items = [item for item in items if "simulation" in item["title_en"].lower()]
        assert len(simulation_items) == 1
        assert simulation_items[0]["is_required"] is True

    def test_supervision_has_emergency_strategy_item(self):
        """Test supervision includes emergency strategy item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("supervision")

        emergency_items = [item for item in items if "emergency" in item["title_en"].lower()]
        assert len(emergency_items) == 1
        assert emergency_items[0]["is_required"] is True

    def test_supervision_has_sensor_failure_item(self):
        """Test supervision includes sensor failure plan item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("supervision")

        sensor_items = [item for item in items if "sensor" in item["title_en"].lower()]
        assert len(sensor_items) == 1

    def test_all_supervision_items_are_required(self):
        """Test that all supervision items are required"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("supervision")

        for item in items:
            assert item["is_required"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# Value Upgrade Checklist Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestValueUpgradeChecklistItems:
    """
    Test Value Upgrade Checklist Items
    اختبار عناصر قائمة تحقق ترقية القيمة
    """

    def test_value_upgrade_items_exist(self):
        """Test that value upgrade items are defined"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("value_upgrade")

        assert len(items) > 0
        assert len(items) == 3

    def test_value_upgrade_has_weather_integration_item(self):
        """Test value upgrade includes weather integration item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("value_upgrade")

        weather_items = [item for item in items if "weather" in item["title_en"].lower()]
        assert len(weather_items) == 1
        assert weather_items[0]["is_required"] is True

    def test_value_upgrade_has_fertilization_sync_item(self):
        """Test value upgrade includes fertilization sync item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("value_upgrade")

        fert_items = [item for item in items if "fertilization" in item["title_en"].lower()]
        assert len(fert_items) == 1

    def test_value_upgrade_has_carbon_impact_item(self):
        """Test value upgrade includes carbon impact item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        items = checklist.get_items_by_category("value_upgrade")

        carbon_items = [item for item in items if "carbon" in item["title_en"].lower()]
        assert len(carbon_items) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Checklist Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestChecklistValidation:
    """
    Test Checklist Validation
    اختبار التحقق من قائمة التحقق
    """

    def test_validate_all_complete(self):
        """Test validation when all required items are complete"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        # Complete all required items
        for item in checklist.items:
            if item["is_required"]:
                checklist.complete_item(
                    item_id=item["item_id"],
                    completed_by=user_id,
                )

        assert checklist.is_complete() is True

    def test_validate_all_incomplete(self):
        """Test validation when no items are complete"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))

        # No items completed
        assert checklist.is_complete() is False

    def test_validate_partial_completion(self):
        """Test validation with partial completion"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        # Complete only first required item
        required_items = [item for item in checklist.items if item["is_required"]]
        if required_items:
            checklist.complete_item(
                item_id=required_items[0]["item_id"],
                completed_by=user_id,
            )

        assert checklist.is_complete() is False

    def test_validate_optional_items_not_required(self):
        """Test that optional items don't affect validation"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        # Complete only required items
        for item in checklist.items:
            if item["is_required"]:
                checklist.complete_item(
                    item_id=item["item_id"],
                    completed_by=user_id,
                )

        # Should be complete even though optional items are not done
        assert checklist.is_complete() is True

        # Verify there are incomplete optional items
        incomplete = checklist.get_incomplete_items(required_only=False)
        optional_incomplete = [item for item in incomplete if not item["is_required"]]
        assert len(optional_incomplete) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Get Incomplete Items Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetIncompleteItems:
    """
    Test Getting Incomplete Items
    اختبار الحصول على العناصر غير المكتملة
    """

    def test_get_incomplete_items_all(self):
        """Test getting all incomplete items when none complete"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))

        incomplete = checklist.get_incomplete_items(required_only=False)
        assert len(incomplete) == len(checklist.items)

    def test_get_incomplete_items_required_only(self):
        """Test getting only required incomplete items"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))

        required_count = len([item for item in checklist.items if item["is_required"]])

        incomplete = checklist.get_incomplete_items(required_only=True)
        assert len(incomplete) == required_count

    def test_get_incomplete_items_after_partial_completion(self):
        """Test getting incomplete items after some are completed"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        # Complete first two required items
        required_items = [item for item in checklist.items if item["is_required"]]
        for item in required_items[:2]:
            checklist.complete_item(item_id=item["item_id"], completed_by=user_id)

        incomplete = checklist.get_incomplete_items(required_only=True)
        assert len(incomplete) == len(required_items) - 2

    def test_get_incomplete_items_empty_when_all_complete(self):
        """Test getting incomplete items when all required are complete"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        # Complete all required items
        for item in checklist.items:
            if item["is_required"]:
                checklist.complete_item(item_id=item["item_id"], completed_by=user_id)

        incomplete = checklist.get_incomplete_items(required_only=True)
        assert len(incomplete) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Arabic Labels Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestArabicLabels:
    """
    Test Arabic Labels in Checklist
    اختبار التسميات العربية في قائمة التحقق
    """

    def test_all_items_have_arabic_titles(self):
        """Test all items have Arabic titles"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))

        for item in checklist.items:
            assert item["title_ar"] is not None
            assert len(item["title_ar"]) > 0
            # Verify it contains Arabic characters
            assert any("\u0600" <= char <= "\u06ff" for char in item["title_ar"])

    def test_all_items_have_arabic_descriptions(self):
        """Test all items have Arabic descriptions"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))

        for item in checklist.items:
            if item["description_ar"] is not None:
                assert len(item["description_ar"]) > 0
                # Verify it contains Arabic characters
                assert any("\u0600" <= char <= "\u06ff" for char in item["description_ar"])

    def test_arabic_title_not_same_as_english(self):
        """Test Arabic titles are different from English"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))

        for item in checklist.items:
            assert item["title_ar"] != item["title_en"]

    def test_specific_arabic_translations(self):
        """Test specific Arabic translations are correct"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))

        # Check water savings goal translation
        water_items = [item for item in checklist.items if "water savings" in item["title_en"].lower()]
        assert len(water_items) > 0
        # Should contain "مياه" (water) in Arabic
        assert "مياه" in water_items[0]["title_ar"]

        # Check simulation translation
        sim_items = [item for item in checklist.items if "simulation" in item["title_en"].lower()]
        assert len(sim_items) > 0
        # Should contain "محاكاة" (simulation) in Arabic
        assert "محاكاة" in sim_items[0]["title_ar"]


# ═══════════════════════════════════════════════════════════════════════════════
# Completion Status Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompletionStatus:
    """
    Test Completion Status Reporting
    اختبار الإبلاغ عن حالة الإكمال
    """

    def test_completion_status_initial(self):
        """Test initial completion status"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))

        status = checklist.get_completion_status()

        assert status["total_items"] == len(checklist.items)
        assert status["completed_items"] == 0
        assert status["completion_percent"] == 0
        assert status["is_complete"] is False

    def test_completion_status_after_partial(self):
        """Test completion status after partial completion"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        # Complete half of items
        half = len(checklist.items) // 2
        for i, item in enumerate(checklist.items):
            if i < half:
                checklist.complete_item(item_id=item["item_id"], completed_by=user_id)

        status = checklist.get_completion_status()

        assert status["completed_items"] == half
        assert 0 < status["completion_percent"] < 100

    def test_completion_status_full(self):
        """Test completion status when fully complete"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        # Complete all items
        for item in checklist.items:
            checklist.complete_item(item_id=item["item_id"], completed_by=user_id)

        status = checklist.get_completion_status()

        assert status["completed_items"] == status["total_items"]
        assert status["completion_percent"] == 100
        assert status["is_complete"] is True

    def test_completion_status_required_vs_total(self):
        """Test completion status distinguishes required from optional"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        # Complete only required items
        for item in checklist.items:
            if item["is_required"]:
                checklist.complete_item(item_id=item["item_id"], completed_by=user_id)

        status = checklist.get_completion_status()

        assert status["required_completion_percent"] == 100
        assert status["completion_percent"] < 100  # Optional not complete
        assert status["is_complete"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# Item Completion Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestItemCompletion:
    """
    Test Individual Item Completion
    اختبار إكمال العناصر الفردية
    """

    def test_complete_item_success(self):
        """Test successfully completing an item"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())
        item_id = checklist.items[0]["item_id"]

        result = checklist.complete_item(
            item_id=item_id,
            completed_by=user_id,
        )

        assert result is True

    def test_complete_item_sets_timestamp(self):
        """Test completing item sets completion timestamp"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())
        item_id = checklist.items[0]["item_id"]

        checklist.complete_item(item_id=item_id, completed_by=user_id)

        item = next(i for i in checklist.items if i["item_id"] == item_id)
        assert item["completed_at"] is not None

    def test_complete_item_sets_user(self):
        """Test completing item sets completing user"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())
        item_id = checklist.items[0]["item_id"]

        checklist.complete_item(item_id=item_id, completed_by=user_id)

        item = next(i for i in checklist.items if i["item_id"] == item_id)
        assert item["completed_by"] == user_id

    def test_complete_item_with_validation_data(self):
        """Test completing item with validation data"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())
        item_id = checklist.items[0]["item_id"]

        validation_data = {
            "target_percent": 25.0,
            "validated_by": "simulation",
            "validation_score": 0.92,
        }

        checklist.complete_item(
            item_id=item_id,
            completed_by=user_id,
            validation_data=validation_data,
        )

        item = next(i for i in checklist.items if i["item_id"] == item_id)
        assert item["validation_data"] == validation_data

    def test_complete_nonexistent_item(self):
        """Test completing a non-existent item returns False"""
        checklist = HMCChecklist(session_id=str(uuid.uuid4()))
        user_id = str(uuid.uuid4())

        result = checklist.complete_item(
            item_id="nonexistent-id",
            completed_by=user_id,
        )

        assert result is False
