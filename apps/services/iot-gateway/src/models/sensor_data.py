"""
نماذج بيانات المستشعرات - SAHOOL IoT
Sensor Data Models for IoT Gateway

يحتوي على نماذج القراءات والبيانات المجمعة وصحة المستشعرات
Contains models for readings, aggregated data, and sensor health
"""

from dataclasses import asdict, dataclass, field
from enum import Enum


class AggregationMethod(str, Enum):
    """طرق التجميع - Aggregation methods"""

    MEAN = "mean"  # المتوسط الحسابي
    MEDIAN = "median"  # الوسيط
    MIN = "min"  # القيمة الدنيا
    MAX = "max"  # القيمة القصوى
    STD = "std"  # الانحراف المعياري
    SUM = "sum"  # المجموع
    COUNT = "count"  # العدد
    PERCENTILE_10 = "p10"  # المئين العاشر
    PERCENTILE_25 = "p25"  # المئين الخامس والعشرون
    PERCENTILE_75 = "p75"  # المئين الخامس والسبعون
    PERCENTILE_90 = "p90"  # المئين التسعون
    RATE_OF_CHANGE = "rate_of_change"  # معدل التغيير
    CUMULATIVE_SUM = "cumulative_sum"  # المجموع التراكمي


class TimeGranularity(str, Enum):
    """دقة الوقت - Time granularity for aggregation"""

    HOURLY = "hourly"  # كل ساعة
    DAILY = "daily"  # يومي
    WEEKLY = "weekly"  # أسبوعي
    MONTHLY = "monthly"  # شهري


class SensorStatus(str, Enum):
    """حالة المستشعر - Sensor status"""

    HEALTHY = "healthy"  # سليم
    WARNING = "warning"  # تحذير
    CRITICAL = "critical"  # حرج
    OFFLINE = "offline"  # غير متصل
    DRIFT_DETECTED = "drift_detected"  # انحراف مكتشف


