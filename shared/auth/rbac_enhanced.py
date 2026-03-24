"""
Enhanced Role-Based Access Control (RBAC) for SAHOOL Platform
التحكم في الوصول المحسن القائم على الدور لمنصة سهول

This module provides advanced RBAC features:
- Hierarchical roles (admin > manager > user)
- Permission inheritance
- Resource-level permissions
- Dynamic permission resolution
- Permission caching for performance
- Attribute-Based Access Control (ABAC) extensions

Security Features:
- Principle of least privilege
- Explicit deny rules
- Permission auditing
- Role hierarchy validation
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from functools import lru_cache
from typing import Any

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Role Definitions
# ─────────────────────────────────────────────────────────────────────────────


class SystemRole(StrEnum):
    """
    System roles with hierarchy.
    أدوار النظام مع التسلسل الهرمي.

    Hierarchy (high to low):
    1. SUPER_ADMIN - Full system access
    2. TENANT_ADMIN - Full tenant access
    3. ADMIN - Administrative access
    4. MANAGER - Management access
    5. SUPERVISOR - Supervisory access
    6. OPERATOR - Operational access
    7. FARMER - Standard farmer access
    8. VIEWER - Read-only access
    9. GUEST - Limited public access
    """

    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    OPERATOR = "operator"
    FARMER = "farmer"
    VIEWER = "viewer"
    GUEST = "guest"


# Role hierarchy - higher roles inherit lower role permissions
ROLE_HIERARCHY: dict[SystemRole, list[SystemRole]] = {
    SystemRole.SUPER_ADMIN: [
        SystemRole.TENANT_ADMIN,
        SystemRole.ADMIN,
        SystemRole.MANAGER,
        SystemRole.SUPERVISOR,
        SystemRole.OPERATOR,
        SystemRole.FARMER,
        SystemRole.VIEWER,
        SystemRole.GUEST,
    ],
    SystemRole.TENANT_ADMIN: [
        SystemRole.ADMIN,
        SystemRole.MANAGER,
        SystemRole.SUPERVISOR,
        SystemRole.OPERATOR,
        SystemRole.FARMER,
        SystemRole.VIEWER,
        SystemRole.GUEST,
    ],
    SystemRole.ADMIN: [
        SystemRole.MANAGER,
        SystemRole.SUPERVISOR,
        SystemRole.OPERATOR,
        SystemRole.FARMER,
        SystemRole.VIEWER,
        SystemRole.GUEST,
    ],
    SystemRole.MANAGER: [
        SystemRole.SUPERVISOR,
        SystemRole.OPERATOR,
        SystemRole.FARMER,
        SystemRole.VIEWER,
        SystemRole.GUEST,
    ],
    SystemRole.SUPERVISOR: [
        SystemRole.OPERATOR,
        SystemRole.FARMER,
        SystemRole.VIEWER,
        SystemRole.GUEST,
    ],
    SystemRole.OPERATOR: [
        SystemRole.FARMER,
        SystemRole.VIEWER,
        SystemRole.GUEST,
    ],
    SystemRole.FARMER: [
        SystemRole.VIEWER,
        SystemRole.GUEST,
    ],
    SystemRole.VIEWER: [
        SystemRole.GUEST,
    ],
    SystemRole.GUEST: [],
}


# ─────────────────────────────────────────────────────────────────────────────
# Permission Definitions
# ─────────────────────────────────────────────────────────────────────────────


class PermissionAction(StrEnum):
    """Standard permission actions"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"
    PUBLISH = "publish"
    ARCHIVE = "archive"
    RESTORE = "restore"
    ASSIGN = "assign"
    REVOKE = "revoke"
    EXECUTE = "execute"
    MANAGE = "manage"  # Full CRUD + special actions


class ResourceType(StrEnum):
    """Platform resource types"""

    # Farm resources
    FARM = "farm"
    FIELD = "field"
    CROP = "crop"
    EQUIPMENT = "equipment"
    INVENTORY = "inventory"

    # Data resources
    WEATHER = "weather"
    ANALYTICS = "analytics"
    REPORT = "report"
    ADVISORY = "advisory"
    NDVI = "ndvi"

    # User management
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    TEAM = "team"

    # Operations
    TASK = "task"
    SCHEDULE = "schedule"
    IRRIGATION = "irrigation"
    SPRAY = "spray"
    HARVEST = "harvest"

    # Business
    BILLING = "billing"
    SUBSCRIPTION = "subscription"
    NOTIFICATION = "notification"
    AUDIT = "audit"

    # System
    SYSTEM = "system"
    CONFIG = "config"
    TENANT = "tenant"


