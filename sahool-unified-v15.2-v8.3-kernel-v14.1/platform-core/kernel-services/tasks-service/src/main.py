"""
Tasks Service - Execution Service
Layer 4: Execution Service

خدمة المهام - طبقة التنفيذ
تستقبل التوصيات من Layer 3 وتحولها إلى مهام قابلة للتنفيذ

Responsibilities:
1. Subscribe to crop recommendations and decisions
2. Create actionable tasks for farmers
3. Track task assignments and completions
4. Publish task lifecycle events
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import nats

sys.path.insert(0, '/app')
from shared.events.base_event import EventTypes, create_event
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.metrics import EVENTS_PUBLISHED, EVENTS_CONSUMED, TASKS_PENDING, init_service_info, get_metrics, get_metrics_content_type

configure_logging(service_name="tasks-service")
logger = get_logger(__name__)
event_logger = EventLogger("tasks-service")

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "tasks-service"
SERVICE_LAYER = "execution"


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    task_id: str
    title: str
    description: str
    field_id: str
    crop_type: str
    priority: TaskPriority
    status: TaskStatus
    action_type: str
    due_date: datetime
    created_at: datetime
    tenant_id: str
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completion_notes: Optional[str] = None
    source_event_id: Optional[str] = None
    proverb_reference: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "priority": self.priority.value,
            "status": self.status.value,
            "action_type": self.action_type,
            "due_date": self.due_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "tenant_id": self.tenant_id,
            "assignee_id": self.assignee_id,
            "assignee_name": self.assignee_name,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "completion_notes": self.completion_notes,
            "source_event_id": self.source_event_id,
            "proverb_reference": self.proverb_reference
        }


class TaskStore:
    """In-memory task storage (use PostgreSQL in production)"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
    
    def create(self, task: Task) -> Task:
        self.tasks[task.task_id] = task
        return task
    
    def get(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def update(self, task: Task) -> Task:
        self.tasks[task.task_id] = task
        return task
    
    def delete(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]
    
    def list_by_status(self, status: TaskStatus) -> List[Task]:
        return [t for t in self.tasks.values() if t.status == status]
    
    def list_by_field(self, field_id: str) -> List[Task]:
        return [t for t in self.tasks.values() if t.field_id == field_id]
    
    def list_by_tenant(self, tenant_id: str) -> List[Task]:
        return [t for t in self.tasks.values() if t.tenant_id == tenant_id]
    
    def list_by_priority(self, priority: TaskPriority) -> List[Task]:
        return [t for t in self.tasks.values() if t.priority == priority]
    
    def list_overdue(self) -> List[Task]:
        now = datetime.utcnow()
        return [t for t in self.tasks.values() 
                if t.due_date < now and t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]]
    
    def get_stats(self, tenant_id: str = None) -> dict:
        tasks = self.tasks.values()
        if tenant_id:
            tasks = [t for t in tasks if t.tenant_id == tenant_id]
        
        return {
            "total": len(list(tasks)),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "assigned": len([t for t in tasks if t.status == TaskStatus.ASSIGNED]),
            "in_progress": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "overdue": len([t for t in tasks if t.status == TaskStatus.OVERDUE]),
            "urgent": len([t for t in tasks if t.priority == TaskPriority.URGENT and t.status == TaskStatus.PENDING])
        }


