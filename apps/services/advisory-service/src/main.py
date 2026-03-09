"""
SAHOOL Advisory Service - Main API Service
Disease diagnosis, nutrient assessment, and fertilizer planning
Port: 8093
"""

# Service version - single source of truth
VERSION = "16.0.0"

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query

# Shared middleware imports - add apps/services/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel, Field

# Add shared modules to path (for crops, yemen_varieties etc.)
# In Docker, shared is at /app/shared
SHARED_PATH = Path("/app/shared")
if not SHARED_PATH.exists():
    # Fallback for local development
    SHARED_PATH = Path(__file__).parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

# Import unified error handling
# Import shared crop catalogs
from crops import (
    ALL_CROPS,
    CATEGORIES_COUNT,
    CropCategory,
    get_crop,
    get_crops_by_category,
)
from crops import (
    search_crops as search_crops_catalog,
)
from yemen_varieties import (
    get_varieties_by_crop,
)

import structlog

logger = structlog.get_logger()

from shared.errors_py import (
    add_request_id_middleware,
    create_success_response,
    setup_exception_handlers,
)

# Import authentication dependencies
from shared.auth.dependencies import get_current_user
from shared.auth.models import User


from .engine import (
    CROP_REQUIREMENTS,
    assess_from_image_event,
    assess_from_ndvi,
    assess_from_symptoms,
    assess_from_visual,
    fertilizer_plan,
    get_action_details,
    get_stage_timeline,
)
from .events import get_publisher
from .kb import (
    get_deficiency,
    get_disease,
    get_diseases_by_crop,
    get_fertilizer,
    get_fertilizers_for_nutrient,
    search_diseases,
)

# Import token revocation
try:
    from shared.auth.revocation_middleware import TokenRevocationMiddleware
    from shared.auth.token_revocation import get_revocation_store

    REVOCATION_AVAILABLE = True
except ImportError:
    REVOCATION_AVAILABLE = False


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - initialize state first to avoid AttributeError
    app.state.publisher = None
    app.state.revocation_store = None
    logger.info("service_starting", service="advisory-service")
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        logger.info("service_ready", service="advisory-service", port=8093)
    except Exception as e:
        logger.warning("nats_connection_failed", error=str(e))

    # Initialize token revocation store
    if REVOCATION_AVAILABLE:
        try:
            revocation_store = get_revocation_store()
            await revocation_store.initialize()
            app.state.revocation_store = revocation_store
            logger.info("token_revocation_store_initialized")
        except Exception as e:
            logger.warning("token_revocation_store_failed", error=str(e))

    yield

    # Shutdown
    if getattr(app.state, "publisher", None):
        await app.state.publisher.close()
    if getattr(app.state, "revocation_store", None):
        await app.state.revocation_store.close()
    logger.info("service_shutting_down", service="advisory-service")


app = FastAPI(
    title="SAHOOL Advisory Service",
    description="Disease diagnosis, nutrient assessment, and fertilizer planning for Yemen agriculture",
    version=VERSION,
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Add token revocation middleware
if REVOCATION_AVAILABLE:
    app.add_middleware(
        TokenRevocationMiddleware,
        exempt_paths=["/healthz", "/health", "/docs", "/redoc", "/openapi.json"],
    )

# Add tenant context middleware
try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    app.add_middleware(
        TenantContextMiddleware,
        require_tenant=False,
    )
except ImportError:
    pass


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "advisory_service", "version": VERSION}


@app.get("/readyz")
def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    # Check if service is ready
    engine_loaded = bool(CROP_REQUIREMENTS)
    checks = {
        "service": "ready",
        "engine": "loaded" if engine_loaded else "not_loaded",
    }

    # Service is ready if engine is loaded
    is_ready = engine_loaded

    if not is_ready:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            content={"status": "not_ready", "service": "advisory_service", "checks": checks},
            status_code=503,
        )

    return {
        "status": "ready",
        "service": "advisory_service",
        "version": VERSION,
        "checks": checks,
    }


