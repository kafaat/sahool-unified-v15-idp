"""
SAHOOL Drone Integration Models - نماذج بيانات تكامل الطائرات بدون طيار

Data models for drone flight planning, missions, waypoints, and variable rate application.
Supports DJI and open-source drone protocols.

Version: 1.0.0
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

# ==============================================================================
# Enumerations - التعدادات
# ==============================================================================


class DroneType(StrEnum):
    """Type of drone platform - نوع منصة الطائرة"""

    DJI_AGRAS_T40 = "dji_agras_t40"  # DJI Agras T40
    DJI_AGRAS_T30 = "dji_agras_t30"  # DJI Agras T30
    DJI_AGRAS_T20P = "dji_agras_t20p"  # DJI Agras T20P
    DJI_MAVIC_3M = "dji_mavic_3m"  # DJI Mavic 3 Multispectral
    DJI_PHANTOM_4_RTK = "dji_phantom_4_rtk"  # DJI Phantom 4 RTK
    DJI_MATRICE_300 = "dji_matrice_300"  # DJI Matrice 300 RTK
    DJI_MATRICE_350 = "dji_matrice_350"  # DJI Matrice 350 RTK
    ARDUPILOT = "ardupilot"  # ArduPilot-based drones
    PX4 = "px4"  # PX4-based drones
    CUSTOM = "custom"  # Custom drone platform


class FlightMode(StrEnum):
    """Flight operation mode - وضع العملية الجوية"""

    MAPPING = "mapping"  # Aerial mapping mission | مهمة رسم الخرائط
    SPRAYING = "spraying"  # Spraying mission | مهمة الرش
    SCOUTING = "scouting"  # Crop scouting | استكشاف المحصول
    SURVEYING = "surveying"  # Field surveying | مسح الحقل
    SPREADING = "spreading"  # Granular spreading | نثر حبيبي
    SEEDING = "seeding"  # Aerial seeding | البذر الجوي
    INSPECTION = "inspection"  # Infrastructure inspection | التفتيش


class FlightStatus(StrEnum):
    """Flight status - حالة الرحلة"""

    PLANNED = "planned"  # مخطط
    READY = "ready"  # جاهز للتنفيذ
    IN_PROGRESS = "in_progress"  # قيد التنفيذ
    PAUSED = "paused"  # متوقف مؤقتاً
    COMPLETED = "completed"  # مكتمل
    ABORTED = "aborted"  # ملغى
    FAILED = "failed"  # فشل


class MissionStatus(StrEnum):
    """Mission status - حالة المهمة"""

    DRAFT = "draft"  # مسودة
    PENDING_APPROVAL = "pending_approval"  # بانتظار الموافقة
    APPROVED = "approved"  # موافق عليه
    SCHEDULED = "scheduled"  # مجدول
    IN_PROGRESS = "in_progress"  # قيد التنفيذ
    COMPLETED = "completed"  # مكتمل
    CANCELLED = "cancelled"  # ملغى


class WaypointAction(StrEnum):
    """Action at waypoint - الإجراء عند نقطة المسار"""

    NONE = "none"  # لا شيء
    HOVER = "hover"  # تحليق ثابت
    TAKE_PHOTO = "take_photo"  # التقاط صورة
    START_RECORDING = "start_recording"  # بدء التسجيل
    STOP_RECORDING = "stop_recording"  # إيقاف التسجيل
    START_SPRAY = "start_spray"  # بدء الرش
    STOP_SPRAY = "stop_spray"  # إيقاف الرش
    CHANGE_ALTITUDE = "change_altitude"  # تغيير الارتفاع
    ROTATE = "rotate"  # دوران
    TILT_CAMERA = "tilt_camera"  # إمالة الكاميرا


class FlightPattern(StrEnum):
    """Flight path pattern - نمط مسار الطيران"""

    PARALLEL = "parallel"  # خطوط متوازية
    CROSSHATCH = "crosshatch"  # تقاطع متعامد
    PERIMETER = "perimeter"  # محيط الحقل
    SPIRAL = "spiral"  # حلزوني
    CONTOUR = "contour"  # خطوط الكنتور (للأراضي المنحدرة)
    CUSTOM = "custom"  # مخصص


class ApplicationMode(StrEnum):
    """Application mode for spraying - وضع التطبيق للرش"""

    UNIFORM = "uniform"  # موحد (معدل ثابت)
    VARIABLE_RATE = "variable_rate"  # معدل متغير (VRA)
    SPOT_SPRAY = "spot_spray"  # رش نقطي
    PRESCRIPTION_MAP = "prescription_map"  # خريطة وصفة


class SprayStatus(StrEnum):
    """Spray system status - حالة نظام الرش"""

    IDLE = "idle"  # خامل
    PRIMING = "priming"  # تجهيز
    SPRAYING = "spraying"  # رش نشط
    PAUSED = "paused"  # متوقف مؤقتاً
    EMPTY = "empty"  # فارغ
    BLOCKED = "blocked"  # مسدود
    ERROR = "error"  # خطأ


class ImageryType(StrEnum):
    """Type of aerial imagery - نوع الصور الجوية"""

    RGB = "rgb"  # صور ملونة
    MULTISPECTRAL = "multispectral"  # متعدد الأطياف
    THERMAL = "thermal"  # حراري
    NDVI = "ndvi"  # مؤشر الغطاء النباتي
    LIDAR = "lidar"  # ليدار


class WeatherCondition(StrEnum):
    """Weather suitability for flight - ملاءمة الطقس للطيران"""

    OPTIMAL = "optimal"  # أمثل
    ACCEPTABLE = "acceptable"  # مقبول
    MARGINAL = "marginal"  # حدّي
    UNFAVORABLE = "unfavorable"  # غير ملائم
    PROHIBITED = "prohibited"  # ممنوع


class VRAZoneType(StrEnum):
    """Variable Rate Application zone type - نوع منطقة المعدل المتغير"""

    HIGH_VIGOR = "high_vigor"  # نمو قوي
    MEDIUM_VIGOR = "medium_vigor"  # نمو متوسط
    LOW_VIGOR = "low_vigor"  # نمو ضعيف
    STRESSED = "stressed"  # إجهاد
    WEED_PATCH = "weed_patch"  # بقعة أعشاب
    PEST_HOTSPOT = "pest_hotspot"  # بؤرة آفات
    BARE_SOIL = "bare_soil"  # تربة مكشوفة
    WATER_BODY = "water_body"  # مسطح مائي (استبعاد)
    EXCLUSION = "exclusion"  # منطقة استبعاد


# ==============================================================================
# Base Data Classes - فئات البيانات الأساسية
# ==============================================================================


@dataclass
class Coordinate:
    """Geographic coordinate with altitude - إحداثي جغرافي مع ارتفاع"""

    lat: float  # خط العرض
    lng: float  # خط الطول
    alt_m: float | None = None  # الارتفاع (متر)
    alt_agl_m: float | None = None  # الارتفاع فوق الأرض (متر)

    def to_tuple(self) -> tuple[float, float]:
        """Return (lat, lng) tuple"""
        return (self.lat, self.lng)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {"lat": self.lat, "lng": self.lng}
        if self.alt_m is not None:
            result["alt_m"] = self.alt_m
        if self.alt_agl_m is not None:
            result["alt_agl_m"] = self.alt_agl_m
        return result


@dataclass
class GeoBoundingBox:
    """Geographic bounding box for a region - مربع الحدود الجغرافية لمنطقة"""

    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float

    def center(self) -> Coordinate:
        """Get center coordinate"""
        return Coordinate(
            lat=(self.min_lat + self.max_lat) / 2, lng=(self.min_lng + self.max_lng) / 2
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "min_lat": self.min_lat,
            "max_lat": self.max_lat,
            "min_lng": self.min_lng,
            "max_lng": self.max_lng,
        }


# Backward-compatible alias
BoundingBox = GeoBoundingBox


# ==============================================================================
# Drone and Equipment Models - نماذج الطائرات والمعدات
# ==============================================================================


@dataclass
class DroneSpecs:
    """Drone specifications - مواصفات الطائرة"""

    drone_type: DroneType
    model_name: str
    model_name_ar: str

    # Physical specs - المواصفات الفيزيائية
    max_takeoff_weight_kg: float  # أقصى وزن إقلاع (كجم)
    empty_weight_kg: float  # الوزن الفارغ (كجم)
    max_payload_kg: float  # أقصى حمولة (كجم)

    # Performance - الأداء
    max_flight_time_min: int  # أقصى وقت طيران (دقيقة)
    max_speed_ms: float  # أقصى سرعة (م/ث)
    max_wind_speed_ms: float  # أقصى سرعة رياح للعمل (م/ث)
    max_altitude_m: float  # أقصى ارتفاع (متر)
    operating_temp_min_c: float  # أدنى درجة حرارة تشغيل
    operating_temp_max_c: float  # أقصى درجة حرارة تشغيل

    # Spray system (if applicable) - نظام الرش
    has_spray_system: bool = False
    tank_capacity_l: float | None = None  # سعة الخزان (لتر)
    spray_width_m: float | None = None  # عرض الرش (متر)
    flow_rate_l_min: float | None = None  # معدل التدفق (لتر/دقيقة)
    nozzle_count: int | None = None  # عدد الفوهات

    # Camera specs - مواصفات الكاميرا
    has_rgb_camera: bool = True
    has_multispectral: bool = False
    has_thermal: bool = False
    camera_resolution_mp: float | None = None  # دقة الكاميرا (ميجابكسل)

    # RTK support - دعم RTK
    has_rtk: bool = False
    rtk_accuracy_cm: float | None = None  # دقة RTK (سم)

    # Protocol support - دعم البروتوكولات
    protocol: str = "dji"  # dji, mavlink, custom


@dataclass
class Drone:
    """Drone asset - أصل الطائرة"""

    id: str
    tenant_id: str
    serial_number: str

    name: str
    name_ar: str

    specs: DroneSpecs
    status: str = "available"  # available, in_flight, maintenance, retired

    # Registration
    registration_number: str | None = None  # رقم التسجيل
    registration_expiry: datetime | None = None

    # Maintenance - الصيانة
    total_flight_hours: float = 0.0  # إجمالي ساعات الطيران
    total_flight_cycles: int = 0  # إجمالي دورات الطيران
    last_maintenance_date: datetime | None = None
    next_maintenance_due: datetime | None = None

    # Current state
    battery_percent: float | None = None
    firmware_version: str | None = None
    last_location: Coordinate | None = None
    last_seen: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "serial_number": self.serial_number,
            "name": self.name,
            "name_ar": self.name_ar,
            "drone_type": self.specs.drone_type.value,
            "model_name": self.specs.model_name,
            "status": self.status,
            "total_flight_hours": self.total_flight_hours,
            "battery_percent": self.battery_percent,
            "last_location": self.last_location.to_dict() if self.last_location else None,
        }


# ==============================================================================
# Waypoint and Flight Path Models - نماذج نقاط المسار ومسار الطيران
# ==============================================================================


@dataclass
class Waypoint:
    """Single waypoint in a flight path - نقطة مسار واحدة في مسار الطيران"""

    index: int  # ترتيب النقطة
    coordinate: Coordinate  # الإحداثيات

    # Navigation - الملاحة
    speed_ms: float | None = None  # السرعة عند هذه النقطة (م/ث)
    heading_deg: float | None = None  # الاتجاه (درجة)
    hover_time_s: float = 0  # وقت التحليق الثابت (ثانية)

    # Camera control - التحكم بالكاميرا
    gimbal_pitch_deg: float | None = None  # إمالة الجيمبل (درجة)
    gimbal_yaw_deg: float | None = None  # دوران الجيمبل (درجة)

    # Actions - الإجراءات
    actions: list[WaypointAction] = field(default_factory=list)
    action_params: dict[str, Any] = field(default_factory=dict)

    # Spray parameters (for spraying missions) - معاملات الرش
    spray_on: bool = False  # الرش مفعل
    spray_rate_l_ha: float | None = None  # معدل الرش (لتر/هكتار)

    # Metadata
    is_photo_point: bool = False  # نقطة تصوير
    is_turn_point: bool = False  # نقطة انعطاف
    segment_id: str | None = None  # معرف القطاع

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "index": self.index,
            "lat": self.coordinate.lat,
            "lng": self.coordinate.lng,
            "alt_agl_m": self.coordinate.alt_agl_m,
            "speed_ms": self.speed_ms,
            "heading_deg": self.heading_deg,
            "hover_time_s": self.hover_time_s,
            "actions": [a.value for a in self.actions],
            "spray_on": self.spray_on,
            "spray_rate_l_ha": self.spray_rate_l_ha,
        }


@dataclass
class FlightPath:
    """Complete flight path with waypoints - مسار الطيران الكامل مع نقاط المسار"""

    id: str
    name: str
    name_ar: str

    waypoints: list[Waypoint]
    pattern: FlightPattern

    # Path parameters - معاملات المسار
    total_distance_m: float  # المسافة الإجمالية (متر)
    estimated_duration_min: float  # المدة المقدرة (دقيقة)
    cruise_altitude_m: float  # ارتفاع الطيران (متر)
    cruise_speed_ms: float  # سرعة الطيران (م/ث)

    # Coverage - التغطية
    swath_width_m: float  # عرض المسار (متر)
    overlap_percent: float = 0  # نسبة التداخل (للتصوير)
    sidelap_percent: float = 0  # نسبة التداخل الجانبي

    # Area
    coverage_area_ha: float = 0  # المساحة المغطاة (هكتار)
    effective_area_ha: float = 0  # المساحة الفعالة (هكتار)

    # Safety - السلامة
    home_location: Coordinate | None = None  # موقع المنزل
    safe_altitude_m: float = 30  # ارتفاع آمن للعودة (متر)

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "pattern": self.pattern.value,
            "waypoint_count": len(self.waypoints),
            "total_distance_m": self.total_distance_m,
            "estimated_duration_min": self.estimated_duration_min,
            "cruise_altitude_m": self.cruise_altitude_m,
            "coverage_area_ha": self.coverage_area_ha,
            "waypoints": [wp.to_dict() for wp in self.waypoints],
        }

    def to_kml(self) -> str:
        """Export path to KML format"""
        coords = "\n".join(
            f"          {wp.coordinate.lng},{wp.coordinate.lat},{wp.coordinate.alt_agl_m or 0}"
            for wp in self.waypoints
        )
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{self.name}</name>
    <description>{self.name_ar}</description>
    <Placemark>
      <name>Flight Path</name>
      <LineString>
        <altitudeMode>relativeToGround</altitudeMode>
        <coordinates>
{coords}
        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>"""

    def to_mavlink_mission(self) -> list[dict]:
        """Export to MAVLink mission format for ArduPilot/PX4"""
        mission_items = []
        for wp in self.waypoints:
            item = {
                "seq": wp.index,
                "frame": 3,  # MAV_FRAME_GLOBAL_RELATIVE_ALT
                "command": 16,  # MAV_CMD_NAV_WAYPOINT
                "current": 1 if wp.index == 0 else 0,
                "autocontinue": 1,
                "param1": wp.hover_time_s,  # Hold time
                "param2": 0,  # Acceptance radius
                "param3": 0,  # Pass through (0 = stop)
                "param4": wp.heading_deg or 0,  # Yaw angle
                "x": wp.coordinate.lat,
                "y": wp.coordinate.lng,
                "z": wp.coordinate.alt_agl_m or self.cruise_altitude_m,
            }
            mission_items.append(item)
        return mission_items


