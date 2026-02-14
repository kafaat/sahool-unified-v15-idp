"""
Traceability API endpoints - نقاط نهاية التتبع
Integrates with shared.traceability module for supply chain tracking.
"""

import json
import uuid
from datetime import datetime
from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

logger = structlog.get_logger()

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


class BatchSplitRequest(BaseModel):
    batch_id: str
    quantities: list[float]


# === Endpoints ===


@router.post("/batches", status_code=201)
async def create_batch(request: BatchCreateRequest, req: Request):
    """Create a new produce batch - إنشاء دفعة منتج جديدة"""
    tracker = _get_tracker()

    if tracker:
        try:
            from shared.traceability import generate_batch_code

            batch_code = request.batch_code or generate_batch_code(request.product_name_en)
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
                    json.dumps({"batch_id": batch.id, "batch_code": batch_code, "tenant_id": request.tenant_id}).encode(),
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
            "batch_code": request.batch_code or f"{request.product_name_en[:2].upper()}-{datetime.utcnow().strftime('%y')}-{uuid.uuid4().hex[:4].upper()}",
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

    event = {"type": "processing", "timestamp": datetime.utcnow().isoformat(), "facility": request.facility_name, "process_type": request.process_type}
    _batches[batch_id].setdefault("events", []).append(event)
    return {"status": "recorded", "event": event}


@router.post("/batches/{batch_id}/events/storage")
async def record_storage_event(batch_id: str, request: StorageEventRequest):
    """Record storage event - تسجيل حدث التخزين"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    event = {"type": "storage", "timestamp": datetime.utcnow().isoformat(), "location": request.location, "temperature_c": request.temperature_c, "humidity_percent": request.humidity_percent}
    _batches[batch_id].setdefault("events", []).append(event)
    return {"status": "recorded", "event": event}


@router.post("/batches/{batch_id}/events/transport")
async def record_transport_event(batch_id: str, request: TransportEventRequest):
    """Record transport event - تسجيل حدث النقل"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    event = {"type": "transport", "timestamp": datetime.utcnow().isoformat(), "origin": request.origin, "destination": request.destination, "mode": request.transport_mode}
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


@router.get("/carbon/{batch_id}")
async def estimate_carbon_footprint(batch_id: str):
    """Estimate carbon footprint for batch - تقدير البصمة الكربونية"""
    if batch_id not in _batches:
        raise HTTPException(status_code=404, detail={"error": "Batch not found", "error_ar": "الدفعة غير موجودة"})

    try:
        from shared.traceability import calculate_carbon_footprint

        events = _batches[batch_id].get("events", [])
        footprint = calculate_carbon_footprint(events)
        return {"batch_id": batch_id, "carbon_footprint_kg_co2": footprint}
    except (ImportError, Exception):
        return {"batch_id": batch_id, "carbon_footprint_kg_co2": None, "message": "Carbon calculation not available"}
