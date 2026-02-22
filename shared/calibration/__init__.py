# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Framework - إطار المعايرة
=======================================
Parameter calibration engine for process-based agricultural models.

Provides:
  types       – CalibrationTarget, CalibrationObservation, TimestampedObservation
  engine      – CalibrationEngine (hill-climbing) + BayesianCalibration (Optuna NLL)
  objective   – Weighted NLL objective function
  optimizer   – BayesianOptimizer (Optuna TPE)
  validation  – Holdout RMSE/MAE/bias evaluation
  repository  – asyncpg persistence for runs & parameter sets
  fingerprint – Deterministic SHA-256 dataset fingerprinting
  errors      – Domain-specific calibration exceptions
  adapters/   – Model-specific predictors (crop_growth, ...)
"""

from shared.calibration.engine import (
    BayesianCalibration,
    CalibrationConfig,
    CalibrationEngine,
    CalibrationOutput,
)
from shared.calibration.types import (
    CalibrationObservation,
    CalibrationResult,
    CalibrationTarget,
    ParameterBound,
    TimestampedObservation,
    ValidationMetrics,
)

__all__ = [
    # Legacy engine
    "CalibrationEngine",
    # Bayesian engine
    "BayesianCalibration",
    "CalibrationConfig",
    "CalibrationOutput",
    # Types
    "CalibrationObservation",
    "CalibrationResult",
    "CalibrationTarget",
    "ParameterBound",
    "TimestampedObservation",
    "ValidationMetrics",
]
