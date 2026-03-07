"""
Edge-Cloud Cooperative Architecture Models
==========================================
نماذج بنية التعاون بين الحافة والسحابة

Data models for the smart agriculture Edge-Cloud cooperative system,
supporting multi-protocol IoT devices, edge computing decisions,
and cloud AI inference.

Key Concepts:
- Perception Layer: 200+ device types, multi-protocol support
- Edge Layer: Local inference, 300ms latency, offline autonomy
- Cloud Layer: YOLOv5 pest detection, moisture prediction (3% error)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

# =============================================================================
# Protocol & Device Enums - تعدادات البروتوكول والأجهزة
# =============================================================================


class DeviceProtocol(StrEnum):
    """
    Communication protocols for IoT devices.
    بروتوكولات الاتصال لأجهزة إنترنت الأشياء
    """

    MQTT = "mqtt"
    """MQTT protocol for lightweight messaging | بروتوكول MQTT للرسائل الخفيفة"""

    HTTP = "http"
    """HTTP/HTTPS REST API | واجهة برمجة HTTP/HTTPS"""

    MODBUS = "modbus"
    """Modbus RTU/TCP for industrial devices | Modbus للأجهزة الصناعية"""

    OPC_UA = "opc_ua"
    """OPC Unified Architecture | بنية OPC الموحدة"""

    COAP = "coap"
    """Constrained Application Protocol | بروتوكول التطبيقات المقيدة"""

    LORAWAN = "lorawan"
    """LoRaWAN for long-range low-power | LoRaWAN للمدى الطويل والطاقة المنخفضة"""

    ZIGBEE = "zigbee"
    """ZigBee mesh networking | شبكة ZigBee"""

    BLUETOOTH_LE = "bluetooth_le"
    """Bluetooth Low Energy | بلوتوث منخفض الطاقة"""


class SensorType(StrEnum):
    """
    Types of agricultural sensors.
    أنواع أجهزة الاستشعار الزراعية
    """

    SOIL_MOISTURE = "soil_moisture"
    """Soil moisture sensor | مستشعر رطوبة التربة"""

    SOIL_TEMPERATURE = "soil_temperature"
    """Soil temperature sensor | مستشعر حرارة التربة"""

    SOIL_PH = "soil_ph"
    """Soil pH sensor | مستشعر حموضة التربة"""

    SOIL_EC = "soil_ec"
    """Soil electrical conductivity | مستشعر الموصلية الكهربائية"""

    AIR_TEMPERATURE = "air_temperature"
    """Air temperature sensor | مستشعر حرارة الهواء"""

    AIR_HUMIDITY = "air_humidity"
    """Air humidity sensor | مستشعر رطوبة الهواء"""

    LIGHT_INTENSITY = "light_intensity"
    """Light intensity sensor | مستشعر شدة الإضاءة"""

    WIND_SPEED = "wind_speed"
    """Wind speed sensor | مستشعر سرعة الرياح"""

    WIND_DIRECTION = "wind_direction"
    """Wind direction sensor | مستشعر اتجاه الرياح"""

    RAINFALL = "rainfall"
    """Rainfall sensor | مستشعر هطول الأمطار"""

    WATER_FLOW = "water_flow"
    """Water flow sensor | مستشعر تدفق المياه"""

    WATER_PRESSURE = "water_pressure"
    """Water pressure sensor | مستشعر ضغط المياه"""

    LEAF_WETNESS = "leaf_wetness"
    """Leaf wetness sensor | مستشعر رطوبة الأوراق"""

    CO2_LEVEL = "co2_level"
    """CO2 concentration sensor | مستشعر تركيز ثاني أكسيد الكربون"""

    NDVI = "ndvi"
    """NDVI vegetation index | مؤشر الغطاء النباتي NDVI"""

    CAMERA = "camera"
    """Camera/imaging sensor | كاميرا/مستشعر تصوير"""


class DeviceManufacturer(StrEnum):
    """
    Supported device manufacturers.
    الشركات المصنعة للأجهزة المدعومة
    """

    HIKVISION = "hikvision"
    """Hikvision cameras and sensors | كاميرات ومستشعرات Hikvision"""

    DJI = "dji"
    """DJI drones and cameras | طائرات وكاميرات DJI"""

    SENTEK = "sentek"
    """Sentek soil sensors | مستشعرات التربة Sentek"""

    DAVIS = "davis"
    """Davis weather stations | محطات الطقس Davis"""

    CAMPBELL = "campbell"
    """Campbell Scientific sensors | مستشعرات Campbell Scientific"""

    DECAGON = "decagon"
    """Decagon/METER soil sensors | مستشعرات Decagon/METER"""

    ONSET = "onset"
    """Onset HOBO sensors | مستشعرات Onset HOBO"""

    NETAFIM = "netafim"
    """Netafim irrigation sensors | مستشعرات ري Netafim"""

    GENERIC = "generic"
    """Generic/unknown manufacturer | مصنع عام/غير معروف"""


class DataQuality(StrEnum):
    """
    Data quality levels for sensor readings.
    مستويات جودة البيانات لقراءات المستشعرات
    """

    EXCELLENT = "excellent"
    """Excellent quality (>95% confidence) | جودة ممتازة (>95% ثقة)"""

    GOOD = "good"
    """Good quality (80-95% confidence) | جودة جيدة (80-95% ثقة)"""

    FAIR = "fair"
    """Fair quality (60-80% confidence) | جودة مقبولة (60-80% ثقة)"""

    POOR = "poor"
    """Poor quality (<60% confidence) | جودة ضعيفة (<60% ثقة)"""

    INVALID = "invalid"
    """Invalid/corrupted data | بيانات غير صالحة/تالفة"""


class DecisionType(StrEnum):
    """
    Types of edge computing decisions.
    أنواع قرارات الحوسبة الطرفية
    """

    IRRIGATION_TRIGGER = "irrigation_trigger"
    """Trigger irrigation based on thresholds | تشغيل الري بناءً على العتبات"""

    IRRIGATION_STOP = "irrigation_stop"
    """Stop irrigation | إيقاف الري"""

    ALERT_CRITICAL = "alert_critical"
    """Critical alert requiring immediate action | تنبيه حرج يتطلب إجراء فوري"""

    ALERT_WARNING = "alert_warning"
    """Warning alert | تنبيه تحذيري"""

    DATA_AGGREGATION = "data_aggregation"
    """Aggregate data for cloud sync | تجميع البيانات للمزامنة السحابية"""

    LOCAL_INFERENCE = "local_inference"
    """Local model inference result | نتيجة الاستدلال المحلي"""

    DEVICE_CONTROL = "device_control"
    """Device control command | أمر التحكم في الجهاز"""

    SCHEDULE_ADJUSTMENT = "schedule_adjustment"
    """Adjust scheduled operations | تعديل العمليات المجدولة"""


class PestCategory(StrEnum):
    """
    Categories of detected pests.
    فئات الآفات المكتشفة
    """

    INSECT = "insect"
    """Insect pest | آفة حشرية"""

    FUNGUS = "fungus"
    """Fungal disease | مرض فطري"""

    BACTERIA = "bacteria"
    """Bacterial disease | مرض بكتيري"""

    VIRUS = "virus"
    """Viral disease | مرض فيروسي"""

    WEED = "weed"
    """Weed infestation | انتشار الأعشاب الضارة"""

    NEMATODE = "nematode"
    """Nematode infestation | انتشار النيماتودا"""


class SystemStatus(StrEnum):
    """
    Status of system components.
    حالة مكونات النظام
    """

    ONLINE = "online"
    """Component is online and functioning | المكون متصل ويعمل"""

    OFFLINE = "offline"
    """Component is offline | المكون غير متصل"""

    DEGRADED = "degraded"
    """Component is functioning with reduced capacity | المكون يعمل بقدرة منخفضة"""

    MAINTENANCE = "maintenance"
    """Component is under maintenance | المكون قيد الصيانة"""

    ERROR = "error"
    """Component has encountered an error | المكون واجه خطأ"""


# =============================================================================
# Configuration Models - نماذج التكوين
# =============================================================================


class SamplingConfig(BaseModel):
    """
    Configuration for sensor data sampling.
    تكوين أخذ عينات بيانات المستشعرات

    Controls the frequency and validation of sensor data collection.

    Example:
        config = SamplingConfig(
            interval_minutes=15,
            min_interval=10,
            max_interval=60,
            adaptive=True
        )
    """

    interval_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,
        description="Sampling interval in minutes | فترة أخذ العينات بالدقائق",
    )

    min_interval: int = Field(
        default=10,
        ge=1,
        description="Minimum sampling interval in minutes | الحد الأدنى لفترة أخذ العينات",
    )

    max_interval: int = Field(
        default=60,
        ge=1,
        le=1440,
        description="Maximum sampling interval in minutes | الحد الأقصى لفترة أخذ العينات",
    )

    adaptive: bool = Field(
        default=True,
        description="Enable adaptive sampling based on conditions | تمكين أخذ العينات التكيفي",
    )

    battery_saving_mode: bool = Field(
        default=False,
        description="Enable battery saving mode with reduced sampling | وضع توفير البطارية",
    )

    high_priority_sensors: list[SensorType] = Field(
        default_factory=list,
        description="Sensors to sample at higher frequency | المستشعرات ذات التردد العالي",
    )

    @field_validator("max_interval")
    @classmethod
    def validate_interval_range(cls, v: int, info) -> int:
        """Ensure max_interval >= min_interval"""
        if info.data.get("min_interval") and v < info.data["min_interval"]:
            raise ValueError("max_interval must be >= min_interval | الحد الأقصى يجب أن يكون >= الحد الأدنى")
        return v


class DeviceConfig(BaseModel):
    """
    Configuration for an IoT device.
    تكوين جهاز إنترنت الأشياء

    Example:
        config = DeviceConfig(
            device_id="sensor_001",
            protocol=DeviceProtocol.MQTT,
            manufacturer=DeviceManufacturer.SENTEK,
            sensor_types=[SensorType.SOIL_MOISTURE, SensorType.SOIL_TEMPERATURE]
        )
    """

    device_id: str = Field(..., min_length=1, description="Unique device identifier | معرف الجهاز الفريد")

    protocol: DeviceProtocol = Field(..., description="Communication protocol | بروتوكول الاتصال")

    manufacturer: DeviceManufacturer = Field(
        default=DeviceManufacturer.GENERIC, description="Device manufacturer | الشركة المصنعة"
    )

    model: str = Field(default="", description="Device model | طراز الجهاز")

    sensor_types: list[SensorType] = Field(
        default_factory=list, description="Types of sensors on device | أنواع المستشعرات على الجهاز"
    )

    # Connection settings
    host: str = Field(default="", description="Device host/IP address | عنوان المضيف/IP")

    port: int = Field(default=0, ge=0, le=65535, description="Connection port | منفذ الاتصال")

    username: str = Field(default="", description="Authentication username | اسم المستخدم للمصادقة")

    # Note: Password should be stored securely, not in config
    use_tls: bool = Field(default=True, description="Use TLS encryption | استخدام تشفير TLS")

    # Sampling
    sampling_config: SamplingConfig = Field(
        default_factory=SamplingConfig, description="Sampling configuration | تكوين أخذ العينات"
    )

    # Location
    latitude: float | None = Field(None, ge=-90, le=90, description="Device latitude | خط عرض الجهاز")

    longitude: float | None = Field(None, ge=-180, le=180, description="Device longitude | خط طول الجهاز")

    zone_id: str = Field(default="", description="Field zone identifier | معرف منطقة الحقل")

    # Metadata
    is_active: bool = Field(default=True, description="Whether device is active | هل الجهاز نشط")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")


# =============================================================================
# Data Models - نماذج البيانات
# =============================================================================


class SensorReading(BaseModel):
    """
    A single sensor reading from an IoT device.
    قراءة مستشعر واحدة من جهاز إنترنت الأشياء

    Example:
        reading = SensorReading(
            device_id="sensor_001",
            sensor_type=SensorType.SOIL_MOISTURE,
            value=42.5,
            unit="%",
            quality=DataQuality.GOOD
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique reading ID | معرف القراءة الفريد")

    device_id: str = Field(..., description="Source device identifier | معرف الجهاز المصدر")

    sensor_type: SensorType = Field(..., description="Type of sensor | نوع المستشعر")

    value: float = Field(..., description="Sensor value | قيمة المستشعر")

    unit: str = Field(default="", description="Unit of measurement | وحدة القياس")

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Reading timestamp | وقت القراءة"
    )

    quality: DataQuality = Field(default=DataQuality.GOOD, description="Data quality assessment | تقييم جودة البيانات")

    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in reading (0-1) | الثقة في القراءة")

    # Location context
    latitude: float | None = Field(None, ge=-90, le=90, description="Reading latitude | خط عرض القراءة")

    longitude: float | None = Field(None, ge=-180, le=180, description="Reading longitude | خط طول القراءة")

    zone_id: str = Field(default="", description="Field zone identifier | معرف منطقة الحقل")

    # Raw data
    raw_value: Any = Field(None, description="Raw value before processing | القيمة الخام قبل المعالجة")

    calibration_applied: bool = Field(
        default=False, description="Whether calibration was applied | هل تم تطبيق المعايرة"
    )

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "device_id": self.device_id,
            "sensor_type": self.sensor_type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "quality": self.quality.value,
            "confidence": self.confidence,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "zone_id": self.zone_id,
            "metadata": self.metadata,
        }


