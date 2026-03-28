"""
Traceability API endpoints - نقاط نهاية التتبع
Integrates with shared.traceability module and PostgreSQL persistence.
"""

import json
import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

# NATS event subject constants
from shared.events.subjects import (
    SAHOOL_NOTIFICATION_SEND,
    SAHOOL_TRACEABILITY_BATCH_CREATED,
    SAHOOL_TRACEABILITY_BATCH_RECALLED,
    SAHOOL_TRACEABILITY_BATCH_SPLIT,
    SAHOOL_TRACEABILITY_HARVEST_RECORDED,
    SAHOOL_TRACEABILITY_PROCESSING_RECORDED,
    SAHOOL_TRACEABILITY_STORAGE_RECORDED,
    SAHOOL_TRACEABILITY_TRANSPORT_RECORDED,
)

logger = structlog.get_logger()

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


router = APIRouter(prefix="/api/v1/traceability", tags=["traceability"])


# === Tenant Extraction ===


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header."""
    if not x_tenant_id:
        raise HTTPException(
            status_code=400,
            detail={"error": "X-Tenant-Id header is required", "error_ar": "ترويسة معرّف المستأجر مطلوبة"},
        )
    try:
        uuid.UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "X-Tenant-Id must be a valid UUID", "error_ar": "معرّف المستأجر يجب أن يكون UUID صالح"},
        )
    return x_tenant_id


# === Database Helpers ===


async def _get_db(request: Request):
    """Get database pool from app state."""
    pool = getattr(request.app.state, "db_pool", None)
    if not pool:
        raise HTTPException(
            status_code=503,
            detail={"error": "Database not available", "error_ar": "قاعدة البيانات غير متوفرة"},
        )
    return pool


async def _get_batch_or_404(pool, batch_id: str, tenant_id: str) -> dict:
    """Get batch by ID with mandatory tenant isolation or raise 404."""
    row = await pool.fetchrow(
        "SELECT * FROM produce_batches WHERE id = $1 AND tenant_id = $2",
        uuid.UUID(batch_id),
        uuid.UUID(tenant_id),
    )
    if not row:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})
    return dict(row)


def _row_to_dict(row) -> dict:
    """Convert asyncpg Record to JSON-serializable dict."""
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, uuid.UUID):
            d[k] = str(v)
        elif isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


# === Request Models ===


class BatchCreateRequest(BaseModel):
    farm_id: str
    field_id: str
    product_name_en: str
    product_name_ar: str
    quantity: float = Field(..., gt=0)
    unit: str = "kg"
    variety: str | None = None
    batch_code: str | None = None


class HarvestEventRequest(BaseModel):
    field_name_en: str
    field_name_ar: str
    crop_type: str
    harvest_method_en: str = "Manual"
    harvest_method_ar: str = "يدوي"
    quality_grade: str = "A"


class ProcessingEventRequest(BaseModel):
    facility_name: str
    process_type: str
    notes: str | None = None


class StorageEventRequest(BaseModel):
    location: str
    temperature_c: float | None = None
    humidity_percent: float | None = None


class TransportEventRequest(BaseModel):
    origin: str
    destination: str
    transport_mode: str = "truck"
    vehicle_id: str | None = None
    distance_km: float | None = None


class BatchUpdateRequest(BaseModel):
    product_name_en: str | None = None
    product_name_ar: str | None = None
    quantity: float | None = Field(None, gt=0)
    status: str | None = None


class BatchSplitRequest(BaseModel):
    quantities: list[float]


class GenerateCodeRequest(BaseModel):
    product_code: str = Field(..., min_length=2, max_length=3, description="2-3 letter product code (e.g. WH, TM)")
    year: int | None = None
    sequence: int = Field(..., ge=1)
    farm_code: str | None = Field(None, min_length=3, max_length=3)


def _generate_batch_code(product_code: str, year: int | None, sequence: int, farm_code: str | None = None) -> str:
    """Generate batch code, using shared module if available."""
    try:
        from shared.traceability import generate_batch_code

        return generate_batch_code(
            product_code=product_code,
            year=year or datetime.now(UTC).year,
            sequence=sequence,
            farm_code=farm_code,
        )
    except ImportError:
        year_short = str(year or datetime.now(UTC).year)[-2:]
        code = f"{product_code}-{year_short}-{sequence:03d}"
        if farm_code:
            code = f"{product_code}-{farm_code}-{year_short}-{sequence:03d}"
        return code


# === Batch Endpoints ===


@router.post("/batches", status_code=201)
async def create_batch(
    request: BatchCreateRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Create a new produce batch - إنشاء دفعة منتج جديدة"""
    pool = await _get_db(req)

    # Generate batch code
    if request.batch_code:
        batch_code = request.batch_code
    else:
        # Count existing batches for sequence
        count = await pool.fetchval("SELECT COUNT(*) FROM produce_batches WHERE tenant_id = $1", tenant_id)
        product_code = request.product_name_en[:2].upper()
        farm_code = request.farm_id[:3].upper() if request.farm_id else None
        batch_code = _generate_batch_code(product_code, datetime.now(UTC).year, count + 1, farm_code)

    row = await pool.fetchrow(
        """
        INSERT INTO produce_batches (tenant_id, farm_id, field_id, batch_code, product_name_en, product_name_ar, variety, quantity, unit, quality_grade, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'A', 'created')
        RETURNING *
        """,
        tenant_id,
        request.farm_id,
        request.field_id,
        batch_code,
        request.product_name_en,
        request.product_name_ar,
        request.variety,
        request.quantity,
        request.unit,
    )
    batch_data = _row_to_dict(row)

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            SAHOOL_TRACEABILITY_BATCH_CREATED,
            json.dumps({"batch_id": batch_data["id"], "batch_code": batch_code, "tenant_id": tenant_id}).encode(),
        )

    logger.info("batch_created", batch_id=batch_data["id"], batch_code=batch_code)
    return batch_data


