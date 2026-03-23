"""
Unit tests for SAHOOL Equipment Maintenance Module - اختبارات وحدة صيانة المعدات

Tests cover:
- Maintenance models
- Predictive maintenance
- Scheduling
- Component tracking
- Cost calculations

Version: 1.0.0
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Optional

import pytest

from shared.equipment_maintenance import (
    MIDDLE_EAST_SEASONS,
    AgriculturalSeason,
    AlertSeverity,
    AlertType,
    ChecklistItem,
    ComponentHealth,
    ComponentType,
    CostOptimizationRecommendation,
    Equipment,
    # Models - Equipment
    EquipmentSpecs,
    EquipmentStatus,
    # Models - Enumerations
    EquipmentType,
    FailureMode,
    FailurePrediction,
    FuelType,
    IrrigationType,
    # Models - Alerts
    MaintenanceAlert,
    MaintenancePart,
    MaintenancePriority,
    MaintenanceSchedule,
    MaintenanceScheduler,
    MaintenanceStatus,
    # Models - Maintenance
    MaintenanceTask,
    MaintenanceType,
    PartCategory,
    PartRequirement,
    PartTransaction,
    PredictiveMaintenanceEngine,
    # Predictor
    RiskLevel,
    # Scheduler
    ScheduleFrequency,
    # Models - Service
    ServiceRecord,
    # Models - Parts
    SparePart,
    UsageMetrics,
    # Models - Helpers
    generate_id,
    get_alert_severity_name,
    get_default_harvester_schedules,
    get_default_tractor_schedules,
    get_equipment_type_name,
    get_maintenance_type_name,
)

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_equipment_specs() -> EquipmentSpecs:
    """Create sample equipment specifications"""
    return EquipmentSpecs(
        manufacturer="John Deere",
        model="5075E",
        year=2022,
        serial_number="JD123456789",
        engine_power_hp=75,
        engine_power_kw=56,
        fuel_type=FuelType.DIESEL,
        fuel_capacity_l=80,
        fuel_consumption_l_hr=15,
        weight_kg=4500,
        length_m=4.5,
        width_m=2.3,
        height_m=2.8,
        working_width_m=2.0,
        oil_change_hours=250,
        filter_change_hours=500,
        major_service_hours=1000,
        overhaul_hours=5000,
    )


@pytest.fixture
def sample_tractor(sample_equipment_specs: EquipmentSpecs) -> Equipment:
    """Create sample tractor equipment"""
    return Equipment(
        id="tractor_001",
        tenant_id="farm_001",
        farm_id="farm_001",
        name="Main Tractor",
        name_ar="الجرار الرئيسي",
        equipment_type=EquipmentType.TRACTOR,
        specs=sample_equipment_specs,
        status=EquipmentStatus.OPERATIONAL,
        location="Field A",
        location_ar="الحقل أ",
        total_hours=1200.0,
        total_kilometers=5000.0,
        total_hectares=250.0,
        hours_since_last_oil_change=180.0,
        hours_since_last_filter_change=350.0,
        hours_since_last_major_service=700.0,
        hours_since_last_overhaul=2000.0,
        purchase_date=datetime(2022, 1, 1, tzinfo=UTC),
        purchase_price=Decimal("150000"),
        warranty_expiry=datetime(2025, 1, 1, tzinfo=UTC),
        is_active=True,
    )


@pytest.fixture
def sample_harvester(sample_equipment_specs: EquipmentSpecs) -> Equipment:
    """Create sample harvester equipment"""
    specs = EquipmentSpecs(
        manufacturer="CLAAS",
        model="LEXION 760",
        year=2021,
        serial_number="CLAAS987654321",
        engine_power_hp=450,
        engine_power_kw=340,
        fuel_type=FuelType.DIESEL,
        fuel_capacity_l=250,
        fuel_consumption_l_hr=60,
        weight_kg=18000,
        working_width_m=7.5,
        hopper_capacity_kg=9000,
        oil_change_hours=200,
        filter_change_hours=400,
        major_service_hours=500,
        overhaul_hours=2000,
    )
    return Equipment(
        id="harvester_001",
        tenant_id="farm_001",
        farm_id="farm_001",
        name="Combine Harvester",
        name_ar="حصادة الدمج",
        equipment_type=EquipmentType.HARVESTER,
        specs=specs,
        status=EquipmentStatus.IN_USE,
        total_hours=800.0,
        total_hectares=500.0,
        hours_since_last_oil_change=150.0,
        purchase_date=datetime(2021, 1, 1, tzinfo=UTC),
        purchase_price=Decimal("500000"),
        is_active=True,
    )


@pytest.fixture
def sample_irrigation_system() -> Equipment:
    """Create sample irrigation system"""
    specs = EquipmentSpecs(
        manufacturer="Netafim",
        model="Dripper System",
        year=2023,
        serial_number="NET111222333",
        fuel_type=FuelType.ELECTRIC,
        working_width_m=100.0,
        irrigation_type=IrrigationType.DRIP,
        flow_rate_m3_hr=5.0,
        coverage_area_ha=10.0,
        pressure_bar=2.0,
        oil_change_hours=0,
        filter_change_hours=500,
        major_service_hours=2000,
        overhaul_hours=10000,
    )
    return Equipment(
        id="irrigation_001",
        tenant_id="farm_001",
        farm_id="farm_001",
        name="Drip Irrigation System",
        name_ar="نظام الري بالتنقيط",
        equipment_type=EquipmentType.IRRIGATION_SYSTEM,
        specs=specs,
        status=EquipmentStatus.IDLE,
        total_hours=1500.0,
        hours_since_last_filter_change=200.0,
        purchase_date=datetime(2023, 1, 1, tzinfo=UTC),
        purchase_price=Decimal("50000"),
        is_active=True,
    )


@pytest.fixture
def sample_spare_part() -> SparePart:
    """Create sample spare part"""
    return SparePart(
        id="part_001",
        tenant_id="farm_001",
        part_number="OIL-FILTER-JD",
        name="Oil Filter",
        name_ar="فلتر الزيت",
        description="Engine oil filter for tractors",
        description_ar="فلتر زيت المحرك للجرارات",
        category=PartCategory.FILTERS,
        manufacturer="John Deere",
        compatible_equipment_types=[EquipmentType.TRACTOR],
        compatible_models=["5075E", "5090E"],
        quantity_on_hand=5,
        quantity_reserved=1,
        quantity_available=4,
        minimum_stock_level=2,
        reorder_level=3,
        reorder_quantity=10,
        maximum_stock_level=20,
        unit_cost=Decimal("150.00"),
        selling_price=Decimal("200.00"),
        lead_time_days=3,
    )


@pytest.fixture
def sample_maintenance_schedule(sample_tractor: Equipment) -> MaintenanceSchedule:
    """Create sample maintenance schedule"""
    return MaintenanceSchedule(
        id="sched_001",
        tenant_id="farm_001",
        equipment_id=sample_tractor.id,
        name="Oil Change",
        name_ar="تغيير الزيت",
        description="Regular oil and filter change",
        description_ar="تغيير الزيت والفلتر بانتظام",
        maintenance_type=MaintenanceType.PREVENTIVE,
        hours_interval=250,
        hours_warning_threshold=225,
        task_title="Engine Oil Change",
        task_title_ar="تغيير زيت المحرك",
        estimated_duration_hours=1.0,
        default_priority=MaintenancePriority.MEDIUM,
        estimated_cost=Decimal("500.00"),
        last_executed_at=datetime.now(UTC) - timedelta(days=30),
        last_executed_hours=950.0,
        next_due_hours=1200.0,
        is_active=True,
    )


# ==============================================================================
# Tests - Equipment Models
# ==============================================================================


@pytest.mark.unit
def test_equipment_model_creation(sample_tractor: Equipment):
    """Test equipment model creation and attributes"""
    assert sample_tractor.id == "tractor_001"
    assert sample_tractor.tenant_id == "farm_001"
    assert sample_tractor.equipment_type == EquipmentType.TRACTOR
    assert sample_tractor.status == EquipmentStatus.OPERATIONAL
    assert sample_tractor.total_hours == 1200.0
    assert sample_tractor.is_active is True


@pytest.mark.unit
def test_equipment_specs_to_dict(sample_equipment_specs: EquipmentSpecs):
    """Test equipment specs conversion to dictionary"""
    specs_dict = sample_equipment_specs.to_dict()

    assert specs_dict["manufacturer"] == "John Deere"
    assert specs_dict["model"] == "5075E"
    assert specs_dict["engine_power_hp"] == 75
    assert specs_dict["fuel_type"] == "diesel"
    assert "service_intervals" in specs_dict
    assert specs_dict["service_intervals"]["oil_change_hours"] == 250


@pytest.mark.unit
def test_equipment_to_dict(sample_tractor: Equipment):
    """Test equipment conversion to dictionary"""
    equip_dict = sample_tractor.to_dict()

    assert equip_dict["id"] == "tractor_001"
    assert equip_dict["equipment_type"] == "tractor"
    assert equip_dict["status"] == "operational"
    assert equip_dict["total_hours"] == 1200.0
    assert equip_dict["total_kilometers"] == 5000.0


@pytest.mark.unit
def test_equipment_maintenance_due_status(sample_tractor: Equipment):
    """Test equipment maintenance due status calculation"""
    status = sample_tractor.get_maintenance_due_status()

    assert "oil_change" in status
    assert "filter_change" in status
    assert "major_service" in status
    assert "overhaul" in status

    # Oil change is NOT approaching yet (180/250 = 72%, threshold is 90% = 225h)
    assert status["oil_change"]["percent_used"] == pytest.approx(72.0)
    assert status["oil_change"]["is_approaching"] is False
    assert status["oil_change"]["is_due"] is False

    # Filter is not approaching yet (350/500 = 70%, threshold is 90% = 450h)
    assert status["filter_change"]["percent_used"] == pytest.approx(70.0)
    assert status["filter_change"]["is_approaching"] is False

    # Major service is approaching (700/1000 = 70%, but hours remaining = 300)
    assert status["major_service"]["is_due"] is False


@pytest.mark.unit
def test_equipment_maintenance_approaching_due():
    """Test equipment maintenance when approaching due"""
    specs = EquipmentSpecs(
        manufacturer="Test",
        model="Test",
        year=2023,
        serial_number="TEST123",
        oil_change_hours=250,
        filter_change_hours=500,
        major_service_hours=1000,
        overhaul_hours=5000,
    )
    equipment = Equipment(
        id="test_equip",
        tenant_id="farm_001",
        farm_id="farm_001",
        name="Test Equipment",
        name_ar="معدة اختبار",
        equipment_type=EquipmentType.TRACTOR,
        specs=specs,
        hours_since_last_oil_change=230.0,  # 92% of 250
    )

    status = equipment.get_maintenance_due_status()
    assert status["oil_change"]["is_approaching"] is True
    assert status["oil_change"]["is_due"] is False


@pytest.mark.unit
def test_equipment_type_names():
    """Test equipment type name translations"""
    assert get_equipment_type_name(EquipmentType.TRACTOR, "en") == "Tractor"
    assert get_equipment_type_name(EquipmentType.TRACTOR, "ar") == "جرار"
    assert get_equipment_type_name(EquipmentType.HARVESTER, "en") == "Harvester"
    assert get_equipment_type_name(EquipmentType.HARVESTER, "ar") == "حصادة"
    assert get_equipment_type_name(EquipmentType.IRRIGATION_SYSTEM, "en") == "Irrigation System"


# ==============================================================================
# Tests - Maintenance Models
# ==============================================================================


@pytest.mark.unit
def test_maintenance_task_creation():
    """Test maintenance task creation"""
    task = MaintenanceTask(
        id="task_001",
        tenant_id="farm_001",
        equipment_id="tractor_001",
        title="Engine Oil Change",
        title_ar="تغيير زيت المحرك",
        description="Regular oil change procedure",
        maintenance_type=MaintenanceType.PREVENTIVE,
        priority=MaintenancePriority.MEDIUM,
        status=MaintenanceStatus.SCHEDULED,
        scheduled_date=datetime.now(UTC),
        due_date=datetime.now(UTC) + timedelta(days=7),
        estimated_duration_hours=1.5,
    )

    assert task.id == "task_001"
    assert task.maintenance_type == MaintenanceType.PREVENTIVE
    assert task.status == MaintenanceStatus.SCHEDULED
    assert task.is_overdue() is False


@pytest.mark.unit
def test_maintenance_task_is_overdue():
    """Test maintenance task overdue detection"""
    past_due_date = datetime.now(UTC) - timedelta(days=1)
    task = MaintenanceTask(
        id="task_001",
        tenant_id="farm_001",
        equipment_id="tractor_001",
        title="Test Task",
        title_ar="مهمة اختبار",
        status=MaintenanceStatus.PENDING,
        due_date=past_due_date,
    )

    assert task.is_overdue() is True

    # Completed tasks are never overdue
    task_completed = MaintenanceTask(
        id="task_002",
        tenant_id="farm_001",
        equipment_id="tractor_001",
        title="Completed Task",
        title_ar="مهمة مكتملة",
        status=MaintenanceStatus.COMPLETED,
        due_date=past_due_date,
    )
    assert task_completed.is_overdue() is False


@pytest.mark.unit
def test_maintenance_schedule_creation(sample_maintenance_schedule: MaintenanceSchedule):
    """Test maintenance schedule creation"""
    assert sample_maintenance_schedule.id == "sched_001"
    assert sample_maintenance_schedule.equipment_id == "tractor_001"
    assert sample_maintenance_schedule.hours_interval == 250
    assert sample_maintenance_schedule.is_active is True
    assert sample_maintenance_schedule.estimated_cost == Decimal("500.00")


@pytest.mark.unit
def test_checklist_item_creation():
    """Test checklist item creation"""
    item = ChecklistItem(
        id="chk_001",
        description="Check oil level",
        description_ar="تحقق من مستوى الزيت",
        is_completed=False,
    )

    assert item.id == "chk_001"
    assert item.is_completed is False

    # Mark as completed
    item.is_completed = True
    item.completed_at = datetime.now(UTC)
    item.completed_by = "tech_001"

    assert item.is_completed is True
    assert item.completed_at is not None


# ==============================================================================
# Tests - Parts and Inventory
# ==============================================================================


@pytest.mark.unit
def test_spare_part_creation(sample_spare_part: SparePart):
    """Test spare part creation"""
    assert sample_spare_part.id == "part_001"
    assert sample_spare_part.part_number == "OIL-FILTER-JD"
    assert sample_spare_part.category == PartCategory.FILTERS
    assert sample_spare_part.quantity_available == 4


@pytest.mark.unit
def test_spare_part_low_stock_detection(sample_spare_part: SparePart):
    """Test low stock detection"""
    # quantity_available=4, reorder_level=3
    # 4 <= 3 is False, so not low stock
    assert sample_spare_part.is_low_stock() is False

    # Set available to 3 (equal to reorder level)
    sample_spare_part.quantity_available = 3
    assert sample_spare_part.is_low_stock() is True

    # Set available to 2 (below reorder level)
    sample_spare_part.quantity_available = 2
    assert sample_spare_part.is_low_stock() is True

    # Add more stock (above reorder level)
    sample_spare_part.quantity_available = 5
    assert sample_spare_part.is_low_stock() is False


@pytest.mark.unit
def test_spare_part_out_of_stock():
    """Test out of stock detection"""
    part = SparePart(
        id="part_002",
        tenant_id="farm_001",
        part_number="FILTER-001",
        name="Air Filter",
        name_ar="فلتر الهواء",
        quantity_on_hand=0,
        quantity_available=0,
    )

    assert part.is_out_of_stock() is True
    assert part.is_low_stock() is True


@pytest.mark.unit
def test_spare_part_needs_reorder():
    """Test reorder requirement detection"""
    part = SparePart(
        id="part_003",
        tenant_id="farm_001",
        part_number="BELT-001",
        name="Drive Belt",
        name_ar="حزام القيادة",
        quantity_on_hand=2,
        reorder_level=5,
    )

    assert part.needs_reorder() is True


@pytest.mark.unit
def test_maintenance_part_creation():
    """Test maintenance part creation"""
    part = MaintenancePart(
        part_id="part_001",
        part_number="OIL-FILTER-JD",
        name="Oil Filter",
        name_ar="فلتر الزيت",
        quantity=1,
        unit_cost=Decimal("150.00"),
        total_cost=Decimal("150.00"),
        is_available=True,
        is_used=False,
    )

    assert part.part_number == "OIL-FILTER-JD"
    assert part.quantity == 1
    assert part.total_cost == Decimal("150.00")


@pytest.mark.unit
def test_part_transaction_creation():
    """Test part transaction creation"""
    transaction = PartTransaction(
        id="trans_001",
        tenant_id="farm_001",
        part_id="part_001",
        part_number="OIL-FILTER-JD",
        transaction_type="issue",
        quantity=1,
        quantity_before=5,
        quantity_after=4,
        unit_cost=Decimal("150.00"),
        total_cost=Decimal("150.00"),
        performed_by="tech_001",
        reason="Equipment maintenance",
        reason_ar="صيانة المعدات",
    )

    assert transaction.transaction_type == "issue"
    assert transaction.quantity_before == 5
    assert transaction.quantity_after == 4


# ==============================================================================
# Tests - Service Records
# ==============================================================================


@pytest.mark.unit
def test_service_record_creation():
    """Test service record creation"""
    parts = [
        MaintenancePart(
            part_id="part_001",
            part_number="OIL-FILTER-JD",
            name="Oil Filter",
            name_ar="فلتر الزيت",
            quantity=1,
            unit_cost=Decimal("150.00"),
            total_cost=Decimal("150.00"),
        )
    ]

    record = ServiceRecord(
        id="record_001",
        tenant_id="farm_001",
        equipment_id="tractor_001",
        service_date=datetime.now(UTC),
        service_type=MaintenanceType.PREVENTIVE,
        description="Regular oil change",
        description_ar="تغيير الزيت العادي",
        hours_at_service=1200.0,
        labor_hours=1.5,
        labor_cost=Decimal("300.00"),
        parts_used=parts,
        parts_cost=Decimal("150.00"),
        total_cost=Decimal("450.00"),
        technician_name="Ahmed Hassan",
        technician_name_ar="أحمد حسن",
        external_service=False,
    )

    assert record.id == "record_001"
    assert record.service_type == MaintenanceType.PREVENTIVE
    assert record.total_cost == Decimal("450.00")
    assert len(record.parts_used) == 1


# ==============================================================================
# Tests - Maintenance Alerts
# ==============================================================================


@pytest.mark.unit
def test_maintenance_alert_creation():
    """Test maintenance alert creation"""
    alert = MaintenanceAlert(
        id="alert_001",
        tenant_id="farm_001",
        equipment_id="tractor_001",
        alert_type=AlertType.SCHEDULED_DUE,
        severity=AlertSeverity.WARNING,
        title="Oil Change Due",
        title_ar="تغيير الزيت مستحق",
        message="Engine oil change is due at 1200 hours",
        message_ar="تغيير زيت المحرك مستحق عند 1200 ساعة",
    )

    assert alert.id == "alert_001"
    assert alert.alert_type == AlertType.SCHEDULED_DUE
    assert alert.severity == AlertSeverity.WARNING
    assert alert.is_active is True


@pytest.mark.unit
def test_alert_severity_names():
    """Test alert severity name translations"""
    assert get_alert_severity_name(AlertSeverity.INFO, "en") == "Information"
    assert get_alert_severity_name(AlertSeverity.INFO, "ar") == "معلومات"
    assert get_alert_severity_name(AlertSeverity.CRITICAL, "en") == "Critical"
    assert get_alert_severity_name(AlertSeverity.CRITICAL, "ar") == "حرج"


# ==============================================================================
# Tests - Maintenance Scheduler
# ==============================================================================


@pytest.mark.unit
def test_scheduler_creation():
    """Test maintenance scheduler creation"""
    scheduler = MaintenanceScheduler(tenant_id="farm_001")

    assert scheduler.tenant_id == "farm_001"
    assert scheduler.season_configs is not None


@pytest.mark.unit
def test_scheduler_register_equipment(sample_tractor: Equipment):
    """Test registering equipment with scheduler"""
    scheduler = MaintenanceScheduler(tenant_id="farm_001")
    scheduler.register_equipment(sample_tractor)

    assert sample_tractor.id in scheduler._equipment
    assert scheduler._equipment[sample_tractor.id] == sample_tractor


@pytest.mark.unit
def test_scheduler_add_and_retrieve_schedule(
    scheduler: MaintenanceScheduler,
    sample_maintenance_schedule: MaintenanceSchedule,
):
    """Test adding and retrieving schedules"""
    scheduler.add_schedule(sample_maintenance_schedule)

    retrieved = scheduler._schedules.get(sample_maintenance_schedule.id)
    assert retrieved is not None
    assert retrieved.id == sample_maintenance_schedule.id


@pytest.fixture
def scheduler(sample_tractor: Equipment) -> MaintenanceScheduler:
    """Create and setup scheduler with equipment"""
    scheduler = MaintenanceScheduler(tenant_id="farm_001")
    scheduler.register_equipment(sample_tractor)
    return scheduler


@pytest.mark.unit
def test_create_default_schedules_tractor(sample_tractor: Equipment):
    """Test creating default schedules for tractor"""
    scheduler = MaintenanceScheduler(tenant_id="farm_001")
    scheduler.register_equipment(sample_tractor)

    schedules = scheduler.create_default_schedules(sample_tractor)

    assert len(schedules) > 0
    assert all(s.equipment_id == sample_tractor.id for s in schedules)

    # Check for expected schedules
    schedule_names = [s.name for s in schedules]
    assert "Engine Oil Change" in schedule_names


@pytest.mark.unit
def test_create_default_schedules_harvester(sample_harvester: Equipment):
    """Test creating default schedules for harvester"""
    scheduler = MaintenanceScheduler(tenant_id="farm_001")
    scheduler.register_equipment(sample_harvester)

    schedules = scheduler.create_default_schedules(sample_harvester)

    assert len(schedules) > 0
    assert any("Harvester" in s.name or "Blade" in s.name for s in schedules)


@pytest.mark.unit
def test_get_current_season():
    """Test getting current agricultural season"""
    scheduler = MaintenanceScheduler(tenant_id="farm_001")

    # Test pre-planting season (Sep 1 - Oct 15)
    pre_plant_date = date(2024, 9, 15)
    season = scheduler.get_current_season(pre_plant_date)
    assert season == AgriculturalSeason.PRE_PLANTING

    # Test planting season (Oct 15 - Nov 30)
    plant_date = date(2024, 11, 1)
    season = scheduler.get_current_season(plant_date)
    assert season == AgriculturalSeason.PLANTING

    # Test growing season (Dec 1 - Mar 31)
    grow_date = date(2024, 1, 15)
    season = scheduler.get_current_season(grow_date)
    assert season == AgriculturalSeason.GROWING


@pytest.mark.unit
def test_calculate_next_due_date_hours_based(
    scheduler: MaintenanceScheduler,
    sample_tractor: Equipment,
    sample_maintenance_schedule: MaintenanceSchedule,
):
    """Test calculating next due date for hours-based schedule"""
    check_time = datetime.now(UTC)
    next_due = scheduler.calculate_next_due_date(
        sample_maintenance_schedule,
        sample_tractor,
        check_time,
    )

    # Should calculate based on hours (1000h at 8h/day = 125 days)
    assert next_due is not None
    # Should be in the future relative to the check time
    assert next_due >= check_time


@pytest.mark.unit
def test_calculate_next_due_hours(
    scheduler: MaintenanceScheduler,
    sample_tractor: Equipment,
    sample_maintenance_schedule: MaintenanceSchedule,
):
    """Test calculating next due hours"""
    next_due_hours = scheduler.calculate_next_due_hours(
        sample_maintenance_schedule,
        sample_tractor,
    )

    # Should be last_executed_hours + hours_interval
    assert next_due_hours == 950.0 + 250  # 1200


@pytest.mark.unit
def test_get_due_schedules(scheduler: MaintenanceScheduler, sample_tractor: Equipment):
    """Test getting due schedules"""
    # Create schedule that's due
    due_schedule = MaintenanceSchedule(
        id="sched_due",
        tenant_id="farm_001",
        equipment_id=sample_tractor.id,
        name="Oil Change",
        name_ar="تغيير الزيت",
        maintenance_type=MaintenanceType.PREVENTIVE,
        hours_interval=250,
        hours_warning_threshold=225,
        last_executed_hours=950.0,
        is_active=True,
    )

    # Register and add schedule
    scheduler.register_equipment(sample_tractor)
    scheduler.add_schedule(due_schedule)

    # Get due schedules - should be in due list
    due_schedules = scheduler.get_due_schedules()
    assert len(due_schedules) > 0


@pytest.mark.unit
def test_generate_task_from_schedule(
    scheduler: MaintenanceScheduler,
    sample_tractor: Equipment,
    sample_maintenance_schedule: MaintenanceSchedule,
):
    """Test generating maintenance task from schedule"""
    scheduler.register_equipment(sample_tractor)

    task = scheduler.generate_task_from_schedule(
        sample_maintenance_schedule,
        datetime.now(UTC),
    )

    assert task.id is not None
    assert task.equipment_id == sample_tractor.id
    assert task.title == sample_maintenance_schedule.task_title
    assert task.status == MaintenanceStatus.SCHEDULED


@pytest.mark.unit
def test_update_schedule_after_completion(
    scheduler: MaintenanceScheduler,
    sample_tractor: Equipment,
    sample_maintenance_schedule: MaintenanceSchedule,
):
    """Test updating schedule after task completion"""
    scheduler.register_equipment(sample_tractor)
    scheduler.add_schedule(sample_maintenance_schedule)

    completion_time = datetime.now(UTC)
    completion_hours = 1200.0

    scheduler.update_schedule_after_completion(
        sample_maintenance_schedule.id,
        completion_time,
        completion_hours,
    )

    updated = scheduler._schedules[sample_maintenance_schedule.id]
    assert updated.last_executed_at == completion_time
    assert updated.execution_count == 1


@pytest.mark.unit
def test_generate_maintenance_alerts(
    scheduler: MaintenanceScheduler,
    sample_tractor: Equipment,
):
    """Test generating maintenance alerts"""
    # Create a due schedule
    due_schedule = MaintenanceSchedule(
        id="sched_alert",
        tenant_id="farm_001",
        equipment_id=sample_tractor.id,
        name="Oil Change",
        name_ar="تغيير الزيت",
        maintenance_type=MaintenanceType.PREVENTIVE,
        hours_interval=250,
        last_executed_hours=950.0,
        is_active=True,
        task_title="Engine Oil Change",
        task_title_ar="تغيير زيت المحرك",
        task_description="Regular oil change",
        task_description_ar="تغيير الزيت العادي",
        estimated_duration_hours=1.0,
        default_priority=MaintenancePriority.MEDIUM,
    )

    scheduler.register_equipment(sample_tractor)
    scheduler.add_schedule(due_schedule)

    alerts = scheduler.generate_maintenance_alerts()

    # Should have at least one alert
    assert len(alerts) > 0
    assert all(isinstance(a, MaintenanceAlert) for a in alerts)


# ==============================================================================
# Tests - Predictive Maintenance
# ==============================================================================


@pytest.mark.unit
def test_predictor_creation():
    """Test predictive maintenance engine creation"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")

    assert engine.tenant_id == "farm_001"