# ==============================================================================
# Mission Models - نماذج المهام
# ==============================================================================


@dataclass
class WeatherCheck:
    """Weather conditions check for flight - فحص ظروف الطقس للطيران"""

    check_time: datetime
    condition: WeatherCondition

    # Parameters - المعاملات
    temperature_c: float  # درجة الحرارة
    humidity_percent: float  # الرطوبة
    wind_speed_ms: float  # سرعة الرياح (م/ث)
    wind_direction_deg: float  # اتجاه الرياح (درجة)
    wind_gust_ms: float | None = None  # هبات الرياح

    # Precipitation - الهطول
    precipitation_mm: float = 0  # الهطول (مم)
    rain_probability_percent: float = 0  # احتمالية المطر

    # Visibility - الرؤية
    visibility_km: float = 10  # الرؤية (كم)
    cloud_cover_percent: float = 0  # الغطاء السحابي

    # Assessment - التقييم
    can_fly: bool = True
    message_en: str = ""
    message_ar: str = ""
    warnings_en: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "check_time": self.check_time.isoformat(),
            "condition": self.condition.value,
            "temperature_c": self.temperature_c,
            "humidity_percent": self.humidity_percent,
            "wind_speed_ms": self.wind_speed_ms,
            "can_fly": self.can_fly,
            "message_en": self.message_en,
            "message_ar": self.message_ar,
        }


