"""Field ownership verification for advisory-service.

Defense-in-depth companion to the tenant + field-ownership guards we
added to ``vegetation-analysis-service`` in PR #1704. Before advisory
fans out a comprehensive aggregation (8 downstream services) or runs a
loan-verification flow, it must confirm the authenticated tenant
actually owns the ``field_id`` they're asking about — otherwise a
valid JWT for tenant A could harvest data for tenant B's fields via
this service, bypassing each downstream's individual gate.

Delegates the authoritative check to ``field-management-service``
(the canonical owner of the ``fields`` table). Matches the pattern in
``apps/services/vegetation-analysis-service/src/field_ownership.py``,
but kept trimmed here — advisory only needs the "does this field
belong to this tenant?" verdict, not the detailed error categorisation
vegetation exposes.

Strict vs lenient mode (``ADVISORY_STRICT_OWNERSHIP`` env var):
  * ``strict=true``  → any field-management outage raises 503.
  * ``strict=false`` → outages downgrade to a warning and allow the
    request through (so a temporary FMS blip doesn't break advisory).

Default is ``false`` — each downstream service enforces its own
tenant guard, so advisory's check is defense-in-depth rather than
the sole line of defence.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = httpx.Timeout(5.0, connect=3.0)


def _field_service_url() -> str:
    """Return the field-management-service base URL from env."""
    return os.getenv("FIELD_MANAGEMENT_URL", "http://field-management-service:3000").rstrip("/")


def _strict_mode() -> bool:
    return os.getenv("ADVISORY_STRICT_OWNERSHIP", "false").lower() in {"1", "true", "yes"}


def _extract_bearer(http_request: Request | None) -> str | None:
    """Pull a Bearer token out of the inbound request, if any."""
    if http_request is None:
        return None
    auth = http_request.headers.get("authorization") or http_request.headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip() or None
    return None


async def verify_field_owned_by_tenant(
    *,
    tenant_id: str,
    field_id: str,
    http_request: Request | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> None:
    """Raise if *field_id* doesn't belong to *tenant_id*.

    :raises HTTPException 400: ``field_id`` rejected by field-management
        as malformed (non-UUID / 422 body-validation).
    :raises HTTPException 403: field belongs to a different tenant.
    :raises HTTPException 404: field not found.
    :raises HTTPException 503: field-management unreachable AND strict
        mode is on. In lenient mode, outages log a warning and
        return without raising.
    """
    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Tenant context required | سياق المستأجر مطلوب",
        )
    # Minimal shape gate — field-management's ParseUUIDPipe will do
    # the authoritative UUID check, but rejecting obviously bogus ids
    # here saves a network hop.
    if not field_id or len(field_id) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid field_id | معرف الحقل غير صالح",
        )

    from urllib.parse import quote as _url_quote

    safe_field_id = _url_quote(field_id, safe="")
    url = f"{_field_service_url()}/api/v1/fields/{safe_field_id}"
    headers: dict[str, str] = {"X-Tenant-Id": tenant_id}
    bearer = _extract_bearer(http_request)
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"

    owns_client = http_client is None
    client = http_client or httpx.AsyncClient(timeout=_HTTP_TIMEOUT)
    try:
        try:
            resp = await client.get(url, headers=headers)
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPError) as e:
            if _strict_mode():
                logger.warning(
                    "advisory.field_ownership.unreachable strict=true field=%s error=%s",
                    field_id,
                    type(e).__name__,
                )
                raise HTTPException(
                    status_code=503,
                    detail="Field ownership service unavailable | خدمة التحقق من ملكية الحقل غير متاحة",
                ) from e
            logger.warning(
                "advisory.field_ownership.unreachable strict=false field=%s error=%s — allowing through",
                field_id,
                type(e).__name__,
            )
            return

        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Field not found | الحقل غير موجود")
        if resp.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Field does not belong to this tenant | الحقل لا ينتمي إلى هذا المستأجر",
            )
        if resp.status_code in (400, 422):
            raise HTTPException(status_code=400, detail="Invalid field_id | معرف الحقل غير صالح")
        if resp.status_code != 200:
            if _strict_mode():
                raise HTTPException(
                    status_code=503,
                    detail="Field ownership check failed | فشل التحقق من ملكية الحقل",
                )
            return

        # 200 — parse and cross-check tenant. FMS wraps the payload as
        # `{success, data: {tenantId, ...}, etag}`.
        try:
            payload: Any = resp.json()
        except ValueError:
            if _strict_mode():
                raise HTTPException(
                    status_code=503,
                    detail="Field service returned invalid JSON | خدمة الحقول أعادت JSON غير صالح",
                )
            return
        if not isinstance(payload, dict):
            if _strict_mode():
                raise HTTPException(status_code=503, detail="Unexpected field payload shape")
            return
        data = payload.get("data", payload)
        if not isinstance(data, dict):
            if _strict_mode():
                raise HTTPException(status_code=503, detail="Unexpected field data shape")
            return
        remote_tenant = data.get("tenantId") or data.get("tenant_id")
        if remote_tenant and remote_tenant != tenant_id:
            # FMS's own ownership check should have returned 403 already,
            # but double-check defensively.
            raise HTTPException(
                status_code=403,
                detail="Field does not belong to this tenant | الحقل لا ينتمي إلى هذا المستأجر",
            )
    finally:
        if owns_client:
            await client.aclose()
