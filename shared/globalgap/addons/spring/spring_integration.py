"""
SPRING Integration Module
وحدة تكامل SPRING

Integration with irrigation-smart service, water footprint calculations,
usage alerts, and seasonal pattern tracking.

التكامل مع خدمة الري الذكي، حسابات البصمة المائية،
تنبيهات الاستخدام، وتتبع الأنماط الموسمية.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .water_metrics import (
    WaterSource,
    WaterUsageMetric,
)

logger = logging.getLogger(__name__)

# ==================== Alert Models ====================


class AlertSeverity(StrEnum):
    """Alert severity level / مستوى خطورة التنبيه"""

    INFO = "INFO"  # معلومات
    WARNING = "WARNING"  # تحذير
    CRITICAL = "CRITICAL"  # حرج


class AlertType(StrEnum):
    """Alert type / نوع التنبيه"""

    EXCESSIVE_USAGE = "EXCESSIVE_USAGE"  # استخدام مفرط
    PERMIT_LIMIT_APPROACHING = "PERMIT_LIMIT_APPROACHING"  # الاقتراب من حد التصريح
    PERMIT_LIMIT_EXCEEDED = "PERMIT_LIMIT_EXCEEDED"  # تجاوز حد التصريح
    WATER_QUALITY_ISSUE = "WATER_QUALITY_ISSUE"  # مشكلة جودة المياه
    EFFICIENCY_DECLINE = "EFFICIENCY_DECLINE"  # انخفاض الكفاءة
    GROUNDWATER_DEPLETION = "GROUNDWATER_DEPLETION"  # استنزاف المياه الجوفية
    SEASONAL_ANOMALY = "SEASONAL_ANOMALY"  # شذوذ موسمي
    MAINTENANCE_DUE = "MAINTENANCE_DUE"  # صيانة مستحقة
    QAT_VS_FOOD_WATER_USE = "QAT_VS_FOOD_WATER_USE"  # استخدام المياه القات مقابل الغذاء


class WaterUsageAlert(BaseModel):
    """
    Water usage alert
    تنبيه استخدام المياه
    """

    alert_id: str = Field(..., description="Alert identifier / معرف التنبيه")
    alert_type: AlertType = Field(..., description="Alert type / نوع التنبيه")
    severity: AlertSeverity = Field(..., description="Severity level / مستوى الخطورة")

    farm_id: str = Field(..., description="Farm identifier / معرف المزرعة")
    source_id: str | None = Field(None, description="Water source ID / معرف مصدر المياه")

    triggered_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Trigger date / تاريخ التفعيل"
    )

    title_en: str = Field(..., description="Alert title (English) / عنوان التنبيه")
    title_ar: str = Field(..., description="Alert title (Arabic) / عنوان التنبيه")

    message_en: str = Field(..., description="Alert message (English) / رسالة التنبيه")
    message_ar: str = Field(..., description="Alert message (Arabic) / رسالة التنبيه")

    threshold_value: float | None = Field(None, description="Threshold value / قيمة العتبة")
    actual_value: float | None = Field(None, description="Actual value / القيمة الفعلية")

    recommended_action_en: str | None = Field(None, description="Recommended action (EN) / الإجراء الموصى به")
    recommended_action_ar: str | None = Field(None, description="Recommended action (AR) / الإجراء الموصى به")

    is_acknowledged: bool = Field(False, description="Alert acknowledged / تم الإقرار بالتنبيه")
    acknowledged_date: datetime | None = Field(None, description="Acknowledgement date / تاريخ الإقرار")

    is_resolved: bool = Field(False, description="Alert resolved / تم حل التنبيه")
    resolved_date: datetime | None = Field(None, description="Resolution date / تاريخ الحل")

    model_config = ConfigDict()


# ==================== Water Footprint Models ====================


class CropWaterFootprint(BaseModel):
    """
    Water footprint for a specific crop
    البصمة المائية لمحصول معين
    """

    crop_type: str = Field(..., description="Crop type / نوع المحصول")
    production_kg: float = Field(..., gt=0, description="Production (kg) / الإنتاج")

    # Water footprint components (m³/kg)
    green_water_m3_per_kg: float = Field(0, ge=0, description="Green water (rainfall) / المياه الخضراء")
    blue_water_m3_per_kg: float = Field(0, ge=0, description="Blue water (irrigation) / المياه الزرقاء")
    grey_water_m3_per_kg: float = Field(0, ge=0, description="Grey water (pollution) / المياه الرمادية")

    total_water_footprint_m3_per_kg: float = Field(..., ge=0, description="Total footprint (m³/kg) / البصمة الكلية")

    # Benchmarks
    regional_benchmark_m3_per_kg: float | None = Field(None, description="Regional benchmark / المعيار الإقليمي")
    global_benchmark_m3_per_kg: float | None = Field(None, description="Global benchmark / المعيار العالمي")

    performance_vs_benchmark: str | None = Field(None, description="Performance rating / تقييم الأداء")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "crop_type": "Tomatoes",
                "production_kg": 50000,
                "green_water_m3_per_kg": 0.05,
                "blue_water_m3_per_kg": 0.15,
                "grey_water_m3_per_kg": 0.02,
                "total_water_footprint_m3_per_kg": 0.22,
                "regional_benchmark_m3_per_kg": 0.25,
                "global_benchmark_m3_per_kg": 0.20,
                "performance_vs_benchmark": "Better than regional, close to global",
            }
        },
    )


class SeasonalPattern(BaseModel):
    """
    Seasonal water usage pattern
    نمط استخدام المياه الموسمي
    """

    season: str = Field(..., description="Season name / اسم الموسم")
    start_date: date = Field(..., description="Season start / بداية الموسم")
    end_date: date = Field(..., description="Season end / نهاية الموسم")

    total_water_use_m3: float = Field(..., ge=0, description="Total water use (m³) / استخدام المياه الكلي")
    average_daily_use_m3: float = Field(..., ge=0, description="Avg daily use (m³) / الاستخدام اليومي المتوسط")
    peak_daily_use_m3: float = Field(..., ge=0, description="Peak daily use (m³) / الاستخدام اليومي الأقصى")

    rainfall_contribution_m3: float = Field(0, ge=0, description="Rainfall (m³) / الأمطار")
    rainfall_percentage: float = Field(0, ge=0, le=100, description="Rainfall % / نسبة الأمطار")

    dominant_crops: list[str] = Field(default_factory=list, description="Dominant crops / المحاصيل السائدة")
    irrigation_methods_used: list[str] = Field(default_factory=list, description="Irrigation methods / طرق الري")

    average_efficiency_percent: float | None = Field(None, description="Avg efficiency % / الكفاءة المتوسطة")

    notes: str | None = Field(None, description="Season notes / ملاحظات الموسم")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "season": "Winter 2024",
                "start_date": "2024-10-01",
                "end_date": "2024-12-31",
                "total_water_use_m3": 15000,
                "average_daily_use_m3": 163,
                "peak_daily_use_m3": 250,
                "rainfall_contribution_m3": 500,
                "rainfall_percentage": 3.33,
                "dominant_crops": ["Tomatoes", "Cucumbers", "Lettuce"],
                "irrigation_methods_used": ["DRIP", "SPRINKLER"],
                "average_efficiency_percent": 82.0,
                "notes": "Good rainfall in November reduced irrigation needs",
            }
        },
    )


# ==================== Integration Class ====================


class SpringIntegration:
    """
    Integration with irrigation-smart service and SPRING analytics
    التكامل مع خدمة الري الذكي وتحليلات SPRING
    """

    def __init__(
        self,
        farm_id: str,
        irrigation_service_url: str | None = None,
        api_key: str | None = None,
    ):
        """
        Initialize SPRING integration

        Args:
            farm_id: Farm identifier
            irrigation_service_url: URL for irrigation-smart service API
            api_key: API key for authentication
        """
        self.farm_id = farm_id
        self.irrigation_service_url = irrigation_service_url or "http://irrigation-smart:8080/api/v1"
        self.api_key = api_key

    def pull_irrigation_data(
        self,
        start_date: date,
        end_date: date,
        include_sensor_data: bool = True,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """
        Pull irrigation data from irrigation-smart service
        سحب بيانات الري من خدمة الري الذكي

        Args:
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            include_sensor_data: Include soil moisture sensor data
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary containing irrigation data

        Raises:
            httpx.HTTPError: If API request fails after retries
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        params = {
            "farm_id": self.farm_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "include_sensors": str(include_sensor_data).lower(),
        }

        url = f"{self.irrigation_service_url}/irrigation/data"

        last_error = None
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    return response.json()

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    "Timeout pulling irrigation data (attempt %d/%d): %s",
                    attempt + 1,
                    max_retries,
                    str(e),
                )
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(
                    "HTTP error pulling irrigation data (attempt %d/%d): %s",
                    attempt + 1,
                    max_retries,
                    str(e),
                )
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    break
            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    "Request error pulling irrigation data (attempt %d/%d): %s",
                    attempt + 1,
                    max_retries,
                    str(e),
                )

        # If all retries failed, log and return empty structure
        logger.error(
            "Failed to pull irrigation data after %d attempts: %s",
            max_retries,
            str(last_error),
        )

        # Return fallback structure for graceful degradation
        return {
            "farm_id": self.farm_id,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "usage_records": [],
            "sensor_readings": [] if include_sensor_data else None,
            "weather_data": {},
            "irrigation_schedules": [],
            "system_status": {
                "active_zones": 0,
                "maintenance_alerts": [],
            },
            "_error": str(last_error) if last_error else None,
            "_fallback": True,
        }

    async def pull_irrigation_data_async(
        self,
        start_date: date,
        end_date: date,
        include_sensor_data: bool = True,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """
        Pull irrigation data asynchronously from irrigation-smart service
        سحب بيانات الري بشكل غير متزامن من خدمة الري الذكي

        Args:
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            include_sensor_data: Include soil moisture sensor data
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary containing irrigation data
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        params = {
            "farm_id": self.farm_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "include_sensors": str(include_sensor_data).lower(),
        }

        url = f"{self.irrigation_service_url}/irrigation/data"

        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    return response.json()

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    "Timeout pulling irrigation data async (attempt %d/%d)",
                    attempt + 1,
                    max_retries,
                )
            except httpx.HTTPStatusError as e:
                last_error = e
                if 400 <= e.response.status_code < 500:
                    break
            except httpx.RequestError as e:
                last_error = e

        logger.error("Failed to pull irrigation data async: %s", str(last_error))
        return {
            "farm_id": self.farm_id,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "usage_records": [],
            "sensor_readings": [] if include_sensor_data else None,
            "weather_data": {},
            "irrigation_schedules": [],
            "system_status": {"active_zones": 0, "maintenance_alerts": []},
            "_error": str(last_error) if last_error else None,
            "_fallback": True,
        }

    def push_alerts_to_service(
        self,
        alerts: list[WaterUsageAlert],
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """
        Push water usage alerts to irrigation-smart service
        إرسال تنبيهات استخدام المياه إلى خدمة الري الذكي

        Args:
            alerts: List of alerts to push
            timeout: Request timeout in seconds

        Returns:
            API response with push status
        """
        if not alerts:
            return {"status": "success", "pushed_count": 0}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        url = f"{self.irrigation_service_url}/alerts/batch"
        payload = {
            "farm_id": self.farm_id,
            "alerts": [alert.model_dump(mode="json") for alert in alerts],
        }

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to push alerts: %s", str(e))
            return {
                "status": "error",
                "error": str(e),
                "pushed_count": 0,
            }

    def calculate_water_footprint(
        self,
        crop_type: str,
        production_kg: float,
        irrigation_water_m3: float,
        rainfall_water_m3: float = 0,
        fertilizer_use_kg: float = 0,
        leaching_fraction: float = 0.1,
    ) -> CropWaterFootprint:
        """
        Calculate water footprint for a crop
        حساب البصمة المائية للمحصول

        Args:
            crop_type: Type of crop
            production_kg: Total production in kg
            irrigation_water_m3: Irrigation water used (blue water)
            rainfall_water_m3: Effective rainfall (green water)
            fertilizer_use_kg: Fertilizer used (for grey water calculation)
            leaching_fraction: Leaching fraction for pollution calculation

        Returns:
            Crop water footprint
        """
        # Blue water (irrigation)
        blue_water_per_kg = irrigation_water_m3 / production_kg if production_kg > 0 else 0

        # Green water (rainfall)
        green_water_per_kg = rainfall_water_m3 / production_kg if production_kg > 0 else 0

        # Grey water (pollution - simplified calculation)
        # Grey water = (fertilizer load) / (max concentration - natural concentration)
        # Simplified: assume 10% of fertilizer leaches, needs dilution
        grey_water_m3 = fertilizer_use_kg * leaching_fraction * 100  # Simplified factor
        grey_water_per_kg = grey_water_m3 / production_kg if production_kg > 0 else 0

        # Total footprint
        total_footprint = blue_water_per_kg + green_water_per_kg + grey_water_per_kg

        # Benchmarks (example values - should be from database)
        benchmarks = self._get_crop_benchmarks(crop_type)

        # Performance rating
        performance = self._assess_footprint_performance(
            total_footprint,
            benchmarks.get("regional"),
            benchmarks.get("global"),
        )

        return CropWaterFootprint(
            crop_type=crop_type,
            production_kg=production_kg,
            green_water_m3_per_kg=round(green_water_per_kg, 4),
            blue_water_m3_per_kg=round(blue_water_per_kg, 4),
            grey_water_m3_per_kg=round(grey_water_per_kg, 4),
            total_water_footprint_m3_per_kg=round(total_footprint, 4),
            regional_benchmark_m3_per_kg=benchmarks.get("regional"),
            global_benchmark_m3_per_kg=benchmarks.get("global"),
            performance_vs_benchmark=performance,
        )

    # ==================== Mock Data Generation Methods ====================

    def _generate_mock_usage_records(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        """Generate realistic mock water usage records for the period"""
        import random
        from datetime import timedelta

        records = []
        current_date = start_date
        record_counter = 1

        # Define farm irrigation patterns (realistic for Yemen agriculture)
        water_sources = [
            {"source_id": "WELL-001", "name": "North Field Well"},
            {"source_id": "WELL-002", "name": "South Field Well"},
            {"source_id": "CANAL-001", "name": "Main Canal"},
        ]

        fields = [
            {"field_id": "FIELD-N1", "crop": "Tomatoes", "area": 2.5, "method": "DRIP"},
            {"field_id": "FIELD-N2", "crop": "Cucumbers", "area": 1.8, "method": "DRIP"},
            {"field_id": "FIELD-S1", "crop": "Wheat", "area": 5.0, "method": "SPRINKLER"},
            {"field_id": "FIELD-S2", "crop": "Date Palm", "area": 3.5, "method": "SUBSURFACE"},
        ]

        while current_date <= end_date:
            # Generate 2-3 irrigation events per day (realistic for Yemen)
            num_events = random.randint(1, 3)

            for _ in range(num_events):
                source = random.choice(water_sources)
                field = random.choice(fields)

                # Realistic water volume based on field size and crop
                if field["crop"] == "Date Palm":
                    volume = random.uniform(80, 150)
                    duration = random.uniform(3, 6)
                elif field["crop"] in ["Tomatoes", "Cucumbers"]:
                    volume = random.uniform(60, 120)
                    duration = random.uniform(4, 8)
                else:  # Wheat, others
                    volume = random.uniform(100, 200)
                    duration = random.uniform(5, 10)

                usage_id = f"WU-{current_date.strftime('%Y%m%d')}-{record_counter:04d}"
                flow_rate = volume / duration if duration > 0 else 0

                records.append(
                    {
                        "usage_id": usage_id,
                        "source_id": source["source_id"],
                        "source_name": source["name"],
                        "field_id": field["field_id"],
                        "crop_type": field["crop"],
                        "measurement_date": current_date.isoformat(),
                        "volume_cubic_meters": round(volume, 2),
                        "crop_area_hectares": field["area"],
                        "irrigation_method": field["method"],
                        "duration_hours": round(duration, 2),
                        "flow_rate_m3_per_hour": round(flow_rate, 2),
                    }
                )
                record_counter += 1

            current_date += timedelta(days=1)

        return records

    def _generate_mock_sensor_readings(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        """Generate realistic mock soil moisture sensor readings"""
        import random
        from datetime import timedelta

        readings = []
        current_date = start_date

        # Define sensor locations (one per field)
        sensors = [
            {"sensor_id": "SM-001", "field_id": "FIELD-N1", "depth_cm": 20},
            {"sensor_id": "SM-002", "field_id": "FIELD-N2", "depth_cm": 20},
            {"sensor_id": "SM-003", "field_id": "FIELD-S1", "depth_cm": 30},
            {"sensor_id": "SM-004", "field_id": "FIELD-S2", "depth_cm": 40},
        ]

        while current_date <= end_date:
            # Generate 2 readings per day (morning and evening)
            for hour in [6, 18]:
                for sensor in sensors:
                    # Realistic soil moisture values (30-70% is optimal, lower after irrigation)
                    base_moisture = random.uniform(35, 65)
                    soil_moisture = max(25, min(75, base_moisture))
                    soil_temperature = random.uniform(18, 35)  # Yemen climate

                    readings.append(
                        {
                            "reading_id": f"SR-{current_date.strftime('%Y%m%d')}-{sensor['sensor_id']}-{hour:02d}",
                            "sensor_id": sensor["sensor_id"],
                            "field_id": sensor["field_id"],
                            "measurement_date": current_date.isoformat(),
                            "measurement_hour": hour,
                            "soil_moisture_percent": round(soil_moisture, 1),
                            "soil_temperature_celsius": round(soil_temperature, 1),
                            "sensor_depth_cm": sensor["depth_cm"],
                            "battery_level_percent": random.randint(70, 100),
                            "signal_strength": random.choice(["STRONG", "GOOD", "FAIR"]),
                        }
                    )

            current_date += timedelta(days=1)

        return readings

    def _generate_mock_weather_data(self, start_date: date, end_date: date) -> dict[str, Any]:
        """Generate realistic mock weather data for the period"""
        import random
        from datetime import timedelta

        weather_records = []
        current_date = start_date

        while current_date <= end_date:
            # Realistic Yemen weather patterns
            min_temp = random.uniform(15, 25)  # Cooler at night
            max_temp = random.uniform(28, 40)  # Hotter during day
            rainfall = random.uniform(0, 5) if random.random() > 0.8 else 0  # 20% chance of rain
            relative_humidity = random.uniform(30, 70)
            wind_speed = random.uniform(5, 20)  # km/h

            weather_records.append(
                {
                    "date": current_date.isoformat(),
                    "min_temperature_celsius": round(min_temp, 1),
                    "max_temperature_celsius": round(max_temp, 1),
                    "avg_temperature_celsius": round((min_temp + max_temp) / 2, 1),
                    "rainfall_mm": round(rainfall, 1),
                    "relative_humidity_percent": round(relative_humidity, 1),
                    "wind_speed_kmh": round(wind_speed, 1),
                    "solar_radiation_mj_m2": round(random.uniform(15, 25), 2),
                    "evapotranspiration_mm": round(random.uniform(3, 8), 2),
                }
            )

            current_date += timedelta(days=1)

        return {
            "weather_records": weather_records,
            "aggregated_rainfall_mm": sum(r["rainfall_mm"] for r in weather_records),
            "avg_temperature_celsius": round(
                sum(r["avg_temperature_celsius"] for r in weather_records) / len(weather_records), 1
            )
            if weather_records
            else 0,
        }

    def _generate_mock_irrigation_schedules(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        """Generate realistic mock irrigation schedules for planned events"""
        import random
        from datetime import timedelta

        schedules = []
        current_date = start_date
        schedule_counter = 1

        fields = [
            {"field_id": "FIELD-N1", "crop": "Tomatoes", "area": 2.5},
            {"field_id": "FIELD-N2", "crop": "Cucumbers", "area": 1.8},
            {"field_id": "FIELD-S1", "crop": "Wheat", "area": 5.0},
            {"field_id": "FIELD-S2", "crop": "Date Palm", "area": 3.5},
        ]

        while current_date <= end_date:
            # Generate 2-3 scheduled events per day
            num_schedules = random.randint(2, 4)

            for _ in range(num_schedules):
                field = random.choice(fields)
                start_hour = random.choice([5, 6, 7, 18, 19, 20])  # Early morning or evening
                duration = random.uniform(3, 8)

                # Realistic planned volumes
                if field["crop"] == "Date Palm":
                    planned_volume = random.uniform(80, 150)
                elif field["crop"] in ["Tomatoes", "Cucumbers"]:
                    planned_volume = random.uniform(60, 120)
                else:
                    planned_volume = random.uniform(100, 200)

                status = random.choice(["SCHEDULED", "IN_PROGRESS", "COMPLETED"])

                schedules.append(
                    {
                        "schedule_id": f"SCH-{current_date.strftime('%Y%m%d')}-{schedule_counter:04d}",
                        "field_id": field["field_id"],
                        "crop_type": field["crop"],
                        "scheduled_date": current_date.isoformat(),
                        "scheduled_start_hour": start_hour,
                        "planned_duration_hours": round(duration, 1),
                        "planned_volume_cubic_meters": round(planned_volume, 2),
                        "status": status,
                        "priority": random.choice(["LOW", "NORMAL", "HIGH"]),
                        "scheduling_reason": random.choice(
                            [
                                "Soil moisture threshold",
                                "Growth stage",
                                "Weather forecast",
                                "Manual request",
                            ]
                        ),
                    }
                )
                schedule_counter += 1

            current_date += timedelta(days=1)

        return schedules

    def _generate_mock_system_status(self) -> dict[str, Any]:
        """Generate realistic mock irrigation system status"""
        return {
            "active_zones": 4,
            "total_zones": 6,
            "zones_operational": ["ZONE-A", "ZONE-B", "ZONE-C", "ZONE-D"],
            "zones_offline": ["ZONE-E", "ZONE-F"],
            "total_equipment": 12,
            "equipment_operational": 11,
            "equipment_needing_maintenance": 1,
            "maintenance_alerts": [
                {
                    "alert_id": "MA-001",
                    "equipment_id": "PUMP-002",
                    "alert_type": "SCHEDULED_MAINTENANCE",
                    "priority": "MEDIUM",
                    "description": "Filter replacement due",
                    "recommended_action": "Schedule filter replacement within 7 days",
                    "last_maintenance": "2024-12-01",
                    "next_scheduled": "2025-01-15",
                }
            ],
            "last_system_check": datetime.now(UTC).isoformat(),
            "overall_system_health": "GOOD",
            "system_uptime_percent": 98.5,
        }

    def generate_usage_alerts(
        self,
        usage_records: list[WaterUsageMetric],
        water_sources: list[WaterSource],
        current_month_usage_m3: float,
        previous_month_usage_m3: float | None = None,
        groundwater_level_change_m: float | None = None,
    ) -> list[WaterUsageAlert]:
        """
        Generate water usage alerts
        إنشاء تنبيهات استخدام المياه

        Args:
            usage_records: Recent usage records
            water_sources: Water sources list
            current_month_usage_m3: Current month total usage
            previous_month_usage_m3: Previous month usage for comparison
            groundwater_level_change_m: Groundwater level change (negative = declining)

        Returns:
            List of alerts
        """
        alerts = []

        # Check permit limits
        for source in water_sources:
            if source.max_daily_extraction_m3:
                # Calculate recent daily usage from this source
                source_usage = [u for u in usage_records if u.source_id == source.source_id]
                if source_usage:
                    daily_avg = sum(u.volume_cubic_meters for u in source_usage) / len(source_usage)

                    # Alert if approaching limit (>90%)
                    if daily_avg > source.max_daily_extraction_m3 * 0.9:
                        alerts.append(self._create_permit_limit_alert(source, daily_avg, AlertSeverity.WARNING))

                    # Critical alert if exceeding limit
                    if daily_avg > source.max_daily_extraction_m3:
                        alerts.append(self._create_permit_limit_alert(source, daily_avg, AlertSeverity.CRITICAL))

        # Check for excessive usage increase
        if previous_month_usage_m3 and current_month_usage_m3 > previous_month_usage_m3 * 1.3:
            alerts.append(self._create_excessive_usage_alert(current_month_usage_m3, previous_month_usage_m3))

        # Check groundwater depletion (critical for Yemen)
        if groundwater_level_change_m and groundwater_level_change_m < -1.0:
            alerts.append(self._create_groundwater_depletion_alert(groundwater_level_change_m))

        # Check for qat vs food crops water use (Yemen-specific)
        qat_usage = sum(u.volume_cubic_meters for u in usage_records if u.crop_type and "qat" in u.crop_type.lower())
        if qat_usage > 0:
            total_usage = sum(u.volume_cubic_meters for u in usage_records)
            qat_percentage = (qat_usage / total_usage * 100) if total_usage > 0 else 0

            if qat_percentage > 30:
                alerts.append(self._create_qat_water_use_alert(qat_percentage))

        return alerts

    def track_seasonal_patterns(
        self,
        usage_records: list[WaterUsageMetric],
        start_date: date,
        end_date: date,
    ) -> list[SeasonalPattern]:
        """
        Track seasonal water usage patterns
        تتبع أنماط استخدام المياه الموسمية

        Args:
            usage_records: Water usage records
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            List of seasonal patterns
        """
        # Define Yemen agricultural seasons
        seasons = self._define_yemen_seasons(start_date.year)

        patterns = []

        for season in seasons:
            season_records = [r for r in usage_records if season["start"] <= r.measurement_date <= season["end"]]

            if not season_records:
                continue

            # Calculate statistics
            total_usage = sum(r.volume_cubic_meters for r in season_records)
            days_in_season = (season["end"] - season["start"]).days + 1
            avg_daily = total_usage / days_in_season if days_in_season > 0 else 0
            peak_daily = max((r.volume_cubic_meters for r in season_records), default=0)

            # Dominant crops
            crop_counts = {}
            for r in season_records:
                if r.crop_type:
                    crop_counts[r.crop_type] = crop_counts.get(r.crop_type, 0) + 1
            dominant_crops = sorted(crop_counts.keys(), key=lambda k: crop_counts[k], reverse=True)[:5]

            # Irrigation methods
            methods = list({r.irrigation_method.value for r in season_records if r.irrigation_method})

            pattern = SeasonalPattern(
                season=season["name"],
                start_date=season["start"],
                end_date=season["end"],
                total_water_use_m3=total_usage,
                average_daily_use_m3=avg_daily,
                peak_daily_use_m3=peak_daily,
                rainfall_contribution_m3=0,  # Would calculate from rainfall data
                rainfall_percentage=0,
                dominant_crops=dominant_crops,
                irrigation_methods_used=methods,
                average_efficiency_percent=None,  # Would calculate from efficiency records
            )

            patterns.append(pattern)

        return patterns

    # ==================== Helper Methods ====================

    def _get_crop_benchmarks(self, crop_type: str) -> dict[str, float | None]:
        """Get water footprint benchmarks for crop type"""
        # Simplified benchmark data (should be from database)
        benchmarks = {
            "tomatoes": {"regional": 0.25, "global": 0.20},
            "cucumbers": {"regional": 0.22, "global": 0.18},
            "lettuce": {"regional": 0.12, "global": 0.10},
            "peppers": {"regional": 0.28, "global": 0.24},
            "onions": {"regional": 0.15, "global": 0.13},
            "wheat": {"regional": 1.50, "global": 1.30},
            "qat": {"regional": 2.00, "global": None},  # High water use
        }

        crop_key = crop_type.lower()
        return benchmarks.get(crop_key, {"regional": None, "global": None})

    def _assess_footprint_performance(
        self,
        actual: float,
        regional_benchmark: float | None,
        global_benchmark: float | None,
    ) -> str:
        """Assess water footprint performance"""
        if not regional_benchmark:
            return "No benchmark available"

        if actual <= regional_benchmark * 0.9:
            return "Excellent - significantly better than regional average"
        elif actual <= regional_benchmark:
            return "Good - better than regional average"
        elif actual <= regional_benchmark * 1.1:
            return "Acceptable - close to regional average"
        elif actual <= regional_benchmark * 1.3:
            return "Needs improvement - above regional average"
        else:
            return "Poor - significantly above regional average"

    def _create_permit_limit_alert(
        self,
        source: WaterSource,
        actual_usage: float,
        severity: AlertSeverity,
    ) -> WaterUsageAlert:
        """Create permit limit alert"""
        percentage = (actual_usage / source.max_daily_extraction_m3 * 100) if source.max_daily_extraction_m3 else 0

        if severity == AlertSeverity.CRITICAL:
            title_en = f"Permit Limit Exceeded - {source.name_en}"
            title_ar = f"تجاوز حد التصريح - {source.name_ar}"
            message_en = (
                f"Water extraction from {source.name_en} exceeds permitted daily limit by {percentage - 100:.1f}%"
            )
            message_ar = (
                f"استخراج المياه من {source.name_ar} يتجاوز الحد اليومي المسموح به بنسبة {percentage - 100:.1f}%"
            )
            action_en = "Immediately reduce water extraction or risk permit violation"
            action_ar = "تقليل استخراج المياه فوراً أو خطر انتهاك التصريح"
            alert_type = AlertType.PERMIT_LIMIT_EXCEEDED
        else:
            title_en = f"Approaching Permit Limit - {source.name_en}"
            title_ar = f"الاقتراب من حد التصريح - {source.name_ar}"
            message_en = f"Water extraction from {source.name_en} at {percentage:.1f}% of permitted daily limit"
            message_ar = f"استخراج المياه من {source.name_ar} عند {percentage:.1f}% من الحد اليومي المسموح به"
            action_en = "Monitor usage closely and implement water conservation measures"
            action_ar = "مراقبة الاستخدام عن كثب وتنفيذ تدابير الحفاظ على المياه"
            alert_type = AlertType.PERMIT_LIMIT_APPROACHING

        return WaterUsageAlert(
            alert_id=f"ALERT-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            alert_type=alert_type,
            severity=severity,
            farm_id=self.farm_id,
            source_id=source.source_id,
            title_en=title_en,
            title_ar=title_ar,
            message_en=message_en,
            message_ar=message_ar,
            threshold_value=source.max_daily_extraction_m3,
            actual_value=actual_usage,
            recommended_action_en=action_en,
            recommended_action_ar=action_ar,
        )

    def _create_excessive_usage_alert(
        self,
        current_usage: float,
        previous_usage: float,
    ) -> WaterUsageAlert:
        """Create excessive usage alert"""
        increase_pct = (current_usage - previous_usage) / previous_usage * 100

        return WaterUsageAlert(
            alert_id=f"ALERT-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            alert_type=AlertType.EXCESSIVE_USAGE,
            severity=AlertSeverity.WARNING,
            farm_id=self.farm_id,
            title_en="Excessive Water Usage Increase",
            title_ar="زيادة مفرطة في استخدام المياه",
            message_en=f"Water usage increased by {increase_pct:.1f}% compared to previous month",
            message_ar=f"زاد استخدام المياه بنسبة {increase_pct:.1f}% مقارنة بالشهر السابق",
            threshold_value=previous_usage * 1.3,
            actual_value=current_usage,
            recommended_action_en="Review irrigation schedules and check for leaks or system inefficiencies",
            recommended_action_ar="مراجعة جداول الري والتحقق من التسربات أو عدم كفاءة النظام",
        )

    def _create_groundwater_depletion_alert(
        self,
        level_change_m: float,
    ) -> WaterUsageAlert:
        """Create groundwater depletion alert (critical for Yemen)"""
        severity = AlertSeverity.CRITICAL if level_change_m < -3.0 else AlertSeverity.WARNING

        return WaterUsageAlert(
            alert_id=f"ALERT-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            alert_type=AlertType.GROUNDWATER_DEPLETION,
            severity=severity,
            farm_id=self.farm_id,
            title_en="Groundwater Level Declining",
            title_ar="انخفاض مستوى المياه الجوفية",
            message_en=f"Groundwater level declined by {abs(level_change_m):.1f} meters. "
            f"This is critical for Yemen's water sustainability.",
            message_ar=f"انخفض مستوى المياه الجوفية بمقدار {abs(level_change_m):.1f} متر. "
            f"هذا أمر بالغ الأهمية لاستدامة المياه في اليمن.",
            threshold_value=-1.0,
            actual_value=level_change_m,
            recommended_action_en="Implement urgent water conservation measures: increase drip irrigation, "
            "reduce water-intensive crops, explore rainwater harvesting",
            recommended_action_ar="تنفيذ تدابير عاجلة للحفاظ على المياه: زيادة الري بالتنقيط، "
            "تقليل المحاصيل كثيفة الاستهلاك للمياه، استكشاف حصاد مياه الأمطار",
        )

    def _create_qat_water_use_alert(self, qat_percentage: float) -> WaterUsageAlert:
        """Create alert for high qat water usage (Yemen-specific)"""
        return WaterUsageAlert(
            alert_id=f"ALERT-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            alert_type=AlertType.QAT_VS_FOOD_WATER_USE,
            severity=AlertSeverity.INFO,
            farm_id=self.farm_id,
            title_en="High Water Use for Qat Cultivation",
            title_ar="استخدام عالي للمياه لزراعة القات",
            message_en=f"Qat cultivation accounts for {qat_percentage:.1f}% of water use. "
            f"Consider shifting to food crops for better water sustainability and food security.",
            message_ar=f"زراعة القات تمثل {qat_percentage:.1f}% من استخدام المياه. "
            f"النظر في التحول إلى محاصيل غذائية لاستدامة أفضل للمياه والأمن الغذائي.",
            threshold_value=30.0,
            actual_value=qat_percentage,
            recommended_action_en="Gradually transition water allocation from qat to high-value food crops "
            "(vegetables, fruits) which provide better nutrition and export potential",
            recommended_action_ar="التحول التدريجي لتخصيص المياه من القات إلى محاصيل غذائية ذات قيمة عالية "
            "(الخضروات، الفواكه) والتي توفر تغذية أفضل وإمكانات تصدير",
        )

    def _define_yemen_seasons(self, year: int) -> list[dict[str, Any]]:
        """Define agricultural seasons for Yemen"""
        return [
            {
                "name": f"Winter {year}",
                "start": date(year, 10, 1),
                "end": date(year, 12, 31),
                "description": "Cool season with some rainfall",
            },
            {
                "name": f"Spring {year}",
                "start": date(year, 1, 1),
                "end": date(year, 3, 31),
                "description": "Moderate temperatures",
            },
            {
                "name": f"Pre-Monsoon {year}",
                "start": date(year, 4, 1),
                "end": date(year, 6, 30),
                "description": "Hot and dry, high irrigation demand",
            },
            {
                "name": f"Monsoon {year}",
                "start": date(year, 7, 1),
                "end": date(year, 9, 30),
                "description": "Rainfall season, reduced irrigation needs",
            },
        ]


# ==================== Convenience Functions ====================


def pull_irrigation_data(
    farm_id: str,
    start_date: date,
    end_date: date,
    service_url: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """
    Pull irrigation data from irrigation-smart service
    سحب بيانات الري من خدمة الري الذكي

    Args:
        farm_id: Farm identifier
        start_date: Start date
        end_date: End date
        service_url: Service URL (optional)
        api_key: API key (optional)

    Returns:
        Irrigation data dictionary
    """
    integration = SpringIntegration(farm_id, service_url, api_key)
    return integration.pull_irrigation_data(start_date, end_date)


def calculate_water_footprint(
    crop_type: str,
    production_kg: float,
    irrigation_water_m3: float,
    rainfall_water_m3: float = 0,
    fertilizer_use_kg: float = 0,
) -> CropWaterFootprint:
    """
    Calculate water footprint for a crop
    حساب البصمة المائية للمحصول

    Args:
        crop_type: Crop type
        production_kg: Production in kg
        irrigation_water_m3: Irrigation water
        rainfall_water_m3: Rainfall water
        fertilizer_use_kg: Fertilizer used

    Returns:
        Crop water footprint
    """
    integration = SpringIntegration("temp")
    return integration.calculate_water_footprint(
        crop_type,
        production_kg,
        irrigation_water_m3,
        rainfall_water_m3,
        fertilizer_use_kg,
    )


def generate_usage_alerts(
    farm_id: str,
    usage_records: list[WaterUsageMetric],
    water_sources: list[WaterSource],
    current_month_usage_m3: float,
    previous_month_usage_m3: float | None = None,
    groundwater_level_change_m: float | None = None,
) -> list[WaterUsageAlert]:
    """
    Generate water usage alerts
    إنشاء تنبيهات استخدام المياه

    Args:
        farm_id: Farm identifier
        usage_records: Usage records
        water_sources: Water sources
        current_month_usage_m3: Current month usage
        previous_month_usage_m3: Previous month usage
        groundwater_level_change_m: Groundwater level change

    Returns:
        List of alerts
    """
    integration = SpringIntegration(farm_id)
    return integration.generate_usage_alerts(
        usage_records,
        water_sources,
        current_month_usage_m3,
        previous_month_usage_m3,
        groundwater_level_change_m,
    )


def track_seasonal_patterns(
    farm_id: str,
    usage_records: list[WaterUsageMetric],
    start_date: date,
    end_date: date,
) -> list[SeasonalPattern]:
    """
    Track seasonal water usage patterns
    تتبع أنماط استخدام المياه الموسمية

    Args:
        farm_id: Farm identifier
        usage_records: Usage records
        start_date: Analysis start
        end_date: Analysis end

    Returns:
        List of seasonal patterns
    """
    integration = SpringIntegration(farm_id)
    return integration.track_seasonal_patterns(usage_records, start_date, end_date)
