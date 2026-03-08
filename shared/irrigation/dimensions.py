"""
Human-Machine Collaborative (HMC) Irrigation Decision Framework - Dimensions
============================================================================
أبعاد إطار قرار الري التعاوني بين الإنسان والآلة

This module implements the four core dimensions of the HMC framework:

1. Goal Anchoring (ترسيخ الأهداف) - Setting clear objectives and boundaries
2. Experience Injection (حقن الخبرة) - Incorporating local/tacit knowledge
3. Supervision Calibration (معايرة الإشراف) - Testing and validation cycles
4. Value Upgrade (ترقية القيمة) - Continuous learning and improvement

Each dimension provides specific methods for human-AI collaboration in
irrigation decision-making, ensuring that human expertise guides AI
recommendations while AI enhances human capabilities.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Callable
from uuid import UUID, uuid4

import structlog

from .models import (
    CalibrationMethod,
    CalibrationResult,
    ChecklistDimension,
    EcologicalConstraint,
    ExperienceRule,
    ExperienceSource,
    IrrigationGoal,
    IrrigationGoalType,
    IrrigationProgram,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Base Dimension Class - الفئة الأساسية للأبعاد
# =============================================================================


class HMCDimension(ABC):
    """
    Abstract base class for HMC framework dimensions.
    الفئة الأساسية المجردة لأبعاد إطار HMC

    Each dimension encapsulates a specific aspect of human-machine
    collaboration in irrigation decision-making.
    """

    def __init__(self, session_id: UUID | None = None):
        """
        Initialize the dimension.
        تهيئة البُعد

        Args:
            session_id: Associated decision session ID | معرف جلسة القرار المرتبطة
        """
        self._session_id = session_id
        self._is_active = True
        self._last_action_at: datetime | None = None
        self._action_count = 0

    @property
    @abstractmethod
    def dimension_type(self) -> ChecklistDimension:
        """Return the dimension type | إرجاع نوع البُعد"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return dimension name (English) | إرجاع اسم البُعد (إنجليزي)"""
        pass

    @property
    @abstractmethod
    def name_ar(self) -> str:
        """Return dimension name (Arabic) | إرجاع اسم البُعد (عربي)"""
        pass

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """
        Get current status of the dimension.
        الحصول على الحالة الحالية للبُعد

        Returns:
            Dictionary with status information | قاموس بمعلومات الحالة
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset dimension to initial state.
        إعادة تعيين البُعد إلى الحالة الأولية
        """
        pass

    def _record_action(self, action_name: str, details: dict[str, Any] | None = None) -> None:
        """Record an action taken in this dimension."""
        self._last_action_at = datetime.now(UTC)
        self._action_count += 1
        logger.info(
            "hmc_dimension_action",
            dimension=self.dimension_type.value,
            action=action_name,
            session_id=str(self._session_id) if self._session_id else None,
            details=details,
        )


# =============================================================================
# Goal Anchoring Dimension - بُعد ترسيخ الأهداف
# =============================================================================


