"""
SAHOOL Equipment Maintenance Models - نماذج صيانة المعدات

Data models for equipment maintenance management including:
- Equipment assets (tractors, harvesters, irrigation systems, sprayers)
- Maintenance schedules and tasks
- Spare parts inventory
- Service history logging
- Maintenance alerts

Version: 1.0.0
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

# ==============================================================================
# Enumerations - التعدادات
# ==============================================================================


class EquipmentType(StrEnum):
    """Type of agricultural equipment - نوع المعدات الزراعية"""

    TRACTOR = "tractor"  # جرار
    HARVESTER = "harvester"  # حصادة
    IRRIGATION_SYSTEM = "irrigation_system"  # نظام ري
    SPRAYER = "sprayer"  # رشاشة
    SEEDER = "seeder"  # بذارة
    PLOW = "plow"  # محراث
    CULTIVATOR = "cultivator"  # مزرعة
    TRAILER = "trailer"  # مقطورة
    PUMP = "pump"  # مضخة
    GENERATOR = "generator"  # مولد كهربائي
    DRONE = "drone"  # طائرة بدون طيار
    OTHER = "other"  # أخرى


class EquipmentStatus(StrEnum):
    """Equipment operational status - حالة تشغيل المعدات"""

    OPERATIONAL = "operational"  # تعمل
    IN_USE = "in_use"  # قيد الاستخدام
    IDLE = "idle"  # خاملة
    UNDER_MAINTENANCE = "under_maintenance"  # تحت الصيانة
    AWAITING_PARTS = "awaiting_parts"  # بانتظار قطع الغيار
    BROKEN_DOWN = "broken_down"  # معطلة
    DECOMMISSIONED = "decommissioned"  # خارج الخدمة


class MaintenanceType(StrEnum):
    """Type of maintenance - نوع الصيانة"""

    PREVENTIVE = "preventive"  # صيانة وقائية
    CORRECTIVE = "corrective"  # صيانة تصحيحية
    PREDICTIVE = "predictive"  # صيانة تنبؤية
    EMERGENCY = "emergency"  # صيانة طارئة
    SCHEDULED = "scheduled"  # صيانة مجدولة
    OVERHAUL = "overhaul"  # إصلاح شامل


class MaintenanceStatus(StrEnum):
    """Maintenance task status - حالة مهمة الصيانة"""

    SCHEDULED = "scheduled"  # مجدولة
    PENDING = "pending"  # معلقة
    IN_PROGRESS = "in_progress"  # قيد التنفيذ
    COMPLETED = "completed"  # مكتملة
    CANCELLED = "cancelled"  # ملغاة
    OVERDUE = "overdue"  # متأخرة


class MaintenancePriority(StrEnum):
    """Maintenance priority level - مستوى أولوية الصيانة"""

    LOW = "low"  # منخفضة
    MEDIUM = "medium"  # متوسطة
    HIGH = "high"  # عالية
    CRITICAL = "critical"  # حرجة
    EMERGENCY = "emergency"  # طارئة


class PartCategory(StrEnum):
    """Spare part category - فئة قطع الغيار"""

    ENGINE = "engine"  # محرك
    TRANSMISSION = "transmission"  # ناقل الحركة
    HYDRAULICS = "hydraulics"  # نظام هيدروليكي
    ELECTRICAL = "electrical"  # نظام كهربائي
    FILTERS = "filters"  # فلاتر
    BELTS = "belts"  # أحزمة
    TIRES = "tires"  # إطارات
    BLADES = "blades"  # شفرات
    NOZZLES = "nozzles"  # فوهات
    PUMPS = "pumps"  # مضخات
    BEARINGS = "bearings"  # محامل
    SEALS = "seals"  # موانع تسرب
    LUBRICANTS = "lubricants"  # زيوت ومواد تشحيم
    IRRIGATION = "irrigation"  # مكونات الري
    OTHER = "other"  # أخرى


class AlertSeverity(StrEnum):
    """Alert severity level - مستوى خطورة التنبيه"""

    INFO = "info"  # معلومات
    WARNING = "warning"  # تحذير
    CRITICAL = "critical"  # حرج
    EMERGENCY = "emergency"  # طارئ


class AlertType(StrEnum):
    """Type of maintenance alert - نوع تنبيه الصيانة"""

    SCHEDULED_DUE = "scheduled_due"  # صيانة مجدولة مستحقة
    OVERDUE = "overdue"  # صيانة متأخرة
    HOURS_THRESHOLD = "hours_threshold"  # عتبة ساعات التشغيل
    BREAKDOWN = "breakdown"  # عطل
    LOW_STOCK = "low_stock"  # مخزون منخفض
    PART_NEEDED = "part_needed"  # قطعة غيار مطلوبة
    PREDICTIVE_WARNING = "predictive_warning"  # تحذير تنبؤي
    WARRANTY_EXPIRY = "warranty_expiry"  # انتهاء الضمان
    INSPECTION_DUE = "inspection_due"  # فحص مستحق


class FuelType(StrEnum):
    """Fuel type for equipment - نوع الوقود"""

    DIESEL = "diesel"  # ديزل
    GASOLINE = "gasoline"  # بنزين
    ELECTRIC = "electric"  # كهربائي
    HYBRID = "hybrid"  # هجين
    LPG = "lpg"  # غاز البترول المسال
    SOLAR = "solar"  # طاقة شمسية
    NONE = "none"  # لا يوجد


class IrrigationType(StrEnum):
    """Type of irrigation system - نوع نظام الري"""

    DRIP = "drip"  # تنقيط
    SPRINKLER = "sprinkler"  # رشاش
    CENTER_PIVOT = "center_pivot"  # محوري مركزي
    LINEAR = "linear"  # خطي
    SURFACE = "surface"  # سطحي
    SUBSURFACE = "subsurface"  # تحت السطح
    FLOOD = "flood"  # غمر


# ==============================================================================
# Equipment Models - نماذج المعدات
# ==============================================================================


@dataclass
class EquipmentSpecs:
    """Equipment specifications - مواصفات المعدات"""

    manufacturer: str  # الشركة المصنعة
    model: str  # الموديل
    year: int  # سنة الصنع
    serial_number: str  # الرقم التسلسلي

    # Power specifications - مواصفات الطاقة
    engine_power_hp: float | None = None  # قوة المحرك (حصان)
    engine_power_kw: float | None = None  # قوة المحرك (كيلوواط)
    fuel_type: FuelType = FuelType.DIESEL
    fuel_capacity_l: float | None = None  # سعة خزان الوقود (لتر)
    fuel_consumption_l_hr: float | None = None  # استهلاك الوقود (لتر/ساعة)

    # Physical specifications - المواصفات الفيزيائية
    weight_kg: float | None = None  # الوزن (كجم)
    length_m: float | None = None  # الطول (متر)
    width_m: float | None = None  # العرض (متر)
    height_m: float | None = None  # الارتفاع (متر)

    # Capacity - السعة
    working_width_m: float | None = None  # عرض العمل (متر)
    tank_capacity_l: float | None = None  # سعة الخزان (لتر)
    hopper_capacity_kg: float | None = None  # سعة القادوس (كجم)

    # Irrigation specific - خاص بالري
    irrigation_type: IrrigationType | None = None
    flow_rate_m3_hr: float | None = None  # معدل التدفق (م³/ساعة)
    coverage_area_ha: float | None = None  # مساحة التغطية (هكتار)
    pressure_bar: float | None = None  # الضغط (بار)

    # Service intervals - فترات الخدمة
    oil_change_hours: int = 250  # ساعات تغيير الزيت
    filter_change_hours: int = 500  # ساعات تغيير الفلتر
    major_service_hours: int = 1000  # ساعات الخدمة الرئيسية
    overhaul_hours: int = 5000  # ساعات الإصلاح الشامل

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "manufacturer": self.manufacturer,
            "model": self.model,
            "year": self.year,
            "serial_number": self.serial_number,
            "engine_power_hp": self.engine_power_hp,
            "fuel_type": self.fuel_type.value,
            "fuel_capacity_l": self.fuel_capacity_l,
            "weight_kg": self.weight_kg,
            "working_width_m": self.working_width_m,
            "irrigation_type": self.irrigation_type.value if self.irrigation_type else None,
            "service_intervals": {
                "oil_change_hours": self.oil_change_hours,
                "filter_change_hours": self.filter_change_hours,
                "major_service_hours": self.major_service_hours,
                "overhaul_hours": self.overhaul_hours,
            },
        }


@dataclass
class Equipment:
    """
    Agricultural equipment asset - أصل المعدات الزراعية
    """

    id: str
    tenant_id: str
    farm_id: str

    # Basic info - المعلومات الأساسية
    name: str
    name_ar: str
    equipment_type: EquipmentType
    specs: EquipmentSpecs

    # Status - الحالة
    status: EquipmentStatus = EquipmentStatus.OPERATIONAL
    location: str | None = None  # Current location
    location_ar: str | None = None
    assigned_field_id: str | None = None

    # Usage tracking - تتبع الاستخدام
    total_hours: float = 0.0  # إجمالي ساعات التشغيل
    total_kilometers: float = 0.0  # إجمالي الكيلومترات (للجرارات)
    total_hectares: float = 0.0  # إجمالي الهكتارات المعالجة
    last_usage_date: datetime | None = None

    # Maintenance tracking - تتبع الصيانة
    hours_since_last_oil_change: float = 0.0
    hours_since_last_filter_change: float = 0.0
    hours_since_last_major_service: float = 0.0
    hours_since_last_overhaul: float = 0.0
    last_maintenance_date: datetime | None = None
    next_maintenance_date: datetime | None = None
    next_maintenance_type: str | None = None
    next_maintenance_type_ar: str | None = None

    # Purchase and warranty - الشراء والضمان
    purchase_date: datetime | None = None
    purchase_price: Decimal | None = None
    purchase_currency: str = "SAR"
    warranty_expiry: datetime | None = None
    insurance_expiry: datetime | None = None
    registration_number: str | None = None

    # Telematics - القياس عن بعد
    has_telematics: bool = False
    telematics_device_id: str | None = None
    last_telemetry_at: datetime | None = None
    fuel_level_percent: float | None = None
    current_lat: float | None = None
    current_lng: float | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    notes: str = ""
    notes_ar: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "equipment_type": self.equipment_type.value,
            "status": self.status.value,
            "specs": self.specs.to_dict(),
            "total_hours": self.total_hours,
            "total_kilometers": self.total_kilometers,
            "total_hectares": self.total_hectares,
            "last_maintenance_date": self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            "next_maintenance_date": self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            "is_active": self.is_active,
            "location": {
                "lat": self.current_lat,
                "lng": self.current_lng,
            }
            if self.current_lat and self.current_lng
            else None,
        }

    def get_maintenance_due_status(self) -> dict:
        """
        Get maintenance due status for all service types
        إرجاع حالة استحقاق الصيانة لجميع أنواع الخدمة
        """
        return {
            "oil_change": {
                "hours_remaining": self.specs.oil_change_hours - self.hours_since_last_oil_change,
                "percent_used": (self.hours_since_last_oil_change / self.specs.oil_change_hours) * 100,
                "is_due": self.hours_since_last_oil_change >= self.specs.oil_change_hours,
                "is_approaching": self.hours_since_last_oil_change >= self.specs.oil_change_hours * 0.9,
            },
            "filter_change": {
                "hours_remaining": self.specs.filter_change_hours - self.hours_since_last_filter_change,
                "percent_used": (self.hours_since_last_filter_change / self.specs.filter_change_hours) * 100,
                "is_due": self.hours_since_last_filter_change >= self.specs.filter_change_hours,
                "is_approaching": self.hours_since_last_filter_change >= self.specs.filter_change_hours * 0.9,
            },
            "major_service": {
                "hours_remaining": self.specs.major_service_hours - self.hours_since_last_major_service,
                "percent_used": (self.hours_since_last_major_service / self.specs.major_service_hours) * 100,
                "is_due": self.hours_since_last_major_service >= self.specs.major_service_hours,
                "is_approaching": self.hours_since_last_major_service >= self.specs.major_service_hours * 0.9,
            },
            "overhaul": {
                "hours_remaining": self.specs.overhaul_hours - self.hours_since_last_overhaul,
                "percent_used": (self.hours_since_last_overhaul / self.specs.overhaul_hours) * 100,
                "is_due": self.hours_since_last_overhaul >= self.specs.overhaul_hours,
                "is_approaching": self.hours_since_last_overhaul >= self.specs.overhaul_hours * 0.9,
            },
        }


# ==============================================================================
# Maintenance Task Models - نماذج مهام الصيانة
# ==============================================================================


@dataclass
class MaintenanceTask:
    """
    Individual maintenance task - مهمة صيانة فردية
    """

    id: str
    tenant_id: str
    equipment_id: str

    # Task details - تفاصيل المهمة
    title: str
    title_ar: str
    description: str = ""
    description_ar: str = ""
    maintenance_type: MaintenanceType = MaintenanceType.SCHEDULED
    priority: MaintenancePriority = MaintenancePriority.MEDIUM

    # Status tracking - تتبع الحالة
    status: MaintenanceStatus = MaintenanceStatus.SCHEDULED
    progress_percent: float = 0.0

    # Scheduling - الجدولة
    scheduled_date: datetime | None = None
    due_date: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    estimated_duration_hours: float = 1.0
    actual_duration_hours: float | None = None

    # Trigger conditions - شروط التفعيل
    triggered_by_hours: float | None = None  # Hours that triggered this task
    triggered_by_date: bool = False  # Triggered by calendar date
    triggered_by_condition: bool = False  # Triggered by detected condition

    # Assignment - التخصيص
    assigned_to: str | None = None  # Technician ID
    assigned_to_name: str | None = None
    assigned_to_name_ar: str | None = None

    # Parts required - قطع الغيار المطلوبة
    parts_required: list[MaintenancePart] = field(default_factory=list)
    parts_cost: Decimal = Decimal("0.00")
    labor_cost: Decimal = Decimal("0.00")
    total_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Work performed - العمل المنجز
    work_performed: str = ""
    work_performed_ar: str = ""
    findings: str = ""
    findings_ar: str = ""
    recommendations: str = ""
    recommendations_ar: str = ""

    # Checklist - قائمة الفحص
    checklist: list[ChecklistItem] = field(default_factory=list)

    # Documentation - التوثيق
    photos: list[str] = field(default_factory=list)  # Photo URLs
    documents: list[str] = field(default_factory=list)  # Document URLs
    technician_signature: str | None = None
    supervisor_signature: str | None = None

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
            "equipment_id": self.equipment_id,
            "title": self.title,
            "title_ar": self.title_ar,
            "maintenance_type": self.maintenance_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "progress_percent": self.progress_percent,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_duration_hours": self.estimated_duration_hours,
            "actual_duration_hours": self.actual_duration_hours,
            "assigned_to_name": self.assigned_to_name,
            "parts_required": [p.to_dict() for p in self.parts_required],
            "total_cost": str(self.total_cost),
            "currency": self.currency,
        }

    def is_overdue(self) -> bool:
        """Check if task is overdue - التحقق من التأخر"""
        if self.status in [MaintenanceStatus.COMPLETED, MaintenanceStatus.CANCELLED]:
            return False
        if self.due_date and datetime.now(UTC) > self.due_date:
            return True
        return False


@dataclass
class ChecklistItem:
    """Maintenance checklist item - عنصر قائمة الفحص"""

    id: str
    description: str
    description_ar: str
    is_completed: bool = False
    completed_at: datetime | None = None
    completed_by: str | None = None
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "description": self.description,
            "description_ar": self.description_ar,
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
        }


@dataclass
class MaintenanceSchedule:
    """
    Recurring maintenance schedule - جدول الصيانة المتكرر
    """

    id: str
    tenant_id: str
    equipment_id: str

    # Schedule details - تفاصيل الجدول
    name: str
    name_ar: str
    description: str = ""
    description_ar: str = ""
    maintenance_type: MaintenanceType = MaintenanceType.PREVENTIVE

    # Trigger conditions - شروط التفعيل
    # Hours-based - بناءً على ساعات التشغيل
    hours_interval: int | None = None  # كل X ساعة
    hours_warning_threshold: int | None = None  # التحذير قبل X ساعة

    # Calendar-based - بناءً على التقويم
    calendar_interval_days: int | None = None  # كل X يوم
    calendar_day_of_week: int | None = None  # يوم الأسبوع (0=الاثنين)
    calendar_day_of_month: int | None = None  # يوم الشهر
    calendar_month: int | None = None  # الشهر (للسنوية)

    # Season-based (agricultural) - بناءً على الموسم
    season_trigger: str | None = None  # pre_season, post_season, mid_season

    # Task template - قالب المهمة
    task_title: str = ""
    task_title_ar: str = ""
    task_description: str = ""
    task_description_ar: str = ""
    estimated_duration_hours: float = 1.0
    default_priority: MaintenancePriority = MaintenancePriority.MEDIUM
    checklist_template: list[dict] = field(default_factory=list)

    # Parts typically needed - قطع الغيار المطلوبة عادة
    typical_parts: list[PartRequirement] = field(default_factory=list)
    estimated_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Execution - التنفيذ
    last_executed_at: datetime | None = None
    last_executed_hours: float | None = None
    next_due_at: datetime | None = None
    next_due_hours: float | None = None
    execution_count: int = 0

    # Active status - حالة النشاط
    is_active: bool = True
    active_from: datetime | None = None
    active_until: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "equipment_id": self.equipment_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "maintenance_type": self.maintenance_type.value,
            "hours_interval": self.hours_interval,
            "calendar_interval_days": self.calendar_interval_days,
            "season_trigger": self.season_trigger,
            "default_priority": self.default_priority.value,
            "estimated_duration_hours": self.estimated_duration_hours,
            "estimated_cost": str(self.estimated_cost),
            "last_executed_at": self.last_executed_at.isoformat() if self.last_executed_at else None,
            "next_due_at": self.next_due_at.isoformat() if self.next_due_at else None,
            "next_due_hours": self.next_due_hours,
            "is_active": self.is_active,
        }


# ==============================================================================
# Parts Inventory Models - نماذج مخزون قطع الغيار
# ==============================================================================


@dataclass
class SparePart:
    """
    Spare part in inventory - قطعة غيار في المخزون
    """

    id: str
    tenant_id: str

    # Part identification - تعريف القطعة
    part_number: str  # رقم القطعة
    name: str
    name_ar: str
    description: str = ""
    description_ar: str = ""
    category: PartCategory = PartCategory.OTHER

    # Manufacturer info - معلومات الشركة المصنعة
    manufacturer: str = ""
    manufacturer_part_number: str | None = None
    alternative_part_numbers: list[str] = field(default_factory=list)

    # Compatible equipment - المعدات المتوافقة
    compatible_equipment_types: list[EquipmentType] = field(default_factory=list)
    compatible_models: list[str] = field(default_factory=list)  # Specific models
    universal: bool = False  # Works with all equipment

    # Inventory - المخزون
    quantity_on_hand: int = 0
    quantity_reserved: int = 0
    quantity_available: int = 0  # on_hand - reserved
    minimum_stock_level: int = 1
    reorder_level: int = 2
    reorder_quantity: int = 5
    maximum_stock_level: int = 20

    # Location - الموقع
    warehouse_location: str = ""
    warehouse_location_ar: str = ""
    bin_location: str | None = None

    # Pricing - التسعير
    unit_cost: Decimal = Decimal("0.00")
    selling_price: Decimal = Decimal("0.00")
    currency: str = "SAR"
    last_purchase_price: Decimal | None = None
    last_purchase_date: datetime | None = None

    # Supplier info - معلومات المورد
    primary_supplier_id: str | None = None
    primary_supplier_name: str | None = None
    lead_time_days: int = 7  # وقت التوريد (أيام)

    # Physical attributes - الخصائص الفيزيائية
    weight_kg: float | None = None
    dimensions: str | None = None  # L x W x H

    # Shelf life - مدة الصلاحية
    has_expiry: bool = False
    shelf_life_months: int | None = None
    expiry_date: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    barcode: str | None = None
    qr_code: str | None = None
    image_url: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "part_number": self.part_number,
            "name": self.name,
            "name_ar": self.name_ar,
            "category": self.category.value,
            "manufacturer": self.manufacturer,
            "quantity_on_hand": self.quantity_on_hand,
            "quantity_available": self.quantity_available,
            "minimum_stock_level": self.minimum_stock_level,
            "reorder_level": self.reorder_level,
            "unit_cost": str(self.unit_cost),
            "is_low_stock": self.is_low_stock(),
            "is_active": self.is_active,
        }

    def is_low_stock(self) -> bool:
        """Check if stock is below reorder level - التحقق من انخفاض المخزون"""
        return self.quantity_available <= self.reorder_level

    def is_out_of_stock(self) -> bool:
        """Check if out of stock - التحقق من نفاد المخزون"""
        return self.quantity_available <= 0

    def needs_reorder(self) -> bool:
        """Check if reorder is needed - التحقق من الحاجة لإعادة الطلب"""
        return self.quantity_on_hand <= self.reorder_level


@dataclass
class MaintenancePart:
    """Part used in a maintenance task - قطعة مستخدمة في مهمة صيانة"""

    part_id: str
    part_number: str
    name: str
    name_ar: str
    quantity: int = 1
    unit_cost: Decimal = Decimal("0.00")
    total_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"
    is_available: bool = True
    is_used: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "part_id": self.part_id,
            "part_number": self.part_number,
            "name": self.name,
            "name_ar": self.name_ar,
            "quantity": self.quantity,
            "unit_cost": str(self.unit_cost),
            "total_cost": str(self.total_cost),
            "is_available": self.is_available,
            "is_used": self.is_used,
        }


@dataclass
class PartRequirement:
    """Required part for a maintenance schedule - قطعة مطلوبة لجدول صيانة"""

    part_id: str
    part_number: str
    name: str
    name_ar: str
    quantity: int = 1
    is_mandatory: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "part_id": self.part_id,
            "part_number": self.part_number,
            "name": self.name,
            "name_ar": self.name_ar,
            "quantity": self.quantity,
            "is_mandatory": self.is_mandatory,
        }


@dataclass
class PartTransaction:
    """Inventory transaction for a part - معاملة مخزون لقطعة غيار"""

    id: str
    tenant_id: str
    part_id: str
    part_number: str

    # Transaction details - تفاصيل المعاملة
    transaction_type: str  # receipt, issue, adjustment, transfer, return
    quantity: int
    quantity_before: int
    quantity_after: int

    # Related entities - الكيانات المرتبطة
    maintenance_task_id: str | None = None
    equipment_id: str | None = None
    purchase_order_id: str | None = None
    supplier_id: str | None = None

    # Cost tracking - تتبع التكلفة
    unit_cost: Decimal = Decimal("0.00")
    total_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Metadata
    transaction_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    performed_by: str = ""
    reason: str = ""
    reason_ar: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "part_id": self.part_id,
            "part_number": self.part_number,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "quantity_before": self.quantity_before,
            "quantity_after": self.quantity_after,
            "unit_cost": str(self.unit_cost),
            "total_cost": str(self.total_cost),
            "transaction_date": self.transaction_date.isoformat(),
            "performed_by": self.performed_by,
        }


# ==============================================================================
# Service History Models - نماذج سجل الخدمة
# ==============================================================================


@dataclass
class ServiceRecord:
    """
    Service history record - سجل تاريخ الخدمة
    """

    id: str
    tenant_id: str
    equipment_id: str
    maintenance_task_id: str | None = None

    # Service details - تفاصيل الخدمة
    service_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    service_type: MaintenanceType = MaintenanceType.SCHEDULED
    description: str = ""
    description_ar: str = ""

    # Equipment state at service - حالة المعدات عند الخدمة
    hours_at_service: float = 0.0
    kilometers_at_service: float = 0.0
    odometer_reading: float | None = None

    # Work performed - العمل المنجز
    work_summary: str = ""
    work_summary_ar: str = ""
    findings: str = ""
    findings_ar: str = ""
    recommendations: str = ""
    recommendations_ar: str = ""

    # Parts used - قطع الغيار المستخدمة
    parts_used: list[MaintenancePart] = field(default_factory=list)
    parts_cost: Decimal = Decimal("0.00")

    # Labor - العمالة
    labor_hours: float = 0.0
    labor_cost: Decimal = Decimal("0.00")
    total_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Technician - الفني
    technician_id: str | None = None
    technician_name: str = ""
    technician_name_ar: str = ""
    external_service: bool = False
    service_provider: str | None = None
    service_provider_ar: str | None = None

    # Documentation - التوثيق
    invoice_number: str | None = None
    work_order_number: str | None = None
    photos: list[str] = field(default_factory=list)
    documents: list[str] = field(default_factory=list)

    # Next service - الخدمة التالية
    next_service_date: datetime | None = None
    next_service_hours: float | None = None
    next_service_type: str | None = None

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
            "equipment_id": self.equipment_id,
            "service_date": self.service_date.isoformat(),
            "service_type": self.service_type.value,
            "description": self.description,
            "description_ar": self.description_ar,
            "hours_at_service": self.hours_at_service,
            "work_summary": self.work_summary,
            "work_summary_ar": self.work_summary_ar,
            "parts_used": [p.to_dict() for p in self.parts_used],
            "parts_cost": str(self.parts_cost),
            "labor_hours": self.labor_hours,
            "labor_cost": str(self.labor_cost),
            "total_cost": str(self.total_cost),
            "technician_name": self.technician_name,
            "external_service": self.external_service,
        }


# ==============================================================================
# Alert Models - نماذج التنبيهات
# ==============================================================================


@dataclass
class MaintenanceAlert:
    """
    Maintenance alert - تنبيه الصيانة
    """

    id: str
    tenant_id: str
    equipment_id: str

    # Alert details - تفاصيل التنبيه
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    title_ar: str
    message: str
    message_ar: str

    # Trigger data - بيانات التفعيل
    triggered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    triggered_by: str = ""  # system, hours, date, condition, user
    trigger_value: str | None = None  # The value that triggered the alert
    threshold_value: str | None = None  # The threshold that was exceeded

    # Related entities - الكيانات المرتبطة
    schedule_id: str | None = None
    task_id: str | None = None
    part_id: str | None = None

    # Status - الحالة
    is_active: bool = True
    acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved: bool = False
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    resolution_notes: str = ""
    resolution_notes_ar: str = ""

    # Notification - الإشعار
    notification_sent: bool = False
    notification_sent_at: datetime | None = None
    notification_channels: list[str] = field(default_factory=list)  # email, sms, push, whatsapp

    # Actions - الإجراءات
    recommended_action: str = ""
    recommended_action_ar: str = ""
    action_taken: str = ""
    action_taken_ar: str = ""

    # Metadata
    expires_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """Convert to dictionary for NATS publishing"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "equipment_id": self.equipment_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "title_ar": self.title_ar,
            "message": self.message,
            "message_ar": self.message_ar,
            "triggered_at": self.triggered_at.isoformat(),
            "is_active": self.is_active,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "recommended_action": self.recommended_action,
            "recommended_action_ar": self.recommended_action_ar,
        }


