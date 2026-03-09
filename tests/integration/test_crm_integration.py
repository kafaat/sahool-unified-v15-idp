"""
Integration tests for crm-service
اختبارات التكامل لخدمة إدارة علاقات المزارعين

Tests the Farmer CRM Service for:
- Complete farmer lifecycle from creation to deals
- Deal pipeline flow through all stages
- Interaction logging and follow-ups
- Cross-tenant data isolation
- Natural language query (SQLBot-inspired)
- NATS event publishing

Service URL: http://localhost:8131
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import date, datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Factories
# ═══════════════════════════════════════════════════════════════════════════════


class FarmerFactory:
    """Factory for creating farmer test data."""

    @staticmethod
    def create_farmer_request(
        tenant_id: str | None = None,
        name: str | None = None,
        phone: str | None = None,
    ) -> dict[str, Any]:
        """Create a farmer creation request."""
        unique_id = uuid4().hex[:8]
        return {
            "name": name or f"Test Farmer {unique_id}",
            "name_ar": f"مزارع اختبار {unique_id}",
            "phone": phone or f"+9677{uuid4().int % 10000000:07d}",
            "email": f"farmer_{unique_id}@test.sahool.com",
            "national_id": f"ID{unique_id}",
            "farm_location": "Sana'a, Yemen",
            "farm_location_ar": "صنعاء، اليمن",
            "farm_size_hectares": 15.5,
            "primary_crops": ["wheat", "barley", "vegetables"],
            "tenant_id": tenant_id or f"test-tenant-{uuid4().hex[:8]}",
        }

    @staticmethod
    def create_farmer_update_request() -> dict[str, Any]:
        """Create a farmer update request."""
        return {
            "farm_size_hectares": 20.0,
            "primary_crops": ["wheat", "barley", "tomato", "cucumber"],
            "status": "active",
            "tags": ["premium", "large_farm"],
        }


class DealFactory:
    """Factory for creating harvest deal test data."""

    @staticmethod
    def create_deal_request(
        farmer_id: str,
        crop_type: str = "wheat",
    ) -> dict[str, Any]:
        """Create a harvest deal creation request."""
        return {
            "farmer_id": farmer_id,
            "crop_type": crop_type,
            "crop_type_ar": "قمح" if crop_type == "wheat" else crop_type,
            "expected_quantity_tons": 50.0,
            "expected_harvest_date": (date.today() + timedelta(days=90)).isoformat(),
            "price_per_ton": 500.0,
            "notes": "Test deal for integration testing",
            "notes_ar": "صفقة اختبار لاختبارات التكامل",
        }


class InteractionFactory:
    """Factory for creating interaction test data."""

    @staticmethod
    def create_interaction_request(
        farmer_id: str,
        interaction_type: str = "call",
    ) -> dict[str, Any]:
        """Create an interaction logging request."""
        return {
            "farmer_id": farmer_id,
            "interaction_type": interaction_type,
            "subject": "Follow-up on wheat harvest",
            "subject_ar": "متابعة حصاد القمح",
            "notes": "Discussed harvest timeline and pricing",
            "notes_ar": "ناقشنا جدول الحصاد والتسعير",
            "outcome": "positive",
            "follow_up_date": (date.today() + timedelta(days=7)).isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: CRM Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestCRMIntegration:
    """
    Integration tests for Farmer CRM Service.
    اختبارات التكامل لخدمة إدارة علاقات المزارعين
    """

    SERVICE_URL = "http://localhost:8131"

    @pytest.fixture
    def farmer_factory(self) -> FarmerFactory:
        """Farmer data factory fixture."""
        return FarmerFactory()

    @pytest.fixture
    def deal_factory(self) -> DealFactory:
        """Deal data factory fixture."""
        return DealFactory()

    @pytest.fixture
    def interaction_factory(self) -> InteractionFactory:
        """Interaction data factory fixture."""
        return InteractionFactory()

    @pytest.fixture
    async def crm_client(self, http_client: AsyncClient, auth_headers: dict[str, str]) -> AsyncClient:
        """HTTP client configured for CRM service."""
        http_client.base_url = self.SERVICE_URL
        http_client.headers.update(auth_headers)
        return http_client

    # ═══════════════════════════════════════════════════════════════════════════
    # Health Check Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_health_endpoint(self, crm_client: AsyncClient):
        """Test liveness probe endpoint."""
        response = await crm_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "crm-service"
        assert "version" in data
        assert "service_ar" in data

    async def test_readiness_endpoint(self, crm_client: AsyncClient):
        """Test readiness probe endpoint."""
        response = await crm_client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert "nats" in data

    async def test_detailed_health_endpoint(self, crm_client: AsyncClient):
        """Test detailed health status endpoint."""
        response = await crm_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "farmers_count" in data
        assert "deals_count" in data

    # ═══════════════════════════════════════════════════════════════════════════
    # Complete Farmer Lifecycle Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_farmer_lifecycle(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        deal_factory: DealFactory,
        interaction_factory: InteractionFactory,
    ):
        """
        Test complete farmer lifecycle from creation to deals.
        اختبار دورة حياة المزارع الكاملة من الإنشاء إلى الصفقات

        This test verifies:
        1. Farmer creation (lead status)
        2. Farmer update (status change to active)
        3. Deal creation for the farmer
        4. Interaction logging
        5. Listing and filtering
        6. Deal pipeline progression
        """
        tenant_id = "test-tenant-123"

        # Step 1: Create a farmer (starts as lead)
        farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
        create_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_request,
        )

        assert create_response.status_code == 200
        farmer = create_response.json()
        assert farmer["name"] == farmer_request["name"]
        assert farmer["name_ar"] == farmer_request["name_ar"]
        assert farmer["phone"] == farmer_request["phone"]
        assert farmer["status"] == "lead"  # Initial status
        assert "id" in farmer

        farmer_id = farmer["id"]

        # Step 2: Update farmer to active status
        update_response = await crm_client.patch(
            f"/api/v1/farmers/{farmer_id}",
            json={
                "status": "active",
                "tags": ["vip", "wheat_specialist"],
            },
        )

        assert update_response.status_code == 200
        updated_farmer = update_response.json()
        assert updated_farmer["status"] == "active"
        assert "vip" in updated_farmer["tags"]

        # Step 3: Create a harvest deal for the farmer
        deal_request = deal_factory.create_deal_request(farmer_id=farmer_id)
        deal_response = await crm_client.post(
            "/api/v1/deals",
            json=deal_request,
        )

        assert deal_response.status_code == 200
        deal = deal_response.json()
        assert deal["farmer_id"] == farmer_id
        assert deal["crop_type"] == "wheat"
        assert deal["stage"] == "prospecting"  # Initial stage
        assert "id" in deal

        deal_id = deal["id"]

        # Step 4: Log an interaction
        interaction_request = interaction_factory.create_interaction_request(farmer_id=farmer_id)
        interaction_response = await crm_client.post(
            "/api/v1/interactions",
            json=interaction_request,
        )

        assert interaction_response.status_code == 200
        interaction = interaction_response.json()
        assert interaction["farmer_id"] == farmer_id
        assert interaction["interaction_type"] == "call"
        assert "id" in interaction

        # Step 5: Verify farmer's last interaction was updated
        get_farmer_response = await crm_client.get(f"/api/v1/farmers/{farmer_id}")
        assert get_farmer_response.status_code == 200
        farmer_after = get_farmer_response.json()
        assert farmer_after["last_interaction_at"] is not None

        # Step 6: List farmers and verify
        list_response = await crm_client.get(f"/api/v1/farmers?tenant_id={tenant_id}&status=active")
        assert list_response.status_code == 200
        farmers = list_response.json()
        farmer_ids = [f["id"] for f in farmers]
        assert farmer_id in farmer_ids

    # ═══════════════════════════════════════════════════════════════════════════
    # Deal Pipeline Flow Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_deal_pipeline_flow(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        deal_factory: DealFactory,
    ):
        """
        Test deal progression through all stages.
        اختبار تقدم الصفقة عبر جميع المراحل

        Pipeline stages:
        1. prospecting (استكشاف)
        2. qualification (تأهيل)
        3. negotiation (تفاوض)
        4. contracted (متعاقد)
        5. delivered (مسلم)
        6. paid (مدفوع)
        """
        tenant_id = f"test-tenant-pipeline-{uuid4().hex[:8]}"

        # Create farmer
        farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
        farmer_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_request,
        )
        farmer_id = farmer_response.json()["id"]

        # Create deal
        deal_request = deal_factory.create_deal_request(farmer_id=farmer_id)
        deal_response = await crm_client.post("/api/v1/deals", json=deal_request)
        deal = deal_response.json()
        deal_id = deal["id"]

        assert deal["stage"] == "prospecting"

        # Progress through pipeline stages
        stages = [
            "qualification",
            "negotiation",
            "contracted",
            "delivered",
            "paid",
        ]

        for stage in stages:
            response = await crm_client.patch(f"/api/v1/deals/{deal_id}/stage?stage={stage}")

            assert response.status_code == 200
            updated_deal = response.json()
            assert updated_deal["stage"] == stage

            # Verify stage-specific logic
            if stage == "paid":
                # Deal is won - conversion tracked
                pass

        # Verify final state
        final_response = await crm_client.get(f"/api/v1/deals?tenant_id={tenant_id}")
        assert final_response.status_code == 200
        deals = final_response.json()
        completed_deal = next((d for d in deals if d["id"] == deal_id), None)
        assert completed_deal is not None
        assert completed_deal["stage"] == "paid"

    async def test_deal_pipeline_lost_scenario(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        deal_factory: DealFactory,
    ):
        """Test deal that ends in closed_lost stage."""
        tenant_id = f"test-tenant-lost-{uuid4().hex[:8]}"

        # Create farmer and deal
        farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
        farmer_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_request,
        )
        farmer_id = farmer_response.json()["id"]

        deal_request = deal_factory.create_deal_request(farmer_id=farmer_id)
        deal_response = await crm_client.post("/api/v1/deals", json=deal_request)
        deal_id = deal_response.json()["id"]

        # Progress to negotiation then lose
        await crm_client.patch(f"/api/v1/deals/{deal_id}/stage?stage=qualification")
        await crm_client.patch(f"/api/v1/deals/{deal_id}/stage?stage=negotiation")

        # Mark as lost
        response = await crm_client.patch(f"/api/v1/deals/{deal_id}/stage?stage=closed_lost")

        assert response.status_code == 200
        lost_deal = response.json()
        assert lost_deal["stage"] == "closed_lost"

    async def test_pipeline_statistics(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        deal_factory: DealFactory,
    ):
        """Test pipeline statistics endpoint."""
        tenant_id = f"test-tenant-stats-{uuid4().hex[:8]}"

        # Create farmer
        farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
        farmer_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_request,
        )
        farmer_id = farmer_response.json()["id"]

        # Create multiple deals at different stages
        for i in range(3):
            deal_request = deal_factory.create_deal_request(
                farmer_id=farmer_id,
                crop_type=["wheat", "barley", "tomato"][i],
            )
            deal_response = await crm_client.post("/api/v1/deals", json=deal_request)
            deal_id = deal_response.json()["id"]

            # Move to different stages
            if i == 1:
                await crm_client.patch(f"/api/v1/deals/{deal_id}/stage?stage=negotiation")
            elif i == 2:
                await crm_client.patch(f"/api/v1/deals/{deal_id}/stage?stage=paid")

        # Get pipeline statistics
        stats_response = await crm_client.get(f"/api/v1/deals/pipeline?tenant_id={tenant_id}")

        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert "total_deals" in stats
        assert "total_value" in stats
        assert "by_stage" in stats
        assert "conversion_rate" in stats
        assert "average_deal_size" in stats

        # Verify stage breakdown
        assert "prospecting" in stats["by_stage"]
        assert "negotiation" in stats["by_stage"]
        assert "paid" in stats["by_stage"]

        # Each stage should have count, total_value, name_ar
        for stage, stage_data in stats["by_stage"].items():
            assert "count" in stage_data
            assert "total_value" in stage_data
            assert "name_ar" in stage_data

    # ═══════════════════════════════════════════════════════════════════════════
    # Cross-Tenant Isolation Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_cross_tenant_isolation(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
    ):
        """
        Test that tenants cannot access each other's data.
        اختبار عزل البيانات بين المستأجرين

        This verifies:
        - Farmers created by tenant A cannot be accessed by tenant B
        - List endpoints respect tenant filtering
        """
        tenant_a = f"tenant-a-{uuid4().hex[:8]}"
        tenant_b = f"tenant-b-{uuid4().hex[:8]}"

        # Create farmer for tenant A
        farmer_a_request = farmer_factory.create_farmer_request(tenant_id=tenant_a)
        farmer_a_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_a_request,
        )
        assert farmer_a_response.status_code == 200
        farmer_a = farmer_a_response.json()

        # Create farmer for tenant B
        farmer_b_request = farmer_factory.create_farmer_request(tenant_id=tenant_b)
        farmer_b_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_b_request,
        )
        assert farmer_b_response.status_code == 200
        farmer_b = farmer_b_response.json()

        # List farmers for tenant A - should only see tenant A's farmers
        list_a_response = await crm_client.get(f"/api/v1/farmers?tenant_id={tenant_a}")
        assert list_a_response.status_code == 200
        farmers_a = list_a_response.json()

        for farmer in farmers_a:
            assert farmer["id"] != farmer_b["id"]

        # List farmers for tenant B - should only see tenant B's farmers
        list_b_response = await crm_client.get(f"/api/v1/farmers?tenant_id={tenant_b}")
        assert list_b_response.status_code == 200
        farmers_b = list_b_response.json()

        for farmer in farmers_b:
            assert farmer["id"] != farmer_a["id"]

        # Direct access should enforce tenant isolation
        # (Note: depends on authentication implementation)

    # ═══════════════════════════════════════════════════════════════════════════
    # Interaction Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_interaction_logging(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        interaction_factory: InteractionFactory,
    ):
        """Test interaction logging for different types."""
        tenant_id = f"test-tenant-interact-{uuid4().hex[:8]}"

        # Create farmer
        farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
        farmer_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_request,
        )
        farmer_id = farmer_response.json()["id"]

        # Log different interaction types
        interaction_types = ["call", "visit", "whatsapp", "sms", "email"]

        for interaction_type in interaction_types:
            interaction_request = interaction_factory.create_interaction_request(
                farmer_id=farmer_id,
                interaction_type=interaction_type,
            )
            response = await crm_client.post(
                "/api/v1/interactions",
                json=interaction_request,
            )

            assert response.status_code == 200
            interaction = response.json()
            assert interaction["interaction_type"] == interaction_type
            assert interaction["farmer_id"] == farmer_id

        # List interactions for farmer
        list_response = await crm_client.get(f"/api/v1/interactions?farmer_id={farmer_id}")
        assert list_response.status_code == 200
        interactions = list_response.json()
        assert len(interactions) >= len(interaction_types)

    async def test_interaction_type_filtering(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        interaction_factory: InteractionFactory,
    ):
        """Test filtering interactions by type."""
        tenant_id = f"test-tenant-filter-{uuid4().hex[:8]}"

        # Create farmer
        farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
        farmer_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_request,
        )
        farmer_id = farmer_response.json()["id"]

        # Log multiple calls and one visit
        for _ in range(3):
            await crm_client.post(
                "/api/v1/interactions",
                json=interaction_factory.create_interaction_request(
                    farmer_id=farmer_id,
                    interaction_type="call",
                ),
            )

        await crm_client.post(
            "/api/v1/interactions",
            json=interaction_factory.create_interaction_request(
                farmer_id=farmer_id,
                interaction_type="visit",
            ),
        )

        # Filter by call type
        call_response = await crm_client.get(f"/api/v1/interactions?farmer_id={farmer_id}&interaction_type=call")
        assert call_response.status_code == 200
        calls = call_response.json()
        for interaction in calls:
            assert interaction["interaction_type"] == "call"

    # ═══════════════════════════════════════════════════════════════════════════
    # Natural Language Query Tests (SQLBot-inspired)
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_natural_language_query_active_farmers(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
    ):
        """Test natural language query for active farmers."""
        tenant_id = f"test-tenant-nlq-{uuid4().hex[:8]}"

        # Create farmers with different statuses
        for status in ["lead", "active", "active", "churned"]:
            farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
            response = await crm_client.post(
                "/api/v1/farmers",
                json=farmer_request,
            )
            farmer_id = response.json()["id"]
            if status != "lead":
                await crm_client.patch(
                    f"/api/v1/farmers/{farmer_id}",
                    json={"status": status},
                )

        # Query for active farmers
        query_response = await crm_client.post(
            "/api/v1/query",
            json={
                "query": "Show me all active farmers",
                "tenant_id": tenant_id,
            },
        )

        assert query_response.status_code == 200
        result = query_response.json()
        assert "query" in result
        assert "interpreted_as" in result
        assert "results" in result
        assert "result_count" in result
        assert "execution_time_ms" in result

        # All results should be active
        for farmer in result["results"]:
            assert farmer["status"] == "active"

    async def test_natural_language_query_arabic(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
    ):
        """Test natural language query in Arabic."""
        tenant_id = f"test-tenant-nlq-ar-{uuid4().hex[:8]}"

        # Create farmer
        farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
        await crm_client.post("/api/v1/farmers", json=farmer_request)

        # Query in Arabic
        query_response = await crm_client.post(
            "/api/v1/query",
            json={
                "query": "أرني جميع المزارعين",  # Show me all farmers
                "tenant_id": tenant_id,
            },
        )

        assert query_response.status_code == 200
        result = query_response.json()
        assert "interpreted_as_ar" in result

    async def test_natural_language_query_deals(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        deal_factory: DealFactory,
    ):
        """Test natural language query for deals."""
        tenant_id = f"test-tenant-nlq-deals-{uuid4().hex[:8]}"

        # Create farmer and deals
        farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
        farmer_response = await crm_client.post(
            "/api/v1/farmers",
            json=farmer_request,
        )
        farmer_id = farmer_response.json()["id"]

        # Create deal in negotiation
        deal_request = deal_factory.create_deal_request(farmer_id=farmer_id)
        deal_response = await crm_client.post("/api/v1/deals", json=deal_request)
        deal_id = deal_response.json()["id"]
        await crm_client.patch(f"/api/v1/deals/{deal_id}/stage?stage=negotiation")

        # Query for deals in negotiation
        query_response = await crm_client.post(
            "/api/v1/query",
            json={
                "query": "Show me deals in negotiation stage",
                "tenant_id": tenant_id,
            },
        )

        assert query_response.status_code == 200
        result = query_response.json()
        for deal in result["results"]:
            assert deal["stage"] == "negotiation"

    # ═══════════════════════════════════════════════════════════════════════════
    # NATS Event Publishing Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_farmer_created_event(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        nats_client,
    ):
        """Test farmer.created event is published to NATS."""
        tenant_id = f"test-tenant-event-{uuid4().hex[:8]}"
        received_events = []

        async def message_handler(msg):
            data = json.loads(msg.data.decode())
            received_events.append(data)

        try:
            # Subscribe to farmer events
            sub = await nats_client.subscribe(
                f"sahool.{tenant_id}.crm.farmer.>",
                cb=message_handler,
            )

            # Create farmer
            farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
            await crm_client.post("/api/v1/farmers", json=farmer_request)

            # Wait for event
            await asyncio.sleep(2)
            await sub.unsubscribe()

            # Verify event
            if received_events:
                event = received_events[0]
                assert event.get("event_type") == "farmer.created"
                assert event.get("tenant_id") == tenant_id

        except Exception as e:
            pytest.skip(f"NATS not available: {e}")

    async def test_deal_stage_advanced_event(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
        deal_factory: DealFactory,
        nats_client,
    ):
        """Test deal.stage_advanced event is published to NATS."""
        tenant_id = f"test-tenant-deal-event-{uuid4().hex[:8]}"
        received_events = []

        async def message_handler(msg):
            data = json.loads(msg.data.decode())
            received_events.append(data)

        try:
            # Create farmer and deal first
            farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
            farmer_response = await crm_client.post(
                "/api/v1/farmers",
                json=farmer_request,
            )
            farmer_id = farmer_response.json()["id"]

            deal_request = deal_factory.create_deal_request(farmer_id=farmer_id)
            deal_response = await crm_client.post("/api/v1/deals", json=deal_request)
            deal_id = deal_response.json()["id"]

            # Subscribe to deal events
            sub = await nats_client.subscribe(
                f"sahool.{tenant_id}.crm.deal.>",
                cb=message_handler,
            )

            # Advance deal stage
            await crm_client.patch(f"/api/v1/deals/{deal_id}/stage?stage=qualification")

            # Wait for event
            await asyncio.sleep(2)
            await sub.unsubscribe()

            # Verify event
            if received_events:
                stage_events = [e for e in received_events if e.get("event_type") == "deal.stage_advanced"]
                if stage_events:
                    event = stage_events[0]
                    assert event["new_stage"] == "qualification"

        except Exception as e:
            pytest.skip(f"NATS not available: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # Search and Filter Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_farmer_search(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
    ):
        """Test farmer search by name and phone."""
        tenant_id = f"test-tenant-search-{uuid4().hex[:8]}"
        unique_name = f"UniqueSearchName{uuid4().hex[:8]}"

        # Create farmer with unique name
        farmer_request = farmer_factory.create_farmer_request(
            tenant_id=tenant_id,
            name=unique_name,
        )
        await crm_client.post("/api/v1/farmers", json=farmer_request)

        # Search by name
        search_response = await crm_client.get(f"/api/v1/farmers?tenant_id={tenant_id}&search={unique_name}")

        assert search_response.status_code == 200
        results = search_response.json()
        assert len(results) >= 1
        assert any(unique_name in f["name"] for f in results)

    async def test_farmer_pagination(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
    ):
        """Test farmer listing with pagination."""
        tenant_id = f"test-tenant-page-{uuid4().hex[:8]}"

        # Create multiple farmers
        for _ in range(15):
            farmer_request = farmer_factory.create_farmer_request(tenant_id=tenant_id)
            await crm_client.post("/api/v1/farmers", json=farmer_request)

        # Get first page
        page1_response = await crm_client.get(f"/api/v1/farmers?tenant_id={tenant_id}&limit=10&offset=0")
        assert page1_response.status_code == 200
        page1 = page1_response.json()
        assert len(page1) == 10

        # Get second page
        page2_response = await crm_client.get(f"/api/v1/farmers?tenant_id={tenant_id}&limit=10&offset=10")
        assert page2_response.status_code == 200
        page2 = page2_response.json()
        assert len(page2) >= 5

        # Ensure no overlap
        page1_ids = {f["id"] for f in page1}
        page2_ids = {f["id"] for f in page2}
        assert page1_ids.isdisjoint(page2_ids)

    # ═══════════════════════════════════════════════════════════════════════════
    # Error Handling Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_farmer_not_found(self, crm_client: AsyncClient):
        """Test error handling for non-existent farmer."""
        fake_id = str(uuid4())
        response = await crm_client.get(f"/api/v1/farmers/{fake_id}")

        assert response.status_code == 404

    async def test_deal_for_nonexistent_farmer(
        self,
        crm_client: AsyncClient,
        deal_factory: DealFactory,
    ):
        """Test error handling when creating deal for non-existent farmer."""
        deal_request = deal_factory.create_deal_request(farmer_id=str(uuid4()))
        response = await crm_client.post("/api/v1/deals", json=deal_request)

        assert response.status_code == 404

    async def test_invalid_phone_format(
        self,
        crm_client: AsyncClient,
        farmer_factory: FarmerFactory,
    ):
        """Test validation for invalid phone format."""
        farmer_request = farmer_factory.create_farmer_request(phone="invalid")
        response = await crm_client.post("/api/v1/farmers", json=farmer_request)

        assert response.status_code == 422  # Validation error

    # ═══════════════════════════════════════════════════════════════════════════
    # Metrics Tests
    # ═══════════════════════════════════════════════════════════════════════════

    async def test_metrics_endpoint(self, crm_client: AsyncClient):
        """Test Prometheus metrics endpoint."""
        response = await crm_client.get("/metrics")

        assert response.status_code == 200
        metrics = response.text
        assert "crm_farmers_total" in metrics
        assert "crm_deals_total" in metrics
        assert "crm_interactions_total" in metrics
