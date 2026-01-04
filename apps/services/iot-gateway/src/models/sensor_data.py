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


def check_value_in_range(
    sensor_type: str, value: float
) -> tuple[bool, str | None]:
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