class GoalAnchoringDimension(HMCDimension):
    """
    Goal Anchoring Dimension - Human defines objectives and boundaries.
    بُعد ترسيخ الأهداف - الإنسان يحدد الأهداف والحدود

    This dimension ensures that:
    1. Primary optimization goals are clearly defined
    2. Ecological boundaries are established
    3. Human-AI responsibilities are clearly divided
    4. Goal alignment is continuously validated

    Key responsibilities of HUMAN (in this dimension):
    - Define primary goal (water saving vs yield vs synergy)
    - Set ecological constraints (salinity limits, water quotas)
    - Specify hard boundaries AI cannot cross
    - Assign tasks to human vs AI

    Key responsibilities of AI (in this dimension):
    - Validate goal feasibility
    - Check constraint consistency
    - Suggest complementary goals
    - Identify potential conflicts

    Example:
        dimension = GoalAnchoringDimension(session_id=session.id)

        # Human sets primary goal
        dimension.set_primary_goal(IrrigationGoal(
            goal_type=IrrigationGoalType.WATER_SAVING,
            target_reduction=0.3
        ))

        # Human sets ecological boundaries
        dimension.set_ecological_boundaries([
            EcologicalConstraint(soil_salinity_limit=4.0)
        ])

        # Define responsibilities
        dimension.define_human_ai_responsibilities(
            human_tasks=["final_approval", "emergency_override"],
            ai_tasks=["schedule_optimization", "volume_calculation"]
        )
    """

    def __init__(self, session_id: UUID | None = None):
        """
        Initialize the Goal Anchoring dimension.
        تهيئة بُعد ترسيخ الأهداف
        """
        super().__init__(session_id)

        # Goals
        self._primary_goal: IrrigationGoal | None = None
        self._secondary_goals: list[IrrigationGoal] = []

        # Constraints
        self._ecological_constraints: list[EcologicalConstraint] = []

        # Responsibilities
        self._human_tasks: list[str] = []
        self._ai_tasks: list[str] = []

        # Validation state
        self._goal_validated = False
        self._constraints_validated = False

    @property
    def dimension_type(self) -> ChecklistDimension:
        return ChecklistDimension.GOAL_ANCHORING

    @property
    def name(self) -> str:
        return "Goal Anchoring"

    @property
    def name_ar(self) -> str:
        return "ترسيخ الأهداف"

    def set_primary_goal(
        self,
        goal: IrrigationGoal,
        validate: bool = True,
    ) -> tuple[bool, list[str]]:
        """
        Set the primary irrigation optimization goal.
        تعيين هدف تحسين الري الرئيسي

        This is the main objective that the AI will optimize for.
        The human defines what success looks like.

        Args:
            goal: Primary irrigation goal | هدف الري الرئيسي
            validate: Whether to validate goal feasibility | التحقق من جدوى الهدف

        Returns:
            Tuple of (success, warnings) | صف من (نجاح، تحذيرات)

        Example:
            success, warnings = dimension.set_primary_goal(
                IrrigationGoal(
                    goal_type=IrrigationGoalType.WATER_SAVING,
                    target_reduction=0.3,
                    priority=1
                )
            )
        """
        warnings: list[str] = []

        # Validate goal if requested
        if validate:
            is_valid, validation_warnings = self._validate_goal(goal)
            warnings.extend(validation_warnings)
            if not is_valid:
                logger.warning(
                    "invalid_primary_goal",
                    goal_type=goal.goal_type.value,
                    warnings=warnings,
                )
                return False, warnings

        # Mark as primary
        goal.is_primary = True
        self._primary_goal = goal
        self._goal_validated = validate

        self._record_action(
            "set_primary_goal",
            {
                "goal_type": goal.goal_type.value,
                "target_value": goal.target_value,
                "target_reduction": goal.target_reduction,
            },
        )

        logger.info(
            "primary_goal_set",
            goal_type=goal.goal_type.value,
            session_id=str(self._session_id) if self._session_id else None,
        )

        return True, warnings

    def add_secondary_goal(
        self,
        goal: IrrigationGoal,
        validate: bool = True,
    ) -> tuple[bool, list[str]]:
        """
        Add a secondary optimization goal.
        إضافة هدف تحسين ثانوي

        Secondary goals are considered after the primary goal.
        They should not conflict with the primary goal.

        Args:
            goal: Secondary goal to add | الهدف الثانوي للإضافة
            validate: Whether to validate | التحقق

        Returns:
            Tuple of (success, warnings) | صف من (نجاح، تحذيرات)
        """
        warnings: list[str] = []

        # Check for conflicts with primary goal
        if self._primary_goal:
            conflicts = self._check_goal_conflicts(self._primary_goal, goal)
            if conflicts:
                warnings.extend(conflicts)
                logger.warning("goal_conflict_detected", conflicts=conflicts)

        if validate:
            is_valid, validation_warnings = self._validate_goal(goal)
            warnings.extend(validation_warnings)
            if not is_valid:
                return False, warnings

        goal.is_primary = False
        self._secondary_goals.append(goal)

        self._record_action("add_secondary_goal", {"goal_type": goal.goal_type.value})
        return True, warnings

    def set_ecological_boundaries(
        self,
        constraints: list[EcologicalConstraint],
        validate: bool = True,
    ) -> tuple[bool, list[str]]:
        """
        Set ecological constraints that AI must respect.
        تعيين القيود البيئية التي يجب أن يحترمها الذكاء الاصطناعي

        These are hard boundaries that cannot be crossed:
        - Maximum soil salinity levels
        - Water quota limitations
        - Carbon emission targets
        - No-irrigation time windows

        Args:
            constraints: List of ecological constraints | قائمة القيود البيئية
            validate: Whether to validate constraints | التحقق من القيود

        Returns:
            Tuple of (success, warnings) | صف من (نجاح، تحذيرات)

        Example:
            success, warnings = dimension.set_ecological_boundaries([
                EcologicalConstraint(
                    soil_salinity_limit=4.0,  # dS/m
                    water_quota_reduction=0.3,
                    no_irrigation_hours=[12, 13, 14]  # Midday
                )
            ])
        """
        warnings: list[str] = []

        if validate:
            for constraint in constraints:
                is_valid, constraint_warnings = self._validate_constraint(constraint)
                warnings.extend(constraint_warnings)
                if not is_valid:
                    return False, warnings

        self._ecological_constraints = constraints
        self._constraints_validated = validate

        self._record_action(
            "set_ecological_boundaries",
            {
                "constraint_count": len(constraints),
            },
        )

        logger.info(
            "ecological_boundaries_set",
            constraint_count=len(constraints),
            session_id=str(self._session_id) if self._session_id else None,
        )

        return True, warnings

    def define_human_ai_responsibilities(
        self,
        human_tasks: list[str],
        ai_tasks: list[str],
    ) -> None:
        """
        Define the division of responsibilities between human and AI.
        تحديد توزيع المسؤوليات بين الإنسان والذكاء الاصطناعي

        Clear responsibility assignment ensures:
        - No critical decisions are made without human oversight
        - AI handles routine calculations and optimization
        - Humans maintain control over sensitive operations

        Args:
            human_tasks: Tasks assigned to human | المهام المسندة للإنسان
            ai_tasks: Tasks assigned to AI | المهام المسندة للذكاء الاصطناعي

        Example:
            dimension.define_human_ai_responsibilities(
                human_tasks=[
                    "goal_definition",
                    "constraint_setting",
                    "final_approval",
                    "emergency_override",
                    "experience_injection"
                ],
                ai_tasks=[
                    "schedule_optimization",
                    "volume_calculation",
                    "weather_integration",
                    "sensor_analysis",
                    "prediction_generation"
                ]
            )
        """
        self._human_tasks = human_tasks
        self._ai_tasks = ai_tasks

        self._record_action(
            "define_responsibilities",
            {
                "human_task_count": len(human_tasks),
                "ai_task_count": len(ai_tasks),
            },
        )

        logger.info(
            "responsibilities_defined",
            human_tasks=human_tasks,
            ai_tasks=ai_tasks,
            session_id=str(self._session_id) if self._session_id else None,
        )

    def validate_goal_alignment(self) -> tuple[bool, list[str]]:
        """
        Validate that all goals and constraints are aligned.
        التحقق من محاذاة جميع الأهداف والقيود

        Checks for:
        - Conflicts between goals
        - Goals that violate constraints
        - Missing required configurations

        Returns:
            Tuple of (is_aligned, issues) | صف من (محاذاة، مشاكل)

        Example:
            is_aligned, issues = dimension.validate_goal_alignment()
            if not is_aligned:
                for issue in issues:
                    print(f"Issue: {issue}")
        """
        issues: list[str] = []

        # Check primary goal exists
        if not self._primary_goal:
            issues.append("Primary goal not set | الهدف الرئيسي غير محدد")

        # Check constraints exist
        if not self._ecological_constraints:
            issues.append("No ecological constraints defined | لم يتم تحديد قيود بيئية")

        # Check goal-constraint compatibility
        if self._primary_goal and self._ecological_constraints:
            for constraint in self._ecological_constraints:
                compatibility_issues = self._check_goal_constraint_compatibility(self._primary_goal, constraint)
                issues.extend(compatibility_issues)

        # Check secondary goals don't conflict with primary
        for secondary in self._secondary_goals:
            if self._primary_goal:
                conflicts = self._check_goal_conflicts(self._primary_goal, secondary)
                issues.extend(conflicts)

        # Check responsibilities defined
        if not self._human_tasks and not self._ai_tasks:
            issues.append("Responsibilities not defined | لم يتم تحديد المسؤوليات")

        is_aligned = len(issues) == 0

        self._record_action(
            "validate_goal_alignment",
            {
                "is_aligned": is_aligned,
                "issue_count": len(issues),
            },
        )

        return is_aligned, issues

    def get_all_goals(self) -> list[IrrigationGoal]:
        """Get all goals (primary + secondary) | الحصول على جميع الأهداف"""
        goals = []
        if self._primary_goal:
            goals.append(self._primary_goal)
        goals.extend(self._secondary_goals)
        return goals

    def get_constraints(self) -> list[EcologicalConstraint]:
        """Get all ecological constraints | الحصول على جميع القيود البيئية"""
        return self._ecological_constraints.copy()

    def get_status(self) -> dict[str, Any]:
        """Get current status of the Goal Anchoring dimension."""
        return {
            "dimension": self.dimension_type.value,
            "name": self.name,
            "name_ar": self.name_ar,
            "has_primary_goal": self._primary_goal is not None,
            "primary_goal_type": self._primary_goal.goal_type.value if self._primary_goal else None,
            "secondary_goal_count": len(self._secondary_goals),
            "constraint_count": len(self._ecological_constraints),
            "human_task_count": len(self._human_tasks),
            "ai_task_count": len(self._ai_tasks),
            "goal_validated": self._goal_validated,
            "constraints_validated": self._constraints_validated,
            "action_count": self._action_count,
            "last_action_at": self._last_action_at.isoformat() if self._last_action_at else None,
        }

    def reset(self) -> None:
        """Reset dimension to initial state."""
        self._primary_goal = None
        self._secondary_goals = []
        self._ecological_constraints = []
        self._human_tasks = []
        self._ai_tasks = []
        self._goal_validated = False
        self._constraints_validated = False
        self._action_count = 0
        self._last_action_at = None

        logger.info(
            "goal_anchoring_dimension_reset",
            session_id=str(self._session_id) if self._session_id else None,
        )

    def _validate_goal(self, goal: IrrigationGoal) -> tuple[bool, list[str]]:
        """Validate a single goal | التحقق من هدف واحد"""
        warnings: list[str] = []

        # Check target values are reasonable
        if goal.goal_type == IrrigationGoalType.WATER_SAVING:
            if goal.target_reduction and goal.target_reduction > 0.5:
                warnings.append(
                    f"Water saving target of {goal.target_reduction:.0%} may be aggressive | "
                    f"هدف توفير المياه {goal.target_reduction:.0%} قد يكون مرتفعاً"
                )

        # Check priority is valid
        if goal.priority < 1 or goal.priority > 10:
            warnings.append("Priority should be between 1 and 10 | الأولوية يجب أن تكون بين 1 و 10")

        return True, warnings

    def _validate_constraint(self, constraint: EcologicalConstraint) -> tuple[bool, list[str]]:
        """Validate a single constraint | التحقق من قيد واحد"""
        warnings: list[str] = []

        # Check salinity limit is reasonable
        if constraint.soil_salinity_limit and constraint.soil_salinity_limit > 8.0:
            warnings.append(
                "Soil salinity limit above 8 dS/m may stress most crops | "
                "حد ملوحة التربة فوق 8 dS/m قد يضغط على معظم المحاصيل"
            )

        # Check water quota is positive
        if constraint.water_quota_m3 and constraint.water_quota_m3 < 100:
            warnings.append(
                "Water quota below 100 m3/ha may be insufficient | حصة المياه أقل من 100 م3/هـ قد تكون غير كافية"
            )

        return True, warnings

    def _check_goal_conflicts(
        self,
        goal1: IrrigationGoal,
        goal2: IrrigationGoal,
    ) -> list[str]:
        """Check for conflicts between two goals | التحقق من التعارضات بين هدفين"""
        conflicts: list[str] = []

        # Water saving and high yield can conflict
        if goal1.goal_type == IrrigationGoalType.WATER_SAVING and goal2.goal_type == IrrigationGoalType.HIGH_YIELD:
            conflicts.append(
                "Water saving and high yield goals may conflict - consider balanced approach | "
                "أهداف توفير المياه والإنتاجية العالية قد تتعارض - فكر في نهج متوازن"
            )

        return conflicts

    def _check_goal_constraint_compatibility(
        self,
        goal: IrrigationGoal,
        constraint: EcologicalConstraint,
    ) -> list[str]:
        """Check goal-constraint compatibility | التحقق من توافق الهدف-القيد"""
        issues: list[str] = []

        # High yield goal with severe water quota
        if (
            goal.goal_type == IrrigationGoalType.HIGH_YIELD
            and constraint.water_quota_reduction
            and constraint.water_quota_reduction > 0.3
        ):
            issues.append(
                "High yield goal may be difficult with >30% water quota reduction | "
                "قد يكون هدف الإنتاجية العالية صعباً مع تخفيض حصة المياه >30%"
            )

        return issues


