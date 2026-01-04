"""
Authentication Models
نماذج المصادقة
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    """User account status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class RoleType(str, Enum):
    """Predefined role types"""

    SUPER_ADMIN = "super_admin"  # Full system access
    TENANT_ADMIN = "tenant_admin"  # Full tenant access
    FARM_MANAGER = "farm_manager"  # Farm management
    FIELD_OPERATOR = "field_operator"  # Field operations
    AGRONOMIST = "agronomist"  # Crop & soil analysis
    VIEWER = "viewer"  # Read-only access


@dataclass
class Permission:
    """
    Permission definition
    تعريف الصلاحية
    """

    id: str
    name: str
    description: str = ""
    resource: str = ""  # Resource this permission applies to
    actions: list[str] = field(default_factory=list)  # create, read, update, delete

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Permission):
            return self.id == other.id
        return False


@dataclass
class Role:
    """
    Role definition with permissions
    تعريف الدور مع الصلاحيات
    """

    id: str
    name: str
    description: str = ""
    permissions: set[Permission] = field(default_factory=set)
    is_system_role: bool = False  # System roles cannot be deleted
    tenant_id: str | None = None  # None for system-wide roles

    def has_permission(self, permission_id: str) -> bool:
        """Check if role has a specific permission"""
        return any(p.id == permission_id for p in self.permissions)

    def add_permission(self, permission: Permission) -> None:
        """Add a permission to this role"""
        self.permissions.add(permission)

    def remove_permission(self, permission_id: str) -> None:
        """Remove a permission from this role"""
        self.permissions = {p for p in self.permissions if p.id != permission_id}

    def __hash__(self):
        return hash(self.id)


@dataclass
class User:
    """
    User model for authentication
    نموذج المستخدم للمصادقة
    """

    id: str
    email: str
    hashed_password: str
    status: UserStatus = UserStatus.ACTIVE
    tenant_id: str | None = None
    roles: list[Role] = field(default_factory=list)

    # Profile
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None

    # Security
    email_verified: bool = False
    phone_verified: bool = False
    two_factor_enabled: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    last_login: datetime | None = None

    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.email

    @property
    def all_permissions(self) -> set[Permission]:
        """Get all permissions from all roles"""
        permissions = set()
        for role in self.roles:
            permissions.update(role.permissions)
        return permissions

    @property
    def role_names(self) -> list[str]:
        """Get list of role names"""
        return [role.name for role in self.roles]

    @property
    def permission_ids(self) -> list[str]:
        """Get list of permission IDs"""
        return [p.id for p in self.all_permissions]

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_id: str) -> bool:
        """Check if user has a specific permission"""
        return any(p.id == permission_id for p in self.all_permissions)

    def has_any_role(self, role_names: list[str]) -> bool:
        """Check if user has any of the specified roles"""
        return any(self.has_role(name) for name in role_names)

    def has_all_roles(self, role_names: list[str]) -> bool:
        """Check if user has all specified roles"""
        return all(self.has_role(name) for name in role_names)

    def can_access_tenant(self, tenant_id: str) -> bool:
        """Check if user can access a specific tenant"""
        # Super admins can access any tenant
        if self.has_role(RoleType.SUPER_ADMIN.value):
            return True
        # Otherwise must match tenant
        return self.tenant_id == tenant_id


# ============================================
# Predefined Permissions
# الصلاحيات المحددة مسبقاً
# ============================================

# Farm permissions
PERM_FARM_CREATE = Permission("farm:create", "Create farms", "farm", ["create"])
PERM_FARM_READ = Permission("farm:read", "View farms", "farm", ["read"])
PERM_FARM_UPDATE = Permission("farm:update", "Update farms", "farm", ["update"])
PERM_FARM_DELETE = Permission("farm:delete", "Delete farms", "farm", ["delete"])

# Field permissions
PERM_FIELD_CREATE = Permission("field:create", "Create fields", "field", ["create"])
PERM_FIELD_READ = Permission("field:read", "View fields", "field", ["read"])
PERM_FIELD_UPDATE = Permission("field:update", "Update fields", "field", ["update"])
PERM_FIELD_DELETE = Permission("field:delete", "Delete fields", "field", ["delete"])

# Crop permissions
PERM_CROP_CREATE = Permission("crop:create", "Create crops", "crop", ["create"])
PERM_CROP_READ = Permission("crop:read", "View crops", "crop", ["read"])
PERM_CROP_UPDATE = Permission("crop:update", "Update crops", "crop", ["update"])
PERM_CROP_DELETE = Permission("crop:delete", "Delete crops", "crop", ["delete"])

# Sensor permissions
PERM_SENSOR_READ = Permission("sensor:read", "View sensor data", "sensor", ["read"])
PERM_SENSOR_MANAGE = Permission(
    "sensor:manage", "Manage sensors", "sensor", ["create", "update", "delete"]
)

# Irrigation permissions
PERM_IRRIGATION_VIEW = Permission(
    "irrigation:view", "View irrigation", "irrigation", ["read"]
)
PERM_IRRIGATION_CONTROL = Permission(
    "irrigation:control", "Control irrigation", "irrigation", ["update"]
)

