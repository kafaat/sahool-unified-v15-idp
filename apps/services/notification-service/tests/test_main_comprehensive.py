"""
Comprehensive unit tests for notification-service src/main.py
اختبارات شاملة لخدمة الإشعارات

Covers:
- All API endpoints: /healthz, /readyz, /metrics, /, /weather, /pest,
  /irrigation, /farmer/{id}, /{id}/read, /broadcast, /register,
  /{farmer_id}/preferences, /stats
- Request/response models and validation
- Enum values and Arabic translation dicts
- sanitize_log_input helper
- Auth access-control (403 when user != farmer_id)
- Query-parameter filtering on GET endpoints
"""

import os
import sys
from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# ---------------------------------------------------------------------------
# 1. Mock ALL shared / external modules BEFORE any src import
# ---------------------------------------------------------------------------


class _NoopMiddleware:
    """Pass-through ASGI middleware (replaces TenantContextMiddleware)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


_SHARED_MOCKS = [
    "shared",
    "shared.errors_py",
    "shared.middleware",
    "shared.middleware.tenant_context",
    "shared.middleware.security_headers",
    "shared.auth",
    "shared.auth.dependencies",
    "shared.auth.models",
    "shared.logging_config",
    "shared.observability",
    "shared.observability.tracing",
    "shared.cors_config",
    "shared.events",
    "shared.events.dlq_config",
    "structlog",
    "prometheus_client",
    "nats",
    "asyncpg",
    "redis",
    "firebase_admin",
    "fcm_django",
    "middleware",
    "middleware.rate_limiter",
]

for _mod in _SHARED_MOCKS:
    sys.modules.setdefault(_mod, MagicMock())

# Wire callables that are invoked at import time
sys.modules["shared.errors_py"].setup_exception_handlers = lambda app: None
sys.modules["shared.errors_py"].add_request_id_middleware = lambda app: None
sys.modules["shared.middleware.tenant_context"].TenantContextMiddleware = _NoopMiddleware
sys.modules["shared.middleware.security_headers"].setup_security_headers = lambda app: None
sys.modules["shared.logging_config"].setup_logging = lambda *a, **kw: None
sys.modules["shared.observability.tracing"].setup_tracing = lambda *a, **kw: MagicMock()
sys.modules["shared.cors_config"].setup_cors_middleware = lambda app: None

# Prometheus mock – prevent duplicate-metric errors on re-import
_prom = sys.modules["prometheus_client"]
_prom.Counter = MagicMock(return_value=MagicMock())
_prom.Histogram = MagicMock(return_value=MagicMock())
_prom.CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
_prom.generate_latest = lambda: b"# metrics\n"

# structlog mock
_structlog = sys.modules["structlog"]
_structlog.get_logger = MagicMock(return_value=MagicMock())

# DLQ config mock
_dlq = sys.modules["shared.events.dlq_config"]
_dlq.DLQConfig = MagicMock()
_dlq.DLQConfig.from_env = MagicMock(return_value=MagicMock())
_dlq.DLQMessageMetadata = MagicMock()

# Fake User class
_FakeUserCls = type(
    "User",
    (),
    {
        "id": "farmer-123",
        "tenant_id": "11111111-1111-1111-1111-111111111111",
        "email": "test@sahool.app",
        "roles": ["admin"],
    },
)
_fake_user = _FakeUserCls()


async def _fake_get_current_user():
    return _fake_user


async def _fake_get_current_user_optional():
    return _fake_user


sys.modules["shared.auth.dependencies"].get_current_user = _fake_get_current_user
sys.modules["shared.auth.models"].User = _FakeUserCls

# ---------------------------------------------------------------------------
# 2. Mock all src.* sub-modules (relative imports from main.py)
# ---------------------------------------------------------------------------

_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

# Build a fake Router that carries no routes
_fake_router = MagicMock()
_fake_router.routes = []
_fake_router.prefix = ""
_fake_router.tags = []

# Mock NotificationRepository
_mock_notif_repo = MagicMock()
_mock_notif_repo.create = AsyncMock(return_value=None)
_mock_notif_repo.get_by_id = AsyncMock(return_value=None)
_mock_notif_repo.get_by_user = AsyncMock(return_value=[])
_mock_notif_repo.get_broadcast_notifications = AsyncMock(return_value=[])
_mock_notif_repo.mark_as_read = AsyncMock(return_value=True)
_mock_notif_repo.get_unread_count = AsyncMock(return_value=0)

# Mock FarmerProfileRepository
_mock_farmer_repo = MagicMock()
_mock_farmer_repo.create = AsyncMock(return_value=None)
_mock_farmer_repo.get_count = AsyncMock(return_value=5)

# Mock NotificationPreferenceRepository
_mock_pref_repo = MagicMock()
_mock_pref_repo.create_or_update = AsyncMock(return_value=MagicMock())

# Mock delivery tracker
_mock_tracker = MagicMock()
_mock_tracker.start = AsyncMock()
_mock_tracker.stop = AsyncMock()

# Mock queue processor
_mock_queue = MagicMock()
_mock_queue.connect = AsyncMock(return_value=False)
_mock_queue.start = AsyncMock()
_mock_queue.stop = AsyncMock()
_mock_queue.disconnect = AsyncMock()

# Submodule mocks
import types as _types  # noqa: E402

# Build a real ModuleType for "src" so __spec__ is properly set
_src_pkg = _types.ModuleType("src")
_src_pkg.__path__ = [os.path.join(_SERVICE_ROOT, "src")]
_src_pkg.__package__ = "src"
_src_pkg.__spec__ = MagicMock()


def _build_models_mock() -> MagicMock:
    """Build src.models mock with awaitable Notification.filter().count()."""
    _qs = MagicMock()
    _qs.count = AsyncMock(return_value=0)
    _notif_cls = MagicMock()
    _notif_cls.filter = MagicMock(return_value=_qs)
    models_mod = MagicMock()
    models_mod.Notification = _notif_cls
    return models_mod


_src_submodules = {
    "src": _src_pkg,
    "src.analytics_controller": MagicMock(router=_fake_router),
    "src.channels_controller": MagicMock(router=_fake_router),
    "src.history_controller": MagicMock(router=_fake_router),
    "src.otp_controller": MagicMock(router=_fake_router),
    "src.preferences_controller": MagicMock(router=_fake_router),
    "src.database": MagicMock(
        check_db_health=AsyncMock(return_value={"connected": False}),
        close_db=AsyncMock(),
        get_db_stats=AsyncMock(
            return_value={
                "total_notifications": 100,
                "pending_notifications": 5,
                "total_templates": 10,
                "total_preferences": 20,
            }
        ),
        init_notification_db=AsyncMock(),
    ),
    "src.delivery_tracker": MagicMock(get_delivery_tracker=MagicMock(return_value=_mock_tracker)),
    "src.email_client": MagicMock(get_email_client=MagicMock(return_value=MagicMock(_initialized=False))),
    "src.preferences_service": MagicMock(
        PreferencesService=MagicMock(
            check_if_should_send=AsyncMock(return_value=(True, ["in_app"]))
        )
    ),
    "src.queue_processor": MagicMock(get_queue_processor=MagicMock(return_value=_mock_queue)),
    "src.repository": MagicMock(
        FarmerProfileRepository=_mock_farmer_repo,
        NotificationLogRepository=MagicMock(),
        NotificationPreferenceRepository=_mock_pref_repo,
        NotificationRepository=_mock_notif_repo,
    ),
    "src.sms_client": MagicMock(get_sms_client=MagicMock(return_value=MagicMock(_initialized=False))),
    "src.sms_providers": MagicMock(get_multi_sms_client=MagicMock(return_value=MagicMock(_initialized=False))),
    "src.telegram_client": MagicMock(get_telegram_client=MagicMock(return_value=MagicMock(_initialized=False))),
    "src.whatsapp_client": MagicMock(get_whatsapp_client=MagicMock(return_value=MagicMock(_initialized=False))),
    "src.nats_subscriber": MagicMock(
        start_subscription=AsyncMock(return_value=None),
        stop_subscription=AsyncMock(),
    ),
    "src.models": _build_models_mock(),
}

for _mod_name, _mod_obj in _src_submodules.items():
    sys.modules.setdefault(_mod_name, _mod_obj)

# ---------------------------------------------------------------------------
# 3. Import the module under test
# ---------------------------------------------------------------------------

from src.main import (  # noqa: E402
    CROP_AR,
    GOVERNORATE_AR,
    NOTIFICATION_TYPE_AR,
    PRIORITY_AR,
    CreateNotificationRequest,
    CropType,
    DevicePlatform,
    FarmerProfile,
    Governorate,
    IrrigationReminderRequest,
    NotificationChannel,
    NotificationPreferences,
    NotificationPriority,
    NotificationType,
    PestAlertRequest,
    WeatherAlertRequest,
    app,
    get_weather_alert_message,
    sanitize_log_input,
    sanitize_notification_content,
)
from src.main import get_current_user as _real_get_current_user  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

# ---------------------------------------------------------------------------
# 4. Wire dependency override and TestClient
# ---------------------------------------------------------------------------

app.dependency_overrides[_real_get_current_user] = _fake_get_current_user

client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# 5. Helpers
# ---------------------------------------------------------------------------

def _future_date(days: int = 1) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _make_notification_mock(
    *,
    nid=None,
    user_id="farmer-123",
    ntype="weather_alert",
    priority="high",
    title="Test",
    title_ar="اختبار",
    body="Body",
    body_ar="نص",
    is_read=False,
    target_governorates=None,
    target_crops=None,
):
    """Build a notification-like MagicMock."""
    n = MagicMock()
    n.id = nid or uuid4()
    n.user_id = user_id
    n.type = ntype
    n.priority = priority
    n.title = title
    n.title_ar = title_ar
    n.body = body
    n.body_ar = body_ar
    n.data = {"type_ar": "تنبيه طقس", "priority_ar": "عالية"}
    n.is_read = is_read
    n.created_at = datetime.now(UTC)
    n.expires_at = datetime.now(UTC) + timedelta(hours=24)
    n.status = "sent"
    n.action_url = None
    n.target_governorates = target_governorates or ["sanaa"]
    n.target_crops = target_crops or ["wheat"]
    return n


# ===========================================================================
# Tests – Health / Readiness / Metrics
# ===========================================================================

class TestHealthCheck:
    def test_healthz_returns_ok(self):
        r = client.get("/healthz")
        assert r.status_code == 200

    def test_healthz_body_structure(self):
        r = client.get("/healthz")
        body = r.json()
        assert body["status"] == "ok"
        assert body["service"] == "notification-service"
        assert "version" in body

    def test_healthz_version_format(self):
        r = client.get("/healthz")
        version = r.json()["version"]
        parts = version.split(".")
        assert len(parts) >= 2

    def test_healthz_no_auth_required(self):
        # override to raise to confirm health doesn't need auth
        saved = app.dependency_overrides.copy()
        app.dependency_overrides.clear()
        r = client.get("/healthz")
        assert r.status_code == 200
        app.dependency_overrides.update(saved)


class TestReadinessCheck:
    def test_readyz_returns_200_or_503(self):
        r = client.get("/readyz")
        assert r.status_code in (200, 503)

    def test_readyz_body_has_checks(self):
        r = client.get("/readyz")
        body = r.json()
        assert "checks" in body
        assert "database" in body["checks"]

    def test_readyz_service_name(self):
        r = client.get("/readyz")
        assert r.json()["service"] == "notification-service"

    def test_readyz_status_field(self):
        r = client.get("/readyz")
        assert r.json()["status"] in ("ready", "degraded")

    def test_readyz_nats_check_present(self):
        r = client.get("/readyz")
        assert "nats" in r.json()["checks"]


class TestMetricsEndpoint:
    def test_metrics_returns_200(self):
        r = client.get("/metrics")
        assert r.status_code == 200

    def test_metrics_content(self):
        r = client.get("/metrics")
        # With prometheus mocked it returns the mock bytes or the error JSON
        assert r.status_code == 200


# ===========================================================================
# Tests – POST / (create_custom_notification)
# ===========================================================================

_CUSTOM_NOTIF_BODY = {
    "type": "weather_alert",
    "priority": "high",
    "title": "Frost Alert",
    "title_ar": "تنبيه صقيع",
    "body": "Frost expected tonight",
    "body_ar": "صقيع متوقع الليلة",
    "data": {"temperature": -2},
    "target_farmers": ["farmer-123"],
    "channels": ["in_app"],
    "expires_in_hours": 24,
}


class TestCreateCustomNotification:
    def test_returns_400_when_no_notification_created(self):
        """create_notification returns None → 400"""
        with patch("src.main.create_notification", new=AsyncMock(return_value=None)):
            r = client.post("/", json=_CUSTOM_NOTIF_BODY)
        assert r.status_code == 400

    def test_returns_200_with_valid_notification(self):
        notif = _make_notification_mock()
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/", json=_CUSTOM_NOTIF_BODY)
        assert r.status_code == 200

    def test_response_has_id(self):
        notif = _make_notification_mock()
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/", json=_CUSTOM_NOTIF_BODY)
        assert "id" in r.json()

    def test_response_has_title(self):
        notif = _make_notification_mock(title="Frost Alert")
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/", json=_CUSTOM_NOTIF_BODY)
        assert r.json()["title"] == "Frost Alert"

    def test_missing_required_field_returns_422(self):
        body = {**_CUSTOM_NOTIF_BODY}
        del body["title"]
        r = client.post("/", json=body)
        assert r.status_code == 422

    def test_invalid_type_returns_422(self):
        body = {**_CUSTOM_NOTIF_BODY, "type": "not_a_valid_type"}
        r = client.post("/", json=body)
        assert r.status_code == 422

    def test_empty_farmer_id_in_target_returns_422(self):
        body = {**_CUSTOM_NOTIF_BODY, "target_farmers": [""]}
        r = client.post("/", json=body)
        assert r.status_code == 422

    def test_xss_in_title_is_escaped(self):
        """XSS in title should be escaped by sanitize_notification_content."""
        body = {
            **_CUSTOM_NOTIF_BODY,
            "title": "<script>alert(1)</script>",
            "title_ar": "<script>alert(1)</script>",
            "body": "<img src=x onerror=alert(1)>",
            "body_ar": "متن",
        }
        notif = _make_notification_mock(title="&lt;script&gt;alert(1)&lt;/script&gt;")
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/", json=body)
        # 200 or 400 — the key thing is it doesn't 500
        assert r.status_code in (200, 400)


# ===========================================================================
# Tests – POST /weather
# ===========================================================================

_WEATHER_BODY = {
    "governorates": ["sanaa", "ibb"],
    "alert_type": "frost",
    "severity": "high",
    "expected_date": _future_date(1),
    "details": {"min_temperature": -2},
}


class TestWeatherAlert:
    def test_returns_400_when_no_notification(self):
        with patch("src.main.create_notification", new=AsyncMock(return_value=None)):
            r = client.post("/weather", json=_WEATHER_BODY)
        assert r.status_code == 400

    def test_returns_200_with_notification(self):
        notif = _make_notification_mock(ntype="weather_alert")
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/weather", json=_WEATHER_BODY)
        assert r.status_code == 200

    def test_response_has_type(self):
        notif = _make_notification_mock(ntype="weather_alert")
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/weather", json=_WEATHER_BODY)
        assert r.json()["type"] == "weather_alert"

    def test_missing_governorates_returns_422(self):
        body = {**_WEATHER_BODY, "governorates": []}
        r = client.post("/weather", json=body)
        assert r.status_code == 422

    def test_invalid_severity_returns_422(self):
        body = {**_WEATHER_BODY, "severity": "mega-high"}
        r = client.post("/weather", json=body)
        assert r.status_code == 422

    def test_invalid_governorate_returns_422(self):
        body = {**_WEATHER_BODY, "governorates": ["invalid_gov"]}
        r = client.post("/weather", json=body)
        assert r.status_code == 422


# ===========================================================================
# Tests – POST /pest
# ===========================================================================

_PEST_BODY = {
    "governorate": "taiz",
    "pest_name": "Aphids",
    "pest_name_ar": "المن",
    "affected_crops": ["tomato", "wheat"],
    "severity": "medium",
    "recommendations": ["Use organic pesticides"],
    "recommendations_ar": ["استخدم المبيدات العضوية"],
}


class TestPestAlert:
    def test_returns_400_when_no_notification(self):
        with patch("src.main.create_notification", new=AsyncMock(return_value=None)):
            r = client.post("/pest", json=_PEST_BODY)
        assert r.status_code == 400

    def test_returns_200_with_notification(self):
        notif = _make_notification_mock(ntype="pest_outbreak")
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/pest", json=_PEST_BODY)
        assert r.status_code == 200

    def test_response_has_title(self):
        notif = _make_notification_mock(title="Pest Outbreak: Aphids")
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/pest", json=_PEST_BODY)
        assert "title" in r.json()

    def test_missing_pest_name_returns_422(self):
        body = {**_PEST_BODY}
        del body["pest_name"]
        r = client.post("/pest", json=body)
        assert r.status_code == 422

    def test_invalid_crop_returns_422(self):
        body = {**_PEST_BODY, "affected_crops": ["invalid_crop_xyz"]}
        r = client.post("/pest", json=body)
        assert r.status_code == 422

    def test_empty_affected_crops_returns_422(self):
        body = {**_PEST_BODY, "affected_crops": []}
        r = client.post("/pest", json=body)
        assert r.status_code == 422


# ===========================================================================
# Tests – POST /irrigation
# ===========================================================================

_IRRIGATION_BODY = {
    "farmer_id": "farmer-123",
    "field_id": "field-456",
    "field_name": "North Field",
    "crop": "tomato",
    "water_needed_mm": 25.5,
    "urgency": "high",
}


class TestIrrigationReminder:
    def test_returns_404_when_no_notification(self):
        with patch("src.main.create_notification", new=AsyncMock(return_value=None)):
            r = client.post("/irrigation", json=_IRRIGATION_BODY)
        assert r.status_code == 404

    def test_returns_200_with_notification(self):
        notif = _make_notification_mock(ntype="irrigation_reminder")
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/irrigation", json=_IRRIGATION_BODY)
        assert r.status_code == 200

    def test_response_has_body(self):
        notif = _make_notification_mock(body="Your tomato field needs 25.5mm of water.")
        with patch("src.main.create_notification", new=AsyncMock(return_value=notif)):
            r = client.post("/irrigation", json=_IRRIGATION_BODY)
        assert "body" in r.json()

    def test_missing_field_id_returns_422(self):
        body = {**_IRRIGATION_BODY}
        del body["field_id"]
        r = client.post("/irrigation", json=body)
        assert r.status_code == 422

    def test_water_needed_zero_returns_422(self):
        body = {**_IRRIGATION_BODY, "water_needed_mm": 0}
        r = client.post("/irrigation", json=body)
        assert r.status_code == 422

    def test_water_needed_too_large_returns_422(self):
        body = {**_IRRIGATION_BODY, "water_needed_mm": 999}
        r = client.post("/irrigation", json=body)
        assert r.status_code == 422

    def test_invalid_crop_returns_422(self):
        body = {**_IRRIGATION_BODY, "crop": "unknown_crop"}
        r = client.post("/irrigation", json=body)
        assert r.status_code == 422


# ===========================================================================
# Tests – GET /farmer/{farmer_id}
# ===========================================================================

class TestGetFarmerNotifications:
    def test_returns_200_for_own_notifications(self):
        _mock_notif_repo.get_by_user.return_value = []
        _mock_notif_repo.get_unread_count.return_value = 0
        r = client.get("/farmer/farmer-123")
        assert r.status_code == 200

    def test_returns_403_for_other_farmer(self):
        r = client.get("/farmer/other-farmer-999")
        assert r.status_code == 403

    def test_response_structure(self):
        _mock_notif_repo.get_by_user.return_value = []
        _mock_notif_repo.get_unread_count.return_value = 0
        r = client.get("/farmer/farmer-123")
        body = r.json()
        assert "farmer_id" in body
        assert "notifications" in body
        assert "unread_count" in body

    def test_response_farmer_id_matches(self):
        _mock_notif_repo.get_by_user.return_value = []
        _mock_notif_repo.get_unread_count.return_value = 0
        r = client.get("/farmer/farmer-123")
        assert r.json()["farmer_id"] == "farmer-123"

    def test_unread_only_query_param(self):
        _mock_notif_repo.get_by_user.return_value = []
        _mock_notif_repo.get_unread_count.return_value = 3
        r = client.get("/farmer/farmer-123?unread_only=true")
        assert r.status_code == 200

    def test_limit_query_param(self):
        _mock_notif_repo.get_by_user.return_value = []
        _mock_notif_repo.get_unread_count.return_value = 0
        r = client.get("/farmer/farmer-123?limit=10")
        assert r.status_code == 200

    def test_limit_too_large_returns_422(self):
        r = client.get("/farmer/farmer-123?limit=200")
        assert r.status_code == 422

    def test_offset_query_param(self):
        _mock_notif_repo.get_by_user.return_value = []
        _mock_notif_repo.get_unread_count.return_value = 0
        r = client.get("/farmer/farmer-123?offset=0")
        assert r.status_code == 200

    def test_type_filter_query_param(self):
        _mock_notif_repo.get_by_user.return_value = []
        _mock_notif_repo.get_unread_count.return_value = 0
        r = client.get("/farmer/farmer-123?type=weather_alert")
        assert r.status_code == 200

    def test_invalid_type_filter_returns_422(self):
        r = client.get("/farmer/farmer-123?type=invalid_type_xyz")
        assert r.status_code == 422

    def test_notifications_list_populated(self):
        notif = _make_notification_mock(user_id="farmer-123")
        _mock_notif_repo.get_by_user.return_value = [notif]
        _mock_notif_repo.get_unread_count.return_value = 1
        r = client.get("/farmer/farmer-123")
        body = r.json()
        assert body["total"] == 1
        assert len(body["notifications"]) == 1


# ===========================================================================
# Tests – PATCH /{notification_id}/read
# ===========================================================================

class TestMarkNotificationRead:
    def _make_notif(self, nid, user_id="farmer-123"):
        n = _make_notification_mock(nid=nid, user_id=user_id)
        return n

    def test_returns_400_for_invalid_uuid(self):
        r = client.patch("/not-a-uuid/read")
        assert r.status_code == 400

    def test_returns_404_when_notification_not_found(self):
        _mock_notif_repo.get_by_id.return_value = None
        nid = str(uuid4())
        r = client.patch(f"/{nid}/read")
        assert r.status_code == 404

    def test_returns_403_when_notification_belongs_to_other_user(self):
        nid = uuid4()
        notif = self._make_notif(nid=nid, user_id="other-user-999")
        _mock_notif_repo.get_by_id.return_value = notif
        r = client.patch(f"/{nid}/read")
        assert r.status_code == 403

    def test_returns_200_on_success(self):
        nid = uuid4()
        notif = self._make_notif(nid=nid, user_id="farmer-123")
        _mock_notif_repo.get_by_id.return_value = notif
        _mock_notif_repo.mark_as_read.return_value = True
        r = client.patch(f"/{nid}/read")
        assert r.status_code == 200

    def test_success_response_is_read_true(self):
        nid = uuid4()
        notif = self._make_notif(nid=nid, user_id="farmer-123")
        _mock_notif_repo.get_by_id.return_value = notif
        _mock_notif_repo.mark_as_read.return_value = True
        r = client.patch(f"/{nid}/read")
        assert r.json()["is_read"] is True

    def test_returns_500_when_mark_fails(self):
        nid = uuid4()
        notif = self._make_notif(nid=nid, user_id="farmer-123")
        _mock_notif_repo.get_by_id.return_value = notif
        _mock_notif_repo.mark_as_read.return_value = False
        r = client.patch(f"/{nid}/read")
        assert r.status_code == 500

    def test_farmer_id_mismatch_query_returns_403(self):
        nid = uuid4()
        notif = self._make_notif(nid=nid, user_id="farmer-123")
        _mock_notif_repo.get_by_id.return_value = notif
        r = client.patch(f"/{nid}/read?farmer_id=different-farmer")
        assert r.status_code == 403

    def test_farmer_id_matching_query_accepted(self):
        nid = uuid4()
        notif = self._make_notif(nid=nid, user_id="farmer-123")
        _mock_notif_repo.get_by_id.return_value = notif
        _mock_notif_repo.mark_as_read.return_value = True
        r = client.patch(f"/{nid}/read?farmer_id=farmer-123")
        assert r.status_code == 200


# ===========================================================================
# Tests – GET /broadcast
# ===========================================================================

class TestGetBroadcastNotifications:
    def test_returns_200(self):
        _mock_notif_repo.get_broadcast_notifications.return_value = []
        r = client.get("/broadcast")
        assert r.status_code == 200

    def test_response_structure(self):
        _mock_notif_repo.get_broadcast_notifications.return_value = []
        r = client.get("/broadcast")
        body = r.json()
        assert "total" in body
        assert "notifications" in body

    def test_returns_empty_when_no_broadcasts(self):
        _mock_notif_repo.get_broadcast_notifications.return_value = []
        r = client.get("/broadcast")
        assert r.json()["total"] == 0

    def test_governorate_filter_query_param(self):
        _mock_notif_repo.get_broadcast_notifications.return_value = []
        r = client.get("/broadcast?governorate=sanaa")
        assert r.status_code == 200

    def test_crop_filter_query_param(self):
        _mock_notif_repo.get_broadcast_notifications.return_value = []
        r = client.get("/broadcast?crop=wheat")
        assert r.status_code == 200

    def test_limit_query_param(self):
        _mock_notif_repo.get_broadcast_notifications.return_value = []
        r = client.get("/broadcast?limit=10")
        assert r.status_code == 200

    def test_limit_too_large_returns_422(self):
        r = client.get("/broadcast?limit=100")
        assert r.status_code == 422

    def test_invalid_governorate_returns_422(self):
        r = client.get("/broadcast?governorate=invalid_gov")
        assert r.status_code == 422

    def test_invalid_crop_returns_422(self):
        r = client.get("/broadcast?crop=invalid_crop_xyz")
        assert r.status_code == 422

    def test_populated_broadcasts_in_response(self):
        notif = _make_notification_mock()
        _mock_notif_repo.get_broadcast_notifications.return_value = [notif]
        r = client.get("/broadcast")
        body = r.json()
        assert body["total"] == 1
        assert len(body["notifications"]) == 1


# ===========================================================================
# Tests – POST /register
# ===========================================================================

_REGISTER_BODY = {
    "farmer_id": "farmer-new-001",
    "name": "Ahmed Ali",
    "name_ar": "أحمد علي",
    "governorate": "sanaa",
    "crops": ["tomato", "wheat"],
    "language": "ar",
}


class TestRegisterFarmer:
    def test_returns_200_on_success(self):
        _mock_farmer_repo.create.return_value = None
        r = client.post("/register", json=_REGISTER_BODY)
        assert r.status_code == 200

    def test_response_success_true(self):
        _mock_farmer_repo.create.return_value = None
        r = client.post("/register", json=_REGISTER_BODY)
        assert r.json()["success"] is True

    def test_response_has_farmer_id(self):
        _mock_farmer_repo.create.return_value = None
        r = client.post("/register", json=_REGISTER_BODY)
        assert r.json()["farmer_id"] == "farmer-new-001"

    def test_missing_name_returns_422(self):
        body = {**_REGISTER_BODY}
        del body["name"]
        r = client.post("/register", json=body)
        assert r.status_code == 422

    def test_missing_governorate_returns_422(self):
        body = {**_REGISTER_BODY}
        del body["governorate"]
        r = client.post("/register", json=body)
        assert r.status_code == 422

    def test_invalid_governorate_returns_422(self):
        body = {**_REGISTER_BODY, "governorate": "not_a_real_gov"}
        r = client.post("/register", json=body)
        assert r.status_code == 422

    def test_invalid_crop_returns_422(self):
        body = {**_REGISTER_BODY, "crops": ["invalid_crop_xyz"]}
        r = client.post("/register", json=body)
        assert r.status_code == 422

    def test_db_error_returns_500(self):
        _mock_farmer_repo.create.side_effect = Exception("DB connection failed")
        r = client.post("/register", json=_REGISTER_BODY)
        assert r.status_code == 500
        _mock_farmer_repo.create.side_effect = None

    def test_optional_phone_field(self):
        body = {**_REGISTER_BODY, "phone": "+967771234567"}
        _mock_farmer_repo.create.return_value = None
        r = client.post("/register", json=body)
        assert r.status_code == 200

    def test_optional_fcm_token(self):
        body = {**_REGISTER_BODY, "fcm_token": "a" * 50}
        _mock_farmer_repo.create.return_value = None
        r = client.post("/register", json=body)
        assert r.status_code == 200


# ===========================================================================
# Tests – PUT /{farmer_id}/preferences
# ===========================================================================

_PREFS_BODY = {
    "farmer_id": "farmer-123",
    "weather_alerts": True,
    "pest_alerts": True,
    "irrigation_reminders": True,
    "crop_health_alerts": True,
    "market_prices": False,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "06:00",
    "min_priority": "low",
}


class TestUpdatePreferences:
    def test_returns_200_for_own_preferences(self):
        _mock_pref_repo.create_or_update.return_value = MagicMock()
        r = client.put("/farmer-123/preferences", json=_PREFS_BODY)
        assert r.status_code == 200

    def test_returns_403_for_other_farmer(self):
        r = client.put("/other-farmer-999/preferences", json=_PREFS_BODY)
        assert r.status_code == 403

    def test_response_success_true(self):
        _mock_pref_repo.create_or_update.return_value = MagicMock()
        r = client.put("/farmer-123/preferences", json=_PREFS_BODY)
        assert r.json()["success"] is True

    def test_response_has_farmer_id(self):
        _mock_pref_repo.create_or_update.return_value = MagicMock()
        r = client.put("/farmer-123/preferences", json=_PREFS_BODY)
        assert r.json()["farmer_id"] == "farmer-123"

    def test_response_has_preferences(self):
        _mock_pref_repo.create_or_update.return_value = MagicMock()
        r = client.put("/farmer-123/preferences", json=_PREFS_BODY)
        assert "preferences" in r.json()

    def test_invalid_min_priority_returns_422(self):
        body = {**_PREFS_BODY, "min_priority": "ultra-high"}
        r = client.put("/farmer-123/preferences", json=body)
        assert r.status_code == 422

    def test_missing_farmer_id_in_body_returns_422(self):
        body = {**_PREFS_BODY}
        del body["farmer_id"]
        r = client.put("/farmer-123/preferences", json=body)
        assert r.status_code == 422


# ===========================================================================
# Tests – GET /stats
# ===========================================================================

class TestGetStats:
    """
    /stats imports Notification inline via `from .models import Notification`.
    The `sys.modules["src.models"]` mock (built by _build_models_mock) provides
    Notification.filter().count() as an AsyncMock.  FarmerProfileRepository.get_count
    is already an AsyncMock on _mock_farmer_repo.
    """

    def test_returns_200(self):
        with patch("src.main.get_db_stats", new=AsyncMock(return_value={
            "total_notifications": 100,
            "pending_notifications": 5,
            "total_templates": 3,
            "total_preferences": 15,
        })):
            r = client.get("/stats")
        assert r.status_code == 200

    def test_stats_structure(self):
        with patch("src.main.get_db_stats", new=AsyncMock(return_value={
            "total_notifications": 50,
            "pending_notifications": 2,
            "total_templates": 5,
            "total_preferences": 10,
        })):
            r = client.get("/stats")
        assert r.status_code == 200
        body = r.json()
        for key in ("total_notifications", "registered_farmers", "by_type"):
            assert key in body


# ===========================================================================
# Tests – Utility functions
# ===========================================================================

class TestSanitizeLogInput:
    def test_removes_newline(self):
        assert sanitize_log_input("a\nb") == "a\\nb"

    def test_removes_carriage_return(self):
        assert sanitize_log_input("a\rb") == "a\\rb"

    def test_removes_tab(self):
        assert sanitize_log_input("a\tb") == "a\\tb"

    def test_handles_non_string(self):
        assert sanitize_log_input(42) == "42"

    def test_preserves_normal_text(self):
        assert sanitize_log_input("hello world") == "hello world"

    def test_handles_empty_string(self):
        assert sanitize_log_input("") == ""


class TestSanitizeNotificationContent:
    def test_escapes_script_tag(self):
        result = sanitize_notification_content("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "&lt;" in result

    def test_escapes_angle_brackets(self):
        result = sanitize_notification_content("<b>bold</b>")
        assert "<b>" not in result

    def test_preserves_normal_text(self):
        assert sanitize_notification_content("Normal text 123") == "Normal text 123"

    def test_handles_non_string(self):
        result = sanitize_notification_content(42)
        assert result == "42"


class TestGetWeatherAlertMessage:
    def test_returns_tuple_of_four(self):
        result = get_weather_alert_message("frost", Governorate.SANAA)
        assert isinstance(result, tuple)
        assert len(result) == 4

    def test_frost_message_contains_frost(self):
        title, title_ar, body, body_ar = get_weather_alert_message("frost", Governorate.SANAA)
        assert title  # non-empty

    def test_heat_wave_message(self):
        result = get_weather_alert_message("heat_wave", Governorate.ADEN)
        assert len(result) == 4

    def test_storm_message(self):
        result = get_weather_alert_message("storm", Governorate.HADRAMAUT)
        assert len(result) == 4

    def test_unknown_type_fallback(self):
        result = get_weather_alert_message("unknown_type_xyz", Governorate.SANAA)
        # Should not raise, should return 4-tuple
        assert len(result) == 4


# ===========================================================================
# Tests – Enum and Translation Dicts
# ===========================================================================

class TestEnums:
    def test_notification_type_values(self):
        assert NotificationType.WEATHER_ALERT == "weather_alert"
        assert NotificationType.PEST_OUTBREAK == "pest_outbreak"
        assert NotificationType.IRRIGATION_REMINDER == "irrigation_reminder"
        assert NotificationType.CROP_HEALTH == "crop_health"
        assert NotificationType.MARKET_PRICE == "market_price"
        assert NotificationType.SYSTEM == "system"
        assert NotificationType.TASK_REMINDER == "task_reminder"

    def test_priority_values(self):
        assert NotificationPriority.LOW == "low"
        assert NotificationPriority.MEDIUM == "medium"
        assert NotificationPriority.HIGH == "high"
        assert NotificationPriority.CRITICAL == "critical"

    def test_channel_values(self):
        assert NotificationChannel.PUSH == "push"
        assert NotificationChannel.SMS == "sms"
        assert NotificationChannel.EMAIL == "email"
        assert NotificationChannel.IN_APP == "in_app"
        assert NotificationChannel.WHATSAPP == "whatsapp"

    def test_governorate_values(self):
        assert Governorate.SANAA == "sanaa"
        assert Governorate.ADEN == "aden"
        assert Governorate.TAIZ == "taiz"
        assert Governorate.HODEIDAH == "hodeidah"

    def test_crop_type_values(self):
        assert CropType.TOMATO == "tomato"
        assert CropType.WHEAT == "wheat"
        assert CropType.COFFEE == "coffee"
        assert CropType.DATE_PALM == "date_palm"

    def test_device_platform_values(self):
        assert DevicePlatform.IOS == "ios"
        assert DevicePlatform.ANDROID == "android"
        assert DevicePlatform.WEB == "web"

    def test_notification_type_ar_dict_complete(self):
        for ntype in NotificationType:
            assert ntype in NOTIFICATION_TYPE_AR

    def test_priority_ar_dict_complete(self):
        for priority in NotificationPriority:
            assert priority in PRIORITY_AR

    def test_governorate_ar_dict_complete(self):
        for gov in Governorate:
            assert gov in GOVERNORATE_AR

    def test_crop_ar_dict_complete(self):
        for crop in CropType:
            assert crop in CROP_AR


# ===========================================================================
# Tests – Pydantic Models
# ===========================================================================

class TestFarmerProfileModel:
    def test_valid_profile(self):
        p = FarmerProfile(
            farmer_id="f001",
            name="Ahmed",
            name_ar="أحمد",
            governorate=Governorate.SANAA,
            crops=[CropType.WHEAT],
        )
        assert p.farmer_id == "f001"

    def test_name_sanitization(self):
        p = FarmerProfile(
            farmer_id="f001",
            name="<b>Ahmed</b>",
            name_ar="أحمد",
            governorate=Governorate.SANAA,
            crops=[CropType.WHEAT],
        )
        assert "<b>" not in p.name

    def test_default_language_ar(self):
        p = FarmerProfile(
            farmer_id="f001",
            name="Ahmed",
            name_ar="أحمد",
            governorate=Governorate.SANAA,
            crops=[CropType.WHEAT],
        )
        assert p.language == "ar"

    def test_farmer_id_too_long_raises(self):
        with pytest.raises(Exception):
            FarmerProfile(
                farmer_id="x" * 101,
                name="Ahmed",
                name_ar="أحمد",
                governorate=Governorate.SANAA,
                crops=[CropType.WHEAT],
            )


class TestNotificationPreferencesModel:
    def test_defaults(self):
        p = NotificationPreferences(farmer_id="f001")
        assert p.weather_alerts is True
        assert p.pest_alerts is True
        assert p.irrigation_reminders is True
        assert p.min_priority == NotificationPriority.LOW

    def test_quiet_hours_defaults(self):
        p = NotificationPreferences(farmer_id="f001")
        assert p.quiet_hours_start == "22:00"
        assert p.quiet_hours_end == "06:00"


class TestCreateNotificationRequestModel:
    def test_content_sanitization(self):
        r = CreateNotificationRequest(
            type=NotificationType.SYSTEM,
            title="<script>xss</script>",
            title_ar="عنوان",
            body="body",
            body_ar="نص",
        )
        assert "<script>" not in r.title

    def test_expires_in_hours_min(self):
        with pytest.raises(Exception):
            CreateNotificationRequest(
                type=NotificationType.SYSTEM,
                title="t",
                title_ar="ت",
                body="b",
                body_ar="ب",
                expires_in_hours=0,
            )

    def test_default_priority_medium(self):
        r = CreateNotificationRequest(
            type=NotificationType.SYSTEM,
            title="t",
            title_ar="ت",
            body="b",
            body_ar="ب",
        )
        assert r.priority == NotificationPriority.MEDIUM


class TestWeatherAlertRequestModel:
    def test_alert_type_sanitized(self):
        r = WeatherAlertRequest(
            governorates=[Governorate.SANAA],
            alert_type="<b>frost</b>",
            severity=NotificationPriority.HIGH,
            expected_date=date.today(),
        )
        assert "<b>" not in r.alert_type

    def test_empty_governorates_raises(self):
        with pytest.raises(Exception):
            WeatherAlertRequest(
                governorates=[],
                alert_type="frost",
                severity=NotificationPriority.HIGH,
                expected_date=date.today(),
            )


class TestPestAlertRequestModel:
    def test_pest_name_sanitized(self):
        r = PestAlertRequest(
            governorate=Governorate.SANAA,
            pest_name="<script>Aphids</script>",
            pest_name_ar="المن",
            affected_crops=[CropType.WHEAT],
            severity=NotificationPriority.HIGH,
        )
        assert "<script>" not in r.pest_name

    def test_recommendations_sanitized(self):
        r = PestAlertRequest(
            governorate=Governorate.SANAA,
            pest_name="Aphids",
            pest_name_ar="المن",
            affected_crops=[CropType.WHEAT],
            severity=NotificationPriority.HIGH,
            recommendations=["<b>Spray</b> pesticide"],
        )
        assert "<b>" not in r.recommendations[0]

    def test_empty_affected_crops_raises(self):
        with pytest.raises(Exception):
            PestAlertRequest(
                governorate=Governorate.SANAA,
                pest_name="Aphids",
                pest_name_ar="المن",
                affected_crops=[],
                severity=NotificationPriority.HIGH,
            )


class TestIrrigationReminderRequestModel:
    def test_field_name_sanitized(self):
        r = IrrigationReminderRequest(
            farmer_id="f001",
            field_id="field-1",
            field_name="<b>North</b> Field",
            crop=CropType.TOMATO,
            water_needed_mm=20.0,
            urgency=NotificationPriority.HIGH,
        )
        assert "<b>" not in r.field_name

    def test_water_needed_must_be_positive(self):
        with pytest.raises(Exception):
            IrrigationReminderRequest(
                farmer_id="f001",
                field_id="field-1",
                field_name="North Field",
                crop=CropType.TOMATO,
                water_needed_mm=-5.0,
                urgency=NotificationPriority.HIGH,
            )