# ============== Request/Response Models ==============


class DiseaseAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    condition_id: str
    confidence: float = Field(ge=0, le=1)
    crop: str | None = None
    weather: dict | None = None
    correlation_id: str | None = None


class SymptomAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    symptoms: list[str]
    lang: str = "ar"
    correlation_id: str | None = None


class NDVIAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    ndvi: float = Field(ge=-1, le=1)
    ndvi_history: list[float] | None = None
    crop: str | None = None
    stage: str | None = None
    correlation_id: str | None = None


class VisualAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    leaf_color: str | None = None
    pattern: str | None = None
    location: str | None = None
    crop: str | None = None
    lang: str = "ar"
    correlation_id: str | None = None


class FertilizerPlanRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    stage: str
    field_size_ha: float = 1.0
    soil_fertility: str = "medium"
    irrigation_type: str = "drip"
    correlation_id: str | None = None


# ============== Helper Functions ==============


def _enforce_tenant(user: User, requested_tenant_id: str) -> None:
    """Validate JWT tenant matches the requested tenant."""
    if user.tenant_id and user.tenant_id != requested_tenant_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail={
                "error": "tenant_mismatch",
                "message_ar": "لا يمكنك الوصول إلى بيانات مستأجر آخر",
                "message_en": "Cannot access another tenant's data",
            },
        )


# ============== Disease Endpoints ==============


@app.post("/api/v1/disease/assess")
async def assess_disease(req: DiseaseAssessRequest, user: User = Depends(get_current_user)):
    """Assess disease from image classification result"""
    _enforce_tenant(user, req.tenant_id)

    assessment = assess_from_image_event(
        condition_id=req.condition_id,
        confidence=req.confidence,
        crop=req.crop,
        weather_context=req.weather,
    )

    if not assessment:
        return {
            "field_id": req.field_id,
            "result": None,
            "message": "Confidence too low or unknown condition",
        }

    # Publish event
    event_id = None
    if getattr(app.state, "publisher", None):
        event_id = await app.state.publisher.publish_recommendation(
            tenant_id=req.tenant_id,
            field_id=req.field_id,
            category=assessment.category,
            severity=assessment.severity,
            title_ar=assessment.title_ar,
            title_en=assessment.title_en,
            actions=assessment.actions,
            confidence=assessment.confidence,
            correlation_id=req.correlation_id,
            details=assessment.details,
        )

    return {
        "field_id": req.field_id,
        "result": assessment.to_dict(),
        "event_id": event_id,
        "published": event_id is not None,
    }


@app.post("/api/v1/disease/symptoms")
async def assess_symptoms(req: SymptomAssessRequest, user: User = Depends(get_current_user)):
    """Assess possible diseases from reported symptoms"""
    _enforce_tenant(user, req.tenant_id)

    assessments = assess_from_symptoms(
        symptoms=req.symptoms,
        crop=req.crop,
        lang=req.lang,
    )

    if not assessments:
        return {
            "field_id": req.field_id,
            "results": [],
            "message": "No matching diseases found",
        }

    # Publish top result as recommendation
    event_id = None
    if getattr(app.state, "publisher", None) and assessments:
        top = assessments[0]
        if top.confidence >= 0.5:
            event_id = await app.state.publisher.publish_recommendation(
                tenant_id=req.tenant_id,
                field_id=req.field_id,
                category=top.category,
                severity=top.severity,
                title_ar=top.title_ar,
                title_en=top.title_en,
                actions=top.actions,
                confidence=top.confidence,
                correlation_id=req.correlation_id,
            )

    return {
        "field_id": req.field_id,
        "results": [a.to_dict() for a in assessments],
        "event_id": event_id,
    }


# NOTE: Static routes MUST come before dynamic routes to avoid path matching issues
@app.get("/api/v1/disease/search")
def search_disease(q: str, lang: str = "ar"):
    """Search diseases by name or symptoms"""
    results = search_diseases(q, lang)
    return {"query": q, "results": results, "count": len(results)}


