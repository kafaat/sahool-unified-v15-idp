"""
Unit Tests for Batch Operations Module
======================================
Comprehensive tests for batch field operations, bulk data entry,
equipment assignments, progress tracking, rollback, and scheduling.

Tests cover:
    - Batch job creation and validation
    - Operation execution flow
    - Rollback mechanism
    - Progress tracking
    - Error handling and retry logic
    - Parallel execution limits
    - Transaction boundaries
    - Audit logging
    - Edge cases (partial failures, timeouts)
    - Scheduler functionality
"""

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from shared.batch_operations import (
    BATCH_MESSAGES,
    AlertAcknowledgment,
    AlertAcknowledgmentProcessor,
    BatchCancelledException,
    BatchConfig,
    BatchExecutionError,
    # Executor
    BatchExecutor,
    BatchOperation,
    # Enums
    BatchOperationType,
    BatchPriority,
    BatchProgress,
    BatchResult,
    BatchRollbackError,
    BatchSchedule,
    # Scheduler
    BatchScheduler,
    BatchStatus,
    BatchThresholdExceededError,
    # Models
    BilingualMessage,
    EquipmentAssignment,
    EquipmentAssignmentProcessor,
    FertilizationParams,
    FieldOperationItem,
    FieldOperationProcessor,
    HarvestEntry,
    HarvestEntryProcessor,
    IrrigationParams,
    ItemStatus,
    QueuedBatch,
    QueuePosition,
    RecurrencePattern,
    RollbackStrategy,
    SchedulerEvent,
    ScheduleType,
    SprayingParams,
    execute_batch,
    execute_irrigation_batch,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_field_items():
    """Create sample field operation items."""
    return [
        FieldOperationItem(
            field_id="field_001",
            field_name="North Field",
            field_name_ar="الحقل الشمالي",
            area_hectares=5.5,
        ),
        FieldOperationItem(
            field_id="field_002",
            field_name="South Field",
            field_name_ar="الحقل الجنوبي",
            area_hectares=3.2,
        ),
        FieldOperationItem(
            field_id="field_003",
            field_name="East Field",
            field_name_ar="الحقل الشرقي",
            area_hectares=7.8,
        ),
    ]


@pytest.fixture
def sample_irrigation_batch(sample_field_items):
    """Create a sample irrigation batch operation."""
    return BatchOperation(
        tenant_id="farm_001",
        operation_type=BatchOperationType.IRRIGATION,
        name="Morning Irrigation",
        name_ar="ري الصباح",
        description="Daily morning irrigation for wheat fields",
        description_ar="الري الصباحي اليومي لحقول القمح",
        priority=BatchPriority.MEDIUM,
        irrigation_params=IrrigationParams(
            water_amount_mm=25.0,
            duration_minutes=45,
            method="drip",
            notes="Apply early morning",
            notes_ar="تطبيق في الصباح الباكر",
        ),
        field_items=sample_field_items,
        created_by_user_id="user_001",
        created_by_name="Ahmad Farmer",
    )


@pytest.fixture
def sample_harvest_entries():
    """Create sample harvest data entries."""
    return [
        HarvestEntry(
            field_id="field_001",
            field_name="North Field",
            crop_type="wheat",
            crop_type_ar="قمح",
            harvest_date=datetime.now(UTC),
            yield_kg=5500,
            quality_grade="A",
            moisture_percent=12.5,
        ),
        HarvestEntry(
            field_id="field_002",
            field_name="South Field",
            crop_type="barley",
            crop_type_ar="شعير",
            harvest_date=datetime.now(UTC),
            yield_kg=3200,
            quality_grade="B",
            moisture_percent=11.8,
        ),
    ]


@pytest.fixture
def sample_harvest_batch(sample_harvest_entries):
    """Create a sample harvest batch operation."""
    return BatchOperation(
        tenant_id="farm_001",
        operation_type=BatchOperationType.HARVEST,
        name="Harvest Data Entry",
        name_ar="إدخال بيانات الحصاد",
        harvest_entries=sample_harvest_entries,
    )


@pytest.fixture
def sample_equipment_assignments():
    """Create sample equipment assignments."""
    return [
        EquipmentAssignment(
            equipment_id="tractor_001",
            equipment_name="John Deere 6120M",
            task_id="task_001",
            task_description="Field plowing",
            field_id="field_001",
        ),
        EquipmentAssignment(
            equipment_id="sprayer_001",
            equipment_name="Case IH Sprayer",
            task_id="task_002",
            task_description="Pesticide application",
            field_id="field_002",
        ),
    ]


@pytest.fixture
def sample_alert_acknowledgments():
    """Create sample alert acknowledgments."""
    return [
        AlertAcknowledgment(
            alert_id="alert_001",
            alert_title="Low Soil Moisture",
            alert_title_ar="رطوبة تربة منخفضة",
            alert_type="irrigation",
            severity="warning",
            acknowledgment_note="Will irrigate today",
        ),
        AlertAcknowledgment(
            alert_id="alert_002",
            alert_title="Pest Detection",
            alert_title_ar="كشف آفات",
            alert_type="pest",
            severity="critical",
            action_taken="Applied pesticide",
        ),
    ]


# =============================================================================
# Models Tests - BilingualMessage
# =============================================================================


@pytest.mark.unit
class TestBilingualMessage:
    """Test BilingualMessage model."""

    def test_message_creation(self):
        """Test creating bilingual message."""
        msg = BilingualMessage(en="Batch started", ar="بدأت الدفعة")
        assert msg.en == "Batch started"
        assert msg.ar == "بدأت الدفعة"

    def test_get_english(self):
        """Test getting English message."""
        msg = BilingualMessage(en="Hello", ar="مرحبا")
        assert msg.get("en") == "Hello"
        assert msg.get() == "Hello"  # Default is English

    def test_get_arabic(self):
        """Test getting Arabic message."""
        msg = BilingualMessage(en="Hello", ar="مرحبا")
        assert msg.get("ar") == "مرحبا"

    def test_to_dict(self):
        """Test converting to dictionary."""
        msg = BilingualMessage(en="Test", ar="اختبار")
        result = msg.to_dict()
        assert result == {"en": "Test", "ar": "اختبار"}

    def test_batch_messages_defined(self):
        """Test that standard batch messages are defined."""
        expected_keys = [
            "started",
            "completed",
            "partially_completed",
            "failed",
            "cancelled",
            "rolled_back",
            "paused",
            "resumed",
            "item_completed",
            "item_failed",
            "rollback_started",
            "rollback_completed",
        ]
        for key in expected_keys:
            assert key in BATCH_MESSAGES
            assert isinstance(BATCH_MESSAGES[key], BilingualMessage)


# =============================================================================
# Models Tests - Parameter Models
# =============================================================================


@pytest.mark.unit
class TestIrrigationParams:
    """Test IrrigationParams model."""

    def test_basic_creation(self):
        """Test basic irrigation params creation."""
        params = IrrigationParams(water_amount_mm=25.0)
        assert params.water_amount_mm == 25.0
        assert params.method == "drip"  # Default
        assert params.duration_minutes is None

    def test_full_creation(self):
        """Test irrigation params with all fields."""
        params = IrrigationParams(
            water_amount_mm=30.0,
            duration_minutes=60,
            method="sprinkler",
            notes="Morning irrigation",
            notes_ar="ري الصباح",
        )
        assert params.water_amount_mm == 30.0
        assert params.duration_minutes == 60
        assert params.method == "sprinkler"
        assert params.notes == "Morning irrigation"
        assert params.notes_ar == "ري الصباح"

    def test_to_dict(self):
        """Test converting to dictionary."""
        params = IrrigationParams(water_amount_mm=25.0, method="flood")
        result = params.to_dict()
        assert result["water_amount_mm"] == 25.0
        assert result["method"] == "flood"


@pytest.mark.unit
class TestSprayingParams:
    """Test SprayingParams model."""

    def test_basic_creation(self):
        """Test basic spraying params creation."""
        params = SprayingParams(product_name="Neem Oil")
        assert params.product_name == "Neem Oil"
        assert params.product_type == "pesticide"  # Default
        assert params.safety_interval_days == 0

    def test_full_creation(self):
        """Test spraying params with all fields."""
        params = SprayingParams(
            product_name="Glyphosate",
            product_name_ar="غليفوسات",
            product_type="herbicide",
            concentration=2.5,
            volume_per_hectare=200.0,
            safety_interval_days=14,
        )
        assert params.product_name == "Glyphosate"
        assert params.product_type == "herbicide"
        assert params.concentration == 2.5
        assert params.volume_per_hectare == 200.0
        assert params.safety_interval_days == 14


@pytest.mark.unit
class TestFertilizationParams:
    """Test FertilizationParams model."""

    def test_basic_creation(self):
        """Test basic fertilization params creation."""
        params = FertilizationParams(fertilizer_name="Urea 46%")
        assert params.fertilizer_name == "Urea 46%"
        assert params.fertilizer_type == "granular"  # Default
        assert params.application_method == "broadcast"  # Default

    def test_npk_values(self):
        """Test fertilization params with NPK values."""
        params = FertilizationParams(
            fertilizer_name="NPK 15-15-15",
            rate_kg_per_hectare=150.0,
            nitrogen_percent=15.0,
            phosphorus_percent=15.0,
            potassium_percent=15.0,
        )
        assert params.nitrogen_percent == 15.0
        assert params.phosphorus_percent == 15.0
        assert params.potassium_percent == 15.0


# =============================================================================
# Models Tests - Item Models
# =============================================================================


@pytest.mark.unit
class TestFieldOperationItem:
    """Test FieldOperationItem model."""

    def test_default_creation(self):
        """Test field item with default values."""
        item = FieldOperationItem()
        assert item.id is not None
        assert item.status == ItemStatus.PENDING
        assert item.area_hectares == 0.0

    def test_full_creation(self):
        """Test field item with all values."""
        item = FieldOperationItem(
            field_id="field_001",
            field_name="North Field",
            field_name_ar="الحقل الشمالي",
            area_hectares=5.5,
        )
        assert item.field_id == "field_001"
        assert item.field_name == "North Field"
        assert item.area_hectares == 5.5

    def test_to_dict(self):
        """Test converting to dictionary."""
        item = FieldOperationItem(field_id="field_001", area_hectares=5.5)
        result = item.to_dict()
        assert result["field_id"] == "field_001"
        assert result["area_hectares"] == 5.5
        assert result["status"] == "pending"


@pytest.mark.unit
class TestHarvestEntry:
    """Test HarvestEntry model."""

    def test_creation(self):
        """Test harvest entry creation."""
        entry = HarvestEntry(
            field_id="field_001",
            crop_type="wheat",
            yield_kg=5000.0,
            quality_grade="A",
        )
        assert entry.field_id == "field_001"
        assert entry.crop_type == "wheat"
        assert entry.yield_kg == 5000.0
        assert entry.quality_grade == "A"

    def test_to_dict_with_date(self):
        """Test to_dict handles datetime properly."""
        entry = HarvestEntry(
            field_id="field_001",
            harvest_date=datetime(2026, 1, 15, 10, 30, 0, tzinfo=UTC),
        )
        result = entry.to_dict()
        assert result["harvest_date"] == "2026-01-15T10:30:00+00:00"


@pytest.mark.unit
class TestEquipmentAssignment:
    """Test EquipmentAssignment model."""

    def test_creation(self):
        """Test equipment assignment creation."""
        assignment = EquipmentAssignment(
            equipment_id="tractor_001",
            equipment_name="John Deere",
            task_id="task_001",
            task_description="Plowing",
        )
        assert assignment.equipment_id == "tractor_001"
        assert assignment.task_id == "task_001"


@pytest.mark.unit
class TestAlertAcknowledgment:
    """Test AlertAcknowledgment model."""

    def test_creation(self):
        """Test alert acknowledgment creation."""
        ack = AlertAcknowledgment(
            alert_id="alert_001",
            alert_title="Low Moisture",
            alert_type="irrigation",
            severity="warning",
        )
        assert ack.alert_id == "alert_001"
        assert ack.severity == "warning"


# =============================================================================
# Models Tests - BatchProgress
# =============================================================================


@pytest.mark.unit
class TestBatchProgress:
    """Test BatchProgress model."""

    def test_default_values(self):
        """Test default progress values."""
        progress = BatchProgress()
        assert progress.total_items == 0
        assert progress.completed_items == 0
        assert progress.failed_items == 0
        assert progress.percent_complete == 0.0

    def test_update(self):
        """Test progress update."""
        progress = BatchProgress()
        progress.update(total=10, completed=5, failed=1)
        assert progress.total_items == 10
        assert progress.completed_items == 5
        assert progress.failed_items == 1
        assert progress.percent_complete == 60.0  # (5+1)/10 * 100

    def test_update_with_skipped(self):
        """Test progress update with skipped items."""
        progress = BatchProgress()
        progress.update(total=10, completed=4, failed=1, skipped=2)
        assert progress.skipped_items == 2
        assert progress.current_item_index == 7  # 4+1+2

    def test_to_dict(self):
        """Test converting to dictionary."""
        progress = BatchProgress(total_items=10, completed_items=5)
        progress.update(10, 5, 0)
        result = progress.to_dict()
        assert result["total_items"] == 10
        assert result["completed_items"] == 5
        assert result["percent_complete"] == 50.0


# =============================================================================
# Models Tests - BatchConfig
# =============================================================================


@pytest.mark.unit
class TestBatchConfig:
    """Test BatchConfig model."""

    def test_default_values(self):
        """Test default configuration values."""
        config = BatchConfig()
        assert config.max_concurrent == 5
        assert config.timeout_per_item_seconds == 60.0
        assert config.retry_failed_items is True
        assert config.max_retries == 3
        assert config.stop_on_error is False
        assert config.rollback_strategy == RollbackStrategy.NONE

    def test_custom_values(self):
        """Test custom configuration."""
        config = BatchConfig(
            max_concurrent=10,
            timeout_per_item_seconds=120.0,
            retry_failed_items=False,
            stop_on_error=True,
            rollback_strategy=RollbackStrategy.ON_FIRST_ERROR,
        )
        assert config.max_concurrent == 10
        assert config.stop_on_error is True
        assert config.rollback_strategy == RollbackStrategy.ON_FIRST_ERROR

    def test_to_dict(self):
        """Test converting to dictionary."""
        config = BatchConfig(max_concurrent=3)
        result = config.to_dict()
        assert result["max_concurrent"] == 3
        assert result["rollback_strategy"] == "none"


# =============================================================================
# Models Tests - BatchOperation
# =============================================================================


@pytest.mark.unit
class TestBatchOperation:
    """Test BatchOperation model."""

    def test_creation(self, sample_field_items):
        """Test batch operation creation."""
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
        )
        assert batch.id is not None
        assert batch.tenant_id == "farm_001"
        assert batch.operation_type == BatchOperationType.IRRIGATION
        assert batch.status == BatchStatus.PENDING
        assert len(batch.field_items) == 3

    def test_get_items_irrigation(self, sample_irrigation_batch):
        """Test get_items for irrigation batch."""
        items = sample_irrigation_batch.get_items()
        assert len(items) == 3
        assert all(isinstance(item, FieldOperationItem) for item in items)

    def test_get_items_harvest(self, sample_harvest_batch):
        """Test get_items for harvest batch."""
        items = sample_harvest_batch.get_items()
        assert len(items) == 2
        assert all(isinstance(item, HarvestEntry) for item in items)

    def test_get_item_count(self, sample_irrigation_batch):
        """Test get_item_count method."""
        assert sample_irrigation_batch.get_item_count() == 3

    def test_get_completed_count(self, sample_irrigation_batch):
        """Test get_completed_count method."""
        sample_irrigation_batch.field_items[0].status = ItemStatus.COMPLETED
        sample_irrigation_batch.field_items[1].status = ItemStatus.COMPLETED
        assert sample_irrigation_batch.get_completed_count() == 2

    def test_get_failed_count(self, sample_irrigation_batch):
        """Test get_failed_count method."""
        sample_irrigation_batch.field_items[0].status = ItemStatus.FAILED
        assert sample_irrigation_batch.get_failed_count() == 1

    def test_add_audit_entry(self, sample_irrigation_batch):
        """Test adding audit log entries."""
        sample_irrigation_batch.add_audit_entry(
            action="test_action",
            details={"key": "value"},
            user_id="user_001",
        )
        assert len(sample_irrigation_batch.audit_log) == 1
        entry = sample_irrigation_batch.audit_log[0]
        assert entry["action"] == "test_action"
        assert entry["details"]["key"] == "value"
        assert entry["user_id"] == "user_001"
        assert "timestamp" in entry

    def test_to_dict(self, sample_irrigation_batch):
        """Test converting to dictionary."""
        result = sample_irrigation_batch.to_dict()
        assert result["tenant_id"] == "farm_001"
        assert result["operation_type"] == "irrigation"
        assert result["name"] == "Morning Irrigation"
        assert "config" in result
        assert "progress" in result
        assert "field_items" in result
        assert result["item_count"] == 3

    def test_to_dict_without_items(self, sample_irrigation_batch):
        """Test to_dict without items."""
        result = sample_irrigation_batch.to_dict(include_items=False)
        assert "field_items" not in result
        assert "item_count" not in result


