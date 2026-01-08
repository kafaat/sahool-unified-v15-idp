"""
SAHOOL Weather API Endpoints
نقاط نهاية واجهة برمجة التطبيقات للطقس

Weather endpoints using Open-Meteo integration for:
- Weather forecast
- Historical weather
- Growing Degree Days (GDD)
- Water balance
- Irrigation recommendations
- Frost risk assessment
"""

import logging
from datetime import date as date_class

from fastapi import HTTPException, Query

from .weather_integration import get_weather_service

logger = logging.getLogger(__name__)


def register_weather_endpoints(app):
    """Register all weather-related endpoints with the FastAPI app"""

    @app.get("/v1/weather/forecast")
    async def get_weather_forecast(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        days: int = Query(7, description="Forecast days (1-16)", ge=1, le=16),
    ):
        """
        توقعات الطقس | Get Weather Forecast

        Get weather forecast for next N days with ET0 (evapotranspiration).
        Useful for irrigation planning and crop water management.

        Data from Open-Meteo free API.

        **Yemen Locations:**
        - Sanaa: lat=15.3694, lon=44.1910 (highland)
        - Aden: lat=12.7855, lon=45.0187 (coastal)
        - Hodeidah: lat=14.8022, lon=42.9511 (coastal)
        - Ibb: lat=13.9667, lon=44.1667 (highland)
        - Taiz: lat=13.5795, lon=44.0202 (mid-elevation)

        **Returns:**
        - Daily forecast: temp, precipitation, ET0
        - Hourly forecast: temp, humidity, wind, solar radiation
        """
        try:
            weather_service = get_weather_service()
            forecast = await weather_service.get_forecast(lat, lon, days)
            return forecast.to_dict()
        except Exception as e:
            logger.error(f"Failed to get forecast: {e}")
            raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}") from e

    @app.get("/v1/weather/historical")
    async def get_historical_weather(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
        end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    ):
        """
        بيانات الطقس التاريخية | Get Historical Weather

        Get historical weather data from 1940 to ~7 days ago.
        Includes summary statistics: avg temp, total precipitation, ET0, GDD.

        Useful for:
        - Analyzing past growing seasons
        - Calibrating yield prediction models
        - Understanding long-term climate patterns

        **Example:**
        ```
        GET /v1/weather/historical?lat=15.3694&lon=44.1910&start_date=2024-01-01&end_date=2024-06-30
        ```
        """
        try:
            start = date_class.fromisoformat(start_date)
            end = date_class.fromisoformat(end_date)

            # Validate date range
            if start >= end:
                raise HTTPException(status_code=400, detail="start_date must be before end_date")

            if (end - start).days > 365:
                raise HTTPException(status_code=400, detail="Maximum 365 days per request")

            weather_service = get_weather_service()
            historical = await weather_service.get_historical(lat, lon, start, end)
            return historical.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to get historical weather: {e}")
            raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}") from e

    @app.get("/v1/weather/gdd")
    async def get_gdd(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
        end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
        base_temp: float = Query(10.0, description="Base temperature (°C)", ge=0, le=20),
    ):
        """
        وحدات الحرارة النامية | Calculate Growing Degree Days (GDD)

        Calculate accumulated Growing Degree Days for crop phenology tracking.

        **GDD Formula:**
        GDD = Σ(max(0, (Tmax + Tmin)/2 - Tbase))

        **Base Temperatures:**
        - Most crops: 10°C (default)
        - Warm-season crops (corn, tomato): 10-12°C
        - Cool-season crops (wheat, barley): 5-8°C
        - Tropical crops (mango, banana): 12-15°C

        **Use Cases:**
        - Predict flowering/harvest dates
        - Track crop development stages
        - Compare seasons
        - Schedule field operations

        **Example:**
        ```
        GET /v1/weather/gdd?lat=15.37&lon=44.19&start_date=2024-03-01&end_date=2024-06-30&base_temp=10
        ```
        """
        try:
            start = date_class.fromisoformat(start_date)
            end = date_class.fromisoformat(end_date)

            if start >= end:
                raise HTTPException(status_code=400, detail="start_date must be before end_date")

            weather_service = get_weather_service()
            gdd = await weather_service.get_growing_degree_days(lat, lon, start, end, base_temp)

            return {
                "location": {"lat": lat, "lon": lon},
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": (end - start).days + 1,
                },
                "base_temperature_c": base_temp,
                "gdd_accumulated": gdd,
                "gdd_per_day": round(gdd / ((end - start).days + 1), 2),
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to calculate GDD: {e}")
            raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}") from e

    @app.get("/v1/weather/water-balance")
    async def get_water_balance(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
        end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
        kc: float = Query(1.0, description="Crop coefficient (0.4-1.3)", ge=0.4, le=1.3),
    ):
        """
        الميزان المائي | Calculate Water Balance

        Calculate water balance: Precipitation - (ET0 × Kc)

        Returns water deficit or surplus in mm, critical for irrigation scheduling.

        **Crop Coefficients (Kc) by Growth Stage:**

        **Cereals (Wheat, Barley):**
        - Initial: 0.3-0.5
        - Mid-season: 1.0-1.15
        - Late: 0.3-0.5

        **Vegetables (Tomato, Potato):**
        - Initial: 0.4-0.6
        - Mid-season: 1.05-1.25
        - Late: 0.7-0.9

        **Fruit Trees (Mango, Date):**
        - Year-round: 0.8-1.1

        **Water Balance Status:**
        - Surplus (> +50mm): Reduce irrigation
        - Balanced (-50 to +50mm): Optimal
        - Deficit (< -50mm): Increase irrigation

        **Example:**
        ```
        GET /v1/weather/water-balance?lat=15.37&lon=44.19&start_date=2024-03-01&end_date=2024-06-30&kc=1.0
        ```
        """
        try:
            start = date_class.fromisoformat(start_date)
            end = date_class.fromisoformat(end_date)

            if start >= end:
                raise HTTPException(status_code=400, detail="start_date must be before end_date")

            if (end - start).days > 365:
                raise HTTPException(status_code=400, detail="Maximum 365 days per request")

            weather_service = get_weather_service()
            balance = await weather_service.get_water_balance(lat, lon, start, end, kc)
            return balance
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to calculate water balance: {e}")
            raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}") from e

    @app.get("/v1/weather/irrigation-advice")
    async def get_irrigation_advice(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        crop_type: str = Query(..., description="Crop code (e.g., 'WHEAT', 'TOMATO')"),
        growth_stage: str = Query(
            ..., description="Growth stage (initial, development, mid, late, harvest)"
        ),
        soil_moisture: float | None = Query(
            None, description="Current soil moisture (0-1)", ge=0, le=1
        ),
        field_id: str | None = Query(None, description="Field identifier"),
    ):
        """
        نصائح الري | Get Irrigation Recommendation

        Get irrigation recommendation based on:
        - 7-day weather forecast with ET0
        - Crop type and growth stage
        - Current soil moisture (if available)

        Returns:
        - Water requirement (mm)
        - Irrigation schedule (frequency in days)
        - Specific recommendations in Arabic and English

        **Growth Stages:**
        - `initial`: Germination/establishment (Kc ~0.5)
        - `development`: Vegetative growth (Kc ~0.7)
        - `mid`: Flowering/peak growth (Kc ~1.0-1.2)
        - `late`: Ripening/maturation (Kc ~0.8)
        - `harvest`: Pre-harvest (Kc ~0.6)

        **Yemen Crop Examples:**
        - Wheat: WHEAT
        - Tomato: TOMATO
        - Potato: POTATO
        - Sorghum: SORGHUM
        - Coffee: COFFEE

        **Example:**
        ```
        GET /v1/weather/irrigation-advice?lat=15.37&lon=44.19&crop_type=WHEAT&growth_stage=mid&soil_moisture=0.4
        ```
        """
        try:
            # Validate growth stage
            valid_stages = [
                "initial",
                "development",
                "mid",
                "late",
                "harvest",
                "germination",
                "flowering",
                "fruiting",
                "ripening",
            ]
            if growth_stage.lower() not in valid_stages:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid growth_stage. Must be one of: {', '.join(valid_stages)}",
                )

            weather_service = get_weather_service()
            recommendation = await weather_service.get_irrigation_recommendation(
                lat, lon, crop_type, growth_stage, soil_moisture, field_id
            )
            return recommendation.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get irrigation advice: {e}")
            raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}") from e

    @app.get("/v1/weather/frost-risk")
    async def get_frost_risk(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        days: int = Query(7, description="Forecast days (1-16)", ge=1, le=16),
    ):
        """
        مخاطر الصقيع | Assess Frost Risk

        Assess frost risk for next N days.

        **Critical for Yemen Highlands:**
        - Sanaa (1,900m elevation): Regular frost in winter
        - Ibb (2,200m elevation): Frost risk Dec-Feb
        - Dhamar (2,400m elevation): High frost risk
        - Taiz (1,400m): Occasional frost

        **Frost Risk Levels:**
        - **Severe** (< -2°C, 95%+ probability): Immediate protection needed
        - **High** (-2°C to 0°C, 70-95% probability): Protect sensitive crops
        - **Moderate** (0°C to 2°C, 40-70% probability): Monitor and prepare
        - **Low** (2°C to 5°C, 10-40% probability): Watch forecasts
        - **None** (> 5°C, <10% probability): No action needed

        **Frost Protection Methods:**
        - Cover crops with plastic sheets or blankets
        - Use smoke/heating for orchards
        - Irrigate before frost (wet soil holds heat)
        - Avoid low-lying areas (cold air pools)

        **Example:**
        ```
        GET /v1/weather/frost-risk?lat=15.3694&lon=44.1910&days=7
        ```
        """
        try:
            weather_service = get_weather_service()
            frost_risks = await weather_service.get_frost_risk(lat, lon, days)

            # Find highest risk
            max_risk_level = "none"
            for risk in frost_risks:
                if risk.risk_level == "severe":
                    max_risk_level = "severe"
                    break
                elif risk.risk_level == "high" and max_risk_level not in ["severe"]:
                    max_risk_level = "high"
                elif risk.risk_level == "moderate" and max_risk_level not in [
                    "severe",
                    "high",
                ]:
                    max_risk_level = "moderate"
                elif risk.risk_level == "low" and max_risk_level == "none":
                    max_risk_level = "low"

            return {
                "location": {"lat": lat, "lon": lon},
                "forecast_days": days,
                "max_risk_level": max_risk_level,
                "frost_risks": [risk.to_dict() for risk in frost_risks],
                "summary": {
                    "days_with_frost_risk": len([r for r in frost_risks if r.risk_level != "none"]),
                    "days_with_high_risk": len(
                        [r for r in frost_risks if r.risk_level in ["severe", "high"]]
                    ),
                    "min_temperature_c": min(r.min_temp_c for r in frost_risks),
                },
            }
        except Exception as e:
            logger.error(f"Failed to assess frost risk: {e}")
            raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}") from e

    logger.info("Weather API endpoints registered successfully")