@dataclass
class Permission:
    """
    Permission definition.
    تعريف الإذن.

    Format: resource:action[:scope]
    Examples:
    - farm:read - Read any farm
    - farm:read:own - Read own farms only
    - farm:* - All farm permissions
    - *:read - Read all resources
    """

    resource: str
    action: str
    scope: str = "*"  # * = all, own = owner only, tenant = same tenant

    def __str__(self) -> str:
        if self.scope == "*":
            return f"{self.resource}:{self.action}"
        return f"{self.resource}:{self.action}:{self.scope}"

    @classmethod
    def from_string(cls, permission_str: str) -> Permission:
        """Parse permission from string"""
        parts = permission_str.split(":")
        if len(parts) == 2:
            return cls(resource=parts[0], action=parts[1])
        elif len(parts) == 3:
            return cls(resource=parts[0], action=parts[1], scope=parts[2])
        else:
            raise ValueError(f"Invalid permission format: {permission_str}")

    def matches(self, other: Permission) -> bool:
        """
        Check if this permission matches/covers another permission.
        Wildcards (*) match any value.
        """
        # Check resource match
        if self.resource != "*" and other.resource != "*":
            if self.resource != other.resource:
                return False

        # Check action match
        if self.action != "*" and other.action != "*":
            if self.action != other.action:
                return False

        # Check scope match (if scope is *, it covers all scopes)
        if self.scope != "*":
            if other.scope != "*" and self.scope != other.scope:
                return False

        return True


# ─────────────────────────────────────────────────────────────────────────────
# Default Role Permissions
# ─────────────────────────────────────────────────────────────────────────────

