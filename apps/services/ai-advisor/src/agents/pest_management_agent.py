"""
Pest Management Agent
وكيل إدارة الآفات

Specialized agent for Integrated Pest Management (IPM).
وكيل متخصص في الإدارة المتكاملة للآفات.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool

from .base_agent import BaseAgent


class PestManagementAgent(BaseAgent):
    """
    Pest Management Agent for Integrated Pest Management (IPM)
    وكيل إدارة الآفات للإدارة المتكاملة للآفات

    Specializes in:
    - Pest identification from symptoms and images
    - IPM strategy development
    - Biological and natural control methods
    - Chemical control as last resort
    - Prevention and monitoring plans
    - Ecological impact assessment

    متخصص في:
    - تحديد الآفات من الأعراض والصور
    - تطوير استراتيجية الإدارة المتكاملة للآفات
    - طرق المكافحة البيولوجية والطبيعية
    - المكافحة الكيميائية كحل أخير
    - خطط الوقاية والمراقبة
    - تقييم الأثر البيئي
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize Pest Management Agent
        تهيئة وكيل إدارة الآفات
        """
        super().__init__(
            name="pest_management",
            role="Integrated Pest Management Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Pest Management Agent
        الحصول على موجه النظام لوكيل إدارة الآفات
        """
        return """You are an expert Entomologist and Integrated Pest Management (IPM) Specialist.

Your expertise includes:
- Identifying pests (insects, mites, rodents, birds) from symptoms and images
- Understanding pest life cycles, behavior, and ecology
- Designing IPM strategies that minimize environmental impact
- Recommending biological controls (predators, parasitoids, pathogens)
- Suggesting cultural and mechanical control methods
- Using chemical controls only when necessary, with safety protocols
- Developing monitoring and prevention programs
- Considering beneficial insects and pollinators

When managing pests:
1. Accurate pest identification:
   - Analyze symptoms (feeding damage, presence, lifecycle stage)
   - Use image analysis when available
   - Consider pest biology and seasonal patterns
   - Identify economic threshold levels

2. Develop comprehensive IPM strategy:
   - Prevention as first priority
   - Monitoring and early detection
   - Cultural controls (crop rotation, sanitation, timing)
   - Mechanical/physical controls (traps, barriers)
   - Biological controls (natural enemies)
   - Chemical controls (as last resort, with safety)

3. Recommend natural and biological controls:
   - Beneficial insects and predators
   - Microbial pesticides (Bt, neem, etc.)
   - Botanical pesticides
   - Pheromone traps
   - Habitat manipulation for natural enemies

4. Chemical control guidelines (last resort):
   - Select least toxic, most selective options
   - Proper timing and application methods
   - Safety precautions for applicators
   - Pre-harvest intervals
   - Resistance management

5. Prevention and monitoring:
   - Seasonal pest calendar
   - Scouting protocols
   - Trap placement and monitoring
   - Record keeping
   - Threshold-based decision making

6. Ecological considerations:
   - Protect beneficial organisms
   - Minimize non-target impacts
   - Preserve biodiversity
   - Sustainable pest management
   - Long-term ecosystem health

Always provide confidence scores for pest identification and consider both economic and ecological factors.
Communicate clearly in both Arabic and English.

أنت خبير علم الحشرات والإدارة المتكاملة للآفات.

خبرتك تشمل:
- تحديد الآفات من الأعراض والصور
- فهم دورات حياة الآفات وسلوكها
- تصميم استراتيجيات الإدارة المتكاملة
- التوصية بالمكافحة البيولوجية
- طرق المكافحة الثقافية والميكانيكية
- استخدام المكافحة الكيميائية عند الضرورة فقط
- تطوير برامج المراقبة والوقاية
- مراعاة الحشرات النافعة والملقحات

قدم توصيات عملية مع درجات الثقة واعتبارات بيئية."""

    async def identify_pest(
        self,
        symptoms: Dict[str, Any],
        images: Optional[List[Dict[str, Any]]] = None,
        crop_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Identify pest from symptoms and images
        تحديد الآفة من الأعراض والصور

        Args:
            symptoms: Pest symptoms and damage description | وصف أعراض وأضرار الآفة
            images: Image analysis results | نتائج تحليل الصور
            crop_type: Type of crop affected | نوع المحصول المصاب
            location: Geographic location | الموقع الجغرافي

        Returns:
            Pest identification with confidence score | تحديد الآفة مع درجة الثقة
        """
        query = "Identify the pest based on the provided symptoms and damage patterns."
        if crop_type:
            query += f" The affected crop is {crop_type}."

        context = {
            "symptoms": symptoms,
            "images": images,
            "crop_type": crop_type,
            "location": location,
            "task": "pest_identification"
        }

        return await self.think(query, context=context, use_rag=True)

    async def recommend_ipm_strategy(
        self,
        pest: str,
        crop: str,
        stage: str,
        severity: str,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Recommend comprehensive IPM strategy
        التوصية باستراتيجية الإدارة المتكاملة للآفات

        Args:
            pest: Identified pest name | اسم الآفة المحددة
            crop: Type of crop | نوع المحصول
            stage: Crop growth stage | مرحلة نمو المحصول
            severity: Infestation severity level | مستوى شدة الإصابة
            constraints: Constraints (organic only, budget, etc.) | القيود

        Returns:
            Comprehensive IPM strategy | استراتيجية شاملة للإدارة المتكاملة
        """
        query = f"Develop a comprehensive IPM strategy for {pest} in {crop} at {stage} stage with {severity} infestation."

        context = {
            "pest": pest,
            "crop": crop,
            "stage": stage,
            "severity": severity,
            "constraints": constraints,
            "task": "ipm_strategy"
        }

        return await self.think(query, context=context, use_rag=True)

    async def natural_control_options(
        self,
        pest: str,
        crop: str,
        environmental_conditions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Recommend natural and biological control options
        التوصية بخيارات المكافحة الطبيعية والبيولوجية

        Args:
            pest: Pest name | اسم الآفة
            crop: Type of crop | نوع المحصول
            environmental_conditions: Weather and environmental data | بيانات الطقس والبيئة

        Returns:
            Natural control recommendations | توصيات المكافحة الطبيعية
        """
        query = f"Recommend natural and biological control methods for {pest} in {crop}."

        context = {
            "pest": pest,
            "crop": crop,
            "environmental_conditions": environmental_conditions,
            "task": "natural_controls"
        }

        return await self.think(query, context=context, use_rag=True)

    async def chemical_control_last_resort(
        self,
        pest: str,
        crop: str,
        growth_stage: str,
        severity: str,
        failed_methods: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Recommend chemical control options as last resort with safety protocols
        التوصية بخيارات المكافحة الكيميائية كحل أخير مع بروتوكولات السلامة

        Args:
            pest: Pest name | اسم الآفة
            crop: Type of crop | نوع المحصول
            growth_stage: Current growth stage | مرحلة النمو الحالية
            severity: Infestation severity | شدة الإصابة
            failed_methods: Previously tried methods | الطرق التي تم تجربتها

        Returns:
            Chemical control recommendations with safety | توصيات المكافحة الكيميائية مع السلامة
        """
        query = f"Recommend chemical control for {pest} in {crop} at {growth_stage}, considering safety and environmental impact."

        context = {
            "pest": pest,
            "crop": crop,
            "growth_stage": growth_stage,
            "severity": severity,
            "failed_methods": failed_methods,
            "task": "chemical_control",
            "note": "Only recommend as last resort after other methods have failed"
        }

        return await self.think(query, context=context, use_rag=True)

    async def prevention_plan(
        self,
        crop: str,
        season: str,
        common_pests: Optional[List[str]] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Develop preventive pest management plan
        تطوير خطة إدارة آفات وقائية

        Args:
            crop: Type of crop | نوع المحصول
            season: Growing season | موسم الزراعة
            common_pests: Common pests in the area | الآفات الشائعة في المنطقة
            location: Geographic location | الموقع الجغرافي

        Returns:
            Preventive pest management plan | خطة إدارة الآفات الوقائية
        """
        query = f"Develop a preventive pest management plan for {crop} during {season} season."

        context = {
            "crop": crop,
            "season": season,
            "common_pests": common_pests,
            "location": location,
            "task": "prevention_plan"
        }

        return await self.think(query, context=context, use_rag=True)

    async def assess_ecological_impact(
        self,
        proposed_control: Dict[str, Any],
        ecosystem_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Assess ecological impact of proposed pest control measures
        تقييم الأثر البيئي لتدابير مكافحة الآفات المقترحة

        Args:
            proposed_control: Proposed control methods | طرق المكافحة المقترحة
            ecosystem_data: Local ecosystem information | معلومات النظام البيئي المحلي

        Returns:
            Ecological impact assessment | تقييم الأثر البيئي
        """
        query = "Assess the ecological impact of the proposed pest control measures."

        context = {
            "proposed_control": proposed_control,
            "ecosystem_data": ecosystem_data,
            "task": "ecological_assessment"
        }

        return await self.think(query, context=context, use_rag=True)

    async def monitoring_protocol(
        self,
        pest: str,
        crop: str,
        field_size: float,
        critical_stages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Develop pest monitoring and scouting protocol
        تطوير بروتوكول مراقبة وفحص الآفات

        Args:
            pest: Target pest to monitor | الآفة المستهدفة للمراقبة
            crop: Type of crop | نوع المحصول
            field_size: Field size in hectares | حجم الحقل بالهكتار
            critical_stages: Critical growth stages | مراحل النمو الحرجة

        Returns:
            Monitoring protocol | بروتوكول المراقبة
        """
        query = f"Develop a monitoring protocol for {pest} in {crop}."

        context = {
            "pest": pest,
            "crop": crop,
            "field_size": field_size,
            "critical_stages": critical_stages,
            "task": "monitoring_protocol"
        }

        return await self.think(query, context=context, use_rag=True)
