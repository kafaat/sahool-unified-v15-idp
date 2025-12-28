"""
A2A Adapter for AI Advisor Service
محول A2A لخدمة المستشار الذكي

Wraps the existing AI Advisor service as an A2A-compatible agent.
يلف خدمة المستشار الذكي الحالية كوكيل متوافق مع A2A.

This demonstrates how to integrate existing services with the A2A protocol.
يوضح كيفية دمج الخدمات الموجودة مع بروتوكول A2A.
"""

import sys
import os
from typing import Dict, Any, List

# Add shared path for imports
# إضافة المسار المشترك للاستيراد
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))

from a2a.agent import A2AAgent, AgentCapability
from a2a.protocol import TaskMessage
import structlog

logger = structlog.get_logger()


class AIAdvisorA2AAgent(A2AAgent):
    """
    A2A Agent wrapper for AI Advisor
    غلاف وكيل A2A للمستشار الذكي

    Exposes AI Advisor capabilities via A2A protocol.
    يعرض قدرات المستشار الذكي عبر بروتوكول A2A.
    """

    def __init__(
        self,
        base_url: str,
        agents: Dict[str, Any],
        supervisor: Any
    ):
        """
        Initialize AI Advisor A2A agent
        تهيئة وكيل A2A للمستشار الذكي

        Args:
            base_url: Base URL of the service
            agents: Dictionary of AI advisor agents
            supervisor: Supervisor instance for multi-agent coordination
        """
        # Initialize base A2A agent
        # تهيئة وكيل A2A الأساسي
        super().__init__(
            agent_id="sahool-ai-advisor",
            name="SAHOOL AI Agricultural Advisor",
            version="1.0.0",
            description="Multi-agent AI system for comprehensive agricultural advisory services including crop disease diagnosis, irrigation optimization, yield prediction, and field analysis.",
            provider="SAHOOL Agricultural Platform",
            task_endpoint=f"{base_url}/a2a/tasks",
            websocket_endpoint=f"{base_url.replace('http', 'ws')}/a2a/ws",
        )

        # Store service components
        # تخزين مكونات الخدمة
        self.agents = agents
        self.supervisor = supervisor

        # Register task handlers
        # تسجيل معالجات المهام
        self._register_handlers()

        logger.info(
            "ai_advisor_a2a_agent_initialized",
            agent_id=self.agent_id,
            capabilities_count=len(self.get_capabilities())
        )

    def get_capabilities(self) -> List[AgentCapability]:
        """
        Define AI Advisor capabilities for A2A
        تحديد قدرات المستشار الذكي لـ A2A

        Returns:
            List of agent capabilities
        """
        return [
            AgentCapability(
                capability_id="crop-disease-diagnosis",
                name="Crop Disease Diagnosis",
                description="Diagnose crop diseases based on symptoms, images, and environmental conditions. Provides treatment recommendations.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop (wheat, corn, tomato, etc.)"
                        },
                        "symptoms": {
                            "type": "object",
                            "description": "Observable disease symptoms",
                            "properties": {
                                "leaf_condition": {"type": "string"},
                                "color_changes": {"type": "string"},
                                "growth_issues": {"type": "string"}
                            }
                        },
                        "image_path": {
                            "type": "string",
                            "description": "Optional path to crop image",
                            "nullable": True
                        },
                        "location": {
                            "type": "string",
                            "description": "Field location",
                            "nullable": True
                        }
                    },
                    "required": ["crop_type", "symptoms"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "diagnosis": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "treatment_recommendations": {"type": "array"},
                        "preventive_measures": {"type": "array"}
                    }
                },
                tags=["agriculture", "disease", "diagnosis", "crop-health"],
                examples=[
                    {
                        "input": {
                            "crop_type": "tomato",
                            "symptoms": {
                                "leaf_condition": "yellow spots",
                                "color_changes": "brown edges"
                            }
                        },
                        "output": {
                            "diagnosis": "Early Blight (Alternaria solani)",
                            "confidence": 0.85,
                            "treatment_recommendations": ["Apply fungicide", "Remove infected leaves"],
                            "preventive_measures": ["Ensure proper spacing", "Avoid overhead watering"]
                        }
                    }
                ]
            ),
            AgentCapability(
                capability_id="irrigation-optimization",
                name="Irrigation Optimization",
                description="Provide irrigation recommendations based on crop type, growth stage, soil conditions, and weather forecast.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "crop_type": {"type": "string"},
                        "growth_stage": {
                            "type": "string",
                            "enum": ["germination", "vegetative", "flowering", "fruiting", "maturity"]
                        },
                        "soil_data": {
                            "type": "object",
                            "properties": {
                                "moisture_level": {"type": "number"},
                                "soil_type": {"type": "string"}
                            }
                        },
                        "weather_data": {
                            "type": "object",
                            "properties": {
                                "temperature": {"type": "number"},
                                "humidity": {"type": "number"},
                                "rainfall_forecast": {"type": "array"}
                            }
                        }
                    },
                    "required": ["crop_type", "growth_stage"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "irrigation_schedule": {"type": "object"},
                        "water_amount_mm": {"type": "number"},
                        "frequency_days": {"type": "number"},
                        "recommendations": {"type": "array"}
                    }
                },
                tags=["agriculture", "irrigation", "water-management", "optimization"],
            ),
            AgentCapability(
                capability_id="yield-prediction",
                name="Yield Prediction",
                description="Predict crop yield based on current conditions, historical data, and growth patterns.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "crop_type": {"type": "string"},
                        "area_hectares": {"type": "number"},
                        "growth_stage": {"type": "string"},
                        "field_data": {"type": "object"},
                        "weather_data": {"type": "object"}
                    },
                    "required": ["crop_type", "area_hectares", "growth_stage"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "predicted_yield_tons": {"type": "number"},
                        "confidence_interval": {"type": "object"},
                        "factors_analysis": {"type": "object"},
                        "optimization_suggestions": {"type": "array"}
                    }
                },
                tags=["agriculture", "yield", "prediction", "analytics"],
            ),
            AgentCapability(
                capability_id="field-analysis",
                name="Comprehensive Field Analysis",
                description="Complete field assessment including satellite imagery analysis, disease risk assessment, and general recommendations.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "crop_type": {"type": "string"},
                        "include_disease_check": {"type": "boolean", "default": True},
                        "include_irrigation": {"type": "boolean", "default": True},
                        "include_yield_prediction": {"type": "boolean", "default": True}
                    },
                    "required": ["field_id", "crop_type"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "satellite_data": {"type": "object"},
                        "field_health_score": {"type": "number"},
                        "disease_risk": {"type": "object"},
                        "irrigation_advice": {"type": "object"},
                        "yield_prediction": {"type": "object"},
                        "overall_recommendations": {"type": "array"}
                    }
                },
                tags=["agriculture", "field-analysis", "comprehensive", "satellite"],
            ),
            AgentCapability(
                capability_id="general-agricultural-query",
                name="General Agricultural Advisory",
                description="Answer general agricultural questions using multi-agent coordination and RAG-enhanced knowledge base.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "language": {
                            "type": "string",
                            "enum": ["en", "ar"],
                            "default": "en"
                        },
                        "context": {"type": "object", "nullable": True}
                    },
                    "required": ["question"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string"},
                        "sources": {"type": "array"},
                        "related_topics": {"type": "array"},
                        "confidence": {"type": "number"}
                    }
                },
                tags=["agriculture", "advisory", "general", "qa"],
            ),
        ]

    def _register_handlers(self):
        """
        Register task handlers for each capability
        تسجيل معالجات المهام لكل قدرة
        """
        self.register_task_handler("crop-disease-diagnosis", self._handle_disease_diagnosis)
        self.register_task_handler("irrigation-optimization", self._handle_irrigation)
        self.register_task_handler("yield-prediction", self._handle_yield_prediction)
        self.register_task_handler("field-analysis", self._handle_field_analysis)
        self.register_task_handler("general-agricultural-query", self._handle_general_query)

    async def _handle_disease_diagnosis(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Handle disease diagnosis task
        معالجة مهمة تشخيص المرض
        """
        params = task.parameters
        disease_expert = self.agents.get("disease_expert")

        if not disease_expert:
            raise ValueError("Disease expert agent not available")

        # Call disease expert
        # استدعاء خبير الأمراض
        result = await disease_expert.diagnose(
            symptoms=params.get("symptoms", {}),
            crop_type=params.get("crop_type"),
            image_analysis=None,  # Image analysis would be done separately
        )

        return {
            "diagnosis": result.get("diagnosis", "Unknown"),
            "confidence": result.get("confidence", 0.0),
            "treatment_recommendations": result.get("recommendations", []),
            "preventive_measures": result.get("prevention", []),
        }

    async def _handle_irrigation(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Handle irrigation optimization task
        معالجة مهمة تحسين الري
        """
        params = task.parameters
        irrigation_advisor = self.agents.get("irrigation_advisor")

        if not irrigation_advisor:
            raise ValueError("Irrigation advisor agent not available")

        # Call irrigation advisor
        # استدعاء مستشار الري
        result = await irrigation_advisor.recommend_irrigation(
            crop_type=params.get("crop_type"),
            growth_stage=params.get("growth_stage"),
            soil_data=params.get("soil_data", {}),
            weather_data=params.get("weather_data", {}),
        )

        return result

    async def _handle_yield_prediction(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Handle yield prediction task
        معالجة مهمة التنبؤ بالمحصول
        """
        params = task.parameters
        yield_predictor = self.agents.get("yield_predictor")

        if not yield_predictor:
            raise ValueError("Yield predictor agent not available")

        # Call yield predictor
        # استدعاء متنبئ المحصول
        result = await yield_predictor.predict_yield(
            crop_type=params.get("crop_type"),
            area=params.get("area_hectares", 1.0),
            growth_stage=params.get("growth_stage"),
            field_data=params.get("field_data", {}),
            weather_data=params.get("weather_data", {}),
        )

        return result

    async def _handle_field_analysis(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Handle comprehensive field analysis task
        معالجة مهمة تحليل الحقل الشامل
        """
        params = task.parameters
        field_analyst = self.agents.get("field_analyst")

        if not field_analyst:
            raise ValueError("Field analyst agent not available")

        # Perform field analysis
        # إجراء تحليل الحقل
        result = await field_analyst.analyze_field(
            field_id=params.get("field_id"),
            satellite_data={},  # Would be fetched from satellite tool
        )

        # Optionally include other analyses
        # اختيارياً تضمين تحليلات أخرى
        response = {
            "field_id": params.get("field_id"),
            "field_analysis": result,
        }

        if params.get("include_disease_check"):
            disease_expert = self.agents.get("disease_expert")
            if disease_expert:
                disease_risk = await disease_expert.assess_risk(
                    crop_type=params.get("crop_type"),
                    location=params.get("field_id"),
                    season="current",
                    environmental_conditions={},
                )
                response["disease_risk"] = disease_risk

        if params.get("include_irrigation"):
            irrigation_advisor = self.agents.get("irrigation_advisor")
            if irrigation_advisor:
                irrigation_advice = await irrigation_advisor.recommend_irrigation(
                    crop_type=params.get("crop_type"),
                    growth_stage="vegetative",
                    soil_data={},
                    weather_data={},
                )
                response["irrigation_advice"] = irrigation_advice

        if params.get("include_yield_prediction"):
            yield_predictor = self.agents.get("yield_predictor")
            if yield_predictor:
                yield_prediction = await yield_predictor.predict_yield(
                    crop_type=params.get("crop_type"),
                    area=1.0,
                    growth_stage="vegetative",
                    field_data=result,
                    weather_data={},
                )
                response["yield_prediction"] = yield_prediction

        return response

    async def _handle_general_query(self, task: TaskMessage) -> Dict[str, Any]:
        """
        Handle general agricultural query
        معالجة استعلام زراعي عام
        """
        params = task.parameters

        if not self.supervisor:
            raise ValueError("Supervisor not available")

        # Use supervisor to coordinate agents
        # استخدام المشرف لتنسيق الوكلاء
        result = await self.supervisor.coordinate(
            query=params.get("question"),
            context=params.get("context"),
        )

        return {
            "answer": result.get("response", ""),
            "sources": result.get("sources", []),
            "related_topics": result.get("related", []),
            "confidence": result.get("confidence", 0.0),
        }


def create_ai_advisor_a2a_agent(
    base_url: str,
    agents: Dict[str, Any],
    supervisor: Any
) -> AIAdvisorA2AAgent:
    """
    Factory function to create AI Advisor A2A agent
    دالة المصنع لإنشاء وكيل A2A للمستشار الذكي

    Args:
        base_url: Base URL of the AI Advisor service
        agents: Dictionary of AI advisor agents
        supervisor: Supervisor instance

    Returns:
        Configured AIAdvisorA2AAgent instance
    """
    return AIAdvisorA2AAgent(
        base_url=base_url,
        agents=agents,
        supervisor=supervisor
    )