@dataclass
class SensorReading:
    """
    قراءة مستشعر واحدة
    Single sensor reading
    """

    device_id: str  # معرف الجهاز
    field_id: str  # معرف الحقل
    sensor_type: str  # نوع المستشعر
    value: float  # القيمة
    unit: str  # الوحدة
    timestamp: str  # وقت القراءة
    metadata: dict | None = None  # بيانات إضافية
    quality_score: float | None = None  # نقاط الجودة (0-100)
    is_outlier: bool = False  # هل هي قيمة شاذة

    def to_dict(self) -> dict:
        """تحويل إلى قاموس - Convert to dictionary"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> "SensorReading":
        """إنشاء من قاموس - Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class AggregatedData:
    """
    بيانات مجمعة للمستشعرات
    Aggregated sensor data
    """

    field_id: str  # معرف الحقل
    sensor_type: str  # نوع المستشعر
    time_range_start: str  # بداية الفترة الزمنية
    time_range_end: str  # نهاية الفترة الزمنية
    granularity: TimeGranularity  # دقة الوقت

    # إحصائيات أساسية - Basic statistics
    mean: float | None = None  # المتوسط
    median: float | None = None  # الوسيط
    min: float | None = None  # القيمة الدنيا
    max: float | None = None  # القيمة القصوى
    std: float | None = None  # الانحراف المعياري
    count: int = 0  # عدد القراءات

    # المئينات - Percentiles
    percentile_10: float | None = None  # المئين العاشر
    percentile_25: float | None = None  # المئين الخامس والعشرون (الربيع الأول)
    percentile_75: float | None = None  # المئين الخامس والسبعون (الربيع الثالث)
    percentile_90: float | None = None  # المئين التسعون

    # مقاييس متقدمة - Advanced metrics
    rate_of_change: float | None = None  # معدل التغيير (وحدة/ساعة)
    cumulative_sum: float | None = None  # المجموع التراكمي (للأمطار)

    # بيانات الجودة - Quality metrics
    data_quality_score: float | None = None  # نقاط جودة البيانات (0-100)
    outlier_count: int = 0  # عدد القيم الشاذة
    missing_count: int = 0  # عدد القراءات المفقودة

    # بيانات إضافية - Additional metadata
    devices: list[str] = field(default_factory=list)  # قائمة الأجهزة المساهمة
    metadata: dict | None = None  # بيانات إضافية

    def to_dict(self) -> dict:
        """تحويل إلى قاموس - Convert to dictionary"""
        result = asdict(self)
        result["granularity"] = self.granularity.value
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> "AggregatedData":
        """إنشاء من قاموس - Create from dictionary"""
        if "granularity" in data and isinstance(data["granularity"], str):
            data["granularity"] = TimeGranularity(data["granularity"])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class SensorHealth:
    """
    صحة المستشعر وحالته
    Sensor health and status information
    """

    device_id: str  # معرف الجهاز
    field_id: str  # معرف الحقل
    sensor_type: str  # نوع المستشعر
    status: SensorStatus  # الحالة
    timestamp: str  # وقت الفحص

    # مقاييس الصحة - Health metrics
    data_quality_score: float = 0.0  # نقاط جودة البيانات (0-100)
    uptime_percentage: float = 0.0  # نسبة وقت التشغيل (0-100)
    battery_level: float | None = None  # مستوى البطارية (0-100)
    signal_strength: float | None = None  # قوة الإشارة (dBm)

    # اكتشاف المشاكل - Issue detection
    drift_detected: bool = False  # هل تم اكتشاف انحراف
    drift_magnitude: float | None = None  # مقدار الانحراف
    consecutive_errors: int = 0  # عدد الأخطاء المتتالية
    last_successful_reading: str | None = None  # آخر قراءة ناجحة

    # الإحصائيات - Statistics
    readings_count_24h: int = 0  # عدد القراءات في 24 ساعة
    expected_readings_24h: int = 0  # العدد المتوقع للقراءات
    outlier_percentage: float = 0.0  # نسبة القيم الشاذة

    # التنبيهات - Alerts
    alerts: list[str] = field(default_factory=list)  # قائمة التنبيهات
    recommendations_ar: list[str] = field(default_factory=list)  # التوصيات بالعربية
    recommendations_en: list[str] = field(default_factory=list)  # التوصيات بالإنجليزية

    # بيانات إضافية - Additional metadata
    metadata: dict | None = None  # بيانات إضافية

    def to_dict(self) -> dict:
        """تحويل إلى قاموس - Convert to dictionary"""
        result = asdict(self)
        result["status"] = self.status.value
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> "SensorHealth":
        """إنشاء من قاموس - Create from dictionary"""
        if "status" in data and isinstance(data["status"], str):
            data["status"] = SensorStatus(data["status"])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    def is_healthy(self) -> bool:
        """هل المستشعر سليم - Check if sensor is healthy"""
        return self.status == SensorStatus.HEALTHY

    def needs_attention(self) -> bool:
        """هل يحتاج المستشعر إلى اهتمام - Check if sensor needs attention"""
        return self.status in [SensorStatus.WARNING, SensorStatus.CRITICAL]


@dataclass
class AlertThreshold:
    """
    عتبات التنبيه للمستشعرات (مناخ اليمن)
    Alert thresholds for sensors (Yemen climate)
    """

    sensor_type: str  # نوع المستشعر
    min_value: float  # القيمة الدنيا
    max_value: float  # القيمة القصوى
    unit: str  # الوحدة
    critical_min: float | None = None  # القيمة الدنيا الحرجة
    critical_max: float | None = None  # القيمة القصوى الحرجة
    description_ar: str = ""  # الوصف بالعربية
    description_en: str = ""  # الوصف بالإنجليزية


# =============================================================================
# مواصفات دقة المستشعرات الزراعية (من معايير ISO ومقالة الاستشعار الزراعي)
# Agricultural Sensor Accuracy Specifications (based on ISO standards and
# agricultural sensing article specifications)
# =============================================================================