class EdgeDecision(BaseModel):
    """
    A decision made by the edge computing layer.
    قرار اتخذته طبقة الحوسبة الطرفية

    Edge decisions enable autonomous operation without cloud connectivity,
    with typical response latency of 300ms or less.

    Example:
        decision = EdgeDecision(
            decision_type=DecisionType.IRRIGATION_TRIGGER,
            action="start_zone_a_irrigation",
            latency_ms=250,
            offline_mode=True
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique decision ID | معرف القرار الفريد")

    gateway_id: str = Field(default="", description="Edge gateway identifier | معرف بوابة الحافة")

    decision_type: DecisionType = Field(..., description="Type of decision | نوع القرار")

    action: str = Field(..., description="Action to execute | الإجراء المراد تنفيذه")

    action_ar: str = Field(default="", description="Action description (Arabic) | وصف الإجراء (عربي)")

    # Performance metrics
    latency_ms: float = Field(
        default=0.0,
        ge=0,
        description="Decision latency in milliseconds | زمن الاستجابة بالمللي ثانية",
    )

    offline_mode: bool = Field(
        default=False, description="Decision made while offline | القرار اتخذ في وضع عدم الاتصال"
    )

    # Context
    trigger_readings: list[UUID] = Field(
        default_factory=list,
        description="Sensor readings that triggered decision | القراءات المحفزة للقرار",
    )

    rule_id: str = Field(default="", description="Rule that triggered decision | القاعدة المحفزة للقرار")

    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in decision (0-1) | الثقة في القرار")

    priority: int = Field(default=5, ge=1, le=10, description="Decision priority (1=highest) | أولوية القرار")

    # Execution
    executed: bool = Field(default=False, description="Whether decision was executed | هل تم تنفيذ القرار")

    executed_at: datetime | None = Field(None, description="Execution timestamp | وقت التنفيذ")

    execution_result: str = Field(default="", description="Execution result | نتيجة التنفيذ")

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp | وقت الإنشاء"
    )

    expires_at: datetime | None = Field(None, description="Decision expiration time | وقت انتهاء صلاحية القرار")

    # Cloud sync
    synced_to_cloud: bool = Field(default=False, description="Synced to cloud | تمت المزامنة مع السحابة")

    synced_at: datetime | None = Field(None, description="Sync timestamp | وقت المزامنة")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "gateway_id": self.gateway_id,
            "decision_type": self.decision_type.value,
            "action": self.action,
            "action_ar": self.action_ar,
            "latency_ms": self.latency_ms,
            "offline_mode": self.offline_mode,
            "trigger_readings": [str(r) for r in self.trigger_readings],
            "rule_id": self.rule_id,
            "confidence": self.confidence,
            "priority": self.priority,
            "executed": self.executed,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "execution_result": self.execution_result,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "synced_to_cloud": self.synced_to_cloud,
            "metadata": self.metadata,
        }


class CloudInference(BaseModel):
    """
    An inference result from cloud AI models.
    نتيجة استدلال من نماذج الذكاء الاصطناعي السحابية

    Cloud inference provides high-accuracy predictions using
    models like YOLOv5 for pest detection with typical
    3% error rate for moisture prediction.

    Example:
        inference = CloudInference(
            model_name="yolov5_pest_detection",
            prediction="aphid_infestation",
            confidence=0.92,
            processing_time_ms=450
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique inference ID | معرف الاستدلال الفريد")

    model_name: str = Field(..., description="Name of AI model used | اسم نموذج الذكاء الاصطناعي")

    model_version: str = Field(default="1.0.0", description="Model version | إصدار النموذج")

    prediction: str = Field(..., description="Prediction result | نتيجة التنبؤ")

    prediction_ar: str = Field(default="", description="Prediction (Arabic) | التنبؤ (عربي)")

    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence (0-1) | ثقة التنبؤ")

    # Performance
    processing_time_ms: float = Field(
        default=0.0,
        ge=0,
        description="Processing time in milliseconds | وقت المعالجة بالمللي ثانية",
    )

    # Structured results
    class_probabilities: dict[str, float] = Field(
        default_factory=dict, description="Probability distribution over classes | توزيع الاحتمالات"
    )

    bounding_boxes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Detected object bounding boxes | مربعات الكائنات المكتشفة",
    )

    numeric_predictions: dict[str, float] = Field(
        default_factory=dict,
        description="Numeric predictions (e.g., moisture, yield) | التنبؤات الرقمية",
    )

    # Error estimation
    error_margin: float = Field(default=0.03, ge=0.0, le=1.0, description="Estimated error margin | هامش الخطأ المقدر")

    # Input context
    input_type: str = Field(default="sensor_data", description="Type of input data | نوع بيانات الإدخال")

    input_summary: str = Field(default="", description="Summary of input data | ملخص بيانات الإدخال")

    # Timestamps
    requested_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Request timestamp | وقت الطلب"
    )

    completed_at: datetime | None = Field(None, description="Completion timestamp | وقت الإكمال")

    # Metadata
    farm_id: str = Field(default="", description="Farm identifier | معرف المزرعة")

    field_id: str = Field(default="", description="Field identifier | معرف الحقل")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "prediction": self.prediction,
            "prediction_ar": self.prediction_ar,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
            "class_probabilities": self.class_probabilities,
            "bounding_boxes": self.bounding_boxes,
            "numeric_predictions": self.numeric_predictions,
            "error_margin": self.error_margin,
            "input_type": self.input_type,
            "requested_at": self.requested_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "farm_id": self.farm_id,
            "field_id": self.field_id,
            "metadata": self.metadata,
        }