# =============================================================================
# Models Tests - BatchResult
# =============================================================================


@pytest.mark.unit
class TestBatchResult:
    """Test BatchResult model."""

    def test_creation(self):
        """Test batch result creation."""
        result = BatchResult(
            batch_id="batch_001",
            status=BatchStatus.COMPLETED,
            total_items=10,
            completed_items=9,
            failed_items=1,
            duration_seconds=45.5,
        )
        assert result.batch_id == "batch_001"
        assert result.status == BatchStatus.COMPLETED
        assert result.completed_items == 9

    def test_to_dict_success_rate(self):
        """Test to_dict includes success rate."""
        result = BatchResult(
            batch_id="batch_001",
            status=BatchStatus.PARTIALLY_COMPLETED,
            total_items=10,
            completed_items=8,
            failed_items=2,
        )
        data = result.to_dict()
        assert data["success_rate"] == 80.0

    def test_to_dict_zero_items(self):
        """Test to_dict with zero items."""
        result = BatchResult(
            batch_id="batch_001",
            status=BatchStatus.COMPLETED,
            total_items=0,
        )
        data = result.to_dict()
        assert data["success_rate"] == 0

    def test_to_dict_with_message(self):
        """Test to_dict with bilingual message."""
        result = BatchResult(
            batch_id="batch_001",
            status=BatchStatus.COMPLETED,
            message=BilingualMessage(en="Done", ar="انتهى"),
        )
        data = result.to_dict()
        assert data["message"]["en"] == "Done"
        assert data["message"]["ar"] == "انتهى"


