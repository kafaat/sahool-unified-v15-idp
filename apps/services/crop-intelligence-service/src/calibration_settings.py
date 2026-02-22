# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Settings - إعدادات المعايرة
=========================================
Environment-based configuration for the Calibration Engine feature.
"""

from __future__ import annotations

import os


def _bool_env(key: str, default: bool) -> bool:
    val = os.environ.get(key, "").strip().lower()
    if val in ("1", "true", "yes", "on"):
        return True
    if val in ("0", "false", "no", "off"):
        return False
    return default


class CalibrationSettings:
    """Read-only settings from environment. إعدادات القراءة فقط من البيئة."""

    @property
    def enabled(self) -> bool:
        """Master kill-switch. مفتاح التعطيل الرئيسي."""
        return _bool_env("CALIBRATION_ENABLED", False)

    @property
    def n_trials(self) -> int:
        return int(os.getenv("CALIBRATION_N_TRIALS", "60"))

    @property
    def seed(self) -> int:
        return int(os.getenv("CALIBRATION_SEED", "42"))

    @property
    def max_rmse_lai(self) -> float:
        return float(os.getenv("CALIBRATION_MAX_RMSE_LAI", "0.8"))

    @property
    def max_rmse_biomass(self) -> float:
        return float(os.getenv("CALIBRATION_MAX_RMSE_BIOMASS", "500.0"))

    @property
    def min_observations(self) -> int:
        """Minimum observations per target to accept. الحد الأدنى للأرصاد."""
        return int(os.getenv("CALIBRATION_MIN_OBSERVATIONS", "3"))

    def as_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "n_trials": self.n_trials,
            "seed": self.seed,
            "max_rmse_lai": self.max_rmse_lai,
            "max_rmse_biomass": self.max_rmse_biomass,
            "min_observations": self.min_observations,
        }
