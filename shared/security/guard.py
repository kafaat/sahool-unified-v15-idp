"""
Authorization Guards
FastAPI-compatible permission enforcement helpers
"""

import logging
from typing import Callable
from functools import wraps

from fastapi import HTTPException

from .rbac import has_permission, has_any_permission, has_all_permissions, is_same_tenant

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Basic Guards
# ─────────────────────────────────────────────────────────────────────────────

def require(principal: dict, perm: str) -> None:
    """
    Require a specific permission.

    Usage:
        @app.post("/tasks")
        async def create_task(principal: dict = Depends(get_principal)):
            require(principal, "fieldops:task.create")
            ...

    Raises:
        HTTPException 403 if permission denied
    """
    if not has_permission(principal, perm):
        logger.warning(
            f"Permission denied: user={principal.get('sub')} "
            f"tenant={principal.get('tid')} perm={perm}"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message_ar": "ليس لديك صلاحية لهذا الإجراء",
                "message_en": f"Permission denied: {perm}",
                "required_permission": perm,
            },
        )


def require_any(principal: dict, perms: list[str]) -> None:
    """
    Require any one of the specified permissions.

    Usage:
        require_any(principal, ["fieldops:task.read", "fieldops:task.admin"])
    """
    if not has_any_permission(principal, perms):
        logger.warning(
            f"Permission denied: user={principal.get('sub')} "
            f"tenant={principal.get('tid')} perms={perms}"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message_ar": "ليس لديك صلاحية لهذا الإجراء",
                "message_en": f"Permission denied: requires one of {perms}",
                "required_permissions": perms,
            },
        )


def require_all(principal: dict, perms: list[str]) -> None:
    """
    Require all of the specified permissions.

    Usage:
        require_all(principal, ["fieldops:task.read", "fieldops:task.update"])
    """
    if not has_all_permissions(principal, perms):
        logger.warning(
            f"Permission denied: user={principal.get('sub')} "
            f"tenant={principal.get('tid')} perms={perms}"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message_ar": "ليس لديك كل الصلاحيات المطلوبة",
                "message_en": f"Permission denied: requires all of {perms}",
                "required_permissions": perms,
            },
        )


# ─────────────────────────────────────────────────────────────────────────────
# Tenant Guards
# ─────────────────────────────────────────────────────────────────────────────

def require_tenant(principal: dict, tenant_id: str) -> None:
    """
    Require principal belongs to the specified tenant.

    Raises:
        HTTPException 403 if tenant mismatch
    """
    if not is_same_tenant(principal, tenant_id):
        # Super admin bypass
        if "super_admin" in principal.get("roles", []):
            return

        logger.warning(
            f"Tenant mismatch: user={principal.get('sub')} "
            f"user_tenant={principal.get('tid')} resource_tenant={tenant_id}"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message_ar": "لا يمكنك الوصول إلى موارد مستأجر آخر",
                "message_en": "Cannot access resources from another tenant",
            },
        )


def require_resource_access(
    principal: dict,
    perm: str,
    resource_tenant_id: str,
) -> None:
    """
    Combined permission and tenant check for resource access.

    Usage:
        require_resource_access(principal, "fieldops:task.read", task.tenant_id)
    """
    require_tenant(principal, resource_tenant_id)
    require(principal, perm)


# ─────────────────────────────────────────────────────────────────────────────
# Role Guards
# ─────────────────────────────────────────────────────────────────────────────

def require_role(principal: dict, role: str) -> None:
    """
    Require principal has a specific role.

    Usage:
        require_role(principal, "admin")
    """
    roles = principal.get("roles", [])

    if role not in roles:
        # Super admin has all roles
        if "super_admin" in roles:
            return

        logger.warning(
            f"Role denied: user={principal.get('sub')} "
            f"tenant={principal.get('tid')} required_role={role}"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message_ar": "دور المستخدم غير كافٍ",
                "message_en": f"Required role: {role}",
                "required_role": role,
            },
        )


def require_any_role(principal: dict, roles: list[str]) -> None:
    """
    Require principal has any of the specified roles.
    """
    user_roles = set(principal.get("roles", []))

    if not user_roles.intersection(set(roles)):
        # Super admin bypass
        if "super_admin" in user_roles:
            return

        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message_ar": "دور المستخدم غير كافٍ",
                "message_en": f"Required one of roles: {roles}",
                "required_roles": roles,
            },
        )


# ─────────────────────────────────────────────────────────────────────────────
# Ownership Guards
# ─────────────────────────────────────────────────────────────────────────────

def require_owner_or_permission(
    principal: dict,
    owner_id: str,
    perm: str,
) -> None:
    """
    Allow access if user is owner OR has the permission.

    Usage:
        # User can edit their own profile OR needs admin permission
        require_owner_or_permission(principal, profile.user_id, "admin:users.update")
    """
    user_id = principal.get("sub")

    # Owner can always access
    if user_id == owner_id:
        return

    # Otherwise need permission
    require(principal, perm)


# ─────────────────────────────────────────────────────────────────────────────
# Decorator Guards
# ─────────────────────────────────────────────────────────────────────────────

def requires(perm: str):
    """
    Decorator to require permission on a route handler.

    Usage:
        @app.post("/tasks")
        @requires("fieldops:task.create")
        async def create_task(principal: dict = Depends(get_principal)):
            ...

    Note: The handler must accept 'principal' as a parameter.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            principal = kwargs.get("principal")
            if principal is None:
                raise HTTPException(status_code=401, detail="authentication_required")
            require(principal, perm)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def requires_role(role: str):
    """
    Decorator to require a role on a route handler.

    Usage:
        @app.delete("/users/{user_id}")
        @requires_role("admin")
        async def delete_user(user_id: str, principal: dict = Depends(get_principal)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            principal = kwargs.get("principal")
            if principal is None:
                raise HTTPException(status_code=401, detail="authentication_required")
            require_role(principal, role)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
