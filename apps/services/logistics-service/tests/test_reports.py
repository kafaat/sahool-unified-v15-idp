"""Tests for logistics-service reports module (api/v1/__init__.py)."""

import os
import sys
from datetime import UTC, datetime, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
# The reports module does `import main as main_mod` (bare import),
# so we need src/ on sys.path for that to resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import the main module first to ensure it is loaded
# (the reports module uses lazy imports from main)
from src import main as main_mod  # noqa: F401

# Now import report helpers and models
from src.api.v1 import (
    CollectionSummary,
    CostSummary,
    DailyReportResponse,
    MonthlyReportResponse,
    ShipmentSummary,
    VehicleSummary,
    WeeklyReportResponse,
    _build_collection_summary,
    _build_shipment_summary,
    _build_vehicle_summary,
    _filter_records_by_date,
    _to_aware_dt,
)


# ==========================================================================
# _to_aware_dt Tests
# ==========================================================================
class TestToAwareDt:
    def test_none_returns_none(self):
        assert _to_aware_dt(None) is None

    def test_iso_string(self):
        result = _to_aware_dt("2025-06-15T10:30:00")
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_iso_string_with_tz(self):
        result = _to_aware_dt("2025-06-15T10:30:00+00:00")
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_invalid_string_returns_none(self):
        assert _to_aware_dt("not-a-date") is None

    def test_naive_datetime(self):
        naive = datetime(2025, 6, 15, 10, 30)
        result = _to_aware_dt(naive)
        assert result.tzinfo == UTC

    def test_aware_datetime_unchanged(self):
        aware = datetime(2025, 6, 15, 10, 30, tzinfo=UTC)
        result = _to_aware_dt(aware)
        assert result is aware

    def test_non_datetime_non_string_returns_none(self):
        assert _to_aware_dt(12345) is None
        assert _to_aware_dt(True) is None


# ==========================================================================
# _filter_records_by_date Tests
# ==========================================================================
class TestFilterRecordsByDate:
    def test_filter_within_range(self):
        now = datetime.now(UTC)
        records = [
            {"created_at": now - timedelta(hours=1)},
            {"created_at": now - timedelta(days=2)},
            {"created_at": now + timedelta(hours=1)},
        ]
        start = now - timedelta(hours=2)
        end = now + timedelta(hours=2)
        result = _filter_records_by_date(records, start, end)
        assert len(result) == 2  # Only the first and third

    def test_filter_empty_records(self):
        now = datetime.now(UTC)
        result = _filter_records_by_date([], now - timedelta(days=1), now)
        assert result == []

    def test_filter_custom_date_field(self):
        now = datetime.now(UTC)
        records = [{"scheduled_date": now}]
        result = _filter_records_by_date(
            records,
            now - timedelta(hours=1),
            now + timedelta(hours=1),
            date_field="scheduled_date",
        )
        assert len(result) == 1

    def test_filter_none_date_excluded(self):
        now = datetime.now(UTC)
        records = [{"created_at": None}, {"created_at": now}]
        result = _filter_records_by_date(records, now - timedelta(hours=1), now + timedelta(hours=1))
        assert len(result) == 1


# ==========================================================================
# _build_vehicle_summary Tests
# ==========================================================================
class TestBuildVehicleSummary:
    def test_empty_vehicles(self):
        summary = _build_vehicle_summary([])
        assert summary.total == 0
        assert summary.active == 0
        assert summary.utilization_rate == 0.0

    def test_mixed_statuses(self):
        vehicles = [
            {"status": "available"},
            {"status": "in_transit"},
            {"status": "loading"},
            {"status": "maintenance"},
            {"status": "out_of_service"},
        ]
        summary = _build_vehicle_summary(vehicles)
        assert summary.total == 5
        assert summary.active == 2  # in_transit + loading
        assert summary.idle == 1  # available
        assert summary.maintenance == 1
        assert summary.out_of_service == 1
        assert summary.utilization_rate == pytest.approx(40.0, abs=0.1)

    def test_all_available(self):
        vehicles = [{"status": "available"}, {"status": "available"}]
        summary = _build_vehicle_summary(vehicles)
        assert summary.active == 0
        assert summary.idle == 2
        assert summary.utilization_rate == 0.0


