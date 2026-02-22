# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Framework - إطار المعايرة
=======================================
Parameter calibration engine for process-based agricultural models.

Provides:
  types     – CalibrationTarget, CalibrationObservation value objects
  engine    – CalibrationEngine (optimizer loop + cost functions)
  adapters/ – Model-specific predictors that bridge CalibrationEngine ↔ process models
"""

from shared.calibration.engine import CalibrationEngine
from shared.calibration.types import (
    CalibrationObservation,
    CalibrationResult,
    CalibrationTarget,
)

__all__ = [
    "CalibrationEngine",
    "CalibrationObservation",
    "CalibrationResult",
    "CalibrationTarget",
]
