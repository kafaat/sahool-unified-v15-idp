"""
SAHOOL Equipment Service - API Response Models
نماذج استجابات الواجهة البرمجية لخدمة المعدات

Provides Pydantic response models with camelCase aliases for the frontend
while preserving snake_case keys for backward compatibility. Also provides
helper serialization so we can emit BOTH legacy fields (snake_case, with the
backend-canonical status enum values such as ``operational``) and the new
frontend-facing shape (camelCase, with the unified status enum ``active``,
``maintenance``, ``repair``, ``idle``, ``retired``) from a single payload.

Design decision (see Wave 2 audit):
    Rather than breaking existing clients / tests by replacing the legacy
    snake_case output, we emit BOTH shapes in the same response object. This
    is additive, non-breaking, and allows the frontend to migrate at its own
    pace. The helper :func:`serialize_equipment` is the single source of
    truth for this shape.

    Status mapping for the frontend (``statusAlias`` + ``status`` top-level
    remains the backend canonical value)::

        operational -> active
        maintenance -> maintenance
        repair      -> repair
        inactive    -> idle
        archived    -> retired
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Status mapping (backend canonical -> frontend canonical)
# ---------------------------------------------------------------------------

#: Map backend canonical status values to the frontend canonical set.
STATUS_OUT_MAP: dict[str, str] = {
    "operational": "active",
    "maintenance": "maintenance",
    "repair": "repair",
    "inactive": "idle",
    "archived": "retired",
}

#: Map frontend canonical status values back to the backend canonical set.
#: Used to accept either form on input without breaking the DB contract.
STATUS_IN_MAP: dict[str, str] = {
    "active": "operational",
    "operational": "operational",
    "maintenance": "maintenance",
    "repair": "repair",
    "idle": "inactive",
    "inactive": "inactive",
    "retired": "archived",
    "archived": "archived",
}


def map_status_out(status: str | None) -> str | None:
    """Translate a backend status value to the frontend-facing alias.

    Unknown values are returned unchanged so we do not silently drop data.
    """
    if status is None:
        return None
    return STATUS_OUT_MAP.get(status, status)


def map_status_in(status: str | None) -> str | None:
    """Translate an incoming status value (either dialect) to the backend value."""
    if status is None:
        return None
    return STATUS_IN_MAP.get(status, status)


# ---------------------------------------------------------------------------
# Pydantic response models (camelCase via Field aliases)
# ---------------------------------------------------------------------------


class LocationResponse(BaseModel):
    """Nested location payload expected by the frontend.

    Built from ``current_lat``, ``current_lon`` and ``current_field_id`` /
    ``field_id`` on the DB record.
    """

    model_config = ConfigDict(populate_by_name=True)

    latitude: float | None = Field(default=None, alias="latitude")
    longitude: float | None = Field(default=None, alias="longitude")
    field_id: str | None = Field(default=None, alias="fieldId")
    name: str | None = Field(default=None, alias="name")


class EquipmentResponse(BaseModel):
    """Frontend-facing equipment response.

    Exposes camelCase aliases so the same object can be serialized with
    ``by_alias=True`` for the web/mobile clients.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="id")
    tenant_id: str = Field(alias="tenantId")
    type: str = Field(alias="type")
    name: str = Field(alias="name")
    name_ar: str | None = Field(default=None, alias="nameAr")
    status: str = Field(alias="status")
    brand: str | None = Field(default=None, alias="brand")
    model: str | None = Field(default=None, alias="model")
    serial_number: str | None = Field(default=None, alias="serialNumber")
    year: int | None = Field(default=None, alias="year")
    purchase_date: datetime | None = Field(default=None, alias="purchaseDate")
    purchase_price: float | None = Field(default=None, alias="purchasePrice")
    location: LocationResponse = Field(alias="location")
    horsepower: int | None = Field(default=None, alias="horsepower")
    fuel_capacity_liters: float | None = Field(default=None, alias="fuelCapacityLiters")
    current_fuel_percent: float | None = Field(default=None, alias="currentFuelPercent")
    current_hours: float | None = Field(default=None, alias="currentHours")
    last_maintenance_date: datetime | None = Field(default=None, alias="lastMaintenanceDate")
    next_maintenance_date: datetime | None = Field(default=None, alias="nextMaintenanceDate")
    next_maintenance_hours: float | None = Field(default=None, alias="nextMaintenanceHours")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    qr_code: str | None = Field(default=None, alias="qrCode")
    metadata: dict | None = Field(default=None, alias="metadata")


