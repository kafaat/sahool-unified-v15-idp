"""
Comprehensive Tests for Crop Health Service
اختبارات شاملة لخدمة صحة المحاصيل
"""

import pytest

# Fixtures are loaded from conftest.py


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client):
        """Test /healthz endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "crop_health"

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "service" in response.json()
        assert "endpoints" in response.json()


class TestZoneManagement:
    """Test zone management endpoints"""

    def test_create_zone(self, client):
        """Test creating a new zone"""
        zone_data = {
            "name": "Test Zone",
            "name_ar": "منطقة اختبار",
            "area_hectares": 5.5,
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
        }

        response = client.post("/api/v1/fields/test_field/zones", json=zone_data)
        assert response.status_code == 200
        assert "zone_id" in response.json()
        assert response.json()["status"] == "created"

    def test_list_zones(self, client):
        """Test listing zones"""
        response = client.get("/api/v1/fields/field_demo/zones")
        assert response.status_code == 200
        assert "zones" in response.json()
        assert "count" in response.json()

    def test_get_zones_geojson(self, client):
        """Test getting zones as GeoJSON"""
        response = client.get("/api/v1/fields/field_demo/zones.geojson")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data


class TestObservationsIngest:
    """Test observation ingestion endpoints"""

    def test_ingest_observation_success(self, client, sample_observation_data):
        """Test successful observation ingestion"""
        response = client.post(
            "/api/v1/fields/test_field/zones/test_zone/observations",
            json=sample_observation_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stored"
        assert data["field_id"] == "test_field"
        assert data["zone_id"] == "test_zone"
        assert "observation_id" in data

    def test_ingest_observation_invalid_indices(self, client):
        """Test ingestion with invalid indices"""
        invalid_data = {
            "captured_at": "2025-12-27T10:00:00Z",
            "source": "sentinel-2",
            "growth_stage": "mid",
            "indices": {
                "ndvi": 2.0,  # Invalid: out of range
                "evi": 0.60,
                "ndre": 0.25,
                "lci": 0.30,
                "ndwi": -0.05,
                "savi": 0.65,
            },
        }

        response = client.post(
            "/api/v1/fields/test_field/zones/test_zone/observations", json=invalid_data
        )

        assert response.status_code == 422  # Validation error

    def test_list_observations(self, client, sample_observation_data):
        """Test listing observations"""
        # First, create an observation
        client.post(
            "/api/v1/fields/test_field2/zones/test_zone2/observations",
            json=sample_observation_data,
        )

        # Then list observations
        response = client.get(
            "/api/v1/fields/test_field2/zones/test_zone2/observations"
        )

        assert response.status_code == 200
        data = response.json()
        assert "observations" in data
        assert "count" in data
        assert data["count"] > 0


class TestFieldDiagnosis:
    """Test field diagnosis endpoints"""

    def test_get_field_diagnosis(self, client):
        """Test getting field diagnosis"""
        response = client.get(
            "/api/v1/fields/field_demo/diagnosis", params={"date": "2025-12-14"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "field_id" in data
        assert "summary" in data
        assert "actions" in data
        assert "map_layers" in data

    def test_diagnosis_summary_structure(self, client):
        """Test diagnosis summary structure"""
        response = client.get(
            "/api/v1/fields/field_demo/diagnosis", params={"date": "2025-12-14"}
        )

        summary = response.json()["summary"]
        assert "zones_total" in summary
        assert "zones_critical" in summary
        assert "zones_warning" in summary
        assert "zones_ok" in summary

    def test_diagnosis_invalid_date(self, client):
        """Test diagnosis with invalid date format"""
        response = client.get(
            "/api/v1/fields/field_demo/diagnosis", params={"date": "invalid-date"}
        )

        assert response.status_code == 400

    def test_diagnosis_nonexistent_field(self, client):
        """Test diagnosis for non-existent field"""
        response = client.get(
            "/api/v1/fields/nonexistent/diagnosis", params={"date": "2025-12-14"}
        )

        assert response.status_code == 404


class TestTimeline:
    """Test timeline endpoints"""

    def test_get_zone_timeline(self, client):
        """Test getting zone timeline"""
        response = client.get(
            "/api/v1/fields/field_demo/zones/zone_a/timeline",
            params={"from": "2025-12-01", "to": "2025-12-31"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "zone_id" in data
        assert "field_id" in data
        assert "series" in data

    def test_timeline_invalid_date_range(self, client):
        """Test timeline with invalid date range"""
        response = client.get(
            "/api/v1/fields/field_demo/zones/zone_a/timeline",
            params={"from": "invalid-date", "to": "2025-12-31"},
        )

        assert response.status_code == 400

    def test_timeline_empty_zone(self, client):
        """Test timeline for zone with no observations"""
        response = client.get(
            "/api/v1/fields/empty_field/zones/empty_zone/timeline",
            params={"from": "2025-12-01", "to": "2025-12-31"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["series"] == []


class TestVRTExport:
    """Test VRT export endpoints"""

    def test_export_vrt(self, client):
        """Test VRT export"""
        response = client.get(
            "/api/v1/fields/field_demo/vrt", params={"date": "2025-12-14"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert "metadata" in data

    def test_vrt_export_with_filter(self, client):
        """Test VRT export with action type filter"""
        response = client.get(
            "/api/v1/fields/field_demo/vrt",
            params={"date": "2025-12-14", "action_type": "irrigation"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "features" in data

    def test_vrt_export_metadata(self, client):
        """Test VRT export metadata structure"""
        response = client.get(
            "/api/v1/fields/field_demo/vrt", params={"date": "2025-12-14"}
        )

        metadata = response.json()["metadata"]
        assert "field_id" in metadata
        assert "date" in metadata
        assert "export_type" in metadata
        assert metadata["export_type"] == "vrt"


class TestQuickDiagnose:
    """Test quick diagnosis endpoint"""

    def test_quick_diagnose(self, client, sample_observation_data):
        """Test quick diagnosis without saving"""
        response = client.post(
            "/api/v1/diagnose",
            json=sample_observation_data,
            params={"zone_id": "temp_zone"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "zone_id" in data
        assert "status" in data
        assert "actions" in data
        assert "indices_received" in data

    def test_quick_diagnose_critical_conditions(self, client):
        """Test quick diagnosis with critical conditions"""
        critical_data = {
            "captured_at": "2025-12-27T10:00:00Z",
            "source": "drone",
            "growth_stage": "mid",
            "indices": {
                "ndvi": 0.35,  # Low NDVI
                "evi": 0.25,
                "ndre": 0.15,
                "lci": 0.12,
                "ndwi": -0.20,  # Very low water
                "savi": 0.30,
            },
        }

        response = client.post("/api/v1/diagnose", json=critical_data)

        assert response.status_code == 200
        data = response.json()
        assert "actions" in data
        # Should have urgent actions
        assert len(data["actions"]) > 0


class TestDecisionEngine:
    """Test decision engine logic"""

    def test_healthy_zone_diagnosis(self):
        """Test diagnosis of healthy zone"""
        from src.decision_engine import (
            GrowthStage,
            Indices,
            ZoneObservation,
            diagnose_zone,
        )

        indices = Indices(
            ndvi=0.80, evi=0.70, ndre=0.30, lci=0.35, ndwi=0.05, savi=0.70
        )

        obs = ZoneObservation(
            zone_id="test_zone", growth_stage=GrowthStage.mid, indices=indices
        )

        actions = diagnose_zone(obs)

        # Healthy zone should have minimal or no urgent actions
        urgent_actions = [a for a in actions if a["priority"] == "P0"]
        assert len(urgent_actions) == 0

    def test_stressed_zone_diagnosis(self):
        """Test diagnosis of stressed zone"""
        from src.decision_engine import (
            GrowthStage,
            Indices,
            ZoneObservation,
            diagnose_zone,
        )

        indices = Indices(
            ndvi=0.40,  # Low
            evi=0.30,
            ndre=0.15,
            lci=0.12,
            ndwi=-0.15,  # Water stress
            savi=0.35,
        )

        obs = ZoneObservation(
            zone_id="stressed_zone", growth_stage=GrowthStage.mid, indices=indices
        )

        actions = diagnose_zone(obs)

        # Stressed zone should have actions
        assert len(actions) > 0

    def test_zone_status_classification(self):
        """Test zone status classification"""
        from src.decision_engine import classify_zone_status

        # Critical actions
        critical_actions = [{"priority": "P0", "type": "irrigation"}]
        assert classify_zone_status(critical_actions) == "critical"

        # Warning actions
        warning_actions = [{"priority": "P1", "type": "fertilization"}]
        assert classify_zone_status(warning_actions) == "warning"

        # OK status
        ok_actions = [{"priority": "P3", "type": "scouting"}]
        assert classify_zone_status(ok_actions) == "ok"


# Integration test for complete workflow
class TestCompleteWorkflow:
    """Integration tests for complete workflow"""

    def test_complete_field_monitoring_workflow(self, client, sample_observation_data):
        """Test complete workflow from zone creation to diagnosis"""
        field_id = "integration_test_field"
        zone_id = None

        # Step 1: Create zone
        zone_response = client.post(
            f"/api/v1/fields/{field_id}/zones",
            json={
                "name": "Integration Test Zone",
                "name_ar": "منطقة اختبار التكامل",
                "area_hectares": 10.0,
            },
        )
        assert zone_response.status_code == 200
        zone_id = zone_response.json()["zone_id"]

        # Step 2: Ingest observation
        obs_response = client.post(
            f"/api/v1/fields/{field_id}/zones/{zone_id}/observations",
            json=sample_observation_data,
        )
        assert obs_response.status_code == 200

        # Step 3: Get diagnosis
        diagnosis_response = client.get(
            f"/api/v1/fields/{field_id}/diagnosis", params={"date": "2025-12-27"}
        )
        assert diagnosis_response.status_code == 200

        # Step 4: Get timeline
        timeline_response = client.get(
            f"/api/v1/fields/{field_id}/zones/{zone_id}/timeline",
            params={"from": "2025-12-01", "to": "2025-12-31"},
        )
        assert timeline_response.status_code == 200

        # Step 5: Export VRT
        vrt_response = client.get(
            f"/api/v1/fields/{field_id}/vrt", params={"date": "2025-12-27"}
        )
        assert vrt_response.status_code == 200
