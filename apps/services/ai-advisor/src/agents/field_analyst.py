"""
Field Analyst Agent
وكيل محلل الحقول

Specialized agent for analyzing field data, NDVI, and crop health metrics.
وكيل متخصص لتحليل بيانات الحقل ومؤشر NDVI ومقاييس صحة المحاصيل.
"""

from typing import Any

from langchain_core.tools import Tool

from .base_agent import BaseAgent


class FieldAnalystAgent(BaseAgent):
    """
    Field Analyst Agent for comprehensive field analysis
    وكيل محلل الحقول للتحليل الشامل للحقل

    Specializes in:
    - NDVI analysis and interpretation
    - Satellite imagery assessment
    - Field health monitoring
    - Temporal trend analysis

    متخصص في:
    - تحليل وتفسير NDVI
    - تقييم الصور الفضائية
    - مراقبة صحة الحقل
    - تحليل الاتجاهات الزمنية
    """

    def __init__(
        self,
        tools: list[Tool] | None = None,
        retriever: Any | None = None,
    ):
        """
        Initialize Field Analyst Agent
        تهيئة وكيل محلل الحقول
        """
        super().__init__(
            name="field_analyst",
            role="Field Data Analysis and NDVI Interpretation Expert",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Field Analyst
        الحصول على موجه النظام لمحلل الحقول
        """
        return """You are an expert Field Analyst specializing in agricultural remote sensing and field data analysis.

Your expertise includes:
- NDVI (Normalized Difference Vegetation Index) interpretation
- Satellite imagery analysis
- Crop health assessment from multispectral data
- Temporal analysis of vegetation changes
- Identifying stress patterns in crops

When analyzing field data:
1. Interpret NDVI values accurately:
   - 0.8-1.0: Very healthy, dense vegetation
   - 0.6-0.8: Healthy vegetation
   - 0.4-0.6: Moderate vegetation/stress
   - 0.2-0.4: Sparse vegetation/high stress
   - Below 0.2: Bare soil or dead vegetation

2. Consider temporal trends:
   - Compare current values with historical data
   - Identify seasonal patterns
   - Detect anomalies or sudden changes

3. Provide actionable insights:
   - Highlight areas needing attention
   - Suggest immediate actions for stressed areas
   - Recommend monitoring frequency

4. Communicate in both Arabic and English when appropriate

Always base your analysis on data and provide confidence levels for your assessments.

أنت خبير تحليل حقول متخصص في الاستشعار عن بعد الزراعي وتحليل بيانات الحقل.

خبرتك تشمل:
- تفسير مؤشر NDVI
- تحليل الصور الفضائية
- تقييم صحة المحاصيل من البيانات متعددة الأطياف
- التحليل الزمني لتغيرات الغطاء النباتي
- تحديد أنماط الإجهاد في المحاصيل

قدم تحليلات دقيقة مبنية على البيانات مع مستويات الثقة."""

    async def analyze_field(
        self,
        field_id: str,
        satellite_data: dict[str, Any] | None = None,
        historical_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive field analysis
        تحليل شامل للحقل

        Args:
            field_id: Field identifier | معرف الحقل
            satellite_data: Current satellite data | البيانات الفضائية الحالية
            historical_data: Historical field data | البيانات التاريخية للحقل

        Returns:
            Analysis results | نتائج التحليل
        """
        query = f"Analyze field {field_id} based on the provided satellite and historical data."

        context = {
            "field_id": field_id,
            "satellite_data": satellite_data,
            "historical_data": historical_data,
            "analysis_type": "comprehensive_field_analysis",
        }

        return await self.think(query, context=context, use_rag=True)

    async def interpret_ndvi(
        self,
        ndvi_value: float,
        crop_type: str | None = None,
        growth_stage: str | None = None,
    ) -> dict[str, Any]:
        """
        Interpret NDVI value in agricultural context
        تفسير قيمة NDVI في السياق الزراعي

        Args:
            ndvi_value: NDVI value to interpret | قيمة NDVI للتفسير
            crop_type: Type of crop | نوع المحصول
            growth_stage: Current growth stage | مرحلة النمو الحالية

        Returns:
            NDVI interpretation | تفسير NDVI
        """
        query = f"Interpret NDVI value of {ndvi_value}"
        if crop_type:
            query += f" for {crop_type} crop"
        if growth_stage:
            query += f" at {growth_stage} stage"

        context = {
            "ndvi_value": ndvi_value,
            "crop_type": crop_type,
            "growth_stage": growth_stage,
        }

        return await self.think(query, context=context, use_rag=True)

    async def detect_anomalies(
        self,
        current_data: dict[str, Any],
        baseline_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Detect anomalies by comparing current and baseline data
        كشف الشذوذات بمقارنة البيانات الحالية والأساسية

        Args:
            current_data: Current field measurements | القياسات الحالية
            baseline_data: Baseline/expected measurements | القياسات الأساسية

        Returns:
            Anomaly detection results | نتائج كشف الشذوذات
        """
        query = "Detect and analyze anomalies in the field data compared to baseline."

        context = {
            "current_data": current_data,
            "baseline_data": baseline_data,
            "analysis_type": "anomaly_detection",
        }

        return await self.think(query, context=context, use_rag=False)

    async def recommend_monitoring(
        self,
        field_status: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Recommend monitoring strategy based on field status
        التوصية باستراتيجية المراقبة بناءً على حالة الحقل

        Args:
            field_status: Current field status | حالة الحقل الحالية

        Returns:
            Monitoring recommendations | توصيات المراقبة
        """
        query = "Based on the current field status, recommend an optimal monitoring strategy."

        context = {"field_status": field_status, "analysis_type": "monitoring_strategy"}

        return await self.think(query, context=context, use_rag=True)
