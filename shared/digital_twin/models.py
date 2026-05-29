# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Digital Twin Domain Models - نماذج التوأم الرقمي
=================================================
Pydantic / dataclass value objects for the field Digital Twin layer.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from shared.digital_twin.decision_chain import DecisionChain

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ObservationType(StrEnum):
    """Type of field observation. نوع الرصد الميداني."""

    NDVI = "ndvi"
    LAI = "lai"
    SOIL_MOISTURE = "soil_moisture"
    CANOPY_TEMPERATURE = "canopy_temp"
    BIOMASS_ESTIMATE = "biomass"
    SOIL_NITROGEN = "soil_nitrogen"


class ObservationSource(StrEnum):
    """Observation data source. مصدر بيانات الرصد."""

    SENTINEL_2 = "sentinel-2"
    UAV = "uav"
    IOT_SENSOR = "iot_sensor"
    MANUAL = "manual"
    PLANET = "planet"
    LANDSAT = "landsat"


class AssimilationFlag(StrEnum):
    """Flags set during state assimilation. رايات التمثيل."""

    NDVI_USED = "NDVI_USED"
    LAI_USED = "LAI_USED"
    SOIL_MOISTURE_USED = "SOIL_MOISTURE_USED"
    ASSIMILATED = "ASSIMILATED"
    MODEL_ONLY = "MODEL_ONLY"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    CALIBRATED_PARAMS_USED = "CALIBRATED_PARAMS_USED"


# ---------------------------------------------------------------------------
# Field Daily State
# ---------------------------------------------------------------------------


class FieldDailyState(BaseModel):
    """
    Daily simulation state for a single field – the core Digital Twin record.
    الحالة اليومية للمحاكاة لحقل واحد – سجل التوأم الرقمي الأساسي.

    Stored once per (tenant_id, field_id, day) in ``field_daily_state`` table.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    field_id: UUID
    day: date

    # ── Agro-meteorology ──────────────────────────────────────────────────
    et0_mm: float | None = None
    """FAO-56 Penman-Monteith reference ET₀ (mm d⁻¹) | التبخر-النتح المرجعي"""
    etc_mm: float | None = None
    """Crop actual ET (mm d⁻¹) | التبخر-النتح الفعلي للمحصول"""

    # ── Crop growth ───────────────────────────────────────────────────────
    phenology_stage: str | None = None
    """Growth stage code (e.g. tillering, grain_fill) | مرحلة النمو"""
    gdd_cum: float | None = None
    """Cumulative Growing Degree Days | وحدات الحرارة التراكمية"""
    lai: float | None = None
    """Leaf Area Index | مؤشر مساحة الأوراق"""
    biomass_kg_ha: float | None = None
    """Aboveground dry biomass (kg ha⁻¹) | الكتلة الحيوية"""
    root_depth_m: float | None = None
    """Effective root depth (m) | عمق الجذور الفعّال"""

    # ── Soil water balance ────────────────────────────────────────────────
    soil_water_mm: float | None = None
    """Current soil water in root zone (mm) | مياه التربة الحالية"""
    depletion_mm: float | None = None
    """Water depletion below field capacity (mm) | عجز الرطوبة"""
    water_stress: float | None = Field(default=None, ge=0.0, le=1.0)
    """Water stress factor Ks ∈ [0, 1] (0=max stress) | معامل إجهاد الرطوبة"""
    n_stress: float | None = Field(default=None, ge=0.0, le=1.0)
    """Nitrogen stress factor ∈ [0, 1] | معامل إجهاد النيتروجين"""
    runoff_mm: float | None = None
    """Surface runoff (mm) | الجريان السطحي"""
    deep_perc_mm: float | None = None
    """Deep percolation / drainage (mm) | الصرف العميق"""

    # ── Applied inputs (that day) ─────────────────────────────────────────
    rainfall_mm: float = 0.0
    """Precipitation (mm) | هطول الأمطار"""
    irrigation_applied_mm: float = 0.0
    """Irrigation applied (mm) | الري المطبّق"""
    nitrogen_applied_kg_ha: float = 0.0
    """Fertiliser N applied (kg ha⁻¹) | النيتروجين المضاف"""

    # ── Quality / assimilation ────────────────────────────────────────────
    confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    """Model confidence score ∈ [0, 1] | درجة الثقة"""
    assimilation_flags: list[AssimilationFlag] = Field(default_factory=list)
    """Flags describing what observations were used | رايات البيانات المستخدمة"""
    notes: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def summary(self) -> dict[str, Any]:
        """Compact summary for NATS event payload. ملخص مضغوط لحمولة الحدث."""
        return {
            "lai": self.lai,
            "depletion_mm": self.depletion_mm,
            "water_stress": self.water_stress,
            "phenology_stage": self.phenology_stage,
            "confidence": self.confidence,
            "assimilation_flags": [f.value for f in self.assimilation_flags],
        }


# ---------------------------------------------------------------------------
# Field Observation
# ---------------------------------------------------------------------------


class FieldObservation(BaseModel):
    """
    A single field observation used for assimilation.
    رصد حقلي واحد يُستخدم في التمثيل.

    Stored in ``field_observation`` table.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    field_id: UUID
    ts: datetime

    source: ObservationSource
    obs_type: ObservationType
    value: float
    quality: float = Field(default=0.7, ge=0.0, le=1.0)
    meta: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Irrigation Recommendation
