"""
Comprehensive unit tests for SAHOOL Equipment Service.
Covers db_models, repository, database, and main (API endpoints).

Target: >60% code coverage across all source files.
"""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

# Add service root to path so we can import src modules
# ---------------------------------------------------------------------------
# 1. DB Models tests (db_models.py)
# ---------------------------------------------------------------------------

class TestEquipmentDBModel:
    """Tests for the Equipment SQLAlchemy model."""

    def test_equipment_repr(self):
        from src.db_models import Equipment

        eq = Equipment()
        eq.equipment_id = "eq_test"
        eq.name = "Test Tractor"
        eq.equipment_type = "tractor"
        eq.status = "operational"

        result = repr(eq)
        assert "eq_test" in result
        assert "Test Tractor" in result
        assert "tractor" in result
        assert "operational" in result

    def test_equipment_default_timestamps(self):
        from src.db_models import Equipment

        eq = Equipment()
        eq.equipment_id = "eq_ts"
        eq.tenant_id = "t1"
        eq.name = "TS Test"
        eq.equipment_type = "pump"
        eq.status = "operational"
        # Column defaults are callables, not set on __init__ directly,
        # but we can verify the model accepts the fields
        now = datetime.now(UTC)
        eq.created_at = now
        eq.updated_at = now
        assert eq.created_at == now
        assert eq.updated_at == now

    def test_equipment_tablename(self):
        from src.db_models import Equipment

        assert Equipment.__tablename__ == "equipment"

    def test_equipment_nullable_fields(self):
        from src.db_models import Equipment

        eq = Equipment()
        eq.equipment_id = "eq_null"
        eq.tenant_id = "t1"
        eq.name = "Null Test"
        eq.equipment_type = "sensor"
        eq.status = "inactive"
        # All optional fields should be settable to None
        eq.name_ar = None
        eq.brand = None
        eq.model = None
        eq.serial_number = None
        eq.year = None
        eq.purchase_date = None
        eq.purchase_price = None
        eq.field_id = None
        eq.location_name = None
        eq.horsepower = None
        eq.fuel_capacity_liters = None
        eq.current_fuel_percent = None
        eq.current_hours = None
        eq.current_lat = None
        eq.current_lon = None
        eq.last_maintenance_at = None
        eq.next_maintenance_at = None
        eq.next_maintenance_hours = None
        eq.qr_code = None
        eq.extra_metadata = None
        assert eq.brand is None
        assert eq.qr_code is None

    def test_equipment_numeric_fields(self):
        from src.db_models import Equipment

        eq = Equipment()
        eq.equipment_id = "eq_num"
        eq.tenant_id = "t1"
        eq.name = "Num Test"
        eq.equipment_type = "tractor"
        eq.status = "operational"
        eq.purchase_price = Decimal("15000.50")
        eq.fuel_capacity_liters = Decimal("200.00")
        eq.current_fuel_percent = Decimal("75.50")
        eq.current_hours = Decimal("1250.75")
        eq.current_lat = Decimal("15.3694123")
        eq.current_lon = Decimal("44.1910456")
        assert eq.purchase_price == Decimal("15000.50")
        assert eq.current_lat == Decimal("15.3694123")
class TestMaintenanceRecordDBModel:
    """Tests for the MaintenanceRecord SQLAlchemy model."""

    def test_maintenance_record_repr(self):
        from src.db_models import MaintenanceRecord

        rec = MaintenanceRecord()
        rec.record_id = "maint_001"
        rec.equipment_id = "eq_001"
        rec.maintenance_type = "oil_change"
        result = repr(rec)
        assert "maint_001" in result
        assert "eq_001" in result
        assert "oil_change" in result

    def test_maintenance_record_tablename(self):
        from src.db_models import MaintenanceRecord

        assert MaintenanceRecord.__tablename__ == "equipment_maintenance"

    def test_maintenance_record_fields(self):
        from src.db_models import MaintenanceRecord

        rec = MaintenanceRecord()
        rec.record_id = "maint_f"
        rec.equipment_id = "eq_f"
        rec.maintenance_type = "repair"
        rec.description = "Fixed engine"
        rec.description_ar = "إصلاح المحرك"
        rec.performed_by = "tech_1"
        rec.performed_at = datetime.now(UTC)
        rec.cost = Decimal("500.00")
        rec.notes = "Replaced gasket"
        rec.parts_replaced = ["gasket", "seal"]
        assert rec.parts_replaced == ["gasket", "seal"]
        assert rec.cost == Decimal("500.00")
