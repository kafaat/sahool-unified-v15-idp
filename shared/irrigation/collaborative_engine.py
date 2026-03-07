"""
Human-Machine Collaborative (HMC) Irrigation Decision Framework - Engine
=========================================================================
محرك إطار قرار الري التعاوني بين الإنسان والآلة

This module implements the main HMCIrrigationEngine class that orchestrates
the collaborative decision-making process between farmers and AI for
irrigation management.

The engine manages the complete lifecycle of an irrigation decision:
1. Session initialization
2. Goal setting by human
3. Program generation by AI
4. Human review and experience injection
5. Calibration and testing
6. Approval and execution
7. Outcome recording and learning

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Callable
from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

import structlog

from .checklist import CollaborativeChecklist
from .dimensions import (
    ExperienceInjectionDimension,
    GoalAnchoringDimension,
    SupervisionCalibrationDimension,
    ValueUpgradeDimension,
)
from .models import (
    CalibrationMethod,
    CalibrationResult,
    DecisionSession,
    DecisionType,
    EcologicalConstraint,
    ExperienceRule,
    HMCError,
    HMCErrors,
    HumanDecision,
    IrrigationGoal,
    IrrigationGoalType,
    IrrigationProgram,
    IrrigationSchedule,
    SessionOutcome,
    SessionStatus,
    ZoneConfiguration,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Helper Functions - دوال مساعدة
# =============================================================================


def _parse_id_to_uuid(value: str | UUID | None) -> UUID | None:
    """
    Parse a string or UUID into a UUID.
    تحويل سلسلة أو UUID إلى UUID

    If the string is not a valid UUID, generate a deterministic UUID from it.
    """
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(value)
    except ValueError:
        # Generate a deterministic UUID from the string
        return uuid5(NAMESPACE_DNS, f"sahool.irrigation.{value}")


# =============================================================================
# Custom Exceptions - استثناءات مخصصة
# =============================================================================


class HMCEngineError(Exception):
    """
    Base exception for HMC Engine errors.
    الاستثناء الأساسي لأخطاء محرك HMC
    """

    def __init__(self, error: HMCError, details: dict[str, Any] | None = None):
        self.error = error
        self.details = details or {}
        super().__init__(f"{error.code}: {error.message}")


class SessionNotFoundError(HMCEngineError):
    """Raised when session is not found."""

    def __init__(self, session_id: UUID):
        super().__init__(
            HMCErrors.SESSION_NOT_FOUND,
            {"session_id": str(session_id)},
        )


class SessionInitError(HMCEngineError):
    """Raised when session is not properly initialized with required dimensions.
    يُطلق عندما لا تتم تهيئة الجلسة بالأبعاد المطلوبة"""

    def __init__(self, missing: str):
        super().__init__(
            HMCErrors.SESSION_INIT_FAILED,
            {"missing_components": missing},
        )


class GoalsNotSetError(HMCEngineError):
    """Raised when goals are required but not set."""

    def __init__(self):
        super().__init__(HMCErrors.GOALS_NOT_SET)


class ProgramNotGeneratedError(HMCEngineError):
    """Raised when program is required but not generated."""

    def __init__(self):
        super().__init__(HMCErrors.PROGRAM_NOT_GENERATED)


class ChecklistIncompleteError(HMCEngineError):
    """Raised when checklist is incomplete for approval."""

    def __init__(self, incomplete_items: list[str]):
        super().__init__(
            HMCErrors.CHECKLIST_INCOMPLETE,
            {"incomplete_items": incomplete_items},
        )


class MaxIterationsReachedError(HMCEngineError):
    """Raised when maximum iterations limit is reached."""

    def __init__(self, iteration_count: int, max_iterations: int):
        super().__init__(
            HMCErrors.MAX_ITERATIONS_REACHED,
            {"iteration_count": iteration_count, "max_iterations": max_iterations},
        )


# =============================================================================
# Program Generator Protocol - بروتوكول منشئ البرنامج
# =============================================================================


class ProgramGenerator:
    """
    Protocol for AI program generation.
    بروتوكول إنشاء البرنامج بالذكاء الاصطناعي

    This can be replaced with actual AI/ML implementation.
    """

    async def generate(
        self,
        goals: list[IrrigationGoal],
        constraints: list[EcologicalConstraint],
        rules: list[ExperienceRule],
        zones: list[ZoneConfiguration],
        context: dict[str, Any],
    ) -> IrrigationProgram:
        """
        Generate an irrigation program based on inputs.
        إنشاء برنامج ري بناءً على المدخلات

        Args:
            goals: Irrigation goals | أهداف الري
            constraints: Ecological constraints | القيود البيئية
            rules: Experience rules | قواعد الخبرة
            zones: Zone configurations | تكوينات المناطق
            context: Additional context | سياق إضافي

        Returns:
            Generated IrrigationProgram | برنامج الري المُنشأ
        """
        raise NotImplementedError


class DefaultProgramGenerator(ProgramGenerator):
    """
    Default program generator with simple rule-based logic.
    منشئ البرنامج الافتراضي بمنطق قائم على القواعد البسيطة

    In production, this would be replaced with an actual AI model.
    """

    async def generate(
        self,
        goals: list[IrrigationGoal],
        constraints: list[EcologicalConstraint],
        rules: list[ExperienceRule],
        zones: list[ZoneConfiguration],
        context: dict[str, Any],
    ) -> IrrigationProgram:
        """Generate a basic irrigation program."""
        # Extract primary goal
        primary_goal = next((g for g in goals if g.is_primary), goals[0] if goals else None)

        # Determine base irrigation parameters
        base_duration = 60  # minutes
        base_interval_hours = 24  # hours

        if primary_goal:
            if primary_goal.goal_type == IrrigationGoalType.WATER_SAVING:
                # Reduce duration for water saving
                reduction = primary_goal.target_reduction or 0.2
                base_duration = int(base_duration * (1 - reduction))
            elif primary_goal.goal_type == IrrigationGoalType.HIGH_YIELD:
                # Increase frequency for high yield
                base_interval_hours = 18

        # Apply constraint limits
        for constraint in constraints:
            if constraint.min_irrigation_interval_hours:
                base_interval_hours = max(
                    base_interval_hours,
                    constraint.min_irrigation_interval_hours,
                )

        # Create schedules for each zone
        schedules = []
        start_time = datetime.now(UTC).replace(hour=6, minute=0, second=0, microsecond=0)

        for i, zone in enumerate(zones):
            zone_duration = base_duration

            # Adjust for productivity level
            if zone.productivity_level.value == "high":
                zone_duration = int(zone_duration * 1.2)
            elif zone.productivity_level.value == "low":
                zone_duration = int(zone_duration * 0.8)

            schedule = IrrigationSchedule(
                zone_id=zone.zone_id,
                start_time=start_time,
                duration_minutes=zone_duration,
                skip_if_rain_mm=5.0,
            )
            schedules.append(schedule)

        # Calculate expected water usage
        total_area = sum(z.area_hectares or 1.0 for z in zones)
        expected_water = total_area * 50  # Simplified: 50 m3/ha

        program = IrrigationProgram(
            name=f"AI Generated - {datetime.now(UTC).strftime('%Y-%m-%d')}",
            name_ar=f"برنامج الذكاء الاصطناعي - {datetime.now(UTC).strftime('%Y-%m-%d')}",
            field_id=context.get("field_id"),
            farm_id=context.get("farm_id"),
            crop_type=context.get("crop_type", ""),
            growth_stage=context.get("growth_stage", ""),
            schedules=schedules,
            start_date=start_time,
            end_date=start_time + timedelta(days=7),
            expected_water_usage_m3=expected_water,
            generated_by="ai",
            generation_model="default_rule_based_v1",
            confidence_score=0.75,
            goals_applied=[g.id for g in goals],
            constraints_applied=[c.id for c in constraints],
            rules_applied=[r.id for r in rules if r.is_active],
        )

        return program


# =============================================================================
# HMC Irrigation Engine - محرك الري HMC
# =============================================================================


class HMCIrrigationEngine:
    """
    Human-Machine Collaborative Irrigation Decision Engine.
    محرك قرار الري التعاوني بين الإنسان والآلة

    This is the main orchestrator for the HMC irrigation decision framework.
    It manages the complete lifecycle of collaborative decision-making
    between farmers and AI systems.

    Key Features:
    - Session-based decision tracking
    - Four-dimension framework integration
    - Checklist validation
    - Iterative refinement support
    - Outcome recording for learning

    Example:
        engine = HMCIrrigationEngine(farm_id="FARM-001", farmer_id="farmer-123")

        # Phase 1: Human sets goals
        session = engine.start_decision_session()
        engine.human_sets_goals(
            goals=[IrrigationGoal(goal_type=IrrigationGoalType.WATER_SAVING)],
            constraints=[EcologicalConstraint(water_quota_reduction=0.3)]
        )

        # Phase 2: AI generates program
        program = await engine.ai_generates_program(context={...})

        # Phase 3: Human reviews and injects experience
        decision = engine.human_reviews_program(program)
        engine.human_injects_experience([
            ExperienceRule(condition="cold_wave", action="reduce_irrigation")
        ])

        # Phase 4: Calibration
        result = engine.run_calibration_cycle()

        # Phase 5: Approval
        if engine.checklist.validate_all().is_complete:
            engine.human_approves_execution()
    """

    def __init__(
        self,
        farm_id: str | UUID,
        farmer_id: str,
        field_id: str | UUID | None = None,
        program_generator: ProgramGenerator | None = None,
        max_iterations: int = 10,
    ):
        """
        Initialize the HMC Irrigation Engine.
        تهيئة محرك الري HMC

        Args:
            farm_id: Farm identifier | معرف المزرعة
            farmer_id: Farmer/user identifier | معرف المزارع
            field_id: Optional field identifier | معرف الحقل (اختياري)
            program_generator: Custom program generator | منشئ البرنامج المخصص
            max_iterations: Maximum iteration cycles allowed | الحد الأقصى لدورات التكرار
        """
        self._farm_id = _parse_id_to_uuid(farm_id) or uuid4()
        self._farmer_id = farmer_id
        self._field_id = _parse_id_to_uuid(field_id)
        self._max_iterations = max_iterations

        # Program generator (use default if not provided)
        self._program_generator = program_generator or DefaultProgramGenerator()

        # Current session
        self._current_session: DecisionSession | None = None

        # Dimensions
        self._goal_dimension: GoalAnchoringDimension | None = None
        self._experience_dimension: ExperienceInjectionDimension | None = None
        self._calibration_dimension: SupervisionCalibrationDimension | None = None
        self._value_dimension: ValueUpgradeDimension | None = None

        # Checklist
        self._checklist: CollaborativeChecklist | None = None

        # Event callbacks
        self._on_session_start: Callable[[DecisionSession], None] | None = None
        self._on_program_generated: Callable[[IrrigationProgram], None] | None = None
        self._on_approval: Callable[[DecisionSession], None] | None = None
        self._on_completion: Callable[[SessionOutcome], None] | None = None

        logger.info(
            "hmc_engine_initialized",
            farm_id=str(self._farm_id),
            farmer_id=self._farmer_id,
            field_id=str(self._field_id) if self._field_id else None,
        )

    # =========================================================================
    # Properties - الخصائص
    # =========================================================================

    @property
    def farm_id(self) -> UUID:
        """Get farm ID."""
        return self._farm_id

    @property
    def farmer_id(self) -> str:
        """Get farmer ID."""
        return self._farmer_id

    @property
    def field_id(self) -> UUID | None:
        """Get field ID."""
        return self._field_id

    @property
    def current_session(self) -> DecisionSession | None:
        """Get current active session."""
        return self._current_session

    @property
    def checklist(self) -> CollaborativeChecklist | None:
        """Get the checklist for current session."""
        return self._checklist

    @property
    def is_session_active(self) -> bool:
        """Check if there is an active session."""
        return self._current_session is not None and self._current_session.status not in [
            SessionStatus.COMPLETED,
            SessionStatus.CANCELLED,
        ]

    # =========================================================================
    # Session Management - إدارة الجلسات
    # =========================================================================

    def start_decision_session(
        self,
        context: dict[str, Any] | None = None,
    ) -> UUID:
        """
        Start a new collaborative decision session.
        بدء جلسة قرار تعاونية جديدة

        Initializes all dimensions and creates a new session for
        the human-AI collaborative irrigation decision process.

        Args:
            context: Additional context for the session | سياق إضافي للجلسة

        Returns:
            Session ID | معرف الجلسة

        Raises:
            HMCEngineError: If session already active | إذا كانت الجلسة نشطة بالفعل

        Example:
            session_id = engine.start_decision_session(
                context={"crop_type": "wheat", "growth_stage": "tillering"}
            )
        """
        # Check for existing active session
        if self.is_session_active:
            logger.warning(
                "session_already_active",
                session_id=str(self._current_session.id) if self._current_session else None,
            )
            # Return existing session ID
            return self._current_session.id if self._current_session else uuid4()

        # Create new session
        session = DecisionSession(
            farm_id=self._farm_id,
            field_id=self._field_id,
            farmer_id=self._farmer_id,
            status=SessionStatus.INITIALIZED,
            context=context or {},
            max_iterations=self._max_iterations,
        )

        self._current_session = session

        # Initialize dimensions
        self._goal_dimension = GoalAnchoringDimension(session_id=session.id)
        self._experience_dimension = ExperienceInjectionDimension(session_id=session.id)
        self._calibration_dimension = SupervisionCalibrationDimension(session_id=session.id)
        self._value_dimension = ValueUpgradeDimension(session_id=session.id)

        # Initialize checklist
        self._checklist = CollaborativeChecklist(session_id=session.id)

        # Trigger callback
        if self._on_session_start:
            self._on_session_start(session)

        logger.info(
            "decision_session_started",
            session_id=str(session.id),
            farm_id=str(self._farm_id),
            farmer_id=self._farmer_id,
        )

        return session.id

    def get_session_status(self) -> dict[str, Any]:
        """
        Get comprehensive status of current session.
        الحصول على حالة شاملة للجلسة الحالية

        Returns:
            Dictionary with session status | قاموس بحالة الجلسة
        """
        if not self._current_session:
            return {"active": False, "message": "No active session"}

        return {
            "active": True,
            "session_id": str(self._current_session.id),
            "status": self._current_session.status.value,
            "iteration_count": self._current_session.iteration_count,
            "max_iterations": self._current_session.max_iterations,
            "has_goals": len(self._current_session.goals) > 0,
            "has_constraints": len(self._current_session.constraints) > 0,
            "has_program": self._current_session.current_program is not None,
            "is_approved": (
                self._current_session.current_program.is_approved if self._current_session.current_program else False
            ),
            "dimension_status": {
                "goal_anchoring": self._goal_dimension.get_status() if self._goal_dimension else None,
                "experience_injection": self._experience_dimension.get_status() if self._experience_dimension else None,
                "supervision_calibration": self._calibration_dimension.get_status()
                if self._calibration_dimension
                else None,
                "value_upgrade": self._value_dimension.get_status() if self._value_dimension else None,
            },
            "checklist_complete": self._checklist.validate_all().is_complete if self._checklist else False,
            "created_at": self._current_session.created_at.isoformat(),
            "updated_at": self._current_session.updated_at.isoformat(),
        }

    def cancel_session(self, reason: str = "") -> None:
        """
        Cancel the current session.
        إلغاء الجلسة الحالية

        Args:
            reason: Reason for cancellation | سبب الإلغاء
        """
        if not self._current_session:
            return

        self._current_session.status = SessionStatus.CANCELLED
        self._current_session.notes = reason
        self._current_session.completed_at = datetime.now(UTC)

        logger.info(
            "decision_session_cancelled",
            session_id=str(self._current_session.id),
            reason=reason,
        )

    # =========================================================================
    # Phase 1: Goal Setting (Human) - المرحلة 1: تحديد الأهداف (الإنسان)
    # =========================================================================

    def human_sets_goals(
        self,
        goals: list[IrrigationGoal],
        constraints: list[EcologicalConstraint] | None = None,
        human_tasks: list[str] | None = None,
        ai_tasks: list[str] | None = None,
    ) -> tuple[bool, list[str]]:
        """
        Human sets irrigation goals and constraints.
        الإنسان يحدد أهداف الري والقيود

        This is the first phase where the farmer defines what success
        looks like and what boundaries the AI must respect.

        Args:
            goals: List of irrigation goals (first is primary) | قائمة أهداف الري
            constraints: Ecological constraints | القيود البيئية
            human_tasks: Tasks assigned to human | المهام المسندة للإنسان
            ai_tasks: Tasks assigned to AI | المهام المسندة للذكاء الاصطناعي

        Returns:
            Tuple of (success, warnings) | صف من (نجاح، تحذيرات)

        Raises:
            HMCEngineError: If no active session | إذا لم تكن هناك جلسة نشطة

        Example:
            success, warnings = engine.human_sets_goals(
                goals=[
                    IrrigationGoal(
                        goal_type=IrrigationGoalType.WATER_SAVING,
                        target_reduction=0.3
                    )
                ],
                constraints=[
                    EcologicalConstraint(
                        soil_salinity_limit=4.0,
                        water_quota_reduction=0.3
                    )
                ]
            )
        """
        self._ensure_session_active()
        if self._current_session is None or self._goal_dimension is None or self._checklist is None:
            raise SessionInitError("session, goal_dimension, or checklist")

        all_warnings: list[str] = []

        # Set primary goal (first in list)
        if goals:
            success, warnings = self._goal_dimension.set_primary_goal(goals[0])
            all_warnings.extend(warnings)
            if not success:
                return False, all_warnings

            # Add secondary goals
            for goal in goals[1:]:
                success, warnings = self._goal_dimension.add_secondary_goal(goal)
                all_warnings.extend(warnings)

        # Set constraints
        if constraints:
            success, warnings = self._goal_dimension.set_ecological_boundaries(constraints)
            all_warnings.extend(warnings)
            if not success:
                return False, all_warnings

        # Define responsibilities
        default_human_tasks = [
            "goal_definition",
            "constraint_setting",
            "experience_injection",
            "final_approval",
            "emergency_override",
        ]
        default_ai_tasks = [
            "schedule_optimization",
            "volume_calculation",
            "weather_integration",
            "sensor_analysis",
            "prediction_generation",
        ]

        self._goal_dimension.define_human_ai_responsibilities(
            human_tasks=human_tasks or default_human_tasks,
            ai_tasks=ai_tasks or default_ai_tasks,
        )

        # Validate alignment
        is_aligned, alignment_issues = self._goal_dimension.validate_goal_alignment()
        if not is_aligned:
            all_warnings.extend(alignment_issues)

        # Update session
        self._current_session.goals = self._goal_dimension.get_all_goals()
        self._current_session.constraints = constraints or []
        self._current_session.status = SessionStatus.GOALS_SET
        self._current_session.updated_at = datetime.now(UTC)

        # Update checklist
        self._checklist.check_item("define_primary_goal", self._farmer_id)
        if constraints:
            self._checklist.check_item("set_ecological_constraints", self._farmer_id)
        self._checklist.check_item("define_responsibilities", self._farmer_id)

        logger.info(
            "human_goals_set",
            session_id=str(self._current_session.id),
            goal_count=len(goals),
            constraint_count=len(constraints) if constraints else 0,
            warning_count=len(all_warnings),
        )

        return True, all_warnings

    # =========================================================================
    # Phase 2: Program Generation (AI) - المرحلة 2: إنشاء البرنامج (الذكاء الاصطناعي)
    # =========================================================================

    async def ai_generates_program(
        self,
        context: dict[str, Any] | None = None,
    ) -> IrrigationProgram:
        """
        AI generates an irrigation program based on goals and constraints.
        الذكاء الاصطناعي ينشئ برنامج ري بناءً على الأهداف والقيود

        Uses the configured program generator to create an optimized
        irrigation schedule that respects all constraints and rules.

        Args:
            context: Additional context for generation | سياق إضافي للإنشاء
                - crop_type: Current crop type
                - growth_stage: Current growth stage
                - weather_forecast: Weather data
                - soil_conditions: Soil sensor data
                - field_conditions: Field-specific data

        Returns:
            Generated IrrigationProgram | برنامج الري المُنشأ

        Raises:
            GoalsNotSetError: If goals not set | إذا لم تُحدد الأهداف

        Example:
            program = await engine.ai_generates_program(
                context={
                    "crop_type": "wheat",
                    "growth_stage": "tillering",
                    "soil_moisture": 35.0
                }
            )
        """
        self._ensure_session_active()
        if (
            self._current_session is None
            or self._goal_dimension is None
            or self._experience_dimension is None
            or self._checklist is None
        ):
            raise SessionInitError("session, goal_dimension, experience_dimension, or checklist")

        # Check goals are set
        goals = self._goal_dimension.get_all_goals()
        if not goals:
            raise GoalsNotSetError()

        # Gather inputs
        constraints = self._goal_dimension.get_constraints()
        rules = self._experience_dimension.get_all_rules()
        zones = self._current_session.zone_configs

        # Add default zone if none configured
        if not zones:
            zones = [
                ZoneConfiguration(
                    zone_id="default_zone",
                    name="Main Zone",
                    name_ar="المنطقة الرئيسية",
                    area_hectares=10.0,
                )
            ]

        # Prepare context
        generation_context = {
            "farm_id": self._current_session.farm_id,
            "field_id": self._current_session.field_id,
            **(context or {}),
            **self._current_session.context,
        }

        # Generate program
        program = await self._program_generator.generate(
            goals=goals,
            constraints=constraints,
            rules=rules,
            zones=zones,
            context=generation_context,
        )

        # Store in session
        if self._current_session.current_program:
            self._current_session.program_history.append(self._current_session.current_program)

        self._current_session.current_program = program
        self._current_session.status = SessionStatus.PROGRAM_GENERATED
        self._current_session.updated_at = datetime.now(UTC)

        # Update checklist
        self._checklist.check_item("ai_generates_program", "ai")

        # Trigger callback
        if self._on_program_generated:
            self._on_program_generated(program)

        logger.info(
            "ai_program_generated",
            session_id=str(self._current_session.id),
            program_id=str(program.id),
            schedule_count=len(program.schedules),
            confidence=program.confidence_score,
        )

        return program

    # =========================================================================
    # Phase 3: Human Review - المرحلة 3: مراجعة الإنسان
    # =========================================================================

    def human_reviews_program(
        self,
        program: IrrigationProgram | None = None,
        decision_type: DecisionType = DecisionType.APPROVE,
        rationale: str = "",
        rationale_ar: str = "",
        modifications: dict[str, Any] | None = None,
    ) -> HumanDecision:
        """
        Human reviews and decides on the AI-generated program.
        الإنسان يراجع ويقرر بشأن البرنامج المُنشأ بالذكاء الاصطناعي

        The farmer can approve, reject, modify, or defer the program.
        This decision is recorded for audit and learning purposes.

        Args:
            program: Program to review (uses current if None) | البرنامج للمراجعة
            decision_type: Type of decision | نوع القرار
            rationale: Reason for decision (English) | سبب القرار
            rationale_ar: Reason for decision (Arabic) | سبب القرار بالعربية
            modifications: Modifications if decision is MODIFY | التعديلات

        Returns:
            HumanDecision record | سجل قرار الإنسان

        Raises:
            ProgramNotGeneratedError: If no program to review | إذا لم يكن هناك برنامج

        Example:
            # Approve the program
            decision = engine.human_reviews_program(
                decision_type=DecisionType.APPROVE,
                rationale="Looks good for current conditions"
            )

            # Modify the program
            decision = engine.human_reviews_program(
                decision_type=DecisionType.MODIFY,
                rationale="Adjust timing for local conditions",
                modifications={"start_time": "06:00"}
            )
        """
        self._ensure_session_active()
        if self._current_session is None or self._checklist is None:
            raise SessionInitError("session or checklist")

        # Use current program if not provided
        program = program or self._current_session.current_program
        if not program:
            raise ProgramNotGeneratedError()

        # Create decision record
        decision = HumanDecision(
            session_id=self._current_session.id,
            recommendation_id=program.id,
            decision_type=decision_type,
            rationale=rationale,
            rationale_ar=rationale_ar,
            override_ai=(decision_type in [DecisionType.REJECT, DecisionType.OVERRIDE]),
            modifications=modifications or {},
            decided_by=self._farmer_id,
            decided_by_role="farmer",
        )

        # Apply modifications if decision is MODIFY
        if decision_type == DecisionType.MODIFY and modifications:
            self._apply_modifications(program, modifications)

        # Store decision
        self._current_session.decisions.append(decision)
        self._current_session.status = SessionStatus.UNDER_REVIEW
        self._current_session.updated_at = datetime.now(UTC)

        # Update checklist
        self._checklist.check_item("human_reviews_program", self._farmer_id)

        logger.info(
            "human_reviewed_program",
            session_id=str(self._current_session.id),
            decision_type=decision_type.value,
            override_ai=decision.override_ai,
        )

        return decision

    def human_injects_experience(
        self,
        rules: list[ExperienceRule],
        validate: bool = True,
    ) -> tuple[bool, list[str]]:
        """
        Human injects local experience rules.
        الإنسان يحقن قواعد الخبرة المحلية

        Allows the farmer to add their domain knowledge and local
        experience that the AI should consider.

        Args:
            rules: Experience rules to inject | قواعد الخبرة للحقن
            validate: Whether to validate rules | التحقق من القواعد

        Returns:
            Tuple of (success, warnings) | صف من (نجاح، تحذيرات)

        Example:
            success, warnings = engine.human_injects_experience([
                ExperienceRule(
                    condition="wheat_cold_wave",
                    action="reduce_irrigation_20%",
                    source=ExperienceSource.FARMER,
                    rationale="Cold reduces evapotranspiration"
                ),
                ExperienceRule(
                    condition="high_wind_above_30kmh",
                    action="delay_irrigation_4h",
                    source=ExperienceSource.RESEARCH,
                    rationale="Reduce evaporation losses"
                )
            ])
        """
        self._ensure_session_active()
        if self._current_session is None or self._experience_dimension is None or self._checklist is None:
            raise SessionInitError("session, experience_dimension, or checklist")

        # Inject rules
        success, warnings = self._experience_dimension.inject_local_experience(rules, validate)

        if success:
            # Update session
            self._current_session.experience_rules.extend(rules)
            self._current_session.status = SessionStatus.EXPERIENCE_INJECTED
            self._current_session.updated_at = datetime.now(UTC)

            # Update checklist
            self._checklist.check_item("inject_experience_rules", self._farmer_id)

            logger.info(
                "experience_injected",
                session_id=str(self._current_session.id),
                rule_count=len(rules),
            )

        return success, warnings

    # =========================================================================
    # Phase 4: Calibration - المرحلة 4: المعايرة
    # =========================================================================

    def run_calibration_cycle(
        self,
        method: CalibrationMethod = CalibrationMethod.SIMULATION,
        control_method: str | None = None,
        trial_area_hectares: float = 1.0,
    ) -> CalibrationResult:
        """
        Run a calibration cycle to test the program.
        تشغيل دورة معايرة لاختبار البرنامج

        Tests the program through simulation or field trial before
        full-scale deployment.

        Args:
            method: Calibration method to use | طريقة المعايرة
            control_method: Control method for comparison | طريقة المقارنة
            trial_area_hectares: Area for field trial | المساحة للتجربة الحقلية

        Returns:
            CalibrationResult | نتيجة المعايرة

        Raises:
            ProgramNotGeneratedError: If no program to calibrate | إذا لم يكن هناك برنامج

        Example:
            # Run simulation
            result = engine.run_calibration_cycle(
                method=CalibrationMethod.SIMULATION
            )

            # Run field trial
            result = engine.run_calibration_cycle(
                method=CalibrationMethod.FIELD_TRIAL,
                control_method="farmer_manual",
                trial_area_hectares=0.5
            )
        """
        self._ensure_session_active()
        if self._current_session is None or self._calibration_dimension is None or self._checklist is None:
            raise SessionInitError("session, calibration_dimension, or checklist")

        program = self._current_session.current_program
        if not program:
            raise ProgramNotGeneratedError()

        # Run calibration based on method
        if method == CalibrationMethod.SIMULATION:
            result = self._calibration_dimension.run_simulation_verification(program)
        elif method == CalibrationMethod.FIELD_TRIAL:
            result = self._calibration_dimension.run_field_trial(
                program,
                control_method=control_method or "farmer_manual",
                trial_area_hectares=trial_area_hectares,
            )
        else:
            # Default to simulation
            result = self._calibration_dimension.run_simulation_verification(program)

        # Store result
        self._current_session.calibration_results.append(result)
        self._current_session.status = SessionStatus.CALIBRATING
        self._current_session.updated_at = datetime.now(UTC)

        # Update checklist
        if method == CalibrationMethod.SIMULATION:
            self._checklist.check_item("run_simulation", "ai")
        elif method == CalibrationMethod.FIELD_TRIAL:
            self._checklist.check_item("conduct_field_trial", self._farmer_id)

        # Check emergency strategies
        strategies = self._calibration_dimension.check_emergency_strategies(program)
        if strategies:
            self._checklist.check_item("define_emergency_procedures", self._farmer_id)

        logger.info(
            "calibration_completed",
            session_id=str(self._current_session.id),
            method=method.value,
            passed=result.is_successful,
            issues_count=len(result.issues_found),
        )

        return result

    # =========================================================================
    # Phase 5: Approval and Execution - المرحلة 5: الموافقة والتنفيذ
    # =========================================================================

    def human_approves_execution(
        self,
        approval_notes: str = "",
    ) -> bool:
        """
        Human approves the program for execution.
        الإنسان يوافق على البرنامج للتنفيذ

        Final approval that authorizes the irrigation program to be
        executed. Requires checklist to be complete.

        Args:
            approval_notes: Notes from approver | ملاحظات من الموافق

        Returns:
            True if approval successful | صحيح إذا نجحت الموافقة

        Raises:
            ProgramNotGeneratedError: If no program | إذا لم يكن هناك برنامج
            ChecklistIncompleteError: If checklist incomplete | إذا القائمة غير مكتملة

        Example:
            if engine.checklist.validate_all().is_complete:
                success = engine.human_approves_execution(
                    approval_notes="Approved after successful simulation"
                )
        """
        self._ensure_session_active()
        if self._current_session is None or self._checklist is None:
            raise SessionInitError("session or checklist")

        program = self._current_session.current_program
        if not program:
            raise ProgramNotGeneratedError()

        # Validate checklist
        validation = self._checklist.validate_all()
        if not validation.is_complete:
            incomplete = self._checklist.get_incomplete_items()
            raise ChecklistIncompleteError([item.item for item in incomplete])

        # Mark checklist item
        self._checklist.check_item("human_approves_execution", self._farmer_id)

        # Update program
        program.is_approved = True
        program.approved_by = self._farmer_id
        program.approved_at = datetime.now(UTC)

        # Update session
        self._current_session.status = SessionStatus.APPROVED
        self._current_session.notes = approval_notes
        self._current_session.updated_at = datetime.now(UTC)

        # Create approval decision record
        approval_decision = HumanDecision(
            session_id=self._current_session.id,
            recommendation_id=program.id,
            decision_type=DecisionType.APPROVE,
            rationale=approval_notes,
            decided_by=self._farmer_id,
            decided_by_role="farmer",
        )
        self._current_session.decisions.append(approval_decision)

        # Trigger callback
        if self._on_approval:
            self._on_approval(self._current_session)

        logger.info(
            "execution_approved",
            session_id=str(self._current_session.id),
            program_id=str(program.id),
            approved_by=self._farmer_id,
        )

        return True

    # =========================================================================
    # Outcome Recording - تسجيل النتائج
    # =========================================================================

    def record_outcome(
        self,
        results: dict[str, Any],
    ) -> SessionOutcome:
        """
        Record the actual outcome after program execution.
        تسجيل النتيجة الفعلية بعد تنفيذ البرنامج

        Captures actual performance for learning and improvement.

        Args:
            results: Dictionary with actual outcomes | قاموس بالنتائج الفعلية
                - actual_water_usage_m3: Actual water used
                - actual_yield: Actual yield achieved
                - actual_cost: Actual cost
                - farmer_satisfaction: Satisfaction rating (1-5)
                - lessons_learned: List of lessons
                - success: Overall success boolean

        Returns:
            SessionOutcome record | سجل نتيجة الجلسة

        Example:
            outcome = engine.record_outcome({
                "actual_water_usage_m3": 1200.0,
                "actual_yield": 4.5,
                "actual_cost": 500.0,
                "farmer_satisfaction": 4,
                "success": True,
                "lessons_learned": ["Dawn irrigation reduced evaporation"]
            })
        """
        self._ensure_session_active()
        if self._current_session is None or self._value_dimension is None or self._checklist is None:
            raise SessionInitError("session, value_dimension, or checklist")

        program = self._current_session.current_program
        if not program:
            raise ProgramNotGeneratedError()

        # Calculate performance vs predictions
        water_saving = None
        if results.get("actual_water_usage_m3") and program.expected_water_usage_m3:
            water_saving = 1 - results["actual_water_usage_m3"] / program.expected_water_usage_m3

        # Create outcome record
        outcome = SessionOutcome(
            session_id=self._current_session.id,
            program_id=program.id,
            actual_water_usage_m3=results.get("actual_water_usage_m3"),
            actual_yield=results.get("actual_yield"),
            actual_cost=results.get("actual_cost"),
            water_saving_achieved=water_saving,
            overall_success=results.get("success", False),
            farmer_satisfaction=results.get("farmer_satisfaction"),
            lessons_learned=results.get("lessons_learned", []),
            raw_data=results,
            recorded_by=self._farmer_id,
        )

        # Store outcome
        self._current_session.outcome = outcome
        self._current_session.status = SessionStatus.COMPLETED
        self._current_session.completed_at = datetime.now(UTC)

        # Update checklist
        self._checklist.check_item("record_outcomes", self._farmer_id)

        # Extract new rules if successful
        if outcome.overall_success and results.get("lessons_learned"):
            observations = [
                {
                    "observation": lesson,
                    "condition": "learned_condition",
                    "outcome": "success",
                    "confidence": 0.7,
                }
                for lesson in results.get("lessons_learned", [])
            ]
            extracted = self._value_dimension.extract_field_rules(observations)
            outcome.new_rules_extracted = [rule.id for rule in extracted]

        # Trigger callback
        if self._on_completion:
            self._on_completion(outcome)

        logger.info(
            "outcome_recorded",
            session_id=str(self._current_session.id),
            success=outcome.overall_success,
            water_saving=water_saving,
            satisfaction=outcome.farmer_satisfaction,
        )

        return outcome

    # =========================================================================
    # Iteration Support - دعم التكرار
    # =========================================================================

    def start_new_iteration(self) -> int:
        """
        Start a new iteration cycle within the session.
        بدء دورة تكرار جديدة ضمن الجلسة

        Allows refining the program through multiple cycles.

        Returns:
            New iteration count | عدد التكرار الجديد

        Raises:
            MaxIterationsReachedError: If max iterations reached | إذا بلغ الحد الأقصى
        """
        self._ensure_session_active()
        if self._current_session is None:
            raise SessionInitError("session")

        if self._current_session.iteration_count >= self._current_session.max_iterations:
            raise MaxIterationsReachedError(
                self._current_session.iteration_count,
                self._current_session.max_iterations,
            )

        self._current_session.iteration_count += 1
        self._current_session.status = SessionStatus.GOALS_SET  # Reset to goals phase
        self._current_session.updated_at = datetime.now(UTC)

        logger.info(
            "new_iteration_started",
            session_id=str(self._current_session.id),
            iteration=self._current_session.iteration_count,
        )

        return self._current_session.iteration_count

    # =========================================================================
    # Reporting - التقارير
    # =========================================================================

    def generate_iteration_report(self) -> dict[str, Any]:
        """
        Generate a report for the current/completed session.
        إنشاء تقرير للجلسة الحالية/المكتملة

        Returns:
            Comprehensive report dictionary | قاموس تقرير شامل

        Example:
            report = engine.generate_iteration_report()
            print(f"Session: {report['session_id']}")
            print(f"Success: {report['outcome']['success'] if report['outcome'] else 'N/A'}")
        """
        if not self._current_session:
            return {"error": "No active session"}

        session = self._current_session

        report = {
            "report_type": "iteration_report",
            "generated_at": datetime.now(UTC).isoformat(),
            "session_id": str(session.id),
            "farm_id": str(session.farm_id),
            "farmer_id": session.farmer_id,
            "status": session.status.value,
            "iteration": {
                "count": session.iteration_count,
                "max": session.max_iterations,
            },
            "goals": {
                "count": len(session.goals),
                "primary": session.goals[0].goal_type.value if session.goals else None,
                "goals": [
                    {
                        "type": g.goal_type.value,
                        "target_reduction": g.target_reduction,
                        "is_primary": g.is_primary,
                    }
                    for g in session.goals
                ],
            },
            "constraints": {
                "count": len(session.constraints),
                "constraints": [
                    {
                        "water_quota_reduction": c.water_quota_reduction,
                        "soil_salinity_limit": c.soil_salinity_limit,
                    }
                    for c in session.constraints
                ],
            },
            "experience_rules": {
                "count": len(session.experience_rules),
                "by_source": self._count_rules_by_source(session.experience_rules),
            },
            "program": None,
            "calibration": {
                "count": len(session.calibration_results),
                "passed": sum(1 for r in session.calibration_results if r.is_successful),
                "issues_total": sum(len(r.issues_found) for r in session.calibration_results),
            },
            "decisions": {
                "count": len(session.decisions),
                "by_type": self._count_decisions_by_type(session.decisions),
            },
            "checklist": self._checklist.validate_all().model_dump() if self._checklist else None,
            "outcome": None,
            "timeline": {
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            },
        }

        # Add program details
        if session.current_program:
            program = session.current_program
            report["program"] = {
                "id": str(program.id),
                "name": program.name,
                "schedule_count": len(program.schedules),
                "expected_water_m3": program.expected_water_usage_m3,
                "confidence": program.confidence_score,
                "is_approved": program.is_approved,
                "approved_by": program.approved_by,
            }

        # Add outcome details
        if session.outcome:
            outcome = session.outcome
            report["outcome"] = {
                "success": outcome.overall_success,
                "actual_water_m3": outcome.actual_water_usage_m3,
                "water_saving": outcome.water_saving_achieved,
                "farmer_satisfaction": outcome.farmer_satisfaction,
                "lessons_learned": outcome.lessons_learned,
                "new_rules_extracted": len(outcome.new_rules_extracted),
            }

        return report

    # =========================================================================
    # Callbacks - الاستدعاءات
    # =========================================================================

    def on_session_start(self, callback: Callable[[DecisionSession], None]) -> None:
        """Register callback for session start."""
        self._on_session_start = callback

    def on_program_generated(self, callback: Callable[[IrrigationProgram], None]) -> None:
        """Register callback for program generation."""
        self._on_program_generated = callback

    def on_approval(self, callback: Callable[[DecisionSession], None]) -> None:
        """Register callback for approval."""
        self._on_approval = callback

    def on_completion(self, callback: Callable[[SessionOutcome], None]) -> None:
        """Register callback for session completion."""
        self._on_completion = callback

    # =========================================================================
    # Zone Configuration - تكوين المناطق
    # =========================================================================

    def configure_zones(
        self,
        zones: list[ZoneConfiguration],
    ) -> None:
        """
        Configure irrigation zones for the session.
        تكوين مناطق الري للجلسة

        Args:
            zones: List of zone configurations | قائمة تكوينات المناطق

        Example:
            engine.configure_zones([
                ZoneConfiguration(
                    zone_id="zone_north",
                    soil_type=SoilType.SANDY_LOAM,
                    productivity_level=ProductivityLevel.HIGH,
                    area_hectares=5.0
                ),
                ZoneConfiguration(
                    zone_id="zone_south",
                    soil_type=SoilType.CLAY,
                    productivity_level=ProductivityLevel.MEDIUM,
                    area_hectares=3.0
                )
            ])
        """
        self._ensure_session_active()
        if self._current_session is None:
            raise SessionInitError("session")

        self._current_session.zone_configs = zones
        self._current_session.updated_at = datetime.now(UTC)

        logger.info(
            "zones_configured",
            session_id=str(self._current_session.id),
            zone_count=len(zones),
        )

    # =========================================================================
    # Helper Methods - طرق مساعدة
    # =========================================================================

    def _ensure_session_active(self) -> None:
        """Ensure there is an active session."""
        if not self.is_session_active:
            raise HMCEngineError(
                HMCError(
                    code="NO_ACTIVE_SESSION",
                    message="No active decision session",
                    message_ar="لا توجد جلسة قرار نشطة",
                    suggested_action="Call start_decision_session() first",
                    suggested_action_ar="استدعِ start_decision_session() أولاً",
                )
            )

    def _apply_modifications(
        self,
        program: IrrigationProgram,
        modifications: dict[str, Any],
    ) -> None:
        """Apply modifications to a program."""
        for key, value in modifications.items():
            if hasattr(program, key):
                setattr(program, key, value)

        program.updated_at = datetime.now(UTC)
        program.version += 1

    def _count_rules_by_source(
        self,
        rules: list[ExperienceRule],
    ) -> dict[str, int]:
        """Count rules by source."""
        counts: dict[str, int] = {}
        for rule in rules:
            source = rule.source.value
            counts[source] = counts.get(source, 0) + 1
        return counts

    def _count_decisions_by_type(
        self,
        decisions: list[HumanDecision],
    ) -> dict[str, int]:
        """Count decisions by type."""
        counts: dict[str, int] = {}
        for decision in decisions:
            dtype = decision.decision_type.value
            counts[dtype] = counts.get(dtype, 0) + 1
        return counts


# =============================================================================
# Factory Functions - دوال المصنع
# =============================================================================


def create_hmc_engine(
    farm_id: str | UUID,
    farmer_id: str,
    field_id: str | UUID | None = None,
    **kwargs,
) -> HMCIrrigationEngine:
    """
    Factory function to create an HMC Irrigation Engine.
    دالة مصنع لإنشاء محرك الري HMC

    Args:
        farm_id: Farm identifier | معرف المزرعة
        farmer_id: Farmer identifier | معرف المزارع
        field_id: Optional field identifier | معرف الحقل
        **kwargs: Additional engine configuration

    Returns:
        Configured HMCIrrigationEngine | محرك HMC مُهيأ

    Example:
        engine = create_hmc_engine(
            farm_id="FARM-001",
            farmer_id="farmer-123",
            field_id="FIELD-001",
            max_iterations=5
        )
    """
    return HMCIrrigationEngine(
        farm_id=farm_id,
        farmer_id=farmer_id,
        field_id=field_id,
        **kwargs,
    )


# Alias for convenience
get_hmc_engine = create_hmc_engine