class Recommendation(BaseModel):
    """
    A recommendation from the cloud AI decision engine.
    توصية من محرك قرارات الذكاء الاصطناعي السحابي

    Example:
        recommendation = Recommendation(
            title="Increase Irrigation",
            title_ar="زيادة الري",
            description="Soil moisture is below optimal threshold",
            priority=2,
            action_required=True
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique recommendation ID | معرف التوصية الفريد")

    title: str = Field(..., description="Recommendation title | عنوان التوصية")

    title_ar: str = Field(default="", description="Title (Arabic) | العنوان (عربي)")

    description: str = Field(..., description="Detailed description | الوصف التفصيلي")

    description_ar: str = Field(default="", description="Description (Arabic) | الوصف (عربي)")

    category: str = Field(default="general", description="Recommendation category | فئة التوصية")

    priority: int = Field(default=5, ge=1, le=10, description="Priority level (1=highest) | مستوى الأولوية")

    action_required: bool = Field(default=False, description="Whether action is required | هل يلزم إجراء")

    suggested_action: str = Field(default="", description="Suggested action | الإجراء المقترح")

    suggested_action_ar: str = Field(default="", description="Suggested action (Arabic) | الإجراء المقترح (عربي)")

    confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence in recommendation | الثقة في التوصية"
    )

    based_on: list[str] = Field(
        default_factory=list,
        description="Data sources/models used | مصادر البيانات/النماذج المستخدمة",
    )

    valid_until: datetime | None = Field(None, description="Recommendation validity period | فترة صلاحية التوصية")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp | وقت الإنشاء"
    )

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")


class PestDetection(BaseModel):
    """
    Result of pest/disease detection from image analysis.
    نتيجة كشف الآفات/الأمراض من تحليل الصور

    Example:
        detection = PestDetection(
            pest_type="red_palm_weevil",
            pest_type_ar="سوسة النخيل الحمراء",
            category=PestCategory.INSECT,
            confidence=0.95,
            severity="high"
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique detection ID | معرف الكشف الفريد")

    pest_type: str = Field(..., description="Type/name of pest | نوع/اسم الآفة")

    pest_type_ar: str = Field(default="", description="Pest type (Arabic) | نوع الآفة (عربي)")

    category: PestCategory = Field(..., description="Pest category | فئة الآفة")

    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence | ثقة الكشف")

    severity: str = Field(default="medium", description="Severity level: low/medium/high/critical | مستوى الشدة")

    # Bounding box
    bbox_x: float | None = Field(None, description="Bounding box X coordinate | إحداثي X للمربع")

    bbox_y: float | None = Field(None, description="Bounding box Y coordinate | إحداثي Y للمربع")

    bbox_width: float | None = Field(None, description="Bounding box width | عرض المربع")

    bbox_height: float | None = Field(None, description="Bounding box height | ارتفاع المربع")

    # Context
    affected_area_percent: float | None = Field(
        None, ge=0, le=100, description="Percentage of affected area | نسبة المنطقة المتضررة"
    )

    recommended_treatment: str = Field(default="", description="Recommended treatment | العلاج الموصى به")

    recommended_treatment_ar: str = Field(default="", description="Treatment (Arabic) | العلاج (عربي)")

    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Detection timestamp | وقت الكشف"
    )

    image_id: str = Field(default="", description="Source image identifier | معرف الصورة المصدر")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")


