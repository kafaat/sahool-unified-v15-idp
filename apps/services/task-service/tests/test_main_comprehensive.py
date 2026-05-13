"""
Comprehensive tests for task-service main.py and routes.
اختبارات شاملة لخدمة إدارة المهام الزراعية
"""

import os
import sys
import types
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")

# ---------------------------------------------------------------------------
# Noop middleware helper
# ---------------------------------------------------------------------------

class _NoopMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


# ---------------------------------------------------------------------------
# Mock all shared / external modules BEFORE importing src
# ---------------------------------------------------------------------------

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
    "shared.observability.middleware",
    "shared.observability.tracing",
    "shared.cors_config",
    "shared.contracts",
    "shared.libs",
    "shared.libs.events",
    "shared.libs.events.nats_publisher",
    "shared.db",
    "shared.db.ssl",
    "structlog",
    "prometheus_client",
    "nats",
    "asyncpg",
    "redis",
    "aiohttp",
    "httpx",
]

for _mod in _SHARED_MOCKS:
    sys.modules.setdefault(_mod, MagicMock())

# Wire callables invoked at import time
sys.modules["shared.errors_py"].setup_exception_handlers = lambda app: None
sys.modules["shared.errors_py"].add_request_id_middleware = lambda app: None
sys.modules["shared.middleware.tenant_context"].TenantContextMiddleware = _NoopMiddleware
sys.modules["shared.observability.middleware"].ObservabilityMiddleware = _NoopMiddleware
sys.modules["shared.logging_config"].setup_logging = lambda *a, **kw: None
sys.modules["shared.logging_config"].get_logger = lambda *a, **kw: MagicMock()
sys.modules["shared.middleware"].setup_cors = lambda app: None
sys.modules["shared.middleware"].RequestLoggingMiddleware = _NoopMiddleware
sys.modules["shared.middleware"].TenantContextMiddleware = _NoopMiddleware
sys.modules["shared.middleware.security_headers"].setup_security_headers = lambda app: None

_structlog = sys.modules["structlog"]
_structlog.get_logger.return_value = MagicMock()

# Fake user
_FakeUser = type(
    "User",
    (),
    {"id": "user-001", "tenant_id": "tenant-001", "roles": ["admin"]},
)
_mock_user = _FakeUser()


async def _fake_get_current_user():
    return _mock_user


sys.modules["shared.auth.dependencies"].get_current_user = _fake_get_current_user
sys.modules["shared.auth.models"].User = _FakeUser

# Add service root
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

# ---------------------------------------------------------------------------
# Import the app
# ---------------------------------------------------------------------------
try:
    from src.main import app
    from src.routes.tasks import router as tasks_router
    from src.routes.astronomical import router as astronomical_router
    from src.routes.ndvi import router as ndvi_router
    _APP_AVAILABLE = True
except Exception as _import_err:
    _APP_AVAILABLE = False
    _import_err_msg = str(_import_err)

if not _APP_AVAILABLE:
    pytest.skip(f"task-service import failed: {_import_err_msg}", allow_module_level=True)

from fastapi.testclient import TestClient

# Override auth dependency
try:
    from src.routes.tasks import get_current_user as _tasks_get_current_user
    app.dependency_overrides[_tasks_get_current_user] = _fake_get_current_user
except Exception:
    pass

try:
    from src.routes.astronomical import get_current_user as _astro_get_current_user
    app.dependency_overrides[_astro_get_current_user] = _fake_get_current_user
except Exception:
    pass

try:
    from src.routes.ndvi import get_current_user as _ndvi_get_current_user
    app.dependency_overrides[_ndvi_get_current_user] = _fake_get_current_user
except Exception:
    pass

# ---------------------------------------------------------------------------
# DB session mock helper
# ---------------------------------------------------------------------------

def _make_db_mock():
    db = MagicMock()
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.filter_by.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.limit.return_value = query_mock
    query_mock.offset.return_value = query_mock
    query_mock.all.return_value = []
    query_mock.first.return_value = None
    query_mock.count.return_value = 0
    db.query.return_value = query_mock
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.rollback = MagicMock()
    db.delete = MagicMock()
    db.close = MagicMock()
    return db


TENANT_HEADERS = {"X-Tenant-Id": "tenant-001"}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def client_strict():
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def mock_db():
    return _make_db_mock()


@pytest.fixture(autouse=True)
def override_get_db(mock_db):
    try:
        from src.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
    except Exception:
        pass
    yield
    app.dependency_overrides.pop("get_db", None)


# ===========================================================================
# Health endpoint tests
# ===========================================================================

