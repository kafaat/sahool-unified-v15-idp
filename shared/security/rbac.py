"""
Role-Based Access Control (RBAC) Policy Engine
Simple and effective permission management
"""

from enum import Enum

# ─────────────────────────────────────────────────────────────────────────────
# Permission Definitions
# ─────────────────────────────────────────────────────────────────────────────


class Permission(str, Enum):
    """
    All permissions in the system.
    Format: service:resource.action
    """

    # FieldOps
    FIELDOPS_TASK_READ = "fieldops:task.read"
    FIELDOPS_TASK_CREATE = "fieldops:task.create"
    FIELDOPS_TASK_UPDATE = "fieldops:task.update"
    FIELDOPS_TASK_DELETE = "fieldops:task.delete"
    FIELDOPS_TASK_ASSIGN = "fieldops:task.assign"
    FIELDOPS_TASK_COMPLETE = "fieldops:task.complete"

    # Fields
    FIELDOPS_FIELD_READ = "fieldops:field.read"
    FIELDOPS_FIELD_CREATE = "fieldops:field.create"
    FIELDOPS_FIELD_UPDATE = "fieldops:field.update"
    FIELDOPS_FIELD_DELETE = "fieldops:field.delete"

    # NDVI
    NDVI_READ = "ndvi:read"
    NDVI_COMPUTE = "ndvi:compute"

    # Weather
    WEATHER_READ = "weather:read"

    # IoT
    IOT_DEVICE_READ = "iot:device.read"
    IOT_DEVICE_CREATE = "iot:device.create"
    IOT_DEVICE_UPDATE = "iot:device.update"
    IOT_DEVICE_DELETE = "iot:device.delete"
    IOT_SENSOR_READ = "iot:sensor.read"

    # Chat
    CHAT_READ = "chat:read"
    CHAT_WRITE = "chat:write"
    CHAT_ADMIN = "chat:admin"

    # Agro Intelligence
    AGRO_DISEASE_READ = "agro:disease.read"
    AGRO_FERTILIZER_READ = "agro:fertilizer.read"
    AGRO_RECOMMENDATION_READ = "agro:recommendation.read"

    # Admin
    ADMIN_USERS_READ = "admin:users.read"
    ADMIN_USERS_CREATE = "admin:users.create"
    ADMIN_USERS_UPDATE = "admin:users.update"
    ADMIN_USERS_DELETE = "admin:users.delete"
    ADMIN_TENANT_MANAGE = "admin:tenant.manage"
    ADMIN_AUDIT_READ = "admin:audit.read"

    # Reports
    REPORTS_READ = "reports:read"
    REPORTS_EXPORT = "reports:export"


# ─────────────────────────────────────────────────────────────────────────────
# Role Definitions
# ─────────────────────────────────────────────────────────────────────────────


class Role(str, Enum):
    """System roles"""

    VIEWER = "viewer"
    WORKER = "worker"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Role to Permissions mapping
