"""
Human-Machine Collaborative (HMC) Irrigation Decision Framework - Checklist
============================================================================
قائمة التحقق لإطار قرار الري التعاوني بين الإنسان والآلة

This module implements the collaborative checklist that ensures all necessary
steps are completed in the human-machine collaborative irrigation decision
process. The checklist is organized into four dimensions:

1. Goal Anchoring (تأكيد ترسيخ الأهداف)
   - Define primary optimization goal
   - Set ecological constraints
   - Define human-AI responsibilities
   - Validate goal alignment

2. Experience Injection (التحقق من حقن الخبرة)
   - Inject local experience rules
   - Translate tacit knowledge
   - Calibrate reward functions
   - Update knowledge base

3. Supervision Calibration (الإشراف على المعايرة)
   - Run simulation verification
   - Conduct field trial
   - Define emergency procedures
   - Submit human feedback

4. Value Upgrade (تعزيز القيمة)
   - Extract field rules
   - Integrate with other systems
   - Explore new goals
   - Record outcomes

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog

from .models import (
    ChecklistDimension,
    CollaborativeChecklistItem,
    ValidationReport,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Checklist Item Definitions - تعريفات عناصر القائمة
# =============================================================================

# Goal Anchoring checklist items
GOAL_ANCHORING_ITEMS = [
    {
        "id": "define_primary_goal",
        "item": "Define primary optimization goal",
        "item_ar": "تحديد هدف التحسين الرئيسي",
        "is_mandatory": True,
        "order": 1,
    },
    {
        "id": "set_ecological_constraints",
        "item": "Set ecological constraints and boundaries",
        "item_ar": "تحديد القيود والحدود البيئية",
        "is_mandatory": True,
        "order": 2,
    },
    {
        "id": "define_responsibilities",
        "item": "Define human-AI task responsibilities",
        "item_ar": "تحديد مسؤوليات المهام بين الإنسان والذكاء الاصطناعي",
        "is_mandatory": True,
        "order": 3,
    },
    {
        "id": "validate_goal_alignment",
        "item": "Validate goal and constraint alignment",
        "item_ar": "التحقق من محاذاة الأهداف والقيود",
        "is_mandatory": False,
        "order": 4,
    },
]

# Experience Injection checklist items
EXPERIENCE_INJECTION_ITEMS = [
    {
        "id": "inject_experience_rules",
        "item": "Inject local experience rules",
        "item_ar": "حقن قواعد الخبرة المحلية",
        "is_mandatory": False,
        "order": 1,
    },
    {
        "id": "translate_tacit_knowledge",
        "item": "Translate tacit knowledge to structured rules",
        "item_ar": "ترجمة المعرفة الضمنية إلى قواعد منظمة",
        "is_mandatory": False,
        "order": 2,
    },
    {
        "id": "calibrate_rewards",
        "item": "Calibrate AI reward function weights",
        "item_ar": "معايرة أوزان دالة مكافأة الذكاء الاصطناعي",
        "is_mandatory": False,
        "order": 3,
    },
    {
        "id": "update_knowledge_base",
        "item": "Update knowledge base with validated rules",
        "item_ar": "تحديث قاعدة المعرفة بالقواعد المصدقة",
        "is_mandatory": False,
        "order": 4,
    },
]

# Supervision Calibration checklist items
SUPERVISION_CALIBRATION_ITEMS = [
    {
        "id": "ai_generates_program",
        "item": "AI generates irrigation program",
        "item_ar": "الذكاء الاصطناعي ينشئ برنامج الري",
        "is_mandatory": True,
        "order": 1,
    },
    {
        "id": "human_reviews_program",
        "item": "Human reviews AI-generated program",
        "item_ar": "الإنسان يراجع البرنامج المُنشأ بالذكاء الاصطناعي",
        "is_mandatory": True,
        "order": 2,
    },
    {
        "id": "run_simulation",
        "item": "Run simulation verification",
        "item_ar": "تشغيل التحقق من المحاكاة",
        "is_mandatory": True,
        "order": 3,
    },
    {
        "id": "conduct_field_trial",
        "item": "Conduct small-scale field trial",
        "item_ar": "إجراء تجربة حقلية صغيرة",
        "is_mandatory": False,
        "order": 4,
    },
    {
        "id": "define_emergency_procedures",
        "item": "Define emergency override procedures",
        "item_ar": "تحديد إجراءات التجاوز الطارئة",
        "is_mandatory": True,
        "order": 5,
    },
    {
        "id": "submit_feedback",
        "item": "Submit human feedback on program",
        "item_ar": "تقديم التغذية الراجعة البشرية على البرنامج",
        "is_mandatory": False,
        "order": 6,
    },
]

# Value Upgrade checklist items
VALUE_UPGRADE_ITEMS = [
    {
        "id": "human_approves_execution",
        "item": "Human approves program for execution",
        "item_ar": "الإنسان يوافق على البرنامج للتنفيذ",
        "is_mandatory": True,
        "order": 1,
    },
    {
        "id": "extract_field_rules",
        "item": "Extract new rules from field observations",
        "item_ar": "استخراج قواعد جديدة من الملاحظات الحقلية",
        "is_mandatory": False,
        "order": 2,
    },
    {
        "id": "integrate_systems",
        "item": "Integrate with fertilization/weather systems",
        "item_ar": "الدمج مع أنظمة التسميد/الطقس",
        "is_mandatory": False,
        "order": 3,
    },
    {
        "id": "explore_new_goals",
        "item": "Explore new optimization goals (e.g., carbon)",
        "item_ar": "استكشاف أهداف تحسين جديدة (مثل الكربون)",
        "is_mandatory": False,
        "order": 4,
    },
    {
        "id": "record_outcomes",
        "item": "Record actual outcomes for learning",
        "item_ar": "تسجيل النتائج الفعلية للتعلم",
        "is_mandatory": False,
        "order": 5,
    },
]


# =============================================================================
# CollaborativeChecklist Class - فئة القائمة التعاونية
# =============================================================================


class CollaborativeChecklist:
    """
    Collaborative Checklist for HMC Irrigation Decisions.
    القائمة التعاونية لقرارات الري HMC

    Manages the validation checklist that ensures all necessary steps
    are completed in the human-machine collaborative process.

    The checklist is organized into four dimensions corresponding to
    the HMC framework:
    1. Goal Anchoring - Setting clear objectives
    2. Experience Injection - Adding local knowledge
    3. Supervision Calibration - Testing and validation
    4. Value Upgrade - Learning and improvement

    Example:
        checklist = CollaborativeChecklist(session_id=session.id)

        # Check items as they are completed
        checklist.check_item("define_primary_goal", "farmer-123")
        checklist.check_item("set_ecological_constraints", "farmer-123")

        # Validate completion
        report = checklist.validate_all()
        if report.is_complete:
            print("All mandatory items complete!")
        else:
            print(f"Incomplete items: {report.blocking_issues}")
    """

    def __init__(self, session_id: UUID | None = None):
        """
        Initialize the collaborative checklist.
        تهيئة القائمة التعاونية

        Args:
            session_id: Associated decision session ID | معرف جلسة القرار المرتبطة
        """
        self._session_id = session_id
        self._items: dict[str, CollaborativeChecklistItem] = {}

        # Initialize all checklist items
        self._initialize_items()

        logger.info(
            "checklist_initialized",
            session_id=str(session_id) if session_id else None,
            total_items=len(self._items),
        )

    def _initialize_items(self) -> None:
        """Initialize all checklist items from definitions."""
        all_items = [
            (ChecklistDimension.GOAL_ANCHORING, GOAL_ANCHORING_ITEMS),
            (ChecklistDimension.EXPERIENCE_INJECTION, EXPERIENCE_INJECTION_ITEMS),
            (ChecklistDimension.SUPERVISION_CALIBRATION, SUPERVISION_CALIBRATION_ITEMS),
            (ChecklistDimension.VALUE_UPGRADE, VALUE_UPGRADE_ITEMS),
        ]

        for dimension, items in all_items:
            for item_def in items:
                item = CollaborativeChecklistItem(
                    dimension=dimension,
                    item=item_def["item"],
                    item_ar=item_def["item_ar"],
                    is_mandatory=item_def["is_mandatory"],
                    order=item_def["order"],
                )
                self._items[item_def["id"]] = item

    # =========================================================================
    # Item Management - إدارة العناصر
    # =========================================================================

    def check_item(
        self,
        item_id: str,
        checked_by: str,
        notes: str = "",
        notes_ar: str = "",
        evidence: dict[str, Any] | None = None,
    ) -> bool:
        """
        Mark a checklist item as completed.
        تعليم عنصر القائمة كمكتمل

        Args:
            item_id: ID of the item to check | معرف العنصر للتحقق
            checked_by: User who completed the item | المستخدم الذي أكمل العنصر
            notes: Optional notes (English) | ملاحظات اختيارية
            notes_ar: Optional notes (Arabic) | ملاحظات بالعربية
            evidence: Optional evidence/artifacts | دليل/قطع أثرية اختيارية

        Returns:
            True if item was found and checked | صحيح إذا وُجد العنصر وحُقق

        Example:
            checklist.check_item(
                "define_primary_goal",
                "farmer-123",
                notes="Set water saving as primary goal with 30% target"
            )
        """
        if item_id not in self._items:
            logger.warning("checklist_item_not_found", item_id=item_id)
            return False

        item = self._items[item_id]
        item.checked = True
        item.checked_at = datetime.now(UTC)
        item.checked_by = checked_by
        item.notes = notes
        item.notes_ar = notes_ar
        if evidence:
            item.evidence = evidence

        logger.info(
            "checklist_item_checked",
            item_id=item_id,
            dimension=item.dimension.value,
            checked_by=checked_by,
        )

        return True

    def uncheck_item(self, item_id: str) -> bool:
        """
        Mark a checklist item as not completed.
        تعليم عنصر القائمة كغير مكتمل

        Args:
            item_id: ID of the item to uncheck | معرف العنصر لإلغاء التحقق

        Returns:
            True if item was found and unchecked | صحيح إذا وُجد العنصر وأُلغي تحققه
        """
        if item_id not in self._items:
            return False

        item = self._items[item_id]
        item.checked = False
        item.checked_at = None
        item.checked_by = ""
        item.notes = ""
        item.notes_ar = ""
        item.evidence = {}

        logger.info(
            "checklist_item_unchecked",
            item_id=item_id,
            dimension=item.dimension.value,
        )

        return True

    def get_item(self, item_id: str) -> CollaborativeChecklistItem | None:
        """
        Get a specific checklist item.
        الحصول على عنصر قائمة محدد

        Args:
            item_id: ID of the item | معرف العنصر

        Returns:
            ChecklistItem or None | عنصر القائمة أو لا شيء
        """
        return self._items.get(item_id)

    def add_custom_item(
        self,
        item_id: str,
        item: str,
        item_ar: str,
        dimension: ChecklistDimension,
        is_mandatory: bool = False,
        order: int = 99,
    ) -> CollaborativeChecklistItem:
        """
        Add a custom checklist item.
        إضافة عنصر قائمة مخصص

        Args:
            item_id: Unique ID for the item | معرف فريد للعنصر
            item: Item description (English) | وصف العنصر
            item_ar: Item description (Arabic) | وصف العنصر بالعربية
            dimension: Which dimension this belongs to | البُعد الذي ينتمي إليه
            is_mandatory: Whether item is mandatory | هل العنصر إلزامي
            order: Display order | ترتيب العرض

        Returns:
            Created ChecklistItem | عنصر القائمة المُنشأ
        """
        custom_item = CollaborativeChecklistItem(
            dimension=dimension,
            item=item,
            item_ar=item_ar,
            is_mandatory=is_mandatory,
            order=order,
        )

        self._items[item_id] = custom_item

        logger.info(
            "custom_checklist_item_added",
            item_id=item_id,
            dimension=dimension.value,
        )

        return custom_item

    # =========================================================================
    # Retrieval Methods - طرق الاسترجاع
    # =========================================================================

    def get_all_items(self) -> list[CollaborativeChecklistItem]:
        """
        Get all checklist items.
        الحصول على جميع عناصر القائمة

        Returns:
            List of all items sorted by dimension and order | قائمة جميع العناصر مرتبة
        """
        items = list(self._items.values())
        # Sort by dimension and then by order
        dimension_order = {
            ChecklistDimension.GOAL_ANCHORING: 1,
            ChecklistDimension.EXPERIENCE_INJECTION: 2,
            ChecklistDimension.SUPERVISION_CALIBRATION: 3,
            ChecklistDimension.VALUE_UPGRADE: 4,
        }
        items.sort(key=lambda x: (dimension_order[x.dimension], x.order))
        return items

    def get_items_by_dimension(
        self,
        dimension: ChecklistDimension,
    ) -> list[CollaborativeChecklistItem]:
        """
        Get checklist items for a specific dimension.
        الحصول على عناصر القائمة لبُعد محدد

        Args:
            dimension: The dimension to filter by | البُعد للتصفية

        Returns:
            List of items in that dimension | قائمة العناصر في ذلك البُعد
        """
        items = [item for item in self._items.values() if item.dimension == dimension]
        items.sort(key=lambda x: x.order)
        return items

    def get_checked_items(self) -> list[CollaborativeChecklistItem]:
        """
        Get all completed checklist items.
        الحصول على جميع عناصر القائمة المكتملة

        Returns:
            List of checked items | قائمة العناصر المحققة
        """
        return [item for item in self._items.values() if item.checked]

    def get_unchecked_items(self) -> list[CollaborativeChecklistItem]:
        """
        Get all incomplete checklist items.
        الحصول على جميع عناصر القائمة غير المكتملة

        Returns:
            List of unchecked items | قائمة العناصر غير المحققة
        """
        return [item for item in self._items.values() if not item.checked]

    def get_mandatory_items(self) -> list[CollaborativeChecklistItem]:
        """
        Get all mandatory checklist items.
        الحصول على جميع عناصر القائمة الإلزامية

        Returns:
            List of mandatory items | قائمة العناصر الإلزامية
        """
        return [item for item in self._items.values() if item.is_mandatory]

    def get_incomplete_items(self) -> list[CollaborativeChecklistItem]:
        """
        Get incomplete mandatory items (blocking issues).
        الحصول على العناصر الإلزامية غير المكتملة (المشاكل المانعة)

        Returns:
            List of incomplete mandatory items | قائمة العناصر الإلزامية غير المكتملة
        """
        return [item for item in self._items.values() if item.is_mandatory and not item.checked]

    # =========================================================================
    # Validation - التحقق
    # =========================================================================

    def validate_all(self) -> ValidationReport:
        """
        Validate completion of all checklist items.
        التحقق من اكتمال جميع عناصر القائمة

        Generates a comprehensive validation report showing:
        - Overall completion status
        - Completion percentage
        - Blocking issues (incomplete mandatory items)
        - Warnings (optional items not completed)
        - Per-dimension status

        Returns:
            ValidationReport with detailed status | تقرير التحقق مع الحالة التفصيلية

        Example:
            report = checklist.validate_all()
            if report.is_complete:
                print("Ready for approval!")
            else:
                for issue in report.blocking_issues:
                    print(f"Blocking: {issue}")
        """
        total_items = len(self._items)
        checked_items = len(self.get_checked_items())
        incomplete_mandatory = self.get_incomplete_items()

        # Calculate completion percentage
        completion_percentage = (checked_items / total_items * 100) if total_items > 0 else 0.0

        # Check if all mandatory items are complete
        is_complete = len(incomplete_mandatory) == 0

        # Build blocking issues list
        blocking_issues = [item.item for item in incomplete_mandatory]
        blocking_issues_ar = [item.item_ar for item in incomplete_mandatory]

        # Build warnings for optional unchecked items
        optional_unchecked = [item for item in self._items.values() if not item.is_mandatory and not item.checked]
        warnings = [item.item for item in optional_unchecked]
        warnings_ar = [item.item_ar for item in optional_unchecked]

        # Build per-dimension status
        dimension_status = {}
        for dimension in ChecklistDimension:
            dim_items = self.get_items_by_dimension(dimension)
            dim_checked = sum(1 for item in dim_items if item.checked)
            dim_mandatory = sum(1 for item in dim_items if item.is_mandatory)
            dim_mandatory_checked = sum(1 for item in dim_items if item.is_mandatory and item.checked)

            dimension_status[dimension.value] = {
                "total": len(dim_items),
                "checked": dim_checked,
                "mandatory": dim_mandatory,
                "mandatory_checked": dim_mandatory_checked,
                "complete": dim_mandatory == dim_mandatory_checked,
                "completion_percentage": (dim_checked / len(dim_items) * 100) if dim_items else 0.0,
            }

        # Build recommendations
        recommendations = []
        if not is_complete:
            if "define_primary_goal" in [self._get_item_id(item) for item in incomplete_mandatory]:
                recommendations.append("Start by defining your primary irrigation goal")
            if "run_simulation" in [self._get_item_id(item) for item in incomplete_mandatory]:
                recommendations.append("Run simulation to verify the program before approval")
            if "human_approves_execution" in [self._get_item_id(item) for item in incomplete_mandatory]:
                recommendations.append("Human approval required before execution")

        # Determine if ready for execution
        ready_for_execution = is_complete

        report = ValidationReport(
            session_id=self._session_id,
            is_complete=is_complete,
            completion_percentage=completion_percentage,
            dimension_status=dimension_status,
            blocking_issues=blocking_issues,
            blocking_issues_ar=blocking_issues_ar,
            warnings=warnings,
            warnings_ar=warnings_ar,
            recommendations=recommendations,
            ready_for_execution=ready_for_execution,
        )

        logger.info(
            "checklist_validated",
            session_id=str(self._session_id) if self._session_id else None,
            is_complete=is_complete,
            completion_percentage=completion_percentage,
            blocking_count=len(blocking_issues),
        )

        return report

    def validate_dimension(
        self,
        dimension: ChecklistDimension,
    ) -> dict[str, Any]:
        """
        Validate completion of a specific dimension.
        التحقق من اكتمال بُعد محدد

        Args:
            dimension: The dimension to validate | البُعد للتحقق

        Returns:
            Dictionary with dimension validation status | قاموس بحالة تحقق البُعد
        """
        dim_items = self.get_items_by_dimension(dimension)
        checked = sum(1 for item in dim_items if item.checked)
        mandatory = sum(1 for item in dim_items if item.is_mandatory)
        mandatory_checked = sum(1 for item in dim_items if item.is_mandatory and item.checked)

        incomplete_mandatory = [item for item in dim_items if item.is_mandatory and not item.checked]

        return {
            "dimension": dimension.value,
            "total_items": len(dim_items),
            "checked_items": checked,
            "mandatory_items": mandatory,
            "mandatory_checked": mandatory_checked,
            "is_complete": mandatory == mandatory_checked,
            "completion_percentage": (checked / len(dim_items) * 100) if dim_items else 0.0,
            "incomplete_mandatory": [{"item": item.item, "item_ar": item.item_ar} for item in incomplete_mandatory],
        }

    # =========================================================================
    # Display and Export - العرض والتصدير
    # =========================================================================

    def to_display_format(self, language: str = "both") -> str:
        """
        Format checklist for display.
        تنسيق القائمة للعرض

        Args:
            language: Display language (en, ar, both) | لغة العرض

        Returns:
            Formatted string for display | سلسلة منسقة للعرض
        """
        output = []

        dimension_names = {
            ChecklistDimension.GOAL_ANCHORING: ("Goal Anchoring", "ترسيخ الأهداف"),
            ChecklistDimension.EXPERIENCE_INJECTION: ("Experience Injection", "حقن الخبرة"),
            ChecklistDimension.SUPERVISION_CALIBRATION: (
                "Supervision Calibration",
                "معايرة الإشراف",
            ),
            ChecklistDimension.VALUE_UPGRADE: ("Value Upgrade", "ترقية القيمة"),
        }

        for dimension in ChecklistDimension:
            en_name, ar_name = dimension_names[dimension]

            if language == "en":
                output.append(f"\n## {en_name}")
            elif language == "ar":
                output.append(f"\n## {ar_name}")
            else:
                output.append(f"\n## {en_name} | {ar_name}")

            items = self.get_items_by_dimension(dimension)
            for item in items:
                checkbox = "[x]" if item.checked else "[ ]"
                mandatory = "*" if item.is_mandatory else ""

                if language == "en":
                    output.append(f"  {checkbox} {item.item}{mandatory}")
                elif language == "ar":
                    output.append(f"  {checkbox} {item.item_ar}{mandatory}")
                else:
                    output.append(f"  {checkbox} {item.item} | {item.item_ar}{mandatory}")

                if item.notes:
                    output.append(f"      Notes: {item.notes}")

        return "\n".join(output)

    def to_dict(self) -> dict[str, Any]:
        """
        Export checklist to dictionary format.
        تصدير القائمة إلى تنسيق القاموس

        Returns:
            Dictionary with checklist data | قاموس ببيانات القائمة
        """
        return {
            "session_id": str(self._session_id) if self._session_id else None,
            "dimensions": {
                dimension.value: {
                    "items": [
                        {
                            "id": self._get_item_id(item),
                            "item": item.item,
                            "item_ar": item.item_ar,
                            "checked": item.checked,
                            "checked_by": item.checked_by,
                            "checked_at": item.checked_at.isoformat() if item.checked_at else None,
                            "is_mandatory": item.is_mandatory,
                            "notes": item.notes,
                            "notes_ar": item.notes_ar,
                        }
                        for item in self.get_items_by_dimension(dimension)
                    ],
                    "validation": self.validate_dimension(dimension),
                }
                for dimension in ChecklistDimension
            },
            "overall_validation": self.validate_all().model_dump(),
        }

    # =========================================================================
    # Statistics - الإحصائيات
    # =========================================================================

    def get_statistics(self) -> dict[str, Any]:
        """
        Get checklist statistics.
        الحصول على إحصائيات القائمة

        Returns:
            Dictionary with checklist statistics | قاموس بإحصائيات القائمة
        """
        total = len(self._items)
        checked = len(self.get_checked_items())
        mandatory = len(self.get_mandatory_items())
        mandatory_checked = mandatory - len(self.get_incomplete_items())

        return {
            "total_items": total,
            "checked_items": checked,
            "unchecked_items": total - checked,
            "mandatory_items": mandatory,
            "mandatory_checked": mandatory_checked,
            "mandatory_unchecked": mandatory - mandatory_checked,
            "optional_items": total - mandatory,
            "completion_percentage": (checked / total * 100) if total > 0 else 0.0,
            "mandatory_completion_percentage": (mandatory_checked / mandatory * 100) if mandatory > 0 else 0.0,
            "by_dimension": {dimension.value: self.validate_dimension(dimension) for dimension in ChecklistDimension},
        }

    # =========================================================================
    # Reset - إعادة التعيين
    # =========================================================================

    def reset(self) -> None:
        """
        Reset all checklist items to unchecked.
        إعادة تعيين جميع عناصر القائمة إلى غير محقق
        """
        for item in self._items.values():
            item.checked = False
            item.checked_at = None
            item.checked_by = ""
            item.notes = ""
            item.notes_ar = ""
            item.evidence = {}

        logger.info(
            "checklist_reset",
            session_id=str(self._session_id) if self._session_id else None,
        )

    def reset_dimension(self, dimension: ChecklistDimension) -> None:
        """
        Reset all items in a specific dimension.
        إعادة تعيين جميع العناصر في بُعد محدد

        Args:
            dimension: The dimension to reset | البُعد لإعادة التعيين
        """
        for item in self.get_items_by_dimension(dimension):
            item.checked = False
            item.checked_at = None
            item.checked_by = ""
            item.notes = ""
            item.notes_ar = ""
            item.evidence = {}

        logger.info(
            "checklist_dimension_reset",
            dimension=dimension.value,
            session_id=str(self._session_id) if self._session_id else None,
        )

    # =========================================================================
    # Helper Methods - طرق مساعدة
    # =========================================================================

    def _get_item_id(self, item: CollaborativeChecklistItem) -> str:
        """Get the ID of an item from the items dictionary."""
        for item_id, stored_item in self._items.items():
            if stored_item.id == item.id:
                return item_id
        return str(item.id)


# =============================================================================
# Factory Function - دالة المصنع
# =============================================================================


def create_checklist(session_id: UUID | None = None) -> CollaborativeChecklist:
    """
    Factory function to create a CollaborativeChecklist.
    دالة مصنع لإنشاء قائمة تعاونية

    Args:
        session_id: Associated session ID | معرف الجلسة المرتبطة

    Returns:
        Initialized CollaborativeChecklist | قائمة تعاونية مُهيأة

    Example:
        checklist = create_checklist(session_id=uuid4())
    """
    return CollaborativeChecklist(session_id=session_id)


# Alias for convenience
get_checklist = create_checklist
