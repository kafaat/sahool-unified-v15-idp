"""
Geofence → FieldOperation auto-draft bridge.

When a piece of tracked equipment enters a field geofence, we want to
pre-create a draft ``field_operation`` record so the farmer / operator
only has to *confirm* the activity afterwards instead of typing it
from scratch. This matches how modern fleet software (Farmonaut,
Trimble, John Deere Ops Center) automatically logs activity based on
telemetry rather than relying on end-of-day paperwork.

Flow::

    equipment-service  ── geofence.entry ──▶  this bridge
                                              │
                                              ├─ classify operation from equipment type
                                              ├─ POST /api/v1/fields/{id}/operations
                                              │   with status="draft", source="geofence_auto"
                                              └─ publish sahool.field_operation.auto_drafted

The draft is always marked as *pending review* — SAHOOL does not
auto-approve agronomic activity on behalf of the farmer, we only
surface the evidence. An operator must explicitly confirm via the
existing ``/field-operations/:id/approve`` endpoint before it counts
for cost rollup, ERP sync, or carbon reporting.

Graceful degradation: a failure to reach field-management-service
does NOT fail the caller's geofence-event request. We log the draft
intent and return ``status="pending_retry"`` — a background retry
worker (or simply the next geofence event) will try again.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import httpx
import structlog

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Equipment → Operation-type classifier
# ---------------------------------------------------------------------------


# Canonical field-management-service operation types (must match
# OPERATION_TYPES in apps/services/field-management-service/src/
# field-operations/dto/field-operation.dto.ts).
EQUIPMENT_TO_OPERATION: dict[str, str] = {
    "tractor": "plowing",
    "harvester": "harvesting",
    "sprayer": "spraying",
    "drone": "scouting",
    "pump": "irrigation",
    "pivot": "irrigation",
    "vehicle": "scouting",
    "sensor": "scouting",
    "other": "other",
}


def classify_operation(equipment_type: str) -> str:
    """
    Map equipment_type → draft operation_type.

    Unknown types fall back to ``"other"`` so the operator can pick
    a better label when reviewing.
    """
    return EQUIPMENT_TO_OPERATION.get(equipment_type.lower(), "other")


# ---------------------------------------------------------------------------
# Event + result DTOs
# ---------------------------------------------------------------------------


@dataclass
class GeofenceEvent:
    """Single geofence entry/exit event consumed by the bridge."""

    equipment_id: str
    tenant_id: str
    geofence_id: str
    geofence_type: str  # field | farm_boundary | allowed | restricted | ...
    alert_type: str  # entry | exit | speeding | idle | ...
    lat: float
    lng: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Optional — if the geofence is directly tied to a field record
    field_id: str | None = None
    crop_season_id: str | None = None
    equipment_type: str = "other"
    equipment_name: str = ""
    operator_id: str | None = None


@dataclass
class AutoOperationResult:
    """Outcome of a single auto-draft attempt."""

    handled: bool
    reason: str  # "drafted" | "skipped" | "pending_retry" | "failed"
    operation_id: str | None = None
    operation_type: str | None = None
    field_id: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "handled": self.handled,
            "reason": self.reason,
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "field_id": self.field_id,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Bridge
# ---------------------------------------------------------------------------


class GeofenceAutoOperationBridge:
    """
    Converts a GeofenceEvent into a draft FieldOperation via
    field-management-service. Stateless — re-use per process.
    """

    DEFAULT_TIMEOUT_SEC = 4.0

    # Only these geofence types should auto-draft operations.
    # Entry into a restricted zone is a SECURITY event, not an
    # agronomic one, and is handled by the alert-service instead.
    FIELD_TYPES = {"field", "farm_boundary"}

    # Only these alert types count as "started an activity".
    ACTIONABLE_ALERTS = {"entry"}

    def __init__(
        self,
        field_management_url: str,
        nats_client: Any | None = None,
        timeout: float | None = None,
    ):
        self.field_management_url = field_management_url.rstrip("/")
        self.nats_client = nats_client
        self.timeout = timeout or self.DEFAULT_TIMEOUT_SEC

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def handle(
        self,
        event: GeofenceEvent,
        auth_header: str | None = None,
    ) -> AutoOperationResult:
        if event.alert_type.lower() not in self.ACTIONABLE_ALERTS:
            return AutoOperationResult(
                handled=False,
                reason="skipped",
                error=f"alert_type={event.alert_type} is not actionable",
            )
        if event.geofence_type.lower() not in self.FIELD_TYPES:
            return AutoOperationResult(
                handled=False,
                reason="skipped",
                error=f"geofence_type={event.geofence_type} is not a field zone",
            )
        if not event.field_id:
            # The geofence MUST be tied to a field for us to draft
            # an operation against it. Without a field_id we log and
            # skip — a human will need to resolve the mapping.
            logger.info(
                "geofence_autoop.skipped_no_field",
                equipment_id=event.equipment_id,
                geofence_id=event.geofence_id,
            )
            return AutoOperationResult(
                handled=False,
                reason="skipped",
                error="geofence has no field_id mapping",
            )

        operation_type = classify_operation(event.equipment_type)

        payload = self._build_payload(event, operation_type)
        result = await self._post_draft(payload, event, auth_header)

        if result.handled:
            await self._publish_drafted_event(event, result)
        return result

    # ------------------------------------------------------------------
    # HTTP call to field-management-service
    # ------------------------------------------------------------------

    async def _post_draft(
        self,
        payload: dict[str, Any],
        event: GeofenceEvent,
        auth_header: str | None,
    ) -> AutoOperationResult:
        url = f"{self.field_management_url}/api/v1/fields/{event.field_id}/operations"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Tenant-Id": event.tenant_id,
            # Idempotency key so the same geofence entry can't create
            # two draft operations if the caller retries.
            "Idempotency-Key": (
                f"geofence-{event.equipment_id}-{event.geofence_id}-{int(event.timestamp.timestamp())}"
            ),
            "X-Source": "geofence_auto",
        }
        if auth_header:
            headers["Authorization"] = auth_header

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                body = resp.json() if resp.content else {}
                data = body.get("data") if isinstance(body, dict) else body
                op_id = data.get("id") if isinstance(data, dict) else None
                return AutoOperationResult(
                    handled=True,
                    reason="drafted",
                    operation_id=op_id,
                    operation_type=payload["operationType"],
                    field_id=event.field_id,
                )
            return AutoOperationResult(
                handled=False,
                reason="pending_retry",
                operation_type=payload["operationType"],
                field_id=event.field_id,
                error=f"HTTP {resp.status_code}: {resp.text[:200]}",
            )
        except httpx.TimeoutException:
            logger.warning("geofence_autoop.timeout", url=url)
            return AutoOperationResult(
                handled=False,
                reason="pending_retry",
                operation_type=payload["operationType"],
                field_id=event.field_id,
                error="timeout",
            )
        except httpx.RequestError as e:
            logger.warning("geofence_autoop.network", url=url, error=str(e))
            return AutoOperationResult(
                handled=False,
                reason="pending_retry",
                operation_type=payload["operationType"],
                field_id=event.field_id,
                error=f"network:{type(e).__name__}",
            )
        except Exception as e:  # pragma: no cover - defensive
            logger.error("geofence_autoop.unexpected", url=url, error=str(e))
            return AutoOperationResult(
                handled=False,
                reason="failed",
                operation_type=payload["operationType"],
                field_id=event.field_id,
                error=f"unexpected:{type(e).__name__}",
            )

    def _build_payload(self, event: GeofenceEvent, operation_type: str) -> dict[str, Any]:
        """
        Build the CreateFieldOperationDto body.

        Schema mirrors field-management-service's
        ``CreateFieldOperationDto`` exactly — do NOT add unknown
        fields or the whitelist=true ValidationPipe will reject them.
        """
        notes = (
            f"Auto-drafted from geofence entry: equipment={event.equipment_name or event.equipment_id}, "
            f"geofence={event.geofence_id}, position=({event.lat:.5f},{event.lng:.5f}). "
            f"Pending operator review."
        )
        payload: dict[str, Any] = {
            "operationType": operation_type,
            "performedAt": event.timestamp.isoformat(),
            "equipmentId": event.equipment_id,
            "notes": notes,
        }
        if event.equipment_name:
            payload["equipmentName"] = event.equipment_name[:255]
        if event.crop_season_id:
            payload["cropSeasonId"] = event.crop_season_id
        return payload

    # ------------------------------------------------------------------
    # NATS event emission
    # ------------------------------------------------------------------

    async def _publish_drafted_event(self, event: GeofenceEvent, result: AutoOperationResult) -> None:
        if self.nats_client is None:
            return
        subject = f"sahool.tenant.{event.tenant_id}.field_operation.auto_drafted"
        body = {
            "equipment_id": event.equipment_id,
            "tenant_id": event.tenant_id,
            "geofence_id": event.geofence_id,
            "field_id": event.field_id,
            "operation_id": result.operation_id,
            "operation_type": result.operation_type,
            "triggered_at": event.timestamp.isoformat(),
            "source": "geofence_auto",
        }
        try:
            maybe = self.nats_client.publish(subject, json.dumps(body).encode())
            if hasattr(maybe, "__await__"):
                await maybe
        except Exception as e:  # pragma: no cover - best-effort
            logger.warning("geofence_autoop.publish_failed", error=str(e), subject=subject)
