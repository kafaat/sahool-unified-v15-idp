"""
Yield Predictor Agent
وكيل التنبؤ بالمحصول

Specialized agent for yield prediction and production forecasting.
وكيل متخصص للتنبؤ بالمحصول وتوقع الإنتاج.
"""

from typing import Any

from langchain_core.tools import Tool

from .base_agent import BaseAgent


class YieldPredictorAgent(BaseAgent):
    """
    Yield Predictor Agent for crop production forecasting
    وكيل التنبؤ بالمحصول لتوقع الإنتاج الزراعي

    Specializes in:
    - Yield estimation and forecasting
    - Production quality assessment
    - Harvest timing recommendations
    - Market readiness analysis
    - Risk factor identification

    متخصص في:
    - تقدير وتوقع المحصول
    - تقييم جودة الإنتاج
    - توصيات توقيت الحصاد
    - تحليل جاهزية السوق
    - تحديد عوامل الخطر
    """

    def __init__(
        self,
        tools: list[Tool] | None = None,
        retriever: Any | None = None,
    ):
        """
        Initialize Yield Predictor Agent
        تهيئة وكيل التنبؤ بالمحصول
        """
        super().__init__(
            name="yield_predictor",
            role="Crop Yield Prediction and Production Forecasting Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Yield Predictor
        الحصول على موجه النظام للتنبؤ بالمحصول
        """
        return """You are an expert Agricultural Scientist specializing in crop yield prediction and production forecasting.

Your expertise includes:
- Yield estimation models and methodologies
- Growth stage assessment and phenology
- Environmental factor impact on yield
- Historical yield data analysis
- Harvest timing optimization
- Quality prediction and grading
- Market value assessment

When predicting yields:
1. Analyze multiple factors:
   - Crop type and variety characteristics
   - Current growth stage and development
   - Weather conditions (past and forecast)
   - Soil health and nutrient status
   - Water availability and irrigation
   - Pest and disease pressure
   - Management practices

2. Use historical context:
   - Compare with previous seasons
   - Identify trends and patterns
   - Account for climate variations
   - Consider technological improvements

3. Provide comprehensive predictions:
   - Expected yield (quantity per area)
   - Confidence intervals and uncertainty
   - Quality expectations
   - Optimal harvest window
   - Risk factors and mitigation

4. Consider economic factors:
   - Market timing
   - Storage requirements
   - Transportation logistics
   - Price trends

5. Identify improvement opportunities:
   - Management practices to boost yield
   - Quality enhancement strategies
   - Risk reduction measures

Always provide:
- Quantitative estimates with units
- Confidence levels and ranges
- Key assumptions and limitations
- Actionable recommendations

Communicate clearly in both Arabic and English.

أنت خبير علوم زراعية متخصص في التنبؤ بالمحصول وتوقع الإنتاج.

خبرتك تشمل:
- نماذج تقدير المحصول
- تقييم مراحل النمو
- تأثير العوامل البيئية على المحصول
- تحليل البيانات التاريخية
- تحسين توقيت الحصاد
- التنبؤ بالجودة
- تقييم القيمة السوقية

قدم تنبؤات شاملة مع تقديرات كمية ومستويات ثقة."""

    async def predict_yield(
        self,
        crop_type: str,
        area: float,
        growth_stage: str,
        field_data: dict[str, Any],
        weather_data: dict[str, Any],
        historical_yields: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Predict crop yield
        التنبؤ بالمحصول

        Args:
            crop_type: Type of crop | نوع المحصول
            area: Field area in hectares | مساحة الحقل بالهكتار
            growth_stage: Current growth stage | مرحلة النمو الحالية
            field_data: Field health and status data | بيانات صحة الحقل
            weather_data: Historical and forecast weather | الطقس التاريخي والمتوقع
            historical_yields: Past yield data | بيانات المحاصيل السابقة

        Returns:
            Yield prediction | التنبؤ بالمحصول
        """
        query = f"Predict yield for {area} hectares of {crop_type} at {growth_stage} stage."

        context = {
            "crop_type": crop_type,
            "area": area,
            "growth_stage": growth_stage,
            "field_data": field_data,
            "weather_data": weather_data,
            "historical_yields": historical_yields,
            "task": "yield_prediction",
        }

        return await self.think(query, context=context, use_rag=True)

    async def assess_quality(
        self,
        crop_type: str,
        growth_conditions: dict[str, Any],
        stress_events: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Assess expected crop quality
        تقييم الجودة المتوقعة للمحصول

        Args:
            crop_type: Type of crop | نوع المحصول
            growth_conditions: Conditions during growth | ظروف النمو
            stress_events: Any stress events occurred | أحداث الإجهاد

        Returns:
            Quality assessment | تقييم الجودة
        """
        query = f"Assess expected quality for {crop_type} based on growth conditions."

        context = {
            "crop_type": crop_type,
            "growth_conditions": growth_conditions,
            "stress_events": stress_events,
            "task": "quality_assessment",
        }

        return await self.think(query, context=context, use_rag=True)

    async def recommend_harvest_time(
        self,
        crop_type: str,
        current_stage: str,
        maturity_indicators: dict[str, Any],
        weather_forecast: dict[str, Any],
        market_conditions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Recommend optimal harvest timing
        التوصية بالتوقيت الأمثل للحصاد

        Args:
            crop_type: Type of crop | نوع المحصول
            current_stage: Current development stage | مرحلة النمو الحالية
            maturity_indicators: Maturity signs and measurements | مؤشرات النضج
            weather_forecast: Upcoming weather forecast | توقعات الطقس القادمة
            market_conditions: Current market situation | ظروف السوق الحالية

        Returns:
            Harvest timing recommendations | توصيات توقيت الحصاد
        """
        query = f"Recommend optimal harvest timing for {crop_type}."

        context = {
            "crop_type": crop_type,
            "current_stage": current_stage,
            "maturity_indicators": maturity_indicators,
            "weather_forecast": weather_forecast,
            "market_conditions": market_conditions,
            "task": "harvest_timing",
        }

        return await self.think(query, context=context, use_rag=True)

    async def analyze_yield_gap(
        self,
        crop_type: str,
        actual_yield: float | None,
        potential_yield: float,
        management_practices: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze yield gap and improvement opportunities
        تحليل فجوة المحصول وفرص التحسين

        Args:
            crop_type: Type of crop | نوع المحصول
            actual_yield: Actual or predicted yield | المحصول الفعلي أو المتوقع
            potential_yield: Theoretical maximum yield | المحصول الأقصى النظري
            management_practices: Current practices | الممارسات الحالية

        Returns:
            Yield gap analysis | تحليل فجوة المحصول
        """
        query = f"Analyze yield gap for {crop_type} and identify improvement opportunities."

        context = {
            "crop_type": crop_type,
            "actual_yield": actual_yield,
            "potential_yield": potential_yield,
            "management_practices": management_practices,
            "task": "yield_gap_analysis",
        }

        return await self.think(query, context=context, use_rag=True)

    async def risk_assessment(
        self,
        crop_type: str,
        current_conditions: dict[str, Any],
        threats: list[dict[str, Any]],
        remaining_growth_period: int,
    ) -> dict[str, Any]:
        """
        Assess risks to final yield
        تقييم المخاطر على المحصول النهائي

        Args:
            crop_type: Type of crop | نوع المحصول
            current_conditions: Current field conditions | الظروف الحالية
            threats: Identified threats | التهديدات المحددة
            remaining_growth_period: Days until harvest | الأيام المتبقية للحصاد

        Returns:
            Risk assessment | تقييم المخاطر
        """
        query = (
            f"Assess yield risks for {crop_type} with {remaining_growth_period} days until harvest."
        )

        context = {
            "crop_type": crop_type,
            "current_conditions": current_conditions,
            "threats": threats,
            "remaining_growth_period": remaining_growth_period,
            "task": "risk_assessment",
        }

        return await self.think(query, context=context, use_rag=True)

    async def forecast_production(
        self,
        farm_data: list[dict[str, Any]],
        season: str,
        regional_factors: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Forecast total farm production
        توقع الإنتاج الإجمالي للمزرعة

        Args:
            farm_data: Data for all fields/crops | بيانات جميع الحقول/المحاصيل
            season: Growing season | الموسم الزراعي
            regional_factors: Regional climate/market factors | عوامل إقليمية

        Returns:
            Production forecast | توقع الإنتاج
        """
        query = f"Forecast total farm production for {season} season."

        context = {
            "farm_data": farm_data,
            "season": season,
            "regional_factors": regional_factors,
            "task": "production_forecast",
        }

        return await self.think(query, context=context, use_rag=True)
