"""
SAHOOL Unified Policy Engine
محرك السياسات الموحد

Single Source of Truth for authorization decisions.
Used by:
- Next.js middleware
- React route guards
- PermissionGate components
- API guards

Architecture:
- PolicyEngine evaluates access decisions
- PolicyContext holds request context
- PolicyResult contains decision + reason
"""

import logging
from enum import Enum
from typing import Optional, List, Set, Dict, Any
from dataclasses import dataclass, field

from .rbac import Role, Permission, has_permission, has_any_permission, ROLE_PERMISSIONS

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Policy Decision
# ─────────────────────────────────────────────────────────────────────────────


class PolicyDecision(str, Enum):
    """Policy evaluation result"""

    ALLOW = "allow"
    DENY = "deny"
    REDIRECT = "redirect"


@dataclass
class PolicyResult:
    """Result of policy evaluation"""

    decision: PolicyDecision
    reason: str
    redirect_to: Optional[str] = None
    required_permissions: Optional[List[str]] = None
    missing_permissions: Optional[List[str]] = None

    @property
    def allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOW

    def to_dict(self) -> dict:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "redirect_to": self.redirect_to,
            "allowed": self.allowed,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Policy Context
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PolicyContext:
    """Context for policy evaluation"""

    # User info
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)

    # Request info
    path: Optional[str] = None
    method: str = "GET"
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_tenant_id: Optional[str] = None

    # Auth state
    is_authenticated: bool = False
    token_valid: bool = False
    token_expired: bool = False

    @property
    def is_super_admin(self) -> bool:
        return Role.SUPER_ADMIN in self.roles or "super_admin" in self.roles

    @property
    def is_admin(self) -> bool:
        return self.is_super_admin or Role.ADMIN in self.roles or "admin" in self.roles

    @classmethod
    def from_principal(cls, principal: Any) -> "PolicyContext":
        """Create context from a Principal object"""
        if principal is None:
            return cls()

        return cls(
            user_id=getattr(principal, "sub", None)
            or getattr(principal, "user_id", None),
            tenant_id=getattr(principal, "tid", None)
            or getattr(principal, "tenant_id", None),
            roles=getattr(principal, "roles", []),
            scopes=getattr(principal, "scopes", []),
            is_authenticated=True,
            token_valid=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Route Policies
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RoutePolicy:
    """Policy definition for a route"""

    path_pattern: str
    require_auth: bool = True
    require_roles: List[str] = field(default_factory=list)
    require_permissions: List[str] = field(default_factory=list)
    require_any_permission: List[str] = field(default_factory=list)
    require_tenant: bool = True
    redirect_to: str = "/login"
    allow_public: bool = False


# Default route policies
DEFAULT_POLICIES: Dict[str, RoutePolicy] = {
    # Public routes
    "/login": RoutePolicy("/login", require_auth=False, allow_public=True),
    "/register": RoutePolicy("/register", require_auth=False, allow_public=True),
    "/forgot-password": RoutePolicy(
        "/forgot-password", require_auth=False, allow_public=True
    ),
    "/reset-password": RoutePolicy(
        "/reset-password", require_auth=False, allow_public=True
    ),
    # API health endpoints
    "/healthz": RoutePolicy("/healthz", require_auth=False, allow_public=True),
    "/readyz": RoutePolicy("/readyz", require_auth=False, allow_public=True),
    "/metrics": RoutePolicy("/metrics", require_auth=False, allow_public=True),
    # Protected routes - Dashboard
    "/dashboard": RoutePolicy("/dashboard", require_auth=True),
    "/": RoutePolicy("/", require_auth=True, redirect_to="/login"),
    # Admin routes
    "/admin": RoutePolicy(
        "/admin",
        require_auth=True,
        require_roles=["admin", "super_admin"],
        redirect_to="/dashboard",
    ),
    "/admin/users": RoutePolicy(
        "/admin/users",
        require_auth=True,
        require_permissions=["admin:user.read"],
        redirect_to="/admin",
    ),
    "/admin/tenants": RoutePolicy(
        "/admin/tenants",
        require_auth=True,
        require_permissions=["admin:tenant.manage"],
        redirect_to="/admin",
    ),
    # Field management
    "/fields": RoutePolicy(
        "/fields",
        require_auth=True,
        require_any_permission=["field:field.read", "field:field.list"],
    ),
    # Reports
    "/reports": RoutePolicy(
        "/reports",
        require_auth=True,
        require_any_permission=["ndvi:report.read", "field:report.read"],
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Policy Engine
# ─────────────────────────────────────────────────────────────────────────────


class PolicyEngine:
    """
    Unified policy engine for authorization decisions.

    Usage:
        engine = PolicyEngine()
        result = engine.evaluate(context, "/admin/users")

        if not result.allowed:
            redirect(result.redirect_to)
    """

    def __init__(self, policies: Optional[Dict[str, RoutePolicy]] = None):
        self._policies = policies or DEFAULT_POLICIES.copy()

    def add_policy(self, path: str, policy: RoutePolicy) -> None:
        """Add or update a route policy"""
        self._policies[path] = policy

    def get_policy(self, path: str) -> Optional[RoutePolicy]:
        """Get policy for a path (exact match first, then prefix match)"""
        # Exact match
        if path in self._policies:
            return self._policies[path]

        # Prefix match (longest first)
        matching = [
            (p, policy)
            for p, policy in self._policies.items()
            if path.startswith(p) and p != "/"
        ]
        if matching:
            matching.sort(key=lambda x: len(x[0]), reverse=True)
            return matching[0][1]

        # Default: require auth
        return RoutePolicy(path, require_auth=True)

    def evaluate(
        self,
        context: PolicyContext,
        path: Optional[str] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> PolicyResult:
        """
        Evaluate policy for a request.

        Args:
            context: Policy context with user/request info
            path: Route path to check
            resource_type: Resource type for permission check
            action: Action on resource

        Returns:
            PolicyResult with decision and reason
        """
        # Use path from context if not provided
        path = path or context.path or "/"

        # Get policy for this path
        policy = self.get_policy(path)

        # Public routes
        if policy.allow_public:
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                reason="public_route",
            )

        # Check authentication
        if policy.require_auth and not context.is_authenticated:
            logger.debug(f"Auth required for {path}, user not authenticated")
            return PolicyResult(
                decision=PolicyDecision.REDIRECT,
                reason="authentication_required",
                redirect_to=policy.redirect_to,
            )

        # Check token validity
        if context.token_expired:
            return PolicyResult(
                decision=PolicyDecision.REDIRECT,
                reason="token_expired",
                redirect_to="/login?expired=true",
            )

        # Check tenant
        if policy.require_tenant and not context.tenant_id:
            return PolicyResult(
                decision=PolicyDecision.REDIRECT,
                reason="tenant_required",
                redirect_to="/select-tenant",
            )

        # Check roles
        if policy.require_roles:
            user_roles = set(context.roles)
            required_roles = set(policy.require_roles)

            # Super admin bypasses role check
            if not context.is_super_admin and not user_roles.intersection(
                required_roles
            ):
                logger.debug(
                    f"Role check failed for {path}: need {required_roles}, have {user_roles}"
                )
                return PolicyResult(
                    decision=PolicyDecision.REDIRECT,
                    reason="insufficient_role",
                    redirect_to=policy.redirect_to,
                )

        # Check required permissions (ALL must match)
        if policy.require_permissions:
            missing = []
            for perm in policy.require_permissions:
                if not self._has_permission(context, perm):
                    missing.append(perm)

            if missing:
                logger.debug(f"Permission check failed for {path}: missing {missing}")
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason="insufficient_permissions",
                    redirect_to=policy.redirect_to,
                    required_permissions=policy.require_permissions,
                    missing_permissions=missing,
                )

        # Check any permission (at least ONE must match)
        if policy.require_any_permission:
            has_any = any(
                self._has_permission(context, perm)
                for perm in policy.require_any_permission
            )
            if not has_any:
                logger.debug(f"Any-permission check failed for {path}")
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason="insufficient_permissions",
                    redirect_to=policy.redirect_to,
                    required_permissions=policy.require_any_permission,
                    missing_permissions=policy.require_any_permission,
                )

        # Check resource-level permission
        if resource_type and action:
            permission = f"{resource_type}:{resource_type}.{action}"
            if not self._has_permission(context, permission):
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason="resource_access_denied",
                    required_permissions=[permission],
                    missing_permissions=[permission],
                )

        # All checks passed
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason="authorized",
        )

    def _has_permission(self, context: PolicyContext, permission: str) -> bool:
        """Check if context has a permission"""
        # Super admin has all permissions
        if context.is_super_admin:
            return True

        # Check explicit scopes
        if permission in context.scopes:
            return True

        # Check role-based permissions
        for role in context.roles:
            try:
                role_enum = Role(role) if isinstance(role, str) else role
                if has_permission([role_enum], Permission(permission)):
                    return True
            except (ValueError, KeyError):
                continue

        return False

    def can_access_resource(
        self,
        context: PolicyContext,
        resource_type: str,
        resource_id: str,
        resource_tenant_id: str,
        action: str = "read",
    ) -> PolicyResult:
        """
        Check if user can access a specific resource.

        Args:
            context: Policy context
            resource_type: Type of resource (field, task, etc.)
            resource_id: ID of the resource
            resource_tenant_id: Tenant that owns the resource
            action: Action to perform

        Returns:
            PolicyResult
        """
        # Must be authenticated
        if not context.is_authenticated:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason="authentication_required",
            )

        # Tenant isolation: user can only access resources in their tenant
        if context.tenant_id != resource_tenant_id:
            # Super admin can access any tenant
            if not context.is_super_admin:
                logger.warning(
                    f"Tenant mismatch: user {context.user_id} (tenant {context.tenant_id}) "
                    f"tried to access resource in tenant {resource_tenant_id}"
                )
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason="tenant_mismatch",
                )

        # Check permission for this resource type and action
        permission = f"{resource_type}:{resource_type}.{action}"
        if not self._has_permission(context, permission):
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason="insufficient_permissions",
                required_permissions=[permission],
                missing_permissions=[permission],
            )

        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason="authorized",
        )


# Global instance
_policy_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get the global policy engine instance"""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine


# Convenience functions
def evaluate_policy(
    context: PolicyContext,
    path: Optional[str] = None,
) -> PolicyResult:
    """Evaluate policy for a request"""
    return get_policy_engine().evaluate(context, path)


def can_access(
    context: PolicyContext,
    resource_type: str,
    resource_id: str,
    resource_tenant_id: str,
    action: str = "read",
) -> PolicyResult:
    """Check if user can access a resource"""
    return get_policy_engine().can_access_resource(
        context, resource_type, resource_id, resource_tenant_id, action
    )
