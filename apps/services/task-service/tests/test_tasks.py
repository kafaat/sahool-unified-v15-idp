"""
SAHOOL Task Service - Unit Tests
اختبارات خدمة إدارة المهام

Uses an in-memory SQLite database and overrides FastAPI dependencies
so tests run without PostgreSQL, NATS or Redis.
"""

import os
import sys
import uuid
from datetime import UTC, datetime, timedelta

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import AFTER conftest has injected the fake 'database' module
from src.database import get_db
from src.main import app

# Re-import the Base that models actually use (the one from conftest)
import database as _db_mod

Base = _db_mod.Base

# ── Test tenant ID (UUID format required by TenantContextMiddleware) ──
TEST_TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"X-Tenant-ID": TEST_TENANT_ID}

# ── In-memory SQLite engine shared across a single test session ──
_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSession = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def _override_get_db():
    db = _TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


# Create all tables once for the module
Base.metadata.create_all(bind=_engine)


# ── Fixtures ──


@pytest.fixture(autouse=True)
def _reset_tables():
    """Recreate tables before every test so each test is isolated."""
    Base.metadata.drop_all(bind=_engine)
    Base.metadata.create_all(bind=_engine)
    yield


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def sample_task():
    """Sample task data for testing"""
    tomorrow = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    return {
        "title": "Test Task",
        "title_ar": "مهمة اختبار",
        "description": "Test description",
        "description_ar": "وصف الاختبار",
        "task_type": "irrigation",
        "priority": "high",
        "field_id": "field_test",
        "assigned_to": "user_test",
        "due_date": tomorrow,
        "scheduled_time": "08:00",
        "estimated_duration_minutes": 60,
    }


# ── Health Endpoint ──


class TestHealthEndpoint:
    """Health check endpoint tests"""

    def test_health_check(self, client):
        """Test health check returns ok status"""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "sahool-task-service" in data["service"]


# ── Task Listing ──


