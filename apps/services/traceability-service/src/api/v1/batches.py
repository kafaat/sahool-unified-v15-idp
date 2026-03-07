"""
Traceability API endpoints - نقاط نهاية التتبع
Integrates with shared.traceability module for supply chain tracking.
"""

import json
import uuid
from datetime import datetime
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

logger = structlog.get_logger()

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}


router = APIRouter(prefix="/api/v1/traceability", tags=["traceability"])

# In-memory storage
_batches: dict[str, dict] = {}
_tracker = None


def _get_tracker():
    global _tracker
    if _tracker is None:
        try:
            from shared.traceability import SupplyChainTracker

            _tracker = SupplyChainTracker()
        except ImportError:
            pass
    return _tracker


# === Request Models ===


class BatchCreateRequest(BaseModel):
    tenant_id: str
    farm_id: str
    field_id: str
    product_name_en: str
    product_name_ar: str
    quantity: float = Field(..., gt=0)
    unit: str = "kg"
    variety: str | None = None
    batch_code: str | None = None


class HarvestEventRequest(BaseModel):
    batch_id: str
    field_name_en: str
    field_name_ar: str
    crop_type: str
    harvest_method_en: str = "Manual"
    harvest_method_ar: str = "يدوي"
    quality_grade: str = "A"


class ProcessingEventRequest(BaseModel):
    batch_id: str
    facility_name: str
    process_type: str
    notes: str | None = None


class StorageEventRequest(BaseModel):
    batch_id: str
    location: str
    temperature_c: float | None = None
    humidity_percent: float | None = None


class TransportEventRequest(BaseModel):
    batch_id: str
    origin: str
    destination: str
    transport_mode: str = "truck"
    vehicle_id: str | None = None


class BatchUpdateRequest(BaseModel):
    product_name_en: str | None = None
    product_name_ar: str | None = None
    quantity: float | None = Field(None, gt=0)
    status: str | None = None


class BatchSplitRequest(BaseModel):
    batch_id: str
    quantities: list[float]


class GenerateCodeRequest(BaseModel):
    product_code: str = Field(..., min_length=2, max_length=3, description="2-3 letter product code (e.g. WH, TM)")
    year: int | None = None
    sequence: int = Field(..., ge=1)
    farm_code: str | None = Field(None, min_length=3, max_length=3)


# === Endpoints ===


