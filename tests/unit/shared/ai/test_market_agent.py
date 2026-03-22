"""
Tests for shared/ai/agents/market_agent.py
اختبارات وكيل السوق

Tests cover:
- MarketSubAgent instantiation and configuration
- Data model creation (MarketPrice, PriceForcast, SellingRecommendation, BuyerMatch)
- Task decomposition for various market queries
- Tool handler methods (prices, forecast, selling, buyers, demand, profit, compare)
- Step result validation
- Factory function
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import UTC, datetime

from shared.ai.agents.market_agent import (
    MarketSubAgent,
    MarketPrice,
    PriceForcast,
    SellingRecommendation,
    BuyerMatch,
    create_market_agent,
)
from shared.ai.agents.base import AgentMode, AgentStep, CollaborationRole, ToolResult


class TestMarketDataModels:
    """Tests for market data models.
    اختبارات نماذج بيانات السوق"""

    def test_market_price_creation(self):
        """Test creating a MarketPrice instance."""
        price = MarketPrice(
            commodity="wheat",
            commodity_ar="قمح",
            price_per_kg=1.85,
            currency="SAR",
            market="Riyadh Wholesale",
            market_ar="جملة الرياض",
            date=datetime.now(UTC),
            quality_grade="A",
            trend="up",
            trend_ar="صاعد",
            change_percent=2.5,
        )
        assert price.commodity == "wheat"
        assert price.price_per_kg == 1.85
        assert price.trend == "up"

    def test_price_forcast_creation(self):
        """Test creating a PriceForcast instance."""
        forecast = PriceForcast(
            commodity="dates",
            commodity_ar="تمور",
            current_price=12.0,
            forecast_prices=[{"date": "2026-02-01", "price": 12.5}],
            trend="up",
            trend_ar="صاعد",
            factors=["Seasonal demand"],
            factors_ar=["الطلب الموسمي"],
            confidence=0.8,
        )
        assert forecast.commodity == "dates"
        assert forecast.confidence == 0.8

    def test_selling_recommendation_creation(self):
        """Test creating a SellingRecommendation instance."""
        rec = SellingRecommendation(
            recommendation_id="rec-001",
            action="hold",
            action_ar="الاحتفاظ",
            confidence=0.85,
            reasoning="Prices trending up",
            reasoning_ar="الأسعار في اتجاه صعودي",
            expected_price=2.0,
            optimal_timing="2-4 weeks",
            optimal_timing_ar="2-4 أسابيع",
            target_markets=["Riyadh"],
            target_markets_ar=["الرياض"],
        )
        assert rec.action == "hold"
        assert rec.created_at is not None

    def test_buyer_match_creation(self):
        """Test creating a BuyerMatch instance."""
        buyer = BuyerMatch(
            buyer_id="B001",
            buyer_name="Al-Marai",
            buyer_type="wholesaler",
            buyer_type_ar="تاجر جملة",
            location="Riyadh",
            location_ar="الرياض",
            commodities_wanted=["wheat", "barley"],
            typical_volume=100.0,
            payment_terms="Net 15",
            payment_terms_ar="صافي 15 يوم",
            match_score=0.85,
            contact_preference="email",
        )
        assert buyer.buyer_id == "B001"
        assert buyer.match_score == 0.85


class TestMarketSubAgentInit:
    """Tests for MarketSubAgent initialization.
    اختبارات تهيئة وكيل السوق"""

    def test_default_initialization(self):
        """Test default agent initialization."""
        agent = MarketSubAgent()
        assert agent.agent_id == "market-sub-agent"
        assert agent.name == "Market Specialist"
        assert agent.name_ar == "متخصص السوق"
        assert agent.mode == AgentMode.EXECUTE
        assert agent.tenant_id == "sahool"
        assert agent.collaboration_role == CollaborationRole.SPECIALIST
        assert agent.market_api_url is None

    def test_custom_initialization(self):
        """Test agent initialization with custom parameters."""
        agent = MarketSubAgent(
            tenant_id="farm_001",
            market_api_url="https://market.api.example.com",
        )
        assert agent.tenant_id == "farm_001"
        assert agent.market_api_url == "https://market.api.example.com"

    def test_supported_commodities(self):
        """Test that supported commodities are defined."""
        assert "wheat" in MarketSubAgent.SUPPORTED_COMMODITIES
        assert "dates" in MarketSubAgent.SUPPORTED_COMMODITIES
        assert "barley" in MarketSubAgent.SUPPORTED_COMMODITIES
        assert len(MarketSubAgent.SUPPORTED_COMMODITIES) == 10


class TestMarketSubAgentDecompose:
    """Tests for task decomposition.
    اختبارات تحليل المهام"""

    @pytest.mark.asyncio
    async def test_decompose_price_task(self):
        """Test decomposing a price inquiry."""
        agent = MarketSubAgent()
        steps = await agent.decompose_task("What is the price of wheat?", {"commodity": "wheat"})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_market_prices"

    @pytest.mark.asyncio
    async def test_decompose_arabic_price_task(self):
        """Test decomposing an Arabic price inquiry."""
        agent = MarketSubAgent()
        steps = await agent.decompose_task("ما سعر القمح؟", {"commodity": "wheat"})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_market_prices"

    @pytest.mark.asyncio
    async def test_decompose_sell_task(self):
        """Test decomposing a selling request generates 3 steps."""
        agent = MarketSubAgent()
        steps = await agent.decompose_task("I want to sell wheat", {"commodity": "wheat", "quantity_tons": 50})
        assert len(steps) == 3
        tool_names = [s.tool_name for s in steps]
        assert "get_market_prices" in tool_names
        assert "get_selling_recommendation" in tool_names
        assert "find_buyers" in tool_names

    @pytest.mark.asyncio
    async def test_decompose_buyer_task(self):
        """Test decomposing a buyer search request."""
        agent = MarketSubAgent()
        steps = await agent.decompose_task("Find buyers for dates", {"commodity": "dates"})
        assert len(steps) == 1
        assert steps[0].tool_name == "find_buyers"

    @pytest.mark.asyncio
    async def test_decompose_forecast_task(self):
        """Test decomposing a price forecast request."""
        agent = MarketSubAgent()
        steps = await agent.decompose_task("Price forecast for wheat", {"commodity": "wheat"})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_price_forecast"

    @pytest.mark.asyncio
    async def test_decompose_default_task(self):
        """Test default decomposition returns comprehensive analysis."""
        agent = MarketSubAgent()
        steps = await agent.decompose_task("analyze the market", {"commodity": "wheat"})
        assert len(steps) == 3
        assert steps[0].tool_name == "get_market_prices"
        assert steps[1].tool_name == "analyze_market_demand"
        assert steps[2].tool_name == "get_price_forecast"


class TestMarketSubAgentValidation:
    """Tests for step result validation.
    اختبارات التحقق من نتائج الخطوات"""

    @pytest.mark.asyncio
    async def test_validate_success(self):
        """Test validating a successful result."""
        agent = MarketSubAgent()
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="get_market_prices", tool_input={},
        )
        result = ToolResult(success=True, result={"prices": []}, error=None)
        valid, msg = await agent.validate_step_result(step, result, {})
        assert valid is True
        assert msg is None

    @pytest.mark.asyncio
    async def test_validate_failure(self):
        """Test validating a failed result."""
        agent = MarketSubAgent()
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="get_market_prices", tool_input={},
        )
        result = ToolResult(success=False, result=None, error="API error")
        valid, msg = await agent.validate_step_result(step, result, {})
        assert valid is False
        assert "API error" in msg


class TestMarketToolHandlers:
    """Tests for tool handler methods.
    اختبارات معالجات الأدوات"""

    @pytest.mark.asyncio
    async def test_get_market_prices(self):
        """Test getting market prices for a commodity."""
        agent = MarketSubAgent()
        result = await agent._get_market_prices(commodity="wheat")
        assert result["commodity"] == "wheat"
        assert result["commodity_ar"] == "قمح"
        assert "prices" in result
        assert len(result["prices"]) == 4  # 4 markets
        assert "average_price" in result
        assert "highest_price" in result
        assert "lowest_price" in result

    @pytest.mark.asyncio
    async def test_get_market_prices_unknown_commodity(self):
        """Test getting prices for unknown commodity uses defaults."""
        agent = MarketSubAgent()
        result = await agent._get_market_prices(commodity="quinoa")
        assert result["commodity"] == "quinoa"
        assert len(result["prices"]) == 4

    @pytest.mark.asyncio
    async def test_get_market_prices_with_quality(self):
        """Test getting prices with quality grade filter."""
        agent = MarketSubAgent()
        result = await agent._get_market_prices(commodity="wheat", quality_grade="B")
        for price in result["prices"]:
            assert price["quality_grade"] == "B"

    @pytest.mark.asyncio
    async def test_get_price_forecast(self):
        """Test getting price forecast."""
        agent = MarketSubAgent()
        result = await agent._get_price_forecast(commodity="wheat", days_ahead=14)
        assert result["commodity"] == "wheat"
        assert "forecast_prices" in result
        assert "trend" in result
        assert "trend_ar" in result
        assert result["confidence"] == 0.75

    @pytest.mark.asyncio
    async def test_get_selling_recommendation_urgent(self):
        """Test getting urgent selling recommendation."""
        agent = MarketSubAgent()
        result = await agent._get_selling_recommendation(
            commodity="wheat",
            quantity_tons=50,
            urgent=True,
        )
        assert result["action"] == "sell_now"
        assert result["action_ar"] == "البيع الآن"
        assert result["commodity"] == "wheat"
        assert result["quantity_tons"] == 50

    @pytest.mark.asyncio
    async def test_get_selling_recommendation_has_markets(self):
        """Test selling recommendation includes target markets."""
        agent = MarketSubAgent()
        result = await agent._get_selling_recommendation(
            commodity="wheat",
            quantity_tons=10,
        )
        assert "target_markets" in result
        assert "target_markets_ar" in result
        assert "recommendation_id" in result
        assert "expected_total_value" in result

    @pytest.mark.asyncio
    async def test_find_buyers_wheat(self):
        """Test finding buyers for wheat."""
        agent = MarketSubAgent()
        result = await agent._find_buyers(commodity="wheat")
        assert result["commodity"] == "wheat"
        assert result["total_matches"] > 0
        assert len(result["buyers"]) > 0
        # Wheat buyers should include Al-Marai and Saudi Grains
        buyer_ids = [b["buyer_id"] for b in result["buyers"]]
        assert "B001" in buyer_ids  # Al-Marai
        assert "B004" in buyer_ids  # Saudi Grains

    @pytest.mark.asyncio
    async def test_find_buyers_filtered_by_type(self):
        """Test finding buyers filtered by buyer type."""
        agent = MarketSubAgent()
        result = await agent._find_buyers(
            commodity="wheat",
            buyer_type="exporter",
        )
        for buyer in result["buyers"]:
            assert buyer["type"] == "exporter"

    @pytest.mark.asyncio
    async def test_find_buyers_no_match(self):
        """Test finding buyers for commodity with no matches."""
        agent = MarketSubAgent()
        result = await agent._find_buyers(commodity="avocado")
        assert result["total_matches"] == 0
        assert "لم يتم العثور" in result["recommendation_ar"]

    @pytest.mark.asyncio
    async def test_analyze_market_demand(self):
        """Test analyzing market demand."""
        agent = MarketSubAgent()
        result = await agent._analyze_market_demand(commodity="wheat")
        assert result["commodity"] == "wheat"
        assert "demand" in result
        assert result["demand"]["level"] == "high"
        assert "supply" in result
        assert "key_factors" in result

    @pytest.mark.asyncio
    async def test_analyze_market_demand_unknown(self):
        """Test analyzing demand for unknown commodity."""
        agent = MarketSubAgent()
        result = await agent._analyze_market_demand(commodity="quinoa")
        assert result["demand"]["level"] == "medium"

    @pytest.mark.asyncio
    async def test_calculate_profit_margin(self):
        """Test calculating profit margin."""
        agent = MarketSubAgent()
        result = await agent._calculate_profit_margin(
            commodity="wheat",
            quantity_tons=10,
            production_cost_per_kg=1.0,
            selling_price_per_kg=2.0,
        )
        assert result["commodity"] == "wheat"
        assert result["quantity_tons"] == 10
        assert result["quantity_kg"] == 10000
        assert result["costs"]["production_per_kg"] == 1.0
        assert result["revenue"]["price_per_kg"] == 2.0
        assert result["profit"]["gross"] > 0
        assert result["profit"]["margin_percent"] > 0

    @pytest.mark.asyncio
    async def test_calculate_profit_margin_with_storage(self):
        """Test calculating profit margin with storage costs."""
        agent = MarketSubAgent()
        result = await agent._calculate_profit_margin(
            commodity="wheat",
            quantity_tons=10,
            production_cost_per_kg=1.0,
            selling_price_per_kg=2.0,
            storage_days=30,
        )
        assert result["costs"]["storage"] > 0

    @pytest.mark.asyncio
    async def test_calculate_profit_margin_auto_price(self):
        """Test calculating profit margin with automatic market price."""
        agent = MarketSubAgent()
        result = await agent._calculate_profit_margin(
            commodity="wheat",
            quantity_tons=5,
            production_cost_per_kg=1.0,
        )
        # Should have fetched market price automatically
        assert result["revenue"]["price_per_kg"] > 0

    @pytest.mark.asyncio
    async def test_compare_markets(self):
        """Test comparing markets for a commodity."""
        agent = MarketSubAgent()
        result = await agent._compare_markets(commodity="wheat")
        assert result["commodity"] == "wheat"
        assert "comparison" in result
        assert len(result["comparison"]) > 0
        assert "best_market" in result
        assert "worst_market" in result
        assert "price_spread_percent" in result
        # Comparison should be sorted by price descending
        prices = [m["price_per_kg"] for m in result["comparison"]]
        assert prices == sorted(prices, reverse=True)


class TestMarketFactoryFunction:
    """Tests for factory function.
    اختبارات دالة الإنشاء"""

    def test_create_market_agent_default(self):
        """Test creating agent with defaults."""
        agent = create_market_agent()
        assert isinstance(agent, MarketSubAgent)
        assert agent.tenant_id == "sahool"

    def test_create_market_agent_custom(self):
        """Test creating agent with custom tenant."""
        agent = create_market_agent(tenant_id="farm_456")
        assert agent.tenant_id == "farm_456"
