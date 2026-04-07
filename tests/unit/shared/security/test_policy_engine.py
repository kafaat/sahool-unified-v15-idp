"""
Tests for shared/security/policy_engine.py
Unified RBAC policy engine
"""

import pytest
from unittest.mock import patch

from shared.security.policy_engine import (
    DEFAULT_POLICIES,
    PolicyContext,
    PolicyDecision,
    PolicyEngine,
    PolicyResult,
    RoutePolicy,
    can_access,
    evaluate_policy,
    get_policy_engine,
)


# ─────────────────────────────────────────────────────────────────────────────
# PolicyDecision
# ─────────────────────────────────────────────────────────────────────────────


class TestPolicyDecision:
    def test_values(self):
        assert PolicyDecision.ALLOW == "allow"
        assert PolicyDecision.DENY == "deny"
        assert PolicyDecision.REDIRECT == "redirect"


# ─────────────────────────────────────────────────────────────────────────────
# PolicyResult
# ─────────────────────────────────────────────────────────────────────────────


class TestPolicyResult:
    def test_allowed_property(self):
        result = PolicyResult(decision=PolicyDecision.ALLOW, reason="ok")
        assert result.allowed is True

    def test_denied_property(self):
        result = PolicyResult(decision=PolicyDecision.DENY, reason="no")
        assert result.allowed is False

    def test_redirect_not_allowed(self):
        result = PolicyResult(decision=PolicyDecision.REDIRECT, reason="auth", redirect_to="/login")
        assert result.allowed is False

    def test_to_dict(self):
        result = PolicyResult(
            decision=PolicyDecision.DENY,
            reason="forbidden",
            redirect_to="/login",
        )
        d = result.to_dict()
        assert d["decision"] == "deny"
        assert d["reason"] == "forbidden"
        assert d["redirect_to"] == "/login"
        assert d["allowed"] is False

    def test_missing_permissions(self):
        result = PolicyResult(
            decision=PolicyDecision.DENY,
            reason="insufficient_permissions",
            required_permissions=["admin:user.read"],
            missing_permissions=["admin:user.read"],
        )
        assert result.missing_permissions == ["admin:user.read"]


# ─────────────────────────────────────────────────────────────────────────────
# PolicyContext
# ─────────────────────────────────────────────────────────────────────────────


class TestPolicyContext:
    def test_default_values(self):
        ctx = PolicyContext()
        assert ctx.user_id is None
        assert ctx.tenant_id is None
        assert ctx.roles == []
        assert ctx.scopes == []
        assert ctx.path is None
        assert ctx.method == "GET"
        assert ctx.is_authenticated is False
        assert ctx.token_valid is False
        assert ctx.token_expired is False

    def test_is_super_admin(self):
        ctx = PolicyContext(roles=["super_admin"])
        assert ctx.is_super_admin is True

    def test_is_super_admin_enum_value(self):
        from shared.security.rbac import Role
        ctx = PolicyContext(roles=[Role.SUPER_ADMIN])
        assert ctx.is_super_admin is True

    def test_is_not_super_admin(self):
        ctx = PolicyContext(roles=["viewer"])
        assert ctx.is_super_admin is False

    def test_is_admin(self):
        ctx = PolicyContext(roles=["admin"])
        assert ctx.is_admin is True

    def test_is_admin_via_super(self):
        ctx = PolicyContext(roles=["super_admin"])
        assert ctx.is_admin is True

    def test_is_not_admin(self):
        ctx = PolicyContext(roles=["viewer"])
        assert ctx.is_admin is False

    def test_from_principal_none(self):
        ctx = PolicyContext.from_principal(None)
        assert ctx.user_id is None
        assert ctx.is_authenticated is False

    def test_from_principal_object(self):
        class FakePrincipal:
            sub = "user-1"
            tid = "tenant-1"
            roles = ["admin"]
            scopes = ["custom:scope"]

        ctx = PolicyContext.from_principal(FakePrincipal())
        assert ctx.user_id == "user-1"
        assert ctx.tenant_id == "tenant-1"
        assert ctx.roles == ["admin"]
        assert ctx.scopes == ["custom:scope"]
        assert ctx.is_authenticated is True
        assert ctx.token_valid is True

    def test_from_principal_with_user_id_attr(self):
        class FakePrincipal:
            user_id = "u2"
            tenant_id = "t2"
            roles = []
            scopes = []

        ctx = PolicyContext.from_principal(FakePrincipal())
        assert ctx.user_id == "u2"
        assert ctx.tenant_id == "t2"