@dataclass
class SensorAccuracySpec:
    """
    مواصفات دقة المستشعر
    Sensor accuracy specification based on agricultural sensing standards

    Reference: Chinese Agricultural Sensing Technology Article (2025)
    """

    sensor_type: str
    accuracy: float  # قيمة الدقة - Accuracy value
    accuracy_unit: str  # وحدة الدقة - Accuracy unit (e.g., "%" for percentage, "abs" for absolute)
    measurement_range_min: float  # الحد الأدنى للقياس - Minimum measurement
    measurement_range_max: float  # الحد الأقصى للقياس - Maximum measurement
    measurement_unit: str  # وحدة القياس - Measurement unit
    response_time_seconds: float  # زمن الاستجابة بالثواني - Response time in seconds
    operating_temp_min: float  # درجة حرارة التشغيل الدنيا - Min operating temp (°C)
    operating_temp_max: float  # درجة حرارة التشغيل القصوى - Max operating temp (°C)
    protection_rating: str  # تصنيف الحماية (IP) - IP protection rating
    calibration_interval_months: int  # فترة المعايرة بالأشهر - Calibration interval
    drift_threshold_percent: float  # عتبة الانحراف المسموحة - Allowed drift threshold
    description_ar: str
    description_en: str


# مواصفات دقة المستشعرات الزراعية وفقاً لمعايير المقالة
# Agricultural sensor accuracy specs based on article standards
SENSOR_ACCURACY_SPECS = {
    "soil_moisture": SensorAccuracySpec(
        sensor_type="soil_moisture",
        accuracy=2.0,  # ±2% حجم - ±2% vol
        accuracy_unit="%",
        measurement_range_min=0.0,
        measurement_range_max=100.0,
        measurement_unit="% vol",
        response_time_seconds=30.0,  # حسب تقنية FDR
        operating_temp_min=-20.0,
        operating_temp_max=60.0,
        protection_rating="IP68",
        calibration_interval_months=12,
        drift_threshold_percent=5.0,
        description_ar="مستشعر رطوبة التربة بتقنية انعكاس مجال التردد (FDR)",
        description_en="Soil moisture sensor using Frequency Domain Reflectometry (FDR)",
    ),
    "soil_ec": SensorAccuracySpec(
        sensor_type="soil_ec",
        accuracy=0.01,  # ±0.01 mS/cm
        accuracy_unit="mS/cm",
        measurement_range_min=0.0,
        measurement_range_max=10.0,
        measurement_unit="mS/cm",
        response_time_seconds=2.0,
        operating_temp_min=0.0,
        operating_temp_max=60.0,
        protection_rating="IP68",
        calibration_interval_months=6,
        drift_threshold_percent=2.0,
        description_ar="مستشعر الموصلية الكهربائية للتربة (الملوحة)",
        description_en="Soil Electrical Conductivity (EC/Salinity) sensor",
    ),
    "soil_ph": SensorAccuracySpec(
        sensor_type="soil_ph",
        accuracy=0.02,  # ±0.02 pH
        accuracy_unit="pH",
        measurement_range_min=4.0,
        measurement_range_max=8.0,
        measurement_unit="pH",
        response_time_seconds=2.0,
        operating_temp_min=0.0,
        operating_temp_max=60.0,
        protection_rating="IP68",
        calibration_interval_months=6,
        drift_threshold_percent=1.0,
        description_ar="مستشعر حموضة التربة مع تعويض تلقائي لدرجة الحرارة",
        description_en="Soil pH sensor with automatic temperature compensation",
    ),
    "air_temperature": SensorAccuracySpec(
        sensor_type="air_temperature",
        accuracy=0.2,  # ±0.2°C
        accuracy_unit="°C",
        measurement_range_min=-40.0,
        measurement_range_max=85.0,
        measurement_unit="°C",
        response_time_seconds=8.0,
        operating_temp_min=-40.0,
        operating_temp_max=85.0,
        protection_rating="IP65",
        calibration_interval_months=12,
        drift_threshold_percent=1.0,
        description_ar="مستشعر درجة حرارة الهواء عالي الدقة",
        description_en="High-precision air temperature sensor",
    ),
    "soil_temperature": SensorAccuracySpec(
        sensor_type="soil_temperature",
        accuracy=0.2,  # ±0.2°C
        accuracy_unit="°C",
        measurement_range_min=-20.0,
        measurement_range_max=60.0,
        measurement_unit="°C",
        response_time_seconds=10.0,
        operating_temp_min=-40.0,
        operating_temp_max=85.0,
        protection_rating="IP68",
        calibration_interval_months=12,
        drift_threshold_percent=1.0,
        description_ar="مستشعر درجة حرارة التربة مقاوم لدرجات الحرارة المنخفضة",
        description_en="Low-temperature resistant soil temperature sensor",
    ),
    "air_humidity": SensorAccuracySpec(
        sensor_type="air_humidity",
        accuracy=2.0,  # ±2% RH
        accuracy_unit="% RH",
        measurement_range_min=0.0,
        measurement_range_max=100.0,
        measurement_unit="% RH",
        response_time_seconds=8.0,
        operating_temp_min=-40.0,
        operating_temp_max=85.0,
        protection_rating="IP65",
        calibration_interval_months=12,
        drift_threshold_percent=2.0,
        description_ar="مستشعر رطوبة الهواء السعوي مع تصميم مضاد للتلوث",
        description_en="Capacitive air humidity sensor with anti-pollution design",
    ),
    "light_intensity": SensorAccuracySpec(
        sensor_type="light_intensity",
        accuracy=5.0,  # ±5%
        accuracy_unit="%",
        measurement_range_min=0.0,
        measurement_range_max=200000.0,
        measurement_unit="lux",
        response_time_seconds=1.0,
        operating_temp_min=-20.0,
        operating_temp_max=60.0,
        protection_rating="IP65",
        calibration_interval_months=12,
        drift_threshold_percent=3.0,
        description_ar="مستشعر شدة الضوء بنطاق طيف 400-700nm (PAR)",
        description_en="Light intensity sensor with 400-700nm spectral response (PAR)",
    ),
    "co2_concentration": SensorAccuracySpec(
        sensor_type="co2_concentration",
        accuracy=50.0,  # ±50ppm + 2% FS
        accuracy_unit="ppm",
        measurement_range_min=0.0,
        measurement_range_max=5000.0,
        measurement_unit="ppm",
        response_time_seconds=10.0,
        operating_temp_min=-10.0,
        operating_temp_max=50.0,
        protection_rating="IP54",
        calibration_interval_months=12,
        drift_threshold_percent=2.0,
        description_ar="مستشعر تركيز ثاني أكسيد الكربون بتقنية الأشعة تحت الحمراء",
        description_en="CO2 concentration sensor using infrared detection technology",
    ),
    "water_flow": SensorAccuracySpec(
        sensor_type="water_flow",
        accuracy=1.0,  # ±1% FS
        accuracy_unit="% FS",
        measurement_range_min=0.0,
        measurement_range_max=50.0,
        measurement_unit="m³/h",
        response_time_seconds=1.0,
        operating_temp_min=-10.0,
        operating_temp_max=60.0,
        protection_rating="IP68",
        calibration_interval_months=12,
        drift_threshold_percent=2.0,
        description_ar="مستشعر تدفق مياه الري مع فلتر مقاوم للانسداد",
        description_en="Irrigation water flow sensor with anti-clogging filter",
    ),
    "chlorophyll": SensorAccuracySpec(
        sensor_type="chlorophyll",
        accuracy=1.0,  # ±1 SPAD
        accuracy_unit="SPAD",
        measurement_range_min=0.0,
        measurement_range_max=99.9,
        measurement_unit="SPAD",
        response_time_seconds=2.0,
        operating_temp_min=5.0,
        operating_temp_max=40.0,
        protection_rating="IP54",
        calibration_interval_months=6,
        drift_threshold_percent=2.0,
        description_ar="مستشعر الكلوروفيل لمراقبة الحالة الغذائية النيتروجينية",
        description_en="Chlorophyll sensor for nitrogen nutritional status monitoring",
    ),
    "leaf_moisture": SensorAccuracySpec(
        sensor_type="leaf_moisture",
        accuracy=2.0,  # ±2% RH
        accuracy_unit="% RH",
        measurement_range_min=0.0,
        measurement_range_max=100.0,
        measurement_unit="% RH",
        response_time_seconds=5.0,
        operating_temp_min=-10.0,
        operating_temp_max=50.0,
        protection_rating="IP65",
        calibration_interval_months=6,
        drift_threshold_percent=3.0,
        description_ar="مستشعر رطوبة الأوراق للإنذار المبكر بالأمراض الفطرية",
        description_en="Leaf moisture sensor for early warning of fungal diseases",
    ),
    "soil_npk": SensorAccuracySpec(
        sensor_type="soil_npk",
        accuracy=5.0,  # ±5% FS
        accuracy_unit="% FS",
        measurement_range_min=0.0,
        measurement_range_max=500.0,
        measurement_unit="mg/kg",
        response_time_seconds=30.0,
        operating_temp_min=-10.0,
        operating_temp_max=50.0,
        protection_rating="IP68",
        calibration_interval_months=6,
        drift_threshold_percent=5.0,
        description_ar="مستشعر خصوبة التربة (النيتروجين والفوسفور والبوتاسيوم)",
        description_en="Soil fertility sensor (Nitrogen, Phosphorus, Potassium)",
    ),
    "wind_speed": SensorAccuracySpec(
        sensor_type="wind_speed",
        accuracy=0.3,  # ±0.3 m/s
        accuracy_unit="m/s",
        measurement_range_min=0.0,
        measurement_range_max=60.0,
        measurement_unit="m/s",
        response_time_seconds=1.0,
        operating_temp_min=-40.0,
        operating_temp_max=60.0,
        protection_rating="IP65",
        calibration_interval_months=12,
        drift_threshold_percent=2.0,
        description_ar="مستشعر سرعة الرياح بتصميم مقاوم للعواصف الرملية",
        description_en="Wind speed sensor with sandstorm-resistant design",
    ),
    "rainfall": SensorAccuracySpec(
        sensor_type="rainfall",
        accuracy=0.2,  # ±0.2mm
        accuracy_unit="mm",
        measurement_range_min=0.0,
        measurement_range_max=500.0,
        measurement_unit="mm",
        response_time_seconds=1.0,
        operating_temp_min=-20.0,
        operating_temp_max=60.0,
        protection_rating="IP68",
        calibration_interval_months=12,
        drift_threshold_percent=2.0,
        description_ar="مستشعر هطول الأمطار",
        description_en="Rainfall sensor",
    ),
}


