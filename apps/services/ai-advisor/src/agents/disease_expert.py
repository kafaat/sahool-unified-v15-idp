"""
Disease Expert Agent
وكيل خبير الأمراض

Specialized agent for crop disease diagnosis and treatment recommendations.
وكيل متخصص لتشخيص أمراض المحاصيل والتوصية بالعلاج.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool

from .base_agent import BaseAgent


class DiseaseExpertAgent(BaseAgent):
    """
    Disease Expert Agent for crop disease diagnosis
    وكيل خبير الأمراض لتشخيص أمراض المحاصيل

    Specializes in:
    - Disease identification from symptoms
    - Image-based disease detection
    - Treatment recommendations
    - Prevention strategies
    - Disease risk assessment

    متخصص في:
    - تحديد الأمراض من الأعراض
    - اكتشاف الأمراض من الصور
    - التوصية بالعلاج
    - استراتيجيات الوقاية
    - تقييم مخاطر الأمراض
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize Disease Expert Agent
        تهيئة وكيل خبير الأمراض
        """
        super().__init__(
            name="disease_expert",
            role="Crop Disease Diagnosis and Treatment Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Disease Expert
        الحصول على موجه النظام لخبير الأمراض
        """
        return """You are an expert Plant Pathologist specializing in crop disease diagnosis and management.

Your expertise includes:
- Identifying diseases from visual symptoms (leaf spots, wilting, discoloration, etc.)
- Analyzing disease patterns and progression
- Understanding pathogen life cycles (fungi, bacteria, viruses, nematodes)
- Recommending integrated pest management (IPM) strategies
- Suggesting preventive measures and biosecurity protocols

When diagnosing diseases:
1. Gather comprehensive symptom information:
   - Visual symptoms (color, pattern, location)
   - Timing and progression
   - Environmental conditions
   - Crop type and variety

2. Consider differential diagnosis:
   - List possible diseases
   - Rank by likelihood based on symptoms
   - Consider regional disease prevalence

3. Provide treatment recommendations:
   - Chemical controls (if necessary, with safety precautions)
   - Biological controls
   - Cultural practices
   - Organic alternatives

4. Emphasize prevention:
   - Crop rotation strategies
   - Resistant varieties
   - Sanitation practices
   - Monitoring protocols

5. Consider environmental and economic factors:
   - Cost-effective solutions
   - Sustainable practices
   - Minimal environmental impact

Communicate clearly in both Arabic and English. Always provide confidence levels for diagnoses.

أنت خبير أمراض نباتية متخصص في تشخيص وإدارة أمراض المحاصيل.

خبرتك تشمل:
- تحديد الأمراض من الأعراض البصرية
- تحليل أنماط الأمراض وتطورها
- فهم دورات حياة مسببات الأمراض
- التوصية باستراتيجيات المكافحة المتكاملة
- اقتراح تدابير الوقاية وبروتوكولات الأمن الحيوي

قدم تشخيصات دقيقة وتوصيات عملية مع مستويات الثقة."""

    async def diagnose(
        self,
        symptoms: Dict[str, Any],
        crop_type: str,
        image_analysis: Optional[Dict[str, Any]] = None,
        environmental_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Diagnose crop disease based on symptoms
        تشخيص مرض المحصول بناءً على الأعراض

        Args:
            symptoms: Disease symptoms description | وصف أعراض المرض
            crop_type: Type of crop affected | نوع المحصول المصاب
            image_analysis: AI image analysis results | نتائج تحليل الصور
            environmental_data: Weather and environmental data | بيانات الطقس والبيئة

        Returns:
            Disease diagnosis | تشخيص المرض
        """
        query = f"Diagnose the disease affecting {crop_type} based on the provided symptoms."

        context = {
            "crop_type": crop_type,
            "symptoms": symptoms,
            "image_analysis": image_analysis,
            "environmental_data": environmental_data,
            "task": "disease_diagnosis"
        }

        return await self.think(query, context=context, use_rag=True)

    async def recommend_treatment(
        self,
        disease: str,
        crop_type: str,
        severity: str,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Recommend treatment for identified disease
        التوصية بعلاج للمرض المحدد

        Args:
            disease: Identified disease name | اسم المرض المحدد
            crop_type: Type of crop | نوع المحصول
            severity: Disease severity level | مستوى خطورة المرض
            constraints: Treatment constraints (organic only, budget, etc.) | قيود العلاج

        Returns:
            Treatment recommendations | توصيات العلاج
        """
        query = f"Recommend treatment for {disease} in {crop_type} at {severity} severity level."

        context = {
            "disease": disease,
            "crop_type": crop_type,
            "severity": severity,
            "constraints": constraints,
            "task": "treatment_recommendation"
        }

        return await self.think(query, context=context, use_rag=True)

    async def assess_risk(
        self,
        crop_type: str,
        location: str,
        season: str,
        environmental_conditions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assess disease risk for a crop
        تقييم مخاطر الأمراض للمحصول

        Args:
            crop_type: Type of crop | نوع المحصول
            location: Field location | موقع الحقل
            season: Current season | الموسم الحالي
            environmental_conditions: Weather and environmental data | بيانات الطقس

        Returns:
            Disease risk assessment | تقييم مخاطر الأمراض
        """
        query = f"Assess disease risk for {crop_type} in {location} during {season}."

        context = {
            "crop_type": crop_type,
            "location": location,
            "season": season,
            "environmental_conditions": environmental_conditions,
            "task": "risk_assessment"
        }

        return await self.think(query, context=context, use_rag=True)

    async def prevention_strategy(
        self,
        crop_type: str,
        common_diseases: List[str],
        farming_practices: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Develop disease prevention strategy
        تطوير استراتيجية الوقاية من الأمراض

        Args:
            crop_type: Type of crop | نوع المحصول
            common_diseases: Common diseases in the area | الأمراض الشائعة
            farming_practices: Current farming practices | الممارسات الزراعية الحالية

        Returns:
            Prevention strategy | استراتيجية الوقاية
        """
        query = f"Develop a comprehensive disease prevention strategy for {crop_type}."

        context = {
            "crop_type": crop_type,
            "common_diseases": common_diseases,
            "farming_practices": farming_practices,
            "task": "prevention_strategy"
        }

        return await self.think(query, context=context, use_rag=True)

    async def analyze_progression(
        self,
        disease: str,
        timeline_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze disease progression over time
        تحليل تطور المرض مع مرور الوقت

        Args:
            disease: Disease name | اسم المرض
            timeline_data: Timeline of disease observations | جدول زمني لملاحظات المرض

        Returns:
            Progression analysis | تحليل التطور
        """
        query = f"Analyze the progression of {disease} based on timeline data."

        context = {
            "disease": disease,
            "timeline_data": timeline_data,
            "task": "progression_analysis"
        }

        return await self.think(query, context=context, use_rag=False)
