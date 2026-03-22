"""
Comprehensive unit tests for SAHOOL Audit Service.
Targets >60% code coverage across models, endpoints, helpers, and edge cases.
"""

import os
import sys

# Ensure test environment
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

from shared.auth.dependencies import get_current_user
from src.main import (
    AuditLogQuery,
    AuditLogResponse,
    AuditStatsResponse,
    ComplianceReportResponse,
    HashChainValidationResponse,
    PaginatedResponse,
    _audit_logs,
    _get_logs_for_tenant,
    app,
    get_tenant_id,
    sanitize_log_input,
)

# Valid UUID for tenant context middleware
VALID_TENANT = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
TENANT_HEADER = {"X-Tenant-ID": VALID_TENANT}


# Override auth dependency for testing
async def _mock_current_user():
    return {"id": "test-user", "tenant_id": VALID_TENANT}


app.dependency_overrides[get_current_user] = _mock_current_user


@pytest.fixture(autouse=True)
def clear_audit_logs():
    """Clear in-memory audit logs before each test."""
    _audit_logs.clear()
    yield
    _audit_logs.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helper / utility function tests
# ---------------------------------------------------------------------------


class TestSanitizeLogInput:
    """Tests for the sanitize_log_input helper function."""

    def test_sanitize_newlines(self):
        assert sanitize_log_input("line1\nline2") == "line1\\nline2"

    def test_sanitize_carriage_return(self):
        assert sanitize_log_input("line1\rline2") == "line1\\rline2"

    def test_sanitize_tab(self):
        assert sanitize_log_input("col1\tcol2") == "col1\\tcol2"

    def test_sanitize_combined(self):
        result = sanitize_log_input("a\nb\rc\td")
        assert result == "a\\nb\\rc\\td"

    def test_sanitize_non_string_input(self):
        result = sanitize_log_input(12345)
        assert result == "12345"

    def test_sanitize_clean_string(self):
        assert sanitize_log_input("hello world") == "hello world"


