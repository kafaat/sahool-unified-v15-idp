"""
Yield Prediction API Endpoints
To be integrated into main.py
NOTE: This file is a template. Endpoints are already in main.py
This file should not be executed - endpoints are in main.py
"""

# Prevent execution - this is a template file
# All endpoints are already in main.py
# If this file is imported, define dummy app to prevent errors
try:
    from fastapi import FastAPI
    # Check if we're in the main module context
    import sys
    if 'main' not in sys.modules or not hasattr(sys.modules.get('main', type('', (), {})()), 'app'):
        raise NameError("app not in main context")
    from main import app  # Try to import app from main
except (NameError, ImportError, AttributeError):
    # Define dummy app to prevent decorator errors
    class DummyApp:
        def post(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    app = DummyApp()

from typing import Optional, List, Dict
from datetime import date, timedelta
from pydantic import BaseModel, Field
from fastapi import HTTPException, Query, Path
import logging
import uuid

logger = logging.getLogger(__name__)

# Dummy variables to prevent NameError
try:
    from main import get_timeseries, SatelliteSource, _sar_processor, _yield_predictor, YEMEN_REGIONS
except ImportError:
    # Define dummies
    async def get_timeseries(*args, **kwargs):
        return {"timeseries": []}
    class SatelliteSource:
        SENTINEL2 = "sentinel2"
    _sar_processor = None
    _yield_predictor = None
    YEMEN_REGIONS = {}

class YieldPredictionRequest(BaseModel):
    """Request for crop yield prediction"""
    field_id: str = Field(..., description="معرف الحقل")
    crop_code: str = Field(..., description="رمز المحصول (WHEAT, TOMATO, etc.)")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    planting_date: Optional[date] = Field(None, description="تاريخ الزراعة")
    field_area_ha: float = Field(default=1.0, ge=0.01, description="مساحة الحقل بالهكتار")

    # Optional: provide NDVI time series (if available)
    ndvi_series: Optional[List[float]] = Field(
        None,
        description="سلسلة زمنية من قيم NDVI (اختياري - سيتم جلبها تلقائياً إذا لم تقدم)"
    )

    # Weather data (optional - will be estimated if not provided)
    precipitation_mm: Optional[float] = Field(None, description="الأمطار الكلية (مم)")
    avg_temp_min: Optional[float] = Field(None, description="متوسط درجة الحرارة الصغرى (°س)")
    avg_temp_max: Optional[float] = Field(None, description="متوسط درجة الحرارة الكبرى (°س)")

    # Optional: soil moisture from SAR
    soil_moisture: Optional[float] = Field(None, ge=0, le=1, description="رطوبة التربة (0-1)")


class YieldPredictionResponse(BaseModel):
    """Response for crop yield prediction"""
    field_id: str
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    predicted_yield_ton_ha: float
    predicted_yield_total_ton: float  # predicted_yield_ton_ha * field_area_ha
    yield_range_min: float
    yield_range_max: float
    confidence: float
    factors: Dict[str, float]
    comparison_to_average: float
    comparison_to_base: float
    recommendations_ar: List[str]
    recommendations_en: List[str]
    prediction_date: str
    growth_stage: str
    days_to_harvest: Optional[int]
    data_sources_used: List[str]


class YieldHistoryItem(BaseModel):
    """Historical yield prediction item"""
    prediction_id: str
    prediction_date: str
    crop_code: str
    crop_name_ar: str
    predicted_yield_ton_ha: float
    actual_yield_ton_ha: Optional[float]
    confidence: float
    growth_stage: str


class RegionalYieldStats(BaseModel):
    """Regional yield statistics"""
    governorate: str
    governorate_ar: str
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    average_yield_ton_ha: float
    min_yield_ton_ha: float
    max_yield_ton_ha: float
    field_count: int
    data_source: str


# Add these endpoints before the `if __name__ == "__main__":` line:
# NOTE: These endpoints are already integrated into main.py
# The decorators below are kept for reference but won't execute if app is not the real FastAPI app

@app.post("/v1/yield-prediction", response_model=YieldPredictionResponse)
async def predict_yield(request: YieldPredictionRequest):
    """
    التنبؤ بإنتاجية المحصول | Predict Crop Yield

    Uses ML-based ensemble model combining:
    - NDVI-based regression (40%)
    - Growing Degree Days model (30%)
    - Water balance model (20%)
    - Soil moisture model (10%)

    Returns predicted yield with confidence interval and actionable recommendations.
    """
    import random

    data_sources = []

    # Get NDVI time series if not provided
    if request.ndvi_series is None or len(request.ndvi_series) == 0:
        # Fetch from timeseries endpoint
        try:
            timeseries_data = await get_timeseries(
                field_id=request.field_id,
                days=90,  # Last 3 months
                satellite=SatelliteSource.SENTINEL2,
            )
            request.ndvi_series = [point["ndvi"] for point in timeseries_data["timeseries"]]
            data_sources.append("sentinel-2_ndvi_timeseries")
        except Exception as e:
            logger.warning(f"Failed to fetch NDVI timeseries: {e}")
            # Generate realistic NDVI series based on crop growth
            days_since_planting = 60  # Assume mid-season
            request.ndvi_series = [
                max(0.2, min(0.8, 0.3 + (i / 10) * 0.5 + random.uniform(-0.05, 0.05)))
                for i in range(10)
            ]
            data_sources.append("simulated_ndvi")
    else:
        data_sources.append("user_provided_ndvi")

    # Prepare weather data
    if request.avg_temp_min is not None and request.avg_temp_max is not None:
        # Generate daily temperature series (assume 90 days)
        temp_min_series = [request.avg_temp_min + random.uniform(-3, 3) for _ in range(90)]
        temp_max_series = [request.avg_temp_max + random.uniform(-3, 3) for _ in range(90)]
        data_sources.append("user_provided_weather")
    else:
        # Use Yemen regional defaults based on location
        # Highland: cooler, Coastal: warmer
        if request.latitude > 14.5:  # Highland region
            temp_min_series = [15 + random.uniform(-2, 2) for _ in range(90)]
            temp_max_series = [28 + random.uniform(-3, 3) for _ in range(90)]
        else:  # Coastal/lowland
            temp_min_series = [22 + random.uniform(-2, 2) for _ in range(90)]
            temp_max_series = [35 + random.uniform(-3, 3) for _ in range(90)]
        data_sources.append("estimated_weather_from_location")

    # Precipitation
    precipitation = request.precipitation_mm or random.uniform(100, 400)
    if request.precipitation_mm:
        data_sources.append("user_provided_precipitation")
    else:
        data_sources.append("estimated_precipitation")

    # Get soil moisture from SAR if available
    soil_moisture = request.soil_moisture
    if soil_moisture is None and _sar_processor:
        try:
            # Try to fetch soil moisture from SAR processor
            sar_result = await _sar_processor.estimate_soil_moisture(
                field_id=request.field_id,
                latitude=request.latitude,
                longitude=request.longitude,
                start_date=date.today() - timedelta(days=30),
                end_date=date.today(),
            )
            if sar_result and sar_result.soil_moisture_timeseries:
                soil_moisture = sar_result.soil_moisture_timeseries[-1].soil_moisture_m3m3
                data_sources.append("sentinel-1_sar_soil_moisture")
        except Exception as e:
            logger.warning(f"Failed to fetch SAR soil moisture: {e}")

    if soil_moisture is None:
        soil_moisture = random.uniform(0.3, 0.5)  # Assume moderate moisture
        data_sources.append("estimated_soil_moisture")

    # Prepare weather data dict
    weather_data = {
        "temp_min_series": temp_min_series,
        "temp_max_series": temp_max_series,
        "precipitation_mm": precipitation,
        "et0_mm": precipitation * 1.2,  # Simple ET0 estimate
    }

    # Call yield predictor
    prediction = await _yield_predictor.predict_yield(
        field_id=request.field_id,
        crop_code=request.crop_code,
        ndvi_series=request.ndvi_series,
        weather_data=weather_data,
        soil_moisture=soil_moisture,
        planting_date=request.planting_date,
        field_area_ha=request.field_area_ha,
    )

    # Calculate total yield
    total_yield = prediction.predicted_yield_ton_ha * request.field_area_ha

    return YieldPredictionResponse(
        field_id=prediction.field_id,
        crop_code=prediction.crop_code,
        crop_name_ar=prediction.crop_name_ar,
        crop_name_en=prediction.crop_name_en,
        predicted_yield_ton_ha=prediction.predicted_yield_ton_ha,
        predicted_yield_total_ton=round(total_yield, 2),
        yield_range_min=prediction.yield_range_min,
        yield_range_max=prediction.yield_range_max,
        confidence=prediction.confidence,
        factors=prediction.factors,
        comparison_to_average=prediction.comparison_to_average,
        comparison_to_base=prediction.comparison_to_base,
        recommendations_ar=prediction.recommendations_ar,
        recommendations_en=prediction.recommendations_en,
        prediction_date=prediction.prediction_date.isoformat(),
        growth_stage=prediction.growth_stage,
        days_to_harvest=prediction.days_to_harvest,
        data_sources_used=data_sources,
    )


@app.get("/v1/yield-history/{field_id}")
async def get_yield_history(
    field_id: str,
    seasons: int = Query(default=5, ge=1, le=20, description="Number of past seasons to retrieve"),
    crop_code: Optional[str] = Query(None, description="Filter by crop code"),
):
    """
    الحصول على سجل التنبؤات السابقة | Get Yield Prediction History

    Returns historical yield predictions for a field, optionally filtered by crop.
    In production, this would fetch from a database. Currently returns simulated data.
    """
    import random
    from datetime import datetime, timedelta

    # Import shared crop catalog
    try:
        import sys
        sys.path.insert(0, "/home/user/sahool-unified-v15-idp")
        from apps.services.shared.crops import ALL_CROPS

        # Get crops for this region (simulated)
        if crop_code:
            crop_codes = [crop_code] if crop_code in ALL_CROPS else ["WHEAT"]
        else:
            # Random selection of common Yemen crops
            crop_codes = random.sample(
                ["WHEAT", "SORGHUM", "TOMATO", "POTATO", "ONION", "CORN"],
                k=min(seasons, 3)
            )
    except (ValueError, KeyError, IndexError):
        crop_codes = ["WHEAT", "TOMATO", "POTATO"]

    # Generate historical predictions
    history = []
    for i in range(seasons):
        crop_code_selected = random.choice(crop_codes) if not crop_code else crop_code

        try:
            from apps.services.shared.crops import get_crop
            crop_info = get_crop(crop_code_selected)
            crop_name_ar = crop_info.name_ar if crop_info else crop_code_selected
            base_yield = crop_info.base_yield_ton_ha if crop_info else 2.0
        except (ImportError, AttributeError, KeyError):
            crop_name_ar = crop_code_selected
            base_yield = 2.0

        # Historical prediction (months ago)
        prediction_date = datetime.utcnow() - timedelta(days=120 * i)

        # Simulated prediction and actual yield
        predicted = round(base_yield * random.uniform(0.7, 1.3), 2)

        # Actual yield (if harvest completed)
        if i > 0:  # Past seasons have actual yields
            actual = round(predicted * random.uniform(0.85, 1.15), 2)
        else:  # Current season - no actual yet
            actual = None

        history.append(
            YieldHistoryItem(
                prediction_id=str(uuid.uuid4()),
                prediction_date=prediction_date.isoformat(),
                crop_code=crop_code_selected,
                crop_name_ar=crop_name_ar,
                predicted_yield_ton_ha=predicted,
                actual_yield_ton_ha=actual,
                confidence=random.uniform(0.7, 0.95),
                growth_stage="harvest_completed" if actual else "ripening",
            )
        )

    return {
        "field_id": field_id,
        "seasons": seasons,
        "crop_filter": crop_code,
        "history": history,
        "summary": {
            "total_predictions": len(history),
            "completed_harvests": len([h for h in history if h.actual_yield_ton_ha]),
            "average_predicted_yield": round(
                sum(h.predicted_yield_ton_ha for h in history) / len(history), 2
            ) if history else 0,
            "average_actual_yield": round(
                sum(h.actual_yield_ton_ha for h in history if h.actual_yield_ton_ha) /
                len([h for h in history if h.actual_yield_ton_ha]), 2
            ) if any(h.actual_yield_ton_ha for h in history) else None,
        }
    }


@app.get("/v1/regional-yields/{governorate}")
async def get_regional_yields(
    governorate: str = Path(..., description="Yemen governorate (e.g., 'ibb', 'taiz', 'hodeidah')"),
    crop: Optional[str] = Query(None, description="Filter by crop code (e.g., 'WHEAT', 'TOMATO')"),
):
    """
    الحصول على إحصائيات الإنتاجية الإقليمية | Get Regional Yield Statistics

    Returns average yields for a specific governorate in Yemen.
    In production, this would aggregate data from multiple fields.
    """
    import random

    # Validate governorate
    if governorate.lower() not in YEMEN_REGIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Governorate '{governorate}' not found. Available: {', '.join(YEMEN_REGIONS.keys())}"
        )

    gov_info = YEMEN_REGIONS[governorate.lower()]
    gov_name_ar = gov_info["name_ar"]
    region_type = gov_info["region"]

    # Import crop catalog
    try:
        import sys
        sys.path.insert(0, "/home/user/sahool-unified-v15-idp")
        from apps.services.shared.crops import ALL_CROPS, get_crops_for_region

        # Get crops suitable for this region
        if crop:
            crops_to_show = [ALL_CROPS[crop]] if crop in ALL_CROPS else []
        else:
            # Get common crops for this region type
            if region_type == "highland":
                crop_codes = ["WHEAT", "BARLEY", "POTATO", "TOMATO", "FABA_BEAN", "COFFEE"]
            elif region_type == "coastal":
                crop_codes = ["SORGHUM", "MILLET", "BANANA", "MANGO", "SESAME", "COTTON"]
            else:  # desert
                crop_codes = ["DATE_PALM", "WHEAT", "BARLEY", "ALFALFA"]

            crops_to_show = [ALL_CROPS[c] for c in crop_codes if c in ALL_CROPS]
    except Exception as e:
        logger.warning(f"Failed to load crop catalog: {e}")
        crops_to_show = []

    if not crops_to_show:
        raise HTTPException(
            status_code=404,
            detail=f"No crop data available for {governorate}"
        )

    # Generate regional statistics
    regional_stats = []
    for crop_info in crops_to_show:
        # Simulate regional variation (±20% from base yield)
        base_yield = crop_info.base_yield_ton_ha
        avg_yield = base_yield * random.uniform(0.8, 1.2)
        min_yield = avg_yield * 0.6
        max_yield = avg_yield * 1.4
        field_count = random.randint(50, 500)

        regional_stats.append(
            RegionalYieldStats(
                governorate=governorate.lower(),
                governorate_ar=gov_name_ar,
                crop_code=crop_info.code,
                crop_name_ar=crop_info.name_ar,
                crop_name_en=crop_info.name_en,
                average_yield_ton_ha=round(avg_yield, 2),
                min_yield_ton_ha=round(min_yield, 2),
                max_yield_ton_ha=round(max_yield, 2),
                field_count=field_count,
                data_source="simulated_regional_data",
            )
        )

    return {
        "governorate": governorate.lower(),
        "governorate_ar": gov_name_ar,
        "region_type": region_type,
        "crop_filter": crop,
        "statistics": regional_stats,
        "summary": {
            "total_crops": len(regional_stats),
            "total_fields": sum(s.field_count for s in regional_stats),
            "highest_yield_crop": max(regional_stats, key=lambda x: x.average_yield_ton_ha).crop_name_en if regional_stats else None,
        },
        "note": "Production system would aggregate real field data. Currently showing simulated regional averages.",
    }