# ==============================================================================
# Equipment-Specific Models - نماذج خاصة بالمعدات
# ==============================================================================


@dataclass
class TractorMaintenanceProfile:
    """Tractor-specific maintenance profile - ملف صيانة خاص بالجرار"""

    equipment_id: str

    # Engine maintenance - صيانة المحرك
    engine_oil_type: str = "15W-40"
    engine_oil_capacity_l: float = 12.0
    oil_filter_part_number: str = ""
    air_filter_part_number: str = ""
    fuel_filter_part_number: str = ""

    # Transmission - ناقل الحركة
    transmission_oil_type: str = "80W-90"
    transmission_oil_capacity_l: float = 20.0

    # Hydraulics - النظام الهيدروليكي
    hydraulic_oil_type: str = "ISO 46"
    hydraulic_oil_capacity_l: float = 40.0

    # Coolant - سائل التبريد
    coolant_type: str = "50/50 Antifreeze"
    coolant_capacity_l: float = 15.0

    # Tires - الإطارات
    front_tire_size: str = ""
    rear_tire_size: str = ""
    front_tire_pressure_psi: float = 25.0
    rear_tire_pressure_psi: float = 15.0

    # Service notes - ملاحظات الخدمة
    special_requirements: str = ""
    special_requirements_ar: str = ""