@app.get("/api/v1/disease/crop/{crop}")
def get_crop_diseases(crop: str):
    """Get all diseases for a specific crop"""
    diseases = get_diseases_by_crop(crop)
    return {"crop": crop, "diseases": diseases, "count": len(diseases)}


@app.get("/api/v1/disease/{disease_id}")
def get_disease_info(disease_id: str, lang: str = "ar"):
    """Get disease information by ID"""
    disease = get_disease(disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail=f"Disease not found: {disease_id}")

    return create_success_response(
        {
            "id": disease_id,
            **disease,
            "actions_details": [get_action_details(action, lang) for action in disease["actions"]],
        }
    )


# ============== Nutrient Endpoints ==============


@app.post("/api/v1/nutrient/ndvi")
async def assess_from_ndvi_endpoint(req: NDVIAssessRequest, user: User = Depends(get_current_user)):
    """Assess nutrient deficiency from NDVI data"""
    _enforce_tenant(user, req.tenant_id)

    assessments = assess_from_ndvi(
        ndvi=req.ndvi,
        ndvi_history=req.ndvi_history,
        crop=req.crop,
        growth_stage=req.stage,
    )

    # Publish top result
    event_id = None
    if getattr(app.state, "publisher", None) and assessments:
        top = assessments[0]
        event_id = await app.state.publisher.publish_nutrient_assessment(
            tenant_id=req.tenant_id,
            field_id=req.field_id,
            deficiency_id=top.deficiency_id,
            nutrient=top.nutrient,
            severity=top.severity,
            title_ar=top.title_ar,
            title_en=top.title_en,
            corrections=top.corrections,
            confidence=top.confidence,
            correlation_id=req.correlation_id,
        )

    return {
        "field_id": req.field_id,
        "ndvi": req.ndvi,
        "results": [a.to_dict() for a in assessments],
        "event_id": event_id,
    }


@app.post("/api/v1/nutrient/visual")
async def assess_visual_endpoint(req: VisualAssessRequest, user: User = Depends(get_current_user)):
    """Assess nutrient deficiency from visual indicators"""
    _enforce_tenant(user, req.tenant_id)

    indicators = {
        "leaf_color": req.leaf_color,
        "pattern": req.pattern,
        "location": req.location,
    }

    assessments = assess_from_visual(indicators, req.crop, req.lang)

    # Publish top result
    event_id = None
    if getattr(app.state, "publisher", None) and assessments:
        top = assessments[0]
        event_id = await app.state.publisher.publish_nutrient_assessment(
            tenant_id=req.tenant_id,
            field_id=req.field_id,
            deficiency_id=top.deficiency_id,
            nutrient=top.nutrient,
            severity=top.severity,
            title_ar=top.title_ar,
            title_en=top.title_en,
            corrections=top.corrections,
            confidence=top.confidence,
            correlation_id=req.correlation_id,
        )

    return {
        "field_id": req.field_id,
        "indicators": indicators,
        "results": [a.to_dict() for a in assessments],
        "event_id": event_id,
    }


@app.get("/api/v1/nutrient/{deficiency_id}")
def get_deficiency_info(deficiency_id: str):
    """Get nutrient deficiency information by ID"""
    deficiency = get_deficiency(deficiency_id)
    if not deficiency:
        raise HTTPException(status_code=404, detail=f"Deficiency not found: {deficiency_id}")

    return create_success_response({"id": deficiency_id, **deficiency})


# ============== Fertilizer Endpoints ==============


