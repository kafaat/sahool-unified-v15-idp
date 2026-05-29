# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Crop Card Schema - مخطّط بطاقة المحصول
=========================================
Strictly-typed Pydantic model. ``extra="forbid"`` mechanically rejects any
field outside the physical-parameters set (no ``region``, no ``yield_history``,
no ``zone_factor``). Neutrality is enforced by the schema itself.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

_CROP_ID_RE = re.compile(r"^[a-z0-9_]{1,32}$")


class CropCard(BaseModel):
    """A location-neutral set of crop parameters."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    crop_id: str
    name_ar: str = Field(min_length=1, max_length=64)
    name_en: str = Field(min_length=1, max_length=64)
    family: str = Field(min_length=1, max_length=32)

    # FAO-56 Kc profile
    kc_initial: float = Field(ge=0.0, le=2.0)
    kc_mid: float = Field(ge=0.0, le=2.0)
    kc_end: float = Field(ge=0.0, le=2.0)
    growth_stage_days: list[int] = Field(min_length=4, max_length=4)

    # Governing thresholds (Maas-Hoffman style + ECOCROP)
    salinity_threshold_dsm: float = Field(ge=0.0, le=30.0)
    salinity_slope_pct: float = Field(ge=0.0, le=100.0)
    ph_min: float = Field(ge=2.0, le=10.0)
    ph_max: float = Field(ge=2.0, le=10.0)
    chilling_hours_required: int = Field(ge=0, le=4000)

    # GDD model
    base_temp_c: float = Field(ge=-10.0, le=20.0)
    max_temp_cap_c: float = Field(ge=15.0, le=50.0)

    # Sources MUST be cited; no calibration data here.
    sources: list[str] = Field(min_length=1)

    @field_validator("crop_id")
    @classmethod
    def _validate_crop_id(cls, v: str) -> str:
        if not _CROP_ID_RE.match(v):
            raise ValueError(f"crop_id must match {_CROP_ID_RE.pattern!r}; got {v!r}")
        return v

    @field_validator("growth_stage_days")
    @classmethod
    def _validate_stage_days(cls, v: list[int]) -> list[int]:
        if any(d < 0 for d in v):
            raise ValueError("growth_stage_days must be non-negative")
        return v


__all__ = ["CropCard"]
