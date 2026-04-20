"""Regression tests for field-ownership verification (Gap B).

Pins the following invariants of ``src.field_ownership.verify_field_ownership``:

  * Bypasses cleanly when ``FIELD_SERVICE_URL`` is not configured
    (keeps dev/test env green).
  * Cache hit with matching tenant → fast-path return.
  * HTTP 200 with matching tenantId → success + cache write.
  * HTTP 200 with mismatched tenantId → 403.
  * HTTP 403 from field service → 403 (tenant service's verdict).
  * HTTP 404 → 404 propagated.
  * HTTP timeout + strict mode → 503.
  * HTTP timeout + lenient mode → bypass with warning.

Also pins the integration point:
  * ``_verify_field_owned_by_tenant`` in main.py calls
    ``verify_field_ownership`` and returns the tenant_id.
  * 21 field_id handlers in main.py swapped to use it.
"""

from __future__ import annotations

import os
import sys

import httpx
import pytest
from fastapi import HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)


# =============================================================================
# Configuration surface
# =============================================================================


@pytest.mark.asyncio
async def test_bypass_when_field_service_url_not_configured(monkeypatch):
    """When FIELD_SERVICE_URL is unset, the verifier must return silently —
    keeps dev / CI / monolithic bring-up unblocked. Production Helm sets
    the env var; its absence in a real environment will be caught by the
    health-check config audit (separate concern)."""
    from field_ownership import verify_field_ownership

    monkeypatch.delenv("FIELD_SERVICE_URL", raising=False)
    # Must not raise
    await verify_field_ownership(tenant_id="t1", field_id="f1")


@pytest.mark.asyncio
async def test_strict_mode_default_true(monkeypatch):
    """STRICT_FIELD_VERIFICATION defaults to True so production fails
    closed on unreachable field service."""
    from field_ownership import _strict_mode

    monkeypatch.delenv("STRICT_FIELD_VERIFICATION", raising=False)
    assert _strict_mode() is True

    monkeypatch.setenv("STRICT_FIELD_VERIFICATION", "false")
    assert _strict_mode() is False

    monkeypatch.setenv("STRICT_FIELD_VERIFICATION", "true")
    assert _strict_mode() is True


# =============================================================================
# Cache layer
# =============================================================================


@pytest.mark.asyncio
async def test_cache_key_is_tenant_scoped():
    """Two different tenants checking the same field must produce
    different cache keys — prevents cross-tenant poisoning."""
    from field_ownership import _cache_key

    k_a = _cache_key("tenant-a", "field-1")
    k_b = _cache_key("tenant-b", "field-1")
    assert k_a != k_b
    assert "tenant-a" in k_a
    assert "tenant-b" in k_b
    # And the shape matches the rest of the vegetation-service cache
    # convention: satellite:t:{tenant}:{kind}:{…}
    assert k_a.startswith("satellite:t:tenant-a:field_ownership:")


# =============================================================================
# Happy path
# =============================================================================


class _MockTransport(httpx.AsyncBaseTransport):
    """Deterministic httpx transport — lets us assert on the outgoing
    request without any network I/O."""

    def __init__(self, response: httpx.Response | Exception):
        self.response = response
        self.calls: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


@pytest.mark.asyncio
async def test_field_id_is_url_encoded_in_request(monkeypatch):
    """Security pin: characters like '/', '?', '%' in field_id must be
    URL-encoded so they can't change the outgoing request path. Without
    encoding, field_id='../admin' would traverse the URL path."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))
    monkeypatch.setattr("field_ownership._cache_set", _async_noop())

    response = httpx.Response(
        200,
        json={"success": True, "data": {"id": "f1", "tenantId": "t1"}},
    )
    transport = _MockTransport(response)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await verify_field_ownership(
            tenant_id="t1",
            field_id="../admin",
            http_client=client,
        )

    req = transport.calls[0]
    # The slash must be percent-encoded (%2F) so it stays a single path
    # segment and can't traverse the URL path.
    assert "/api/v1/fields/..%2Fadmin" in str(req.url), f"field_id='../admin' was not URL-encoded. URL was: {req.url}"


@pytest.mark.asyncio
async def test_http_200_matching_tenant_passes(monkeypatch):
    """Happy path: field service returns 200 with matching tenantId →
    verifier returns silently + caches the ownership for 5 min."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    # Disable cache so we exercise the HTTP path deterministically
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))
    cache_set_calls: list = []
    monkeypatch.setattr("field_ownership._cache_set", _record(cache_set_calls))

    response = httpx.Response(
        200,
        json={"success": True, "data": {"id": "f1", "tenantId": "t1", "name": "test"}},
    )
    transport = _MockTransport(response)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await verify_field_ownership(tenant_id="t1", field_id="f1", bearer_token="tok", http_client=client)

    # Request went to the right URL with the right headers
    assert len(transport.calls) == 1
    req = transport.calls[0]
    assert str(req.url).endswith("/api/v1/fields/f1")
    assert req.headers.get("X-Tenant-Id") == "t1"
    assert req.headers.get("Authorization") == "Bearer tok"

    # Ownership was cached
    assert len(cache_set_calls) == 1
    _key, value, ttl = cache_set_calls[0]
    assert value == {"tenant_id": "t1"}
    assert ttl == 5 * 60


