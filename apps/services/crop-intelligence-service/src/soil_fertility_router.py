# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Soil & Fertility Router - موجّه التربة والخصوبة
=================================================
FastAPI router exposing shared/soil_testing and shared/fertilizer_management
modules through the crop-intelligence-service API.

Endpoints:
  POST /soil/interpret         – Interpret soil test results
  POST /soil/amendment-plan    – Generate amendment/fertilizer plan from soil test
  POST /soil/trends            – Analyse multi-year soil nutrient trends
  GET  /fertilizer/crops       – List supported crops with nutrient requirements
  POST /fertilizer/recommend   – Generate fertilizer recommendation
  POST /fertilizer/blend       – Calculate optimal fertilizer blend for NPK targets
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger()

router = APIRouter(tags=["Soil & Fertility"])


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header - استخراج معرف المستأجر من الهيدر"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class MacronutrientsIn(BaseModel):
    """Macronutrient lab results (ppm). نتائج العناصر الكبرى."""

    nitrogen_nitrate_ppm: float = Field(default=25.0, ge=0, description="NO₃-N (ppm)")
    phosphorus_ppm: float = Field(default=15.0, ge=0, description="P Olsen (ppm)")
    potassium_ppm: float = Field(default=180.0, ge=0, description="K (ppm)")


class SoilPropertiesIn(BaseModel):
    """Soil physical / chemical properties. خصائص التربة."""

    ph: float = Field(default=7.5, ge=3.0, le=10.0)
    ec_ds_m: float = Field(default=1.5, ge=0.0, description="EC (dS/m)")
    organic_matter_percent: float = Field(default=1.5, ge=0.0, le=100.0)


class SoilTestIn(BaseModel):
    """Input for soil test interpretation. مدخلات تحليل التربة."""

    field_id: str
    sample_date: datetime | None = None
    crop: str = Field(default="wheat", description="Target crop")
    macronutrients: MacronutrientsIn = Field(default_factory=MacronutrientsIn)
    properties: SoilPropertiesIn = Field(default_factory=SoilPropertiesIn)


class FertilizerRecommendIn(BaseModel):
    """Input for fertilizer recommendation. مدخلات توصية التسميد."""

    crop: str = Field(default="wheat")
    target_yield_tons_ha: float = Field(default=5.0, gt=0)
    field_area_hectares: float = Field(default=1.0, gt=0)
    soil_n_ppm: float = Field(default=20.0, ge=0)
    soil_p_ppm: float = Field(default=15.0, ge=0)
    soil_k_ppm: float = Field(default=150.0, ge=0)
    growth_stage: str = Field(default="seeding")


class BlendTargetsIn(BaseModel):
    """NPK blend targets (kg/ha). أهداف خلطة الأسمدة."""

    n_kg_ha: float = Field(default=100.0, ge=0)
    p2o5_kg_ha: float = Field(default=50.0, ge=0)
    k2o_kg_ha: float = Field(default=60.0, ge=0)
    field_area_hectares: float = Field(default=1.0, gt=0)


class SoilTrendIn(BaseModel):
    """Multi-year trend request. طلب اتجاهات التربة."""

    field_id: str
    tests: list[dict[str, Any]] = Field(
        ..., min_length=2, description="List of {sample_date, n_ppm, p_ppm, k_ppm, ph, ec}"
    )


# ---------------------------------------------------------------------------
# POST /soil/interpret
# ---------------------------------------------------------------------------


