"""
Tasks Service - خدمة المهام
Layer 4: Execution Service

The "Hands" that creates and manages farmer tasks.

Responsibilities:
1. Subscribe to recommendations from Layer 3
2. Create actionable tasks
3. Track task status and completion
4. Manage task assignments

Events Consumed:
- crop.action.recommended
- advisor.recommendation.created

Events Produced:
- task.created
- task.assigned
- task.completed
- task.overdue
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import nats

sys.path.insert(0, '/app')
from shared.events.base_event import create_event, EventTypes, generate_id  # noqa: E402
from shared.utils.logging import configure_logging, get_logger, EventLogger  # noqa: E402
from shared.metrics import EVENTS_PUBLISHED, EVENTS_CONSUMED, TASKS_PENDING, init_service_info  # noqa: E402

configure_logging(service_name="tasks-service")
logger = get_logger(__name__)
event_logger = EventLogger("tasks-service")

SERVICE_NAME = "tasks-service"
SERVICE_LAYER = "execution"
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")


# ============================================
# Domain Models
# ============================================

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
    """A farmer task"""
    id: str
    tenant_id: str
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    field_id: str
    crop_type: Optional[str]
    action_type: str
    priority: TaskPriority
    status: TaskStatus
    due_date: str
    created_at: str
    source_event_id: str
    proverb_reference: Optional[str]
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    assigned_at: Optional[str] = None
    completed_at: Optional[str] = None
    completion_notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "title": {"ar": self.title_ar, "en": self.title_en},
            "description": {"ar": self.description_ar, "en": self.description_en},
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "action_type": self.action_type,
            "priority": self.priority.value,
            "status": self.status.value,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "source_event_id": self.source_event_id,
            "proverb_reference": self.proverb_reference,
            "assignee": {
                "id": self.assignee_id,
                "name": self.assignee_name
            } if self.assignee_id else None,
            "assigned_at": self.assigned_at,
            "completed_at": self.completed_at,
            "completion_notes": self.completion_notes,
            "metadata": self.metadata
        }


# ============================================
# Task Manager
# ============================================

class TaskManager:
    """Manages task lifecycle"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
    
    def create_task_from_recommendation(self, event: Dict) -> Task:
        """Create task from crop.action.recommended event"""
        payload = event.get("payload", {})
        rec = payload.get("recommendation", {})
        details = rec.get("details", {})
        
        # Build title and description from recommendation
        reason = rec.get("reason", {})
        
        task = Task(
            id=f"task_{generate_id()}",
            tenant_id=event.get("tenant_id", "default"),
            title_ar=reason.get("ar", "مهمة جديدة"),
            title_en=reason.get("en", "New task"),
            description_ar=reason.get("ar", ""),
            description_en=reason.get("en", ""),
            field_id=details.get("field_id", "unknown"),
            crop_type=details.get("crop_type"),
            action_type=rec.get("action_type", "general"),
            priority=TaskPriority(rec.get("priority", "medium")),
            status=TaskStatus.PENDING,
            due_date=rec.get("deadline", (datetime.utcnow() + timedelta(days=7)).isoformat()),
            created_at=datetime.utcnow().isoformat(),
            source_event_id=event.get("event_id", ""),
            proverb_reference=rec.get("proverb_reference"),
            metadata={
                "source_signal": rec.get("source_signal"),
                "planting_id": details.get("planting_id")
            }
        )
        
        self.tasks[task.id] = task
        TASKS_PENDING.labels(tenant_id=task.tenant_id, priority=task.priority.value).inc()
        
        logger.info("task_created", task_id=task.id, action=task.action_type, priority=task.priority.value)
        return task
    
    def assign_task(self, task_id: str, assignee_id: str, assignee_name: str) -> Optional[Task]:
        """Assign task to user"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        task.assignee_id = assignee_id
        task.assignee_name = assignee_name
        task.assigned_at = datetime.utcnow().isoformat()
        task.status = TaskStatus.ASSIGNED
        
        logger.info("task_assigned", task_id=task_id, assignee=assignee_id)
        return task
    
    def complete_task(self, task_id: str, completed_by: str, notes: Optional[str] = None) -> Optional[Task]:
        """Mark task as completed"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow().isoformat()
        task.completion_notes = notes
        
        TASKS_PENDING.labels(tenant_id=task.tenant_id, priority=task.priority.value).dec()
        
        logger.info("task_completed", task_id=task_id, completed_by=completed_by)
        return task
    
    def get_pending_tasks(self, tenant_id: Optional[str] = None) -> List[Task]:
        """Get pending tasks"""
        tasks = [t for t in self.tasks.values() if t.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED]]
        if tenant_id:
            tasks = [t for t in tasks if t.tenant_id == tenant_id]
        return sorted(tasks, key=lambda t: (0 if t.priority == TaskPriority.URGENT else 1 if t.priority == TaskPriority.HIGH else 2, t.due_date))
    
    def check_overdue_tasks(self) -> List[Task]:
        """Find overdue tasks"""
        now = datetime.utcnow()
        overdue = []
        for task in self.tasks.values():
            if task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED]:
                due = datetime.fromisoformat(task.due_date.replace("Z", ""))
                if due < now:
                    task.status = TaskStatus.OVERDUE
                    overdue.append(task)
        return overdue