class TestMaintenanceAlertDBModel:
    """Tests for the MaintenanceAlert SQLAlchemy model."""

    def test_maintenance_alert_repr(self):
        from src.db_models import MaintenanceAlert

        alert = MaintenanceAlert()
        alert.alert_id = "alert_test"
        alert.equipment_id = "eq_001"
        alert.priority = "high"
        alert.is_overdue = True
        result = repr(alert)
        assert "alert_test" in result
        assert "eq_001" in result
        assert "high" in result
        assert "True" in result

    def test_maintenance_alert_tablename(self):
        from src.db_models import MaintenanceAlert

        assert MaintenanceAlert.__tablename__ == "equipment_alerts"

    def test_maintenance_alert_fields(self):
        from src.db_models import MaintenanceAlert

        alert = MaintenanceAlert()
        alert.alert_id = "alert_f"
        alert.equipment_id = "eq_f"
        alert.equipment_name = "Test Equipment"
        alert.maintenance_type = "calibration"
        alert.description = "Calibration due"
        alert.description_ar = "المعايرة مستحقة"
        alert.priority = "medium"
        alert.due_at = datetime.now(UTC) + timedelta(days=7)
        alert.due_hours = Decimal("500.00")
        alert.is_overdue = False
        alert.created_at = datetime.now(UTC)
        assert alert.priority == "medium"
        assert alert.is_overdue is False
class TestBaseDeclarative:
    """Test Base declarative_base export."""

    def test_base_is_available(self):
        from src.db_models import Base
        assert Base is not None
        # All three models should be registered
        assert "equipment" in Base.metadata.tables
        assert "equipment_maintenance" in Base.metadata.tables
        assert "equipment_alerts" in Base.metadata.tables
# ---------------------------------------------------------------------------
# 2. Repository tests (repository.py) - with mocked Session
# ---------------------------------------------------------------------------

class TestRepositoryCreateEquipment:
    """Tests for repository.create_equipment."""

    def test_create_equipment_adds_and_flushes(self):
        from src.db_models import Equipment
        from src.repository import create_equipment

        db = MagicMock()
        eq = Equipment()
        eq.equipment_id = "eq_new"
        result = create_equipment(db, eq)
        db.add.assert_called_once_with(eq)
        db.flush.assert_called_once()
        assert result is eq
class TestRepositoryGetEquipment:
    """Tests for repository.get_equipment."""

    def test_get_equipment_without_tenant(self):
        from src.repository import get_equipment

        db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "found_eq"
        db.execute.return_value = mock_result

        result = get_equipment(db, equipment_id="eq_001")
        assert result == "found_eq"
        db.execute.assert_called_once()

    def test_get_equipment_with_tenant(self):
        from src.repository import get_equipment

        db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "found_eq"
        db.execute.return_value = mock_result

        result = get_equipment(db, equipment_id="eq_001", tenant_id="t1")
        assert result == "found_eq"

    def test_get_equipment_not_found(self):
        from src.repository import get_equipment

        db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute.return_value = mock_result

        result = get_equipment(db, equipment_id="nonexistent")
        assert result is None
class TestRepositoryGetEquipmentByQR:
    """Tests for repository.get_equipment_by_qr."""

    def test_get_by_qr_found(self):
        from src.repository import get_equipment_by_qr

        db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "eq_by_qr"
        db.execute.return_value = mock_result

        result = get_equipment_by_qr(db, qr_code="QR_123")
        assert result == "eq_by_qr"

    def test_get_by_qr_with_tenant(self):
        from src.repository import get_equipment_by_qr

        db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "eq_by_qr"
        db.execute.return_value = mock_result

        result = get_equipment_by_qr(db, qr_code="QR_123", tenant_id="t1")
        assert result == "eq_by_qr"

    def test_get_by_qr_not_found(self):
        from src.repository import get_equipment_by_qr

        db = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute.return_value = mock_result

        result = get_equipment_by_qr(db, qr_code="NONEXISTENT")
        assert result is None
