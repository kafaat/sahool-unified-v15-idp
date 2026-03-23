"""
SAHOOL Alert Service - Comprehensive Repository Tests
Tests for uncovered repository paths: update_alert_rule, mark_rule_triggered,
get_rules_ready_to_trigger edge cases, delete_alert_rule with tenant,
get_active_alerts with tenant, and statistics edge cases.
"""

import pytest

try:
    import sqlalchemy  # noqa: F401
except ImportError:
    pytest.skip("sqlalchemy not installed", allow_module_level=True)

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from uuid import UUID, uuid4


@pytest.fixture
def mock_db():
    session = MagicMock()
    session.add = MagicMock()
    session.delete = MagicMock()
    session.flush = MagicMock()
    session.execute = MagicMock()
    return session


def _make_mock_alert(**kwargs):
    from src.db_models import Alert

    defaults = dict(  # noqa: C408
        id=uuid4(),
        field_id="field-001",
        tenant_id=uuid4(),
        type="weather",
        severity="high",
        status="active",
        title="Alert",
        title_en="Alert EN",
        message="Msg",
        message_en="Msg EN",
        recommendations=[],
        recommendations_en=[],
        extra_metadata={},
        source_service=None,
        correlation_id=None,
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
    defaults.update(kwargs)
    return Alert(**defaults)


def _make_mock_rule(**kwargs):
    from src.db_models import AlertRule

    now = datetime.now(UTC)
    defaults = dict(  # noqa: C408
        id=uuid4(),
        field_id="field-001",
        tenant_id=uuid4(),
        name="Rule",
        name_en="Rule EN",
        enabled=True,
        condition={"metric": "ndvi", "operator": "lt", "value": 0.3},
        alert_config={"type": "ndvi_low", "severity": "high", "title": "T"},
        cooldown_hours=24,
        last_triggered_at=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(kwargs)
    return AlertRule(**defaults)


# ═══════════════════════════════════════════════════════════════════════════════
# update_alert_rule Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestUpdateAlertRule:
    """Tests for update_alert_rule repository function."""

    def test_update_rule_not_found(self, mock_db):
        from src.repository import update_alert_rule

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = update_alert_rule(mock_db, rule_id=uuid4(), enabled=False)
        assert result is None

    def test_update_rule_changes_fields(self, mock_db):
        from src.repository import update_alert_rule

        rule = _make_mock_rule(enabled=True, cooldown_hours=24)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = rule
        mock_db.execute.return_value = mock_result

        result = update_alert_rule(mock_db, rule_id=rule.id, enabled=False, cooldown_hours=48)

        assert result is rule
        assert rule.enabled is False
        assert rule.cooldown_hours == 48
        assert rule.updated_at is not None

    def test_update_rule_ignores_nonexistent_fields(self, mock_db):
        from src.repository import update_alert_rule

        rule = _make_mock_rule()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = rule
        mock_db.execute.return_value = mock_result

        result = update_alert_rule(mock_db, rule_id=rule.id, nonexistent_field="value")

        assert result is rule  # Should not crash


# ═══════════════════════════════════════════════════════════════════════════════
# mark_rule_triggered Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestMarkRuleTriggered:
    """Tests for mark_rule_triggered repository function."""

    def test_mark_not_found(self, mock_db):
        from src.repository import mark_rule_triggered

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = mark_rule_triggered(mock_db, uuid4())
        assert result is None

    def test_mark_updates_timestamp(self, mock_db):
        from src.repository import mark_rule_triggered

        rule = _make_mock_rule(last_triggered_at=None)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = rule
        mock_db.execute.return_value = mock_result

        before = datetime.now(UTC)
        result = mark_rule_triggered(mock_db, rule.id)

        assert result is rule
        assert rule.last_triggered_at is not None
        assert rule.last_triggered_at >= before


# ═══════════════════════════════════════════════════════════════════════════════
# get_rules_ready_to_trigger Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════
class TestGetRulesReadyToTrigger:
    """Edge case tests for get_rules_ready_to_trigger."""

    def test_rule_in_cooldown_not_ready(self, mock_db):
        from src.repository import get_rules_ready_to_trigger

        rule = _make_mock_rule(
            last_triggered_at=datetime.now(UTC) - timedelta(hours=1),
            cooldown_hours=24,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value = [rule]
        mock_db.execute.return_value = mock_result

        ready = get_rules_ready_to_trigger(mock_db)
        assert len(ready) == 0  # Still in cooldown

    def test_rule_cooldown_zero_always_ready(self, mock_db):
        from src.repository import get_rules_ready_to_trigger

        rule = _make_mock_rule(
            last_triggered_at=datetime.now(UTC),
            cooldown_hours=0,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value = [rule]
        mock_db.execute.return_value = mock_result

        ready = get_rules_ready_to_trigger(mock_db)
        assert len(ready) == 1

    def test_multiple_rules_mixed(self, mock_db):
        from src.repository import get_rules_ready_to_trigger

        # Rule 1: never triggered -> ready
        rule1 = _make_mock_rule(last_triggered_at=None, cooldown_hours=24)
        # Rule 2: in cooldown -> not ready
        rule2 = _make_mock_rule(
            last_triggered_at=datetime.now(UTC) - timedelta(hours=1),
            cooldown_hours=24,
        )
        # Rule 3: past cooldown -> ready
        rule3 = _make_mock_rule(
            last_triggered_at=datetime.now(UTC) - timedelta(hours=25),
            cooldown_hours=24,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value = [rule1, rule2, rule3]
        mock_db.execute.return_value = mock_result

        ready = get_rules_ready_to_trigger(mock_db)
        assert len(ready) == 2

    def test_with_tenant_filter(self, mock_db):
        from src.repository import get_rules_ready_to_trigger

        rule = _make_mock_rule(last_triggered_at=None)

        mock_result = MagicMock()
        mock_result.scalars.return_value = [rule]
        mock_db.execute.return_value = mock_result

        ready = get_rules_ready_to_trigger(mock_db, tenant_id=uuid4())
        assert len(ready) == 1

    def test_empty_rules(self, mock_db):
        from src.repository import get_rules_ready_to_trigger

        mock_result = MagicMock()
        mock_result.scalars.return_value = []
        mock_db.execute.return_value = mock_result

        ready = get_rules_ready_to_trigger(mock_db)
        assert len(ready) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# delete_alert_rule with tenant Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestDeleteAlertRuleWithTenant:
    """Tests for delete_alert_rule with tenant isolation."""

    def test_delete_with_tenant(self, mock_db):
        from src.repository import delete_alert_rule

        rule = _make_mock_rule()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = rule
        mock_db.execute.return_value = mock_result

        result = delete_alert_rule(mock_db, rule.id, tenant_id=str(uuid4()))
        assert result is True
        mock_db.delete.assert_called_once_with(rule)

    def test_delete_not_found_with_tenant(self, mock_db):
        from src.repository import delete_alert_rule

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = delete_alert_rule(mock_db, uuid4(), tenant_id=str(uuid4()))
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# delete_alert with tenant Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestDeleteAlertWithTenant:
    """Tests for delete_alert with tenant isolation."""

    def test_delete_with_tenant(self, mock_db):
        from src.repository import delete_alert

        alert = _make_mock_alert()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = alert
        mock_db.execute.return_value = mock_result

        result = delete_alert(mock_db, alert.id, tenant_id=str(uuid4()))
        assert result is True

    def test_delete_not_found_with_tenant(self, mock_db):
        from src.repository import delete_alert

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = delete_alert(mock_db, uuid4(), tenant_id=str(uuid4()))
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# get_active_alerts Extended Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestGetActiveAlertsExtended:
    """Extended tests for get_active_alerts with tenant/field filters."""

    def test_with_tenant_filter(self, mock_db):
        from src.repository import get_active_alerts

        alert = _make_mock_alert()

        mock_result = MagicMock()
        mock_result.scalars.return_value = [alert]
        mock_db.execute.return_value = mock_result

        alerts = get_active_alerts(mock_db, tenant_id=uuid4())
        assert len(alerts) == 1

    def test_with_both_filters(self, mock_db):
        from src.repository import get_active_alerts

        mock_result = MagicMock()
        mock_result.scalars.return_value = []
        mock_db.execute.return_value = mock_result

        alerts = get_active_alerts(mock_db, tenant_id=uuid4(), field_id="field-1")
        assert len(alerts) == 0

    def test_empty_result(self, mock_db):
        from src.repository import get_active_alerts

        mock_result = MagicMock()
        mock_result.scalars.return_value = []
        mock_db.execute.return_value = mock_result

        alerts = get_active_alerts(mock_db)
        assert alerts == []


# ═══════════════════════════════════════════════════════════════════════════════
# get_alert_statistics Extended Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestGetAlertStatisticsExtended:
    """Extended tests for statistics calculation."""

    def test_multiple_types_and_severities(self, mock_db):
        from src.repository import get_alert_statistics

        alerts = [
            _make_mock_alert(type="weather", severity="high", status="active"),
            _make_mock_alert(type="weather", severity="low", status="resolved"),
            _make_mock_alert(type="pest", severity="critical", status="acknowledged"),
            _make_mock_alert(type="pest", severity="critical", status="active"),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value = alerts
        mock_db.execute.return_value = mock_result

        stats = get_alert_statistics(mock_db, days=30)

        assert stats["total_alerts"] == 4
        assert stats["active_alerts"] == 2
        assert stats["by_type"]["weather"] == 2
        assert stats["by_type"]["pest"] == 2
        assert stats["by_severity"]["critical"] == 2
        assert stats["by_status"]["active"] == 2
        assert stats["acknowledged_count"] == 1
        assert stats["resolved_count"] == 1

    def test_resolution_time_calculation(self, mock_db):
        from src.repository import get_alert_statistics

        now = datetime.now(UTC)
        alert1 = _make_mock_alert(
            status="resolved",
            created_at=now - timedelta(hours=6),
            resolved_at=now,
        )
        alert2 = _make_mock_alert(
            status="resolved",
            created_at=now - timedelta(hours=4),
            resolved_at=now,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value = [alert1, alert2]
        mock_db.execute.return_value = mock_result

        stats = get_alert_statistics(mock_db, days=30)

        # Average of 6 and 4 = 5
        assert stats["average_resolution_hours"] == 5.0

    def test_no_resolved_alerts_gives_none_avg(self, mock_db):
        from src.repository import get_alert_statistics

        alert = _make_mock_alert(status="active")

        mock_result = MagicMock()
        mock_result.scalars.return_value = [alert]
        mock_db.execute.return_value = mock_result

        stats = get_alert_statistics(mock_db, days=30)

        assert stats["average_resolution_hours"] is None

    def test_stats_with_field_filter(self, mock_db):
        from src.repository import get_alert_statistics

        mock_result = MagicMock()
        mock_result.scalars.return_value = []
        mock_db.execute.return_value = mock_result

        stats = get_alert_statistics(mock_db, field_id="field-1", days=7)

        assert stats["total_alerts"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# update_alert_status Extended Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestUpdateAlertStatusExtended:
    """Extended tests for update_alert_status."""

    def test_update_with_tenant_filter(self, mock_db):
        from src.repository import update_alert_status

        alert = _make_mock_alert()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = alert
        mock_db.execute.return_value = mock_result

        result = update_alert_status(
            mock_db,
            alert_id=alert.id,
            status="acknowledged",
            user_id="user-1",
            tenant_id=str(uuid4()),
        )
        assert result is alert
        assert alert.status == "acknowledged"

    def test_update_resolved_without_note(self, mock_db):
        from src.repository import update_alert_status

        alert = _make_mock_alert()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = alert
        mock_db.execute.return_value = mock_result

        result = update_alert_status(
            mock_db,
            alert_id=alert.id,
            status="resolved",
            user_id="user-1",
        )
        assert result.status == "resolved"
        assert result.resolved_by == "user-1"
        assert result.resolution_note is None  # note was not provided

    def test_update_generic_status(self, mock_db):
        """Test a status that isn't acknowledged/dismissed/resolved."""
        from src.repository import update_alert_status

        alert = _make_mock_alert()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = alert
        mock_db.execute.return_value = mock_result

        result = update_alert_status(
            mock_db,
            alert_id=alert.id,
            status="expired",
        )
        assert result.status == "expired"
        # No special timestamp tracking for expired


# ═══════════════════════════════════════════════════════════════════════════════
# get_alert_rule Extended Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestGetAlertRuleExtended:
    """Extended tests for get_alert_rule."""

    def test_get_rule_with_tenant(self, mock_db):
        from src.repository import get_alert_rule

        rule = _make_mock_rule()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = rule
        mock_db.execute.return_value = mock_result

        result = get_alert_rule(mock_db, rule_id=rule.id, tenant_id=uuid4())
        assert result is rule

    def test_get_rule_not_found(self, mock_db):
        from src.repository import get_alert_rule

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = get_alert_rule(mock_db, rule_id=uuid4())
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════════
# get_enabled_rules Extended Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestGetEnabledRulesExtended:
    """Extended tests for get_enabled_rules."""

    def test_with_tenant(self, mock_db):
        from src.repository import get_enabled_rules

        rule = _make_mock_rule()

        mock_result = MagicMock()
        mock_result.scalars.return_value = [rule]
        mock_db.execute.return_value = mock_result

        rules = get_enabled_rules(mock_db, tenant_id=uuid4())
        assert len(rules) == 1

    def test_no_enabled_rules(self, mock_db):
        from src.repository import get_enabled_rules

        mock_result = MagicMock()
        mock_result.scalars.return_value = []
        mock_db.execute.return_value = mock_result

        rules = get_enabled_rules(mock_db)
        assert rules == []


# ═══════════════════════════════════════════════════════════════════════════════
# SEVERITY_ORDER Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestSeverityOrder:
    """Tests for the SEVERITY_ORDER constant."""

    def test_ordering(self):
        from src.repository import SEVERITY_ORDER

        assert SEVERITY_ORDER["critical"] < SEVERITY_ORDER["high"]
        assert SEVERITY_ORDER["high"] < SEVERITY_ORDER["medium"]
        assert SEVERITY_ORDER["medium"] < SEVERITY_ORDER["low"]
        assert SEVERITY_ORDER["low"] < SEVERITY_ORDER["info"]

    def test_all_severities_present(self):
        from src.repository import SEVERITY_ORDER

        assert set(SEVERITY_ORDER.keys()) == {"critical", "high", "medium", "low", "info"}
