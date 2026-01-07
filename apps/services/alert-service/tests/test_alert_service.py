"""
SAHOOL Alert Service - Service Layer Tests
Comprehensive unit tests for alert business logic
Coverage: Repository operations, alert rules, statistics, event processing
"""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    session = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.close = MagicMock()
    session.execute = MagicMock()
    session.query = MagicMock()
    session.add = MagicMock()
    session.delete = MagicMock()
    session.flush = MagicMock()
    return session


@pytest.fixture
def mock_alert(mock_db_session):
    """Create a mock alert"""
    from src.db_models import Alert

    alert = Alert(
        id=uuid4(),
        field_id='field-123',
        tenant_id='tenant-1',
        type='ndvi_low',
        severity='high',
        status='active',
        title='Low NDVI Alert',
        title_en='Low NDVI Alert',
        message='NDVI below threshold',
        message_en='NDVI below threshold',
        recommendations=['Check irrigation'],
        recommendations_en=['Check irrigation'],
        metadata={'current_ndvi': 0.15},
        source_service='ndvi-engine',
        correlation_id=str(uuid4())
    )
    alert.created_at = datetime.now(UTC)
    return alert


@pytest.fixture
def mock_alert_rule(mock_db_session):
    """Create a mock alert rule"""
    from src.db_models import AlertRule

    rule = AlertRule(
        id=uuid4(),
        field_id='field-123',
        tenant_id='tenant-1',
        name='Low Soil Moisture',
        name_en='Low Soil Moisture',
        enabled=True,
        condition={'metric': 'soil_moisture', 'operator': 'lt', 'value': 20},
        alert_config={'type': 'irrigation', 'severity': 'high', 'title': 'Low Moisture'},
        cooldown_hours=24
    )
    rule.created_at = datetime.now(UTC)
    rule.updated_at = datetime.now(UTC)
    return rule