class TestRepositoryListEquipment:
    """Tests for repository.list_equipment."""

    def test_list_equipment_basic(self):
        from src.repository import list_equipment

        db = MagicMock()
        # Mock count query
        count_result = MagicMock()
        count_result.scalar.return_value = 3
        # Mock list query - scalars returns iterable
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["eq1", "eq2", "eq3"]

        db.execute.side_effect = [count_result, scalars_mock]

        equipment_list, total = list_equipment(db, tenant_id="t1")
        assert total == 3
        assert len(equipment_list) == 3

    def test_list_equipment_with_type_filter(self):
        from src.repository import list_equipment

        db = MagicMock()
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["eq_tractor"]
        db.execute.side_effect = [count_result, scalars_mock]

        equipment_list, total = list_equipment(
            db, tenant_id="t1", equipment_type="tractor"
        )
        assert total == 1

    def test_list_equipment_with_status_filter(self):
        from src.repository import list_equipment

        db = MagicMock()
        count_result = MagicMock()
        count_result.scalar.return_value = 2
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["eq1", "eq2"]
        db.execute.side_effect = [count_result, scalars_mock]

        equipment_list, total = list_equipment(
            db, tenant_id="t1", status="operational"
        )
        assert total == 2

    def test_list_equipment_with_field_filter(self):
        from src.repository import list_equipment

        db = MagicMock()
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["eq1"]
        db.execute.side_effect = [count_result, scalars_mock]

        equipment_list, total = list_equipment(
            db, tenant_id="t1", field_id="field_north"
        )
        assert total == 1

    def test_list_equipment_pagination(self):
        from src.repository import list_equipment

        db = MagicMock()
        count_result = MagicMock()
        count_result.scalar.return_value = 10
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["eq1", "eq2"]
        db.execute.side_effect = [count_result, scalars_mock]

        equipment_list, total = list_equipment(
            db, tenant_id="t1", skip=2, limit=2
        )
        assert total == 10
        assert len(equipment_list) == 2

    def test_list_equipment_zero_count(self):
        from src.repository import list_equipment

        db = MagicMock()
        count_result = MagicMock()
        count_result.scalar.return_value = None  # Returns None when 0
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = []
        db.execute.side_effect = [count_result, scalars_mock]

        equipment_list, total = list_equipment(db, tenant_id="t1")
        assert total == 0
        assert len(equipment_list) == 0
class TestRepositoryUpdateEquipment:
    """Tests for repository.update_equipment."""

    def test_update_equipment_found(self):
        from src.repository import update_equipment

        mock_eq = MagicMock()
        mock_eq.equipment_id = "eq_001"
        mock_eq.name = "Old Name"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_eq

        result = update_equipment(
            db, equipment_id="eq_001", tenant_id="t1", name="New Name"
        )
        assert result is mock_eq

    def test_update_equipment_not_found(self):
        from src.repository import update_equipment

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        result = update_equipment(
            db, equipment_id="nonexistent", tenant_id="t1", name="X"
        )
        assert result is None

    def test_update_equipment_skips_none_values(self):
        from src.repository import update_equipment

        mock_eq = MagicMock()
        mock_eq.name = "Original"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_eq

        result = update_equipment(
            db, equipment_id="eq_001", tenant_id="t1", name=None
        )
        # name should NOT be updated because value is None
        assert result is mock_eq

    def test_update_equipment_ignores_nonexistent_attrs(self):
        from src.repository import update_equipment

        mock_eq = MagicMock(spec=["equipment_id", "tenant_id", "updated_at"])
        mock_eq.equipment_id = "eq_001"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_eq

        # 'nonexistent_field' doesn't exist on Equipment
        result = update_equipment(
            db, equipment_id="eq_001", tenant_id="t1", nonexistent_field="val"
        )
        assert result is mock_eq
