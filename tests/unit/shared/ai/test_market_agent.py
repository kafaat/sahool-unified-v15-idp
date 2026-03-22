"""
Tests for shared/ai/agents/market_agent.py
اختبارات وكيل السوق

Tests cover:
- Data model creation (MarketPrice, PriceForcast, SellingRecommendation, BuyerMatch)
- MarketSubAgent initialization (via patched base)
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


@pytest.fixture
def market_agent():
    """Create a MarketSubAgent with mocked base init.
    إنشاء وكيل سوق مع تهيئة أساسية محاكاة"""
    with patch("shared.ai.agents.market_agent.BaseAutonomousAgent.__init__", return_value=None):
        agent = MarketSubAgent.__new__(MarketSubAgent)
        agent.agent_id = "market-sub-agent"
        agent.name = "Market Specialist"
        agent.name_ar = "متخصص السوق"
        agent.description = "Specialized agent for market intelligence and selling advice"
        agent.description_ar = "وكيل متخصص للذكاء السوقي ونصائح البيع"
        agent.mode = AgentMode.EXECUTE
        agent.tenant_id = "sahool"
        agent.collaboration_role = CollaborationRole.SPECIALIST
        agent.market_api_url = None
        agent._price_cache = {}
        agent.tools = {}
        agent.capabilities = []
        agent.state = "idle"
        agent.current_task = None
        agent.steps = []
        agent.current_step_index = 0
        agent.execution_history = []
        return agent


class TestMarketSubAgentInit:
    """Tests for MarketSubAgent configuration.
    اختبارات تكوين وكيل السوق"""

    def test_supported_commodities(self):
        """Test that supported commodities are defined."""
        assert "wheat" in MarketSubAgent.SUPPORTED_COMMODITIES
        assert "dates" in MarketSubAgent.SUPPORTED_COMMODITIES
        assert "barley" in MarketSubAgent.SUPPORTED_COMMODITIES
        assert len(MarketSubAgent.SUPPORTED_COMMODITIES) == 10

    def test_agent_attributes(self, market_agent):
        """Test agent attributes after creation."""
        assert market_agent.agent_id == "market-sub-agent"
        assert market_agent.name == "Market Specialist"
        assert market_agent.market_api_url is None


class TestMarketSubAgentDecompose:
    """Tests for task decomposition.
    اختبارات تحليل المهام"""

    @pytest.mark.asyncio
    async def test_decompose_price_task(self, market_agent):
        """Test decomposing a price inquiry."""
        steps = await market_agent.decompose_task(
            "What is the price of wheat?",
            {"commodity": "wheat"},
        )
        assert len(steps) == 1
        assert steps[0].tool_name == "get_market_prices"

    @pytest.mark.asyncio
    async def test_decompose_arabic_price_task(self, market_agent):
        """Test decomposing an Arabic price inquiry."""
        steps = await market_agent.decompose_task("ما سعر القمح؟", {"commodity": "wheat"})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_market_prices"

    @pytest.mark.asyncio
    async def test_decompose_sell_task(self, market_agent):
        """Test decomposing a selling request generates 3 steps."""
        steps = await market_agent.decompose_task(
            "I want to sell wheat",
            {"commodity": "wheat", "quantity_tons": 50},
        )
        assert len(steps) == 3
        tool_names = [s.tool_name for s in steps]
        assert "get_market_prices" in tool_names
        assert "get_selling_recommendation" in tool_names
        assert "find_buyers" in tool_names

    @pytest.mark.asyncio
    async def test_decompose_buyer_task(self, market_agent):
        """Test decomposing a buyer search request."""
        steps = await market_agent.decompose_task("Find buyers for dates", {"commodity": "dates"})
        assert len(steps) == 1
        assert steps[0].tool_name == "find_buyers"

    @pytest.mark.asyncio
    async def test_decompose_forecast_task(self, market_agent):
        """Test decomposing a price forecast request."""
        steps = await market_agent.decompose_task("What is the forecast for wheat?", {"commodity": "wheat"})
        assert len(steps) == 1
        assert steps[0].tool_name == "get_price_forecast"

    @pytest.mark.asyncio
    async def test_decompose_default_task(self, market_agent):
        """Test default decomposition returns comprehensive analysis."""
        steps = await market_agent.decompose_task("analyze the market", {"commodity": "wheat"})
        assert len(steps) == 3
        assert steps[0].tool_name == "get_market_prices"
        assert steps[1].tool_name == "analyze_market_demand"
        assert steps[2].tool_name == "get_price_forecast"


class TestMarketSubAgentValidation:
    """Tests for step result validation.
    اختبارات التحقق من نتائج الخطوات"""

    @pytest.mark.asyncio
    async def test_validate_success(self, market_agent):
        """Test validating a successful result."""
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="get_market_prices", tool_input={},
        )
        result = ToolResult(tool_name="get_market_prices", success=True, result={"prices": []}, error=None)
        valid, msg = await market_agent.validate_step_result(step, result, {})
        assert valid is True
        assert msg is None

    @pytest.mark.asyncio
    async def test_validate_failure(self, market_agent):
        """Test validating a failed result."""
        step = AgentStep(
            step_id="1", step_number=1,
            description="test", description_ar="اختبار",
            tool_name="get_market_prices", tool_input={},
        )
        result = ToolResult(tool_name="get_market_prices", success=False, result=None, error="API error")
        valid, msg = await market_agent.validate_step_result(step, result, {})
        assert valid is False
        assert "API error" in msg


class TestMarketToolHandlers:
    """Tests for tool handler methods.
    اختبارات معالجات الأدوات"""

    @pytest.mark.asyncio
    async def test_get_market_prices(self, market_agent):
        """Test getting market prices for a commodity."""
        result = await market_agent._get_market_prices(commodity="wheat")
        assert result["commodity"] == "wheat"
        assert result["commodity_ar"] == "قمح"
        assert "prices" in result
        assert len(result["prices"]) == 4
        assert "average_price" in result
        assert "highest_price" in result
        assert "lowest_price" in result

    @pytest.mark.asyncio
    async def test_get_market_prices_unknown_commodity(self, market_agent):
        """Test getting prices for unknown commodity uses defaults."""
        result = await market_agent._get_market_prices(commodity="quinoa")
        assert result["commodity"] == "quinoa"
        assert len(result["prices"]) == 4

    @pytest.mark.asyncio
    async def test_get_market_prices_with_quality(self, market_agent):
        """Test getting prices with quality grade filter."""
        result = await market_agent._get_market_prices(commodity="wheat", quality_grade="B")
        for price in result["prices"]:
            assert price["quality_grade"] == "B"

    @pytest.mark.asyncio
    async def test_get_price_forecast(self, market_agent):
        """Test getting price forecast."""
        result = await market_agent._get_price_forecast(commodity="wheat", days_ahead=14)
        assert result["commodity"] == "wheat"
        assert "forecast_prices" in result
        assert "trend" in result
        assert "trend_ar" in result
        assert result["confidence"] == 0.75

    @pytest.mark.asyncio
    async def test_get_selling_recommendation_urgent(self, market_agent):
        """Test getting urgent selling recommendation."""
        result = await market_agent._get_selling_recommendation(
            commodity="wheat",
            quantity_tons=50,
            urgent=True,
        )
        assert result["action"] == "sell_now"
        assert result["action_ar"] == "البيع الآن"
        assert result["commodity"] == "wheat"
        assert result["quantity_tons"] == 50

    @pytest.mark.asyncio
    async def test_get_selling_recommendation_has_markets(self, market_agent):
        """Test selling recommendation includes target markets."""
        result = await market_agent._get_selling_recommendation(
            commodity="wheat",
            quantity_tons=10,
        )
        assert "target_markets" in result
        assert "target_markets_ar" in result
        assert "recommendation_id" in result
        assert "expected_total_value" in result

    @pytest.mark.asyncio
    async def test_find_buyers_wheat(self, market_agent):
        """Test finding buyers for wheat."""
        result = await market_agent._find_buyers(commodity="wheat")
        assert result["commodity"] == "wheat"
        assert result["total_matches"] > 0
        assert len(result["buyers"]) > 0
        buyer_ids = [b["buyer_id"] for b in result["buyers"]]
        assert "B001" in buyer_ids
        assert "B004" in buyer_ids

    @pytest.mark.asyncio
    async def test_find_buyers_filtered_by_type(self, market_agent):
        """Test finding buyers filtered by buyer type."""
        result = await market_agent._find_buyers(
            commodity="wheat",
            buyer_type="exporter",
        )
        for buyer in result["buyers"]:
            assert buyer["type"] == "exporter"

    @pytest.mark.asyncio
    async def test_find_buyers_no_match(self, market_agent):
        """Test finding buyers for commodity with no matches."""
        result = await market_agent._find_buyers(commodity="avocado")
        assert result["total_matches"] == 0
        assert "لم يتم العثور" in result["recommendation_ar"]

    @pytest.mark.asyncio
    async def test_analyze_market_demand(self, market_agent):
        """Test analyzing market demand."""
        result = await market_agent._analyze_market_demand(commodity="wheat")
        assert result["commodity"] == "wheat"
        assert "demand" in result
        assert result["demand"]["level"] == "high"
        assert "supply" in result

    @pytest.mark.asyncio
    async def test_analyze_market_demand_unknown(self, market_agent):
        """Test analyzing demand for unknown commodity."""
        result = await market_agent._analyze_market_demand(commodity="quinoa")
        assert result["demand"]["level"] == "medium"

    @pytest.mark.asyncio
    async def test_calculate_profit_margin(self, market_agent):
        """Test calculating profit margin."""
        result = await market_agent._calculate_profit_margin(
            commodity="wheat",
            quantity_tons=10,
            production_cost_per_kg=1.0,
            selling_price_per_kg=2.0,
        )
        assert result["commodity"] == "wheat"
        assert result["quantity_kg"] == 10000
        assert result["profit"]["gross"] > 0
        assert result["profit"]["margin_percent"] > 0

    @pytest.mark.asyncio
    async def test_calculate_profit_margin_with_storage(self, market_agent):
        """Test calculating profit margin with storage costs."""
        result = await market_agent._calculate_profit_margin(
            commodity="wheat",
            quantity_tons=10,
            production_cost_per_kg=1.0,
            selling_price_per_kg=2.0,
            storage_days=30,
        )
        assert result["costs"]["storage"] > 0

    @pytest.mark.asyncio
    async def test_calculate_profit_margin_auto_price(self, market_agent):
        """Test calculating profit margin with automatic market price."""
        result = await market_agent._calculate_profit_margin(
            commodity="wheat",
            quantity_tons=5,
            production_cost_per_kg=1.0,
        )
        assert result["revenue"]["price_per_kg"] > 0

    @pytest.mark.asyncio
    async def test_compare_markets(self, market_agent):
        """Test comparing markets for a commodity."""
        result = await market_agent._compare_markets(commodity="wheat")
        assert result["commodity"] == "wheat"
        assert len(result["comparison"]) > 0
        assert "best_market" in result
        assert "worst_market" in result
        assert "price_spread_percent" in result
        prices = [m["price_per_kg"] for m in result["comparison"]]
        assert prices == sorted(prices, reverse=True)


class TestMarketFactoryFunction:
    """Tests for factory function.
    اختبارات دالة الإنشاء"""

    def test_create_market_agent_factory(self):
        """Test factory function creates correct type."""
        with patch("shared.ai.agents.market_agent.BaseAutonomousAgent.__init__", return_value=None):
            with patch.object(MarketSubAgent, "_register_default_tools"):
                with patch.object(MarketSubAgent, "_register_default_capabilities"):
                    agent = create_market_agent(tenant_id="farm_456")
                    assert isinstance(agent, MarketSubAgent)