class TestAlertRepository:
    """Test alert repository operations"""

    def test_create_alert(self, mock_db_session, mock_alert):
        """Test creating an alert"""
        from src.repository import create_alert

        result = create_alert(mock_db_session, mock_alert)

        assert result == mock_alert
        mock_db_session.add.assert_called_once_with(mock_alert)
        mock_db_session.flush.assert_called_once()

    def test_get_alert_by_id(self, mock_db_session, mock_alert):
        """Test getting alert by ID"""
        from src.repository import get_alert

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_alert)
        mock_db_session.execute = MagicMock(return_value=mock_result)

        result = get_alert(mock_db_session, alert_id=mock_alert.id)

        assert result == mock_alert

    def test_get_alert_by_id_with_tenant(self, mock_db_session, mock_alert):
        """Test getting alert by ID with tenant isolation"""
        from src.repository import get_alert

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_alert)
        mock_db_session.execute = MagicMock(return_value=mock_result)

        result = get_alert(
            mock_db_session,
            alert_id=mock_alert.id,
            tenant_id=UUID('12345678-1234-5678-1234-567812345678')
        )

        assert result == mock_alert

    def test_get_alert_not_found(self, mock_db_session):
        """Test getting non-existent alert"""
        from src.repository import get_alert

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = MagicMock(return_value=mock_result)

        result = get_alert(mock_db_session, alert_id=uuid4())

        assert result is None

    def test_get_alerts_by_field(self, mock_db_session, mock_alert):
        """Test getting alerts by field"""
        from src.repository import get_alerts_by_field

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        alerts, total = get_alerts_by_field(
            mock_db_session,
            field_id='field-123'
        )

        assert len(alerts) == 1
        assert alerts[0] == mock_alert
        assert total == 1

    def test_get_alerts_by_field_with_filters(self, mock_db_session, mock_alert):
        """Test getting alerts with filters"""
        from src.repository import get_alerts_by_field

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        alerts, total = get_alerts_by_field(
            mock_db_session,
            field_id='field-123',
            status='active',
            alert_type='ndvi_low',
            severity='high',
            skip=0,
            limit=10
        )

        assert len(alerts) == 1

    def test_get_alerts_by_field_pagination(self, mock_db_session, mock_alert):
        """Test pagination in alerts retrieval"""
        from src.repository import get_alerts_by_field

        mock_alerts = [mock_alert] * 5
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=mock_alerts)
        mock_db_session.execute = MagicMock(return_value=mock_result)

        alerts, total = get_alerts_by_field(
            mock_db_session,
            field_id='field-123',
            skip=10,
            limit=5
        )

        assert len(alerts) == 5

    def test_get_alerts_by_tenant(self, mock_db_session, mock_alert):
        """Test getting alerts by tenant"""
        from src.repository import get_alerts_by_tenant

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        alerts = get_alerts_by_tenant(
            mock_db_session,
            tenant_id=UUID('12345678-1234-5678-1234-567812345678')
        )

        assert len(alerts) == 1

    def test_get_alerts_by_tenant_with_filters(self, mock_db_session, mock_alert):
        """Test getting alerts by tenant with filters"""
        from src.repository import get_alerts_by_tenant

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        start_date = datetime.now(UTC) - timedelta(days=7)
        end_date = datetime.now(UTC)

        alerts = get_alerts_by_tenant(
            mock_db_session,
            tenant_id=UUID('12345678-1234-5678-1234-567812345678'),
            status='active',
            start_date=start_date,
            end_date=end_date
        )

        assert len(alerts) == 1

    def test_update_alert_status(self, mock_db_session, mock_alert):
        """Test updating alert status"""
        from src.repository import update_alert_status

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_alert

        result = update_alert_status(
            mock_db_session,
            alert_id=mock_alert.id,
            status='acknowledged',
            user_id='user-123'
        )

        assert result == mock_alert
        assert mock_alert.status == 'acknowledged'
        assert mock_alert.acknowledged_by == 'user-123'
        assert mock_alert.acknowledged_at is not None

    def test_update_alert_status_resolved(self, mock_db_session, mock_alert):
        """Test updating alert to resolved status"""
        from src.repository import update_alert_status

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_alert

        result = update_alert_status(
            mock_db_session,
            alert_id=mock_alert.id,
            status='resolved',
            user_id='user-123',
            note='Fixed irrigation system'
        )

        assert result == mock_alert
        assert mock_alert.status == 'resolved'
        assert mock_alert.resolved_by == 'user-123'
        assert mock_alert.resolution_note == 'Fixed irrigation system'
        assert mock_alert.resolved_at is not None

    def test_update_alert_status_dismissed(self, mock_db_session, mock_alert):
        """Test updating alert to dismissed status"""
        from src.repository import update_alert_status

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_alert

        result = update_alert_status(
            mock_db_session,
            alert_id=mock_alert.id,
            status='dismissed',
            user_id='user-123'
        )

        assert result == mock_alert
        assert mock_alert.status == 'dismissed'
        assert mock_alert.dismissed_by == 'user-123'
        assert mock_alert.dismissed_at is not None

    def test_update_alert_status_not_found(self, mock_db_session):
        """Test updating non-existent alert"""
        from src.repository import update_alert_status

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = update_alert_status(
            mock_db_session,
            alert_id=uuid4(),
            status='acknowledged'
        )

        assert result is None

    def test_delete_alert(self, mock_db_session, mock_alert):
        """Test deleting an alert"""
        from src.repository import delete_alert

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_alert

        result = delete_alert(mock_db_session, mock_alert.id)

        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_alert)

    def test_delete_alert_not_found(self, mock_db_session):
        """Test deleting non-existent alert"""
        from src.repository import delete_alert

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = delete_alert(mock_db_session, uuid4())

        assert result is False

    def test_get_active_alerts(self, mock_db_session, mock_alert):
        """Test getting active alerts"""
        from src.repository import get_active_alerts

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        alerts = get_active_alerts(mock_db_session)

        assert len(alerts) == 1
        assert alerts[0] == mock_alert

    def test_get_active_alerts_by_field(self, mock_db_session, mock_alert):
        """Test getting active alerts for a field"""
        from src.repository import get_active_alerts

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        alerts = get_active_alerts(
            mock_db_session,
            field_id='field-123'
        )

        assert len(alerts) == 1