@pytest.mark.unit
def test_predictor_register_equipment(sample_tractor: Equipment):
    """Test registering equipment with predictor"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    assert sample_tractor.id in engine._equipment


@pytest.mark.unit
def test_calculate_usage_metrics(
    sample_tractor: Equipment,
):
    """Test calculating usage metrics"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    metrics = engine.calculate_usage_metrics(sample_tractor.id, period_days=30)

    assert metrics is not None
    assert metrics.equipment_id == sample_tractor.id
    assert metrics.total_hours > 0
    assert metrics.avg_daily_hours > 0


@pytest.mark.unit
def test_assess_component_health_engine(sample_tractor: Equipment):
    """Test assessing component health"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    health = engine.assess_component_health(
        sample_tractor.id,
        ComponentType.ENGINE,
    )

    assert health.component_type == ComponentType.ENGINE
    assert health.equipment_id == sample_tractor.id
    assert 0 <= health.health_score <= 100
    assert 0 <= health.confidence <= 1
    assert health.risk_level in RiskLevel


@pytest.mark.unit
def test_assess_component_health_belts(sample_tractor: Equipment):
    """Test assessing belt component health"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    health = engine.assess_component_health(
        sample_tractor.id,
        ComponentType.BELTS,
    )

    assert health.component_type == ComponentType.BELTS
    # Belts have lower life expectancy (1500 hours)
    # At 1200 hours, belt health should show higher wear
    assert health.current_wear_percent > 50


