"""
Soil Science Agent
وكيل علوم التربة

Specialized agent for soil health analysis and restoration.
وكيل متخصص لتحليل صحة التربة واستعادتها.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool

from .base_agent import BaseAgent


class SoilScienceAgent(BaseAgent):
    """
    Soil Science Agent for comprehensive soil analysis and improvement
    وكيل علوم التربة للتحليل الشامل للتربة وتحسينها

    Specializes in:
    - Comprehensive soil health assessment
    - Nutrient availability and interactions
    - Soil restoration and improvement plans
    - Soil microbiome enhancement
    - Organic matter building strategies
    - Soil-water-nutrient interactions

    متخصص في:
    - التقييم الشامل لصحة التربة
    - توفر المغذيات والتفاعلات
    - خطط استعادة وتحسين التربة
    - تعزيز الكائنات الحية الدقيقة في التربة
    - استراتيجيات بناء المادة العضوية
    - تفاعلات التربة والماء والمغذيات
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize Soil Science Agent
        تهيئة وكيل علوم التربة
        """
        super().__init__(
            name="soil_science",
            role="Soil Science and Pedology Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Soil Science Agent
        الحصول على موجه النظام لوكيل علوم التربة
        """
        return """You are an expert Soil Scientist and Pedologist specializing in soil health and sustainable agriculture.

Your expertise includes:
- Soil physical, chemical, and biological properties
- Nutrient cycling and availability
- Soil-water relationships and dynamics
- Soil organic matter and carbon sequestration
- Soil microbiome and biological activity
- Soil degradation and restoration
- Sustainable soil management practices
- Precision agriculture and soil mapping

When analyzing soil health:
1. Comprehensive soil assessment:
   - Physical properties (texture, structure, bulk density, porosity)
   - Chemical properties (pH, CEC, nutrient levels, salinity)
   - Biological properties (organic matter, microbial activity, biodiversity)
   - Soil depth and horizons
   - Water holding capacity and drainage
   - Erosion risk and compaction

2. Nutrient availability analysis:
   - Macro-nutrients (N, P, K, Ca, Mg, S)
   - Micro-nutrients (Fe, Mn, Zn, Cu, B, Mo, Cl)
   - Nutrient interactions and antagonisms
   - pH impact on nutrient availability
   - Moisture impact on nutrient uptake
   - Seasonal variations in nutrient availability
   - Nutrient fixation and release mechanisms

3. Soil restoration planning:
   - Identify degradation causes (erosion, compaction, salinization, acidification)
   - Set soil health targets based on crop requirements
   - Develop phased improvement plan
   - Recommend soil amendments (organic and mineral)
   - Suggest cover cropping and green manures
   - Design crop rotation for soil improvement
   - Implement conservation practices

4. Soil microbiome recommendations:
   - Enhance beneficial bacteria and fungi
   - Improve mycorrhizal associations
   - Increase biological nitrogen fixation
   - Promote decomposer organisms
   - Use biological inoculants appropriately
   - Reduce soil disturbance
   - Maintain soil cover and diversity

5. Organic matter building:
   - Calculate organic matter deficit
   - Recommend organic amendments (compost, manure, biochar)
   - Design cover crop systems
   - Implement reduced tillage
   - Crop residue management
   - Assess carbon sequestration potential
   - Monitor organic matter changes over time

6. Soil-water-nutrient interactions:
   - Optimize irrigation for nutrient efficiency
   - Prevent nutrient leaching
   - Manage waterlogging and drainage
   - Address salinity issues
   - Fertigation strategies
   - Timing of fertilizer applications
   - Water quality impact on soil

7. Soil health monitoring:
   - Key indicators to track
   - Sampling protocols and timing
   - Interpretation of soil test results
   - Trend analysis over seasons
   - Early warning signs of degradation
   - Adaptive management based on monitoring

8. Sustainable practices:
   - Conservation agriculture principles
   - Integrated nutrient management
   - Biological soil health enhancement
   - Climate-smart soil management
   - Long-term soil fertility
   - Economic viability of improvements

Always provide evidence-based recommendations with confidence scores.
Consider both immediate improvements and long-term soil health.
Integrate soil management with crop production goals.
Communicate clearly in both Arabic and English with specific, actionable advice.

أنت خبير علوم التربة والبيدولوجيا متخصص في صحة التربة والزراعة المستدامة.

خبرتك تشمل:
- الخصائص الفيزيائية والكيميائية والبيولوجية للتربة
- دورة المغذيات وتوفرها
- العلاقات المائية في التربة
- المادة العضوية وعزل الكربون
- الكائنات الحية الدقيقة في التربة
- تدهور التربة واستعادتها
- ممارسات الإدارة المستدامة للتربة
- الزراعة الدقيقة ورسم خرائط التربة

قدم توصيات قائمة على الأدلة مع درجات الثقة واعتبار التحسينات الفورية والصحة طويلة الأجل للتربة."""

    async def analyze_soil_health(
        self,
        soil_data: Dict[str, Any],
        crop_history: Optional[List[str]] = None,
        management_practices: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive soil health assessment
        إجراء تقييم شامل لصحة التربة

        Args:
            soil_data: Soil test results and properties | نتائج تحليل التربة والخصائص
            crop_history: Previous crops grown | المحاصيل السابقة
            management_practices: Current management practices | الممارسات الإدارية الحالية

        Returns:
            Comprehensive soil health assessment | تقييم شامل لصحة التربة
        """
        query = "Perform a comprehensive soil health assessment based on the provided soil data."

        context = {
            "soil_data": soil_data,
            "crop_history": crop_history,
            "management_practices": management_practices,
            "task": "soil_health_assessment"
        }

        return await self.think(query, context=context, use_rag=True)

    async def nutrient_availability(
        self,
        soil_data: Dict[str, Any],
        moisture: Dict[str, Any],
        crop_requirements: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze nutrient availability considering soil-water-nutrient interactions
        تحليل توفر المغذيات مع مراعاة تفاعلات التربة والماء والمغذيات

        Args:
            soil_data: Soil chemical properties and pH | الخصائص الكيميائية للتربة والرقم الهيدروجيني
            moisture: Soil moisture data | بيانات رطوبة التربة
            crop_requirements: Specific crop nutrient requirements | متطلبات المغذيات للمحصول

        Returns:
            Nutrient availability analysis | تحليل توفر المغذيات
        """
        query = "Analyze nutrient availability considering soil moisture and crop requirements."

        context = {
            "soil_data": soil_data,
            "moisture": moisture,
            "crop_requirements": crop_requirements,
            "task": "nutrient_availability"
        }

        return await self.think(query, context=context, use_rag=True)

    async def restoration_plan(
        self,
        soil_data: Dict[str, Any],
        target_crops: List[str],
        timeframe: str,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Develop comprehensive soil improvement and restoration plan
        تطوير خطة شاملة لتحسين واستعادة التربة

        Args:
            soil_data: Current soil condition | حالة التربة الحالية
            target_crops: Crops to be grown | المحاصيل المراد زراعتها
            timeframe: Timeline for improvement | الجدول الزمني للتحسين
            constraints: Budget, material availability, etc. | الميزانية وتوافر المواد

        Returns:
            Soil restoration plan | خطة استعادة التربة
        """
        query = f"Develop a soil restoration plan for growing {', '.join(target_crops)} within {timeframe}."

        context = {
            "soil_data": soil_data,
            "target_crops": target_crops,
            "timeframe": timeframe,
            "constraints": constraints,
            "task": "restoration_plan"
        }

        return await self.think(query, context=context, use_rag=True)

    async def microbiome_recommendations(
        self,
        soil_data: Dict[str, Any],
        biological_indicators: Optional[Dict[str, Any]] = None,
        climate_zone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Recommend strategies to improve soil biological activity and microbiome
        التوصية باستراتيجيات لتحسين النشاط البيولوجي والكائنات الحية الدقيقة في التربة

        Args:
            soil_data: Soil properties | خصائص التربة
            biological_indicators: Microbial activity measurements | قياسات النشاط الميكروبي
            climate_zone: Climate zone for region-specific recommendations | المنطقة المناخية

        Returns:
            Soil microbiome improvement recommendations | توصيات تحسين الكائنات الحية الدقيقة
        """
        query = "Recommend strategies to enhance soil biological activity and microbiome health."

        context = {
            "soil_data": soil_data,
            "biological_indicators": biological_indicators,
            "climate_zone": climate_zone,
            "task": "microbiome_recommendations"
        }

        return await self.think(query, context=context, use_rag=True)

    async def organic_matter_building(
        self,
        current_om: float,
        target_om: float,
        soil_type: str,
        available_resources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Develop plan to build soil organic matter
        تطوير خطة لبناء المادة العضوية في التربة

        Args:
            current_om: Current organic matter percentage | نسبة المادة العضوية الحالية
            target_om: Target organic matter percentage | نسبة المادة العضوية المستهدفة
            soil_type: Soil texture and type | نسيج ونوع التربة
            available_resources: Available organic materials | المواد العضوية المتاحة

        Returns:
            Organic matter building plan | خطة بناء المادة العضوية
        """
        query = f"Develop a plan to increase soil organic matter from {current_om}% to {target_om}% in {soil_type} soil."

        context = {
            "current_om": current_om,
            "target_om": target_om,
            "soil_type": soil_type,
            "available_resources": available_resources,
            "task": "organic_matter_building"
        }

        return await self.think(query, context=context, use_rag=True)

    async def soil_water_management(
        self,
        soil_data: Dict[str, Any],
        water_regime: str,
        drainage_issues: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Optimize soil-water relationships for better crop production
        تحسين العلاقات المائية في التربة لإنتاج محاصيل أفضل

        Args:
            soil_data: Soil physical properties | الخصائص الفيزيائية للتربة
            water_regime: Rainfall or irrigation pattern | نمط الأمطار أو الري
            drainage_issues: Drainage problems if any | مشاكل الصرف إن وجدت

        Returns:
            Soil-water management recommendations | توصيات إدارة المياه في التربة
        """
        query = "Optimize soil-water management for improved crop production."

        context = {
            "soil_data": soil_data,
            "water_regime": water_regime,
            "drainage_issues": drainage_issues,
            "task": "soil_water_management"
        }

        return await self.think(query, context=context, use_rag=True)

    async def salinity_management(
        self,
        soil_data: Dict[str, Any],
        water_quality: Dict[str, Any],
        crop_tolerance: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Manage soil salinity and sodicity issues
        إدارة مشاكل ملوحة التربة والصودية

        Args:
            soil_data: Soil EC, SAR, and chemical properties | التوصيل الكهربائي ونسبة امتصاص الصوديوم
            water_quality: Irrigation water quality | جودة مياه الري
            crop_tolerance: Salt tolerance of target crop | تحمل الملح للمحصول المستهدف

        Returns:
            Salinity management recommendations | توصيات إدارة الملوحة
        """
        query = "Develop a strategy to manage soil salinity and sodicity."

        context = {
            "soil_data": soil_data,
            "water_quality": water_quality,
            "crop_tolerance": crop_tolerance,
            "task": "salinity_management"
        }

        return await self.think(query, context=context, use_rag=True)

    async def erosion_control(
        self,
        soil_data: Dict[str, Any],
        topography: Dict[str, Any],
        climate: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Recommend soil erosion control measures
        التوصية بتدابير مكافحة تآكل التربة

        Args:
            soil_data: Soil properties | خصائص التربة
            topography: Slope and field characteristics | الميل وخصائص الحقل
            climate: Rainfall intensity and patterns | شدة الأمطار والأنماط

        Returns:
            Erosion control recommendations | توصيات مكافحة التآكل
        """
        query = "Recommend soil erosion control and conservation measures."

        context = {
            "soil_data": soil_data,
            "topography": topography,
            "climate": climate,
            "task": "erosion_control"
        }

        return await self.think(query, context=context, use_rag=True)

    async def carbon_sequestration(
        self,
        soil_data: Dict[str, Any],
        management_options: List[str],
        timeframe: str,
    ) -> Dict[str, Any]:
        """
        Assess carbon sequestration potential and develop implementation plan
        تقييم إمكانات عزل الكربون وتطوير خطة تنفيذ

        Args:
            soil_data: Current soil carbon levels | مستويات الكربون الحالية في التربة
            management_options: Potential management practices | الممارسات الإدارية المحتملة
            timeframe: Timeline for carbon sequestration | الجدول الزمني لعزل الكربون

        Returns:
            Carbon sequestration plan | خطة عزل الكربون
        """
        query = f"Assess carbon sequestration potential over {timeframe} and recommend practices."

        context = {
            "soil_data": soil_data,
            "management_options": management_options,
            "timeframe": timeframe,
            "task": "carbon_sequestration"
        }

        return await self.think(query, context=context, use_rag=True)

    async def fertilizer_recommendations(
        self,
        soil_data: Dict[str, Any],
        crop: str,
        target_yield: float,
        organic_preference: bool = False,
    ) -> Dict[str, Any]:
        """
        Provide integrated fertilizer recommendations based on soil analysis
        تقديم توصيات متكاملة للأسمدة بناءً على تحليل التربة

        Args:
            soil_data: Soil test results | نتائج تحليل التربة
            crop: Target crop | المحصول المستهدف
            target_yield: Desired yield level | مستوى الإنتاج المرغوب
            organic_preference: Prefer organic fertilizers | تفضيل الأسمدة العضوية

        Returns:
            Fertilizer recommendations | توصيات الأسمدة
        """
        query = f"Recommend fertilizers for {crop} to achieve {target_yield} yield based on soil analysis."

        context = {
            "soil_data": soil_data,
            "crop": crop,
            "target_yield": target_yield,
            "organic_preference": organic_preference,
            "task": "fertilizer_recommendations"
        }

        return await self.think(query, context=context, use_rag=True)
