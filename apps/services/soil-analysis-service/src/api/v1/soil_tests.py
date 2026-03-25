"""
Soil analysis API endpoints - نقاط نهاية تحليل التربة
Integrates with shared.soil_testing module for business logic.
"""

import json
import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

logger = structlog.get_logger()

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


router = APIRouter(prefix="/api/v1/soil", tags=["soil-analysis"])

# In-memory storage (replaced by DB in production)
_soil_tests: dict[str, dict] = {}


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header - استخراج معرف المستأجر من الهيدر"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


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


class NutrientStatusRequest(BaseModel):
    nutrient: str = Field(..., description="Nutrient code: N, P, K, Ca, Mg, S, Fe, Mn, Zn, Cu, B")
    value: float = Field(..., ge=0, description="Value in ppm")
    extraction_method: str = "olsen"


class PhStatusRequest(BaseModel):
    ph: float = Field(..., ge=0, le=14, description="Soil pH value")


class EcStatusRequest(BaseModel):
    ec_ds_m: float = Field(..., ge=0, description="EC in dS/m")


class FertilizerRateRequest(BaseModel):
    nutrient_needed_kg_ha: float = Field(..., gt=0, description="Nutrient needed in kg/ha")
    fertilizer_nutrient_percent: float = Field(..., gt=0, le=100, description="Nutrient content in fertilizer (%)")


class NutrientTrendRequest(BaseModel):
    field_id: str
    nutrient: str = Field(..., description="Nutrient code: N, P, K, etc.")


class PeriodCompareRequest(BaseModel):
    field_id: str
    period1_start: datetime
    period1_end: datetime
    period2_start: datetime
    period2_end: datetime


class TrendRequest(BaseModel):
    field_id: str


# === Endpoints ===


