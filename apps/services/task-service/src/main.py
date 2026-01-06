"""
SAHOOL Task Service - خدمة إدارة المهام الزراعية
Port: 8103

Provides task management for agricultural operations:
- Task CRUD (create, read, update, delete)
- Task assignment and completion
- Evidence attachment (photos, notes)
- Task filtering and search
"""

import os
import uuid
from datetime import datetime, timedelta
from enum import Enum

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "sahool-task-service"
SERVICE_PORT = int(os.getenv("PORT", "8103"))

app = FastAPI(
    title="SAHOOL Task Service",
    description="Agricultural task management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - Secure configuration
# In production, use explicit origins from environment or CORS_SETTINGS
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from shared.cors_config import CORS_SETTINGS

    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
    # Fallback for standalone deployment
    ALLOWED_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
    )

# ═══════════════════════════════════════════════════════════════════════════
# Enums & Models
# ═══════════════════════════════════════════════════════════════════════════


class TaskType(str, Enum):
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    SPRAYING = "spraying"
    SCOUTING = "scouting"
    MAINTENANCE = "maintenance"
    SAMPLING = "sampling"
    HARVEST = "harvest"
    PLANTING = "planting"
    OTHER = "other"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class TaskCreate(BaseModel):
    """Create a new task"""

    title: str = Field(..., min_length=1, max_length=200)
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType = TaskType.OTHER
    priority: TaskPriority = TaskPriority.MEDIUM
    field_id: str | None = None
    zone_id: str | None = None
    assigned_to: str | None = None
    due_date: datetime | None = None
    scheduled_time: str | None = None  # HH:MM format
    estimated_duration_minutes: int | None = None
    metadata: dict | None = None


class TaskUpdate(BaseModel):
    """Update task properties"""

    title: str | None = None
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType | None = None
    priority: TaskPriority | None = None
    field_id: str | None = None
    zone_id: str | None = None
    assigned_to: str | None = None
    due_date: datetime | None = None
    scheduled_time: str | None = None
    estimated_duration_minutes: int | None = None
    status: TaskStatus | None = None
    metadata: dict | None = None


class TaskComplete(BaseModel):
    """Complete a task with evidence"""

    notes: str | None = None
    notes_ar: str | None = None
    photo_urls: list[str] | None = None
    actual_duration_minutes: int | None = None
    completion_metadata: dict | None = None


class Evidence(BaseModel):
    """Evidence attached to a task"""

    evidence_id: str
    task_id: str
    type: str  # photo, note, voice, measurement
    content: str  # URL or text content
    captured_at: datetime
    location: dict | None = None  # {lat, lon}


class Task(BaseModel):
    """Full task model"""

    task_id: str
    tenant_id: str
    title: str
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    field_id: str | None = None
    zone_id: str | None = None
    assigned_to: str | None = None
    created_by: str
    due_date: datetime | None = None
    scheduled_time: str | None = None
    estimated_duration_minutes: int | None = None
    actual_duration_minutes: int | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    completion_notes: str | None = None
    evidence: list[Evidence] = []
    metadata: dict | None = None


# ═══════════════════════════════════════════════════════════════════════════
# In-Memory Storage (Replace with PostgreSQL in production)
# ═══════════════════════════════════════════════════════════════════════════

# TODO: MIGRATE TO POSTGRESQL
# Current: tasks_db and evidence_db stored in-memory (lost on restart)
# Issues:
#   - No persistence across service restarts
#   - No multi-instance support (distributed deployment)
#   - No transaction support for task + evidence updates
#   - No audit trail for task status changes
# Required:
#   1. Create PostgreSQL tables:
#      a) 'tasks' table:
#         - task_id (UUID, PK)
#         - tenant_id (VARCHAR, indexed)
#         - title, title_ar (VARCHAR)
#         - description, description_ar (TEXT)
#         - task_type (VARCHAR)
#         - priority (VARCHAR)
#         - status (VARCHAR, indexed)
#         - field_id (VARCHAR, indexed)
#         - zone_id (VARCHAR)
#         - assigned_to (VARCHAR, indexed)
#         - created_by (VARCHAR)
#         - due_date (TIMESTAMP, indexed)
#         - scheduled_time (TIME)
#         - estimated_duration_minutes (INTEGER)
#         - actual_duration_minutes (INTEGER)
#         - created_at (TIMESTAMP)
#         - updated_at (TIMESTAMP)
#         - completed_at (TIMESTAMP)
#         - completion_notes (TEXT)
#         - metadata (JSONB)
#      b) 'task_evidence' table:
#         - evidence_id (UUID, PK)
#         - task_id (UUID, FK -> tasks.task_id)
#         - type (VARCHAR)
#         - content (TEXT)
#         - captured_at (TIMESTAMP)
#         - location (GEOGRAPHY POINT)
#   2. Create Tortoise ORM models: Task, TaskEvidence
#   3. Create repository: TaskRepository with methods similar to current functions
#   4. Add indexes: (tenant_id, status), (assigned_to, status), (field_id, status)
#   5. Add task status history table for audit trail
# Migration Priority: HIGH - Task management is core functionality
tasks_db: dict[str, Task] = {}
evidence_db: dict[str, Evidence] = {}


