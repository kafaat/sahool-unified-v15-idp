"""
SAHOOL Crop Rotation API
واجهة برمجة تطبيقات تدوير المحاصيل

FastAPI endpoints for crop rotation planning
"""

import os
from datetime import date

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .crop_rotation import (
    CropFamily,
    CropRotationPlanner,
    SeasonPlan,
    to_dict,
)

# ============== Request/Response Models ==============


class SeasonPlanRequest(BaseModel):
    """Request model for season plan"""

    season_id: str
    year: int
    season: str
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    crop_family: str
    planting_date: str | None = None
    harvest_date: str | None = None
    expected_yield: float | None = None
    notes: str | None = None


class CreateRotationPlanRequest(BaseModel):
    """Request to create rotation plan"""

    field_id: str
    field_name: str
    start_year: int
    num_years: int = Field(default=5, ge=1, le=10)
    history: list[SeasonPlanRequest] | None = None
    preferences: list[str] | None = None


class EvaluateRotationRequest(BaseModel):
    """Request to evaluate rotation"""

    seasons: list[SeasonPlanRequest]


class RotationRuleResponse(BaseModel):
    """Response model for rotation rule"""

    crop_family: str
    min_years_between: int
    good_predecessors: list[str]
    bad_predecessors: list[str]
    nitrogen_effect: str
    disease_risk: dict[str, float]
    root_depth: str
    nutrient_demand: str


# ============== Initialize Planner ==============

planner = CropRotationPlanner()


# ============== API Endpoints ==============


async def create_rotation_plan_endpoint(
    field_id: str = Query(..., description="Field ID"),
    field_name: str = Query(..., description="Field name"),
    start_year: int = Query(..., description="Starting year"),
    num_years: int = Query(5, ge=1, le=10, description="Number of years to plan"),
    preferences: list[str] | None = Query(None, description="Crop preferences"),
) -> dict:
    """
    Create optimal crop rotation plan
    إنشاء خطة تدوير محاصيل مثلى

    Args:
        field_id: Field identifier
        field_name: Name of the field
        start_year: Starting year for rotation
        num_years: Number of years to plan (1-10)
        preferences: Optional list of preferred crop codes

    Returns:
        Complete rotation plan with recommendations
    """
    # Get field history
    history = await planner.get_field_history(field_id, years=5)

    # Create rotation plan
    plan = await planner.create_rotation_plan(
        field_id=field_id,
        field_name=field_name,
        start_year=start_year,
        num_years=num_years,
        history=history,
        preferences=preferences,
    )

    return to_dict(plan)


async def create_rotation_plan_with_history(req: CreateRotationPlanRequest) -> dict:
    """
    Create rotation plan with custom history
    إنشاء خطة تدوير مع سجل مخصص

    Allows passing custom field history instead of fetching from database
    """
    # Convert request history to SeasonPlan objects
    history = []
    if req.history:
        for h in req.history:
            history.append(
                SeasonPlan(
                    season_id=h.season_id,
                    year=h.year,
                    season=h.season,
                    crop_code=h.crop_code,
                    crop_name_ar=h.crop_name_ar,
                    crop_name_en=h.crop_name_en,
                    crop_family=CropFamily(h.crop_family),
                    planting_date=(
                        date.fromisoformat(h.planting_date) if h.planting_date else None
                    ),
                    harvest_date=(
                        date.fromisoformat(h.harvest_date) if h.harvest_date else None
                    ),
                    expected_yield=h.expected_yield,
                    notes=h.notes,
                )
            )

    # Create rotation plan
    plan = await planner.create_rotation_plan(
        field_id=req.field_id,
        field_name=req.field_name,
        start_year=req.start_year,
        num_years=req.num_years,
        history=history,
        preferences=req.preferences,
    )

    return to_dict(plan)


async def suggest_next_crop_endpoint(
    field_id: str, season: str = "winter", history_json: str | None = None
) -> dict:
    """
    Suggest best crops for next season
    اقتراح أفضل المحاصيل للموسم القادم

    Args:
        field_id: Field identifier
        season: Growing season (winter, summer, spring, autumn)
        history_json: Optional JSON string of field history

    Returns:
        Ranked list of crop suggestions with suitability scores
    """
    # Get field history
    history = await planner.get_field_history(field_id, years=5)

    # Get suggestions
    suggestions = await planner.suggest_next_crop(
        field_id=field_id, history=history, season=season
    )

    return {
        "field_id": field_id,
        "season": season,
        "suggestions": [to_dict(s) for s in suggestions],
        "count": len(suggestions),
    }


async def evaluate_rotation_endpoint(req: EvaluateRotationRequest) -> dict:
    """
    Evaluate a rotation plan
    تقييم خطة تدوير

    Args:
        req: Request with list of seasons to evaluate

    Returns:
        Evaluation with diversity, soil health, and disease risk scores
    """
    # Convert request seasons to SeasonPlan objects
    seasons = []
    for s in req.seasons:
        seasons.append(
            SeasonPlan(
                season_id=s.season_id,
                year=s.year,
                season=s.season,
                crop_code=s.crop_code,
                crop_name_ar=s.crop_name_ar,
                crop_name_en=s.crop_name_en,
                crop_family=CropFamily(s.crop_family),
                planting_date=(
                    date.fromisoformat(s.planting_date) if s.planting_date else None
                ),
                harvest_date=(
                    date.fromisoformat(s.harvest_date) if s.harvest_date else None
                ),
                expected_yield=s.expected_yield,
                notes=s.notes,
            )
        )

    # Evaluate rotation
    evaluation = planner.evaluate_rotation(seasons)

    return {"evaluation": evaluation, "seasons_count": len(seasons)}


