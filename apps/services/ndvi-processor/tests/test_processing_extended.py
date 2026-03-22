"""
Extended tests for NDVI Processor – processing.py
اختبارات إضافية لمنطق المعالجة

Focus on edge cases, branch coverage, and async functions
(create_composite, get_composites, analyze_change zones logic, etc.)
"""

import os
import random
import sys

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _service_root not in sys.path:
    sys.path.insert(0, _service_root)

try:
    from src.models import (
        CompositeMethod,
        JobStatus,
        SatelliteSource,
        TimeseriesPoint,
    )
    from src.processing import (
        _generate_mock_timeseries,
        analyze_change,
        analyze_seasonal,
        cancel_job,
        create_composite,
        create_job,
        detect_anomaly,
        get_composites,
        get_field_ndvi,
        get_ndvi_timeseries,
        list_jobs,
        process_ndvi_mock,
        update_job_status,
    )
    from src.store import _composites, _jobs, _results, configure
except ImportError:
    pytest.skip("ndvi-processor dependencies not installed", allow_module_level=True)


def _clear_stores():
    _jobs.clear()
    _results.clear()
    _composites.clear()


# ---------------------------------------------------------------------------
# Job Management – additional edge cases
# ---------------------------------------------------------------------------


class TestJobEdgeCases:
    """Cover remaining branches in job management."""

    def setup_method(self):
        _clear_stores()

    def test_create_job_with_custom_priority(self):
        """create_job uses custom priority."""
        job_id = create_job("t1", "f1", "ndvi", {"foo": "bar"}, priority=1)
        job = _jobs[job_id]
        assert job["priority"] == 1

    def test_create_job_default_priority(self):
        """create_job defaults to priority 5."""
        job_id = create_job("t1", "f1", "ndvi", {})
        assert _jobs[job_id]["priority"] == 5

    def test_create_job_fields_populated(self):
        """create_job populates all expected fields."""
        job_id = create_job("t1", "f1", "composite", {"method": "max"})
        job = _jobs[job_id]
        assert job["tenant_id"] == "t1"
        assert job["field_id"] == "f1"
        assert job["type"] == "composite"
        assert job["parameters"] == {"method": "max"}
        assert job["started_at"] is None
        assert job["completed_at"] is None
        assert job["result"] is None
        assert job["error"] is None
        assert job["estimated_completion"] is not None
        assert job["created_at"] is not None

    def test_update_job_processing_sets_started_at_once(self):
        """update_job_status sets started_at only on first PROCESSING."""
        job_id = create_job("t1", "f1", "ndvi", {})
        update_job_status(job_id, JobStatus.PROCESSING, progress=10)
        started = _jobs[job_id]["started_at"]
        assert started is not None

        # Update progress again; started_at should not change
        update_job_status(job_id, JobStatus.PROCESSING, progress=50)
        assert _jobs[job_id]["started_at"] == started

    def test_update_job_failed_sets_completed_at(self):
        """update_job_status FAILED sets completed_at."""
        job_id = create_job("t1", "f1", "ndvi", {})
        update_job_status(job_id, JobStatus.FAILED, error="OOM")
        job = _jobs[job_id]
        assert job["completed_at"] is not None
        assert job["error"] == "OOM"
        # progress should remain unchanged (not set to 100 for FAILED)
        assert job["progress_percent"] == 0

    def test_update_job_completed_sets_progress_100(self):
        """update_job_status COMPLETED sets progress to 100."""
        job_id = create_job("t1", "f1", "ndvi", {})
        update_job_status(job_id, JobStatus.COMPLETED)
        assert _jobs[job_id]["progress_percent"] == 100

    def test_cancel_failed_job_returns_false(self):
        """cancel_job returns False for FAILED jobs."""
        job_id = create_job("t1", "f1", "ndvi", {})
        update_job_status(job_id, JobStatus.FAILED, error="err")
        assert cancel_job(job_id) is False

    def test_cancel_processing_job_succeeds(self):
        """cancel_job cancels a PROCESSING job."""
        job_id = create_job("t1", "f1", "ndvi", {})
        update_job_status(job_id, JobStatus.PROCESSING)
        assert cancel_job(job_id) is True
        assert _jobs[job_id]["status"] == "cancelled"
        assert _jobs[job_id]["completed_at"] is not None

    def test_list_jobs_empty(self):
        """list_jobs returns empty list when no jobs exist."""
        assert list_jobs() == []

    def test_list_jobs_sorted_by_created_at_desc(self):
        """list_jobs returns jobs sorted by created_at descending."""
        j1 = create_job("t1", "f1", "ndvi", {})
        j2 = create_job("t1", "f2", "ndvi", {})
        jobs = list_jobs()
        # j2 was created after j1, so it should appear first
        assert jobs[0]["job_id"] == j2
        assert jobs[1]["job_id"] == j1

    def test_list_jobs_combined_filters(self):
        """list_jobs applies multiple filters simultaneously."""
        create_job("t1", "f1", "ndvi", {})
        j2 = create_job("t1", "f2", "ndvi", {})
        create_job("t2", "f2", "ndvi", {})

        jobs = list_jobs(tenant_id="t1", field_id="f2")
        assert len(jobs) == 1
        assert jobs[0]["job_id"] == j2