class MoisturePrediction(BaseModel):
    """
    Soil moisture prediction from cloud AI.
    تنبؤ رطوبة التربة من الذكاء الاصطناعي السحابي

    Achieves approximately 3% error rate for 3-day predictions.

    Example:
        prediction = MoisturePrediction(
            predictions=[42.5, 40.2, 38.1],
            error_margin=0.03,
            prediction_horizon_days=3
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique prediction ID | معرف التنبؤ الفريد")

    # Predictions
    predictions: list[float] = Field(..., description="Daily moisture predictions (%) | التنبؤات اليومية (%)")

    prediction_horizon_days: int = Field(
        default=3, ge=1, le=30, description="Number of days predicted | عدد أيام التنبؤ"
    )

    # Error metrics
    error_margin: float = Field(
        default=0.03, ge=0.0, le=1.0, description="Expected error margin (~3%) | هامش الخطأ المتوقع"
    )

    confidence_intervals: list[tuple[float, float]] = Field(
        default_factory=list, description="Confidence intervals for each day | فترات الثقة لكل يوم"
    )

    # Input context
    initial_moisture: float = Field(
        default=0.0, ge=0, le=100, description="Initial soil moisture (%) | الرطوبة الأولية"
    )

    weather_factors: dict[str, Any] = Field(
        default_factory=dict, description="Weather factors used | عوامل الطقس المستخدمة"
    )

    soil_type: str = Field(default="", description="Soil type | نوع التربة")

    crop_type: str = Field(default="", description="Crop type | نوع المحصول")

    # Model info
    model_name: str = Field(default="moisture_lstm", description="Model used | النموذج المستخدم")

    model_version: str = Field(default="1.0.0", description="Model version | إصدار النموذج")

    # Timestamps
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Generation timestamp | وقت التوليد"
    )

    valid_from: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Prediction start date | تاريخ بدء التنبؤ",
    )

    # Location
    field_id: str = Field(default="", description="Field identifier | معرف الحقل")

    zone_id: str = Field(default="", description="Zone identifier | معرف المنطقة")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")


class YieldEstimation(BaseModel):
    """
    Crop yield estimation from cloud AI.
    تقدير إنتاجية المحصول من الذكاء الاصطناعي السحابي

    Provides 15-day yield curve predictions.

    Example:
        estimation = YieldEstimation(
            crop_type="wheat",
            estimated_yield_kg_ha=4500.0,
            yield_curve=[4200, 4300, 4350, ...],
            confidence=0.85
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique estimation ID | معرف التقدير الفريد")

    # Crop context
    crop_type: str = Field(..., description="Crop type | نوع المحصول")

    crop_type_ar: str = Field(default="", description="Crop type (Arabic) | نوع المحصول (عربي)")

    growth_stage: str = Field(default="", description="Current growth stage | مرحلة النمو الحالية")

    # Yield estimates
    estimated_yield_kg_ha: float = Field(
        ..., ge=0, description="Estimated yield in kg/hectare | الإنتاجية المقدرة كجم/هكتار"
    )

    yield_curve: list[float] = Field(default_factory=list, description="15-day yield curve | منحنى الإنتاجية لـ 15 يوم")

    min_yield_kg_ha: float | None = Field(None, ge=0, description="Minimum yield estimate | الحد الأدنى للإنتاجية")

    max_yield_kg_ha: float | None = Field(None, ge=0, description="Maximum yield estimate | الحد الأقصى للإنتاجية")

    # Confidence
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Estimation confidence | ثقة التقدير")

    # Factors
    contributing_factors: dict[str, float] = Field(
        default_factory=dict, description="Factors and their weights | العوامل وأوزانها"
    )

    risk_factors: list[str] = Field(default_factory=list, description="Identified risk factors | عوامل الخطر المحددة")

    risk_factors_ar: list[str] = Field(default_factory=list, description="Risk factors (Arabic) | عوامل الخطر (عربي)")

    # Input data
    field_area_ha: float = Field(default=0.0, ge=0, description="Field area in hectares | مساحة الحقل بالهكتار")

    weather_forecast_used: bool = Field(
        default=True, description="Whether weather forecast was used | هل تم استخدام توقعات الطقس"
    )

    # Model info
    model_name: str = Field(default="yield_prediction", description="Model used | النموذج المستخدم")

    model_version: str = Field(default="1.0.0", description="Model version | إصدار النموذج")

    # Timestamps
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Generation timestamp | وقت التوليد"
    )

    forecast_horizon_days: int = Field(
        default=15, ge=1, le=90, description="Forecast horizon in days | أفق التنبؤ بالأيام"
    )

    # Location
    field_id: str = Field(default="", description="Field identifier | معرف الحقل")

    farm_id: str = Field(default="", description="Farm identifier | معرف المزرعة")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")