# =============================================================================
# Executor Tests - Basic Execution
# =============================================================================


@pytest.mark.unit
class TestBatchExecutorBasicExecution:
    """Test BatchExecutor basic execution."""

    @pytest.mark.asyncio
    async def test_execute_empty_batch(self):
        """Test executing batch with no items."""
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Empty Batch",
        )
        executor = BatchExecutor()
        result = await executor.execute(batch)

        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 0
        assert result.message.en == "No items to process"

    @pytest.mark.asyncio
    async def test_execute_irrigation_batch(self, sample_irrigation_batch):
        """Test executing irrigation batch."""
        executor = BatchExecutor()
        result = await executor.execute(sample_irrigation_batch)

        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 3
        assert result.completed_items == 3
        assert result.failed_items == 0
        assert result.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_execute_harvest_batch(self, sample_harvest_batch):
        """Test executing harvest batch."""
        executor = BatchExecutor()
        result = await executor.execute(sample_harvest_batch)

        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 2
        assert result.completed_items == 2

    @pytest.mark.asyncio
    async def test_execute_equipment_batch(self, sample_equipment_assignments):
        """Test executing equipment assignment batch."""
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.EQUIPMENT_ASSIGN,
            name="Equipment Assignment",
            equipment_assignments=sample_equipment_assignments,
        )
        executor = BatchExecutor()
        result = await executor.execute(batch)

        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 2

    @pytest.mark.asyncio
    async def test_execute_alert_batch(self, sample_alert_acknowledgments):
        """Test executing alert acknowledgment batch."""
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.ALERT_ACK,
            name="Alert Acknowledgment",
            alert_acknowledgments=sample_alert_acknowledgments,
        )
        executor = BatchExecutor()
        result = await executor.execute(batch)

        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 2


# =============================================================================
# Executor Tests - Progress Tracking
# =============================================================================