class TaskService:
    """Core tasks service"""
    
    def __init__(self):
        self.nc = None
        self.js = None
        self.store = TaskStore()
        self.running = False
    
    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("nats_connected")
    
    async def start(self):
        self.running = True
        
        # Subscribe to Layer 3 events
        subscriptions = [
            (EventTypes.CROP_ACTION_RECOMMENDED, "tasks-crop-rec"),
            (EventTypes.DISEASE_RISK_CALCULATED, "tasks-disease"),
            (EventTypes.ADVISOR_RECOMMENDATION_CREATED, "tasks-advisor"),
        ]
        
        for subject, durable in subscriptions:
            try:
                sub = await self.js.pull_subscribe(subject=subject, durable=durable, stream="SAHOOL")
                asyncio.create_task(self._process_events(sub, subject))
            except Exception as e:
                logger.warning("subscription_failed", subject=subject, error=str(e))
        
        # Start overdue checker
        asyncio.create_task(self._check_overdue_tasks())
        
        logger.info("tasks_service_started")
    
    async def _process_events(self, sub, subject: str):
        while self.running:
            try:
                messages = await sub.fetch(batch=10, timeout=1)
                for msg in messages:
                    await self._handle_event(msg, subject)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("event_processing_error", error=str(e))
                await asyncio.sleep(1)
    
    async def _handle_event(self, msg, subject: str):
        try:
            event_data = json.loads(msg.data.decode())
            event_type = event_data.get("event_type", subject)
            
            EVENTS_CONSUMED.labels(service=SERVICE_NAME, event_type=event_type, tenant_id="default").inc()
            event_logger.received(event_type, event_id=event_data.get("event_id"))
            
            if event_type == EventTypes.CROP_ACTION_RECOMMENDED:
                await self._create_task_from_recommendation(event_data)
            
            await msg.ack()
        except Exception as e:
            logger.error("event_handling_failed", error=str(e))
            await msg.nak()
    
    async def _create_task_from_recommendation(self, event_data: dict):
        """Create task from crop recommendation"""
        payload = event_data.get("payload", {})
        
        # Map priority
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT
        }
        
        priority = priority_map.get(payload.get("priority", "medium"), TaskPriority.MEDIUM)
        
        # Calculate due date
        deadline_str = payload.get("deadline")
        if deadline_str:
            try:
                due_date = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
            except:
                due_date = datetime.utcnow() + timedelta(days=3)
        else:
            # Default based on priority
            days = {"urgent": 1, "high": 3, "medium": 7, "low": 14}
            due_date = datetime.utcnow() + timedelta(days=days.get(priority.value, 7))
        
        # Create task
        task = Task(
            task_id=f"task_{uuid4().hex[:12]}",
            title=payload.get("description_ar", "مهمة زراعية"),
            description=payload.get("reason_ar", ""),
            field_id=payload.get("field_id", ""),
            crop_type=payload.get("crop_type", ""),
            priority=priority,
            status=TaskStatus.PENDING,
            action_type=payload.get("action", ""),
            due_date=due_date,
            created_at=datetime.utcnow(),
            tenant_id=event_data.get("tenant_id", "default"),
            source_event_id=event_data.get("event_id"),
            proverb_reference=payload.get("proverb_reference")
        )
        
        self.store.create(task)
        
        # Update metrics
        TASKS_PENDING.labels(tenant_id=task.tenant_id, priority=priority.value).inc()
        
        # Publish task created event
        await self._publish_task_created(task, event_data.get("correlation_id"))
        
        logger.info("task_created", task_id=task.task_id, field_id=task.field_id, priority=priority.value)
    
    async def _publish_task_created(self, task: Task, correlation_id: str = None):
        event = create_event(
            event_type=EventTypes.TASK_CREATED,
            payload={
                "task": task.to_dict(),
                "requires_immediate_attention": task.priority == TaskPriority.URGENT
            },
            tenant_id=task.tenant_id,
            correlation_id=correlation_id
        )
        
        await self.js.publish(
            subject=EventTypes.TASK_CREATED,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.TASK_CREATED, tenant_id=task.tenant_id).inc()
        event_logger.published(EventTypes.TASK_CREATED, event_id=event["event_id"])
    
    async def _publish_task_assigned(self, task: Task):
        event = create_event(
            event_type=EventTypes.TASK_ASSIGNED,
            payload={
                "task_id": task.task_id,
                "assignee_id": task.assignee_id,
                "assignee_name": task.assignee_name,
                "field_id": task.field_id,
                "due_date": task.due_date.isoformat()
            },
            tenant_id=task.tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.TASK_ASSIGNED,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.TASK_ASSIGNED, tenant_id=task.tenant_id).inc()
    
    async def _publish_task_completed(self, task: Task):
        event = create_event(
            event_type=EventTypes.TASK_COMPLETED,
            payload={
                "task_id": task.task_id,
                "completed_by": task.assignee_id,
                "completed_at": task.completed_at.isoformat(),
                "notes": task.completion_notes,
                "field_id": task.field_id
            },
            tenant_id=task.tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.TASK_COMPLETED,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.TASK_COMPLETED, tenant_id=task.tenant_id).inc()
    
    async def _publish_task_overdue(self, task: Task):
        event = create_event(
            event_type=EventTypes.TASK_OVERDUE,
            payload={
                "task_id": task.task_id,
                "title": task.title,
                "field_id": task.field_id,
                "due_date": task.due_date.isoformat(),
                "overdue_hours": (datetime.utcnow() - task.due_date).total_seconds() / 3600,
                "assignee_id": task.assignee_id
            },
            tenant_id=task.tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.TASK_OVERDUE,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.TASK_OVERDUE, tenant_id=task.tenant_id).inc()
    
    async def _check_overdue_tasks(self):
        """Check for overdue tasks periodically"""
        while self.running:
            try:
                overdue = self.store.list_overdue()
                for task in overdue:
                    if task.status != TaskStatus.OVERDUE:
                        task.status = TaskStatus.OVERDUE
                        self.store.update(task)
                        await self._publish_task_overdue(task)
                        logger.warning("task_overdue", task_id=task.task_id)
            except Exception as e:
                logger.error("overdue_check_failed", error=str(e))
            
            await asyncio.sleep(300)  # Check every 5 minutes
    
    async def assign_task(self, task_id: str, assignee_id: str, assignee_name: str) -> Task:
        task = self.store.get(task_id)
        if not task:
            raise ValueError("Task not found")
        
        task.assignee_id = assignee_id
        task.assignee_name = assignee_name
        task.assigned_at = datetime.utcnow()
        task.status = TaskStatus.ASSIGNED
        
        self.store.update(task)
        await self._publish_task_assigned(task)
        
        TASKS_PENDING.labels(tenant_id=task.tenant_id, priority=task.priority.value).dec()
        
        return task
    
    async def complete_task(self, task_id: str, notes: str = None) -> Task:
        task = self.store.get(task_id)
        if not task:
            raise ValueError("Task not found")
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.completion_notes = notes
        
        self.store.update(task)
        await self._publish_task_completed(task)
        
        return task
    
    async def stop(self):
        self.running = False
        if self.nc:
            await self.nc.close()