@app.post("/api/v1/fertilizer/plan")
async def create_fertilizer_plan(req: FertilizerPlanRequest, user: User = Depends(get_current_user)):
    """Generate fertilizer plan for crop and stage"""
    _enforce_tenant(user, req.tenant_id)

    plan = fertilizer_plan(
        crop=req.crop,
        stage=req.stage,
        field_size_ha=req.field_size_ha,
        soil_fertility=req.soil_fertility,
        irrigation_type=req.irrigation_type,
    )

    # Publish event
    event_id = None
    if getattr(app.state, "publisher", None):
        event_id = await app.state.publisher.publish_fertilizer_plan(
            tenant_id=req.tenant_id,
            field_id=req.field_id,
            crop=req.crop,
            stage=req.stage,
            plan=plan.applications,
            correlation_id=req.correlation_id,
            notes=plan.notes,
        )

    return {
        "field_id": req.field_id,
        **plan.to_dict(),
        "event_id": event_id,
        "published": event_id is not None,
    }


@app.get("/api/v1/fertilizer/{fertilizer_id}")
def get_fertilizer_info(fertilizer_id: str):
    """Get fertilizer information by ID"""
    fert = get_fertilizer(fertilizer_id)
    if not fert:
        raise HTTPException(status_code=404, detail=f"Fertilizer not found: {fertilizer_id}")

    return create_success_response({"id": fertilizer_id, **fert})


@app.get("/api/v1/fertilizer/nutrient/{nutrient}")
def get_fertilizers_by_nutrient(nutrient: str):
    """Get fertilizers that provide a specific nutrient"""
    fertilizers = get_fertilizers_for_nutrient(nutrient.upper())
    return {"nutrient": nutrient, "fertilizers": fertilizers, "count": len(fertilizers)}


# ============== Crop Information ==============


@app.get("/api/v1/crops/categories")
def list_categories():
    """List crop categories with counts"""
    categories = []
    for category in CropCategory:
        crops_in_category = get_crops_by_category(category)
        categories.append(
            {
                "code": category.value,
                "name_en": category.value.replace("_", " ").title(),
                "count": len(crops_in_category),
                "crops": [crop.code for crop in crops_in_category],
            }
        )

    return {
        "categories": categories,
        "total_categories": len(categories),
        "total_crops": len(ALL_CROPS),
    }


@app.get("/api/v1/crops/search")
def search_crops_endpoint(q: str):
    """Search crops by Arabic or English name"""
    if not q or len(q) < 2:
        raise HTTPException(status_code=422, detail="Query must be at least 2 characters")

    results = search_crops_catalog(q)

    return {
        "query": q,
        "results": [
            {
                "code": crop.code,
                "name_en": crop.name_en,
                "name_ar": crop.name_ar,
                "scientific_name": crop.scientific_name,
                "category": crop.category.value,
                "growth_habit": crop.growth_habit.value,
                "growing_season_days": crop.growing_season_days,
                "water_requirement": crop.water_requirement.value,
                "base_yield_ton_ha": crop.base_yield_ton_ha,
                "yemen_regions": crop.yemen_regions or [],
                "local_varieties": crop.local_varieties or [],
            }
            for crop in results
        ],
        "count": len(results),
    }


@app.get("/api/v1/crops")
def list_all_crops(
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of crops per category"),
    offset: int = Query(default=0, ge=0, description="Number of crops to skip per category"),
):
    """List all crops grouped by category with pagination"""
    crops_by_category = {}
    total_crops = 0

    for category in CropCategory:
        crops_in_category = get_crops_by_category(category)
        # Apply pagination per category
        paginated_crops = crops_in_category[offset : offset + limit]
        crops_by_category[category.value] = [
            {
                "code": crop.code,
                "name_en": crop.name_en,
                "name_ar": crop.name_ar,
                "scientific_name": crop.scientific_name,
                "growing_season_days": crop.growing_season_days,
                "base_yield_ton_ha": crop.base_yield_ton_ha,
                "water_requirement": crop.water_requirement.value,
                "yemen_regions": crop.yemen_regions or [],
                "has_local_varieties": bool(crop.local_varieties),
            }
            for crop in paginated_crops
        ]
        total_crops += len(crops_in_category)

    return {
        "categories": crops_by_category,
        "total_crops": total_crops,
        "limit": limit,
        "offset": offset,
        "category_counts": CATEGORIES_COUNT,
    }