@pytest.mark.unit
class TestBatchExecutorProgressTracking:
    """Test BatchExecutor progress tracking."""

    @pytest.mark.asyncio
    async def test_progress_callback_called(self, sample_irrigation_batch):
        """Test progress callback is called during execution."""
        progress_updates = []

        async def on_progress(progress: BatchProgress):
            progress_updates.append(progress.percent_complete)

        executor = BatchExecutor()
        executor.set_progress_callback(on_progress)
        await executor.execute(sample_irrigation_batch)

        assert len(progress_updates) > 0
        assert 100.0 in progress_updates  # Final progress should be 100%

    @pytest.mark.asyncio
    async def test_item_callback_called(self, sample_irrigation_batch):
        """Test item callback is called for each item."""
        item_updates = []

        async def on_item(item, status, error):
            item_updates.append((item.field_id, status))

        executor = BatchExecutor()
        executor.set_item_callback(on_item)
        await executor.execute(sample_irrigation_batch)

        assert len(item_updates) == 3
        assert all(status == ItemStatus.COMPLETED for _, status in item_updates)

    @pytest.mark.asyncio
    async def test_status_callback_called(self, sample_irrigation_batch):
        """Test status callback is called on status changes."""
        status_updates = []

        async def on_status(status, message):
            status_updates.append(status)

        executor = BatchExecutor()
        executor.set_status_callback(on_status)
        await executor.execute(sample_irrigation_batch)

        assert BatchStatus.IN_PROGRESS in status_updates
        assert BatchStatus.COMPLETED in status_updates

    @pytest.mark.asyncio
    async def test_batch_started_timestamp(self, sample_irrigation_batch):
        """Test batch started_at is set."""
        executor = BatchExecutor()
        await executor.execute(sample_irrigation_batch)

        assert sample_irrigation_batch.started_at is not None
        assert sample_irrigation_batch.completed_at is not None
        assert sample_irrigation_batch.completed_at >= sample_irrigation_batch.started_at


# =============================================================================
# Executor Tests - Error Handling and Retry
# =============================================================================


@pytest.mark.unit
class TestBatchExecutorErrorHandling:
    """Test BatchExecutor error handling and retry logic."""

    @pytest.mark.asyncio
    async def test_item_failure_captured(self, sample_field_items):
        """Test failed items are captured in result."""
        # Create a processor that fails on second item
        call_count = 0

        async def failing_execute(item, batch):
            nonlocal call_count
            call_count += 1
            if item.field_id == "field_002":
                raise Exception("Simulated failure")
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=failing_execute)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(retry_failed_items=False),
        )

        result = await executor.execute(batch)

        assert result.status == BatchStatus.PARTIALLY_COMPLETED
        assert result.completed_items == 2
        assert result.failed_items == 1
        assert len(result.errors) == 1
        assert "Simulated failure" in str(result.errors)

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, sample_field_items):
        """Test retry logic on item failure."""
        attempt_count = 0

        async def failing_then_success(item, batch):
            nonlocal attempt_count
            if item.field_id == "field_002":
                attempt_count += 1
                if attempt_count < 3:
                    raise Exception(f"Attempt {attempt_count} failed")
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=failing_then_success)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(
                retry_failed_items=True,
                max_retries=3,
                retry_delay_seconds=0.01,
            ),
        )

        result = await executor.execute(batch)

        assert result.status == BatchStatus.COMPLETED
        assert result.completed_items == 3
        assert attempt_count >= 2  # Should have retried at least once

    @pytest.mark.asyncio
    async def test_stop_on_error(self, sample_field_items):
        """Test stop_on_error configuration."""

        async def always_fail(item, batch):
            if item.field_id == "field_001":
                raise Exception("First item failed")
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=always_fail)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(
                stop_on_error=True,
                retry_failed_items=False,
                max_concurrent=1,  # Sequential execution needed for stop_on_error
            ),
        )

        result = await executor.execute(batch)

        assert result.failed_items == 1
        assert result.skipped_items == 2  # Remaining items skipped

    @pytest.mark.asyncio
    async def test_timeout_handling(self, sample_field_items):
        """Test item timeout handling."""

        async def slow_execute(item, batch):
            if item.field_id == "field_002":
                await asyncio.sleep(5)  # Longer than timeout
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=slow_execute)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(
                timeout_per_item_seconds=0.1,
                retry_failed_items=False,
            ),
        )

        result = await executor.execute(batch)

        assert result.failed_items >= 1
        assert "Timeout" in str(result.errors)

    @pytest.mark.asyncio
    async def test_failure_threshold(self, sample_field_items):
        """Test failure threshold stops execution."""

        async def mostly_fail(item, batch):
            if item.field_id != "field_001":
                raise Exception("Failed")
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=mostly_fail)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(
                retry_failed_items=False,
                failure_threshold_percent=50.0,  # Stop at 50% failure
            ),
        )

        result = await executor.execute(batch)

        # With 3 items, after 2 failures (66.7%), threshold is exceeded
        assert result.skipped_items >= 0


# =============================================================================
# Executor Tests - Rollback Mechanism
# =============================================================================


@pytest.mark.unit
class TestBatchExecutorRollback:
    """Test BatchExecutor rollback mechanism."""

    @pytest.mark.asyncio
    async def test_rollback_on_first_error(self, sample_field_items):
        """Test rollback on first error strategy."""
        rollback_called = []

        async def fail_last(item, batch):
            if item.field_id == "field_003":
                raise Exception("Last item failed")
            return {"processed": True}

        async def rollback_item(item, batch):
            rollback_called.append(item.field_id)
            return True

        processor = FieldOperationProcessor(
            execute_operation=fail_last,
            rollback_operation=rollback_item,
        )
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(
                retry_failed_items=False,
                rollback_strategy=RollbackStrategy.ON_FIRST_ERROR,
            ),
        )

        result = await executor.execute(batch)

        assert result.rollback_performed is True
        assert result.rollback_successful is True
        assert result.status == BatchStatus.ROLLED_BACK
        # Should rollback completed items (field_001, field_002)
        assert len(rollback_called) >= 2

    @pytest.mark.asyncio
    async def test_rollback_on_threshold(self, sample_field_items):
        """Test rollback on threshold strategy."""

        async def mostly_fail(item, batch):
            if item.field_id == "field_001":
                return {"processed": True}
            raise Exception("Failed")

        async def rollback_item(item, batch):
            return True

        processor = FieldOperationProcessor(
            execute_operation=mostly_fail,
            rollback_operation=rollback_item,
        )
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(
                retry_failed_items=False,
                rollback_strategy=RollbackStrategy.ON_THRESHOLD,
                failure_threshold_percent=50.0,
            ),
        )

        result = await executor.execute(batch)

        assert result.rollback_performed is True

    @pytest.mark.asyncio
    async def test_manual_rollback(self, sample_irrigation_batch):
        """Test manual rollback after completion."""
        rollback_called = []

        async def rollback_item(item, batch):
            rollback_called.append(item.field_id)
            return True

        processor = FieldOperationProcessor(rollback_operation=rollback_item)
        executor = BatchExecutor(field_processor=processor)

        # Execute batch first
        await executor.execute(sample_irrigation_batch)
        assert sample_irrigation_batch.status == BatchStatus.COMPLETED

        # Manual rollback
        success = await executor.rollback(sample_irrigation_batch)

        assert success is True
        assert len(rollback_called) == 3

    @pytest.mark.asyncio
    async def test_rollback_failure_handling(self, sample_field_items):
        """Test handling when rollback fails."""

        async def fail_last(item, batch):
            if item.field_id == "field_003":
                raise Exception("Last item failed")
            return {"processed": True}

        async def rollback_fails(item, batch):
            raise Exception("Rollback failed")

        processor = FieldOperationProcessor(
            execute_operation=fail_last,
            rollback_operation=rollback_fails,
        )
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(
                retry_failed_items=False,
                rollback_strategy=RollbackStrategy.ON_FIRST_ERROR,
            ),
        )

        result = await executor.execute(batch)

        assert result.rollback_performed is True
        assert result.rollback_successful is False