class PaginationResponse(BaseModel):
    """Unified pagination envelope shared with the frontend."""

    total: int
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Serialization helper (single source of truth)
# ---------------------------------------------------------------------------


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def serialize_equipment(eq: Any) -> dict[str, Any]:
    """Serialize a DB equipment row to a dict with BOTH legacy and camelCase keys.

    We deliberately emit the union of snake_case (legacy) and camelCase (new)
    field names plus a nested ``location`` object so that:

    * Existing clients and tests that rely on ``equipment_id``,
      ``equipment_type``, ``status == "operational"``, etc. continue to work.
    * New frontend clients can consume ``id``, ``type``, ``status == "active"``,
      ``nameAr``, ``location.latitude`` and so on via the response.
    """

    lat = _to_float(getattr(eq, "current_lat", None))
    lon = _to_float(getattr(eq, "current_lon", None))
    field_id = getattr(eq, "field_id", None)
    # ``current_field_id`` is an alternative name some models use; prefer it
    # if present on the row.
    current_field_id = getattr(eq, "current_field_id", None)
    location_field_id = current_field_id or field_id
    location_name = getattr(eq, "location_name", None)

    location = {
        "latitude": lat,
        "longitude": lon,
        "field_id": location_field_id,
        "fieldId": location_field_id,
        "name": location_name,
    }

    backend_status = getattr(eq, "status", None)
    frontend_status = map_status_out(backend_status)

    extra_metadata = getattr(eq, "extra_metadata", None)
    if extra_metadata is None:
        extra_metadata = getattr(eq, "metadata", None)

    equipment_id = getattr(eq, "equipment_id", None)
    equipment_type = getattr(eq, "equipment_type", None)
    name = getattr(eq, "name", None)
    name_ar = getattr(eq, "name_ar", None)

    purchase_price = _to_float(getattr(eq, "purchase_price", None))
    fuel_capacity = _to_float(getattr(eq, "fuel_capacity_liters", None))
    fuel_percent = _to_float(getattr(eq, "current_fuel_percent", None))
    hours = _to_float(getattr(eq, "current_hours", None))
    next_maint_hours = _to_float(getattr(eq, "next_maintenance_hours", None))

    last_maint_at = getattr(eq, "last_maintenance_at", None)
    next_maint_at = getattr(eq, "next_maintenance_at", None)

    payload: dict[str, Any] = {
        # -- Legacy snake_case keys (backwards compatibility) ---------------
        "equipment_id": equipment_id,
        "tenant_id": getattr(eq, "tenant_id", None),
        "name": name,
        "name_ar": name_ar,
        "equipment_type": equipment_type,
        "status": backend_status,
        "brand": getattr(eq, "brand", None),
        "model": getattr(eq, "model", None),
        "serial_number": getattr(eq, "serial_number", None),
        "year": getattr(eq, "year", None),
        "purchase_date": getattr(eq, "purchase_date", None),
        "purchase_price": purchase_price,
        "field_id": field_id,
        "location_name": location_name,
        "horsepower": getattr(eq, "horsepower", None),
        "fuel_capacity_liters": fuel_capacity,
        "current_fuel_percent": fuel_percent,
        "current_hours": hours,
        "current_lat": lat,
        "current_lon": lon,
        "last_maintenance_at": last_maint_at,
        "next_maintenance_at": next_maint_at,
        "next_maintenance_hours": next_maint_hours,
        "created_at": getattr(eq, "created_at", None),
        "updated_at": getattr(eq, "updated_at", None),
        "metadata": extra_metadata,
        "qr_code": getattr(eq, "qr_code", None),
        # -- Frontend-facing aliases ---------------------------------------
        "id": equipment_id,
        "tenantId": getattr(eq, "tenant_id", None),
        "type": equipment_type,
        "nameAr": name_ar,
        "statusAlias": frontend_status,
        "statusBackend": backend_status,
        "brandName": getattr(eq, "brand", None),
        "modelName": getattr(eq, "model", None),
        "serialNumber": getattr(eq, "serial_number", None),
        "purchaseDate": getattr(eq, "purchase_date", None),
        "purchasePrice": purchase_price,
        "location": location,
        "fuelCapacityLiters": fuel_capacity,
        "currentFuelPercent": fuel_percent,
        "currentHours": hours,
        "lastMaintenanceDate": last_maint_at,
        "nextMaintenanceDate": next_maint_at,
        "nextMaintenanceHours": next_maint_hours,
        "createdAt": getattr(eq, "created_at", None),
        "updatedAt": getattr(eq, "updated_at", None),
        "qrCode": getattr(eq, "qr_code", None),
    }

    return payload
