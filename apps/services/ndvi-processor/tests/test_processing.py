"""
Unit Tests for NDVI Processing Functions
اختبارات الوحدة لدوال معالجة NDVI
"""

from src.models import (
    CompositeMethod,
    JobStatus,
    SatelliteSource,
)
from src.processing import (
    analyze_change,
    analyze_seasonal,
    cancel_job,
    create_composite,
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


class TestJobManagement:
    """Test job creation and management"""

    def test_create_job(self):
        """Test creating a new processing job"""
        job_id = create_job(
            tenant_id="test_tenant",
            field_id="field_001",
            job_type="ndvi_calculation",
            parameters={"source": "sentinel-2"},
            priority=5,
        )

        assert job_id is not None
        assert isinstance(job_id, str)

        job = get_job(job_id)
        assert job is not None
        assert job["tenant_id"] == "test_tenant"
        assert job["field_id"] == "field_001"
        assert job["type"] == "ndvi_calculation"
        assert job["status"] == JobStatus.QUEUED.value
        assert job["priority"] == 5
        assert job["progress_percent"] == 0

    def test_get_job_not_found(self):
        """Test getting non-existent job"""
        job = get_job("nonexistent_job_id")
        assert job is None

    def test_update_job_status_to_processing(self):
        """Test updating job status to processing"""
        job_id = create_job(
            tenant_id="test_tenant",
            field_id="field_001",
            job_type="ndvi_calculation",
            parameters={},
        )

        updated_job = update_job_status(job_id, JobStatus.PROCESSING, progress=25)

        assert updated_job is not None
        assert updated_job["status"] == JobStatus.PROCESSING.value
        assert updated_job["progress_percent"] == 25
        assert updated_job["started_at"] is not None

    def test_update_job_status_to_completed(self):
        """Test updating job status to completed"""
        job_id = create_job(
            tenant_id="test_tenant",
            field_id="field_001",
            job_type="ndvi_calculation",
            parameters={},
        )

        result = {"ndvi_mean": 0.65, "files": {}}
        updated_job = update_job_status(
            job_id, JobStatus.COMPLETED, progress=100, result=result
        )

        assert updated_job is not None
        assert updated_job["status"] == JobStatus.COMPLETED.value
        assert updated_job["progress_percent"] == 100
        assert updated_job["completed_at"] is not None
        assert updated_job["result"] == result

    def test_update_job_status_to_failed(self):
        """Test updating job status to failed"""
        job_id = create_job(
            tenant_id="test_tenant",
            field_id="field_001",
            job_type="ndvi_calculation",
            parameters={},
        )

        updated_job = update_job_status(
            job_id, JobStatus.FAILED, error="Processing error"
        )

        assert updated_job is not None
        assert updated_job["status"] == JobStatus.FAILED.value
        assert updated_job["error"] == "Processing error"
        assert updated_job["completed_at"] is not None

    def test_cancel_job(self):
        """Test cancelling a job"""
        job_id = create_job(
            tenant_id="test_tenant",
            field_id="field_001",
            job_type="ndvi_calculation",
            parameters={},
        )

        success = cancel_job(job_id)
        assert success is True

        job = get_job(job_id)
        assert job["status"] == JobStatus.CANCELLED.value

    def test_cancel_completed_job(self):
        """Test cancelling a completed job (should fail)"""
        job_id = create_job(
            tenant_id="test_tenant",
            field_id="field_001",
            job_type="ndvi_calculation",
            parameters={},
        )

        update_job_status(job_id, JobStatus.COMPLETED)
        success = cancel_job(job_id)
        assert success is False

    def test_list_jobs_all(self):
        """Test listing all jobs"""
        create_job("tenant1", "field1", "ndvi", {})
        create_job("tenant1", "field2", "ndvi", {})
        create_job("tenant2", "field3", "ndvi", {})

        jobs = list_jobs()
        assert len(jobs) >= 3

    def test_list_jobs_by_tenant(self):
        """Test listing jobs filtered by tenant"""
        create_job("tenant_test", "field1", "ndvi", {})
        create_job("tenant_test", "field2", "ndvi", {})
        create_job("other_tenant", "field3", "ndvi", {})

        jobs = list_jobs(tenant_id="tenant_test")
        assert all(j["tenant_id"] == "tenant_test" for j in jobs)

    def test_list_jobs_by_field(self):
        """Test listing jobs filtered by field"""
        create_job("tenant1", "field_specific", "ndvi", {})
        create_job("tenant1", "field_specific", "ndvi", {})
        create_job("tenant1", "other_field", "ndvi", {})

        jobs = list_jobs(field_id="field_specific")
        assert all(j["field_id"] == "field_specific" for j in jobs)

    def test_list_jobs_by_status(self):
        """Test listing jobs filtered by status"""
        job_id1 = create_job("tenant1", "field1", "ndvi", {})
        create_job("tenant1", "field2", "ndvi", {})

        update_job_status(job_id1, JobStatus.COMPLETED)

        jobs = list_jobs(status=JobStatus.COMPLETED.value)
        assert len([j for j in jobs if j["job_id"] == job_id1]) > 0


class TestNDVIProcessing:
    """Test NDVI processing functions"""

    def test_process_ndvi_mock_sentinel2(self):
        """Test mock NDVI processing with Sentinel-2"""
        result = process_ndvi_mock(
            field_id="field_001",
            source=SatelliteSource.SENTINEL_2,
            date_range=("2025-12-01", "2025-12-15"),
        )

        assert result.field_id == "field_001"
        assert result.source.satellite == "sentinel-2"
        assert result.source.resolution_meters == 10
        assert -1 <= result.statistics.mean <= 1
        assert result.statistics.min <= result.statistics.mean <= result.statistics.max
        assert result.quality.cloud_cover_percent <= 20  # Default threshold

    def test_process_ndvi_mock_landsat(self):
        """Test mock NDVI processing with Landsat"""
        result = process_ndvi_mock(
            field_id="field_002",
            source=SatelliteSource.LANDSAT_8,
            date_range=("2025-12-01", "2025-12-15"),
        )

        assert result.source.satellite == "landsat-8"
        assert result.source.resolution_meters == 30

    def test_process_ndvi_mock_modis(self):
        """Test mock NDVI processing with MODIS"""
        result = process_ndvi_mock(
            field_id="field_003",
            source=SatelliteSource.MODIS,
            date_range=("2025-12-01", "2025-12-15"),
        )

        assert result.source.satellite == "modis"
        assert result.source.resolution_meters == 250

    def test_process_ndvi_with_options(self):
        """Test NDVI processing with custom options"""
        result = process_ndvi_mock(
            field_id="field_004",
            source=SatelliteSource.SENTINEL_2,
            date_range=("2025-12-01", "2025-12-15"),
            options={
                "atmospheric_correction": False,
                "cloud_masking": False,
                "cloud_threshold_percent": 30,
            },
        )

        assert result.processing.atmospheric_correction is None
        assert result.processing.cloud_mask is None

    def test_get_field_ndvi(self):
        """Test retrieving NDVI data for a field"""
        # First, process some NDVI data
        process_ndvi_mock(
            field_id="field_get_test",
            source=SatelliteSource.SENTINEL_2,
            date_range=("2025-12-01", "2025-12-01"),
        )

        result = get_field_ndvi("field_get_test")
        assert result is not None
        assert result["field_id"] == "field_get_test"

    def test_get_field_ndvi_not_found(self):
        """Test retrieving NDVI for non-existent field"""
        result = get_field_ndvi("nonexistent_field")
        assert result is None

    def test_get_field_ndvi_by_date(self):
        """Test retrieving NDVI for specific date"""
        process_ndvi_mock(
            field_id="field_date_test",
            source=SatelliteSource.SENTINEL_2,
            date_range=("2025-12-15", "2025-12-15"),
        )

        result = get_field_ndvi("field_date_test", date="2025-12-15")
        assert result is not None
        assert result["date"] == "2025-12-15"


class TestTimeseriesAnalysis:
    """Test timeseries analysis functions"""

    def test_get_ndvi_timeseries(self):
        """Test getting NDVI timeseries"""
        timeseries = get_ndvi_timeseries(
            "field_timeseries_test", "2025-01-01", "2025-01-31"
        )

        assert len(timeseries) > 0
        assert all(hasattr(p, "date") for p in timeseries)
        assert all(hasattr(p, "ndvi_mean") for p in timeseries)
        assert all(-1 <= p.ndvi_mean <= 1 for p in timeseries)

    def test_timeseries_date_range(self):
        """Test timeseries respects date range"""
        timeseries = get_ndvi_timeseries("field_range_test", "2025-06-01", "2025-06-30")

        for point in timeseries:
            assert "2025-06-01" <= point.date <= "2025-06-30"


class TestChangeAnalysis:
    """Test change analysis functions"""

    def test_analyze_change(self):
        """Test change analysis between two dates"""
        result = analyze_change(
            "field_change_test", "2025-01-01", "2025-06-01", include_zones=True
        )

        assert result["field_id"] == "field_change_test"
        assert result["date1"] == "2025-01-01"
        assert result["date2"] == "2025-06-01"
        assert "change" in result
        assert "mean_change" in result["change"]
        assert "percent_change" in result["change"]
        assert result["zones"] is not None

    def test_analyze_change_without_zones(self):
        """Test change analysis without zone breakdown"""
        result = analyze_change(
            "field_no_zones", "2025-01-01", "2025-06-01", include_zones=False
        )

        assert result["zones"] is None

    def test_analyze_change_metrics(self):
        """Test change analysis metrics are valid"""
        result = analyze_change(
            "field_metrics", "2025-01-01", "2025-12-01", include_zones=True
        )

        change = result["change"]
        assert "mean_change" in change
        assert "percent_increased" in change
        assert "percent_decreased" in change
        assert "percent_stable" in change

        # Percentages should sum to ~100
        total_pct = (
            change["percent_increased"]
            + change["percent_decreased"]
            + change["percent_stable"]
        )
        assert 95 <= total_pct <= 105


class TestSeasonalAnalysis:
    """Test seasonal analysis functions"""

    def test_analyze_seasonal(self):
        """Test seasonal analysis"""
        result = analyze_seasonal("field_seasonal_test", 2025)

        assert result["field_id"] == "field_seasonal_test"
        assert result["year"] == 2025
        assert len(result["seasons"]) == 4
        assert "peak_month" in result
        assert "trough_month" in result
        assert "annual_mean" in result

    def test_seasonal_stats_structure(self):
        """Test seasonal statistics structure"""
        result = analyze_seasonal("field_seasons", 2025)

        for season in result["seasons"]:
            assert "season" in season
            assert "season_ar" in season
            assert "months" in season
            assert "ndvi_mean" in season
            assert "ndvi_max" in season
            assert "ndvi_min" in season
            assert "observations_count" in season


class TestAnomalyDetection:
    """Test anomaly detection functions"""

    def test_detect_anomaly(self):
        """Test anomaly detection"""
        result = detect_anomaly("field_anomaly_test", "2025-12-27", current_ndvi=0.3)

        assert result["field_id"] == "field_anomaly_test"
        assert result["date"] == "2025-12-27"
        assert "current_ndvi" in result
        assert "historical_mean" in result
        assert "historical_std" in result
        assert "z_score" in result
        assert "is_anomaly" in result
        assert isinstance(result["is_anomaly"], bool)

    def test_detect_anomaly_auto_ndvi(self):
        """Test anomaly detection with auto-generated NDVI"""
        result = detect_anomaly("field_auto_anomaly", "2025-12-27")

        assert "current_ndvi" in result
        assert -1 <= result["current_ndvi"] <= 1

    def test_anomaly_severity(self):
        """Test anomaly severity classification"""
        # Test with extreme values to trigger anomaly
        result = detect_anomaly("field_extreme", "2025-12-27", current_ndvi=0.1)

        if result["is_anomaly"]:
            assert result["anomaly_type"] in ["positive", "negative"]
            assert result["severity"] in ["high", "medium"]


class TestCompositing:
    """Test composite creation functions"""

    def test_create_composite(self):
        """Test creating a monthly composite"""
        composite = create_composite(
            field_id="field_composite_test",
            year=2025,
            month=12,
            method=CompositeMethod.MAX_NDVI,
            source=SatelliteSource.SENTINEL_2,
        )

        assert composite["field_id"] == "field_composite_test"
        assert composite["year"] == 2025
        assert composite["month"] == 12
        assert composite["method"] == "max_ndvi"
        assert composite["source"] == "sentinel-2"
        assert "statistics" in composite
        assert "files" in composite
        assert composite["images_used"] > 0

    def test_create_composite_different_methods(self):
        """Test different compositing methods"""
        methods = [
            CompositeMethod.MAX_NDVI,
            CompositeMethod.MEAN_NDVI,
            CompositeMethod.MEDIAN_NDVI,
            CompositeMethod.MIN_CLOUD,
        ]

        for method in methods:
            composite = create_composite(
                field_id="field_method_test",
                year=2025,
                month=1,
                method=method,
                source=SatelliteSource.SENTINEL_2,
            )
            assert composite["method"] == method.value

    def test_get_composites(self):
        """Test retrieving composites for a field"""
        # Create some composites first
        create_composite(
            "field_get_comp",
            2025,
            11,
            CompositeMethod.MAX_NDVI,
            SatelliteSource.SENTINEL_2,
        )
        create_composite(
            "field_get_comp",
            2025,
            12,
            CompositeMethod.MAX_NDVI,
            SatelliteSource.SENTINEL_2,
        )

        composites = get_composites("field_get_comp")
        assert len(composites) >= 2

    def test_get_composites_by_year(self):
        """Test retrieving composites filtered by year"""
        create_composite(
            "field_year_comp",
            2025,
            1,
            CompositeMethod.MAX_NDVI,
            SatelliteSource.SENTINEL_2,
        )
        create_composite(
            "field_year_comp",
            2024,
            12,
            CompositeMethod.MAX_NDVI,
            SatelliteSource.SENTINEL_2,
        )

        composites_2025 = get_composites("field_year_comp", year=2025)
        assert all(c["year"] == 2025 for c in composites_2025)

    def test_composite_statistics(self):
        """Test composite statistics are valid"""
        composite = create_composite(
            "field_stats", 2025, 6, CompositeMethod.MAX_NDVI, SatelliteSource.SENTINEL_2
        )

        stats = composite["statistics"]
        assert -1 <= stats["mean"] <= 1
        assert stats["min"] <= stats["mean"] <= stats["max"]
        assert stats["std"] >= 0
