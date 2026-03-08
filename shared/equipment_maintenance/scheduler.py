"""
SAHOOL Equipment Maintenance Scheduler - جدولة صيانة المعدات

Provides maintenance scheduling functionality including:
- Calendar-based scheduling (daily, weekly, monthly, yearly)
- Hours-based scheduling (operating hours intervals)
- Season-based scheduling (pre/post/mid agricultural season)
- Automatic task generation from schedules
- Schedule conflict detection
- Workload balancing

Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from enum import StrEnum

from .models import (
    AlertSeverity,
    AlertType,
    ChecklistItem,
    Equipment,
    EquipmentType,
    MaintenanceAlert,
    MaintenancePart,
    MaintenancePriority,
    MaintenanceSchedule,
    MaintenanceStatus,
    MaintenanceTask,
    MaintenanceType,
    PartRequirement,
    generate_id,
)

# ==============================================================================
# Enumerations - التعدادات
# ==============================================================================


class ScheduleFrequency(StrEnum):
    """Schedule frequency type - نوع تكرار الجدولة"""

    HOURS = "hours"  # بناءً على ساعات التشغيل
    DAILY = "daily"  # يومي
    WEEKLY = "weekly"  # أسبوعي
    BIWEEKLY = "biweekly"  # كل أسبوعين
    MONTHLY = "monthly"  # شهري
    QUARTERLY = "quarterly"  # ربع سنوي
    SEMI_ANNUALLY = "semi_annually"  # نصف سنوي
    ANNUALLY = "annually"  # سنوي
    SEASONAL = "seasonal"  # موسمي
    ON_DEMAND = "on_demand"  # عند الطلب


class AgriculturalSeason(StrEnum):
    """Agricultural season - الموسم الزراعي"""

    PRE_PLANTING = "pre_planting"  # قبل الزراعة
    PLANTING = "planting"  # موسم الزراعة
    GROWING = "growing"  # موسم النمو
    PRE_HARVEST = "pre_harvest"  # قبل الحصاد
    HARVEST = "harvest"  # موسم الحصاد
    POST_HARVEST = "post_harvest"  # بعد الحصاد
    OFF_SEASON = "off_season"  # خارج الموسم


# ==============================================================================
# Data Classes - فئات البيانات
# ==============================================================================


@dataclass
class ScheduledTask:
    """A task scheduled for execution - مهمة مجدولة للتنفيذ"""

    schedule_id: str
    equipment_id: str
    scheduled_date: datetime
    due_date: datetime
    title: str
    title_ar: str
    description: str
    description_ar: str
    maintenance_type: MaintenanceType
    priority: MaintenancePriority
    estimated_duration_hours: float
    checklist: list[dict] = field(default_factory=list)
    parts_required: list[PartRequirement] = field(default_factory=list)
    triggered_by: str = ""  # hours, calendar, season, condition


@dataclass
class ScheduleConflict:
    """Schedule conflict information - معلومات تعارض الجدولة"""

    schedule_id_1: str
    schedule_id_2: str
    conflict_date: datetime
    equipment_id: str
    conflict_type: str  # overlap, resource_conflict, part_shortage
    message: str
    message_ar: str
    resolution_suggestion: str
    resolution_suggestion_ar: str


@dataclass
class WorkloadSummary:
    """Workload summary for a period - ملخص حجم العمل لفترة"""

    period_start: datetime
    period_end: datetime
    total_tasks: int
    total_hours: float
    tasks_by_type: dict[str, int] = field(default_factory=dict)
    tasks_by_priority: dict[str, int] = field(default_factory=dict)
    tasks_by_equipment: dict[str, int] = field(default_factory=dict)
    peak_days: list[date] = field(default_factory=list)
    average_tasks_per_day: float = 0.0


@dataclass
class SeasonConfig:
    """Season configuration for scheduling - تكوين الموسم للجدولة"""

    season: AgriculturalSeason
    start_month: int
    start_day: int
    end_month: int
    end_day: int
    region: str = "middle_east"

    def get_start_date(self, year: int) -> date:
        """Get start date for a specific year"""
        return date(year, self.start_month, self.start_day)

    def get_end_date(self, year: int) -> date:
        """Get end date for a specific year"""
        return date(year, self.end_month, self.end_day)


# ==============================================================================
# Default Season Configurations - تكوينات الموسم الافتراضية
# ==============================================================================

# Middle East agricultural seasons (Saudi Arabia, Gulf)
MIDDLE_EAST_SEASONS = {
    AgriculturalSeason.PRE_PLANTING: SeasonConfig(
        season=AgriculturalSeason.PRE_PLANTING,
        start_month=9,
        start_day=1,
        end_month=10,
        end_day=15,
        region="middle_east",
    ),
    AgriculturalSeason.PLANTING: SeasonConfig(
        season=AgriculturalSeason.PLANTING,
        start_month=10,
        start_day=15,
        end_month=11,
        end_day=30,
        region="middle_east",
    ),
    AgriculturalSeason.GROWING: SeasonConfig(
        season=AgriculturalSeason.GROWING,
        start_month=12,
        start_day=1,
        end_month=3,
        end_day=31,
        region="middle_east",
    ),
    AgriculturalSeason.PRE_HARVEST: SeasonConfig(
        season=AgriculturalSeason.PRE_HARVEST,
        start_month=4,
        start_day=1,
        end_month=4,
        end_day=15,
        region="middle_east",
    ),
    AgriculturalSeason.HARVEST: SeasonConfig(
        season=AgriculturalSeason.HARVEST,
        start_month=4,
        start_day=15,
        end_month=5,
        end_day=31,
        region="middle_east",
    ),
    AgriculturalSeason.POST_HARVEST: SeasonConfig(
        season=AgriculturalSeason.POST_HARVEST,
        start_month=6,
        start_day=1,
        end_month=6,
        end_day=30,
        region="middle_east",
    ),
    AgriculturalSeason.OFF_SEASON: SeasonConfig(
        season=AgriculturalSeason.OFF_SEASON,
        start_month=7,
        start_day=1,
        end_month=8,
        end_day=31,
        region="middle_east",
    ),
}


# ==============================================================================
# Equipment-Specific Schedules - جداول خاصة بالمعدات
# ==============================================================================


def get_default_tractor_schedules(equipment_id: str, tenant_id: str) -> list[MaintenanceSchedule]:
    """
    Get default maintenance schedules for tractors
    الحصول على جداول الصيانة الافتراضية للجرارات
    """
    return [
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Engine Oil Change",
            name_ar="تغيير زيت المحرك",
            description="Regular engine oil and filter change",
            description_ar="تغيير زيت المحرك والفلتر بشكل دوري",
            maintenance_type=MaintenanceType.PREVENTIVE,
            hours_interval=250,
            hours_warning_threshold=225,
            task_title="Engine Oil Change",
            task_title_ar="تغيير زيت المحرك",
            estimated_duration_hours=1.0,
            default_priority=MaintenancePriority.MEDIUM,
            checklist_template=[
                {"description": "Drain old oil", "description_ar": "تصريف الزيت القديم"},
                {"description": "Replace oil filter", "description_ar": "استبدال فلتر الزيت"},
                {
                    "description": "Add new oil (check capacity)",
                    "description_ar": "إضافة زيت جديد (تحقق من السعة)",
                },
                {"description": "Check for leaks", "description_ar": "التحقق من التسريبات"},
                {
                    "description": "Record oil type and quantity",
                    "description_ar": "تسجيل نوع وكمية الزيت",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Air Filter Replacement",
            name_ar="استبدال فلتر الهواء",
            description="Replace air filter element",
            description_ar="استبدال عنصر فلتر الهواء",
            maintenance_type=MaintenanceType.PREVENTIVE,
            hours_interval=500,
            hours_warning_threshold=475,
            task_title="Air Filter Replacement",
            task_title_ar="استبدال فلتر الهواء",
            estimated_duration_hours=0.5,
            default_priority=MaintenancePriority.MEDIUM,
            checklist_template=[
                {
                    "description": "Remove air filter housing cover",
                    "description_ar": "إزالة غطاء علبة الفلتر",
                },
                {
                    "description": "Remove old filter element",
                    "description_ar": "إزالة عنصر الفلتر القديم",
                },
                {"description": "Clean housing interior", "description_ar": "تنظيف داخل العلبة"},
                {
                    "description": "Install new filter element",
                    "description_ar": "تركيب عنصر الفلتر الجديد",
                },
                {"description": "Secure housing cover", "description_ar": "تأمين غطاء العلبة"},
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Hydraulic System Service",
            name_ar="خدمة النظام الهيدروليكي",
            description="Hydraulic oil and filter change",
            description_ar="تغيير الزيت والفلتر الهيدروليكي",
            maintenance_type=MaintenanceType.PREVENTIVE,
            hours_interval=1000,
            hours_warning_threshold=950,
            task_title="Hydraulic System Service",
            task_title_ar="خدمة النظام الهيدروليكي",
            estimated_duration_hours=2.0,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {
                    "description": "Drain hydraulic reservoir",
                    "description_ar": "تصريف خزان الهيدروليك",
                },
                {
                    "description": "Replace hydraulic filter",
                    "description_ar": "استبدال الفلتر الهيدروليكي",
                },
                {"description": "Inspect hoses for wear", "description_ar": "فحص الخراطيم للتآكل"},
                {
                    "description": "Check cylinder seals",
                    "description_ar": "التحقق من حشوات الأسطوانات",
                },
                {
                    "description": "Refill with correct oil type",
                    "description_ar": "إعادة التعبئة بنوع الزيت الصحيح",
                },
                {
                    "description": "Bleed air from system",
                    "description_ar": "تنفيس الهواء من النظام",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Pre-Season Inspection",
            name_ar="فحص ما قبل الموسم",
            description="Comprehensive inspection before planting season",
            description_ar="فحص شامل قبل موسم الزراعة",
            maintenance_type=MaintenanceType.SCHEDULED,
            season_trigger="pre_planting",
            task_title="Pre-Season Inspection",
            task_title_ar="فحص ما قبل الموسم",
            estimated_duration_hours=4.0,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {
                    "description": "Check all fluid levels",
                    "description_ar": "التحقق من جميع مستويات السوائل",
                },
                {
                    "description": "Inspect tire condition and pressure",
                    "description_ar": "فحص حالة الإطارات والضغط",
                },
                {
                    "description": "Test all lights and signals",
                    "description_ar": "اختبار جميع الأضواء والإشارات",
                },
                {"description": "Inspect brake system", "description_ar": "فحص نظام الفرامل"},
                {
                    "description": "Check PTO operation",
                    "description_ar": "التحقق من عمل عمود الإدارة",
                },
                {"description": "Test 3-point hitch", "description_ar": "اختبار الرابطة الثلاثية"},
                {
                    "description": "Inspect belts and hoses",
                    "description_ar": "فحص الأحزمة والخراطيم",
                },
                {"description": "Grease all fittings", "description_ar": "تشحيم جميع النقاط"},
            ],
        ),
    ]


def get_default_harvester_schedules(equipment_id: str, tenant_id: str) -> list[MaintenanceSchedule]:
    """
    Get default maintenance schedules for harvesters
    الحصول على جداول الصيانة الافتراضية للحصادات
    """
    return [
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Daily Harvester Check",
            name_ar="الفحص اليومي للحصادة",
            description="Daily inspection during harvest season",
            description_ar="الفحص اليومي خلال موسم الحصاد",
            maintenance_type=MaintenanceType.PREVENTIVE,
            calendar_interval_days=1,
            season_trigger="harvest",
            task_title="Daily Harvester Check",
            task_title_ar="الفحص اليومي للحصادة",
            estimated_duration_hours=0.5,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {
                    "description": "Check engine oil level",
                    "description_ar": "التحقق من مستوى زيت المحرك",
                },
                {"description": "Inspect knife sections", "description_ar": "فحص أقسام السكين"},
                {"description": "Check belt tensions", "description_ar": "التحقق من شد الأحزمة"},
                {"description": "Clean radiator screen", "description_ar": "تنظيف شبكة المبرد"},
                {"description": "Grease daily points", "description_ar": "تشحيم النقاط اليومية"},
                {
                    "description": "Check grain tank sensors",
                    "description_ar": "فحص مجسات خزان الحبوب",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Knife Blade Sharpening",
            name_ar="شحذ شفرات السكين",
            description="Sharpen or replace cutting blades",
            description_ar="شحذ أو استبدال شفرات القطع",
            maintenance_type=MaintenanceType.PREVENTIVE,
            hours_interval=50,
            hours_warning_threshold=45,
            task_title="Knife Blade Maintenance",
            task_title_ar="صيانة شفرات السكين",
            estimated_duration_hours=2.0,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {
                    "description": "Inspect all knife sections",
                    "description_ar": "فحص جميع أقسام السكين",
                },
                {
                    "description": "Mark sections needing replacement",
                    "description_ar": "تحديد الأقسام التي تحتاج استبدال",
                },
                {
                    "description": "Sharpen or replace sections",
                    "description_ar": "شحذ أو استبدال الأقسام",
                },
                {"description": "Check knife guards", "description_ar": "فحص واقيات السكين"},
                {
                    "description": "Verify knife alignment",
                    "description_ar": "التحقق من محاذاة السكين",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Post-Harvest Storage Prep",
            name_ar="تجهيز التخزين بعد الحصاد",
            description="Prepare harvester for off-season storage",
            description_ar="تجهيز الحصادة للتخزين في غير الموسم",
            maintenance_type=MaintenanceType.SCHEDULED,
            season_trigger="post_harvest",
            task_title="Post-Harvest Storage Preparation",
            task_title_ar="تجهيز التخزين بعد الحصاد",
            estimated_duration_hours=8.0,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {
                    "description": "Clean entire machine thoroughly",
                    "description_ar": "تنظيف الآلة بالكامل جيداً",
                },
                {
                    "description": "Change engine oil and filter",
                    "description_ar": "تغيير زيت المحرك والفلتر",
                },
                {
                    "description": "Drain fuel or add stabilizer",
                    "description_ar": "تصريف الوقود أو إضافة مثبت",
                },
                {"description": "Grease all fittings", "description_ar": "تشحيم جميع النقاط"},
                {"description": "Apply rust preventative", "description_ar": "تطبيق مانع الصدأ"},
                {
                    "description": "Remove batteries for storage",
                    "description_ar": "إزالة البطاريات للتخزين",
                },
                {"description": "Cover machine", "description_ar": "تغطية الآلة"},
                {
                    "description": "Document any repairs needed",
                    "description_ar": "توثيق أي إصلاحات مطلوبة",
                },
            ],
        ),
    ]


def get_default_irrigation_schedules(equipment_id: str, tenant_id: str) -> list[MaintenanceSchedule]:
    """
    Get default maintenance schedules for irrigation systems
    الحصول على جداول الصيانة الافتراضية لأنظمة الري
    """
    return [
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Filter Cleaning",
            name_ar="تنظيف الفلتر",
            description="Clean or backwash irrigation filters",
            description_ar="تنظيف أو غسل فلاتر الري عكسياً",
            maintenance_type=MaintenanceType.PREVENTIVE,
            hours_interval=100,
            hours_warning_threshold=90,
            task_title="Irrigation Filter Cleaning",
            task_title_ar="تنظيف فلتر الري",
            estimated_duration_hours=1.0,
            default_priority=MaintenancePriority.MEDIUM,
            checklist_template=[
                {"description": "Shut off water supply", "description_ar": "إيقاف إمداد المياه"},
                {"description": "Release pressure", "description_ar": "تحرير الضغط"},
                {"description": "Remove filter elements", "description_ar": "إزالة عناصر الفلتر"},
                {
                    "description": "Clean elements thoroughly",
                    "description_ar": "تنظيف العناصر جيداً",
                },
                {"description": "Inspect for damage", "description_ar": "فحص التلف"},
                {"description": "Reinstall elements", "description_ar": "إعادة تركيب العناصر"},
                {
                    "description": "Check pressure differential",
                    "description_ar": "التحقق من فرق الضغط",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Emitter/Nozzle Check",
            name_ar="فحص البواعث/الفوهات",
            description="Inspect and clean emitters or sprinkler nozzles",
            description_ar="فحص وتنظيف البواعث أو فوهات الرشاشات",
            maintenance_type=MaintenanceType.PREVENTIVE,
            calendar_interval_days=30,
            task_title="Emitter/Nozzle Inspection",
            task_title_ar="فحص البواعث/الفوهات",
            estimated_duration_hours=3.0,
            default_priority=MaintenancePriority.MEDIUM,
            checklist_template=[
                {
                    "description": "Walk field to inspect emitters",
                    "description_ar": "المشي في الحقل لفحص البواعث",
                },
                {
                    "description": "Mark clogged or damaged emitters",
                    "description_ar": "تحديد البواعث المسدودة أو التالفة",
                },
                {
                    "description": "Clean or replace as needed",
                    "description_ar": "التنظيف أو الاستبدال حسب الحاجة",
                },
                {"description": "Check flow rates", "description_ar": "التحقق من معدلات التدفق"},
                {
                    "description": "Record replacement count",
                    "description_ar": "تسجيل عدد الاستبدالات",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Pump Maintenance",
            name_ar="صيانة المضخة",
            description="Irrigation pump service and inspection",
            description_ar="خدمة وفحص مضخة الري",
            maintenance_type=MaintenanceType.PREVENTIVE,
            hours_interval=500,
            hours_warning_threshold=475,
            task_title="Pump Service",
            task_title_ar="خدمة المضخة",
            estimated_duration_hours=2.0,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {
                    "description": "Check pump alignment",
                    "description_ar": "التحقق من محاذاة المضخة",
                },
                {
                    "description": "Inspect seals for leaks",
                    "description_ar": "فحص الحشوات للتسريبات",
                },
                {"description": "Check bearings", "description_ar": "فحص المحامل"},
                {
                    "description": "Measure flow rate and pressure",
                    "description_ar": "قياس معدل التدفق والضغط",
                },
                {"description": "Inspect impeller condition", "description_ar": "فحص حالة المروحة"},
                {
                    "description": "Check electrical connections",
                    "description_ar": "التحقق من التوصيلات الكهربائية",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Pre-Season System Startup",
            name_ar="بدء تشغيل النظام قبل الموسم",
            description="System startup and testing before irrigation season",
            description_ar="بدء تشغيل واختبار النظام قبل موسم الري",
            maintenance_type=MaintenanceType.SCHEDULED,
            season_trigger="pre_planting",
            task_title="Irrigation System Startup",
            task_title_ar="بدء تشغيل نظام الري",
            estimated_duration_hours=4.0,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {
                    "description": "Inspect all mainlines for damage",
                    "description_ar": "فحص جميع الخطوط الرئيسية للتلف",
                },
                {
                    "description": "Check valve operation",
                    "description_ar": "التحقق من عمل الصمامات",
                },
                {"description": "Flush mainlines", "description_ar": "شطف الخطوط الرئيسية"},
                {"description": "Flush lateral lines", "description_ar": "شطف الخطوط الفرعية"},
                {"description": "Test pressure regulation", "description_ar": "اختبار تنظيم الضغط"},
                {
                    "description": "Verify controller programming",
                    "description_ar": "التحقق من برمجة وحدة التحكم",
                },
                {
                    "description": "Run full system test",
                    "description_ar": "تشغيل اختبار النظام الكامل",
                },
            ],
        ),
    ]


def get_default_sprayer_schedules(equipment_id: str, tenant_id: str) -> list[MaintenanceSchedule]:
    """
    Get default maintenance schedules for sprayers
    الحصول على جداول الصيانة الافتراضية للرشاشات
    """
    return [
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Post-Application Cleaning",
            name_ar="التنظيف بعد الرش",
            description="Clean sprayer after each use",
            description_ar="تنظيف الرشاشة بعد كل استخدام",
            maintenance_type=MaintenanceType.PREVENTIVE,
            calendar_interval_days=1,  # After each use
            task_title="Sprayer Cleaning",
            task_title_ar="تنظيف الرشاشة",
            estimated_duration_hours=0.5,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {"description": "Triple rinse tank", "description_ar": "شطف الخزان ثلاث مرات"},
                {"description": "Flush all hoses", "description_ar": "شطف جميع الخراطيم"},
                {"description": "Clean nozzle filters", "description_ar": "تنظيف فلاتر الفوهات"},
                {
                    "description": "Run clean water through system",
                    "description_ar": "تشغيل ماء نظيف في النظام",
                },
                {
                    "description": "Dispose of rinse water properly",
                    "description_ar": "التخلص من ماء الشطف بشكل صحيح",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Nozzle Calibration",
            name_ar="معايرة الفوهات",
            description="Calibrate sprayer nozzles for accurate application",
            description_ar="معايرة فوهات الرشاشة للتطبيق الدقيق",
            maintenance_type=MaintenanceType.PREVENTIVE,
            calendar_interval_days=30,
            task_title="Nozzle Calibration",
            task_title_ar="معايرة الفوهات",
            estimated_duration_hours=1.5,
            default_priority=MaintenancePriority.HIGH,
            checklist_template=[
                {
                    "description": "Measure output of each nozzle",
                    "description_ar": "قياس خرج كل فوهة",
                },
                {
                    "description": "Compare to rated output",
                    "description_ar": "مقارنة مع الخرج المقنن",
                },
                {
                    "description": "Replace worn nozzles (>10% variation)",
                    "description_ar": "استبدال الفوهات البالية (+10% تفاوت)",
                },
                {"description": "Check spray pattern", "description_ar": "التحقق من نمط الرش"},
                {
                    "description": "Verify pressure gauge accuracy",
                    "description_ar": "التحقق من دقة مقياس الضغط",
                },
                {
                    "description": "Calculate actual application rate",
                    "description_ar": "حساب معدل التطبيق الفعلي",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Pump Service",
            name_ar="خدمة المضخة",
            description="Service sprayer pump",
            description_ar="خدمة مضخة الرشاشة",
            maintenance_type=MaintenanceType.PREVENTIVE,
            hours_interval=100,
            hours_warning_threshold=90,
            task_title="Sprayer Pump Service",
            task_title_ar="خدمة مضخة الرشاشة",
            estimated_duration_hours=2.0,
            default_priority=MaintenancePriority.MEDIUM,
            checklist_template=[
                {
                    "description": "Check pump oil level",
                    "description_ar": "التحقق من مستوى زيت المضخة",
                },
                {
                    "description": "Inspect diaphragms/pistons",
                    "description_ar": "فحص الحجابات/المكابس",
                },
                {"description": "Check seals for leaks", "description_ar": "فحص الحشوات للتسريبات"},
                {"description": "Verify pressure output", "description_ar": "التحقق من خرج الضغط"},
                {
                    "description": "Check drive belt tension",
                    "description_ar": "التحقق من شد حزام القيادة",
                },
            ],
        ),
        MaintenanceSchedule(
            id=generate_id("sched"),
            tenant_id=tenant_id,
            equipment_id=equipment_id,
            name="Boom Inspection",
            name_ar="فحص الذراع",
            description="Inspect and adjust spray boom",
            description_ar="فحص وضبط ذراع الرش",
            maintenance_type=MaintenanceType.PREVENTIVE,
            calendar_interval_days=14,
            task_title="Boom Inspection",
            task_title_ar="فحص الذراع",
            estimated_duration_hours=1.0,
            default_priority=MaintenancePriority.MEDIUM,
            checklist_template=[
                {"description": "Check boom level", "description_ar": "التحقق من مستوى الذراع"},
                {"description": "Inspect breakaway joints", "description_ar": "فحص مفاصل الفصل"},
                {
                    "description": "Check hydraulic cylinders",
                    "description_ar": "فحص الأسطوانات الهيدروليكية",
                },
                {
                    "description": "Verify nozzle spacing",
                    "description_ar": "التحقق من تباعد الفوهات",
                },
                {
                    "description": "Test boom height sensors",
                    "description_ar": "اختبار مجسات ارتفاع الذراع",
                },
            ],
        ),
    ]


# ==============================================================================
# Maintenance Scheduler Class - فئة جدولة الصيانة
# ==============================================================================


class MaintenanceScheduler:
    """
    Maintenance scheduler for agricultural equipment
    جدولة الصيانة للمعدات الزراعية
    """

    def __init__(
        self,
        tenant_id: str,
        season_configs: dict[AgriculturalSeason, SeasonConfig] | None = None,
    ):
        """
        Initialize the scheduler

        Args:
            tenant_id: Tenant identifier
            season_configs: Optional custom season configurations
        """
        self.tenant_id = tenant_id
        self.season_configs = season_configs or MIDDLE_EAST_SEASONS
        self._schedules: dict[str, MaintenanceSchedule] = {}
        self._equipment: dict[str, Equipment] = {}

    def register_equipment(self, equipment: Equipment) -> None:
        """
        Register equipment with the scheduler
        تسجيل المعدات مع الجدولة
        """
        self._equipment[equipment.id] = equipment

    def add_schedule(self, schedule: MaintenanceSchedule) -> None:
        """
        Add a maintenance schedule
        إضافة جدول صيانة
        """
        self._schedules[schedule.id] = schedule

    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a maintenance schedule
        إزالة جدول صيانة
        """
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        return False

    def get_schedules_for_equipment(self, equipment_id: str) -> list[MaintenanceSchedule]:
        """
        Get all schedules for a specific equipment
        الحصول على جميع الجداول لمعدات محددة
        """
        return [s for s in self._schedules.values() if s.equipment_id == equipment_id]

    def create_default_schedules(self, equipment: Equipment) -> list[MaintenanceSchedule]:
        """
        Create default maintenance schedules based on equipment type
        إنشاء جداول صيانة افتراضية بناءً على نوع المعدات
        """
        schedules: list[MaintenanceSchedule] = []

        if equipment.equipment_type == EquipmentType.TRACTOR:
            schedules = get_default_tractor_schedules(equipment.id, self.tenant_id)
        elif equipment.equipment_type == EquipmentType.HARVESTER:
            schedules = get_default_harvester_schedules(equipment.id, self.tenant_id)
        elif equipment.equipment_type == EquipmentType.IRRIGATION_SYSTEM:
            schedules = get_default_irrigation_schedules(equipment.id, self.tenant_id)
        elif equipment.equipment_type == EquipmentType.SPRAYER:
            schedules = get_default_sprayer_schedules(equipment.id, self.tenant_id)

        # Add all schedules to the scheduler
        for schedule in schedules:
            self.add_schedule(schedule)

        return schedules

    def get_current_season(self, check_date: date | None = None) -> AgriculturalSeason:
        """
        Determine the current agricultural season
        تحديد الموسم الزراعي الحالي
        """
        check_date = check_date or date.today()

        for season, config in self.season_configs.items():
            start = config.get_start_date(check_date.year)
            end = config.get_end_date(check_date.year)

            # Handle year boundary (e.g., winter season)
            if start > end:
                if check_date >= start or check_date <= end:
                    return season
            else:
                if start <= check_date <= end:
                    return season

        return AgriculturalSeason.OFF_SEASON

    def calculate_next_due_date(
        self,
        schedule: MaintenanceSchedule,
        equipment: Equipment,
        from_date: datetime | None = None,
    ) -> datetime | None:
        """
        Calculate the next due date for a schedule
        حساب تاريخ الاستحقاق التالي للجدول
        """
        from_date = from_date or datetime.now(UTC)

        # Hours-based scheduling
        if schedule.hours_interval:
            hours_remaining = schedule.hours_interval - (equipment.total_hours - (schedule.last_executed_hours or 0))
            if hours_remaining <= 0:
                return from_date  # Due now
            # Estimate based on average usage (assume 8 hours/day if active)
            days_until_due = hours_remaining / 8
            return from_date + timedelta(days=days_until_due)

        # Calendar-based scheduling
        if schedule.calendar_interval_days:
            if schedule.last_executed_at:
                return schedule.last_executed_at + timedelta(days=schedule.calendar_interval_days)
            return from_date + timedelta(days=schedule.calendar_interval_days)

        # Day of week scheduling
        if schedule.calendar_day_of_week is not None:
            current_day = from_date.weekday()
            target_day = schedule.calendar_day_of_week
            days_ahead = target_day - current_day
            if days_ahead <= 0:
                days_ahead += 7
            return from_date + timedelta(days=days_ahead)

        # Day of month scheduling
        if schedule.calendar_day_of_month:
            target_day = schedule.calendar_day_of_month
            if from_date.day < target_day:
                return from_date.replace(day=target_day)
            else:
                # Next month
                if from_date.month == 12:
                    next_month = from_date.replace(year=from_date.year + 1, month=1, day=target_day)
                else:
                    next_month = from_date.replace(month=from_date.month + 1, day=target_day)
                return next_month

        # Season-based scheduling
        if schedule.season_trigger:
            try:
                target_season = AgriculturalSeason(schedule.season_trigger)
                config = self.season_configs.get(target_season)
                if config:
                    season_start = config.get_start_date(from_date.year)
                    if from_date.date() < season_start:
                        return datetime.combine(season_start, datetime.min.time(), tzinfo=UTC)
                    # Next year
                    next_year_start = config.get_start_date(from_date.year + 1)
                    return datetime.combine(next_year_start, datetime.min.time(), tzinfo=UTC)
            except ValueError:
                pass

        return None

    def calculate_next_due_hours(
        self,
        schedule: MaintenanceSchedule,
        equipment: Equipment,
    ) -> float | None:
        """
        Calculate the hours at which maintenance is next due
        حساب الساعات التي تستحق فيها الصيانة التالية
        """
        if not schedule.hours_interval:
            return None

        last_hours = schedule.last_executed_hours or 0
        return last_hours + schedule.hours_interval

    def get_due_schedules(
        self,
        equipment_id: str | None = None,
        check_date: datetime | None = None,
        include_approaching: bool = True,
    ) -> list[tuple[MaintenanceSchedule, str]]:
        """
        Get all schedules that are due or approaching due date
        الحصول على جميع الجداول المستحقة أو التي تقترب من تاريخ الاستحقاق

        Returns:
            List of tuples (schedule, trigger_reason)
        """
        check_date = check_date or datetime.now(UTC)
        due_schedules: list[tuple[MaintenanceSchedule, str]] = []

        for schedule in self._schedules.values():
            if not schedule.is_active:
                continue
            if equipment_id and schedule.equipment_id != equipment_id:
                continue

            equipment = self._equipment.get(schedule.equipment_id)
            if not equipment:
                continue

            # Check hours-based
            if schedule.hours_interval:
                hours_since = equipment.total_hours - (schedule.last_executed_hours or 0)
                if hours_since >= schedule.hours_interval:
                    due_schedules.append((schedule, "hours_exceeded"))
                elif include_approaching and schedule.hours_warning_threshold:
                    if hours_since >= schedule.hours_warning_threshold:
                        due_schedules.append((schedule, "hours_approaching"))

            # Check calendar-based
            next_due = self.calculate_next_due_date(schedule, equipment, check_date)
            if next_due and next_due <= check_date:
                due_schedules.append((schedule, "date_exceeded"))
            elif include_approaching and next_due:
                warning_threshold = timedelta(days=7)  # 7 days warning
                if next_due - check_date <= warning_threshold:
                    due_schedules.append((schedule, "date_approaching"))

            # Check season-based
            if schedule.season_trigger:
                current_season = self.get_current_season(check_date.date())
                try:
                    target_season = AgriculturalSeason(schedule.season_trigger)
                    if current_season == target_season:
                        # Check if already executed this season
                        if schedule.last_executed_at:
                            season_config = self.season_configs.get(target_season)
                            if season_config:
                                season_start = datetime.combine(
                                    season_config.get_start_date(check_date.year),
                                    datetime.min.time(),
                                    tzinfo=UTC,
                                )
                                if schedule.last_executed_at < season_start:
                                    due_schedules.append((schedule, "season_trigger"))
                        else:
                            due_schedules.append((schedule, "season_trigger"))
                except ValueError:
                    pass

        return due_schedules

    def generate_task_from_schedule(
        self,
        schedule: MaintenanceSchedule,
        scheduled_date: datetime | None = None,
        triggered_by: str = "schedule",
    ) -> MaintenanceTask:
        """
        Generate a maintenance task from a schedule
        إنشاء مهمة صيانة من جدول
        """
        scheduled_date = scheduled_date or datetime.now(UTC)
        equipment = self._equipment.get(schedule.equipment_id)

        # Create checklist items from template
        checklist = [
            ChecklistItem(
                id=generate_id("chk"),
                description=item.get("description", ""),
                description_ar=item.get("description_ar", ""),
            )
            for item in schedule.checklist_template
        ]

        # Create part requirements
        parts_required = [
            MaintenancePart(
                part_id=req.part_id,
                part_number=req.part_number,
                name=req.name,
                name_ar=req.name_ar,
                quantity=req.quantity,
            )
            for req in schedule.typical_parts
        ]

        task = MaintenanceTask(
            id=generate_id("task"),
            tenant_id=schedule.tenant_id,
            equipment_id=schedule.equipment_id,
            title=schedule.task_title or schedule.name,
            title_ar=schedule.task_title_ar or schedule.name_ar,
            description=schedule.task_description or schedule.description,
            description_ar=schedule.task_description_ar or schedule.description_ar,
            maintenance_type=schedule.maintenance_type,
            priority=schedule.default_priority,
            status=MaintenanceStatus.SCHEDULED,
            scheduled_date=scheduled_date,
            due_date=scheduled_date + timedelta(days=7),  # Default 7 days to complete
            estimated_duration_hours=schedule.estimated_duration_hours,
            triggered_by_hours=equipment.total_hours if equipment and schedule.hours_interval else None,
            triggered_by_date=bool(schedule.calendar_interval_days),
            triggered_by_condition=triggered_by == "condition",
            checklist=checklist,
            parts_required=parts_required,
        )

        return task

    def generate_scheduled_tasks(
        self,
        start_date: datetime,
        end_date: datetime,
        equipment_id: str | None = None,
    ) -> list[ScheduledTask]:
        """
        Generate all scheduled tasks for a date range
        إنشاء جميع المهام المجدولة لنطاق تاريخ
        """
        scheduled_tasks: list[ScheduledTask] = []
        current_date = start_date

        for schedule in self._schedules.values():
            if not schedule.is_active:
                continue
            if equipment_id and schedule.equipment_id != equipment_id:
                continue

            equipment = self._equipment.get(schedule.equipment_id)
            if not equipment:
                continue

            # Calculate all occurrences in the date range
            next_due = self.calculate_next_due_date(schedule, equipment, current_date)

            while next_due and next_due <= end_date:
                task = ScheduledTask(
                    schedule_id=schedule.id,
                    equipment_id=schedule.equipment_id,
                    scheduled_date=next_due,
                    due_date=next_due + timedelta(days=7),
                    title=schedule.task_title or schedule.name,
                    title_ar=schedule.task_title_ar or schedule.name_ar,
                    description=schedule.task_description or schedule.description,
                    description_ar=schedule.task_description_ar or schedule.description_ar,
                    maintenance_type=schedule.maintenance_type,
                    priority=schedule.default_priority,
                    estimated_duration_hours=schedule.estimated_duration_hours,
                    checklist=schedule.checklist_template,
                    parts_required=schedule.typical_parts,
                    triggered_by="hours" if schedule.hours_interval else "calendar",
                )
                scheduled_tasks.append(task)

                # Calculate next occurrence
                if schedule.calendar_interval_days:
                    next_due = next_due + timedelta(days=schedule.calendar_interval_days)
                else:
                    break  # Hours-based schedules don't repeat in date range

        return sorted(scheduled_tasks, key=lambda t: t.scheduled_date)

    def detect_schedule_conflicts(
        self,
        start_date: datetime,
        end_date: datetime,
        equipment_id: str | None = None,
    ) -> list[ScheduleConflict]:
        """
        Detect scheduling conflicts in a date range
        اكتشاف تعارضات الجدولة في نطاق تاريخ
        """
        conflicts: list[ScheduleConflict] = []
        scheduled_tasks = self.generate_scheduled_tasks(start_date, end_date, equipment_id)

        # Group tasks by equipment and date
        tasks_by_equipment_date: dict[tuple[str, date], list[ScheduledTask]] = {}
        for task in scheduled_tasks:
            key = (task.equipment_id, task.scheduled_date.date())
            if key not in tasks_by_equipment_date:
                tasks_by_equipment_date[key] = []
            tasks_by_equipment_date[key].append(task)

        # Find days with multiple tasks for same equipment
        for (equip_id, task_date), tasks in tasks_by_equipment_date.items():
            if len(tasks) > 1:
                total_hours = sum(t.estimated_duration_hours for t in tasks)
                if total_hours > 8:  # More than a workday
                    conflict = ScheduleConflict(
                        schedule_id_1=tasks[0].schedule_id,
                        schedule_id_2=tasks[1].schedule_id,
                        conflict_date=tasks[0].scheduled_date,
                        equipment_id=equip_id,
                        conflict_type="workload_overload",
                        message=f"Total maintenance work ({total_hours:.1f}h) exceeds daily capacity on {task_date}",
                        message_ar=f"إجمالي أعمال الصيانة ({total_hours:.1f} ساعة) يتجاوز السعة اليومية في {task_date}",
                        resolution_suggestion="Consider spreading tasks across multiple days",
                        resolution_suggestion_ar="فكر في توزيع المهام على عدة أيام",
                    )
                    conflicts.append(conflict)

        return conflicts

    def get_workload_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        equipment_id: str | None = None,
    ) -> WorkloadSummary:
        """
        Get workload summary for a period
        الحصول على ملخص حجم العمل لفترة
        """
        scheduled_tasks = self.generate_scheduled_tasks(start_date, end_date, equipment_id)

        tasks_by_type: dict[str, int] = {}
        tasks_by_priority: dict[str, int] = {}
        tasks_by_equipment: dict[str, int] = {}
        tasks_by_date: dict[date, int] = {}
        total_hours = 0.0

        for task in scheduled_tasks:
            # Count by type
            type_key = task.maintenance_type.value
            tasks_by_type[type_key] = tasks_by_type.get(type_key, 0) + 1

            # Count by priority
            priority_key = task.priority.value
            tasks_by_priority[priority_key] = tasks_by_priority.get(priority_key, 0) + 1

            # Count by equipment
            tasks_by_equipment[task.equipment_id] = tasks_by_equipment.get(task.equipment_id, 0) + 1

            # Count by date
            task_date = task.scheduled_date.date()
            tasks_by_date[task_date] = tasks_by_date.get(task_date, 0) + 1

            # Sum hours
            total_hours += task.estimated_duration_hours

        # Find peak days
        peak_threshold = max(tasks_by_date.values()) if tasks_by_date else 0
        peak_days = [d for d, count in tasks_by_date.items() if count == peak_threshold]

        # Calculate average
        num_days = (end_date - start_date).days or 1
        avg_tasks = len(scheduled_tasks) / num_days

        return WorkloadSummary(
            period_start=start_date,
            period_end=end_date,
            total_tasks=len(scheduled_tasks),
            total_hours=total_hours,
            tasks_by_type=tasks_by_type,
            tasks_by_priority=tasks_by_priority,
            tasks_by_equipment=tasks_by_equipment,
            peak_days=peak_days,
            average_tasks_per_day=avg_tasks,
        )

    def update_schedule_after_completion(
        self,
        schedule_id: str,
        completed_at: datetime,
        hours_at_completion: float | None = None,
    ) -> None:
        """
        Update schedule after task completion
        تحديث الجدول بعد إتمام المهمة
        """
        if schedule_id not in self._schedules:
            return

        schedule = self._schedules[schedule_id]
        schedule.last_executed_at = completed_at
        schedule.execution_count += 1

        if hours_at_completion is not None:
            schedule.last_executed_hours = hours_at_completion
            if schedule.hours_interval:
                schedule.next_due_hours = hours_at_completion + schedule.hours_interval

        # Calculate next due date
        equipment = self._equipment.get(schedule.equipment_id)
        if equipment:
            schedule.next_due_at = self.calculate_next_due_date(schedule, equipment, completed_at)

        schedule.updated_at = datetime.now(UTC)

    def generate_maintenance_alerts(
        self,
        check_date: datetime | None = None,
    ) -> list[MaintenanceAlert]:
        """
        Generate maintenance alerts for all equipment
        إنشاء تنبيهات الصيانة لجميع المعدات
        """
        check_date = check_date or datetime.now(UTC)
        alerts: list[MaintenanceAlert] = []

        due_schedules = self.get_due_schedules(check_date=check_date, include_approaching=True)

        for schedule, trigger_reason in due_schedules:
            equipment = self._equipment.get(schedule.equipment_id)
            if not equipment:
                continue

            # Determine severity
            if trigger_reason.endswith("_exceeded"):
                severity = AlertSeverity.CRITICAL
            else:
                severity = AlertSeverity.WARNING

            # Create alert messages
            if "hours" in trigger_reason:
                hours_since = equipment.total_hours - (schedule.last_executed_hours or 0)
                message = f"Maintenance due at {schedule.hours_interval}h. Current: {hours_since:.0f}h"
                message_ar = f"الصيانة مستحقة عند {schedule.hours_interval} ساعة. الحالي: {hours_since:.0f} ساعة"
                trigger_value = f"{hours_since:.0f}h"
                threshold_value = f"{schedule.hours_interval}h"
            else:
                message = f"Scheduled maintenance is due: {schedule.name}"
                message_ar = f"الصيانة المجدولة مستحقة: {schedule.name_ar}"
                trigger_value = check_date.isoformat()
                threshold_value = schedule.next_due_at.isoformat() if schedule.next_due_at else ""

            alert = MaintenanceAlert(
                id=generate_id("alert"),
                tenant_id=schedule.tenant_id,
                equipment_id=schedule.equipment_id,
                alert_type=AlertType.SCHEDULED_DUE if "approaching" in trigger_reason else AlertType.OVERDUE,
                severity=severity,
                title=f"Maintenance Due: {schedule.name}",
                title_ar=f"صيانة مستحقة: {schedule.name_ar}",
                message=message,
                message_ar=message_ar,
                triggered_by="hours" if "hours" in trigger_reason else "calendar",
                trigger_value=trigger_value,
                threshold_value=threshold_value,
                schedule_id=schedule.id,
                recommended_action=f"Schedule {schedule.name} maintenance",
                recommended_action_ar=f"جدولة صيانة {schedule.name_ar}",
            )
            alerts.append(alert)

        return alerts
