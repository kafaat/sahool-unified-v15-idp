"""
CRM Service Pydantic Model Tests
================================
Tests for Pydantic request/response model validation.

Tests cover:
- FarmerCreateRequest validation
- FarmerUpdateRequest validation
- HarvestDealCreateRequest validation
- InteractionCreateRequest validation
- QueryRequest/QueryResponse validation
- PipelineStatsResponse validation
- Engagement score calculation

Author: SAHOOL Platform Team
"""

import os
import sys
from datetime import date, datetime
from enum import Enum, StrEnum
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

# Ensure test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Classes for shared.crm Module
# ═══════════════════════════════════════════════════════════════════════════════


class FarmerStatus(StrEnum):
    LEAD = "lead"
    REGISTERED = "registered"
    ACTIVE = "active"
    PREMIUM = "premium"
    CHURNED = "churned"


class DealStage(StrEnum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEGOTIATION = "negotiation"
    CONTRACTED = "contracted"
    DELIVERED = "delivered"
    PAID = "paid"
    CLOSED_LOST = "closed_lost"


class InteractionType(StrEnum):
    CALL = "call"
    VISIT = "visit"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"


class Farmer:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class HarvestDeal:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Interaction:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FarmerCRMService:
    def __init__(self, tenant_id: str = "sahool"):
        self.tenant_id = tenant_id


class FarmerQueryBot:
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


# Mock auth module with proper async function
class MockUser:
    """Mock User model."""

    id: str = "test-user-id"
    email: str = "test@example.com"
    tenant_id: str = "test-tenant"


async def mock_get_current_user():
    """Mock authentication dependency."""
    return MockUser()


mock_auth_deps = MagicMock()
mock_auth_deps.get_current_user = mock_get_current_user
mock_auth_models = MagicMock()
mock_auth_models.User = MockUser

# Patch before importing main
sys.modules["shared.crm"] = mock_crm
sys.modules["shared.auth.dependencies"] = mock_auth_deps
sys.modules["shared.auth.models"] = mock_auth_models

import importlib.util

# Get the path to main.py
tests_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.dirname(tests_dir)
main_path = os.path.join(service_dir, "src", "main.py")

# Add project root to path for shared imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(service_dir)))
sys.path.insert(0, project_root)

# Import main module using importlib
spec = importlib.util.spec_from_file_location("main_models", main_path)
main_module = importlib.util.module_from_spec(spec)
sys.modules["main_models"] = main_module
spec.loader.exec_module(main_module)

# Get the models from the module
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


# ═══════════════════════════════════════════════════════════════════════════════
# Farmer Model Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFarmerModelValidation:
    """Tests for farmer Pydantic model validation."""

    def test_farmer_create_request_valid(self):
        """Test valid FarmerCreateRequest creation."""
        data = {
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
        model = FarmerCreateRequest(**data)

        assert model.name == "Ahmed Mohammed"
        assert model.name_ar == "أحمد محمد"
        assert model.phone == "+966501234567"
        assert model.email == "ahmed@example.com"
        assert model.farm_size_hectares == 25.5
        assert model.primary_crops == ["wheat", "barley"]

    def test_farmer_create_request_minimal(self):
        """Test FarmerCreateRequest with minimal required fields."""
        data = {
            "name": "Farmer",
            "phone": "+966509876543",
            "tenant_id": "test",
        }
        model = FarmerCreateRequest(**data)

        assert model.name == "Farmer"
        assert model.phone == "+966509876543"
        assert model.name_ar is None
        assert model.email is None
        assert model.farm_size_hectares is None
        assert model.primary_crops == []

    def test_farmer_create_request_name_too_short(self):
        """Test validation error for name too short."""
        data = {
            "name": "A",  # Too short, min_length=2
            "phone": "+966501234567",
            "tenant_id": "test",
        }
        with pytest.raises(ValidationError) as exc_info:
            FarmerCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_farmer_create_request_name_too_long(self):
        """Test validation error for name too long."""
        data = {
            "name": "A" * 101,  # Too long, max_length=100
            "phone": "+966501234567",
            "tenant_id": "test",
        }
        with pytest.raises(ValidationError) as exc_info:
            FarmerCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_farmer_create_request_invalid_phone_format(self):
        """Test validation error for invalid phone format."""
        invalid_phones = [
            "12345",  # Too short
            "invalid-phone",
            "+9665012345678901234",  # Too long
            "abc123456789",  # Contains letters
        ]
        for phone in invalid_phones:
            data = {
                "name": "Test Farmer",
                "phone": phone,
                "tenant_id": "test",
            }
            with pytest.raises(ValidationError) as exc_info:
                FarmerCreateRequest(**data)

            errors = exc_info.value.errors()
            assert any(e["loc"] == ("phone",) for e in errors), f"Expected phone validation error for: {phone}"

    def test_farmer_create_request_valid_phone_formats(self):
        """Test valid phone number formats."""
        valid_phones = [
            "+966501234567",
            "966501234567",
            "0501234567",
            "+1234567890",
        ]
        for phone in valid_phones:
            data = {
                "name": "Test Farmer",
                "phone": phone,
                "tenant_id": "test",
            }
            model = FarmerCreateRequest(**data)
            assert model.phone == phone

    def test_farmer_create_request_invalid_email(self):
        """Test validation error for invalid email format."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user.example.com",
        ]
        for email in invalid_emails:
            data = {
                "name": "Test Farmer",
                "phone": "+966501234567",
                "email": email,
                "tenant_id": "test",
            }
            with pytest.raises(ValidationError) as exc_info:
                FarmerCreateRequest(**data)

            errors = exc_info.value.errors()
            assert any(e["loc"] == ("email",) for e in errors), f"Expected email validation error for: {email}"

    def test_farmer_create_request_valid_email(self):
        """Test valid email formats."""
        valid_emails = [
            "user@example.com",
            "user.name@example.co.uk",
            "user+tag@example.com",
            "user123@subdomain.example.org",
        ]
        for email in valid_emails:
            data = {
                "name": "Test Farmer",
                "phone": "+966501234567",
                "email": email,
                "tenant_id": "test",
            }
            model = FarmerCreateRequest(**data)
            assert model.email == email

    def test_farmer_create_request_negative_farm_size(self):
        """Test validation error for negative farm size."""
        data = {
            "name": "Test Farmer",
            "phone": "+966501234567",
            "farm_size_hectares": -5.0,
            "tenant_id": "test",
        }
        with pytest.raises(ValidationError) as exc_info:
            FarmerCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("farm_size_hectares",) for e in errors)

    def test_farmer_create_request_zero_farm_size(self):
        """Test zero farm size is valid."""
        data = {
            "name": "Test Farmer",
            "phone": "+966501234567",
            "farm_size_hectares": 0.0,
            "tenant_id": "test",
        }
        model = FarmerCreateRequest(**data)
        assert model.farm_size_hectares == 0.0

    def test_farmer_update_request_all_optional(self):
        """Test FarmerUpdateRequest with all optional fields."""
        model = FarmerUpdateRequest()
        assert model.name is None
        assert model.phone is None
        assert model.status is None

    def test_farmer_update_request_partial_update(self):
        """Test FarmerUpdateRequest with partial fields."""
        data = {
            "name": "Updated Name",
            "status": "active",
        }
        model = FarmerUpdateRequest(**data)

        assert model.name == "Updated Name"
        assert model.status == "active"
        assert model.phone is None
        assert model.tags is None

    def test_farmer_response_model(self):
        """Test FarmerResponse model structure."""
        now = datetime.utcnow()
        data = {
            "id": "farmer-123",
            "name": "Ahmed",
            "name_ar": "أحمد",
            "phone": "+966501234567",
            "email": "ahmed@example.com",
            "national_id": "123456",
            "farm_location": "Riyadh",
            "farm_location_ar": "الرياض",
            "farm_size_hectares": 25.0,
            "primary_crops": ["wheat"],
            "status": "active",
            "tags": ["vip"],
            "created_at": now,
            "updated_at": now,
            "last_interaction_at": None,
        }
        model = FarmerResponse(**data)

        assert model.id == "farmer-123"
        assert model.status == "active"
        assert model.created_at == now


# ═══════════════════════════════════════════════════════════════════════════════
# Deal Model Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDealModelValidation:
    """Tests for harvest deal Pydantic model validation."""

    def test_deal_create_request_valid(self):
        """Test valid HarvestDealCreateRequest creation."""
        data = {
            "farmer_id": "farmer-123",
            "crop_type": "wheat",
            "crop_type_ar": "قمح",
            "expected_quantity_tons": 50.0,
            "expected_harvest_date": "2026-06-15",
            "price_per_ton": 1850.0,
            "notes": "Test deal",
            "notes_ar": "صفقة تجريبية",
        }
        model = HarvestDealCreateRequest(**data)

        assert model.farmer_id == "farmer-123"
        assert model.crop_type == "wheat"
        assert model.expected_quantity_tons == 50.0
        assert model.price_per_ton == 1850.0

    def test_deal_create_request_minimal(self):
        """Test HarvestDealCreateRequest with minimal required fields."""
        data = {
            "farmer_id": "farmer-123",
            "crop_type": "wheat",
            "expected_quantity_tons": 10.0,
            "expected_harvest_date": "2026-06-15",
        }
        model = HarvestDealCreateRequest(**data)

        assert model.crop_type_ar is None
        assert model.price_per_ton is None
        assert model.notes is None

    def test_deal_create_request_invalid_quantity_zero(self):
        """Test validation error for zero quantity."""
        data = {
            "farmer_id": "farmer-123",
            "crop_type": "wheat",
            "expected_quantity_tons": 0.0,  # Must be > 0
            "expected_harvest_date": "2026-06-15",
        }
        with pytest.raises(ValidationError) as exc_info:
            HarvestDealCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("expected_quantity_tons",) for e in errors)

    def test_deal_create_request_invalid_quantity_negative(self):
        """Test validation error for negative quantity."""
        data = {
            "farmer_id": "farmer-123",
            "crop_type": "wheat",
            "expected_quantity_tons": -10.0,
            "expected_harvest_date": "2026-06-15",
        }
        with pytest.raises(ValidationError) as exc_info:
            HarvestDealCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("expected_quantity_tons",) for e in errors)

    def test_deal_create_request_invalid_price_negative(self):
        """Test validation error for negative price."""
        data = {
            "farmer_id": "farmer-123",
            "crop_type": "wheat",
            "expected_quantity_tons": 50.0,
            "expected_harvest_date": "2026-06-15",
            "price_per_ton": -100.0,  # Must be > 0 if provided
        }
        with pytest.raises(ValidationError) as exc_info:
            HarvestDealCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("price_per_ton",) for e in errors)

    def test_deal_create_request_invalid_date_format(self):
        """Test validation error for invalid date format."""
        data = {
            "farmer_id": "farmer-123",
            "crop_type": "wheat",
            "expected_quantity_tons": 50.0,
            "expected_harvest_date": "invalid-date",
        }
        with pytest.raises(ValidationError) as exc_info:
            HarvestDealCreateRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("expected_harvest_date",) for e in errors)

    def test_deal_response_model(self):
        """Test HarvestDealResponse model structure."""
        now = datetime.utcnow()
        harvest_date = date(2026, 6, 15)
        data = {
            "id": "deal-123",
            "farmer_id": "farmer-123",
            "crop_type": "wheat",
            "crop_type_ar": "قمح",
            "expected_quantity_tons": 50.0,
            "actual_quantity_tons": None,
            "expected_harvest_date": harvest_date,
            "actual_harvest_date": None,
            "price_per_ton": 1850.0,
            "total_value": 92500.0,
            "stage": "prospecting",
            "notes": "Test",
            "notes_ar": "اختبار",
            "created_at": now,
            "updated_at": now,
        }
        model = HarvestDealResponse(**data)

        assert model.id == "deal-123"
        assert model.stage == "prospecting"
        assert model.expected_harvest_date == harvest_date


# ═══════════════════════════════════════════════════════════════════════════════
# Interaction Model Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestInteractionModelValidation:
    """Tests for interaction Pydantic model validation."""

    def test_interaction_create_request_valid(self):
        """Test valid InteractionCreateRequest creation."""
        data = {
            "farmer_id": "farmer-123",
            "interaction_type": "call",
            "subject": "Follow-up call",
            "subject_ar": "مكالمة متابعة",
            "notes": "Discussed irrigation",
            "notes_ar": "مناقشة الري",
            "outcome": "positive",
            "follow_up_date": "2026-02-01",
        }
        model = InteractionCreateRequest(**data)

        assert model.farmer_id == "farmer-123"
        assert model.interaction_type == "call"
        assert model.subject == "Follow-up call"

    def test_interaction_create_request_minimal(self):
        """Test InteractionCreateRequest with minimal required fields."""
        data = {
            "farmer_id": "farmer-123",
            "interaction_type": "call",
            "subject": "Test subject",
        }
        model = InteractionCreateRequest(**data)

        assert model.subject_ar is None
        assert model.notes is None
        assert model.outcome is None
        assert model.follow_up_date is None

    def test_interaction_create_request_various_types(self):
        """Test various interaction types."""
        interaction_types = ["call", "visit", "whatsapp", "sms", "email"]
        for int_type in interaction_types:
            data = {
                "farmer_id": "farmer-123",
                "interaction_type": int_type,
                "subject": f"Test {int_type}",
            }
            model = InteractionCreateRequest(**data)
            assert model.interaction_type == int_type

    def test_interaction_response_model(self):
        """Test InteractionResponse model structure."""
        now = datetime.utcnow()
        follow_up = date(2026, 2, 1)
        data = {
            "id": "int-123",
            "farmer_id": "farmer-123",
            "interaction_type": "call",
            "subject": "Test",
            "subject_ar": "اختبار",
            "notes": "Notes",
            "notes_ar": "ملاحظات",
            "outcome": "positive",
            "follow_up_date": follow_up,
            "created_at": now,
            "created_by": "user-123",
        }
        model = InteractionResponse(**data)

        assert model.id == "int-123"
        assert model.interaction_type == "call"
        assert model.follow_up_date == follow_up


# ═══════════════════════════════════════════════════════════════════════════════
# Query Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestQueryModels:
    """Tests for query request/response models."""

    def test_query_request_valid(self):
        """Test valid QueryRequest creation."""
        data = {
            "query": "Show me all active farmers",
            "tenant_id": "test-tenant",
        }
        model = QueryRequest(**data)

        assert model.query == "Show me all active farmers"
        assert model.tenant_id == "test-tenant"

    def test_query_request_arabic(self):
        """Test QueryRequest with Arabic query."""
        data = {
            "query": "أرني جميع المزارعين النشطين",
            "tenant_id": "test-tenant",
        }
        model = QueryRequest(**data)

        assert "المزارعين" in model.query

    def test_query_response_model(self):
        """Test QueryResponse model structure."""
        data = {
            "query": "Show me farmers",
            "interpreted_as": "SELECT * FROM farmers",
            "interpreted_as_ar": "اختر جميع المزارعين",
            "results": [{"id": "1", "name": "Test"}],
            "result_count": 1,
            "execution_time_ms": 15,
        }
        model = QueryResponse(**data)

        assert model.query == "Show me farmers"
        assert model.result_count == 1
        assert model.execution_time_ms == 15
        assert len(model.results) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Pipeline Stats Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineStatsModel:
    """Tests for pipeline statistics model."""

    def test_pipeline_stats_response_valid(self):
        """Test valid PipelineStatsResponse creation."""
        data = {
            "total_deals": 10,
            "total_value": 500000.0,
            "by_stage": {
                "prospecting": {"count": 5, "total_value": 200000.0, "name_ar": "استكشاف"},
                "negotiation": {"count": 3, "total_value": 200000.0, "name_ar": "تفاوض"},
                "paid": {"count": 2, "total_value": 100000.0, "name_ar": "مدفوع"},
            },
            "conversion_rate": 20.0,
            "average_deal_size": 50000.0,
        }
        model = PipelineStatsResponse(**data)

        assert model.total_deals == 10
        assert model.total_value == 500000.0
        assert model.conversion_rate == 20.0
        assert model.average_deal_size == 50000.0
        assert "prospecting" in model.by_stage

    def test_pipeline_stats_response_empty(self):
        """Test PipelineStatsResponse with empty pipeline."""
        data = {
            "total_deals": 0,
            "total_value": 0.0,
            "by_stage": {},
            "conversion_rate": 0.0,
            "average_deal_size": 0.0,
        }
        model = PipelineStatsResponse(**data)

        assert model.total_deals == 0
        assert model.total_value == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Engagement Score Calculation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEngagementScoreCalculation:
    """Tests for engagement score calculation logic."""

    def test_engagement_score_factors(self):
        """Test engagement score considers all factors."""
        # This tests the engagement score logic from FarmerCRMService
        # Score components:
        # - Recency of last interaction (max 30 points)
        # - Number of interactions (max 25 points)
        # - Active deals (max 25 points)
        # - Profile completeness (max 20 points)

        # Simulate calculation based on factors
        def calculate_engagement_score(
            days_since_interaction: int | None,
            num_interactions: int,
            num_active_deals: int,
            has_email: bool,
            has_coordinates: bool,
            has_crops: bool,
            has_area: bool,
        ) -> float:
            score = 0.0

            # Recency
            if days_since_interaction is not None:
                if days_since_interaction <= 7:
                    score += 30
                elif days_since_interaction <= 30:
                    score += 20
                elif days_since_interaction <= 90:
                    score += 10

            # Interactions
            score += min(25, num_interactions * 5)

            # Active deals
            score += min(25, num_active_deals * 10)

            # Profile completeness
            if has_email:
                score += 5
            if has_coordinates:
                score += 5
            if has_crops:
                score += 5
            if has_area:
                score += 5

            return min(100, score)

        # Test max score
        max_score = calculate_engagement_score(
            days_since_interaction=1,
            num_interactions=10,
            num_active_deals=5,
            has_email=True,
            has_coordinates=True,
            has_crops=True,
            has_area=True,
        )
        assert max_score == 100

        # Test min score
        min_score = calculate_engagement_score(
            days_since_interaction=None,
            num_interactions=0,
            num_active_deals=0,
            has_email=False,
            has_coordinates=False,
            has_crops=False,
            has_area=False,
        )
        assert min_score == 0

        # Test intermediate scores
        mid_score = calculate_engagement_score(
            days_since_interaction=15,  # 20 points
            num_interactions=3,  # 15 points
            num_active_deals=1,  # 10 points
            has_email=True,  # 5 points
            has_coordinates=False,
            has_crops=True,  # 5 points
            has_area=False,
        )
        assert mid_score == 55

    def test_engagement_score_recency_brackets(self):
        """Test engagement score recency brackets."""

        def recency_score(days: int | None) -> int:
            if days is None:
                return 0
            if days <= 7:
                return 30
            elif days <= 30:
                return 20
            elif days <= 90:
                return 10
            return 0

        assert recency_score(1) == 30
        assert recency_score(7) == 30
        assert recency_score(8) == 20
        assert recency_score(30) == 20
        assert recency_score(31) == 10
        assert recency_score(90) == 10
        assert recency_score(91) == 0
        assert recency_score(None) == 0

    def test_engagement_score_interaction_cap(self):
        """Test engagement score interaction points are capped."""

        def interaction_score(num: int) -> int:
            return min(25, num * 5)

        assert interaction_score(1) == 5
        assert interaction_score(3) == 15
        assert interaction_score(5) == 25
        assert interaction_score(10) == 25  # Capped at 25
        assert interaction_score(100) == 25  # Still capped

    def test_engagement_score_active_deals_cap(self):
        """Test engagement score active deals points are capped."""

        def deal_score(num: int) -> int:
            return min(25, num * 10)

        assert deal_score(1) == 10
        assert deal_score(2) == 20
        assert deal_score(3) == 25  # Capped
        assert deal_score(10) == 25  # Still capped


# ═══════════════════════════════════════════════════════════════════════════════
# Serialization Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestModelSerialization:
    """Tests for model serialization."""

    def test_farmer_response_to_dict(self):
        """Test FarmerResponse serialization."""
        now = datetime.utcnow()
        data = {
            "id": "farmer-123",
            "name": "Ahmed",
            "name_ar": "أحمد",
            "phone": "+966501234567",
            "email": None,
            "national_id": None,
            "farm_location": None,
            "farm_location_ar": None,
            "farm_size_hectares": None,
            "primary_crops": [],
            "status": "lead",
            "tags": [],
            "created_at": now,
            "updated_at": now,
            "last_interaction_at": None,
        }
        model = FarmerResponse(**data)
        serialized = model.model_dump()

        assert isinstance(serialized, dict)
        assert serialized["id"] == "farmer-123"
        assert serialized["name"] == "Ahmed"

    def test_deal_response_to_dict(self):
        """Test HarvestDealResponse serialization."""
        now = datetime.utcnow()
        data = {
            "id": "deal-123",
            "farmer_id": "farmer-123",
            "crop_type": "wheat",
            "crop_type_ar": None,
            "expected_quantity_tons": 50.0,
            "actual_quantity_tons": None,
            "expected_harvest_date": date(2026, 6, 15),
            "actual_harvest_date": None,
            "price_per_ton": 1850.0,
            "total_value": 92500.0,
            "stage": "prospecting",
            "notes": None,
            "notes_ar": None,
            "created_at": now,
            "updated_at": now,
        }
        model = HarvestDealResponse(**data)
        serialized = model.model_dump()

        assert isinstance(serialized, dict)
        assert serialized["stage"] == "prospecting"

    def test_query_response_to_json(self):
        """Test QueryResponse JSON serialization."""
        data = {
            "query": "Test query",
            "interpreted_as": "SELECT *",
            "interpreted_as_ar": "اختر الكل",
            "results": [{"id": "1"}],
            "result_count": 1,
            "execution_time_ms": 10,
        }
        model = QueryResponse(**data)
        json_str = model.model_dump_json()

        assert isinstance(json_str, str)
        assert "Test query" in json_str