@router.post(
    "/soil/interpret",
    summary="Interpret soil test | تفسير تحليل التربة",
)
def interpret_soil_test(body: SoilTestIn, tenant_id: str = Depends(get_tenant_id)) -> dict:
    """
    Run soil test interpretation using shared/soil_testing module.
    تفسير نتائج تحليل التربة باستخدام وحدة التحليل المشتركة.
    """
    try:
        from shared.soil_testing import (
            MacronutrientResults,
            SoilProperties,
            SoilTestInterpreter,
            SoilTestResult,
        )
    except ImportError as exc:
        raise HTTPException(503, f"soil_testing module not available: {exc}")

    sample_date = body.sample_date or datetime.utcnow()
    result = SoilTestResult(
        id=f"api-{body.field_id}",
        tenant_id=tenant_id,
        field_id=body.field_id,
        sample_id=f"sample-{body.field_id}",
        sample_date=sample_date,
        macronutrients=MacronutrientResults(
            nitrogen_nitrate_ppm=body.macronutrients.nitrogen_nitrate_ppm,
            phosphorus_ppm=body.macronutrients.phosphorus_ppm,
            potassium_ppm=body.macronutrients.potassium_ppm,
        ),
        soil_properties=SoilProperties(
            ph=body.properties.ph,
            ec_ds_m=body.properties.ec_ds_m,
            organic_matter_percent=body.properties.organic_matter_percent,
        ),
    )

    interpreter = SoilTestInterpreter()
    report = interpreter.interpret(result, crop=body.crop)

    return {
        "field_id": body.field_id,
        "crop": body.crop,
        "report": {
            "summary": getattr(report, "summary", str(report)),
            "summary_ar": getattr(report, "summary_ar", None),
            "interpretations": getattr(report, "interpretations", []),
        },
    }


# ---------------------------------------------------------------------------
# POST /soil/amendment-plan
# ---------------------------------------------------------------------------


@router.post(
    "/soil/amendment-plan",
    summary="Generate amendment plan | خطة التعديل",
)
def generate_amendment_plan(body: SoilTestIn, tenant_id: str = Depends(get_tenant_id)) -> dict:
    """
    Generate soil amendment plan using shared/soil_testing.
    إنشاء خطة تعديل التربة.
    """
    try:
        from shared.soil_testing import (
            MacronutrientResults,
            SoilAmendmentRecommender,
            SoilProperties,
            SoilTestResult,
        )
    except ImportError as exc:
        raise HTTPException(503, f"soil_testing module not available: {exc}")

    sample_date = body.sample_date or datetime.utcnow()
    result = SoilTestResult(
        id=f"api-{body.field_id}",
        tenant_id=tenant_id,
        field_id=body.field_id,
        sample_id=f"sample-{body.field_id}",
        sample_date=sample_date,
        macronutrients=MacronutrientResults(
            nitrogen_nitrate_ppm=body.macronutrients.nitrogen_nitrate_ppm,
            phosphorus_ppm=body.macronutrients.phosphorus_ppm,
            potassium_ppm=body.macronutrients.potassium_ppm,
        ),
        soil_properties=SoilProperties(
            ph=body.properties.ph,
            ec_ds_m=body.properties.ec_ds_m,
            organic_matter_percent=body.properties.organic_matter_percent,
        ),
    )

    recommender = SoilAmendmentRecommender()
    plan = recommender.generate_plan(result, crop=body.crop)

    return {
        "field_id": body.field_id,
        "crop": body.crop,
        "plan": {
            "summary": getattr(plan, "summary", str(plan)),
            "summary_ar": getattr(plan, "summary_ar", None),
            "recommendations": getattr(plan, "recommendations", []),
        },
    }


# ---------------------------------------------------------------------------
# POST /soil/trends
# ---------------------------------------------------------------------------


@router.post(
    "/soil/trends",
    summary="Analyse soil trends | تحليل اتجاهات التربة",
)
def analyse_soil_trends(body: SoilTrendIn, tenant_id: str = Depends(get_tenant_id)) -> dict:
    """
    Analyse multi-year soil nutrient trends using shared/soil_testing.
    تحليل اتجاهات العناصر الغذائية على مدى عدة سنوات.
    """
    try:
        from shared.soil_testing import SoilTrendAnalyzer
    except ImportError as exc:
        raise HTTPException(503, f"soil_testing module not available: {exc}")

    analyzer = SoilTrendAnalyzer()
    trend_report = analyzer.analyze_trends(
        body.field_id,
        tenant_id,
        body.tests,
    )

    return {
        "field_id": body.field_id,
        "n_samples": len(body.tests),
        "trend_report": {
            "summary": getattr(trend_report, "summary", str(trend_report)),
            "summary_ar": getattr(trend_report, "summary_ar", None),
        },
    }


