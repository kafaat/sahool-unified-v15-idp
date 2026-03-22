"""
Tests for lowcode-engine API endpoints.
"""

import os
import sys
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

# Add project root to path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
sys.path.insert(0, project_root)

# Set test environment variables
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")


# ============================================================================
# Test Health Endpoints
# ============================================================================


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test the /healthz endpoint returns OK status."""
        response = await async_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "lowcode-engine"
        assert "version" in data
        assert data["service_ar"] == "محرك التطوير منخفض الكود"

    @pytest.mark.asyncio
    async def test_readiness_endpoint(self, async_client: AsyncClient):
        """Test the /readyz endpoint returns readiness status."""
        response = await async_client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "nats" in data
        assert "components_loaded" in data

    @pytest.mark.asyncio
    async def test_detailed_health_endpoint(self, async_client: AsyncClient):
        """Test the /health endpoint returns detailed status."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "lowcode-engine"
        assert "database_connected" in data
        assert "nats_connected" in data
        assert "components_count" in data
        assert "data_models_count" in data
        assert "pages_count" in data


# ============================================================================
# Test Component Endpoints
# ============================================================================


class TestComponentEndpoints:
    """Tests for component material endpoints."""

    @pytest.mark.asyncio
    async def test_list_components(self, async_client: AsyncClient):
        """Test listing all components."""
        response = await async_client.get("/api/v1/components")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check component structure
        component = data[0]
        assert "component_id" in component
        assert "name" in component
        assert "category" in component
        assert "props" in component
        assert "is_container" in component

    @pytest.mark.asyncio
    async def test_list_components_by_category(self, async_client: AsyncClient):
        """Test filtering components by category."""
        response = await async_client.get("/api/v1/components?category=form")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # All returned components should be in the form category
        for component in data:
            assert component["category"] == "form"

    @pytest.mark.asyncio
    async def test_list_components_agriculture_category(self, async_client: AsyncClient):
        """Test filtering components by agriculture category."""
        response = await async_client.get("/api/v1/components?category=agriculture")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        for component in data:
            assert component["category"] == "agriculture"

    @pytest.mark.asyncio
    async def test_get_component(self, async_client: AsyncClient):
        """Test getting a specific component by name."""
        response = await async_client.get("/api/v1/components/field_map")

        assert response.status_code == 200
        data = response.json()
        assert data["component_id"] == "field_map"
        assert data["name"] == "Field Map"
        assert "name_ar" in data
        assert "props" in data
        assert "events" in data

    @pytest.mark.asyncio
    async def test_get_component_not_found(self, async_client: AsyncClient):
        """Test getting a non-existent component returns 404."""
        response = await async_client.get("/api/v1/components/nonexistent_component")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Component not found"

    @pytest.mark.asyncio
    async def test_list_categories(self, async_client: AsyncClient):
        """Test listing component categories."""
        response = await async_client.get("/api/v1/components/categories")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check category structure
        category = data[0]
        assert "value" in category
        assert "name" in category
        assert "name_ar" in category


# ============================================================================
# Test Data Model Endpoints
# ============================================================================