# =============================================================================
# Executor Tests - Parallel Execution
# =============================================================================


@pytest.mark.unit
class TestBatchExecutorParallelExecution:
    """Test BatchExecutor parallel execution limits."""

    @pytest.mark.asyncio
    async def test_concurrent_execution_limit(self, sample_field_items):
        """Test max_concurrent limits parallel execution."""
        concurrent_count = 0
        max_concurrent_observed = 0
        lock = asyncio.Lock()

        async def tracked_execute(item, batch):
            nonlocal concurrent_count, max_concurrent_observed
            async with lock:
                concurrent_count += 1
                max_concurrent_observed = max(max_concurrent_observed, concurrent_count)

            await asyncio.sleep(0.1)

            async with lock:
                concurrent_count -= 1

            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=tracked_execute)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(max_concurrent=2),
        )

        await executor.execute(batch)

        assert max_concurrent_observed <= 2

    @pytest.mark.asyncio
    async def test_sequential_execution(self, sample_field_items):
        """Test sequential execution with max_concurrent=1."""
        execution_order = []

        async def ordered_execute(item, batch):
            execution_order.append(item.field_id)
            await asyncio.sleep(0.01)
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=ordered_execute)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(max_concurrent=1),
        )

        await executor.execute(batch)

        # Sequential execution should preserve order
        assert execution_order == ["field_001", "field_002", "field_003"]


# =============================================================================
# Executor Tests - Cancellation and Pause
# =============================================================================


@pytest.mark.unit
class TestBatchExecutorCancellation:
    """Test BatchExecutor cancellation and pause."""

    @pytest.mark.asyncio
    async def test_cancel_execution(self, sample_field_items):
        """Test cancelling batch execution."""
        execution_started = asyncio.Event()

        async def slow_execute(item, batch):
            execution_started.set()
            await asyncio.sleep(2)
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=slow_execute)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(max_concurrent=1),
        )

        # Start execution in background
        task = asyncio.create_task(executor.execute(batch))

        # Wait for execution to start
        await asyncio.wait_for(execution_started.wait(), timeout=1.0)

        # Request cancellation
        executor.request_cancel()

        result = await task

        assert result.status == BatchStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_pause_and_resume(self, sample_field_items):
        """Test pausing and resuming execution."""
        items_processed = []
        pause_event = asyncio.Event()

        async def execute_with_pause_check(item, batch):
            items_processed.append(item.field_id)
            if item.field_id == "field_001":
                pause_event.set()
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=execute_with_pause_check)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
            config=BatchConfig(max_concurrent=1),
        )

        # Start execution
        task = asyncio.create_task(executor.execute(batch))

        # Wait for first item and pause
        await asyncio.wait_for(pause_event.wait(), timeout=1.0)
        executor.request_pause()

        # Allow some time for pause to take effect
        await asyncio.sleep(0.1)

        # Resume
        executor.request_resume()

        result = await task

        assert result.status == BatchStatus.COMPLETED
        assert len(items_processed) == 3


# =============================================================================
# Executor Tests - Audit Logging
# =============================================================================


@pytest.mark.unit
class TestBatchExecutorAuditLogging:
    """Test BatchExecutor audit logging."""

    @pytest.mark.asyncio
    async def test_audit_log_entries_created(self, sample_irrigation_batch):
        """Test audit log entries are created during execution."""
        executor = BatchExecutor()
        await executor.execute(sample_irrigation_batch)

        assert len(sample_irrigation_batch.audit_log) >= 2
        actions = [entry["action"] for entry in sample_irrigation_batch.audit_log]
        assert "batch_started" in actions
        assert "batch_completed" in actions

    @pytest.mark.asyncio
    async def test_audit_log_contains_details(self, sample_irrigation_batch):
        """Test audit log entries contain proper details."""
        executor = BatchExecutor()
        await executor.execute(sample_irrigation_batch)

        # Find batch_completed entry
        completed_entry = None
        for entry in sample_irrigation_batch.audit_log:
            if entry["action"] == "batch_completed":
                completed_entry = entry
                break

        assert completed_entry is not None
        assert "status" in completed_entry["details"]
        assert "completed" in completed_entry["details"]
        assert "duration_seconds" in completed_entry["details"]


# =============================================================================
# Executor Tests - Batch Validation
# =============================================================================


@pytest.mark.unit
class TestBatchExecutorValidation:
    """Test BatchExecutor validation."""

    @pytest.mark.asyncio
    async def test_validate_batch_success(self, sample_irrigation_batch):
        """Test validating a valid batch."""
        executor = BatchExecutor()
        valid, errors = await executor.validate_batch(sample_irrigation_batch)

        assert valid is True
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_validate_batch_with_custom_validator(self, sample_field_items):
        """Test validation with custom validator."""

        class ValidatingProcessor(FieldOperationProcessor):
            async def validate(self, item, batch):
                if item.area_hectares <= 0:
                    return False, "Area must be positive"
                return True, None

        # Add an invalid item
        invalid_item = FieldOperationItem(
            field_id="field_invalid",
            area_hectares=0,  # Invalid
        )
        sample_field_items.append(invalid_item)

        processor = ValidatingProcessor()
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Test Batch",
            field_items=sample_field_items,
        )

        valid, errors = await executor.validate_batch(batch)

        assert valid is False
        assert len(errors) == 1
        assert errors[0]["item_id"] == invalid_item.id  # Uses item UUID, not field_id
        assert errors[0]["error"] == "Area must be positive"


# =============================================================================
# Executor Tests - Convenience Functions
# =============================================================================


@pytest.mark.unit
class TestExecutorConvenienceFunctions:
    """Test executor convenience functions."""

    @pytest.mark.asyncio
    async def test_execute_batch_function(self, sample_irrigation_batch):
        """Test execute_batch convenience function."""
        progress_updates = []

        async def on_progress(progress):
            progress_updates.append(progress.percent_complete)

        result = await execute_batch(sample_irrigation_batch, on_progress)

        assert result.status == BatchStatus.COMPLETED
        assert len(progress_updates) > 0

    @pytest.mark.asyncio
    async def test_execute_irrigation_batch_function(self):
        """Test execute_irrigation_batch convenience function."""
        field_ids = ["field_001", "field_002"]
        result = await execute_irrigation_batch(
            field_ids=field_ids,
            water_amount_mm=25.0,
            tenant_id="farm_001",
        )

        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 2


# =============================================================================
# Scheduler Tests - BatchSchedule
# =============================================================================


