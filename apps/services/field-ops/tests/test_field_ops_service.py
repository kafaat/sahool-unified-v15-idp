"""
Comprehensive Tests for Field Operations Service
اختبارات شاملة لخدمة عمليات الحقول
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app, _fields, _operations


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_field_data():
    """Sample field data for testing"""
    return {
        "tenant_id": "test_tenant",
        "name": "Test Field",
        "name_ar": "حقل اختبار",
        "area_hectares": 10.5,
        "crop_type": "wheat",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        },
        "metadata": {"soil_type": "loamy"},
    }


@pytest.fixture
def sample_operation_data():
    """Sample operation data for testing"""
    return {
        "tenant_id": "test_tenant",
        "field_id": "field_123",
        "operation_type": "irrigation",
        "scheduled_date": "2025-12-30T10:00:00Z",
        "notes": "Regular irrigation",
        "metadata": {"water_amount": "20mm"},
    }


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client):
        """Test /healthz endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "field_ops"

    def test_readiness_check(self, client):
        """Test /readyz endpoint"""
        response = client.get("/readyz")
        assert response.status_code == 200
        assert "status" in response.json()


class TestFieldManagement:
    """Test field management endpoints"""

    def test_create_field(self, client, sample_field_data):
        """Test creating a new field"""
        response = client.post("/fields", json=sample_field_data)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Field"
        assert data["area_hectares"] == 10.5
        assert data["tenant_id"] == "test_tenant"

    def test_get_field(self, client, sample_field_data):
        """Test getting field by ID"""
        # Create field first
        create_response = client.post("/fields", json=sample_field_data)
        field_id = create_response.json()["id"]

        # Get field
        response = client.get(f"/fields/{field_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == field_id
        assert data["name"] == "Test Field"

    def test_get_nonexistent_field(self, client):
        """Test getting non-existent field"""
        response = client.get("/fields/nonexistent_id")
        assert response.status_code == 404

    def test_list_fields(self, client, sample_field_data):
        """Test listing fields for a tenant"""
        # Create some fields
        client.post("/fields", json=sample_field_data)
        client.post("/fields", json={**sample_field_data, "name": "Field 2"})

        # List fields
        response = client.get("/fields", params={"tenant_id": "test_tenant"})

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 2

    def test_list_fields_with_pagination(self, client, sample_field_data):
        """Test field listing with pagination"""
        response = client.get(
            "/fields", params={"tenant_id": "test_tenant", "skip": 0, "limit": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert "skip" in data
        assert "limit" in data

    def test_update_field(self, client, sample_field_data):
        """Test updating field information"""
        # Create field
        create_response = client.post("/fields", json=sample_field_data)
        field_id = create_response.json()["id"]

        # Update field
        update_data = {
            "name": "Updated Field",
            "area_hectares": 15.0,
            "crop_type": "corn",
        }

        response = client.put(f"/fields/{field_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Field"
        assert data["area_hectares"] == 15.0
        assert data["crop_type"] == "corn"

    def test_delete_field(self, client, sample_field_data):
        """Test deleting a field"""
        # Create field
        create_response = client.post("/fields", json=sample_field_data)
        field_id = create_response.json()["id"]

        # Delete field
        response = client.delete(f"/fields/{field_id}")

        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

        # Verify field is deleted
        get_response = client.get(f"/fields/{field_id}")
        assert get_response.status_code == 404


class TestOperationsManagement:
    """Test operations management endpoints"""

    def test_create_operation(self, client, sample_operation_data):
        """Test creating a new operation"""
        response = client.post("/operations", json=sample_operation_data)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["operation_type"] == "irrigation"
        assert data["status"] == "scheduled"

    def test_get_operation(self, client, sample_operation_data):
        """Test getting operation by ID"""
        # Create operation
        create_response = client.post("/operations", json=sample_operation_data)
        operation_id = create_response.json()["id"]

        # Get operation
        response = client.get(f"/operations/{operation_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == operation_id

    def test_get_nonexistent_operation(self, client):
        """Test getting non-existent operation"""
        response = client.get("/operations/nonexistent_id")
        assert response.status_code == 404

    def test_list_operations(self, client, sample_field_data, sample_operation_data):
        """Test listing operations for a field"""
        # Create field
        field_response = client.post("/fields", json=sample_field_data)
        field_id = field_response.json()["id"]

        # Create operations
        op_data = {**sample_operation_data, "field_id": field_id}
        client.post("/operations", json=op_data)
        client.post("/operations", json={**op_data, "operation_type": "fertilizing"})

        # List operations
        response = client.get("/operations", params={"field_id": field_id})

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 2

    def test_list_operations_with_status_filter(
        self, client, sample_field_data, sample_operation_data
    ):
        """Test listing operations with status filter"""
        # Create field
        field_response = client.post("/fields", json=sample_field_data)
        field_id = field_response.json()["id"]

        # Create operation
        op_data = {**sample_operation_data, "field_id": field_id}
        client.post("/operations", json=op_data)

        # List scheduled operations
        response = client.get(
            "/operations", params={"field_id": field_id, "status": "scheduled"}
        )

        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "scheduled" for item in data["items"])

    def test_complete_operation(self, client, sample_operation_data):
        """Test marking operation as completed"""
        # Create operation
        create_response = client.post("/operations", json=sample_operation_data)
        operation_id = create_response.json()["id"]

        # Complete operation
        response = client.post(f"/operations/{operation_id}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_date"] is not None

    def test_complete_nonexistent_operation(self, client):
        """Test completing non-existent operation"""
        response = client.post("/operations/nonexistent_id/complete")
        assert response.status_code == 404


class TestTenantStatistics:
    """Test tenant statistics endpoints"""

    def test_get_tenant_stats(self, client, sample_field_data, sample_operation_data):
        """Test getting tenant statistics"""
        tenant_id = "stats_test_tenant"

        # Create some fields
        field_data = {**sample_field_data, "tenant_id": tenant_id}
        field1 = client.post("/fields", json=field_data).json()
        field2 = client.post(
            "/fields", json={**field_data, "name": "Field 2", "area_hectares": 8.5}
        ).json()

        # Create some operations
        op_data = {
            **sample_operation_data,
            "tenant_id": tenant_id,
            "field_id": field1["id"],
        }
        client.post("/operations", json=op_data)
        client.post("/operations", json={**op_data, "operation_type": "harvesting"})

        # Get stats
        response = client.get(f"/stats/tenant/{tenant_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == tenant_id
        assert data["fields_count"] >= 2
        assert data["total_area_hectares"] >= 19.0  # 10.5 + 8.5
        assert "operations" in data
        assert data["operations"]["total"] >= 2

    def test_tenant_stats_structure(self, client):
        """Test tenant stats response structure"""
        response = client.get("/stats/tenant/any_tenant")

        assert response.status_code == 200
        data = response.json()
        assert "tenant_id" in data
        assert "fields_count" in data
        assert "total_area_hectares" in data
        assert "operations" in data
        assert "total" in data["operations"]
        assert "scheduled" in data["operations"]
        assert "completed" in data["operations"]


class TestValidation:
    """Test input validation"""

    def test_create_field_invalid_area(self, client, sample_field_data):
        """Test field creation with invalid area"""
        invalid_data = {**sample_field_data, "area_hectares": -5.0}

        response = client.post("/fields", json=invalid_data)
        assert response.status_code == 422

    def test_create_field_missing_required_fields(self, client):
        """Test field creation with missing required fields"""
        invalid_data = {
            "tenant_id": "test",
            "name": "Test",
            # Missing area_hectares
        }

        response = client.post("/fields", json=invalid_data)
        assert response.status_code == 422


# Integration test for complete workflow
class TestCompleteWorkflow:
    """Integration tests for complete workflow"""

    def test_complete_field_operations_workflow(self, client, sample_field_data):
        """Test complete workflow from field creation to operation completion"""
        tenant_id = "workflow_test_tenant"
        field_data = {**sample_field_data, "tenant_id": tenant_id}

        # Step 1: Create field
        field_response = client.post("/fields", json=field_data)
        assert field_response.status_code == 200
        field_id = field_response.json()["id"]

        # Step 2: Create operation
        op_data = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "operation_type": "planting",
            "scheduled_date": "2025-12-30T08:00:00Z",
            "notes": "Wheat planting season",
        }

        op_response = client.post("/operations", json=op_data)
        assert op_response.status_code == 200
        operation_id = op_response.json()["id"]

        # Step 3: List operations for field
        list_response = client.get("/operations", params={"field_id": field_id})
        assert list_response.status_code == 200
        assert list_response.json()["total"] >= 1

        # Step 4: Complete operation
        complete_response = client.post(f"/operations/{operation_id}/complete")
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "completed"

        # Step 5: Get tenant stats
        stats_response = client.get(f"/stats/tenant/{tenant_id}")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["fields_count"] >= 1
        assert stats["operations"]["completed"] >= 1

        # Step 6: Update field info
        update_response = client.put(
            f"/fields/{field_id}", json={"crop_type": "wheat_updated"}
        )
        assert update_response.status_code == 200
