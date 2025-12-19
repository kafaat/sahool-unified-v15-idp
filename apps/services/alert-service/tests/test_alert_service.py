"""
Alert Service Tests
اختبارات خدمة التنبيهات
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4


class TestAlertCreation:
    """Test suite for alert creation."""

    def test_create_alert_with_required_fields(self):
        """Test creating alert with required fields."""
        alert = self._create_alert(
            type="ndvi_low",
            severity="warning",
            field_id="field-123",
            message="NDVI dropped below threshold"
        )

        assert alert["id"] is not None
        assert alert["type"] == "ndvi_low"
        assert alert["severity"] == "warning"
        assert alert["field_id"] == "field-123"
        assert alert["status"] == "active"

    def test_create_alert_with_metadata(self):
        """Test creating alert with additional metadata."""
        metadata = {
            "current_ndvi": 0.15,
            "threshold": 0.25,
            "zone": "Zone A"
        }

        alert = self._create_alert(
            type="ndvi_low",
            severity="warning",
            field_id="field-123",
            message="Low NDVI detected",
            metadata=metadata
        )

        assert alert["metadata"] == metadata
        assert alert["metadata"]["current_ndvi"] == 0.15

    def test_alert_has_timestamp(self):
        """Test alert has creation timestamp."""
        alert = self._create_alert(
            type="weather_alert",
            severity="info",
            field_id="field-456",
            message="Rain expected"
        )

        assert "created_at" in alert
        assert isinstance(alert["created_at"], datetime)

    @pytest.mark.parametrize("severity,is_valid", [
        ("info", True),
        ("warning", True),
        ("critical", True),
        ("invalid", False),
    ])
    def test_validate_severity(self, severity: str, is_valid: bool):
        """Test severity validation."""
        if is_valid:
            alert = self._create_alert(
                type="test",
                severity=severity,
                field_id="field-1",
                message="Test"
            )
            assert alert["severity"] == severity
        else:
            with pytest.raises(ValueError):
                self._create_alert(
                    type="test",
                    severity=severity,
                    field_id="field-1",
                    message="Test"
                )

    @staticmethod
    def _create_alert(
        type: str,
        severity: str,
        field_id: str,
        message: str,
        metadata: dict = None
    ) -> dict:
        """Create a new alert."""
        valid_severities = ["info", "warning", "critical"]
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity: {severity}")

        return {
            "id": str(uuid4()),
            "type": type,
            "severity": severity,
            "field_id": field_id,
            "message": message,
            "metadata": metadata or {},
            "status": "active",
            "created_at": datetime.utcnow(),
        }


class TestAlertFiltering:
    """Test suite for alert filtering."""

    @pytest.fixture
    def sample_alerts(self):
        """Create sample alerts for testing."""
        return [
            {
                "id": "1",
                "type": "ndvi_low",
                "severity": "critical",
                "field_id": "field-1",
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(hours=1),
            },
            {
                "id": "2",
                "type": "weather",
                "severity": "warning",
                "field_id": "field-1",
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(hours=2),
            },
            {
                "id": "3",
                "type": "ndvi_low",
                "severity": "warning",
                "field_id": "field-2",
                "status": "dismissed",
                "created_at": datetime.utcnow() - timedelta(days=1),
            },
            {
                "id": "4",
                "type": "irrigation",
                "severity": "info",
                "field_id": "field-2",
                "status": "active",
                "created_at": datetime.utcnow(),
            },
        ]

    def test_filter_by_severity(self, sample_alerts):
        """Test filtering alerts by severity."""
        result = self._filter_alerts(sample_alerts, severity="critical")

        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_by_field(self, sample_alerts):
        """Test filtering alerts by field ID."""
        result = self._filter_alerts(sample_alerts, field_id="field-1")

        assert len(result) == 2
        assert all(a["field_id"] == "field-1" for a in result)

    def test_filter_by_status(self, sample_alerts):
        """Test filtering alerts by status."""
        result = self._filter_alerts(sample_alerts, status="active")

        assert len(result) == 3
        assert all(a["status"] == "active" for a in result)

    def test_filter_by_type(self, sample_alerts):
        """Test filtering alerts by type."""
        result = self._filter_alerts(sample_alerts, type="ndvi_low")

        assert len(result) == 2
        assert all(a["type"] == "ndvi_low" for a in result)

    def test_filter_multiple_criteria(self, sample_alerts):
        """Test filtering with multiple criteria."""
        result = self._filter_alerts(
            sample_alerts,
            field_id="field-1",
            status="active"
        )

        assert len(result) == 2

    @staticmethod
    def _filter_alerts(
        alerts: list,
        severity: str = None,
        field_id: str = None,
        status: str = None,
        type: str = None
    ) -> list:
        """Filter alerts based on criteria."""
        result = alerts

        if severity:
            result = [a for a in result if a["severity"] == severity]
        if field_id:
            result = [a for a in result if a["field_id"] == field_id]
        if status:
            result = [a for a in result if a["status"] == status]
        if type:
            result = [a for a in result if a["type"] == type]

        return result


class TestAlertActions:
    """Test suite for alert actions (dismiss, acknowledge, etc.)."""

    def test_dismiss_alert(self):
        """Test dismissing an alert."""
        alert = {
            "id": "1",
            "status": "active",
            "dismissed_at": None,
            "dismissed_by": None,
        }

        result = self._dismiss_alert(alert, user_id="user-123")

        assert result["status"] == "dismissed"
        assert result["dismissed_by"] == "user-123"
        assert result["dismissed_at"] is not None

    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        alert = {
            "id": "1",
            "status": "active",
            "acknowledged_at": None,
            "acknowledged_by": None,
        }

        result = self._acknowledge_alert(alert, user_id="user-456")

        assert result["status"] == "acknowledged"
        assert result["acknowledged_by"] == "user-456"

    def test_cannot_dismiss_already_dismissed(self):
        """Test cannot dismiss already dismissed alert."""
        alert = {
            "id": "1",
            "status": "dismissed",
        }

        with pytest.raises(ValueError, match="already dismissed"):
            self._dismiss_alert(alert, user_id="user-123")

    def test_resolve_alert(self):
        """Test resolving an alert."""
        alert = {
            "id": "1",
            "status": "active",
            "resolved_at": None,
            "resolution_note": None,
        }

        result = self._resolve_alert(
            alert,
            user_id="user-789",
            note="Issue fixed by irrigation"
        )

        assert result["status"] == "resolved"
        assert result["resolution_note"] == "Issue fixed by irrigation"

    @staticmethod
    def _dismiss_alert(alert: dict, user_id: str) -> dict:
        """Dismiss an alert."""
        if alert["status"] == "dismissed":
            raise ValueError("Alert is already dismissed")

        return {
            **alert,
            "status": "dismissed",
            "dismissed_by": user_id,
            "dismissed_at": datetime.utcnow(),
        }

    @staticmethod
    def _acknowledge_alert(alert: dict, user_id: str) -> dict:
        """Acknowledge an alert."""
        return {
            **alert,
            "status": "acknowledged",
            "acknowledged_by": user_id,
            "acknowledged_at": datetime.utcnow(),
        }

    @staticmethod
    def _resolve_alert(alert: dict, user_id: str, note: str = None) -> dict:
        """Resolve an alert."""
        return {
            **alert,
            "status": "resolved",
            "resolved_by": user_id,
            "resolved_at": datetime.utcnow(),
            "resolution_note": note,
        }


class TestAlertNotifications:
    """Test suite for alert notifications."""

    def test_should_notify_for_critical_alert(self):
        """Test that critical alerts trigger notifications."""
        alert = {"severity": "critical", "type": "ndvi_low"}

        should_notify = self._should_send_notification(alert)

        assert should_notify is True

    def test_should_notify_for_warning_based_on_config(self):
        """Test warning notifications based on config."""
        alert = {"severity": "warning", "type": "ndvi_low"}
        config = {"notify_on_warning": True}

        should_notify = self._should_send_notification(alert, config)

        assert should_notify is True

    def test_should_not_notify_for_info_by_default(self):
        """Test info alerts don't trigger notifications by default."""
        alert = {"severity": "info", "type": "weather"}

        should_notify = self._should_send_notification(alert)

        assert should_notify is False

    @staticmethod
    def _should_send_notification(alert: dict, config: dict = None) -> bool:
        """Determine if notification should be sent."""
        config = config or {}

        if alert["severity"] == "critical":
            return True
        if alert["severity"] == "warning" and config.get("notify_on_warning", False):
            return True
        if alert["severity"] == "info" and config.get("notify_on_info", False):
            return True

        return False