# =============================================================================
# Experience Injection Dimension - بُعد حقن الخبرة
# =============================================================================


class ExperienceInjectionDimension(HMCDimension):
    """
    Experience Injection Dimension - Human injects local/tacit knowledge.
    بُعد حقن الخبرة - الإنسان يحقن المعرفة المحلية/الضمنية

    This dimension enables farmers to encode their experience:
    1. Local farming rules that work for their specific conditions
    2. Tacit knowledge that isn't in textbooks
    3. Traditional wisdom validated over generations
    4. Learned patterns from past seasons

    Key responsibilities of HUMAN (in this dimension):
    - Provide local experience rules
    - Explain tacit knowledge
    - Validate/reject AI-suggested rules
    - Calibrate reward functions

    Key responsibilities of AI (in this dimension):
    - Translate tacit knowledge into structured rules
    - Suggest patterns from data
    - Identify conflicts between rules
    - Learn from human corrections

    Example:
        dimension = ExperienceInjectionDimension(session_id=session.id)

        # Human injects local experience
        dimension.inject_local_experience([
            ExperienceRule(
                condition="wheat_cold_wave_below_5C",
                action="reduce_irrigation_20%",
                source=ExperienceSource.FARMER,
                rationale="Cold reduces ET and water demand"
            )
        ])

        # Translate tacit knowledge
        rule = dimension.translate_tacit_knowledge(
            "When the leaves curl slightly in the morning, wait one more day before irrigating"
        )
    """

    def __init__(self, session_id: UUID | None = None):
        """
        Initialize the Experience Injection dimension.
        تهيئة بُعد حقن الخبرة
        """
        super().__init__(session_id)

        # Experience rules
        self._experience_rules: list[ExperienceRule] = []

        # Knowledge base
        self._knowledge_base: dict[str, list[ExperienceRule]] = {
            "crop_specific": [],
            "weather_related": [],
            "soil_related": [],
            "seasonal": [],
            "emergency": [],
        }

        # Reward adjustments
        self._reward_adjustments: dict[str, float] = {}

        # Translation history
        self._translation_history: list[dict[str, Any]] = []

    @property
    def dimension_type(self) -> ChecklistDimension:
        return ChecklistDimension.EXPERIENCE_INJECTION

    @property
    def name(self) -> str:
        return "Experience Injection"

    @property
    def name_ar(self) -> str:
        return "حقن الخبرة"

    def inject_local_experience(
        self,
        rules: list[ExperienceRule],
        validate: bool = True,
    ) -> tuple[bool, list[str]]:
        """
        Inject local farming experience rules.
        حقن قواعد الخبرة الزراعية المحلية

        These rules encode farmer knowledge that should guide AI:
        - Crop-specific practices
        - Local climate adaptations
        - Soil-specific adjustments
        - Timing optimizations

        Args:
            rules: List of experience rules to inject | قائمة قواعد الخبرة للحقن
            validate: Whether to validate rules | التحقق من القواعد

        Returns:
            Tuple of (success, warnings) | صف من (نجاح، تحذيرات)

        Example:
            success, warnings = dimension.inject_local_experience([
                ExperienceRule(
                    condition="wheat_tillering_stage",
                    action="increase_irrigation_frequency",
                    source=ExperienceSource.FARMER,
                    rationale="Tillering requires consistent moisture"
                ),
                ExperienceRule(
                    condition="high_wind_speed_above_30kmh",
                    action="delay_irrigation_4h",
                    source=ExperienceSource.RESEARCH,
                    rationale="Reduce evaporation losses"
                )
            ])
        """
        warnings: list[str] = []

        if validate:
            # Check for conflicts among new rules
            for i, rule1 in enumerate(rules):
                for j, rule2 in enumerate(rules[i + 1 :], i + 1):
                    conflicts = self._check_rule_conflicts(rule1, rule2)
                    if conflicts:
                        warnings.extend(conflicts)

            # Check for conflicts with existing rules
            for new_rule in rules:
                for existing_rule in self._experience_rules:
                    conflicts = self._check_rule_conflicts(new_rule, existing_rule)
                    if conflicts:
                        warnings.extend(conflicts)

        # Add rules
        self._experience_rules.extend(rules)

        # Categorize rules
        for rule in rules:
            self._categorize_rule(rule)

        self._record_action(
            "inject_local_experience",
            {
                "rule_count": len(rules),
                "sources": list({r.source.value for r in rules}),
            },
        )

        logger.info(
            "local_experience_injected",
            rule_count=len(rules),
            session_id=str(self._session_id) if self._session_id else None,
        )

        return True, warnings

    def translate_tacit_knowledge(
        self,
        knowledge_text: str,
        source: ExperienceSource = ExperienceSource.FARMER,
        language: str = "en",
    ) -> ExperienceRule:
        """
        Translate tacit knowledge into a structured rule.
        ترجمة المعرفة الضمنية إلى قاعدة منظمة

        Converts natural language descriptions of farming experience
        into structured rules that can be used by the AI.

        Args:
            knowledge_text: Natural language description | الوصف باللغة الطبيعية
            source: Source of the knowledge | مصدر المعرفة
            language: Language of input (en/ar) | لغة الإدخال

        Returns:
            Structured ExperienceRule | قاعدة خبرة منظمة

        Example:
            rule = dimension.translate_tacit_knowledge(
                "When wheat leaves start curling in the morning, "
                "it means the plant is under slight water stress. "
                "Wait one more day before irrigating to encourage "
                "deeper root growth."
            )
        """
        # Parse the knowledge text to extract condition and action
        # This is a simplified implementation - in production, this would use NLP/LLM

        condition, action, rationale = self._parse_tacit_knowledge(knowledge_text)

        rule = ExperienceRule(
            condition=condition,
            action=action,
            source=source,
            rationale=rationale,
            confidence=0.7,  # Lower confidence for auto-translated rules
        )

        if language == "ar":
            rule.condition_ar = condition
            rule.action_ar = action
            rule.rationale_ar = rationale
        else:
            rule.condition_ar = ""
            rule.action_ar = ""
            rule.rationale_ar = ""

        # Record translation
        self._translation_history.append(
            {
                "original_text": knowledge_text,
                "language": language,
                "translated_rule_id": str(rule.id),
                "translated_at": datetime.now(UTC).isoformat(),
            }
        )

        self._record_action(
            "translate_tacit_knowledge",
            {
                "language": language,
                "text_length": len(knowledge_text),
            },
        )

        logger.info(
            "tacit_knowledge_translated",
            rule_id=str(rule.id),
            source=source.value,
        )

        return rule

    def calibrate_reward_function(
        self,
        adjustments: dict[str, float],
    ) -> None:
        """
        Calibrate the AI's reward function based on human preferences.
        معايرة دالة المكافأة للذكاء الاصطناعي بناءً على تفضيلات الإنسان

        Allows farmers to adjust how much weight the AI gives to
        different outcomes when optimizing irrigation.

        Args:
            adjustments: Dictionary of reward adjustments | قاموس تعديلات المكافآت
                - Keys: "water_efficiency", "yield_boost", "cost_reduction",
                        "soil_health", "labor_saving"
                - Values: Multipliers (1.0 = default, >1.0 = more important)

        Example:
            dimension.calibrate_reward_function({
                "water_efficiency": 1.5,  # 50% more important
                "yield_boost": 0.8,       # 20% less important
                "cost_reduction": 1.2,    # 20% more important
                "soil_health": 1.0,       # Default
            })
        """
        # Validate adjustments
        valid_keys = {
            "water_efficiency",
            "yield_boost",
            "cost_reduction",
            "soil_health",
            "labor_saving",
            "timing_flexibility",
            "equipment_wear",
        }

        for key, value in adjustments.items():
            if key not in valid_keys:
                logger.warning(f"Unknown reward key: {key}")
            if value < 0:
                logger.warning(f"Negative reward adjustment for {key}: {value}")

        self._reward_adjustments.update(adjustments)

        self._record_action(
            "calibrate_reward_function",
            {
                "adjustment_count": len(adjustments),
                "adjustments": adjustments,
            },
        )

        logger.info(
            "reward_function_calibrated",
            adjustments=adjustments,
            session_id=str(self._session_id) if self._session_id else None,
        )

    def update_knowledge_base(
        self,
        new_rules: list[ExperienceRule],
        replace_existing: bool = False,
    ) -> int:
        """
        Update the knowledge base with new or improved rules.
        تحديث قاعدة المعرفة بقواعد جديدة أو محسنة

        Args:
            new_rules: Rules to add/update | القواعد للإضافة/التحديث
            replace_existing: Whether to replace existing rules with same ID | استبدال القواعد الموجودة

        Returns:
            Number of rules added/updated | عدد القواعد المضافة/المحدثة
        """
        count = 0

        for new_rule in new_rules:
            if replace_existing:
                # Remove existing rule with same ID
                self._experience_rules = [r for r in self._experience_rules if r.id != new_rule.id]

            # Add new rule
            self._experience_rules.append(new_rule)
            self._categorize_rule(new_rule)
            count += 1

        self._record_action(
            "update_knowledge_base",
            {
                "rule_count": count,
                "replace_existing": replace_existing,
            },
        )

        return count

    def get_rules_for_context(
        self,
        crop_type: str | None = None,
        growth_stage: str | None = None,
        weather_condition: str | None = None,
    ) -> list[ExperienceRule]:
        """
        Get applicable rules for a given context.
        الحصول على القواعد المطبقة لسياق معين

        Args:
            crop_type: Current crop type | نوع المحصول الحالي
            growth_stage: Current growth stage | مرحلة النمو الحالية
            weather_condition: Current weather | الطقس الحالي

        Returns:
            List of applicable rules | قائمة القواعد المطبقة
        """
        applicable = []

        for rule in self._experience_rules:
            if not rule.is_active:
                continue

            # Check crop type filter
            if crop_type and rule.crop_types and crop_type not in rule.crop_types:
                continue

            # Check growth stage filter
            if growth_stage and rule.growth_stages and growth_stage not in rule.growth_stages:
                continue

            applicable.append(rule)

        # Sort by confidence
        applicable.sort(key=lambda r: r.confidence, reverse=True)

        return applicable

    def get_all_rules(self) -> list[ExperienceRule]:
        """Get all experience rules | الحصول على جميع قواعد الخبرة"""
        return self._experience_rules.copy()

    def get_reward_adjustments(self) -> dict[str, float]:
        """Get current reward adjustments | الحصول على تعديلات المكافآت الحالية"""
        return self._reward_adjustments.copy()

    def get_status(self) -> dict[str, Any]:
        """Get current status of the Experience Injection dimension."""
        return {
            "dimension": self.dimension_type.value,
            "name": self.name,
            "name_ar": self.name_ar,
            "total_rules": len(self._experience_rules),
            "rules_by_source": self._count_rules_by_source(),
            "rules_by_category": {k: len(v) for k, v in self._knowledge_base.items()},
            "reward_adjustments": self._reward_adjustments,
            "translation_count": len(self._translation_history),
            "action_count": self._action_count,
            "last_action_at": self._last_action_at.isoformat() if self._last_action_at else None,
        }

    def reset(self) -> None:
        """Reset dimension to initial state."""
        self._experience_rules = []
        self._knowledge_base = {
            "crop_specific": [],
            "weather_related": [],
            "soil_related": [],
            "seasonal": [],
            "emergency": [],
        }
        self._reward_adjustments = {}
        self._translation_history = []
        self._action_count = 0
        self._last_action_at = None

        logger.info(
            "experience_injection_dimension_reset",
            session_id=str(self._session_id) if self._session_id else None,
        )

    def _parse_tacit_knowledge(self, text: str) -> tuple[str, str, str]:
        """
        Parse tacit knowledge text into condition, action, rationale.
        تحليل نص المعرفة الضمنية إلى شرط وإجراء ومبرر

        This is a simplified implementation. In production, this would
        use NLP/LLM for more accurate extraction.
        """
        # Simple keyword-based extraction
        text_lower = text.lower()

        # Extract condition (look for "when", "if")
        condition = ""
        if "when" in text_lower:
            start = text_lower.find("when")
            end = text_lower.find(",", start)
            if end == -1:
                end = text_lower.find(".", start)
            if end == -1:
                end = min(start + 100, len(text))
            condition = text[start:end].strip()
        elif "if" in text_lower:
            start = text_lower.find("if")
            end = text_lower.find(",", start)
            if end == -1:
                end = text_lower.find(".", start)
            if end == -1:
                end = min(start + 100, len(text))
            condition = text[start:end].strip()
        else:
            condition = text[: min(50, len(text))]

        # Extract action (look for imperative verbs)
        action = ""
        action_keywords = ["reduce", "increase", "delay", "advance", "skip", "wait", "apply"]
        for keyword in action_keywords:
            if keyword in text_lower:
                start = text_lower.find(keyword)
                end = text_lower.find(".", start)
                if end == -1:
                    end = min(start + 50, len(text))
                action = text[start:end].strip()
                break

        if not action:
            action = "adjust_irrigation"

        # Rationale is the rest
        rationale = text if len(text) <= 200 else text[:200] + "..."

        return condition, action, rationale

    def _categorize_rule(self, rule: ExperienceRule) -> None:
        """Categorize a rule into the knowledge base."""
        # Categorize by keywords in condition
        condition_lower = rule.condition.lower()

        if any(crop in condition_lower for crop in ["wheat", "barley", "tomato", "palm"]):
            self._knowledge_base["crop_specific"].append(rule)
        elif any(weather in condition_lower for weather in ["rain", "wind", "cold", "heat", "temperature"]):
            self._knowledge_base["weather_related"].append(rule)
        elif any(soil in condition_lower for soil in ["soil", "salinity", "moisture"]):
            self._knowledge_base["soil_related"].append(rule)
        elif any(season in condition_lower for season in ["winter", "summer", "spring", "fall"]):
            self._knowledge_base["seasonal"].append(rule)
        elif any(emergency in condition_lower for emergency in ["emergency", "critical", "urgent"]):
            self._knowledge_base["emergency"].append(rule)

    def _check_rule_conflicts(
        self,
        rule1: ExperienceRule,
        rule2: ExperienceRule,
    ) -> list[str]:
        """Check for conflicts between two rules."""
        conflicts: list[str] = []

        # Simple conflict detection: same condition, different action
        if rule1.condition.lower() == rule2.condition.lower() and rule1.action.lower() != rule2.action.lower():
            conflicts.append(
                f"Conflicting actions for same condition: '{rule1.condition}' -> "
                f"'{rule1.action}' vs '{rule2.action}' | "
                f"إجراءات متعارضة لنفس الشرط: '{rule1.condition}'"
            )

        return conflicts

    def _count_rules_by_source(self) -> dict[str, int]:
        """Count rules by source."""
        counts: dict[str, int] = {}
        for rule in self._experience_rules:
            source_key = rule.source.value
            counts[source_key] = counts.get(source_key, 0) + 1
        return counts


