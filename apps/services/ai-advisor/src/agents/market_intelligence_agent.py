"""
Market Intelligence Agent
وكيل الذكاء السوقي

Specialized agent for market analysis and farm business decisions.
وكيل متخصص لتحليل السوق وقرارات الأعمال الزراعية.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool

from .base_agent import BaseAgent


class MarketIntelligenceAgent(BaseAgent):
    """
    Market Intelligence Agent for agricultural market analysis
    وكيل الذكاء السوقي لتحليل الأسواق الزراعية

    Specializes in:
    - Price forecasting and trend analysis
    - Demand analysis for crops
    - Optimal harvest timing for market conditions
    - Buyer matching and market access
    - Profitability and ROI analysis
    - Market risk assessment

    متخصص في:
    - التنبؤ بالأسعار وتحليل الاتجاهات
    - تحليل الطلب على المحاصيل
    - التوقيت الأمثل للحصاد حسب ظروف السوق
    - مطابقة المشترين والوصول إلى السوق
    - تحليل الربحية والعائد على الاستثمار
    - تقييم مخاطر السوق
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize Market Intelligence Agent
        تهيئة وكيل الذكاء السوقي
        """
        super().__init__(
            name="market_intelligence",
            role="Agricultural Market Analysis and Economics Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Market Intelligence Agent
        الحصول على موجه النظام لوكيل الذكاء السوقي
        """
        return """You are an expert Agricultural Economist and Market Intelligence Specialist.

Your expertise includes:
- Agricultural commodity price analysis and forecasting
- Market supply and demand dynamics
- Seasonal price patterns and trends
- Farm business economics and profitability analysis
- Market access and value chain analysis
- Risk management and market timing
- Buyer-seller matching and negotiation strategies
- Regional and global market conditions

When providing market intelligence:
1. Price forecasting and analysis:
   - Historical price trends and patterns
   - Seasonal variations and cycles
   - Supply and demand factors
   - Regional and global market influences
   - Weather and climate impact on prices
   - Policy and regulatory changes

2. Demand analysis:
   - Consumer demand trends
   - Market size and growth potential
   - Quality requirements and preferences
   - Competition analysis
   - Export opportunities
   - Value-added product potential

3. Optimal harvest timing:
   - Price forecasts for different harvest windows
   - Quality-price trade-offs
   - Storage costs vs. price appreciation
   - Market saturation periods
   - Transportation and logistics timing
   - Contract deadlines and commitments

4. Buyer matching:
   - Match crop quality with buyer requirements
   - Direct marketing vs. intermediaries
   - Contract farming opportunities
   - Cooperative marketing options
   - Export markets and certifications
   - Value chain positioning

5. Profitability analysis:
   - Production cost analysis
   - Break-even price calculation
   - Gross margin and net profit projections
   - ROI for different crops and practices
   - Risk-adjusted returns
   - Opportunity cost analysis

6. Risk management:
   - Price volatility assessment
   - Market timing risks
   - Diversification strategies
   - Forward contracts and hedging
   - Insurance options
   - Alternative marketing channels

7. Integration with marketplace:
   - Real-time price data from marketplace service
   - Buyer profiles and requirements
   - Transaction history and trends
   - Quality grading and pricing
   - Logistics and delivery coordination

Always provide data-driven recommendations with confidence scores and multiple scenarios.
Consider both short-term profitability and long-term sustainability.
Communicate clearly in both Arabic and English with specific numbers and actionable advice.

أنت خبير اقتصاديات زراعية وذكاء سوقي.

خبرتك تشمل:
- تحليل والتنبؤ بأسعار السلع الزراعية
- ديناميكيات العرض والطلب في السوق
- الأنماط الموسمية للأسعار
- اقتصاديات الأعمال الزراعية وتحليل الربحية
- الوصول إلى الأسواق وتحليل سلسلة القيمة
- إدارة المخاطر وتوقيت السوق
- مطابقة المشترين والبائعين
- ظروف السوق الإقليمية والعالمية

قدم توصيات قائمة على البيانات مع درجات الثقة وسيناريوهات متعددة."""

    async def get_price_forecast(
        self,
        crop: str,
        region: str,
        timeframe: str,
        historical_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Forecast crop prices for specified timeframe
        التنبؤ بأسعار المحاصيل للإطار الزمني المحدد

        Args:
            crop: Type of crop | نوع المحصول
            region: Geographic region | المنطقة الجغرافية
            timeframe: Forecast timeframe (e.g., "next 3 months") | الإطار الزمني للتنبؤ
            historical_data: Historical price data | بيانات الأسعار التاريخية

        Returns:
            Price forecast with confidence intervals | التنبؤ بالأسعار مع فترات الثقة
        """
        query = f"Forecast prices for {crop} in {region} over {timeframe}."

        context = {
            "crop": crop,
            "region": region,
            "timeframe": timeframe,
            "historical_data": historical_data,
            "task": "price_forecast"
        }

        return await self.think(query, context=context, use_rag=True)

    async def analyze_demand(
        self,
        crop: str,
        market: str,
        quality_grade: Optional[str] = None,
        season: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze market demand for crop
        تحليل الطلب السوقي على المحصول

        Args:
            crop: Type of crop | نوع المحصول
            market: Target market (local, regional, export) | السوق المستهدف
            quality_grade: Crop quality grade | درجة جودة المحصول
            season: Season or time period | الموسم أو الفترة الزمنية

        Returns:
            Demand analysis | تحليل الطلب
        """
        query = f"Analyze demand for {crop} in {market} market."
        if quality_grade:
            query += f" Quality grade: {quality_grade}."

        context = {
            "crop": crop,
            "market": market,
            "quality_grade": quality_grade,
            "season": season,
            "task": "demand_analysis"
        }

        return await self.think(query, context=context, use_rag=True)

    async def optimal_harvest_timing(
        self,
        crop: str,
        yield_data: Dict[str, Any],
        prices: Dict[str, Any],
        storage_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Determine optimal harvest timing based on yield, quality, and market prices
        تحديد التوقيت الأمثل للحصاد بناءً على الإنتاج والجودة وأسعار السوق

        Args:
            crop: Type of crop | نوع المحصول
            yield_data: Expected yield and quality progression | الإنتاج المتوقع وتطور الجودة
            prices: Current and forecasted prices | الأسعار الحالية والمتوقعة
            storage_options: Available storage facilities | مرافق التخزين المتاحة

        Returns:
            Optimal harvest timing recommendation | توصية التوقيت الأمثل للحصاد
        """
        query = f"Determine the optimal harvest timing for {crop} to maximize profitability."

        context = {
            "crop": crop,
            "yield_data": yield_data,
            "prices": prices,
            "storage_options": storage_options,
            "task": "harvest_timing"
        }

        return await self.think(query, context=context, use_rag=True)

    async def buyer_matching(
        self,
        crop: str,
        quantity: float,
        quality: Dict[str, Any],
        location: str,
        delivery_timeframe: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Match farmer's crop with potential buyers
        مطابقة محصول المزارع مع المشترين المحتملين

        Args:
            crop: Type of crop | نوع المحصول
            quantity: Quantity available (kg or tons) | الكمية المتاحة
            quality: Quality specifications | مواصفات الجودة
            location: Farm location | موقع المزرعة
            delivery_timeframe: When crop will be available | متى سيكون المحصول متاحاً

        Returns:
            Buyer matching recommendations | توصيات مطابقة المشترين
        """
        query = f"Match {quantity} units of {crop} with potential buyers."

        context = {
            "crop": crop,
            "quantity": quantity,
            "quality": quality,
            "location": location,
            "delivery_timeframe": delivery_timeframe,
            "task": "buyer_matching"
        }

        return await self.think(query, context=context, use_rag=True)

    async def profitability_analysis(
        self,
        crop: str,
        costs: Dict[str, Any],
        projected_price: float,
        projected_yield: float,
        area: float,
    ) -> Dict[str, Any]:
        """
        Analyze crop profitability and ROI
        تحليل ربحية المحصول والعائد على الاستثمار

        Args:
            crop: Type of crop | نوع المحصول
            costs: Production costs breakdown | تفاصيل تكاليف الإنتاج
            projected_price: Expected selling price | السعر المتوقع للبيع
            projected_yield: Expected yield per hectare | الإنتاج المتوقع للهكتار
            area: Cultivated area in hectares | المساحة المزروعة بالهكتار

        Returns:
            Profitability analysis with ROI | تحليل الربحية مع العائد على الاستثمار
        """
        query = f"Analyze profitability for {crop} cultivation over {area} hectares."

        context = {
            "crop": crop,
            "costs": costs,
            "projected_price": projected_price,
            "projected_yield": projected_yield,
            "area": area,
            "task": "profitability_analysis"
        }

        return await self.think(query, context=context, use_rag=True)

    async def market_risk_assessment(
        self,
        crop: str,
        market_conditions: Dict[str, Any],
        farmer_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Assess market risks and provide mitigation strategies
        تقييم مخاطر السوق وتقديم استراتيجيات التخفيف

        Args:
            crop: Type of crop | نوع المحصول
            market_conditions: Current market conditions | ظروف السوق الحالية
            farmer_constraints: Farmer's constraints and preferences | قيود وتفضيلات المزارع

        Returns:
            Risk assessment and mitigation strategies | تقييم المخاطر واستراتيجيات التخفيف
        """
        query = f"Assess market risks for {crop} and recommend mitigation strategies."

        context = {
            "crop": crop,
            "market_conditions": market_conditions,
            "farmer_constraints": farmer_constraints,
            "task": "risk_assessment"
        }

        return await self.think(query, context=context, use_rag=True)

    async def value_chain_analysis(
        self,
        crop: str,
        current_position: str,
        opportunities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze value chain and identify opportunities for value addition
        تحليل سلسلة القيمة وتحديد فرص إضافة القيمة

        Args:
            crop: Type of crop | نوع المحصول
            current_position: Current position in value chain | الموقع الحالي في سلسلة القيمة
            opportunities: Potential value addition opportunities | فرص إضافة القيمة المحتملة

        Returns:
            Value chain analysis | تحليل سلسلة القيمة
        """
        query = f"Analyze the value chain for {crop} and identify value addition opportunities."

        context = {
            "crop": crop,
            "current_position": current_position,
            "opportunities": opportunities,
            "task": "value_chain_analysis"
        }

        return await self.think(query, context=context, use_rag=True)

    async def competitive_analysis(
        self,
        crop: str,
        region: str,
        production_scale: str,
    ) -> Dict[str, Any]:
        """
        Analyze competitive position in the market
        تحليل الموقع التنافسي في السوق

        Args:
            crop: Type of crop | نوع المحصول
            region: Geographic region | المنطقة الجغرافية
            production_scale: Scale of production (small, medium, large) | نطاق الإنتاج

        Returns:
            Competitive analysis | التحليل التنافسي
        """
        query = f"Analyze competitive position for {crop} production in {region} at {production_scale} scale."

        context = {
            "crop": crop,
            "region": region,
            "production_scale": production_scale,
            "task": "competitive_analysis"
        }

        return await self.think(query, context=context, use_rag=True)