# ─────────────────────────────────────────────────────────────────────────────
# RoutePolicy
# ─────────────────────────────────────────────────────────────────────────────


class TestRoutePolicy:
    def test_defaults(self):
        policy = RoutePolicy("/test")
        assert policy.path_pattern == "/test"
        assert policy.require_auth is True
        assert policy.require_roles == []
        assert policy.require_permissions == []
        assert policy.require_any_permission == []
        assert policy.require_tenant is True
        assert policy.redirect_to == "/login"
        assert policy.allow_public is False

    def test_public_route(self):
        policy = RoutePolicy("/login", require_auth=False, allow_public=True)
        assert policy.allow_public is True
        assert policy.require_auth is False


# ─────────────────────────────────────────────────────────────────────────────
# PolicyEngine - evaluate()
# ─────────────────────────────────────────────────────────────────────────────


class TestPolicyEngineEvaluate:
    def setup_method(self):
        self.engine = PolicyEngine()

    def test_public_route_allows_anonymous(self):
        ctx = PolicyContext(is_authenticated=False)
        result = self.engine.evaluate(ctx, "/login")
        assert result.allowed is True
        assert result.reason == "public_route"

    def test_healthz_is_public(self):
        ctx = PolicyContext()
        result = self.engine.evaluate(ctx, "/healthz")
        assert result.allowed is True

    def test_unauthenticated_on_protected_route_redirects(self):
        ctx = PolicyContext(is_authenticated=False)
        result = self.engine.evaluate(ctx, "/dashboard")
        assert result.decision == PolicyDecision.REDIRECT
        assert result.reason == "authentication_required"

    def test_expired_token_redirects(self):
        ctx = PolicyContext(is_authenticated=True, token_expired=True, tenant_id="t1")
        result = self.engine.evaluate(ctx, "/dashboard")
        assert result.decision == PolicyDecision.REDIRECT
        assert result.reason == "token_expired"
        assert "expired" in result.redirect_to

    def test_missing_tenant_redirects(self):
        ctx = PolicyContext(is_authenticated=True, tenant_id=None)
        result = self.engine.evaluate(ctx, "/dashboard")
        assert result.decision == PolicyDecision.REDIRECT
        assert result.reason == "tenant_required"

    def test_insufficient_role_redirects(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["viewer"],
        )
        result = self.engine.evaluate(ctx, "/admin")
        assert result.decision == PolicyDecision.REDIRECT
        assert result.reason == "insufficient_role"

    def test_admin_role_allowed(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["admin"],
        )
        result = self.engine.evaluate(ctx, "/admin")
        assert result.allowed is True

    def test_super_admin_bypasses_roles(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["super_admin"],
        )
        result = self.engine.evaluate(ctx, "/admin")
        assert result.allowed is True

    def test_missing_required_permissions_denies(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["viewer"],
        )
        result = self.engine.evaluate(ctx, "/admin/users")
        assert result.decision == PolicyDecision.DENY
        assert result.reason == "insufficient_permissions"
        assert "admin:user.read" in result.missing_permissions

    def test_admin_has_user_read_permission_via_scope(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["admin"],
            scopes=["admin:user.read"],
        )
        result = self.engine.evaluate(ctx, "/admin/users")
        assert result.allowed is True

    def test_super_admin_has_user_read_permission(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["super_admin"],
        )
        result = self.engine.evaluate(ctx, "/admin/users")
        assert result.allowed is True

    def test_require_any_permission_denied(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["worker"],  # Worker doesn't have field:field.read or field:field.list
        )
        result = self.engine.evaluate(ctx, "/fields")
        assert result.decision == PolicyDecision.DENY
        assert result.reason == "insufficient_permissions"

    def test_resource_type_action_check(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["viewer"],
        )
        result = self.engine.evaluate(ctx, "/some-path", resource_type="field", action="delete")
        assert result.decision == PolicyDecision.DENY
        assert result.reason == "resource_access_denied"

    def test_super_admin_resource_type_access(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["super_admin"],
        )
        result = self.engine.evaluate(ctx, "/some-path", resource_type="field", action="delete")
        assert result.allowed is True

    def test_all_checks_pass(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["admin"],
        )
        result = self.engine.evaluate(ctx, "/dashboard")
        assert result.allowed is True
        assert result.reason == "authorized"

    def test_uses_context_path_as_fallback(self):
        ctx = PolicyContext(
            is_authenticated=False,
            path="/login",
        )
        result = self.engine.evaluate(ctx)
        assert result.allowed is True

    def test_default_path_is_root(self):
        ctx = PolicyContext(is_authenticated=False)
        result = self.engine.evaluate(ctx)
        # "/" requires auth
        assert result.decision == PolicyDecision.REDIRECT