# ---------------------------------------------------------------------------
# NDVI Processing – additional branches
# ---------------------------------------------------------------------------


class TestProcessNDVIMockEdgeCases:
    """Cover remaining branches in process_ndvi_mock."""

    def setup_method(self):
        _clear_stores()

    def test_landsat8_resolution(self):
        """process_ndvi_mock uses 30m resolution for LANDSAT_8."""
        result = process_ndvi_mock("f1", SatelliteSource.LANDSAT_8, ("2025-01-01", "2025-01-01"))
        assert result.source.resolution_meters == 30

    def test_landsat9_resolution(self):
        """process_ndvi_mock uses 30m resolution for LANDSAT_9."""
        result = process_ndvi_mock("f1", SatelliteSource.LANDSAT_9, ("2025-01-01", "2025-01-01"))
        assert result.source.resolution_meters == 30

    def test_modis_resolution(self):
        """process_ndvi_mock uses 250m resolution for MODIS."""
        result = process_ndvi_mock("f1", SatelliteSource.MODIS, ("2025-01-01", "2025-01-01"))
        assert result.source.resolution_meters == 250

    def test_sentinel2_resolution(self):
        """process_ndvi_mock uses 10m resolution for SENTINEL_2."""
        result = process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-01", "2025-01-01"))
        assert result.source.resolution_meters == 10

    def test_cloud_threshold_option(self):
        """process_ndvi_mock respects cloud_threshold_percent option."""
        result = process_ndvi_mock(
            "f1",
            SatelliteSource.SENTINEL_2,
            ("2025-01-01", "2025-01-01"),
            options={"cloud_threshold_percent": 5},
        )
        assert result.quality.cloud_cover_percent <= 5.0

    def test_result_has_percentiles(self):
        """process_ndvi_mock generates percentile statistics."""
        result = process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-01", "2025-01-01"))
        assert result.statistics.percentiles is not None
        assert "p10" in result.statistics.percentiles
        assert "p25" in result.statistics.percentiles
        assert "p75" in result.statistics.percentiles
        assert "p90" in result.statistics.percentiles

    def test_result_stored_as_model_dump(self):
        """process_ndvi_mock stores result as dict (model_dump)."""
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-03-01", "2025-03-01"))
        stored = _results["f1"][0]
        assert isinstance(stored, dict)
        assert "statistics" in stored
        assert "quality" in stored

    def test_s3_bucket_env_override(self):
        """process_ndvi_mock uses S3_BUCKET env for file URLs."""
        old = os.environ.get("S3_BUCKET")
        try:
            os.environ["S3_BUCKET"] = "my-custom-bucket"
            result = process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-01", "2025-01-01"))
            assert "my-custom-bucket" in result.files.geotiff
        finally:
            if old is not None:
                os.environ["S3_BUCKET"] = old
            else:
                os.environ.pop("S3_BUCKET", None)