@dataclass
class SprayMission:
    """Spraying mission definition - تعريف مهمة الرش"""

    id: str
    tenant_id: str
    field_id: str

    name: str
    name_ar: str

    # Status
    status: MissionStatus = MissionStatus.DRAFT

    # Product information - معلومات المنتج
    product_id: str = ""  # معرف المنتج (مبيد/سماد)
    product_name: str = ""
    product_name_ar: str = ""
    product_type: str = ""  # pesticide, fertilizer, growth_regulator

    # Application parameters - معاملات التطبيق
    application_mode: ApplicationMode = ApplicationMode.UNIFORM
    target_rate_l_ha: float = 0  # المعدل المستهدف (لتر/هكتار)
    min_rate_l_ha: float | None = None  # الحد الأدنى للمعدل
    max_rate_l_ha: float | None = None  # الحد الأقصى للمعدل
    concentration_percent: float | None = None  # التركيز (%)

    # Total application - إجمالي التطبيق
    total_area_ha: float = 0  # المساحة الإجمالية (هكتار)
    total_volume_l: float = 0  # الحجم الإجمالي (لتر)
    estimated_tank_fills: int = 1  # عدد تعبئات الخزان

    # Flight parameters - معاملات الطيران
    flight_altitude_m: float = 3  # ارتفاع الطيران (متر)
    flight_speed_ms: float = 5  # سرعة الطيران (م/ث)
    swath_width_m: float = 5  # عرض الرش (متر)

    # VRA settings (if applicable) - إعدادات المعدل المتغير
    prescription_map_id: str | None = None
    vra_zones: list[VRAZone] = field(default_factory=list)

    # Safety - السلامة
    buffer_zone_m: float = 10  # المنطقة العازلة (متر)
    exclusion_zones: list[list[Coordinate]] = field(default_factory=list)
    wind_limit_ms: float = 6  # حد الرياح (م/ث)

    # Scheduling - الجدولة
    scheduled_date: datetime | None = None
    scheduled_time_start: str | None = None  # e.g., "06:00"
    scheduled_time_end: str | None = None  # e.g., "10:00"

    # Assigned resources - الموارد المخصصة
    drone_id: str | None = None
    pilot_id: str | None = None
    pilot_name: str | None = None

    # Compliance - الامتثال
    phi_days: int | None = None  # فترة ما قبل الحصاد
    rei_hours: int | None = None  # فترة إعادة الدخول
    compliance_checked: bool = False

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "status": self.status.value,
            "product_name": self.product_name,
            "application_mode": self.application_mode.value,
            "target_rate_l_ha": self.target_rate_l_ha,
            "total_area_ha": self.total_area_ha,
            "total_volume_l": self.total_volume_l,
            "flight_altitude_m": self.flight_altitude_m,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "drone_id": self.drone_id,
        }