class TestAlertRuleRepository:
    """Test alert rule repository operations"""

    def test_create_alert_rule(self, mock_db_session, mock_alert_rule):
        """Test creating an alert rule"""
        from src.repository import create_alert_rule

        result = create_alert_rule(mock_db_session, mock_alert_rule)

        assert result == mock_alert_rule
        mock_db_session.add.assert_called_once_with(mock_alert_rule)
        mock_db_session.flush.assert_called_once()

    def test_get_alert_rule(self, mock_db_session, mock_alert_rule):
        """Test getting alert rule by ID"""
        from src.repository import get_alert_rule

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_alert_rule)
        mock_db_session.execute = MagicMock(return_value=mock_result)

        result = get_alert_rule(mock_db_session, rule_id=mock_alert_rule.id)

        assert result == mock_alert_rule

    def test_get_alert_rules_by_field(self, mock_db_session, mock_alert_rule):
        """Test getting alert rules by field"""
        from src.repository import get_alert_rules_by_field

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert_rule])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        rules = get_alert_rules_by_field(
            mock_db_session,
            field_id='field-123'
        )

        assert len(rules) == 1
        assert rules[0] == mock_alert_rule

    def test_get_alert_rules_by_field_enabled_only(self, mock_db_session, mock_alert_rule):
        """Test getting only enabled rules"""
        from src.repository import get_alert_rules_by_field

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert_rule])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        rules = get_alert_rules_by_field(
            mock_db_session,
            field_id='field-123',
            enabled_only=True
        )

        assert len(rules) == 1

    def test_get_enabled_rules(self, mock_db_session, mock_alert_rule):
        """Test getting all enabled rules"""
        from src.repository import get_enabled_rules

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert_rule])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        rules = get_enabled_rules(mock_db_session)

        assert len(rules) == 1

    def test_update_alert_rule(self, mock_db_session, mock_alert_rule):
        """Test updating alert rule"""
        from src.repository import update_alert_rule

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_alert_rule

        result = update_alert_rule(
            mock_db_session,
            rule_id=mock_alert_rule.id,
            enabled=False,
            cooldown_hours=48
        )

        assert result == mock_alert_rule
        assert mock_alert_rule.enabled is False
        assert mock_alert_rule.cooldown_hours == 48

    def test_delete_alert_rule(self, mock_db_session, mock_alert_rule):
        """Test deleting alert rule"""
        from src.repository import delete_alert_rule

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_alert_rule

        result = delete_alert_rule(mock_db_session, mock_alert_rule.id)

        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_alert_rule)

    def test_mark_rule_triggered(self, mock_db_session, mock_alert_rule):
        """Test marking rule as triggered"""
        from src.repository import mark_rule_triggered

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_alert_rule

        result = mark_rule_triggered(mock_db_session, mock_alert_rule.id)

        assert result == mock_alert_rule
        assert mock_alert_rule.last_triggered_at is not None

    def test_get_rules_ready_to_trigger(self, mock_db_session, mock_alert_rule):
        """Test getting rules ready to trigger"""
        from src.repository import get_rules_ready_to_trigger

        # Rule never triggered
        mock_alert_rule.last_triggered_at = None

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert_rule])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        rules = get_rules_ready_to_trigger(mock_db_session)

        assert len(rules) == 1

    def test_get_rules_ready_to_trigger_after_cooldown(self, mock_db_session, mock_alert_rule):
        """Test getting rules after cooldown period"""
        from src.repository import get_rules_ready_to_trigger

        # Rule triggered more than cooldown period ago
        mock_alert_rule.last_triggered_at = datetime.now(UTC) - timedelta(hours=25)
        mock_alert_rule.cooldown_hours = 24

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert_rule])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        rules = get_rules_ready_to_trigger(mock_db_session)

        assert len(rules) == 1


