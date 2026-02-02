"""
Tests for Scout Reports API.
اختبارات واجهة برمجة تقارير المسح الحقلي.
"""

import pytest


class TestScoutReportsAPI:
    """Test cases for scout report endpoints."""

    def test_create_report(self, client, sample_scout_report):
        """Test creating a new scout report."""
        response = client.post("/api/v1/scouts/reports", json=sample_scout_report)
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == sample_scout_report["field_id"]
        assert data["crop"] == sample_scout_report["crop"]
        assert data["status"] == "draft"
        assert "id" in data
        assert "created_at" in data

    def test_list_reports(self, client, sample_scout_report):
        """Test listing scout reports."""
        # Create a report first
        client.post("/api/v1/scouts/reports", json=sample_scout_report)

        response = client.get("/api/v1/scouts/reports")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "reports" in data
        assert isinstance(data["reports"], list)

    def test_list_reports_filter_by_field(self, client, sample_scout_report):
        """Test filtering reports by field ID."""
        # Create a report
        client.post("/api/v1/scouts/reports", json=sample_scout_report)

        response = client.get(f"/api/v1/scouts/reports?field_id={sample_scout_report['field_id']}")
        assert response.status_code == 200
        data = response.json()
        for report in data["reports"]:
            assert report["field_id"] == sample_scout_report["field_id"]

    def test_list_reports_filter_by_status(self, client, sample_scout_report):
        """Test filtering reports by status."""
        response = client.get("/api/v1/scouts/reports?status=draft")
        assert response.status_code == 200

    def test_get_report_by_id(self, client, sample_scout_report):
        """Test getting specific report by ID."""
        # Create a report
        create_response = client.post("/api/v1/scouts/reports", json=sample_scout_report)
        report_id = create_response.json()["id"]

        # Get the report
        response = client.get(f"/api/v1/scouts/reports/{report_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report_id

    def test_get_report_not_found(self, client):
        """Test getting non-existent report."""
        response = client.get("/api/v1/scouts/reports/nonexistent-id")
        assert response.status_code == 404

    def test_update_report(self, client, sample_scout_report):
        """Test updating a scout report."""
        # Create a report
        create_response = client.post("/api/v1/scouts/reports", json=sample_scout_report)
        report_id = create_response.json()["id"]

        # Update the report
        updated_data = sample_scout_report.copy()
        updated_data["general_notes"] = "Updated notes"
        response = client.put(f"/api/v1/scouts/reports/{report_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["general_notes"] == "Updated notes"

    def test_delete_report(self, client, sample_scout_report):
        """Test deleting a scout report."""
        # Create a report
        create_response = client.post("/api/v1/scouts/reports", json=sample_scout_report)
        report_id = create_response.json()["id"]

        # Delete the report
        response = client.delete(f"/api/v1/scouts/reports/{report_id}")
        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f"/api/v1/scouts/reports/{report_id}")
        assert get_response.status_code == 404

    def test_get_reports_by_field(self, client, sample_scout_report):
        """Test getting all reports for a field."""
        # Create multiple reports for same field
        client.post("/api/v1/scouts/reports", json=sample_scout_report)
        client.post("/api/v1/scouts/reports", json=sample_scout_report)

        response = client.get(f"/api/v1/scouts/reports/field/{sample_scout_report['field_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == sample_scout_report["field_id"]
        assert data["total"] >= 2


class TestObservationsAPI:
    """Test cases for observation endpoints."""

    def test_add_observation_to_report(self, client, sample_scout_report, sample_observation):
        """Test adding observation to a report."""
        # Create a report
        create_response = client.post("/api/v1/scouts/reports", json=sample_scout_report)
        report_id = create_response.json()["id"]

        # Add observation
        response = client.post(
            f"/api/v1/scouts/reports/{report_id}/observations",
            json=sample_observation,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pest_id"] == sample_observation["pest_id"]
        assert data["infestation_level"] == sample_observation["infestation_level"]
        assert "id" in data

    def test_add_observation_to_nonexistent_report(self, client, sample_observation):
        """Test adding observation to non-existent report."""
        response = client.post(
            "/api/v1/scouts/reports/nonexistent/observations",
            json=sample_observation,
        )
        assert response.status_code == 404

    def test_observation_with_location(self, client, sample_scout_report, sample_observation):
        """Test adding observation with GPS location."""
        # Create a report
        create_response = client.post("/api/v1/scouts/reports", json=sample_scout_report)
        report_id = create_response.json()["id"]

        # Add observation with location
        obs_with_location = sample_observation.copy()
        obs_with_location["location"] = {
            "latitude": 24.7136,
            "longitude": 46.6753,
            "accuracy_m": 5.0,
        }

        response = client.post(
            f"/api/v1/scouts/reports/{report_id}/observations",
            json=obs_with_location,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["location"]["latitude"] == 24.7136


class TestReportWorkflow:
    """Test report submission workflow."""

    def test_submit_report(self, client, sample_scout_report, sample_observation):
        """Test submitting a report for review."""
        # Create a report
        create_response = client.post("/api/v1/scouts/reports", json=sample_scout_report)
        report_id = create_response.json()["id"]

        # Add observation (required for submission)
        client.post(
            f"/api/v1/scouts/reports/{report_id}/observations",
            json=sample_observation,
        )

        # Submit report
        response = client.post(f"/api/v1/scouts/reports/{report_id}/submit")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "submitted"

    def test_submit_empty_report_fails(self, client, sample_scout_report):
        """Test that submitting report without observations fails."""
        # Create a report without observations
        create_response = client.post("/api/v1/scouts/reports", json=sample_scout_report)
        report_id = create_response.json()["id"]

        # Try to submit
        response = client.post(f"/api/v1/scouts/reports/{report_id}/submit")
        assert response.status_code == 400


class TestScoutStatistics:
    """Test scouting statistics endpoint."""

    def test_get_statistics(self, client):
        """Test getting scouting statistics."""
        response = client.get("/api/v1/scouts/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "period_days" in data
        assert "total_reports" in data
        assert "total_observations" in data
        assert "top_pests" in data
        assert "reports_by_status" in data

    def test_get_statistics_with_field_filter(self, client):
        """Test statistics filtered by field."""
        response = client.get("/api/v1/scouts/statistics?field_id=FIELD-001")
        assert response.status_code == 200

    def test_get_statistics_custom_period(self, client):
        """Test statistics with custom period."""
        response = client.get("/api/v1/scouts/statistics?days=90")
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 90