@dataclass
class HarvesterMaintenanceProfile:
    """Harvester-specific maintenance profile - ملف صيانة خاص بالحصادة"""

    equipment_id: str

    # Cutting system - نظام القطع
    blade_type: str = ""
    blade_part_number: str = ""
    blade_sharpening_hours: int = 100
    blade_replacement_hours: int = 500

    # Threshing - الدراس
    concave_clearance_mm: float = 10.0
    rotor_speed_rpm: int = 1000

    # Cleaning - التنظيف
    sieve_type: str = ""
    fan_speed_rpm: int = 800

    # Belts - الأحزمة
    drive_belt_part_numbers: list[str] = field(default_factory=list)
    belt_tension_check_hours: int = 50

    # Service notes
    harvest_season_prep: str = ""
    harvest_season_prep_ar: str = ""
    post_season_storage: str = ""
    post_season_storage_ar: str = ""


@dataclass
class IrrigationMaintenanceProfile:
    """Irrigation system maintenance profile - ملف صيانة نظام الري"""

    equipment_id: str

    # System type - نوع النظام
    irrigation_type: IrrigationType = IrrigationType.DRIP

    # Pump maintenance - صيانة المضخة
    pump_type: str = ""
    pump_model: str = ""
    impeller_part_number: str = ""
    seal_kit_part_number: str = ""
    pump_oil_type: str | None = None

    # Filtration - الترشيح
    filter_type: str = ""  # disc, screen, sand
    filter_mesh_size: int | None = None
    filter_cleaning_frequency_hours: int = 100
    filter_replacement_frequency_months: int = 12

    # Emitters/Sprinklers - البواعث/الرشاشات
    emitter_type: str = ""
    emitter_flow_rate_lph: float = 0.0
    nozzle_part_number: str | None = None
    emitter_check_frequency_months: int = 3

    # Pressure - الضغط
    operating_pressure_bar: float = 2.0
    max_pressure_bar: float = 4.0
    pressure_regulator_setting: float | None = None

    # Winterization - التجهيز للشتاء
    requires_winterization: bool = False
    winterization_procedure: str = ""
    winterization_procedure_ar: str = ""


