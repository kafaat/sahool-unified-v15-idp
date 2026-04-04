"""
Pytest Configuration and Shared Fixtures
Provides common test fixtures and configurations for all notification service tests
"""

import asyncio
import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src modules from other services to avoid cross-contamination in CI
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _mod in list(sys.modules):
    if not (_mod == "src" or _mod.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_service_root):
        del sys.modules[_mod]
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

# Set test environment before any service imports
os.environ["ENVIRONMENT"] = "test"
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_notification():
    """Create a mock notification object for testing"""
    notif = MagicMock()
    notif.id = uuid4()
    notif.user_id = "user-123"
    notif.tenant_id = "tenant-1"
    notif.title = "Test Notification"
    notif.title_ar = "إشعار تجريبي"
    notif.body = "Test body"
    notif.body_ar = "نص تجريبي"
    notif.type = "weather_alert"
    notif.priority = "high"
    notif.channel = "push"
    notif.status = "pending"
    notif.created_at = datetime.utcnow()
    notif.expires_at = datetime.utcnow() + timedelta(hours=24)
    notif.data = {"type_ar": "تنبيه طقس", "priority_ar": "عالية"}
    notif.is_read = False
    notif.is_expired = False
    notif.action_url = None
    return notif


@pytest.fixture
def mock_farmer_profile():
    """Create a mock farmer profile"""
    return {
        "farmer_id": "farmer-123",
        "name": "Ahmed Ali",
        "name_ar": "أحمد علي",
        "governorate": "sanaa",
        "crops": ["tomato", "coffee"],
        "phone": "+967771234567",
        "email": "ahmed@example.com",
        "fcm_token": "mock-fcm-token",
        "language": "ar",
    }


@pytest.fixture
def mock_notification_preference():
    """Create a mock notification preference"""
    pref = MagicMock()
    pref.id = uuid4()
    pref.user_id = "user-123"
    pref.channel = "push"
    pref.enabled = True
    pref.quiet_hours_start = None
    pref.quiet_hours_end = None
    pref.min_priority = "low"
    pref.notification_types = {
        "weather_alerts": True,
        "pest_alerts": True,
        "irrigation_reminders": True,
        "crop_health_alerts": True,
        "market_prices": True,
    }
    return pref


@pytest.fixture
def mock_notification_log():
    """Create a mock notification log entry"""
    log = MagicMock()
    log.id = uuid4()
    log.notification_id = uuid4()
    log.channel = "sms"
    log.status = "sent"
    log.provider_message_id = "SM123456"
    log.sent_at = datetime.utcnow()
    log.error_message = None
    return log


@pytest.fixture
def mock_sms_client():
    """Create a mock SMS client"""
    client = MagicMock()
    client._initialized = True
    client.send_sms = AsyncMock(return_value="SM123456")
    client.send_bulk_sms = AsyncMock(return_value={"success_count": 3, "failure_count": 0, "results": []})
    client.send_sms_with_retry = AsyncMock(return_value="SM123456")
    client.validate_phone_number = MagicMock(return_value=True)
    return client


@pytest.fixture
def mock_email_client():
    """Create a mock Email client"""
    client = MagicMock()
    client._initialized = True
    client.send_email = AsyncMock(return_value="msg-123456")
    client.send_bulk_email = AsyncMock(return_value={"success_count": 3, "failure_count": 0, "results": []})
    client.send_email_with_retry = AsyncMock(return_value="msg-123456")
    return client


@pytest.fixture
def mock_firebase_client():
    """Create a mock Firebase client"""
    client = MagicMock()
    client._initialized = True
    client.send_notification = MagicMock(return_value="fcm-msg-123")
    client.send_to_topic = MagicMock(return_value="fcm-topic-msg-123")
    client.send_multicast = MagicMock(return_value={"success_count": 3, "failure_count": 0, "responses": []})
    client.subscribe_to_topic = MagicMock(return_value={"success_count": 1, "failure_count": 0})
    client.send_with_retry = MagicMock(return_value="fcm-msg-retry-123")
    return client


def _mock_user():
    """Create a mock authenticated user for testing"""
    user = MagicMock()
    user.id = "test-user-123"
    user.tenant_id = "11111111-1111-1111-1111-111111111111"
    user.email = "test@sahool.app"
    user.role = "admin"
    user.is_active = True
    return user


