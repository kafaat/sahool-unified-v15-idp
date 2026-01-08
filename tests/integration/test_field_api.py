"""
SAHOOL Field API Integration Tests
Tests for Field Operations API endpoints
"""

import sys

import pytest

sys.path.insert(0, "kernel/services/field_ops/src")


class TestFieldCRUD:
    """Integration tests for Field CRUD operations"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from main import _fields, app

        # Clear in-memory store before each test
        _fields.clear()

        return TestClient(app)

    def test_create_field(self, client, sample_field_data):
        """Should create a new field"""
        response = client.post("/fields", json=sample_field_data)

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == sample_field_data["name"]
        assert body["area_hectares"] == sample_field_data["area_hectares"]
        assert "id" in body

    def test_create_field_returns_id(self, client, sample_field_data):
        """Created field should have UUID id"""
        response = client.post("/fields", json=sample_field_data)
        body = response.json()

        assert "id" in body
        assert len(body["id"]) == 36  # UUID length

    def test_get_field_by_id(self, client, sample_field_data):
        """Should retrieve field by ID"""
        # Create first
        create_response = client.post("/fields", json=sample_field_data)
        field_id = create_response.json()["id"]

        # Get by ID
        response = client.get(f"/fields/{field_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == field_id
        assert body["name"] == sample_field_data["name"]

    def test_get_nonexistent_field_returns_404(self, client):
        """Should return 404 for non-existent field"""
        response = client.get("/fields/nonexistent-id")

        assert response.status_code == 404

    def test_list_fields_by_tenant(self, client, sample_field_data):
        """Should list fields for a tenant"""
        # Create two fields
        client.post("/fields", json=sample_field_data)
        second_field = sample_field_data.copy()
        second_field["name"] = "Second Field"
        client.post("/fields", json=second_field)

        # List
        response = client.get(f"/fields?tenant_id={sample_field_data['tenant_id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        assert len(body["items"]) == 2

    def test_list_fields_pagination(self, client, sample_field_data):
        """Should paginate field list"""
        # Create 3 fields
        for i in range(3):
            data = sample_field_data.copy()
            data["name"] = f"Field {i}"
            client.post("/fields", json=data)

        # Get page with limit 2
        response = client.get(f"/fields?tenant_id={sample_field_data['tenant_id']}&limit=2")
        body = response.json()

        assert body["total"] == 3
        assert len(body["items"]) == 2
        assert body["limit"] == 2

    def test_update_field(self, client, sample_field_data):
        """Should update field properties"""
        # Create
        create_response = client.post("/fields", json=sample_field_data)
        field_id = create_response.json()["id"]

        # Update
        update_data = {"name": "Updated Name", "area_hectares": 50.0}
        response = client.put(f"/fields/{field_id}", json=update_data)

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Updated Name"
        assert body["area_hectares"] == 50.0

    def test_delete_field(self, client, sample_field_data):
        """Should delete field"""
        # Create
        create_response = client.post("/fields", json=sample_field_data)
        field_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/fields/{field_id}")

        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

        # Verify deleted
        get_response = client.get(f"/fields/{field_id}")
        assert get_response.status_code == 404


class TestOperationsCRUD:
    """Integration tests for Operations CRUD"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from main import _fields, _operations, app

        _fields.clear()
        _operations.clear()

        return TestClient(app)

    def test_create_operation(self, client, sample_operation_data):
        """Should create a new operation"""
        response = client.post("/operations", json=sample_operation_data)

        assert response.status_code == 200
        body = response.json()
        assert body["operation_type"] == sample_operation_data["operation_type"]
        assert body["status"] == "scheduled"

    def test_get_operation(self, client, sample_operation_data):
        """Should get operation by ID"""
        create_response = client.post("/operations", json=sample_operation_data)
        op_id = create_response.json()["id"]

        response = client.get(f"/operations/{op_id}")

        assert response.status_code == 200
        assert response.json()["id"] == op_id

    def test_complete_operation(self, client, sample_operation_data):
        """Should mark operation as completed"""
        create_response = client.post("/operations", json=sample_operation_data)
        op_id = create_response.json()["id"]

        response = client.post(f"/operations/{op_id}/complete")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "completed"
        assert body["completed_date"] is not None


class TestTenantStats:
    """Integration tests for tenant statistics"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from main import _fields, _operations, app

        _fields.clear()
        _operations.clear()

        return TestClient(app)

    def test_get_tenant_stats(self, client, sample_field_data, sample_operation_data):
        """Should return tenant statistics"""
        # Create a field
        client.post("/fields", json=sample_field_data)

        # Create an operation
        sample_operation_data["tenant_id"] = sample_field_data["tenant_id"]
        client.post("/operations", json=sample_operation_data)

        # Get stats
        response = client.get(f"/stats/tenant/{sample_field_data['tenant_id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["fields_count"] == 1
        assert body["total_area_hectares"] == sample_field_data["area_hectares"]
        assert body["operations"]["total"] == 1