class TestAlertStatistics:
    """Test alert statistics operations"""

    def test_get_alert_statistics(self, mock_db_session, mock_alert):
        """Test getting alert statistics"""
        from src.repository import get_alert_statistics

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        stats = get_alert_statistics(
            mock_db_session,
            tenant_id=UUID('12345678-1234-5678-1234-567812345678'),
            days=30
        )

        assert 'total_alerts' in stats
        assert 'active_alerts' in stats
        assert 'by_type' in stats
        assert 'by_severity' in stats
        assert 'by_status' in stats

    def test_get_alert_statistics_by_field(self, mock_db_session, mock_alert):
        """Test getting statistics for specific field"""
        from src.repository import get_alert_statistics

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        stats = get_alert_statistics(
            mock_db_session,
            tenant_id=UUID('12345678-1234-5678-1234-567812345678'),
            field_id='field-123',
            days=7
        )

        assert stats['total_alerts'] >= 0

    def test_get_alert_statistics_resolution_time(self, mock_db_session, mock_alert):
        """Test calculating average resolution time"""
        from src.repository import get_alert_statistics

        # Set resolved times for calculation
        mock_alert.resolved_at = mock_alert.created_at + timedelta(hours=4)

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        stats = get_alert_statistics(
            mock_db_session,
            tenant_id=UUID('12345678-1234-5678-1234-567812345678'),
            days=30
        )

        assert 'average_resolution_hours' in stats
        if stats['average_resolution_hours'] is not None:
            assert stats['average_resolution_hours'] > 0

    def test_get_alert_statistics_empty(self, mock_db_session):
        """Test statistics with no alerts"""
        from src.repository import get_alert_statistics

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        stats = get_alert_statistics(
            mock_db_session,
            tenant_id=UUID('12345678-1234-5678-1234-567812345678'),
            days=30
        )

        assert stats['total_alerts'] == 0
        assert stats['active_alerts'] == 0


class TestAlertModels:
    """Test alert data models"""

    def test_alert_to_dict(self, mock_alert):
        """Test alert to_dict method"""
        result = mock_alert.to_dict()

        assert 'id' in result
        assert 'field_id' in result
        assert 'type' in result
        assert 'severity' in result
        assert 'status' in result

    def test_alert_rule_to_dict(self, mock_alert_rule):
        """Test alert rule to_dict method"""
        result = mock_alert_rule.to_dict()

        assert 'id' in result
        assert 'field_id' in result
        assert 'name' in result
        assert 'enabled' in result
        assert 'condition' in result
        assert 'alert_config' in result


class TestAlertTypes:
    """Test alert types and enums"""

    def test_alert_type_enum(self):
        """Test AlertType enum"""
        from src.models import AlertType

        assert AlertType.WEATHER == 'weather'
        assert AlertType.NDVI_LOW == 'ndvi_low'
        assert AlertType.IRRIGATION == 'irrigation'

    def test_alert_severity_enum(self):
        """Test AlertSeverity enum"""
        from src.models import AlertSeverity

        assert AlertSeverity.CRITICAL == 'critical'
        assert AlertSeverity.HIGH == 'high'
        assert AlertSeverity.MEDIUM == 'medium'
        assert AlertSeverity.LOW == 'low'

    def test_alert_status_enum(self):
        """Test AlertStatus enum"""
        from src.models import AlertStatus

        assert AlertStatus.ACTIVE == 'active'
        assert AlertStatus.ACKNOWLEDGED == 'acknowledged'
        assert AlertStatus.DISMISSED == 'dismissed'
        assert AlertStatus.RESOLVED == 'resolved'


class TestAlertValidation:
    """Test alert validation"""

    def test_alert_create_validation(self):
        """Test alert creation validation"""
        from src.models import AlertCreate, AlertType, AlertSeverity

        alert_data = AlertCreate(
            field_id='field-123',
            type=AlertType.NDVI_LOW,
            severity=AlertSeverity.HIGH,
            title='Test Alert',
            message='Test message'
        )

        assert alert_data.field_id == 'field-123'
        assert alert_data.type == AlertType.NDVI_LOW
        assert alert_data.severity == AlertSeverity.HIGH

    def test_alert_update_validation(self):
        """Test alert update validation"""
        from src.models import AlertUpdate, AlertStatus

        update_data = AlertUpdate(
            status=AlertStatus.ACKNOWLEDGED,
            acknowledged_by='user-123'
        )

        assert update_data.status == AlertStatus.ACKNOWLEDGED
        assert update_data.acknowledged_by == 'user-123'

    def test_alert_rule_create_validation(self):
        """Test alert rule creation validation"""
        from src.models import (
            AlertRuleCreate,
            RuleCondition,
            AlertRuleConfig,
            AlertType,
            AlertSeverity,
            ConditionOperator
        )

        condition = RuleCondition(
            metric='soil_moisture',
            operator=ConditionOperator.LT,
            value=20.0
        )

        alert_config = AlertRuleConfig(
            type=AlertType.IRRIGATION,
            severity=AlertSeverity.HIGH,
            title='Low Moisture'
        )

        rule_data = AlertRuleCreate(
            field_id='field-123',
            name='Low Moisture Rule',
            enabled=True,
            condition=condition,
            alert_config=alert_config,
            cooldown_hours=24
        )

        assert rule_data.field_id == 'field-123'
        assert rule_data.condition.metric == 'soil_moisture'
        assert rule_data.alert_config.type == AlertType.IRRIGATION


