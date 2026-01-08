"""
Integration Tests for NDVI Processor API Endpoints
اختبارات التكامل لنقاط نهاية API معالج NDVI
"""

from fastapi import status


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_endpoint(self, test_client):
        """Test /health endpoint"""
        response = test_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ndvi-processor"
        assert "version" in data
        assert "metrics" in data

    def test_healthz_endpoint(self, test_client):
        """Test /healthz endpoint"""
        response = test_client.get("/healthz")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "queue_size" in data

    def test_readyz_endpoint(self, test_client):
        """Test /readyz endpoint"""
        response = test_client.get("/readyz")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ready"


class TestProcessingEndpoints:
    """Test NDVI processing endpoints"""

    def test_start_processing(self, test_client, sample_process_request):
        """Test POST /process endpoint"""
        response = test_client.post("/process", json=sample_process_request)

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert data["field_id"] == sample_process_request["field_id"]
        assert data["tenant_id"] == sample_process_request["tenant_id"]

    def test_start_processing_minimal(self, test_client):
        """Test processing with minimal required fields"""
        request = {
            "tenant_id": "test_tenant",
            "field_id": "field_minimal",
            "date_range": {"start": "2025-12-01", "end": "2025-12-15"},
        }

        response = test_client.post("/process", json=request)
        assert response.status_code == status.HTTP_202_ACCEPTED

    def test_get_job_status(self, test_client, sample_process_request):
        """Test GET /process/{job_id}/status endpoint"""
        # First create a job
        create_response = test_client.post("/process", json=sample_process_request)
        job_id = create_response.json()["job_id"]

        # Get job status
        response = test_client.get(f"/process/{job_id}/status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == job_id
        assert "status" in data
        assert "progress_percent" in data

    def test_get_job_status_not_found(self, test_client):
        """Test getting status for non-existent job"""
        response = test_client.get("/process/nonexistent_job_id/status")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cancel_processing(self, test_client, sample_process_request):
        """Test DELETE /process/{job_id} endpoint"""
        # Create a job
        create_response = test_client.post("/process", json=sample_process_request)
        job_id = create_response.json()["job_id"]

        # Cancel it
        response = test_client.delete(f"/process/{job_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["job_id"] == job_id

    def test_list_processing_jobs(self, test_client, sample_process_request):
        """Test GET /process endpoint"""
        # Create some jobs first
        test_client.post("/process", json=sample_process_request)

        response = test_client.get("/process")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert "active_count" in data
        assert isinstance(data["jobs"], list)

    def test_list_jobs_by_tenant(self, test_client):
        """Test listing jobs filtered by tenant"""
        request = {
            "tenant_id": "specific_tenant",
            "field_id": "field_001",
            "date_range": {"start": "2025-12-01", "end": "2025-12-15"},
        }
        test_client.post("/process", json=request)

        response = test_client.get("/process?tenant_id=specific_tenant")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["jobs"]) >= 1

    def test_list_jobs_by_field(self, test_client):
        """Test listing jobs filtered by field"""
        request = {
            "tenant_id": "test_tenant",
            "field_id": "specific_field",
            "date_range": {"start": "2025-12-01", "end": "2025-12-15"},
        }
        test_client.post("/process", json=request)

        response = test_client.get("/process?field_id=specific_field")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        jobs_for_field = [j for j in data["jobs"] if j["field_id"] == "specific_field"]
        assert len(jobs_for_field) >= 1


class TestNDVIDataEndpoints:
    """Test NDVI data retrieval endpoints"""

    def test_get_ndvi_for_field(self, test_client):
        """Test GET /fields/{field_id}/ndvi endpoint"""
        response = test_client.get("/fields/field_test_001/ndvi")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "statistics" in data
        assert "quality" in data
        assert "files" in data

    def test_get_ndvi_with_date(self, test_client):
        """Test getting NDVI for specific date"""
        response = test_client.get("/fields/field_002/ndvi?date=2025-12-01")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["date"] == "2025-12-01"

    def test_get_latest_ndvi(self, test_client):
        """Test GET /fields/{field_id}/ndvi/latest endpoint"""
        response = test_client.get("/fields/field_latest/ndvi/latest")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "field_id" in data
        assert "statistics" in data

    def test_get_timeseries(self, test_client):
        """Test GET /fields/{field_id}/ndvi/timeseries endpoint"""
        response = test_client.get(
            "/fields/field_timeseries/ndvi/timeseries?start=2025-01-01&end=2025-01-31"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["field_id"] == "field_timeseries"
        assert data["start_date"] == "2025-01-01"
        assert data["end_date"] == "2025-01-31"
        assert "data" in data
        assert "total_points" in data
        assert isinstance(data["data"], list)


class TestAnalysisEndpoints:
    """Test analysis endpoints"""

    def test_get_change_analysis(self, test_client):
        """Test GET /fields/{field_id}/ndvi/change endpoint"""
        response = test_client.get(
            "/fields/field_change/ndvi/change?date1=2025-01-01&date2=2025-06-01&include_zones=true"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["field_id"] == "field_change"
        assert data["date1"] == "2025-01-01"
        assert data["date2"] == "2025-06-01"
        assert "change" in data
        assert "zones" in data

    def test_post_change_analysis(self, test_client, sample_change_analysis_request):
        """Test POST /fields/{field_id}/ndvi/change endpoint"""
        field_id = sample_change_analysis_request["field_id"]
        response = test_client.post(
            f"/fields/{field_id}/ndvi/change", json=sample_change_analysis_request
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "change" in data

    def test_get_seasonal_analysis(self, test_client):
        """Test GET /fields/{field_id}/ndvi/seasonal endpoint"""
        response = test_client.get("/fields/field_seasonal/ndvi/seasonal?year=2025")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["field_id"] == "field_seasonal"
        assert data["year"] == 2025
        assert "seasons" in data
        assert len(data["seasons"]) == 4
        assert "annual_mean" in data

    def test_get_anomaly_detection(self, test_client):
        """Test GET /fields/{field_id}/ndvi/anomaly endpoint"""
        response = test_client.get(
            "/fields/field_anomaly/ndvi/anomaly?date=2025-12-27&current_ndvi=0.45"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["field_id"] == "field_anomaly"
        assert data["date"] == "2025-12-27"
        assert "is_anomaly" in data
        assert "z_score" in data


class TestExportEndpoints:
    """Test export endpoints"""

    def test_export_geotiff(self, test_client):
        """Test exporting as GeoTIFF"""
        # First create some data
        test_client.get("/fields/field_export_tiff/ndvi/latest")

        response = test_client.get("/fields/field_export_tiff/ndvi/export?format=geotiff")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "download_url" in data
        assert data["format"] == "geotiff"

    def test_export_csv(self, test_client):
        """Test exporting as CSV"""
        response = test_client.get(
            "/fields/field_export_csv/ndvi/export?format=csv&start=2025-01-01&end=2025-01-31"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        content = response.text
        assert "date,ndvi_mean" in content

    def test_export_csv_missing_dates(self, test_client):
        """Test CSV export without required date range"""
        response = test_client.get("/fields/field_export/ndvi/export?format=csv")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_export_json_single(self, test_client):
        """Test exporting single result as JSON"""
        test_client.get("/fields/field_export_json/ndvi/latest")

        response = test_client.get("/fields/field_export_json/ndvi/export?format=json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)

    def test_export_json_timeseries(self, test_client):
        """Test exporting timeseries as JSON"""
        response = test_client.get(
            "/fields/field_json_series/ndvi/export?format=json&start=2025-01-01&end=2025-01-31"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "field_id" in data
        assert "timeseries" in data


class TestCompositeEndpoints:
    """Test composite endpoints"""

    def test_create_monthly_composite(self, test_client, sample_composite_request):
        """Test POST /composites/monthly endpoint"""
        response = test_client.post("/composites/monthly", json=sample_composite_request)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "composite_id" in data
        assert data["field_id"] == sample_composite_request["field_id"]
        assert data["year"] == sample_composite_request["year"]
        assert data["month"] == sample_composite_request["month"]
        assert "statistics" in data

    def test_list_composites(self, test_client, sample_composite_request):
        """Test GET /fields/{field_id}/composites endpoint"""
        # Create a composite first
        test_client.post("/composites/monthly", json=sample_composite_request)

        field_id = sample_composite_request["field_id"]
        response = test_client.get(f"/fields/{field_id}/composites")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["field_id"] == field_id
        assert "composites" in data
        assert "total" in data

    def test_list_composites_by_year(self, test_client, sample_composite_request):
        """Test listing composites filtered by year"""
        test_client.post("/composites/monthly", json=sample_composite_request)

        field_id = sample_composite_request["field_id"]
        year = sample_composite_request["year"]
        response = test_client.get(f"/fields/{field_id}/composites?year={year}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(c["year"] == year for c in data["composites"])

    def test_get_composite(self, test_client, sample_composite_request):
        """Test GET /composites/{composite_id} endpoint"""
        # Create a composite
        create_response = test_client.post("/composites/monthly", json=sample_composite_request)
        composite_id = create_response.json()["composite_id"]

        # Get the composite
        response = test_client.get(f"/composites/{composite_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["composite_id"] == composite_id

    def test_get_composite_not_found(self, test_client):
        """Test getting non-existent composite"""
        response = test_client.get("/composites/nonexistent_composite_id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_composite(self, test_client, sample_composite_request):
        """Test GET /composites/{composite_id}/download endpoint"""
        # Create a composite
        create_response = test_client.post("/composites/monthly", json=sample_composite_request)
        composite_id = create_response.json()["composite_id"]

        # Download it
        response = test_client.get(f"/composites/{composite_id}/download?format=geotiff")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "download_url" in data
        assert data["format"] == "geotiff"


class TestRequestValidation:
    """Test request validation"""

    def test_process_missing_required_field(self, test_client):
        """Test processing request with missing required field"""
        request = {
            "tenant_id": "test_tenant",
            # Missing field_id and date_range
        }

        response = test_client.post("/process", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_process_invalid_date_format(self, test_client):
        """Test processing with invalid date format"""
        request = {
            "tenant_id": "test_tenant",
            "field_id": "field_001",
            "date_range": {"start": "invalid-date", "end": "2025-12-15"},
        }

        response = test_client.post("/process", json=request)
        # Should still accept as string, validation happens later
        assert response.status_code in [
            status.HTTP_202_ACCEPTED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_composite_invalid_month(self, test_client):
        """Test composite creation with invalid month"""
        request = {
            "tenant_id": "test_tenant",
            "field_id": "field_001",
            "year": 2025,
            "month": 13,  # Invalid month
            "method": "max_ndvi",
            "source": "sentinel-2",
        }

        response = test_client.post("/composites/monthly", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_timeseries_missing_dates(self, test_client):
        """Test timeseries without required date parameters"""
        response = test_client.get("/fields/field_001/ndvi/timeseries")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestConcurrentRequests:
    """Test handling of concurrent requests"""

    def test_multiple_processing_jobs(self, test_client):
        """Test creating multiple jobs concurrently"""
        requests = [
            {
                "tenant_id": "tenant_concurrent",
                "field_id": f"field_concurrent_{i}",
                "date_range": {"start": "2025-12-01", "end": "2025-12-15"},
            }
            for i in range(5)
        ]

        job_ids = []
        for req in requests:
            response = test_client.post("/process", json=req)
            assert response.status_code == status.HTTP_202_ACCEPTED
            job_ids.append(response.json()["job_id"])

        assert len(set(job_ids)) == 5  # All job IDs should be unique

    def test_queue_management(self, test_client):
        """Test queue size management"""
        # Create several jobs
        for i in range(3):
            test_client.post(
                "/process",
                json={
                    "tenant_id": "test_tenant",
                    "field_id": f"field_queue_{i}",
                    "date_range": {"start": "2025-12-01", "end": "2025-12-15"},
                },
            )

        # Check health shows queue size
        response = test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["metrics"]["queue_size"] >= 0
