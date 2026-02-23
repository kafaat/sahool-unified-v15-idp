# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Digital Twin Feature Flags - راية الميزات للتوأم الرقمي
==========================================================
Environment-based feature toggles for incremental rollout.
All flags default to the safest / most conservative setting.

Environment variables:
  PROCESS_MODELS_ENABLED        – Enable process-based simulation (default: true)
  ASSIMILATION_ENABLED          – Enable NDVI/sensor assimilation (default: false)
  PROSAIL_INVERSION_ENABLED     – Enable PROSAIL RTM inversion (default: false)
  SOIL_CARBON_ENABLED           – Enable soil carbon model output (default: false)
  PEST_EPI_ENABLED              – Enable pest epidemiology model (default: false)
  TWIN_DB_PERSIST_ENABLED       – Write states to DB (default: true)
  TWIN_NATS_EVENTS_ENABLED      – Publish NATS events (default: true)
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


class DigitalTwinFlags:
    """
    Centralised feature flag reader for the Digital Twin module.
    قارئ رايات الميزات المركزي لوحدة التوأم الرقمي.

    Usage::

        flags = DigitalTwinFlags()
        if flags.process_models_enabled:
            result = pipeline.step(...)
    """

    @property
    def process_models_enabled(self) -> bool:
        """Core process-based simulation active. | المحاكاة الفيزيائية الأساسية."""
        return _bool_env("PROCESS_MODELS_ENABLED", True)

    @property
    def assimilation_enabled(self) -> bool:
        """NDVI / sensor data assimilation active. | تمثيل البيانات المرصودة."""
        return _bool_env("ASSIMILATION_ENABLED", False)

    @property
    def prosail_inversion_enabled(self) -> bool:
        """PROSAIL RTM inversion for LAI retrieval. | عكس نموذج PROSAIL."""
        return _bool_env("PROSAIL_INVERSION_ENABLED", False)

    @property
    def soil_carbon_enabled(self) -> bool:
        """Soil carbon model outputs exposed. | نموذج كربون التربة."""
        return _bool_env("SOIL_CARBON_ENABLED", False)

    @property
    def pest_epi_enabled(self) -> bool:
        """Pest epidemiology model active. | نموذج وبائيات الآفات."""
        return _bool_env("PEST_EPI_ENABLED", False)

    @property
    def db_persist_enabled(self) -> bool:
        """Persist twin state to PostgreSQL. | حفظ الحالة في قاعدة البيانات."""
        return _bool_env("TWIN_DB_PERSIST_ENABLED", True)

    @property
    def nats_events_enabled(self) -> bool:
        """Publish twin events to NATS. | نشر أحداث NATS."""
        return _bool_env("TWIN_NATS_EVENTS_ENABLED", True)

    def as_dict(self) -> dict[str, bool]:
        return {
            "process_models_enabled": self.process_models_enabled,
            "assimilation_enabled": self.assimilation_enabled,
            "prosail_inversion_enabled": self.prosail_inversion_enabled,
            "soil_carbon_enabled": self.soil_carbon_enabled,
            "pest_epi_enabled": self.pest_epi_enabled,
            "db_persist_enabled": self.db_persist_enabled,
            "nats_events_enabled": self.nats_events_enabled,
        }