class TestDataModelEndpoints:
    """Tests for data model endpoints."""

    @pytest.mark.asyncio
    async def test_create_data_model(self, async_client: AsyncClient, data_model_create_request: dict):
        """Test creating a new data model."""
        response = await async_client.post(
            "/api/v1/models",
            json=data_model_create_request,
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == data_model_create_request["name"]
        assert data["name_ar"] == data_model_create_request["name_ar"]
        assert len(data["fields"]) == len(data_model_create_request["fields"])
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_data_model_minimal(self, async_client: AsyncClient):
        """Test creating a data model with minimal fields."""
        request = {
            "name": "MinimalModel",
            "fields": [{"name": "id", "field_type": "string"}],
            "tenant_id": "test-tenant",
        }

        response = await async_client.post("/api/v1/models", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MinimalModel"
        assert len(data["fields"]) == 1

    @pytest.mark.asyncio
    async def test_create_data_model_validation_error(self, async_client: AsyncClient):
        """Test creating a data model with invalid data."""
        request = {
            "name": "",  # Empty name should fail
            "fields": [],
            "tenant_id": "test-tenant",
        }

        response = await async_client.post("/api/v1/models", json=request)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_data_models(self, async_client: AsyncClient, data_model_create_request: dict):
        """Test listing data models."""
        # First create a model
        await async_client.post("/api/v1/models", json=data_model_create_request)

        # Then list models
        response = await async_client.get("/api/v1/models?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_data_models_with_limit(self, async_client: AsyncClient):
        """Test listing data models with limit parameter."""
        response = await async_client.get("/api/v1/models?tenant_id=test-tenant&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_get_data_model(self, async_client: AsyncClient, data_model_create_request: dict):
        """Test getting a specific data model by ID."""
        # First create a model
        create_response = await async_client.post("/api/v1/models", json=data_model_create_request)
        model_id = create_response.json()["id"]

        # Then get it
        response = await async_client.get(f"/api/v1/models/{model_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == model_id
        assert data["name"] == data_model_create_request["name"]

    @pytest.mark.asyncio
    async def test_get_data_model_not_found(self, async_client: AsyncClient):
        """Test getting a non-existent data model returns 404."""
        response = await async_client.get("/api/v1/models/nonexistent-id")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Data model not found"


# ============================================================================
# Test Page Endpoints
# ============================================================================


class TestPageEndpoints:
    """Tests for page endpoints."""

    @pytest.mark.asyncio
    async def test_create_page(self, async_client: AsyncClient, page_create_request: dict):
        """Test creating a new page."""
        response = await async_client.post("/api/v1/pages", json=page_create_request)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == page_create_request["name"]
        assert data["route"] == page_create_request["route"]
        assert data["is_published"] is False
        assert data["version"] == 1
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_page_minimal(self, async_client: AsyncClient):
        """Test creating a page with minimal fields."""
        request = {
            "name": "Minimal Page",
            "route": "/minimal",
            "tenant_id": "test-tenant",
        }

        response = await async_client.post("/api/v1/pages", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Minimal Page"
        assert data["route"] == "/minimal"
        assert data["blocks"] == []

    @pytest.mark.asyncio
    async def test_create_page_invalid_route(self, async_client: AsyncClient):
        """Test creating a page with invalid route fails."""
        request = {
            "name": "Invalid Route Page",
            "route": "invalid-route",  # Missing leading slash
            "tenant_id": "test-tenant",
        }

        response = await async_client.post("/api/v1/pages", json=request)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_pages(self, async_client: AsyncClient, page_create_request: dict):
        """Test listing pages."""
        # First create a page
        await async_client.post("/api/v1/pages", json=page_create_request)

        # Then list pages
        response = await async_client.get("/api/v1/pages?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_pages_filter_published(self, async_client: AsyncClient):
        """Test listing pages filtered by published status."""
        response = await async_client.get("/api/v1/pages?tenant_id=test-tenant&is_published=false")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        for page in data:
            assert page["is_published"] is False

    @pytest.mark.asyncio
    async def test_get_page(self, async_client: AsyncClient, page_create_request: dict):
        """Test getting a specific page by ID."""
        # First create a page
        create_response = await async_client.post("/api/v1/pages", json=page_create_request)
        page_id = create_response.json()["id"]

        # Then get it
        response = await async_client.get(f"/api/v1/pages/{page_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == page_id
        assert data["name"] == page_create_request["name"]

    @pytest.mark.asyncio
    async def test_get_page_not_found(self, async_client: AsyncClient):
        """Test getting a non-existent page returns 404."""
        response = await async_client.get("/api/v1/pages/nonexistent-id")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Page not found"

    @pytest.mark.asyncio
    async def test_update_page_publish(self, async_client: AsyncClient, page_create_request: dict):
        """Test publishing a page updates its status."""
        # First create a page
        create_response = await async_client.post("/api/v1/pages", json=page_create_request)
        page_id = create_response.json()["id"]

        # Verify it's not published
        get_response = await async_client.get(f"/api/v1/pages/{page_id}")
        assert get_response.json()["is_published"] is False

        # Publish it
        publish_response = await async_client.post(f"/api/v1/pages/{page_id}/publish")

        assert publish_response.status_code == 200
        assert publish_response.json()["is_published"] is True

    @pytest.mark.asyncio
    async def test_publish_page(self, async_client: AsyncClient, page_create_request: dict):
        """Test the publish page endpoint."""
        # First create a page
        create_response = await async_client.post("/api/v1/pages", json=page_create_request)
        page_id = create_response.json()["id"]

        # Then publish it
        response = await async_client.post(f"/api/v1/pages/{page_id}/publish")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == page_id
        assert data["is_published"] is True

    @pytest.mark.asyncio
    async def test_publish_page_not_found(self, async_client: AsyncClient):
        """Test publishing a non-existent page returns 404."""
        response = await async_client.post("/api/v1/pages/nonexistent-id/publish")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Page not found"

    @pytest.mark.asyncio
    async def test_render_page(self, async_client: AsyncClient, page_create_request: dict):
        """Test rendering a page."""
        # First create a page
        create_response = await async_client.post("/api/v1/pages", json=page_create_request)
        page_id = create_response.json()["id"]

        # Then render it
        response = await async_client.get(f"/api/v1/pages/{page_id}/render")

        assert response.status_code == 200
        data = response.json()
        assert data["page_id"] == page_id
        assert data["name"] == page_create_request["name"]
        assert "rendered_blocks" in data

    @pytest.mark.asyncio
    async def test_render_page_not_found(self, async_client: AsyncClient):
        """Test rendering a non-existent page returns 404."""
        response = await async_client.get("/api/v1/pages/nonexistent-id/render")

        assert response.status_code == 404


# ============================================================================
# Test AI Suggestion Endpoints
# ============================================================================


class TestAISuggestionEndpoints:
    """Tests for AI suggestion endpoints."""

    @pytest.mark.asyncio
    async def test_ai_suggest_components(self, async_client: AsyncClient, ai_suggestion_request: dict):
        """Test AI component suggestions."""
        response = await async_client.post("/api/v1/ai/suggest", json=ai_suggestion_request)

        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert "reasoning" in data
        assert "reasoning_ar" in data
        assert "confidence" in data
        assert isinstance(data["suggestions"], list)
        assert isinstance(data["confidence"], float)

    @pytest.mark.asyncio
    async def test_ai_suggest_components_with_keywords(self, async_client: AsyncClient):
        """Test AI suggestions respond to relevant keywords."""
        request = {
            "description": "Create a field map showing irrigation zones and water sensors",
            "context": {},
        }

        response = await async_client.post("/api/v1/ai/suggest", json=request)

        assert response.status_code == 200
        data = response.json()

        # Should suggest field_map and irrigation components
        component_ids = [s["component_id"] for s in data["suggestions"]]

        # At least one relevant component should be suggested
        relevant_components = {"field_map", "irrigation_scheduler", "sensor_display"}
        assert len(set(component_ids) & relevant_components) > 0

    @pytest.mark.asyncio
    async def test_ai_suggest_components_arabic_keywords(self, async_client: AsyncClient):
        """Test AI suggestions respond to Arabic keywords."""
        request = {
            "description": "Create a dashboard for crop health monitoring",
            "description_ar": "إنشاء لوحة تحكم لمراقبة صحة المحصول",
            "context": {},
        }

        response = await async_client.post("/api/v1/ai/suggest", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "reasoning_ar" in data

    @pytest.mark.asyncio
    async def test_ai_suggest_components_validation_error(self, async_client: AsyncClient):
        """Test AI suggestions with invalid request."""
        request = {
            "description": "short",  # Too short (min_length=10)
        }

        response = await async_client.post("/api/v1/ai/suggest", json=request)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_templates(self, async_client: AsyncClient):
        """Test listing page templates."""
        response = await async_client.get("/api/v1/ai/templates")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check template structure
        template = data[0]
        assert "id" in template
        assert "name" in template
        assert "name_ar" in template
        assert "description" in template
        assert "components" in template

    @pytest.mark.asyncio
    async def test_generate_page_from_template(self, async_client: AsyncClient):
        """Test generating a page from a template."""
        response = await async_client.post(
            "/api/v1/ai/generate-page",
            params={
                "template_id": "field-dashboard",
                "name": "My Field Dashboard",
                "name_ar": "لوحة تحكم حقلي",
                "tenant_id": "test-tenant",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Field Dashboard"
        assert data["name_ar"] == "لوحة تحكم حقلي"
        assert len(data["blocks"]) > 0

    @pytest.mark.asyncio
    async def test_generate_page_from_invalid_template(self, async_client: AsyncClient):
        """Test generating a page from non-existent template returns 404."""
        response = await async_client.post(
            "/api/v1/ai/generate-page",
            params={
                "template_id": "nonexistent-template",
                "name": "Test Page",
                "tenant_id": "test-tenant",
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Template not found"


# ============================================================================
# Test Metrics Endpoint
# ============================================================================


class TestMetricsEndpoint:
    """Tests for metrics endpoint."""

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, async_client: AsyncClient):
        """Test the /metrics endpoint returns Prometheus-format metrics."""
        response = await async_client.get("/metrics")

        assert response.status_code == 200
        content = response.text

        # Check for expected metrics
        assert "lowcode_components_total" in content
        assert "lowcode_data_models_total" in content
        assert "lowcode_pages_total" in content
        assert "lowcode_pages_published" in content

        # Check for Prometheus format indicators
        assert "# HELP" in content
        assert "# TYPE" in content