class TestAlertEvents:
    """Test alert event handling"""

    @pytest.mark.asyncio
    async def test_publish_alert_created(self):
        """Test publishing alert created event"""
        from src.events import AlertPublisher

        mock_nc = AsyncMock()
        publisher = AlertPublisher(mock_nc)

        await publisher.publish_alert_created(
            alert_id='alert-123',
            field_id='field-123',
            tenant_id='tenant-1',
            alert_type='ndvi_low',
            severity='high',
            title='Test Alert'
        )

        assert mock_nc.publish.called

    @pytest.mark.asyncio
    async def test_publish_alert_updated(self):
        """Test publishing alert updated event"""
        from src.events import AlertPublisher

        mock_nc = AsyncMock()
        publisher = AlertPublisher(mock_nc)

        await publisher.publish_alert_updated(
            alert_id='alert-123',
            field_id='field-123',
            old_status='active',
            new_status='acknowledged',
            updated_by='user-123'
        )

        assert mock_nc.publish.called

    @pytest.mark.asyncio
    async def test_subscribe_to_external_alerts(self):
        """Test subscribing to external alerts"""
        from src.events import AlertSubscriber

        mock_nc = AsyncMock()
        subscriber = AlertSubscriber(mock_nc)

        await subscriber.subscribe_to_external_alerts()

        # Should subscribe to multiple topics
        assert mock_nc.subscribe.call_count >= 3


class TestDatabaseConnection:
    """Test database connection functions"""

    def test_check_db_connection_success(self):
        """Test successful database connection check"""
        with patch('src.database.SessionLocal') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value = mock_db
            mock_db.execute = MagicMock()
            mock_db.close = MagicMock()

            from src.database import check_db_connection

            result = check_db_connection()

            assert result is True

    def test_check_db_connection_failure(self):
        """Test failed database connection check"""
        with patch('src.database.SessionLocal', side_effect=Exception('Connection error')):
            from src.database import check_db_connection

            result = check_db_connection()

            assert result is False


class TestErrorHandling:
    """Test error handling in repository"""

    def test_create_alert_with_duplicate_id(self, mock_db_session, mock_alert):
        """Test handling duplicate alert creation"""
        from src.repository import create_alert

        mock_db_session.flush.side_effect = Exception('Duplicate key')

        with pytest.raises(Exception):
            create_alert(mock_db_session, mock_alert)

    def test_update_nonexistent_alert(self, mock_db_session):
        """Test updating non-existent alert"""
        from src.repository import update_alert_status

        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = update_alert_status(
            mock_db_session,
            alert_id=uuid4(),
            status='acknowledged'
        )

        assert result is None


class TestComplexQueries:
    """Test complex query scenarios"""

    def test_get_alerts_with_multiple_filters(self, mock_db_session, mock_alert):
        """Test getting alerts with multiple filters"""
        from src.repository import get_alerts_by_field

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=[mock_alert])
        mock_db_session.execute = MagicMock(return_value=mock_result)

        alerts, total = get_alerts_by_field(
            mock_db_session,
            field_id='field-123',
            tenant_id=UUID('12345678-1234-5678-1234-567812345678'),
            status='active',
            alert_type='ndvi_low',
            severity='high'
        )

        assert len(alerts) == 1

    def test_get_statistics_with_grouping(self, mock_db_session):
        """Test statistics with grouping"""
        from src.repository import get_alert_statistics

        # Create multiple mock alerts with different types
        alerts = []
        for i in range(5):
            alert = MagicMock()
            alert.type = 'ndvi_low' if i < 3 else 'weather'
            alert.severity = 'high'
            alert.status = 'active'
            alerts.append(alert)

        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=alerts)
        mock_db_session.execute = MagicMock(return_value=mock_result)

        stats = get_alert_statistics(
            mock_db_session,
            tenant_id=UUID('12345678-1234-5678-1234-567812345678'),
            days=30
        )

        assert stats['total_alerts'] == 5
        assert 'ndvi_low' in stats['by_type']