# Report permissions
PERM_REPORT_VIEW = Permission("report:view", "View reports", "report", ["read"])
PERM_REPORT_EXPORT = Permission("report:export", "Export reports", "report", ["export"])

# Billing permissions
PERM_BILLING_VIEW = Permission("billing:view", "View billing", "billing", ["read"])
PERM_BILLING_MANAGE = Permission(
    "billing:manage", "Manage billing", "billing", ["create", "update", "delete"]
)

# User management permissions
PERM_USER_READ = Permission("user:read", "View users", "user", ["read"])
PERM_USER_MANAGE = Permission(
    "user:manage", "Manage users", "user", ["create", "update", "delete"]
)

# Role management permissions
PERM_ROLE_READ = Permission("role:read", "View roles", "role", ["read"])
PERM_ROLE_MANAGE = Permission(
    "role:manage", "Manage roles", "role", ["create", "update", "delete"]
)

# System permissions
PERM_SYSTEM_ADMIN = Permission("system:admin", "System administration", "system", ["*"])


# ============================================
# Predefined Roles
# الأدوار المحددة مسبقاً
# ============================================

ROLE_SUPER_ADMIN = Role(
    id="super_admin",
    name=RoleType.SUPER_ADMIN.value,
    description="Full system access",
    is_system_role=True,
    permissions={PERM_SYSTEM_ADMIN},
)

ROLE_TENANT_ADMIN = Role(
    id="tenant_admin",
    name=RoleType.TENANT_ADMIN.value,
    description="Full tenant access",
    is_system_role=True,
    permissions={
        PERM_FARM_CREATE,
        PERM_FARM_READ,
        PERM_FARM_UPDATE,
        PERM_FARM_DELETE,
        PERM_FIELD_CREATE,
        PERM_FIELD_READ,
        PERM_FIELD_UPDATE,
        PERM_FIELD_DELETE,
        PERM_CROP_CREATE,
        PERM_CROP_READ,
        PERM_CROP_UPDATE,
        PERM_CROP_DELETE,
        PERM_SENSOR_READ,
        PERM_SENSOR_MANAGE,
        PERM_IRRIGATION_VIEW,
        PERM_IRRIGATION_CONTROL,
        PERM_REPORT_VIEW,
        PERM_REPORT_EXPORT,
        PERM_BILLING_VIEW,
        PERM_BILLING_MANAGE,
        PERM_USER_READ,
        PERM_USER_MANAGE,
        PERM_ROLE_READ,
        PERM_ROLE_MANAGE,
    },
)

ROLE_FARM_MANAGER = Role(
    id="farm_manager",
    name=RoleType.FARM_MANAGER.value,
    description="Farm management access",
    is_system_role=True,
    permissions={
        PERM_FARM_READ,
        PERM_FARM_UPDATE,
        PERM_FIELD_CREATE,
        PERM_FIELD_READ,
        PERM_FIELD_UPDATE,
        PERM_FIELD_DELETE,
        PERM_CROP_CREATE,
        PERM_CROP_READ,
        PERM_CROP_UPDATE,
        PERM_CROP_DELETE,
        PERM_SENSOR_READ,
        PERM_SENSOR_MANAGE,
        PERM_IRRIGATION_VIEW,
        PERM_IRRIGATION_CONTROL,
        PERM_REPORT_VIEW,
        PERM_REPORT_EXPORT,
        PERM_USER_READ,
    },
)

ROLE_FIELD_OPERATOR = Role(
    id="field_operator",
    name=RoleType.FIELD_OPERATOR.value,
    description="Field operations access",
    is_system_role=True,
    permissions={
        PERM_FARM_READ,
        PERM_FIELD_READ,
        PERM_FIELD_UPDATE,
        PERM_CROP_READ,
        PERM_CROP_UPDATE,
        PERM_SENSOR_READ,
        PERM_IRRIGATION_VIEW,
        PERM_IRRIGATION_CONTROL,
    },
)

ROLE_AGRONOMIST = Role(
    id="agronomist",
    name=RoleType.AGRONOMIST.value,
    description="Agronomist access",
    is_system_role=True,
    permissions={
        PERM_FARM_READ,
        PERM_FIELD_READ,
        PERM_CROP_READ,
        PERM_CROP_UPDATE,
        PERM_SENSOR_READ,
        PERM_REPORT_VIEW,
        PERM_REPORT_EXPORT,
    },
)

ROLE_VIEWER = Role(
    id="viewer",
    name=RoleType.VIEWER.value,
    description="Read-only access",
    is_system_role=True,
    permissions={
        PERM_FARM_READ,
        PERM_FIELD_READ,
        PERM_CROP_READ,
        PERM_SENSOR_READ,
        PERM_REPORT_VIEW,
    },
)

# Role registry
SYSTEM_ROLES = {
    RoleType.SUPER_ADMIN.value: ROLE_SUPER_ADMIN,
    RoleType.TENANT_ADMIN.value: ROLE_TENANT_ADMIN,
    RoleType.FARM_MANAGER.value: ROLE_FARM_MANAGER,
    RoleType.FIELD_OPERATOR.value: ROLE_FIELD_OPERATOR,
    RoleType.AGRONOMIST.value: ROLE_AGRONOMIST,
    RoleType.VIEWER.value: ROLE_VIEWER,
}