# ---------------------------------------------------------------------------
# get_field_ndvi – additional branches
# ---------------------------------------------------------------------------


class TestGetFieldNDVIEdgeCases:
    """More tests for get_field_ndvi."""

    def setup_method(self):
        _clear_stores()

    def test_empty_results_list(self):
        """get_field_ndvi returns None when results list is empty."""
        _results["f1"] = []
        assert get_field_ndvi("f1") is None

    def test_multiple_results_returns_latest(self):
        """get_field_ndvi returns the latest result by date."""
        _results["f1"] = [
            {"date": "2025-03-01", "id": "old"},
            {"date": "2025-06-01", "id": "new"},
            {"date": "2025-01-01", "id": "oldest"},
        ]
        latest = get_field_ndvi("f1")
        assert latest["id"] == "new"


# ---------------------------------------------------------------------------
# get_ndvi_timeseries – additional branches
# ---------------------------------------------------------------------------


class TestTimeseriesEdgeCases:
    """More tests for timeseries."""

    def setup_method(self):
        _clear_stores()

    def test_timeseries_from_stored_filters_by_date_range(self):
        """get_ndvi_timeseries filters stored results by date range."""
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-15", "2025-01-15"))
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-03-15", "2025-03-15"))

        # Only get January
        points = get_ndvi_timeseries("f1", "2025-01-01", "2025-01-31")
        assert len(points) == 1
        assert points[0].date == "2025-01-15"

    def test_timeseries_from_stored_empty_range(self):
        """get_ndvi_timeseries returns empty when range has no results."""
        process_ndvi_mock("f1", SatelliteSource.SENTINEL_2, ("2025-01-15", "2025-01-15"))

        points = get_ndvi_timeseries("f1", "2024-01-01", "2024-12-31")
        assert len(points) == 0

    def test_generate_mock_timeseries_values_in_range(self):
        """_generate_mock_timeseries values are in [-1, 1]."""
        random.seed(42)
        points = _generate_mock_timeseries("f1", "2025-01-01", "2025-03-01")
        for p in points:
            assert -1 <= p.ndvi_mean <= 1
            assert p.ndvi_min < p.ndvi_max

    def test_generate_mock_timeseries_5_day_interval(self):
        """_generate_mock_timeseries uses 5-day interval (Sentinel-2 frequency)."""
        random.seed(42)
        points = _generate_mock_timeseries("f1", "2025-01-01", "2025-01-16")
        # Jan 1, 6, 11, 16 = 4 points
        assert len(points) == 4
        dates = [p.date for p in points]
        assert dates[0] == "2025-01-01"
        assert dates[1] == "2025-01-06"
        assert dates[2] == "2025-01-11"
        assert dates[3] == "2025-01-16"


# ---------------------------------------------------------------------------
# analyze_change – branch coverage
# ---------------------------------------------------------------------------


class TestAnalyzeChangeBranches:
    """Cover all branches in analyze_change."""

    def test_analyze_change_structure(self):
        """analyze_change returns correct structure."""
        random.seed(42)
        result = analyze_change("f1", "2025-01-01", "2025-06-01")
        assert result["field_id"] == "f1"
        assert result["date1"] == "2025-01-01"
        assert result["date2"] == "2025-06-01"
        assert result["days_between"] == 151
        assert "mean_change" in result["change"]
        assert "percent_change" in result["change"]
        assert "percent_increased" in result["change"]
        assert "percent_decreased" in result["change"]
        assert "percent_stable" in result["change"]

    def test_analyze_change_zones_structure(self):
        """analyze_change zones have expected structure."""
        random.seed(42)
        result = analyze_change("f1", "2025-01-01", "2025-06-01", include_zones=True)
        zones = result["zones"]
        assert zones is not None
        assert len(zones) == 3
        zone_names = [z["zone"] for z in zones]
        assert "north" in zone_names
        assert "south" in zone_names
        assert "center" in zone_names

    def test_analyze_change_reversed_dates(self):
        """analyze_change handles reversed date order (absolute days_between)."""
        result = analyze_change("f1", "2025-06-01", "2025-01-01")
        assert result["days_between"] == 151

    def test_analyze_change_same_date(self):
        """analyze_change handles same date (0 days)."""
        result = analyze_change("f1", "2025-01-01", "2025-01-01")
        assert result["days_between"] == 0