class TestGetTenantId:
    """Tests for the get_tenant_id dependency."""

    def test_valid_tenant_id(self):
        result = get_tenant_id("tenant-abc")
        assert result == "tenant-abc"

    def test_missing_tenant_id_raises(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            get_tenant_id(None)
        assert exc.value.status_code == 400
        assert "X-Tenant-Id" in str(exc.value.detail)


class TestGetLogsForTenant:
    """Tests for the _get_logs_for_tenant helper."""

    def test_creates_new_list_for_new_tenant(self):
        logs = _get_logs_for_tenant("new-tenant")
        assert logs == []
        assert "new-tenant" in _audit_logs

    def test_returns_existing_list(self):
        _audit_logs["existing"] = [{"id": "1"}]
        logs = _get_logs_for_tenant("existing")
        assert len(logs) == 1
        assert logs[0]["id"] == "1"


# ---------------------------------------------------------------------------
# Pydantic model tests
# ---------------------------------------------------------------------------


class TestPydanticModels:
    """Tests for Pydantic request/response models."""

    def test_audit_log_response_defaults(self):
        resp = AuditLogResponse(
            id="log-1",
            tenant_id="t1",
            user_id="u1",
            action="login",
            category="auth",
            severity="info",
            created_at="2026-01-01T00:00:00Z",
        )
        assert resp.success is True
        assert resp.resource_type is None
        assert resp.error_code is None

    def test_audit_log_query_defaults(self):
        q = AuditLogQuery()
        assert q.skip == 0
        assert q.limit == 50
        assert q.user_id is None

    def test_hash_chain_validation_response(self):
        r = HashChainValidationResponse(
            valid=True,
            total_entries=10,
            validated_entries=10,
            invalid_entries=[],
            errors=[],
        )
        assert r.valid is True

    def test_compliance_report_response(self):
        r = ComplianceReportResponse(
            tenant_id="t1",
            report_generated="2026-01-01",
            period={"start": "2026-01-01", "end": "2026-01-31"},
            framework="general",
            summary={"total_events": 0},
            by_category={},
            by_severity={},
            chain_integrity={"valid": True},
        )
        assert r.framework == "general"

    def test_audit_stats_response(self):
        r = AuditStatsResponse(
            total_events=100,
            events_by_category={"auth": 50},
            events_by_severity={"info": 80},
            failed_events=5,
            unique_users=10,
            chain_coverage_percent=95.5,
        )
        assert r.total_events == 100

    def test_paginated_response(self):
        r = PaginatedResponse(
            items=[{"a": 1}],
            total=1,
            skip=0,
            limit=50,
            has_more=False,
        )
        assert r.has_more is False


# ---------------------------------------------------------------------------
# Health endpoint tests
# ---------------------------------------------------------------------------


class TestHealthEndpoints:
    def test_health_returns_service_info(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "audit-service"
        assert data["version"] == "16.0.0"
        assert "dependencies" in data

    def test_healthz(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_readyz_structure(self, client):
        resp = client.get("/readyz")
        data = resp.json()
        assert "status" in data
        assert "database" in data
        assert "nats" in data


# ---------------------------------------------------------------------------
# Audit log endpoint tests with data
# ---------------------------------------------------------------------------


def _seed_logs(tenant_id: str, count: int = 5):
    """Seed in-memory audit logs for testing."""
    now = datetime.now(UTC)
    logs = _get_logs_for_tenant(tenant_id)
    for i in range(count):
        logs.append(
            {
                "id": f"log-{i}",
                "tenant_id": tenant_id,
                "user_id": f"user-{i % 3}",
                "action": "auth.login.failed" if i == 0 else "field.update",
                "category": "security" if i < 2 else "operations",
                "severity": "warning" if i < 2 else "info",
                "resource_type": "field",
                "resource_id": f"field-{i}",
                "success": i != 0,
                "created_at": (now - timedelta(hours=count - i)).isoformat(),
                "entry_hash": f"hash-{i}" if i > 0 else None,
                "prev_hash": f"hash-{i - 1}" if i > 1 else None,
                "details": {"ip": "10.0.0.1"},
            }
        )


class TestAuditLogEndpoints:
    def test_get_logs_empty(self, client):
        resp = client.get("/api/v1/audit/logs", headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_get_logs_with_data(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get("/api/v1/audit/logs", headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5

    def test_get_logs_filter_by_user_id(self, client):
        _seed_logs(VALID_TENANT, 6)
        resp = client.get(
            "/api/v1/audit/logs",
            params={"user_id": "user-0"},
            headers=TENANT_HEADER,
        )
        data = resp.json()
        assert all(item["user_id"] == "user-0" for item in data["items"])

    def test_get_logs_filter_by_action(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get(
            "/api/v1/audit/logs",
            params={"action": "field.update"},
            headers=TENANT_HEADER,
        )
        data = resp.json()
        assert all(item["action"] == "field.update" for item in data["items"])

    def test_get_logs_filter_by_category(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get(
            "/api/v1/audit/logs",
            params={"category": "security"},
            headers=TENANT_HEADER,
        )
        data = resp.json()
        assert all(item["category"] == "security" for item in data["items"])

    def test_get_logs_filter_by_success(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get(
            "/api/v1/audit/logs",
            params={"success": False},
            headers=TENANT_HEADER,
        )
        data = resp.json()
        assert all(item["success"] is False for item in data["items"])

    def test_get_logs_pagination(self, client):
        _seed_logs(VALID_TENANT, 10)
        resp = client.get(
            "/api/v1/audit/logs",
            params={"skip": 2, "limit": 3},
            headers=TENANT_HEADER,
        )
        data = resp.json()
        assert len(data["items"]) == 3
        assert data["skip"] == 2
        assert data["limit"] == 3
        assert data["has_more"] is True

    def test_get_logs_filter_by_resource(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get(
            "/api/v1/audit/logs",
            params={"resource_type": "field", "resource_id": "field-2"},
            headers=TENANT_HEADER,
        )
        data = resp.json()
        assert all(item["resource_id"] == "field-2" for item in data["items"])

    def test_get_specific_log_found(self, client):
        _seed_logs(VALID_TENANT, 3)
        resp = client.get("/api/v1/audit/logs/log-1", headers=TENANT_HEADER)
        assert resp.status_code == 200
        assert resp.json()["id"] == "log-1"

    def test_get_specific_log_not_found(self, client):
        resp = client.get("/api/v1/audit/logs/nonexistent", headers=TENANT_HEADER)
        assert resp.status_code == 404


class TestUserAuditTrail:
    def test_user_trail(self, client):
        _seed_logs(VALID_TENANT, 6)
        resp = client.get(
            "/api/v1/audit/users/user-0/trail",
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all(item["user_id"] == "user-0" for item in data["items"])

    def test_user_trail_with_category_filter(self, client):
        _seed_logs(VALID_TENANT, 6)
        resp = client.get(
            "/api/v1/audit/users/user-0/trail",
            params={"category": "security"},
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200


class TestResourceAuditTrail:
    def test_resource_trail(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get(
            "/api/v1/audit/resources/field/field-2/trail",
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all(item["resource_type"] == "field" for item in data["items"])
        assert all(item["resource_id"] == "field-2" for item in data["items"])


# ---------------------------------------------------------------------------
# Hash chain validation tests
# ---------------------------------------------------------------------------


class TestHashChainValidation:
    def test_validate_empty_chain(self, client):
        resp = client.get("/api/v1/audit/chain/validate", headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert data["total_entries"] == 0

    def test_validate_chain_with_entries(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get("/api/v1/audit/chain/validate", headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert "valid" in data
        assert "validated_entries" in data
        assert "invalid_entries" in data

    def test_chain_summary_empty(self, client):
        resp = client.get("/api/v1/audit/chain/summary", headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == VALID_TENANT
        assert data["total_entries"] == 0
        assert data["chain_coverage_percent"] == 0

    def test_chain_summary_with_data(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get("/api/v1/audit/chain/summary", headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_entries"] == 5
        assert data["entries_with_hash"] > 0
        assert data["chain_coverage_percent"] > 0


# ---------------------------------------------------------------------------
# Compliance reporting tests
# ---------------------------------------------------------------------------


class TestComplianceReport:
    def test_compliance_report_empty(self, client):
        resp = client.get(
            "/api/v1/audit/compliance/report",
            params={
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T23:59:59Z",
                "framework": "general",
            },
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == VALID_TENANT
        assert data["framework"] == "general"
        assert data["summary"]["total_events"] == 0

    def test_compliance_report_gdpr(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get(
            "/api/v1/audit/compliance/report",
            params={
                "start_date": "2020-01-01T00:00:00Z",
                "end_date": "2030-12-31T23:59:59Z",
                "framework": "GDPR",
            },
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["framework"] == "GDPR"
        assert data["summary"]["total_events"] == 5

    def test_compliance_report_soc2(self, client):
        resp = client.get(
            "/api/v1/audit/compliance/report",
            params={
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T23:59:59Z",
                "framework": "SOC2",
            },
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["framework"] == "SOC2"


# ---------------------------------------------------------------------------
# Statistics tests
# ---------------------------------------------------------------------------


class TestAuditStats:
    def test_stats_empty(self, client):
        resp = client.get(
            "/api/v1/audit/stats",
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_events"] == 0
        assert data["chain_coverage_percent"] == 0

    def test_stats_with_data(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get(
            "/api/v1/audit/stats",
            params={"period": "90d"},
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_events"] == 5
        assert data["unique_users"] > 0

    def test_stats_period_7d(self, client):
        _seed_logs(VALID_TENANT, 3)
        resp = client.get(
            "/api/v1/audit/stats",
            params={"period": "7d"},
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Security events / failed logins tests
# ---------------------------------------------------------------------------


class TestSecurityEndpoints:
    def test_security_events_empty(self, client):
        resp = client.get("/api/v1/audit/security-events", headers=TENANT_HEADER)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_security_events_with_data(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get("/api/v1/audit/security-events", headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert all(item["category"] == "security" for item in data["items"])

    def test_failed_logins_empty(self, client):
        resp = client.get("/api/v1/audit/failed-logins", headers=TENANT_HEADER)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_failed_logins_with_data(self, client):
        _seed_logs(VALID_TENANT, 5)
        resp = client.get(
            "/api/v1/audit/failed-logins",
            params={"hours": 48},
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all(item["action"] == "auth.login.failed" for item in data["items"])


# ---------------------------------------------------------------------------
# Export tests
# ---------------------------------------------------------------------------


class TestExport:
    def test_export_json_empty(self, client):
        resp = client.get(
            "/api/v1/audit/export",
            params={
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T23:59:59Z",
                "format": "json",
            },
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200

    def test_export_json_with_data(self, client):
        _seed_logs(VALID_TENANT, 3)
        resp = client.get(
            "/api/v1/audit/export",
            params={
                "start_date": "2020-01-01T00:00:00Z",
                "end_date": "2030-12-31T23:59:59Z",
                "format": "json",
            },
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_export_csv(self, client):
        _seed_logs(VALID_TENANT, 3)
        resp = client.get(
            "/api/v1/audit/export",
            params={
                "start_date": "2020-01-01T00:00:00Z",
                "end_date": "2030-12-31T23:59:59Z",
                "format": "csv",
            },
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")

    def test_export_csv_empty(self, client):
        resp = client.get(
            "/api/v1/audit/export",
            params={
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T23:59:59Z",
                "format": "csv",
            },
            headers=TENANT_HEADER,
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Missing tenant header tests
# ---------------------------------------------------------------------------


class TestMissingTenantHeader:
    def test_logs_no_tenant(self, client):
        resp = client.get("/api/v1/audit/logs")
        assert resp.status_code == 400

    def test_stats_no_tenant(self, client):
        resp = client.get("/api/v1/audit/stats")
        assert resp.status_code == 400

    def test_chain_validate_no_tenant(self, client):
        resp = client.get("/api/v1/audit/chain/validate")
        assert resp.status_code == 400

    def test_export_no_tenant(self, client):
        resp = client.get(
            "/api/v1/audit/export",
            params={
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T23:59:59Z",
            },
        )
        assert resp.status_code == 400
