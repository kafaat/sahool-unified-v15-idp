"""
CRM Service API Endpoint Tests
==============================
Comprehensive tests for all CRM service API endpoints.

Tests cover:
- Health endpoints (/healthz, /readyz, /health)
- Farmer CRUD (/api/v1/farmers)
- Deal management (/api/v1/deals)
- Interaction logging (/api/v1/interactions)
- Natural language queries (/api/v1/query)
- Pipeline statistics (/api/v1/deals/pipeline)
- Metrics endpoint (/metrics)

Author: SAHOOL Platform Team
"""

import os
import sys
from datetime import date, datetime
from enum import Enum, StrEnum
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# Ensure test environment
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Classes for shared.crm Module
# ═══════════════════════════════════════════════════════════════════════════════


class FarmerStatus(StrEnum):
    """Mock FarmerStatus enum."""

    LEAD = "lead"
    REGISTERED = "registered"
    ACTIVE = "active"
    PREMIUM = "premium"
    CHURNED = "churned"


class DealStage(StrEnum):
    """Mock DealStage enum."""

    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEGOTIATION = "negotiation"
    CONTRACTED = "contracted"
    DELIVERED = "delivered"
    PAID = "paid"
    CLOSED_LOST = "closed_lost"


class InteractionType(StrEnum):
    """Mock InteractionType enum."""

    CALL = "call"
    VISIT = "visit"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"
    ADVISORY = "advisory"
    SUPPORT = "support"


class Farmer:
    """Mock Farmer model."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Set defaults for attributes that might not be passed
        if not hasattr(self, "last_interaction_at"):
            self.last_interaction_at = None
        if not hasattr(self, "actual_quantity_tons"):
            self.actual_quantity_tons = None
        if not hasattr(self, "total_value"):
            self.total_value = None


class HarvestDeal:
    """Mock HarvestDeal model."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Set defaults
        if not hasattr(self, "actual_quantity_tons"):
            self.actual_quantity_tons = None
        if not hasattr(self, "actual_harvest_date"):
            self.actual_harvest_date = None
        if not hasattr(self, "total_value"):
            self.total_value = None


class Interaction:
    """Mock Interaction model."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, "created_by"):
            self.created_by = None


class FarmerCRMService:
    """Mock FarmerCRMService."""

    def __init__(self, tenant_id: str = "sahool"):
        self.tenant_id = tenant_id


class FarmerQueryBot:
    """Mock FarmerQueryBot."""

    def __init__(self, crm_service):
        self.crm = crm_service


# Create mock module
mock_crm = MagicMock()
mock_crm.FarmerCRMService = FarmerCRMService
mock_crm.FarmerQueryBot = FarmerQueryBot
mock_crm.Farmer = Farmer
mock_crm.FarmerStatus = FarmerStatus
mock_crm.HarvestDeal = HarvestDeal
mock_crm.DealStage = DealStage
mock_crm.Interaction = Interaction
mock_crm.InteractionType = InteractionType


# Mock User class with proper attributes
class MockUser:
    """Mock User model for authentication."""

    def __init__(self, tenant_id: str = "test-tenant"):
        self.id = "test-user-id"
        self.email = "test@example.com"
        self.tenant_id = tenant_id


# Mock auth dependencies - must return a proper user
def mock_get_current_user():
    """Dependency override for get_current_user."""
    return MockUser(tenant_id="test-tenant")


mock_auth_deps = MagicMock()
mock_auth_deps.get_current_user = mock_get_current_user
mock_auth_models = MagicMock()
mock_auth_models.User = MockUser

# Patch before importing main
sys.modules["shared.crm"] = mock_crm
sys.modules["shared.auth.dependencies"] = mock_auth_deps
sys.modules["shared.auth.models"] = mock_auth_models


# ═══════════════════════════════════════════════════════════════════════════════
# Import App After Patching
# ═══════════════════════════════════════════════════════════════════════════════

import importlib.util

# Get the path to main.py
tests_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.dirname(tests_dir)
main_path = os.path.join(service_dir, "src", "main.py")

# Add project root to path for shared imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(service_dir)))
sys.path.insert(0, project_root)

# Import main module using importlib
spec = importlib.util.spec_from_file_location("main", main_path)
main_module = importlib.util.module_from_spec(spec)
sys.modules["main"] = main_module
spec.loader.exec_module(main_module)

# Get the objects from the module
app = main_module.app
farmers = main_module.farmers
deals = main_module.deals
interactions = main_module.interactions
FarmerCreateRequest = main_module.FarmerCreateRequest
FarmerUpdateRequest = main_module.FarmerUpdateRequest
FarmerResponse = main_module.FarmerResponse
HarvestDealCreateRequest = main_module.HarvestDealCreateRequest
HarvestDealResponse = main_module.HarvestDealResponse
InteractionCreateRequest = main_module.InteractionCreateRequest
InteractionResponse = main_module.InteractionResponse
QueryRequest = main_module.QueryRequest
QueryResponse = main_module.QueryResponse
PipelineStatsResponse = main_module.PipelineStatsResponse
get_current_user_dep = main_module.get_current_user


# ═══════════════════════════════════════════════════════════════════════════════
# Test Imports
# ═══════════════════════════════════════════════════════════════════════════════

from httpx import ASGITransport, AsyncClient

# ═══════════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear in-memory storage before each test."""
    farmers.clear()
    deals.clear()
    interactions.clear()
    yield
    farmers.clear()
    deals.clear()
    interactions.clear()