# ============================================
# Tasks Service
# ============================================

class TasksService:
    """Main tasks service"""
    
    def __init__(self):
        self.nc = None
        self.js = None
        self.manager = TaskManager()
        self.running = False
    
    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("nats_connected")
    
    async def start(self):
        """Start event processing"""
        self.running = True
        
        # Subscribe to Layer 3 events
        subjects = ["crop.action.recommended", "advisor.recommendation.created"]
        
        for subject in subjects:
            try:
                sub = await self.js.pull_subscribe(
                    subject=subject,
                    durable=f"tasks-{subject.replace('.', '-')}",
                    stream="SAHOOL"
                )
                asyncio.create_task(self._process_subscription(sub, subject))
                logger.info("subscribed", subject=subject)
            except Exception as e:
                logger.warning("subscription_failed", subject=subject, error=str(e))
        
        # Start overdue checker
        asyncio.create_task(self._check_overdue_loop())
    
    async def _process_subscription(self, sub, subject: str):
        while self.running:
            try:
                messages = await sub.fetch(batch=10, timeout=1)
                for msg in messages:
                    await self._handle_message(msg, subject)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("subscription_error", subject=subject, error=str(e))
                await asyncio.sleep(1)
    
    async def _handle_message(self, msg, subject: str):
        try:
            event = json.loads(msg.data.decode())
            event_type = event.get("event_type", subject)
            
            EVENTS_CONSUMED.labels(service=SERVICE_NAME, event_type=event_type, tenant_id=event.get("tenant_id", "default")).inc()
            event_logger.consumed(event_type)
            
            # Create task from recommendation
            task = self.manager.create_task_from_recommendation(event)
            
            # Publish task.created event
            await self._publish_task_created(task, event)
            
            await msg.ack()
            
        except Exception as e:
            logger.error("message_handling_failed", error=str(e))
            await msg.nak()
    
    async def _publish_task_created(self, task: Task, source_event: Dict):
        """Publish task.created event"""
        event = create_event(
            event_type=EventTypes.TASK_CREATED,
            payload={"task": task.to_dict()},
            tenant_id=task.tenant_id,
            correlation_id=source_event.get("correlation_id"),
            causation_id=source_event.get("event_id")
        )
        
        await self.js.publish(subject=EventTypes.TASK_CREATED, payload=json.dumps(event).encode())
        event_logger.published(EventTypes.TASK_CREATED, task_id=task.id)
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.TASK_CREATED, tenant_id=task.tenant_id).inc()
    
    async def _publish_task_assigned(self, task: Task):
        event = create_event(
            event_type=EventTypes.TASK_ASSIGNED,
            payload={"task": task.to_dict()},
            tenant_id=task.tenant_id
        )
        await self.js.publish(subject=EventTypes.TASK_ASSIGNED, payload=json.dumps(event).encode())
        event_logger.published(EventTypes.TASK_ASSIGNED, task_id=task.id)
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.TASK_ASSIGNED, tenant_id=task.tenant_id).inc()
    
    async def _publish_task_completed(self, task: Task):
        event = create_event(
            event_type=EventTypes.TASK_COMPLETED,
            payload={"task": task.to_dict()},
            tenant_id=task.tenant_id
        )
        await self.js.publish(subject=EventTypes.TASK_COMPLETED, payload=json.dumps(event).encode())
        event_logger.published(EventTypes.TASK_COMPLETED, task_id=task.id)
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.TASK_COMPLETED, tenant_id=task.tenant_id).inc()
    
    async def _publish_task_overdue(self, task: Task):
        event = create_event(
            event_type=EventTypes.TASK_OVERDUE,
            payload={"task": task.to_dict()},
            tenant_id=task.tenant_id
        )
        await self.js.publish(subject=EventTypes.TASK_OVERDUE, payload=json.dumps(event).encode())
        event_logger.published(EventTypes.TASK_OVERDUE, task_id=task.id)
    
    async def _check_overdue_loop(self):
        """Periodically check for overdue tasks"""
        while self.running:
            try:
                overdue = self.manager.check_overdue_tasks()
                for task in overdue:
                    await self._publish_task_overdue(task)
                    logger.warning("task_overdue", task_id=task.id)
            except Exception as e:
                logger.error("overdue_check_failed", error=str(e))
            await asyncio.sleep(3600)  # Check every hour
    
    async def stop(self):
        self.running = False
        if self.nc: await self.nc.close()
        logger.info("service_stopped")