# =============================================================================
# System Metrics - مقاييس النظام
# =============================================================================


class SystemMetrics(BaseModel):
    """
    Metrics for the Edge-Cloud cooperative system.
    مقاييس نظام التعاون بين الحافة والسحابة

    Example:
        metrics = SystemMetrics(
            edge_latency_ms=280.0,
            cloud_latency_ms=1200.0,
            edge_accuracy=0.88,
            cloud_accuracy=0.95,
            uptime_percent=99.5
        )
    """

    # Latency metrics
    edge_latency_ms: float = Field(
        default=0.0, ge=0, description="Average edge layer latency (ms) | متوسط زمن استجابة الحافة"
    )

    cloud_latency_ms: float = Field(
        default=0.0,
        ge=0,
        description="Average cloud layer latency (ms) | متوسط زمن استجابة السحابة",
    )

    total_latency_ms: float = Field(
        default=0.0, ge=0, description="Total system latency (ms) | إجمالي زمن استجابة النظام"
    )

    # Accuracy metrics
    edge_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Edge layer accuracy | دقة طبقة الحافة")

    cloud_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Cloud layer accuracy | دقة طبقة السحابة")

    moisture_prediction_error: float = Field(
        default=0.03,
        ge=0.0,
        le=1.0,
        description="Moisture prediction error rate (~3%) | معدل خطأ تنبؤ الرطوبة",
    )

    # Availability
    uptime_percent: float = Field(
        default=0.0, ge=0.0, le=100.0, description="System uptime percentage | نسبة وقت التشغيل"
    )

    edge_uptime_percent: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Edge layer uptime | وقت تشغيل طبقة الحافة"
    )

    cloud_uptime_percent: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Cloud layer uptime | وقت تشغيل طبقة السحابة"
    )

    # Throughput
    readings_per_minute: float = Field(
        default=0.0, ge=0, description="Sensor readings per minute | القراءات في الدقيقة"
    )

    decisions_per_minute: float = Field(default=0.0, ge=0, description="Decisions per minute | القرارات في الدقيقة")

    inferences_per_minute: float = Field(
        default=0.0, ge=0, description="Cloud inferences per minute | الاستدلالات في الدقيقة"
    )

    # Device metrics
    total_devices: int = Field(default=0, ge=0, description="Total registered devices | إجمالي الأجهزة المسجلة")

    active_devices: int = Field(default=0, ge=0, description="Currently active devices | الأجهزة النشطة حالياً")

    offline_devices: int = Field(default=0, ge=0, description="Offline devices | الأجهزة غير المتصلة")

    # Sync metrics
    sync_success_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Edge-cloud sync success rate | معدل نجاح المزامنة"
    )

    pending_sync_count: int = Field(default=0, ge=0, description="Pending items to sync | العناصر المعلقة للمزامنة")

    last_sync_at: datetime | None = Field(None, description="Last successful sync | آخر مزامنة ناجحة")

    # Timestamps
    measured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Measurement timestamp | وقت القياس"
    )

    measurement_period_seconds: int = Field(
        default=60, ge=1, description="Measurement period in seconds | فترة القياس بالثواني"
    )

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")