async def get_rotation_history_endpoint(
    field_id: str,
    years: int = Query(5, ge=1, le=10, description="Number of years of history"),
) -> dict:
    """
    Get crop rotation history for a field
    الحصول على سجل تدوير المحاصيل للحقل

    Args:
        field_id: Field identifier
        years: Number of years of history to retrieve

    Returns:
        Historical crop rotation data
    """
    history = await planner.get_field_history(field_id, years=years)

    return {
        "field_id": field_id,
        "years": years,
        "history": [to_dict(h) for h in history],
        "count": len(history),
    }


async def get_rotation_rules_endpoint() -> dict:
    """
    Get all crop rotation rules
    الحصول على جميع قواعد تدوير المحاصيل

    Returns:
        All rotation rules by crop family
    """
    rules = {}

    for family, rule in planner.ROTATION_RULES.items():
        rules[family.value] = {
            "crop_family": family.value,
            "min_years_between": rule.min_years_between,
            "good_predecessors": [f.value for f in rule.good_predecessors],
            "bad_predecessors": [f.value for f in rule.bad_predecessors],
            "nitrogen_effect": rule.nitrogen_effect,
            "disease_risk": rule.disease_risk,
            "root_depth": rule.root_depth,
            "nutrient_demand": rule.nutrient_demand,
        }

    return {"rules": rules, "families_count": len(rules)}


async def get_crop_families_endpoint() -> dict:
    """
    Get all crop families with their crop mappings
    الحصول على جميع العائلات النباتية مع محاصيلها

    Returns:
        All crop families and their associated crops
    """
    families = {}

    for crop_code, family in planner.CROP_FAMILY_MAP.items():
        if family.value not in families:
            families[family.value] = []
        families[family.value].append(crop_code)

    return {
        "families": families,
        "total_families": len(families),
        "total_crops": len(planner.CROP_FAMILY_MAP),
    }


async def check_rotation_compatibility_endpoint(
    crop_family: str,
    previous_crops: list[str] = Query(..., description="List of previous crop codes"),
) -> dict:
    """
    Check if a crop is compatible with previous crops
    التحقق من توافق محصول مع المحاصيل السابقة

    Args:
        crop_family: Crop family to check
        previous_crops: List of previous crop codes

    Returns:
        Compatibility check result with warnings
    """
    try:
        family = CropFamily(crop_family)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid crop family: {crop_family}"
        )

    # Convert previous crops to SeasonPlan objects
    history = []
    current_year = 2025

    for i, crop_code in enumerate(reversed(previous_crops)):
        crop_family_enum = planner.get_crop_family(crop_code)
        history.append(
            SeasonPlan(
                season_id=f"check_{i}",
                year=current_year - i - 1,
                season="winter",
                crop_code=crop_code,
                crop_name_ar=planner._get_crop_name_ar(crop_family_enum),
                crop_name_en=planner._get_crop_name_en(crop_family_enum),
                crop_family=crop_family_enum,
            )
        )

    # Reverse to get chronological order
    history = list(reversed(history))

    # Check rotation rule
    is_valid, messages = planner.check_rotation_rule(family, history)

    return {
        "crop_family": crop_family,
        "previous_crops": previous_crops,
        "is_compatible": is_valid,
        "warnings_ar": [m[0] for m in messages],
        "warnings_en": [m[1] for m in messages],
        "nitrogen_balance": planner.calculate_nitrogen_balance(
            history
            + [
                SeasonPlan(
                    season_id="proposed",
                    year=current_year,
                    season="winter",
                    crop_code=planner._get_crop_for_family(family),
                    crop_name_ar=planner._get_crop_name_ar(family),
                    crop_name_en=planner._get_crop_name_en(family),
                    crop_family=family,
                )
            ]
        ),
        "disease_risk": planner.get_disease_risk(history),
    }


# ============== Standalone App (for testing) ==============

if __name__ == "__main__":
    # This allows running the module standalone for testing
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI(
        title="SAHOOL Crop Rotation API",
        description="Crop rotation planning for soil health and disease prevention",
        version="1.0.0",
    )

    # Register endpoints
    app.post("/v1/rotation/plan")(create_rotation_plan_with_history)
    app.get("/v1/rotation/plan")(create_rotation_plan_endpoint)
    app.get("/v1/rotation/suggest/{field_id}")(suggest_next_crop_endpoint)
    app.post("/v1/rotation/evaluate")(evaluate_rotation_endpoint)
    app.get("/v1/rotation/history/{field_id}")(get_rotation_history_endpoint)
    app.get("/v1/rotation/rules")(get_rotation_rules_endpoint)
    app.get("/v1/rotation/families")(get_crop_families_endpoint)
    app.get("/v1/rotation/check")(check_rotation_compatibility_endpoint)

    @app.get("/healthz")
    def health():
        return {"status": "ok", "service": "crop_rotation", "version": "1.0.0"}

    port = int(os.getenv("PORT", 8099))
    uvicorn.run(app, host="0.0.0.0", port=port)
