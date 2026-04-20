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
