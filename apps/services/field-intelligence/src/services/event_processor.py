"""
معالج الأحداث - Event Processor
Processes field events and triggers appropriate rules
"""

import logging
from datetime import datetime
from uuid import uuid4

import httpx

from ..models.events import (
    AstronomicalEvent,
    EventCreate,
    EventResponse,
    EventSeverity,
    EventStatus,
    EventType,
    NDVIDropEvent,
    SoilMoistureEvent,
    WeatherAlertEvent,
)
from ..models.rules import Rule
from .rules_engine import RulesEngine

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    معالج الأحداث الحقلية
    Field Event Processor

    يقوم بـ:
    - استقبال الأحداث من مصادر مختلفة
    - معالجة البيانات وتحليلها
    - تفعيل القواعد المناسبة
    - التكامل مع الخدمات الأخرى
    """

    def __init__(self, rules_engine: RulesEngine | None = None):
        self.rules_engine = rules_engine or RulesEngine()
        self.http_client = httpx.AsyncClient(timeout=10.0)

    async def process_event(self, event: EventCreate, available_rules: list[Rule]) -> EventResponse:
        """
        معالجة حدث جديد
        Process new event

        Args:
            event: بيانات الحدث
            available_rules: القواعد المتاحة للتطبيق

        Returns:
            استجابة الحدث مع نتائج التنفيذ
        """
        try:
            # إنشاء معرف الحدث
            event_id = str(uuid4())
            now = datetime.utcnow()

            # تحويل إلى EventResponse
            event_response = EventResponse(
                event_id=event_id,
                tenant_id=event.tenant_id,
                field_id=event.field_id,
                event_type=event.event_type,
                severity=event.severity,
                status=EventStatus.ACTIVE,
                title=event.title,
                title_ar=event.title_ar,
                description=event.description,
                description_ar=event.description_ar,
                source_service=event.source_service,
                metadata=event.metadata,
                location=event.location,
                created_at=now,
                correlation_id=event.correlation_id,
            )

            logger.info(f"⚡ معالجة حدث جديد: {event.event_type.value} للحقل {event.field_id}")

            # تقييم القواعد
            execution_results = await self.rules_engine.evaluate_rules(
                event_response, available_rules
            )

            # تجميع نتائج التنفيذ
            triggered_rules = []
            created_tasks = []
            notifications_sent = 0

            for result in execution_results:
                if result.success:
                    triggered_rules.append(result.rule_id)

                    # استخراج المهام والإشعارات من نتائج التنفيذ
                    for detail in result.execution_details:
                        if detail.get("action_type") == "create_task" and detail.get("success"):
                            created_tasks.append(detail.get("task_id", "unknown"))
                        elif detail.get("action_type") == "send_notification" and detail.get(
                            "success"
                        ):
                            notifications_sent += detail.get("recipients_count", 1)

            # تحديث استجابة الحدث
            event_response.triggered_rules = triggered_rules
            event_response.created_tasks = created_tasks
            event_response.notifications_sent = notifications_sent

            logger.info(
                f"✓ تمت معالجة الحدث {event_id}: "
                f"{len(triggered_rules)} قاعدة، "
                f"{len(created_tasks)} مهمة، "
                f"{notifications_sent} إشعار"
            )

            return event_response

        except Exception as e:
            logger.error(
                f"خطأ في معالجة الحدث: {str(e)}",
                exc_info=True,
            )
            raise

    async def process_ndvi_drop(
        self, field_id: str, tenant_id: str, ndvi_data: NDVIDropEvent
    ) -> EventResponse:
        """
        معالجة حدث انخفاض NDVI
        Process NDVI drop event

        Args:
            field_id: معرف الحقل
            tenant_id: معرف المستأجر
            ndvi_data: بيانات انخفاض NDVI

        Returns:
            استجابة الحدث
        """
        # تحديد الخطورة بناءً على نسبة الانخفاض
        if ndvi_data.drop_percentage >= 30:
            severity = EventSeverity.CRITICAL
        elif ndvi_data.drop_percentage >= 20:
            severity = EventSeverity.HIGH
        elif ndvi_data.drop_percentage >= 10:
            severity = EventSeverity.MEDIUM
        else:
            severity = EventSeverity.LOW

        event = EventCreate(
            tenant_id=tenant_id,
            field_id=field_id,
            event_type=EventType.NDVI_DROP,
            severity=severity,
            title=f"NDVI Drop Detected: {ndvi_data.drop_percentage:.1f}%",
            title_ar=f"انخفاض في مؤشر NDVI: {ndvi_data.drop_percentage:.1f}٪",
            description=(
                f"NDVI dropped from {ndvi_data.previous_ndvi:.3f} "
                f"to {ndvi_data.current_ndvi:.3f} "
                f"({ndvi_data.drop_percentage:.1f}% decrease)"
            ),
            description_ar=(
                f"انخفض مؤشر NDVI من {ndvi_data.previous_ndvi:.3f} "
                f"إلى {ndvi_data.current_ndvi:.3f} "
                f"(انخفاض بنسبة {ndvi_data.drop_percentage:.1f}٪)"
            ),
            source_service="ndvi-engine",
            metadata={
                "current_ndvi": ndvi_data.current_ndvi,
                "previous_ndvi": ndvi_data.previous_ndvi,
                "drop_percentage": ndvi_data.drop_percentage,
                "threshold": ndvi_data.threshold,
                "analysis_date": ndvi_data.analysis_date.isoformat(),
                "affected_area_hectares": ndvi_data.affected_area_hectares,
                "image_url": ndvi_data.image_url,
                "satellite_source": ndvi_data.satellite_source,
            },
        )

        # في الإنتاج، استرجاع القواعد من قاعدة البيانات
        return await self.process_event(event, available_rules=[])

    async def process_weather_alert(
        self, field_id: str, tenant_id: str, weather_data: WeatherAlertEvent
    ) -> EventResponse:
        """
        معالجة تنبيه الطقس
        Process weather alert event

        Args:
            field_id: معرف الحقل
            tenant_id: معرف المستأجر
            weather_data: بيانات تنبيه الطقس

        Returns:
            استجابة الحدث
        """
        # تحديد الخطورة بناءً على نوع التنبيه
        severity_map = {
            "frost": EventSeverity.CRITICAL,
            "heatwave": EventSeverity.HIGH,
            "storm": EventSeverity.HIGH,
            "drought": EventSeverity.HIGH,
            "heavy_rain": EventSeverity.MEDIUM,
            "wind": EventSeverity.MEDIUM,
        }
        severity = severity_map.get(weather_data.alert_type, EventSeverity.MEDIUM)

        event = EventCreate(
            tenant_id=tenant_id,
            field_id=field_id,
            event_type=EventType.WEATHER_ALERT,
            severity=severity,
            title=f"Weather Alert: {weather_data.alert_type.replace('_', ' ').title()}",
            title_ar=weather_data.alert_type_ar or f"تنبيه طقس: {weather_data.alert_type}",
            description=weather_data.weather_condition,
            description_ar=weather_data.weather_condition,
            source_service="weather-service",
            metadata={
                "alert_type": weather_data.alert_type,
                "weather_condition": weather_data.weather_condition,
                "temperature_celsius": weather_data.temperature_celsius,
                "humidity_percent": weather_data.humidity_percent,
                "wind_speed_kmh": weather_data.wind_speed_kmh,
                "precipitation_mm": weather_data.precipitation_mm,
                "forecast_hours": weather_data.forecast_hours,
                "recommendations": weather_data.recommendations,
                "recommendations_ar": weather_data.recommendations_ar,
            },
        )

        return await self.process_event(event, available_rules=[])

    async def process_soil_moisture(
        self, field_id: str, tenant_id: str, moisture_data: SoilMoistureEvent
    ) -> EventResponse:
        """
        معالجة حدث رطوبة التربة
        Process soil moisture event

        Args:
            field_id: معرف الحقل
            tenant_id: معرف المستأجر
            moisture_data: بيانات رطوبة التربة

        Returns:
            استجابة الحدث
        """
        current = moisture_data.current_moisture_percent

        # تحديد نوع الحدث والخطورة
        if current < moisture_data.optimal_min:
            event_type = EventType.SOIL_MOISTURE_LOW
            severity = (
                EventSeverity.HIGH
                if current < moisture_data.optimal_min * 0.7
                else EventSeverity.MEDIUM
            )
            title = "Low Soil Moisture Detected"
            title_ar = "انخفاض في رطوبة التربة"
        elif current > moisture_data.optimal_max:
            event_type = EventType.SOIL_MOISTURE_HIGH
            severity = EventSeverity.MEDIUM
            title = "High Soil Moisture Detected"
            title_ar = "ارتفاع في رطوبة التربة"
        else:
            # رطوبة طبيعية - لا داعي للحدث
            return None

        event = EventCreate(
            tenant_id=tenant_id,
            field_id=field_id,
            event_type=event_type,
            severity=severity,
            title=title,
            title_ar=title_ar,
            description=(
                f"Soil moisture at {current:.1f}% "
                f"(optimal range: {moisture_data.optimal_min:.1f}% - {moisture_data.optimal_max:.1f}%)"
            ),
            description_ar=(
                f"رطوبة التربة عند {current:.1f}٪ "
                f"(النطاق الأمثل: {moisture_data.optimal_min:.1f}٪ - {moisture_data.optimal_max:.1f}٪)"
            ),
            source_service="iot-gateway",
            metadata={
                "current_moisture_percent": current,
                "optimal_min": moisture_data.optimal_min,
                "optimal_max": moisture_data.optimal_max,
                "sensor_id": moisture_data.sensor_id,
                "depth_cm": moisture_data.depth_cm,
                "measurement_time": moisture_data.measurement_time.isoformat(),
                "zone_id": moisture_data.zone_id,
                "irrigation_recommendation": moisture_data.irrigation_recommendation,
                "irrigation_recommendation_ar": moisture_data.irrigation_recommendation_ar,
            },
        )

        return await self.process_event(event, available_rules=[])

    async def process_astronomical_event(
        self, field_id: str, tenant_id: str, astro_data: AstronomicalEvent
    ) -> EventResponse:
        """
        معالجة حدث فلكي زراعي
        Process astronomical agricultural event

        Args:
            field_id: معرف الحقل
            tenant_id: معرف المستأجر
            astro_data: بيانات الحدث الفلكي

        Returns:
            استجابة الحدث
        """
        event = EventCreate(
            tenant_id=tenant_id,
            field_id=field_id,
            event_type=EventType.ASTRONOMICAL_EVENT,
            severity=EventSeverity.LOW,  # الأحداث الفلكية عادة معلوماتية
            title=astro_data.event_name,
            title_ar=astro_data.event_name_ar,
            description=(
                f"{astro_data.event_name} - {astro_data.event_category.title()} "
                f"({astro_data.moon_phase or 'N/A'})"
            ),
            description_ar=(
                f"{astro_data.event_name_ar} - {astro_data.event_category} "
                f"({astro_data.moon_phase_ar or 'غير محدد'})"
            ),
            source_service="astronomical-calendar",
            metadata={
                "event_date": astro_data.event_date.isoformat(),
                "event_category": astro_data.event_category,
                "moon_phase": astro_data.moon_phase,
                "moon_phase_ar": astro_data.moon_phase_ar,
                "recommended_crops": astro_data.recommended_crops,
                "recommended_crops_ar": astro_data.recommended_crops_ar,
                "traditional_practice": astro_data.traditional_practice,
                "traditional_practice_ar": astro_data.traditional_practice_ar,
                "scientific_rationale": astro_data.scientific_rationale,
                "scientific_rationale_ar": astro_data.scientific_rationale_ar,
            },
        )

        return await self.process_event(event, available_rules=[])

    async def fetch_astronomical_calendar(self, date: str, governorate: str | None = None) -> dict:
        """
        جلب التقويم الفلكي من خدمة التقويم الفلكي
        Fetch astronomical calendar from astronomical-calendar service

        Args:
            date: التاريخ بصيغة YYYY-MM-DD
            governorate: المحافظة (اختياري)

        Returns:
            بيانات التقويم الفلكي
        """
        try:
            # في الإنتاج، استخدام متغير البيئة للـ URL
            base_url = "http://astronomical-calendar:8111"
            url = f"{base_url}/api/v1/calendar/date/{date}"

            if governorate:
                url += f"?governorate={governorate}"

            response = await self.http_client.get(url)
            response.raise_for_status()

            logger.info(f"✓ تم جلب التقويم الفلكي ليوم {date}")
            return response.json()

        except Exception as e:
            logger.error(f"خطأ في جلب التقويم الفلكي: {str(e)}")
            return {}

    async def close(self):
        """إغلاق الاتصالات"""
        await self.http_client.aclose()