task_service = TaskService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", layer=SERVICE_LAYER)
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await task_service.connect()
    await task_service.start()
    logger.info("service_started")
    yield
    await task_service.stop()


app = FastAPI(title="Tasks Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    return {"status": "ready" if task_service.nc and task_service.nc.is_connected else "not_ready"}


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response
    return Response(content=get_metrics(), media_type=get_metrics_content_type())


@app.get("/api/tasks")
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    field_id: Optional[str] = None,
    tenant_id: str = "default"
):
    tasks = list(task_service.store.tasks.values())
    
    if status:
        tasks = [t for t in tasks if t.status.value == status]
    if priority:
        tasks = [t for t in tasks if t.priority.value == priority]
    if field_id:
        tasks = [t for t in tasks if t.field_id == field_id]
    tasks = [t for t in tasks if t.tenant_id == tenant_id]
    
    # Sort by priority and due date
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    tasks.sort(key=lambda t: (priority_order.get(t.priority.value, 4), t.due_date))
    
    return {"tasks": [t.to_dict() for t in tasks]}


@app.get("/api/tasks/stats")
async def get_stats(tenant_id: str = "default"):
    return task_service.store.get_stats(tenant_id)


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    task = task_service.store.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task.to_dict()


class AssignTaskRequest(BaseModel):
    assignee_id: str
    assignee_name: str


@app.post("/api/tasks/{task_id}/assign")
async def assign_task(task_id: str, request: AssignTaskRequest):
    try:
        task = await task_service.assign_task(task_id, request.assignee_id, request.assignee_name)
        return {"message": "Task assigned", "task": task.to_dict()}
    except ValueError as e:
        raise HTTPException(404, str(e))


class CompleteTaskRequest(BaseModel):
    notes: Optional[str] = None


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: str, request: CompleteTaskRequest):
    try:
        task = await task_service.complete_task(task_id, request.notes)
        return {"message": "Task completed", "task": task.to_dict()}
    except ValueError as e:
        raise HTTPException(404, str(e))


class CreateTaskRequest(BaseModel):
    title: str
    description: str
    field_id: str
    crop_type: str
    priority: str = "medium"
    action_type: str
    due_days: int = 7
    tenant_id: str = "default"


@app.post("/api/tasks")
async def create_task(request: CreateTaskRequest):
    """Manually create a task"""
    priority = TaskPriority(request.priority) if request.priority in [p.value for p in TaskPriority] else TaskPriority.MEDIUM
    
    task = Task(
        task_id=f"task_{uuid4().hex[:12]}",
        title=request.title,
        description=request.description,
        field_id=request.field_id,
        crop_type=request.crop_type,
        priority=priority,
        status=TaskStatus.PENDING,
        action_type=request.action_type,
        due_date=datetime.utcnow() + timedelta(days=request.due_days),
        created_at=datetime.utcnow(),
        tenant_id=request.tenant_id
    )
    
    task_service.store.create(task)
    await task_service._publish_task_created(task)
    
    return {"message": "Task created", "task": task.to_dict()}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("TASKS_PORT", "8089")), reload=os.getenv("ENV") == "development")
