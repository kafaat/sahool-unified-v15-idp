"""
Tests for Thresholds & Alerts API.
اختبارات واجهة برمجة العتبات والتنبيهات.
"""

import pytest


class TestThresholdsAPI:
    """Test cases for threshold endpoints."""

    def test_list_thresholds(self, client):
        """Test listing all thresholds."""
        response = client.get("/api/v1/thresholds")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5  # We have multiple thresholds

    def test_list_thresholds_by_crop(self, client):
        """Test filtering thresholds by crop."""
        response = client.get("/api/v1/thresholds?crop=tomato")
        assert response.status_code == 200
        data = response.json()
        for threshold in data:
            assert threshold["crop"].lower() == "tomato"

    def test_list_thresholds_by_pest(self, client):
        """Test filtering thresholds by pest."""
        response = client.get("/api/v1/thresholds?pest_id=aphids")
        assert response.status_code == 200
        data = response.json()
        for threshold in data:
            assert threshold["pest_id"] == "aphids"

    def test_get_threshold_by_crop_pest(self, client):
        """Test getting specific threshold."""
        response = client.get("/api/v1/thresholds/crop/wheat/pest/aphids")
        assert response.status_code == 200
        data = response.json()
        assert data["pest_id"] == "aphids"
        assert data["crop"] == "wheat"
        assert "threshold_value" in data
        assert "action_threshold" in data
        assert "economic_injury_level" in data

    def test_get_threshold_not_found(self, client):
        """Test getting non-existent threshold."""
        response = client.get("/api/v1/thresholds/crop/banana/pest/unknown")
        assert response.status_code == 404

    def test_rpw_threshold_zero_tolerance(self, client):
        """Test Red Palm Weevil has zero tolerance threshold."""
        response = client.get("/api/v1/thresholds/crop/date_palm/pest/rpw")
        assert response.status_code == 200
        data = response.json()
        assert data["threshold_value"] == 1
        assert data["action_threshold"] == 1
        assert "zero tolerance" in data.get("notes_en", "").lower() or data["threshold_value"] == 1