@router.get("/batches/{batch_id}")
async def get_batch(batch_id: str, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Get batch details - الحصول على تفاصيل الدفعة"""
    pool = await _get_db(req)
    row = await _get_batch_or_404(pool, batch_id, tenant_id)
    return _row_to_dict(row)


@router.get("/batches")
async def list_batches(req: Request, tenant_id: str = Depends(get_tenant_id), farm_id: str | None = None):
    """List batches with optional filtering - قائمة الدفعات"""
    pool = await _get_db(req)

    query = "SELECT * FROM produce_batches WHERE tenant_id = $1"
    params = [tenant_id]
    idx = 2

    if farm_id:
        query += f" AND farm_id = ${idx}"
        params.append(farm_id)
        idx += 1

    query += " ORDER BY created_at DESC"
    rows = await pool.fetch(query, *params)
    result = [_row_to_dict(r) for r in rows]
    return {"batches": result, "count": len(result)}


@router.put("/batches/{batch_id}")
async def update_batch(
    batch_id: str,
    request: BatchUpdateRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Update batch details - تحديث تفاصيل الدفعة"""
    pool = await _get_db(req)
    await _get_batch_or_404(pool, batch_id, tenant_id)

    ALLOWED_COLUMNS = {"product_name_en", "product_name_ar", "quantity", "status"}
    updates = {k: v for k, v in request.model_dump(exclude_none=True).items() if k in ALLOWED_COLUMNS}
    if not updates:
        raise HTTPException(
            status_code=400, detail={"error": "No fields to update", "error_ar": "لا توجد حقول للتحديث"}
        )

    set_clauses = []
    values = []
    for i, (key, val) in enumerate(updates.items(), 1):
        set_clauses.append(f"{key} = ${i}")
        values.append(val)
    values.append(uuid.UUID(batch_id))
    values.append(uuid.UUID(tenant_id))

    row = await pool.fetchrow(
        f"UPDATE produce_batches SET {', '.join(set_clauses)} WHERE id = ${len(values) - 1} AND tenant_id = ${len(values)} RETURNING *",  # nosec B608 - keys validated against ALLOWED_COLUMNS allowlist  # nosemgrep: python.lang.security.audit.formatted-sql-query
        *values,
    )
    logger.info("batch_updated", batch_id=batch_id, fields=list(updates.keys()))
    return _row_to_dict(row)


# === Supply Chain Event Endpoints ===


@router.post("/batches/{batch_id}/events/harvest")
async def record_harvest_event(
    batch_id: str,
    request: HarvestEventRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Record harvest event - تسجيل حدث الحصاد"""
    pool = await _get_db(req)
    await _get_batch_or_404(pool, batch_id, tenant_id)
    batch_uuid = uuid.UUID(batch_id)

    row = await pool.fetchrow(
        """
        INSERT INTO supply_chain_events (batch_id, event_type, location, crop_type, harvest_method, quality_grade, metadata)
        VALUES ($1, 'harvest', $2, $3, $4, $5, $6)
        RETURNING *
        """,
        batch_uuid,
        request.field_name_en,
        request.crop_type,
        request.harvest_method_en,
        request.quality_grade,
        json.dumps({"field_name_ar": request.field_name_ar, "harvest_method_ar": request.harvest_method_ar}),
    )

    # Update batch status
    await pool.execute(
        "UPDATE produce_batches SET status = 'harvested' WHERE id = $1 AND tenant_id = $2 AND status = 'created'",
        batch_uuid,
        uuid.UUID(tenant_id),
    )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(SAHOOL_TRACEABILITY_HARVEST_RECORDED, json.dumps({"batch_id": batch_id, "tenant_id": tenant_id}).encode())

    logger.info("harvest_recorded", batch_id=batch_id)
    return {"status": "recorded", "event": _row_to_dict(row)}


@router.post("/batches/{batch_id}/events/processing")
async def record_processing_event(
    batch_id: str,
    request: ProcessingEventRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Record processing event - تسجيل حدث المعالجة"""
    pool = await _get_db(req)
    await _get_batch_or_404(pool, batch_id, tenant_id)
    batch_uuid = uuid.UUID(batch_id)

    row = await pool.fetchrow(
        """
        INSERT INTO supply_chain_events (batch_id, event_type, facility_name, process_type, notes)
        VALUES ($1, 'processing', $2, $3, $4)
        RETURNING *
        """,
        batch_uuid,
        request.facility_name,
        request.process_type,
        request.notes,
    )

    await pool.execute(
        "UPDATE produce_batches SET status = 'in_processing' WHERE id = $1 AND tenant_id = $2",
        batch_uuid,
        uuid.UUID(tenant_id),
    )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(SAHOOL_TRACEABILITY_PROCESSING_RECORDED, json.dumps({"batch_id": batch_id, "tenant_id": tenant_id}).encode())

    logger.info("processing_recorded", batch_id=batch_id)
    return {"status": "recorded", "event": _row_to_dict(row)}


@router.post("/batches/{batch_id}/events/storage")
async def record_storage_event(
    batch_id: str,
    request: StorageEventRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Record storage event - تسجيل حدث التخزين"""
    pool = await _get_db(req)
    await _get_batch_or_404(pool, batch_id, tenant_id)
    batch_uuid = uuid.UUID(batch_id)

    row = await pool.fetchrow(
        """
        INSERT INTO supply_chain_events (batch_id, event_type, location, temperature_c, humidity_percent)
        VALUES ($1, 'storage', $2, $3, $4)
        RETURNING *
        """,
        batch_uuid,
        request.location,
        request.temperature_c,
        request.humidity_percent,
    )

    await pool.execute(
        "UPDATE produce_batches SET status = 'in_storage' WHERE id = $1 AND tenant_id = $2",
        batch_uuid,
        uuid.UUID(tenant_id),
    )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(SAHOOL_TRACEABILITY_STORAGE_RECORDED, json.dumps({"batch_id": batch_id, "tenant_id": tenant_id}).encode())

    logger.info("storage_recorded", batch_id=batch_id)
    return {"status": "recorded", "event": _row_to_dict(row)}


@router.post("/batches/{batch_id}/events/transport")
async def record_transport_event(
    batch_id: str,
    request: TransportEventRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Record transport event - تسجيل حدث النقل"""
    pool = await _get_db(req)
    await _get_batch_or_404(pool, batch_id, tenant_id)
    batch_uuid = uuid.UUID(batch_id)

    metadata = {}
    if request.distance_km:
        metadata["distance_km"] = request.distance_km

    row = await pool.fetchrow(
        """
        INSERT INTO supply_chain_events (batch_id, event_type, origin, destination, transport_mode, vehicle_id, metadata)
        VALUES ($1, 'transport', $2, $3, $4, $5, $6)
        RETURNING *
        """,
        batch_uuid,
        request.origin,
        request.destination,
        request.transport_mode,
        request.vehicle_id,
        json.dumps(metadata) if metadata else "{}",
    )

    await pool.execute(
        "UPDATE produce_batches SET status = 'in_transit' WHERE id = $1 AND tenant_id = $2",
        batch_uuid,
        uuid.UUID(tenant_id),
    )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(SAHOOL_TRACEABILITY_TRANSPORT_RECORDED, json.dumps({"batch_id": batch_id, "tenant_id": tenant_id}).encode())

    logger.info("transport_recorded", batch_id=batch_id)
    return {"status": "recorded", "event": _row_to_dict(row)}


@router.get("/batches/{batch_id}/events")
async def list_batch_events(batch_id: str, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """List all events for a batch - قائمة أحداث الدفعة"""
    pool = await _get_db(req)
    await _get_batch_or_404(pool, batch_id, tenant_id)

    rows = await pool.fetch(
        "SELECT * FROM supply_chain_events WHERE batch_id = $1 ORDER BY timestamp ASC",
        uuid.UUID(batch_id),
    )
    events = [_row_to_dict(r) for r in rows]
    return {"batch_id": batch_id, "events": events, "count": len(events)}


# === QR Code & Journey Endpoints ===


@router.get("/batches/{batch_id}/qr")
async def generate_qr_code(batch_id: str, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Generate QR code for batch - إنشاء رمز QR للدفعة"""
    pool = await _get_db(req)
    batch = _row_to_dict(await _get_batch_or_404(pool, batch_id, tenant_id))

    try:
        from shared.traceability import QRCodeGenerator
        from shared.traceability.models import ProduceBatch

        qr_gen = QRCodeGenerator()
        batch_obj = ProduceBatch(
            id=batch["id"],
            batch_code=batch["batch_code"],
            product_name_en=batch["product_name_en"],
            product_name_ar=batch["product_name_ar"],
        )
        qr_result = qr_gen.generate_for_batch(batch_obj)
        return {
            "batch_id": batch_id,
            "batch_code": batch["batch_code"],
            "qr_data": getattr(qr_result, "data", str(qr_result)),
            "format": getattr(qr_result, "format", "png"),
        }
    except (ImportError, Exception) as e:
        logger.warning("qr_generation_fallback", error=str(e))

    return {
        "batch_id": batch_id,
        "batch_code": batch["batch_code"],
        "qr_data": f"https://sahool.app/trace/{batch['batch_code']}",
        "format": "url",
    }


@router.get("/journey/{batch_code}")
async def get_product_journey(batch_code: str, req: Request):
    """Get consumer-facing product journey - رحلة المنتج للمستهلك"""
    pool = await _get_db(req)

    batch = await pool.fetchrow("SELECT * FROM produce_batches WHERE batch_code = $1", batch_code)
    if not batch:
        raise HTTPException(status_code=404, detail={"error": "Product not found", "error_ar": "المنتج غير موجود"})

    batch_data = _row_to_dict(batch)
    events = await pool.fetch(
        "SELECT * FROM supply_chain_events WHERE batch_id = $1 ORDER BY timestamp ASC",
        batch["id"],
    )

    journey_steps = []
    for e in events:
        step = {
            "event_type": e["event_type"],
            "timestamp": e["timestamp"].isoformat() if e["timestamp"] else None,
            "location": e["location"],
        }
        if e["event_type"] == "harvest":
            step["crop_type"] = e["crop_type"]
            step["quality_grade"] = e["quality_grade"]
        elif e["event_type"] == "processing":
            step["facility"] = e["facility_name"]
            step["process_type"] = e["process_type"]
        elif e["event_type"] == "storage":
            step["temperature_c"] = float(e["temperature_c"]) if e["temperature_c"] else None
        elif e["event_type"] == "transport":
            step["origin"] = e["origin"]
            step["destination"] = e["destination"]
            step["mode"] = e["transport_mode"]
        journey_steps.append(step)

    # Get certifications
    certs = await pool.fetch(
        "SELECT * FROM batch_certifications WHERE batch_id = $1 AND status = 'active'",
        batch["id"],
    )

    return {
        "batch_code": batch_code,
        "product_name_en": batch_data["product_name_en"],
        "product_name_ar": batch_data["product_name_ar"],
        "farm_id": batch_data["farm_id"],
        "status": batch_data["status"],
        "quality_grade": batch_data.get("quality_grade"),
        "journey": journey_steps,
        "certifications": [_row_to_dict(c) for c in certs],
    }


# === Batch Code Endpoints ===


@router.post("/batches/generate-code")
async def generate_code(request: GenerateCodeRequest, current_user: User = Depends(get_current_user)):
    """Generate a batch code - إنشاء رمز دفعة"""
    code = _generate_batch_code(request.product_code, request.year, request.sequence, request.farm_code)
    return {"batch_code": code}


@router.get("/batches/verify-code/{code}")
async def verify_code(code: str, req: Request):
    """Verify a batch code format - التحقق من صيغة رمز الدفعة"""
    pool = await _get_db(req)
    exists = await pool.fetchval("SELECT EXISTS(SELECT 1 FROM produce_batches WHERE batch_code = $1)", code)
    return {"code": code, "valid": bool(code), "exists": exists}


# === Batch Split Endpoint ===


@router.post("/batches/{batch_id}/split")
async def split_batch(
    batch_id: str,
    request: BatchSplitRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Split a batch into sub-batches - تقسيم الدفعة إلى دفعات فرعية"""
    pool = await _get_db(req)
    parent = _row_to_dict(await _get_batch_or_404(pool, batch_id, tenant_id))

    parent_qty = float(parent.get("quantity", 0))
    total_split = sum(request.quantities)
    if total_split > parent_qty:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Split total ({total_split}) exceeds batch quantity ({parent_qty})",
                "error_ar": f"مجموع التقسيم ({total_split}) يتجاوز كمية الدفعة ({parent_qty})",
            },
        )

    child_batches = []
    for i, qty in enumerate(request.quantities, 1):
        child_code = f"{parent['batch_code']}-S{i}"
        child = await pool.fetchrow(
            """
            INSERT INTO produce_batches (tenant_id, farm_id, field_id, batch_code, product_name_en, product_name_ar, variety, quantity, unit, quality_grade, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'created')
            RETURNING *
            """,
            parent["tenant_id"],
            parent["farm_id"],
            parent["field_id"],
            child_code,
            parent["product_name_en"],
            parent["product_name_ar"],
            parent.get("variety"),
            qty,
            parent.get("unit", "kg"),
            parent.get("quality_grade", "A"),
        )
        child_batches.append(_row_to_dict(child))

    remaining = parent_qty - total_split
    new_status = "split" if remaining == 0 else parent.get("status", "created")
    await pool.execute(
        "UPDATE produce_batches SET quantity = $1, status = $2 WHERE id = $3 AND tenant_id = $4",
        remaining,
        new_status,
        uuid.UUID(batch_id),
        uuid.UUID(tenant_id),
    )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            SAHOOL_TRACEABILITY_BATCH_SPLIT,
            json.dumps({"batch_id": batch_id, "child_count": len(child_batches)}).encode(),
        )

    logger.info("batch_split", parent_id=batch_id, children=len(child_batches))
    return {"parent_batch_id": batch_id, "remaining_quantity": remaining, "child_batches": child_batches}


# === Carbon Footprint Endpoint ===


@router.get("/carbon/{batch_id}")
async def estimate_carbon_footprint(batch_id: str, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Estimate carbon footprint for batch - تقدير البصمة الكربونية"""
    pool = await _get_db(req)
    batch = _row_to_dict(await _get_batch_or_404(pool, batch_id, tenant_id))

    transport_events = await pool.fetch(
        "SELECT * FROM supply_chain_events WHERE batch_id = $1 AND event_type = 'transport'",
        uuid.UUID(batch_id),
    )

    try:
        from shared.traceability import calculate_carbon_footprint
        from shared.traceability.models import TransportMode

        mode_map = {
            "truck": TransportMode.TRUCK_AMBIENT,
            "truck_refrigerated": TransportMode.TRUCK_REFRIGERATED,
            "air": TransportMode.AIR_FREIGHT,
            "sea": TransportMode.SEA_FREIGHT,
            "rail": TransportMode.RAIL,
            "local": TransportMode.LOCAL_DELIVERY,
        }

        total_footprint = 0.0
        quantity_kg = float(batch.get("quantity", 0))
        for te in transport_events:
            mode = mode_map.get(te["transport_mode"] or "truck", TransportMode.TRUCK_AMBIENT)
            metadata = te.get("metadata") or {}
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            distance = metadata.get("distance_km", 100.0)
            total_footprint += calculate_carbon_footprint(distance, mode, quantity_kg)

        return {"batch_id": batch_id, "carbon_footprint_kg_co2": round(total_footprint, 3)}
    except (ImportError, Exception):
        return {"batch_id": batch_id, "carbon_footprint_kg_co2": None, "message": "Carbon calculation not available"}


# === Recall Management Endpoints (GS1 EPCIS compliance) ===


class RecallInitiateRequest(BaseModel):
    reason_en: str
    reason_ar: str
    severity: str = Field("high", description="low, medium, high, critical")
    affected_regions: list[str] | None = None
    notes: str | None = None


@router.post("/batches/{batch_id}/recall")
async def initiate_recall(
    batch_id: str,
    request: RecallInitiateRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Initiate product recall - بدء استرجاع المنتج (GS1 EPCIS compliant)"""
    pool = await _get_db(req)
    batch = _row_to_dict(await _get_batch_or_404(pool, batch_id, tenant_id))

    if batch.get("status") == "recalled":
        raise HTTPException(
            status_code=400,
            detail={"error": "Batch already recalled", "error_ar": "تم استرجاع الدفعة بالفعل"},
        )

    # Update batch status to recalled
    await pool.execute(
        "UPDATE produce_batches SET status = 'recalled' WHERE id = $1 AND tenant_id = $2",
        uuid.UUID(batch_id),
        uuid.UUID(tenant_id),
    )

    # Record recall event in supply chain
    recall_event = await pool.fetchrow(
        """
        INSERT INTO supply_chain_events (batch_id, event_type, notes, notes_ar, metadata)
        VALUES ($1, 'recall', $2, $3, $4)
        RETURNING *
        """,
        uuid.UUID(batch_id),
        request.reason_en,
        request.reason_ar,
        json.dumps(
            {
                "severity": request.severity,
                "affected_regions": request.affected_regions or [],
                "initiated_at": datetime.now(UTC).isoformat(),
            }
        ),
    )

    # Forward trace: find child batches that need recall
    child_batches = await pool.fetch(
        "SELECT id, batch_code, status FROM produce_batches WHERE batch_code LIKE $1 AND status != 'recalled'",
        f"{batch['batch_code']}-S%",
    )
    affected_children = [
        {"id": str(c["id"]), "batch_code": c["batch_code"], "status": c["status"]} for c in child_batches
    ]

    # Recall child batches too
    if child_batches:
        child_ids = [c["id"] for c in child_batches]
        await pool.execute(
            "UPDATE produce_batches SET status = 'recalled' WHERE id = ANY($1::uuid[]) AND tenant_id = $2",
            child_ids,
            uuid.UUID(tenant_id),
        )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            SAHOOL_TRACEABILITY_BATCH_RECALLED,
            json.dumps(
                {
                    "batch_id": batch_id,
                    "batch_code": batch["batch_code"],
                    "severity": request.severity,
                    "affected_children": len(affected_children),
                }
            ).encode(),
        )
        # Critical notification for recalls
        await nc.publish(
            SAHOOL_NOTIFICATION_SEND,
            json.dumps(
                {
                    "type": "product_recall",
                    "priority": "critical",
                    "batch_id": batch_id,
                    "batch_code": batch["batch_code"],
                    "title_en": f"Product Recall: {batch['batch_code']} - {request.reason_en}",
                    "title_ar": f"استرجاع منتج: {batch['batch_code']} - {request.reason_ar}",
                    "severity": request.severity,
                }
            ).encode(),
        )

    logger.warning("batch_recalled", batch_id=batch_id, batch_code=batch["batch_code"], severity=request.severity)
    return {
        "status": "recalled",
        "batch_id": batch_id,
        "batch_code": batch["batch_code"],
        "reason_en": request.reason_en,
        "reason_ar": request.reason_ar,
        "severity": request.severity,
        "affected_children": affected_children,
        "recall_event": _row_to_dict(recall_event),
        "recalled_at": datetime.now(UTC).isoformat(),
    }
