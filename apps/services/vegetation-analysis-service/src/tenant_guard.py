"""Defense-in-depth tenant presence guard for the vegetation-analysis-service.

Every authenticated endpoint must verify the JWT carries a valid
``tenant_id`` — even though Kong enforces it at the gateway, a direct
pod-network call (e.g. an in-cluster misconfiguration or a sidecar
vulnerability) would bypass Kong. This module provides a single,
importable guard so every sub-module (``parcel_endpoints``,
``boundary_endpoints``, ``gdd_endpoints``, ``spray_endpoints``,
``weather_endpoints``, ``vra_endpoints``) applies the exact same
check as ``main.py``.

Kept tiny + import-free (besides ``fastapi``) so it can be imported
from any sub-module without creating a circular dependency with
``main.py``.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException


def require_tenant_id(user: Any) -> str:
    """Extract ``tenant_id`` from the authenticated user, or raise 403.

    Matches the behaviour of ``main._require_tenant_id`` so a user with
    a missing / empty ``tenant_id`` receives the same bilingual 403
    across every endpoint in the service.

    :param user: The object returned by ``shared.auth.dependencies.get_current_user``.
        Accepts the full ``User`` dataclass, the lightweight fallback
        dict (``{"token": "..."}``), or ``None``.
    :returns: The non-empty ``tenant_id`` (always a ``str``).
    :raises HTTPException 403: When the user has no tenant context, or
        the ``tenant_id`` is not a non-empty string (guards against
        truthy-but-wrong-type values like ``MagicMock()``).
    """
    tenant_id: Any = ""
    if user is not None:
        # Support both the User dataclass and the lightweight dict fallback
        tenant_id = getattr(user, "tenant_id", "")
        if not tenant_id and isinstance(user, dict):
            tenant_id = user.get("tenant_id", "")
    # Hardened type check: require non-empty ``str`` — a bare MagicMock()
    # or a stray int would otherwise slip past the old truthy check.
    if isinstance(tenant_id, str):
        tenant_id = tenant_id.strip()
        if tenant_id:
            return tenant_id
    raise HTTPException(
        status_code=403,
        detail="Tenant context required | سياق المستأجر مطلوب",
    )


def validate_field_id(field_id: str) -> None:
    """Reject malformed ``field_id`` path parameters before they reach
    downstream code. Mirrors ``main._validate_field_id`` so sub-file
    handlers can validate without a circular import.

    :raises HTTPException 400: When ``field_id`` is empty or longer
        than 100 characters.
    """
    if not field_id or len(field_id) > 100:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid field_id", "error_ar": "معرف الحقل غير صالح"},
        )


async def verify_field_owned_by_tenant(
    user: Any,
    field_id: str,
    http_request: Any = None,
) -> str:
    """Sub-file equivalent of ``main._verify_field_owned_by_tenant``.

    Composes ``require_tenant_id`` + ``validate_field_id`` +
    ``field_ownership.verify_field_ownership`` so sub-modules
    (boundary_endpoints, gdd_endpoints, vra_endpoints) can enforce
    cross-service ownership without creating a circular import with
    ``main.py``.

    Delegates ownership resolution to field-management-service (the
    canonical owner of the ``fields`` table) using the inbound Bearer
    JWT extracted from ``http_request``.

    :raises HTTPException 400: ``field_id`` malformed.
    :raises HTTPException 403: tenant missing, or field belongs to
        another tenant.
    :raises HTTPException 404: field does not exist.
    :raises HTTPException 503: field-management-service unreachable
        (strict mode only).
    """
    tenant_id = require_tenant_id(user)
    validate_field_id(field_id)

    # Extract the inbound Bearer token (case-insensitive header lookup).
    # Only Bearer scheme — Basic/etc. stripped to avoid leaking unrelated
    # credentials downstream.
    bearer_token: str | None = None
    if http_request is not None:
        auth_header = http_request.headers.get("authorization") or http_request.headers.get("Authorization") or ""
        if auth_header.lower().startswith("bearer "):
            bearer_token = auth_header[7:].strip() or None

    # Lazy import so a missing dependency inside field_ownership (e.g.
    # httpx) surfaces to the caller instead of being masked as "module
    # missing". Matches the pattern in main._verify_field_owned_by_tenant.
    try:
        from .field_ownership import verify_field_ownership
    except ModuleNotFoundError as exc:
        if exc.name not in {"field_ownership", __package__ + ".field_ownership" if __package__ else "field_ownership"}:
            raise
        from field_ownership import verify_field_ownership  # standalone test path
    except ImportError as exc:
        if "relative import" not in str(exc):
            raise
        from field_ownership import verify_field_ownership  # standalone test path

    await verify_field_ownership(tenant_id, field_id, bearer_token=bearer_token)
    return tenant_id