@dataclass
class MappingMission:
    """Aerial mapping mission definition - تعريف مهمة رسم الخرائط الجوية"""

    id: str
    tenant_id: str
    field_id: str

    name: str
    name_ar: str

    # Status
    status: MissionStatus = MissionStatus.DRAFT

    # Imagery type - نوع الصور
    imagery_types: list[ImageryType] = field(default_factory=lambda: [ImageryType.RGB])

    # Flight parameters - معاملات الطيران
    flight_altitude_m: float = 50  # ارتفاع الطيران (متر)
    flight_speed_ms: float = 8  # سرعة الطيران (م/ث)
    gsd_cm_px: float = 2  # دقة الأرض (سم/بكسل)

    # Overlap settings - إعدادات التداخل
    frontal_overlap_percent: float = 80  # التداخل الأمامي (%)
    side_overlap_percent: float = 70  # التداخل الجانبي (%)

    # Pattern - النمط
    pattern: FlightPattern = FlightPattern.PARALLEL
    heading_deg: float | None = None  # اتجاه خطوط الطيران

    # Coverage - التغطية
    total_area_ha: float = 0
    estimated_photos: int = 0
    estimated_flight_time_min: float = 0

    # Processing - المعالجة
    generate_orthomosaic: bool = True  # إنشاء فسيفساء
    generate_dsm: bool = False  # إنشاء نموذج سطح رقمي
    generate_ndvi: bool = False  # إنشاء خريطة NDVI

    # Scheduling - الجدولة
    scheduled_date: datetime | None = None
    optimal_time_window_en: str = ""  # e.g., "10:00-14:00 for minimal shadows"
    optimal_time_window_ar: str = ""

    # Assigned resources
    drone_id: str | None = None
    pilot_id: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "status": self.status.value,
            "imagery_types": [t.value for t in self.imagery_types],
            "flight_altitude_m": self.flight_altitude_m,
            "gsd_cm_px": self.gsd_cm_px,
            "frontal_overlap_percent": self.frontal_overlap_percent,
            "side_overlap_percent": self.side_overlap_percent,
            "total_area_ha": self.total_area_ha,
            "estimated_photos": self.estimated_photos,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
        }