@dataclass
class SprayerMaintenanceProfile:
    """Sprayer-specific maintenance profile - ملف صيانة خاص بالرشاشة"""

    equipment_id: str

    # Tank - الخزان
    tank_capacity_l: float = 0.0
    tank_material: str = ""  # polyethylene, stainless steel, fiberglass

    # Pump - المضخة
    pump_type: str = ""  # centrifugal, piston, diaphragm
    pump_model: str = ""
    pump_flow_rate_lpm: float = 0.0
    pump_max_pressure_bar: float = 0.0
    pump_seal_kit_part_number: str = ""

    # Nozzles - الفوهات
    nozzle_type: str = ""  # flat fan, cone, air induction
    nozzle_size: str = ""  # e.g., "02" for 0.2 GPM
    nozzle_material: str = ""  # brass, stainless, ceramic, polymer
    nozzle_part_number: str = ""
    nozzle_count: int = 0
    nozzle_spacing_cm: float = 50.0

    # Boom - الذراع
    boom_width_m: float = 0.0
    boom_height_adjustment: bool = False
    boom_fold_type: str = ""  # manual, hydraulic

    # Filters - الفلاتر
    suction_filter_mesh: int = 50
    pressure_filter_mesh: int = 80
    nozzle_filter_mesh: int = 100
    filter_part_numbers: list[str] = field(default_factory=list)

    # Calibration - المعايرة
    last_calibration_date: datetime | None = None
    calibration_frequency_months: int = 6
    flow_rate_tolerance_percent: float = 10.0

    # Cleaning - التنظيف
    tank_rinse_procedure: str = ""
    tank_rinse_procedure_ar: str = ""
    decontamination_required: bool = False