def get_sensor_accuracy_spec(sensor_type: str) -> SensorAccuracySpec | None:
    """
    الحصول على مواصفات دقة المستشعر
    Get sensor accuracy specification

    Args:
        sensor_type: نوع المستشعر - Sensor type

    Returns:
        SensorAccuracySpec or None if not found
    """
    return SENSOR_ACCURACY_SPECS.get(sensor_type.lower())


def validate_reading_accuracy(
    sensor_type: str, value: float, reference_value: float | None = None
) -> tuple[bool, float | None, str]:
    """
    التحقق من دقة القراءة مقارنة بالمواصفات
    Validate reading accuracy against specifications

    Args:
        sensor_type: نوع المستشعر
        value: القيمة المقاسة
        reference_value: القيمة المرجعية (للمعايرة)

    Returns:
        (is_valid, deviation, message)
    """
    spec = get_sensor_accuracy_spec(sensor_type)
    if not spec:
        return True, None, "No accuracy spec defined"

    # Check if value is in range
    if value < spec.measurement_range_min or value > spec.measurement_range_max:
        return (
            False,
            None,
            f"Value {value} out of range [{spec.measurement_range_min}, {spec.measurement_range_max}]",
        )

    # If reference value provided, check deviation
    if reference_value is not None:
        if spec.accuracy_unit == "%":
            deviation = abs(value - reference_value)
            is_valid = deviation <= spec.accuracy
        elif spec.accuracy_unit == "% FS":
            full_scale = spec.measurement_range_max - spec.measurement_range_min
            deviation = abs(value - reference_value)
            is_valid = deviation <= (spec.accuracy / 100) * full_scale
        else:
            deviation = abs(value - reference_value)
            is_valid = deviation <= spec.accuracy

        status = "valid" if is_valid else "deviation exceeds spec"
        return is_valid, deviation, status

    return True, None, "Within specification range"


