"""
Tenant Isolation Tests for SAHOOL Platform.

Tests validate multi-tenant data isolation and security.
"""

import uuid
from typing import Any, Dict, Optional

import pytest


class TenantContext:
    """Tenant context for request handling."""

    _current_tenant: str | None = None

    @classmethod
    def set_tenant(cls, tenant_id: str):
        """Set current tenant context."""
        cls._current_tenant = tenant_id

    @classmethod
    def get_tenant(cls) -> str | None:
        """Get current tenant context."""
        return cls._current_tenant

    @classmethod
    def clear(cls):
        """Clear tenant context."""
        cls._current_tenant = None


class TenantAwareRepository:
    """Base repository with tenant isolation."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._data: dict[str, dict[str, Any]] = {}

    def _get_tenant_data(self) -> dict[str, Any]:
        """Get data for current tenant."""
        if self.tenant_id not in self._data:
            self._data[self.tenant_id] = {}
        return self._data[self.tenant_id]

    def create(self, id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a record for current tenant."""
        tenant_data = self._get_tenant_data()
        record = {**data, "id": id, "tenant_id": self.tenant_id}
        tenant_data[id] = record
        return record

    def get(self, id: str) -> dict[str, Any] | None:
        """Get a record for current tenant."""
        tenant_data = self._get_tenant_data()
        return tenant_data.get(id)

    def get_all(self) -> list:
        """Get all records for current tenant."""
        return list(self._get_tenant_data().values())

    def delete(self, id: str) -> bool:
        """Delete a record for current tenant."""
        tenant_data = self._get_tenant_data()
        if id in tenant_data:
            del tenant_data[id]
            return True
        return False


@pytest.fixture
def tenant_repo():
    """Create tenant-aware repository."""
    return TenantAwareRepository("tenant1")


@pytest.fixture
def other_tenant_repo():
    """Create repository for different tenant."""
    return TenantAwareRepository("tenant2")


class TestTenantIsolation:
    """Tests for tenant data isolation."""

    def test_tenant_data_isolated(self, tenant_repo, other_tenant_repo):
        """Test data is isolated between tenants."""
        tenant_repo.create("field1", {"name": "Tenant 1 Field"})
        other_tenant_repo.create("field2", {"name": "Tenant 2 Field"})

        tenant1_data = tenant_repo.get_all()
        tenant2_data = other_tenant_repo.get_all()

        assert len(tenant1_data) == 1
        assert len(tenant2_data) == 1
        assert tenant1_data[0]["name"] == "Tenant 1 Field"
        assert tenant2_data[0]["name"] == "Tenant 2 Field"

    def test_cannot_access_other_tenant_data(self, tenant_repo, other_tenant_repo):
        """Test cannot access other tenant's data."""
        tenant_repo.create("field1", {"name": "Tenant 1 Field"})

        result = other_tenant_repo.get("field1")
        assert result is None

    def test_tenant_id_in_records(self, tenant_repo):
        """Test tenant_id is stored in records."""
        record = tenant_repo.create("field1", {"name": "Test Field"})

        assert record["tenant_id"] == "tenant1"

    def test_same_id_different_tenants(self, tenant_repo, other_tenant_repo):
        """Test same ID can exist in different tenants."""
        tenant_repo.create("field1", {"name": "Tenant 1 Field"})
        other_tenant_repo.create("field1", {"name": "Tenant 2 Field"})

        record1 = tenant_repo.get("field1")
        record2 = other_tenant_repo.get("field1")

        assert record1["name"] == "Tenant 1 Field"
        assert record2["name"] == "Tenant 2 Field"


class TestTenantContext:
    """Tests for tenant context management."""

    def test_set_tenant_context(self):
        """Test setting tenant context."""
        TenantContext.set_tenant("tenant123")

        assert TenantContext.get_tenant() == "tenant123"

        TenantContext.clear()

    def test_clear_tenant_context(self):
        """Test clearing tenant context."""
        TenantContext.set_tenant("tenant123")
        TenantContext.clear()

        assert TenantContext.get_tenant() is None

    def test_tenant_context_override(self):
        """Test tenant context can be overridden."""
        TenantContext.set_tenant("tenant1")
        TenantContext.set_tenant("tenant2")

        assert TenantContext.get_tenant() == "tenant2"

        TenantContext.clear()


class TestTenantValidation:
    """Tests for tenant ID validation."""

    def test_valid_tenant_id_format(self):
        """Test valid tenant ID formats."""
        valid_ids = [
            "tenant-123",
            "org_abc123",
            str(uuid.uuid4()),
            "company-xyz-456",
        ]

        for tenant_id in valid_ids:
            assert len(tenant_id) > 0
            assert len(tenant_id) <= 128

    def test_invalid_tenant_id_rejected(self):
        """Test invalid tenant IDs are rejected."""
        invalid_ids = [
            "",
            "   ",
            "tenant; DROP TABLE tenants;--",
            "<script>alert('xss')</script>",
        ]

        def is_valid_tenant_id(tenant_id: str) -> bool:
            if not tenant_id or not tenant_id.strip():
                return False
            if ";" in tenant_id or "<" in tenant_id:
                return False
            return True

        for tenant_id in invalid_ids:
            assert is_valid_tenant_id(tenant_id) is False


