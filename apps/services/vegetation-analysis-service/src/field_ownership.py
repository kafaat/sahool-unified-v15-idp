"""Cross-service field-ownership verification.

Closes the latent tenant-isolation gap documented in
``main._require_tenant_id`` — that helper only verifies the *caller*
has a tenant; it does not check whether the ``{field_id}`` path
parameter actually belongs to that tenant. Until this module landed,
any authenticated user with any tenant could query field-scoped
endpoints for any field id.

Resolution pattern (Climate FieldView / FarmBeats / John Deere
Operations Center convention): the field-ownership table lives in
one canonical service (``field-management-service`` on
``SERVICE_PORTS.FIELD_MANAGEMENT=3000``). Every other service that
takes a ``field_id`` in its path must delegate the ownership check
to that service.

This module implements that delegation with:

  * A 5-minute Redis cache keyed by ``(tenant_id, field_id)`` so
    repeat calls for the same field within the TTL window don't
    pay the HTTP round-trip.
  * Honest failure modes — the caller picks strict vs lenient via
    ``STRICT_FIELD_VERIFICATION`` env var.
  * Explicit bypass when ``FIELD_SERVICE_URL`` is not configured
    (dev / test / monolithic bring-up) so tests don't break.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


def _field_service_url() -> str | None:
    """Resolved at call time (not import time) so tests can monkey-patch
    ``os.environ`` and have the helper pick up the change."""
    return os.environ.get("FIELD_SERVICE_URL")


def _strict_mode() -> bool:
    """When True, an unreachable field-management-service causes a 503
    instead of a lenient bypass. Default True in production; tests can
    flip via env var."""
    return os.environ.get("STRICT_FIELD_VERIFICATION", "true").lower() == "true"


# Cache TTL — field ownership rarely changes. 5 min is the EOSDA /
# FarmBeats convention (short enough that a farm transfer takes effect
# within a user session, long enough to kill the round-trip on hot
# endpoints like `/v1/timeseries/{field_id}`).
_OWNERSHIP_CACHE_TTL = 5 * 60

# HTTP timeout — the field service SLO is 250 ms p99; 2 s is generous
# for tail-latency without letting a slow dep block the request too long.
_HTTP_TIMEOUT = 2.0


# =============================================================================
# Cache helpers (use the existing tenant-scoped cache module)
# =============================================================================


def _cache_key(tenant_id: str, field_id: str) -> str:
    """Tenant-scoped cache key. Same convention as
    ``cache._ns()`` so all vegetation-service caches share one
    Redis namespace."""
    tenant = (tenant_id or "global").strip() or "global"
    return f"satellite:t:{tenant}:field_ownership:{field_id}"


def _resolve_cache_fn(name: str):
    """Import cache_get / cache_set defensively so a genuine error inside
    ``cache.py`` (e.g. missing dependency) surfaces instead of being
    swallowed as "module missing" — only the relative-vs-absolute path
    choice is tolerated.

    Catches both ``ModuleNotFoundError`` (when the module file is
    missing) AND the bare ``ImportError`` Python raises when a relative
    import has no parent package (i.e. standalone test execution).
    """
    try:
        from .cache import cache_get, cache_set  # type: ignore

        return {"cache_get": cache_get, "cache_set": cache_set}[name]
    except ModuleNotFoundError as exc:
        if exc.name not in {"cache", (__package__ + ".cache") if __package__ else "cache"}:
            raise
    except ImportError as exc:
        # Raised as bare ImportError (not ModuleNotFoundError) when the
        # module is imported standalone (no package context).
        if "relative import" not in str(exc):
            raise
    try:
        from cache import cache_get, cache_set  # type: ignore

        return {"cache_get": cache_get, "cache_set": cache_set}[name]
    except ModuleNotFoundError as exc:
        if exc.name != "cache":
            raise
        return None


async def _cache_get(key: str) -> dict[str, Any] | None:
    """Best-effort Redis GET. Returns None on any failure."""
    fn = _resolve_cache_fn("cache_get")
    if fn is None:
        return None
    try:
        return await fn(key)
    except Exception:
        return None


async def _cache_set(key: str, value: dict[str, Any], ttl: int) -> None:
    """Best-effort Redis SETEX. Silent on failure."""
    fn = _resolve_cache_fn("cache_set")
    if fn is None:
        return
    try:
        await fn(key, value, ttl)
    except Exception:
        pass


# =============================================================================
# Public API
# =============================================================================


async def verify_field_ownership(
    tenant_id: str,
    field_id: str,
    bearer_token: str | None = None,
    *,
    http_client: httpx.AsyncClient | None = None,
) -> None:
    """Verify that ``field_id`` belongs to ``tenant_id``. Raises on mismatch.

    :param tenant_id: The authenticated caller's tenant_id (already
        extracted by ``_require_tenant_id``).
    :param field_id: The ``{field_id}`` path parameter.
    :param bearer_token: Forwarded to the field service as the
        ``Authorization: Bearer …`` header so the field service can
        re-authenticate and enforce its own RBAC. When ``None``, the
        field service relies on the tenant-id header alone (which is
        fine for in-cluster calls behind Kong).
    :param http_client: Inject a client for testing. Default creates a
        short-lived one per call (acceptable overhead given the cache
        hit-rate should be > 95% on warm endpoints).

    Raises:
      * ``HTTPException 403`` — field exists but belongs to a different
        tenant, OR the field service itself returned 403.
      * ``HTTPException 404`` — field does not exist.
      * ``HTTPException 503`` — field service unreachable AND strict
        mode is on. In lenient mode the function logs and returns,
        letting the caller proceed (dev / test convenience only).

    Returns silently on success — the caller's existing ``_require_tenant_id``
    has already authenticated the session.
    """
    service_url = _field_service_url()
    if not service_url:
        # Lenient-by-default when not configured — keeps dev & CI green.
        # Production deployments set FIELD_SERVICE_URL via Helm.
        logger.info("field_ownership_verification_skipped reason=FIELD_SERVICE_URL_not_configured")
        return

    if not tenant_id or not field_id:
        # Called before _require_tenant_id — programmer error.
        raise HTTPException(
            status_code=500,
            detail=("Field-ownership check invoked without context | تم استدعاء فحص ملكية الحقل بدون سياق"),
        )

    # 1. Cache lookup
    cache_key = _cache_key(tenant_id, field_id)
    cached = await _cache_get(cache_key)
    if cached is not None:
        cached_tenant = cached.get("tenant_id")
        if cached_tenant == tenant_id:
            return
        # Shouldn't happen (cache is tenant-scoped) but guard anyway
        raise HTTPException(
            status_code=403,
            detail="Field does not belong to this tenant | الحقل لا ينتمي إلى هذا المستأجر",
        )

    # 2. Live HTTP call to field-management-service
    # URL-encode the field_id path segment so characters like '/', '?', '%'
    # can't change request semantics or escape the intended endpoint
    # (e.g., a field_id of "../../admin" would otherwise traverse paths).
    from urllib.parse import quote as _url_quote

    safe_field_id = _url_quote(field_id, safe="")
    url = f"{service_url.rstrip('/')}/api/v1/fields/{safe_field_id}"
    headers: dict[str, str] = {"X-Tenant-Id": tenant_id}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    owns_client = http_client is None
    client = http_client or httpx.AsyncClient(timeout=_HTTP_TIMEOUT)
    try:
        try:
            resp = await client.get(url, headers=headers)
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPError) as e:
            if _strict_mode():
                logger.warning(f"field_ownership_verify_failed strict=true field_id={field_id} error={e}")
                raise HTTPException(
                    status_code=503,
                    detail=("Field ownership service unavailable | خدمة التحقق من ملكية الحقل غير متاحة"),
                ) from e
            logger.warning(
                f"field_ownership_verify_failed strict=false field_id={field_id} error={e} — allowing through"
            )
            return

        if resp.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Field not found | الحقل غير موجود",
            )
        if resp.status_code == 403:
            # field-management-service enforces tenant ownership itself
            # and returned 403 — that's the definitive verdict.
            raise HTTPException(
                status_code=403,
                detail="Field does not belong to this tenant | الحقل لا ينتمي إلى هذا المستأجر",
            )
        if resp.status_code in (400, 422):
            # field-management-service's ``ParseUUIDPipe`` rejects
            # malformed field ids (non-UUID) with 400, and Pydantic
            # body validation errors return 422. Preserve that as a
            # caller-facing 400 — otherwise strict mode would surface
            # it as 503 "service unavailable" (misleading) and lenient
            # mode would silently bypass validation. Per Copilot review.
            raise HTTPException(
                status_code=400,
                detail="Invalid field_id | معرف الحقل غير صالح",
            )
        if resp.status_code != 200:
            # Any other unexpected status — strict mode 503, lenient bypass.
            if _strict_mode():
                logger.warning(
                    f"field_ownership_verify_unexpected_status status={resp.status_code} field_id={field_id}"
                )
                raise HTTPException(
                    status_code=503,
                    detail="Field ownership check failed | فشل التحقق من ملكية الحقل",
                )
            return

        # 3. Parse + verify
        try:
            payload = resp.json()
        except (ValueError, json.JSONDecodeError):
            # Shouldn't happen from a NestJS service returning JSON, but guard anyway
            if _strict_mode():
                raise HTTPException(
                    status_code=503,
                    detail=("Field service returned invalid JSON | خدمة الحقول أعادت JSON غير صالح"),
                )
            return

        # A well-formed field response is a JSON object (``{success, data, etag}``).
        # `resp.json()` can legally return a list/string/number on HTTP 200, so
        # the naive ``payload.get(...)`` would raise AttributeError and bubble as
        # a 500 — bypass the strict/lenient decision. Guard with isinstance.
        if not isinstance(payload, dict):
            if _strict_mode():
                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Field service returned unexpected payload shape | خدمة الحقول أعادت شكل استجابة غير متوقع"
                    ),
                )
            return

        data = payload.get("data", payload)  # field-management wraps in {success, data, etag}
        if not isinstance(data, dict):
            if _strict_mode():
                raise HTTPException(
                    status_code=503,
                    detail=("Field service returned unexpected data shape | خدمة الحقول أعادت شكل بيانات غير متوقع"),
                )
            return

        remote_tenant = data.get("tenantId") or data.get("tenant_id")
        if not remote_tenant:
            # Missing tenantId in response — can't verify.
            if _strict_mode():
                raise HTTPException(
                    status_code=503,
                    detail=("Field response missing tenantId | استجابة الحقل بدون معرف المستأجر"),
                )
            return

        if remote_tenant != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="Field does not belong to this tenant | الحقل لا ينتمي إلى هذا المستأجر",
            )

        # 4. Cache the confirmed ownership
        await _cache_set(cache_key, {"tenant_id": remote_tenant}, _OWNERSHIP_CACHE_TTL)
    finally:
        if owns_client:
            await client.aclose()