# ==============================================================================
# Flight Log Models - نماذج سجل الطيران
# ==============================================================================


@dataclass
class FlightTelemetry:
    """Real-time flight telemetry data - بيانات القياس عن بعد للطيران"""

    timestamp: datetime
    position: Coordinate

    # Attitude - وضعية الطائرة
    roll_deg: float = 0
    pitch_deg: float = 0
    yaw_deg: float = 0

    # Velocity - السرعة
    ground_speed_ms: float = 0
    vertical_speed_ms: float = 0
    heading_deg: float = 0

    # System status - حالة النظام
    battery_percent: float = 100
    battery_voltage: float = 0
    battery_current: float = 0
    battery_temperature_c: float | None = None

    # GPS - نظام تحديد المواقع
    gps_satellites: int = 0
    gps_hdop: float = 0
    rtk_fix: bool = False

    # Spray status (if applicable) - حالة الرش
    spray_status: SprayStatus = SprayStatus.IDLE
    tank_level_percent: float | None = None
    flow_rate_l_min: float | None = None
    total_sprayed_l: float = 0

    # RC signal - إشارة التحكم
    rc_signal_percent: float | None = None
    home_distance_m: float = 0

    # Warnings - التحذيرات
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "lat": self.position.lat,
            "lng": self.position.lng,
            "alt_agl_m": self.position.alt_agl_m,
            "ground_speed_ms": self.ground_speed_ms,
            "heading_deg": self.heading_deg,
            "battery_percent": self.battery_percent,
            "spray_status": self.spray_status.value,
            "tank_level_percent": self.tank_level_percent,
            "total_sprayed_l": self.total_sprayed_l,
        }


