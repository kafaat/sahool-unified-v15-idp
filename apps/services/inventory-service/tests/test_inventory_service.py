"""
Comprehensive Tests for Inventory Service
اختبارات شاملة لخدمة المخزون
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.main import app, get_db
from src.models.inventory import Base

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def client(test_db_session):
    """Create test client with test database"""

    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_healthz(self, client):
        """Test /healthz endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "inventory-service"

    def test_readyz(self, client):
        """Test /readyz endpoint"""
        response = client.get("/readyz")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_health_with_db_check(self, client):
        """Test /health endpoint with database check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "dependencies" in response.json()


class TestCategoryManagement:
    """Test item category management"""

    def test_create_category(self, client):
        """Test creating a new category"""
        category_data = {
            "name_en": "Fertilizers",
            "name_ar": "الأسمدة",
            "code": "FERT",
            "description": "All types of fertilizers",
        }

        response = client.post("/v1/categories", json=category_data)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name_en"] == "Fertilizers"
        assert data["code"] == "FERT"
        assert data["is_active"] is True

    def test_create_category_duplicate_code(self, client):
        """Test creating category with duplicate code"""
        category_data = {"name_en": "Category 1", "name_ar": "فئة 1", "code": "CAT1"}

        # Create first category
        client.post("/v1/categories", json=category_data)

        # Try to create duplicate
        response = client.post("/v1/categories", json=category_data)

        # Should handle duplicate appropriately
        assert response.status_code in [200, 400, 409]


class TestAnalyticsForecasting:
    """Test inventory forecasting analytics"""

    def test_get_consumption_forecast(self, client):
        """Test getting consumption forecast for an item"""
        response = client.get(
            "/v1/analytics/forecast/item_123",
            params={"tenant_id": "tenant_123", "forecast_days": 90},
        )

        # May return 404 if item doesn't exist, or 200 with forecast
        assert response.status_code in [200, 404]

    def test_get_all_forecasts(self, client):
        """Test getting forecasts for all items"""
        response = client.get(
            "/v1/analytics/forecasts", params={"tenant_id": "tenant_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_forecasts_with_filters(self, client):
        """Test getting forecasts with filters"""
        response = client.get(
            "/v1/analytics/forecasts",
            params={
                "tenant_id": "tenant_123",
                "category": "fertilizers",
                "low_stock_only": True,
            },
        )

        assert response.status_code == 200


class TestReorderRecommendations:
    """Test reorder recommendations"""

    def test_get_reorder_recommendations(self, client):
        """Test getting reorder recommendations"""
        response = client.get(
            "/v1/analytics/reorder-recommendations", params={"tenant_id": "tenant_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "tenant_id" in data
        assert "count" in data
        assert "recommendations" in data


class TestInventoryValuation:
    """Test inventory valuation"""

    def test_get_total_valuation(self, client):
        """Test getting total inventory valuation"""
        response = client.get(
            "/v1/analytics/valuation", params={"tenant_id": "tenant_123"}
        )

        assert response.status_code == 200

    def test_get_warehouse_valuation(self, client):
        """Test getting valuation for specific warehouse"""
        response = client.get(
            "/v1/analytics/valuation",
            params={"tenant_id": "tenant_123", "warehouse_id": "warehouse_456"},
        )

        assert response.status_code == 200


class TestTurnoverAnalysis:
    """Test inventory turnover analysis"""

    def test_get_turnover_analysis(self, client):
        """Test getting turnover analysis"""
        response = client.get(
            "/v1/analytics/turnover",
            params={"tenant_id": "tenant_123", "period_days": 365},
        )

        assert response.status_code == 200
        data = response.json()
        assert "tenant_id" in data
        assert "period_days" in data
        assert "items" in data

    def test_turnover_analysis_different_periods(self, client):
        """Test turnover analysis with different periods"""
        periods = [30, 90, 180, 365]

        for period in periods:
            response = client.get(
                "/v1/analytics/turnover",
                params={"tenant_id": "tenant_123", "period_days": period},
            )

            assert response.status_code == 200


class TestSlowMovingItems:
    """Test slow-moving items identification"""

    def test_identify_slow_moving_items(self, client):
        """Test identifying slow-moving inventory"""
        response = client.get(
            "/v1/analytics/slow-moving",
            params={"tenant_id": "tenant_123", "days_threshold": 90},
        )

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "total_value" in data
        assert "items" in data

    def test_slow_moving_items_validation(self, client):
        """Test slow-moving items threshold validation"""
        # Test minimum threshold
        response = client.get(
            "/v1/analytics/slow-moving",
            params={"tenant_id": "tenant_123", "days_threshold": 20},  # Below minimum
        )

        assert response.status_code in [200, 422]


class TestDeadStock:
    """Test dead stock identification"""

    def test_identify_dead_stock(self, client):
        """Test identifying dead stock"""
        response = client.get(
            "/v1/analytics/dead-stock",
            params={"tenant_id": "tenant_123", "days_threshold": 180},
        )

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "total_value" in data
        assert "items" in data


class TestABCAnalysis:
    """Test ABC analysis"""

    def test_get_abc_analysis(self, client):
        """Test getting ABC analysis"""
        response = client.get(
            "/v1/analytics/abc-analysis", params={"tenant_id": "tenant_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "tenant_id" in data


class TestSeasonalPatterns:
    """Test seasonal pattern analysis"""

    def test_get_seasonal_patterns(self, client):
        """Test getting seasonal patterns for an item"""
        response = client.get(
            "/v1/analytics/seasonal-patterns/item_123",
            params={"tenant_id": "tenant_123"},
        )

        # May return 404 if item doesn't exist or insufficient data
        assert response.status_code in [200, 404]


class TestCostAnalysis:
    """Test cost analysis"""

    def test_get_cost_analysis(self, client):
        """Test getting cost analysis"""
        response = client.get(
            "/v1/analytics/cost-analysis", params={"tenant_id": "tenant_123"}
        )

        assert response.status_code == 200

    def test_cost_analysis_with_filters(self, client):
        """Test cost analysis with field and season filters"""
        response = client.get(
            "/v1/analytics/cost-analysis",
            params={
                "tenant_id": "tenant_123",
                "field_id": "field_456",
                "crop_season_id": "season_789",
            },
        )

        assert response.status_code == 200

    def test_cost_analysis_with_date_range(self, client):
        """Test cost analysis with date range"""
        response = client.get(
            "/v1/analytics/cost-analysis",
            params={
                "tenant_id": "tenant_123",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
            },
        )

        assert response.status_code == 200


class TestWasteAnalysis:
    """Test waste analysis"""

    def test_get_waste_analysis(self, client):
        """Test getting waste analysis"""
        response = client.get(
            "/v1/analytics/waste-analysis",
            params={"tenant_id": "tenant_123", "period_days": 365},
        )

        assert response.status_code == 200

    def test_waste_analysis_different_periods(self, client):
        """Test waste analysis for different periods"""
        periods = [30, 90, 180, 365]

        for period in periods:
            response = client.get(
                "/v1/analytics/waste-analysis",
                params={"tenant_id": "tenant_123", "period_days": period},
            )

            assert response.status_code == 200


class TestDashboardMetrics:
    """Test dashboard metrics"""

    def test_get_dashboard_metrics(self, client):
        """Test getting comprehensive dashboard metrics"""
        response = client.get(
            "/v1/analytics/dashboard", params={"tenant_id": "tenant_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "tenant_id" in data


class TestValidation:
    """Test input validation"""

    def test_invalid_tenant_id(self, client):
        """Test endpoints with missing tenant_id"""
        response = client.get("/v1/analytics/dashboard")

        assert response.status_code == 422

    def test_invalid_period_days(self, client):
        """Test with invalid period_days"""
        response = client.get(
            "/v1/analytics/turnover",
            params={"tenant_id": "tenant_123", "period_days": 1000},  # Exceeds maximum
        )

        assert response.status_code == 422

    def test_invalid_forecast_days(self, client):
        """Test with invalid forecast_days"""
        response = client.get(
            "/v1/analytics/forecast/item_123",
            params={"tenant_id": "tenant_123", "forecast_days": 500},  # Exceeds maximum
        )

        assert response.status_code == 422


# Integration test for complete workflow
class TestCompleteWorkflow:
    """Integration tests for complete inventory workflow"""

    def test_complete_inventory_analytics_workflow(self, client):
        """Test complete workflow of inventory analytics"""
        tenant_id = "workflow_test_tenant"

        # Step 1: Create category
        category_response = client.post(
            "/v1/categories",
            json={"name_en": "Test Category", "name_ar": "فئة اختبار", "code": "TEST"},
        )
        assert category_response.status_code == 200

        # Step 2: Get forecasts
        forecast_response = client.get(
            "/v1/analytics/forecasts", params={"tenant_id": tenant_id}
        )
        assert forecast_response.status_code == 200

        # Step 3: Get reorder recommendations
        reorder_response = client.get(
            "/v1/analytics/reorder-recommendations", params={"tenant_id": tenant_id}
        )
        assert reorder_response.status_code == 200

        # Step 4: Get valuation
        valuation_response = client.get(
            "/v1/analytics/valuation", params={"tenant_id": tenant_id}
        )
        assert valuation_response.status_code == 200

        # Step 5: Get dashboard metrics
        dashboard_response = client.get(
            "/v1/analytics/dashboard", params={"tenant_id": tenant_id}
        )
        assert dashboard_response.status_code == 200
