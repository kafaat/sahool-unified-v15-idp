"""
SAHOOL Growing Degree Days (GDD) API Endpoints
نقاط نهاية واجهة برمجة التطبيقات لوحدات الحرارة النامية

GDD endpoints for crop development tracking:
- Complete GDD charts with daily accumulation
- Growth stage mapping and milestones
- Harvest date predictions
- GDD forecasting
- Crop-specific requirements
- Comparison to historical normal

Similar to OneSoil's GDD tracking feature.
"""

import logging
from datetime import date as date_class

from fastapi import HTTPException, Query

from .gdd_tracker import get_gdd_tracker

logger = logging.getLogger(__name__)


def register_gdd_endpoints(app):
    """Register all GDD-related endpoints with the FastAPI app"""

    @app.get("/v1/gdd/chart/{field_id}")
    async def get_gdd_chart(
        field_id: str,
        crop_code: str = Query(..., description="Crop code (e.g., 'WHEAT', 'TOMATO')"),
        planting_date: str = Query(..., description="Planting date (YYYY-MM-DD)"),
        lat: float = Query(..., description="Field latitude", ge=-90, le=90),
        lon: float = Query(..., description="Field longitude", ge=-180, le=180),
        end_date: str | None = Query(None, description="End date (default: today)"),
        method: str = Query(
            "simple", description="Calculation method: simple, modified, sine"
        ),
    ):
        """
        مخطط وحدات الحرارة النامية | Get GDD Accumulation Chart

        Get comprehensive GDD tracking chart for a field from planting to current date.

        **Features:**
        - Daily GDD accumulation from planting
        - Growth stage identification
        - Milestone tracking (emergence, flowering, harvest)
        - Harvest date prediction
        - Comparison to historical normal
        - Visual chart data for mobile app

        **Calculation Methods:**
        - `simple`: (Tmax + Tmin) / 2 - Tbase (fastest, most common)
        - `modified`: Apply upper/lower cutoffs (more accurate for extreme temps)
        - `sine`: Sine wave approximation (most accurate, slower)

        **Supported Crops:**
        - Cereals: WHEAT, BARLEY, CORN, SORGHUM, MILLET
        - Vegetables: TOMATO, POTATO, ONION, CUCUMBER, PEPPER
        - Legumes: FABA_BEAN, LENTIL, CHICKPEA
        - Cash: COTTON, COFFEE, QAT
        - Fruits: DATE_PALM, GRAPE, MANGO
        - Fodder: ALFALFA

        **Example:**
        ```
        GET /v1/gdd/chart/field123?crop_code=WHEAT&planting_date=2024-03-01&lat=15.37&lon=44.19
        ```

        **Returns:**
        ```json
        {
          "field_id": "field123",
          "crop": {"code": "WHEAT", "name_ar": "قمح", "name_en": "Wheat"},
          "planting_date": "2024-03-01",
          "current_status": {
            "date": "2024-05-15",
            "total_gdd": 1247.5,
            "days_since_planting": 75,
            "avg_daily_gdd": 16.6
          },
          "current_stage": {
            "name_en": "Flowering",
            "name_ar": "الإزهار",
            "next_stage_en": "Grain Fill",
            "next_stage_ar": "امتلاء الحبوب",
            "gdd_to_next_stage": 252.5
          },
          "milestones": [...],
          "harvest_prediction": {
            "estimated_date": "2024-06-20",
            "gdd_remaining": 752.5,
            "days_remaining": 36
          },
          "comparison": {
            "vs_normal_percent": 8.5,
            "description_ar": "متقدم بنسبة 8.5% عن المعدل الطبيعي",
            "description_en": "8.5% ahead of normal"
          },
          "daily_data": [...]
        }
        ```

        **Use Cases:**
        - Track crop development progress
        - Predict flowering and harvest dates
        - Plan field operations (fertilization, irrigation)
        - Compare current season to normal
        - Optimize harvest timing
        - Mobile app charts and progress bars
        """
        try:
            # Parse dates
            plant_date = date_class.fromisoformat(planting_date)
            end_dt = (
                date_class.fromisoformat(end_date) if end_date else date_class.today()
            )

            # Validate dates
            if plant_date > end_dt:
                raise HTTPException(
                    status_code=400, detail="planting_date must be before end_date"
                )

            if plant_date > date_class.today():
                raise HTTPException(
                    status_code=400, detail="planting_date cannot be in the future"
                )

            # Validate method
            valid_methods = ["simple", "modified", "sine"]
            if method not in valid_methods:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid method. Must be one of: {', '.join(valid_methods)}",
                )

            # Get GDD tracker
            tracker = get_gdd_tracker()

            # Generate chart
            chart = await tracker.get_gdd_chart(
                field_id=field_id,
                crop_code=crop_code,
                planting_date=plant_date,
                latitude=lat,
                longitude=lon,
                end_date=end_dt,
                method=method,
            )

            return chart.to_dict()

        except ValueError as e:
            if "Unknown crop" in str(e):
                tracker = get_gdd_tracker()
                available_crops = tracker.get_all_crops()
                crop_codes = [c["crop_code"] for c in available_crops]
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown crop: {crop_code}. Available crops: {', '.join(crop_codes[:10])}...",
                ) from e
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Failed to generate GDD chart: {e}")
            raise HTTPException(
                status_code=500, detail=f"GDD calculation error: {str(e)}"
            ) from e

    @app.get("/v1/gdd/forecast")
    async def get_gdd_forecast(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        current_gdd: float = Query(..., description="Current accumulated GDD", ge=0),
        target_gdd: float = Query(..., description="Target GDD to reach", ge=0),
        base_temp: float = Query(
            10.0, description="Base temperature (°C)", ge=0, le=20
        ),
        upper_temp: float | None = Query(
            None, description="Upper cutoff temp (°C)", ge=20, le=45
        ),
        method: str = Query(
            "simple", description="Calculation method: simple, modified, sine"
        ),
    ):
        """
        توقع وحدات الحرارة النامية | Forecast GDD Accumulation

        Forecast when a target GDD will be reached using weather forecast.

        **Use Cases:**
        - Predict flowering date: "When will we reach 1300 GDD?"
        - Estimate harvest date: "When will we reach 2000 GDD?"
        - Plan irrigation: "When will next growth stage begin?"
        - Schedule fertilization: "When to apply nitrogen?"

        **How it Works:**
        1. Takes current accumulated GDD
        2. Uses 16-day weather forecast to project future GDD
        3. Calculates daily GDD accumulation
        4. Estimates date when target will be reached
        5. If target beyond forecast, uses historical average to extrapolate

        **Example Use Case - Wheat Flowering:**
        ```
        Wheat planted March 1, currently at 1100 GDD (May 10).
        Flowering requires 1500 GDD.
        When will flowering occur?

        GET /v1/gdd/forecast?lat=15.37&lon=44.19&current_gdd=1100&target_gdd=1500&base_temp=0
        ```

        **Example Response:**
        ```json
        {
          "current_gdd": 1100,
          "target_gdd": 1500,
          "gdd_needed": 400,
          "estimated_date": "2024-05-28",
          "is_estimated": false,
          "forecast_data": [
            {"date": "2024-05-11", "daily_gdd": 18.5, "accumulated_gdd": 1118.5},
            {"date": "2024-05-12", "daily_gdd": 17.2, "accumulated_gdd": 1135.7},
            ...
          ]
        }
        ```

        **Integration with Mobile App:**
        - Show countdown to next milestone
        - Display progress bars
        - Push notifications when stages reached
        - Update field task scheduling
        """
        try:
            # Validate
            if current_gdd >= target_gdd:
                raise HTTPException(
                    status_code=400, detail="current_gdd must be less than target_gdd"
                )

            valid_methods = ["simple", "modified", "sine"]
            if method not in valid_methods:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid method. Must be one of: {', '.join(valid_methods)}",
                )

            # Get tracker
            tracker = get_gdd_tracker()

            # Generate forecast
            forecast = await tracker.get_gdd_forecast(
                latitude=lat,
                longitude=lon,
                current_gdd=current_gdd,
                target_gdd=target_gdd,
                base_temp=base_temp,
                upper_temp=upper_temp,
                method=method,
            )

            return forecast

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to generate GDD forecast: {e}")
            raise HTTPException(
                status_code=500, detail=f"Forecast error: {str(e)}"
            ) from e

    @app.get("/v1/gdd/requirements/{crop_code}")
    async def get_crop_gdd_requirements(
        crop_code: str,
    ):
        """
        متطلبات المحصول | Get Crop GDD Requirements

        Get complete GDD requirements and growth stages for a crop.

        **What You Get:**
        - Base temperature for the crop
        - Upper cutoff temperature (if applicable)
        - Total GDD required from planting to harvest
        - All growth stages with GDD thresholds
        - Stage descriptions in Arabic and English

        **Use Cases:**
        - Understand crop development timeline
        - Plan planting dates
        - Estimate season length
        - Compare different crops
        - Educational content for farmers

        **Example:**
        ```
        GET /v1/gdd/requirements/WHEAT
        ```

        **Response:**
        ```json
        {
          "crop_code": "WHEAT",
          "crop_name_ar": "قمح",
          "crop_name_en": "Wheat",
          "base_temp_c": 0,
          "upper_temp_c": 30,
          "total_gdd_required": 2000,
          "stages": [
            {
              "name_en": "Emergence",
              "name_ar": "الإنبات",
              "gdd_start": 0,
              "gdd_end": 150,
              "gdd_duration": 150,
              "description_ar": "ظهور البادرات",
              "description_en": "Seedling emergence"
            },
            ...
          ]
        }
        ```

        **All Yemen Crops Supported:**
        - 6 Cereals (wheat, barley, corn, sorghum, millet, rice)
        - 11 Vegetables (tomato, potato, onion, cucumber, pepper, etc.)
        - 6 Legumes (faba bean, lentil, chickpea, etc.)
        - 5 Cash crops (cotton, coffee, qat, sesame, tobacco)
        - 9 Fruits (date palm, grape, mango, banana, citrus, etc.)
        - 3 Fodder crops (alfalfa, rhodes grass, sudan grass)

        **40+ crops total!**
        """
        try:
            # Get tracker
            tracker = get_gdd_tracker()

            # Get requirements
            requirements = await tracker.get_crop_requirements(crop_code.upper())

            return requirements.to_dict()

        except ValueError as e:
            tracker = get_gdd_tracker()
            available_crops = tracker.get_all_crops()
            crop_codes = [c["crop_code"] for c in available_crops]
            raise HTTPException(
                status_code=404,
                detail=f"Crop '{crop_code}' not found. Available crops: {', '.join(crop_codes[:15])}...",
            ) from e
        except Exception as e:
            logger.error(f"Failed to get crop requirements: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e

    @app.get("/v1/gdd/stage/{crop_code}")
    async def get_growth_stage_from_gdd(
        crop_code: str,
        gdd: float = Query(..., description="Accumulated GDD", ge=0),
    ):
        """
        مرحلة النمو | Get Growth Stage from GDD

        Determine current growth stage based on accumulated GDD.

        **Simple API for Stage Lookup:**
        - Input: Crop + GDD
        - Output: Current stage + Next stage + GDD to next

        **Example:**
        ```
        GET /v1/gdd/stage/WHEAT?gdd=1247.5
        ```

        **Response:**
        ```json
        {
          "crop_code": "WHEAT",
          "crop_name_ar": "قمح",
          "crop_name_en": "Wheat",
          "accumulated_gdd": 1247.5,
          "current_stage": {
            "name_en": "Flowering",
            "name_ar": "الإزهار",
            "gdd_start": 1100,
            "gdd_end": 1500
          },
          "next_stage": {
            "name_en": "Grain Fill",
            "name_ar": "امتلاء الحبوب",
            "gdd_start": 1500,
            "gdd_end": 1700
          },
          "gdd_to_next_stage": 252.5,
          "progress_percent": 61.9
        }
        ```

        **Use Cases:**
        - Quick stage lookup
        - Mobile app stage indicator
        - Alert generation
        - Task recommendations
        """
        try:
            # Get tracker
            tracker = get_gdd_tracker()

            # Validate crop
            crop_code_upper = crop_code.upper()
            requirements = await tracker.get_crop_requirements(crop_code_upper)

            # Get current stage
            current_en, current_ar, next_en, next_ar, gdd_to_next = (
                tracker.get_current_stage(crop_code_upper, gdd)
            )

            # Find stage details
            stages = requirements.stages
            current_stage_info = None
            next_stage_info = None

            for stage in stages:
                if stage["name_en"] == current_en:
                    current_stage_info = stage
                if stage["name_en"] == next_en:
                    next_stage_info = stage

            # Calculate progress
            total_gdd = requirements.total_gdd_required
            progress_percent = (gdd / total_gdd) * 100 if total_gdd > 0 else 0

            return {
                "crop_code": crop_code_upper,
                "crop_name_ar": requirements.crop_name_ar,
                "crop_name_en": requirements.crop_name_en,
                "accumulated_gdd": round(gdd, 1),
                "current_stage": (
                    {
                        "name_en": current_en,
                        "name_ar": current_ar,
                        "gdd_start": (
                            current_stage_info["gdd_start"] if current_stage_info else 0
                        ),
                        "gdd_end": (
                            current_stage_info["gdd_end"] if current_stage_info else 0
                        ),
                        "description_ar": (
                            current_stage_info["description_ar"]
                            if current_stage_info
                            else ""
                        ),
                        "description_en": (
                            current_stage_info["description_en"]
                            if current_stage_info
                            else ""
                        ),
                    }
                    if current_stage_info
                    else None
                ),
                "next_stage": (
                    {
                        "name_en": next_en,
                        "name_ar": next_ar,
                        "gdd_start": (
                            next_stage_info["gdd_start"] if next_stage_info else 0
                        ),
                        "gdd_end": next_stage_info["gdd_end"] if next_stage_info else 0,
                        "description_ar": (
                            next_stage_info["description_ar"] if next_stage_info else ""
                        ),
                        "description_en": (
                            next_stage_info["description_en"] if next_stage_info else ""
                        ),
                    }
                    if next_stage_info
                    else None
                ),
                "gdd_to_next_stage": round(gdd_to_next, 1),
                "progress_percent": round(progress_percent, 1),
                "total_gdd_required": round(total_gdd, 1),
            }

        except ValueError as e:
            tracker = get_gdd_tracker()
            available_crops = tracker.get_all_crops()
            crop_codes = [c["crop_code"] for c in available_crops]
            raise HTTPException(
                status_code=404,
                detail=f"Crop '{crop_code}' not found. Available: {', '.join(crop_codes[:10])}...",
            ) from e
        except Exception as e:
            logger.error(f"Failed to get growth stage: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e

    @app.get("/v1/gdd/crops")
    async def list_supported_crops():
        """
        قائمة المحاصيل | List All Supported Crops

        Get list of all crops with GDD tracking support.

        **40+ Yemen Crops:**

        **Cereals (الحبوب):**
        - Wheat, Barley, Corn, Sorghum, Millet, Rice

        **Vegetables (الخضروات):**
        - Tomato, Potato, Onion, Carrot, Cucumber, Squash
        - Pepper, Eggplant, Okra, Cabbage, Lettuce

        **Legumes (البقوليات):**
        - Faba Bean, Lentil, Chickpea, Cowpea, Peanut, Alfalfa

        **Cash Crops (المحاصيل النقدية):**
        - Cotton, Coffee, Qat, Sesame, Tobacco

        **Fruits (الفواكه):**
        - Date Palm, Grape, Mango, Banana, Papaya
        - Citrus, Pomegranate, Fig, Guava

        **Fodder (الأعلاف):**
        - Alfalfa, Rhodes Grass, Sudan Grass

        **Response:**
        ```json
        [
          {
            "crop_code": "WHEAT",
            "crop_name_ar": "قمح",
            "crop_name_en": "Wheat",
            "base_temp_c": 0,
            "upper_temp_c": 30,
            "total_gdd_required": 2000,
            "num_stages": 8
          },
          ...
        ]
        ```
        """
        try:
            tracker = get_gdd_tracker()
            crops = tracker.get_all_crops()
            return {"total_crops": len(crops), "crops": crops}
        except Exception as e:
            logger.error(f"Failed to list crops: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e

    logger.info("GDD API endpoints registered successfully")