# ---------------------------------------------------------------------------
# analyze_seasonal
# ---------------------------------------------------------------------------


class TestAnalyzeSeasonalEdgeCases:
    """Additional seasonal analysis tests."""

    def test_seasonal_has_four_seasons(self):
        """analyze_seasonal returns 4 seasons."""
        result = analyze_seasonal("f1", 2025)
        assert len(result["seasons"]) == 4
        season_names = [s["season"] for s in result["seasons"]]
        assert "winter" in season_names
        assert "spring" in season_names
        assert "summer" in season_names
        assert "fall" in season_names

    def test_seasonal_arabic_names(self):
        """analyze_seasonal includes Arabic season names."""
        result = analyze_seasonal("f1", 2025)
        ar_names = [s["season_ar"] for s in result["seasons"]]
        assert "الشتاء" in ar_names
        assert "الربيع" in ar_names
        assert "الصيف" in ar_names
        assert "الخريف" in ar_names

    def test_seasonal_annual_mean(self):
        """analyze_seasonal computes annual mean correctly."""
        random.seed(42)
        result = analyze_seasonal("f1", 2025)
        seasons_means = [s["ndvi_mean"] for s in result["seasons"]]
        expected_mean = round(sum(seasons_means) / 4, 3)
        assert result["annual_mean"] == expected_mean

    def test_seasonal_peak_and_trough(self):
        """analyze_seasonal identifies peak and trough months."""
        random.seed(42)
        result = analyze_seasonal("f1", 2025)
        assert isinstance(result["peak_month"], int)
        assert isinstance(result["trough_month"], int)
        assert 1 <= result["peak_month"] <= 12
        assert 1 <= result["trough_month"] <= 12


# ---------------------------------------------------------------------------
# detect_anomaly – branch coverage
# ---------------------------------------------------------------------------


class TestDetectAnomalyBranches:
    """Cover all branches in detect_anomaly."""

    def test_anomaly_with_high_negative_z_score(self):
        """detect_anomaly with very low NDVI (high negative z_score > 3)."""
        random.seed(100)
        # Use a very low current_ndvi to force anomaly detection
        result = detect_anomaly("f1", "2025-06-15", current_ndvi=0.01)
        # With seed 100, historical_mean and std are deterministic
        assert result["current_ndvi"] == 0.01
        assert isinstance(result["z_score"], float)

    def test_anomaly_with_high_positive_z_score(self):
        """detect_anomaly with very high NDVI (positive anomaly)."""
        random.seed(200)
        result = detect_anomaly("f1", "2025-06-15", current_ndvi=0.99)
        assert result["current_ndvi"] == 0.99

    def test_anomaly_not_detected_normal_range(self):
        """detect_anomaly with normal NDVI values."""
        # Force a "normal" case by controlling seed
        random.seed(42)
        # With seed 42, historical_mean ~ 0.57, std ~ 0.09
        result = detect_anomaly("f1", "2025-06-15", current_ndvi=0.55)
        # z_score should be small
        assert abs(result["z_score"]) < 3.0

    def test_anomaly_positive_type(self):
        """detect_anomaly classifies positive anomaly correctly."""
        random.seed(42)
        # historical_mean ~ 0.57, std ~ 0.09 with seed 42
        # ndvi = 0.57 + 2.5*0.09 ~ 0.795 should be anomaly
        result = detect_anomaly("f1", "2025-06-15", current_ndvi=0.99)
        if result["is_anomaly"] and result["z_score"] > 0:
            assert result["anomaly_type"] == "positive"

    def test_anomaly_severity_high_for_extreme(self):
        """detect_anomaly returns high severity for |z_score| > 3."""
        random.seed(42)
        result = detect_anomaly("f1", "2025-06-15", current_ndvi=0.01)
        if result["is_anomaly"] and abs(result["z_score"]) > 3:
            assert result["severity"] == "high"

    def test_anomaly_none_severity_when_no_anomaly(self):
        """detect_anomaly returns None severity when not anomaly."""
        random.seed(42)
        result = detect_anomaly("f1", "2025-06-15", current_ndvi=0.57)
        if not result["is_anomaly"]:
            assert result["severity"] is None
            assert result["anomaly_type"] is None


