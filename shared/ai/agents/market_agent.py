"""
Market Sub-Agent
=================
وكيل فرعي للسوق

Specialized sub-agent for agricultural market intelligence and
pricing/selling advice.

Features:
- Market price analysis and forecasting
- Optimal selling time recommendations
- Buyer/marketplace matching
- Price trend analysis
- Contract negotiation support
- Market demand forecasting

Author: SAHOOL Platform Team
Created: January 2026
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any

import structlog

from .base import (
    AgentMode,
    AgentStep,
    AgentTool,
    AgentCapability,
    BaseAutonomousAgent,
    CollaborationRole,
    ToolResult,
)
from ..llm_provider import LLMProviderManager

logger = structlog.get_logger()


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class MarketPrice:
    """
    Market price information for a commodity.
    معلومات سعر السوق لسلعة
    """

    commodity: str
    commodity_ar: str
    price_per_kg: float
    currency: str  # SAR, USD, etc.
    market: str
    market_ar: str
    date: datetime
    quality_grade: str
    trend: str  # up, down, stable
    trend_ar: str
    change_percent: float


@dataclass
class PriceForcast:
    """
    Price forecast for a commodity.
    توقعات السعر لسلعة
    """

    commodity: str
    commodity_ar: str
    current_price: float
    forecast_prices: list[dict[str, Any]]  # {date, price, confidence}
    trend: str
    trend_ar: str
    factors: list[str]
    factors_ar: list[str]
    confidence: float


@dataclass
class SellingRecommendation:
    """
    Recommendation for optimal selling.
    توصية للبيع الأمثل
    """

    recommendation_id: str
    action: str  # sell_now, hold, sell_partial
    action_ar: str
    confidence: float
    reasoning: str
    reasoning_ar: str
    expected_price: float
    optimal_timing: str
    optimal_timing_ar: str
    target_markets: list[str]
    target_markets_ar: list[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class BuyerMatch:
    """
    Potential buyer match.
    مطابقة مشتري محتمل
    """

    buyer_id: str
    buyer_name: str
    buyer_type: str  # wholesaler, retailer, exporter, processor
    buyer_type_ar: str
    location: str
    location_ar: str
    commodities_wanted: list[str]
    typical_volume: float
    payment_terms: str
    payment_terms_ar: str
    match_score: float
    contact_preference: str


# ============================================================================
# MARKET SUB-AGENT
# ============================================================================


class MarketSubAgent(BaseAutonomousAgent):
    """
    Specialized sub-agent for market intelligence and selling advice.
    وكيل فرعي متخصص للذكاء السوقي ونصائح البيع

    Provides:
    - Market price monitoring and analysis
    - Price trend forecasting
    - Optimal selling timing recommendations
    - Buyer/marketplace matching
    - Contract negotiation support
    - Demand forecasting

    Example:
        market_agent = MarketSubAgent(tenant_id="farm_001")

        # Get current prices
        prices = await market_agent.get_market_prices(
            commodity="wheat",
            region="central"
        )

        # Get selling recommendation
        recommendation = await market_agent.get_selling_recommendation(
            commodity="wheat",
            quantity_tons=50,
            quality_grade="A"
        )

        # Find buyers
        buyers = await market_agent.find_buyers(
            commodity="wheat",
            quantity_tons=50,
            location="Riyadh"
        )
    """

    # Market configuration
    SUPPORTED_COMMODITIES = [
        "wheat",
        "barley",
        "dates",
        "tomatoes",
        "cucumbers",
        "potatoes",
        "onions",
        "alfalfa",
        "corn",
        "sorghum",
    ]

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        parent_agent: BaseAutonomousAgent | None = None,
        market_api_url: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize Market Sub-Agent.
        تهيئة وكيل السوق الفرعي

        Args:
            tenant_id: Tenant ID for multi-tenancy
            llm_manager: LLM provider manager
            parent_agent: Parent agent for coordination
            market_api_url: External market API URL (optional)
        """
        super().__init__(
            agent_id=kwargs.get("agent_id", "market-sub-agent"),
            name=kwargs.get("name", "Market Specialist"),
            name_ar=kwargs.get("name_ar", "متخصص السوق"),
            description="Specialized agent for market intelligence and selling advice",
            description_ar="وكيل متخصص للذكاء السوقي ونصائح البيع",
            mode=AgentMode.EXECUTE,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            parent_agent=parent_agent,
            collaboration_role=CollaborationRole.SPECIALIST,
        )

        self.market_api_url = market_api_url
        self._price_cache: dict[str, list[MarketPrice]] = {}

    def _register_default_tools(self) -> None:
        """Register market-specific tools."""

        # Tool 1: Get Market Prices
        self.register_tool(
            AgentTool(
                name="get_market_prices",
                name_ar="الحصول على أسعار السوق",
                description="Get current market prices for agricultural commodities",
                description_ar="الحصول على أسعار السوق الحالية للسلع الزراعية",
                input_schema={
                    "type": "object",
                    "properties": {
                        "commodity": {"type": "string"},
                        "region": {"type": "string"},
                        "quality_grade": {"type": "string"},
                    },
                    "required": ["commodity"],
                },
                handler=self._get_market_prices,
                tags=["market", "prices"],
            )
        )

        # Tool 2: Get Price Forecast
        self.register_tool(
            AgentTool(
                name="get_price_forecast",
                name_ar="الحصول على توقعات الأسعار",
                description="Get price forecast for a commodity",
                description_ar="الحصول على توقعات أسعار سلعة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "commodity": {"type": "string"},
                        "days_ahead": {"type": "integer", "default": 30},
                    },
                    "required": ["commodity"],
                },
                handler=self._get_price_forecast,
                tags=["market", "forecast"],
            )
        )

        # Tool 3: Get Selling Recommendation
        self.register_tool(
            AgentTool(
                name="get_selling_recommendation",
                name_ar="الحصول على توصية البيع",
                description="Get recommendation for optimal selling strategy",
                description_ar="الحصول على توصية لاستراتيجية البيع المثلى",
                input_schema={
                    "type": "object",
                    "properties": {
                        "commodity": {"type": "string"},
                        "quantity_tons": {"type": "number"},
                        "quality_grade": {"type": "string"},
                        "storage_cost_per_day": {"type": "number"},
                        "urgent": {"type": "boolean", "default": False},
                    },
                    "required": ["commodity", "quantity_tons"],
                },
                handler=self._get_selling_recommendation,
                tags=["market", "selling", "recommendation"],
            )
        )

        # Tool 4: Find Buyers
        self.register_tool(
            AgentTool(
                name="find_buyers",
                name_ar="البحث عن مشترين",
                description="Find potential buyers for agricultural products",
                description_ar="البحث عن مشترين محتملين للمنتجات الزراعية",
                input_schema={
                    "type": "object",
                    "properties": {
                        "commodity": {"type": "string"},
                        "quantity_tons": {"type": "number"},
                        "quality_grade": {"type": "string"},
                        "location": {"type": "string"},
                        "buyer_type": {
                            "type": "string",
                            "enum": ["any", "wholesaler", "retailer", "exporter", "processor"],
                        },
                    },
                    "required": ["commodity"],
                },
                handler=self._find_buyers,
                tags=["market", "buyers"],
            )
        )

        # Tool 5: Analyze Market Demand
        self.register_tool(
            AgentTool(
                name="analyze_market_demand",
                name_ar="تحليل طلب السوق",
                description="Analyze current and projected market demand",
                description_ar="تحليل طلب السوق الحالي والمتوقع",
                input_schema={
                    "type": "object",
                    "properties": {
                        "commodity": {"type": "string"},
                        "region": {"type": "string"},
                        "timeframe": {
                            "type": "string",
                            "enum": ["current", "monthly", "seasonal", "annual"],
                        },
                    },
                    "required": ["commodity"],
                },
                handler=self._analyze_market_demand,
                tags=["market", "demand", "analysis"],
            )
        )

        # Tool 6: Calculate Profit Margin
        self.register_tool(
            AgentTool(
                name="calculate_profit_margin",
                name_ar="حساب هامش الربح",
                description="Calculate expected profit margin for a sale",
                description_ar="حساب هامش الربح المتوقع لعملية بيع",
                input_schema={
                    "type": "object",
                    "properties": {
                        "commodity": {"type": "string"},
                        "quantity_tons": {"type": "number"},
                        "production_cost_per_kg": {"type": "number"},
                        "selling_price_per_kg": {"type": "number"},
                        "transportation_cost": {"type": "number"},
                        "storage_days": {"type": "integer"},
                    },
                    "required": ["commodity", "quantity_tons", "production_cost_per_kg"],
                },
                handler=self._calculate_profit_margin,
                tags=["market", "profit", "calculation"],
            )
        )

        # Tool 7: Compare Markets
        self.register_tool(
            AgentTool(
                name="compare_markets",
                name_ar="مقارنة الأسواق",
                description="Compare prices and conditions across different markets",
                description_ar="مقارنة الأسعار والظروف عبر أسواق مختلفة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "commodity": {"type": "string"},
                        "markets": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["commodity"],
                },
                handler=self._compare_markets,
                tags=["market", "comparison"],
            )
        )

    def _register_default_capabilities(self) -> None:
        """Register market capabilities."""
        self.register_capability(
            AgentCapability(
                name="market_analysis",
                name_ar="تحليل السوق",
                description="Analyze agricultural market prices and trends",
                description_ar="تحليل أسعار واتجاهات السوق الزراعي",
                domains=["market", "pricing", "analysis"],
                skill_level=0.9,
            )
        )

        self.register_capability(
            AgentCapability(
                name="selling_advisory",
                name_ar="استشارات البيع",
                description="Provide selling recommendations and buyer matching",
                description_ar="تقديم توصيات البيع ومطابقة المشترين",
                domains=["market", "selling", "negotiation"],
                skill_level=0.85,
            )
        )

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """Decompose market-related task."""
        commodity = context.get("commodity", "wheat")
        quantity = context.get("quantity_tons", 10)

        task_lower = task.lower()

        # Detect task type
        if any(w in task_lower for w in ["price", "سعر", "أسعار"]):
            return [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=1,
                    description="Get market prices",
                    description_ar="الحصول على أسعار السوق",
                    tool_name="get_market_prices",
                    tool_input={"commodity": commodity},
                ),
            ]

        elif any(w in task_lower for w in ["sell", "بيع", "بع"]):
            return [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=1,
                    description="Get market prices",
                    description_ar="الحصول على أسعار السوق",
                    tool_name="get_market_prices",
                    tool_input={"commodity": commodity},
                ),
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=2,
                    description="Get selling recommendation",
                    description_ar="الحصول على توصية البيع",
                    tool_name="get_selling_recommendation",
                    tool_input={"commodity": commodity, "quantity_tons": quantity},
                ),
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=3,
                    description="Find potential buyers",
                    description_ar="البحث عن مشترين محتملين",
                    tool_name="find_buyers",
                    tool_input={"commodity": commodity, "quantity_tons": quantity},
                ),
            ]

        elif any(w in task_lower for w in ["buyer", "مشتري", "مشترين"]):
            return [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=1,
                    description="Find buyers",
                    description_ar="البحث عن مشترين",
                    tool_name="find_buyers",
                    tool_input={"commodity": commodity},
                ),
            ]

        elif any(w in task_lower for w in ["forecast", "توقع", "توقعات"]):
            return [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=1,
                    description="Get price forecast",
                    description_ar="الحصول على توقعات الأسعار",
                    tool_name="get_price_forecast",
                    tool_input={"commodity": commodity},
                ),
            ]

        # Default: comprehensive market analysis
        return [
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Get market prices",
                description_ar="الحصول على أسعار السوق",
                tool_name="get_market_prices",
                tool_input={"commodity": commodity},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Analyze market demand",
                description_ar="تحليل طلب السوق",
                tool_name="analyze_market_demand",
                tool_input={"commodity": commodity},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=3,
                description="Get price forecast",
                description_ar="الحصول على توقعات الأسعار",
                tool_name="get_price_forecast",
                tool_input={"commodity": commodity},
            ),
        ]

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate market step result."""
        if not result.success:
            return False, f"Tool failed: {result.error}"
        return True, None

    # ========================================================================
    # TOOL HANDLERS
    # ========================================================================

    async def _get_market_prices(
        self,
        commodity: str,
        region: str | None = None,
        quality_grade: str | None = None,
    ) -> dict[str, Any]:
        """Get current market prices."""
        logger.info("getting_market_prices", commodity=commodity, region=region)

        # Commodity translations
        commodity_translations = {
            "wheat": "قمح",
            "barley": "شعير",
            "dates": "تمور",
            "tomatoes": "طماطم",
            "cucumbers": "خيار",
            "potatoes": "بطاطس",
            "onions": "بصل",
            "alfalfa": "برسيم",
        }

        # Simulated market prices (in production, would call market API)
        base_prices = {
            "wheat": 1.85,
            "barley": 1.50,
            "dates": 12.00,
            "tomatoes": 3.50,
            "cucumbers": 2.80,
            "potatoes": 2.20,
            "onions": 1.80,
            "alfalfa": 0.90,
        }

        base_price = base_prices.get(commodity.lower(), 2.00)

        # Generate prices for different markets
        markets = [
            {"name": "Riyadh Wholesale", "name_ar": "جملة الرياض", "factor": 1.0},
            {"name": "Jeddah Market", "name_ar": "سوق جدة", "factor": 1.05},
            {"name": "Dammam Central", "name_ar": "الدمام المركزي", "factor": 0.98},
            {"name": "Export (GCC)", "name_ar": "التصدير (خليجي)", "factor": 1.15},
        ]

        prices = []
        for market in markets:
            price = base_price * market["factor"]
            change = (hash(commodity + market["name"]) % 10 - 5) / 100  # -5% to +5%

            prices.append(
                {
                    "market": market["name"],
                    "market_ar": market["name_ar"],
                    "price_per_kg": round(price, 2),
                    "currency": "SAR",
                    "change_percent": round(change * 100, 1),
                    "trend": "up" if change > 0.02 else "down" if change < -0.02 else "stable",
                    "trend_ar": "صاعد" if change > 0.02 else "هابط" if change < -0.02 else "مستقر",
                    "quality_grade": quality_grade or "A",
                    "last_updated": datetime.now(UTC).isoformat(),
                }
            )

        # Sort by price (highest first)
        prices.sort(key=lambda x: x["price_per_kg"], reverse=True)

        return {
            "commodity": commodity,
            "commodity_ar": commodity_translations.get(commodity.lower(), commodity),
            "region": region or "All",
            "prices": prices,
            "average_price": round(sum(p["price_per_kg"] for p in prices) / len(prices), 2),
            "highest_price": prices[0],
            "lowest_price": prices[-1],
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def _get_price_forecast(
        self,
        commodity: str,
        days_ahead: int = 30,
    ) -> dict[str, Any]:
        """Get price forecast for commodity."""
        logger.info("getting_price_forecast", commodity=commodity, days=days_ahead)

        # Get current prices
        current = await self._get_market_prices(commodity)
        current_price = current.get("average_price", 2.0)

        # Generate forecast with seasonal factors
        month = datetime.now().month

        # Seasonal factors (simplified)
        seasonal_factors = {
            "wheat": {
                1: 1.1,
                2: 1.15,
                3: 1.1,
                4: 0.95,
                5: 0.85,
                6: 0.9,
                7: 0.95,
                8: 1.0,
                9: 1.05,
                10: 1.1,
                11: 1.1,
                12: 1.1,
            },
            "dates": {
                1: 0.9,
                2: 0.85,
                3: 0.85,
                4: 0.9,
                5: 0.95,
                6: 1.0,
                7: 1.1,
                8: 1.2,
                9: 1.3,
                10: 1.2,
                11: 1.0,
                12: 0.95,
            },
        }

        factors = seasonal_factors.get(commodity.lower(), dict.fromkeys(range(1, 13), 1.0))

        forecasts = []
        for day in range(0, days_ahead, 7):  # Weekly forecasts
            future_month = ((month - 1 + (day // 30)) % 12) + 1
            factor = factors.get(future_month, 1.0)
            noise = (hash(str(day) + commodity) % 10 - 5) / 100
            forecast_price = current_price * factor * (1 + noise)

            forecasts.append(
                {
                    "days_ahead": day,
                    "price_per_kg": round(forecast_price, 2),
                    "confidence": max(0.5, 0.95 - (day * 0.01)),
                    "range_low": round(forecast_price * 0.95, 2),
                    "range_high": round(forecast_price * 1.05, 2),
                }
            )

        # Determine overall trend
        if forecasts[-1]["price_per_kg"] > current_price * 1.05:
            trend = "up"
            trend_ar = "صاعد"
        elif forecasts[-1]["price_per_kg"] < current_price * 0.95:
            trend = "down"
            trend_ar = "هابط"
        else:
            trend = "stable"
            trend_ar = "مستقر"

        return {
            "commodity": commodity,
            "current_price": current_price,
            "forecast_prices": forecasts,
            "trend": trend,
            "trend_ar": trend_ar,
            "factors": [
                "Seasonal demand patterns",
                "Regional production estimates",
                "Import/export trends",
            ],
            "factors_ar": [
                "أنماط الطلب الموسمي",
                "تقديرات الإنتاج الإقليمي",
                "اتجاهات الاستيراد/التصدير",
            ],
            "confidence": 0.75,
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def _get_selling_recommendation(
        self,
        commodity: str,
        quantity_tons: float,
        quality_grade: str | None = None,
        storage_cost_per_day: float | None = None,
        urgent: bool = False,
    ) -> dict[str, Any]:
        """Get selling recommendation."""
        logger.info("getting_selling_recommendation", commodity=commodity, quantity=quantity_tons)

        # Get current prices and forecast
        prices = await self._get_market_prices(commodity, quality_grade=quality_grade)
        forecast = await self._get_price_forecast(commodity)

        current_price = prices.get("average_price", 2.0)
        trend = forecast.get("trend", "stable")
        storage_cost = storage_cost_per_day or 0.005  # Default 0.005 SAR/kg/day

        # Decision logic
        if urgent:
            action = "sell_now"
            action_ar = "البيع الآن"
            reasoning = "Urgent sale requested - recommend selling at best available price"
            reasoning_ar = "طُلب بيع عاجل - يُنصح بالبيع بأفضل سعر متاح"
            timing = "Immediate"
            timing_ar = "فوري"
        elif trend == "up" and not urgent:
            action = "hold"
            action_ar = "الاحتفاظ"
            reasoning = "Prices trending upward. Hold for 2-4 weeks if storage permits. Expected gain: 5-10%"
            reasoning_ar = "الأسعار في اتجاه صعودي. الاحتفاظ لمدة 2-4 أسابيع إذا سمح التخزين. الربح المتوقع: 5-10%"
            timing = "2-4 weeks"
            timing_ar = "2-4 أسابيع"
        elif trend == "down":
            action = "sell_now"
            action_ar = "البيع الآن"
            reasoning = "Prices trending downward. Recommend selling soon to avoid losses"
            reasoning_ar = "الأسعار في اتجاه هبوطي. يُنصح بالبيع قريباً لتجنب الخسائر"
            timing = "Within 1 week"
            timing_ar = "خلال أسبوع"
        else:
            # Stable - consider storage costs
            storage_weeks = 4
            storage_loss = storage_cost * 7 * storage_weeks * quantity_tons * 1000
            if storage_loss > current_price * quantity_tons * 1000 * 0.03:  # More than 3% of value
                action = "sell_now"
                action_ar = "البيع الآن"
                reasoning = (
                    f"Storage costs ({storage_loss:.0f} SAR for 4 weeks) exceed potential gains"
                )
                reasoning_ar = f"تكاليف التخزين ({storage_loss:.0f} ريال لمدة 4 أسابيع) تتجاوز المكاسب المحتملة"
                timing = "Within 1-2 weeks"
                timing_ar = "خلال 1-2 أسبوع"
            else:
                action = "sell_partial"
                action_ar = "بيع جزئي"
                reasoning = "Stable market. Consider selling 50% now and 50% in 2-3 weeks"
                reasoning_ar = "سوق مستقر. يُنصح ببيع 50% الآن و50% خلال 2-3 أسابيع"
                timing = "Split over 2-3 weeks"
                timing_ar = "توزيع على 2-3 أسابيع"

        # Best markets
        best_markets = sorted(
            prices.get("prices", []), key=lambda x: x["price_per_kg"], reverse=True
        )[:3]

        return {
            "recommendation_id": str(uuid.uuid4()),
            "commodity": commodity,
            "quantity_tons": quantity_tons,
            "quality_grade": quality_grade or "A",
            "action": action,
            "action_ar": action_ar,
            "confidence": 0.8,
            "reasoning": reasoning,
            "reasoning_ar": reasoning_ar,
            "current_price_per_kg": current_price,
            "expected_total_value": round(current_price * quantity_tons * 1000, 2),
            "optimal_timing": timing,
            "optimal_timing_ar": timing_ar,
            "target_markets": [m["market"] for m in best_markets],
            "target_markets_ar": [m["market_ar"] for m in best_markets],
            "best_market": best_markets[0] if best_markets else None,
            "price_trend": trend,
            "created_at": datetime.now(UTC).isoformat(),
        }

    async def _find_buyers(
        self,
        commodity: str,
        quantity_tons: float | None = None,
        quality_grade: str | None = None,
        location: str | None = None,
        buyer_type: str = "any",
    ) -> dict[str, Any]:
        """Find potential buyers."""
        logger.info("finding_buyers", commodity=commodity, location=location)

        # Simulated buyer database
        all_buyers = [
            {
                "buyer_id": "B001",
                "name": "Al-Marai Distribution",
                "name_ar": "توزيع المراعي",
                "type": "wholesaler",
                "type_ar": "تاجر جملة",
                "location": "Riyadh",
                "location_ar": "الرياض",
                "commodities": ["wheat", "barley", "alfalfa"],
                "volume_range": "50-500 tons",
                "payment": "Net 15",
                "payment_ar": "صافي 15 يوم",
                "rating": 4.8,
            },
            {
                "buyer_id": "B002",
                "name": "Gulf Agricultural Trading",
                "name_ar": "تجارة الخليج الزراعية",
                "type": "exporter",
                "type_ar": "مصدّر",
                "location": "Dammam",
                "location_ar": "الدمام",
                "commodities": ["dates", "wheat", "vegetables"],
                "volume_range": "100-1000 tons",
                "payment": "LC",
                "payment_ar": "اعتماد مستندي",
                "rating": 4.5,
            },
            {
                "buyer_id": "B003",
                "name": "Panda Supermarkets",
                "name_ar": "أسواق بنده",
                "type": "retailer",
                "type_ar": "تاجر تجزئة",
                "location": "Multiple",
                "location_ar": "متعدد",
                "commodities": ["tomatoes", "cucumbers", "potatoes", "onions"],
                "volume_range": "10-100 tons",
                "payment": "Net 30",
                "payment_ar": "صافي 30 يوم",
                "rating": 4.7,
            },
            {
                "buyer_id": "B004",
                "name": "Saudi Grains Organization",
                "name_ar": "المؤسسة السعودية للحبوب",
                "type": "processor",
                "type_ar": "مصنّع",
                "location": "Riyadh",
                "location_ar": "الرياض",
                "commodities": ["wheat", "barley", "corn"],
                "volume_range": "500-5000 tons",
                "payment": "Government Contract",
                "payment_ar": "عقد حكومي",
                "rating": 5.0,
            },
        ]

        # Filter buyers
        matched = []
        for buyer in all_buyers:
            # Check commodity match
            if commodity.lower() not in [c.lower() for c in buyer["commodities"]]:
                continue

            # Check buyer type
            if buyer_type != "any" and buyer["type"] != buyer_type:
                continue

            # Calculate match score
            score = 0.7  # Base score for commodity match
            if location and location.lower() in buyer["location"].lower():
                score += 0.15
            score += buyer["rating"] / 50  # Rating contribution

            matched.append(
                {
                    "buyer_id": buyer["buyer_id"],
                    "name": buyer["name"],
                    "name_ar": buyer["name_ar"],
                    "type": buyer["type"],
                    "type_ar": buyer["type_ar"],
                    "location": buyer["location"],
                    "location_ar": buyer["location_ar"],
                    "volume_range": buyer["volume_range"],
                    "payment_terms": buyer["payment"],
                    "payment_terms_ar": buyer["payment_ar"],
                    "rating": buyer["rating"],
                    "match_score": round(score, 2),
                }
            )

        # Sort by match score
        matched.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "commodity": commodity,
            "quantity_tons": quantity_tons,
            "location_filter": location,
            "buyer_type_filter": buyer_type,
            "total_matches": len(matched),
            "buyers": matched[:10],  # Top 10
            "recommendation": f"Found {len(matched)} potential buyers. Top match: {matched[0]['name']}"
            if matched
            else "No matching buyers found",
            "recommendation_ar": f"تم العثور على {len(matched)} مشترين محتملين. أفضل مطابقة: {matched[0]['name_ar']}"
            if matched
            else "لم يتم العثور على مشترين مطابقين",
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def _analyze_market_demand(
        self,
        commodity: str,
        region: str | None = None,
        timeframe: str = "current",
    ) -> dict[str, Any]:
        """Analyze market demand."""
        logger.info("analyzing_demand", commodity=commodity, timeframe=timeframe)

        # Simulated demand data
        demand_levels = {
            "wheat": {"level": "high", "growth": 5},
            "dates": {"level": "high", "growth": 8},
            "tomatoes": {"level": "medium", "growth": 2},
            "barley": {"level": "medium", "growth": 3},
        }

        data = demand_levels.get(commodity.lower(), {"level": "medium", "growth": 0})

        demand_level = data["level"]
        demand_ar = {"high": "مرتفع", "medium": "متوسط", "low": "منخفض"}.get(demand_level, "متوسط")

        return {
            "commodity": commodity,
            "region": region or "Kingdom-wide",
            "region_ar": region or "على مستوى المملكة",
            "timeframe": timeframe,
            "demand": {
                "level": demand_level,
                "level_ar": demand_ar,
                "growth_percent": data["growth"],
                "trend": "increasing"
                if data["growth"] > 0
                else "decreasing"
                if data["growth"] < 0
                else "stable",
                "trend_ar": "متزايد"
                if data["growth"] > 0
                else "متناقص"
                if data["growth"] < 0
                else "مستقر",
            },
            "supply": {
                "level": "adequate",
                "level_ar": "كافٍ",
                "local_production_percent": 35,
                "import_percent": 65,
            },
            "key_factors": [
                "Population growth",
                "Ramadan consumption spike",
                "Export demand from GCC",
            ],
            "key_factors_ar": [
                "النمو السكاني",
                "ارتفاع استهلاك رمضان",
                "طلب التصدير من دول الخليج",
            ],
            "outlook": "positive" if data["growth"] > 2 else "neutral",
            "outlook_ar": "إيجابي" if data["growth"] > 2 else "محايد",
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def _calculate_profit_margin(
        self,
        commodity: str,
        quantity_tons: float,
        production_cost_per_kg: float,
        selling_price_per_kg: float | None = None,
        transportation_cost: float | None = None,
        storage_days: int = 0,
    ) -> dict[str, Any]:
        """Calculate profit margin."""
        logger.info("calculating_profit", commodity=commodity, quantity=quantity_tons)

        # Get market price if not provided
        if not selling_price_per_kg:
            prices = await self._get_market_prices(commodity)
            selling_price_per_kg = prices.get("average_price", 2.0)

        quantity_kg = quantity_tons * 1000
        transportation_cost = transportation_cost or (quantity_kg * 0.05)  # Default 0.05 SAR/kg
        storage_cost = storage_days * 0.005 * quantity_kg  # 0.005 SAR/kg/day

        total_production_cost = production_cost_per_kg * quantity_kg
        total_costs = total_production_cost + transportation_cost + storage_cost
        total_revenue = selling_price_per_kg * quantity_kg
        gross_profit = total_revenue - total_costs
        profit_margin_percent = (gross_profit / total_revenue) * 100 if total_revenue > 0 else 0

        return {
            "commodity": commodity,
            "quantity_tons": quantity_tons,
            "quantity_kg": quantity_kg,
            "costs": {
                "production_per_kg": production_cost_per_kg,
                "total_production": round(total_production_cost, 2),
                "transportation": round(transportation_cost, 2),
                "storage": round(storage_cost, 2),
                "total": round(total_costs, 2),
            },
            "revenue": {
                "price_per_kg": selling_price_per_kg,
                "total": round(total_revenue, 2),
            },
            "profit": {
                "gross": round(gross_profit, 2),
                "margin_percent": round(profit_margin_percent, 1),
                "per_kg": round(gross_profit / quantity_kg, 2) if quantity_kg > 0 else 0,
            },
            "assessment": "profitable"
            if profit_margin_percent > 15
            else "marginal"
            if profit_margin_percent > 5
            else "low_margin",
            "assessment_ar": "مربح"
            if profit_margin_percent > 15
            else "هامشي"
            if profit_margin_percent > 5
            else "هامش منخفض",
            "currency": "SAR",
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def _compare_markets(
        self,
        commodity: str,
        markets: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compare prices across markets."""
        logger.info("comparing_markets", commodity=commodity)

        prices = await self._get_market_prices(commodity)

        market_comparison = []
        for price_info in prices.get("prices", []):
            market_comparison.append(
                {
                    "market": price_info["market"],
                    "market_ar": price_info["market_ar"],
                    "price_per_kg": price_info["price_per_kg"],
                    "trend": price_info["trend"],
                    "trend_ar": price_info["trend_ar"],
                    "change_percent": price_info["change_percent"],
                }
            )

        # Sort by price
        market_comparison.sort(key=lambda x: x["price_per_kg"], reverse=True)

        # Calculate price spread
        if market_comparison:
            highest = market_comparison[0]["price_per_kg"]
            lowest = market_comparison[-1]["price_per_kg"]
            spread = ((highest - lowest) / lowest) * 100 if lowest > 0 else 0
        else:
            spread = 0

        return {
            "commodity": commodity,
            "comparison": market_comparison,
            "best_market": market_comparison[0] if market_comparison else None,
            "worst_market": market_comparison[-1] if market_comparison else None,
            "price_spread_percent": round(spread, 1),
            "recommendation": f"Best price at {market_comparison[0]['market']} ({market_comparison[0]['price_per_kg']} SAR/kg)"
            if market_comparison
            else "No market data available",
            "recommendation_ar": f"أفضل سعر في {market_comparison[0]['market_ar']} ({market_comparison[0]['price_per_kg']} ريال/كجم)"
            if market_comparison
            else "لا تتوفر بيانات السوق",
            "generated_at": datetime.now(UTC).isoformat(),
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_market_agent(
    tenant_id: str = "sahool",
    parent_agent: BaseAutonomousAgent | None = None,
) -> MarketSubAgent:
    """
    Factory function to create a MarketSubAgent.
    دالة لإنشاء وكيل السوق الفرعي
    """
    return MarketSubAgent(
        tenant_id=tenant_id,
        parent_agent=parent_agent,
    )