# عتبات التنبيه لمناخ اليمن
# Alert thresholds for Yemen climate
YEMEN_THRESHOLDS = {
    "soil_moisture": AlertThreshold(
        sensor_type="soil_moisture",
        min_value=20.0,
        max_value=80.0,
        critical_min=10.0,
        critical_max=90.0,
        unit="%",
        description_ar="رطوبة التربة المثلى للزراعة في اليمن",
        description_en="Optimal soil moisture for agriculture in Yemen",
    ),
    "air_temperature": AlertThreshold(
        sensor_type="air_temperature",
        min_value=5.0,
        max_value=45.0,
        critical_min=0.0,
        critical_max=50.0,
        unit="°C",
        description_ar="درجة حرارة الهواء الآمنة للمحاصيل",
        description_en="Safe air temperature for crops",
    ),
    "soil_temperature": AlertThreshold(
        sensor_type="soil_temperature",
        min_value=10.0,
        max_value=35.0,
        critical_min=5.0,
        critical_max=40.0,
        unit="°C",
        description_ar="درجة حرارة التربة المثلى",
        description_en="Optimal soil temperature",
    ),
    "air_humidity": AlertThreshold(
        sensor_type="air_humidity",
        min_value=10.0,
        max_value=95.0,
        critical_min=5.0,
        critical_max=98.0,
        unit="%",
        description_ar="رطوبة الهواء النسبية",
        description_en="Relative air humidity",
    ),
    "soil_ec": AlertThreshold(
        sensor_type="soil_ec",
        min_value=0.0,
        max_value=4.0,
        critical_min=0.0,
        critical_max=6.0,
        unit="dS/m",
        description_ar="الملوحة الكهربائية للتربة",
        description_en="Soil electrical conductivity (salinity)",
    ),
    "soil_ph": AlertThreshold(
        sensor_type="soil_ph",
        min_value=5.5,
        max_value=8.5,
        critical_min=4.5,
        critical_max=9.5,
        unit="",
        description_ar="حموضة التربة",
        description_en="Soil pH level",
    ),
    "rainfall": AlertThreshold(
        sensor_type="rainfall",
        min_value=0.0,
        max_value=100.0,  # يومي - daily
        critical_min=0.0,
        critical_max=200.0,
        unit="mm",
        description_ar="معدل هطول الأمطار اليومي",
        description_en="Daily rainfall rate",
    ),
    "wind_speed": AlertThreshold(
        sensor_type="wind_speed",
        min_value=0.0,
        max_value=15.0,  # m/s
        critical_min=0.0,
        critical_max=25.0,
        unit="m/s",
        description_ar="سرعة الرياح",
        description_en="Wind speed",
    ),
}


def get_threshold(sensor_type: str) -> AlertThreshold | None:
    """
    الحصول على عتبة التنبيه لنوع المستشعر
    Get alert threshold for sensor type
    """
    return YEMEN_THRESHOLDS.get(sensor_type.lower())


def check_value_in_range(sensor_type: str, value: float) -> tuple[bool, str | None]:
    """
    التحقق من القيمة ضمن النطاق المقبول
    Check if value is within acceptable range

    Returns:
        (is_valid, severity) where severity is None, 'warning', or 'critical'
    """
    threshold = get_threshold(sensor_type)
    if not threshold:
        return True, None  # لا توجد عتبة معرفة - No threshold defined

    # فحص القيم الحرجة - Check critical values
    if threshold.critical_min is not None and value < threshold.critical_min:
        return False, "critical"
    if threshold.critical_max is not None and value > threshold.critical_max:
        return False, "critical"

    # فحص القيم التحذيرية - Check warning values
    if value < threshold.min_value or value > threshold.max_value:
        return False, "warning"

    return True, None
