"""
SAHOOL Spray Time Advisor API Endpoints
نقاط نهاية واجهة برمجة التطبيقات لمستشار وقت الرش

Spray time recommendation endpoints:
- Spray forecast (7-day outlook with optimal windows)
- Best spray time (find optimal time in next N days)
- Evaluate specific time (check if a time is suitable)
"""

import logging
from datetime import datetime

from fastapi import HTTPException, Query

from .spray_advisor import (
    SprayCondition,
    SprayProduct,
    get_spray_advisor,
)

logger = logging.getLogger(__name__)


def register_spray_endpoints(app):
    """Register all spray-related endpoints with the FastAPI app"""

    @app.get("/v1/spray/forecast")
    async def get_spray_forecast(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        days: int = Query(7, description="Forecast days (1-16)", ge=1, le=16),
        product_type: str | None = Query(
            None,
            description="Product type: herbicide, insecticide, fungicide, foliar_fertilizer, growth_regulator",
        ),
    ):
        """
        توقعات أوقات الرش | Get Spray Time Forecast

        Get spray time recommendations for next N days based on weather conditions.

        Identifies optimal spray windows during daylight hours (6 AM - 6 PM) considering:
        - **Temperature**: 10-30°C ideal (varies by product)
        - **Humidity**: 40-80% ideal
        - **Wind Speed**: < 15 km/h (prevents drift)
        - **Rain Probability**: < 20% (prevents wash-off)
        - **Delta-T**: 2-8°C optimal (wet bulb depression)

        **Product Types:**
        - `herbicide`: Higher temp needed (15-28°C), longer rain-free period (6h)
        - `insecticide`: Lower wind tolerance (<10 km/h)
        - `fungicide`: Lower humidity preferred (<70%)
        - `foliar_fertilizer`: Higher humidity needed (>60%)
        - `growth_regulator`: Moderate conditions (15-25°C)

        **Spray Conditions:**
        - `excellent` (score 85-100): Perfect conditions
        - `good` (score 70-84): Safe to spray
        - `marginal` (score 50-69): Some risk, use caution
        - `poor` (score 30-49): Not recommended
        - `dangerous` (score 0-29): Do not spray

        **Example:**
        ```
        GET /v1/spray/forecast?lat=15.3694&lon=44.1910&days=7&product_type=herbicide
        ```

        **Returns:**
        ```json
        [
          {
            "date": "2024-12-25",
            "overall_condition": "good",
            "best_window": {
              "start_time": "2024-12-25T07:00:00",
              "end_time": "2024-12-25T11:00:00",
              "duration_hours": 4,
              "condition": "good",
              "score": 78.5,
              "weather": {...},
              "risks": ["low_humidity"],
              "recommendations_ar": [...],
              "recommendations_en": [...]
            },
            "all_windows": [...],
            "hours_suitable": 6.5,
            "daily_summary": {...}
          }
        ]
        ```
        """
        try:
            # Validate and convert product type
            product = None
            if product_type:
                try:
                    product = SprayProduct(product_type.lower())
                except ValueError:
                    valid_types = [p.value for p in SprayProduct]
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid product_type. Must be one of: {', '.join(valid_types)}",
                    )

            spray_advisor = get_spray_advisor()
            forecast = await spray_advisor.get_spray_forecast(lat, lon, days, product)

            return {
                "location": {"lat": lat, "lon": lon},
                "forecast_days": days,
                "product_type": product_type,
                "forecast": [day.to_dict() for day in forecast],
                "summary": {
                    "total_suitable_hours": sum(day.hours_suitable for day in forecast),
                    "days_with_good_conditions": len(
                        [
                            d
                            for d in forecast
                            if d.overall_condition
                            in [SprayCondition.EXCELLENT, SprayCondition.GOOD]
                        ]
                    ),
                    "best_day": (
                        max(
                            forecast,
                            key=lambda d: d.best_window.score if d.best_window else 0,
                        ).date.isoformat()
                        if any(d.best_window for d in forecast)
                        else None
                    ),
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get spray forecast: {e}")
            raise HTTPException(
                status_code=500, detail=f"Spray advisor error: {str(e)}"
            ) from e

    @app.get("/v1/spray/best-time")
    async def get_best_spray_time(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        product_type: str = Query(
            ..., description="Product type (herbicide, insecticide, etc.)"
        ),
        within_days: int = Query(
            3, description="Search within next N days", ge=1, le=7
        ),
    ):
        """
        أفضل وقت للرش | Find Best Spray Time

        Find the single best spray window in the next N days for a specific product.

        This endpoint searches all available spray windows and returns the one with
        the highest suitability score, considering product-specific requirements.

        **Use Case:**
        When you need to spray but have flexibility in timing, use this endpoint
        to find the absolute best time.

        **Example:**
        ```
        GET /v1/spray/best-time?lat=15.37&lon=44.19&product_type=insecticide&within_days=3
        ```

        **Returns:**
        ```json
        {
          "location": {"lat": 15.37, "lon": 44.19},
          "product_type": "insecticide",
          "search_period_days": 3,
          "best_window": {
            "start_time": "2024-12-26T08:00:00",
            "end_time": "2024-12-26T12:00:00",
            "duration_hours": 4,
            "condition": "excellent",
            "score": 92.3,
            ...
          }
        }
        ```

        Returns 404 if no suitable windows found.
        """
        try:
            # Validate and convert product type
            try:
                product = SprayProduct(product_type.lower())
            except ValueError:
                valid_types = [p.value for p in SprayProduct]
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid product_type. Must be one of: {', '.join(valid_types)}",
                )

            spray_advisor = get_spray_advisor()
            best_window = await spray_advisor.get_best_spray_time(
                lat, lon, product, within_days
            )

            if not best_window:
                raise HTTPException(
                    status_code=404,
                    detail=f"No suitable spray windows found in next {within_days} days. "
                    f"Try increasing the search period or checking specific conditions.",
                )

            return {
                "location": {"lat": lat, "lon": lon},
                "product_type": product_type,
                "search_period_days": within_days,
                "best_window": best_window.to_dict(),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to find best spray time: {e}")
            raise HTTPException(
                status_code=500, detail=f"Spray advisor error: {str(e)}"
            ) from e

    @app.post("/v1/spray/evaluate")
    async def evaluate_spray_time(
        lat: float = Query(..., description="Latitude", ge=-90, le=90),
        lon: float = Query(..., description="Longitude", ge=-180, le=180),
        target_datetime: str = Query(
            ..., description="Target spray time (ISO 8601 format)"
        ),
        product_type: str | None = Query(None, description="Product type (optional)"),
    ):
        """
        تقييم وقت محدد للرش | Evaluate Specific Spray Time

        Evaluate if a specific date/time is suitable for spraying.

        **Use Case:**
        When you have a planned spray time and want to check if conditions will be suitable.

        **Example:**
        ```
        POST /v1/spray/evaluate?lat=15.37&lon=44.19&target_datetime=2024-12-26T09:00:00&product_type=herbicide
        ```

        **Target DateTime Format:**
        - ISO 8601 format: `2024-12-26T09:00:00`
        - With timezone: `2024-12-26T09:00:00+03:00`
        - Must be within next 16 days

        **Returns:**
        ```json
        {
          "location": {"lat": 15.37, "lon": 44.19},
          "target_time": "2024-12-26T09:00:00",
          "product_type": "herbicide",
          "evaluation": {
            "start_time": "2024-12-26T09:00:00",
            "end_time": "2024-12-26T10:00:00",
            "condition": "good",
            "score": 75.2,
            "weather": {
              "temperature_c": 22.5,
              "humidity_percent": 65.0,
              "wind_speed_kmh": 8.2,
              "precipitation_probability": 10.0
            },
            "risks": ["low_humidity"],
            "recommendations_ar": [...],
            "recommendations_en": [...]
          }
        }
        ```
        """
        try:
            # Parse target datetime
            try:
                target_dt = datetime.fromisoformat(
                    target_datetime.replace("Z", "+00:00")
                )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid target_datetime format. Use ISO 8601 format (e.g., 2024-12-26T09:00:00)",
                )

            # Check if target is in valid range (next 16 days)
            now = datetime.now(target_dt.tzinfo) if target_dt.tzinfo else datetime.now()
            days_ahead = (target_dt - now).days

            if days_ahead < 0:
                raise HTTPException(
                    status_code=400, detail="target_datetime must be in the future"
                )
            if days_ahead > 16:
                raise HTTPException(
                    status_code=400,
                    detail="target_datetime must be within next 16 days (weather forecast limit)",
                )

            # Validate and convert product type
            product = None
            if product_type:
                try:
                    product = SprayProduct(product_type.lower())
                except ValueError:
                    valid_types = [p.value for p in SprayProduct]
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid product_type. Must be one of: {', '.join(valid_types)}",
                    )

            spray_advisor = get_spray_advisor()
            evaluation = await spray_advisor.evaluate_spray_time(
                lat, lon, target_dt, product
            )

            return {
                "location": {"lat": lat, "lon": lon},
                "target_time": target_datetime,
                "product_type": product_type,
                "evaluation": evaluation.to_dict(),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to evaluate spray time: {e}")
            raise HTTPException(
                status_code=500, detail=f"Spray advisor error: {str(e)}"
            ) from e

    @app.get("/v1/spray/conditions")
    async def get_spray_conditions_info():
        """
        معلومات ظروف الرش | Get Spray Conditions Information

        Get detailed information about spray conditions, risk factors, and guidelines.

        **Returns:**
        Reference information about:
        - Ideal conditions for each product type
        - Risk factors and their meanings
        - Spray condition levels
        - Delta-T guidelines
        - Yemen-specific considerations

        **Example:**
        ```
        GET /v1/spray/conditions
        ```
        """
        return {
            "ideal_conditions": {
                "general": {
                    "temperature_c": {"min": 10, "max": 30},
                    "humidity_percent": {"min": 40, "max": 80},
                    "wind_speed_kmh": {"max": 15},
                    "rain_probability_percent": {"max": 20},
                    "delta_t_c": {"min": 2, "max": 8},
                },
                "herbicide": {
                    "temperature_c": {"min": 15, "max": 28},
                    "humidity_percent": {"min": 50},
                    "rain_free_hours_after": 6,
                    "notes_ar": "درجة حرارة أعلى مطلوبة لامتصاص أفضل",
                    "notes_en": "Higher temperature needed for better absorption",
                },
                "insecticide": {
                    "wind_speed_kmh": {"max": 10},
                    "temperature_c": {"min": 12, "max": 28},
                    "notes_ar": "رياح أقل مطلوبة للتلامس الجيد",
                    "notes_en": "Lower wind needed for good contact",
                },
                "fungicide": {
                    "humidity_percent": {"max": 70},
                    "temperature_c": {"max": 25},
                    "notes_ar": "رطوبة أقل تقلل انتشار الجراثيم",
                    "notes_en": "Lower humidity reduces spore spread",
                },
                "foliar_fertilizer": {
                    "humidity_percent": {"min": 60},
                    "temperature_c": {"max": 28},
                    "notes_ar": "رطوبة أعلى تحسن الامتصاص",
                    "notes_en": "Higher humidity improves absorption",
                },
                "growth_regulator": {
                    "temperature_c": {"min": 15, "max": 25},
                    "humidity_percent": {"min": 50},
                    "wind_speed_kmh": {"max": 12},
                    "notes_ar": "ظروف معتدلة مطلوبة",
                    "notes_en": "Moderate conditions required",
                },
            },
            "condition_levels": {
                "excellent": {
                    "score_range": "85-100",
                    "description_ar": "ظروف ممتازة - المضي قدماً بثقة",
                    "description_en": "Perfect conditions - proceed with confidence",
                },
                "good": {
                    "score_range": "70-84",
                    "description_ar": "ظروف جيدة - آمن للمضي قدماً",
                    "description_en": "Good conditions - safe to proceed",
                },
                "marginal": {
                    "score_range": "50-69",
                    "description_ar": "ظروف هامشية - توخى الحذر",
                    "description_en": "Marginal conditions - exercise caution",
                },
                "poor": {
                    "score_range": "30-49",
                    "description_ar": "ظروف غير موصى بها - فكر في التأجيل",
                    "description_en": "Poor conditions - consider postponing",
                },
                "dangerous": {
                    "score_range": "0-29",
                    "description_ar": "⚠️ لا ترش! ظروف خطيرة",
                    "description_en": "⚠️ DO NOT SPRAY! Dangerous conditions",
                },
            },
            "risk_factors": {
                "spray_drift": {
                    "cause_ar": "رياح قوية (> 15 كم/س)",
                    "cause_en": "High wind (> 15 km/h)",
                    "impact_ar": "انجراف الرذاذ إلى مناطق غير مستهدفة",
                    "impact_en": "Spray drifts to non-target areas",
                    "mitigation_ar": "قلل ضغط الرش، استخدم فوهات أكبر، أو أجّل",
                    "mitigation_en": "Reduce pressure, use larger nozzles, or postpone",
                },
                "wash_off": {
                    "cause_ar": "أمطار متوقعة (> 20% احتمال)",
                    "cause_en": "Rain forecast (> 20% probability)",
                    "impact_ar": "غسل المبيد قبل الامتصاص",
                    "impact_en": "Product washed off before absorption",
                    "mitigation_ar": "انتظر 4-6 ساعات بدون مطر بعد الرش",
                    "mitigation_en": "Wait for 4-6 hours rain-free after spraying",
                },
                "evaporation": {
                    "cause_ar": "رطوبة منخفضة + حرارة مرتفعة",
                    "cause_en": "Low humidity + high temperature",
                    "impact_ar": "تبخر القطرات قبل الوصول للهدف",
                    "impact_en": "Droplets evaporate before reaching target",
                    "mitigation_ar": "ارش في الصباح الباكر أو المساء",
                    "mitigation_en": "Spray early morning or evening",
                },
                "phytotoxicity": {
                    "cause_ar": "حرارة مرتفعة (> 30°م)",
                    "cause_en": "High temperature (> 30°C)",
                    "impact_ar": "إتلاف النبات من الحرارة + الكيماويات",
                    "impact_en": "Plant damage from heat + chemicals",
                    "mitigation_ar": "ارش في أوقات أبرد، قلل الجرعة",
                    "mitigation_en": "Spray during cooler times, reduce dosage",
                },
                "inversion_risk": {
                    "cause_ar": "دلتا-T منخفض (< 2°م)",
                    "cause_en": "Low Delta-T (< 2°C)",
                    "impact_ar": "انعكاس حراري - قطرات معلقة في الهواء",
                    "impact_en": "Temperature inversion - droplets suspended",
                    "mitigation_ar": "انتظر حتى تستقر الظروف الجوية",
                    "mitigation_en": "Wait for atmospheric conditions to stabilize",
                },
            },
            "delta_t_guide": {
                "description_ar": "الفرق بين درجة الحرارة الجافة والرطبة",
                "description_en": "Difference between dry bulb and wet bulb temperature",
                "ranges": {
                    "too_low": {
                        "value": "< 2°C",
                        "description_ar": "خطر انعكاس حراري",
                        "description_en": "Temperature inversion risk",
                    },
                    "ideal": {
                        "value": "2-8°C",
                        "description_ar": "ظروف مثالية للرش",
                        "description_en": "Ideal spraying conditions",
                    },
                    "too_high": {
                        "value": "> 8°C",
                        "description_ar": "تبخر سريع للقطرات",
                        "description_en": "Rapid droplet evaporation",
                    },
                },
            },
            "yemen_considerations": {
                "highlands": {
                    "regions_ar": "صنعاء، إب، ذمار (ارتفاع > 1500م)",
                    "regions_en": "Sanaa, Ibb, Dhamar (elevation > 1500m)",
                    "notes_ar": "انتبه لدرجات الحرارة المنخفضة صباحاً، خطر صقيع في الشتاء",
                    "notes_en": "Watch for low morning temps, frost risk in winter",
                    "best_time_ar": "منتصف النهار (10 ص - 3 م)",
                    "best_time_en": "Mid-day (10 AM - 3 PM)",
                },
                "coastal": {
                    "regions_ar": "الحديدة، عدن، المكلا",
                    "regions_en": "Hodeidah, Aden, Mukalla",
                    "notes_ar": "رطوبة عالية، رياح ساحلية، تجنب منتصف النهار في الصيف",
                    "notes_en": "High humidity, coastal winds, avoid midday in summer",
                    "best_time_ar": "الصباح الباكر (6-9 ص) أو المساء (4-6 م)",
                    "best_time_en": "Early morning (6-9 AM) or evening (4-6 PM)",
                },
                "mid_elevation": {
                    "regions_ar": "تعز، ريمة",
                    "regions_en": "Taiz, Raymah",
                    "notes_ar": "ظروف معتدلة، راقب الرياح الجبلية",
                    "notes_en": "Moderate conditions, watch for mountain winds",
                    "best_time_ar": "الصباح (7-11 ص)",
                    "best_time_en": "Morning (7-11 AM)",
                },
            },
            "safety_reminders_ar": [
                "ارتدِ معدات الحماية الشخصية دائماً (قفازات، نظارات، قناع)",
                "اقرأ ملصق المبيد واتبع التعليمات",
                "احتفظ بسجل للرش (التاريخ، الوقت، المنتج، الظروف)",
                "تجنب الرش بالقرب من المنازل والمياه",
                "نظف المعدات بعد الاستخدام",
            ],
            "safety_reminders_en": [
                "Always wear PPE (gloves, goggles, mask)",
                "Read product label and follow instructions",
                "Keep spray records (date, time, product, conditions)",
                "Avoid spraying near homes and water bodies",
                "Clean equipment after use",
            ],
        }

    logger.info("Spray advisor API endpoints registered successfully")