@router.post("/batches", status_code=201)
async def create_batch(request: BatchCreateRequest, req: Request, _user=Depends(get_current_user)):
    """Create a new produce batch - إنشاء دفعة منتج جديدة"""
    tracker = _get_tracker()

    if tracker:
        try:
            from shared.traceability import generate_batch_code

            product_code = request.product_name_en[:2].upper()
            batch_code = request.batch_code or generate_batch_code(
                product_code=product_code,
                year=datetime.utcnow().year,
                sequence=len(_batches) + 1,
                farm_code=request.farm_id[:3].upper() if request.farm_id else None,
            )
            batch = tracker.create_batch(
                tenant_id=request.tenant_id,
                farm_id=request.farm_id,
                field_id=request.field_id,
                product_name_en=request.product_name_en,
                product_name_ar=request.product_name_ar,
                batch_code=batch_code,
                quantity=request.quantity,
            )
            batch_data = {
                "id": batch.id,
                "batch_code": batch.batch_code,
                "product_name_en": batch.product_name_en,
                "product_name_ar": batch.product_name_ar,
                "quantity": batch.quantity,
                "farm_id": request.farm_id,
                "field_id": request.field_id,
                "tenant_id": request.tenant_id,
                "status": batch.status.value if hasattr(batch.status, "value") else str(batch.status),
                "created_at": datetime.utcnow().isoformat(),
                "_batch_obj": batch,
            }
            _batches[batch.id] = batch_data

            nc = getattr(req.app.state, "nc", None)
            if nc:
                await nc.publish(
                    "sahool.traceability.batch_created",
                    json.dumps(
                        {"batch_id": batch.id, "batch_code": batch_code, "tenant_id": request.tenant_id}
                    ).encode(),
                )

            logger.info("batch_created", batch_id=batch.id, batch_code=batch_code)
            return {k: v for k, v in batch_data.items() if k != "_batch_obj"}
        except Exception as e:
            logger.error("batch_creation_failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    else:
        batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        batch_data = {
            "id": batch_id,
            "batch_code": request.batch_code
            or f"{request.product_name_en[:2].upper()}-{datetime.utcnow().strftime('%y')}-{uuid.uuid4().hex[:4].upper()}",
            "product_name_en": request.product_name_en,
            "product_name_ar": request.product_name_ar,
            "quantity": request.quantity,
            "unit": request.unit,
            "farm_id": request.farm_id,
            "field_id": request.field_id,
            "tenant_id": request.tenant_id,
            "status": "created",
            "events": [],
            "created_at": datetime.utcnow().isoformat(),
        }
        _batches[batch_id] = batch_data
        return batch_data


@router.get("/batches/{batch_id}")
async def get_batch(batch_id: str):
    """Get batch details - الحصول على تفاصيل الدفعة"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})
    return {k: v for k, v in _batches[batch_id].items() if k != "_batch_obj"}


@router.get("/batches")
async def list_batches(tenant_id: str | None = None, farm_id: str | None = None):
    """List batches with optional filtering - قائمة الدفعات"""
    result = list(_batches.values())
    if tenant_id:
        result = [b for b in result if b.get("tenant_id") == tenant_id]
    if farm_id:
        result = [b for b in result if b.get("farm_id") == farm_id]
    return {"batches": [{k: v for k, v in b.items() if k != "_batch_obj"} for b in result], "count": len(result)}


@router.post("/batches/{batch_id}/events/harvest")
async def record_harvest_event(batch_id: str, request: HarvestEventRequest, req: Request):
    """Record harvest event - تسجيل حدث الحصاد"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    tracker = _get_tracker()
    if tracker:
        try:
            batch_obj = _batches[batch_id].get("_batch_obj")
            if batch_obj:
                tracker.record_harvest(
                    batch_id=batch_obj.id,
                    field_name_en=request.field_name_en,
                    field_name_ar=request.field_name_ar,
                    crop_type=request.crop_type,
                    harvest_method_en=request.harvest_method_en,
                    harvest_method_ar=request.harvest_method_ar,
                )
        except Exception as e:
            logger.warning("harvest_record_fallback", error=str(e))

    event = {
        "type": "harvest",
        "timestamp": datetime.utcnow().isoformat(),
        "crop_type": request.crop_type,
        "quality_grade": request.quality_grade,
        "field_name": request.field_name_en,
    }
    _batches[batch_id].setdefault("events", []).append(event)

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish("sahool.traceability.harvest_recorded", json.dumps({"batch_id": batch_id}).encode())

    logger.info("harvest_recorded", batch_id=batch_id)
    return {"status": "recorded", "event": event}


@router.post("/batches/{batch_id}/events/processing")
async def record_processing_event(batch_id: str, request: ProcessingEventRequest):
    """Record processing event - تسجيل حدث المعالجة"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    event = {
        "type": "processing",
        "timestamp": datetime.utcnow().isoformat(),
        "facility": request.facility_name,
        "process_type": request.process_type,
    }
    _batches[batch_id].setdefault("events", []).append(event)
    return {"status": "recorded", "event": event}


@router.post("/batches/{batch_id}/events/storage")
async def record_storage_event(batch_id: str, request: StorageEventRequest):
    """Record storage event - تسجيل حدث التخزين"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    event = {
        "type": "storage",
        "timestamp": datetime.utcnow().isoformat(),
        "location": request.location,
        "temperature_c": request.temperature_c,
        "humidity_percent": request.humidity_percent,
    }
    _batches[batch_id].setdefault("events", []).append(event)
    return {"status": "recorded", "event": event}


@router.post("/batches/{batch_id}/events/transport")
async def record_transport_event(batch_id: str, request: TransportEventRequest):
    """Record transport event - تسجيل حدث النقل"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    event = {
        "type": "transport",
        "timestamp": datetime.utcnow().isoformat(),
        "origin": request.origin,
        "destination": request.destination,
        "mode": request.transport_mode,
    }
    _batches[batch_id].setdefault("events", []).append(event)
    return {"status": "recorded", "event": event}


@router.get("/batches/{batch_id}/qr")
async def generate_qr_code(batch_id: str):
    """Generate QR code for batch - إنشاء رمز QR للدفعة"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    batch = _batches[batch_id]
    try:
        from shared.traceability import QRCodeGenerator

        qr_gen = QRCodeGenerator()
        batch_obj = batch.get("_batch_obj")
        if batch_obj:
            qr_result = qr_gen.generate_for_batch(batch_obj)
            return {
                "batch_id": batch_id,
                "batch_code": batch.get("batch_code"),
                "qr_data": qr_result.data,
                "format": qr_result.format,
            }
    except (ImportError, Exception) as e:
        logger.warning("qr_generation_fallback", error=str(e))

    return {
        "batch_id": batch_id,
        "batch_code": batch.get("batch_code"),
        "qr_data": f"https://sahool.app/trace/{batch.get('batch_code', batch_id)}",
        "format": "url",
    }


@router.get("/journey/{batch_code}")
async def get_product_journey(batch_code: str):
    """Get consumer-facing product journey - رحلة المنتج للمستهلك"""
    batch = next((b for b in _batches.values() if b.get("batch_code") == batch_code), None)
    if not batch:
        raise HTTPException(status_code=404, detail={"error": "Product not found", "error_ar": "المنتج غير موجود"})

    tracker = _get_tracker()
    if tracker:
        try:
            batch_obj = batch.get("_batch_obj")
            if batch_obj:
                journey = tracker.build_product_journey(batch_obj.id)
                return {
                    "batch_code": batch_code,
                    "product_name_en": batch.get("product_name_en"),
                    "product_name_ar": batch.get("product_name_ar"),
                    "journey": journey,
                }
        except Exception as e:
            logger.warning("journey_build_fallback", error=str(e))

    return {
        "batch_code": batch_code,
        "product_name_en": batch.get("product_name_en"),
        "product_name_ar": batch.get("product_name_ar"),
        "events": batch.get("events", []),
        "farm_id": batch.get("farm_id"),
        "status": batch.get("status"),
    }


