"""
Unit Tests for NDVI Processor Service - Processing & Models
اختبارات وحدة خدمة معالج NDVI - المعالجة والنماذج

Tests for the FastAPI service source code under apps/services/ndvi-processor/src/.
These ensure coverage is collected for the apps/services tree in CI.
"""

import os
import sys

import pytest

# Ensure the project root is on sys.path so that "shared.*" imports resolve,
# and the service package can be imported as "src.*" via the apps path.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Add the ndvi-processor service directory so "src" resolves as a package.
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _service_root not in sys.path:
    sys.path.insert(0, _service_root)

try:
    from src.models import (
        ChangeAnalysisResponse,
        CompositeMethod,
        CompositeResponse,
        DateRange,
        ExportFormat,
        FileUrls,
        JobResponse,
        JobStatus,
        NDVIResult,
        NDVIStatistics,
        ProcessingInfo,
        ProcessRequest,
        QualityMetrics,
        SatelliteSource,
        SeasonalAnalysisResponse,
        SourceInfo,
        TimeseriesPoint,
        TimeseriesResponse,
        TrendDirection,
        ZoneChange,
    )
    from src.processing import (
        analyze_change,
        analyze_seasonal,
        cancel_job,
        create_job,
        detect_anomaly,
        get_composites,
        get_field_ndvi,
        get_job,
        get_ndvi_timeseries,
        list_jobs,
        process_ndvi_mock,
        update_job_status,
    )
    from src.store import _composites, _jobs, _results
