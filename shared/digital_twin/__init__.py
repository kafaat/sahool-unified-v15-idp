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
from shared.digital_twin.decisions import DecisionEngine
from shared.digital_twin.feature_flags import DigitalTwinFlags
from shared.digital_twin.models import (
    AssimilationFlag,
    FieldDailyState,
    FieldObservation,
    IrrigationRecommendation,
    ObservationType,
    ObservationSource,
)
from shared.digital_twin.pipeline import TwinPipeline
from shared.digital_twin.repository import TwinRepository

__all__ = [
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
]