# ─────────────────────────────────────────────────────────────────────────────
# PolicyEngine - get_policy() / add_policy()
# ─────────────────────────────────────────────────────────────────────────────


class TestPolicyEngineGetPolicy:
    def test_exact_match(self):
        engine = PolicyEngine()
        policy = engine.get_policy("/login")
        assert policy.allow_public is True

    def test_prefix_match(self):
        engine = PolicyEngine()
        # /admin/users/123 should match /admin/users prefix
        policy = engine.get_policy("/admin/users/123")
        assert policy is not None
        assert "admin:user.read" in policy.require_permissions

    def test_longest_prefix_wins(self):
        engine = PolicyEngine()
        # /admin/users should match /admin/users (longer) over /admin
        policy = engine.get_policy("/admin/users")
        assert "admin:user.read" in policy.require_permissions

    def test_no_match_returns_default(self):
        engine = PolicyEngine()
        policy = engine.get_policy("/unknown/path/here")
        assert policy is not None
        assert policy.require_auth is True

    def test_add_policy(self):
        engine = PolicyEngine()
        custom_policy = RoutePolicy("/custom", require_auth=False, allow_public=True)
        engine.add_policy("/custom", custom_policy)
        policy = engine.get_policy("/custom")
        assert policy.allow_public is True

    def test_custom_policies(self):
        policies = {"/api": RoutePolicy("/api", allow_public=True)}
        engine = PolicyEngine(policies=policies)
        result = engine.get_policy("/api")
        assert result.allow_public is True
        # Default policies should not be present
        result2 = engine.get_policy("/login")
        assert result2.require_auth is True  # default for unknown paths


# ─────────────────────────────────────────────────────────────────────────────
# PolicyEngine - can_access_resource()
# ─────────────────────────────────────────────────────────────────────────────


class TestCanAccessResource:
    def setup_method(self):
        self.engine = PolicyEngine()

    def test_unauthenticated_denied(self):
        ctx = PolicyContext(is_authenticated=False)
        result = self.engine.can_access_resource(ctx, "field", "f1", "t1")
        assert result.decision == PolicyDecision.DENY
        assert result.reason == "authentication_required"

    def test_tenant_mismatch_denied(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["admin"],
        )
        result = self.engine.can_access_resource(ctx, "field", "f1", "t2")
        assert result.decision == PolicyDecision.DENY
        assert result.reason == "tenant_mismatch"

    def test_super_admin_cross_tenant_allowed(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["super_admin"],
        )
        result = self.engine.can_access_resource(ctx, "field", "f1", "t2")
        assert result.allowed is True

    def test_insufficient_permission_denied(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["viewer"],
        )
        result = self.engine.can_access_resource(ctx, "field", "f1", "t1", action="delete")
        assert result.decision == PolicyDecision.DENY
        assert result.reason == "insufficient_permissions"

    def test_authorized(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["admin"],
            scopes=["field:field.read"],
        )
        result = self.engine.can_access_resource(ctx, "field", "f1", "t1")
        assert result.allowed is True

    def test_with_scope_permission(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=[],
            scopes=["custom:custom.read"],
        )
        result = self.engine.can_access_resource(ctx, "custom", "c1", "t1", action="read")
        assert result.allowed is True