# ==============================================================================
# Helper Functions - دوال مساعدة
# ==============================================================================


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())[:12]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def get_equipment_type_name(equipment_type: EquipmentType, language: str = "en") -> str:
    """
    Get human-readable name for equipment type
    الحصول على اسم مقروء لنوع المعدات
    """
    names = {
        EquipmentType.TRACTOR: {"en": "Tractor", "ar": "جرار"},
        EquipmentType.HARVESTER: {"en": "Harvester", "ar": "حصادة"},
        EquipmentType.IRRIGATION_SYSTEM: {"en": "Irrigation System", "ar": "نظام ري"},
        EquipmentType.SPRAYER: {"en": "Sprayer", "ar": "رشاشة"},
        EquipmentType.SEEDER: {"en": "Seeder", "ar": "بذارة"},
        EquipmentType.PLOW: {"en": "Plow", "ar": "محراث"},
        EquipmentType.CULTIVATOR: {"en": "Cultivator", "ar": "مزرعة"},
        EquipmentType.TRAILER: {"en": "Trailer", "ar": "مقطورة"},
        EquipmentType.PUMP: {"en": "Pump", "ar": "مضخة"},
        EquipmentType.GENERATOR: {"en": "Generator", "ar": "مولد كهربائي"},
        EquipmentType.DRONE: {"en": "Drone", "ar": "طائرة بدون طيار"},
        EquipmentType.OTHER: {"en": "Other", "ar": "أخرى"},
    }
    return names.get(equipment_type, {"en": "Unknown", "ar": "غير معروف"}).get(language, "Unknown")


