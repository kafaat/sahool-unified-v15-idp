"""
SAHOOL Notification Service - Support Tickets Controller
وحدة التحكم في تذاكر الدعم - FastAPI Routes

Handles HTTP endpoints for the support ticketing system.

Features:
- Full CRUD on support tickets (list, create, retrieve, update)
- Optimistic locking via ``version`` column (PUT)
- Reply/append endpoint (POST /{id}/reply)
- Tenant isolation: tenant_id is sourced exclusively from the authenticated
  user's JWT (``tid`` claim, surfaced as ``User.tenant_id``).
- NATS events are published on tenant-scoped subjects using
  ``shared.events.subjects.get_tenant_subject`` so events from one tenant are
  never visible to another.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Authentication dependency (fail-secure fallback)
# ---------------------------------------------------------------------------
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:  # pragma: no cover - defensive fallback
    from pydantic import BaseModel as _BaseModel

    class User(_BaseModel):  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str | None = None

    async def get_current_user() -> User:  # type: ignore[no-redef]
        raise HTTPException(
            status_code=503,
            detail="Authentication backend unavailable",
        )


# ---------------------------------------------------------------------------
# Tenant-scoped NATS subject helper (fallback if shared module not available)
# ---------------------------------------------------------------------------
try:
    from shared.events.subjects import get_tenant_subject
except ImportError:  # pragma: no cover - defensive fallback

    def get_tenant_subject(tenant_id: str, domain: str, action: str) -> str:  # type: ignore[no-redef]
        if not tenant_id:
            raise ValueError("tenant_id is required for tenant-scoped subjects")
        return f"sahool.tenant.{tenant_id}.{domain}.{action}"


logger = logging.getLogger("sahool-notifications.support-tickets-controller")

# Router - Kong uses strip_path; we keep explicit prefix so both upstream
# (direct) and downstream (through Kong with strip_path=false) paths are valid
# within the service itself.
router = APIRouter(prefix="/api/v1/support", tags=["Support Tickets"])


# =============================================================================
# Enums
# =============================================================================


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# =============================================================================
# Request / Response Models
# =============================================================================


class SupportTicketCreate(BaseModel):
    """Payload for creating a support ticket."""

    subject: str = Field(..., min_length=1, max_length=500)
    subject_ar: str | None = Field(None, max_length=500)
    message: str = Field(..., min_length=1, max_length=10_000)
    message_ar: str | None = Field(None, max_length=10_000)
    priority: TicketPriority = TicketPriority.MEDIUM
    assigned_to: UUID | None = None


class SupportTicketUpdate(BaseModel):
    """Payload for updating a support ticket (optimistic locking)."""

    subject: str | None = Field(None, min_length=1, max_length=500)
    subject_ar: str | None = Field(None, max_length=500)
    message: str | None = Field(None, min_length=1, max_length=10_000)
    message_ar: str | None = Field(None, max_length=10_000)
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_to: UUID | None = None
    version: int = Field(..., ge=1, description="Current version for optimistic locking")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: int) -> int:
        if v < 1:
            raise ValueError("version must be >= 1")
        return v


class SupportTicketReplyCreate(BaseModel):
    """Payload for appending a reply to a ticket."""

    message: str = Field(..., min_length=1, max_length=10_000)


class SupportTicketReply(BaseModel):
    id: UUID
    ticket_id: UUID
    tenant_id: UUID
    user_id: UUID
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupportTicket(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    subject: str
    subject_ar: str | None = None
    message: str
    message_ar: str | None = None
    status: TicketStatus
    priority: TicketPriority
    assigned_to: UUID | None = None
    created_at: datetime
    updated_at: datetime
    version: int

    model_config = ConfigDict(from_attributes=True)


class SupportTicketListResponse(BaseModel):
    items: list[SupportTicket]
    total: int
    limit: int
    offset: int


# =============================================================================
# Storage backend
# =============================================================================
#
# We provide an in-memory store that is safe for tests and local development.
# In production, this module is expected to be wired to the shared Postgres
# instance via the SQL migration (``migrations/<ts>_support_tickets.sql``).
# The in-memory fallback mirrors the SQL schema 1:1 so behavior stays
# consistent across environments.

_TICKETS: dict[UUID, dict[str, Any]] = {}
_REPLIES: dict[UUID, list[dict[str, Any]]] = {}


def _require_tenant_id(user: User) -> UUID:
    """Extract and validate tenant_id from the authenticated user's JWT.

    Raises ``403`` if the user has no tenant binding (fail-secure). Tenant IDs
    MUST be valid UUIDs - this matches the shared contract for all SAHOOL
    services and the ``get_tenant_subject`` pattern.
    """

    tenant_id_raw = getattr(user, "tenant_id", None)
    if not tenant_id_raw:
        raise HTTPException(
            status_code=403,
            detail="Tenant context missing from authentication token",
        )
    try:
        return UUID(str(tenant_id_raw))
    except (ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(
            status_code=403,
            detail=f"Invalid tenant_id in authentication token: {exc}",
        ) from exc


def _require_user_id(user: User) -> UUID:
    """Extract user.id and coerce it to a UUID.

    Falls back to a deterministic UUID5 if the token carries a non-UUID id
    (e.g. a legacy string identifier in tests) to keep the SQL contract
    intact.
    """

    user_id_raw = getattr(user, "id", None)
    if not user_id_raw:
        raise HTTPException(status_code=401, detail="Authenticated user missing id")
    try:
        return UUID(str(user_id_raw))
    except (ValueError, TypeError, AttributeError):
        # Deterministic UUID5 mapping for non-UUID ids (e.g. tests).
        import uuid as _uuid

        return _uuid.uuid5(_uuid.NAMESPACE_OID, f"sahool-user:{user_id_raw}")


async def _publish_ticket_event(action: str, tenant_id: UUID, payload: dict[str, Any]) -> None:
    """Publish a tenant-scoped NATS event for ticket lifecycle changes.

    Uses the app-scoped NATS connection from ``main._nats_subscriber`` if
    available. Silently logs and returns on failure - NATS publishing must
    never break API requests.
    """

    subject = get_tenant_subject(str(tenant_id), "notification", f"support_ticket_{action}")

    try:
        # Late import to avoid circular imports between main and this module.
        from . import main as _main_module  # type: ignore[attr-defined]

        subscriber = getattr(_main_module, "_nats_subscriber", None)
        if subscriber is None:
            return
        nc = getattr(subscriber, "_nc", None)
        if nc is None:
            return
        await nc.publish(subject, json.dumps(payload, default=str).encode("utf-8"))
        logger.debug("support_ticket_event_published", subject=subject)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("support_ticket_event_publish_failed subject=%s err=%s", subject, exc)


# =============================================================================
# Routes
# =============================================================================


@router.get(
    "/tickets",
    response_model=SupportTicketListResponse,
    summary="List support tickets",
)
async def list_tickets(
    status_filter: TicketStatus | None = Query(None, alias="status"),
    priority: TicketPriority | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
) -> SupportTicketListResponse:
    """List support tickets for the authenticated user's tenant.

    Supports filtering by ``status`` and ``priority``, with pagination via
    ``limit`` and ``offset``. Results are always scoped to ``tenant_id`` from
    the JWT - never from headers or query params.
    """

    tenant_id = _require_tenant_id(user)

    items = [t for t in _TICKETS.values() if t["tenant_id"] == tenant_id]
    if status_filter is not None:
        items = [t for t in items if t["status"] == status_filter]
    if priority is not None:
        items = [t for t in items if t["priority"] == priority]

    items.sort(key=lambda t: t["created_at"], reverse=True)
    total = len(items)
    paged = items[offset : offset + limit]

    return SupportTicketListResponse(
        items=[SupportTicket(**t) for t in paged],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/tickets",
    response_model=SupportTicket,
    status_code=status.HTTP_201_CREATED,
    summary="Create a support ticket",
)
async def create_ticket(
    payload: SupportTicketCreate,
    user: User = Depends(get_current_user),
) -> SupportTicket:
    """Create a new support ticket for the caller's tenant."""

    tenant_id = _require_tenant_id(user)
    user_id = _require_user_id(user)

    now = datetime.now(UTC)
    ticket_id = uuid4()
    record: dict[str, Any] = {
        "id": ticket_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "subject": payload.subject,
        "subject_ar": payload.subject_ar,
        "message": payload.message,
        "message_ar": payload.message_ar,
        "status": TicketStatus.OPEN,
        "priority": payload.priority,
        "assigned_to": payload.assigned_to,
        "created_at": now,
        "updated_at": now,
        "version": 1,
    }
    _TICKETS[ticket_id] = record
    _REPLIES[ticket_id] = []

    await _publish_ticket_event(
        action="created",
        tenant_id=tenant_id,
        payload={
            "ticket_id": str(ticket_id),
            "tenant_id": str(tenant_id),
            "user_id": str(user_id),
            "priority": str(payload.priority),
            "status": str(TicketStatus.OPEN),
        },
    )

    return SupportTicket(**record)