@pytest.mark.unit
def test_assess_equipment_health(sample_tractor: Equipment):
    """Test assessing overall equipment health"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    health_list = engine.assess_equipment_health(sample_tractor.id)

    assert len(health_list) > 0
    assert all(isinstance(h, ComponentHealth) for h in health_list)

    # Should have risk levels from the enum
    risk_order_map = {
        RiskLevel.CRITICAL: 0,
        RiskLevel.HIGH: 1,
        RiskLevel.MODERATE: 2,
        RiskLevel.LOW: 3,
        RiskLevel.MINIMAL: 4,
    }

    # Verify sorted by risk level (highest risk first)
    for i in range(len(health_list) - 1):
        current_order = risk_order_map.get(health_list[i].risk_level, 5)
        next_order = risk_order_map.get(health_list[i + 1].risk_level, 5)
        assert current_order <= next_order, f"Risk levels not properly sorted at index {i}"


@pytest.mark.unit
def test_predict_failures(sample_tractor: Equipment):
    """Test failure prediction"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    predictions = engine.predict_failures(sample_tractor.id, horizon_days=90)

    # Should return list of predictions (may be empty for healthy equipment)
    assert isinstance(predictions, list)
    assert all(isinstance(p, FailurePrediction) for p in predictions)


@pytest.mark.unit
def test_generate_insights(sample_tractor: Equipment):
    """Test generating predictive insights"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    insights = engine.generate_insights(sample_tractor.id)

    # Should return list of insights
    assert isinstance(insights, list)
    assert all(hasattr(i, "id") for i in insights)
    assert all(hasattr(i, "title") for i in insights)


# ==============================================================================
# Tests - Cost Calculations
# ==============================================================================


@pytest.mark.unit
def test_maintenance_task_cost_calculation():
    """Test calculating maintenance task cost"""
    parts = [
        MaintenancePart(
            part_id="part_001",
            part_number="OIL-FILTER-JD",
            name="Oil Filter",
            name_ar="فلتر الزيت",
            quantity=1,
            unit_cost=Decimal("150.00"),
            total_cost=Decimal("150.00"),
        ),
        MaintenancePart(
            part_id="part_002",
            part_number="OIL-10W40",
            name="Engine Oil 10W-40",
            name_ar="زيت المحرك 10-40",
            quantity=5,
            unit_cost=Decimal("50.00"),
            total_cost=Decimal("250.00"),
        ),
    ]

    task = MaintenanceTask(
        id="task_001",
        tenant_id="farm_001",
        equipment_id="tractor_001",
        title="Oil Change",
        title_ar="تغيير الزيت",
        parts_required=parts,
        parts_cost=Decimal("400.00"),
        labor_cost=Decimal("200.00"),
        total_cost=Decimal("600.00"),
    )

    assert task.parts_cost == Decimal("400.00")
    assert task.labor_cost == Decimal("200.00")
    assert task.total_cost == Decimal("600.00")


@pytest.mark.unit
def test_service_record_cost_tracking():
    """Test service record cost tracking"""
    parts = [
        MaintenancePart(
            part_id="part_001",
            part_number="OIL-FILTER",
            name="Oil Filter",
            name_ar="فلتر الزيت",
            quantity=1,
            unit_cost=Decimal("150.00"),
            total_cost=Decimal("150.00"),
        )
    ]

    record = ServiceRecord(
        id="record_001",
        tenant_id="farm_001",
        equipment_id="tractor_001",
        parts_used=parts,
        parts_cost=Decimal("150.00"),
        labor_hours=2.0,
        labor_cost=Decimal("400.00"),
        total_cost=Decimal("550.00"),
    )

    assert record.parts_cost == Decimal("150.00")
    assert record.labor_hours == 2.0
    assert record.labor_cost == Decimal("400.00")
    assert record.total_cost == Decimal("550.00")


@pytest.mark.unit
def test_cost_optimization_recommendation(sample_tractor: Equipment):
    """Test cost optimization recommendation"""
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    recommendations = engine.get_cost_optimization_recommendations(sample_tractor.id)

    assert isinstance(recommendations, list)
    assert all(isinstance(r, CostOptimizationRecommendation) for r in recommendations)

    # Check recommendation structure
    for rec in recommendations:
        assert rec.equipment_id == sample_tractor.id
        assert rec.recommendation_type in ["timing", "bundling", "parts", "outsourcing"]
        assert rec.current_cost >= Decimal("0.00")
        assert rec.recommended_cost >= Decimal("0.00")


# ==============================================================================
# Tests - Helper Functions
# ==============================================================================


@pytest.mark.unit
def test_generate_id():
    """Test ID generation"""
    id1 = generate_id("test")
    id2 = generate_id("test")

    assert id1.startswith("test_")
    assert id2.startswith("test_")
    assert id1 != id2  # Should be unique


@pytest.mark.unit
def test_generate_id_without_prefix():
    """Test ID generation without prefix"""
    id1 = generate_id()
    id2 = generate_id()

    assert len(id1) == 12
    assert len(id2) == 12
    assert id1 != id2


@pytest.mark.unit
def test_maintenance_type_names():
    """Test maintenance type name translations"""
    assert get_maintenance_type_name(MaintenanceType.PREVENTIVE, "en") == "Preventive Maintenance"
    assert get_maintenance_type_name(MaintenanceType.PREVENTIVE, "ar") == "صيانة وقائية"
    assert get_maintenance_type_name(MaintenanceType.CORRECTIVE, "en") == "Corrective Maintenance"
    assert get_maintenance_type_name(MaintenanceType.CORRECTIVE, "ar") == "صيانة تصحيحية"


# ==============================================================================
# Tests - Integration Scenarios
# ==============================================================================


@pytest.mark.unit
def test_complete_maintenance_workflow(sample_tractor: Equipment):
    """Test complete maintenance workflow"""
    # 1. Create scheduler and register equipment
    scheduler = MaintenanceScheduler(tenant_id="farm_001")
    scheduler.register_equipment(sample_tractor)

    # 2. Create default schedules
    schedules = scheduler.create_default_schedules(sample_tractor)
    assert len(schedules) > 0

    # 3. Generate alerts
    alerts = scheduler.generate_maintenance_alerts()
    assert isinstance(alerts, list)

    # 4. Generate task from schedule
    task = scheduler.generate_task_from_schedule(schedules[0])
    assert task.id is not None

    # 5. Mark as completed
    scheduler.update_schedule_after_completion(
        schedules[0].id,
        datetime.now(UTC),
        sample_tractor.total_hours,
    )

    # 6. Verify update
    updated = scheduler._schedules[schedules[0].id]
    assert updated.execution_count == 1


@pytest.mark.unit
def test_predictive_maintenance_workflow(sample_tractor: Equipment):
    """Test predictive maintenance workflow"""
    # 1. Create predictor
    engine = PredictiveMaintenanceEngine(tenant_id="farm_001")
    engine.register_equipment(sample_tractor)

    # 2. Assess component health
    components = [ComponentType.ENGINE, ComponentType.BELTS, ComponentType.BEARINGS]
    for component in components:
        health = engine.assess_component_health(sample_tractor.id, component)
        assert health is not None

    # 3. Get overall equipment health
    health_list = engine.assess_equipment_health(sample_tractor.id)
    assert len(health_list) > 0

    # 4. Generate insights
    insights = engine.generate_insights(sample_tractor.id)
    assert isinstance(insights, list)

    # 5. Get cost optimization recommendations
    recommendations = engine.get_cost_optimization_recommendations(sample_tractor.id)
    assert isinstance(recommendations, list)


@pytest.mark.unit
def test_multi_equipment_maintenance_tracking():
    """Test tracking maintenance for multiple equipment"""
    # Create multiple equipment
    equipment_list = [
        Equipment(
            id=f"tractor_{i}",
            tenant_id="farm_001",
            farm_id="farm_001",
            name=f"Tractor {i}",
            name_ar=f"جرار {i}",
            equipment_type=EquipmentType.TRACTOR,
            specs=EquipmentSpecs(
                manufacturer="John Deere",
                model="5075E",
                year=2022,
                serial_number=f"JD{i:08d}",
            ),
            total_hours=float(i * 200),
        )
        for i in range(1, 4)
    ]

    # Create scheduler and register all
    scheduler = MaintenanceScheduler(tenant_id="farm_001")
    for equip in equipment_list:
        scheduler.register_equipment(equip)
        scheduler.create_default_schedules(equip)

    # Verify all registered
    assert len(scheduler._equipment) == 3
    assert len(scheduler._schedules) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
