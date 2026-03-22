"""
CRM Service Test Fixtures
=========================
Shared fixtures for testing CRM service endpoints.

Author: SAHOOL Platform Team
"""

import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import sys
from datetime import date, datetime
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""


# ═══════════════════════════════════════════════════════════════════════════════
# Mock shared.crm Module
# ═══════════════════════════════════════════════════════════════════════════════


class MockFarmerStatus:
    """Mock FarmerStatus enum."""

    LEAD = "lead"
    REGISTERED = "registered"
    ACTIVE = "active"
    PREMIUM = "premium"
    CHURNED = "churned"


class MockDealStage:
    """Mock DealStage enum."""

    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEGOTIATION = "negotiation"
    CONTRACTED = "contracted"
    DELIVERED = "delivered"
    PAID = "paid"
    CLOSED_LOST = "closed_lost"

    def __iter__(self):
        return iter(
            [
                self.PROSPECTING,
                self.QUALIFICATION,
                self.NEGOTIATION,
                self.CONTRACTED,
                self.DELIVERED,
                self.PAID,
                self.CLOSED_LOST,
            ]
        )


class MockInteractionType:
    """Mock InteractionType enum."""

    ADVISORY = "advisory"
    SUPPORT = "support"
    SALES = "sales"
    TRAINING = "training"
    INSPECTION = "inspection"
    CALL = "call"
    VISIT = "visit"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"


class MockFarmer:
    """Mock Farmer model."""

    def __init__(
        self,
        id: str,
        name: str,
        phone: str,
        name_ar: str | None = None,
        email: str | None = None,
        national_id: str | None = None,
        farm_location: str | None = None,
        farm_location_ar: str | None = None,
        farm_size_hectares: float | None = None,
        primary_crops: list[str] | None = None,
        status: str = "lead",
        tags: list[str] | None = None,
        tenant_id: str = "test-tenant",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        last_interaction_at: datetime | None = None,
    ):
        self.id = id
        self.name = name
        self.name_ar = name_ar
        self.phone = phone
        self.email = email
        self.national_id = national_id
        self.farm_location = farm_location
        self.farm_location_ar = farm_location_ar
        self.farm_size_hectares = farm_size_hectares
        self.primary_crops = primary_crops or []
        self.status = MockFarmerStatusEnum(status)
        self.tags = tags or []
        self.tenant_id = tenant_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_interaction_at = last_interaction_at


class MockFarmerStatusEnum:
    """Mock FarmerStatus enum value."""

    def __init__(self, value: str):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, MockFarmerStatusEnum):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self):
        return hash(self.value)


class MockDealStageEnum:
    """Mock DealStage enum value."""

    def __init__(self, value: str):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, MockDealStageEnum):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self):
        return hash(self.value)


class MockInteractionTypeEnum:
    """Mock InteractionType enum value."""

    def __init__(self, value: str):
        self.value = value