class TestRepositoryDeleteEquipment:
    """Tests for repository.delete_equipment."""

    def test_delete_equipment_found(self):
        from src.repository import delete_equipment

        mock_eq = MagicMock()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_eq

        result = delete_equipment(db, "eq_001", "t1")
        assert result is True
        db.delete.assert_called_once_with(mock_eq)

    def test_delete_equipment_not_found(self):
        from src.repository import delete_equipment

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        result = delete_equipment(db, "nonexistent", "t1")
        assert result is False
        db.delete.assert_not_called()
class TestRepositoryGetEquipmentStats:
    """Tests for repository.get_equipment_stats."""

    def test_stats_empty(self):
        from src.repository import get_equipment_stats

        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        stats = get_equipment_stats(db, tenant_id="t1")
        assert stats["total"] == 0
        assert stats["by_type"] == {}
        assert stats["by_status"] == {}
        assert stats["operational"] == 0
        assert stats["maintenance"] == 0
        assert stats["inactive"] == 0

    def test_stats_with_data(self):
        from src.repository import get_equipment_stats

        eq1 = MagicMock(equipment_type="tractor", status="operational")
        eq2 = MagicMock(equipment_type="tractor", status="operational")
        eq3 = MagicMock(equipment_type="pump", status="maintenance")
        eq4 = MagicMock(equipment_type="drone", status="inactive")
        eq5 = MagicMock(equipment_type="tractor", status="repair")

        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [
            eq1, eq2, eq3, eq4, eq5,
        ]

        stats = get_equipment_stats(db, tenant_id="t1")
        assert stats["total"] == 5
        assert stats["by_type"]["tractor"] == 3
        assert stats["by_type"]["pump"] == 1
        assert stats["by_type"]["drone"] == 1
        assert stats["operational"] == 2
        assert stats["maintenance"] == 2  # 1 maintenance + 1 repair
        assert stats["inactive"] == 1
class TestRepositoryMaintenanceRecords:
    """Tests for maintenance record repository functions."""

    def test_create_maintenance_record(self):
        from src.db_models import MaintenanceRecord
        from src.repository import create_maintenance_record

        db = MagicMock()
        rec = MaintenanceRecord()
        rec.record_id = "maint_new"
        result = create_maintenance_record(db, rec)
        db.add.assert_called_once_with(rec)
        db.flush.assert_called_once()
        assert result is rec

    def test_get_maintenance_history(self):
        from src.repository import get_maintenance_history

        db = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["rec1", "rec2"]
        db.execute.return_value = scalars_mock

        result = get_maintenance_history(db, equipment_id="eq_001", limit=10)
        assert len(result) == 2
class TestRepositoryMaintenanceAlerts:
    """Tests for maintenance alert repository functions."""

    def test_create_maintenance_alert(self):
        from src.db_models import MaintenanceAlert
        from src.repository import create_maintenance_alert

        db = MagicMock()
        alert = MaintenanceAlert()
        alert.alert_id = "alert_new"
        result = create_maintenance_alert(db, alert)
        db.add.assert_called_once_with(alert)
        db.flush.assert_called_once()
        assert result is alert

    def test_get_maintenance_alerts_no_equipment(self):
        from src.repository import get_maintenance_alerts

        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = get_maintenance_alerts(db, tenant_id="t_empty")
        assert result == []

    def test_get_maintenance_alerts_with_data(self):
        from src.repository import get_maintenance_alerts

        db = MagicMock()
        # First call: equipment_ids
        db.query.return_value.filter.return_value.all.return_value = [
            ("eq_001",), ("eq_002",)
        ]
        # Second call: alerts via select/execute
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["alert1", "alert2"]
        db.execute.return_value = scalars_mock

        result = get_maintenance_alerts(db, tenant_id="t1")
        assert len(result) == 2

    def test_get_maintenance_alerts_with_priority(self):
        from src.repository import get_maintenance_alerts

        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [("eq_001",)]
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["alert_high"]
        db.execute.return_value = scalars_mock

        result = get_maintenance_alerts(db, tenant_id="t1", priority="high")
        assert len(result) == 1

    def test_get_maintenance_alerts_overdue_only(self):
        from src.repository import get_maintenance_alerts

        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [("eq_001",)]
        scalars_mock = MagicMock()
        scalars_mock.scalars.return_value = ["overdue_alert"]
        db.execute.return_value = scalars_mock

        result = get_maintenance_alerts(db, tenant_id="t1", overdue_only=True)
        assert len(result) == 1

    def test_delete_maintenance_alert_found(self):
        from src.repository import delete_maintenance_alert

        mock_alert = MagicMock()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_alert

        result = delete_maintenance_alert(db, "alert_001")
        assert result is True
        db.delete.assert_called_once_with(mock_alert)

    def test_delete_maintenance_alert_not_found(self):
        from src.repository import delete_maintenance_alert

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        result = delete_maintenance_alert(db, "nonexistent")
        assert result is False