# =============================================================================
# Supervision Calibration Dimension - بُعد معايرة الإشراف
# =============================================================================


class SupervisionCalibrationDimension(HMCDimension):
    """
    Supervision Calibration Dimension - Human supervises and calibrates AI.
    بُعد معايرة الإشراف - الإنسان يشرف ويعاير الذكاء الاصطناعي

    This dimension ensures AI recommendations are:
    1. Tested through simulation before deployment
    2. Validated with small-scale field trials
    3. Equipped with emergency override strategies
    4. Continuously improved through human feedback

    Key responsibilities of HUMAN (in this dimension):
    - Review simulation results
    - Approve field trials
    - Define emergency procedures
    - Provide feedback on outcomes

    Key responsibilities of AI (in this dimension):
    - Run digital twin simulations
    - Compare with control methods
    - Identify potential risks
    - Adapt based on feedback

    Example:
        dimension = SupervisionCalibrationDimension(session_id=session.id)

        # Run simulation verification
        sim_result = dimension.run_simulation_verification(program)

        # Run field trial
        trial_result = dimension.run_field_trial(
            program,
            control_method="farmer_manual"
        )

        # Check emergency strategies
        strategies = dimension.check_emergency_strategies(program)
    """

    def __init__(self, session_id: UUID | None = None):
        """
        Initialize the Supervision Calibration dimension.
        تهيئة بُعد معايرة الإشراف
        """
        super().__init__(session_id)

        # Calibration results
        self._simulation_results: list[CalibrationResult] = []
        self._field_trial_results: list[CalibrationResult] = []

        # Emergency strategies
        self._emergency_strategies: list[dict[str, Any]] = []

        # Human feedback
        self._feedback_history: list[dict[str, Any]] = []

        # Simulation callback (can be set externally)
        self._simulation_callback: Callable[[IrrigationProgram], CalibrationResult] | None = None

    @property
    def dimension_type(self) -> ChecklistDimension:
        return ChecklistDimension.SUPERVISION_CALIBRATION

    @property
    def name(self) -> str:
        return "Supervision Calibration"

    @property
    def name_ar(self) -> str:
        return "معايرة الإشراف"

    def set_simulation_callback(
        self,
        callback: Callable[[IrrigationProgram], CalibrationResult],
    ) -> None:
        """
        Set a custom simulation callback for verification.
        تعيين استدعاء محاكاة مخصص للتحقق

        Args:
            callback: Function that takes a program and returns calibration result
        """
        self._simulation_callback = callback
        logger.info("simulation_callback_set")

    def run_simulation_verification(
        self,
        program: IrrigationProgram,
        simulation_params: dict[str, Any] | None = None,
    ) -> CalibrationResult:
        """
        Run simulation verification of the irrigation program.
        تشغيل التحقق من المحاكاة لبرنامج الري

        Uses a digital twin or model to simulate program execution
        before actual deployment, identifying potential issues.

        Args:
            program: Irrigation program to verify | برنامج الري للتحقق
            simulation_params: Additional simulation parameters | معلمات المحاكاة الإضافية

        Returns:
            CalibrationResult with simulation outcomes | نتيجة المعايرة مع نتائج المحاكاة

        Example:
            result = dimension.run_simulation_verification(program)
            if result.simulation_passed:
                print("Simulation passed!")
            else:
                print(f"Issues: {result.issues_found}")
        """
        # Use custom callback if set
        if self._simulation_callback:
            result = self._simulation_callback(program)
        else:
            # Default simulation (simplified)
            result = self._default_simulation(program, simulation_params or {})

        result.method = CalibrationMethod.SIMULATION
        result.program_id = program.id
        result.session_id = self._session_id

        self._simulation_results.append(result)

        self._record_action(
            "run_simulation_verification",
            {
                "program_id": str(program.id),
                "passed": result.simulation_passed,
                "issues_count": len(result.issues_found),
            },
        )

        logger.info(
            "simulation_verification_completed",
            program_id=str(program.id),
            passed=result.simulation_passed,
            issues=result.issues_found,
        )

        return result

    def run_field_trial(
        self,
        program: IrrigationProgram,
        control_method: str,
        trial_area_hectares: float = 1.0,
        duration_days: int = 7,
    ) -> CalibrationResult:
        """
        Run a small-scale field trial comparing AI vs control method.
        تشغيل تجربة حقلية صغيرة تقارن الذكاء الاصطناعي بطريقة المقارنة

        Deploys the program on a small portion of the field to
        validate predictions before full-scale deployment.

        Args:
            program: Irrigation program to test | برنامج الري للاختبار
            control_method: Comparison method (farmer_manual, previous_ai, standard) | طريقة المقارنة
            trial_area_hectares: Trial area size | حجم منطقة التجربة
            duration_days: Trial duration | مدة التجربة

        Returns:
            CalibrationResult with trial outcomes | نتيجة المعايرة مع نتائج التجربة

        Example:
            result = dimension.run_field_trial(
                program,
                control_method="farmer_manual",
                trial_area_hectares=0.5,
                duration_days=14
            )
        """
        result = CalibrationResult(
            method=CalibrationMethod.FIELD_TRIAL,
            program_id=program.id,
            session_id=self._session_id,
            control_method=control_method,
            test_area_hectares=trial_area_hectares,
            duration_hours=duration_days * 24,
            started_at=datetime.now(UTC),
        )

        # In reality, this would be async and completed after the trial
        # For now, we create a placeholder result

        # Add default recommendations
        result.recommendations = [
            "Monitor soil moisture daily",
            "Compare plant health indicators",
            "Record actual water usage",
        ]
        result.recommendations_ar = [
            "مراقبة رطوبة التربة يومياً",
            "مقارنة مؤشرات صحة النبات",
            "تسجيل استهلاك المياه الفعلي",
        ]

        self._field_trial_results.append(result)

        self._record_action(
            "run_field_trial",
            {
                "program_id": str(program.id),
                "control_method": control_method,
                "trial_area_hectares": trial_area_hectares,
                "duration_days": duration_days,
            },
        )

        logger.info(
            "field_trial_started",
            program_id=str(program.id),
            control_method=control_method,
            trial_area=trial_area_hectares,
        )

        return result

    def check_emergency_strategies(
        self,
        program: IrrigationProgram,
    ) -> list[str]:
        """
        Check and return emergency override strategies for the program.
        التحقق وإرجاع استراتيجيات التجاوز الطارئة للبرنامج

        Ensures that human operators have clear procedures for:
        - Equipment failure
        - Unexpected weather events
        - Crop stress situations
        - System errors

        Args:
            program: Irrigation program to check | برنامج الري للتحقق

        Returns:
            List of emergency strategies | قائمة الاستراتيجيات الطارئة

        Example:
            strategies = dimension.check_emergency_strategies(program)
            for strategy in strategies:
                print(strategy)
        """
        strategies = []

        # Standard emergency strategies
        default_strategies = [
            {
                "trigger": "Equipment failure",
                "trigger_ar": "عطل المعدات",
                "action": "Switch to manual override, notify maintenance",
                "action_ar": "التحويل إلى التجاوز اليدوي، إخطار الصيانة",
                "priority": "high",
            },
            {
                "trigger": "Unexpected heavy rain",
                "trigger_ar": "أمطار غزيرة غير متوقعة",
                "action": "Cancel scheduled irrigation, adjust future schedule",
                "action_ar": "إلغاء الري المجدول، تعديل الجدول المستقبلي",
                "priority": "medium",
            },
            {
                "trigger": "Crop water stress detected",
                "trigger_ar": "اكتشاف إجهاد مائي للمحصول",
                "action": "Trigger emergency irrigation, alert farmer",
                "action_ar": "تفعيل ري طارئ، تنبيه المزارع",
                "priority": "high",
            },
            {
                "trigger": "System communication loss",
                "trigger_ar": "فقدان اتصال النظام",
                "action": "Fall back to pre-programmed schedule, send alert",
                "action_ar": "العودة إلى الجدول المبرمج مسبقاً، إرسال تنبيه",
                "priority": "medium",
            },
            {
                "trigger": "Soil salinity spike",
                "trigger_ar": "ارتفاع مفاجئ في ملوحة التربة",
                "action": "Increase leaching fraction, extend irrigation duration",
                "action_ar": "زيادة نسبة الغسيل، تمديد مدة الري",
                "priority": "high",
            },
        ]

        self._emergency_strategies = default_strategies

        # Format strategies for return
        for strategy in default_strategies:
            strategies.append(
                f"[{strategy['priority'].upper()}] {strategy['trigger']}: {strategy['action']} | "
                f"{strategy['trigger_ar']}: {strategy['action_ar']}"
            )

        self._record_action(
            "check_emergency_strategies",
            {
                "program_id": str(program.id),
                "strategy_count": len(strategies),
            },
        )

        return strategies

    def submit_human_feedback(
        self,
        feedback: str,
        feedback_type: str = "general",
        rating: int | None = None,
        related_program_id: UUID | None = None,
    ) -> None:
        """
        Submit human feedback on AI recommendations.
        تقديم تغذية راجعة بشرية على توصيات الذكاء الاصطناعي

        Feedback is used to improve future recommendations
        and calibrate AI behavior.

        Args:
            feedback: Feedback text | نص التغذية الراجعة
            feedback_type: Type of feedback (general, correction, suggestion) | نوع التغذية الراجعة
            rating: Optional rating 1-5 | تقييم اختياري 1-5
            related_program_id: Program this feedback relates to | البرنامج المرتبط

        Example:
            dimension.submit_human_feedback(
                feedback="The irrigation started too early in the morning",
                feedback_type="correction",
                rating=3,
                related_program_id=program.id
            )
        """
        feedback_entry = {
            "id": str(uuid4()),
            "feedback": feedback,
            "feedback_type": feedback_type,
            "rating": rating,
            "related_program_id": str(related_program_id) if related_program_id else None,
            "submitted_at": datetime.now(UTC).isoformat(),
            "session_id": str(self._session_id) if self._session_id else None,
        }

        self._feedback_history.append(feedback_entry)

        self._record_action(
            "submit_human_feedback",
            {
                "feedback_type": feedback_type,
                "rating": rating,
                "has_related_program": related_program_id is not None,
            },
        )

        logger.info(
            "human_feedback_submitted",
            feedback_type=feedback_type,
            rating=rating,
            session_id=str(self._session_id) if self._session_id else None,
        )

    def complete_field_trial(
        self,
        trial_id: UUID,
        actual_results: dict[str, Any],
    ) -> CalibrationResult | None:
        """
        Complete a field trial with actual results.
        إكمال التجربة الحقلية بالنتائج الفعلية

        Args:
            trial_id: ID of the trial to complete | معرف التجربة للإكمال
            actual_results: Dictionary with actual measured outcomes | قاموس بالنتائج الفعلية

        Returns:
            Updated CalibrationResult or None if not found | نتيجة المعايرة المحدثة
        """
        for result in self._field_trial_results:
            if result.id == trial_id:
                result.completed_at = datetime.now(UTC)
                result.field_test_passed = actual_results.get("success", False)
                result.predicted_water_saving = actual_results.get("water_saving")
                result.predicted_yield_impact = actual_results.get("yield_impact")
                result.improvement_over_control = actual_results.get("improvement_over_control")
                result.raw_data = actual_results

                if actual_results.get("issues"):
                    result.issues_found.extend(actual_results["issues"])

                self._record_action(
                    "complete_field_trial",
                    {
                        "trial_id": str(trial_id),
                        "success": result.field_test_passed,
                    },
                )

                return result

        return None

    def get_all_results(self) -> list[CalibrationResult]:
        """Get all calibration results (simulation + field trial)."""
        return self._simulation_results + self._field_trial_results

    def get_feedback_history(self) -> list[dict[str, Any]]:
        """Get all submitted feedback."""
        return self._feedback_history.copy()

    def get_status(self) -> dict[str, Any]:
        """Get current status of the Supervision Calibration dimension."""
        return {
            "dimension": self.dimension_type.value,
            "name": self.name,
            "name_ar": self.name_ar,
            "simulation_count": len(self._simulation_results),
            "simulations_passed": sum(1 for r in self._simulation_results if r.simulation_passed),
            "field_trial_count": len(self._field_trial_results),
            "trials_passed": sum(1 for r in self._field_trial_results if r.field_test_passed),
            "emergency_strategies_count": len(self._emergency_strategies),
            "feedback_count": len(self._feedback_history),
            "action_count": self._action_count,
            "last_action_at": self._last_action_at.isoformat() if self._last_action_at else None,
        }

    def reset(self) -> None:
        """Reset dimension to initial state."""
        self._simulation_results = []
        self._field_trial_results = []
        self._emergency_strategies = []
        self._feedback_history = []
        self._action_count = 0
        self._last_action_at = None

        logger.info(
            "supervision_calibration_dimension_reset",
            session_id=str(self._session_id) if self._session_id else None,
        )

    def _default_simulation(
        self,
        program: IrrigationProgram,
        params: dict[str, Any],
    ) -> CalibrationResult:
        """Run a default simulation (simplified)."""
        result = CalibrationResult(
            method=CalibrationMethod.SIMULATION,
            simulation_passed=True,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )

        issues: list[str] = []
        issues_ar: list[str] = []

        # Check basic program validity
        if not program.schedules:
            issues.append("No irrigation schedules defined")
            issues_ar.append("لم يتم تحديد جداول ري")
            result.simulation_passed = False

        # Check total water usage is reasonable
        if program.expected_water_usage_m3:
            if program.expected_water_usage_m3 > 10000:
                issues.append("Very high water usage predicted (>10000 m3)")
                issues_ar.append("استخدام مياه مرتفع جداً متوقع (>10000 م3)")

        # Check schedule timing
        for schedule in program.schedules:
            if schedule.duration_minutes > 180:
                issues.append(f"Long irrigation duration in zone {schedule.zone_id}: {schedule.duration_minutes} min")
                issues_ar.append(f"مدة ري طويلة في المنطقة {schedule.zone_id}: {schedule.duration_minutes} دقيقة")

        result.issues_found = issues
        result.issues_found_ar = issues_ar

        # Set predictions (simplified)
        result.predicted_water_saving = 0.15  # Assume 15% saving
        result.predicted_yield_impact = 2.0  # Assume 2% yield improvement

        return result