@router.get(
    "/tickets/{ticket_id}",
    response_model=SupportTicket,
    summary="Get a support ticket by id",
)
async def get_ticket(
    ticket_id: UUID,
    user: User = Depends(get_current_user),
) -> SupportTicket:
    tenant_id = _require_tenant_id(user)

    record = _TICKETS.get(ticket_id)
    if record is None or record["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return SupportTicket(**record)


@router.put(
    "/tickets/{ticket_id}",
    response_model=SupportTicket,
    summary="Update a support ticket (optimistic locking)",
)
async def update_ticket(
    ticket_id: UUID,
    payload: SupportTicketUpdate,
    user: User = Depends(get_current_user),
) -> SupportTicket:
    """Update a ticket using optimistic locking on the ``version`` column.

    The client MUST supply the ``version`` it last saw. If the stored
    version no longer matches, a ``409 Conflict`` is returned so the client
    can refetch and retry.
    """

    tenant_id = _require_tenant_id(user)

    record = _TICKETS.get(ticket_id)
    if record is None or record["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if record["version"] != payload.version:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Version conflict: expected {record['version']}, "
                f"got {payload.version}"
            ),
        )

    updates = payload.model_dump(exclude_unset=True, exclude={"version"})
    for field, value in updates.items():
        record[field] = value
    record["version"] += 1
    record["updated_at"] = datetime.now(UTC)

    await _publish_ticket_event(
        action="updated",
        tenant_id=tenant_id,
        payload={
            "ticket_id": str(ticket_id),
            "tenant_id": str(tenant_id),
            "status": str(record["status"]),
            "priority": str(record["priority"]),
            "version": record["version"],
        },
    )

    return SupportTicket(**record)


