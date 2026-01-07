"""
SAHOOL Alert Service - API Tests
Comprehensive API endpoint testing with mocked dependencies
Coverage: API endpoints, error handling, CRUD operations, alert actions
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi.testclient import TestClient


@pytest.fixture
def mock_db():
    """Mock database session"""
    session = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.close = MagicMock()
    session.execute = MagicMock()
    session.query = MagicMock()
    return session


@pytest.fixture
def mock_alert():
    """Create a mock alert object"""
    alert = MagicMock()
    alert.id = uuid4()
    alert.field_id = 'field-123'
    alert.tenant_id = 'tenant-1'
    alert.type = 'ndvi_low'
    alert.severity = 'high'
    alert.status = 'active'
    alert.title = 'Low NDVI Alert'
    alert.title_en = 'Low NDVI Alert'
    alert.message = 'NDVI below threshold'
    alert.message_en = 'NDVI below threshold'
    alert.recommendations = ['Check irrigation']
    alert.recommendations_en = ['Check irrigation']
    alert.metadata = {'current_ndvi': 0.15}
    alert.source_service = 'ndvi-engine'
    alert.correlation_id = str(uuid4())
    alert.created_at = datetime.utcnow()
    alert.expires_at = None
    alert.acknowledged_at = None
    alert.acknowledged_by = None
    alert.dismissed_at = None
    alert.dismissed_by = None
    alert.resolved_at = None
    alert.resolved_by = None
    alert.resolution_note = None
    alert.to_dict = MagicMock(return_value={
        'id': str(alert.id),
        'field_id': alert.field_id,
        'tenant_id': alert.tenant_id,
        'type': alert.type,
        'severity': alert.severity,
        'status': alert.status,
        'title': alert.title,
        'title_en': alert.title_en,
        'message': alert.message,
        'message_en': alert.message_en,
        'recommendations': alert.recommendations,
        'recommendations_en': alert.recommendations_en,
        'metadata': alert.metadata,
        'source_service': alert.source_service,
        'correlation_id': alert.correlation_id,
        'created_at': alert.created_at.isoformat(),
        'expires_at': None,
        'acknowledged_at': None,
        'acknowledged_by': None,
        'dismissed_at': None,
        'dismissed_by': None,
        'resolved_at': None,
        'resolved_by': None,
        'resolution_note': None
    })
    return alert


@pytest.fixture
def mock_alert_rule():
    """Create a mock alert rule"""
    rule = MagicMock()
    rule.id = uuid4()
    rule.field_id = 'field-123'
    rule.tenant_id = 'tenant-1'
    rule.name = 'Low Soil Moisture Rule'
    rule.name_en = 'Low Soil Moisture Rule'
    rule.enabled = True
    rule.condition = {'metric': 'soil_moisture', 'operator': 'lt', 'value': 20}
    rule.alert_config = {'type': 'irrigation', 'severity': 'high', 'title': 'Low Moisture'}
    rule.cooldown_hours = 24
    rule.last_triggered_at = None
    rule.created_at = datetime.utcnow()
    rule.updated_at = datetime.utcnow()
    rule.to_dict = MagicMock(return_value={
        'id': str(rule.id),
        'field_id': rule.field_id,
        'tenant_id': rule.tenant_id,
        'name': rule.name,
        'name_en': rule.name_en,
        'enabled': rule.enabled,
        'condition': rule.condition,
        'alert_config': rule.alert_config,
        'cooldown_hours': rule.cooldown_hours,
        'last_triggered_at': None,
        'created_at': rule.created_at.isoformat(),
        'updated_at': rule.updated_at.isoformat()
    })
    return rule


@pytest.fixture
def app_client(mock_db):
    """Create test client with mocked dependencies"""
    with patch('src.main.check_db_connection', return_value=True):
        with patch('src.main.get_publisher', new=AsyncMock()):
            with patch('src.main.get_subscriber', new=AsyncMock()):
                with patch('src.main.get_db', return_value=mock_db):
                    from src.main import app
                    client = TestClient(app)
                    yield client


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, app_client):
        """Test health endpoint"""
        response = app_client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert data['service'] == 'alert-service'
        assert data['version'] == '16.0.0'

    def test_healthz_check(self, app_client):
        """Test healthz endpoint"""
        response = app_client.get('/healthz')
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert data['service'] == 'alert-service'

    def test_readiness_check(self, app_client):
        """Test readyz endpoint"""
        with patch('src.main.check_db_connection', return_value=True):
            response = app_client.get('/readyz')
            assert response.status_code == 200
            data = response.json()
            assert 'database' in data
            assert data['database'] is True


class TestAlertCreation:
    """Test alert creation endpoints"""

    def test_create_alert_success(self, app_client, mock_alert):
        """Test creating a new alert"""
        payload = {
            'field_id': 'field-123',
            'tenant_id': 'tenant-1',
            'type': 'ndvi_low',
            'severity': 'high',
            'title': 'Low NDVI Alert',
            'message': 'NDVI below threshold',
            'recommendations': ['Check irrigation']
        }

        with patch('src.main.create_alert_internal', new=AsyncMock(return_value=mock_alert.to_dict())):
            response = app_client.post(
                '/alerts',
                json=payload,
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 200
            data = response.json()
            assert data['field_id'] == 'field-123'
            assert data['type'] == 'ndvi_low'

    def test_create_alert_missing_tenant_header(self, app_client):
        """Test creating alert without tenant header"""
        payload = {
            'field_id': 'field-123',
            'type': 'ndvi_low',
            'severity': 'high',
            'title': 'Test',
            'message': 'Test'
        }

        response = app_client.post('/alerts', json=payload)
        assert response.status_code == 400

    def test_create_alert_validation_error(self, app_client):
        """Test validation errors"""
        payload = {
            'field_id': 'field-123',
            # Missing required fields
        }

        response = app_client.post(
            '/alerts',
            json=payload,
            headers={'X-Tenant-Id': 'tenant-1'}
        )
        assert response.status_code == 422

    def test_create_alert_tenant_mismatch(self, app_client):
        """Test tenant ID mismatch"""
        payload = {
            'field_id': 'field-123',
            'tenant_id': 'tenant-2',  # Different from header
            'type': 'ndvi_low',
            'severity': 'high',
            'title': 'Test',
            'message': 'Test'
        }

        response = app_client.post(
            '/alerts',
            json=payload,
            headers={'X-Tenant-Id': 'tenant-1'}
        )
        assert response.status_code == 403


class TestAlertRetrieval:
    """Test alert retrieval endpoints"""

    def test_get_alert_by_id(self, app_client, mock_alert, mock_db):
        """Test getting alert by ID"""
        with patch('src.main.get_alert', return_value=mock_alert):
            response = app_client.get(
                f'/alerts/{mock_alert.id}',
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 200
            data = response.json()
            assert data['id'] == str(mock_alert.id)

    def test_get_alert_not_found(self, app_client, mock_db):
        """Test getting non-existent alert"""
        with patch('src.main.get_alert', return_value=None):
            alert_id = str(uuid4())
            response = app_client.get(
                f'/alerts/{alert_id}',
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 404

    def test_get_alert_invalid_id(self, app_client):
        """Test getting alert with invalid ID format"""
        response = app_client.get(
            '/alerts/invalid-id',
            headers={'X-Tenant-Id': 'tenant-1'}
        )
        assert response.status_code == 400

    def test_get_alerts_by_field(self, app_client, mock_alert, mock_db):
        """Test getting alerts for a field"""
        with patch('src.main.get_alerts_by_field', return_value=([mock_alert], 1)):
            response = app_client.get(
                '/alerts/field/field-123',
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 200
            data = response.json()
            assert 'items' in data
            assert data['total'] == 1

    def test_get_alerts_by_field_with_filters(self, app_client, mock_alert, mock_db):
        """Test getting alerts with filters"""
        with patch('src.main.get_alerts_by_field', return_value=([mock_alert], 1)):
            response = app_client.get(
                '/alerts/field/field-123',
                params={
                    'status': 'active',
                    'severity': 'high',
                    'type': 'ndvi_low',
                    'skip': 0,
                    'limit': 10
                },
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 200

    def test_get_alerts_pagination(self, app_client, mock_alert, mock_db):
        """Test pagination in alerts retrieval"""
        with patch('src.main.get_alerts_by_field', return_value=([mock_alert], 100)):
            response = app_client.get(
                '/alerts/field/field-123',
                params={'skip': 10, 'limit': 20},
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 200
            data = response.json()
            assert data['skip'] == 10
            assert data['limit'] == 20
            assert data['has_more'] is True


class TestAlertActions:
    """Test alert action endpoints"""

    def test_acknowledge_alert(self, app_client, mock_alert, mock_db):
        """Test acknowledging an alert"""
        with patch('src.main.get_alert', return_value=mock_alert):
            with patch('src.main.update_alert_status', return_value=mock_alert):
                response = app_client.post(
                    f'/alerts/{mock_alert.id}/acknowledge',
                    params={'user_id': 'user-123'},
                    headers={'X-Tenant-Id': 'tenant-1'}
                )
                assert response.status_code == 200

    def test_acknowledge_alert_invalid_status(self, app_client, mock_alert, mock_db):
        """Test acknowledging already acknowledged alert"""
        mock_alert.status = 'acknowledged'

        with patch('src.main.get_alert', return_value=mock_alert):
            response = app_client.post(
                f'/alerts/{mock_alert.id}/acknowledge',
                params={'user_id': 'user-123'},
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 400

    def test_resolve_alert(self, app_client, mock_alert, mock_db):
        """Test resolving an alert"""
        with patch('src.main.get_alert', return_value=mock_alert):
            with patch('src.main.update_alert_status', return_value=mock_alert):
                response = app_client.post(
                    f'/alerts/{mock_alert.id}/resolve',
                    params={'user_id': 'user-123', 'note': 'Fixed irrigation'},
                    headers={'X-Tenant-Id': 'tenant-1'}
                )
                assert response.status_code == 200

    def test_resolve_alert_already_resolved(self, app_client, mock_alert, mock_db):
        """Test resolving already resolved alert"""
        mock_alert.status = 'resolved'

        with patch('src.main.get_alert', return_value=mock_alert):
            response = app_client.post(
                f'/alerts/{mock_alert.id}/resolve',
                params={'user_id': 'user-123'},
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 400

    def test_dismiss_alert(self, app_client, mock_alert, mock_db):
        """Test dismissing an alert"""
        with patch('src.main.get_alert', return_value=mock_alert):
            with patch('src.main.update_alert_status', return_value=mock_alert):
                response = app_client.post(
                    f'/alerts/{mock_alert.id}/dismiss',
                    params={'user_id': 'user-123'},
                    headers={'X-Tenant-Id': 'tenant-1'}
                )
                assert response.status_code == 200

    def test_dismiss_alert_already_dismissed(self, app_client, mock_alert, mock_db):
        """Test dismissing already dismissed alert"""
        mock_alert.status = 'dismissed'

        with patch('src.main.get_alert', return_value=mock_alert):
            response = app_client.post(
                f'/alerts/{mock_alert.id}/dismiss',
                params={'user_id': 'user-123'},
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 400


class TestAlertUpdate:
    """Test alert update endpoints"""

    def test_update_alert_status(self, app_client, mock_alert, mock_db):
        """Test updating alert status"""
        payload = {
            'status': 'acknowledged',
            'acknowledged_by': 'user-123'
        }

        with patch('src.main.get_alert', return_value=mock_alert):
            with patch('src.main.update_alert_status', return_value=mock_alert):
                response = app_client.patch(
                    f'/alerts/{mock_alert.id}',
                    json=payload,
                    headers={'X-Tenant-Id': 'tenant-1'}
                )
                assert response.status_code == 200

    def test_update_alert_not_found(self, app_client, mock_db):
        """Test updating non-existent alert"""
        payload = {'status': 'acknowledged'}

        with patch('src.main.get_alert', return_value=None):
            alert_id = str(uuid4())
            response = app_client.patch(
                f'/alerts/{alert_id}',
                json=payload,
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 404


class TestAlertDeletion:
    """Test alert deletion endpoints"""

    def test_delete_alert(self, app_client, mock_alert, mock_db):
        """Test deleting an alert"""
        with patch('src.main.get_alert', return_value=mock_alert):
            with patch('src.main.delete_alert', return_value=True):
                response = app_client.delete(
                    f'/alerts/{mock_alert.id}',
                    headers={'X-Tenant-Id': 'tenant-1'}
                )
                assert response.status_code == 200
                data = response.json()
                assert data['status'] == 'deleted'

    def test_delete_alert_not_found(self, app_client, mock_db):
        """Test deleting non-existent alert"""
        with patch('src.main.get_alert', return_value=None):
            alert_id = str(uuid4())
            response = app_client.delete(
                f'/alerts/{alert_id}',
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 404


class TestAlertRules:
    """Test alert rules endpoints"""

    def test_create_alert_rule(self, app_client, mock_alert_rule, mock_db):
        """Test creating an alert rule"""
        payload = {
            'field_id': 'field-123',
            'tenant_id': 'tenant-1',
            'name': 'Low Moisture Rule',
            'enabled': True,
            'condition': {
                'metric': 'soil_moisture',
                'operator': 'lt',
                'value': 20
            },
            'alert_config': {
                'type': 'irrigation',
                'severity': 'high',
                'title': 'Low Moisture'
            },
            'cooldown_hours': 24
        }

        with patch('src.main.create_alert_rule', return_value=mock_alert_rule):
            response = app_client.post('/alerts/rules', json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data['field_id'] == 'field-123'

    def test_get_alert_rules(self, app_client, mock_alert_rule, mock_db):
        """Test getting alert rules"""
        with patch('src.main.get_alert_rules_by_field', return_value=[mock_alert_rule]):
            response = app_client.get(
                '/alerts/rules',
                params={'field_id': 'field-123'}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_get_alert_rules_filtered(self, app_client, mock_alert_rule, mock_db):
        """Test getting filtered alert rules"""
        mock_alert_rule.enabled = True

        with patch('src.main.get_alert_rules_by_field', return_value=[mock_alert_rule]):
            response = app_client.get(
                '/alerts/rules',
                params={'field_id': 'field-123', 'enabled': True}
            )
            assert response.status_code == 200

    def test_delete_alert_rule(self, app_client, mock_alert_rule, mock_db):
        """Test deleting an alert rule"""
        with patch('src.main.delete_alert_rule', return_value=True):
            response = app_client.delete(f'/alerts/rules/{mock_alert_rule.id}')
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'deleted'

    def test_delete_alert_rule_not_found(self, app_client, mock_db):
        """Test deleting non-existent rule"""
        with patch('src.main.delete_alert_rule', return_value=False):
            rule_id = str(uuid4())
            response = app_client.delete(f'/alerts/rules/{rule_id}')
            assert response.status_code == 404


class TestAlertStatistics:
    """Test alert statistics endpoints"""

    def test_get_alert_stats(self, app_client, mock_db):
        """Test getting alert statistics"""
        mock_stats = {
            'total_alerts': 100,
            'active_alerts': 25,
            'by_type': {'ndvi_low': 30, 'weather': 20},
            'by_severity': {'high': 40, 'medium': 35},
            'by_status': {'active': 25, 'resolved': 60},
            'acknowledged_count': 15,
            'resolved_count': 60,
            'average_resolution_hours': 4.5
        }

        with patch('src.main.get_alert_statistics', return_value=mock_stats):
            response = app_client.get(
                '/alerts/stats',
                params={'period': '30d'},
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 200
            data = response.json()
            assert data['total_alerts'] == 100
            assert data['active_alerts'] == 25

    def test_get_alert_stats_by_field(self, app_client, mock_db):
        """Test getting stats filtered by field"""
        mock_stats = {
            'total_alerts': 10,
            'active_alerts': 2,
            'by_type': {'ndvi_low': 8},
            'by_severity': {'high': 5},
            'by_status': {'active': 2},
            'acknowledged_count': 3,
            'resolved_count': 5,
            'average_resolution_hours': 3.0
        }

        with patch('src.main.get_alert_statistics', return_value=mock_stats):
            response = app_client.get(
                '/alerts/stats',
                params={'field_id': 'field-123', 'period': '7d'},
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            assert response.status_code == 200


class TestEventHandlers:
    """Test external event handlers"""

    @pytest.mark.asyncio
    async def test_handle_ndvi_anomaly(self):
        """Test handling NDVI anomaly event"""
        from src.main import handle_ndvi_anomaly

        event_data = {
            'event_id': 'evt-123',
            'field_id': 'field-123',
            'tenant_id': 'tenant-1',
            'severity': 'high',
            'anomaly_type': 'significant_drop',
            'current_ndvi': 0.15,
            'correlation_id': str(uuid4())
        }

        with patch('src.main.create_alert_internal', new=AsyncMock()):
            await handle_ndvi_anomaly(event_data)

    @pytest.mark.asyncio
    async def test_handle_weather_alert(self):
        """Test handling weather alert event"""
        from src.main import handle_weather_alert

        event_data = {
            'event_id': 'evt-456',
            'field_id': 'field-123',
            'tenant_id': 'tenant-1',
            'severity': 'severe',
            'title': 'Storm Warning',
            'title_en': 'Storm Warning',
            'message': 'Heavy rain expected',
            'message_en': 'Heavy rain expected',
            'recommendations': ['Secure equipment'],
            'recommendations_en': ['Secure equipment']
        }

        with patch('src.main.create_alert_internal', new=AsyncMock()):
            await handle_weather_alert(event_data)

    @pytest.mark.asyncio
    async def test_handle_iot_threshold(self):
        """Test handling IoT threshold event"""
        from src.main import handle_iot_threshold

        event_data = {
            'event_id': 'evt-789',
            'field_id': 'field-123',
            'tenant_id': 'tenant-1',
            'metric': 'soil_moisture',
            'value': 15,
            'threshold': 25
        }

        with patch('src.main.create_alert_internal', new=AsyncMock()):
            await handle_iot_threshold(event_data)


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_uuid_format(self, app_client):
        """Test handling invalid UUID format"""
        response = app_client.get(
            '/alerts/not-a-uuid',
            headers={'X-Tenant-Id': 'tenant-1'}
        )
        assert response.status_code == 400

    def test_database_error(self, app_client, mock_db):
        """Test handling database errors"""
        with patch('src.main.get_alert', side_effect=Exception('DB Error')):
            alert_id = str(uuid4())
            response = app_client.get(
                f'/alerts/{alert_id}',
                headers={'X-Tenant-Id': 'tenant-1'}
            )
            # Should handle error gracefully
            assert response.status_code in [500, 404]

    def test_validation_errors(self, app_client):
        """Test request validation errors"""
        invalid_payload = {
            'field_id': 'field-123',
            'type': 'invalid_type',  # Invalid enum
            'severity': 'high'
        }

        response = app_client.post(
            '/alerts',
            json=invalid_payload,
            headers={'X-Tenant-Id': 'tenant-1'}
        )
        assert response.status_code == 422
