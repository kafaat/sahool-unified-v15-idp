"""
Tests for shared/security/guard.py
Authorization guards and decorators
"""

import pytest
from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from shared.security.guard import (
    require,
    require_all,
    require_any,
    require_any_role,
    require_owner_or_permission,
    require_resource_access,
    require_role,
    require_tenant,
    requires,
    requires_role,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures / Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _principal(roles=None, sub="user-1", tenant_id="tenant-1", scopes=None):
    return {
        "sub": sub,
        "tenant_id": tenant_id,
        "roles": roles or [],
        "scopes": scopes or [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# require()
# ─────────────────────────────────────────────────────────────────────────────


class TestRequire:
    def test_allowed(self):
        # Admin has all standard permissions
        principal = _principal(roles=["admin"])
        require(principal, "fieldops:task.create")  # Should not raise

    def test_denied(self):
        principal = _principal(roles=["viewer"])
        with pytest.raises(HTTPException) as exc_info:
            require(principal, "fieldops:task.create")
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == "forbidden"
        assert exc_info.value.detail["required_permission"] == "fieldops:task.create"

    def test_super_admin_always_allowed(self):
        principal = _principal(roles=["super_admin"])
        require(principal, "some:random.perm")  # Should not raise


# ─────────────────────────────────────────────────────────────────────────────
# require_any()
# ─────────────────────────────────────────────────────────────────────────────


class TestRequireAny:
    def test_allowed_with_first_perm(self):
        principal = _principal(roles=["admin"])
        require_any(principal, ["fieldops:task.read", "fieldops:task.admin"])

    def test_denied_no_matching_perm(self):
        principal = _principal(roles=["viewer"])
        with pytest.raises(HTTPException) as exc_info:
            require_any(principal, ["fieldops:task.create", "fieldops:task.delete"])
        assert exc_info.value.status_code == 403

    def test_allowed_with_scope(self):
        principal = _principal(roles=[], scopes=["custom:perm"])
        require_any(principal, ["custom:perm", "other:perm"])


# ─────────────────────────────────────────────────────────────────────────────
# require_all()
# ─────────────────────────────────────────────────────────────────────────────


class TestRequireAll:
    def test_allowed_with_all_perms(self):
        principal = _principal(roles=["admin"])
        require_all(principal, ["fieldops:task.read", "fieldops:task.update"])

    def test_denied_missing_some(self):
        principal = _principal(roles=["viewer"])
        with pytest.raises(HTTPException) as exc_info:
            require_all(principal, ["fieldops:task.read", "fieldops:task.create"])
        assert exc_info.value.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# require_tenant()
# ─────────────────────────────────────────────────────────────────────────────


class TestRequireTenant:
    def test_same_tenant_allowed(self):
        principal = _principal(tenant_id="t1")
        require_tenant(principal, "t1")  # Should not raise

    def test_different_tenant_denied(self):
        principal = _principal(tenant_id="t1")
        with pytest.raises(HTTPException) as exc_info:
            require_tenant(principal, "t2")
        assert exc_info.value.status_code == 403

    def test_super_admin_bypasses_tenant(self):
        principal = _principal(roles=["super_admin"], tenant_id="t1")
        require_tenant(principal, "t2")  # Should not raise

    def test_tenant_from_tid(self):
        principal = {"sub": "u1", "tid": "t1", "roles": []}
        require_tenant(principal, "t1")  # Should not raise


# ─────────────────────────────────────────────────────────────────────────────
# require_resource_access()
# ─────────────────────────────────────────────────────────────────────────────


class TestRequireResourceAccess:
    def test_allowed(self):
        principal = _principal(roles=["admin"], tenant_id="t1")
        require_resource_access(principal, "fieldops:task.read", "t1")

    def test_wrong_tenant_denied(self):
        principal = _principal(roles=["admin"], tenant_id="t1")
        with pytest.raises(HTTPException):
            require_resource_access(principal, "fieldops:task.read", "t2")

    def test_wrong_perm_denied(self):
        principal = _principal(roles=["viewer"], tenant_id="t1")
        with pytest.raises(HTTPException):
            require_resource_access(principal, "fieldops:task.create", "t1")


# ─────────────────────────────────────────────────────────────────────────────
# require_role()
# ─────────────────────────────────────────────────────────────────────────────


class TestRequireRole:
    def test_has_role(self):
        principal = _principal(roles=["admin"])
        require_role(principal, "admin")

    def test_missing_role(self):
        principal = _principal(roles=["viewer"])
        with pytest.raises(HTTPException) as exc_info:
            require_role(principal, "admin")
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["required_role"] == "admin"

    def test_super_admin_bypasses(self):
        principal = _principal(roles=["super_admin"])
        require_role(principal, "admin")

    def test_no_roles(self):
        principal = _principal(roles=[])
        with pytest.raises(HTTPException):
            require_role(principal, "worker")


# ─────────────────────────────────────────────────────────────────────────────
# require_any_role()
# ─────────────────────────────────────────────────────────────────────────────


class TestRequireAnyRole:
    def test_has_matching_role(self):
        principal = _principal(roles=["worker"])
        require_any_role(principal, ["admin", "worker"])

    def test_no_matching_role(self):
        principal = _principal(roles=["viewer"])
        with pytest.raises(HTTPException) as exc_info:
            require_any_role(principal, ["admin", "manager"])
        assert exc_info.value.status_code == 403

    def test_super_admin_bypass(self):
        principal = _principal(roles=["super_admin"])
        require_any_role(principal, ["admin", "manager"])


# ─────────────────────────────────────────────────────────────────────────────
# require_owner_or_permission()
# ─────────────────────────────────────────────────────────────────────────────


class TestRequireOwnerOrPermission:
    def test_owner_allowed(self):
        principal = _principal(sub="user-1", roles=["viewer"])
        require_owner_or_permission(principal, "user-1", "admin:users.update")

    def test_non_owner_with_permission_allowed(self):
        principal = _principal(sub="user-1", roles=["admin"])
        require_owner_or_permission(principal, "user-2", "admin:users.update")

    def test_non_owner_without_permission_denied(self):
        principal = _principal(sub="user-1", roles=["viewer"])
        with pytest.raises(HTTPException):
            require_owner_or_permission(principal, "user-2", "admin:users.update")


# ─────────────────────────────────────────────────────────────────────────────
# @requires decorator
# ─────────────────────────────────────────────────────────────────────────────


class TestRequiresDecorator:
    @pytest.mark.asyncio
    async def test_requires_with_valid_principal(self):
        @requires("fieldops:task.read")
        async def handler(principal=None):
            return "ok"

        principal = _principal(roles=["admin"])
        result = await handler(principal=principal)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_requires_without_principal_raises_401(self):
        @requires("fieldops:task.read")
        async def handler(principal=None):
            return "ok"

        with pytest.raises(HTTPException) as exc_info:
            await handler()
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_requires_insufficient_perm_raises_403(self):
        @requires("fieldops:task.create")
        async def handler(principal=None):
            return "ok"

        principal = _principal(roles=["viewer"])
        with pytest.raises(HTTPException) as exc_info:
            await handler(principal=principal)
        assert exc_info.value.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# @requires_role decorator
# ─────────────────────────────────────────────────────────────────────────────


class TestRequiresRoleDecorator:
    @pytest.mark.asyncio
    async def test_requires_role_with_valid_role(self):
        @requires_role("admin")
        async def handler(principal=None):
            return "ok"

        principal = _principal(roles=["admin"])
        result = await handler(principal=principal)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_requires_role_without_principal(self):
        @requires_role("admin")
        async def handler(principal=None):
            return "ok"

        with pytest.raises(HTTPException) as exc_info:
            await handler()
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_requires_role_wrong_role(self):
        @requires_role("admin")
        async def handler(principal=None):
            return "ok"

        principal = _principal(roles=["viewer"])
        with pytest.raises(HTTPException) as exc_info:
            await handler(principal=principal)
        assert exc_info.value.status_code == 403