except ImportError:
    pytest.skip("ndvi-processor dependencies not installed", allow_module_level=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clear_stores():
    """Reset in-memory stores between tests."""
    _jobs.clear()
    _results.clear()
    _composites.clear()


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------


class TestModels:
    """Tests for Pydantic data models."""

    def test_satellite_source_enum(self):
        assert SatelliteSource.SENTINEL_2 == "sentinel-2"
        assert SatelliteSource.LANDSAT_8 == "landsat-8"

    def test_job_status_enum(self):
        assert JobStatus.QUEUED == "queued"
        assert JobStatus.COMPLETED == "completed"

    def test_export_format_enum(self):
        assert ExportFormat.GEOTIFF == "geotiff"
        assert ExportFormat.CSV == "csv"

    def test_composite_method_enum(self):
        assert CompositeMethod.MAX_NDVI == "max_ndvi"

    def test_trend_direction_enum(self):
        assert TrendDirection.IMPROVING == "improving"
        assert TrendDirection.STABLE == "stable"

    def test_date_range_model(self):
        dr = DateRange(start="2025-01-01", end="2025-01-31")
        assert dr.start == "2025-01-01"
        assert dr.end == "2025-01-31"

    def test_ndvi_statistics_model(self):
        stats = NDVIStatistics(mean=0.5, std=0.1, min=0.2, max=0.8)
        assert stats.mean == 0.5
        assert stats.median is None

    def test_quality_metrics_model(self):
        qm = QualityMetrics(cloud_cover_percent=10.0, valid_pixels_percent=90.0)
        assert qm.shadow_percent is None

    def test_file_urls_model(self):
        fu = FileUrls(geotiff="s3://bucket/file.tif")
        assert fu.png is None

    def test_timeseries_point_model(self):
        tp = TimeseriesPoint(
            date="2025-01-15",
            ndvi_mean=0.6,
            ndvi_min=0.4,
            ndvi_max=0.8,
            cloud_cover_percent=5.0,
            source="sentinel-2",
        )
        assert tp.ndvi_mean == 0.6

    def test_zone_change_model(self):
        zc = ZoneChange(
            zone="north",
            zone_name_ar="الشمال",
            ndvi_date1=0.5,
            ndvi_date2=0.6,
            change=0.1,
            change_percent=20.0,
            trend=TrendDirection.IMPROVING,
        )
        assert zc.change == 0.1

    def test_process_request_model(self):
        pr = ProcessRequest(
            tenant_id="t1",
            field_id="f1",
            date_range=DateRange(start="2025-01-01", end="2025-01-31"),
        )
        assert pr.source == SatelliteSource.SENTINEL_2
        assert pr.priority == 5


# ---------------------------------------------------------------------------
# Processing Logic Tests
# ---------------------------------------------------------------------------


class TestJobManagement:
    """Tests for job CRUD operations."""

    def setup_method(self):
        _clear_stores()

    def test_create_and_get_job(self):
        job_id = create_job(
            tenant_id="tenant-1",
            field_id="field-1",
            job_type="ndvi_calculation",
            parameters={"source": "sentinel-2"},
        )
        assert isinstance(job_id, str)

        job = get_job(job_id)
        assert job is not None
        assert job["status"] == "queued"
        assert job["field_id"] == "field-1"
        assert job["progress_percent"] == 0

    def test_get_nonexistent_job(self):
        assert get_job("nonexistent-id") is None

    def test_update_job_status_processing(self):
        job_id = create_job("t1", "f1", "ndvi", {})
        updated = update_job_status(job_id, JobStatus.PROCESSING, progress=50)
        assert updated["status"] == "processing"
        assert updated["progress_percent"] == 50
        assert updated["started_at"] is not None

    def test_update_job_status_completed(self):
        job_id = create_job("t1", "f1", "ndvi", {})
        update_job_status(job_id, JobStatus.PROCESSING)
        updated = update_job_status(job_id, JobStatus.COMPLETED, progress=100, result={"ndvi_mean": 0.6})
        assert updated["status"] == "completed"
        assert updated["completed_at"] is not None
        assert updated["result"]["ndvi_mean"] == 0.6

    def test_update_job_status_failed(self):
        job_id = create_job("t1", "f1", "ndvi", {})
        updated = update_job_status(job_id, JobStatus.FAILED, error="timeout")
        assert updated["status"] == "failed"
        assert updated["error"] == "timeout"

    def test_update_nonexistent_job(self):
        assert update_job_status("nope", JobStatus.PROCESSING) is None

    def test_cancel_job(self):
        job_id = create_job("t1", "f1", "ndvi", {})
        assert cancel_job(job_id) is True
        job = get_job(job_id)
        assert job["status"] == "cancelled"

    def test_cancel_completed_job_fails(self):
        job_id = create_job("t1", "f1", "ndvi", {})
        update_job_status(job_id, JobStatus.COMPLETED)
        assert cancel_job(job_id) is False

    def test_cancel_nonexistent_job_fails(self):
        assert cancel_job("nope") is False

    def test_list_jobs_by_tenant(self):
        create_job("t1", "f1", "ndvi", {})
        create_job("t2", "f2", "ndvi", {})
        jobs = list_jobs(tenant_id="t1")
        assert len(jobs) == 1
        assert jobs[0]["tenant_id"] == "t1"

    def test_list_jobs_filter_tenant(self):
        create_job("t1", "f1", "ndvi", {})
        create_job("t2", "f2", "ndvi", {})
        jobs = list_jobs(tenant_id="t1")
        assert len(jobs) == 1
        assert jobs[0]["tenant_id"] == "t1"

    def test_list_jobs_filter_field(self):
        create_job("t1", "f1", "ndvi", {})
        create_job("t1", "f2", "ndvi", {})
        jobs = list_jobs(tenant_id="t1", field_id="f2")
        assert len(jobs) == 1

    def test_list_jobs_filter_status(self):
        j1 = create_job("t1", "f1", "ndvi", {})
        create_job("t1", "f2", "ndvi", {})
        update_job_status(j1, JobStatus.COMPLETED)
        jobs = list_jobs(tenant_id="t1", status="completed")
        assert len(jobs) == 1


class TestNDVIProcessing:
    """Tests for NDVI processing mock."""

    def setup_method(self):
        _clear_stores()

    def test_process_ndvi_mock_returns_result(self):
        result = process_ndvi_mock(
            field_id="field-001",
            source=SatelliteSource.SENTINEL_2,
            date_range=("2025-01-01", "2025-01-15"),
        )
        assert isinstance(result, NDVIResult)
        assert result.field_id == "field-001"
        assert result.date == "2025-01-01"
        assert -1 <= result.statistics.mean <= 1
        assert result.files.geotiff is not None

    def test_process_ndvi_mock_stores_result(self):
        process_ndvi_mock(
            field_id="field-002",
            source=SatelliteSource.SENTINEL_2,
            date_range=("2025-02-01", "2025-02-28"),
        )
        assert "field-002" in _results
        assert len(_results["field-002"]) >= 1

    def test_process_ndvi_mock_different_sources(self):
        for src in SatelliteSource:
            result = process_ndvi_mock(
                field_id=f"field-src-{src.value}",
                source=src,
                date_range=("2025-01-01", "2025-01-01"),
            )
            assert result.source.satellite == src.value

    def test_process_ndvi_mock_with_options(self):
        result = process_ndvi_mock(
            field_id="field-opts",
            source=SatelliteSource.SENTINEL_2,
            date_range=("2025-01-01", "2025-01-01"),
            options={"atmospheric_correction": False, "cloud_masking": False},
        )
        assert result.processing.atmospheric_correction is None
        assert result.processing.cloud_mask is None


class TestFieldNDVI:
    """Tests for get_field_ndvi."""

    def setup_method(self):
        _clear_stores()

    def test_get_field_ndvi_empty(self):
        assert get_field_ndvi("no-such-field") is None

    def test_get_field_ndvi_latest(self):
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-01", "2025-01-01"))
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-02-01", "2025-02-01"))
        latest = get_field_ndvi("f1")
        assert latest is not None
        assert latest["date"] == "2025-02-01"

    def test_get_field_ndvi_by_date(self):
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-01", "2025-01-01"))
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-02-01", "2025-02-01"))
        result = get_field_ndvi("f1", "2025-01-01")
        assert result is not None
        assert result["date"] == "2025-01-01"

    def test_get_field_ndvi_date_not_found(self):
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-01", "2025-01-01"))
        assert get_field_ndvi("f1", "2099-12-31") is None


class TestTimeseries:
    """Tests for timeseries generation."""

    def setup_method(self):
        _clear_stores()

    def test_get_ndvi_timeseries_generates_mock(self):
        points = get_ndvi_timeseries("unknown-field", "2025-01-01", "2025-02-01")
        assert len(points) > 0
        assert all(isinstance(p, TimeseriesPoint) for p in points)

    def test_get_ndvi_timeseries_from_stored(self):
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-15", "2025-01-15"))
        points = get_ndvi_timeseries("f1", "2025-01-01", "2025-01-31")
        assert len(points) >= 1


class TestAnalysis:
    """Tests for change, seasonal, and anomaly analysis."""

    def test_analyze_change(self):
        result = analyze_change("f1", "2025-01-01", "2025-06-01")
        assert result["field_id"] == "f1"
        assert result["days_between"] > 0
        assert "change" in result
        assert "zones" in result

    def test_analyze_change_no_zones(self):
        result = analyze_change("f1", "2025-01-01", "2025-06-01", include_zones=False)
        assert result["zones"] is None

    def test_analyze_seasonal(self):
        result = analyze_seasonal("f1", 2025)
        assert result["field_id"] == "f1"
        assert result["year"] == 2025
        assert len(result["seasons"]) == 4
        assert "peak_month" in result
        assert "trough_month" in result

    def test_detect_anomaly_with_ndvi(self):
        result = detect_anomaly("f1", "2025-06-15", current_ndvi=0.1)
        assert result["field_id"] == "f1"
        assert result["current_ndvi"] == 0.1
        assert "z_score" in result
        assert isinstance(result["is_anomaly"], bool)

    def test_detect_anomaly_without_ndvi(self):
        result = detect_anomaly("f1", "2025-06-15")
        assert -1 <= result["current_ndvi"] <= 1


class TestStore:
    """Tests for the store module."""

    def setup_method(self):
        _clear_stores()

    def test_store_configure_no_args(self):
        from src.store import configure

        configure()  # should not raise

    def test_composites_empty(self):
        assert get_composites("f1") == []


class TestLifespan:
    """Regression tests for the FastAPI lifespan manager."""

    @pytest.mark.asyncio
    async def test_lifespan_passes_real_pool_to_store(self, monkeypatch):
        """When DATABASE_URL is set and create_pool succeeds, store.configure
        must receive the real pool (regression: previously received None because
        the local db_pool variable was never reassigned).
        """
        from unittest.mock import AsyncMock, MagicMock

        from src import main as main_module

        monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@pgbouncer:6432/db")
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.delenv("NATS_URL", raising=False)

        fake_pool = MagicMock(name="pool")
        fake_pool.close = AsyncMock()

        async def fake_create_pool(*_args, **_kwargs):
            return fake_pool

        fake_asyncpg = MagicMock()
        fake_asyncpg.create_pool = fake_create_pool
        monkeypatch.setitem(sys.modules, "asyncpg", fake_asyncpg)

        received: dict = {}

        async def fake_ensure_tables(pool):
            received["ensure_tables_pool"] = pool

        def fake_configure(db_pool=None, nats_client=None):
            received["configure_db_pool"] = db_pool
            received["configure_nats"] = nats_client

        monkeypatch.setattr(main_module.ndvi_store, "ensure_tables", fake_ensure_tables)
        monkeypatch.setattr(main_module.ndvi_store, "configure", fake_configure)

        async with main_module.lifespan(main_module.app):
            pass

        assert received["ensure_tables_pool"] is fake_pool
        assert received["configure_db_pool"] is fake_pool
        fake_pool.close.assert_awaited_once()


# ---------------------------------------------------------------------------
# Tenant Isolation Regression Tests
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    """Cross-tenant reads must not leak data once a tenant_id filter is supplied."""

    TENANT_A = "11111111-1111-1111-1111-111111111111"
    TENANT_B = "22222222-2222-2222-2222-222222222222"

    def setup_method(self):
        _clear_stores()

    def _seed(self, field_id: str, tenant_id: str, date: str) -> None:
        _results.setdefault(field_id, []).append(
            {
                "id": f"{tenant_id[:8]}-{date}",
                "tenant_id": tenant_id,
                "field_id": field_id,
                "date": date,
                "statistics": {"mean": 0.5, "min": 0.4, "max": 0.6, "std": 0.05},
                "quality": {"cloud_cover_percent": 5.0, "valid_pixels_percent": 95.0},
                "source": {"satellite": "sentinel-2", "resolution_meters": 10},
                "files": {"geotiff": "s3://x.tif"},
            }
        )

    def test_get_field_ndvi_filters_by_tenant(self):
        self._seed("field-1", self.TENANT_A, "2025-01-15")
        self._seed("field-1", self.TENANT_B, "2025-02-15")

        result_a = get_field_ndvi("field-1", tenant_id=self.TENANT_A)
        result_b = get_field_ndvi("field-1", tenant_id=self.TENANT_B)

        assert result_a is not None and result_a["tenant_id"] == self.TENANT_A
        assert result_b is not None and result_b["tenant_id"] == self.TENANT_B
        assert result_a["date"] != result_b["date"]

    def test_get_field_ndvi_returns_none_for_other_tenant(self):
        self._seed("field-1", self.TENANT_A, "2025-01-15")

        assert get_field_ndvi("field-1", tenant_id=self.TENANT_B) is None

    def test_get_field_ndvi_no_filter_returns_all(self):
        """Backwards compat: without tenant_id the reader sees everything (dev/test)."""
        self._seed("field-1", self.TENANT_A, "2025-01-15")
        self._seed("field-1", self.TENANT_B, "2025-02-15")

        result = get_field_ndvi("field-1")
        assert result is not None  # latest by date

    def test_get_ndvi_timeseries_filters_by_tenant(self):
        self._seed("field-1", self.TENANT_A, "2025-01-15")
        self._seed("field-1", self.TENANT_B, "2025-01-20")

        points_a = get_ndvi_timeseries("field-1", "2025-01-01", "2025-01-31", tenant_id=self.TENANT_A)

        assert len(points_a) == 1
        assert points_a[0].date == "2025-01-15"

    def test_get_composites_filters_by_tenant(self):
        _composites["c-a"] = {
            "composite_id": "c-a",
            "tenant_id": self.TENANT_A,
            "field_id": "field-1",
            "year": 2025,
            "month": 1,
        }
        _composites["c-b"] = {
            "composite_id": "c-b",
            "tenant_id": self.TENANT_B,
            "field_id": "field-1",
            "year": 2025,
            "month": 1,
        }

        only_a = get_composites("field-1", tenant_id=self.TENANT_A)
        assert len(only_a) == 1
        assert only_a[0]["composite_id"] == "c-a"

    def test_get_job_refuses_cross_tenant_lookup(self):
        job_id = create_job(
            tenant_id=self.TENANT_A, field_id="f1", job_type="ndvi_calculation", parameters={}
        )
        assert get_job(job_id, tenant_id=self.TENANT_A) is not None
        assert get_job(job_id, tenant_id=self.TENANT_B) is None
        # Unscoped lookup still works (used by internal/background paths).
        assert get_job(job_id) is not None

    def test_cancel_job_refuses_cross_tenant(self):
        job_id = create_job(
            tenant_id=self.TENANT_A, field_id="f1", job_type="ndvi_calculation", parameters={}
        )
        assert cancel_job(job_id, tenant_id=self.TENANT_B) is False
        # Ensure the job is still queued, not cancelled.
        job = get_job(job_id)
        assert job is not None and job["status"] == "queued"
        # Correct tenant can cancel.
        assert cancel_job(job_id, tenant_id=self.TENANT_A) is True


# ---------------------------------------------------------------------------
# Store tenant tagging regression
# ---------------------------------------------------------------------------


class TestStoreTenantTagging:
    """store.save_result / save_composite must tag tenant_id on in-memory records."""

    TENANT_A = "11111111-1111-1111-1111-111111111111"

    def setup_method(self):
        _clear_stores()

    @pytest.mark.asyncio
    async def test_save_result_tags_tenant_id(self):
        from src.store import save_result

        result_dict = {
            "id": "r1",
            "field_id": "field-1",
            "date": "2025-01-15",
            "statistics": {"mean": 0.5, "min": 0.4, "max": 0.6, "std": 0.05},
            "quality": {"cloud_cover_percent": 5.0, "valid_pixels_percent": 95.0},
            "source": {"satellite": "sentinel-2", "resolution_meters": 10},
            "files": {"geotiff": "s3://x.tif"},
        }

        await save_result("field-1", self.TENANT_A, result_dict)
        stored = _results["field-1"][0]
        assert stored["tenant_id"] == self.TENANT_A
        # Ensure original dict was not mutated.
        assert "tenant_id" not in result_dict

    @pytest.mark.asyncio
    async def test_save_composite_tags_tenant_id(self):
        from src.store import save_composite

        composite_dict = {
            "composite_id": "c1",
            "field_id": "field-1",
            "year": 2025,
            "month": 1,
            "method": "max_ndvi",
            "source": "sentinel-2",
            "statistics": {"mean": 0.5, "min": 0.4, "max": 0.6, "std": 0.05},
            "images_used": 5,
            "files": {"geotiff": "s3://x.tif"},
            "created_at": "2025-01-01T00:00:00+00:00",
        }

        await save_composite("c1", self.TENANT_A, composite_dict)
        assert _composites["c1"]["tenant_id"] == self.TENANT_A
        # Original dict not mutated.
        assert "tenant_id" not in composite_dict