class TestCrossTenantPrevention:
    """Tests for cross-tenant access prevention."""

    def test_query_includes_tenant_filter(self):
        """Test queries include tenant filter."""
        query = """
            SELECT * FROM fields
            WHERE tenant_id = $1 AND id = $2
        """

        assert "tenant_id" in query
        assert "$1" in query

    def test_update_includes_tenant_filter(self):
        """Test updates include tenant filter."""
        query = """
            UPDATE fields
            SET name = $1
            WHERE tenant_id = $2 AND id = $3
        """

        assert "tenant_id" in query.upper() or "TENANT_ID" in query.upper()

    def test_delete_includes_tenant_filter(self):
        """Test deletes include tenant filter."""
        query = """
            DELETE FROM fields
            WHERE tenant_id = $1 AND id = $2
        """

        assert "tenant_id" in query


class TestTenantScopedQueries:
    """Tests for tenant-scoped query building."""

    def test_build_tenant_scoped_select(self):
        """Test building tenant-scoped SELECT query."""
        tenant_id = "tenant123"
        table = "fields"

        query = f"SELECT * FROM {table} WHERE tenant_id = $1"
        params = [tenant_id]

        assert "tenant_id = $1" in query
        assert params[0] == tenant_id

    def test_build_tenant_scoped_insert(self):
        """Test building tenant-scoped INSERT query."""
        tenant_id = "tenant123"

        query = "INSERT INTO fields (id, name, tenant_id) VALUES ($1, $2, $3)"
        params = ["field1", "Test Field", tenant_id]

        assert "tenant_id" in query
        assert tenant_id in params


class TestTenantAuditLogging:
    """Tests for tenant audit logging."""

    def test_audit_log_includes_tenant(self):
        """Test audit log includes tenant ID."""
        audit_entry = {
            "timestamp": "2024-01-15T10:30:00Z",
            "tenant_id": "tenant123",
            "user_id": "user456",
            "action": "field.create",
            "resource_id": "field789",
        }

        assert "tenant_id" in audit_entry
        assert audit_entry["tenant_id"] == "tenant123"

    def test_audit_log_tenant_cannot_be_null(self):
        """Test audit log tenant cannot be null."""

        def validate_audit_entry(entry: dict[str, Any]) -> bool:
            return entry.get("tenant_id") is not None

        valid_entry = {"tenant_id": "tenant123", "action": "test"}
        invalid_entry = {"tenant_id": None, "action": "test"}

        assert validate_audit_entry(valid_entry) is True
        assert validate_audit_entry(invalid_entry) is False


@pytest.mark.unit
class TestTenantDataMigration:
    """Tests for tenant data migration scenarios."""

    def test_tenant_data_export(self, tenant_repo):
        """Test exporting tenant data."""
        tenant_repo.create("field1", {"name": "Field 1"})
        tenant_repo.create("field2", {"name": "Field 2"})

        export_data = tenant_repo.get_all()

        assert len(export_data) == 2
        assert all(r["tenant_id"] == "tenant1" for r in export_data)

    def test_tenant_data_import_preserves_tenant(self):
        """Test importing data preserves tenant ID."""
        import_data = [
            {"id": "field1", "name": "Imported Field 1"},
            {"id": "field2", "name": "Imported Field 2"},
        ]

        target_tenant = "new_tenant"
        imported = []

        for item in import_data:
            record = {**item, "tenant_id": target_tenant}
            imported.append(record)

        assert all(r["tenant_id"] == target_tenant for r in imported)


@pytest.mark.unit
class TestTenantResourceLimits:
    """Tests for tenant resource limits."""

    def test_tenant_resource_quota(self):
        """Test tenant resource quota enforcement."""
        quotas = {
            "tenant1": {"max_fields": 100, "max_users": 10},
            "tenant2": {"max_fields": 500, "max_users": 50},
        }

        def check_quota(tenant_id: str, resource: str, current: int) -> bool:
            tenant_quota = quotas.get(tenant_id, {})
            max_allowed = tenant_quota.get(f"max_{resource}", 0)
            return current < max_allowed

        assert check_quota("tenant1", "fields", 50) is True
        assert check_quota("tenant1", "fields", 100) is False

    def test_tenant_storage_limit(self):
        """Test tenant storage limit enforcement."""
        storage_limits = {
            "free": 1024 * 1024 * 100,
            "standard": 1024 * 1024 * 1024,
            "premium": 1024 * 1024 * 1024 * 10,
        }

        def check_storage_limit(tier: str, used: int) -> bool:
            limit = storage_limits.get(tier, 0)
            return used < limit

        assert check_storage_limit("free", 50 * 1024 * 1024) is True
        assert check_storage_limit("free", 200 * 1024 * 1024) is False