def seed_demo_data():
    """Seed demo tasks for testing"""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    demo_tasks = [
        Task(
            task_id="task_001",
            tenant_id="tenant_demo",
            title="Irrigate North Field",
            title_ar="ري الحقل الشمالي",
            description="Sector C needs irrigation using pump #2",
            description_ar="القطاع C يحتاج ري باستخدام مضخة رقم 2",
            task_type=TaskType.IRRIGATION,
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            field_id="field_north",
            assigned_to="user_ahmed",
            created_by="user_admin",
            due_date=today + timedelta(hours=10),
            scheduled_time="08:00",
            estimated_duration_minutes=120,
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
            metadata={"pump_id": "pump_2", "water_volume_m3": 500},
        ),
        Task(
            task_id="task_002",
            tenant_id="tenant_demo",
            title="Pest Inspection",
            title_ar="فحص الحشرات",
            description="Weekly pest inspection for tomato greenhouse",
            description_ar="فحص أسبوعي للحشرات في بيت الطماطم المحمي",
            task_type=TaskType.SCOUTING,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.COMPLETED,
            field_id="field_greenhouse",
            assigned_to="user_ahmed",
            created_by="user_admin",
            due_date=today + timedelta(hours=12),
            scheduled_time="10:30",
            estimated_duration_minutes=60,
            actual_duration_minutes=45,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(hours=2),
            completed_at=now - timedelta(hours=2),
            completion_notes="No pests found. Healthy plants.",
        ),
        Task(
            task_id="task_003",
            tenant_id="tenant_demo",
            title="Collect Soil Samples",
            title_ar="جمع عينات التربة",
            description="Collect samples for nutrient analysis",
            description_ar="جمع عينات لتحليل المغذيات",
            task_type=TaskType.SAMPLING,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            field_id="field_south",
            assigned_to="user_ahmed",
            created_by="user_admin",
            due_date=today + timedelta(hours=16),
            scheduled_time="14:00",
            estimated_duration_minutes=90,
            created_at=now - timedelta(hours=12),
            updated_at=now - timedelta(hours=12),
        ),
        Task(
            task_id="task_004",
            tenant_id="tenant_demo",
            title="Apply NPK Fertilizer",
            title_ar="تسميد التربة (NPK)",
            description="Apply 50kg/ha NPK to south field",
            description_ar="تطبيق 50 كجم/هكتار NPK للحقل الجنوبي",
            task_type=TaskType.FERTILIZATION,
            priority=TaskPriority.LOW,
            status=TaskStatus.PENDING,
            field_id="field_south",
            assigned_to="user_mohammed",
            created_by="user_admin",
            due_date=today + timedelta(days=1),
            scheduled_time="07:00",
            estimated_duration_minutes=180,
            created_at=now - timedelta(hours=6),
            updated_at=now - timedelta(hours=6),
            metadata={"fertilizer_type": "NPK 20-20-20", "rate_kg_ha": 50},
        ),
        Task(
            task_id="task_005",
            tenant_id="tenant_demo",
            title="Irrigation System Maintenance",
            title_ar="صيانة نظام الري",
            description="Check filters and valves",
            description_ar="فحص الفلاتر والصمامات",
            task_type=TaskType.MAINTENANCE,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            field_id="field_north",
            assigned_to="user_tech",
            created_by="user_admin",
            due_date=today + timedelta(days=2),
            created_at=now - timedelta(hours=3),
            updated_at=now - timedelta(hours=3),
        ),
        Task(
            task_id="task_006",
            tenant_id="tenant_demo",
            title="Fungicide Spray",
            title_ar="رش مبيد فطري",
            description="Preventive spray for east field",
            description_ar="رش وقائي للحقل الشرقي",
            task_type=TaskType.SPRAYING,
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            field_id="field_east",
            assigned_to="user_ahmed",
            created_by="user_admin",
            due_date=today + timedelta(days=3),
            scheduled_time="06:00",
            estimated_duration_minutes=150,
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1),
            metadata={"chemical": "Mancozeb", "rate_ml_ha": 2500},
        ),
    ]

    for task in demo_tasks:
        tasks_db[task.task_id] = task


