"""
Audit Service Tests
"""

import os

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

# Set test environment before importing app
os.environ.setdefault("ENVIRONMENT", "test")

# Valid UUID tenant ID (TenantContextMiddleware requires UUID format)
VALID_TENANT_ID = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def auth_client():
    """Create a test client with auth dependency overridden.

    Clears dependency_overrides on teardown to prevent state leakage.
    """
    from src.main import app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    # Override the auth dependency so we don't need real JWT tokens
    async def mock_current_user():
        return User(
            id="test-user-id",
            email="test@example.com",
            tenant_id=VALID_TENANT_ID,
            roles=["admin"],
        )

    app.dependency_overrides[get_current_user] = mock_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_import_main():
    """Smoke test: verify main module can be imported"""
    from src import main

    assert main is not None
    assert main.app is not None


def test_health_endpoint():
    """Test health endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "audit-service"
    assert "version" in data


def test_healthz_endpoint():
    """Test healthz endpoint (liveness probe)"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "audit-service"


def test_readyz_endpoint():
    """Test readyz endpoint (readiness probe)"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "nats" in data


def test_get_audit_logs_requires_tenant(auth_client):
    """Test that audit logs endpoint requires tenant header"""
    response = auth_client.get("/api/v1/audit/logs")
    assert response.status_code == 400
    data = response.json()
    # TenantContextMiddleware returns {"error": "missing_tenant", ...}
    assert data["error"] == "missing_tenant"


def test_get_audit_logs_with_tenant(auth_client):
    """Test audit logs endpoint with tenant header"""
    response = auth_client.get("/api/v1/audit/logs", headers={"X-Tenant-Id": VALID_TENANT_ID})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "has_more" in data


def test_get_audit_stats(auth_client):
    """Test audit statistics endpoint.

    The response model declares snake_case fields with camelCase aliases
    (``populate_by_name=True, by_alias=True``) so FastAPI actually
    serialises camelCase (``totalEvents``) by default. Accept either
    casing so the assertion is robust to future alias changes.
    """
    response = auth_client.get("/api/v1/audit/stats", headers={"X-Tenant-Id": VALID_TENANT_ID})
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data or "totalEvents" in data
    assert "events_by_category" in data or "eventsByCategory" in data
    assert "events_by_severity" in data or "eventsBySeverity" in data


def test_validate_hash_chain(auth_client):
    """Test hash chain validation endpoint"""
    response = auth_client.get("/api/v1/audit/chain/validate", headers={"X-Tenant-Id": VALID_TENANT_ID})
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert "total_entries" in data
    assert "validated_entries" in data


def test_get_chain_summary(auth_client):
    """Test chain summary endpoint"""
    response = auth_client.get("/api/v1/audit/chain/summary", headers={"X-Tenant-Id": VALID_TENANT_ID})
    assert response.status_code == 200
    data = response.json()
    assert "tenant_id" in data
    assert "total_entries" in data
    assert "chain_coverage_percent" in data


def test_get_compliance_report(auth_client):
    """Test compliance report endpoint"""
    response = auth_client.get(
        "/api/v1/audit/compliance/report",
        params={
            "start_date": "2026-01-01T00:00:00Z",
            "end_date": "2026-01-31T23:59:59Z",
            "framework": "general",
        },
        headers={"X-Tenant-Id": VALID_TENANT_ID},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == VALID_TENANT_ID
    assert data["framework"] == "general"
    assert "summary" in data
    assert "by_category" in data


def test_get_security_events(auth_client):
    """Test security events endpoint"""
    response = auth_client.get("/api/v1/audit/security-events", headers={"X-Tenant-Id": VALID_TENANT_ID})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_failed_logins(auth_client):
    """Test failed logins endpoint"""
    response = auth_client.get("/api/v1/audit/failed-logins", headers={"X-Tenant-Id": VALID_TENANT_ID})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_export_audit_logs_json(auth_client):
    """Test export endpoint with JSON format"""
    response = auth_client.get(
        "/api/v1/audit/export",
        params={
            "start_date": "2026-01-01T00:00:00Z",
            "end_date": "2026-01-31T23:59:59Z",
            "format": "json",
        },
        headers={"X-Tenant-Id": VALID_TENANT_ID},
    )
    assert response.status_code == 200


def test_get_user_audit_trail(auth_client):
    """Test user audit trail endpoint"""
    response = auth_client.get("/api/v1/audit/users/user-123/trail", headers={"X-Tenant-Id": VALID_TENANT_ID})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_resource_audit_trail(auth_client):
    """Test resource audit trail endpoint"""
    response = auth_client.get(
        "/api/v1/audit/resources/field/field-123/trail", headers={"X-Tenant-Id": VALID_TENANT_ID}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
