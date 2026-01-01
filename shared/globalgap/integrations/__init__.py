"""
GlobalGAP Integration Adapters
محولات تكامل GlobalGAP

Integration adapters connecting GlobalGAP compliance management with existing SAHOOL services.
These adapters map service data to GlobalGAP requirements and generate compliance reports.

محولات التكامل التي تربط إدارة الامتثال لـ GlobalGAP مع خدمات سهول الحالية.
تربط هذه المحولات بيانات الخدمة بمتطلبات GlobalGAP وتولد تقارير الامتثال.

Integrations:
    - irrigation_integration: Links irrigation-smart with SPRING water management requirements
    - crop_health_integration: Links crop-health-ai with IPM documentation
    - fertilizer_integration: Links fertilizer-advisor with nutrient management plans
    - field_ops_integration: Links field-ops with traceability and harvest tracking

Usage:
    from shared.globalgap.integrations import (
        IrrigationIntegration,
        CropHealthIntegration,
        FertilizerIntegration,
        FieldOpsIntegration,
        GlobalGAPSubjects
    )

    # Irrigation integration
    async with IrrigationIntegration() as irrigation:
        await irrigation.record_irrigation_event(
            farm_id=uuid4(),
            tenant_id=uuid4(),
            water_volume_m3=150.0,
            water_source=WaterSource.WELL,
            irrigation_method=IrrigationMethod.DRIP
        )

        report = await irrigation.generate_water_usage_report(
            farm_id=uuid4(),
            tenant_id=uuid4(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            records=[...],
            total_irrigated_area_ha=10.5
        )

    # Crop health integration
    async with CropHealthIntegration() as crop_health:
        await crop_health.record_pest_detection(
            farm_id=uuid4(),
            tenant_id=uuid4(),
            pest_or_disease_name_en="Aphid",
            pest_category=PestCategory.INSECT,
            severity_level=SeverityLevel.MEDIUM,
            detection_method=DetectionMethod.AI_DETECTION
        )

        ipm_report = await crop_health.generate_ipm_report(
            farm_id=uuid4(),
            tenant_id=uuid4(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            detections=[...],
            ppp_applications=[...]
        )

    # Fertilizer integration
    async with FertilizerIntegration() as fertilizer:
        await fertilizer.record_fertilizer_application(
            farm_id=uuid4(),
            tenant_id=uuid4(),
            fertilizer_name="NPK 20-20-20",
            fertilizer_type=FertilizerType.INORGANIC,
            quantity_applied_kg=100.0,
            application_method=ApplicationMethod.BROADCAST,
            application_reason_en="Pre-planting application",
            based_on_soil_test=True,
            nutrient_plan_followed=True
        )

        plan = await fertilizer.generate_nutrient_management_plan(
            farm_id=uuid4(),
            tenant_id=uuid4(),
            crop_type="tomato",
            target_yield_kg_per_ha=50000,
            soil_test_date=date(2024, 1, 15),
            growing_season="2024-Spring"
        )

    # Field operations integration
    async with FieldOpsIntegration() as field_ops:
        batch = await field_ops.track_harvest_batch(
            farm_id=uuid4(),
            tenant_id=uuid4(),
            batch_number="BATCH-2024-001",
            product_name_en="Tomato",
            crop_type="tomato",
            harvest_date=date.today(),
            quantity_kg=1000.0,
            harvest_method=HarvestMethod.MANUAL
        )

        traceability = await field_ops.create_traceability_record(
            farm_id=uuid4(),
            tenant_id=uuid4(),
            batch_id=batch.id,
            batch_number=batch.batch_number,
            product_name_en="Tomato",
            ggn="4000000000001",
            planting_date=date(2024, 1, 1),
            harvest_date=date(2024, 6, 1),
            quantity_kg=1000.0
        )
"""

# ─────────────────────────────────────────────────────────────────────────────
# Event definitions and subjects
# ─────────────────────────────────────────────────────────────────────────────

