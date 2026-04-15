"""
Unit tests for shared/batch_operations/models.py
Tests batch operation data models including enums, BilingualMessage,
IrrigationParams, SprayingParams, FertilizationParams, FieldOperationItem,
HarvestEntry, EquipmentAssignment, AlertAcknowledgment, BatchProgress,
BatchConfig, BatchOperation, and BatchResult.
"""

import pytest
from datetime import datetime, UTC

from shared.batch_operations.models import (
    # Enums
    BatchOperationType,
    BatchStatus,
    BatchPriority,
    ItemStatus,
    RollbackStrategy,
    # Dataclasses
    BilingualMessage,
    BATCH_MESSAGES,
    IrrigationParams,
    SprayingParams,
    FertilizationParams,
    FieldOperationItem,
    HarvestEntry,
    EquipmentAssignment,
    AlertAcknowledgment,
    BatchProgress,
    BatchConfig,
    BatchOperation,
    BatchResult,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_batch_operation_type(self):
        assert BatchOperationType.IRRIGATION == "irrigation"
        assert BatchOperationType.SPRAYING == "spraying"
        assert BatchOperationType.HARVEST == "harvest"
        assert BatchOperationType.EQUIPMENT_ASSIGN == "equipment_assign"
        assert BatchOperationType.ALERT_ACK == "alert_ack"

    def test_batch_status(self):
        assert BatchStatus.PENDING == "pending"
        assert BatchStatus.IN_PROGRESS == "in_progress"
        assert BatchStatus.COMPLETED == "completed"
        assert BatchStatus.ROLLED_BACK == "rolled_back"

    def test_batch_priority(self):
        assert BatchPriority.LOW == "low"
        assert BatchPriority.URGENT == "urgent"

    def test_item_status(self):
        assert ItemStatus.PENDING == "pending"
        assert ItemStatus.SKIPPED == "skipped"
        assert ItemStatus.ROLLED_BACK == "rolled_back"

    def test_rollback_strategy(self):
        assert RollbackStrategy.NONE == "none"
        assert RollbackStrategy.ON_FIRST_ERROR == "on_first_error"
        assert RollbackStrategy.ON_THRESHOLD == "on_threshold"
        assert RollbackStrategy.MANUAL == "manual"


# =============================================================================
# BilingualMessage Tests
# =============================================================================


class TestBilingualMessage:
    def test_creation(self):
        msg = BilingualMessage(en="Hello", ar="مرحبا")
        assert msg.en == "Hello"
        assert msg.ar == "مرحبا"

    def test_get_english(self):
        msg = BilingualMessage(en="Started", ar="بدأ")
        assert msg.get("en") == "Started"
        assert msg.get() == "Started"

    def test_get_arabic(self):
        msg = BilingualMessage(en="Started", ar="بدأ")
        assert msg.get("ar") == "بدأ"

    def test_to_dict(self):
        msg = BilingualMessage(en="Test", ar="اختبار")
        d = msg.to_dict()
        assert d == {"en": "Test", "ar": "اختبار"}

    def test_batch_messages_dict(self):
        assert "started" in BATCH_MESSAGES
        assert "completed" in BATCH_MESSAGES
        assert "failed" in BATCH_MESSAGES
        assert BATCH_MESSAGES["started"].get("en") == "Batch operation started"
        assert BATCH_MESSAGES["started"].get("ar") == "بدأت عملية الدفعة"


# =============================================================================
# Parameter Models Tests
# =============================================================================


class TestIrrigationParams:
    def test_creation(self):
        params = IrrigationParams(water_amount_mm=25.0)
        assert params.water_amount_mm == 25.0
        assert params.method == "drip"
        assert params.duration_minutes is None

    def test_to_dict(self):
        params = IrrigationParams(
            water_amount_mm=30.0,
            duration_minutes=60,
            method="sprinkler",
            notes="Morning irrigation",
        )
        d = params.to_dict()
        assert d["water_amount_mm"] == 30.0
        assert d["duration_minutes"] == 60
        assert d["method"] == "sprinkler"


class TestSprayingParams:
    def test_creation(self):
        params = SprayingParams(product_name="Neem Oil")
        assert params.product_name == "Neem Oil"
        assert params.product_type == "pesticide"
        assert params.safety_interval_days == 0

    def test_to_dict(self):
        params = SprayingParams(
            product_name="Fungicide X",
            product_type="fungicide",
            concentration=0.5,
            volume_per_hectare=200.0,
            safety_interval_days=14,
        )
        d = params.to_dict()
        assert d["product_name"] == "Fungicide X"
        assert d["safety_interval_days"] == 14


class TestFertilizationParams:
    def test_creation(self):
        params = FertilizationParams(fertilizer_name="Urea 46%")
        assert params.fertilizer_name == "Urea 46%"
        assert params.fertilizer_type == "granular"
        assert params.application_method == "broadcast"

    def test_to_dict(self):
        params = FertilizationParams(
            fertilizer_name="DAP",
            rate_kg_per_hectare=100.0,
            nitrogen_percent=18.0,
            phosphorus_percent=46.0,
        )
        d = params.to_dict()
        assert d["fertilizer_name"] == "DAP"
        assert d["rate_kg_per_hectare"] == 100.0
        assert d["nitrogen_percent"] == 18.0


# =============================================================================
# Item Models Tests
# =============================================================================


class TestFieldOperationItem:
    def test_creation_defaults(self):
        item = FieldOperationItem()
        assert item.id  # UUID
        assert item.status == ItemStatus.PENDING
        assert item.area_hectares == 0.0

    def test_to_dict(self):
        now = datetime.now(UTC)
        item = FieldOperationItem(
            field_id="field-001",
            field_name="North Field",
            area_hectares=5.0,
            status=ItemStatus.COMPLETED,
            started_at=now,
            completed_at=now,
        )
        d = item.to_dict()
        assert d["field_id"] == "field-001"
        assert d["status"] == "completed"
        assert d["area_hectares"] == 5.0
        assert d["started_at"] is not None


class TestHarvestEntry:
    def test_creation_defaults(self):
        entry = HarvestEntry()
        assert entry.id
        assert entry.yield_kg == 0.0
        assert entry.status == ItemStatus.PENDING

    def test_to_dict(self):
        entry = HarvestEntry(
            field_id="field-002",
            crop_type="wheat",
            yield_kg=4500.0,
            quality_grade="A",
            moisture_percent=12.5,
        )
        d = entry.to_dict()
        assert d["crop_type"] == "wheat"
        assert d["yield_kg"] == 4500.0
        assert d["quality_grade"] == "A"


class TestEquipmentAssignment:
    def test_creation_defaults(self):
        assign = EquipmentAssignment()
        assert assign.id
        assert assign.status == ItemStatus.PENDING

    def test_to_dict(self):
        assign = EquipmentAssignment(
            equipment_id="eq-001",
            equipment_name="Tractor",
            task_id="task-001",
        )
        d = assign.to_dict()
        assert d["equipment_id"] == "eq-001"
        assert d["status"] == "pending"


class TestAlertAcknowledgment:
    def test_creation_defaults(self):
        ack = AlertAcknowledgment()
        assert ack.id
        assert ack.status == ItemStatus.PENDING

    def test_to_dict(self):
        ack = AlertAcknowledgment(
            alert_id="alert-001",
            alert_title="Frost Warning",
            severity="critical",
        )
        d = ack.to_dict()
        assert d["alert_id"] == "alert-001"
        assert d["severity"] == "critical"


# =============================================================================
# BatchProgress Tests
# =============================================================================


class TestBatchProgress:
    def test_creation_defaults(self):
        progress = BatchProgress()
        assert progress.total_items == 0
        assert progress.percent_complete == 0.0

    def test_update(self):
        progress = BatchProgress()
        progress.update(total=10, completed=5, failed=2, skipped=1)
        assert progress.total_items == 10
        assert progress.completed_items == 5
        assert progress.failed_items == 2
        assert progress.skipped_items == 1
        assert progress.current_item_index == 8  # 5 + 2 + 1
        assert progress.percent_complete == 80.0

    def test_update_zero_total(self):
        progress = BatchProgress()
        progress.update(total=0, completed=0, failed=0)
        assert progress.percent_complete == 0.0

    def test_to_dict(self):
        progress = BatchProgress()
        progress.update(total=4, completed=3, failed=1)
        d = progress.to_dict()
        assert d["total_items"] == 4
        assert d["percent_complete"] == 100.0


# =============================================================================
# BatchConfig Tests
# =============================================================================


class TestBatchConfig:
    def test_creation_defaults(self):
        config = BatchConfig()
        assert config.max_concurrent == 5
        assert config.timeout_per_item_seconds == 60.0
        assert config.retry_failed_items is True
        assert config.max_retries == 3
        assert config.stop_on_error is False
        assert config.rollback_strategy == RollbackStrategy.NONE
        assert config.dry_run is False

    def test_to_dict(self):
        config = BatchConfig(
            max_concurrent=10,
            stop_on_error=True,
            rollback_strategy=RollbackStrategy.ON_FIRST_ERROR,
        )
        d = config.to_dict()
        assert d["max_concurrent"] == 10
        assert d["stop_on_error"] is True
        assert d["rollback_strategy"] == "on_first_error"


# =============================================================================
# BatchOperation Tests
# =============================================================================


class TestBatchOperation:
    def test_creation_defaults(self):
        op = BatchOperation()
        assert op.id
        assert op.operation_type == BatchOperationType.IRRIGATION
        assert op.status == BatchStatus.PENDING
        assert op.priority == BatchPriority.MEDIUM

    def test_get_items_irrigation(self):
        item = FieldOperationItem(field_id="f1")
        op = BatchOperation(
            operation_type=BatchOperationType.IRRIGATION,
            field_items=[item],
        )
        assert len(op.get_items()) == 1
        assert op.get_item_count() == 1

    def test_get_items_harvest(self):
        entry = HarvestEntry(field_id="f1")
        op = BatchOperation(
            operation_type=BatchOperationType.HARVEST,
            harvest_entries=[entry],
        )
        assert len(op.get_items()) == 1

    def test_get_items_equipment(self):
        assign = EquipmentAssignment(equipment_id="eq1")
        op = BatchOperation(
            operation_type=BatchOperationType.EQUIPMENT_ASSIGN,
            equipment_assignments=[assign],
        )
        assert len(op.get_items()) == 1

    def test_get_items_alert_ack(self):
        ack = AlertAcknowledgment(alert_id="a1")
        op = BatchOperation(
            operation_type=BatchOperationType.ALERT_ACK,
            alert_acknowledgments=[ack],
        )
        assert len(op.get_items()) == 1

    def test_completed_and_failed_counts(self):
        items = [
            FieldOperationItem(status=ItemStatus.COMPLETED),
            FieldOperationItem(status=ItemStatus.COMPLETED),
            FieldOperationItem(status=ItemStatus.FAILED),
            FieldOperationItem(status=ItemStatus.PENDING),
        ]
        op = BatchOperation(
            operation_type=BatchOperationType.IRRIGATION,
            field_items=items,
        )
        assert op.get_completed_count() == 2
        assert op.get_failed_count() == 1

    def test_add_audit_entry(self):
        op = BatchOperation()
        op.add_audit_entry("started", {"user": "admin"}, user_id="u1")
        assert len(op.audit_log) == 1
        assert op.audit_log[0]["action"] == "started"
        assert op.audit_log[0]["user_id"] == "u1"

    def test_to_dict_with_items(self):
        op = BatchOperation(
            name="Test Batch",
            irrigation_params=IrrigationParams(water_amount_mm=25.0),
        )
        d = op.to_dict(include_items=True)
        assert d["name"] == "Test Batch"
        assert "irrigation_params" in d
        assert "item_count" in d
        assert "field_items" in d

    def test_to_dict_without_items(self):
        op = BatchOperation(name="Test Batch")
        d = op.to_dict(include_items=False)
        assert "field_items" not in d
        assert "item_count" not in d


# =============================================================================
# BatchResult Tests
# =============================================================================


class TestBatchResult:
    def test_creation(self):
        result = BatchResult(
            batch_id="batch-001",
            status=BatchStatus.COMPLETED,
            total_items=10,
            completed_items=8,
            failed_items=2,
            duration_seconds=45.5,
        )
        assert result.batch_id == "batch-001"
        assert result.status == BatchStatus.COMPLETED
        assert result.rollback_performed is False

    def test_to_dict_success_rate(self):
        result = BatchResult(
            batch_id="batch-001",
            status=BatchStatus.COMPLETED,
            total_items=10,
            completed_items=8,
            failed_items=2,
        )
        d = result.to_dict()
        assert d["success_rate"] == 80.0

    def test_to_dict_zero_items(self):
        result = BatchResult(
            batch_id="batch-002",
            status=BatchStatus.FAILED,
            total_items=0,
        )
        d = result.to_dict()
        assert d["success_rate"] == 0

    def test_to_dict_with_message(self):
        msg = BilingualMessage(en="Done", ar="تم")
        result = BatchResult(
            batch_id="batch-003",
            status=BatchStatus.COMPLETED,
            message=msg,
        )
        d = result.to_dict()
        assert d["message"] == {"en": "Done", "ar": "تم"}

    def test_to_dict_without_message(self):
        result = BatchResult(
            batch_id="batch-004",
            status=BatchStatus.FAILED,
        )
        d = result.to_dict()
        assert d["message"] is None