@dataclass
class FlightLog:
    """Complete flight log record - سجل الرحلة الكامل"""

    id: str
    tenant_id: str
    drone_id: str
    mission_id: str | None = None
    mission_type: FlightMode | None = None

    # Flight status
    status: FlightStatus = FlightStatus.PLANNED

    # Timing - التوقيت
    planned_start: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    duration_min: float = 0

    # Location - الموقع
    field_id: str | None = None
    takeoff_location: Coordinate | None = None
    landing_location: Coordinate | None = None

    # Flight stats - إحصائيات الطيران
    max_altitude_m: float = 0
    max_speed_ms: float = 0
    total_distance_m: float = 0
    covered_area_ha: float = 0

    # Spray stats (if applicable) - إحصائيات الرش
    total_sprayed_l: float = 0
    avg_spray_rate_l_ha: float = 0
    tank_fills: int = 0

    # Battery - البطارية
    start_battery_percent: float | None = None
    end_battery_percent: float | None = None
    battery_consumed_wh: float | None = None

    # Telemetry - القياس عن بعد
    telemetry_log: list[FlightTelemetry] = field(default_factory=list)
    telemetry_interval_s: float = 1  # Recording interval

    # Photos - الصور
    photos_taken: int = 0
    photo_ids: list[str] = field(default_factory=list)

    # Pilot - الطيار
    pilot_id: str = ""
    pilot_name: str = ""

    # Weather at time of flight - الطقس وقت الطيران
    weather_at_start: WeatherCheck | None = None
    weather_at_end: WeatherCheck | None = None

    # Issues and notes - المشاكل والملاحظات
    issues: list[str] = field(default_factory=list)
    issues_ar: list[str] = field(default_factory=list)
    abort_reason: str | None = None
    abort_reason_ar: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "drone_id": self.drone_id,
            "mission_id": self.mission_id,
            "mission_type": self.mission_type.value if self.mission_type else None,
            "status": self.status.value,
            "actual_start": self.actual_start.isoformat() if self.actual_start else None,
            "actual_end": self.actual_end.isoformat() if self.actual_end else None,
            "duration_min": self.duration_min,
            "total_distance_m": self.total_distance_m,
            "covered_area_ha": self.covered_area_ha,
            "total_sprayed_l": self.total_sprayed_l,
            "photos_taken": self.photos_taken,
            "pilot_name": self.pilot_name,
        }

    def get_track_geojson(self) -> dict:
        """Export flight track as GeoJSON"""
        coordinates = [
            [t.position.lng, t.position.lat, t.position.alt_agl_m or 0] for t in self.telemetry_log
        ]
        return {
            "type": "Feature",
            "properties": {
                "flight_id": self.id,
                "drone_id": self.drone_id,
                "duration_min": self.duration_min,
                "total_distance_m": self.total_distance_m,
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates,
            },
        }


