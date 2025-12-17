"""
SAHOOL RBAC Unit Tests
Tests for Role-Based Access Control without I/O
"""

import pytest

from shared.security.rbac import (
    Permission,
    Role,
    can_access_resource,
    get_all_permissions,
    get_role_permissions,
    has_all_permissions,
    has_any_permission,
    has_permission,
    is_same_tenant,
)


class TestGetRolePermissions:
    """Tests for get_role_permissions function"""

    def test_viewer_has_read_permissions(self):
        """Viewer role should have read-only permissions"""
        perms = get_role_permissions(Role.VIEWER)

        assert Permission.FIELDOPS_TASK_READ in perms
        assert Permission.FIELDOPS_FIELD_READ in perms
        assert Permission.NDVI_READ in perms
        assert Permission.WEATHER_READ in perms

    def test_viewer_lacks_write_permissions(self):
        """Viewer role should not have write permissions"""
        perms = get_role_permissions(Role.VIEWER)

        assert Permission.FIELDOPS_TASK_CREATE not in perms
        assert Permission.FIELDOPS_TASK_DELETE not in perms
        assert Permission.FIELDOPS_FIELD_CREATE not in perms

    def test_worker_has_task_update(self):
        """Worker role should be able to update and complete tasks"""
        perms = get_role_permissions(Role.WORKER)

        assert Permission.FIELDOPS_TASK_UPDATE in perms
        assert Permission.FIELDOPS_TASK_COMPLETE in perms
        assert Permission.CHAT_WRITE in perms

    def test_supervisor_can_create_tasks(self):
        """Supervisor should be able to create and assign tasks"""
        perms = get_role_permissions(Role.SUPERVISOR)

        assert Permission.FIELDOPS_TASK_CREATE in perms
        assert Permission.FIELDOPS_TASK_ASSIGN in perms

    def test_manager_has_full_field_control(self):
        """Manager should have full CRUD on fields"""
        perms = get_role_permissions(Role.MANAGER)

        assert Permission.FIELDOPS_FIELD_READ in perms
        assert Permission.FIELDOPS_FIELD_CREATE in perms
        assert Permission.FIELDOPS_FIELD_UPDATE in perms
        assert Permission.FIELDOPS_FIELD_DELETE in perms

    def test_admin_has_user_management(self):
        """Admin should be able to manage users"""
        perms = get_role_permissions(Role.ADMIN)

        assert Permission.ADMIN_USERS_READ in perms
        assert Permission.ADMIN_USERS_CREATE in perms
        assert Permission.ADMIN_USERS_UPDATE in perms
        assert Permission.ADMIN_USERS_DELETE in perms

    def test_super_admin_has_tenant_management(self):
        """Only super_admin should have tenant management"""
        super_perms = get_role_permissions(Role.SUPER_ADMIN)
        admin_perms = get_role_permissions(Role.ADMIN)

        assert Permission.ADMIN_TENANT_MANAGE in super_perms
        assert Permission.ADMIN_TENANT_MANAGE not in admin_perms

    def test_unknown_role_returns_empty(self):
        """Unknown role should return empty set"""
        perms = get_role_permissions("unknown_role")

        assert perms == set()


class TestGetAllPermissions:
    """Tests for get_all_permissions function"""

    def test_combines_roles_and_scopes(self):
        """Should combine permissions from roles and explicit scopes"""
        roles = [Role.VIEWER]
        scopes = [Permission.FIELDOPS_TASK_CREATE]  # Not in viewer role

        perms = get_all_permissions(roles, scopes)

        assert Permission.FIELDOPS_TASK_READ in perms  # From role
        assert Permission.FIELDOPS_TASK_CREATE in perms  # From scope

    def test_multiple_roles_union(self):
        """Multiple roles should have union of permissions"""
        roles = [Role.VIEWER, Role.WORKER]
        scopes = []

        perms = get_all_permissions(roles, scopes)

        # Worker-specific
        assert Permission.FIELDOPS_TASK_UPDATE in perms
        assert Permission.CHAT_WRITE in perms


