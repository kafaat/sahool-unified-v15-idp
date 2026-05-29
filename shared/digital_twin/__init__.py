# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Digital Twin Domain Package - حزمة التوأم الرقمي
==================================================
Connects the process-based kernel (shared/process_models) to the live SAHOOL
platform by providing:

  models         – FieldDailyState, FieldObservation, IrrigationRecommendation
  repository     – asyncpg DB persistence with in-memory fallback
  pipeline       – Daily twin step (ET₀ → SWB → crop growth → state → events)
  assimilation   – Kalman-lite NDVI/sensor state correction
  decisions      – RAW-based irrigation + QUEFTS fertilizer recommendations
  feature_flags  – Environment-based feature toggles

Database tables created by migrations/001_digital_twin_tables.sql:
  field_daily_state        – Daily simulation state per field
  field_observation        – NDVI/LAI/sensor observations for assimilation
  irrigation_recommendation – Computed irrigation decisions
"""

from shared.digital_twin.assimilation import AssimilationEngine
from shared.digital_twin.decision_chain import ChainStep, DecisionChain, start_chain
from shared.digital_twin.decisions import DecisionEngine
from shared.digital_twin.errors import (
    ContextPipelineError,
    DigitalTwinError,
    NeutralityViolation,
    UnsafeRecommendationError,
)
from shared.digital_twin.evidence_class import (
    Confidence,
    EvidenceClass,
    IndicationSignal,
    classify_quality,
    corroborate_indications,
    enforce_indication_ceiling,
)
from shared.digital_twin.feature_flags import DigitalTwinFlags
from shared.digital_twin.feedback_loop import (
    OutcomeRecord,
    evaluate_outcome,
    should_trigger_recalibration,
)
from shared.digital_twin.field_lifecycle import (
    GOVERNING_OBSERVABLES,
    FieldQualityState,
    LifecycleAssessment,
    SoilTestChoice,
    effective_confidence_cap,
    resolve_state,
)
from shared.digital_twin.models import (
    AssimilationFlag,
    BackendDetail,
    FarmerView,
    FieldDailyState,
    FieldObservation,
    IrrigationRecommendation,
    ObservationSource,
    ObservationType,
)
from shared.digital_twin.pesticide_gate import (
    PesticideGateResult,
    PesticideGateStatus,
)
from shared.digital_twin.pesticide_gate import (
    evaluate as evaluate_pesticide_gate,
)
from shared.digital_twin.pipeline import TwinPipeline
from shared.digital_twin.repository import TwinRepository

__all__ = [
    # Existing
    "FieldDailyState",
    "FieldObservation",
    "IrrigationRecommendation",
    "AssimilationFlag",
    "ObservationType",
    "ObservationSource",
    "TwinRepository",
    "TwinPipeline",
    "AssimilationEngine",
    "DecisionEngine",
    "DigitalTwinFlags",
    # Decision Kernel additions
    "FieldQualityState",
    "SoilTestChoice",
    "LifecycleAssessment",
    "GOVERNING_OBSERVABLES",
    "resolve_state",
    "effective_confidence_cap",
    "EvidenceClass",
    "Confidence",
    "IndicationSignal",
    "classify_quality",
    "enforce_indication_ceiling",
    "corroborate_indications",
    "PesticideGateStatus",
    "PesticideGateResult",
    "evaluate_pesticide_gate",
    "FarmerView",
    "BackendDetail",
    "ChainStep",
    "DecisionChain",
    "start_chain",
    "OutcomeRecord",
    "evaluate_outcome",
    "should_trigger_recalibration",
    # Errors
    "DigitalTwinError",
    "ContextPipelineError",
    "NeutralityViolation",
    "UnsafeRecommendationError",
]