# =============================================================================
# IFTTT-Style Rule Models - نماذج قواعد IFTTT
# =============================================================================


class RuleCondition(BaseModel):
    """
    A condition in an IFTTT-style rule.
    شرط في قاعدة نمط IFTTT

    Example:
        condition = RuleCondition(
            sensor_type=SensorType.SOIL_MOISTURE,
            operator="<",
            threshold=30.0
        )
    """

    sensor_type: SensorType = Field(..., description="Sensor type to monitor | نوع المستشعر للمراقبة")

    operator: str = Field(..., description="Comparison operator (<, >, <=, >=, ==, !=) | عامل المقارنة")

    threshold: float = Field(..., description="Threshold value | قيمة العتبة")

    unit: str = Field(default="", description="Unit of measurement | وحدة القياس")

    zone_id: str | None = Field(None, description="Specific zone (optional) | المنطقة المحددة (اختياري)")


class RuleAction(BaseModel):
    """
    An action in an IFTTT-style rule.
    إجراء في قاعدة نمط IFTTT

    Example:
        action = RuleAction(
            action_type="start_irrigation",
            parameters={"zone": "A", "duration_minutes": 30}
        )
    """

    action_type: str = Field(..., description="Type of action | نوع الإجراء")

    action_type_ar: str = Field(default="", description="Action type (Arabic) | نوع الإجراء (عربي)")

    parameters: dict[str, Any] = Field(default_factory=dict, description="Action parameters | معلمات الإجراء")

    delay_seconds: int = Field(default=0, ge=0, description="Delay before execution | التأخير قبل التنفيذ")


