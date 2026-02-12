"""
SAHOOL Equipment Maintenance Module - وحدة صيانة المعدات

A comprehensive equipment maintenance management module for agricultural equipment
providing maintenance scheduling, predictive maintenance, parts inventory tracking,
service history logging, and maintenance alerts.

Supported Equipment Types:
- Tractors (جرارات)
- Harvesters (حصادات)
- Irrigation Systems (أنظمة ري)
- Sprayers (رشاشات)
- And more...

Features:
- Maintenance schedule management (calendar, hours, and season-based)
- Predictive maintenance based on usage patterns and component health
- Spare parts inventory tracking with reorder alerts
- Service history logging with cost tracking
- Maintenance alerts with bilingual support (Arabic/English)

Usage:
    from shared.equipment_maintenance import (
        # Models
        Equipment,
        EquipmentType,
        EquipmentStatus,
        MaintenanceTask,
        MaintenanceSchedule,
        SparePart,
        ServiceRecord,
        MaintenanceAlert,

        # Scheduler
        MaintenanceScheduler,
        AgriculturalSeason,

        # Predictor
        PredictiveMaintenanceEngine,
        ComponentHealth,
        PredictiveInsight,
    )

    # Create scheduler
    scheduler = MaintenanceScheduler(tenant_id="farm_001")
    scheduler.register_equipment(my_tractor)
    scheduler.create_default_schedules(my_tractor)

    # Get due maintenance
    due_schedules = scheduler.get_due_schedules()

    # Create predictive engine
    predictor = PredictiveMaintenanceEngine(tenant_id="farm_001")
    predictor.register_equipment(my_tractor)

    # Get equipment health
    health = predictor.assess_equipment_health(my_tractor.id)

    # Get predictive insights
    insights = predictor.generate_insights(my_tractor.id)

Version: 1.0.0
"""

# ==============================================================================
# Models - نماذج البيانات
# ==============================================================================

from .models import (
    AlertSeverity,
    AlertType,
    ChecklistItem,
    Equipment,
    # Equipment models - نماذج المعدات
    EquipmentSpecs,
    EquipmentStatus,
    # Enumerations - التعدادات
    EquipmentType,
    FuelType,
    HarvesterMaintenanceProfile,
    IrrigationMaintenanceProfile,
    IrrigationType,
    # Alerts - التنبيهات
    MaintenanceAlert,
    MaintenancePart,
    MaintenancePriority,
    MaintenanceSchedule,
    MaintenanceStatus,
    # Maintenance task models - نماذج مهام الصيانة
    MaintenanceTask,
    MaintenanceType,
    PartCategory,
    PartRequirement,
    PartTransaction,
    # Service history - سجل الخدمة
    ServiceRecord,
    # Parts models - نماذج قطع الغيار
    SparePart,
    SprayerMaintenanceProfile,
    # Equipment profiles - ملفات تعريف المعدات
    TractorMaintenanceProfile,
    # Helper functions - دوال مساعدة
    generate_id,
    get_alert_severity_name,
    get_equipment_type_name,
    get_maintenance_type_name,
)

# ==============================================================================
# Predictor - التنبؤ
# ==============================================================================
from .predictor import (
    # Component data - بيانات المكونات
    COMPONENT_LIFE_HOURS,
    FAILURE_MODE_PROBABILITY,
    REPAIR_COST_SAR,
    ComponentHealth,
    ComponentType,
    CostOptimizationRecommendation,
    FailureMode,
    FailurePrediction,
    PredictiveInsight,
    # Main predictor class - فئة التنبؤ الرئيسية
    PredictiveMaintenanceEngine,
    # Enumerations - التعدادات
    RiskLevel,
    # Data classes - فئات البيانات
    UsageMetrics,
)

# ==============================================================================
# Scheduler - الجدولة
# ==============================================================================
from .scheduler import (
    # Season configurations - تكوينات الموسم
    MIDDLE_EAST_SEASONS,
    AgriculturalSeason,
    # Main scheduler class - فئة الجدولة الرئيسية
    MaintenanceScheduler,
    ScheduleConflict,
    # Data classes - فئات البيانات
    ScheduledTask,
    # Enumerations - التعدادات
    ScheduleFrequency,
    SeasonConfig,
    WorkloadSummary,
    get_default_harvester_schedules,
    get_default_irrigation_schedules,
    get_default_sprayer_schedules,
    # Default schedules - الجداول الافتراضية
    get_default_tractor_schedules,
)

# ==============================================================================
# Module Version and Info - إصدار ومعلومات الوحدة
# ==============================================================================

__version__ = "1.0.0"
__author__ = "SAHOOL Team"
__license__ = "Proprietary"

__all__ = [
    # Version
    "__version__",
    # Models - Enumerations
    "EquipmentType",
    "EquipmentStatus",
    "MaintenanceType",
    "MaintenanceStatus",
    "MaintenancePriority",
    "PartCategory",
    "AlertSeverity",
    "AlertType",
    "FuelType",
    "IrrigationType",
    # Models - Equipment
    "EquipmentSpecs",
    "Equipment",
    # Models - Maintenance
    "MaintenanceTask",
    "ChecklistItem",
    "MaintenanceSchedule",
    # Models - Parts
    "SparePart",
    "MaintenancePart",
    "PartRequirement",
    "PartTransaction",
    # Models - Service
    "ServiceRecord",
    # Models - Alerts
    "MaintenanceAlert",
    # Models - Profiles
    "TractorMaintenanceProfile",
    "HarvesterMaintenanceProfile",
    "IrrigationMaintenanceProfile",
    "SprayerMaintenanceProfile",
    # Models - Helpers
    "generate_id",
    "get_equipment_type_name",
    "get_maintenance_type_name",
    "get_alert_severity_name",
    # Scheduler - Enumerations
    "ScheduleFrequency",
    "AgriculturalSeason",
    # Scheduler - Data classes
    "ScheduledTask",
    "ScheduleConflict",
    "WorkloadSummary",
    "SeasonConfig",
    # Scheduler - Season configs
    "MIDDLE_EAST_SEASONS",
    # Scheduler - Default schedules
    "get_default_tractor_schedules",
    "get_default_harvester_schedules",
    "get_default_irrigation_schedules",
    "get_default_sprayer_schedules",
    # Scheduler - Main class
    "MaintenanceScheduler",
    # Predictor - Enumerations
    "RiskLevel",
    "ComponentType",
    "FailureMode",
    # Predictor - Data classes
    "UsageMetrics",
    "ComponentHealth",
    "PredictiveInsight",
    "FailurePrediction",
    "CostOptimizationRecommendation",
    # Predictor - Component data
    "COMPONENT_LIFE_HOURS",
    "FAILURE_MODE_PROBABILITY",
    "REPAIR_COST_SAR",
    # Predictor - Main class
    "PredictiveMaintenanceEngine",
]
