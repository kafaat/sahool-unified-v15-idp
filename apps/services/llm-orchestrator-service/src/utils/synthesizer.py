# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Response Synthesizer for LLM Orchestrator Service.

This module synthesizes responses from multiple agent results
into a coherent, human-friendly summary with actionable recommendations.

مُجمّع الاستجابات لخدمة تنسيق نماذج اللغة الكبيرة.
تجمع هذه الوحدة الاستجابات من نتائج عدة وكلاء
في ملخص متسق ومفهوم للإنسان مع توصيات قابلة للتنفيذ.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

import structlog

from ..api.schemas import (
    ActionType,
    AgentResult,
    AutoAction,
    IntentClassification,
    IntentType,
    OrchestratorResponse,
)

logger = structlog.get_logger(__name__)


# Summary templates for different intents (Arabic and English)
SUMMARY_TEMPLATES: dict[IntentType, dict[str, str]] = {
    IntentType.CROP_DISEASE: {
        "en": "Crop health analysis completed. {disease_count} potential issues detected.",
        "ar": "اكتمل تحليل صحة المحصول. تم اكتشاف {disease_count} مشكلة محتملة.",
    },
    IntentType.IRRIGATION_QUERY: {
        "en": "Irrigation analysis completed. Current soil moisture: {moisture}%.",
        "ar": "اكتمل تحليل الري. رطوبة التربة الحالية: {moisture}%.",
    },
    IntentType.FERTILIZER_ADVICE: {
        "en": "Fertilizer recommendation generated. {nutrient_count} nutrient adjustments suggested.",
        "ar": "تم إنشاء توصية الأسمدة. تم اقتراح {nutrient_count} تعديلات غذائية.",
    },
    IntentType.PEST_DETECTION: {
        "en": "Pest analysis completed. Risk level: {risk_level}.",
        "ar": "اكتمل تحليل الآفات. مستوى الخطر: {risk_level}.",
    },
    IntentType.WEATHER_QUERY: {
        "en": "Weather forecast retrieved. {conditions} expected for the next {days} days.",
        "ar": "تم استرجاع توقعات الطقس. {conditions} متوقع للأيام الـ {days} القادمة.",
    },
    IntentType.YIELD_PREDICTION: {
        "en": "Yield prediction completed. Estimated yield: {yield_value} tons/hectare.",
        "ar": "اكتملت توقعات الإنتاجية. الإنتاجية المقدرة: {yield_value} طن/هكتار.",
    },
    IntentType.FIELD_ANALYSIS: {
        "en": "Field analysis completed. {zone_count} zones analyzed.",
        "ar": "اكتمل تحليل الحقل. تم تحليل {zone_count} منطقة.",
    },
    IntentType.TERRAIN_ANALYSIS: {
        "en": "Terrain analysis completed. Average slope: {slope}%.",
        "ar": "اكتمل تحليل التضاريس. متوسط الميل: {slope}%.",
    },
    IntentType.HYDROLOGY_QUERY: {
        "en": "Hydrology analysis completed. Drainage status: {status}.",
        "ar": "اكتمل تحليل الهيدرولوجيا. حالة الصرف: {status}.",
    },
    IntentType.LEVELING_QUERY: {
        "en": "Leveling analysis completed. Cut/fill ratio: {ratio}.",
        "ar": "اكتمل تحليل التسوية. نسبة القطع/الردم: {ratio}.",
    },
    IntentType.IMAGE_ANALYSIS: {
        "en": "Image analysis completed. {detection_count} objects detected.",
        "ar": "اكتمل تحليل الصورة. تم اكتشاف {detection_count} كائن.",
    },
    IntentType.GENERAL_ADVISORY: {
        "en": "Agricultural advisory completed. {recommendation_count} recommendations generated.",
        "ar": "اكتملت الاستشارة الزراعية. تم إنشاء {recommendation_count} توصية.",
    },
    IntentType.MULTI_INTENT: {
        "en": "Comprehensive analysis completed. {agent_count} analyses performed.",
        "ar": "اكتمل التحليل الشامل. تم إجراء {agent_count} تحليل.",
    },
    IntentType.UNKNOWN: {
        "en": "Analysis completed based on available data.",
        "ar": "اكتمل التحليل بناءً على البيانات المتاحة.",
    },
}