# ---------------------------------------------------------------------------
# GET /fertilizer/crops
# ---------------------------------------------------------------------------


@router.get(
    "/fertilizer/crops",
    summary="List crop nutrient requirements | متطلبات المحاصيل",
)
def list_crop_requirements() -> dict:
    """
    List supported crops and their nutrient requirements.
    قائمة المحاصيل ومتطلباتها الغذائية.
    """
    try:
        from shared.fertilizer_management import (
            CROP_NUTRIENT_REQUIREMENTS,
            get_supported_crops,
        )
    except ImportError as exc:
        raise HTTPException(503, f"fertilizer_management module not available: {exc}")

    return {
        "supported_crops": get_supported_crops(),
        "requirements": {
            crop: {
                "name_ar": info.get("name_ar", crop),
                "N_kg_per_ton": info.get("N"),
                "P2O5_kg_per_ton": info.get("P2O5"),
                "K2O_kg_per_ton": info.get("K2O"),
                "typical_yield_t_ha": info.get("typical_yield"),
            }
            for crop, info in CROP_NUTRIENT_REQUIREMENTS.items()
        },
    }


# ---------------------------------------------------------------------------
# POST /fertilizer/recommend
# ---------------------------------------------------------------------------


@router.post(
    "/fertilizer/recommend",
    summary="Fertilizer recommendation | توصية التسميد",
)
def recommend_fertilizer(body: FertilizerRecommendIn) -> dict:
    """
    Generate a fertilizer recommendation using shared/fertilizer_management.
    إنشاء توصية التسميد.
    """
    try:
        from shared.fertilizer_management import calculate_quick_recommendation
    except ImportError as exc:
        raise HTTPException(503, f"fertilizer_management module not available: {exc}")

    rec = calculate_quick_recommendation(
        crop=body.crop,
        soil_n_ppm=body.soil_n_ppm,
        soil_p_ppm=body.soil_p_ppm,
        soil_k_ppm=body.soil_k_ppm,
        target_yield=body.target_yield_tons_ha,
    )

    return {
        "crop": body.crop,
        "growth_stage": body.growth_stage,
        "field_area_hectares": body.field_area_hectares,
        "recommendation": rec,
    }


# ---------------------------------------------------------------------------
# POST /fertilizer/blend
# ---------------------------------------------------------------------------


@router.post(
    "/fertilizer/blend",
    summary="Calculate fertilizer blend | حساب الخلطة",
)
def calculate_blend(body: BlendTargetsIn) -> dict:
    """
    Calculate optimal fertilizer blend for NPK targets.
    حساب الخلطة المثلى للأسمدة.
    """
    try:
        from shared.fertilizer_management import calculate_blend_for_targets
    except ImportError as exc:
        raise HTTPException(503, f"fertilizer_management module not available: {exc}")

    blend = calculate_blend_for_targets(
        n_kg_ha=body.n_kg_ha,
        p_kg_ha=body.p2o5_kg_ha,
        k_kg_ha=body.k2o_kg_ha,
    )

    return {
        "targets": {
            "N": body.n_kg_ha,
            "P2O5": body.p2o5_kg_ha,
            "K2O": body.k2o_kg_ha,
        },
        "field_area_hectares": body.field_area_hectares,
        "blend": {
            "products": getattr(blend, "products", []),
            "total_cost": getattr(blend, "total_cost", None),
            "summary": str(blend),
        },
    }