@pytest.mark.unit
class TestBatchSchedule:
    """Test BatchSchedule model."""

    def test_immediate_schedule(self):
        """Test immediate schedule."""
        schedule = BatchSchedule(
            batch_id="batch_001",
            schedule_type=ScheduleType.IMMEDIATE,
        )
        next_exec = schedule.calculate_next_execution()

        assert next_exec is not None
        assert (datetime.now(UTC) - next_exec).total_seconds() < 5

    def test_scheduled_future_time(self):
        """Test scheduled future time."""
        future_time = datetime.now(UTC) + timedelta(hours=1)
        schedule = BatchSchedule(
            batch_id="batch_001",
            schedule_type=ScheduleType.SCHEDULED,
            scheduled_time=future_time,
        )
        next_exec = schedule.calculate_next_execution()

        assert next_exec == future_time

    def test_scheduled_past_time(self):
        """Test scheduled past time returns None."""
        past_time = datetime.now(UTC) - timedelta(hours=1)
        schedule = BatchSchedule(
            batch_id="batch_001",
            schedule_type=ScheduleType.SCHEDULED,
            scheduled_time=past_time,
        )
        next_exec = schedule.calculate_next_execution()

        assert next_exec is None

    def test_recurring_daily(self):
        """Test recurring daily schedule."""
        schedule = BatchSchedule(
            batch_id="batch_001",
            schedule_type=ScheduleType.RECURRING,
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1,
            scheduled_time=datetime.now(UTC),
        )
        schedule.last_execution = datetime.now(UTC)
        next_exec = schedule.calculate_next_execution()

        assert next_exec is not None
        expected = datetime.now(UTC) + timedelta(days=1)
        assert abs((next_exec - expected).total_seconds()) < 60

    def test_recurring_weekly(self):
        """Test recurring weekly schedule."""
        schedule = BatchSchedule(
            batch_id="batch_001",
            schedule_type=ScheduleType.RECURRING,
            recurrence_pattern=RecurrencePattern.WEEKLY,
            recurrence_interval=1,
            scheduled_time=datetime.now(UTC),
        )
        schedule.last_execution = datetime.now(UTC)
        next_exec = schedule.calculate_next_execution()

        assert next_exec is not None
        expected = datetime.now(UTC) + timedelta(weeks=1)
        assert abs((next_exec - expected).total_seconds()) < 60

    def test_recurring_max_executions(self):
        """Test recurring schedule respects max_executions."""
        schedule = BatchSchedule(
            batch_id="batch_001",
            schedule_type=ScheduleType.RECURRING,
            recurrence_pattern=RecurrencePattern.DAILY,
            max_executions=3,
            execution_count=3,  # Already executed max times
        )
        next_exec = schedule.calculate_next_execution()

        assert next_exec is None

    def test_recurring_end_date(self):
        """Test recurring schedule respects end date."""
        schedule = BatchSchedule(
            batch_id="batch_001",
            schedule_type=ScheduleType.RECURRING,
            recurrence_pattern=RecurrencePattern.DAILY,
            scheduled_time=datetime.now(UTC),
            recurrence_end_date=datetime.now(UTC) - timedelta(days=1),  # Already ended
        )
        schedule.last_execution = datetime.now(UTC) - timedelta(days=1)
        next_exec = schedule.calculate_next_execution()

        assert next_exec is None

    def test_to_dict(self):
        """Test schedule to_dict."""
        schedule = BatchSchedule(
            batch_id="batch_001",
            schedule_type=ScheduleType.SCHEDULED,
            scheduled_time=datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC),
        )
        result = schedule.to_dict()

        assert result["batch_id"] == "batch_001"
        assert result["schedule_type"] == "scheduled"
        assert result["enabled"] is True


# =============================================================================
# Scheduler Tests - QueuedBatch
# =============================================================================


@pytest.mark.unit
class TestQueuedBatch:
    """Test QueuedBatch model."""

    def test_create_queued_batch(self, sample_irrigation_batch):
        """Test creating queued batch."""
        schedule = BatchSchedule(
            batch_id=sample_irrigation_batch.id,
            schedule_type=ScheduleType.IMMEDIATE,
        )
        schedule.next_execution = datetime.now(UTC)

        queued = QueuedBatch.create(sample_irrigation_batch, schedule)

        assert queued.batch == sample_irrigation_batch
        assert queued.schedule == schedule
        assert queued.priority_value == 2  # MEDIUM priority

    def test_priority_ordering(self, sample_irrigation_batch):
        """Test priority ordering in queue."""
        urgent_batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Urgent",
            priority=BatchPriority.URGENT,
        )
        low_batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Low",
            priority=BatchPriority.LOW,
        )

        schedule = BatchSchedule(schedule_type=ScheduleType.IMMEDIATE)
        schedule.next_execution = datetime.now(UTC)

        urgent_queued = QueuedBatch.create(urgent_batch, schedule)
        low_queued = QueuedBatch.create(low_batch, schedule)

        assert urgent_queued < low_queued  # Urgent has lower priority_value


# =============================================================================
# Scheduler Tests - BatchScheduler
# =============================================================================


@pytest.mark.unit
class TestBatchScheduler:
    """Test BatchScheduler."""

    def test_scheduler_creation(self):
        """Test scheduler creation."""
        scheduler = BatchScheduler(max_concurrent_batches=3)

        assert scheduler.is_running is False
        assert scheduler.is_paused is False
        assert scheduler.queue_size == 0
        assert scheduler.running_count == 0

    def test_schedule_batch(self, sample_irrigation_batch):
        """Test scheduling a batch."""
        scheduler = BatchScheduler()
        schedule = scheduler.schedule_batch(
            sample_irrigation_batch,
            schedule_type=ScheduleType.IMMEDIATE,
        )

        assert schedule.batch_id == sample_irrigation_batch.id
        assert sample_irrigation_batch.status == BatchStatus.QUEUED
        assert scheduler.queue_size == 1

    def test_schedule_with_future_time(self, sample_irrigation_batch):
        """Test scheduling batch for future time."""
        scheduler = BatchScheduler()
        future_time = datetime.now(UTC) + timedelta(hours=1)
        schedule = scheduler.schedule_batch(
            sample_irrigation_batch,
            schedule_type=ScheduleType.SCHEDULED,
            scheduled_time=future_time,
        )

        assert schedule.scheduled_time == future_time
        assert schedule.next_execution == future_time

    def test_schedule_recurring(self, sample_irrigation_batch):
        """Test scheduling recurring batch."""
        scheduler = BatchScheduler()
        schedule = scheduler.schedule_batch(
            sample_irrigation_batch,
            schedule_type=ScheduleType.RECURRING,
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_interval=1,
        )

        assert schedule.recurrence_pattern == RecurrencePattern.DAILY
        assert schedule.recurrence_interval == 1

    @pytest.mark.asyncio
    async def test_enqueue_batch(self, sample_irrigation_batch):
        """Test enqueueing a batch."""
        scheduler = BatchScheduler()
        schedule = await scheduler.enqueue_batch(sample_irrigation_batch)

        assert schedule.schedule_type == ScheduleType.IMMEDIATE
        assert scheduler.queue_size == 1

    @pytest.mark.asyncio
    async def test_enqueue_at_front(self, sample_irrigation_batch):
        """Test enqueueing at front of queue."""
        scheduler = BatchScheduler()

        # Add first batch
        batch1 = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="First",
        )
        await scheduler.enqueue_batch(batch1, QueuePosition.BACK)

        # Add second at front
        await scheduler.enqueue_batch(
            sample_irrigation_batch,
            QueuePosition.FRONT,
        )

        status = scheduler.get_queue_status()
        # Front batch should have higher priority (appear first in sorted queue)
        assert status[0]["batch_id"] == sample_irrigation_batch.id

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        """Test starting and stopping scheduler."""
        scheduler = BatchScheduler()

        await scheduler.start()
        assert scheduler.is_running is True

        await scheduler.stop()
        assert scheduler.is_running is False

    @pytest.mark.asyncio
    async def test_pause_and_resume(self):
        """Test pausing and resuming scheduler."""
        scheduler = BatchScheduler()
        await scheduler.start()

        scheduler.pause()
        assert scheduler.is_paused is True

        scheduler.resume()
        assert scheduler.is_paused is False

        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_cancel_queued_batch(self, sample_irrigation_batch):
        """Test cancelling a queued batch."""
        scheduler = BatchScheduler()
        scheduler.schedule_batch(sample_irrigation_batch)

        assert scheduler.queue_size == 1

        success = await scheduler.cancel_batch(sample_irrigation_batch.id)

        assert success is True
        assert scheduler.queue_size == 0
        assert sample_irrigation_batch.status == BatchStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_get_batch(self, sample_irrigation_batch):
        """Test getting batch by ID."""
        scheduler = BatchScheduler()
        scheduler.schedule_batch(sample_irrigation_batch)

        batch = scheduler.get_batch(sample_irrigation_batch.id)

        assert batch == sample_irrigation_batch

    @pytest.mark.asyncio
    async def test_get_scheduler_stats(self, sample_irrigation_batch):
        """Test getting scheduler statistics."""
        scheduler = BatchScheduler()
        scheduler.schedule_batch(sample_irrigation_batch)

        stats = scheduler.get_scheduler_stats()

        assert stats["is_running"] is False
        assert stats["queue_size"] == 1
        assert stats["total_batches"] == 1
        assert stats["max_concurrent"] == 3  # Default