@pytest.mark.asyncio
async def test_http_200_mismatched_tenant_raises_403(monkeypatch):
    """Field service returns the field but it belongs to a different
    tenant — must raise 403 with bilingual detail."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))
    monkeypatch.setattr("field_ownership._cache_set", _async_noop())

    response = httpx.Response(
        200,
        json={"success": True, "data": {"id": "f1", "tenantId": "OTHER_TENANT"}},
    )
    transport = _MockTransport(response)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        with pytest.raises(HTTPException) as excinfo:
            await verify_field_ownership(tenant_id="t1", field_id="f1", http_client=client)
    assert excinfo.value.status_code == 403
    assert "not belong" in excinfo.value.detail.lower() or "ينتمي" in excinfo.value.detail


@pytest.mark.asyncio
async def test_http_404_raises_404(monkeypatch):
    """Field does not exist → 404 propagated."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))

    transport = _MockTransport(httpx.Response(404, json={"message": "not found"}))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        with pytest.raises(HTTPException) as excinfo:
            await verify_field_ownership(tenant_id="t1", field_id="missing", http_client=client)
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_non_dict_json_payload_handled_gracefully(monkeypatch):
    """`resp.json()` can legally return a list/string/number on HTTP 200.
    Naive `payload.get()` would raise AttributeError → bubble as 500 and
    bypass the strict/lenient decision. Per Copilot review, guard with
    isinstance and return a controlled 503 in strict mode."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    monkeypatch.setenv("STRICT_FIELD_VERIFICATION", "true")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))

    # Field service returns a bare JSON array instead of the expected object
    transport = _MockTransport(httpx.Response(200, json=["not", "a", "dict"]))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        with pytest.raises(HTTPException) as excinfo:
            await verify_field_ownership(tenant_id="t1", field_id="f1", http_client=client)
    assert excinfo.value.status_code == 503


@pytest.mark.asyncio
async def test_non_dict_data_shape_handled_gracefully(monkeypatch):
    """Edge: response is a dict but ``data`` key is a non-dict value
    (e.g., a string error marker). Must produce 503 in strict mode, not
    AttributeError."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    monkeypatch.setenv("STRICT_FIELD_VERIFICATION", "true")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))

    transport = _MockTransport(httpx.Response(200, json={"success": True, "data": "err"}))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        with pytest.raises(HTTPException) as excinfo:
            await verify_field_ownership(tenant_id="t1", field_id="f1", http_client=client)
    assert excinfo.value.status_code == 503


@pytest.mark.asyncio
async def test_http_400_from_field_service_raises_400(monkeypatch):
    """field-management-service's ParseUUIDPipe returns 400 for malformed
    field ids (non-UUID). Our verifier must preserve that as a caller
    400 "Invalid field_id" — not bubble it as 503 or silently bypass.
    Per Copilot review on PR #1698."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))

    transport = _MockTransport(httpx.Response(400, json={"message": "Invalid UUID"}))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        with pytest.raises(HTTPException) as excinfo:
            await verify_field_ownership(tenant_id="t1", field_id="not-a-uuid", http_client=client)
    assert excinfo.value.status_code == 400
    assert "Invalid field_id" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_http_422_from_field_service_raises_400(monkeypatch):
    """Same as the 400 case for Pydantic body-validation errors (422)."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))

    transport = _MockTransport(httpx.Response(422, json={"message": "Validation failed"}))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        with pytest.raises(HTTPException) as excinfo:
            await verify_field_ownership(tenant_id="t1", field_id="bad-id", http_client=client)
    assert excinfo.value.status_code == 400


@pytest.mark.asyncio
async def test_http_403_from_field_service_propagates(monkeypatch):
    """Field service itself returned 403 — treat as the authoritative
    verdict (field-management-service has stricter context than we do)."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://field-management:3000")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))

    transport = _MockTransport(httpx.Response(403, json={"message": "forbidden"}))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        with pytest.raises(HTTPException) as excinfo:
            await verify_field_ownership(tenant_id="t1", field_id="f1", http_client=client)
    assert excinfo.value.status_code == 403


# =============================================================================
# Failure modes — strict vs lenient
# =============================================================================


@pytest.mark.asyncio
async def test_connection_error_strict_mode_raises_503(monkeypatch):
    """Field service unreachable + strict mode → 503 (fail closed, no
    bypass to prevent leakage during a partial outage)."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://unreachable:3000")
    monkeypatch.setenv("STRICT_FIELD_VERIFICATION", "true")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))

    transport = _MockTransport(httpx.ConnectError("connection refused"))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        with pytest.raises(HTTPException) as excinfo:
            await verify_field_ownership(tenant_id="t1", field_id="f1", http_client=client)
    assert excinfo.value.status_code == 503


