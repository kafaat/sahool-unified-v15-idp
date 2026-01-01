"""
Irrigation Advisor Agent
وكيل مستشار الري

Specialized agent for irrigation recommendations and water management.
وكيل متخصص لتوصيات الري وإدارة المياه.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool

from .base_agent import BaseAgent


class IrrigationAdvisorAgent(BaseAgent):
    """
    Irrigation Advisor Agent for water management
    وكيل مستشار الري لإدارة المياه

    Specializes in:
    - Irrigation scheduling
    - Water requirement calculation
    - Soil moisture analysis
    - Irrigation system optimization
    - Water conservation strategies

    متخصص في:
    - جدولة الري
    - حساب احتياجات المياه
    - تحليل رطوبة التربة
    - تحسين أنظمة الري
    - استراتيجيات توفير المياه
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize Irrigation Advisor Agent
        تهيئة وكيل مستشار الري
        """
        super().__init__(
            name="irrigation_advisor",
            role="Irrigation and Water Management Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Irrigation Advisor
        الحصول على موجه النظام لمستشار الري
        """
        return """You are an expert Irrigation Engineer and Water Management Specialist.

Your expertise includes:
- Calculating crop water requirements (ETc) based on evapotranspiration
- Designing irrigation schedules considering soil type, crop stage, and weather
- Optimizing different irrigation systems (drip, sprinkler, surface, subsurface)
- Analyzing soil moisture data and sensor readings
- Water conservation and efficiency improvement
- Deficit irrigation strategies
- Salinity management

When providing irrigation recommendations:
1. Calculate water requirements:
   - Reference evapotranspiration (ET0)
   - Crop coefficient (Kc) for different growth stages
   - Effective rainfall
   - Irrigation efficiency

2. Consider multiple factors:
   - Soil type and water holding capacity
   - Crop type and growth stage
   - Root depth and distribution
   - Climate and weather forecast
   - Water availability and quality

3. Optimize irrigation timing:
   - Frequency and duration
   - Time of day (early morning preferred)
   - Avoid stress periods
   - Consider phenological stages

4. Promote water efficiency:
   - Minimize deep percolation and runoff
   - Suggest system improvements
   - Recommend monitoring tools
   - Water-saving techniques

5. Address special conditions:
   - Drought management
   - Saline water use
   - Poor drainage
   - Fertigation opportunities

Always provide practical, actionable recommendations with specific quantities and timing.
Communicate in both Arabic and English when appropriate.

أنت خبير هندسة الري وإدارة المياه.

خبرتك تشمل:
- حساب احتياجات المحاصيل من المياه
- تصميم جداول الري
- تحسين أنظمة الري المختلفة
- تحليل رطوبة التربة
- توفير المياه وتحسين الكفاءة
- استراتيجيات الري الناقص
- إدارة الملوحة

قدم توصيات عملية وقابلة للتطبيق مع كميات وأوقات محددة."""

    async def recommend_irrigation(
        self,
        crop_type: str,
        growth_stage: str,
        soil_data: Dict[str, Any],
        weather_data: Dict[str, Any],
        irrigation_system: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Recommend irrigation schedule and amount
        التوصية بجدول الري والكمية

        Args:
            crop_type: Type of crop | نوع المحصول
            growth_stage: Current growth stage | مرحلة النمو الحالية
            soil_data: Soil moisture and properties | رطوبة التربة وخصائصها
            weather_data: Current and forecast weather | الطقس الحالي والمتوقع
            irrigation_system: Type of irrigation system | نوع نظام الري

        Returns:
            Irrigation recommendations | توصيات الري
        """
        query = f"Recommend irrigation for {crop_type} at {growth_stage} stage."

        context = {
            "crop_type": crop_type,
            "growth_stage": growth_stage,
            "soil_data": soil_data,
            "weather_data": weather_data,
            "irrigation_system": irrigation_system,
            "task": "irrigation_recommendation",
        }

        return await self.think(query, context=context, use_rag=True)

    async def calculate_water_requirement(
        self,
        crop_type: str,
        area: float,
        growth_stage: str,
        et0: float,
        rainfall: Optional[float] = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculate crop water requirement
        حساب احتياجات المحصول من المياه

        Args:
            crop_type: Type of crop | نوع المحصول
            area: Field area in hectares | مساحة الحقل بالهكتار
            growth_stage: Current growth stage | مرحلة النمو
            et0: Reference evapotranspiration (mm/day) | التبخر النتح المرجعي
            rainfall: Effective rainfall (mm) | الأمطار الفعالة

        Returns:
            Water requirement calculation | حساب احتياجات المياه
        """
        query = f"Calculate water requirement for {area} hectares of {crop_type}."

        context = {
            "crop_type": crop_type,
            "area": area,
            "growth_stage": growth_stage,
            "et0": et0,
            "rainfall": rainfall,
            "task": "water_calculation",
        }

        return await self.think(query, context=context, use_rag=True)

    async def analyze_soil_moisture(
        self,
        sensor_data: List[Dict[str, Any]],
        soil_type: str,
        crop_type: str,
    ) -> Dict[str, Any]:
        """
        Analyze soil moisture sensor data
        تحليل بيانات مستشعرات رطوبة التربة

        Args:
            sensor_data: Soil moisture readings | قراءات رطوبة التربة
            soil_type: Type of soil | نوع التربة
            crop_type: Type of crop | نوع المحصول

        Returns:
            Soil moisture analysis | تحليل رطوبة التربة
        """
        query = "Analyze soil moisture data and determine irrigation needs."

        context = {
            "sensor_data": sensor_data,
            "soil_type": soil_type,
            "crop_type": crop_type,
            "task": "moisture_analysis",
        }

        return await self.think(query, context=context, use_rag=True)

    async def optimize_system(
        self,
        current_system: Dict[str, Any],
        field_characteristics: Dict[str, Any],
        water_availability: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Optimize irrigation system performance
        تحسين أداء نظام الري

        Args:
            current_system: Current irrigation system details | تفاصيل النظام الحالي
            field_characteristics: Field properties | خصائص الحقل
            water_availability: Water source and quality | مصدر المياه وجودتها

        Returns:
            System optimization recommendations | توصيات تحسين النظام
        """
        query = "Optimize the irrigation system for better efficiency and performance."

        context = {
            "current_system": current_system,
            "field_characteristics": field_characteristics,
            "water_availability": water_availability,
            "task": "system_optimization",
        }

        return await self.think(query, context=context, use_rag=True)

    async def drought_management(
        self,
        crop_type: str,
        growth_stage: str,
        water_deficit: float,
        priority_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Develop drought management strategy
        تطوير استراتيجية إدارة الجفاف

        Args:
            crop_type: Type of crop | نوع المحصول
            growth_stage: Current growth stage | مرحلة النمو
            water_deficit: Water shortage percentage | نسبة نقص المياه
            priority_areas: Areas to prioritize | المناطق ذات الأولوية

        Returns:
            Drought management strategy | استراتيجية إدارة الجفاف
        """
        query = f"Develop drought management strategy for {crop_type} with {water_deficit}% water deficit."

        context = {
            "crop_type": crop_type,
            "growth_stage": growth_stage,
            "water_deficit": water_deficit,
            "priority_areas": priority_areas,
            "task": "drought_management",
        }

        return await self.think(query, context=context, use_rag=True)

    async def fertigation_advice(
        self,
        crop_type: str,
        growth_stage: str,
        soil_analysis: Dict[str, Any],
        irrigation_schedule: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Provide fertigation (fertilizer + irrigation) advice
        تقديم نصائح التسميد مع الري

        Args:
            crop_type: Type of crop | نوع المحصول
            growth_stage: Current growth stage | مرحلة النمو
            soil_analysis: Soil nutrient analysis | تحليل مغذيات التربة
            irrigation_schedule: Current irrigation schedule | جدول الري الحالي

        Returns:
            Fertigation recommendations | توصيات التسميد مع الري
        """
        query = f"Recommend fertigation strategy for {crop_type} at {growth_stage}."

        context = {
            "crop_type": crop_type,
            "growth_stage": growth_stage,
            "soil_analysis": soil_analysis,
            "irrigation_schedule": irrigation_schedule,
            "task": "fertigation_advice",
        }

        return await self.think(query, context=context, use_rag=True)
