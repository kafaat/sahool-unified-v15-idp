"""
Ecological Expert Agent
وكيل خبير الزراعة الإيكولوجية

Specialized agent for ecological agriculture recommendations and transition planning.
وكيل متخصص لتوصيات الزراعة الإيكولوجية وتخطيط التحول.

Based on the 2025 ecological agriculture article series.
مبني على سلسلة مقالات الزراعة الإيكولوجية 2025.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool

from .base_agent import BaseAgent


class EcologicalExpertAgent(BaseAgent):
    """
    Ecological Expert Agent for sustainable agriculture
    وكيل خبير الزراعة الإيكولوجية للزراعة المستدامة

    Specializes in:
    - Ecological farming practices
    - Transition planning from conventional to ecological
    - Biodiversity enhancement
    - Soil health improvement
    - Water conservation strategies
    - Natural pest management
    - GlobalGAP compliance support
    - Pitfall identification and avoidance

    متخصص في:
    - ممارسات الزراعة الإيكولوجية
    - تخطيط التحول من التقليدي إلى الإيكولوجي
    - تعزيز التنوع البيولوجي
    - تحسين صحة التربة
    - استراتيجيات الحفاظ على المياه
    - المكافحة الطبيعية للآفات
    - دعم الامتثال لـ GlobalGAP
    - تحديد المزالق وتجنبها
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize Ecological Expert Agent
        تهيئة وكيل خبير الزراعة الإيكولوجية
        """
        super().__init__(
            name="ecological_expert",
            role="Ecological Agriculture and Sustainability Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Ecological Expert
        الحصول على موجه النظام لخبير الزراعة الإيكولوجية
        """
        return """You are an expert in Ecological Agriculture and Sustainable Farming Systems.

Your expertise includes:
- Understanding ecological principles and their application in farming
- Designing regenerative agriculture systems
- Soil health restoration and management
- Biodiversity conservation on farms
- Water conservation and efficient irrigation
- Natural pest and disease management
- Climate adaptation strategies
- Transition planning from conventional to ecological farming
- GlobalGAP IFA v6 compliance for sustainability

When advising farmers:
1. Assess Current Situation:
   - Current farming practices and their impacts
   - Available resources and constraints
   - Market and certification goals
   - Local climate and environmental conditions

2. Identify Ecological Opportunities:
   - Soil improvement potential
   - Biodiversity enhancement possibilities
   - Water use optimization
   - Natural pest control options
   - Waste recycling and closed-loop systems

3. Provide Practical Recommendations:
   - Start with low-cost, high-impact practices
   - Prioritize soil health as foundation
   - Suggest companion planting combinations
   - Recommend cover crop rotations
   - Design gradual transition pathways

4. Address Common Pitfalls:
   - Warn against over-tillage and soil compaction
   - Prevent over-irrigation and nutrient imbalance
   - Avoid pesticide overuse
   - Guide away from monoculture risks
   - Emphasize record-keeping importance

5. Support Certification Goals:
   - Map practices to GlobalGAP control points
   - Document sustainability improvements
   - Build audit-ready evidence
   - Track environmental indicators

Always provide bilingual responses (Arabic and English) and consider:
- Yemen's specific climatic and soil conditions
- Local resource availability
- Economic feasibility for small-scale farmers
- Cultural farming traditions and preferences

أنت خبير في الزراعة الإيكولوجية وأنظمة الزراعة المستدامة.

خبرتك تشمل:
- فهم المبادئ الإيكولوجية وتطبيقها في الزراعة
- تصميم أنظمة الزراعة التجديدية
- استعادة صحة التربة وإدارتها
- الحفاظ على التنوع البيولوجي في المزارع
- الحفاظ على المياه والري الفعال
- المكافحة الطبيعية للآفات والأمراض
- استراتيجيات التكيف مع المناخ
- تخطيط التحول من الزراعة التقليدية إلى الإيكولوجية
- الامتثال لـ GlobalGAP IFA v6 للاستدامة

قدم نصائح عملية ثنائية اللغة مع مراعاة الظروف المحلية في اليمن."""

    async def assess_farm_ecology(
        self,
        farm_data: Dict[str, Any],
        current_practices: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assess current farm ecology and sustainability level
        تقييم البيئة الحالية للمزرعة ومستوى الاستدامة

        Args:
            farm_data: Farm location, size, crops | بيانات المزرعة
            current_practices: Current farming practices | الممارسات الحالية

        Returns:
            Ecological assessment | التقييم الإيكولوجي
        """
        query = """Assess the current ecological status of this farm and provide:
        1. Sustainability score (0-100)
        2. Key ecological strengths
        3. Areas needing improvement
        4. Biodiversity assessment
        5. Soil health indicators"""

        context = {
            "farm_data": farm_data,
            "current_practices": current_practices,
            "task": "ecological_assessment"
        }

        return await self.think(query, context=context, use_rag=True)

    async def plan_transition(
        self,
        current_practices: Dict[str, Any],
        target_practices: List[str],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Plan transition from conventional to ecological farming
        تخطيط التحول من الزراعة التقليدية إلى الإيكولوجية

        Args:
            current_practices: Current farming methods | الممارسات الحالية
            target_practices: Target ecological practices | الممارسات المستهدفة
            constraints: Budget, time, labor constraints | القيود

        Returns:
            Transition plan | خطة التحول
        """
        query = f"""Create a practical transition plan from conventional to ecological farming.
        Target practices: {', '.join(target_practices)}

        Include:
        1. Phased implementation timeline
        2. Quick wins to start immediately
        3. Required resources and investments
        4. Expected benefits at each phase
        5. Risk mitigation strategies
        6. GlobalGAP compliance alignment"""

        context = {
            "current_practices": current_practices,
            "target_practices": target_practices,
            "constraints": constraints,
            "task": "transition_planning"
        }

        return await self.think(query, context=context, use_rag=True)

    async def recommend_practices(
        self,
        crop_type: str,
        soil_type: str,
        climate: str,
        goals: List[str],
    ) -> Dict[str, Any]:
        """
        Recommend ecological practices for specific conditions
        التوصية بالممارسات الإيكولوجية لظروف محددة

        Args:
            crop_type: Type of crop | نوع المحصول
            soil_type: Soil characteristics | خصائص التربة
            climate: Climate conditions | الظروف المناخية
            goals: Farmer's goals (yield, quality, certification) | أهداف المزارع

        Returns:
            Practice recommendations | توصيات الممارسات
        """
        query = f"""Recommend ecological practices for:
        - Crop: {crop_type}
        - Soil: {soil_type}
        - Climate: {climate}
        - Goals: {', '.join(goals)}

        Provide:
        1. Priority practices with highest impact
        2. Companion planting suggestions
        3. Cover crop recommendations
        4. Natural pest control methods
        5. Water conservation techniques
        6. Expected outcomes and timeline"""

        context = {
            "crop_type": crop_type,
            "soil_type": soil_type,
            "climate": climate,
            "goals": goals,
            "task": "practice_recommendation"
        }

        return await self.think(query, context=context, use_rag=True)

    async def diagnose_pitfalls(
        self,
        observed_issues: List[str],
        current_practices: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Diagnose common agricultural pitfalls
        تشخيص المزالق الزراعية الشائعة

        Args:
            observed_issues: Observed problems | المشاكل الملاحظة
            current_practices: Current farming practices | الممارسات الحالية

        Returns:
            Pitfall diagnosis and solutions | تشخيص المزالق والحلول
        """
        query = f"""Diagnose potential agricultural pitfalls based on:
        - Observed issues: {', '.join(observed_issues)}

        Provide:
        1. Identified pitfalls with severity level
        2. Root cause analysis
        3. Immediate corrective actions
        4. Long-term prevention strategies
        5. Expected recovery timeline
        6. Cost of inaction vs intervention"""

        context = {
            "observed_issues": observed_issues,
            "current_practices": current_practices,
            "task": "pitfall_diagnosis"
        }

        return await self.think(query, context=context, use_rag=True)

    async def companion_planting_design(
        self,
        main_crop: str,
        field_size: float,
        existing_plants: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Design companion planting layout
        تصميم تخطيط الزراعة التصاحبية

        Args:
            main_crop: Primary crop to grow | المحصول الرئيسي
            field_size: Field size in dunums | حجم الحقل بالدونم
            existing_plants: Already planted species | النباتات الموجودة

        Returns:
            Companion planting design | تصميم الزراعة التصاحبية
        """
        query = f"""Design a companion planting layout for {main_crop} in {field_size} dunums.
        {'Existing plants: ' + ', '.join(existing_plants) if existing_plants else ''}

        Include:
        1. Recommended companion plants
        2. Planting layout and spacing
        3. Timing for each species
        4. Expected pest deterrence benefits
        5. Pollinator attraction potential
        6. Harvest scheduling"""

        context = {
            "main_crop": main_crop,
            "field_size": field_size,
            "existing_plants": existing_plants,
            "task": "companion_planting"
        }

        return await self.think(query, context=context, use_rag=True)

    async def soil_restoration_plan(
        self,
        soil_analysis: Dict[str, Any],
        target_improvements: List[str],
    ) -> Dict[str, Any]:
        """
        Create soil restoration plan
        إنشاء خطة استعادة التربة

        Args:
            soil_analysis: Current soil test results | نتائج تحليل التربة
            target_improvements: Desired improvements | التحسينات المطلوبة

        Returns:
            Soil restoration plan | خطة استعادة التربة
        """
        query = f"""Create a soil restoration plan targeting: {', '.join(target_improvements)}

        Provide:
        1. Organic matter building strategies
        2. Cover crop rotation plan
        3. Composting recommendations
        4. Biological inoculants if needed
        5. Timeline for improvement milestones
        6. Monitoring indicators"""

        context = {
            "soil_analysis": soil_analysis,
            "target_improvements": target_improvements,
            "task": "soil_restoration"
        }

        return await self.think(query, context=context, use_rag=True)

    async def water_conservation_strategy(
        self,
        current_irrigation: Dict[str, Any],
        water_availability: str,
        crops: List[str],
    ) -> Dict[str, Any]:
        """
        Develop water conservation strategy
        تطوير استراتيجية الحفاظ على المياه

        Args:
            current_irrigation: Current irrigation system | نظام الري الحالي
            water_availability: Water source and availability | توفر المياه
            crops: Crops being grown | المحاصيل المزروعة

        Returns:
            Water conservation strategy | استراتيجية الحفاظ على المياه
        """
        query = f"""Develop a water conservation strategy for: {', '.join(crops)}
        Water availability: {water_availability}

        Include:
        1. Irrigation optimization recommendations
        2. Mulching and soil cover strategies
        3. Rainwater harvesting if applicable
        4. Drought-resistant variety suggestions
        5. Expected water savings percentage
        6. Cost-benefit analysis"""

        context = {
            "current_irrigation": current_irrigation,
            "water_availability": water_availability,
            "crops": crops,
            "task": "water_conservation"
        }

        return await self.think(query, context=context, use_rag=True)

    async def globalgap_alignment(
        self,
        current_practices: Dict[str, Any],
        target_control_points: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Assess and improve GlobalGAP compliance through ecological practices
        تقييم وتحسين امتثال GlobalGAP من خلال الممارسات الإيكولوجية

        Args:
            current_practices: Current farming practices | الممارسات الحالية
            target_control_points: Specific CPs to address | نقاط التحكم المستهدفة

        Returns:
            GlobalGAP alignment recommendations | توصيات المواءمة مع GlobalGAP
        """
        query = """Assess GlobalGAP IFA v6 compliance and recommend ecological practices that:
        1. Fulfill sustainability control points (CB.1, CB.3, CB.5, CB.7, AF.1, AF.4)
        2. Build audit-ready evidence
        3. Integrate with existing farm operations
        4. Provide production and environmental benefits
        5. Support certification journey"""

        context = {
            "current_practices": current_practices,
            "target_control_points": target_control_points,
            "task": "globalgap_alignment"
        }

        return await self.think(query, context=context, use_rag=True)
