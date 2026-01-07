"""
SAHOOL Field Core Service - Main API
Crop profitability analysis and financial insights
Port: 8090
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Query

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.middleware import (
    RequestLoggingMiddleware,
    TenantContextMiddleware,
    setup_cors,
)
from shared.observability.middleware import ObservabilityMiddleware

from pydantic import BaseModel, Field

# Add shared middleware to path
shared_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "shared")
)
sys.path.insert(0, shared_path)
from shared.errors_py import setup_exception_handlers, add_request_id_middleware

import logging

from profitability_analyzer import (
    CostCategory,
    ProfitabilityAnalyzer,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Field Core Service...")
    # Initialize connections
    app.state.db_connected = False
    app.state.nats_connected = False

    # Try database connection
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(
                db_url, min_size=2, max_size=10
            )
            app.state.db_connected = True
            logger.info("Database connected")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            app.state.db_pool = None
    else:
        app.state.db_pool = None

    # Try NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("NATS connected")
        except Exception as e:
            logger.warning(f"NATS connection failed: {e}")
            app.state.nc = None
    else:
        app.state.nc = None

    # Initialize profitability analyzer
    app.state.analyzer = ProfitabilityAnalyzer(
        db_pool=getattr(app.state, "db_pool", None)
    )

    logger.info("Field Core ready on port 8090")
    yield

    # Cleanup
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
    logger.info("Field Core shutting down")


app = FastAPI(
    title="SAHOOL Field Core",
    description="Crop profitability analysis and financial insights for farmers",
    version="15.3.3",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Setup rate limiting middleware
try:
    from middleware.rate_limiter import setup_rate_limiting

    setup_rate_limiting(app, use_redis=os.getenv("REDIS_URL") is not None)
    logger.info("Rate limiting enabled")
except ImportError as e:
    logger.warning(f"Rate limiting not available: {e}")
except Exception as e:
    logger.warning(f"Failed to setup rate limiting: {e}")


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "service": "field_core",
        "version": "15.3.3",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }


# ============== Request/Response Models ==============


class CostItemRequest(BaseModel):
    category: str
    description: str
    amount: float
    unit: str = "YER"
    quantity: float = 1.0
    unit_cost: float | None = None


class RevenueItemRequest(BaseModel):
    description: str
    quantity: float
    unit: str = "kg"
    unit_price: float
    grade: str | None = None


class AnalyzeCropRequest(BaseModel):
    field_id: str
    crop_season_id: str
    crop_code: str
    area_ha: float = Field(gt=0)
    costs: list[CostItemRequest] | None = None
    revenues: list[RevenueItemRequest] | None = None


class CropDataRequest(BaseModel):
    field_id: str
    crop_season_id: str | None = None
    crop_code: str
    area_ha: float = Field(gt=0)
    costs: list[dict] | None = None
    revenues: list[dict] | None = None


class AnalyzeSeasonRequest(BaseModel):
    farmer_id: str
    season_year: str
    crops: list[CropDataRequest]


# ============== Profitability Endpoints ==============


@app.get("/v1/profitability/crop/{crop_season_id}")
async def get_crop_profitability(
    crop_season_id: str,
    field_id: str = Query(..., description="Field ID"),
    crop_code: str = Query(..., description="Crop code"),
    area_ha: float = Query(..., gt=0, description="Area in hectares"),
):
    """
    Get profitability analysis for a specific crop season.
    Uses regional estimates if actual data not available.
    """
    try:
        analyzer: ProfitabilityAnalyzer = app.state.analyzer

        analysis = await analyzer.analyze_crop(
            field_id=field_id,
            crop_season_id=crop_season_id,
            crop_code=crop_code,
            area_ha=area_ha,
            costs=None,  # Will use regional estimates
            revenues=None,
        )

        return analysis
    except Exception as e:
        logger.error(f"Error analyzing crop: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/v1/profitability/analyze")
async def analyze_profitability(request: AnalyzeCropRequest):
    """
    Analyze crop profitability with custom costs and revenues.
    If costs/revenues not provided, uses regional estimates.
    """
    try:
        analyzer: ProfitabilityAnalyzer = app.state.analyzer

        # Convert request models to dicts
        costs_dict = None
        if request.costs:
            costs_dict = [
                {
                    "category": c.category,
                    "description": c.description,
                    "amount": c.amount,
                    "unit": c.unit,
                    "quantity": c.quantity,
                    "unit_cost": c.unit_cost or c.amount,
                }
                for c in request.costs
            ]

        revenues_dict = None
        if request.revenues:
            revenues_dict = [
                {
                    "description": r.description,
                    "quantity": r.quantity,
                    "unit": r.unit,
                    "unit_price": r.unit_price,
                    "grade": r.grade,
                }
                for r in request.revenues
            ]

        analysis = await analyzer.analyze_crop(
            field_id=request.field_id,
            crop_season_id=request.crop_season_id,
            crop_code=request.crop_code,
            area_ha=request.area_ha,
            costs=costs_dict,
            revenues=revenues_dict,
        )

        # Get recommendations
        recommendations = analyzer.generate_recommendations(analysis)

        return {"analysis": analysis, "recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error analyzing profitability: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/v1/profitability/season")
async def get_season_summary(request: AnalyzeSeasonRequest):
    """
    Analyze all crops for a farmer in a season.
    Returns summary with rankings and recommendations.
    """
    try:
        analyzer: ProfitabilityAnalyzer = app.state.analyzer

        # Convert request to dict format
        crops_data = [
            {
                "field_id": crop.field_id,
                "crop_season_id": crop.crop_season_id
                or f"{crop.field_id}-{request.season_year}",
                "crop_code": crop.crop_code,
                "area_ha": crop.area_ha,
                "costs": crop.costs,
                "revenues": crop.revenues,
            }
            for crop in request.crops
        ]

        summary = await analyzer.analyze_season(
            farmer_id=request.farmer_id,
            season_year=request.season_year,
            crops_data=crops_data,
        )

        return summary
    except Exception as e:
        logger.error(f"Error analyzing season: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/v1/profitability/compare")
async def compare_crops(
    crops: str = Query(..., description="Comma-separated crop codes"),
    area_ha: float = Query(1.0, gt=0, description="Area in hectares"),
    region: str = Query("sanaa", description="Region for benchmarks"),
):
    """
    Compare profitability of different crops.
    Useful for planning next season.
    Returns crops sorted by profitability.
    """
    try:
        analyzer: ProfitabilityAnalyzer = app.state.analyzer

        crop_codes = [c.strip() for c in crops.split(",")]

        comparisons = await analyzer.compare_crops(
            crop_codes=crop_codes, area_ha=area_ha, region=region
        )

        return {
            "region": region,
            "area_ha": area_ha,
            "crops": comparisons,
            "best_crop": comparisons[0] if comparisons else None,
            "worst_crop": comparisons[-1] if comparisons else None,
        }
    except Exception as e:
        logger.error(f"Error comparing crops: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/v1/profitability/break-even")
async def calculate_break_even(
    crop_code: str = Query(..., description="Crop code"),
    area_ha: float = Query(..., gt=0, description="Area in hectares"),
    total_costs: float = Query(..., gt=0, description="Total costs in YER"),
    expected_price: float = Query(
        ..., gt=0, description="Expected price per kg in YER"
    ),
):
    """
    Calculate break-even yield and price for a crop.
    Helps farmers understand minimum requirements for profitability.
    """
    try:
        analyzer: ProfitabilityAnalyzer = app.state.analyzer

        result = await analyzer.calculate_break_even(
            crop_code=crop_code,
            area_ha=area_ha,
            total_costs=total_costs,
            expected_price=expected_price,
        )

        return result
    except Exception as e:
        logger.error(f"Error calculating break-even: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/v1/profitability/history/{field_id}/{crop_code}")
async def get_historical(
    field_id: str,
    crop_code: str,
    years: int = Query(5, ge=1, le=10, description="Number of years of history"),
):
    """
    Get historical profitability data for a crop on a specific field.
    Shows trends over time.
    """
    try:
        analyzer: ProfitabilityAnalyzer = app.state.analyzer

        history = await analyzer.get_historical_profitability(
            field_id=field_id, crop_code=crop_code, years=years
        )

        return {
            "field_id": field_id,
            "crop_code": crop_code,
            "years_analyzed": years,
            "history": history,
        }
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/v1/profitability/benchmarks/{crop_code}")
async def get_benchmarks(
    crop_code: str, region: str = Query("sanaa", description="Region for benchmarks")
):
    """
    Get regional benchmark costs, yields, and revenues for a crop.
    Useful for comparison and planning.
    """
    try:
        analyzer: ProfitabilityAnalyzer = app.state.analyzer

        benchmarks = await analyzer.get_regional_benchmarks(
            crop_code=crop_code, region=region
        )

        if not benchmarks:
            raise HTTPException(
                status_code=404,
                detail=f"No benchmark data available for crop {crop_code}",
            )

        return benchmarks
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting benchmarks: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/v1/profitability/cost-breakdown/{crop_code}")
async def get_cost_breakdown(
    crop_code: str, area_ha: float = Query(1.0, gt=0, description="Area in hectares")
):
    """
    Get detailed cost breakdown by category for a crop.
    Shows what percentage each cost category represents.
    """
    try:
        analyzer: ProfitabilityAnalyzer = app.state.analyzer

        breakdown = await analyzer.get_cost_breakdown(
            crop_code=crop_code, area_ha=area_ha
        )

        if not breakdown:
            raise HTTPException(
                status_code=404, detail=f"No cost data available for crop {crop_code}"
            )

        return {"crop_code": crop_code, "area_ha": area_ha, "breakdown": breakdown}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cost breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============== Utility Endpoints ==============


@app.get("/v1/crops/list")
async def list_available_crops():
    """
    List all crops with available profitability data.
    Returns crop codes, names in both languages, and regional data availability.
    """
    analyzer: ProfitabilityAnalyzer = app.state.analyzer

    crops = []
    for crop_code in analyzer.CROP_NAMES_EN:
        crops.append(
            {
                "crop_code": crop_code,
                "name_en": analyzer.CROP_NAMES_EN[crop_code],
                "name_ar": analyzer.CROP_NAMES_AR[crop_code],
                "has_regional_data": crop_code in analyzer.REGIONAL_COSTS,
                "regional_yield_kg_ha": analyzer.REGIONAL_YIELDS.get(crop_code),
                "regional_price_yer_kg": analyzer.REGIONAL_PRICES.get(crop_code),
            }
        )

    return {"total": len(crops), "crops": crops}


@app.get("/v1/costs/categories")
async def list_cost_categories():
    """List all available cost categories"""
    return {
        "categories": [
            {
                "code": cat.value,
                "name_en": cat.value.title(),
                "name_ar": {
                    "seeds": "بذور",
                    "fertilizer": "أسمدة",
                    "pesticides": "مبيدات",
                    "irrigation": "ري",
                    "labor": "عمالة",
                    "machinery": "آلات",
                    "land": "أرض",
                    "marketing": "تسويق",
                    "other": "أخرى",
                }.get(cat.value, cat.value),
            }
            for cat in CostCategory
        ]
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8090))
    uvicorn.run(app, host="0.0.0.0", port=port)
