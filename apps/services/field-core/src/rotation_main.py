"""
SAHOOL Crop Rotation Service - Main API
خدمة تدوير المحاصيل - الواجهة الرئيسية

Complete FastAPI service for crop rotation planning
Port: 8099
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import rotation API endpoints
from .rotation_api import (
    check_rotation_compatibility_endpoint,
    create_rotation_plan_endpoint,
    create_rotation_plan_with_history,
    evaluate_rotation_endpoint,
    get_crop_families_endpoint,
    get_rotation_history_endpoint,
    get_rotation_rules_endpoint,
    suggest_next_crop_endpoint,
)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🌾 Starting Crop Rotation Service...")
    print("✅ Crop Rotation Service ready on port 8099")

    yield

    # Shutdown
    print("👋 Crop Rotation Service shutting down")


# Create FastAPI app
app = FastAPI(
    title="SAHOOL Crop Rotation Service",
    description="""
    Crop rotation planning for soil health and disease prevention
    تخطيط تدوير المحاصيل لصحة التربة ومنع الأمراض

    Features:
    - 5-year rotation planning
    - Crop family compatibility checking
    - Disease risk assessment
    - Nitrogen balance tracking
    - Soil health scoring
    - Yemen-specific crop recommendations

    Based on agronomic principles from OneSoil and LiteFarm.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware - secure origins from environment
CORS_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:8080",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# ============== Health Check ==============


@app.get("/healthz")
@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "crop_rotation",
        "version": "1.0.0",
        "port": 8099,
    }


# ============== Rotation Planning Endpoints ==============


@app.get("/v1/rotation/plan")
async def create_rotation_plan(
    field_id: str,
    field_name: str,
    start_year: int,
    num_years: int = 5,
):
    """
    GET endpoint to create rotation plan
    Create optimal crop rotation plan for a field

    Query Parameters:
    - field_id: Field identifier
    - field_name: Name of the field
    - start_year: Starting year for rotation (e.g., 2025)
    - num_years: Number of years to plan (1-10, default: 5)
    """
    return await create_rotation_plan_endpoint(
        field_id=field_id,
        field_name=field_name,
        start_year=start_year,
        num_years=num_years,
    )


@app.post("/v1/rotation/plan")
async def create_rotation_plan_post(req: dict):
    """
    POST endpoint to create rotation plan with custom history
    Create optimal crop rotation plan with provided field history

    Request Body:
    {
        "field_id": "string",
        "field_name": "string",
        "start_year": 2025,
        "num_years": 5,
        "history": [
            {
                "season_id": "string",
                "year": 2024,
                "season": "winter",
                "crop_code": "WHEAT",
                "crop_name_ar": "قمح",
                "crop_name_en": "Wheat",
                "crop_family": "cereals"
            }
        ],
        "preferences": ["WHEAT", "TOMATO"]
    }
    """
    from .rotation_api import CreateRotationPlanRequest

    request = CreateRotationPlanRequest(**req)
    return await create_rotation_plan_with_history(request)


# ============== Crop Suggestions ==============


@app.get("/v1/rotation/suggest/{field_id}")
async def suggest_next_crop(field_id: str, season: str = "winter"):
    """
    Suggest best crops for next season based on field history

    Path Parameters:
    - field_id: Field identifier

    Query Parameters:
    - season: Growing season (winter, summer, spring, autumn)

    Returns ranked list of crop suggestions with suitability scores
    """
    return await suggest_next_crop_endpoint(field_id=field_id, season=season)


# ============== Rotation Evaluation ==============


@app.post("/v1/rotation/evaluate")
async def evaluate_rotation(req: dict):
    """
    Evaluate a rotation plan for soil health and disease risk

    Request Body:
    {
        "seasons": [
            {
                "season_id": "string",
                "year": 2024,
                "season": "winter",
                "crop_code": "WHEAT",
                "crop_name_ar": "قمح",
                "crop_name_en": "Wheat",
                "crop_family": "cereals"
            }
        ]
    }

    Returns:
    - diversity_score: 0-100
    - soil_health_score: 0-100
    - disease_risk_score: 0-100 (lower is better)
    - nitrogen_balance: positive/neutral/negative
    - recommendations: List of recommendations
    - warnings: List of warnings
    """
    from .rotation_api import EvaluateRotationRequest

    request = EvaluateRotationRequest(**req)
    return await evaluate_rotation_endpoint(request)