# ---------------------------------------------------------------------------
# 3. Database module tests (database.py) - mocked engine/session
# ---------------------------------------------------------------------------

class TestDatabaseGetDB:
    """Tests for get_db dependency."""

    def test_get_db_yields_session_and_commits(self):
        with patch("src.database.SessionLocal") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session

            from src.database import get_db

            gen = get_db()
            session = next(gen)
            assert session is mock_session

            # Exhaust the generator (no exception)
            try:
                next(gen)
            except StopIteration:
                pass

            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    def test_get_db_rollbacks_on_exception(self):
        with patch("src.database.SessionLocal") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session

            from src.database import get_db

            gen = get_db()
            session = next(gen)

            # Simulate exception
            with pytest.raises(ValueError):
                gen.throw(ValueError("test error"))

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
class TestDatabaseCheckConnection:
    """Tests for check_db_connection."""

    def test_check_db_connection_success(self):
        with patch("src.database.SessionLocal") as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session

            from src.database import check_db_connection

            result = check_db_connection()
            assert result is True
            mock_session.execute.assert_called_once()
            mock_session.close.assert_called_once()

    def test_check_db_connection_failure(self):
        with patch("src.database.SessionLocal") as MockSession:
            MockSession.return_value.execute.side_effect = Exception("DB down")

            from src.database import check_db_connection

            result = check_db_connection()
            assert result is False
class TestDatabaseInitDB:
    """Tests for init_db."""

    def test_init_db_with_id_column(self):
        with patch("src.database.Base") as MockBase, \
             patch("src.database.SessionLocal") as MockSession, \
             patch("src.database.engine") as mock_engine:

            mock_session = MagicMock()
            MockSession.return_value = mock_session

            # Simulate 'id' column existing
            mock_result = MagicMock()
            mock_result.fetchone.return_value = ("id",)
            mock_session.execute.return_value = mock_result

            from src.database import init_db
            init_db()

            MockBase.metadata.create_all.assert_called_once()
            # Should have executed ALTER TABLE statements
            assert mock_session.execute.call_count >= 2
            mock_session.commit.assert_called()

    def test_init_db_with_equipment_id_column(self):
        with patch("src.database.Base") as MockBase, \
             patch("src.database.SessionLocal") as MockSession, \
             patch("src.database.engine") as mock_engine:

            mock_session = MagicMock()
            MockSession.return_value = mock_session

            # First query: no 'id' column
            result1 = MagicMock()
            result1.fetchone.return_value = None
            # Second query: 'equipment_id' exists
            result2 = MagicMock()
            result2.fetchone.return_value = ("equipment_id",)
            mock_session.execute.side_effect = [result1, result2]

            from src.database import init_db
            init_db()

            MockBase.metadata.create_all.assert_called_once()

    def test_init_db_no_table(self):
        with patch("src.database.Base") as MockBase, \
             patch("src.database.SessionLocal") as MockSession, \
             patch("src.database.engine"):

            mock_session = MagicMock()
            MockSession.return_value = mock_session

            result1 = MagicMock()
            result1.fetchone.return_value = None
            result2 = MagicMock()
            result2.fetchone.return_value = None
            mock_session.execute.side_effect = [result1, result2]

            from src.database import init_db
            init_db()

    def test_init_db_exception_handled(self):
        with patch("src.database.Base") as MockBase, \
             patch("src.database.SessionLocal") as MockSession, \
             patch("src.database.engine"):

            MockSession.side_effect = Exception("Connection failed")

            from src.database import init_db
            # Should not raise
            init_db()