# Default permissions for each role (before inheritance)
DEFAULT_ROLE_PERMISSIONS: dict[SystemRole, list[str]] = {
    SystemRole.SUPER_ADMIN: [
        "*:*",  # All permissions
    ],
    SystemRole.TENANT_ADMIN: [
        "tenant:manage",
        "user:*",
        "role:*",
        "team:*",
        "billing:*",
        "subscription:*",
        "config:manage",
        "audit:read",
    ],
    SystemRole.ADMIN: [
        "user:*:tenant",
        "role:read",
        "team:*:tenant",
        "farm:*",
        "field:*",
        "crop:*",
        "equipment:*",
        "inventory:*",
        "task:*",
        "report:*",
        "analytics:*",
        "config:read",
    ],
    SystemRole.MANAGER: [
        "farm:*:own",
        "field:*:own",
        "crop:*:own",
        "equipment:*:own",
        "inventory:*:own",
        "task:*:own",
        "team:read:own",
        "user:read:own",
        "report:*:own",
        "analytics:read",
        "schedule:*:own",
    ],
    SystemRole.SUPERVISOR: [
        "farm:read:own",
        "field:*:own",
        "crop:*:own",
        "equipment:read:own",
        "inventory:read:own",
        "task:*:own",
        "schedule:*:own",
        "report:read:own",
    ],
    SystemRole.OPERATOR: [
        "farm:read:assigned",
        "field:read:assigned",
        "crop:update:assigned",
        "equipment:read:assigned",
        "task:read:assigned",
        "task:update:assigned",
        "irrigation:execute:assigned",
        "spray:execute:assigned",
    ],
    SystemRole.FARMER: [
        "farm:read:own",
        "field:read:own",
        "crop:read:own",
        "weather:read",
        "advisory:read:own",
        "ndvi:read:own",
        "task:read:own",
        "notification:read:own",
    ],
    SystemRole.VIEWER: [
        "farm:read:own",
        "field:read:own",
        "crop:read:own",
        "weather:read",
        "report:read:own",
    ],
    SystemRole.GUEST: [
        "weather:read",  # Public weather data only
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# RBAC Manager
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AccessContext:
    """
    Context for access control decision.
    سياق قرار التحكم في الوصول.
    """

    user_id: str
    user_roles: list[str]
    user_permissions: list[str] = field(default_factory=list)
    tenant_id: str | None = None
    resource_owner_id: str | None = None
    resource_tenant_id: str | None = None
    resource_type: str = ""
    resource_id: str = ""
    action: str = ""
    attributes: dict = field(default_factory=dict)


@dataclass
class AccessDecision:
    """
    Access control decision result.
    نتيجة قرار التحكم في الوصول.
    """

    allowed: bool
    reason: str
    reason_ar: str
    matched_permission: str | None = None
    checked_permissions: list[str] = field(default_factory=list)


class RBACManager:
    """
    Enhanced Role-Based Access Control Manager.
    مدير التحكم في الوصول المحسن القائم على الدور.

    Features:
    - Hierarchical role inheritance
    - Permission caching
    - Custom role/permission definitions
    - Scope-based access (own, tenant, all)
    - Attribute-based extensions

    Example:
        >>> rbac = RBACManager()
        >>> await rbac.initialize()
        >>>
        >>> # Check permission
        >>> decision = await rbac.check_permission(
        ...     user_id="user123",
        ...     user_roles=["farmer"],
        ...     resource="farm",
        ...     action="read",
        ...     resource_owner_id="user123"  # Checking own resource
        ... )
        >>> print(decision.allowed)  # True
        >>>
        >>> # Get effective permissions
        >>> permissions = await rbac.get_effective_permissions(["manager"])
    """

    # Redis key prefixes
    ROLE_PERMISSIONS_PREFIX = "rbac:role:"
    USER_PERMISSIONS_PREFIX = "rbac:user:"
    CACHE_PREFIX = "rbac:cache:"

    # Cache configuration
    CACHE_TTL = 300  # 5 minutes

    def __init__(self, redis_url: str | None = None):
        """
        Initialize RBAC manager.

        Args:
            redis_url: Redis connection URL
        """
        self._redis: aioredis.Redis | None = None
        self._redis_url = redis_url or getattr(config, "REDIS_URL", None) or self._build_redis_url()
        self._initialized = False

        # Custom role permissions (override defaults)
        self._custom_role_permissions: dict[str, list[str]] = {}

        # Deny rules (explicit denies)
        self._deny_rules: dict[str, list[str]] = {}

        # In-memory cache
        self._permission_cache: dict[str, tuple[list[str], float]] = {}

    def _build_redis_url(self) -> str:
        """Build Redis URL from configuration"""
        if hasattr(config, "REDIS_PASSWORD") and config.REDIS_PASSWORD:
            return (
                f"redis://:{config.REDIS_PASSWORD}@"
                f"{getattr(config, 'REDIS_HOST', 'localhost')}:"
                f"{getattr(config, 'REDIS_PORT', 6379)}/"
                f"{getattr(config, 'REDIS_DB', 0)}"
            )
        return (
            f"redis://{getattr(config, 'REDIS_HOST', 'localhost')}:"
            f"{getattr(config, 'REDIS_PORT', 6379)}/"
            f"{getattr(config, 'REDIS_DB', 0)}"
        )

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        if self._initialized:
            return

        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory RBAC storage")
            self._initialized = True
            return

        try:
            self._redis = await aioredis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            await self._redis.ping()
            self._initialized = True
            logger.info("RBAC manager initialized with Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory storage: {e}")
            self._redis = None
            self._initialized = True

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
        self._initialized = False

    # ─────────────────────────────────────────────────────────────────────────
    # Permission Checking
    # ─────────────────────────────────────────────────────────────────────────

    async def check_permission(
        self,
        user_id: str,
        user_roles: list[str],
        resource: str,
        action: str,
        user_permissions: list[str] | None = None,
        tenant_id: str | None = None,
        resource_owner_id: str | None = None,
        resource_tenant_id: str | None = None,
        resource_id: str = "",
        attributes: dict | None = None,
    ) -> AccessDecision:
        """
        Check if user has permission to perform action on resource.
        التحقق مما إذا كان المستخدم لديه إذن لتنفيذ إجراء على المورد.

        Args:
            user_id: User ID
            user_roles: User's roles
            resource: Resource type (e.g., "farm", "field")
            action: Action to perform (e.g., "read", "update")
            user_permissions: Additional user-specific permissions
            tenant_id: User's tenant ID
            resource_owner_id: Resource owner's user ID
            resource_tenant_id: Resource's tenant ID
            resource_id: Specific resource ID
            attributes: Additional attributes for ABAC

        Returns:
            AccessDecision with allowed status and reason
        """
        if not self._initialized:
            await self.initialize()

        context = AccessContext(
            user_id=user_id,
            user_roles=user_roles,
            user_permissions=user_permissions or [],
            tenant_id=tenant_id,
            resource_owner_id=resource_owner_id,
            resource_tenant_id=resource_tenant_id,
            resource_type=resource,
            resource_id=resource_id,
            action=action,
            attributes=attributes or {},
        )

        # Check explicit deny rules first
        deny_decision = await self._check_deny_rules(context)
        if deny_decision:
            return deny_decision

        # Get effective permissions for user's roles
        effective_permissions = await self.get_effective_permissions(
            user_roles,
            user_permissions,
        )

        # Build required permission variations
        required_permissions = self._build_required_permissions(resource, action, context)

        # Check each required permission
        for required in required_permissions:
            for perm_str in effective_permissions:
                perm = Permission.from_string(perm_str)
                if perm.matches(required):
                    # Check scope if applicable
                    if self._check_scope(perm, context):
                        return AccessDecision(
                            allowed=True,
                            reason=f"Permission granted via {perm_str}",
                            reason_ar=f"تم منح الإذن عبر {perm_str}",
                            matched_permission=perm_str,
                            checked_permissions=required_permissions,
                        )

        # No matching permission found
        return AccessDecision(
            allowed=False,
            reason=f"No permission found for {resource}:{action}",
            reason_ar=f"لم يتم العثور على إذن لـ {resource}:{action}",
            matched_permission=None,
            checked_permissions=required_permissions,
        )

    async def _check_deny_rules(self, context: AccessContext) -> AccessDecision | None:
        """Check explicit deny rules (denies take precedence)"""
        for user_id, denied_permissions in self._deny_rules.items():
            if user_id == context.user_id or user_id == "*":
                for denied in denied_permissions:
                    if self._permission_matches_context(denied, context):
                        return AccessDecision(
                            allowed=False,
                            reason=f"Explicitly denied by rule: {denied}",
                            reason_ar=f"مرفوض صراحة بواسطة القاعدة: {denied}",
                            matched_permission=denied,
                        )
        return None

    def _build_required_permissions(
        self,
        resource: str,
        action: str,
        context: AccessContext,
    ) -> list[Permission]:
        """Build list of required permissions to check"""
        permissions = []

        # Specific permission
        permissions.append(Permission(resource=resource, action=action, scope="*"))

        # Wildcard action
        permissions.append(Permission(resource=resource, action="*", scope="*"))

        # Wildcard resource
        permissions.append(Permission(resource="*", action=action, scope="*"))

        # Full wildcard
        permissions.append(Permission(resource="*", action="*", scope="*"))

        # Manage action covers all actions
        permissions.append(Permission(resource=resource, action="manage", scope="*"))

        return permissions

    def _check_scope(self, permission: Permission, context: AccessContext) -> bool:
        """Check if permission scope is satisfied"""
        scope = permission.scope

        if scope == "*":
            # All resources allowed
            return True

        if scope == "own":
            # Only own resources
            return context.resource_owner_id == context.user_id

        if scope == "tenant":
            # Same tenant resources
            return context.tenant_id is not None and context.resource_tenant_id == context.tenant_id

        if scope == "assigned":
            # Resources assigned to user (check attributes)
            assigned_users = context.attributes.get("assigned_users", [])
            return context.user_id in assigned_users

        return False

    def _permission_matches_context(
        self,
        permission_str: str,
        context: AccessContext,
    ) -> bool:
        """Check if a permission string matches the context"""
        perm = Permission.from_string(permission_str)
        return (perm.resource == "*" or perm.resource == context.resource_type) and (
            perm.action == "*" or perm.action == context.action
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Permission Resolution
    # ─────────────────────────────────────────────────────────────────────────

    async def get_effective_permissions(
        self,
        roles: list[str],
        user_permissions: list[str] | None = None,
    ) -> list[str]:
        """
        Get all effective permissions for roles (with inheritance).
        الحصول على جميع الأذونات الفعالة للأدوار (مع الوراثة).

        Args:
            roles: List of role names
            user_permissions: Additional user-specific permissions

        Returns:
            List of all effective permission strings
        """
        if not self._initialized:
            await self.initialize()

        # Check cache
        cache_key = ":".join(sorted(roles))
        if cache_key in self._permission_cache:
            perms, timestamp = self._permission_cache[cache_key]
            if time.time() - timestamp < self.CACHE_TTL:
                # Add user permissions and return
                return list(set(perms + (user_permissions or [])))

        all_permissions = set()

        for role in roles:
            # Get role's direct permissions
            role_perms = await self._get_role_permissions(role)
            all_permissions.update(role_perms)

            # Get inherited permissions from role hierarchy
            inherited_roles = self._get_inherited_roles(role)
            for inherited_role in inherited_roles:
                inherited_perms = await self._get_role_permissions(inherited_role)
                all_permissions.update(inherited_perms)

        # Cache the result
        result = list(all_permissions)
        self._permission_cache[cache_key] = (result, time.time())

        # Add user-specific permissions
        if user_permissions:
            result = list(set(result + user_permissions))

        return result

    async def _get_role_permissions(self, role: str) -> list[str]:
        """Get permissions for a specific role"""
        # Check custom role permissions first
        if role in self._custom_role_permissions:
            return self._custom_role_permissions[role]

        # Check default role permissions
        try:
            system_role = SystemRole(role)
            return DEFAULT_ROLE_PERMISSIONS.get(system_role, [])
        except ValueError:
            # Custom role not in system roles
            if self._redis:
                key = f"{self.ROLE_PERMISSIONS_PREFIX}{role}"
                perms = await self._redis.smembers(key)
                return list(perms) if perms else []
            return []

    def _get_inherited_roles(self, role: str) -> list[str]:
        """Get all roles inherited by a role"""
        try:
            system_role = SystemRole(role)
            inherited = ROLE_HIERARCHY.get(system_role, [])
            return [r.value for r in inherited]
        except ValueError:
            return []

    # ─────────────────────────────────────────────────────────────────────────
    # Role Management
    # ─────────────────────────────────────────────────────────────────────────

    async def create_custom_role(
        self,
        role_name: str,
        permissions: list[str],
        inherits_from: str | None = None,
    ) -> bool:
        """
        Create a custom role with permissions.
        إنشاء دور مخصص مع الأذونات.

        Args:
            role_name: Name for the custom role
            permissions: List of permission strings
            inherits_from: Optional parent role to inherit from

        Returns:
            True if created successfully
        """
        if not self._initialized:
            await self.initialize()

        # Validate parent role if specified
        if inherits_from:
            try:
                SystemRole(inherits_from)
            except ValueError:
                # Check if it's an existing custom role
                if inherits_from not in self._custom_role_permissions:
                    return False

        # Store custom role permissions
        self._custom_role_permissions[role_name] = permissions

        if self._redis:
            key = f"{self.ROLE_PERMISSIONS_PREFIX}{role_name}"
            if permissions:
                await self._redis.sadd(key, *permissions)

        # Clear cache
        self._permission_cache.clear()

        logger.info(f"Created custom role: {role_name} with {len(permissions)} permissions")
        return True

    async def add_permission_to_role(self, role_name: str, permission: str) -> bool:
        """Add permission to a role"""
        if not self._initialized:
            await self.initialize()

        if role_name in self._custom_role_permissions:
            if permission not in self._custom_role_permissions[role_name]:
                self._custom_role_permissions[role_name].append(permission)
        else:
            self._custom_role_permissions[role_name] = [permission]

        if self._redis:
            key = f"{self.ROLE_PERMISSIONS_PREFIX}{role_name}"
            await self._redis.sadd(key, permission)

        self._permission_cache.clear()
        return True

    async def remove_permission_from_role(self, role_name: str, permission: str) -> bool:
        """Remove permission from a role"""
        if not self._initialized:
            await self.initialize()

        if role_name in self._custom_role_permissions:
            if permission in self._custom_role_permissions[role_name]:
                self._custom_role_permissions[role_name].remove(permission)

        if self._redis:
            key = f"{self.ROLE_PERMISSIONS_PREFIX}{role_name}"
            await self._redis.srem(key, permission)

        self._permission_cache.clear()
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Deny Rules
    # ─────────────────────────────────────────────────────────────────────────

    async def add_deny_rule(
        self,
        user_id: str,  # or "*" for all users
        permission: str,
    ) -> bool:
        """
        Add an explicit deny rule.
        إضافة قاعدة رفض صريحة.

        Deny rules always take precedence over allow rules.

        Args:
            user_id: User ID or "*" for all users
            permission: Permission to deny

        Returns:
            True if added successfully
        """
        if user_id not in self._deny_rules:
            self._deny_rules[user_id] = []

        if permission not in self._deny_rules[user_id]:
            self._deny_rules[user_id].append(permission)

        logger.warning(f"Added deny rule: {user_id} -> {permission}")
        return True

    async def remove_deny_rule(self, user_id: str, permission: str) -> bool:
        """Remove a deny rule"""
        if user_id in self._deny_rules:
            if permission in self._deny_rules[user_id]:
                self._deny_rules[user_id].remove(permission)
                return True
        return False

    # ─────────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def get_role_permissions(self, role: str) -> list[str]:
        """Get direct permissions for a role (without inheritance)"""
        return await self._get_role_permissions(role)

    async def get_all_permissions_for_role(self, role: str) -> list[str]:
        """Get all permissions including inherited"""
        return await self.get_effective_permissions([role])

    def get_role_hierarchy(self, role: str) -> list[str]:
        """Get role hierarchy (parent roles)"""
        return self._get_inherited_roles(role)

    def is_role_higher(self, role1: str, role2: str) -> bool:
        """Check if role1 is higher than role2 in hierarchy"""
        try:
            r1 = SystemRole(role1)
            r2 = SystemRole(role2)
            return r2 in ROLE_HIERARCHY.get(r1, [])
        except ValueError:
            return False


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Dependencies
# ─────────────────────────────────────────────────────────────────────────────


def require_permission(
    resource: str,
    action: str,
    scope: str = "*",
) -> Callable:
    """
    Dependency to require specific permission.
    تبعية تتطلب إذنا محددا.

    Args:
        resource: Resource type
        action: Required action
        scope: Permission scope

    Returns:
        Dependency function

    Example:
        >>> @app.delete("/farms/{farm_id}")
        ... async def delete_farm(
        ...     farm_id: str,
        ...     user: User = Depends(require_permission("farm", "delete"))
        ... ):
        ...     pass
    """
    from fastapi import Depends, HTTPException, Request, status

    from .dependencies import get_current_active_user
    from .models import User

    async def permission_checker(
        request: Request,
        user: User = Depends(get_current_active_user),
    ) -> User:
        rbac = await get_rbac_manager()

        # Get resource owner if available from path params
        resource_owner_id = None
        if hasattr(request.state, "resource_owner_id"):
            resource_owner_id = request.state.resource_owner_id

        decision = await rbac.check_permission(
            user_id=user.id,
            user_roles=user.roles,
            resource=resource,
            action=action,
            user_permissions=user.permissions,
            tenant_id=user.tenant_id,
            resource_owner_id=resource_owner_id,
        )

        if not decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "insufficient_permissions",
                    "message": decision.reason,
                    "message_ar": decision.reason_ar,
                },
            )

        return user

    return permission_checker


# ─────────────────────────────────────────────────────────────────────────────
# Global Instance
# ─────────────────────────────────────────────────────────────────────────────

_rbac_manager: RBACManager | None = None


async def get_rbac_manager() -> RBACManager:
    """
    Get global RBAC manager.
    الحصول على مدير RBAC العام.

    Returns:
        RBACManager instance
    """
    global _rbac_manager

    if _rbac_manager is None:
        _rbac_manager = RBACManager()
        await _rbac_manager.initialize()

    return _rbac_manager
