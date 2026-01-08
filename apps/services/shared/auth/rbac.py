"""
Role-Based Access Control (RBAC) Manager
مدير التحكم في الوصول المبني على الأدوار
"""

import logging
from collections.abc import Callable
from functools import wraps

from .models import SYSTEM_ROLES, Permission, Role, User

logger = logging.getLogger(__name__)


class RBACManager:
    """
    Manages roles, permissions, and access control
    إدارة الأدوار والصلاحيات والتحكم في الوصول
    """

    def __init__(self):
        self._roles: dict[str, Role] = dict(SYSTEM_ROLES)
        self._permissions: dict[str, Permission] = {}
        self._role_hierarchy: dict[str, list[str]] = {
            "super_admin": [
                "tenant_admin",
                "farm_manager",
                "field_operator",
                "agronomist",
                "viewer",
            ],
            "tenant_admin": ["farm_manager", "field_operator", "agronomist", "viewer"],
            "farm_manager": ["field_operator", "viewer"],
            "agronomist": ["viewer"],
        }

    def get_role(self, role_name: str) -> Role | None:
        """Get a role by name"""
        return self._roles.get(role_name)

    def register_role(self, role: Role) -> None:
        """Register a new role"""
        self._roles[role.name] = role
        logger.info(f"Registered role: {role.name}")

    def register_permission(self, permission: Permission) -> None:
        """Register a new permission"""
        self._permissions[permission.id] = permission
        logger.debug(f"Registered permission: {permission.id}")

    def get_inherited_roles(self, role_name: str) -> list[str]:
        """Get all roles inherited by a role"""
        inherited = []
        if role_name in self._role_hierarchy:
            for child in self._role_hierarchy[role_name]:
                inherited.append(child)
                inherited.extend(self.get_inherited_roles(child))
        return inherited

    def get_effective_permissions(self, user: User) -> set[Permission]:
        """
        Get all effective permissions for a user including inherited ones
        الحصول على جميع الصلاحيات الفعالة للمستخدم بما في ذلك الموروثة
        """
        permissions = set()

        for role in user.roles:
            # Direct permissions
            permissions.update(role.permissions)

            # Inherited permissions from child roles
            for inherited_role_name in self.get_inherited_roles(role.name):
                inherited_role = self.get_role(inherited_role_name)
                if inherited_role:
                    permissions.update(inherited_role.permissions)

        return permissions

    def can_access_resource(
        self,
        user: User,
        resource: str,
        action: str,
    ) -> bool:
        """
        Check if user can access a resource with specific action
        التحقق مما إذا كان المستخدم يمكنه الوصول إلى مورد بإجراء محدد
        """
        # Super admin has access to everything
        if user.has_role("super_admin"):
            return True

        effective_permissions = self.get_effective_permissions(user)

        for permission in effective_permissions:
            # Check for wildcard permission
            if "*" in permission.actions:
                if permission.resource == resource or permission.resource == "*":
                    return True

            # Check for specific permission
            if permission.resource == resource and action in permission.actions:
                return True

        return False

    def check_permission(self, user: User, permission_id: str) -> bool:
        """
        Check if user has a specific permission
        التحقق مما إذا كان المستخدم لديه صلاحية محددة
        """
        if user.has_role("super_admin"):
            return True

        effective_permissions = self.get_effective_permissions(user)
        return any(p.id == permission_id for p in effective_permissions)


class PermissionChecker:
    """
    Permission checking utilities
    أدوات التحقق من الصلاحيات
    """

    def __init__(self, rbac: RBACManager | None = None):
        self.rbac = rbac or RBACManager()

    def has_permission(self, user: User, permission_id: str) -> bool:
        """Check if user has permission"""
        return self.rbac.check_permission(user, permission_id)

    def has_any_permission(self, user: User, permission_ids: list[str]) -> bool:
        """Check if user has any of the permissions"""
        return any(self.has_permission(user, p) for p in permission_ids)

    def has_all_permissions(self, user: User, permission_ids: list[str]) -> bool:
        """Check if user has all permissions"""
        return all(self.has_permission(user, p) for p in permission_ids)

    def can_access(self, user: User, resource: str, action: str) -> bool:
        """Check if user can access resource"""
        return self.rbac.can_access_resource(user, resource, action)

    def assert_permission(self, user: User, permission_id: str) -> None:
        """Assert user has permission, raise if not"""
        if not self.has_permission(user, permission_id):
            raise PermissionError(f"User {user.id} does not have permission: {permission_id}")

    def assert_access(self, user: User, resource: str, action: str) -> None:
        """Assert user can access resource, raise if not"""
        if not self.can_access(user, resource, action):
            raise PermissionError(f"User {user.id} cannot {action} resource: {resource}")


# Global instances
_rbac_manager: RBACManager | None = None
_permission_checker: PermissionChecker | None = None


def get_rbac_manager() -> RBACManager:
    """Get or create the RBAC manager"""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager


def get_permission_checker() -> PermissionChecker:
    """Get or create the permission checker"""
    global _permission_checker
    if _permission_checker is None:
        _permission_checker = PermissionChecker(get_rbac_manager())
    return _permission_checker


def requires_permission(permission_id: str) -> Callable:
    """
    Decorator to require a specific permission
    ديكوراتور لطلب صلاحية محددة
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # User should be in kwargs or first arg
            user = kwargs.get("user") or (args[0] if args else None)
            if user is None:
                raise ValueError("User not found in function arguments")

            checker = get_permission_checker()
            checker.assert_permission(user, permission_id)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def requires_role(role_name: str) -> Callable:
    """
    Decorator to require a specific role
    ديكوراتور لطلب دور محدد
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.get("user") or (args[0] if args else None)
            if user is None:
                raise ValueError("User not found in function arguments")

            if not user.has_role(role_name):
                raise PermissionError(f"User {user.id} does not have role: {role_name}")

            return func(*args, **kwargs)

        return wrapper

    return decorator