@router.post("/tests", status_code=201)
async def create_soil_test(
    request: SoilTestCreateRequest,
    req: Request,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new soil test record - إنشاء سجل تحليل تربة جديد"""
    test_id = f"ST-{uuid.uuid4().hex[:8].upper()}"
    sample_id = f"SMP-{uuid.uuid4().hex[:8].upper()}"

    try:
        from shared.soil_testing import MacronutrientResults, SoilProperties, SoilTestResult

        soil_test = SoilTestResult(
            id=test_id,
            tenant_id=tenant_id,
            field_id=request.field_id,
            sample_id=sample_id,
            sample_date=request.sample_date or datetime.now(UTC),
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
            "tenant_id": tenant_id,
            "sample_date": (request.sample_date or datetime.now(UTC)).isoformat(),
            "macronutrients": request.macronutrients.model_dump(),
            "soil_properties": request.soil_properties.model_dump(),
            "notes": request.notes,
            "created_at": datetime.now(UTC).isoformat(),
            "_soil_test_obj": soil_test,
        }

        # Publish NATS event
        nc = getattr(req.app.state, "nc", None)
        if nc:
            await nc.publish(
                "sahool.soil.test_created",
                json.dumps({"test_id": test_id, "field_id": request.field_id, "tenant_id": tenant_id}).encode(),
            )

        logger.info("soil_test_created", test_id=test_id, field_id=request.field_id)
        result = {k: v for k, v in _soil_tests[test_id].items() if k != "_soil_test_obj"}
        return result

    except ImportError:
        _soil_tests[test_id] = {
            "id": test_id,
            "sample_id": sample_id,
            "field_id": request.field_id,
            "tenant_id": tenant_id,
            "sample_date": (request.sample_date or datetime.now(UTC)).isoformat(),
            "macronutrients": request.macronutrients.model_dump(),
            "soil_properties": request.soil_properties.model_dump(),
            "notes": request.notes,
            "created_at": datetime.now(UTC).isoformat(),
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
async def delete_soil_test(test_id: str, current_user: User = Depends(get_current_user)):
    """Delete soil test - حذف تحليل التربة"""
    if test_id not in _soil_tests:
        raise HTTPException(status_code=404, detail={"error": "Test not found", "error_ar": "التحليل غير موجود"})
    del _soil_tests[test_id]
    logger.info("soil_test_deleted", test_id=test_id)


@router.post("/interpret")
async def interpret_soil_test(request: InterpretRequest, req: Request, current_user: User = Depends(get_current_user)):
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

        result = {
            "test_id": request.test_id,
            "crop": request.crop,
            "summary": report.summary_en,
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

        # Publish NATS event for interpretation completed
        nc = getattr(req.app.state, "nc", None)
        if nc:
            try:
                await nc.publish(
                    "sahool.soil.test_interpreted",
                    json.dumps(
                        {
                            "test_id": request.test_id,
                            "crop": request.crop,
                            "overall_health": report.overall_health,
                            "field_id": test_data.get("field_id"),
                            "tenant_id": test_data.get("tenant_id"),
                        }
                    ).encode(),
                )
            except Exception:
                logger.warning("nats_publish_failed", subject="sahool.soil.test_interpreted")

        return result
    except ImportError:
        return {
            "test_id": request.test_id,
            "crop": request.crop,
            "summary": "Soil interpretation module not available",
            "summary_ar": "وحدة تفسير التربة غير متوفرة",
            "interpretations": [],
        }


@router.post("/recommendations/amendment-plan")
async def generate_amendment_plan(request: AmendmentPlanRequest, req: Request, current_user: User = Depends(get_current_user)):
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
        plan = recommender.generate_plan(
            soil_test_obj, crop=request.crop, target_yield=request.target_yield_t_ha, field_area_ha=request.area_ha
        )

        result = {
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

        # Publish NATS event for amendment plan generated
        nc = getattr(req.app.state, "nc", None)
        if nc:
            try:
                await nc.publish(
                    "sahool.soil.amendment_plan_generated",
                    json.dumps(
                        {
                            "test_id": request.test_id,
                            "crop": request.crop,
                            "area_ha": request.area_ha,
                            "total_cost": plan.total_cost,
                            "field_id": test_data.get("field_id"),
                            "tenant_id": test_data.get("tenant_id"),
                        }
                    ).encode(),
                )
            except Exception:
                logger.warning("nats_publish_failed", subject="sahool.soil.amendment_plan_generated")

        return result
    except ImportError:
        return {
            "test_id": request.test_id,
            "summary": "Amendment recommendation module not available",
            "summary_ar": "وحدة توصيات التعديل غير متوفرة",
            "recommendations": [],
        }


@router.post("/trends")
async def analyze_soil_trends(request: TrendRequest, req: Request, tenant_id: str = Depends(get_tenant_id), current_user: User = Depends(get_current_user)):
    """Analyze soil trends for a field - تحليل اتجاهات التربة للحقل"""
    field_tests = [t for t in _soil_tests.values() if t["field_id"] == request.field_id and t["tenant_id"] == tenant_id]

    if not field_tests:
        return {
            "field_id": request.field_id,
            "message": "No soil tests found for this field",
            "message_ar": "لا توجد تحاليل تربة لهذا الحقل",
            "trends": [],
        }

    try:
        from shared.soil_testing import SoilTrendAnalyzer

        soil_test_objs = [t["_soil_test_obj"] for t in field_tests if "_soil_test_obj" in t]
        if not soil_test_objs:
            return {"field_id": request.field_id, "message": "No processable tests", "trends": []}

        analyzer = SoilTrendAnalyzer()
        report = analyzer.analyze_trends(request.field_id, tenant_id, soil_test_objs)

        result = {
            "field_id": request.field_id,
            "summary": report.summary_en,
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

        # Publish NATS event for trends analyzed
        nc = getattr(req.app.state, "nc", None)
        if nc:
            try:
                await nc.publish(
                    "sahool.soil.trends_analyzed",
                    json.dumps(
                        {
                            "field_id": request.field_id,
                            "tenant_id": tenant_id,
                            "trends_count": len(report.trends),
                        }
                    ).encode(),
                )
            except Exception:
                logger.warning("nats_publish_failed", subject="sahool.soil.trends_analyzed")

        return result
    except ImportError:
        return {
            "field_id": request.field_id,
            "message": "Trend analysis module not available",
            "message_ar": "وحدة تحليل الاتجاهات غير متوفرة",
            "trends": [],
        }


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


@router.post("/interpretation/nutrient-status")
async def check_nutrient_status(request: NutrientStatusRequest, current_user: User = Depends(get_current_user)):
    """Check individual nutrient status - فحص حالة عنصر غذائي فردي"""
    try:
        from shared.soil_testing import get_nutrient_status
        from shared.soil_testing.models import ExtractionMethod

        method = ExtractionMethod(request.extraction_method)
        status, description_en, description_ar = get_nutrient_status(
            nutrient=request.nutrient,
            value=request.value,
            extraction_method=method,
        )
        return {
            "nutrient": request.nutrient,
            "value": request.value,
            "status": status.value if hasattr(status, "value") else str(status),
            "description": description_en,
            "description_ar": description_ar,
            "extraction_method": request.extraction_method,
        }
    except ImportError:
        return {
            "nutrient": request.nutrient,
            "value": request.value,
            "status": None,
            "message": "Nutrient status module not available",
        }


@router.post("/interpretation/ph-status")
async def check_ph_status(request: PhStatusRequest, current_user: User = Depends(get_current_user)):
    """Check soil pH status - فحص حالة حموضة التربة"""
    try:
        from shared.soil_testing import get_ph_status

        status_en, status_ar = get_ph_status(request.ph)
        return {"ph": request.ph, "status": status_en, "status_ar": status_ar}
    except ImportError:
        return {"ph": request.ph, "status": None, "message": "pH status module not available"}


@router.post("/interpretation/ec-status")
async def check_ec_status(request: EcStatusRequest, current_user: User = Depends(get_current_user)):
    """Check soil EC/salinity status - فحص حالة ملوحة التربة"""
    try:
        from shared.soil_testing import get_ec_status

        status_en, status_ar = get_ec_status(request.ec_ds_m)
        return {"ec_ds_m": request.ec_ds_m, "status": status_en, "status_ar": status_ar}
    except ImportError:
        return {"ec_ds_m": request.ec_ds_m, "status": None, "message": "EC status module not available"}


@router.post("/recommendations/calculate-rate")
async def calculate_rate(request: FertilizerRateRequest, current_user: User = Depends(get_current_user)):
    """Calculate fertilizer application rate - حساب معدل تطبيق السماد"""
    try:
        from shared.soil_testing import calculate_fertilizer_rate

        rate_kg_ha = calculate_fertilizer_rate(
            nutrient_needed_kg_ha=request.nutrient_needed_kg_ha,
            fertilizer_nutrient_percent=request.fertilizer_nutrient_percent,
        )
        return {
            "nutrient_needed_kg_ha": request.nutrient_needed_kg_ha,
            "fertilizer_nutrient_percent": request.fertilizer_nutrient_percent,
            "application_rate_kg_ha": round(rate_kg_ha, 2),
        }
    except ImportError:
        return {"application_rate_kg_ha": None, "message": "Rate calculation module not available"}


@router.post("/trends/nutrient")
async def get_single_nutrient_trend(request: NutrientTrendRequest, tenant_id: str = Depends(get_tenant_id), current_user: User = Depends(get_current_user)):
    """Get trend for a specific nutrient - الحصول على اتجاه عنصر غذائي محدد"""
    field_tests = [t for t in _soil_tests.values() if t["field_id"] == request.field_id and t["tenant_id"] == tenant_id]

    if not field_tests:
        return {
            "field_id": request.field_id,
            "nutrient": request.nutrient,
            "message": "No soil tests found",
            "message_ar": "لا توجد تحاليل تربة",
        }

    try:
        from shared.soil_testing import get_nutrient_trend

        soil_test_objs = [t["_soil_test_obj"] for t in field_tests if "_soil_test_obj" in t]
        if not soil_test_objs:
            return {"field_id": request.field_id, "nutrient": request.nutrient, "message": "No processable tests"}

        trend = get_nutrient_trend(soil_test_objs, nutrient=request.nutrient)
        return {
            "field_id": request.field_id,
            "nutrient": trend.nutrient_code,
            "nutrient_name": trend.nutrient_name,
            "nutrient_name_ar": trend.nutrient_name_ar,
            "unit": trend.unit,
        }
    except ImportError:
        return {
            "field_id": request.field_id,
            "nutrient": request.nutrient,
            "message": "Nutrient trend module not available",
        }


@router.post("/trends/compare-periods")
async def compare_periods(request: PeriodCompareRequest, tenant_id: str = Depends(get_tenant_id), current_user: User = Depends(get_current_user)):
    """Compare soil health between two periods - مقارنة صحة التربة بين فترتين"""
    field_tests = [t for t in _soil_tests.values() if t["field_id"] == request.field_id and t["tenant_id"] == tenant_id]

    if not field_tests:
        return {"field_id": request.field_id, "message": "No soil tests found", "message_ar": "لا توجد تحاليل تربة"}

    try:
        from shared.soil_testing import compare_soil_periods

        soil_test_objs = [t["_soil_test_obj"] for t in field_tests if "_soil_test_obj" in t]
        if not soil_test_objs:
            return {"field_id": request.field_id, "message": "No processable tests"}

        comparison = compare_soil_periods(
            soil_test_objs,
            period1_start=request.period1_start,
            period1_end=request.period1_end,
            period2_start=request.period2_start,
            period2_end=request.period2_end,
        )
        return {"field_id": request.field_id, "comparison": comparison}
    except ImportError:
        return {"field_id": request.field_id, "message": "Period comparison module not available"}