class TestTaskList:
    """Task listing tests"""

    def test_list_tasks(self, client):
        """Test listing all tasks"""
        response = client.get("/api/v1/tasks", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert isinstance(data["tasks"], list)

    def test_list_tasks_with_status_filter(self, client, sample_task):
        """Test filtering tasks by status"""
        client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        response = client.get("/api/v1/tasks?status=pending", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "pending"

    def test_list_tasks_with_type_filter(self, client, sample_task):
        """Test filtering tasks by type"""
        client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        response = client.get("/api/v1/tasks?task_type=irrigation", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["task_type"] == "irrigation"

    def test_list_tasks_with_priority_filter(self, client, sample_task):
        """Test filtering tasks by priority"""
        client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        response = client.get("/api/v1/tasks?priority=high", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["priority"] == "high"

    def test_list_tasks_pagination(self, client):
        """Test task list pagination"""
        response = client.get("/api/v1/tasks?limit=2&offset=0", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 2
        assert data["offset"] == 0


# ── Today / Upcoming ──


class TestTodayTasks:
    """Today's tasks tests"""

    def test_get_today_tasks(self, client):
        """Test getting today's tasks"""
        response = client.get("/api/v1/tasks/today", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "count" in data


class TestUpcomingTasks:
    """Upcoming tasks tests"""

    def test_get_upcoming_tasks(self, client):
        """Test getting upcoming tasks"""
        response = client.get("/api/v1/tasks/upcoming?days=7", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "count" in data
        assert data["days"] == 7

    def test_get_upcoming_tasks_custom_days(self, client):
        """Test getting upcoming tasks with custom days"""
        response = client.get("/api/v1/tasks/upcoming?days=14", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["days"] == 14


# ── Stats ──


class TestTaskStats:
    """Task statistics tests"""

    def test_get_stats(self, client):
        """Test getting task statistics"""
        response = client.get("/api/v1/tasks/stats", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "pending" in data
        assert "in_progress" in data
        assert "completed" in data
        assert "overdue" in data
        assert "week_progress" in data
        assert "completed" in data["week_progress"]
        assert "total" in data["week_progress"]
        assert "percentage" in data["week_progress"]


# ── CRUD ──


class TestTaskCRUD:
    """Task CRUD operations tests"""

    def test_create_task(self, client, sample_task):
        """Test creating new task"""
        response = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_task["title"]
        assert data["task_type"] == sample_task["task_type"]
        assert data["priority"] == sample_task["priority"]
        assert data["status"] == "pending"
        assert data["task_id"] is not None

    def test_get_task_by_id(self, client, sample_task):
        """Test getting task by ID"""
        create_resp = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_resp.json()["task_id"]

        response = client.get(f"/api/v1/tasks/{task_id}", headers=HEADERS)
        assert response.status_code == 200
        assert response.json()["task_id"] == task_id


    def test_get_task_not_found(self, client):
        """Test getting non-existent task"""
        response = client.get("/api/v1/tasks/nonexistent_id", headers=HEADERS)
        assert response.status_code == 404

    def test_update_task(self, client, sample_task):
        """Test updating task"""
        create_resp = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_resp.json()["task_id"]

        update_data = {
            "title": "Updated Title",
            "priority": "urgent",
        }
        response = client.put(f"/api/v1/tasks/{task_id}", json=update_data, headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "urgent"


# ── Workflow ──


class TestTaskWorkflow:
    """Task workflow tests"""

    def test_start_task(self, client, sample_task):
        """Test starting a task"""
        create_response = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_response.json()["task_id"]

        response = client.post(f"/api/v1/tasks/{task_id}/start", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_complete_task(self, client, sample_task):
        """Test completing a task"""
        create_response = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_response.json()["task_id"]
        client.post(f"/api/v1/tasks/{task_id}/start", headers=HEADERS)

        complete_data = {
            "notes": "Task completed successfully",
            "notes_ar": "تم إنجاز المهمة بنجاح",
            "actual_duration_minutes": 45,
        }
        response = client.post(f"/api/v1/tasks/{task_id}/complete", json=complete_data, headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["actual_duration_minutes"] == 45
        assert data["completed_at"] is not None

    def test_cancel_task(self, client, sample_task):
        """Test cancelling a task"""
        create_response = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_response.json()["task_id"]

        response = client.post(
            f"/api/v1/tasks/{task_id}/cancel?reason=Weather%20conditions",
            headers=HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        # cancel_reason is stored in task_metadata, exposed as metadata
        assert data["metadata"]["cancel_reason"] == "Weather conditions"

    def test_start_non_pending_task_fails(self, client, sample_task):
        """Test that starting a non-pending task fails"""
        create_response = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_response.json()["task_id"]
        client.post(f"/api/v1/tasks/{task_id}/start", headers=HEADERS)

        # Try to start again - should fail with 400
        response = client.post(f"/api/v1/tasks/{task_id}/start", headers=HEADERS)
        assert response.status_code == 400


# ── Evidence ──


class TestTaskEvidence:
    """Task evidence tests"""

    def test_add_photo_evidence(self, client, sample_task):
        """Test adding photo evidence to a task"""
        create_resp = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_resp.json()["task_id"]

        response = client.post(
            f"/api/v1/tasks/{task_id}/evidence"
            "?evidence_type=photo"
            "&content=https://example.com/photo.jpg"
            "&lat=15.37"
            "&lon=44.19",
            headers=HEADERS,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "photo"
        assert data["content"] == "https://example.com/photo.jpg"
        assert data["location"]["lat"] == 15.37
        assert data["location"]["lon"] == 44.19

    def test_add_note_evidence(self, client, sample_task):
        """Test adding note evidence to a task"""
        create_resp = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_resp.json()["task_id"]

        response = client.post(
            f"/api/v1/tasks/{task_id}/evidence?evidence_type=note&content=Field%20looks%20healthy",
            headers=HEADERS,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "note"
        assert data["content"] == "Field looks healthy"

    def test_complete_with_photos(self, client, sample_task):
        """Test completing a task with photo URLs"""
        create_response = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_response.json()["task_id"]

        complete_data = {
            "notes": "Done",
            "photo_urls": [
                "https://example.com/photo1.jpg",
                "https://example.com/photo2.jpg",
            ],
        }
        response = client.post(f"/api/v1/tasks/{task_id}/complete", json=complete_data, headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert len(data["evidence"]) == 2


# ── Delete ──


class TestTaskDelete:
    """Task deletion tests"""

    def test_delete_task(self, client, sample_task):
        """Test deleting a task"""
        create_response = client.post("/api/v1/tasks", json=sample_task, headers=HEADERS)
        task_id = create_response.json()["task_id"]

        response = client.delete(f"/api/v1/tasks/{task_id}", headers=HEADERS)
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/tasks/{task_id}", headers=HEADERS)
        assert get_response.status_code == 404


# ── Task Types ──


class TestTaskTypes:
    """Task type enum tests"""

    def test_all_task_types_valid(self, client):
        """Test that all task types are accepted"""
        types = [
            "irrigation",
            "fertilization",
            "spraying",
            "scouting",
            "maintenance",
            "sampling",
            "harvest",
            "planting",
            "other",
        ]
        for task_type in types:
            data = {
                "title": f"Test {task_type}",
                "task_type": task_type,
            }
            response = client.post("/api/v1/tasks", json=data, headers=HEADERS)
            assert response.status_code == 201, f"Failed for type: {task_type}"


# ── Task Priorities ──


class TestTaskPriorities:
    """Task priority enum tests"""

    def test_all_priorities_valid(self, client):
        """Test that all priority levels are accepted"""
        priorities = ["low", "medium", "high", "urgent"]
        for priority in priorities:
            data = {
                "title": f"Test {priority}",
                "priority": priority,
            }
            response = client.post("/api/v1/tasks", json=data, headers=HEADERS)
            assert response.status_code == 201, f"Failed for priority: {priority}"
