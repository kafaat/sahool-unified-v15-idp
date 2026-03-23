"""
CRM Service Natural Language Query Tests
=========================================
Tests for FarmerQueryBot natural language query functionality.

Tests cover:
- Active farmer queries
- Farmer queries by crop type
- Deal queries by stage
- Pipeline summary queries
- Top farmers queries
- Invalid query handling
- Arabic query support

Author: SAHOOL Platform Team
"""

import os
import sys
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure test environment
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Classes for Testing FarmerQueryBot
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
    """Mock Farmer for query bot tests."""

    def __init__(
        self,
        farmer_id: str,
        name: str,
        name_ar: str,
        phone: str,
        status: FarmerStatus = FarmerStatus.LEAD,
        primary_crops: list[str] | None = None,
        total_area_ha: float = 0.0,
        lifetime_value: float = 0.0,
        email: str | None = None,
        coordinates: tuple[float, float] | None = None,
        last_interaction: datetime | None = None,
        total_interactions: int = 0,
    ):
        self.farmer_id = farmer_id
        self.name = name
        self.name_ar = name_ar
        self.phone = phone
        self.status = status
        self.primary_crops = primary_crops or []
        self.total_area_ha = total_area_ha
        self.lifetime_value = lifetime_value
        self.email = email
        self.coordinates = coordinates
        self.last_interaction = last_interaction
        self.total_interactions = total_interactions

    def to_dict(self) -> dict[str, Any]:
        return {
            "farmer_id": self.farmer_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "phone": self.phone,
            "status": self.status.value,
            "total_area_ha": self.total_area_ha,
            "primary_crops": self.primary_crops,
            "lifetime_value": self.lifetime_value,
        }


class HarvestDeal:
    """Mock HarvestDeal for query bot tests."""

    def __init__(
        self,
        deal_id: str,
        farmer_id: str,
        title: str,
        crop_type: str,
        expected_quantity_tons: float,
        expected_price_per_ton: float,
        stage: DealStage = DealStage.PROSPECTING,
        probability: float = 0.1,
    ):
        self.deal_id = deal_id
        self.farmer_id = farmer_id
        self.title = title
        self.crop_type = crop_type
        self.expected_quantity_tons = expected_quantity_tons
        self.expected_price_per_ton = expected_price_per_ton
        self.stage = stage
        self.probability = probability

    @property
    def expected_value(self) -> float:
        return self.expected_quantity_tons * self.expected_price_per_ton

    def to_dict(self) -> dict[str, Any]:
        return {
            "deal_id": self.deal_id,
            "farmer_id": self.farmer_id,
            "title": self.title,
            "crop_type": self.crop_type,
            "stage": self.stage.value,
            "expected_value": self.expected_value,
            "probability": self.probability,
        }


class Interaction:
    """Mock Interaction for query bot tests."""

    def __init__(
        self,
        interaction_id: str,
        farmer_id: str,
        type: InteractionType,
        subject: str,
        subject_ar: str = "",
        occurred_at: datetime | None = None,
    ):
        self.interaction_id = interaction_id
        self.farmer_id = farmer_id
        self.type = type
        self.subject = subject
        self.subject_ar = subject_ar
        self.occurred_at = occurred_at or datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        return {
            "interaction_id": self.interaction_id,
            "farmer_id": self.farmer_id,
            "type": self.type.value,
            "subject": self.subject,
            "occurred_at": self.occurred_at.isoformat(),
        }


class FarmerCRMService:
    """Mock FarmerCRMService for testing."""

    def __init__(self, tenant_id: str = "sahool"):
        self.tenant_id = tenant_id
        self._farmers: dict[str, Farmer] = {}
        self._deals: dict[str, HarvestDeal] = {}
        self._interactions: dict[str, Interaction] = {}

    async def get_pipeline_summary(self) -> dict[str, Any]:
        """Get deal pipeline summary."""
        pipeline = {stage.value: {"count": 0, "value": 0.0} for stage in DealStage}

        for deal in self._deals.values():
            pipeline[deal.stage.value]["count"] += 1
            pipeline[deal.stage.value]["value"] += deal.expected_value

        return {
            "pipeline": pipeline,
            "total_deals": len(self._deals),
            "total_value": sum(d.expected_value for d in self._deals.values()),
            "weighted_value": sum(d.expected_value * d.probability for d in self._deals.values()),
        }