# Seed on startup
seed_demo_data()


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


def get_tenant_id(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")
) -> str:
    """Extract tenant ID from X-Tenant-Id header"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/api/v1/tasks", response_model=dict)
async def list_tasks(
    field_id: str | None = Query(None, description="Filter by field"),
    status: TaskStatus | None = Query(None, description="Filter by status"),
    task_type: TaskType | None = Query(None, description="Filter by type"),
    priority: TaskPriority | None = Query(None, description="Filter by priority"),
    assigned_to: str | None = Query(None, description="Filter by assignee"),
    due_before: datetime | None = Query(None, description="Due before date"),
    due_after: datetime | None = Query(None, description="Due after date"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """List tasks with optional filters"""
    filtered = [t for t in tasks_db.values() if t.tenant_id == tenant_id]

    if field_id:
        filtered = [t for t in filtered if t.field_id == field_id]
    if status:
        filtered = [t for t in filtered if t.status == status]
    if task_type:
        filtered = [t for t in filtered if t.task_type == task_type]
    if priority:
        filtered = [t for t in filtered if t.priority == priority]
    if assigned_to:
        filtered = [t for t in filtered if t.assigned_to == assigned_to]
    if due_before:
        filtered = [t for t in filtered if t.due_date and t.due_date <= due_before]
    if due_after:
        filtered = [t for t in filtered if t.due_date and t.due_date >= due_after]

    # Sort by due_date (urgent first), then priority
    priority_order = {
        TaskPriority.URGENT: 0,
        TaskPriority.HIGH: 1,
        TaskPriority.MEDIUM: 2,
        TaskPriority.LOW: 3,
    }
    filtered.sort(
        key=lambda t: (t.due_date or datetime.max, priority_order.get(t.priority, 99))
    )

    total = len(filtered)
    paginated = filtered[offset : offset + limit]

    return {
        "tasks": [t.model_dump() for t in paginated],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/tasks/today", response_model=dict)
async def get_today_tasks(
    tenant_id: str = Depends(get_tenant_id),
):
    """Get tasks due today"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_tasks = [
        t
        for t in tasks_db.values()
        if t.tenant_id == tenant_id
        and t.due_date
        and today_start <= t.due_date < today_end
    ]

    return {
        "tasks": [t.model_dump() for t in today_tasks],
        "count": len(today_tasks),
    }