@app.get("/api/v1/crops/{crop_code}")
def get_crop_details(crop_code: str):
    """Get single crop details with Yemen varieties"""
    crop = get_crop(crop_code)
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop not found: {crop_code}")

    # Get Yemen varieties for this crop
    varieties = get_varieties_by_crop(crop_code)

    return {
        "code": crop.code,
        "name_en": crop.name_en,
        "name_ar": crop.name_ar,
        "scientific_name": crop.scientific_name,
        "category": crop.category.value,
        "growth_habit": crop.growth_habit.value,
        "growing_conditions": {
            "growing_season_days": crop.growing_season_days,
            "optimal_temp_min": crop.optimal_temp_min,
            "optimal_temp_max": crop.optimal_temp_max,
            "water_requirement": crop.water_requirement.value,
        },
        "yield_data": {
            "base_yield_ton_ha": crop.base_yield_ton_ha,
            "yield_unit": crop.yield_unit,
        },
        "yemen_specific": {
            "suitable_regions": crop.yemen_regions or [],
            "local_varieties": crop.local_varieties or [],
            "variety_count": len(varieties),
        },
        "coefficients": {
            "kc_ini": crop.kc_ini,
            "kc_mid": crop.kc_mid,
            "kc_end": crop.kc_end,
        },
        "economics": {
            "price_usd_per_ton": crop.price_usd_per_ton,
        },
        "varieties_available": len(varieties),
    }


@app.get("/api/v1/crops/{crop_code}/varieties")
def get_crop_varieties(crop_code: str):
    """Get Yemen-specific varieties for a crop"""
    # First check if crop exists
    crop = get_crop(crop_code)
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop not found: {crop_code}")

    # Get varieties for this crop
    varieties = get_varieties_by_crop(crop_code)

    return {
        "crop_code": crop_code,
        "crop_name_en": crop.name_en,
        "crop_name_ar": crop.name_ar,
        "varieties": [
            {
                "code": v.code,
                "name_en": v.name_en,
                "name_ar": v.name_ar,
                "name_local": v.name_local,
                "origin": v.origin.value,
                "maturity": v.maturity.value,
                "days_to_maturity": v.days_to_maturity,
                "yield_potential_ton_ha": v.yield_potential_ton_ha,
                "suitable_regions": [r.value for r in v.suitable_regions],
                "altitude_range": {
                    "min_m": v.altitude_min_m,
                    "max_m": v.altitude_max_m,
                },
                "tolerance": {
                    "drought": v.drought_tolerance,
                    "heat": v.heat_tolerance,
                },
                "disease_resistance": v.disease_resistance,
                "special_traits": v.special_traits,
                "seed_source": v.seed_source,
                "description_ar": v.description_ar,
            }
            for v in varieties
        ],
        "count": len(varieties),
    }


@app.get("/api/v1/crops/{crop}/stages")
def get_crop_stages(crop: str):
    """Get growth stages for a crop"""
    timeline = get_stage_timeline(crop)
    if not timeline:
        raise HTTPException(status_code=404, detail=f"Crop not found: {crop}")

    return create_success_response({"crop": crop, "stages": timeline})


@app.get("/api/v1/crops/{crop}/requirements")
def get_crop_requirements_legacy(crop: str):
    """Get nutrient requirements for a crop (legacy endpoint)"""
    if crop not in CROP_REQUIREMENTS:
        raise HTTPException(status_code=404, detail=f"Crop not found: {crop}")

    return create_success_response({"crop": crop, **CROP_REQUIREMENTS[crop]})


# ============== Actions ==============


@app.get("/api/v1/actions/{action_id}")
def get_action(action_id: str, lang: str = "ar"):
    """Get detailed action instructions"""
    details = get_action_details(action_id, lang)
    return {"id": action_id, **details}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8093))
    uvicorn.run(app, host="0.0.0.0", port=port)