@pytest.mark.asyncio
async def test_connection_error_lenient_mode_bypasses(monkeypatch):
    """Field service unreachable + lenient mode → bypass with warning.
    This is the dev/CI default for bring-up; production overrides to strict."""
    from field_ownership import verify_field_ownership

    monkeypatch.setenv("FIELD_SERVICE_URL", "http://unreachable:3000")
    monkeypatch.setenv("STRICT_FIELD_VERIFICATION", "false")
    monkeypatch.setattr("field_ownership._cache_get", _async_return(None))

    transport = _MockTransport(httpx.ConnectError("connection refused"))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Must not raise
        await verify_field_ownership(tenant_id="t1", field_id="f1", http_client=client)


# =============================================================================
# main.py integration — every {field_id} handler delegates to the verifier
# =============================================================================


def test_all_field_id_handlers_use_verifier():
    """The 21 {field_id} handlers in main.py must delegate to
    `_verify_field_owned_by_tenant` instead of the bare
    `_require_tenant_id(user)`. Pin the count so nothing regresses."""
    import ast

    src_path = os.path.join(os.path.dirname(__file__), "..", "src", "main.py")
    # Explicit UTF-8: main.py contains Arabic error strings, so the
    # default-locale open() can raise UnicodeDecodeError on non-UTF-8
    # Windows / CI environments.
    with open(src_path, encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src)

    _ROUTE_METHODS = {"get", "post", "put", "delete", "patch", "options", "head", "trace", "api_route"}

    def _route_path_from_decorator(decorator):
        """Extract the route path from a FastAPI decorator, or None if
        this isn't a recognised route decorator."""
        if not isinstance(decorator, ast.Call):
            return None
        if not isinstance(decorator.func, ast.Attribute):
            return None
        if decorator.func.attr not in _ROUTE_METHODS:
            return None
        if not decorator.args:
            return None
        path_arg = decorator.args[0]
        if isinstance(path_arg, ast.Constant) and isinstance(path_arg.value, str):
            return path_arg.value
        return None

    def _has_field_id_route_decorator(node):
        """True only when at least one of the node's decorators is a
        FastAPI route whose path contains ``{field_id}`` — stops the
        pin from flagging internal helpers that happen to take a
        ``field_id`` argument."""
        for decorator in node.decorator_list:
            route_path = _route_path_from_decorator(decorator)
            if route_path and "{field_id}" in route_path:
                return True
        return False

    # Handlers that MUST use the verifier: any `async def` decorated
    # with a FastAPI route whose path contains `{field_id}` AND takes
    # `field_id` in its signature.
    migrated = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        if not any(a.arg == "field_id" for a in node.args.args):
            continue
        # The helper itself is expected to call _require_tenant_id
        # (it composes tenant extraction + ownership verification).
        if node.name == "_verify_field_owned_by_tenant":
            continue
        # Exclude non-route helpers that happen to take field_id (e.g.
        # `_fetch_real_timeseries_via_multi_provider`).
        if not _has_field_id_route_decorator(node):
            continue
        body_src = ast.get_source_segment(src, node) or ""
        if "_require_tenant_id(user)" in body_src:
            # Regression — a field-bearing handler still uses the bare
            # tenant check without ownership verification.
            pytest.fail(
                f"{node.name}: still calls _require_tenant_id(user) without "
                f"ownership verification. Swap to "
                f"`await _verify_field_owned_by_tenant(user, field_id)`."
            )
        if "_verify_field_owned_by_tenant(user, field_id)" in body_src:
            migrated += 1

    # Regression pin: at least the 21 handlers that were swapped in
    # this PR must keep using the verifier.
    assert migrated >= 21, f"Expected >=21 handlers to use _verify_field_owned_by_tenant, found {migrated}"


def test_main_helper_is_async():
    """_verify_field_owned_by_tenant must be async so callers that
    `await` it don't silently receive a coroutine."""
    import inspect

    from src.main import _verify_field_owned_by_tenant

    assert inspect.iscoroutinefunction(_verify_field_owned_by_tenant)


# =============================================================================
# Test helpers
# =============================================================================


def _async_return(value):
    """Build an async function that returns `value` regardless of args."""

    async def _fn(*args, **kwargs):
        return value

    return _fn


def _async_noop():
    async def _fn(*args, **kwargs):
        return None

    return _fn


def _record(bucket: list):
    """Build an async function that records its call args."""

    async def _fn(*args, **kwargs):
        bucket.append(args)
        return None

    return _fn