@app.get("/api/v1/tasks/upcoming", response_model=dict)
async def get_upcoming_tasks(
    days: int = Query(7, ge=1, le=30),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get upcoming tasks for the next N days"""
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    tomorrow = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    upcoming = [
        t
        for t in tasks_db.values()
        if t.tenant_id == tenant_id
        and t.due_date
        and tomorrow <= t.due_date <= future
        and t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
    ]

    return {
        "tasks": [t.model_dump() for t in upcoming],
        "count": len(upcoming),
        "days": days,
    }


@app.get("/api/v1/tasks/stats", response_model=dict)
async def get_task_stats(
    tenant_id: str = Depends(get_tenant_id),
):
    """Get task statistics"""
    tenant_tasks = [t for t in tasks_db.values() if t.tenant_id == tenant_id]

    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)

    week_tasks = [
        t for t in tenant_tasks if t.due_date and week_start <= t.due_date < week_end
    ]

    completed_this_week = len(
        [t for t in week_tasks if t.status == TaskStatus.COMPLETED]
    )
    total_this_week = len(week_tasks)

    return {
        "total": len(tenant_tasks),
        "pending": len([t for t in tenant_tasks if t.status == TaskStatus.PENDING]),
        "in_progress": len(
            [t for t in tenant_tasks if t.status == TaskStatus.IN_PROGRESS]
        ),
        "completed": len([t for t in tenant_tasks if t.status == TaskStatus.COMPLETED]),
        "overdue": len(
            [
                t
                for t in tenant_tasks
                if t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
                and t.due_date
                and t.due_date < now
            ]
        ),
        "week_progress": {
            "completed": completed_this_week,
            "total": total_this_week,
            "percentage": (
                round(completed_this_week / total_this_week * 100)
                if total_this_week > 0
                else 0
            ),
        },
    }


@app.get("/api/v1/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get a specific task by ID"""
    task = tasks_db.get(task_id)
    if not task or task.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/api/v1/tasks", response_model=Task, status_code=201)
async def create_task(
    data: TaskCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new task"""
    now = datetime.utcnow()
    task_id = f"task_{uuid.uuid4().hex[:12]}"

    task = Task(
        task_id=task_id,
        tenant_id=tenant_id,
        title=data.title,
        title_ar=data.title_ar,
        description=data.description,
        description_ar=data.description_ar,
        task_type=data.task_type,
        priority=data.priority,
        status=TaskStatus.PENDING,
        field_id=data.field_id,
        zone_id=data.zone_id,
        assigned_to=data.assigned_to,
        created_by="user_system",  # Would come from auth in production
        due_date=data.due_date,
        scheduled_time=data.scheduled_time,
        estimated_duration_minutes=data.estimated_duration_minutes,
        created_at=now,
        updated_at=now,
        metadata=data.metadata,
    )

    tasks_db[task_id] = task
    return task


@app.put("/api/v1/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update a task"""
    task = tasks_db.get(task_id)
    if not task or task.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()
    tasks_db[task_id] = task
    return task


@app.post("/api/v1/tasks/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: str,
    data: TaskComplete,
    tenant_id: str = Depends(get_tenant_id),
):
    """Mark a task as completed with evidence"""
    task = tasks_db.get(task_id)
    if not task or task.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Task not found")

    now = datetime.utcnow()
    task.status = TaskStatus.COMPLETED
    task.completed_at = now
    task.updated_at = now
    task.completion_notes = data.notes or data.notes_ar

    if data.actual_duration_minutes:
        task.actual_duration_minutes = data.actual_duration_minutes

    # Add photo evidence
    if data.photo_urls:
        for url in data.photo_urls:
            evidence = Evidence(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                type="photo",
                content=url,
                captured_at=now,
            )
            task.evidence.append(evidence)
            evidence_db[evidence.evidence_id] = evidence

    if data.completion_metadata:
        task.metadata = {**(task.metadata or {}), **data.completion_metadata}

    tasks_db[task_id] = task
    return task


@app.post("/api/v1/tasks/{task_id}/start", response_model=Task)
async def start_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Mark a task as in progress"""
    task = tasks_db.get(task_id)
    if not task or task.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail="Task is not pending")

    task.status = TaskStatus.IN_PROGRESS
    task.updated_at = datetime.utcnow()
    tasks_db[task_id] = task
    return task


@app.post("/api/v1/tasks/{task_id}/cancel", response_model=Task)
async def cancel_task(
    task_id: str,
    reason: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Cancel a task"""
    task = tasks_db.get(task_id)
    if not task or task.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = TaskStatus.CANCELLED
    task.updated_at = datetime.utcnow()
    if reason:
        task.metadata = {**(task.metadata or {}), "cancel_reason": reason}

    tasks_db[task_id] = task
    return task


@app.delete("/api/v1/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Delete a task"""
    task = tasks_db.get(task_id)
    if not task or task.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Task not found")

    del tasks_db[task_id]


@app.post("/api/v1/tasks/{task_id}/evidence", response_model=Evidence, status_code=201)
async def add_evidence(
    task_id: str,
    evidence_type: str = Query(
        ..., description="Type: photo, note, voice, measurement"
    ),
    content: str = Query(..., description="URL or text content"),
    lat: float | None = None,
    lon: float | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Add evidence to a task"""
    task = tasks_db.get(task_id)
    if not task or task.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Task not found")

    evidence = Evidence(
        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        type=evidence_type,
        content=content,
        captured_at=datetime.utcnow(),
        location={"lat": lat, "lon": lon} if lat and lon else None,
    )

    task.evidence.append(evidence)
    task.updated_at = datetime.utcnow()
    tasks_db[task_id] = task
    evidence_db[evidence.evidence_id] = evidence

    return evidence


# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