@router.post(
    "/tickets/{ticket_id}/reply",
    response_model=SupportTicketReply,
    status_code=status.HTTP_201_CREATED,
    summary="Append a reply to a support ticket",
)
async def reply_to_ticket(
    ticket_id: UUID,
    payload: SupportTicketReplyCreate,
    user: User = Depends(get_current_user),
) -> SupportTicketReply:
    """Append a reply to a support ticket.

    Bumps the parent ticket's ``updated_at`` and ``version`` so concurrent
    editors observe the change via optimistic locking on the next update.
    """

    tenant_id = _require_tenant_id(user)
    user_id = _require_user_id(user)

    record = _TICKETS.get(ticket_id)
    if record is None or record["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Ticket not found")

    now = datetime.now(UTC)
    reply_record: dict[str, Any] = {
        "id": uuid4(),
        "ticket_id": ticket_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "message": payload.message,
        "created_at": now,
    }
    _REPLIES.setdefault(ticket_id, []).append(reply_record)

    # Touch parent ticket: bump version and updated_at
    record["updated_at"] = now
    record["version"] += 1

    await _publish_ticket_event(
        action="replied",
        tenant_id=tenant_id,
        payload={
            "ticket_id": str(ticket_id),
            "tenant_id": str(tenant_id),
            "user_id": str(user_id),
            "reply_id": str(reply_record["id"]),
        },
    )

    return SupportTicketReply(**reply_record)


# =============================================================================
# Test helpers (not exported via router)
# =============================================================================


def _reset_store() -> None:
    """Reset the in-memory store - used by tests."""

    _TICKETS.clear()
    _REPLIES.clear()