class MockHarvestDeal:
    """Mock HarvestDeal model."""

    def __init__(
        self,
        id: str,
        farmer_id: str,
        crop_type: str,
        expected_quantity_tons: float,
        expected_harvest_date: date,
        crop_type_ar: str | None = None,
        actual_quantity_tons: float | None = None,
        actual_harvest_date: date | None = None,
        price_per_ton: float | None = None,
        total_value: float | None = None,
        stage: str = "prospecting",
        notes: str | None = None,
        notes_ar: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id
        self.farmer_id = farmer_id
        self.crop_type = crop_type
        self.crop_type_ar = crop_type_ar
        self.expected_quantity_tons = expected_quantity_tons
        self.actual_quantity_tons = actual_quantity_tons
        self.expected_harvest_date = expected_harvest_date
        self.actual_harvest_date = actual_harvest_date
        self.price_per_ton = price_per_ton
        self.total_value = total_value
        self.stage = MockDealStageEnum(stage)
        self.notes = notes
        self.notes_ar = notes_ar
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()


class MockInteraction:
    """Mock Interaction model."""

    def __init__(
        self,
        id: str,
        farmer_id: str,
        interaction_type: str,
        subject: str,
        subject_ar: str | None = None,
        notes: str | None = None,
        notes_ar: str | None = None,
        outcome: str | None = None,
        follow_up_date: date | None = None,
        created_at: datetime | None = None,
        created_by: str | None = None,
    ):
        self.id = id
        self.farmer_id = farmer_id
        self.interaction_type = MockInteractionTypeEnum(interaction_type)
        self.subject = subject
        self.subject_ar = subject_ar
        self.notes = notes
        self.notes_ar = notes_ar
        self.outcome = outcome
        self.follow_up_date = follow_up_date
        self.created_at = created_at or datetime.utcnow()
        self.created_by = created_by


# Create mock enums with proper enum-like behavior
class FarmerStatusEnum:
    LEAD = MockFarmerStatusEnum("lead")
    REGISTERED = MockFarmerStatusEnum("registered")
    ACTIVE = MockFarmerStatusEnum("active")
    PREMIUM = MockFarmerStatusEnum("premium")
    CHURNED = MockFarmerStatusEnum("churned")

    def __call__(self, value: str):
        return MockFarmerStatusEnum(value)


class DealStageEnum:
    PROSPECTING = MockDealStageEnum("prospecting")
    QUALIFICATION = MockDealStageEnum("qualification")
    NEGOTIATION = MockDealStageEnum("negotiation")
    CONTRACTED = MockDealStageEnum("contracted")
    DELIVERED = MockDealStageEnum("delivered")
    PAID = MockDealStageEnum("paid")
    CLOSED_LOST = MockDealStageEnum("closed_lost")

    def __call__(self, value: str):
        return MockDealStageEnum(value)

    def __iter__(self):
        return iter(
            [
                self.PROSPECTING,
                self.QUALIFICATION,
                self.NEGOTIATION,
                self.CONTRACTED,
                self.DELIVERED,
                self.PAID,
                self.CLOSED_LOST,
            ]
        )


class InteractionTypeEnum:
    ADVISORY = MockInteractionTypeEnum("advisory")
    SUPPORT = MockInteractionTypeEnum("support")
    SALES = MockInteractionTypeEnum("sales")
    TRAINING = MockInteractionTypeEnum("training")
    INSPECTION = MockInteractionTypeEnum("inspection")
    CALL = MockInteractionTypeEnum("call")
    VISIT = MockInteractionTypeEnum("visit")
    WHATSAPP = MockInteractionTypeEnum("whatsapp")
    SMS = MockInteractionTypeEnum("sms")
    EMAIL = MockInteractionTypeEnum("email")

    def __call__(self, value: str):
        return MockInteractionTypeEnum(value)


# Mock services
class MockFarmerCRMService:
    """Mock FarmerCRMService."""

    def __init__(self, tenant_id: str = "sahool"):
        self.tenant_id = tenant_id
        self._farmers = {}
        self._deals = {}
        self._interactions = {}


class MockFarmerQueryBot:
    """Mock FarmerQueryBot."""

    def __init__(self, crm_service: MockFarmerCRMService):
        self.crm = crm_service

    async def query(self, natural_query: str) -> dict:
        return {
            "query_type": "mock",
            "results": [],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def mock_crm_module():
    """Create mock CRM module."""
    mock_module = MagicMock()
    mock_module.FarmerCRMService = MockFarmerCRMService
    mock_module.FarmerQueryBot = MockFarmerQueryBot
    mock_module.Farmer = MockFarmer
    mock_module.FarmerStatus = FarmerStatusEnum()
    mock_module.HarvestDeal = MockHarvestDeal
    mock_module.DealStage = DealStageEnum()
    mock_module.Interaction = MockInteraction
    mock_module.InteractionType = InteractionTypeEnum()
    return mock_module


@pytest.fixture(scope="session")
def mock_auth():
    """Create mock auth dependencies."""
    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_user.tenant_id = "test-tenant"
    mock_user.email = "test@example.com"

    async def mock_get_current_user():
        return mock_user

    return {
        "get_current_user": mock_get_current_user,
        "User": MagicMock,
    }


@pytest.fixture
def app(mock_crm_module, mock_auth):
    """Create FastAPI test application with mocked dependencies."""
    # Patch the imports before importing main
    with patch.dict(
        "sys.modules",
        {
            "shared.crm": mock_crm_module,
            "shared.auth.dependencies": MagicMock(get_current_user=mock_auth["get_current_user"]),
            "shared.auth.models": MagicMock(User=mock_auth["User"]),
        },
    ):
        # Import after patching
        from apps.services.crm_service.src import main

        # Clear in-memory storage for each test
        main.farmers.clear()
        main.deals.clear()
        main.interactions.clear()

        yield main.app


@pytest.fixture
async def client(app) -> AsyncClient:
    """Create async test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_farmer_data() -> dict:
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
def sample_deal_data() -> dict:
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
def sample_interaction_data() -> dict:
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


@pytest.fixture
def sample_query_data() -> dict:
    """Sample NLQ query data."""
    return {
        "query": "Show me all active farmers",
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def created_farmer(sample_farmer_data) -> dict:
    """Create a farmer and return response data."""
    return {
        "id": "test-farmer-id",
        "name": sample_farmer_data["name"],
        "name_ar": sample_farmer_data["name_ar"],
        "phone": sample_farmer_data["phone"],
        "email": sample_farmer_data["email"],
        "national_id": sample_farmer_data["national_id"],
        "farm_location": sample_farmer_data["farm_location"],
        "farm_location_ar": sample_farmer_data["farm_location_ar"],
        "farm_size_hectares": sample_farmer_data["farm_size_hectares"],
        "primary_crops": sample_farmer_data["primary_crops"],
        "status": "lead",
        "tags": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "last_interaction_at": None,
    }
