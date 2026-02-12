"""
Human-Machine Collaborative (HMC) Irrigation Decision Framework
===============================================================
إطار قرار الري التعاوني بين الإنسان والآلة

A comprehensive framework for collaborative irrigation decision-making
between farmers (domain experts) and AI systems. Based on the four-dimension
HMC approach:

1. **Goal Anchoring** (ترسيخ الأهداف)
   - Human defines primary optimization goals
   - Sets ecological constraints and boundaries
   - Assigns human-AI responsibilities

2. **Experience Injection** (حقن الخبرة)
   - Human injects local farming experience
   - Translates tacit knowledge to rules
   - Calibrates AI reward functions

3. **Supervision Calibration** (معايرة الإشراف)
   - Tests programs through simulation
   - Validates with field trials
   - Defines emergency procedures

4. **Value Upgrade** (ترقية القيمة)
   - Extracts new rules from outcomes
   - Integrates with other systems
   - Continuous improvement cycle

Key Features:
- Session-based decision tracking with full audit trail
- Bilingual support (Arabic/English) throughout
- Integration with SAHOOL agents and services
- Validation checklist for each dimension
- Outcome recording for continuous learning

Quick Start:
    from shared.irrigation import (
        HMCIrrigationEngine,
        IrrigationGoal,
        IrrigationGoalType,
        EcologicalConstraint,
        ExperienceRule,
        ExperienceSource,
    )

    # Create engine
    engine = HMCIrrigationEngine(
        farm_id="FARM-001",
        farmer_id="farmer-123"
    )

    # Phase 1: Human sets goals
    session_id = engine.start_decision_session()
    engine.human_sets_goals(
        goals=[IrrigationGoal(goal_type=IrrigationGoalType.WATER_SAVING)],
        constraints=[EcologicalConstraint(water_quota_reduction=0.3)]
    )

    # Phase 2: AI generates program
    program = await engine.ai_generates_program(
        context={"crop_type": "wheat", "growth_stage": "tillering"}
    )

    # Phase 3: Human reviews and injects experience
    engine.human_reviews_program(program)
    engine.human_injects_experience([
        ExperienceRule(
            condition="cold_wave",
            action="reduce_irrigation_20%",
            source=ExperienceSource.FARMER
        )
    ])

    # Phase 4: Calibration
    result = engine.run_calibration_cycle()

    # Phase 5: Approval
    if engine.checklist.validate_all().is_complete:
        engine.human_approves_execution()

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
License: Proprietary - KAFAAT
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "SAHOOL Platform Team"

# =============================================================================
# Models - النماذج
# =============================================================================

# =============================================================================
# Checklist - قائمة التحقق
# =============================================================================
from .checklist import (
    EXPERIENCE_INJECTION_ITEMS,
    # Item definitions
    GOAL_ANCHORING_ITEMS,
    SUPERVISION_CALIBRATION_ITEMS,
    VALUE_UPGRADE_ITEMS,
    CollaborativeChecklist,
    # Factory functions
    create_checklist,
    get_checklist,
)

# =============================================================================
# Collaborative Engine - المحرك التعاوني
# =============================================================================
from .collaborative_engine import (
    ChecklistIncompleteError,
    DefaultProgramGenerator,
    GoalsNotSetError,
    # Exceptions
    HMCEngineError,
    # Main engine
    HMCIrrigationEngine,
    MaxIterationsReachedError,
    # Program generator
    ProgramGenerator,
    ProgramNotGeneratedError,
    SessionNotFoundError,
    # Factory functions
    create_hmc_engine,
    get_hmc_engine,
)

# =============================================================================
# Dimensions - الأبعاد
# =============================================================================
from .dimensions import (
    ExperienceInjectionDimension,
    # Four HMC dimensions
    GoalAnchoringDimension,
    # Base class
    HMCDimension,
    SupervisionCalibrationDimension,
    ValueUpgradeDimension,
)

# =============================================================================
# Integration - التكامل
# =============================================================================
from .integration import (
    # Protocols
    FarmAdvisorAgent,
    FertilizationService,
    # Integration Manager
    HMCIntegrationManager,
    IrrigationSubAgent,
    WeatherService,
    # Singleton
    get_integration_manager,
    # Helper functions
    integrate_with_farm_advisor,
    integrate_with_irrigation_agent,
    reset_integration_manager,
    sync_with_fertilization_system,
    sync_with_weather_service,
)
from .models import (
    # Core Models
    BilingualLabel,
    CalibrationMethod,
    CalibrationResult,
    ChecklistDimension,
    CollaborativeChecklistItem,
    DecisionSession,
    DecisionType,
    EcologicalConstraint,
    ExperienceRule,
    ExperienceSource,
    # Error Models
    HMCError,
    HMCErrors,
    HumanDecision,
    IrrigationGoal,
    # Enums
    IrrigationGoalType,
    IrrigationProgram,
    IrrigationSchedule,
    ProductivityLevel,
    SessionOutcome,
    SessionStatus,
    SoilType,
    ValidationReport,
    ZoneConfiguration,
)

# =============================================================================
# All Exports - جميع الصادرات
# =============================================================================

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # === Enums ===
    "IrrigationGoalType",
    "ExperienceSource",
    "DecisionType",
    "SoilType",
    "ProductivityLevel",
    "ChecklistDimension",
    "CalibrationMethod",
    "SessionStatus",
    # === Core Models ===
    "BilingualLabel",
    "IrrigationGoal",
    "EcologicalConstraint",
    "ExperienceRule",
    "HumanDecision",
    "CalibrationResult",
    "ZoneConfiguration",
    "CollaborativeChecklistItem",
    "IrrigationSchedule",
    "IrrigationProgram",
    "ValidationReport",
    "SessionOutcome",
    "DecisionSession",
    # === Error Models ===
    "HMCError",
    "HMCErrors",
    # === Dimensions ===
    "HMCDimension",
    "GoalAnchoringDimension",
    "ExperienceInjectionDimension",
    "SupervisionCalibrationDimension",
    "ValueUpgradeDimension",
    # === Engine ===
    "HMCIrrigationEngine",
    "ProgramGenerator",
    "DefaultProgramGenerator",
    # === Exceptions ===
    "HMCEngineError",
    "SessionNotFoundError",
    "GoalsNotSetError",
    "ProgramNotGeneratedError",
    "ChecklistIncompleteError",
    "MaxIterationsReachedError",
    # === Checklist ===
    "CollaborativeChecklist",
    "GOAL_ANCHORING_ITEMS",
    "EXPERIENCE_INJECTION_ITEMS",
    "SUPERVISION_CALIBRATION_ITEMS",
    "VALUE_UPGRADE_ITEMS",
    # === Integration Protocols ===
    "FarmAdvisorAgent",
    "IrrigationSubAgent",
    "WeatherService",
    "FertilizationService",
    # === Integration Manager ===
    "HMCIntegrationManager",
    # === Factory Functions ===
    "create_hmc_engine",
    "get_hmc_engine",
    "create_checklist",
    "get_checklist",
    "get_integration_manager",
    "reset_integration_manager",
    # === Helper Functions ===
    "integrate_with_farm_advisor",
    "integrate_with_irrigation_agent",
    "sync_with_weather_service",
    "sync_with_fertilization_system",
]


# =============================================================================
# Convenience Functions - دوال الراحة
# =============================================================================


def quick_start(
    farm_id: str,
    farmer_id: str,
    field_id: str | None = None,
) -> HMCIrrigationEngine:
    """
    Quick start function to create an HMC engine and start a session.
    دالة بداية سريعة لإنشاء محرك HMC وبدء جلسة

    Args:
        farm_id: Farm identifier | معرف المزرعة
        farmer_id: Farmer identifier | معرف المزارع
        field_id: Optional field identifier | معرف الحقل (اختياري)

    Returns:
        HMCIrrigationEngine with session started | محرك HMC مع جلسة بادئة

    Example:
        from shared.irrigation import quick_start

        engine = quick_start(
            farm_id="FARM-001",
            farmer_id="farmer-123"
        )
        # Session is already started, ready to set goals
    """
    engine = HMCIrrigationEngine(
        farm_id=farm_id,
        farmer_id=farmer_id,
        field_id=field_id,
    )
    engine.start_decision_session()
    return engine


def get_framework_info() -> dict:
    """
    Get information about the HMC framework.
    الحصول على معلومات عن إطار HMC

    Returns:
        Dictionary with framework information | قاموس بمعلومات الإطار
    """
    return {
        "name": "Human-Machine Collaborative (HMC) Irrigation Decision Framework",
        "name_ar": "إطار قرار الري التعاوني بين الإنسان والآلة",
        "version": __version__,
        "author": __author__,
        "dimensions": [
            {
                "name": "Goal Anchoring",
                "name_ar": "ترسيخ الأهداف",
                "description": "Human defines objectives and boundaries",
                "description_ar": "الإنسان يحدد الأهداف والحدود",
            },
            {
                "name": "Experience Injection",
                "name_ar": "حقن الخبرة",
                "description": "Human injects local/tacit knowledge",
                "description_ar": "الإنسان يحقن المعرفة المحلية/الضمنية",
            },
            {
                "name": "Supervision Calibration",
                "name_ar": "معايرة الإشراف",
                "description": "Testing and validation cycles",
                "description_ar": "دورات الاختبار والتحقق",
            },
            {
                "name": "Value Upgrade",
                "name_ar": "ترقية القيمة",
                "description": "Continuous learning and improvement",
                "description_ar": "التعلم والتحسين المستمر",
            },
        ],
        "goal_types": [g.value for g in IrrigationGoalType],
        "experience_sources": [s.value for s in ExperienceSource],
        "calibration_methods": [m.value for m in CalibrationMethod],
    }


# Add to __all__
__all__.extend(
    [
        "quick_start",
        "get_framework_info",
    ]
)