def get_maintenance_type_name(maintenance_type: MaintenanceType, language: str = "en") -> str:
    """
    Get human-readable name for maintenance type
    الحصول على اسم مقروء لنوع الصيانة
    """
    names = {
        MaintenanceType.PREVENTIVE: {"en": "Preventive Maintenance", "ar": "صيانة وقائية"},
        MaintenanceType.CORRECTIVE: {"en": "Corrective Maintenance", "ar": "صيانة تصحيحية"},
        MaintenanceType.PREDICTIVE: {"en": "Predictive Maintenance", "ar": "صيانة تنبؤية"},
        MaintenanceType.EMERGENCY: {"en": "Emergency Maintenance", "ar": "صيانة طارئة"},
        MaintenanceType.SCHEDULED: {"en": "Scheduled Maintenance", "ar": "صيانة مجدولة"},
        MaintenanceType.OVERHAUL: {"en": "Major Overhaul", "ar": "إصلاح شامل"},
    }
    return names.get(maintenance_type, {"en": "Unknown", "ar": "غير معروف"}).get(language, "Unknown")


def get_alert_severity_name(severity: AlertSeverity, language: str = "en") -> str:
    """
    Get human-readable name for alert severity
    الحصول على اسم مقروء لخطورة التنبيه
    """
    names = {
        AlertSeverity.INFO: {"en": "Information", "ar": "معلومات"},
        AlertSeverity.WARNING: {"en": "Warning", "ar": "تحذير"},
        AlertSeverity.CRITICAL: {"en": "Critical", "ar": "حرج"},
        AlertSeverity.EMERGENCY: {"en": "Emergency", "ar": "طارئ"},
    }
    return names.get(severity, {"en": "Unknown", "ar": "غير معروف"}).get(language, "Unknown")