class TestHasPermission:
    """Tests for has_permission function"""

    def test_worker_has_task_read(self, test_principal):
        """Worker should have task read permission"""
        test_principal["roles"] = ["worker"]

        assert has_permission(test_principal, Permission.FIELDOPS_TASK_READ) is True

    def test_worker_lacks_task_delete(self, test_principal):
        """Worker should not have task delete permission"""
        test_principal["roles"] = ["worker"]

        assert has_permission(test_principal, Permission.FIELDOPS_TASK_DELETE) is False

    def test_admin_bypass(self, admin_principal):
        """Admin should have all permissions (except tenant manage)"""
        assert has_permission(admin_principal, Permission.FIELDOPS_TASK_DELETE) is True
        assert has_permission(admin_principal, Permission.ADMIN_USERS_DELETE) is True

    def test_admin_lacks_tenant_manage(self, admin_principal):
        """Admin should not have tenant management"""
        assert has_permission(admin_principal, Permission.ADMIN_TENANT_MANAGE) is False

    def test_super_admin_has_tenant_manage(self):
        """Super admin should have tenant management"""
        principal = {"roles": ["super_admin"], "scopes": []}

        assert has_permission(principal, Permission.ADMIN_TENANT_MANAGE) is True

    def test_explicit_scope_grants_permission(self, test_principal):
        """Explicit scope should grant permission not in role"""
        test_principal["roles"] = ["viewer"]
        test_principal["scopes"] = [Permission.FIELDOPS_TASK_DELETE]

        assert has_permission(test_principal, Permission.FIELDOPS_TASK_DELETE) is True


class TestHasAnyPermission:
    """Tests for has_any_permission function"""

    def test_returns_true_if_any_match(self, test_principal):
        """Should return True if any permission matches"""
        test_principal["roles"] = ["worker"]

        result = has_any_permission(
            test_principal,
            [Permission.FIELDOPS_TASK_READ, Permission.ADMIN_TENANT_MANAGE],
        )

        assert result is True

    def test_returns_false_if_none_match(self, test_principal):
        """Should return False if no permissions match"""
        test_principal["roles"] = ["viewer"]

        result = has_any_permission(
            test_principal,
            [Permission.FIELDOPS_TASK_DELETE, Permission.ADMIN_USERS_DELETE],
        )

        assert result is False


class TestHasAllPermissions:
    """Tests for has_all_permissions function"""

    def test_returns_true_if_all_match(self, test_principal):
        """Should return True if all permissions match"""
        test_principal["roles"] = ["worker"]

        result = has_all_permissions(
            test_principal,
            [Permission.FIELDOPS_TASK_READ, Permission.FIELDOPS_TASK_UPDATE],
        )

        assert result is True

    def test_returns_false_if_any_missing(self, test_principal):
        """Should return False if any permission is missing"""
        test_principal["roles"] = ["worker"]

        result = has_all_permissions(
            test_principal,
            [Permission.FIELDOPS_TASK_READ, Permission.FIELDOPS_TASK_DELETE],
        )

        assert result is False


class TestIsSameTenant:
    """Tests for is_same_tenant function"""

    def test_same_tenant_returns_true(self, test_principal, test_tenant_id):
        """Should return True for same tenant"""
        assert is_same_tenant(test_principal, test_tenant_id) is True

    def test_different_tenant_returns_false(self, test_principal):
        """Should return False for different tenant"""
        assert is_same_tenant(test_principal, "different-tenant") is False


class TestCanAccessResource:
    """Tests for can_access_resource function"""

    def test_same_tenant_with_permission(self, test_principal, test_tenant_id):
        """Should allow access for same tenant with permission"""
        test_principal["roles"] = ["worker"]

        result = can_access_resource(
            test_principal,
            Permission.FIELDOPS_TASK_READ,
            test_tenant_id,
        )

        assert result is True

    def test_same_tenant_without_permission(self, test_principal, test_tenant_id):
        """Should deny access for same tenant without permission"""
        test_principal["roles"] = ["viewer"]

        result = can_access_resource(
            test_principal,
            Permission.FIELDOPS_TASK_DELETE,
            test_tenant_id,
        )

        assert result is False

    def test_cross_tenant_denied_for_regular_user(self, test_principal):
        """Should deny cross-tenant access for non-super_admin"""
        test_principal["roles"] = ["admin"]

        result = can_access_resource(
            test_principal,
            Permission.FIELDOPS_TASK_READ,
            "different-tenant",
        )

        assert result is False

    def test_cross_tenant_allowed_for_super_admin(self):
        """Should allow cross-tenant access for super_admin"""
        principal = {"tid": "tenant-1", "roles": ["super_admin"], "scopes": []}

        result = can_access_resource(
            principal,
            Permission.FIELDOPS_TASK_READ,
            "tenant-2",  # Different tenant
        )

        assert result is True