class IFTTTRule(BaseModel):
    """
    An IFTTT-style rule for edge computing automation.
    قاعدة نمط IFTTT لأتمتة الحوسبة الطرفية

    Enables local decision-making without cloud connectivity.

    Example:
        rule = IFTTTRule(
            name="Low Moisture Auto Irrigation",
            name_ar="الري التلقائي عند انخفاض الرطوبة",
            conditions=[condition],
            actions=[action],
            is_active=True
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique rule ID | معرف القاعدة الفريد")

    name: str = Field(..., min_length=1, description="Rule name | اسم القاعدة")

    name_ar: str = Field(default="", description="Rule name (Arabic) | اسم القاعدة (عربي)")

    description: str = Field(default="", description="Rule description | وصف القاعدة")

    description_ar: str = Field(default="", description="Description (Arabic) | الوصف (عربي)")

    # Conditions and actions
    conditions: list[RuleCondition] = Field(
        ..., min_length=1, description="Conditions that must all be true | الشروط التي يجب أن تتحقق"
    )

    condition_logic: str = Field(default="AND", description="Logic between conditions (AND/OR) | المنطق بين الشروط")

    actions: list[RuleAction] = Field(..., min_length=1, description="Actions to execute | الإجراءات المراد تنفيذها")

    # Execution settings
    is_active: bool = Field(default=True, description="Whether rule is active | هل القاعدة نشطة")

    priority: int = Field(default=5, ge=1, le=10, description="Rule priority (1=highest) | أولوية القاعدة")

    cooldown_minutes: int = Field(
        default=60,
        ge=0,
        description="Minimum time between triggers | الحد الأدنى للوقت بين التفعيلات",
    )

    max_daily_triggers: int = Field(
        default=10, ge=1, description="Maximum triggers per day | الحد الأقصى للتفعيلات اليومية"
    )

    # Time constraints
    active_hours_start: int | None = Field(
        None, ge=0, le=23, description="Start hour for rule (0-23) | ساعة بدء القاعدة"
    )

    active_hours_end: int | None = Field(None, ge=0, le=23, description="End hour for rule (0-23) | ساعة نهاية القاعدة")

    # Metadata
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp | وقت الإنشاء"
    )

    last_triggered_at: datetime | None = Field(None, description="Last trigger time | آخر وقت تفعيل")

    trigger_count: int = Field(default=0, ge=0, description="Total trigger count | إجمالي عدد التفعيلات")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")
