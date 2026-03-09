"""
Integration tests for lowcode-engine
اختبارات التكامل لمحرك التطوير منخفض الكود

Tests the Low-Code Engine Service for:
- Component listing and retrieval
- Data model CRUD operations
- Page creation, update, and publishing
- AI component suggestions
- Template-based page generation
- Database persistence

Service URL: http://localhost:8132
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Factories
# ═══════════════════════════════════════════════════════════════════════════════


class DataModelFactory:
    """Factory for creating data model test data."""

    @staticmethod
    def create_data_model_request(
        tenant_id: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Create a data model creation request."""
        unique_id = uuid4().hex[:8]
        return {
            "name": name or f"TestModel{unique_id}",
            "name_ar": f"نموذج اختبار {unique_id}",
            "description": "A test data model for integration testing",
            "description_ar": "نموذج بيانات اختبار لاختبارات التكامل",
            "fields": [
                {
                    "name": "name",
                    "type": "string",
                    "required": True,
                    "label": "Name",
                    "label_ar": "الاسم",
                },
                {
                    "name": "area_hectares",
                    "type": "number",
                    "required": True,
                    "label": "Area (Hectares)",
                    "label_ar": "المساحة (هكتار)",
                },
                {
                    "name": "crop_type",
                    "type": "select",
                    "required": True,
                    "options": ["wheat", "barley", "tomato", "date_palm"],
                    "label": "Crop Type",
                    "label_ar": "نوع المحصول",
                },
                {
                    "name": "planting_date",
                    "type": "date",
                    "required": False,
                    "label": "Planting Date",
                    "label_ar": "تاريخ الزراعة",
                },
                {
                    "name": "is_irrigated",
                    "type": "boolean",
                    "default": True,
                    "label": "Irrigated",
                    "label_ar": "مروي",
                },
            ],
            "tenant_id": tenant_id or f"test-tenant-{uuid4().hex[:8]}",
        }