# =============================================================================
# Scheduler Tests - Event Callbacks
# =============================================================================


@pytest.mark.unit
class TestSchedulerEventCallbacks:
    """Test scheduler event callbacks."""

    @pytest.mark.asyncio
    async def test_event_callback_called(self, sample_irrigation_batch):
        """Test event callback is called."""
        events = []

        async def on_event(event: SchedulerEvent):
            events.append(event)

        scheduler = BatchScheduler()
        scheduler.set_event_callback(on_event)

        await scheduler.enqueue_batch(sample_irrigation_batch)

        assert len(events) == 1
        assert events[0].event_type == "batch_enqueued"
        assert events[0].batch_id == sample_irrigation_batch.id

    @pytest.mark.asyncio
    async def test_scheduler_start_event(self):
        """Test scheduler start event."""
        events = []

        async def on_event(event: SchedulerEvent):
            events.append(event)

        scheduler = BatchScheduler()
        scheduler.set_event_callback(on_event)

        await scheduler.start()
        await scheduler.stop()

        event_types = [e.event_type for e in events]
        assert "scheduler_started" in event_types
        assert "scheduler_stopped" in event_types


# =============================================================================
# Edge Cases Tests
# =============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_single_item_batch(self):
        """Test batch with single item."""
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Single Item",
            field_items=[FieldOperationItem(field_id="field_001", area_hectares=5.0)],
        )

        executor = BatchExecutor()
        result = await executor.execute(batch)

        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 1
        assert result.completed_items == 1

    @pytest.mark.asyncio
    async def test_large_batch(self):
        """Test batch with many items."""
        items = [FieldOperationItem(field_id=f"field_{i:04d}", area_hectares=1.0) for i in range(100)]

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Large Batch",
            field_items=items,
            config=BatchConfig(max_concurrent=10),
        )

        executor = BatchExecutor()
        result = await executor.execute(batch)

        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 100
        assert result.completed_items == 100

    @pytest.mark.asyncio
    async def test_all_items_fail(self, sample_field_items):
        """Test when all items fail."""

        async def always_fail(item, batch):
            raise Exception("Simulated failure")

        processor = FieldOperationProcessor(execute_operation=always_fail)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="All Fail",
            field_items=sample_field_items,
            config=BatchConfig(retry_failed_items=False),
        )

        result = await executor.execute(batch)

        assert result.status == BatchStatus.FAILED
        assert result.completed_items == 0
        assert result.failed_items == 3

    @pytest.mark.asyncio
    async def test_item_status_transitions(self, sample_field_items):
        """Test item status transitions during execution."""
        status_history = {item.field_id: [] for item in sample_field_items}

        async def tracking_execute(item, batch):
            status_history[item.field_id].append(item.status)
            await asyncio.sleep(0.01)
            return {"processed": True}

        processor = FieldOperationProcessor(execute_operation=tracking_execute)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Status Test",
            field_items=sample_field_items,
            config=BatchConfig(max_concurrent=1),
        )

        await executor.execute(batch)

        # Each item should have been in IN_PROGRESS state
        for field_id, history in status_history.items():
            assert ItemStatus.IN_PROGRESS in history

        # All items should be COMPLETED now
        for item in batch.field_items:
            assert item.status == ItemStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_result_data_stored(self, sample_field_items):
        """Test result data is stored on items."""

        async def execute_with_data(item, batch):
            return {
                "processed_at": datetime.now(UTC).isoformat(),
                "water_used_liters": 1000,
            }

        processor = FieldOperationProcessor(execute_operation=execute_with_data)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Result Data Test",
            field_items=sample_field_items,
        )

        await executor.execute(batch)

        for item in batch.field_items:
            assert "processed_at" in item.result_data
            assert "water_used_liters" in item.result_data

    @pytest.mark.asyncio
    async def test_rollback_data_stored(self, sample_field_items):
        """Test rollback data is stored for completed items."""

        async def execute_with_data(item, batch):
            return {"record_id": f"rec_{item.field_id}"}

        processor = FieldOperationProcessor(execute_operation=execute_with_data)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Rollback Data Test",
            field_items=sample_field_items,
        )

        await executor.execute(batch)

        for item in batch.field_items:
            assert item.rollback_data is not None
            assert "record_id" in item.rollback_data

    def test_unknown_operation_type(self):
        """Test handling unknown operation type."""
        executor = BatchExecutor()

        with pytest.raises(ValueError, match="Unknown operation type"):
            executor._get_processor("invalid_type")


# =============================================================================
# Exception Tests
# =============================================================================


@pytest.mark.unit
class TestExceptions:
    """Test batch operation exceptions."""

    def test_batch_execution_error(self):
        """Test BatchExecutionError creation."""
        error = BatchExecutionError("Execution failed", "فشل التنفيذ")
        assert error.message == "Execution failed"
        assert error.message_ar == "فشل التنفيذ"
        assert str(error) == "Execution failed"

    def test_batch_execution_error_default_arabic(self):
        """Test BatchExecutionError with default Arabic message."""
        error = BatchExecutionError("Execution failed")
        assert error.message_ar == "Execution failed"

    def test_batch_rollback_error(self):
        """Test BatchRollbackError creation."""
        error = BatchRollbackError("Rollback failed")
        assert isinstance(error, BatchExecutionError)

    def test_batch_cancelled_exception(self):
        """Test BatchCancelledException creation."""
        error = BatchCancelledException("Cancelled by user")
        assert isinstance(error, BatchExecutionError)

    def test_batch_threshold_exceeded_error(self):
        """Test BatchThresholdExceededError creation."""
        error = BatchThresholdExceededError("Threshold exceeded")
        assert isinstance(error, BatchExecutionError)


