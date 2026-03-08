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
os.environ["ENVIRONMENT"] = "test"


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
    assert data["version"] == "16.0.0"


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


def test_get_audit_logs_requires_tenant():
    """Test that audit logs endpoint requires tenant header"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/logs")
    assert response.status_code == 400
    assert "X-Tenant-Id" in response.json()["detail"]


def test_get_audit_logs_with_tenant():
    """Test audit logs endpoint with tenant header"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/logs", headers={"X-Tenant-Id": "test-tenant"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "has_more" in data


def test_get_audit_stats():
    """Test audit statistics endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/stats", headers={"X-Tenant-Id": "test-tenant"})
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "events_by_category" in data
    assert "events_by_severity" in data


def test_validate_hash_chain():
    """Test hash chain validation endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/chain/validate", headers={"X-Tenant-Id": "test-tenant"})
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert "total_entries" in data
    assert "validated_entries" in data


def test_get_chain_summary():
    """Test chain summary endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/chain/summary", headers={"X-Tenant-Id": "test-tenant"})
    assert response.status_code == 200
    data = response.json()
    assert "tenant_id" in data
    assert "total_entries" in data
    assert "chain_coverage_percent" in data


def test_get_compliance_report():
    """Test compliance report endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get(
        "/api/v1/audit/compliance/report",
        params={
            "start_date": "2026-01-01T00:00:00Z",
            "end_date": "2026-01-31T23:59:59Z",
            "framework": "general",
        },
        headers={"X-Tenant-Id": "test-tenant"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "test-tenant"
    assert data["framework"] == "general"
    assert "summary" in data
    assert "by_category" in data


def test_get_security_events():
    """Test security events endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/security-events", headers={"X-Tenant-Id": "test-tenant"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_failed_logins():
    """Test failed logins endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/failed-logins", headers={"X-Tenant-Id": "test-tenant"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_export_audit_logs_json():
    """Test export endpoint with JSON format"""
    from src.main import app

    client = TestClient(app)
    response = client.get(
        "/api/v1/audit/export",
        params={
            "start_date": "2026-01-01T00:00:00Z",
            "end_date": "2026-01-31T23:59:59Z",
            "format": "json",
        },
        headers={"X-Tenant-Id": "test-tenant"},
    )
    assert response.status_code == 200


def test_get_user_audit_trail():
    """Test user audit trail endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/users/user-123/trail", headers={"X-Tenant-Id": "test-tenant"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_resource_audit_trail():
    """Test resource audit trail endpoint"""
    from src.main import app

    client = TestClient(app)
    response = client.get("/api/v1/audit/resources/field/field-123/trail", headers={"X-Tenant-Id": "test-tenant"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