class TestThresholdAssessment:
    """Test threshold assessment endpoint."""

    def test_assess_below_threshold(self, client):
        """Test assessment when value is below threshold."""
        response = client.post(
            "/api/v1/thresholds/assess",
            json={
                "pest_id": "aphids",
                "crop": "wheat",
                "current_value": 5.0,  # Below action threshold (15)
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "below"
        assert data["urgency"] == "low"

    def test_assess_approaching_threshold(self, client):
        """Test assessment when value is approaching threshold."""
        response = client.post(
            "/api/v1/thresholds/assess",
            json={
                "pest_id": "aphids",
                "crop": "wheat",
                "current_value": 12.0,  # Approaching action threshold (15)
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approaching"
        assert data["urgency"] == "medium"

    def test_assess_at_threshold(self, client):
        """Test assessment when value is at action threshold."""
        response = client.post(
            "/api/v1/thresholds/assess",
            json={
                "pest_id": "aphids",
                "crop": "wheat",
                "current_value": 20.0,  # At/above action threshold
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["at_threshold", "exceeded"]
        assert data["urgency"] in ["high", "critical"]

    def test_assess_exceeded_threshold(self, client):
        """Test assessment when value exceeds economic threshold."""
        response = client.post(
            "/api/v1/thresholds/assess",
            json={
                "pest_id": "aphids",
                "crop": "wheat",
                "current_value": 40.0,  # Above economic injury level (30)
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "exceeded"
        assert data["urgency"] == "critical"
        assert data["yield_loss_estimate_percent"] is not None

    def test_assess_returns_bilingual_content(self, client):
        """Test assessment returns Arabic content."""
        response = client.post(
            "/api/v1/thresholds/assess",
            json={
                "pest_id": "aphids",
                "crop": "wheat",
                "current_value": 25.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "status_ar" in data
        assert "recommendation_ar" in data

    def test_assess_unknown_pest_crop(self, client):
        """Test assessment for unknown pest-crop combination."""
        response = client.post(
            "/api/v1/thresholds/assess",
            json={
                "pest_id": "unknown_pest",
                "crop": "unknown_crop",
                "current_value": 10.0,
            },
        )
        assert response.status_code == 404


class TestAlertsAPI:
    """Test cases for alert endpoints."""

    def test_list_alerts(self, client):
        """Test listing alerts."""
        response = client.get("/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "alerts" in data

    def test_list_alerts_filter_by_priority(self, client):
        """Test filtering alerts by priority."""
        response = client.get("/api/v1/alerts?priority=critical")
        assert response.status_code == 200

    def test_list_alerts_filter_by_status(self, client):
        """Test filtering alerts by status."""
        response = client.get("/api/v1/alerts?status=active")
        assert response.status_code == 200

    def test_create_alert(self, client):
        """Test creating a manual alert."""
        response = client.post(
            "/api/v1/alerts/create",
            params={
                "field_id": "FIELD-001",
                "pest_id": "rpw",
                "priority": "critical",
                "message_en": "Red Palm Weevil detected",
                "message_ar": "تم اكتشاف سوسة النخيل الحمراء",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "FIELD-001"
        assert data["pest_id"] == "rpw"
        assert data["priority"] == "critical"
        assert data["status"] == "active"

    def test_get_alert_by_id(self, client):
        """Test getting alert by ID."""
        # Create an alert first
        create_response = client.post(
            "/api/v1/alerts/create",
            params={
                "field_id": "FIELD-002",
                "pest_id": "aphids",
                "priority": "medium",
                "message_en": "Aphid infestation",
                "message_ar": "إصابة بالمن",
            },
        )
        alert_id = create_response.json()["id"]

        # Get the alert
        response = client.get(f"/api/v1/alerts/{alert_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == alert_id

    def test_acknowledge_alert(self, client):
        """Test acknowledging an alert."""
        # Create an alert first
        create_response = client.post(
            "/api/v1/alerts/create",
            params={
                "field_id": "FIELD-003",
                "pest_id": "whitefly",
                "priority": "high",
                "message_en": "Whitefly detected",
                "message_ar": "تم اكتشاف الذبابة البيضاء",
            },
        )
        alert_id = create_response.json()["id"]

        # Acknowledge the alert
        response = client.post(
            f"/api/v1/alerts/{alert_id}/acknowledge",
            params={"acknowledged_by": "test_user"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["alert"]["status"] == "acknowledged"
        assert data["alert"]["acknowledged_by"] == "test_user"

    def test_resolve_alert(self, client):
        """Test resolving an alert."""
        # Create an alert first
        create_response = client.post(
            "/api/v1/alerts/create",
            params={
                "field_id": "FIELD-004",
                "pest_id": "thrips",
                "priority": "low",
                "message_en": "Thrips observed",
                "message_ar": "لوحظ التربس",
            },
        )
        alert_id = create_response.json()["id"]

        # Resolve the alert
        response = client.post(f"/api/v1/alerts/{alert_id}/resolve")
        assert response.status_code == 200
        data = response.json()
        assert data["alert"]["status"] == "resolved"


class TestThresholdDataIntegrity:
    """Test threshold database integrity."""

    def test_all_thresholds_have_required_fields(self, client):
        """Test all thresholds have required fields."""
        response = client.get("/api/v1/thresholds")
        data = response.json()

        required_fields = [
            "id", "pest_id", "pest_name_en", "pest_name_ar",
            "crop", "threshold_value", "threshold_unit",
            "action_threshold", "economic_injury_level",
            "sampling_method_en", "sampling_method_ar",
        ]

        for threshold in data:
            for field in required_fields:
                assert field in threshold, f"Missing field {field} in threshold {threshold.get('id')}"

    def test_all_thresholds_have_bilingual_content(self, client):
        """Test all thresholds have Arabic content."""
        response = client.get("/api/v1/thresholds")
        data = response.json()

        for threshold in data:
            assert threshold["pest_name_ar"], f"Missing Arabic pest name for {threshold['id']}"
            assert threshold["sampling_method_ar"], f"Missing Arabic sampling method for {threshold['id']}"
            assert threshold["threshold_unit_ar"], f"Missing Arabic unit for {threshold['id']}"
