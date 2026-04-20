"""Regression tests for PR #1703 — residual gaps from the comprehensive
audit after PRs #1697-#1702 landed.

Pins:
  1. ``tenant_guard.validate_field_id`` rejects malformed ids.
  2. ``tenant_guard.verify_field_owned_by_tenant`` composes tenant +
     validate + cross-service ownership (via field_ownership).
  3. Bearer token forwarded from ``http_request`` to the verifier.
  4. The 4 sub-file ``{field_id}`` handlers use the composed helper.
  5. The 3 main.py body-param handlers call
     ``_verify_field_owned_by_tenant`` with the body's field_id.
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
# tenant_guard.validate_field_id
# =============================================================================


def test_validate_field_id_rejects_empty():
    from tenant_guard import validate_field_id

    with pytest.raises(HTTPException) as exc:
        validate_field_id("")
    assert exc.value.status_code == 400


def test_validate_field_id_rejects_too_long():
    from tenant_guard import validate_field_id

    with pytest.raises(HTTPException) as exc:
        validate_field_id("a" * 101)
    assert exc.value.status_code == 400


def test_validate_field_id_accepts_valid():
    from tenant_guard import validate_field_id

    validate_field_id("field_123")
    validate_field_id("00000000-0000-0000-0000-000000000001")


# =============================================================================
# tenant_guard.verify_field_owned_by_tenant — composition
# =============================================================================


@pytest.mark.asyncio
async def test_verify_field_owned_by_tenant_raises_403_when_no_tenant():
    """The composed helper must inherit require_tenant_id's 403 for
    users without a tenant."""
    from tenant_guard import verify_field_owned_by_tenant

    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(user=None, field_id="field_1")
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_verify_field_owned_by_tenant_raises_400_on_bad_field_id():
    """The composed helper must inherit validate_field_id's 400 BEFORE
    reaching the HTTP call to field-management-service."""
    from tenant_guard import verify_field_owned_by_tenant

    user = MagicMock(tenant_id="t1")
    with pytest.raises(HTTPException) as exc:
        await verify_field_owned_by_tenant(user=user, field_id="")
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_verify_field_owned_by_tenant_forwards_bearer(monkeypatch):
    """Mirror of the same invariant for main._verify_field_owned_by_tenant:
    Bearer JWT from inbound request must reach field_ownership."""
    from tenant_guard import verify_field_owned_by_tenant

    captured: dict = {}

    async def _fake_verify(tenant_id, field_id, bearer_token=None, **kwargs):
        captured["bearer_token"] = bearer_token

    try:
        monkeypatch.setattr("src.field_ownership.verify_field_ownership", _fake_verify)
    except AttributeError:
        pass
    try:
        monkeypatch.setattr("field_ownership.verify_field_ownership", _fake_verify)
    except AttributeError:
        pass

    user = MagicMock(tenant_id="t1")
    mock_req = MagicMock()
    mock_req.headers = {"Authorization": "Bearer jwt-abc"}

    tenant_id = await verify_field_owned_by_tenant(
        user=user, field_id="field_1", http_request=mock_req
    )
    assert tenant_id == "t1"
    assert captured["bearer_token"] == "jwt-abc"


# =============================================================================
# Pin: the 4 {field_id} sub-file handlers use the composed helper
# =============================================================================


_SUBFILE_FIELD_ID_HANDLERS = [
    ("boundary_endpoints.py", "get_boundary_changes"),
    ("gdd_endpoints.py", "get_gdd_chart"),
    ("vra_endpoints.py", "get_management_zones"),
    ("vra_endpoints.py", "get_field_prescriptions"),
]


@pytest.mark.parametrize("fname,handler", _SUBFILE_FIELD_ID_HANDLERS)
def test_subfile_field_id_handlers_use_ownership_verification(fname: str, handler: str):
    """Regression: every sub-file handler whose route contains
    ``{field_id}`` must delegate to ``verify_field_owned_by_tenant``
    (which composes tenant + validate + cross-service ownership)."""
    src_path = os.path.join(os.path.dirname(__file__), "..", "src", fname)
    with open(src_path, encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == handler:
            body_src = ast.get_source_segment(src, node) or ""
            assert "verify_field_owned_by_tenant" in body_src, (
                f"{fname}::{handler} does not call verify_field_owned_by_tenant. "
                "Ownership check missing — cross-tenant field_id access possible."
            )
            # Also confirm http_request is threaded through
            arg_names = [a.arg for a in node.args.args]
            assert "http_request" in arg_names, (
                f"{fname}::{handler} does not accept http_request. "
                "Bearer JWT can't be forwarded to field-management-service."
            )
            return
    pytest.fail(f"Handler {handler} not found in {fname}")


# =============================================================================
# Pin: the 3 main.py body-param endpoints now verify ownership
# =============================================================================


_MAIN_BODY_PARAM_HANDLERS = [
    "interpret_indices",
    "predict_yield",
    "interpolate_cloudy_pixels",
]


@pytest.mark.parametrize("handler", _MAIN_BODY_PARAM_HANDLERS)
def test_main_body_param_handlers_verify_ownership(handler: str):
    """Regression: body-param handlers in main.py that take a field_id
    (in body or query) must call ``_verify_field_owned_by_tenant`` —
    the tenant-only ``_require_tenant_id`` is not sufficient for
    field-scoped data."""
    src_path = os.path.join(os.path.dirname(__file__), "..", "src", "main.py")
    with open(src_path, encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == handler:
            body_src = ast.get_source_segment(src, node) or ""
            assert "_verify_field_owned_by_tenant" in body_src, (
                f"main.py::{handler} does not call _verify_field_owned_by_tenant. "
                "Missing ownership check for field-scoped operation."
            )
            arg_names = [a.arg for a in node.args.args]
            assert "http_request" in arg_names, (
                f"main.py::{handler} does not accept http_request. "
                "Bearer JWT can't be forwarded to field-management-service."
            )
            return
    pytest.fail(f"Handler {handler} not found in main.py")
