"""
Soil analysis API endpoints - نقاط نهاية تحليل التربة
Integrates with shared.soil_testing module for business logic.
"""

import json
import uuid
from datetime import datetime
from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/soil", tags=["soil-analysis"])

# In-memory storage (replaced by DB in production)
_soil_tests: dict[str, dict] = {}


# === Request/Response Models ===


class MacronutrientsInput(BaseModel):
    nitrogen_nitrate_ppm: float = Field(..., ge=0, description="Nitrogen (NO3) ppm")
    phosphorus_ppm: float = Field(..., ge=0, description="Phosphorus ppm")
    potassium_ppm: float = Field(..., ge=0, description="Potassium ppm")
    calcium_ppm: float | None = None
    magnesium_ppm: float | None = None
    sulfur_ppm: float | None = None


class SoilPropertiesInput(BaseModel):
    ph: float = Field(..., ge=0, le=14, description="Soil pH")
    ec_ds_m: float = Field(..., ge=0, description="EC dS/m")
    organic_matter_percent: float = Field(..., ge=0, le=100)
    cec_meq_100g: float | None = None


class SoilTestCreateRequest(BaseModel):
    field_id: str
    tenant_id: str
    sample_date: datetime | None = None
    sample_depth_cm: float = 30.0
    macronutrients: MacronutrientsInput
    soil_properties: SoilPropertiesInput
    notes: str | None = None
    notes_ar: str | None = None


class InterpretRequest(BaseModel):
    test_id: str
    crop: str = "wheat"


class AmendmentPlanRequest(BaseModel):
    test_id: str
    crop: str = "wheat"
    target_yield_t_ha: float = 5.0
    area_ha: float = 1.0


class TrendRequest(BaseModel):
    field_id: str
    tenant_id: str


# === Endpoints ===


@router.post("/tests", status_code=201)
async def create_soil_test(request: SoilTestCreateRequest, req: Request):
    """Create a new soil test record - إنشاء سجل تحليل تربة جديد"""
    test_id = f"ST-{uuid.uuid4().hex[:8].upper()}"
    sample_id = f"SMP-{uuid.uuid4().hex[:8].upper()}"

    try:
        from shared.soil_testing import MacronutrientResults, SoilProperties, SoilTestResult

        soil_test = SoilTestResult(
            id=test_id,
            tenant_id=request.tenant_id,
            field_id=request.field_id,
            sample_id=sample_id,
            sample_date=request.sample_date or datetime.utcnow(),
            macronutrients=MacronutrientResults(
                nitrogen_nitrate_ppm=request.macronutrients.nitrogen_nitrate_ppm,
                phosphorus_ppm=request.macronutrients.phosphorus_ppm,
                potassium_ppm=request.macronutrients.potassium_ppm,
            ),
            soil_properties=SoilProperties(
                ph=request.soil_properties.ph,
                ec_ds_m=request.soil_properties.ec_ds_m,
                organic_matter_percent=request.soil_properties.organic_matter_percent,
            ),
        )

        _soil_tests[test_id] = {
            "id": test_id,
            "sample_id": sample_id,
            "field_id": request.field_id,
            "tenant_id": request.tenant_id,
            "sample_date": (request.sample_date or datetime.utcnow()).isoformat(),
            "macronutrients": request.macronutrients.model_dump(),
            "soil_properties": request.soil_properties.model_dump(),
            "notes": request.notes,
            "created_at": datetime.utcnow().isoformat(),
            "_soil_test_obj": soil_test,
        }

        # Publish NATS event
        nc = getattr(req.app.state, "nc", None)
        if nc:
            await nc.publish(
                "sahool.soil.test_created",
                json.dumps({"test_id": test_id, "field_id": request.field_id, "tenant_id": request.tenant_id}).encode(),
            )

        logger.info("soil_test_created", test_id=test_id, field_id=request.field_id)
        result = {k: v for k, v in _soil_tests[test_id].items() if k != "_soil_test_obj"}
        return result

    except ImportError:
        _soil_tests[test_id] = {
            "id": test_id,
            "sample_id": sample_id,
            "field_id": request.field_id,
            "tenant_id": request.tenant_id,
            "sample_date": (request.sample_date or datetime.utcnow()).isoformat(),
            "macronutrients": request.macronutrients.model_dump(),
            "soil_properties": request.soil_properties.model_dump(),
            "notes": request.notes,
            "created_at": datetime.utcnow().isoformat(),
        }
        return _soil_tests[test_id]


@router.get("/tests/{test_id}")
async def get_soil_test(test_id: str):
    """Get soil test by ID - الحصول على تحليل التربة"""
    if test_id not in _soil_tests:
        raise HTTPException(status_code=404, detail={"error": "Test not found", "error_ar": "التحليل غير موجود"})
    result = {k: v for k, v in _soil_tests[test_id].items() if k != "_soil_test_obj"}
    return result


@router.get("/tests/field/{field_id}")
async def get_field_soil_tests(field_id: str):
    """Get all soil tests for a field - الحصول على جميع تحاليل التربة للحقل"""
    tests = [
        {k: v for k, v in t.items() if k != "_soil_test_obj"} for t in _soil_tests.values() if t["field_id"] == field_id
    ]
    return {"field_id": field_id, "tests": tests, "count": len(tests)}


@router.delete("/tests/{test_id}", status_code=204)
async def delete_soil_test(test_id: str):
    """Delete soil test - حذف تحليل التربة"""
    if test_id not in _soil_tests:
        raise HTTPException(status_code=404, detail={"error": "Test not found", "error_ar": "التحليل غير موجود"})
    del _soil_tests[test_id]
    logger.info("soil_test_deleted", test_id=test_id)