class TestDatabaseDropAll:
    """Test drop_all_tables."""

    def test_drop_all_tables(self):
        with patch("src.database.Base") as MockBase, \
             patch("src.database.engine") as mock_engine:
            from src.database import drop_all_tables
            drop_all_tables()
            MockBase.metadata.drop_all.assert_called_once_with(bind=mock_engine)
# ---------------------------------------------------------------------------
# 4. Main module tests - Enums, Pydantic models, helpers
# ---------------------------------------------------------------------------

class TestEnums:
    """Test StrEnum definitions in main.py."""

    def test_equipment_type_values(self):
        from src.main import EquipmentType

        assert EquipmentType.TRACTOR == "tractor"
        assert EquipmentType.PUMP == "pump"
        assert EquipmentType.DRONE == "drone"
        assert EquipmentType.HARVESTER == "harvester"
        assert EquipmentType.SPRAYER == "sprayer"
        assert EquipmentType.PIVOT == "pivot"
        assert EquipmentType.SENSOR == "sensor"
        assert EquipmentType.VEHICLE == "vehicle"
        assert EquipmentType.OTHER == "other"
        # All 9 types
        assert len(EquipmentType) == 9

    def test_equipment_status_values(self):
        from src.main import EquipmentStatus

        assert EquipmentStatus.OPERATIONAL == "operational"
        assert EquipmentStatus.MAINTENANCE == "maintenance"
        assert EquipmentStatus.INACTIVE == "inactive"
        assert EquipmentStatus.REPAIR == "repair"
        assert len(EquipmentStatus) == 4

    def test_maintenance_priority_values(self):
        from src.main import MaintenancePriority

        assert MaintenancePriority.LOW == "low"
        assert MaintenancePriority.MEDIUM == "medium"
        assert MaintenancePriority.HIGH == "high"
        assert MaintenancePriority.CRITICAL == "critical"
        assert len(MaintenancePriority) == 4

    def test_maintenance_type_values(self):
        from src.main import MaintenanceType

        assert MaintenanceType.OIL_CHANGE == "oil_change"
        assert MaintenanceType.FILTER_CHANGE == "filter_change"
        assert MaintenanceType.TIRE_CHECK == "tire_check"
        assert MaintenanceType.BATTERY_CHECK == "battery_check"
        assert MaintenanceType.CALIBRATION == "calibration"
        assert MaintenanceType.GENERAL_SERVICE == "general_service"
        assert MaintenanceType.REPAIR == "repair"
        assert MaintenanceType.OTHER == "other"
        assert len(MaintenanceType) == 8