from .events import (
    # Subject constants
    GlobalGAPSubjects,
    # Compliance events
    ComplianceUpdatedEvent,
    ComplianceRequirementFailedEvent,
    # Audit events
    AuditScheduledEvent,
    AuditCompletedEvent,
    # Non-conformance events
    NonConformanceDetectedEvent,
    CorrectiveActionCompletedEvent,
    # Certificate events
    CertificateExpiringEvent,
    CertificateIssuedEvent,
    # Integration-specific events
    WaterUsageRecordedEvent,
    IPMActivityRecordedEvent,
    FertilizerApplicationRecordedEvent,
    TraceabilityRecordCreatedEvent,
)

# ─────────────────────────────────────────────────────────────────────────────
# Irrigation Integration
# ─────────────────────────────────────────────────────────────────────────────

from .irrigation_integration import (
    # Enums
    WaterSource,
    IrrigationMethod,
    WaterQualityStatus,
    # Models
    WaterUsageRecord,
    WaterUsageReport,
    SPRINGCompliance,
    # Integration
    IrrigationIntegration,
)

# ─────────────────────────────────────────────────────────────────────────────
# Crop Health Integration
# ─────────────────────────────────────────────────────────────────────────────

from .crop_health_integration import (
    # Enums
    PestCategory,
    IPMActivityType,
    DetectionMethod,
    SeverityLevel,
    PPPType,
    # Models
    PestDetectionRecord,
    PPPApplicationRecord,
    IPMReport,
    # Integration
    CropHealthIntegration,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fertilizer Integration
# ─────────────────────────────────────────────────────────────────────────────

from .fertilizer_integration import (
    # Enums
    FertilizerType,
    ApplicationMethod,
    NutrientType,
    # Models
    FertilizerApplicationRecord,
    NutrientRequirement,
    NutrientManagementPlan,
    MRLComplianceCheck,
    # Integration
    FertilizerIntegration,
)

# ─────────────────────────────────────────────────────────────────────────────
# Field Operations Integration
# ─────────────────────────────────────────────────────────────────────────────

from .field_ops_integration import (
    # Enums
    ActivityType,
    HarvestMethod,
    PackagingType,
    # Models
    FieldActivity,
    HarvestBatch,
    TraceabilityRecord,
    ActivityComplianceMapping,
    # Integration
    FieldOpsIntegration,
)

# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # ─── Event definitions ───
    "GlobalGAPSubjects",
    # Compliance events
    "ComplianceUpdatedEvent",
    "ComplianceRequirementFailedEvent",
    # Audit events
    "AuditScheduledEvent",
    "AuditCompletedEvent",
    # Non-conformance events
    "NonConformanceDetectedEvent",
    "CorrectiveActionCompletedEvent",
    # Certificate events
    "CertificateExpiringEvent",
    "CertificateIssuedEvent",
    # Integration events
    "WaterUsageRecordedEvent",
    "IPMActivityRecordedEvent",
    "FertilizerApplicationRecordedEvent",
    "TraceabilityRecordCreatedEvent",
    # ─── Irrigation Integration ───
    "IrrigationIntegration",
    "WaterSource",
    "IrrigationMethod",
    "WaterQualityStatus",
    "WaterUsageRecord",
    "WaterUsageReport",
    "SPRINGCompliance",
    # ─── Crop Health Integration ───
    "CropHealthIntegration",
    "PestCategory",
    "IPMActivityType",
    "DetectionMethod",
    "SeverityLevel",
    "PPPType",
    "PestDetectionRecord",
    "PPPApplicationRecord",
    "IPMReport",
    # ─── Fertilizer Integration ───
    "FertilizerIntegration",
    "FertilizerType",
    "ApplicationMethod",
    "NutrientType",
    "FertilizerApplicationRecord",
    "NutrientRequirement",
    "NutrientManagementPlan",
    "MRLComplianceCheck",
    # ─── Field Operations Integration ───
    "FieldOpsIntegration",
    "ActivityType",
    "HarvestMethod",
    "PackagingType",
    "FieldActivity",
    "HarvestBatch",
    "TraceabilityRecord",
    "ActivityComplianceMapping",
]

# ─────────────────────────────────────────────────────────────────────────────
# Version
# ─────────────────────────────────────────────────────────────────────────────

__version__ = "1.0.0"