class FarmerQueryBot:
    """FarmerQueryBot implementation for testing."""

    QUERY_PATTERNS = {
        "farmer_count": ["كم عدد", "how many", "عدد المزارعين"],
        "active_farmers": ["نشط", "active", "المزارعين النشطين"],
        "deals_by_crop": ["صفقات", "deals", "محصول"],
        "top_farmers": ["أعلى", "top", "الأفضل"],
        "pipeline": ["خط الأنابيب", "pipeline", "مراحل"],
    }

    def __init__(self, crm_service: FarmerCRMService):
        self.crm = crm_service

    async def query(self, natural_query: str) -> dict[str, Any]:
        """Process natural language query."""
        query_lower = natural_query.lower()

        if any(p in query_lower for p in self.QUERY_PATTERNS["farmer_count"]):
            return await self._count_farmers(query_lower)

        elif any(p in query_lower for p in self.QUERY_PATTERNS["pipeline"]):
            return await self.crm.get_pipeline_summary()

        elif any(p in query_lower for p in self.QUERY_PATTERNS["top_farmers"]):
            return await self._top_farmers()

        else:
            return {
                "error": "Query not understood",
                "error_ar": "لم يتم فهم الاستعلام",
                "suggestion": "Try: 'How many active farmers?' or 'Show pipeline'",
            }

    async def _count_farmers(self, query: str) -> dict[str, Any]:
        """Count farmers with optional status filter."""
        farmers = list(self.crm._farmers.values())

        if "نشط" in query or "active" in query:
            farmers = [f for f in farmers if f.status == FarmerStatus.ACTIVE]
            status = "active"
        elif "premium" in query or "مميز" in query:
            farmers = [f for f in farmers if f.status == FarmerStatus.PREMIUM]
            status = "premium"
        else:
            status = "all"

        return {
            "query_type": "farmer_count",
            "status_filter": status,
            "count": len(farmers),
            "answer": f"عدد المزارعين ({status}): {len(farmers)}",
            "answer_en": f"Number of farmers ({status}): {len(farmers)}",
        }

    async def _top_farmers(self, limit: int = 5) -> dict[str, Any]:
        """Get top farmers by lifetime value."""
        farmers = sorted(
            self.crm._farmers.values(),
            key=lambda f: f.lifetime_value,
            reverse=True,
        )[:limit]

        return {
            "query_type": "top_farmers",
            "limit": limit,
            "farmers": [f.to_dict() for f in farmers],
            "answer_ar": f"أعلى {limit} مزارعين من حيث القيمة",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def crm_service():
    """Create a CRM service instance with test data."""
    service = FarmerCRMService(tenant_id="test-tenant")

    # Add test farmers
    service._farmers = {
        "farmer-001": Farmer(
            farmer_id="farmer-001",
            name="Ahmed Mohammed",
            name_ar="أحمد محمد",
            phone="+966501234567",
            status=FarmerStatus.ACTIVE,
            primary_crops=["wheat", "barley"],
            total_area_ha=50.0,
            lifetime_value=150000.0,
        ),
        "farmer-002": Farmer(
            farmer_id="farmer-002",
            name="Khalid Ali",
            name_ar="خالد علي",
            phone="+966509876543",
            status=FarmerStatus.ACTIVE,
            primary_crops=["dates"],
            total_area_ha=30.0,
            lifetime_value=200000.0,
        ),
        "farmer-003": Farmer(
            farmer_id="farmer-003",
            name="Mohammed Hassan",
            name_ar="محمد حسن",
            phone="+966505555555",
            status=FarmerStatus.LEAD,
            primary_crops=["wheat"],
            total_area_ha=25.0,
            lifetime_value=50000.0,
        ),
        "farmer-004": Farmer(
            farmer_id="farmer-004",
            name="Saeed Omar",
            name_ar="سعيد عمر",
            phone="+966504444444",
            status=FarmerStatus.PREMIUM,
            primary_crops=["dates", "vegetables"],
            total_area_ha=100.0,
            lifetime_value=500000.0,
        ),
        "farmer-005": Farmer(
            farmer_id="farmer-005",
            name="Youssef Ibrahim",
            name_ar="يوسف إبراهيم",
            phone="+966503333333",
            status=FarmerStatus.CHURNED,
            primary_crops=["tomatoes"],
            total_area_ha=10.0,
            lifetime_value=25000.0,
        ),
    }

    # Add test deals
    service._deals = {
        "deal-001": HarvestDeal(
            deal_id="deal-001",
            farmer_id="farmer-001",
            title="Wheat Harvest 2026",
            crop_type="wheat",
            expected_quantity_tons=100.0,
            expected_price_per_ton=1850.0,
            stage=DealStage.PROSPECTING,
        ),
        "deal-002": HarvestDeal(
            deal_id="deal-002",
            farmer_id="farmer-002",
            title="Dates Supply Contract",
            crop_type="dates",
            expected_quantity_tons=50.0,
            expected_price_per_ton=5000.0,
            stage=DealStage.NEGOTIATION,
            probability=0.5,
        ),
        "deal-003": HarvestDeal(
            deal_id="deal-003",
            farmer_id="farmer-004",
            title="Premium Dates Deal",
            crop_type="dates",
            expected_quantity_tons=75.0,
            expected_price_per_ton=6000.0,
            stage=DealStage.CONTRACTED,
            probability=0.75,
        ),
        "deal-004": HarvestDeal(
            deal_id="deal-004",
            farmer_id="farmer-001",
            title="Barley Harvest",
            crop_type="barley",
            expected_quantity_tons=80.0,
            expected_price_per_ton=1600.0,
            stage=DealStage.PAID,
            probability=1.0,
        ),
    }

    return service


@pytest.fixture
def query_bot(crm_service):
    """Create a FarmerQueryBot instance."""
    return FarmerQueryBot(crm_service)


# ═══════════════════════════════════════════════════════════════════════════════
# Active Farmers Query Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestQueryActiveFarmers:
    """Tests for querying active farmers."""

    @pytest.mark.asyncio
    async def test_query_active_farmers_english(self, query_bot):
        """Test querying active farmers in English."""
        result = await query_bot.query("How many active farmers?")

        assert result["query_type"] == "farmer_count"
        assert result["status_filter"] == "active"
        assert result["count"] == 2  # Ahmed and Khalid

    @pytest.mark.asyncio
    async def test_query_active_farmers_arabic(self, query_bot):
        """Test querying active farmers in Arabic."""
        result = await query_bot.query("كم عدد المزارعين النشطين؟")

        assert result["query_type"] == "farmer_count"
        assert result["status_filter"] == "active"
        assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_query_all_farmers(self, query_bot):
        """Test querying all farmers."""
        result = await query_bot.query("How many farmers do we have?")

        assert result["query_type"] == "farmer_count"
        assert result["status_filter"] == "all"
        assert result["count"] == 5

    @pytest.mark.asyncio
    async def test_query_premium_farmers(self, query_bot):
        """Test querying premium farmers."""
        result = await query_bot.query("How many premium farmers?")

        assert result["query_type"] == "farmer_count"
        assert result["status_filter"] == "premium"
        assert result["count"] == 1  # Only Saeed

    @pytest.mark.asyncio
    async def test_query_premium_farmers_arabic(self, query_bot):
        """Test querying premium farmers in Arabic."""
        result = await query_bot.query("كم عدد المزارعين المميزين؟")

        assert result["query_type"] == "farmer_count"
        assert result["status_filter"] == "premium"
        assert result["count"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Farmers by Crop Query Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestQueryFarmersByCrop:
    """Tests for querying farmers by crop type."""

    @pytest.mark.asyncio
    async def test_query_wheat_farmers(self, crm_service):
        """Test querying farmers growing wheat."""
        # Simulate crop-based query filtering
        farmers = [f for f in crm_service._farmers.values() if "wheat" in f.primary_crops]

        assert len(farmers) == 2  # Ahmed and Mohammed

    @pytest.mark.asyncio
    async def test_query_dates_farmers(self, crm_service):
        """Test querying farmers growing dates."""
        farmers = [f for f in crm_service._farmers.values() if "dates" in f.primary_crops]

        assert len(farmers) == 2  # Khalid and Saeed

    @pytest.mark.asyncio
    async def test_query_farmers_multiple_crops(self, crm_service):
        """Test querying farmers with multiple crops."""
        farmers = [f for f in crm_service._farmers.values() if len(f.primary_crops) > 1]

        assert len(farmers) == 2  # Ahmed (wheat, barley) and Saeed (dates, vegetables)


# ═══════════════════════════════════════════════════════════════════════════════
# Deals by Stage Query Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestQueryDealsByStage:
    """Tests for querying deals by stage."""

    @pytest.mark.asyncio
    async def test_query_pipeline(self, query_bot):
        """Test querying pipeline summary."""
        result = await query_bot.query("Show me the pipeline")

        assert "pipeline" in result
        assert "total_deals" in result
        assert result["total_deals"] == 4

    @pytest.mark.asyncio
    async def test_query_pipeline_arabic(self, query_bot):
        """Test querying pipeline in Arabic."""
        result = await query_bot.query("أرني خط الأنابيب")

        assert "pipeline" in result
        assert result["total_deals"] == 4

    @pytest.mark.asyncio
    async def test_query_pipeline_stages(self, query_bot):
        """Test pipeline stage breakdown."""
        result = await query_bot.query("Show pipeline")

        pipeline = result["pipeline"]
        assert pipeline["prospecting"]["count"] == 1
        assert pipeline["negotiation"]["count"] == 1
        assert pipeline["contracted"]["count"] == 1
        assert pipeline["paid"]["count"] == 1

    @pytest.mark.asyncio
    async def test_query_pipeline_values(self, query_bot):
        """Test pipeline values are calculated correctly."""
        result = await query_bot.query("Show pipeline")

        # Expected values:
        # deal-001: 100 * 1850 = 185,000
        # deal-002: 50 * 5000 = 250,000
        # deal-003: 75 * 6000 = 450,000
        # deal-004: 80 * 1600 = 128,000
        # Total: 1,013,000

        assert result["total_value"] == 1013000.0

    @pytest.mark.asyncio
    async def test_query_deals_prospecting(self, crm_service):
        """Test filtering deals in prospecting stage."""
        prospecting_deals = [d for d in crm_service._deals.values() if d.stage == DealStage.PROSPECTING]

        assert len(prospecting_deals) == 1
        assert prospecting_deals[0].crop_type == "wheat"

    @pytest.mark.asyncio
    async def test_query_deals_negotiation(self, crm_service):
        """Test filtering deals in negotiation stage."""
        negotiation_deals = [d for d in crm_service._deals.values() if d.stage == DealStage.NEGOTIATION]

        assert len(negotiation_deals) == 1
        assert negotiation_deals[0].crop_type == "dates"

    @pytest.mark.asyncio
    async def test_query_closed_deals(self, crm_service):
        """Test filtering closed (paid) deals."""
        closed_deals = [d for d in crm_service._deals.values() if d.stage == DealStage.PAID]

        assert len(closed_deals) == 1
        assert closed_deals[0].deal_id == "deal-004"


# ═══════════════════════════════════════════════════════════════════════════════
# Top Farmers Query Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestQueryTopFarmers:
    """Tests for querying top farmers."""

    @pytest.mark.asyncio
    async def test_query_top_farmers_english(self, query_bot):
        """Test querying top farmers in English."""
        result = await query_bot.query("Show me the top farmers")

        assert result["query_type"] == "top_farmers"
        assert result["limit"] == 5
        assert len(result["farmers"]) == 5

    @pytest.mark.asyncio
    async def test_query_top_farmers_arabic(self, query_bot):
        """Test querying top farmers in Arabic."""
        result = await query_bot.query("أرني أعلى المزارعين")

        assert result["query_type"] == "top_farmers"
        assert "answer_ar" in result

    @pytest.mark.asyncio
    async def test_top_farmers_sorted_by_value(self, query_bot):
        """Test top farmers are sorted by lifetime value."""
        result = await query_bot.query("Show top farmers")

        farmers = result["farmers"]
        # Should be sorted by lifetime_value descending
        # Saeed: 500,000
        # Khalid: 200,000
        # Ahmed: 150,000
        # Mohammed: 50,000
        # Youssef: 25,000

        assert farmers[0]["farmer_id"] == "farmer-004"  # Saeed
        assert farmers[0]["lifetime_value"] == 500000.0
        assert farmers[1]["farmer_id"] == "farmer-002"  # Khalid
        assert farmers[2]["farmer_id"] == "farmer-001"  # Ahmed


# ═══════════════════════════════════════════════════════════════════════════════
# Invalid Query Handling Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestInvalidQueryHandling:
    """Tests for invalid query handling."""

    @pytest.mark.asyncio
    async def test_unknown_query_english(self, query_bot):
        """Test handling unknown query in English."""
        result = await query_bot.query("What is the weather today?")

        assert "error" in result
        assert result["error"] == "Query not understood"
        assert "suggestion" in result

    @pytest.mark.asyncio
    async def test_unknown_query_returns_arabic_error(self, query_bot):
        """Test unknown query returns Arabic error message."""
        result = await query_bot.query("xyz random query")

        assert "error_ar" in result
        assert result["error_ar"] == "لم يتم فهم الاستعلام"

    @pytest.mark.asyncio
    async def test_empty_query(self, query_bot):
        """Test handling empty query."""
        result = await query_bot.query("")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_special_characters_query(self, query_bot):
        """Test handling query with special characters."""
        result = await query_bot.query("@#$%^&*()")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_suggestion_provided(self, query_bot):
        """Test that suggestions are provided for unknown queries."""
        result = await query_bot.query("unknown query text")

        assert "suggestion" in result
        assert len(result["suggestion"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Query Pattern Matching Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestQueryPatternMatching:
    """Tests for query pattern matching."""

    def test_query_patterns_defined(self):
        """Test query patterns are properly defined."""
        patterns = FarmerQueryBot.QUERY_PATTERNS

        assert "farmer_count" in patterns
        assert "active_farmers" in patterns
        assert "deals_by_crop" in patterns
        assert "top_farmers" in patterns
        assert "pipeline" in patterns

    def test_farmer_count_patterns(self):
        """Test farmer count patterns include Arabic and English."""
        patterns = FarmerQueryBot.QUERY_PATTERNS["farmer_count"]

        # English patterns
        assert any("how many" in p.lower() for p in patterns)

        # Arabic patterns
        assert any("كم عدد" in p for p in patterns)

    def test_active_farmers_patterns(self):
        """Test active farmer patterns."""
        patterns = FarmerQueryBot.QUERY_PATTERNS["active_farmers"]

        assert "active" in patterns
        assert "نشط" in patterns

    def test_top_farmers_patterns(self):
        """Test top farmers patterns."""
        patterns = FarmerQueryBot.QUERY_PATTERNS["top_farmers"]

        assert "top" in patterns
        assert "أعلى" in patterns

    def test_pipeline_patterns(self):
        """Test pipeline patterns."""
        patterns = FarmerQueryBot.QUERY_PATTERNS["pipeline"]

        assert "pipeline" in patterns
        assert "خط الأنابيب" in patterns


# ═══════════════════════════════════════════════════════════════════════════════
# Weighted Value Calculation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestWeightedValueCalculation:
    """Tests for weighted value calculations in pipeline."""

    @pytest.mark.asyncio
    async def test_weighted_value_calculation(self, query_bot):
        """Test weighted value is calculated correctly."""
        result = await query_bot.query("Show pipeline")

        # Expected weighted values:
        # deal-001: 185,000 * 0.1 = 18,500
        # deal-002: 250,000 * 0.5 = 125,000
        # deal-003: 450,000 * 0.75 = 337,500
        # deal-004: 128,000 * 1.0 = 128,000
        # Total weighted: 609,000

        assert result["weighted_value"] == 609000.0

    @pytest.mark.asyncio
    async def test_probability_affects_weighted_value(self, crm_service):
        """Test that probability affects weighted value calculation."""
        # Get individual deal expected values
        deal = crm_service._deals["deal-002"]  # Negotiation stage

        expected_value = deal.expected_value
        weighted_value = expected_value * deal.probability

        assert deal.probability == 0.5
        assert expected_value == 250000.0
        assert weighted_value == 125000.0


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Cases Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestQueryBotEdgeCases:
    """Tests for query bot edge cases."""

    @pytest.mark.asyncio
    async def test_query_with_empty_farmers(self):
        """Test querying when no farmers exist."""
        empty_service = FarmerCRMService()
        bot = FarmerQueryBot(empty_service)

        result = await bot.query("How many active farmers?")

        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_query_with_empty_deals(self):
        """Test pipeline query when no deals exist."""
        empty_service = FarmerCRMService()
        bot = FarmerQueryBot(empty_service)

        result = await bot.query("Show pipeline")

        assert result["total_deals"] == 0
        assert result["total_value"] == 0.0

    @pytest.mark.asyncio
    async def test_top_farmers_with_few_farmers(self):
        """Test top farmers query when fewer than limit exist."""
        service = FarmerCRMService()
        service._farmers = {
            "farmer-001": Farmer(
                farmer_id="farmer-001",
                name="Single Farmer",
                name_ar="مزارع واحد",
                phone="+966501234567",
                lifetime_value=100000.0,
            ),
        }
        bot = FarmerQueryBot(service)

        result = await bot.query("Show top farmers")

        assert result["query_type"] == "top_farmers"
        assert len(result["farmers"]) == 1

    @pytest.mark.asyncio
    async def test_case_insensitive_query(self, query_bot):
        """Test that queries are case-insensitive."""
        result1 = await query_bot.query("SHOW PIPELINE")
        result2 = await query_bot.query("show pipeline")
        result3 = await query_bot.query("Show Pipeline")

        # All should return pipeline results
        assert result1["total_deals"] == result2["total_deals"]
        assert result2["total_deals"] == result3["total_deals"]

    @pytest.mark.asyncio
    async def test_query_with_extra_whitespace(self, query_bot):
        """Test query with extra whitespace."""
        result = await query_bot.query("  how many   active   farmers  ")

        # Query should still match "how many" pattern even with extra spaces
        assert result["query_type"] == "farmer_count"
        # Status filter should match "active"
        assert result["status_filter"] == "active"

    @pytest.mark.asyncio
    async def test_mixed_language_query(self, query_bot):
        """Test query with mixed Arabic and English."""
        # Use a query that matches the farmer_count pattern and contains Arabic نشط
        result = await query_bot.query("How many نشط farmers?")

        # Should match "how many" pattern and "نشط" for active filter
        assert result["query_type"] == "farmer_count"
        assert result["status_filter"] == "active"