# ============== Field History ==============


@app.get("/v1/rotation/history/{field_id}")
async def get_rotation_history(field_id: str, years: int = 5):
    """
    Get crop rotation history for a field

    Path Parameters:
    - field_id: Field identifier

    Query Parameters:
    - years: Number of years of history to retrieve (1-10, default: 5)
    """
    return await get_rotation_history_endpoint(field_id=field_id, years=years)


# ============== Rotation Rules ==============


@app.get("/v1/rotation/rules")
async def get_rotation_rules():
    """
    Get all crop rotation rules by family

    Returns rotation rules including:
    - Minimum years between same family
    - Good/bad predecessor families
    - Nitrogen effect (fix, neutral, deplete, heavy_deplete)
    - Disease risk profiles
    - Root depth (shallow, medium, deep)
    - Nutrient demand (light, medium, heavy)
    """
    return await get_rotation_rules_endpoint()


@app.get("/v1/rotation/families")
async def get_crop_families():
    """
    Get all crop families with their crop mappings

    Returns:
    - families: Dictionary of family -> [crop codes]
    - total_families: Number of crop families
    - total_crops: Total number of crops
    """
    return await get_crop_families_endpoint()


# ============== Compatibility Checking ==============


@app.get("/v1/rotation/check")
async def check_rotation_compatibility(crop_family: str, previous_crops: str):
    """
    Check if a crop family is compatible with previous crops

    Query Parameters:
    - crop_family: Crop family to check (e.g., "cereals", "legumes")
    - previous_crops: Comma-separated list of previous crop codes (e.g., "WHEAT,TOMATO")

    Returns:
    - is_compatible: Boolean
    - warnings: List of compatibility warnings
    - nitrogen_balance: Nitrogen balance assessment
    - disease_risk: Disease risk assessment
    """
    crops_list = [c.strip() for c in previous_crops.split(",")]
    return await check_rotation_compatibility_endpoint(
        crop_family=crop_family, previous_crops=crops_list
    )


# ============== Documentation ==============


@app.get("/")
def root():
    """API root with service information"""
    return {
        "service": "SAHOOL Crop Rotation Planning",
        "version": "1.0.0",
        "description": "Crop rotation planning for soil health and disease prevention",
        "endpoints": {
            "health": "/healthz",
            "docs": "/docs",
            "rotation_plan_get": "/v1/rotation/plan?field_id=F001&field_name=Field1&start_year=2025&num_years=5",
            "rotation_plan_post": "/v1/rotation/plan",
            "suggest_crop": "/v1/rotation/suggest/{field_id}?season=winter",
            "evaluate_rotation": "/v1/rotation/evaluate",
            "field_history": "/v1/rotation/history/{field_id}?years=5",
            "rotation_rules": "/v1/rotation/rules",
            "crop_families": "/v1/rotation/families",
            "check_compatibility": "/v1/rotation/check?crop_family=cereals&previous_crops=WHEAT,TOMATO",
        },
        "features": [
            "5-year rotation planning",
            "Crop family compatibility checking",
            "Disease risk assessment",
            "Nitrogen balance tracking",
            "Soil health scoring",
            "Yemen-specific crop recommendations",
        ],
        "principles": [
            "No monoculture - avoid same crop family repeatedly",
            "Legume inclusion - every 3-4 years for nitrogen",
            "Deep vs shallow roots - alternate for soil structure",
            "Disease break - 4+ years for solanaceae",
            "Nutrient balance - heavy feeders after nitrogen fixers",
        ],
    }


# ============== Run Server ==============


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8099))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
