"""
SAHOOL Platform - Agricultural Domain Metrics
مقاييس المجال الزراعي

Provides comprehensive Prometheus metrics for agricultural operations:
- Field monitoring metrics
- NDVI and vegetation analysis
- Weather and irrigation
- Crop health and yield
- IoT sensor data
- AI/ML model performance
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

try:
    from prometheus_client import (
        REGISTRY,
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    CollectorRegistry = None


class CropType(StrEnum):
    """Crop types for metrics labeling | أنواع المحاصيل"""

    WHEAT = "wheat"
    BARLEY = "barley"
    DATE_PALM = "date_palm"
    TOMATO = "tomato"
    CUCUMBER = "cucumber"
    CORN = "corn"
    RICE = "rice"
    COTTON = "cotton"
    OTHER = "other"


class AlertSeverity(StrEnum):
    """Alert severity levels | مستويات خطورة التنبيه"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class MetricLabels:
    """Standard metric labels for SAHOOL platform"""

    tenant_id: str = ""
    farm_id: str = ""
    field_id: str = ""
    crop_type: str = ""
    region: str = ""


class AgriculturalMetrics:
    """
    Comprehensive agricultural metrics collector.
    جامع المقاييس الزراعية الشامل.

    Provides domain-specific metrics for:
    - Field operations
    - Crop monitoring
    - Weather tracking
    - Irrigation management
    - Yield prediction
    - IoT sensors
    """

    def __init__(self, registry: CollectorRegistry | None = None):
        self.registry = registry or REGISTRY if PROMETHEUS_AVAILABLE else None
        self._metrics: dict[str, Any] = {}

        if PROMETHEUS_AVAILABLE:
            self._setup_metrics()

    def _setup_metrics(self) -> None:
        """Initialize all agricultural metrics."""
        self._setup_field_metrics()
        self._setup_ndvi_metrics()
        self._setup_weather_metrics()
        self._setup_irrigation_metrics()
        self._setup_crop_health_metrics()
        self._setup_yield_metrics()
        self._setup_iot_metrics()
        self._setup_ai_metrics()
        self._setup_business_metrics()

    def _setup_field_metrics(self) -> None:
        """Field management metrics | مقاييس إدارة الحقول"""
        self._metrics["fields_total"] = Gauge(
            "sahool_fields_total",
            "Total number of registered fields | إجمالي عدد الحقول المسجلة",
            ["tenant_id", "region"],
            registry=self.registry,
        )

        self._metrics["field_area_hectares"] = Gauge(
            "sahool_field_area_hectares_total",
            "Total field area in hectares | إجمالي مساحة الحقول بالهكتار",
            ["tenant_id", "region", "crop_type"],
            registry=self.registry,
        )

        self._metrics["field_operations_total"] = Counter(
            "sahool_field_operations_total",
            "Total field operations performed | إجمالي العمليات الحقلية المنفذة",
            ["tenant_id", "operation_type", "crop_type"],
            registry=self.registry,
        )

        self._metrics["field_operation_duration"] = Histogram(
            "sahool_field_operation_duration_seconds",
            "Duration of field operations | مدة العمليات الحقلية",
            ["operation_type"],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120],
            registry=self.registry,
        )

    def _setup_ndvi_metrics(self) -> None:
        """NDVI and vegetation index metrics | مقاييس NDVI ومؤشرات الغطاء النباتي"""
        self._metrics["ndvi_calculations_total"] = Counter(
            "sahool_ndvi_calculations_total",
            "Total NDVI calculations performed | إجمالي حسابات NDVI المنفذة",
            ["satellite_source", "tenant_id"],
            registry=self.registry,
        )

        self._metrics["ndvi_value"] = Histogram(
            "sahool_ndvi_value",
            "Distribution of NDVI values | توزيع قيم NDVI",
            ["crop_type", "region"],
            buckets=[-0.5, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry,
        )

        self._metrics["ndvi_anomalies_detected"] = Counter(
            "sahool_ndvi_anomalies_total",
            "NDVI anomalies detected | شذوذات NDVI المكتشفة",
            ["anomaly_type", "severity", "crop_type"],
            registry=self.registry,
        )

        # NOTE: field_id removed from labels to prevent high-cardinality explosion.
        # 10,000 fields × multiple metrics = 100,000+ time series → Prometheus OOM.
        # Use region/crop_type for aggregation; field-level data goes to the database.
        self._metrics["ndvi_last_update"] = Gauge(
            "sahool_ndvi_last_update_timestamp_seconds",
            "Timestamp of last NDVI update | وقت آخر تحديث NDVI",
            ["region", "crop_type"],
            registry=self.registry,
        )

        self._metrics["lai_value"] = Histogram(
            "sahool_lai_value",
            "Leaf Area Index distribution | توزيع مؤشر مساحة الورقة",
            ["crop_type"],
            buckets=[0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8],
            registry=self.registry,
        )

        self._metrics["evi_value"] = Histogram(
            "sahool_evi_value",
            "Enhanced Vegetation Index distribution | توزيع مؤشر الغطاء النباتي المحسن",
            ["crop_type"],
            buckets=[-0.5, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
            registry=self.registry,
        )

    def _setup_weather_metrics(self) -> None:
        """Weather and climate metrics | مقاييس الطقس والمناخ"""
        self._metrics["weather_requests_total"] = Counter(
            "sahool_weather_requests_total",
            "Total weather data requests | إجمالي طلبات بيانات الطقس",
            ["provider", "request_type"],
            registry=self.registry,
        )

        self._metrics["weather_temperature"] = Gauge(
            "sahool_weather_temperature_celsius",
            "Current temperature in Celsius | درجة الحرارة الحالية بالسيلزيوس",
            ["region", "measurement_type"],
            registry=self.registry,
        )

        self._metrics["weather_humidity"] = Gauge(
            "sahool_weather_humidity_percent",
            "Current humidity percentage | نسبة الرطوبة الحالية",
            ["region"],
            registry=self.registry,
        )

        self._metrics["weather_precipitation"] = Gauge(
            "sahool_weather_precipitation_mm",
            "Precipitation in millimeters | هطول الأمطار بالمليمتر",
            ["region", "period"],
            registry=self.registry,
        )

        self._metrics["weather_alerts_total"] = Counter(
            "sahool_weather_alerts_total",
            "Weather alerts issued | تنبيهات الطقس الصادرة",
            ["alert_type", "severity", "region"],
            registry=self.registry,
        )

        self._metrics["et0_value"] = Gauge(
            "sahool_et0_mm_per_day",
            "Reference evapotranspiration (ET0) | التبخر النتح المرجعي",
            ["region", "calculation_method"],
            registry=self.registry,
        )

        self._metrics["weather_last_update"] = Gauge(
            "sahool_weather_last_update_timestamp_seconds",
            "Timestamp of last weather update | وقت آخر تحديث للطقس",
            ["region"],
            registry=self.registry,
        )

    def _setup_irrigation_metrics(self) -> None:
        """Irrigation management metrics | مقاييس إدارة الري"""
        self._metrics["irrigation_events_total"] = Counter(
            "sahool_irrigation_events_total",
            "Total irrigation events | إجمالي أحداث الري",
            ["tenant_id", "irrigation_type", "crop_type"],
            registry=self.registry,
        )

        self._metrics["irrigation_water_volume_liters"] = Counter(
            "sahool_irrigation_water_volume_liters_total",
            "Total water volume used in liters | إجمالي حجم المياه المستخدمة باللتر",
            ["irrigation_type"],
            registry=self.registry,
        )

        self._metrics["irrigation_recommendations_total"] = Counter(
            "sahool_irrigation_recommendations_total",
            "Irrigation recommendations issued | توصيات الري الصادرة",
            ["recommendation_type", "urgency"],
            registry=self.registry,
        )

        self._metrics["soil_moisture_percent"] = Gauge(
            "sahool_soil_moisture_percent",
            "Current soil moisture percentage | نسبة رطوبة التربة الحالية",
            ["region", "depth_cm"],
            registry=self.registry,
        )

        self._metrics["water_stress_index"] = Gauge(
            "sahool_water_stress_index",
            "Water stress index (0-1) | مؤشر الإجهاد المائي",
            ["region", "crop_type"],
            registry=self.registry,
        )

    def _setup_crop_health_metrics(self) -> None:
        """Crop health monitoring metrics | مقاييس مراقبة صحة المحاصيل"""
        self._metrics["crop_health_score"] = Gauge(
            "sahool_crop_health_score",
            "Crop health score (0-100) | درجة صحة المحصول",
            ["region", "crop_type"],
            registry=self.registry,
        )

        self._metrics["disease_detections_total"] = Counter(
            "sahool_disease_detections_total",
            "Total crop disease detections | إجمالي اكتشافات أمراض المحاصيل",
            ["disease_type", "crop_type", "severity"],
            registry=self.registry,
        )

        self._metrics["pest_detections_total"] = Counter(
            "sahool_pest_detections_total",
            "Total pest detections | إجمالي اكتشافات الآفات",
            ["pest_type", "crop_type", "severity"],
            registry=self.registry,
        )

        self._metrics["weed_detections_total"] = Counter(
            "sahool_weed_detections_total",
            "Total weed detections | إجمالي اكتشافات الأعشاب الضارة",
            ["weed_type", "density_level"],
            registry=self.registry,
        )

        self._metrics["growth_stage_fields"] = Gauge(
            "sahool_growth_stage_fields_total",
            "Fields by growth stage | الحقول حسب مرحلة النمو",
            ["crop_type", "growth_stage"],
            registry=self.registry,
        )

        self._metrics["crop_stress_alerts"] = Counter(
            "sahool_crop_stress_alerts_total",
            "Crop stress alerts issued | تنبيهات إجهاد المحاصيل الصادرة",
            ["stress_type", "severity", "crop_type"],
            registry=self.registry,
        )

    def _setup_yield_metrics(self) -> None:
        """Yield estimation and prediction metrics | مقاييس تقدير والتنبؤ بالإنتاجية"""
        self._metrics["yield_predictions_total"] = Counter(
            "sahool_yield_predictions_total",
            "Total yield predictions made | إجمالي تنبؤات الإنتاجية",
            ["crop_type", "model_version"],
            registry=self.registry,
        )

        self._metrics["yield_predicted_tons_per_hectare"] = Histogram(
            "sahool_yield_predicted_tons_per_hectare",
            "Predicted yield in tons per hectare | الإنتاجية المتوقعة بالطن/هكتار",
            ["crop_type"],
            buckets=[0.5, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15],
            registry=self.registry,
        )

        self._metrics["yield_actual_tons_per_hectare"] = Histogram(
            "sahool_yield_actual_tons_per_hectare",
            "Actual harvested yield in tons per hectare | الإنتاجية الفعلية المحصودة",
            ["crop_type"],
            buckets=[0.5, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15],
            registry=self.registry,
        )

        self._metrics["yield_prediction_accuracy"] = Gauge(
            "sahool_yield_prediction_accuracy_percent",
            "Yield prediction accuracy percentage | دقة تنبؤ الإنتاجية",
            ["crop_type", "model_version"],
            registry=self.registry,
        )

        self._metrics["harvest_ready_fields"] = Gauge(
            "sahool_harvest_ready_fields_total",
            "Fields ready for harvest | الحقول الجاهزة للحصاد",
            ["crop_type", "region"],
            registry=self.registry,
        )

    def _setup_iot_metrics(self) -> None:
        """IoT sensor and device metrics | مقاييس مستشعرات وأجهزة إنترنت الأشياء"""
        self._metrics["iot_devices_total"] = Gauge(
            "sahool_iot_devices_total",
            "Total registered IoT devices | إجمالي أجهزة إنترنت الأشياء المسجلة",
            ["device_type", "status"],
            registry=self.registry,
        )

        self._metrics["iot_readings_total"] = Counter(
            "sahool_iot_readings_total",
            "Total sensor readings received | إجمالي قراءات المستشعرات المستلمة",
            ["sensor_type", "device_id"],
            registry=self.registry,
        )

        self._metrics["iot_reading_latency"] = Histogram(
            "sahool_iot_reading_latency_seconds",
            "IoT reading processing latency | زمن معالجة قراءة إنترنت الأشياء",
            ["sensor_type"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1],
            registry=self.registry,
        )

        self._metrics["iot_device_last_seen"] = Gauge(
            "sahool_iot_device_last_seen_timestamp_seconds",
            "Last seen timestamp for IoT device | آخر ظهور لجهاز إنترنت الأشياء",
            ["device_id"],
            registry=self.registry,
        )

        self._metrics["iot_offline_devices"] = Gauge(
            "sahool_iot_offline_devices_total",
            "Number of offline IoT devices | عدد أجهزة إنترنت الأشياء غير المتصلة",
            ["device_type"],
            registry=self.registry,
        )

        self._metrics["iot_battery_level"] = Gauge(
            "sahool_iot_battery_level_percent",
            "IoT device battery level | مستوى بطارية جهاز إنترنت الأشياء",
            ["device_id", "device_type"],
            registry=self.registry,
        )

    def _setup_ai_metrics(self) -> None:
        """AI/ML model metrics | مقاييس نماذج الذكاء الاصطناعي"""
        self._metrics["ai_inference_total"] = Counter(
            "sahool_ai_inference_total",
            "Total AI model inferences | إجمالي استدلالات نموذج الذكاء الاصطناعي",
            ["model_name", "model_version", "status"],
            registry=self.registry,
        )

        self._metrics["ai_inference_duration"] = Histogram(
            "sahool_ai_inference_duration_seconds",
            "AI model inference duration | مدة استدلال نموذج الذكاء الاصطناعي",
            ["model_name"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
            registry=self.registry,
        )

        self._metrics["ai_model_accuracy"] = Gauge(
            "sahool_ai_model_accuracy",
            "AI model accuracy score | درجة دقة نموذج الذكاء الاصطناعي",
            ["model_name", "model_version"],
            registry=self.registry,
        )

        self._metrics["ai_advisory_total"] = Counter(
            "sahool_ai_advisory_total",
            "Total AI advisories generated | إجمالي الاستشارات المولدة بالذكاء الاصطناعي",
            ["advisory_type", "crop_type"],
            registry=self.registry,
        )

        self._metrics["ai_advisory_feedback"] = Counter(
            "sahool_ai_advisory_feedback_total",
            "Advisory feedback received | الملاحظات المستلمة على الاستشارات",
            ["advisory_type", "feedback_type"],
            registry=self.registry,
        )

        self._metrics["vision_detections_total"] = Counter(
            "sahool_vision_detections_total",
            "Total computer vision detections | إجمالي اكتشافات الرؤية الحاسوبية",
            ["detection_type", "model_name", "confidence_level"],
            registry=self.registry,
        )

    def _setup_business_metrics(self) -> None:
        """Business and operational metrics | المقاييس التجارية والتشغيلية"""
        self._metrics["active_users"] = Gauge(
            "sahool_active_users_gauge",
            "Number of active users | عدد المستخدمين النشطين",
            ["tenant_id", "user_type"],
            registry=self.registry,
        )

        self._metrics["api_requests_total"] = Counter(
            "sahool_api_requests_total",
            "Total API requests | إجمالي طلبات API",
            ["endpoint", "method", "status_code"],
            registry=self.registry,
        )

        self._metrics["tasks_created_total"] = Counter(
            "sahool_tasks_created_total",
            "Total tasks created | إجمالي المهام المنشأة",
            ["task_type", "priority"],
            registry=self.registry,
        )

        self._metrics["tasks_completed_total"] = Counter(
            "sahool_tasks_completed_total",
            "Total tasks completed | إجمالي المهام المكتملة",
            ["task_type", "completion_status"],
            registry=self.registry,
        )

        self._metrics["notifications_sent_total"] = Counter(
            "sahool_notifications_sent_total",
            "Total notifications sent | إجمالي الإشعارات المرسلة",
            ["notification_type", "channel", "status"],
            registry=self.registry,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Recording Methods | طرق التسجيل
    # ═══════════════════════════════════════════════════════════════════════════

    def record_ndvi_calculation(
        self,
        ndvi_value: float,
        crop_type: str = "unknown",
        satellite_source: str = "sentinel-2",
        tenant_id: str = "default",
        region: str = "unknown",
        field_id: str | None = None,
    ) -> None:
        """Record an NDVI calculation.

        The ``field_id`` parameter is deprecated and ignored — metrics
        are now aggregated by region/crop_type to prevent cardinality explosion.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["ndvi_calculations_total"].labels(
            satellite_source=satellite_source,
            tenant_id=tenant_id,
        ).inc()

        self._metrics["ndvi_value"].labels(
            crop_type=crop_type,
            region=region,
        ).observe(ndvi_value)

        self._metrics["ndvi_last_update"].labels(
            region=region,
            crop_type=crop_type,
        ).set(time.time())

    def record_weather_update(
        self,
        region: str,
        temperature: float | None = None,
        humidity: float | None = None,
        precipitation: float | None = None,
        et0: float | None = None,
    ) -> None:
        """Record weather data update."""
        if not PROMETHEUS_AVAILABLE:
            return

        if temperature is not None:
            self._metrics["weather_temperature"].labels(
                region=region,
                measurement_type="current",
            ).set(temperature)

        if humidity is not None:
            self._metrics["weather_humidity"].labels(
                region=region,
            ).set(humidity)

        if precipitation is not None:
            self._metrics["weather_precipitation"].labels(
                region=region,
                period="daily",
            ).set(precipitation)

        if et0 is not None:
            self._metrics["et0_value"].labels(
                region=region,
                calculation_method="penman_monteith",
            ).set(et0)

        self._metrics["weather_last_update"].labels(
            region=region,
        ).set(time.time())

    def record_disease_detection(
        self,
        disease_type: str,
        crop_type: str,
        severity: str = "medium",
        confidence: float = 0.0,
    ) -> None:
        """Record a disease detection."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["disease_detections_total"].labels(
            disease_type=disease_type,
            crop_type=crop_type,
            severity=severity,
        ).inc()

    def record_pest_detection(
        self,
        pest_type: str,
        crop_type: str,
        severity: str = "medium",
    ) -> None:
        """Record a pest detection."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["pest_detections_total"].labels(
            pest_type=pest_type,
            crop_type=crop_type,
            severity=severity,
        ).inc()

    def record_irrigation_event(
        self,
        water_volume_liters: float,
        irrigation_type: str = "drip",
        crop_type: str = "unknown",
        tenant_id: str = "default",
        field_id: str | None = None,
    ) -> None:
        """Record an irrigation event.

        The ``field_id`` parameter is deprecated and ignored.
        ``tenant_id`` is still used as a label on ``irrigation_events_total``
        for event counting; water volume is aggregated by ``irrigation_type`` only.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["irrigation_events_total"].labels(
            tenant_id=tenant_id,
            irrigation_type=irrigation_type,
            crop_type=crop_type,
        ).inc()

        self._metrics["irrigation_water_volume_liters"].labels(
            irrigation_type=irrigation_type,
        ).inc(water_volume_liters)

    def record_yield_prediction(
        self,
        crop_type: str,
        predicted_yield: float,
        model_version: str = "v1",
    ) -> None:
        """Record a yield prediction."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["yield_predictions_total"].labels(
            crop_type=crop_type,
            model_version=model_version,
        ).inc()

        self._metrics["yield_predicted_tons_per_hectare"].labels(
            crop_type=crop_type,
        ).observe(predicted_yield)

    def record_ai_inference(
        self,
        model_name: str,
        duration_seconds: float,
        success: bool = True,
        model_version: str = "v1",
    ) -> None:
        """Record an AI model inference."""
        if not PROMETHEUS_AVAILABLE:
            return

        status = "success" if success else "failure"

        self._metrics["ai_inference_total"].labels(
            model_name=model_name,
            model_version=model_version,
            status=status,
        ).inc()

        self._metrics["ai_inference_duration"].labels(
            model_name=model_name,
        ).observe(duration_seconds)

    def record_iot_reading(
        self,
        device_id: str,
        sensor_type: str,
        latency_seconds: float,
    ) -> None:
        """Record an IoT sensor reading."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["iot_readings_total"].labels(
            sensor_type=sensor_type,
            device_id=device_id,
        ).inc()

        self._metrics["iot_reading_latency"].labels(
            sensor_type=sensor_type,
        ).observe(latency_seconds)

        self._metrics["iot_device_last_seen"].labels(
            device_id=device_id,
        ).set(time.time())

    def set_crop_health_score(
        self,
        score: float,
        crop_type: str = "unknown",
        region: str = "unknown",
        field_id: str | None = None,
    ) -> None:
        """Set the crop health score aggregated by region and crop type.

        The ``field_id`` parameter is deprecated and ignored — metric
        labels are now ``region`` and ``crop_type``.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["crop_health_score"].labels(
            region=region,
            crop_type=crop_type,
        ).set(score)

    def set_soil_moisture(
        self,
        moisture_percent: float,
        depth_cm: str = "30",
        region: str = "unknown",
        field_id: str | None = None,
    ) -> None:
        """Set aggregated soil moisture for a region/depth combination.

        The ``field_id`` parameter is deprecated and ignored — metric
        labels are now ``region`` and ``depth_cm``.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["soil_moisture_percent"].labels(
            region=region,
            depth_cm=depth_cm,
        ).set(moisture_percent)

    @contextmanager
    def measure_operation(self, operation_type: str):
        """
        Context manager to measure operation duration.
        مدير سياق لقياس مدة العملية.
        """
        start = time.time()
        try:
            yield
        finally:
            if PROMETHEUS_AVAILABLE:
                duration = time.time() - start
                self._metrics["field_operation_duration"].labels(
                    operation_type=operation_type,
                ).observe(duration)


# Global instance
_agricultural_metrics: AgriculturalMetrics | None = None


def get_agricultural_metrics() -> AgriculturalMetrics:
    """Get the global agricultural metrics instance."""
    global _agricultural_metrics
    if _agricultural_metrics is None:
        _agricultural_metrics = AgriculturalMetrics()
    return _agricultural_metrics