@pytest.fixture
def setup_app_state():
    """Setup app state for testing."""
    # Initialize state attributes that would normally be set in lifespan
    app.state.publisher = None
    app.state.nats_connected = False
    app.state.db_pool = None
    app.state.db_connected = False
    app.state.crm_repo = None

    # Disable rate limiting for tests by setting limiter.enabled to False
    if hasattr(app.state, "limiter"):
        original_enabled = app.state.limiter.enabled
        app.state.limiter.enabled = False
    else:
        original_enabled = None

    yield

    # Restore rate limiter after test
    if original_enabled is not None:
        app.state.limiter.enabled = original_enabled


@pytest.fixture
async def client(setup_app_state):
    """Create async test client with proper dependency overrides."""
    # Override the authentication dependency
    app.dependency_overrides[get_current_user_dep] = lambda: MockUser(tenant_id="test-tenant")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def sample_farmer_data():
    """Sample farmer creation data."""
    return {
        "name": "Ahmed Mohammed",
        "name_ar": "أحمد محمد",
        "phone": "+966501234567",
        "email": "ahmed@example.com",
        "national_id": "1234567890",
        "farm_location": "Riyadh",
        "farm_location_ar": "الرياض",
        "farm_size_hectares": 25.5,
        "primary_crops": ["wheat", "barley"],
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def sample_deal_data():
    """Sample deal creation data."""
    return {
        "farmer_id": "",  # Will be set in tests
        "crop_type": "wheat",
        "crop_type_ar": "قمح",
        "expected_quantity_tons": 50.0,
        "expected_harvest_date": "2026-06-15",
        "price_per_ton": 1850.0,
        "notes": "First wheat deal",
        "notes_ar": "أول صفقة قمح",
    }


@pytest.fixture
def sample_interaction_data():
    """Sample interaction creation data."""
    return {
        "farmer_id": "",  # Will be set in tests
        "interaction_type": "call",
        "subject": "Follow-up on irrigation advice",
        "subject_ar": "متابعة نصيحة الري",
        "notes": "Farmer confirmed implementing the advice",
        "notes_ar": "أكد المزارع تطبيق النصيحة",
        "outcome": "positive",
        "follow_up_date": "2026-02-01",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoint Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test /healthz liveness probe."""
        response = await client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "crm-service"
        assert data["service_ar"] == "خدمة إدارة علاقات المزارعين"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_readiness_endpoint(self, client):
        """Test /readyz readiness probe."""
        response = await client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "nats" in data

    @pytest.mark.asyncio
    async def test_health_detailed_endpoint(self, client):
        """Test /health detailed status."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "crm-service"
        assert "farmers_count" in data
        assert "deals_count" in data

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client):
        """Test /metrics Prometheus endpoint."""
        response = await client.get("/metrics")

        assert response.status_code == 200
        content = response.text
        assert "crm_farmers_total" in content
        assert "crm_deals_total" in content
        assert "crm_interactions_total" in content


# ═══════════════════════════════════════════════════════════════════════════════
# Farmer Endpoint Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFarmerEndpoints:
    """Test farmer CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_farmer(self, client, sample_farmer_data):
        """Test POST /api/v1/farmers creates a farmer."""
        response = await client.post("/api/v1/farmers", json=sample_farmer_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_farmer_data["name"]
        assert data["name_ar"] == sample_farmer_data["name_ar"]
        assert data["phone"] == sample_farmer_data["phone"]
        assert data["email"] == sample_farmer_data["email"]
        assert data["status"] == "lead"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_farmer_minimal(self, client):
        """Test creating farmer with minimal required fields."""
        minimal_data = {
            "name": "Farmer Name",
            "phone": "+966509876543",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/farmers", json=minimal_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == minimal_data["name"]
        assert data["phone"] == minimal_data["phone"]
        assert data["name_ar"] is None
        assert data["email"] is None

    @pytest.mark.asyncio
    async def test_create_farmer_invalid_phone(self, client):
        """Test validation error for invalid phone number."""
        invalid_data = {
            "name": "Test Farmer",
            "phone": "invalid-phone",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/farmers", json=invalid_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_farmer_invalid_email(self, client):
        """Test validation error for invalid email."""
        invalid_data = {
            "name": "Test Farmer",
            "phone": "+966501234567",
            "email": "invalid-email",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/farmers", json=invalid_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_farmers(self, client, sample_farmer_data):
        """Test GET /api/v1/farmers lists farmers."""
        # Create a farmer first
        await client.post("/api/v1/farmers", json=sample_farmer_data)

        response = await client.get("/api/v1/farmers?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == sample_farmer_data["name"]

    @pytest.mark.asyncio
    async def test_list_farmers_empty(self, client):
        """Test listing farmers when none exist."""
        response = await client.get("/api/v1/farmers?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_list_farmers_with_status_filter(self, client, sample_farmer_data):
        """Test filtering farmers by status."""
        # Create a farmer
        await client.post("/api/v1/farmers", json=sample_farmer_data)

        # Filter by lead status (default)
        response = await client.get("/api/v1/farmers?tenant_id=test-tenant&status=lead")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Filter by active status (should be empty)
        response = await client.get("/api/v1/farmers?tenant_id=test-tenant&status=active")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_farmers_with_search(self, client, sample_farmer_data):
        """Test searching farmers by name."""
        # Create a farmer
        await client.post("/api/v1/farmers", json=sample_farmer_data)

        # Search by name
        response = await client.get("/api/v1/farmers?tenant_id=test-tenant&search=ahmed")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Search with no results
        response = await client.get("/api/v1/farmers?tenant_id=test-tenant&search=nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_farmers_pagination(self, client):
        """Test farmers list pagination."""
        # Create multiple farmers
        for i in range(5):
            await client.post(
                "/api/v1/farmers",
                json={
                    "name": f"Farmer {i}",
                    "phone": f"+96650123456{i}",
                    "tenant_id": "test-tenant",
                },
            )

        # Test limit
        response = await client.get("/api/v1/farmers?tenant_id=test-tenant&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Test offset
        response = await client.get("/api/v1/farmers?tenant_id=test-tenant&offset=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_get_farmer(self, client, sample_farmer_data):
        """Test GET /api/v1/farmers/{farmer_id}."""
        # Create a farmer first
        create_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = create_response.json()["id"]

        # Get the farmer (requires tenant_id query param)
        response = await client.get(f"/api/v1/farmers/{farmer_id}?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == farmer_id
        assert data["name"] == sample_farmer_data["name"]

    @pytest.mark.asyncio
    async def test_get_farmer_not_found(self, client):
        """Test getting non-existent farmer returns 404."""
        response = await client.get("/api/v1/farmers/nonexistent-id?tenant_id=test-tenant")

        assert response.status_code == 404
        # Check for error response structure
        data = response.json()
        assert "error" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_update_farmer(self, client, sample_farmer_data):
        """Test PATCH /api/v1/farmers/{farmer_id}."""
        # Create a farmer first
        create_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = create_response.json()["id"]

        # Update the farmer
        update_data = {
            "name": "Ahmed Updated",
            "status": "active",
            "farm_size_hectares": 50.0,
        }
        response = await client.patch(f"/api/v1/farmers/{farmer_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Ahmed Updated"
        assert data["status"] == "active"
        assert data["farm_size_hectares"] == 50.0
        # Check that other fields are preserved
        assert data["phone"] == sample_farmer_data["phone"]

    @pytest.mark.asyncio
    async def test_update_farmer_not_found(self, client):
        """Test updating non-existent farmer returns 404."""
        update_data = {"name": "Updated Name"}
        response = await client.patch("/api/v1/farmers/nonexistent-id", json=update_data)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_farmer_tags(self, client, sample_farmer_data):
        """Test updating farmer tags."""
        # Create a farmer first
        create_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = create_response.json()["id"]

        # Update tags
        update_data = {"tags": ["vip", "wheat-producer"]}
        response = await client.patch(f"/api/v1/farmers/{farmer_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["tags"] == ["vip", "wheat-producer"]


# ═══════════════════════════════════════════════════════════════════════════════
# Deal Endpoint Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDealEndpoints:
    """Test harvest deal endpoints."""

    @pytest.mark.asyncio
    async def test_create_deal(self, client, sample_farmer_data, sample_deal_data):
        """Test POST /api/v1/deals creates a deal."""
        # Create a farmer first
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        # Create a deal
        sample_deal_data["farmer_id"] = farmer_id
        response = await client.post("/api/v1/deals", json=sample_deal_data)

        assert response.status_code == 200
        data = response.json()
        assert data["farmer_id"] == farmer_id
        assert data["crop_type"] == sample_deal_data["crop_type"]
        assert data["expected_quantity_tons"] == sample_deal_data["expected_quantity_tons"]
        assert data["stage"] == "prospecting"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_deal_farmer_not_found(self, client, sample_deal_data):
        """Test creating deal for non-existent farmer returns 404."""
        sample_deal_data["farmer_id"] = "nonexistent-farmer"
        response = await client.post("/api/v1/deals", json=sample_deal_data)

        assert response.status_code == 404
        # Error detail includes the resource ID
        assert "Farmer not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_deal_invalid_quantity(self, client, sample_farmer_data):
        """Test validation error for invalid quantity."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        invalid_deal = {
            "farmer_id": farmer_id,
            "crop_type": "wheat",
            "expected_quantity_tons": -5.0,  # Invalid: must be > 0
            "expected_harvest_date": "2026-06-15",
        }
        response = await client.post("/api/v1/deals", json=invalid_deal)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_deals(self, client, sample_farmer_data, sample_deal_data):
        """Test GET /api/v1/deals lists deals."""
        # Create farmer and deal
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        await client.post("/api/v1/deals", json=sample_deal_data)

        response = await client.get("/api/v1/deals?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_list_deals_by_farmer(self, client, sample_farmer_data, sample_deal_data):
        """Test filtering deals by farmer_id."""
        # Create farmer and deal
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        await client.post("/api/v1/deals", json=sample_deal_data)

        response = await client.get(f"/api/v1/deals?tenant_id=test-tenant&farmer_id={farmer_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["farmer_id"] == farmer_id

    @pytest.mark.asyncio
    async def test_list_deals_by_stage(self, client, sample_farmer_data, sample_deal_data):
        """Test filtering deals by stage."""
        # Create farmer and deal
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        await client.post("/api/v1/deals", json=sample_deal_data)

        # Filter by prospecting stage
        response = await client.get("/api/v1/deals?tenant_id=test-tenant&stage=prospecting")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Filter by negotiation stage (should be empty)
        response = await client.get("/api/v1/deals?tenant_id=test-tenant&stage=negotiation")
        assert response.status_code == 200
        assert len(response.json()) == 0

    @pytest.mark.asyncio
    async def test_advance_deal_stage(self, client, sample_farmer_data, sample_deal_data):
        """Test PATCH /api/v1/deals/{deal_id}/stage."""
        # Create farmer and deal
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        deal_response = await client.post("/api/v1/deals", json=sample_deal_data)
        deal_id = deal_response.json()["id"]

        # Advance stage
        response = await client.patch(f"/api/v1/deals/{deal_id}/stage?stage=negotiation")

        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "negotiation"

    @pytest.mark.asyncio
    async def test_advance_deal_stage_not_found(self, client):
        """Test advancing stage of non-existent deal returns 404."""
        response = await client.patch("/api/v1/deals/nonexistent-id/stage?stage=negotiation")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_pipeline_summary(self, client, sample_farmer_data, sample_deal_data):
        """Test GET /api/v1/deals/pipeline."""
        # Create farmer and deals
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id

        # Create multiple deals in different stages
        deal1 = await client.post("/api/v1/deals", json=sample_deal_data)
        deal2 = await client.post("/api/v1/deals", json={**sample_deal_data, "price_per_ton": 2000.0})

        # Move one to negotiation
        await client.patch(f"/api/v1/deals/{deal2.json()['id']}/stage?stage=negotiation")

        response = await client.get("/api/v1/deals/pipeline?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert data["total_deals"] == 2
        assert "by_stage" in data
        assert data["by_stage"]["prospecting"]["count"] == 1
        assert data["by_stage"]["negotiation"]["count"] == 1
        assert "conversion_rate" in data
        assert "average_deal_size" in data


# ═══════════════════════════════════════════════════════════════════════════════
# Interaction Endpoint Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestInteractionEndpoints:
    """Test interaction logging endpoints."""

    @pytest.mark.asyncio
    async def test_log_interaction(self, client, sample_farmer_data, sample_interaction_data):
        """Test POST /api/v1/interactions."""
        # Create a farmer first
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        # Log interaction
        sample_interaction_data["farmer_id"] = farmer_id
        response = await client.post("/api/v1/interactions", json=sample_interaction_data)

        assert response.status_code == 200
        data = response.json()
        assert data["farmer_id"] == farmer_id
        assert data["subject"] == sample_interaction_data["subject"]
        assert data["interaction_type"] == "call"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_log_interaction_farmer_not_found(self, client, sample_interaction_data):
        """Test logging interaction for non-existent farmer returns 404."""
        sample_interaction_data["farmer_id"] = "nonexistent-farmer"
        response = await client.post("/api/v1/interactions", json=sample_interaction_data)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_log_interaction_updates_farmer_last_interaction(
        self, client, sample_farmer_data, sample_interaction_data
    ):
        """Test that logging interaction updates farmer's last_interaction_at."""
        # Create a farmer first
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        # Check initial last_interaction_at is None
        initial_farmer = await client.get(f"/api/v1/farmers/{farmer_id}?tenant_id=test-tenant")
        assert initial_farmer.json()["last_interaction_at"] is None

        # Log interaction
        sample_interaction_data["farmer_id"] = farmer_id
        await client.post("/api/v1/interactions", json=sample_interaction_data)

        # Check last_interaction_at is updated
        updated_farmer = await client.get(f"/api/v1/farmers/{farmer_id}?tenant_id=test-tenant")
        assert updated_farmer.json()["last_interaction_at"] is not None

    @pytest.mark.asyncio
    async def test_get_farmer_interactions(self, client, sample_farmer_data, sample_interaction_data):
        """Test GET /api/v1/interactions."""
        # Create a farmer and interactions
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        # Log multiple interactions
        sample_interaction_data["farmer_id"] = farmer_id
        await client.post("/api/v1/interactions", json=sample_interaction_data)
        await client.post(
            "/api/v1/interactions",
            json={
                **sample_interaction_data,
                "subject": "Another interaction",
                "interaction_type": "visit",
            },
        )

        response = await client.get(f"/api/v1/interactions?farmer_id={farmer_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_farmer_interactions_filter_by_type(self, client, sample_farmer_data, sample_interaction_data):
        """Test filtering interactions by type."""
        # Create a farmer and interactions
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        # Log interactions of different types
        sample_interaction_data["farmer_id"] = farmer_id
        await client.post("/api/v1/interactions", json=sample_interaction_data)  # call
        await client.post(
            "/api/v1/interactions",
            json={
                **sample_interaction_data,
                "interaction_type": "visit",
            },
        )

        # Filter by call
        response = await client.get(f"/api/v1/interactions?farmer_id={farmer_id}&interaction_type=call")
        assert response.status_code == 200
        assert len(response.json()) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Natural Language Query Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestNaturalLanguageQuery:
    """Test natural language query endpoint."""

    @pytest.mark.asyncio
    async def test_natural_language_query_active_farmers(self, client, sample_farmer_data):
        """Test querying for active farmers."""
        # Create and activate a farmer
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        await client.patch(f"/api/v1/farmers/{farmer_id}", json={"status": "active"})

        query_data = {
            "query": "Show me all active farmers",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "result_count" in data
        assert data["result_count"] == 1
        assert "interpreted_as" in data
        assert "interpreted_as_ar" in data

    @pytest.mark.asyncio
    async def test_natural_language_query_arabic(self, client, sample_farmer_data):
        """Test querying in Arabic."""
        # Create and activate a farmer
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        await client.patch(f"/api/v1/farmers/{farmer_id}", json={"status": "active"})

        query_data = {
            "query": "أرني جميع المزارعين النشطين",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert data["result_count"] >= 0

    @pytest.mark.asyncio
    async def test_natural_language_query_lead_farmers(self, client, sample_farmer_data):
        """Test querying for lead farmers."""
        await client.post("/api/v1/farmers", json=sample_farmer_data)

        query_data = {
            "query": "Show me lead farmers",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert data["result_count"] == 1

    @pytest.mark.asyncio
    async def test_natural_language_query_deals(self, client, sample_farmer_data, sample_deal_data):
        """Test querying for deals."""
        # Create farmer and deal
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        await client.post("/api/v1/deals", json=sample_deal_data)

        query_data = {
            "query": "Show me all deals",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert data["result_count"] == 1

    @pytest.mark.asyncio
    async def test_natural_language_query_deals_in_negotiation(self, client, sample_farmer_data, sample_deal_data):
        """Test querying for deals in negotiation stage."""
        # Create farmer and deal
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        deal_response = await client.post("/api/v1/deals", json=sample_deal_data)
        deal_id = deal_response.json()["id"]

        # Advance to negotiation
        await client.patch(f"/api/v1/deals/{deal_id}/stage?stage=negotiation")

        query_data = {
            "query": "deals in negotiation",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert data["result_count"] == 1
        assert "negotiation" in data["interpreted_as"]

    @pytest.mark.asyncio
    async def test_natural_language_query_unknown_pattern(self, client):
        """Test handling of unknown query patterns."""
        query_data = {
            "query": "xyz unknown query abc",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert "Unknown query pattern" in data["interpreted_as"]

    @pytest.mark.asyncio
    async def test_natural_language_query_execution_time(self, client):
        """Test that execution time is reported."""
        query_data = {
            "query": "Show me all farmers",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert "execution_time_ms" in data
        assert isinstance(data["execution_time_ms"], int)


# ═══════════════════════════════════════════════════════════════════════════════
# Pipeline Summary Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineSummary:
    """Test pipeline statistics endpoint."""

    @pytest.mark.asyncio
    async def test_get_pipeline_summary_empty(self, client):
        """Test pipeline summary with no deals."""
        response = await client.get("/api/v1/deals/pipeline?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert data["total_deals"] == 0
        assert data["total_value"] == 0
        assert data["conversion_rate"] == 0
        assert data["average_deal_size"] == 0

    @pytest.mark.asyncio
    async def test_get_pipeline_summary_by_stage(self, client, sample_farmer_data, sample_deal_data):
        """Test pipeline summary shows correct stage breakdown."""
        # Create farmer
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id

        # Create deals in various stages
        deal1 = await client.post("/api/v1/deals", json=sample_deal_data)
        deal2 = await client.post("/api/v1/deals", json=sample_deal_data)
        deal3 = await client.post("/api/v1/deals", json=sample_deal_data)

        # Advance some deals
        await client.patch(f"/api/v1/deals/{deal2.json()['id']}/stage?stage=contracted")
        await client.patch(f"/api/v1/deals/{deal3.json()['id']}/stage?stage=paid")

        response = await client.get("/api/v1/deals/pipeline?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        assert data["total_deals"] == 3
        assert data["by_stage"]["prospecting"]["count"] == 1
        assert data["by_stage"]["contracted"]["count"] == 1
        assert data["by_stage"]["paid"]["count"] == 1
        # Conversion rate should be 1/3 * 100 = 33.33%
        assert data["conversion_rate"] > 33 and data["conversion_rate"] < 34

    @pytest.mark.asyncio
    async def test_get_pipeline_summary_arabic_names(self, client, sample_farmer_data, sample_deal_data):
        """Test pipeline summary includes Arabic stage names."""
        # Create farmer and deal
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        await client.post("/api/v1/deals", json=sample_deal_data)

        response = await client.get("/api/v1/deals/pipeline?tenant_id=test-tenant")

        assert response.status_code == 200
        data = response.json()
        # Check Arabic names are present
        assert data["by_stage"]["prospecting"]["name_ar"] == "استكشاف"


# ═══════════════════════════════════════════════════════════════════════════════
# Additional Edge Case Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_create_farmer_with_all_fields(self, client):
        """Test creating farmer with all optional fields."""
        full_data = {
            "name": "Complete Farmer",
            "name_ar": "مزارع كامل",
            "phone": "+966501234567",
            "email": "complete@example.com",
            "national_id": "1234567890",
            "farm_location": "Riyadh",
            "farm_location_ar": "الرياض",
            "farm_size_hectares": 100.5,
            "primary_crops": ["wheat", "barley", "dates"],
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/farmers", json=full_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == full_data["name"]
        assert data["name_ar"] == full_data["name_ar"]
        assert data["farm_size_hectares"] == full_data["farm_size_hectares"]
        assert len(data["primary_crops"]) == 3

    @pytest.mark.asyncio
    async def test_create_deal_without_optional_fields(self, client, sample_farmer_data):
        """Test creating deal with only required fields."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        minimal_deal = {
            "farmer_id": farmer_id,
            "crop_type": "wheat",
            "expected_quantity_tons": 10.0,
            "expected_harvest_date": "2026-06-15",
        }
        response = await client.post("/api/v1/deals", json=minimal_deal)

        assert response.status_code == 200
        data = response.json()
        assert data["price_per_ton"] is None
        assert data["notes"] is None

    @pytest.mark.asyncio
    async def test_search_farmers_by_phone(self, client, sample_farmer_data):
        """Test searching farmers by phone number."""
        await client.post("/api/v1/farmers", json=sample_farmer_data)

        # Search by phone
        response = await client.get("/api/v1/farmers?tenant_id=test-tenant&search=501234567")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_update_farmer_primary_crops(self, client, sample_farmer_data):
        """Test updating farmer's primary crops."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        update_data = {"primary_crops": ["tomatoes", "cucumbers"]}
        response = await client.patch(f"/api/v1/farmers/{farmer_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["primary_crops"] == ["tomatoes", "cucumbers"]

    @pytest.mark.asyncio
    async def test_interaction_with_follow_up_date(self, client, sample_farmer_data):
        """Test creating interaction with follow-up date."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        interaction_data = {
            "farmer_id": farmer_id,
            "interaction_type": "visit",
            "subject": "Field inspection",
            "follow_up_date": "2026-02-15",
        }
        response = await client.post("/api/v1/interactions", json=interaction_data)

        assert response.status_code == 200
        data = response.json()
        assert data["follow_up_date"] == "2026-02-15"

    @pytest.mark.asyncio
    async def test_deal_value_calculation(self, client, sample_farmer_data):
        """Test deal value is calculated correctly in pipeline."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]

        # Create deal with known values
        deal_data = {
            "farmer_id": farmer_id,
            "crop_type": "wheat",
            "expected_quantity_tons": 100.0,
            "expected_harvest_date": "2026-06-15",
            "price_per_ton": 2000.0,
        }
        await client.post("/api/v1/deals", json=deal_data)

        # Check pipeline value
        response = await client.get("/api/v1/deals/pipeline?tenant_id=test-tenant")
        data = response.json()

        # Value should be 100 * 2000 = 200,000
        assert data["total_value"] == 200000.0
        assert data["by_stage"]["prospecting"]["total_value"] == 200000.0


# ═══════════════════════════════════════════════════════════════════════════════
# Security and Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSecurityAndValidation:
    """Tests for security features and input validation."""

    @pytest.mark.asyncio
    async def test_query_too_long(self, client):
        """Test query length validation (max 500 chars)."""
        long_query = "Show me farmers " * 50  # > 500 chars
        query_data = {
            "query": long_query,
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 400
        data = response.json()
        assert "too long" in data["error"].lower() or "too long" in data.get("detail", "").lower()

    @pytest.mark.asyncio
    async def test_query_too_complex(self, client):
        """Test query complexity validation (max 5 conditions)."""
        # Query with more than 5 and/or conditions
        # The check_query_complexity function counts: and, or, و, أو
        complex_query = "farmers and wheat and barley and dates and tomatoes and cucumbers and carrots"
        query_data = {
            "query": complex_query,
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 400
        data = response.json()
        assert "complex" in data["error"].lower() or "complex" in data.get("detail", "").lower()

    @pytest.mark.asyncio
    async def test_query_sanitization_removes_sql_keywords(self, client, sample_farmer_data):
        """Test that dangerous SQL keywords are removed from queries."""
        await client.post("/api/v1/farmers", json=sample_farmer_data)

        # Query with SQL injection attempt
        query_data = {
            "query": "Show me farmers; DROP TABLE farmers;",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        # Should not crash, dangerous patterns removed
        assert response.status_code == 200
        # Result should still work but without dangerous patterns

    @pytest.mark.asyncio
    async def test_tenant_access_denied_on_farmer_list(self, client, sample_farmer_data):
        """Test tenant access validation on farmer list."""
        # Create farmer with one tenant
        await client.post("/api/v1/farmers", json=sample_farmer_data)

        # Try to access with different tenant (dependency override still uses test-tenant)
        # This test verifies the tenant_id parameter is checked
        response = await client.get("/api/v1/farmers?tenant_id=other-tenant")

        # Should get 403 Forbidden
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_tenant_access_denied_on_deals_list(self, client, sample_farmer_data, sample_deal_data):
        """Test tenant access validation on deals list."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        await client.post("/api/v1/deals", json=sample_deal_data)

        # Try to access deals with wrong tenant
        response = await client.get("/api/v1/deals?tenant_id=other-tenant")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_tenant_access_denied_on_pipeline(self, client):
        """Test tenant access validation on pipeline stats."""
        response = await client.get("/api/v1/deals/pipeline?tenant_id=wrong-tenant")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_tenant_access_denied_on_query(self, client):
        """Test tenant access validation on NLQ."""
        query_data = {
            "query": "Show me all farmers",
            "tenant_id": "wrong-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# Additional Response Format Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestResponseFormats:
    """Tests for API response formats and error responses."""

    @pytest.mark.asyncio
    async def test_error_response_structure_404(self, client):
        """Test 404 error response has correct structure."""
        response = await client.get("/api/v1/farmers/nonexistent?tenant_id=test-tenant")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "error_ar" in data
        assert "error_code" in data
        assert data["error_code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_error_response_structure_403(self, client):
        """Test 403 error response has correct structure."""
        response = await client.get("/api/v1/farmers?tenant_id=wrong-tenant")

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert "error_ar" in data
        assert data["error_ar"] == "تم رفض الوصول"
        assert data["error_code"] == "FORBIDDEN"

    @pytest.mark.asyncio
    async def test_request_id_in_response_headers(self, client):
        """Test X-Request-ID is present in response headers."""
        response = await client.get("/healthz")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_custom_request_id_preserved(self, client):
        """Test custom X-Request-ID is preserved in response."""
        custom_id = "my-custom-request-id-12345"
        response = await client.get("/healthz", headers={"X-Request-ID": custom_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

    @pytest.mark.asyncio
    async def test_farmer_response_has_all_fields(self, client, sample_farmer_data):
        """Test farmer response includes all expected fields."""
        response = await client.post("/api/v1/farmers", json=sample_farmer_data)

        assert response.status_code == 200
        data = response.json()

        # Check all expected fields
        expected_fields = [
            "id",
            "name",
            "name_ar",
            "phone",
            "email",
            "national_id",
            "farm_location",
            "farm_location_ar",
            "farm_size_hectares",
            "primary_crops",
            "status",
            "tags",
            "created_at",
            "updated_at",
            "last_interaction_at",
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_deal_response_has_all_fields(self, client, sample_farmer_data, sample_deal_data):
        """Test deal response includes all expected fields."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id

        response = await client.post("/api/v1/deals", json=sample_deal_data)

        assert response.status_code == 200
        data = response.json()

        # Check all expected fields
        expected_fields = [
            "id",
            "farmer_id",
            "crop_type",
            "crop_type_ar",
            "expected_quantity_tons",
            "actual_quantity_tons",
            "expected_harvest_date",
            "actual_harvest_date",
            "price_per_ton",
            "total_value",
            "stage",
            "notes",
            "notes_ar",
            "created_at",
            "updated_at",
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_interaction_response_has_all_fields(self, client, sample_farmer_data, sample_interaction_data):
        """Test interaction response includes all expected fields."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_interaction_data["farmer_id"] = farmer_id

        response = await client.post("/api/v1/interactions", json=sample_interaction_data)

        assert response.status_code == 200
        data = response.json()

        # Check all expected fields
        expected_fields = [
            "id",
            "farmer_id",
            "interaction_type",
            "subject",
            "subject_ar",
            "notes",
            "notes_ar",
            "outcome",
            "follow_up_date",
            "created_at",
            "created_by",
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"


# ═══════════════════════════════════════════════════════════════════════════════
# Additional NLQ Pattern Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestNLQPatterns:
    """Additional tests for NLQ pattern matching."""

    @pytest.mark.asyncio
    async def test_query_farmers_by_location_arabic(self, client, sample_farmer_data):
        """Test querying with Arabic location term."""
        await client.post("/api/v1/farmers", json=sample_farmer_data)

        query_data = {
            "query": "المزارعين",  # "farmers" in Arabic
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert data["result_count"] >= 0

    @pytest.mark.asyncio
    async def test_query_deals_by_crop_type(self, client, sample_farmer_data, sample_deal_data):
        """Test querying deals by crop type."""
        farmer_response = await client.post("/api/v1/farmers", json=sample_farmer_data)
        farmer_id = farmer_response.json()["id"]
        sample_deal_data["farmer_id"] = farmer_id
        await client.post("/api/v1/deals", json=sample_deal_data)

        query_data = {
            "query": "wheat deals",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        # Should find deals containing wheat
        assert data["result_count"] >= 0

    @pytest.mark.asyncio
    async def test_query_result_count_matches_results_length(self, client, sample_farmer_data):
        """Test that result_count matches actual results length."""
        # Create multiple farmers
        for i in range(3):
            data = {**sample_farmer_data, "phone": f"+96650123456{i}"}
            await client.post("/api/v1/farmers", json=data)

        query_data = {
            "query": "Show all farmers",
            "tenant_id": "test-tenant",
        }
        response = await client.post("/api/v1/query", json=query_data)

        assert response.status_code == 200
        data = response.json()
        assert data["result_count"] == len(data["results"])