# ==============================================================================
# Variable Rate Application Models - نماذج التطبيق بالمعدل المتغير
# ==============================================================================


@dataclass
class VRAZone:
    """Variable Rate Application zone - منطقة التطبيق بالمعدل المتغير"""

    id: str
    zone_type: VRAZoneType

    # Geometry - الشكل الهندسي
    boundary: list[Coordinate]  # Polygon boundary
    area_ha: float = 0  # مساحة المنطقة (هكتار)
    centroid: Coordinate | None = None

    # Application rate - معدل التطبيق
    rate_l_ha: float = 0  # معدل التطبيق (لتر/هكتار)
    rate_percent: float = 100  # نسبة من المعدل الأساسي (%)

    # Source data - البيانات المصدر
    ndvi_mean: float | None = None
    ndvi_std: float | None = None
    lai_mean: float | None = None
    source_imagery_id: str | None = None
    source_date: datetime | None = None

    # Labels - التسميات
    label_en: str = ""
    label_ar: str = ""
    recommendation_en: str = ""
    recommendation_ar: str = ""

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "zone_type": self.zone_type.value,
            "area_ha": self.area_ha,
            "rate_l_ha": self.rate_l_ha,
            "rate_percent": self.rate_percent,
            "ndvi_mean": self.ndvi_mean,
            "label_en": self.label_en,
            "label_ar": self.label_ar,
            "boundary": [c.to_dict() for c in self.boundary],
        }

    def to_geojson(self) -> dict:
        """Export zone as GeoJSON Feature"""
        return {
            "type": "Feature",
            "properties": {
                "id": self.id,
                "zone_type": self.zone_type.value,
                "area_ha": self.area_ha,
                "rate_l_ha": self.rate_l_ha,
                "rate_percent": self.rate_percent,
                "ndvi_mean": self.ndvi_mean,
                "label_en": self.label_en,
                "label_ar": self.label_ar,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[c.lng, c.lat] for c in self.boundary]],
            },
        }


@dataclass
class PrescriptionMap:
    """Variable Rate Application prescription map - خريطة وصفة المعدل المتغير"""

    id: str
    tenant_id: str
    field_id: str

    name: str
    name_ar: str

    # Map parameters - معاملات الخريطة
    zones: list[VRAZone]
    total_area_ha: float = 0

    # Base application parameters - معاملات التطبيق الأساسية
    base_rate_l_ha: float = 0  # المعدل الأساسي
    product_id: str | None = None
    product_name: str = ""
    product_name_ar: str = ""

    # Source data - البيانات المصدر
    source_type: str = "ndvi"  # ndvi, lai, yield, manual, soil
    source_imagery_id: str | None = None
    source_date: datetime | None = None

    # Classification - التصنيف
    zone_count: int = 5  # عدد المناطق
    classification_method: str = "quantile"  # quantile, equal_interval, jenks

    # Statistics - الإحصائيات
    min_rate_l_ha: float = 0
    max_rate_l_ha: float = 0
    avg_rate_l_ha: float = 0
    total_volume_l: float = 0

    # Validation - التحقق
    validated: bool = False
    validated_by: str | None = None
    validated_at: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "zone_count": len(self.zones),
            "total_area_ha": self.total_area_ha,
            "base_rate_l_ha": self.base_rate_l_ha,
            "product_name": self.product_name,
            "source_type": self.source_type,
            "min_rate_l_ha": self.min_rate_l_ha,
            "max_rate_l_ha": self.max_rate_l_ha,
            "avg_rate_l_ha": self.avg_rate_l_ha,
            "total_volume_l": self.total_volume_l,
            "validated": self.validated,
        }

    def to_geojson(self) -> dict:
        """Export prescription map as GeoJSON FeatureCollection"""
        features = [zone.to_geojson() for zone in self.zones]
        return {
            "type": "FeatureCollection",
            "properties": {
                "id": self.id,
                "name": self.name,
                "name_ar": self.name_ar,
                "field_id": self.field_id,
                "base_rate_l_ha": self.base_rate_l_ha,
                "total_area_ha": self.total_area_ha,
            },
            "features": features,
        }