@router.put("/batches/{batch_id}")
async def update_batch(batch_id: str, request: BatchUpdateRequest):
    """Update batch details - تحديث تفاصيل الدفعة"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    batch = _batches[batch_id]
    updates = request.model_dump(exclude_none=True)
    batch.update(updates)
    logger.info("batch_updated", batch_id=batch_id, fields=list(updates.keys()))
    return {k: v for k, v in batch.items() if k != "_batch_obj"}


@router.get("/batches/{batch_id}/events")
async def list_batch_events(batch_id: str):
    """List all events for a batch - قائمة أحداث الدفعة"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    events = _batches[batch_id].get("events", [])
    return {"batch_id": batch_id, "events": events, "count": len(events)}


@router.post("/batches/generate-code")
async def generate_code(request: GenerateCodeRequest):
    """Generate a batch code - إنشاء رمز دفعة"""
    try:
        from shared.traceability import generate_batch_code

        code = generate_batch_code(
            product_code=request.product_code,
            year=request.year or datetime.utcnow().year,
            sequence=request.sequence,
            farm_code=request.farm_code,
        )
        return {"batch_code": code}
    except ImportError:
        year_short = str(request.year or datetime.utcnow().year)[-2:]
        code = f"{request.product_code}-{year_short}-{request.sequence:03d}"
        if request.farm_code:
            code = f"{request.product_code}-{request.farm_code}-{year_short}-{request.sequence:03d}"
        return {"batch_code": code}


@router.get("/batches/verify-code/{code}")
async def verify_code(code: str):
    """Verify a batch code format - التحقق من صيغة رمز الدفعة"""
    try:
        from shared.traceability import decode_qr_data

        decoded = decode_qr_data(code)
        exists = any(b.get("batch_code") == code for b in _batches.values())
        return {"code": code, "valid": decoded is not None, "exists": exists, "decoded": decoded}
    except ImportError:
        exists = any(b.get("batch_code") == code for b in _batches.values())
        return {"code": code, "valid": bool(code), "exists": exists}


@router.post("/batches/{batch_id}/split")
async def split_batch(batch_id: str, request: BatchSplitRequest):
    """Split a batch into sub-batches - تقسيم الدفعة إلى دفعات فرعية"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    parent = _batches[batch_id]
    parent_qty = parent.get("quantity", 0)
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
        child_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        child = {
            "id": child_id,
            "batch_code": f"{parent.get('batch_code', '')}-S{i}",
            "product_name_en": parent.get("product_name_en"),
            "product_name_ar": parent.get("product_name_ar"),
            "quantity": qty,
            "unit": parent.get("unit", "kg"),
            "farm_id": parent.get("farm_id"),
            "field_id": parent.get("field_id"),
            "tenant_id": parent.get("tenant_id"),
            "parent_batch_id": batch_id,
            "status": "created",
            "events": list(parent.get("events", [])),
            "created_at": datetime.utcnow().isoformat(),
        }
        _batches[child_id] = child
        child_batches.append(child)

    parent["quantity"] = parent_qty - total_split
    parent["status"] = "split" if parent["quantity"] == 0 else parent.get("status", "created")

    logger.info("batch_split", parent_id=batch_id, children=len(child_batches))
    return {"parent_batch_id": batch_id, "remaining_quantity": parent["quantity"], "child_batches": child_batches}


@router.get("/carbon/{batch_id}")
async def estimate_carbon_footprint(batch_id: str):
    """Estimate carbon footprint for batch - تقدير البصمة الكربونية"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    try:
        from shared.traceability import calculate_carbon_footprint
        from shared.traceability.models import TransportMode

        batch = _batches[batch_id]
        events = batch.get("events", [])
        transport_events = [e for e in events if e.get("type") == "transport"]

        total_footprint = 0.0
        quantity_kg = batch.get("quantity", 0)
        mode_map = {
            "truck": TransportMode.TRUCK_AMBIENT,
            "truck_refrigerated": TransportMode.TRUCK_REFRIGERATED,
            "air": TransportMode.AIR_FREIGHT,
            "sea": TransportMode.SEA_FREIGHT,
            "rail": TransportMode.RAIL,
            "local": TransportMode.LOCAL_DELIVERY,
        }
        for te in transport_events:
            mode = mode_map.get(te.get("mode", "truck"), TransportMode.TRUCK_AMBIENT)
            distance = te.get("distance_km", 100.0)
            total_footprint += calculate_carbon_footprint(distance, mode, quantity_kg)

        return {"batch_id": batch_id, "carbon_footprint_kg_co2": round(total_footprint, 3)}
    except (ImportError, Exception):
        return {"batch_id": batch_id, "carbon_footprint_kg_co2": None, "message": "Carbon calculation not available"}
