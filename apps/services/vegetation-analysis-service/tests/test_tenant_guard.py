"""Regression tests for Gap C — tenant presence guards on sub-file endpoints.

Pins two invariants:

1. The ``require_tenant_id(user)`` helper in ``src/tenant_guard.py``
   rejects missing / empty tenant_id with a bilingual 403 across every
   supported user shape (dataclass, dict fallback, None).

2. Every protected handler in the sub-files (``parcel_endpoints``,
   ``boundary_endpoints``, ``gdd_endpoints``, ``spray_endpoints``,
   ``weather_endpoints``, ``vra_endpoints``) calls ``require_tenant_id``.
   Public reference endpoints (``/info``, ``/strategies``, ``/crops``,
   etc.) are explicitly exempt.

Defense-in-depth rationale: Kong strips unauthenticated requests at the
gateway, but a direct pod-network call or an intra-cluster sidecar bug
could bypass Kong. Every handler that touches tenant-scoped data must
enforce the check itself.
"""

from __future__ import annotations

import ast
import os
import sys
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)


# =============================================================================
# The helper itself
# =============================================================================


def test_require_tenant_id_accepts_dataclass_like_user():
    from tenant_guard import require_tenant_id

    user = MagicMock(tenant_id="t1")
    assert require_tenant_id(user) == "t1"


def test_require_tenant_id_accepts_dict_fallback():
    """When the ImportError fallback path produces ``{"token": "...",
    "tenant_id": "..."}`` instead of the full User dataclass, the guard
    must still work."""
    from tenant_guard import require_tenant_id

    assert require_tenant_id({"token": "tok", "tenant_id": "t1"}) == "t1"


def test_require_tenant_id_rejects_none():
    from tenant_guard import require_tenant_id

    with pytest.raises(HTTPException) as exc_info:
        require_tenant_id(None)
    assert exc_info.value.status_code == 403
    assert "tenant" in str(exc_info.value.detail).lower()


def test_require_tenant_id_rejects_empty_tenant():
    from tenant_guard import require_tenant_id

    # User exists but tenant_id is empty string
    user = MagicMock(tenant_id="")
    with pytest.raises(HTTPException) as exc_info:
        require_tenant_id(user)
    assert exc_info.value.status_code == 403


def test_require_tenant_id_rejects_missing_attr():
    from tenant_guard import require_tenant_id

    # Dict with no tenant_id key
    with pytest.raises(HTTPException) as exc_info:
        require_tenant_id({"token": "tok"})
    assert exc_info.value.status_code == 403


def test_require_tenant_id_bilingual_detail():
    from tenant_guard import require_tenant_id

    with pytest.raises(HTTPException) as exc_info:
        require_tenant_id(None)
    detail = str(exc_info.value.detail)
    assert "Tenant context required" in detail
    assert "سياق المستأجر مطلوب" in detail  # Arabic


def test_require_tenant_id_rejects_non_string_tenant_id():
    """Hardening (Copilot review): a truthy-but-non-string tenant_id
    (e.g., bare MagicMock() attribute, accidental int) must be rejected.
    Otherwise `MagicMock()` auto-attributes would silently pass."""
    from tenant_guard import require_tenant_id

    class _BadUser:
        tenant_id = 42  # int, not str

    with pytest.raises(HTTPException) as exc_info:
        require_tenant_id(_BadUser())
    assert exc_info.value.status_code == 403


def test_require_tenant_id_rejects_whitespace_only_tenant_id():
    """Whitespace-only tenant_id must be rejected (stripped → empty)."""
    from tenant_guard import require_tenant_id

    user = MagicMock(tenant_id="   ")
    with pytest.raises(HTTPException) as exc_info:
        require_tenant_id(user)
    assert exc_info.value.status_code == 403


def test_require_tenant_id_strips_whitespace_on_valid_tenant():
    """Valid tenant_id with whitespace returns the stripped value."""
    from tenant_guard import require_tenant_id

    user = MagicMock(tenant_id="  t1  ")
    assert require_tenant_id(user) == "t1"


# =============================================================================
# Integration — every protected sub-file handler calls the guard
# =============================================================================

_SUB_FILES = (
    "parcel_endpoints.py",
    "boundary_endpoints.py",
    "gdd_endpoints.py",
    "spray_endpoints.py",
    "weather_endpoints.py",
    "vra_endpoints.py",
)

# Reference / catalog endpoints that stay unauthenticated on purpose
_PUBLIC_ROUTE_SUBSTRINGS = {"/info", "/strategies", "/categories", "/list"}
_PUBLIC_ROUTE_SUFFIXES = ("/crops",)


def _is_public_route(route: str) -> bool:
    if any(p in route for p in _PUBLIC_ROUTE_SUBSTRINGS):
        return True
    return route.endswith(_PUBLIC_ROUTE_SUFFIXES)


def _handlers_missing_guard(fname: str) -> list[str]:
    """Return the names of authenticated handlers in *fname* that are
    missing a ``require_tenant_id`` / ``_enforce_tenant`` / tenant_id
    check in their body."""
    path = os.path.join(os.path.dirname(__file__), "..", "src", fname)
    with open(path) as f:
        src = f.read()
    tree = ast.parse(src)

    missing: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        # Only route handlers
        route = None
        for deco in node.decorator_list:
            if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute):
                if deco.func.attr in {"get", "post", "put", "patch", "delete"}:
                    if deco.args and isinstance(deco.args[0], ast.Constant):
                        route = deco.args[0].value
        if not route or _is_public_route(route):
            continue

        body_src = ast.get_source_segment(src, node) or ""
        args_src = " ".join(ast.get_source_segment(src, a) or "" for a in node.args.args)
        has_auth = "get_current_user" in (args_src + body_src)
        if not has_auth:
            # Not in scope — separate "no auth" class of gap; this test
            # only pins the "has auth but missing tenant check" class
            continue

        has_guard = any(
            marker in body_src
            for marker in (
                "require_tenant_id",
                "_enforce_tenant",
                "user.tenant_id",
                'getattr(user, "tenant_id"',
                "getattr(user, 'tenant_id'",
                'getattr(_user, "tenant_id"',
                "getattr(_user, 'tenant_id'",
            )
        )
        if not has_guard:
            missing.append(f"{fname}::{node.name} ({route})")
    return missing


@pytest.mark.parametrize("fname", _SUB_FILES)
def test_subfile_handlers_all_enforce_tenant_presence(fname: str):
    """Defense-in-depth pin: every authenticated sub-file handler that
    isn't a public reference endpoint must call ``require_tenant_id``."""
    missing = _handlers_missing_guard(fname)
    assert not missing, (
        f"{fname}: {len(missing)} authenticated handler(s) bypass tenant "
        f"presence check — Kong is the only thing between the caller and "
        f"tenant data. Add `require_tenant_id(_user)` to:\n  " + "\n  ".join(missing)
    )


def test_tenant_guard_module_import_path():
    """The guard module must be importable from ``src.tenant_guard``
    without any side effects (no env lookups, no network calls). Keeps
    it safe for sub-file imports that happen during FastAPI startup."""
    import importlib
    import sys as _sys

    # Remove any cached import to exercise a cold path
    for mod in list(_sys.modules):
        if mod.endswith("tenant_guard"):
            del _sys.modules[mod]
    mod = importlib.import_module("src.tenant_guard")
    assert callable(mod.require_tenant_id)