# ==============================================================================
# Imagery Processing Models - نماذج معالجة الصور
# ==============================================================================


@dataclass
class AerialImage:
    """Single aerial image record - سجل صورة جوية واحدة"""

    id: str
    flight_id: str
    sequence: int

    # Location - الموقع
    capture_time: datetime
    position: Coordinate
    gimbal_pitch_deg: float = -90  # إمالة الكاميرا
    gimbal_yaw_deg: float = 0

    # Image properties - خصائص الصورة
    imagery_type: ImageryType = ImageryType.RGB
    file_path: str = ""
    file_size_bytes: int = 0
    width_px: int = 0
    height_px: int = 0
    gsd_cm_px: float = 0  # دقة الأرض

    # Exposure - التعريض
    iso: int | None = None
    shutter_speed: str | None = None
    aperture: float | None = None
    exposure_compensation: float | None = None

    # Multispectral bands (if applicable) - النطاقات الطيفية
    bands: list[str] = field(default_factory=list)  # e.g., ["red", "green", "nir", "rededge"]

    # Georeference - المرجعية الجغرافية
    has_rtk_geotag: bool = False
    footprint: list[Coordinate] = field(default_factory=list)  # Image footprint polygon

    # Quality - الجودة
    blur_score: float | None = None  # 0-1, higher is sharper
    exposure_quality: str | None = None  # underexposed, optimal, overexposed

    # Processing - المعالجة
    processed: bool = False
    orthomosaic_id: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "flight_id": self.flight_id,
            "sequence": self.sequence,
            "capture_time": self.capture_time.isoformat(),
            "lat": self.position.lat,
            "lng": self.position.lng,
            "alt_agl_m": self.position.alt_agl_m,
            "imagery_type": self.imagery_type.value,
            "gsd_cm_px": self.gsd_cm_px,
            "width_px": self.width_px,
            "height_px": self.height_px,
        }


@dataclass
class ProcessedImagery:
    """Processed imagery product - منتج صور معالجة"""

    id: str
    tenant_id: str
    field_id: str
    flight_id: str

    name: str
    name_ar: str

    # Type - النوع
    product_type: str  # orthomosaic, dsm, ndvi, lai, thermal
    imagery_type: ImageryType

    # Source - المصدر
    source_image_count: int = 0
    processing_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    processing_software: str = ""

    # Coverage - التغطية
    coverage_area_ha: float = 0
    bounding_box: BoundingBox | None = None
    gsd_cm_px: float = 0

    # Files - الملفات
    file_path: str = ""
    file_format: str = "geotiff"  # geotiff, cog, png
    file_size_mb: float = 0
    thumbnail_path: str | None = None

    # Statistics (for index maps) - الإحصائيات
    min_value: float | None = None
    max_value: float | None = None
    mean_value: float | None = None
    std_value: float | None = None

    # Quality - الجودة
    quality_score: float | None = None  # 0-1
    georef_accuracy_cm: float | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "flight_id": self.flight_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "product_type": self.product_type,
            "imagery_type": self.imagery_type.value,
            "processing_date": self.processing_date.isoformat(),
            "coverage_area_ha": self.coverage_area_ha,
            "gsd_cm_px": self.gsd_cm_px,
            "mean_value": self.mean_value,
        }


# ==============================================================================
# Helper Functions - دوال مساعدة
# ==============================================================================


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())[:12]
    return f"{prefix}_{unique_id}" if prefix else unique_id