tasks_service = TasksService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", layer=SERVICE_LAYER)
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await tasks_service.connect()
    await tasks_service.start()
    logger.info("service_started")
    yield
    await tasks_service.stop()


app = FastAPI(title="Tasks Service", description="SAHOOL - Task Execution Service (Layer 4)", version="1.0.0", lifespan=lifespan)


# ============================================
# API Endpoints (Layer 4 has public API)
# ============================================

@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}

@app.get("/readyz")
async def ready():
    return {"status": "ready" if tasks_service.nc and tasks_service.nc.is_connected else "not_ready"}

@app.get("/api/tasks")
async def get_tasks(tenant_id: Optional[str] = None, status: Optional[str] = None):
    """Get all tasks"""
    tasks = list(tasks_service.manager.tasks.values())
    if tenant_id:
        tasks = [t for t in tasks if t.tenant_id == tenant_id]
    if status:
        tasks = [t for t in tasks if t.status.value == status]
    return {"tasks": [t.to_dict() for t in tasks]}

@app.get("/api/tasks/pending")
async def get_pending_tasks(tenant_id: Optional[str] = None):
    """Get pending tasks sorted by priority"""
    tasks = tasks_service.manager.get_pending_tasks(tenant_id)
    return {"tasks": [t.to_dict() for t in tasks]}

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    task = tasks_service.manager.tasks.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task.to_dict()


class AssignTaskRequest(BaseModel):
    assignee_id: str
    assignee_name: str

@app.post("/api/tasks/{task_id}/assign")
async def assign_task(task_id: str, request: AssignTaskRequest):
    """Assign task to user"""
    task = tasks_service.manager.assign_task(task_id, request.assignee_id, request.assignee_name)
    if not task:
        raise HTTPException(404, "Task not found")
    await tasks_service._publish_task_assigned(task)
    return task.to_dict()


class CompleteTaskRequest(BaseModel):
    completed_by: str
    notes: Optional[str] = None

@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: str, request: CompleteTaskRequest):
    """Mark task as completed"""
    task = tasks_service.manager.complete_task(task_id, request.completed_by, request.notes)
    if not task:
        raise HTTPException(404, "Task not found")
    await tasks_service._publish_task_completed(task)
    return task.to_dict()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("TASKS_PORT", "8089")), reload=os.getenv("ENV") == "development")