# ─────────────────────────────────────────────────────────────────────────────
# _has_permission internal
# ─────────────────────────────────────────────────────────────────────────────


class TestHasPermission:
    def test_super_admin_has_all(self):
        engine = PolicyEngine()
        ctx = PolicyContext(roles=["super_admin"])
        assert engine._has_permission(ctx, "anything:here") is True

    def test_scope_match(self):
        engine = PolicyEngine()
        ctx = PolicyContext(roles=[], scopes=["custom:perm"])
        assert engine._has_permission(ctx, "custom:perm") is True

    def test_scope_based_permission_for_viewer(self):
        """Viewer role permissions are accessible via explicit scopes"""
        engine = PolicyEngine()
        ctx = PolicyContext(roles=["viewer"], scopes=["fieldops:task.read"])
        assert engine._has_permission(ctx, "fieldops:task.read") is True

    def test_no_scope_no_super_admin(self):
        """Viewer role has fieldops:task.read via RBAC role grants"""
        engine = PolicyEngine()
        ctx = PolicyContext(roles=["viewer"])
        # After fixing has_permission signature mismatch (P1-3), the role-based
        # path now correctly passes a dict to has_permission() instead of a list.
        # The viewer role is granted fieldops:task.read in shared/security/rbac.py.
        result = engine._has_permission(ctx, "fieldops:task.read")
        assert result is True

    def test_invalid_role_raises_attribute_error(self):
        """Invalid role enum value raises ValueError which is caught"""
        engine = PolicyEngine()
        ctx = PolicyContext(roles=["nonexistent_role_xyz"])
        # "nonexistent_role_xyz" is not a valid Role enum, so Role(role) raises ValueError
        # which is caught by (ValueError, KeyError)
        assert engine._has_permission(ctx, "fieldops:task.read") is False

    def test_invalid_permission_value_caught(self):
        """Invalid Permission enum value raises ValueError which is caught"""
        engine = PolicyEngine()
        ctx = PolicyContext(roles=["viewer"])
        # "invalid:permission.xyz" is not a valid Permission enum
        # Role("viewer") succeeds, then Permission("invalid:permission.xyz") raises ValueError
        # which is caught
        assert engine._has_permission(ctx, "invalid:permission.xyz") is False


# ─────────────────────────────────────────────────────────────────────────────
# Global instance and convenience functions
# ─────────────────────────────────────────────────────────────────────────────


class TestGlobalInstance:
    def setup_method(self):
        import shared.security.policy_engine as pe_mod
        pe_mod._policy_engine = None

    def teardown_method(self):
        import shared.security.policy_engine as pe_mod
        pe_mod._policy_engine = None

    def test_get_policy_engine_singleton(self):
        e1 = get_policy_engine()
        e2 = get_policy_engine()
        assert e1 is e2

    def test_evaluate_policy_convenience(self):
        ctx = PolicyContext(is_authenticated=False)
        result = evaluate_policy(ctx, "/login")
        assert result.allowed is True

    def test_can_access_convenience(self):
        ctx = PolicyContext(
            is_authenticated=True,
            tenant_id="t1",
            roles=["admin"],
            scopes=["field:field.read"],
        )
        result = can_access(ctx, "field", "f1", "t1")
        assert result.allowed is True


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT_POLICIES
# ─────────────────────────────────────────────────────────────────────────────


class TestDefaultPolicies:
    def test_public_routes(self):
        public_paths = ["/login", "/register", "/forgot-password", "/reset-password", "/healthz", "/readyz", "/metrics"]
        for path in public_paths:
            assert path in DEFAULT_POLICIES
            assert DEFAULT_POLICIES[path].allow_public is True

    def test_dashboard_requires_auth(self):
        assert "/dashboard" in DEFAULT_POLICIES
        assert DEFAULT_POLICIES["/dashboard"].require_auth is True

    def test_admin_requires_roles(self):
        assert "/admin" in DEFAULT_POLICIES
        assert "admin" in DEFAULT_POLICIES["/admin"].require_roles