ROLE_PERMISSIONS: dict[str, set[str]] = {
    # Viewer: Read-only access
    Role.VIEWER: {
        Permission.FIELDOPS_TASK_READ,
        Permission.FIELDOPS_FIELD_READ,
        Permission.NDVI_READ,
        Permission.WEATHER_READ,
        Permission.IOT_DEVICE_READ,
        Permission.IOT_SENSOR_READ,
        Permission.CHAT_READ,
        Permission.AGRO_DISEASE_READ,
        Permission.AGRO_FERTILIZER_READ,
        Permission.AGRO_RECOMMENDATION_READ,
        Permission.REPORTS_READ,
    },
    # Worker: Field operations
    Role.WORKER: {
        # All viewer permissions
        Permission.FIELDOPS_TASK_READ,
        Permission.FIELDOPS_FIELD_READ,
        Permission.NDVI_READ,
        Permission.WEATHER_READ,
        Permission.IOT_DEVICE_READ,
        Permission.IOT_SENSOR_READ,
        Permission.CHAT_READ,
        Permission.AGRO_DISEASE_READ,
        Permission.AGRO_FERTILIZER_READ,
        Permission.AGRO_RECOMMENDATION_READ,
        Permission.REPORTS_READ,
        # Worker-specific
        Permission.FIELDOPS_TASK_UPDATE,
        Permission.FIELDOPS_TASK_COMPLETE,
        Permission.CHAT_WRITE,
    },
    # Supervisor: Team lead
    Role.SUPERVISOR: {
        # All worker permissions
        Permission.FIELDOPS_TASK_READ,
        Permission.FIELDOPS_TASK_UPDATE,
        Permission.FIELDOPS_TASK_COMPLETE,
        Permission.FIELDOPS_FIELD_READ,
        Permission.NDVI_READ,
        Permission.WEATHER_READ,
        Permission.IOT_DEVICE_READ,
        Permission.IOT_SENSOR_READ,
        Permission.CHAT_READ,
        Permission.CHAT_WRITE,
        Permission.AGRO_DISEASE_READ,
        Permission.AGRO_FERTILIZER_READ,
        Permission.AGRO_RECOMMENDATION_READ,
        Permission.REPORTS_READ,
        # Supervisor-specific
        Permission.FIELDOPS_TASK_CREATE,
        Permission.FIELDOPS_TASK_ASSIGN,
        Permission.IOT_DEVICE_UPDATE,
    },
    # Manager: Full operational control
    Role.MANAGER: {
        # All supervisor permissions plus
        Permission.FIELDOPS_TASK_READ,
        Permission.FIELDOPS_TASK_CREATE,
        Permission.FIELDOPS_TASK_UPDATE,
        Permission.FIELDOPS_TASK_DELETE,
        Permission.FIELDOPS_TASK_ASSIGN,
        Permission.FIELDOPS_TASK_COMPLETE,
        Permission.FIELDOPS_FIELD_READ,
        Permission.FIELDOPS_FIELD_CREATE,
        Permission.FIELDOPS_FIELD_UPDATE,
        Permission.FIELDOPS_FIELD_DELETE,
        Permission.NDVI_READ,
        Permission.NDVI_COMPUTE,
        Permission.WEATHER_READ,
        Permission.IOT_DEVICE_READ,
        Permission.IOT_DEVICE_CREATE,
        Permission.IOT_DEVICE_UPDATE,
        Permission.IOT_DEVICE_DELETE,
        Permission.IOT_SENSOR_READ,
        Permission.CHAT_READ,
        Permission.CHAT_WRITE,
        Permission.CHAT_ADMIN,
        Permission.AGRO_DISEASE_READ,
        Permission.AGRO_FERTILIZER_READ,
        Permission.AGRO_RECOMMENDATION_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_EXPORT,
    },
    # Admin: Tenant administration
    Role.ADMIN: {
        # All manager permissions plus admin
        Permission.FIELDOPS_TASK_READ,
        Permission.FIELDOPS_TASK_CREATE,
        Permission.FIELDOPS_TASK_UPDATE,
        Permission.FIELDOPS_TASK_DELETE,
        Permission.FIELDOPS_TASK_ASSIGN,
        Permission.FIELDOPS_TASK_COMPLETE,
        Permission.FIELDOPS_FIELD_READ,
        Permission.FIELDOPS_FIELD_CREATE,
        Permission.FIELDOPS_FIELD_UPDATE,
        Permission.FIELDOPS_FIELD_DELETE,
        Permission.NDVI_READ,
        Permission.NDVI_COMPUTE,
        Permission.WEATHER_READ,
        Permission.IOT_DEVICE_READ,
        Permission.IOT_DEVICE_CREATE,
        Permission.IOT_DEVICE_UPDATE,
        Permission.IOT_DEVICE_DELETE,
        Permission.IOT_SENSOR_READ,
        Permission.CHAT_READ,
        Permission.CHAT_WRITE,
        Permission.CHAT_ADMIN,
        Permission.AGRO_DISEASE_READ,
        Permission.AGRO_FERTILIZER_READ,
        Permission.AGRO_RECOMMENDATION_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_EXPORT,
        Permission.ADMIN_USERS_READ,
        Permission.ADMIN_USERS_CREATE,
        Permission.ADMIN_USERS_UPDATE,
        Permission.ADMIN_USERS_DELETE,
        Permission.ADMIN_AUDIT_READ,
    },
    # Super Admin: Full system access
    Role.SUPER_ADMIN: {
        # Everything
        Permission.FIELDOPS_TASK_READ,
        Permission.FIELDOPS_TASK_CREATE,
        Permission.FIELDOPS_TASK_UPDATE,
        Permission.FIELDOPS_TASK_DELETE,
        Permission.FIELDOPS_TASK_ASSIGN,
        Permission.FIELDOPS_TASK_COMPLETE,
        Permission.FIELDOPS_FIELD_READ,
        Permission.FIELDOPS_FIELD_CREATE,
        Permission.FIELDOPS_FIELD_UPDATE,
        Permission.FIELDOPS_FIELD_DELETE,
        Permission.NDVI_READ,
        Permission.NDVI_COMPUTE,
        Permission.WEATHER_READ,
        Permission.IOT_DEVICE_READ,
        Permission.IOT_DEVICE_CREATE,
        Permission.IOT_DEVICE_UPDATE,
        Permission.IOT_DEVICE_DELETE,
        Permission.IOT_SENSOR_READ,
        Permission.CHAT_READ,
        Permission.CHAT_WRITE,
        Permission.CHAT_ADMIN,
        Permission.AGRO_DISEASE_READ,
        Permission.AGRO_FERTILIZER_READ,
        Permission.AGRO_RECOMMENDATION_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_EXPORT,
        Permission.ADMIN_USERS_READ,
        Permission.ADMIN_USERS_CREATE,
        Permission.ADMIN_USERS_UPDATE,
        Permission.ADMIN_USERS_DELETE,
        Permission.ADMIN_TENANT_MANAGE,
        Permission.ADMIN_AUDIT_READ,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Permission Check Functions
# ─────────────────────────────────────────────────────────────────────────────


def get_role_permissions(role: str) -> set[str]:
    """Get all permissions for a role"""
    return ROLE_PERMISSIONS.get(role, set())


def get_all_permissions(roles: list[str], scopes: list[str]) -> set[str]:
    """
    Get all permissions from roles and explicit scopes.
    Scopes take precedence and can override role permissions.
    """
    permissions = set()

    # Add permissions from roles
    for role in roles:
        permissions.update(get_role_permissions(role))

    # Add explicit scopes
    permissions.update(scopes)

    return permissions


def has_permission(principal: dict, perm: str) -> bool:
    """
    Check if principal has a specific permission.

    Args:
        principal: Decoded JWT payload with roles and scopes
        perm: Permission string to check

    Returns:
        True if permission is granted
    """
    roles = principal.get("roles", [])
    scopes = principal.get("scopes", [])

    # Super admin and admin bypass
    if "super_admin" in roles or "admin" in roles:
        # Admin has all permissions except super_admin specific
        if "admin" in roles and perm == Permission.ADMIN_TENANT_MANAGE:
            return "super_admin" in roles
        return True

    # Check explicit scopes first
    if perm in scopes:
        return True

    # Check role permissions
    all_permissions = get_all_permissions(roles, scopes)
    return perm in all_permissions


def has_any_permission(principal: dict, perms: list[str]) -> bool:
    """Check if principal has any of the specified permissions"""
    return any(has_permission(principal, p) for p in perms)


def has_all_permissions(principal: dict, perms: list[str]) -> bool:
    """Check if principal has all specified permissions"""
    return all(has_permission(principal, p) for p in perms)


def is_same_tenant(principal: dict, tenant_id: str) -> bool:
    """Check if principal belongs to the specified tenant"""
    return principal.get("tid") == tenant_id


def can_access_resource(
    principal: dict,
    perm: str,
    resource_tenant_id: str,
) -> bool:
    """
    Check if principal can access a resource.
    Combines permission check with tenant isolation.
    """
    if not is_same_tenant(principal, resource_tenant_id):
        # Cross-tenant access only for super_admin
        if "super_admin" not in principal.get("roles", []):
            return False

    return has_permission(principal, perm)