class ResponseSynthesizer:
    """
    Synthesizes coherent responses from agent results.
    يجمع استجابات متسقة من نتائج الوكلاء.
    """

    def __init__(self) -> None:
        """Initialize the response synthesizer."""
        pass

    def synthesize(
        self,
        intent: IntentClassification,
        agent_results: list[AgentResult],
        request_id: str | None = None,
    ) -> OrchestratorResponse:
        """
        Synthesize a complete response from agent results.
        تجميع استجابة كاملة من نتائج الوكلاء.
        """
        request_id = request_id or str(uuid.uuid4())
        datetime.utcnow()

        # Calculate totals
        successful_results = [r for r in agent_results if r.success]
        failed_results = [r for r in agent_results if not r.success]
        cached_count = sum(1 for r in agent_results if r.cached)
        total_latency = sum(r.latency_ms for r in agent_results)

        # Generate summary
        summary_en, summary_ar = self._generate_summary(intent, successful_results, agent_results)

        # Extract recommendations
        recommendations_en, recommendations_ar = self._extract_recommendations(
            intent, successful_results
        )

        # Generate actions
        actions = self._generate_actions(intent, successful_results)

        # Determine overall success
        required_agents = [r for r in agent_results if not r.cached]
        success = len(successful_results) > 0 and len(failed_results) < len(required_agents)

        logger.info(
            "response_synthesized",
            request_id=request_id,
            success=success,
            agents_called=len(agent_results),
            successful=len(successful_results),
            failed=len(failed_results),
            cached=cached_count,
            total_latency_ms=total_latency,
            recommendations=len(recommendations_en),
            actions=len(actions),
        )

        return OrchestratorResponse(
            request_id=request_id,
            success=success,
            summary_en=summary_en,
            summary_ar=summary_ar,
            detailed_results=agent_results,
            actions=actions,
            recommendations_en=recommendations_en,
            recommendations_ar=recommendations_ar,
            intent=intent,
            total_latency_ms=total_latency,
            agents_called=len(agent_results),
            cached_responses=cached_count,
            metadata={
                "successful_agents": [r.agent_name for r in successful_results],
                "failed_agents": [r.agent_name for r in failed_results],
                "synthesis_time": datetime.utcnow().isoformat(),
            },
        )

    def _generate_summary(
        self,
        intent: IntentClassification,
        successful_results: list[AgentResult],
        all_results: list[AgentResult],
    ) -> tuple[str, str]:
        """Generate bilingual summary."""
        templates = SUMMARY_TEMPLATES.get(
            intent.intent_type, SUMMARY_TEMPLATES[IntentType.GENERAL_ADVISORY]
        )

        # Extract values for template filling
        values = self._extract_summary_values(intent, successful_results)

        try:
            summary_en = templates["en"].format(**values)
            summary_ar = templates["ar"].format(**values)
        except KeyError:
            # Fallback if template variables missing
            summary_en = f"Analysis completed. {len(successful_results)} of {len(all_results)} agents responded successfully."
            summary_ar = (
                f"اكتمل التحليل. {len(successful_results)} من {len(all_results)} وكيل استجاب بنجاح."
            )

        return summary_en, summary_ar

    def _extract_summary_values(
        self,
        intent: IntentClassification,
        results: list[AgentResult],
    ) -> dict[str, Any]:
        """Extract values from results for summary templates."""
        values: dict[str, Any] = {
            "disease_count": 0,
            "moisture": "N/A",
            "nutrient_count": 0,
            "risk_level": "unknown",
            "conditions": "variable",
            "days": 7,
            "yield_value": "N/A",
            "zone_count": 0,
            "slope": "N/A",
            "status": "unknown",
            "ratio": "N/A",
            "detection_count": 0,
            "recommendation_count": len(results),
            "agent_count": len(results),
        }

        for result in results:
            if not result.result:
                continue

            data = result.result

            # Extract disease count
            if "detection_count" in data:
                values["disease_count"] = data["detection_count"]
                values["detection_count"] = data["detection_count"]
            elif "detections" in data and isinstance(data["detections"], list):
                values["disease_count"] = len(data["detections"])
                values["detection_count"] = len(data["detections"])

            # Extract moisture
            if "soil_moisture" in data:
                values["moisture"] = f"{data['soil_moisture']:.1f}"

            # Extract nutrient count
            if "deficiencies" in data and isinstance(data["deficiencies"], list):
                values["nutrient_count"] = len(data["deficiencies"])

            # Extract risk level
            if "overall_health" in data:
                health = data["overall_health"]
                if isinstance(health, dict):
                    values["risk_level"] = health.get("status_en", "unknown")
                else:
                    values["risk_level"] = str(health)

            # Extract weather conditions
            if "forecast" in data or "conditions" in data:
                values["conditions"] = data.get("conditions", "variable conditions")

            # Extract yield
            if "predicted_yield_kg_ha" in data:
                values["yield_value"] = f"{data['predicted_yield_kg_ha'] / 1000:.2f}"
            elif "prediction" in data and isinstance(data["prediction"], dict):
                pred = data["prediction"]
                if "predicted_yield_kg_ha" in pred:
                    values["yield_value"] = f"{pred['predicted_yield_kg_ha'] / 1000:.2f}"

            # Extract zone count
            if "zones_total" in data:
                values["zone_count"] = data["zones_total"]
            elif "zones" in data and isinstance(data["zones"], list):
                values["zone_count"] = len(data["zones"])

            # Extract slope
            if "average_slope" in data:
                values["slope"] = f"{data['average_slope']:.1f}"

            # Extract status
            if "status" in data:
                values["status"] = data["status"]

        return values

    def _extract_recommendations(
        self,
        intent: IntentClassification,
        results: list[AgentResult],
    ) -> tuple[list[str], list[str]]:
        """Extract recommendations from agent results."""
        recommendations_en: list[str] = []
        recommendations_ar: list[str] = []

        for result in results:
            if not result.result:
                continue

            data = result.result

            # Extract from standard recommendation fields
            if "recommendations" in data:
                recs = data["recommendations"]
                if isinstance(recs, list):
                    for rec in recs:
                        if isinstance(rec, dict):
                            if "recommendation_en" in rec:
                                recommendations_en.append(rec["recommendation_en"])
                            if "recommendation_ar" in rec:
                                recommendations_ar.append(rec["recommendation_ar"])
                            if "text" in rec:
                                recommendations_en.append(rec["text"])
                        elif isinstance(rec, str):
                            recommendations_en.append(rec)

            # Extract from actions
            if "actions" in data and isinstance(data["actions"], list):
                for action in data["actions"]:
                    if isinstance(action, dict):
                        if "title" in action:
                            recommendations_ar.append(action["title"])
                        if "title_en" in action:
                            recommendations_en.append(action["title_en"])
                        if "reason" in action:
                            recommendations_ar.append(action["reason"])
                        if "reason_en" in action:
                            recommendations_en.append(action["reason_en"])

            # Extract from detections
            if "detections" in data and isinstance(data["detections"], list):
                for detection in data["detections"]:
                    if isinstance(detection, dict):
                        # Extract treatment recommendations
                        if "treatment" in detection:
                            treatment = detection["treatment"]
                            if isinstance(treatment, dict):
                                if "recommendation_en" in treatment:
                                    recommendations_en.append(treatment["recommendation_en"])
                                if "recommendation_ar" in treatment:
                                    recommendations_ar.append(treatment["recommendation_ar"])

            # Extract from fertilizer plan
            if "fertilizer_plan" in data and isinstance(data["fertilizer_plan"], dict):
                plan = data["fertilizer_plan"]
                if "applications" in plan:
                    for app in plan["applications"]:
                        if isinstance(app, dict):
                            product = app.get("product", "")
                            rate = app.get("rate_kg_ha", "")
                            if product and rate:
                                recommendations_en.append(f"Apply {product} at {rate} kg/ha")
                                recommendations_ar.append(f"تطبيق {product} بمعدل {rate} كجم/هكتار")

        # Remove duplicates while preserving order
        recommendations_en = list(dict.fromkeys(recommendations_en))[:10]
        recommendations_ar = list(dict.fromkeys(recommendations_ar))[:10]

        # Add default recommendations if none found
        if not recommendations_en:
            recommendations_en = [
                "Continue monitoring crop health regularly",
                "Check irrigation levels as needed",
                "Consult with local agricultural experts for specific advice",
            ]
            recommendations_ar = [
                "استمر في مراقبة صحة المحصول بانتظام",
                "تحقق من مستويات الري حسب الحاجة",
                "استشر الخبراء الزراعيين المحليين للحصول على مشورة محددة",
            ]

        return recommendations_en, recommendations_ar

    def _generate_actions(
        self,
        intent: IntentClassification,
        results: list[AgentResult],
    ) -> list[AutoAction]:
        """Generate automated actions based on intent and results."""
        actions: list[AutoAction] = []

        # Map intents to potential actions
        intent_actions: dict[IntentType, list[tuple[ActionType, str, str]]] = {
            IntentType.CROP_DISEASE: [
                (
                    ActionType.TRIGGER_PEST_SCAN,
                    "Initiate detailed pest scan",
                    "بدء فحص الآفات التفصيلي",
                ),
                (
                    ActionType.SEND_ALERT,
                    "Send disease alert to field team",
                    "إرسال تنبيه المرض لفريق الحقل",
                ),
            ],
            IntentType.IRRIGATION_QUERY: [
                (
                    ActionType.SCHEDULE_IRRIGATION,
                    "Schedule next irrigation session",
                    "جدولة جلسة الري التالية",
                ),
            ],
            IntentType.FERTILIZER_ADVICE: [
                (
                    ActionType.APPLY_FERTILIZER,
                    "Schedule fertilizer application",
                    "جدولة تطبيق السماد",
                ),
                (
                    ActionType.CREATE_TASK,
                    "Create fertilization task",
                    "إنشاء مهمة التسميد",
                ),
            ],
            IntentType.PEST_DETECTION: [
                (
                    ActionType.TRIGGER_PEST_SCAN,
                    "Schedule detailed pest inspection",
                    "جدولة فحص الآفات التفصيلي",
                ),
                (ActionType.SEND_ALERT, "Alert pest control team", "تنبيه فريق مكافحة الآفات"),
            ],
            IntentType.FIELD_ANALYSIS: [
                (ActionType.GENERATE_REPORT, "Generate field report", "إنشاء تقرير الحقل"),
                (
                    ActionType.UPDATE_FIELD_STATUS,
                    "Update field status",
                    "تحديث حالة الحقل",
                ),
            ],
        }

        # Get relevant actions for the intent
        potential_actions = intent_actions.get(intent.intent_type, [])

        for action_type, reason_en, reason_ar in potential_actions:
            # Determine priority based on results
            priority: str = "medium"

            # Check results for severity indicators
            for result in results:
                if result.result:
                    data = result.result
                    if "overall_health" in data:
                        health = data["overall_health"]
                        if isinstance(health, dict):
                            status = health.get("status_en", "").lower()
                            if status in ("critical", "poor"):
                                priority = "high"
                            elif status in ("fair", "warning"):
                                priority = "medium"

                    if "risk_level" in data:
                        risk = str(data["risk_level"]).lower()
                        if risk in ("critical", "high"):
                            priority = "high"

            # Generate action
            actions.append(
                AutoAction(
                    action_type=action_type,
                    params={"intent": intent.intent_type.value},
                    requires_confirmation=True,
                    priority=priority,
                    reason_en=reason_en,
                    reason_ar=reason_ar,
                    expires_at=datetime.utcnow() + timedelta(hours=24),
                )
            )

        return actions[:5]  # Limit to 5 actions


async def synthesize_response(
    intent: IntentClassification,
    agent_results: list[AgentResult],
    request_id: str | None = None,
) -> OrchestratorResponse:
    """
    Convenience function to synthesize response.
    دالة مساعدة لتجميع الاستجابة.
    """
    synthesizer = ResponseSynthesizer()
    return synthesizer.synthesize(intent, agent_results, request_id)