# ---------------------------------------------------------------------------


class IrrigationRecommendation(BaseModel):
    """
    Computed irrigation recommendation for a field-day.
    توصية الري المحسوبة ليوم حقل معين.

    Stored in ``irrigation_recommendation`` table.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    field_id: UUID
    day: date

    recommended_mm: float = Field(ge=0.0)
    """Recommended irrigation depth (mm) | عمق الري الموصى به"""
    reason_codes: list[str] = Field(default_factory=list)
    """Reason codes driving the recommendation | رموز السبب"""
    explanation: dict[str, Any] = Field(default_factory=dict)
    """Bilingual explanation (en/ar) | الشرح ثنائي اللغة"""
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)

    # ── Decision Kernel additions (additive, backward-compatible) ─────────
    farmer_view: FarmerView | None = None
    """Farmer-facing slice (suggestion not command). | شريحة المزارع — اقتراح لا أمر."""
    backend_detail: BackendDetail | None = None
    """Engineering detail (raw inputs, calibration, cognitive accounting). | تفاصيل هندسية."""
    decision_chain: DecisionChain | None = None
    """Knowledge-layer trace: every step that produced this recommendation. | سلسلة القرار."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Decision Kernel views (farmer-facing vs engineering-facing)
# ---------------------------------------------------------------------------


class FarmerView(BaseModel):
    """
    Farmer-facing slice of a recommendation. Mechanically forbids fields not
    in the schema (``extra="forbid"``) so the farmer surface stays simple.
    شريحة المزارع — تَفرض schema بسيطاً ولا تقبل حقولاً غير معروفة.
    """

    model_config = ConfigDict(extra="forbid")

    signal: str = Field(pattern="^(green|yellow|red|gray)$")
    headline_ar: str = Field(min_length=1)
    headline_en: str = Field(min_length=1)
    next_action_ar: str = Field(min_length=1)
    next_action_en: str = Field(min_length=1)
    prompt_style: str = Field(default="suggestion", pattern="^(suggestion|command)$")
    """Default 'suggestion' — the platform assists, it does not command."""
    confidence_label: str = Field(default="low", pattern="^(low|medium|high)$")


class BackendDetail(BaseModel):
    """
    Engineering-facing detail. ``extra="allow"`` so services may attach
    domain-specific raw fields without schema bloat.
    تفاصيل هندسية — تَقبل حقولاً إضافية للخدمات.
    """

    model_config = ConfigDict(extra="allow")

    engines_used: list[str] = Field(default_factory=list)
    zone_factor: float | None = None
    zone_factor_status: str = Field(default="uncalibrated", pattern="^(uncalibrated|pending|calibrated)$")
    raw_inputs: dict[str, Any] = Field(default_factory=dict)
    workspace_key: str | None = None
    """Cognitive isolation key (tenant/farm/season). | مفتاح فضاء العمل."""
    compute_cost_summary: dict[str, float] = Field(default_factory=dict)
    """Cognitive accounting: {"total_ms": ..., "per_engine": {...}}. | محاسبة إدراكية."""


# Resolve forward references for IrrigationRecommendation (FarmerView/BackendDetail
# are declared after it for narrative flow).
IrrigationRecommendation.model_rebuild()