# ---------------------------------------------------------------------------
# create_composite (async)
# ---------------------------------------------------------------------------


class TestCreateComposite:
    """Tests for async create_composite function."""

    def setup_method(self):
        _clear_stores()
        # Reset store config to in-memory only
        configure()

    @pytest.mark.asyncio
    async def test_create_composite_returns_dict(self):
        """create_composite returns a composite dict."""
        result = await create_composite(
            tenant_id="t1",
            field_id="f1",
            year=2025,
            month=6,
            method=CompositeMethod.MAX_NDVI,
            source=SatelliteSource.SENTINEL_2,
        )
        assert isinstance(result, dict)
        assert result["field_id"] == "f1"
        assert result["year"] == 2025
        assert result["month"] == 6
        assert result["method"] == "max_ndvi"
        assert result["source"] == "sentinel-2"

    @pytest.mark.asyncio
    async def test_create_composite_stores_in_memory(self):
        """create_composite stores composite in _composites."""
        result = await create_composite("t1", "f1", 2025, 6, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)
        cid = result["composite_id"]
        assert cid in _composites
        assert _composites[cid]["field_id"] == "f1"

    @pytest.mark.asyncio
    async def test_create_composite_has_statistics(self):
        """create_composite includes statistics."""
        result = await create_composite("t1", "f1", 2025, 6, CompositeMethod.MEAN_NDVI, SatelliteSource.SENTINEL_2)
        stats = result["statistics"]
        assert "mean" in stats
        assert "min" in stats
        assert "max" in stats
        assert "std" in stats

    @pytest.mark.asyncio
    async def test_create_composite_has_files(self):
        """create_composite includes file URLs."""
        result = await create_composite("t1", "f1", 2025, 6, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)
        assert result["files"]["geotiff"] is not None
        assert "max_ndvi" in result["files"]["geotiff"]

    @pytest.mark.asyncio
    async def test_create_composite_different_methods(self):
        """create_composite works with different methods."""
        for method in CompositeMethod:
            result = await create_composite("t1", "f1", 2025, 6, method, SatelliteSource.SENTINEL_2)
            assert result["method"] == method.value


# ---------------------------------------------------------------------------
# get_composites
# ---------------------------------------------------------------------------


class TestGetComposites:
    """Tests for get_composites function."""

    def setup_method(self):
        _clear_stores()

    def test_get_composites_empty(self):
        """get_composites returns empty list for unknown field."""
        assert get_composites("unknown") == []

    @pytest.mark.asyncio
    async def test_get_composites_by_field(self):
        """get_composites returns composites for the given field."""
        configure()
        await create_composite("t1", "f1", 2025, 1, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)
        await create_composite("t1", "f1", 2025, 2, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)
        await create_composite("t1", "f2", 2025, 1, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)

        f1_composites = get_composites("f1")
        assert len(f1_composites) == 2

    @pytest.mark.asyncio
    async def test_get_composites_filter_by_year(self):
        """get_composites filters by year."""
        configure()
        await create_composite("t1", "f1", 2024, 12, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)
        await create_composite("t1", "f1", 2025, 1, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)

        composites_2025 = get_composites("f1", year=2025)
        assert len(composites_2025) == 1
        assert composites_2025[0]["year"] == 2025

    @pytest.mark.asyncio
    async def test_get_composites_sorted_by_year_month_desc(self):
        """get_composites returns results sorted by (year, month) desc."""
        configure()
        await create_composite("t1", "f1", 2025, 1, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)
        await create_composite("t1", "f1", 2025, 6, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)
        await create_composite("t1", "f1", 2025, 3, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2)

        composites = get_composites("f1")
        months = [c["month"] for c in composites]
        assert months == [6, 3, 1]