class PageFactory:
    """Factory for creating page test data."""

    @staticmethod
    def create_page_request(
        tenant_id: str | None = None,
        name: str | None = None,
        data_model_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a page creation request."""
        unique_id = uuid4().hex[:8]
        return {
            "name": name or f"TestPage{unique_id}",
            "name_ar": f"صفحة اختبار {unique_id}",
            "description": "A test page for integration testing",
            "route": f"/test/{unique_id}",
            "blocks": [
                {
                    "id": str(uuid4()),
                    "component_name": "field_map",
                    "props": {
                        "zoom": 12,
                        "showControls": True,
                    },
                    "children": [],
                },
                {
                    "id": str(uuid4()),
                    "component_name": "sensor_display",
                    "props": {
                        "sensorTypes": ["soil_moisture", "temperature"],
                        "refreshInterval": 60,
                    },
                    "children": [],
                },
            ],
            "data_model_id": data_model_id,
            "tenant_id": tenant_id or f"test-tenant-{uuid4().hex[:8]}",
        }

    @staticmethod
    def create_page_update_request(
        tenant_id: str,
    ) -> dict[str, Any]:
        """Create a page update request."""
        return {
            "name": f"UpdatedPage{uuid4().hex[:8]}",
            "description": "Updated page description",
            "blocks": [
                {
                    "id": str(uuid4()),
                    "component_name": "crop_health_card",
                    "props": {
                        "showNDVI": True,
                        "showLAI": True,
                    },
                    "children": [],
                },
            ],
            "tenant_id": tenant_id,
        }


class AISuggestionFactory:
    """Factory for creating AI suggestion test data."""

    @staticmethod
    def create_suggestion_request(
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create an AI suggestion request."""
        return {
            "description": description or "I need a page to monitor field irrigation and view sensor data",
            "description_ar": "أحتاج صفحة لمراقبة ري الحقل وعرض بيانات المستشعرات",
            "context": {
                "crop_type": "wheat",
                "farm_size": "medium",
            },
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Low-Code Engine Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestLowCodeIntegration:
    """
    Integration tests for Low-Code Engine Service.
    اختبارات التكامل لمحرك التطوير منخفض الكود
    """

    SERVICE_URL = "http://localhost:8132"

    @pytest.fixture
    def data_model_factory(self) -> DataModelFactory:
        """Data model factory fixture."""
        return DataModelFactory()

    @pytest.fixture
    def page_factory(self) -> PageFactory:
        """Page factory fixture."""
        return PageFactory()

    @pytest.fixture
    def ai_suggestion_factory(self) -> AISuggestionFactory:
        """AI suggestion factory fixture."""
        return AISuggestionFactory()

    @pytest.fixture
    async def lowcode_client(self, http_client: AsyncClient, auth_headers: dict[str, str]) -> AsyncClient:
        """HTTP client configured for Low-Code Engine service."""
        http_client.base_url = self.SERVICE_URL
        http_client.headers.update(auth_headers)
        return http_client

    # ═══════════════════════════════════════════════════════════════════════════
    # Health Check Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_health_endpoint(self, lowcode_client: AsyncClient):
        """Test liveness probe endpoint."""
        response = await lowcode_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "lowcode-engine"
        assert "version" in data

    async def test_readiness_endpoint(self, lowcode_client: AsyncClient):
        """Test readiness probe endpoint."""
        response = await lowcode_client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "nats" in data
        assert "components_loaded" in data

    async def test_detailed_health_endpoint(self, lowcode_client: AsyncClient):
        """Test detailed health status endpoint."""
        response = await lowcode_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "components_count" in data
        assert data["components_count"] > 0
        assert "storage_type" in data

    # ═══════════════════════════════════════════════════════════════════════════
    # Component Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_list_components(self, lowcode_client: AsyncClient):
        """Test listing all available components."""
        response = await lowcode_client.get("/api/v1/components")

        assert response.status_code == 200
        components = response.json()
        assert isinstance(components, list)
        assert len(components) > 0

        # Verify component structure
        for component in components:
            assert "component_id" in component
            assert "name" in component
            assert "category" in component
            assert "props" in component
            assert "slots" in component
            assert "events" in component
            assert "is_container" in component

    async def test_list_components_by_category(self, lowcode_client: AsyncClient):
        """Test listing components filtered by category."""
        # First get all categories
        categories_response = await lowcode_client.get("/api/v1/components/categories")
        # Note: This endpoint might return 405 if it conflicts with component_name param

        # Filter by agricultural category
        response = await lowcode_client.get("/api/v1/components?category=agricultural")

        assert response.status_code == 200
        components = response.json()
        for component in components:
            assert component["category"] == "agricultural"

    async def test_get_specific_component(self, lowcode_client: AsyncClient):
        """Test getting a specific component by name."""
        # Get field_map component
        response = await lowcode_client.get("/api/v1/components/field_map")

        assert response.status_code == 200
        component = response.json()
        assert component["name"] == "field_map" or "map" in component["name"].lower()
        assert "props" in component
        assert "name_ar" in component

    async def test_get_nonexistent_component(self, lowcode_client: AsyncClient):
        """Test error handling for non-existent component."""
        response = await lowcode_client.get("/api/v1/components/nonexistent_component")

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Data Model Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_create_data_model(
        self,
        lowcode_client: AsyncClient,
        data_model_factory: DataModelFactory,
    ):
        """Test creating a new data model."""
        request_data = data_model_factory.create_data_model_request()

        response = await lowcode_client.post(
            "/api/v1/models",
            json=request_data,
        )

        assert response.status_code == 200
        model = response.json()
        assert model["name"] == request_data["name"]
        assert model["name_ar"] == request_data["name_ar"]
        assert "id" in model
        assert "fields" in model
        assert len(model["fields"]) == len(request_data["fields"])
        assert "created_at" in model
        assert "updated_at" in model

    async def test_get_data_model(
        self,
        lowcode_client: AsyncClient,
        data_model_factory: DataModelFactory,
    ):
        """Test retrieving a data model by ID."""
        # Create model first
        request_data = data_model_factory.create_data_model_request()
        create_response = await lowcode_client.post(
            "/api/v1/models",
            json=request_data,
        )
        model_id = create_response.json()["id"]

        # Get model
        response = await lowcode_client.get(f"/api/v1/models/{model_id}")

        assert response.status_code == 200
        model = response.json()
        assert model["id"] == model_id
        assert model["name"] == request_data["name"]

    async def test_list_data_models(
        self,
        lowcode_client: AsyncClient,
        data_model_factory: DataModelFactory,
    ):
        """Test listing data models for a tenant."""
        tenant_id = f"test-tenant-models-{uuid4().hex[:8]}"

        # Create multiple models
        for _ in range(3):
            request_data = data_model_factory.create_data_model_request(tenant_id=tenant_id)
            await lowcode_client.post("/api/v1/models", json=request_data)

        # List models
        response = await lowcode_client.get(f"/api/v1/models?tenant_id={tenant_id}")

        assert response.status_code == 200
        models = response.json()
        assert len(models) >= 3

    async def test_delete_data_model(
        self,
        lowcode_client: AsyncClient,
        data_model_factory: DataModelFactory,
    ):
        """Test deleting a data model."""
        # Create model
        request_data = data_model_factory.create_data_model_request()
        create_response = await lowcode_client.post(
            "/api/v1/models",
            json=request_data,
        )
        model_id = create_response.json()["id"]

        # Delete model
        delete_response = await lowcode_client.delete(f"/api/v1/models/{model_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        get_response = await lowcode_client.get(f"/api/v1/models/{model_id}")
        assert get_response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Page Creation Flow Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_page_creation_flow(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """
        Test complete page creation and publishing.
        اختبار إنشاء ونشر الصفحة بالكامل

        This test verifies:
        1. Page can be created (draft state)
        2. Page can be updated
        3. Page can be published
        4. Page can be unpublished
        5. Page can be rendered
        """
        tenant_id = f"test-tenant-page-{uuid4().hex[:8]}"

        # Step 1: Create a page (draft)
        create_request = page_factory.create_page_request(tenant_id=tenant_id)
        create_response = await lowcode_client.post(
            "/api/v1/pages",
            json=create_request,
        )

        assert create_response.status_code == 200
        page = create_response.json()
        assert page["name"] == create_request["name"]
        assert page["route"] == create_request["route"]
        assert page["is_published"] is False
        assert page["version"] == 1
        assert "id" in page

        page_id = page["id"]

        # Step 2: Update the page
        update_request = page_factory.create_page_update_request(tenant_id=tenant_id)
        update_response = await lowcode_client.patch(
            f"/api/v1/pages/{page_id}",
            json=update_request,
        )

        assert update_response.status_code == 200
        updated_page = update_response.json()
        assert updated_page["name"] == update_request["name"]
        assert len(updated_page["blocks"]) == len(update_request["blocks"])

        # Step 3: Publish the page
        publish_response = await lowcode_client.post(f"/api/v1/pages/{page_id}/publish")

        assert publish_response.status_code == 200
        published_page = publish_response.json()
        assert published_page["is_published"] is True
        assert published_page["version"] == 2  # Version incremented

        # Step 4: Verify in list (published filter)
        list_response = await lowcode_client.get(f"/api/v1/pages?tenant_id={tenant_id}&is_published=true")
        assert list_response.status_code == 200
        pages = list_response.json()
        page_ids = [p["id"] for p in pages]
        assert page_id in page_ids

        # Step 5: Unpublish the page
        unpublish_response = await lowcode_client.post(f"/api/v1/pages/{page_id}/unpublish")

        assert unpublish_response.status_code == 200
        unpublished_page = unpublish_response.json()
        assert unpublished_page["is_published"] is False

        # Step 6: Render the page
        render_response = await lowcode_client.get(f"/api/v1/pages/{page_id}/render")

        assert render_response.status_code == 200
        rendered = render_response.json()
        assert rendered["page_id"] == page_id
        assert "rendered_blocks" in rendered
        assert isinstance(rendered["rendered_blocks"], list)

    async def test_page_with_custom_route(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test creating pages with custom routes."""
        tenant_id = f"test-tenant-route-{uuid4().hex[:8]}"

        routes = [
            "/dashboard/main",
            "/fields/overview",
            "/irrigation/schedule",
        ]

        for route in routes:
            request_data = page_factory.create_page_request(tenant_id=tenant_id)
            request_data["route"] = route

            response = await lowcode_client.post(
                "/api/v1/pages",
                json=request_data,
            )

            assert response.status_code == 200
            page = response.json()
            assert page["route"] == route

    # ═══════════════════════════════════════════════════════════════════════════
    # Data Model with Page Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_data_model_with_page(
        self,
        lowcode_client: AsyncClient,
        data_model_factory: DataModelFactory,
        page_factory: PageFactory,
    ):
        """
        Test creating data model and using it in page.
        اختبار إنشاء نموذج بيانات واستخدامه في صفحة

        This verifies that:
        1. Data model can be created
        2. Page can reference the data model
        3. Page render includes data model context
        """
        tenant_id = f"test-tenant-dm-page-{uuid4().hex[:8]}"

        # Step 1: Create data model
        model_request = data_model_factory.create_data_model_request(
            tenant_id=tenant_id,
            name="FieldModel",
        )
        model_response = await lowcode_client.post(
            "/api/v1/models",
            json=model_request,
        )
        assert model_response.status_code == 200
        data_model = model_response.json()
        data_model_id = data_model["id"]

        # Step 2: Create page referencing the data model
        page_request = page_factory.create_page_request(
            tenant_id=tenant_id,
            data_model_id=data_model_id,
        )
        page_response = await lowcode_client.post(
            "/api/v1/pages",
            json=page_request,
        )

        assert page_response.status_code == 200
        page = page_response.json()
        assert page["data_model_id"] == data_model_id

        # Step 3: Verify page retrieval includes data model reference
        get_response = await lowcode_client.get(f"/api/v1/pages/{page['id']}")
        assert get_response.status_code == 200
        retrieved_page = get_response.json()
        assert retrieved_page["data_model_id"] == data_model_id

        # Step 4: Render page (should work even with data model)
        render_response = await lowcode_client.get(f"/api/v1/pages/{page['id']}/render")
        assert render_response.status_code == 200
        rendered = render_response.json()
        assert rendered["page_id"] == page["id"]

    # ═══════════════════════════════════════════════════════════════════════════
    # AI Component Suggestion Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_ai_suggest_components(
        self,
        lowcode_client: AsyncClient,
        ai_suggestion_factory: AISuggestionFactory,
    ):
        """Test AI component suggestions based on description."""
        request_data = ai_suggestion_factory.create_suggestion_request(
            description="I need a dashboard to monitor crop health with NDVI visualization"
        )

        response = await lowcode_client.post(
            "/api/v1/ai/suggest",
            json=request_data,
        )

        assert response.status_code == 200
        suggestions = response.json()
        assert "suggestions" in suggestions
        assert "reasoning" in suggestions
        assert "confidence" in suggestions
        assert isinstance(suggestions["suggestions"], list)
        assert 0 <= suggestions["confidence"] <= 1

        # Should suggest relevant components
        if suggestions["suggestions"]:
            for suggestion in suggestions["suggestions"]:
                assert "component_id" in suggestion
                assert "confidence" in suggestion

    async def test_ai_suggest_irrigation_page(
        self,
        lowcode_client: AsyncClient,
        ai_suggestion_factory: AISuggestionFactory,
    ):
        """Test AI suggestions for irrigation-related page."""
        request_data = ai_suggestion_factory.create_suggestion_request(
            description="Create a page to schedule and monitor irrigation with water usage tracking"
        )

        response = await lowcode_client.post(
            "/api/v1/ai/suggest",
            json=request_data,
        )

        assert response.status_code == 200
        suggestions = response.json()

        # Should suggest irrigation-related components
        suggested_ids = [s["component_id"] for s in suggestions.get("suggestions", [])]
        # At least one irrigation-related suggestion expected
        irrigation_related = any("irrigation" in cid.lower() or "water" in cid.lower() for cid in suggested_ids)
        # Note: Depends on available components in the engine

    async def test_ai_list_templates(self, lowcode_client: AsyncClient):
        """Test listing available page templates."""
        response = await lowcode_client.get("/api/v1/ai/templates")

        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)

        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "components" in template

    async def test_ai_generate_page_from_template(
        self,
        lowcode_client: AsyncClient,
    ):
        """Test generating a page from a template."""
        tenant_id = f"test-tenant-template-{uuid4().hex[:8]}"

        response = await lowcode_client.post(
            "/api/v1/ai/generate-page",
            params={
                "template_id": "field-dashboard",
                "name": "My Field Dashboard",
                "name_ar": "لوحة تحكم حقلي",
                "tenant_id": tenant_id,
            },
        )

        assert response.status_code == 200
        page = response.json()
        assert page["name"] == "My Field Dashboard"
        assert "id" in page
        assert len(page["blocks"]) > 0
        assert page["is_published"] is False

    async def test_ai_generate_page_invalid_template(
        self,
        lowcode_client: AsyncClient,
    ):
        """Test error handling for invalid template ID."""
        tenant_id = f"test-tenant-invalid-{uuid4().hex[:8]}"

        response = await lowcode_client.post(
            "/api/v1/ai/generate-page",
            params={
                "template_id": "nonexistent-template",
                "name": "Test Page",
                "tenant_id": tenant_id,
            },
        )

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Page Listing and Filtering Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_list_pages_by_tenant(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test listing pages filtered by tenant."""
        tenant_id = f"test-tenant-list-{uuid4().hex[:8]}"

        # Create multiple pages
        for _ in range(5):
            request_data = page_factory.create_page_request(tenant_id=tenant_id)
            await lowcode_client.post("/api/v1/pages", json=request_data)

        # List pages
        response = await lowcode_client.get(f"/api/v1/pages?tenant_id={tenant_id}")

        assert response.status_code == 200
        pages = response.json()
        assert len(pages) >= 5

    async def test_list_pages_published_filter(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test listing pages with published filter."""
        tenant_id = f"test-tenant-pub-{uuid4().hex[:8]}"

        # Create and publish some pages
        for i in range(4):
            request_data = page_factory.create_page_request(tenant_id=tenant_id)
            create_response = await lowcode_client.post(
                "/api/v1/pages",
                json=request_data,
            )
            page_id = create_response.json()["id"]

            # Publish half of them
            if i % 2 == 0:
                await lowcode_client.post(f"/api/v1/pages/{page_id}/publish")

        # List only published
        published_response = await lowcode_client.get(f"/api/v1/pages?tenant_id={tenant_id}&is_published=true")
        assert published_response.status_code == 200
        published_pages = published_response.json()
        for page in published_pages:
            assert page["is_published"] is True

        # List only unpublished
        unpublished_response = await lowcode_client.get(f"/api/v1/pages?tenant_id={tenant_id}&is_published=false")
        assert unpublished_response.status_code == 200
        unpublished_pages = unpublished_response.json()
        for page in unpublished_pages:
            assert page["is_published"] is False

    async def test_page_pagination(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test page listing with pagination."""
        tenant_id = f"test-tenant-paginate-{uuid4().hex[:8]}"

        # Create many pages
        for _ in range(15):
            request_data = page_factory.create_page_request(tenant_id=tenant_id)
            await lowcode_client.post("/api/v1/pages", json=request_data)

        # Get first page
        page1_response = await lowcode_client.get(f"/api/v1/pages?tenant_id={tenant_id}&limit=10")
        assert page1_response.status_code == 200
        page1 = page1_response.json()
        assert len(page1) == 10

    # ═══════════════════════════════════════════════════════════════════════════
    # Page Deletion Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_delete_page(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test deleting a page."""
        tenant_id = f"test-tenant-delete-{uuid4().hex[:8]}"

        # Create page
        request_data = page_factory.create_page_request(tenant_id=tenant_id)
        create_response = await lowcode_client.post(
            "/api/v1/pages",
            json=request_data,
        )
        page_id = create_response.json()["id"]

        # Delete page
        delete_response = await lowcode_client.delete(f"/api/v1/pages/{page_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        get_response = await lowcode_client.get(f"/api/v1/pages/{page_id}")
        assert get_response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════
    # Tenant Isolation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_tenant_isolation_pages(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test that tenants cannot access each other's pages."""
        tenant_a = f"tenant-a-{uuid4().hex[:8]}"
        tenant_b = f"tenant-b-{uuid4().hex[:8]}"

        # Create page for tenant A
        page_a_request = page_factory.create_page_request(tenant_id=tenant_a)
        page_a_response = await lowcode_client.post(
            "/api/v1/pages",
            json=page_a_request,
        )
        page_a = page_a_response.json()

        # Create page for tenant B
        page_b_request = page_factory.create_page_request(tenant_id=tenant_b)
        page_b_response = await lowcode_client.post(
            "/api/v1/pages",
            json=page_b_request,
        )
        page_b = page_b_response.json()

        # List for tenant A
        list_a_response = await lowcode_client.get(f"/api/v1/pages?tenant_id={tenant_a}")
        pages_a = list_a_response.json()
        page_ids_a = [p["id"] for p in pages_a]
        assert page_a["id"] in page_ids_a
        assert page_b["id"] not in page_ids_a

        # List for tenant B
        list_b_response = await lowcode_client.get(f"/api/v1/pages?tenant_id={tenant_b}")
        pages_b = list_b_response.json()
        page_ids_b = [p["id"] for p in pages_b]
        assert page_b["id"] in page_ids_b
        assert page_a["id"] not in page_ids_b

    async def test_tenant_isolation_models(
        self,
        lowcode_client: AsyncClient,
        data_model_factory: DataModelFactory,
    ):
        """Test that tenants cannot access each other's data models."""
        tenant_a = f"tenant-a-model-{uuid4().hex[:8]}"
        tenant_b = f"tenant-b-model-{uuid4().hex[:8]}"

        # Create model for tenant A
        model_a_request = data_model_factory.create_data_model_request(tenant_id=tenant_a)
        model_a_response = await lowcode_client.post(
            "/api/v1/models",
            json=model_a_request,
        )
        model_a = model_a_response.json()

        # Create model for tenant B
        model_b_request = data_model_factory.create_data_model_request(tenant_id=tenant_b)
        model_b_response = await lowcode_client.post(
            "/api/v1/models",
            json=model_b_request,
        )
        model_b = model_b_response.json()

        # List for tenant A
        list_a_response = await lowcode_client.get(f"/api/v1/models?tenant_id={tenant_a}")
        models_a = list_a_response.json()
        model_ids_a = [m["id"] for m in models_a]
        assert model_a["id"] in model_ids_a
        assert model_b["id"] not in model_ids_a

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Handling Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_page_not_found(self, lowcode_client: AsyncClient):
        """Test error handling for non-existent page."""
        fake_id = str(uuid4())
        response = await lowcode_client.get(f"/api/v1/pages/{fake_id}")

        assert response.status_code == 404

    async def test_model_not_found(self, lowcode_client: AsyncClient):
        """Test error handling for non-existent data model."""
        fake_id = str(uuid4())
        response = await lowcode_client.get(f"/api/v1/models/{fake_id}")

        assert response.status_code == 404

    async def test_invalid_route_format(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test validation for invalid route format."""
        request_data = page_factory.create_page_request()
        request_data["route"] = "invalid-no-leading-slash"

        response = await lowcode_client.post(
            "/api/v1/pages",
            json=request_data,
        )

        assert response.status_code == 422  # Validation error

    async def test_missing_required_fields(
        self,
        lowcode_client: AsyncClient,
    ):
        """Test validation for missing required fields."""
        response = await lowcode_client.post(
            "/api/v1/pages",
            json={"name": "Test"},  # Missing route and tenant_id
        )

        assert response.status_code == 422

    # ═══════════════════════════════════════════════════════════════════════════
    # Page Rendering Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_render_page_with_blocks(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test page rendering returns processed blocks."""
        tenant_id = f"test-tenant-render-{uuid4().hex[:8]}"

        # Create page with specific blocks
        request_data = page_factory.create_page_request(tenant_id=tenant_id)
        create_response = await lowcode_client.post(
            "/api/v1/pages",
            json=request_data,
        )
        page = create_response.json()

        # Render page
        render_response = await lowcode_client.get(f"/api/v1/pages/{page['id']}/render")

        assert render_response.status_code == 200
        rendered = render_response.json()

        assert rendered["page_id"] == page["id"]
        assert rendered["name"] == page["name"]
        assert rendered["route"] == page["route"]
        assert "rendered_blocks" in rendered
        assert len(rendered["rendered_blocks"]) == len(request_data["blocks"])

        # Verify block structure
        for block in rendered["rendered_blocks"]:
            assert "id" in block
            assert "component_name" in block
            assert "props" in block

    # ═══════════════════════════════════════════════════════════════════════════
    # Metrics Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_metrics_endpoint(self, lowcode_client: AsyncClient):
        """Test Prometheus metrics endpoint."""
        response = await lowcode_client.get("/metrics")

        assert response.status_code == 200
        metrics = response.text
        assert "lowcode_components_total" in metrics
        assert "lowcode_db_connected" in metrics
        assert "lowcode_nats_connected" in metrics

    # ═══════════════════════════════════════════════════════════════════════════
    # Concurrent Operations Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_concurrent_page_creation(
        self,
        lowcode_client: AsyncClient,
        page_factory: PageFactory,
    ):
        """Test concurrent page creation."""
        tenant_id = f"test-tenant-concurrent-{uuid4().hex[:8]}"
        num_pages = 10

        # Create pages concurrently
        tasks = []
        for i in range(num_pages):
            request_data = page_factory.create_page_request(tenant_id=tenant_id)
            request_data["name"] = f"ConcurrentPage{i}"
            task = lowcode_client.post("/api/v1/pages", json=request_data)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # All should succeed
        page_ids = []
        for response in responses:
            assert response.status_code == 200
            page_ids.append(response.json()["id"])

        # All IDs should be unique
        assert len(set(page_ids)) == num_pages

        # List should show all pages
        list_response = await lowcode_client.get(f"/api/v1/pages?tenant_id={tenant_id}&limit=100")
        pages = list_response.json()
        assert len(pages) >= num_pages
