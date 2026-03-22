"""
SAHOOL Alert Service - Comprehensive DB Model Tests
Tests for Alert and AlertRule SQLAlchemy ORM models, to_dict(), __repr__(), and edge cases.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

try:
    import sqlalchemy  # noqa: F401
except ImportError:
    pytest.skip("sqlalchemy not installed", allow_module_level=True)

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4


# ═══════════════════════════════════════════════════════════════════════════════
# Alert Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertModel:
    """Tests for Alert SQLAlchemy model."""

    def _make_alert(self, **overrides):
        from src.db_models import Alert

        defaults = dict(
            id=uuid4(),
            field_id="field-001",
            tenant_id=uuid4(),
            type="weather",
            severity="high",
            status="active",
            title="Test Alert",
            title_en="Test Alert EN",
            message="Alert message",
            message_en="Alert message EN",
            recommendations=["rec1"],
            recommendations_en=["rec1-en"],
            extra_metadata={"key": "value"},
            source_service="weather-service",
            correlation_id="corr-123",
            created_at=datetime.now(UTC),
            expires_at=None,
            acknowledged_at=None,
            acknowledged_by=None,
            dismissed_at=None,
            dismissed_by=None,
            resolved_at=None,
            resolved_by=None,
            resolution_note=None,
        )
        defaults.update(overrides)
        alert = Alert(**defaults)
        return alert

    def test_to_dict_basic(self):
        alert = self._make_alert()
        d = alert.to_dict()

        assert d["id"] == str(alert.id)
        assert d["field_id"] == "field-001"
        assert d["type"] == "weather"
        assert d["severity"] == "high"
        assert d["status"] == "active"
        assert d["title"] == "Test Alert"
        assert d["title_en"] == "Test Alert EN"
        assert d["message"] == "Alert message"
        assert d["message_en"] == "Alert message EN"
        assert d["recommendations"] == ["rec1"]
        assert d["recommendations_en"] == ["rec1-en"]
        assert d["metadata"] == {"key": "value"}
        assert d["source_service"] == "weather-service"
        assert d["correlation_id"] == "corr-123"

    def test_to_dict_none_tenant(self):
        alert = self._make_alert(tenant_id=None)
        d = alert.to_dict()
        assert d["tenant_id"] is None

    def test_to_dict_with_tenant(self):
        tid = uuid4()
        alert = self._make_alert(tenant_id=tid)
        d = alert.to_dict()
        assert d["tenant_id"] == str(tid)

    def test_to_dict_none_expires_at(self):
        alert = self._make_alert(expires_at=None)
        d = alert.to_dict()
        assert d["expires_at"] is None

    def test_to_dict_with_expires_at(self):
        now = datetime.now(UTC)
        alert = self._make_alert(expires_at=now)
        d = alert.to_dict()
        assert d["expires_at"] == now.isoformat()

    def test_to_dict_acknowledged(self):
        now = datetime.now(UTC)
        alert = self._make_alert(acknowledged_at=now, acknowledged_by="user-1")
        d = alert.to_dict()
        assert d["acknowledged_at"] == now.isoformat()
        assert d["acknowledged_by"] == "user-1"

    def test_to_dict_dismissed(self):
        now = datetime.now(UTC)
        alert = self._make_alert(dismissed_at=now, dismissed_by="user-2")
        d = alert.to_dict()
        assert d["dismissed_at"] == now.isoformat()
        assert d["dismissed_by"] == "user-2"

    def test_to_dict_resolved(self):
        now = datetime.now(UTC)
        alert = self._make_alert(
            resolved_at=now,
            resolved_by="user-3",
            resolution_note="Fixed",
        )
        d = alert.to_dict()
        assert d["resolved_at"] == now.isoformat()
        assert d["resolved_by"] == "user-3"
        assert d["resolution_note"] == "Fixed"

    def test_to_dict_none_recommendations(self):
        alert = self._make_alert(recommendations=None, recommendations_en=None)
        d = alert.to_dict()
        assert d["recommendations"] == []
        assert d["recommendations_en"] == []

    def test_to_dict_none_metadata(self):
        alert = self._make_alert(extra_metadata=None)
        d = alert.to_dict()
        assert d["metadata"] == {}

    def test_repr(self):
        alert = self._make_alert()
        r = repr(alert)
        assert "Alert(" in r
        assert "field-001" in r
        assert "weather" in r
        assert "high" in r
        assert "active" in r

    def test_tablename(self):
        from src.db_models import Alert

        assert Alert.__tablename__ == "alerts"

    def test_table_args_has_indexes(self):
        from src.db_models import Alert

        # __table_args__ should be a tuple with Index objects
        assert isinstance(Alert.__table_args__, tuple)
        assert len(Alert.__table_args__) >= 5  # 5 indexes defined


# ═══════════════════════════════════════════════════════════════════════════════
# AlertRule Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertRuleModel:
    """Tests for AlertRule SQLAlchemy model."""

    def _make_rule(self, **overrides):
        from src.db_models import AlertRule

        now = datetime.now(UTC)
        defaults = dict(
            id=uuid4(),
            field_id="field-001",
            tenant_id=uuid4(),
            name="Test Rule",
            name_en="Test Rule EN",
            enabled=True,
            condition={"metric": "ndvi", "operator": "lt", "value": 0.3},
            alert_config={"type": "ndvi_low", "severity": "high", "title": "NDVI Low"},
            cooldown_hours=24,
            last_triggered_at=None,
            created_at=now,
            updated_at=now,
        )
        defaults.update(overrides)
        return AlertRule(**defaults)

    def test_to_dict_basic(self):
        rule = self._make_rule()
        d = rule.to_dict()

        assert d["id"] == str(rule.id)
        assert d["field_id"] == "field-001"
        assert d["name"] == "Test Rule"
        assert d["name_en"] == "Test Rule EN"
        assert d["enabled"] is True
        assert d["condition"]["metric"] == "ndvi"
        assert d["alert_config"]["type"] == "ndvi_low"
        assert d["cooldown_hours"] == 24
        assert d["last_triggered_at"] is None

    def test_to_dict_none_tenant(self):
        rule = self._make_rule(tenant_id=None)
        d = rule.to_dict()
        assert d["tenant_id"] is None

    def test_to_dict_with_tenant(self):
        tid = uuid4()
        rule = self._make_rule(tenant_id=tid)
        d = rule.to_dict()
        assert d["tenant_id"] == str(tid)

    def test_to_dict_with_last_triggered(self):
        now = datetime.now(UTC)
        rule = self._make_rule(last_triggered_at=now)
        d = rule.to_dict()
        assert d["last_triggered_at"] == now.isoformat()

    def test_to_dict_disabled_rule(self):
        rule = self._make_rule(enabled=False)
        d = rule.to_dict()
        assert d["enabled"] is False

    def test_repr(self):
        rule = self._make_rule()
        r = repr(rule)
        assert "AlertRule(" in r
        assert "field-001" in r
        assert "Test Rule" in r

    def test_tablename(self):
        from src.db_models import AlertRule

        assert AlertRule.__tablename__ == "alert_rules"

    def test_table_args_has_indexes(self):
        from src.db_models import AlertRule

        assert isinstance(AlertRule.__table_args__, tuple)
        assert len(AlertRule.__table_args__) >= 3

    def test_to_dict_timestamps_are_isoformat(self):
        rule = self._make_rule()
        d = rule.to_dict()
        # Verify they parse back
        datetime.fromisoformat(d["created_at"])
        datetime.fromisoformat(d["updated_at"])


# ═══════════════════════════════════════════════════════════════════════════════
# Base declarative_base Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestBase:
    """Test the SQLAlchemy Base."""

    def test_base_exists(self):
        from src.db_models import Base

        assert Base is not None

    def test_base_has_metadata(self):
        from src.db_models import Base

        assert hasattr(Base, "metadata")
        # Metadata should contain both tables
        table_names = list(Base.metadata.tables.keys())
        assert "alerts" in table_names
        assert "alert_rules" in table_names