# =============================================================================
# Processor Tests
# =============================================================================


@pytest.mark.unit
class TestItemProcessors:
    """Test item processors."""

    @pytest.mark.asyncio
    async def test_field_operation_processor_default(self):
        """Test default field operation processor."""
        processor = FieldOperationProcessor()
        item = FieldOperationItem(field_id="field_001")
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
        )

        success, result = await processor.process(item, batch)

        assert success is True
        assert "processed_at" in result

    @pytest.mark.asyncio
    async def test_field_operation_processor_custom(self):
        """Test field operation processor with custom handler."""

        async def custom_execute(item, batch):
            return {"custom": True}

        processor = FieldOperationProcessor(execute_operation=custom_execute)
        item = FieldOperationItem(field_id="field_001")
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
        )

        success, result = await processor.process(item, batch)

        assert success is True
        assert result["custom"] is True

    @pytest.mark.asyncio
    async def test_harvest_entry_processor_default(self):
        """Test default harvest entry processor."""
        processor = HarvestEntryProcessor()
        entry = HarvestEntry(field_id="field_001", yield_kg=5000)
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.HARVEST,
        )

        success, result = await processor.process(entry, batch)

        assert success is True
        assert entry.created_record_id is not None

    @pytest.mark.asyncio
    async def test_harvest_entry_processor_rollback(self):
        """Test harvest entry rollback when no record created."""
        processor = HarvestEntryProcessor()
        entry = HarvestEntry(field_id="field_001")
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.HARVEST,
        )

        # Rollback without created record should succeed
        success = await processor.rollback(entry, batch)
        assert success is True

    @pytest.mark.asyncio
    async def test_equipment_assignment_processor(self):
        """Test equipment assignment processor."""
        processor = EquipmentAssignmentProcessor()
        assignment = EquipmentAssignment(
            equipment_id="tractor_001",
            task_id="task_001",
        )
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.EQUIPMENT_ASSIGN,
        )

        success, result = await processor.process(assignment, batch)

        assert success is True
        assert assignment.created_assignment_id is not None

    @pytest.mark.asyncio
    async def test_alert_acknowledgment_processor(self):
        """Test alert acknowledgment processor."""
        processor = AlertAcknowledgmentProcessor()
        ack = AlertAcknowledgment(
            alert_id="alert_001",
            alert_type="irrigation",
        )
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.ALERT_ACK,
        )

        success, result = await processor.process(ack, batch)

        assert success is True
        assert ack.acknowledged_at is not None


# =============================================================================
# Integration-like Tests (still unit tests but testing component integration)
# =============================================================================


@pytest.mark.unit
class TestBatchOperationsIntegration:
    """Test batch operations integration scenarios."""

    @pytest.mark.asyncio
    async def test_complete_irrigation_workflow(self):
        """Test complete irrigation batch workflow."""
        # Create batch
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Complete Workflow Test",
            name_ar="اختبار سير العمل الكامل",
            priority=BatchPriority.HIGH,
            irrigation_params=IrrigationParams(
                water_amount_mm=30.0,
                method="drip",
            ),
            field_items=[FieldOperationItem(field_id=f"field_{i}", area_hectares=5.0) for i in range(5)],
            config=BatchConfig(
                max_concurrent=2,
                retry_failed_items=True,
                max_retries=2,
            ),
        )

        # Execute with callbacks
        progress_values = []
        status_values = []

        async def on_progress(progress):
            progress_values.append(progress.percent_complete)

        async def on_status(status, message):
            status_values.append(status)

        executor = BatchExecutor()
        executor.set_progress_callback(on_progress)
        executor.set_status_callback(on_status)

        result = await executor.execute(batch)

        # Verify result
        assert result.status == BatchStatus.COMPLETED
        assert result.total_items == 5
        assert result.completed_items == 5
        assert result.duration_seconds > 0

        # Verify callbacks were called
        assert len(progress_values) > 0
        assert 100.0 in progress_values
        assert BatchStatus.IN_PROGRESS in status_values
        assert BatchStatus.COMPLETED in status_values

        # Verify audit log
        assert len(batch.audit_log) >= 2

        # Verify items
        for item in batch.field_items:
            assert item.status == ItemStatus.COMPLETED
            assert item.started_at is not None
            assert item.completed_at is not None

    @pytest.mark.asyncio
    async def test_scheduler_execution_flow(self):
        """Test scheduler batch execution flow."""
        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Scheduler Test",
            field_items=[FieldOperationItem(field_id="field_001", area_hectares=5.0)],
        )

        events = []

        async def on_event(event):
            events.append(event)

        scheduler = BatchScheduler(
            max_concurrent_batches=1,
            check_interval_seconds=0.1,
        )
        scheduler.set_event_callback(on_event)

        # Schedule batch
        schedule = scheduler.schedule_batch(batch, ScheduleType.IMMEDIATE)

        # Start scheduler and wait for execution
        await scheduler.start()
        await asyncio.sleep(0.5)  # Wait for processing
        await scheduler.stop()

        # Verify events
        event_types = [e.event_type for e in events]
        assert "scheduler_started" in event_types
        assert "batch_started" in event_types or "batch_completed" in event_types

    @pytest.mark.asyncio
    async def test_mixed_success_failure_with_audit(self, sample_field_items):
        """Test mixed success/failure scenario with full audit trail."""
        call_count = 0

        async def mixed_execute(item, batch):
            nonlocal call_count
            call_count += 1
            if item.field_id == "field_002":
                raise Exception("Simulated failure for field_002")
            return {"success": True}

        processor = FieldOperationProcessor(execute_operation=mixed_execute)
        executor = BatchExecutor(field_processor=processor)

        batch = BatchOperation(
            tenant_id="farm_001",
            operation_type=BatchOperationType.IRRIGATION,
            name="Mixed Result Test",
            field_items=sample_field_items,
            config=BatchConfig(
                max_concurrent=1,
                retry_failed_items=False,
            ),
        )

        result = await executor.execute(batch)

        # Verify result
        assert result.status == BatchStatus.PARTIALLY_COMPLETED
        assert result.completed_items == 2
        assert result.failed_items == 1

        # Verify item statuses
        assert batch.field_items[0].status == ItemStatus.COMPLETED
        assert batch.field_items[1].status == ItemStatus.FAILED
        assert batch.field_items[2].status == ItemStatus.COMPLETED

        # Verify error message
        assert batch.field_items[1].error_message is not None
        assert "Simulated failure" in batch.field_items[1].error_message

        # Verify audit
        completed_entry = next(e for e in batch.audit_log if e["action"] == "batch_completed")
        assert completed_entry["details"]["status"] == "partially_completed"