# ==========================================================================
# _build_shipment_summary Tests
# ==========================================================================
class TestBuildShipmentSummary:
    def test_empty_shipments(self):
        summary = _build_shipment_summary([])
        assert summary.total == 0
        assert summary.on_time_rate == 0.0

    def test_mixed_shipments(self):
        now = datetime.now(UTC)
        shipments = [
            {"status": "scheduled", "actual_arrival": None, "estimated_arrival": None},
            {"status": "in_transit", "actual_arrival": None, "estimated_arrival": None},
            {
                "status": "delivered",
                "actual_arrival": now,
                "estimated_arrival": now + timedelta(hours=1),
            },
            {"status": "cancelled", "actual_arrival": None, "estimated_arrival": None},
        ]
        summary = _build_shipment_summary(shipments)
        assert summary.total == 4
        assert summary.pending == 1  # scheduled
        assert summary.delivered == 1
        assert summary.cancelled == 1
        assert summary.on_time_rate == 100.0  # 1 delivered, on time

    def test_delivered_no_estimate_counts_on_time(self):
        now = datetime.now(UTC)
        shipments = [
            {"status": "delivered", "actual_arrival": now, "estimated_arrival": None},
        ]
        summary = _build_shipment_summary(shipments)
        assert summary.on_time_rate == 100.0

    def test_late_delivery(self):
        now = datetime.now(UTC)
        shipments = [
            {
                "status": "delivered",
                "actual_arrival": now,
                "estimated_arrival": now - timedelta(hours=1),
            },
        ]
        summary = _build_shipment_summary(shipments)
        assert summary.on_time_rate == 0.0


# ==========================================================================
# _build_collection_summary Tests
# ==========================================================================
class TestBuildCollectionSummary:
    def test_empty_collections(self):
        summary = _build_collection_summary([])
        assert summary.total_collections == 0
        assert summary.total_weight_kg == 0.0
        assert summary.fields_covered == 0

    def test_mixed_collections(self):
        collections = [
            {
                "field_id": "f1",
                "crop_type": "wheat",
                "crop_type_ar": "قمح",
                "estimated_quantity_kg": 2000,
                "actual_quantity_kg": 1800,
                "priority": "high",
            },
            {
                "field_id": "f2",
                "crop_type": "wheat",
                "crop_type_ar": "قمح",
                "estimated_quantity_kg": 1500,
                "actual_quantity_kg": None,
                "priority": "medium",
            },
            {
                "field_id": "f1",
                "crop_type": "tomato",
                "crop_type_ar": "طماطم",
                "estimated_quantity_kg": 800,
                "actual_quantity_kg": 750,
                "priority": "urgent",
            },
        ]
        summary = _build_collection_summary(collections)
        assert summary.total_collections == 3
        assert summary.total_weight_kg == 4300.0
        assert summary.actual_weight_kg == 2550.0
        assert summary.fields_covered == 2
        assert len(summary.by_crop) == 2  # wheat and tomato


# ==========================================================================
# Report Response Model Tests
# ==========================================================================
class TestReportModels:
    def test_vehicle_summary_model(self):
        vs = VehicleSummary(
            total=10,
            active=3,
            idle=5,
            maintenance=2,
            utilization_rate=30.0,
        )
        assert vs.out_of_service == 0  # default

    def test_cost_summary_model(self):
        cs = CostSummary(
            fuel_cost=1000,
            maintenance_cost=500,
            labor_cost=800,
            total_cost=2300,
            cost_per_delivery=115,
        )
        assert cs.currency == "SAR"

    def test_daily_report_model(self):
        vs = VehicleSummary(total=1, active=0, idle=1, maintenance=0, utilization_rate=0.0)
        ss = ShipmentSummary(total=0, pending=0, in_transit=0, delivered=0, cancelled=0, on_time_rate=0.0)
        cs = CollectionSummary(total_collections=0, total_weight_kg=0, fields_covered=0)
        report = DailyReportResponse(
            report_date="2025-06-15",
            tenant_id="tenant_demo",
            vehicles=vs,
            shipments=ss,
            collections=cs,
            generated_at="2025-06-15T10:00:00Z",
        )
        assert report.report_type == "daily"
        assert report.report_type_ar == "يومي"

    def test_weekly_report_model(self):
        vs = VehicleSummary(total=1, active=0, idle=1, maintenance=0, utilization_rate=0.0)
        ss = ShipmentSummary(total=0, pending=0, in_transit=0, delivered=0, cancelled=0, on_time_rate=0.0)
        cs = CollectionSummary(total_collections=0, total_weight_kg=0, fields_covered=0)
        report = WeeklyReportResponse(
            week_start="2025-06-09",
            week_end="2025-06-15",
            tenant_id="tenant_demo",
            vehicles=vs,
            shipments=ss,
            collections=cs,
            generated_at="2025-06-15T10:00:00Z",
        )
        assert report.report_type == "weekly"

    def test_monthly_report_model(self):
        vs = VehicleSummary(total=1, active=0, idle=1, maintenance=0, utilization_rate=0.0)
        ss = ShipmentSummary(total=0, pending=0, in_transit=0, delivered=0, cancelled=0, on_time_rate=0.0)
        cs = CollectionSummary(total_collections=0, total_weight_kg=0, fields_covered=0)
        cost = CostSummary(fuel_cost=0, maintenance_cost=0, labor_cost=0, total_cost=0, cost_per_delivery=0)
        report = MonthlyReportResponse(
            month="2025-06",
            month_start="2025-06-01",
            month_end="2025-06-30",
            tenant_id="tenant_demo",
            vehicles=vs,
            shipments=ss,
            collections=cs,
            costs=cost,
            generated_at="2025-06-30T10:00:00Z",
        )
        assert report.report_type == "monthly"
        assert report.report_type_ar == "شهري"
