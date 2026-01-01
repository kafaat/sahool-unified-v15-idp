"""
SAHOOL Task Service - Unit Tests
اختبارات خدمة إدارة المهام
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app, tasks_db, TaskType, TaskPriority, TaskStatus


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_task():
    """Sample task data for testing"""
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
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


class TestHealthEndpoint:
    """Health check endpoint tests"""

    def test_health_check(self, client):
        """Test health check returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "sahool-task-service" in data["service"]


class TestTaskList:
    """Task listing tests"""

    def test_list_tasks(self, client):
        """Test listing all tasks"""
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert isinstance(data["tasks"], list)

    def test_list_tasks_with_status_filter(self, client):
        """Test filtering tasks by status"""
        response = client.get("/api/v1/tasks?status=pending")
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "pending"

    def test_list_tasks_with_type_filter(self, client):
        """Test filtering tasks by type"""
        response = client.get("/api/v1/tasks?task_type=irrigation")
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["task_type"] == "irrigation"

    def test_list_tasks_with_priority_filter(self, client):
        """Test filtering tasks by priority"""
        response = client.get("/api/v1/tasks?priority=high")
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["priority"] == "high"

    def test_list_tasks_pagination(self, client):
        """Test task list pagination"""
        response = client.get("/api/v1/tasks?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 2
        assert data["offset"] == 0


class TestTodayTasks:
    """Today's tasks tests"""

    def test_get_today_tasks(self, client):
        """Test getting today's tasks"""
        response = client.get("/api/v1/tasks/today")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "count" in data


class TestUpcomingTasks:
    """Upcoming tasks tests"""

    def test_get_upcoming_tasks(self, client):
        """Test getting upcoming tasks"""
        response = client.get("/api/v1/tasks/upcoming?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "count" in data
        assert data["days"] == 7

    def test_get_upcoming_tasks_custom_days(self, client):
        """Test getting upcoming tasks with custom days"""
        response = client.get("/api/v1/tasks/upcoming?days=14")
        assert response.status_code == 200
        data = response.json()
        assert data["days"] == 14


class TestTaskStats:
    """Task statistics tests"""

    def test_get_stats(self, client):
        """Test getting task statistics"""
        response = client.get("/api/v1/tasks/stats")
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


class TestTaskCRUD:
    """Task CRUD operations tests"""

    def test_create_task(self, client, sample_task):
        """Test creating new task"""
        response = client.post("/api/v1/tasks", json=sample_task)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_task["title"]
        assert data["task_type"] == sample_task["task_type"]
        assert data["priority"] == sample_task["priority"]
        assert data["status"] == "pending"
        assert data["task_id"] is not None

    def test_get_task_by_id(self, client):
        """Test getting task by ID"""
        response = client.get("/api/v1/tasks/task_001")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task_001"

    def test_get_task_not_found(self, client):
        """Test getting non-existent task"""
        response = client.get("/api/v1/tasks/nonexistent_id")
        assert response.status_code == 404

    def test_update_task(self, client):
        """Test updating task"""
        update_data = {
            "title": "Updated Title",
            "priority": "urgent",
        }
        response = client.put("/api/v1/tasks/task_001", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "urgent"


class TestTaskWorkflow:
    """Task workflow tests"""

    def test_start_task(self, client, sample_task):
        """Test starting a task"""
        # Create a new task first
        create_response = client.post("/api/v1/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]

        # Start the task
        response = client.post(f"/api/v1/tasks/{task_id}/start")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_complete_task(self, client, sample_task):
        """Test completing a task"""
        # Create and start a task
        create_response = client.post("/api/v1/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]
        client.post(f"/api/v1/tasks/{task_id}/start")

        # Complete the task
        complete_data = {
            "notes": "Task completed successfully",
            "notes_ar": "تم إنجاز المهمة بنجاح",
            "actual_duration_minutes": 45,
        }
        response = client.post(f"/api/v1/tasks/{task_id}/complete", json=complete_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["actual_duration_minutes"] == 45
        assert data["completed_at"] is not None

    def test_cancel_task(self, client, sample_task):
        """Test cancelling a task"""
        # Create a task
        create_response = client.post("/api/v1/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]

        # Cancel the task
        response = client.post(
            f"/api/v1/tasks/{task_id}/cancel?reason=Weather%20conditions"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["metadata"]["cancel_reason"] == "Weather conditions"

    def test_start_non_pending_task_fails(self, client, sample_task):
        """Test that starting a non-pending task fails"""
        # Create and start a task
        create_response = client.post("/api/v1/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]
        client.post(f"/api/v1/tasks/{task_id}/start")

        # Try to start again
        response = client.post(f"/api/v1/tasks/{task_id}/start")
        assert response.status_code == 400


class TestTaskEvidence:
    """Task evidence tests"""

    def test_add_photo_evidence(self, client):
        """Test adding photo evidence to a task"""
        response = client.post(
            "/api/v1/tasks/task_001/evidence"
            "?evidence_type=photo"
            "&content=https://example.com/photo.jpg"
            "&lat=15.37"
            "&lon=44.19"
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "photo"
        assert data["content"] == "https://example.com/photo.jpg"
        assert data["location"]["lat"] == 15.37
        assert data["location"]["lon"] == 44.19

    def test_add_note_evidence(self, client):
        """Test adding note evidence to a task"""
        response = client.post(
            "/api/v1/tasks/task_001/evidence"
            "?evidence_type=note"
            "&content=Field%20looks%20healthy"
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "note"
        assert data["content"] == "Field looks healthy"

    def test_complete_with_photos(self, client, sample_task):
        """Test completing a task with photo URLs"""
        # Create a task
        create_response = client.post("/api/v1/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]

        # Complete with photos
        complete_data = {
            "notes": "Done",
            "photo_urls": [
                "https://example.com/photo1.jpg",
                "https://example.com/photo2.jpg",
            ],
        }
        response = client.post(f"/api/v1/tasks/{task_id}/complete", json=complete_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["evidence"]) == 2


class TestTaskDelete:
    """Task deletion tests"""

    def test_delete_task(self, client, sample_task):
        """Test deleting a task"""
        # Create a task
        create_response = client.post("/api/v1/tasks", json=sample_task)
        task_id = create_response.json()["task_id"]

        # Delete the task
        response = client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 404


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
            response = client.post("/api/v1/tasks", json=data)
            assert response.status_code == 201, f"Failed for type: {task_type}"


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
            response = client.post("/api/v1/tasks", json=data)
            assert response.status_code == 201, f"Failed for priority: {priority}"
