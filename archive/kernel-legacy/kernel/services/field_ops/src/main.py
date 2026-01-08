"""
SAHOOL Field Operations Service - Main API
Agricultural field management and operations
Port: 8080
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Field Operations Service...")
    # Initialize connections
    app.state.db_connected = False
    app.state.nats_connected = False

    # Try database connection
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
            app.state.db_connected = True
            logger.info("Database connected")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            app.state.db_pool = None

    # Try NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("NATS connected")
        except Exception as e:
            logger.warning(f"NATS connection failed: {e}")
            app.state.nc = None

    logger.info("Field Operations ready on port 8080")
    yield

    # Cleanup
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
    logger.info("Field Operations shutting down")


app = FastAPI(
    title="SAHOOL Field Operations",
    description="Agricultural field management, operations tracking, and data aggregation",
    version="15.3.3",
    lifespan=lifespan,
)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "service": "field_ops",
        "version": "15.3.3",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }


# ============== Request/Response Models ==============


class FieldCreate(BaseModel):
    tenant_id: str
    name: str
    name_ar: str | None = None
    area_hectares: float = Field(gt=0)
    crop_type: str | None = None
    geometry: dict | None = None
    metadata: dict | None = None


class FieldUpdate(BaseModel):
    name: str | None = None
    name_ar: str | None = None
    area_hectares: float | None = Field(default=None, gt=0)
    crop_type: str | None = None
    geometry: dict | None = None
    metadata: dict | None = None


class FieldResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    name_ar: str | None
    area_hectares: float
    crop_type: str | None
    created_at: str
    updated_at: str


class OperationCreate(BaseModel):
    tenant_id: str
    field_id: str
    operation_type: str  # planting, irrigation, fertilizing, harvesting, etc.
    scheduled_date: str | None = None
    notes: str | None = None
    metadata: dict | None = None


class OperationResponse(BaseModel):
    id: str
    field_id: str
    operation_type: str
    status: str
    scheduled_date: str | None
    completed_date: str | None
    created_at: str


# ============== Mock Data Store ==============

# In-memory store for demo (replace with database in production)
_fields: dict = {}
_operations: dict = {}


# ============== Field Endpoints ==============


@app.post("/fields", response_model=FieldResponse)
async def create_field(field: FieldCreate):
    """Create a new agricultural field"""
    field_id = str(uuid4())
    now = datetime.now(UTC).isoformat()

    field_data = {
        "id": field_id,
        "tenant_id": field.tenant_id,
        "name": field.name,
        "name_ar": field.name_ar,
        "area_hectares": field.area_hectares,
        "crop_type": field.crop_type,
        "geometry": field.geometry,
        "metadata": field.metadata or {},
        "created_at": now,
        "updated_at": now,
    }

    _fields[field_id] = field_data

    # Publish event if NATS connected
    if hasattr(app.state, "nc") and app.state.nc:
        try:
            import json

            await app.state.nc.publish(
                "sahool.fields.created",
                json.dumps({"field_id": field_id, "tenant_id": field.tenant_id}).encode(),
            )
        except Exception:
            pass

    return FieldResponse(**field_data)


@app.get("/fields/{field_id}", response_model=FieldResponse)
async def get_field(field_id: str):
    """Get field by ID"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="Field not found")
    return FieldResponse(**_fields[field_id])


@app.get("/fields")
async def list_fields(
    tenant_id: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List fields for a tenant"""
    tenant_fields = [f for f in _fields.values() if f["tenant_id"] == tenant_id]
    return {
        "items": tenant_fields[skip : skip + limit],
        "total": len(tenant_fields),
        "skip": skip,
        "limit": limit,
    }


@app.put("/fields/{field_id}", response_model=FieldResponse)
async def update_field(field_id: str, update: FieldUpdate):
    """Update field information"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="Field not found")

    field_data = _fields[field_id]
    update_dict = update.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        if value is not None:
            field_data[key] = value

    field_data["updated_at"] = datetime.utcnow().isoformat()
    _fields[field_id] = field_data

    return FieldResponse(**field_data)


@app.delete("/fields/{field_id}")
async def delete_field(field_id: str):
    """Delete a field"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="Field not found")

    del _fields[field_id]
    return {"status": "deleted", "field_id": field_id}


# ============== Operations Endpoints ==============


@app.post("/operations", response_model=OperationResponse)
async def create_operation(op: OperationCreate):
    """Create a field operation"""
    op_id = str(uuid4())
    now = datetime.now(UTC).isoformat()

    op_data = {
        "id": op_id,
        "tenant_id": op.tenant_id,
        "field_id": op.field_id,
        "operation_type": op.operation_type,
        "status": "scheduled",
        "scheduled_date": op.scheduled_date,
        "completed_date": None,
        "notes": op.notes,
        "metadata": op.metadata or {},
        "created_at": now,
    }

    _operations[op_id] = op_data

    return OperationResponse(**op_data)


@app.get("/operations/{operation_id}", response_model=OperationResponse)
async def get_operation(operation_id: str):
    """Get operation by ID"""
    if operation_id not in _operations:
        raise HTTPException(status_code=404, detail="Operation not found")
    return OperationResponse(**_operations[operation_id])


@app.get("/operations")
async def list_operations(
    field_id: str = Query(...),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List operations for a field"""
    field_ops = [o for o in _operations.values() if o["field_id"] == field_id]
    if status:
        field_ops = [o for o in field_ops if o["status"] == status]

    return {
        "items": field_ops[skip : skip + limit],
        "total": len(field_ops),
        "skip": skip,
        "limit": limit,
    }


@app.post("/operations/{operation_id}/complete")
async def complete_operation(operation_id: str):
    """Mark operation as completed"""
    if operation_id not in _operations:
        raise HTTPException(status_code=404, detail="Operation not found")

    op_data = _operations[operation_id]
    op_data["status"] = "completed"
    op_data["completed_date"] = datetime.utcnow().isoformat()
    _operations[operation_id] = op_data

    # Publish event if NATS connected
    if hasattr(app.state, "nc") and app.state.nc:
        try:
            import json

            await app.state.nc.publish(
                "sahool.operations.completed",
                json.dumps(
                    {
                        "operation_id": operation_id,
                        "field_id": op_data["field_id"],
                        "operation_type": op_data["operation_type"],
                    }
                ).encode(),
            )
        except Exception:
            pass

    return OperationResponse(**op_data)


# ============== Aggregation Endpoints ==============


@app.get("/stats/tenant/{tenant_id}")
async def get_tenant_stats(tenant_id: str):
    """Get statistics for a tenant"""
    tenant_fields = [f for f in _fields.values() if f["tenant_id"] == tenant_id]
    tenant_ops = [o for o in _operations.values() if o["tenant_id"] == tenant_id]

    return {
        "tenant_id": tenant_id,
        "fields_count": len(tenant_fields),
        "total_area_hectares": sum(f["area_hectares"] for f in tenant_fields),
        "operations": {
            "total": len(tenant_ops),
            "scheduled": len([o for o in tenant_ops if o["status"] == "scheduled"]),
            "completed": len([o for o in tenant_ops if o["status"] == "completed"]),
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