class TestPydanticModels:
    """Test Pydantic request/response models."""

    def test_equipment_create_required_fields(self):
        from src.main import EquipmentCreate, EquipmentType

        ec = EquipmentCreate(name="Pump A", equipment_type=EquipmentType.PUMP)
        assert ec.name == "Pump A"
        assert ec.equipment_type == EquipmentType.PUMP
        assert ec.name_ar is None
        assert ec.brand is None
        assert ec.metadata is None

    def test_equipment_create_all_fields(self):
        from src.main import EquipmentCreate, EquipmentType

        ec = EquipmentCreate(
            name="Full Equipment",
            name_ar="معدة كاملة",
            equipment_type=EquipmentType.TRACTOR,
            brand="TestBrand",
            model="T-100",
            serial_number="SN-001",
            year=2023,
            purchase_date=datetime(2023, 1, 1),
            purchase_price=50000.0,
            field_id="field_1",
            location_name="North Field",
            horsepower=200,
            fuel_capacity_liters=500.0,
            metadata={"custom": "data"},
        )
        assert ec.purchase_price == 50000.0
        assert ec.metadata == {"custom": "data"}

    def test_equipment_create_name_validation_empty(self):
        from pydantic import ValidationError
        from src.main import EquipmentCreate, EquipmentType

        with pytest.raises(ValidationError):
            EquipmentCreate(name="", equipment_type=EquipmentType.PUMP)

    def test_equipment_create_name_validation_too_long(self):
        from pydantic import ValidationError
        from src.main import EquipmentCreate, EquipmentType

        with pytest.raises(ValidationError):
            EquipmentCreate(name="x" * 201, equipment_type=EquipmentType.PUMP)

    def test_equipment_create_missing_type(self):
        from pydantic import ValidationError
        from src.main import EquipmentCreate

        with pytest.raises(ValidationError):
            EquipmentCreate(name="No Type")

    def test_equipment_update_partial(self):
        from src.main import EquipmentUpdate

        eu = EquipmentUpdate(name="Updated")
        assert eu.name == "Updated"
        assert eu.status is None
        assert eu.brand is None

    def test_equipment_update_all_none(self):
        from src.main import EquipmentUpdate

        eu = EquipmentUpdate()
        assert eu.name is None
        assert eu.equipment_type is None
        assert eu.status is None

    def test_equipment_response_model(self):
        from src.main import Equipment, EquipmentStatus, EquipmentType

        now = datetime.now(UTC)
        eq = Equipment(
            equipment_id="eq_resp",
            tenant_id="t1",
            name="Response Test",
            equipment_type=EquipmentType.SENSOR,
            status=EquipmentStatus.OPERATIONAL,
            created_at=now,
            updated_at=now,
        )
        assert eq.equipment_id == "eq_resp"
        assert eq.metadata is None
        assert eq.qr_code is None

    def test_maintenance_record_model(self):
        from src.main import MaintenanceRecord as MR
        from src.main import MaintenanceType

        now = datetime.now(UTC)
        rec = MR(
            record_id="maint_resp",
            equipment_id="eq_001",
            maintenance_type=MaintenanceType.OIL_CHANGE,
            description="Oil changed",
            performed_at=now,
        )
        assert rec.record_id == "maint_resp"
        assert rec.cost is None
        assert rec.parts_replaced is None

    def test_maintenance_alert_model(self):
        from src.main import MaintenanceAlert as MA
        from src.main import MaintenancePriority, MaintenanceType

        now = datetime.now(UTC)
        alert = MA(
            alert_id="alert_resp",
            equipment_id="eq_001",
            equipment_name="Test",
            maintenance_type=MaintenanceType.CALIBRATION,
            description="Cal due",
            priority=MaintenancePriority.HIGH,
            created_at=now,
        )
        assert alert.alert_id == "alert_resp"
        assert alert.is_overdue is False
        assert alert.due_at is None
class TestGetTenantId:
    """Test get_tenant_id helper."""

    def test_get_tenant_id_with_user(self):
        from src.main import get_tenant_id

        mock_user = MagicMock()
        mock_user.tenant_id = "user_tenant"

        # When AUTH_AVAILABLE is True (default in source)
        with patch("src.main.AUTH_AVAILABLE", True):
            result = get_tenant_id(user=mock_user)
            assert result == "user_tenant"

    def test_get_tenant_id_no_auth(self):
        from src.main import get_tenant_id

        with patch("src.main.AUTH_AVAILABLE", False):
            result = get_tenant_id(user=None)
            assert result == "tenant_demo"

    def test_get_tenant_id_auth_but_no_user(self):
        from src.main import get_tenant_id

        with patch("src.main.AUTH_AVAILABLE", True):
            result = get_tenant_id(user=None)
            assert result == "tenant_demo"
class TestSeedDemoData:
    """Test seed_demo_data function."""

    def test_seed_demo_data_skips_when_data_exists(self):
        from src.main import seed_demo_data

        db = MagicMock()
        db.query.return_value.count.return_value = 5

        seed_demo_data(db)
        # Should not add any equipment
        db.add.assert_not_called()

    def test_seed_demo_data_seeds_when_empty(self):
        from src.main import seed_demo_data

        db = MagicMock()
        db.query.return_value.count.return_value = 0

        seed_demo_data(db)
        # Should have called add for 5 equipment + 2 alerts = 7
        assert db.add.call_count == 7
        db.commit.assert_called_once()
class TestServiceConstants:
    """Test service-level constants."""

    def test_service_name(self):
        from src.main import SERVICE_NAME
        assert SERVICE_NAME == "sahool-equipment-service"

    def test_app_title(self):
        from src.main import app
        assert app.title == "SAHOOL Equipment Service"

    def test_app_version(self):
        from src.main import app
        assert app.version == "16.0.0"