@pytest.fixture
async def async_client():
    """Create async test client for FastAPI"""
    try:
        import httpx
        from src.main import app

        # Override auth dependency to return a mock user.
        # Auth is mandatory (User, not User | None) on farmer endpoints.
        mock_user = _mock_user()
        mock_user.id = "farmer-123"  # Match test farmer_id values
        try:
            from shared.auth.dependencies import get_current_user

            app.dependency_overrides[get_current_user] = lambda: mock_user
        except BaseException as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
                raise
            pass

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-Tenant-ID": "11111111-1111-1111-1111-111111111111"},
        ) as client:
            yield client

        app.dependency_overrides.clear()
    except BaseException as e:
        if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
            raise
        pytest.skip("httpx or src.main not available")


@pytest.fixture
def client():
    """Create sync test client for FastAPI"""
    try:
        from fastapi.testclient import TestClient
        from src.main import app

        # Override auth dependency to return a mock user.
        # Auth is mandatory (User, not User | None) on farmer endpoints.
        mock_user = _mock_user()
        mock_user.id = "farmer-123"  # Match test farmer_id values
        try:
            from shared.auth.dependencies import get_current_user

            app.dependency_overrides[get_current_user] = lambda: mock_user
        except BaseException as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
                raise
            pass

        client = TestClient(app, headers={"X-Tenant-ID": "11111111-1111-1111-1111-111111111111"})
        yield client

        app.dependency_overrides.clear()
    except BaseException as e:
        if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
            raise
        pytest.skip("fastapi.testclient or src.main not available")


@pytest.fixture
def mock_notification_repository():
    """Mock NotificationRepository for testing"""
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_user = AsyncMock()
    repo.get_broadcast_notifications = AsyncMock()
    repo.mark_as_read = AsyncMock()
    repo.update_status = AsyncMock()
    repo.delete = AsyncMock()
    repo.get_unread_count = AsyncMock()
    return repo


@pytest.fixture
def mock_notification_preference_repository():
    """Mock NotificationPreferenceRepository for testing"""
    repo = MagicMock()
    repo.create_or_update = AsyncMock()
    repo.get_by_user = AsyncMock()
    repo.get_by_user_and_channel = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_notification_log_repository():
    """Mock NotificationLogRepository for testing"""
    repo = MagicMock()
    repo.create_log = AsyncMock()
    repo.get_logs_by_notification = AsyncMock()
    repo.get_failed_logs = AsyncMock()
    return repo


@pytest.fixture(autouse=True)
def reset_farmer_profiles():
    """Reset farmer profiles state before each test.
    FARMER_PROFILES was migrated to database-backed FarmerProfileRepository."""
    yield


@pytest.fixture
def sample_weather_alert_data():
    """Sample weather alert request data"""
    from datetime import date

    return {
        "governorates": ["sanaa", "ibb"],
        "alert_type": "frost",
        "severity": "high",
        "expected_date": (date.today() + timedelta(days=1)).isoformat(),
        "details": {"min_temperature": -2, "duration_hours": 6},
    }


@pytest.fixture
def sample_pest_alert_data():
    """Sample pest alert request data"""
    return {
        "governorate": "taiz",
        "pest_name": "Aphids",
        "pest_name_ar": "المن",
        "affected_crops": ["tomato", "potato"],
        "severity": "medium",
        "recommendations": ["Use organic pesticides"],
        "recommendations_ar": ["استخدم المبيدات العضوية"],
    }


@pytest.fixture
def sample_irrigation_reminder_data():
    """Sample irrigation reminder request data"""
    return {
        "farmer_id": "farmer-123",
        "field_id": "field-456",
        "field_name": "North Field",
        "crop": "tomato",
        "water_needed_mm": 25.5,
        "urgency": "high",
    }


@pytest.fixture
def sample_notification_request():
    """Sample notification creation request"""
    return {
        "type": "weather_alert",
        "priority": "high",
        "title": "Weather Alert",
        "title_ar": "تنبيه طقس",
        "body": "Frost expected tonight",
        "body_ar": "صقيع متوقع الليلة",
        "data": {"temperature": -2},
        "target_farmers": ["farmer-123"],
        "channels": ["push", "in_app"],
        "expires_in_hours": 24,
    }