@router.post("/interpret")
async def interpret_soil_test(request: InterpretRequest):
    """Interpret soil test results - تفسير نتائج تحليل التربة"""
    if request.test_id not in _soil_tests:
        raise HTTPException(status_code=404, detail={"error": "Test not found", "error_ar": "التحليل غير موجود"})

    test_data = _soil_tests[request.test_id]

    try:
        from shared.soil_testing import SoilTestInterpreter

        soil_test_obj = test_data.get("_soil_test_obj")
        if not soil_test_obj:
            raise HTTPException(status_code=400, detail="Soil test object not available for interpretation")

        interpreter = SoilTestInterpreter()
        report = interpreter.interpret(soil_test_obj, crop=request.crop)
        return {
            "test_id": request.test_id,
            "crop": request.crop,
            "summary": report.summary,
            "summary_ar": report.summary_ar,
            "interpretations": [
                {
                    "nutrient": i.nutrient,
                    "value": i.value,
                    "status": i.status.value if hasattr(i.status, "value") else str(i.status),
                    "recommendation": i.recommendation,
                    "recommendation_ar": i.recommendation_ar,
                }
                for i in report.interpretations
            ],
            "overall_health": report.overall_health,
        }
    except ImportError:
        return {
            "test_id": request.test_id,
            "crop": request.crop,
            "summary": "Soil interpretation module not available",
            "summary_ar": "وحدة تفسير التربة غير متوفرة",
            "interpretations": [],
        }


@router.post("/recommendations/amendment-plan")
async def generate_amendment_plan(request: AmendmentPlanRequest):
    """Generate soil amendment plan - إنشاء خطة تعديل التربة"""
    if request.test_id not in _soil_tests:
        raise HTTPException(status_code=404, detail={"error": "Test not found", "error_ar": "التحليل غير موجود"})

    test_data = _soil_tests[request.test_id]

    try:
        from shared.soil_testing import SoilAmendmentRecommender

        soil_test_obj = test_data.get("_soil_test_obj")
        if not soil_test_obj:
            raise HTTPException(status_code=400, detail="Soil test object not available")

        recommender = SoilAmendmentRecommender()
        plan = recommender.generate_plan(soil_test_obj, crop=request.crop, area_ha=request.area_ha)
        return {
            "test_id": request.test_id,
            "crop": request.crop,
            "area_ha": request.area_ha,
            "summary": plan.summary,
            "summary_ar": plan.summary_ar,
            "recommendations": [
                {
                    "product": r.product,
                    "rate_kg_ha": r.rate_kg_ha,
                    "total_kg": r.total_kg,
                    "cost_estimate": getattr(r, "cost_estimate", None),
                    "application_method": r.application_method,
                    "timing": r.timing,
                }
                for r in plan.recommendations
            ],
            "total_cost": plan.total_cost,
        }
    except ImportError:
        return {
            "test_id": request.test_id,
            "summary": "Amendment recommendation module not available",
            "summary_ar": "وحدة توصيات التعديل غير متوفرة",
            "recommendations": [],
        }


@router.post("/trends")
async def analyze_soil_trends(request: TrendRequest):
    """Analyze soil trends for a field - تحليل اتجاهات التربة للحقل"""
    field_tests = [t for t in _soil_tests.values() if t["field_id"] == request.field_id and t["tenant_id"] == request.tenant_id]

    if not field_tests:
        return {"field_id": request.field_id, "message": "No soil tests found for this field", "message_ar": "لا توجد تحاليل تربة لهذا الحقل", "trends": []}

    try:
        from shared.soil_testing import SoilTrendAnalyzer

        soil_test_objs = [t["_soil_test_obj"] for t in field_tests if "_soil_test_obj" in t]
        if not soil_test_objs:
            return {"field_id": request.field_id, "message": "No processable tests", "trends": []}

        analyzer = SoilTrendAnalyzer()
        report = analyzer.analyze_trends(request.field_id, request.tenant_id, soil_test_objs)
        return {
            "field_id": request.field_id,
            "summary": report.summary,
            "summary_ar": report.summary_ar,
            "trends": [
                {
                    "nutrient": t.nutrient,
                    "direction": t.direction,
                    "change_percent": t.change_percent,
                }
                for t in report.trends
            ],
        }
    except ImportError:
        return {"field_id": request.field_id, "message": "Trend analysis module not available", "message_ar": "وحدة تحليل الاتجاهات غير متوفرة", "trends": []}


@router.get("/products")
async def list_fertilizer_products():
    """List available fertilizer products - قائمة المنتجات السمادية المتاحة"""
    try:
        from shared.soil_testing import FERTILIZER_PRODUCTS

        return {"products": FERTILIZER_PRODUCTS, "count": len(FERTILIZER_PRODUCTS)}
    except ImportError:
        return {"products": [], "count": 0, "message": "Products data not available"}


@router.get("/crops/{crop}/requirements")
async def get_crop_nutrient_requirements(crop: str):
    """Get nutrient requirements for a crop - الحصول على متطلبات المحصول من العناصر الغذائية"""
    try:
        from shared.soil_testing import get_crop_requirements

        reqs = get_crop_requirements(crop)
        return {"crop": crop, "requirements": reqs}
    except ImportError:
        return {"crop": crop, "requirements": None, "message": "Crop requirements data not available"}