# =============================================================================
# Value Upgrade Dimension - بُعد ترقية القيمة
# =============================================================================


class ValueUpgradeDimension(HMCDimension):
    """
    Value Upgrade Dimension - Continuous learning and improvement.
    بُعد ترقية القيمة - التعلم والتحسين المستمر

    This dimension focuses on:
    1. Extracting new rules from field observations
    2. Integrating with other farm systems
    3. Exploring new optimization goals
    4. Continuous improvement of AI models

    Key responsibilities of HUMAN (in this dimension):
    - Validate extracted rules
    - Approve system integrations
    - Define new exploration goals
    - Provide outcome feedback

    Key responsibilities of AI (in this dimension):
    - Extract patterns from observations
    - Suggest system integrations
    - Identify improvement opportunities
    - Learn from outcomes

    Example:
        dimension = ValueUpgradeDimension(session_id=session.id)

        # Extract rules from field observations
        new_rules = dimension.extract_field_rules([
            {"observation": "High yield when irrigated at dawn", ...}
        ])

        # Integrate with other systems
        dimension.integrate_with_fertilization_system()

        # Explore carbon reduction goals
        dimension.explore_carbon_reduction_goals()
    """

    def __init__(self, session_id: UUID | None = None):
        """
        Initialize the Value Upgrade dimension.
        تهيئة بُعد ترقية القيمة
        """
        super().__init__(session_id)

        # Extracted rules
        self._extracted_rules: list[ExperienceRule] = []

        # Integrations
        self._active_integrations: list[str] = []
        self._integration_status: dict[str, dict[str, Any]] = {}

        # Exploration goals
        self._exploration_goals: list[dict[str, Any]] = []

        # Learning metrics
        self._learning_metrics: dict[str, Any] = {
            "rules_extracted": 0,
            "rules_validated": 0,
            "integrations_active": 0,
            "exploration_goals_set": 0,
        }

    @property
    def dimension_type(self) -> ChecklistDimension:
        return ChecklistDimension.VALUE_UPGRADE

    @property
    def name(self) -> str:
        return "Value Upgrade"

    @property
    def name_ar(self) -> str:
        return "ترقية القيمة"

    def extract_field_rules(
        self,
        observations: list[dict[str, Any]],
        min_confidence: float = 0.7,
    ) -> list[ExperienceRule]:
        """
        Extract new experience rules from field observations.
        استخراج قواعد خبرة جديدة من الملاحظات الحقلية

        Analyzes patterns in field data to derive rules that
        can improve future irrigation decisions.

        Args:
            observations: List of field observations | قائمة الملاحظات الحقلية
                Each observation should have: observation, condition,
                outcome, confidence, timestamp
            min_confidence: Minimum confidence threshold | الحد الأدنى للثقة

        Returns:
            List of extracted ExperienceRule | قائمة قواعد الخبرة المستخرجة

        Example:
            rules = dimension.extract_field_rules([
                {
                    "observation": "Irrigated at 6 AM, no evaporation loss",
                    "condition": "dawn_irrigation",
                    "outcome": "reduced_water_loss",
                    "confidence": 0.85
                },
                {
                    "observation": "Delayed irrigation during sandstorm",
                    "condition": "high_wind_above_40kmh",
                    "outcome": "reduced_waste",
                    "confidence": 0.9
                }
            ])
        """
        extracted_rules: list[ExperienceRule] = []

        for obs in observations:
            confidence = obs.get("confidence", 0.5)

            if confidence < min_confidence:
                continue

            rule = ExperienceRule(
                condition=obs.get("condition", "unknown_condition"),
                action=self._derive_action_from_outcome(obs.get("outcome", "")),
                source=ExperienceSource.AI_LEARNED,
                rationale=obs.get("observation", ""),
                confidence=confidence,
                metadata={
                    "extracted_from": "field_observation",
                    "extraction_timestamp": datetime.now(UTC).isoformat(),
                    "original_observation": obs,
                },
            )

            extracted_rules.append(rule)
            self._extracted_rules.append(rule)

        self._learning_metrics["rules_extracted"] += len(extracted_rules)

        self._record_action(
            "extract_field_rules",
            {
                "observation_count": len(observations),
                "rules_extracted": len(extracted_rules),
            },
        )

        logger.info(
            "field_rules_extracted",
            observation_count=len(observations),
            rules_extracted=len(extracted_rules),
        )

        return extracted_rules

    def integrate_with_fertilization_system(
        self,
        fertilization_endpoint: str | None = None,
    ) -> bool:
        """
        Integrate irrigation decisions with the fertilization system.
        دمج قرارات الري مع نظام التسميد

        Enables water-fertilizer synergy optimization (fertigation).

        Args:
            fertilization_endpoint: API endpoint for fertilization service | نقطة نهاية خدمة التسميد

        Returns:
            True if integration successful | صحيح إذا نجح الدمج

        Example:
            success = dimension.integrate_with_fertilization_system(
                fertilization_endpoint="http://fertigation-service:8000"
            )
        """
        integration_name = "fertilization_system"

        # Record integration
        self._active_integrations.append(integration_name)
        self._integration_status[integration_name] = {
            "endpoint": fertilization_endpoint,
            "status": "active",
            "connected_at": datetime.now(UTC).isoformat(),
            "features": ["fertigation_scheduling", "nutrient_optimization", "ec_management"],
        }

        self._learning_metrics["integrations_active"] = len(self._active_integrations)

        self._record_action(
            "integrate_with_fertilization_system",
            {
                "endpoint": fertilization_endpoint,
            },
        )

        logger.info(
            "fertilization_system_integrated",
            endpoint=fertilization_endpoint,
            session_id=str(self._session_id) if self._session_id else None,
        )

        return True

    def integrate_with_weather_alerts(
        self,
        weather_endpoint: str | None = None,
    ) -> bool:
        """
        Integrate with weather alert system for proactive adjustments.
        الدمج مع نظام تنبيهات الطقس للتعديلات الاستباقية

        Enables automatic schedule adjustments based on weather forecasts.

        Args:
            weather_endpoint: API endpoint for weather service | نقطة نهاية خدمة الطقس

        Returns:
            True if integration successful | صحيح إذا نجح الدمج

        Example:
            success = dimension.integrate_with_weather_alerts(
                weather_endpoint="http://weather-service:8092"
            )
        """
        integration_name = "weather_alerts"

        self._active_integrations.append(integration_name)
        self._integration_status[integration_name] = {
            "endpoint": weather_endpoint,
            "status": "active",
            "connected_at": datetime.now(UTC).isoformat(),
            "features": [
                "rain_forecast_adjustment",
                "wind_speed_optimization",
                "temperature_adaptation",
                "evapotranspiration_correction",
            ],
        }

        self._learning_metrics["integrations_active"] = len(self._active_integrations)

        self._record_action(
            "integrate_with_weather_alerts",
            {
                "endpoint": weather_endpoint,
            },
        )

        logger.info(
            "weather_alerts_integrated",
            endpoint=weather_endpoint,
            session_id=str(self._session_id) if self._session_id else None,
        )

        return True

    def explore_carbon_reduction_goals(
        self,
        target_reduction_percent: float = 20.0,
    ) -> dict[str, Any]:
        """
        Explore carbon reduction goals for sustainable irrigation.
        استكشاف أهداف تقليل الكربون للري المستدام

        Analyzes opportunities to reduce carbon footprint through:
        - Reduced pumping energy
        - Optimized fertilizer application
        - Improved water efficiency

        Args:
            target_reduction_percent: Target carbon reduction percentage | نسبة تقليل الكربون المستهدفة

        Returns:
            Dictionary with exploration results | قاموس بنتائج الاستكشاف

        Example:
            results = dimension.explore_carbon_reduction_goals(
                target_reduction_percent=25.0
            )
        """
        exploration_result = {
            "goal": "carbon_reduction",
            "target_percent": target_reduction_percent,
            "opportunities": [
                {
                    "category": "pumping_optimization",
                    "category_ar": "تحسين الضخ",
                    "potential_reduction": 8.0,
                    "description": "Shift irrigation to off-peak electricity hours",
                    "description_ar": "نقل الري إلى ساعات الكهرباء غير الذروة",
                },
                {
                    "category": "water_efficiency",
                    "category_ar": "كفاءة المياه",
                    "potential_reduction": 12.0,
                    "description": "Reduce water waste through precision scheduling",
                    "description_ar": "تقليل هدر المياه من خلال الجدولة الدقيقة",
                },
                {
                    "category": "fertigation_optimization",
                    "category_ar": "تحسين التسميد بالري",
                    "potential_reduction": 5.0,
                    "description": "Optimize fertilizer application timing",
                    "description_ar": "تحسين توقيت تطبيق الأسمدة",
                },
            ],
            "total_potential": 25.0,
            "feasibility": "high" if target_reduction_percent <= 25 else "medium",
            "explored_at": datetime.now(UTC).isoformat(),
        }

        self._exploration_goals.append(exploration_result)
        self._learning_metrics["exploration_goals_set"] += 1

        self._record_action(
            "explore_carbon_reduction_goals",
            {
                "target_percent": target_reduction_percent,
                "total_potential": exploration_result["total_potential"],
            },
        )

        logger.info(
            "carbon_reduction_explored",
            target_percent=target_reduction_percent,
            feasibility=exploration_result["feasibility"],
        )

        return exploration_result

    def validate_extracted_rule(
        self,
        rule_id: UUID,
        is_valid: bool,
        validation_notes: str = "",
    ) -> bool:
        """
        Validate an AI-extracted rule through human review.
        التحقق من قاعدة مستخرجة بواسطة الذكاء الاصطناعي من خلال المراجعة البشرية

        Args:
            rule_id: ID of the rule to validate | معرف القاعدة للتحقق
            is_valid: Whether the rule is valid | هل القاعدة صالحة
            validation_notes: Notes from human reviewer | ملاحظات من المراجع البشري

        Returns:
            True if rule found and updated | صحيح إذا وجدت القاعدة وحُدثت
        """
        for rule in self._extracted_rules:
            if rule.id == rule_id:
                rule.is_active = is_valid
                rule.validation_count += 1
                rule.metadata["validation_notes"] = validation_notes
                rule.metadata["validated_at"] = datetime.now(UTC).isoformat()

                if is_valid:
                    self._learning_metrics["rules_validated"] += 1
                    # Increase confidence for validated rules
                    rule.confidence = min(rule.confidence + 0.1, 1.0)

                self._record_action(
                    "validate_extracted_rule",
                    {
                        "rule_id": str(rule_id),
                        "is_valid": is_valid,
                    },
                )

                return True

        return False

    def get_extracted_rules(self, validated_only: bool = False) -> list[ExperienceRule]:
        """Get extracted rules, optionally filtered to validated only."""
        if validated_only:
            return [r for r in self._extracted_rules if r.validation_count > 0 and r.is_active]
        return self._extracted_rules.copy()

    def get_active_integrations(self) -> list[str]:
        """Get list of active integrations."""
        return self._active_integrations.copy()

    def get_integration_status(self, integration_name: str) -> dict[str, Any] | None:
        """Get status of a specific integration."""
        return self._integration_status.get(integration_name)

    def get_exploration_goals(self) -> list[dict[str, Any]]:
        """Get all exploration goals."""
        return self._exploration_goals.copy()

    def get_learning_metrics(self) -> dict[str, Any]:
        """Get learning metrics."""
        return self._learning_metrics.copy()

    def get_status(self) -> dict[str, Any]:
        """Get current status of the Value Upgrade dimension."""
        return {
            "dimension": self.dimension_type.value,
            "name": self.name,
            "name_ar": self.name_ar,
            "extracted_rules_count": len(self._extracted_rules),
            "validated_rules_count": self._learning_metrics["rules_validated"],
            "active_integrations": self._active_integrations,
            "exploration_goals_count": len(self._exploration_goals),
            "learning_metrics": self._learning_metrics,
            "action_count": self._action_count,
            "last_action_at": self._last_action_at.isoformat() if self._last_action_at else None,
        }

    def reset(self) -> None:
        """Reset dimension to initial state."""
        self._extracted_rules = []
        self._active_integrations = []
        self._integration_status = {}
        self._exploration_goals = []
        self._learning_metrics = {
            "rules_extracted": 0,
            "rules_validated": 0,
            "integrations_active": 0,
            "exploration_goals_set": 0,
        }
        self._action_count = 0
        self._last_action_at = None

        logger.info(
            "value_upgrade_dimension_reset",
            session_id=str(self._session_id) if self._session_id else None,
        )

    def _derive_action_from_outcome(self, outcome: str) -> str:
        """Derive an action from an observed outcome."""
        outcome_lower = outcome.lower()

        action_mappings = {
            "reduced_water_loss": "schedule_irrigation_at_dawn",
            "reduced_waste": "delay_irrigation_during_adverse_weather",
            "improved_yield": "maintain_current_practice",
            "crop_stress": "increase_irrigation_frequency",
            "overwatering": "reduce_irrigation_volume",
            "nutrient_deficiency": "integrate_with_fertigation",
        }

        for key, action in action_mappings.items():
            if key in outcome_lower:
                return action

        return f"apply_learned_practice_{outcome[:20]}"
