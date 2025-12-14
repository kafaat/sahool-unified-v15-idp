"""
Tests for Guard Module
"""

import pytest
from fastapi import HTTPException

from shared.security.guard import (
    require,
    require_any,
    require_all,
    require_tenant,
    require_resource_access,
    require_role,
    require_any_role,
    require_owner_or_permission,
)
from shared.security.rbac import Permission


class TestRequire:
    """Test basic permission requirement"""

    def test_require_passes_with_permission(self):
        """Test require passes when permission exists"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        # Should not raise
        require(principal, Permission.FIELDOPS_TASK_COMPLETE)

    def test_require_raises_without_permission(self):
        """Test require raises 403 when permission missing"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["viewer"],
            "scopes": [],
        }

        with pytest.raises(HTTPException) as exc_info:
            require(principal, Permission.FIELDOPS_TASK_DELETE)

        assert exc_info.value.status_code == 403
        assert "forbidden" in exc_info.value.detail["error"]


class TestRequireAny:
    """Test requiring any of multiple permissions"""

    def test_require_any_passes_with_one(self):
        """Test require_any passes when one permission exists"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        require_any(
            principal,
            [Permission.FIELDOPS_TASK_DELETE, Permission.FIELDOPS_TASK_COMPLETE],
        )

    def test_require_any_raises_with_none(self):
        """Test require_any raises when no permissions match"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["viewer"],
            "scopes": [],
        }

        with pytest.raises(HTTPException) as exc_info:
            require_any(
                principal,
                [Permission.FIELDOPS_TASK_DELETE, Permission.ADMIN_USERS_CREATE],
            )

        assert exc_info.value.status_code == 403


class TestRequireAll:
    """Test requiring all permissions"""

    def test_require_all_passes_with_all(self):
        """Test require_all passes when all permissions exist"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["manager"],
            "scopes": [],
        }

        require_all(
            principal,
            [Permission.FIELDOPS_TASK_CREATE, Permission.FIELDOPS_TASK_DELETE],
        )

    def test_require_all_raises_with_missing(self):
        """Test require_all raises when any permission missing"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        with pytest.raises(HTTPException):
            require_all(
                principal,
                [Permission.FIELDOPS_TASK_COMPLETE, Permission.FIELDOPS_TASK_DELETE],
            )


class TestRequireTenant:
    """Test tenant requirement"""

    def test_require_tenant_same(self):
        """Test require_tenant passes for same tenant"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": [],
            "scopes": [],
        }

        require_tenant(principal, "tenant-456")

    def test_require_tenant_different(self):
        """Test require_tenant raises for different tenant"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": [],
            "scopes": [],
        }

        with pytest.raises(HTTPException) as exc_info:
            require_tenant(principal, "tenant-789")

        assert exc_info.value.status_code == 403

    def test_require_tenant_super_admin_bypass(self):
        """Test super admin can bypass tenant check"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["super_admin"],
            "scopes": [],
        }

        # Should not raise
        require_tenant(principal, "tenant-789")


class TestRequireResourceAccess:
    """Test combined resource access check"""

    def test_require_resource_access_passes(self):
        """Test passes with correct permission and tenant"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        require_resource_access(
            principal,
            Permission.FIELDOPS_TASK_READ,
            "tenant-456",
        )

    def test_require_resource_access_wrong_tenant(self):
        """Test fails with wrong tenant"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["admin"],
            "scopes": [],
        }

        with pytest.raises(HTTPException):
            require_resource_access(
                principal,
                Permission.FIELDOPS_TASK_READ,
                "tenant-789",
            )


class TestRequireRole:
    """Test role requirement"""

    def test_require_role_passes(self):
        """Test require_role passes with correct role"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["admin"],
            "scopes": [],
        }

        require_role(principal, "admin")

    def test_require_role_raises(self):
        """Test require_role raises without role"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        with pytest.raises(HTTPException):
            require_role(principal, "admin")


class TestRequireAnyRole:
    """Test requiring any of multiple roles"""

    def test_require_any_role_passes(self):
        """Test passes with one matching role"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["supervisor"],
            "scopes": [],
        }

        require_any_role(principal, ["manager", "supervisor", "admin"])

    def test_require_any_role_raises(self):
        """Test raises with no matching role"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["viewer"],
            "scopes": [],
        }

        with pytest.raises(HTTPException):
            require_any_role(principal, ["manager", "admin"])


class TestRequireOwnerOrPermission:
    """Test owner or permission check"""

    def test_owner_can_access(self):
        """Test owner can access their own resource"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["viewer"],
            "scopes": [],
        }

        # Owner can access even without permission
        require_owner_or_permission(
            principal,
            "user-123",  # Same as principal sub
            Permission.ADMIN_USERS_UPDATE,
        )

    def test_non_owner_needs_permission(self):
        """Test non-owner needs explicit permission"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["admin"],
            "scopes": [],
        }

        # Non-owner with permission can access
        require_owner_or_permission(
            principal,
            "user-456",  # Different user
            Permission.ADMIN_USERS_UPDATE,
        )

    def test_non_owner_without_permission_denied(self):
        """Test non-owner without permission is denied"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["viewer"],
            "scopes": [],
        }

        with pytest.raises(HTTPException):
            require_owner_or_permission(
                principal,
                "user-456",  # Different user
                Permission.ADMIN_USERS_UPDATE,
            )
