"""
SAHOOL Agro Advisor - Main API Service
Disease diagnosis, nutrient assessment, and fertilizer planning
Port: 8095
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .kb import (
    get_disease,
    get_diseases_by_crop,
    search_diseases,
    get_deficiency,
    get_fertilizer,
    get_fertilizers_for_nutrient,
)
from .engine import (
    assess_from_image_event,
    assess_from_symptoms,
    assess_from_ndvi,
    assess_from_visual,
    get_action_details,
    fertilizer_plan,
    get_stage_timeline,
    CROP_REQUIREMENTS,
)
from .events import get_publisher


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🌱 Starting Agro Advisor Service...")
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        print("✅ Agro Advisor ready on port 8095")
    except Exception as e:
        print(f"⚠️ NATS connection failed (running without events): {e}")
        app.state.publisher = None

    yield

    # Shutdown
    if app.state.publisher:
        await app.state.publisher.close()
    print("👋 Agro Advisor shutting down")


app = FastAPI(
    title="SAHOOL Agro Advisor",
    description="Disease diagnosis, nutrient assessment, and fertilizer planning for Yemen agriculture",
    version="15.3.3",
    lifespan=lifespan,
)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "agro_advisor", "version": "15.3.3"}


# ============== Request/Response Models ==============


class DiseaseAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    condition_id: str
    confidence: float = Field(ge=0, le=1)
    crop: Optional[str] = None
    weather: Optional[dict] = None
    correlation_id: Optional[str] = None


class SymptomAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    symptoms: list[str]
    lang: str = "ar"
    correlation_id: Optional[str] = None


class NDVIAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    ndvi: float = Field(ge=-1, le=1)
    ndvi_history: Optional[list[float]] = None
    crop: Optional[str] = None
    stage: Optional[str] = None
    correlation_id: Optional[str] = None


class VisualAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    leaf_color: Optional[str] = None
    pattern: Optional[str] = None
    location: Optional[str] = None
    crop: Optional[str] = None
    lang: str = "ar"
    correlation_id: Optional[str] = None


class FertilizerPlanRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    stage: str
    field_size_ha: float = 1.0
    soil_fertility: str = "medium"
    irrigation_type: str = "drip"
    correlation_id: Optional[str] = None


# ============== Disease Endpoints ==============


@app.post("/disease/assess")
async def assess_disease(req: DiseaseAssessRequest):
    """Assess disease from image classification result"""
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
    if app.state.publisher:
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


@app.post("/disease/symptoms")
async def assess_symptoms(req: SymptomAssessRequest):
    """Assess possible diseases from reported symptoms"""
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
    if app.state.publisher and assessments:
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


@app.get("/disease/{disease_id}")
def get_disease_info(disease_id: str, lang: str = "ar"):
    """Get disease information by ID"""
    disease = get_disease(disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")

    return {
        "id": disease_id,
        **disease,
        "actions_details": [
            get_action_details(action, lang) for action in disease["actions"]
        ],
    }


@app.get("/disease/crop/{crop}")
def get_crop_diseases(crop: str):
    """Get all diseases for a specific crop"""
    diseases = get_diseases_by_crop(crop)
    return {"crop": crop, "diseases": diseases, "count": len(diseases)}


@app.get("/disease/search")
def search_disease(q: str, lang: str = "ar"):
    """Search diseases by name or symptoms"""
    results = search_diseases(q, lang)
    return {"query": q, "results": results, "count": len(results)}


# ============== Nutrient Endpoints ==============


@app.post("/nutrient/ndvi")
async def assess_from_ndvi_endpoint(req: NDVIAssessRequest):
    """Assess nutrient deficiency from NDVI data"""
    assessments = assess_from_ndvi(
        ndvi=req.ndvi,
        ndvi_history=req.ndvi_history,
        crop=req.crop,
        growth_stage=req.stage,
    )

    # Publish top result
    event_id = None
    if app.state.publisher and assessments:
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


@app.post("/nutrient/visual")
async def assess_visual_endpoint(req: VisualAssessRequest):
    """Assess nutrient deficiency from visual indicators"""
    indicators = {
        "leaf_color": req.leaf_color,
        "pattern": req.pattern,
        "location": req.location,
    }

    assessments = assess_from_visual(indicators, req.crop, req.lang)

    # Publish top result
    event_id = None
    if app.state.publisher and assessments:
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


@app.get("/nutrient/{deficiency_id}")
def get_deficiency_info(deficiency_id: str):
    """Get nutrient deficiency information by ID"""
    deficiency = get_deficiency(deficiency_id)
    if not deficiency:
        raise HTTPException(status_code=404, detail="Deficiency not found")

    return {"id": deficiency_id, **deficiency}


# ============== Fertilizer Endpoints ==============


@app.post("/fertilizer/plan")
async def create_fertilizer_plan(req: FertilizerPlanRequest):
    """Generate fertilizer plan for crop and stage"""
    plan = fertilizer_plan(
        crop=req.crop,
        stage=req.stage,
        field_size_ha=req.field_size_ha,
        soil_fertility=req.soil_fertility,
        irrigation_type=req.irrigation_type,
    )

    # Publish event
    event_id = None
    if app.state.publisher:
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


@app.get("/fertilizer/{fertilizer_id}")
def get_fertilizer_info(fertilizer_id: str):
    """Get fertilizer information by ID"""
    fert = get_fertilizer(fertilizer_id)
    if not fert:
        raise HTTPException(status_code=404, detail="Fertilizer not found")

    return {"id": fertilizer_id, **fert}


@app.get("/fertilizer/nutrient/{nutrient}")
def get_fertilizers_by_nutrient(nutrient: str):
    """Get fertilizers that provide a specific nutrient"""
    fertilizers = get_fertilizers_for_nutrient(nutrient.upper())
    return {"nutrient": nutrient, "fertilizers": fertilizers, "count": len(fertilizers)}


# ============== Crop Information ==============


@app.get("/crops")
def list_crops():
    """List supported crops"""
    return {
        "crops": list(CROP_REQUIREMENTS.keys()),
        "count": len(CROP_REQUIREMENTS),
    }


@app.get("/crops/{crop}/stages")
def get_crop_stages(crop: str):
    """Get growth stages for a crop"""
    timeline = get_stage_timeline(crop)
    if not timeline:
        raise HTTPException(status_code=404, detail="Crop not found")

    return {"crop": crop, "stages": timeline}


@app.get("/crops/{crop}/requirements")
def get_crop_requirements(crop: str):
    """Get nutrient requirements for a crop"""
    if crop not in CROP_REQUIREMENTS:
        raise HTTPException(status_code=404, detail="Crop not found")

    return {"crop": crop, **CROP_REQUIREMENTS[crop]}


# ============== Actions ==============


@app.get("/actions/{action_id}")
def get_action(action_id: str, lang: str = "ar"):
    """Get detailed action instructions"""
    details = get_action_details(action_id, lang)
    return {"id": action_id, **details}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8095))
    uvicorn.run(app, host="0.0.0.0", port=port)
