"""
Tests for RBAC Module
"""

from shared.security.rbac import (
    Permission,
    Role,
    can_access_resource,
    get_role_permissions,
    has_all_permissions,
    has_any_permission,
    has_permission,
    is_same_tenant,
)


class TestRolePermissions:
    """Test role permission definitions"""

    def test_viewer_has_read_permissions(self):
        """Test viewer role has read-only permissions"""
        viewer_perms = get_role_permissions(Role.VIEWER)

        assert Permission.FIELDOPS_TASK_READ in viewer_perms
        assert Permission.FIELDOPS_FIELD_READ in viewer_perms
        assert Permission.NDVI_READ in viewer_perms

        # Should NOT have write permissions
        assert Permission.FIELDOPS_TASK_CREATE not in viewer_perms
        assert Permission.FIELDOPS_TASK_DELETE not in viewer_perms

    def test_worker_has_complete_permission(self):
        """Test worker can complete tasks"""
        worker_perms = get_role_permissions(Role.WORKER)

        assert Permission.FIELDOPS_TASK_COMPLETE in worker_perms
        assert Permission.FIELDOPS_TASK_UPDATE in worker_perms
        assert Permission.CHAT_WRITE in worker_perms

    def test_manager_has_full_crud(self):
        """Test manager has full CRUD on resources"""
        manager_perms = get_role_permissions(Role.MANAGER)

        assert Permission.FIELDOPS_TASK_CREATE in manager_perms
        assert Permission.FIELDOPS_TASK_UPDATE in manager_perms
        assert Permission.FIELDOPS_TASK_DELETE in manager_perms
        assert Permission.FIELDOPS_FIELD_CREATE in manager_perms

    def test_admin_has_user_management(self):
        """Test admin can manage users"""
        admin_perms = get_role_permissions(Role.ADMIN)

        assert Permission.ADMIN_USERS_CREATE in admin_perms
        assert Permission.ADMIN_USERS_UPDATE in admin_perms
        assert Permission.ADMIN_USERS_DELETE in admin_perms
        assert Permission.ADMIN_AUDIT_READ in admin_perms

    def test_super_admin_has_tenant_management(self):
        """Test super admin has all permissions"""
        super_perms = get_role_permissions(Role.SUPER_ADMIN)

        assert Permission.ADMIN_TENANT_MANAGE in super_perms


class TestHasPermission:
    """Test permission checking"""

    def test_has_permission_from_role(self):
        """Test permission granted through role"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        assert has_permission(principal, Permission.FIELDOPS_TASK_COMPLETE)
        assert has_permission(principal, Permission.FIELDOPS_TASK_READ)

    def test_has_permission_from_scope(self):
        """Test permission granted through explicit scope"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": [],
            "scopes": ["fieldops:task.delete"],
        }

        assert has_permission(principal, "fieldops:task.delete")

    def test_no_permission(self):
        """Test permission denied"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["viewer"],
            "scopes": [],
        }

        assert not has_permission(principal, Permission.FIELDOPS_TASK_DELETE)
        assert not has_permission(principal, Permission.ADMIN_USERS_CREATE)

    def test_admin_bypass(self):
        """Test admin role bypasses most permission checks"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["admin"],
            "scopes": [],
        }

        assert has_permission(principal, Permission.FIELDOPS_TASK_DELETE)
        assert has_permission(principal, Permission.ADMIN_USERS_CREATE)
        # Admin cannot manage tenants
        assert not has_permission(principal, Permission.ADMIN_TENANT_MANAGE)

    def test_super_admin_has_all(self):
        """Test super admin has all permissions"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["super_admin"],
            "scopes": [],
        }

        assert has_permission(principal, Permission.ADMIN_TENANT_MANAGE)
        assert has_permission(principal, Permission.FIELDOPS_TASK_DELETE)


class TestHasAnyPermission:
    """Test checking for any permission"""

    def test_has_any_one_match(self):
        """Test returns true when one permission matches"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        result = has_any_permission(
            principal,
            [Permission.FIELDOPS_TASK_DELETE, Permission.FIELDOPS_TASK_COMPLETE],
        )

        assert result is True

    def test_has_any_none_match(self):
        """Test returns false when no permission matches"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["viewer"],
            "scopes": [],
        }

        result = has_any_permission(
            principal,
            [Permission.FIELDOPS_TASK_DELETE, Permission.ADMIN_USERS_CREATE],
        )

        assert result is False


class TestHasAllPermissions:
    """Test checking for all permissions"""

    def test_has_all_when_all_match(self):
        """Test returns true when all permissions match"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["manager"],
            "scopes": [],
        }

        result = has_all_permissions(
            principal,
            [Permission.FIELDOPS_TASK_CREATE, Permission.FIELDOPS_TASK_DELETE],
        )

        assert result is True

    def test_has_all_when_some_missing(self):
        """Test returns false when some permissions missing"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        result = has_all_permissions(
            principal,
            [Permission.FIELDOPS_TASK_COMPLETE, Permission.FIELDOPS_TASK_DELETE],
        )

        assert result is False


class TestTenantIsolation:
    """Test tenant isolation checks"""

    def test_same_tenant(self):
        """Test same tenant check"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": [],
            "scopes": [],
        }

        assert is_same_tenant(principal, "tenant-456")
        assert not is_same_tenant(principal, "tenant-789")

    def test_can_access_resource_same_tenant(self):
        """Test resource access in same tenant"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["worker"],
            "scopes": [],
        }

        assert can_access_resource(
            principal,
            Permission.FIELDOPS_TASK_READ,
            "tenant-456",
        )

    def test_cannot_access_resource_different_tenant(self):
        """Test resource access denied for different tenant"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["admin"],
            "scopes": [],
        }

        assert not can_access_resource(
            principal,
            Permission.FIELDOPS_TASK_READ,
            "tenant-789",
        )

    def test_super_admin_cross_tenant(self):
        """Test super admin can access cross-tenant"""
        principal = {
            "sub": "user-123",
            "tid": "tenant-456",
            "roles": ["super_admin"],
            "scopes": [],
        }

        assert can_access_resource(
            principal,
            Permission.FIELDOPS_TASK_READ,
            "tenant-789",
        )