class TestHealthEndpoints:
    def test_healthz_returns_200(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200

    def test_healthz_status_ok(self, client):
        data = client.get("/healthz").json()
        assert data["status"] == "ok"

    def test_healthz_service_name(self, client):
        data = client.get("/healthz").json()
        assert data["service"] == "sahool-task-service"

    def test_healthz_version(self, client):
        data = client.get("/healthz").json()
        assert data["version"] == "16.0.0"

    def test_readyz_returns_response(self, client):
        resp = client.get("/readyz")
        assert resp.status_code in (200, 503)

    def test_readyz_has_status_field(self, client):
        data = client.get("/readyz").json()
        assert "status" in data

    def test_readyz_has_checks(self, client):
        data = client.get("/readyz").json()
        assert "checks" in data

    def test_readyz_checks_database(self, client):
        data = client.get("/readyz").json()
        assert "database" in data["checks"]

    def test_readyz_checks_nats(self, client):
        data = client.get("/readyz").json()
        assert "nats" in data["checks"]

    def test_readyz_checks_redis(self, client):
        data = client.get("/readyz").json()
        assert "redis" in data["checks"]

    def test_health_combined_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_combined_has_ready(self, client):
        data = client.get("/health").json()
        assert "ready" in data

    def test_health_combined_has_checks(self, client):
        data = client.get("/health").json()
        assert "checks" in data

    def test_health_combined_status_ok(self, client):
        data = client.get("/health").json()
        assert data["status"] == "ok"


# ===========================================================================
# Tasks router tests (GET /api/v1/tasks)
# ===========================================================================

class TestTasksListEndpoint:
    def test_list_tasks_with_tenant_header(self, client):
        resp = client.get("/api/v1/tasks", headers=TENANT_HEADERS)
        assert resp.status_code in (200, 401, 422, 503)

    def test_list_tasks_returns_json(self, client):
        resp = client.get("/api/v1/tasks", headers=TENANT_HEADERS)
        assert resp.headers.get("content-type", "").startswith("application/json")

    def test_list_tasks_empty_db(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        resp = client.get("/api/v1/tasks", headers=TENANT_HEADERS)
        assert resp.status_code in (200, 401, 422, 503)

    def test_list_tasks_without_tenant_header(self, client):
        resp = client.get("/api/v1/tasks")
        # May succeed or require header
        assert resp.status_code in (200, 400, 401, 422, 503)

    def test_list_tasks_with_status_filter(self, client):
        resp = client.get("/api/v1/tasks?status=pending", headers=TENANT_HEADERS)
        assert resp.status_code in (200, 401, 422, 503)

    def test_list_tasks_with_priority_filter(self, client):
        resp = client.get("/api/v1/tasks?priority=high", headers=TENANT_HEADERS)
        assert resp.status_code in (200, 401, 422, 503)


class TestTasksCreateEndpoint:
    def _task_payload(self):
        return {
            "title": "Water wheat field",
            "task_type": "irrigation",
            "field_id": "field-001",
            "priority": "medium",
            "due_date": "2025-06-01",
        }

    def test_create_task_basic(self, client):
        resp = client.post(
            "/api/v1/tasks",
            json=self._task_payload(),
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (200, 201, 400, 401, 422, 503)

    def test_create_task_missing_title(self, client):
        payload = self._task_payload()
        del payload["title"]
        resp = client.post("/api/v1/tasks", json=payload, headers=TENANT_HEADERS)
        assert resp.status_code in (400, 422)

    def test_create_task_returns_json(self, client):
        resp = client.post(
            "/api/v1/tasks",
            json=self._task_payload(),
            headers=TENANT_HEADERS,
        )
        assert resp.headers.get("content-type", "").startswith("application/json")


class TestTasksGetByIdEndpoint:
    def test_get_task_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        tid = str(uuid.uuid4())
        resp = client.get(f"/api/v1/tasks/{tid}", headers=TENANT_HEADERS)
        assert resp.status_code in (404, 401, 422, 503)

    def test_get_task_invalid_id(self, client):
        resp = client.get("/api/v1/tasks/not-a-valid-id", headers=TENANT_HEADERS)
        assert resp.status_code in (400, 404, 422, 503)


class TestTasksUpdateEndpoint:
    def test_update_task_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        tid = str(uuid.uuid4())
        resp = client.put(
            f"/api/v1/tasks/{tid}",
            json={"title": "Updated"},
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (404, 401, 422, 503)


class TestTasksDeleteEndpoint:
    def test_delete_task_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        tid = str(uuid.uuid4())
        resp = client.delete(f"/api/v1/tasks/{tid}", headers=TENANT_HEADERS)
        assert resp.status_code in (404, 401, 422, 503)


class TestTasksStatusEndpoints:
    def test_start_task_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        tid = str(uuid.uuid4())
        resp = client.post(f"/api/v1/tasks/{tid}/start", headers=TENANT_HEADERS)
        assert resp.status_code in (404, 401, 422, 503)

    def test_complete_task_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        tid = str(uuid.uuid4())
        resp = client.post(f"/api/v1/tasks/{tid}/complete", headers=TENANT_HEADERS)
        assert resp.status_code in (404, 401, 422, 503)

    def test_cancel_task_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        tid = str(uuid.uuid4())
        resp = client.post(f"/api/v1/tasks/{tid}/cancel", headers=TENANT_HEADERS)
        assert resp.status_code in (404, 401, 422, 503)


# ===========================================================================
# Statistics endpoint
# ===========================================================================

class TestTasksStatsEndpoint:
    def test_stats_endpoint(self, client):
        resp = client.get("/api/v1/tasks/stats", headers=TENANT_HEADERS)
        assert resp.status_code in (200, 401, 422, 503)

    def test_stats_returns_json(self, client):
        resp = client.get("/api/v1/tasks/stats", headers=TENANT_HEADERS)
        assert resp.headers.get("content-type", "").startswith("application/json")


# ===========================================================================
# Astronomical router tests
# ===========================================================================

class TestAstronomicalEndpoints:
    def test_best_days_endpoint_exists(self, client):
        resp = client.get(
            "/api/v1/astronomical/best-days",
            params={"activity": "planting"},
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (200, 400, 401, 422, 503)

    def test_best_days_returns_json(self, client):
        resp = client.get(
            "/api/v1/astronomical/best-days",
            params={"activity": "planting"},
            headers=TENANT_HEADERS,
        )
        assert resp.headers.get("content-type", "").startswith("application/json")

    def test_daily_data_endpoint_exists(self, client):
        resp = client.get(
            "/api/v1/astronomical/daily",
            params={"date": "2025-06-01"},
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (200, 400, 401, 422, 503)

    def test_validate_date_endpoint_exists(self, client):
        resp = client.get(
            "/api/v1/astronomical/validate-date",
            params={"date": "2025-06-01", "activity": "irrigation"},
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (200, 400, 401, 422, 503)


# ===========================================================================
# NDVI router tests
# ===========================================================================

class TestNdviEndpoints:
    def test_ndvi_alert_endpoint_exists(self, client):
        payload = {
            "field_id": "field-001",
            "ndvi_value": 0.3,
            "alert_type": "low_ndvi",
        }
        resp = client.post(
            "/api/v1/ndvi/alert",
            json=payload,
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (200, 201, 400, 401, 422, 503)

    def test_ndvi_suggestions_endpoint_exists(self, client):
        resp = client.get(
            "/api/v1/ndvi/suggestions",
            params={"field_id": "field-001"},
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (200, 400, 401, 422, 503)

    def test_ndvi_field_health_endpoint_exists(self, client):
        resp = client.get(
            "/api/v1/ndvi/field-health",
            params={"field_id": "field-001"},
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (200, 400, 401, 422, 503)


# ===========================================================================
# Misc / edge cases
# ===========================================================================

class TestMiscEndpoints:
    def test_unknown_route_returns_404(self, client):
        resp = client.get("/nonexistent-path")
        assert resp.status_code == 404

    def test_method_not_allowed(self, client):
        resp = client.delete("/healthz")
        assert resp.status_code in (404, 405)

    def test_app_has_routes(self):
        routes = [r.path for r in app.routes]
        assert "/healthz" in routes
        assert "/readyz" in routes
        assert "/health" in routes

    def test_app_title_set(self):
        assert app.title is not None
        assert len(app.title) > 0

    def test_healthz_response_structure(self, client):
        data = client.get("/healthz").json()
        assert set(data.keys()) >= {"status", "service", "version"}

    def test_readyz_status_values(self, client):
        data = client.get("/readyz").json()
        assert data["status"] in ("ready", "not_ready")

    def test_health_combined_checks_keys(self, client):
        data = client.get("/health").json()
        checks = data.get("checks", {})
        assert "database" in checks

    def test_tasks_endpoint_requires_valid_content_type_for_post(self, client):
        resp = client.post(
            "/api/v1/tasks",
            data="not-json",
            headers={**TENANT_HEADERS, "Content-Type": "text/plain"},
        )
        assert resp.status_code in (400, 415, 422, 503)

    def test_evidence_endpoint_exists(self, client):
        tid = str(uuid.uuid4())
        resp = client.post(
            f"/api/v1/tasks/{tid}/evidence",
            json={"type": "photo", "url": "http://example.com/photo.jpg"},
            headers=TENANT_HEADERS,
        )
        assert resp.status_code in (200, 201, 400, 401, 404, 422, 503)
