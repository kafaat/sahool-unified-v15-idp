"""
Farm Advisor Agent
==================
وكيل مستشار المزرعة

Bilingual agricultural advisor with dual-agent pattern (Plan/Execute).
Inspired by OpenCode's Build/Plan agents.

Features:
- Plan mode: Read-only analysis, safety checks
- Execute mode: Carry out recommendations
- Arabic-first with English support
- Integration with all SAHOOL services
- Specialized sub-agents for different domains (NEW)
- Collaborative decision making with consensus (NEW)
- Learning from farmer feedback (NEW)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

from ..llm_provider import LLMProviderManager
from ..validation import escape_prompt_input
from .base import (
    AgentCapability,
    AgentMode,
    AgentStep,
    AgentTool,
    BaseAutonomousAgent,
    CollaborationRole,
    ConsensusType,
    MemoryType,
    ToolResult,
)

logger = structlog.get_logger()


@dataclass
class FarmContext:
    """
    Farm context for advisory.
    سياق المزرعة للاستشارة
    """

    farm_id: str
    farmer_id: str
    farmer_name: str | None = None
    preferred_language: str = "ar"  # ar or en
    fields: list[dict[str, Any]] = field(default_factory=list)
    active_crops: list[str] = field(default_factory=list)
    location: dict[str, float] | None = None
    water_sources: list[str] = field(default_factory=list)
    equipment: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborativeDecision:
    """
    Result of a collaborative decision.
    نتيجة قرار تعاوني
    """

    decision_id: str
    topic: str
    topic_ar: str
    participating_agents: list[str]
    final_recommendation: dict[str, Any]
    confidence: float
    consensus_type: str
    individual_recommendations: list[dict[str, Any]]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ========================================
# SPECIALIZED SUB-AGENTS
# الوكلاء الفرعيين المتخصصين
# ========================================


class IrrigationSubAgent(BaseAutonomousAgent):
    """
    Specialized sub-agent for irrigation recommendations.
    وكيل فرعي متخصص لتوصيات الري
    """

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        parent_agent: BaseAutonomousAgent | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            agent_id=kwargs.get("agent_id", "irrigation-sub-agent"),
            name=kwargs.get("name", "Irrigation Specialist"),
            name_ar=kwargs.get("name_ar", "متخصص الري"),
            description="Specialized agent for irrigation scheduling and optimization",
            description_ar="وكيل متخصص في جدولة وتحسين الري",
            mode=AgentMode.EXECUTE,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            collaboration_role=CollaborationRole.SPECIALIST,
        )
        self.parent_agent = parent_agent

    def _register_default_tools(self) -> None:
        """Register irrigation-specific tools."""
        self.register_tool(
            AgentTool(
                name="calculate_et",
                name_ar="حساب التبخر-نتح",
                description="Calculate evapotranspiration using Penman-Monteith",
                description_ar="حساب التبخر-نتح باستخدام بنمان-مونتيث",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "weather_data": {"type": "object"},
                        "crop_coefficient": {"type": "number"},
                    },
                    "required": ["field_id"],
                },
                handler=self._calculate_et,
                tags=["irrigation", "et"],
            )
        )

        self.register_tool(
            AgentTool(
                name="calculate_water_balance",
                name_ar="حساب التوازن المائي",
                description="Calculate soil water balance",
                description_ar="حساب التوازن المائي للتربة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "soil_moisture": {"type": "number"},
                        "et_value": {"type": "number"},
                        "rainfall_mm": {"type": "number"},
                    },
                    "required": ["field_id"],
                },
                handler=self._calculate_water_balance,
                tags=["irrigation", "water_balance"],
            )
        )

        self.register_tool(
            AgentTool(
                name="optimize_irrigation_schedule",
                name_ar="تحسين جدول الري",
                description="Optimize irrigation schedule for water efficiency",
                description_ar="تحسين جدول الري لكفاءة المياه",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "crop_type": {"type": "string"},
                        "growth_stage": {"type": "string"},
                        "water_budget": {"type": "number"},
                    },
                    "required": ["field_id"],
                },
                handler=self._optimize_schedule,
                tags=["irrigation", "optimization"],
            )
        )

    def _register_default_capabilities(self) -> None:
        """Register irrigation capabilities."""
        self.register_capability(
            AgentCapability(
                name="irrigation_calculation",
                name_ar="حساب الري",
                description="Calculate irrigation requirements and scheduling",
                description_ar="حساب متطلبات الري والجدولة",
                domains=["irrigation", "water_management"],
                skill_level=0.9,
            )
        )

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """Decompose irrigation task."""
        field_id = context.get("field_id")

        return [
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Calculate evapotranspiration",
                description_ar="حساب التبخر-نتح",
                tool_name="calculate_et",
                tool_input={"field_id": field_id},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Calculate water balance",
                description_ar="حساب التوازن المائي",
                tool_name="calculate_water_balance",
                tool_input={"field_id": field_id},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=3,
                description="Optimize irrigation schedule",
                description_ar="تحسين جدول الري",
                tool_name="optimize_irrigation_schedule",
                tool_input={"field_id": field_id},
            ),
        ]

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate irrigation calculation results."""
        if not result.success:
            return False, f"Tool failed: {result.error}"

        data = result.result or {}

        if step.tool_name == "calculate_et":
            et = data.get("et_value", 0)
            if et < 0 or et > 15:  # Reasonable ET range mm/day
                return False, f"Unreasonable ET value: {et} mm/day"

        elif step.tool_name == "optimize_irrigation_schedule":
            water = data.get("recommended_amount_mm", 0)
            if water < 0 or water > 100:
                return False, f"Unreasonable irrigation amount: {water}mm"

        return True, None

    # Tool handlers
    async def _calculate_et(
        self,
        field_id: str,
        weather_data: dict[str, Any] | None = None,
        crop_coefficient: float = 1.0,
    ) -> dict[str, Any]:
        """Calculate evapotranspiration."""
        logger.info("calculating_et", field_id=field_id)

        # Simplified ET calculation
        et_reference = 5.5  # mm/day reference ET
        et_crop = et_reference * crop_coefficient

        return {
            "field_id": field_id,
            "et_reference": et_reference,
            "crop_coefficient": crop_coefficient,
            "et_value": et_crop,
            "unit": "mm/day",
            "calculation_method": "Penman-Monteith (simplified)",
        }

    async def _calculate_water_balance(
        self,
        field_id: str,
        soil_moisture: float | None = None,
        et_value: float | None = None,
        rainfall_mm: float = 0,
    ) -> dict[str, Any]:
        """Calculate soil water balance."""
        logger.info("calculating_water_balance", field_id=field_id)

        soil_moisture = soil_moisture or 38
        et_value = et_value or 5.5

        # Calculate deficit
        field_capacity = 50
        deficit = field_capacity - soil_moisture + et_value - rainfall_mm

        return {
            "field_id": field_id,
            "current_moisture": soil_moisture,
            "field_capacity": field_capacity,
            "et_loss": et_value,
            "rainfall_gain": rainfall_mm,
            "water_deficit_mm": max(0, deficit),
            "status": "deficit" if deficit > 10 else "adequate",
        }

    async def _optimize_schedule(
        self,
        field_id: str,
        crop_type: str | None = None,
        growth_stage: str | None = None,
        water_budget: float | None = None,
    ) -> dict[str, Any]:
        """Optimize irrigation schedule."""
        logger.info("optimizing_schedule", field_id=field_id)

        return {
            "field_id": field_id,
            "recommended_amount_mm": 25,
            "recommended_time": "06:00",
            "frequency_days": 3,
            "method": "drip",
            "efficiency_factor": 0.9,
            "reasoning": "Based on ET calculation and current soil moisture",
            "reasoning_ar": "بناءً على حساب التبخر-نتح ورطوبة التربة الحالية",
        }


class FertilizerSubAgent(BaseAutonomousAgent):
    """
    Specialized sub-agent for fertilizer recommendations.
    وكيل فرعي متخصص لتوصيات التسميد
    """

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        parent_agent: BaseAutonomousAgent | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            agent_id=kwargs.get("agent_id", "fertilizer-sub-agent"),
            name=kwargs.get("name", "Fertilizer Specialist"),
            name_ar=kwargs.get("name_ar", "متخصص التسميد"),
            description="Specialized agent for nutrient management and fertilizer recommendations",
            description_ar="وكيل متخصص في إدارة العناصر الغذائية وتوصيات التسميد",
            mode=AgentMode.EXECUTE,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            collaboration_role=CollaborationRole.SPECIALIST,
        )
        self.parent_agent = parent_agent

    def _register_default_tools(self) -> None:
        """Register fertilizer-specific tools."""
        self.register_tool(
            AgentTool(
                name="analyze_soil_nutrients",
                name_ar="تحليل مغذيات التربة",
                description="Analyze soil nutrient levels from test results",
                description_ar="تحليل مستويات مغذيات التربة من نتائج الاختبار",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "soil_test": {"type": "object"},
                    },
                    "required": ["field_id"],
                },
                handler=self._analyze_nutrients,
                tags=["fertilizer", "nutrients"],
            )
        )

        self.register_tool(
            AgentTool(
                name="calculate_nutrient_requirements",
                name_ar="حساب متطلبات العناصر الغذائية",
                description="Calculate crop nutrient requirements based on yield target",
                description_ar="حساب متطلبات العناصر الغذائية بناءً على هدف الإنتاج",
                input_schema={
                    "type": "object",
                    "properties": {
                        "crop_type": {"type": "string"},
                        "growth_stage": {"type": "string"},
                        "target_yield": {"type": "number"},
                        "area_ha": {"type": "number"},
                    },
                    "required": ["crop_type"],
                },
                handler=self._calculate_requirements,
                tags=["fertilizer", "calculation"],
            )
        )

        self.register_tool(
            AgentTool(
                name="recommend_fertilizer",
                name_ar="توصية السماد",
                description="Recommend specific fertilizer products and application rates",
                description_ar="توصية منتجات سماد محددة ومعدلات التطبيق",
                input_schema={
                    "type": "object",
                    "properties": {
                        "nutrient_deficit": {"type": "object"},
                        "crop_type": {"type": "string"},
                        "budget": {"type": "number"},
                    },
                    "required": ["nutrient_deficit"],
                },
                handler=self._recommend_fertilizer,
                tags=["fertilizer", "recommendation"],
            )
        )

    def _register_default_capabilities(self) -> None:
        """Register fertilizer capabilities."""
        self.register_capability(
            AgentCapability(
                name="fertilizer_recommendation",
                name_ar="توصية التسميد",
                description="Provide nutrient management and fertilizer recommendations",
                description_ar="تقديم إدارة العناصر الغذائية وتوصيات التسميد",
                domains=["fertilizer", "nutrition"],
                skill_level=0.9,
            )
        )

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """Decompose fertilizer task."""
        field_id = context.get("field_id")
        crop_type = context.get("crop_type", "wheat")

        return [
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Analyze soil nutrients",
                description_ar="تحليل مغذيات التربة",
                tool_name="analyze_soil_nutrients",
                tool_input={"field_id": field_id},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Calculate nutrient requirements",
                description_ar="حساب متطلبات العناصر الغذائية",
                tool_name="calculate_nutrient_requirements",
                tool_input={"crop_type": crop_type},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=3,
                description="Recommend fertilizer products",
                description_ar="توصية منتجات السماد",
                tool_name="recommend_fertilizer",
                tool_input={"crop_type": crop_type},
            ),
        ]

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate fertilizer calculation results."""
        if not result.success:
            return False, f"Tool failed: {result.error}"
        return True, None

    async def _analyze_nutrients(
        self,
        field_id: str,
        soil_test: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze soil nutrient levels."""
        logger.info("analyzing_nutrients", field_id=field_id)

        soil_test = soil_test or {"nitrogen": 18, "phosphorus": 25, "potassium": 150}

        return {
            "field_id": field_id,
            "nitrogen": {"value": soil_test.get("nitrogen", 18), "status": "low", "target": 25},
            "phosphorus": {
                "value": soil_test.get("phosphorus", 25),
                "status": "adequate",
                "target": 20,
            },
            "potassium": {
                "value": soil_test.get("potassium", 150),
                "status": "adequate",
                "target": 120,
            },
            "deficiencies": ["nitrogen"],
        }

    async def _calculate_requirements(
        self,
        crop_type: str,
        growth_stage: str | None = None,
        target_yield: float = 5.0,
        area_ha: float = 1.0,
    ) -> dict[str, Any]:
        """Calculate nutrient requirements."""
        logger.info("calculating_requirements", crop_type=crop_type)

        # Simplified nutrient requirements per ton of yield
        nutrient_per_ton = {"wheat": {"N": 25, "P": 5, "K": 15}}
        req = nutrient_per_ton.get(crop_type, {"N": 20, "P": 4, "K": 10})

        return {
            "crop_type": crop_type,
            "target_yield_t_ha": target_yield,
            "nitrogen_kg_ha": req["N"] * target_yield,
            "phosphorus_kg_ha": req["P"] * target_yield,
            "potassium_kg_ha": req["K"] * target_yield,
            "total_for_area": {
                "N": req["N"] * target_yield * area_ha,
                "P": req["P"] * target_yield * area_ha,
                "K": req["K"] * target_yield * area_ha,
            },
        }

    async def _recommend_fertilizer(
        self,
        nutrient_deficit: dict[str, Any] | None = None,
        crop_type: str | None = None,
        budget: float | None = None,
    ) -> dict[str, Any]:
        """Recommend fertilizer products."""
        logger.info("recommending_fertilizer")

        return {
            "recommendations": [
                {
                    "product": "Urea 46%",
                    "product_ar": "يوريا 46%",
                    "rate_kg_ha": 46,
                    "timing": "Now - tillering stage",
                    "timing_ar": "الآن - مرحلة التفريع",
                    "method": "Broadcast with morning dew",
                    "method_ar": "نثر مع ندى الصباح",
                    "cost_sar": 115,
                },
            ],
            "total_cost_sar": 115,
            "expected_roi_percent": 1025,
        }


class PestControlSubAgent(BaseAutonomousAgent):
    """
    Specialized sub-agent for pest and disease management.
    وكيل فرعي متخصص لإدارة الآفات والأمراض
    """

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        parent_agent: BaseAutonomousAgent | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            agent_id=kwargs.get("agent_id", "pest-control-sub-agent"),
            name=kwargs.get("name", "Pest Control Specialist"),
            name_ar=kwargs.get("name_ar", "متخصص مكافحة الآفات"),
            description="Specialized agent for integrated pest management",
            description_ar="وكيل متخصص في الإدارة المتكاملة للآفات",
            mode=AgentMode.EXECUTE,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            collaboration_role=CollaborationRole.SPECIALIST,
        )
        self.parent_agent = parent_agent

    def _register_default_tools(self) -> None:
        """Register pest control tools."""
        self.register_tool(
            AgentTool(
                name="identify_pest",
                name_ar="تحديد الآفة",
                description="Identify pest or disease from symptoms",
                description_ar="تحديد الآفة أو المرض من الأعراض",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symptoms": {"type": "array", "items": {"type": "string"}},
                        "crop_type": {"type": "string"},
                        "image_url": {"type": "string"},
                    },
                    "required": ["symptoms"],
                },
                handler=self._identify_pest,
                tags=["pest", "identification"],
            )
        )

        self.register_tool(
            AgentTool(
                name="assess_infestation_level",
                name_ar="تقييم مستوى الإصابة",
                description="Assess the severity of pest/disease infestation",
                description_ar="تقييم شدة إصابة الآفة/المرض",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pest_id": {"type": "string"},
                        "affected_area_percent": {"type": "number"},
                        "population_density": {"type": "number"},
                    },
                    "required": ["pest_id"],
                },
                handler=self._assess_infestation,
                tags=["pest", "assessment"],
            )
        )

        self.register_tool(
            AgentTool(
                name="recommend_treatment",
                name_ar="توصية العلاج",
                description="Recommend IPM treatment strategy",
                description_ar="توصية استراتيجية المكافحة المتكاملة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pest_id": {"type": "string"},
                        "severity": {"type": "string"},
                        "crop_type": {"type": "string"},
                        "organic_only": {"type": "boolean"},
                    },
                    "required": ["pest_id", "severity"],
                },
                handler=self._recommend_treatment,
                tags=["pest", "treatment"],
            )
        )

    def _register_default_capabilities(self) -> None:
        """Register pest control capabilities."""
        self.register_capability(
            AgentCapability(
                name="pest_management",
                name_ar="إدارة الآفات",
                description="Identify and manage pests and diseases",
                description_ar="تحديد وإدارة الآفات والأمراض",
                domains=["pest_control", "disease_management", "ipm"],
                skill_level=0.85,
            )
        )

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """Decompose pest control task."""
        return [
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Identify pest/disease",
                description_ar="تحديد الآفة/المرض",
                tool_name="identify_pest",
                tool_input={
                    "symptoms": context.get("symptoms", []),
                    "crop_type": context.get("crop_type"),
                },
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Assess infestation level",
                description_ar="تقييم مستوى الإصابة",
                tool_name="assess_infestation_level",
                tool_input={"pest_id": "pending"},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=3,
                description="Recommend treatment",
                description_ar="توصية العلاج",
                tool_name="recommend_treatment",
                tool_input={"pest_id": "pending", "severity": "pending"},
            ),
        ]

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate pest control results."""
        if not result.success:
            return False, f"Tool failed: {result.error}"
        return True, None

    async def _identify_pest(
        self,
        symptoms: list[str],
        crop_type: str | None = None,
        image_url: str | None = None,
    ) -> dict[str, Any]:
        """Identify pest from symptoms."""
        logger.info("identifying_pest", symptoms=symptoms)

        symptom_text = " ".join(symptoms).lower()

        # Simplified identification
        if "yellow" in symptom_text or "اصفرار" in symptom_text:
            return {
                "pest_id": "nitrogen_deficiency",
                "type": "nutrient_deficiency",
                "name": "Nitrogen Deficiency",
                "name_ar": "نقص النيتروجين",
                "confidence": 0.85,
            }
        elif "spots" in symptom_text or "بقع" in symptom_text:
            return {
                "pest_id": "leaf_rust",
                "type": "disease",
                "name": "Leaf Rust",
                "name_ar": "صدأ الأوراق",
                "confidence": 0.75,
            }
        elif "weevil" in symptom_text or "سوسة" in symptom_text:
            return {
                "pest_id": "red_palm_weevil",
                "type": "pest",
                "name": "Red Palm Weevil",
                "name_ar": "سوسة النخيل الحمراء",
                "confidence": 0.90,
                "critical": True,
            }

        return {
            "pest_id": "unknown",
            "type": "unknown",
            "name": "Unknown issue",
            "confidence": 0.3,
            "recommendation": "Consult agronomist",
        }

    async def _assess_infestation(
        self,
        pest_id: str,
        affected_area_percent: float = 10,
        population_density: float | None = None,
    ) -> dict[str, Any]:
        """Assess infestation severity."""
        logger.info("assessing_infestation", pest_id=pest_id)

        if affected_area_percent < 5:
            severity = "low"
            severity_ar = "منخفض"
        elif affected_area_percent < 20:
            severity = "medium"
            severity_ar = "متوسط"
        else:
            severity = "high"
            severity_ar = "مرتفع"

        return {
            "pest_id": pest_id,
            "affected_area_percent": affected_area_percent,
            "severity": severity,
            "severity_ar": severity_ar,
            "economic_threshold_reached": affected_area_percent > 10,
        }

    async def _recommend_treatment(
        self,
        pest_id: str,
        severity: str,
        crop_type: str | None = None,
        organic_only: bool = False,
    ) -> dict[str, Any]:
        """Recommend treatment strategy."""
        logger.info("recommending_treatment", pest_id=pest_id, severity=severity)

        if pest_id == "red_palm_weevil":
            return {
                "pest_id": pest_id,
                "urgency": "critical",
                "urgency_ar": "حرج",
                "treatments": [
                    {
                        "method": "Chemical injection",
                        "method_ar": "الحقن الكيميائي",
                        "product": "Emamectin benzoate 5%",
                        "rate": "50-100ml per injection point",
                        "timing": "Within 24-48 hours",
                    }
                ],
                "preventive_measures": ["Pheromone traps", "Regular inspection"],
            }

        return {
            "pest_id": pest_id,
            "urgency": severity,
            "treatments": [
                {
                    "method": "Fungicide application" if pest_id == "leaf_rust" else "Cultural control",
                    "product": "Propiconazole" if pest_id == "leaf_rust" else "N/A",
                }
            ],
        }


class HarvestPlannerSubAgent(BaseAutonomousAgent):
    """
    Specialized sub-agent for harvest planning.
    وكيل فرعي متخصص لتخطيط الحصاد
    """

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        parent_agent: BaseAutonomousAgent | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            agent_id=kwargs.get("agent_id", "harvest-planner-sub-agent"),
            name=kwargs.get("name", "Harvest Planning Specialist"),
            name_ar=kwargs.get("name_ar", "متخصص تخطيط الحصاد"),
            description="Specialized agent for harvest timing and logistics",
            description_ar="وكيل متخصص في توقيت الحصاد والخدمات اللوجستية",
            mode=AgentMode.EXECUTE,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            collaboration_role=CollaborationRole.SPECIALIST,
        )
        self.parent_agent = parent_agent

    def _register_default_tools(self) -> None:
        """Register harvest planning tools."""
        self.register_tool(
            AgentTool(
                name="assess_crop_maturity",
                name_ar="تقييم نضج المحصول",
                description="Assess crop maturity for harvest readiness",
                description_ar="تقييم نضج المحصول للاستعداد للحصاد",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "crop_type": {"type": "string"},
                        "planted_date": {"type": "string"},
                    },
                    "required": ["field_id", "crop_type"],
                },
                handler=self._assess_maturity,
                tags=["harvest", "maturity"],
            )
        )

        self.register_tool(
            AgentTool(
                name="calculate_optimal_harvest_window",
                name_ar="حساب نافذة الحصاد المثلى",
                description="Calculate optimal harvest timing window",
                description_ar="حساب نافذة توقيت الحصاد المثلى",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "maturity_data": {"type": "object"},
                        "weather_forecast": {"type": "object"},
                    },
                    "required": ["field_id"],
                },
                handler=self._calculate_window,
                tags=["harvest", "timing"],
            )
        )

        self.register_tool(
            AgentTool(
                name="plan_harvest_logistics",
                name_ar="تخطيط لوجستيات الحصاد",
                description="Plan harvest equipment and labor logistics",
                description_ar="تخطيط معدات الحصاد والعمالة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "area_ha": {"type": "number"},
                        "harvest_date": {"type": "string"},
                        "equipment_available": {"type": "array"},
                    },
                    "required": ["field_id"],
                },
                handler=self._plan_logistics,
                tags=["harvest", "logistics"],
            )
        )

    def _register_default_capabilities(self) -> None:
        """Register harvest planning capabilities."""
        self.register_capability(
            AgentCapability(
                name="harvest_planning",
                name_ar="تخطيط الحصاد",
                description="Plan harvest timing and logistics",
                description_ar="تخطيط توقيت الحصاد والخدمات اللوجستية",
                domains=["harvest", "logistics", "yield"],
                skill_level=0.85,
            )
        )

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """Decompose harvest planning task."""
        field_id = context.get("field_id")
        crop_type = context.get("crop_type", "wheat")

        return [
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Assess crop maturity",
                description_ar="تقييم نضج المحصول",
                tool_name="assess_crop_maturity",
                tool_input={"field_id": field_id, "crop_type": crop_type},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Calculate harvest window",
                description_ar="حساب نافذة الحصاد",
                tool_name="calculate_optimal_harvest_window",
                tool_input={"field_id": field_id},
            ),
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=3,
                description="Plan harvest logistics",
                description_ar="تخطيط لوجستيات الحصاد",
                tool_name="plan_harvest_logistics",
                tool_input={"field_id": field_id},
            ),
        ]

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate harvest planning results."""
        if not result.success:
            return False, f"Tool failed: {result.error}"
        return True, None

    async def _assess_maturity(
        self,
        field_id: str,
        crop_type: str,
        planted_date: str | None = None,
    ) -> dict[str, Any]:
        """Assess crop maturity."""
        logger.info("assessing_maturity", field_id=field_id, crop_type=crop_type)

        return {
            "field_id": field_id,
            "crop_type": crop_type,
            "maturity_percent": 85,
            "days_to_maturity": 10,
            "moisture_content_percent": 14,
            "ready_for_harvest": False,
            "recommendation": "Wait 7-10 days for optimal maturity",
            "recommendation_ar": "انتظر 7-10 أيام للنضج الأمثل",
        }

    async def _calculate_window(
        self,
        field_id: str,
        maturity_data: dict[str, Any] | None = None,
        weather_forecast: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Calculate optimal harvest window."""
        logger.info("calculating_harvest_window", field_id=field_id)

        return {
            "field_id": field_id,
            "optimal_window": {
                "start": "2026-05-01",
                "end": "2026-05-07",
            },
            "confidence": 0.85,
            "weather_risk": "low",
            "conditions": "Clear skies expected, low humidity",
            "conditions_ar": "سماء صافية متوقعة، رطوبة منخفضة",
        }

    async def _plan_logistics(
        self,
        field_id: str,
        area_ha: float = 8.5,
        harvest_date: str | None = None,
        equipment_available: list[str] | None = None,
    ) -> dict[str, Any]:
        """Plan harvest logistics."""
        logger.info("planning_logistics", field_id=field_id)

        return {
            "field_id": field_id,
            "area_ha": area_ha,
            "estimated_duration_hours": area_ha * 2,
            "equipment_required": ["combine_harvester", "grain_cart", "transport_truck"],
            "labor_required": 4,
            "storage_capacity_needed_tons": area_ha * 4.5,
            "estimated_yield_tons": area_ha * 4.5,
            "cost_estimate_sar": area_ha * 500,
        }


class FarmAdvisorAgent(BaseAutonomousAgent):
    """
    Bilingual Farm Advisor Agent.
    وكيل مستشار المزرعة ثنائي اللغة

    Inspired by OpenCode's dual-agent pattern:
    - PLAN mode: Analyze situation, create recommendations (read-only)
    - EXECUTE mode: Implement recommendations (with approval)

    Example:
        # Plan mode - get advice without executing
        advisor = FarmAdvisorAgent(mode=AgentMode.PLAN)
        plan = await advisor.run(
            task="متى يجب أن أسقي القمح؟",
            context={"farm_id": "FARM-001", "field_id": "F003"}
        )

        # Execute mode - implement the plan
        advisor = FarmAdvisorAgent(mode=AgentMode.EXECUTE)
        result = await advisor.run(
            task="Apply irrigation schedule to field F003",
            context={"farm_id": "FARM-001", "field_id": "F003"}
        )
    """

    # Advisory thresholds
    IRRIGATION_MOISTURE_LOW = 30  # %
    IRRIGATION_MOISTURE_HIGH = 60  # %
    NDVI_HEALTHY_MIN = 0.6
    FERTILIZER_N_THRESHOLD = 25  # ppm

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        mode: AgentMode = AgentMode.HYBRID,
        preferred_language: str = "ar",
        enable_sub_agents: bool = True,
    ):
        """
        Initialize Farm Advisor Agent.
        تهيئة وكيل مستشار المزرعة

        Args:
            tenant_id: Tenant ID for multi-tenancy
            llm_manager: LLM provider manager
            mode: Operation mode (plan/execute/hybrid)
            preferred_language: Preferred language (ar/en)
            enable_sub_agents: Whether to spawn specialized sub-agents
        """
        super().__init__(
            agent_id="farm-advisor-agent",
            name="Farm Advisor Agent",
            name_ar="وكيل مستشار المزرعة",
            description="Bilingual agricultural advisor for farmers",
            description_ar="مستشار زراعي ثنائي اللغة للمزارعين",
            mode=mode,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            collaboration_role=CollaborationRole.COORDINATOR,
        )

        self.preferred_language = preferred_language
        self.farm_context: FarmContext | None = None
        self.conversation_history: list[dict[str, str]] = []

        # === NEW: Sub-agent management ===
        self.enable_sub_agents = enable_sub_agents
        self._irrigation_agent: IrrigationSubAgent | None = None
        self._fertilizer_agent: FertilizerSubAgent | None = None
        self._pest_agent: PestControlSubAgent | None = None
        self._harvest_agent: HarvestPlannerSubAgent | None = None

        # === NEW: Collaborative decision state ===
        self.pending_decisions: dict[str, CollaborativeDecision] = {}
        self.decision_history: list[CollaborativeDecision] = []

        # === NEW: Farmer feedback tracking ===
        self.farmer_satisfaction_scores: list[float] = []
        self.recommendation_outcomes: dict[str, dict[str, Any]] = {}

    def _register_default_tools(self) -> None:
        """Register advisory tools."""

        # Tool 1: Get Field Status
        self.register_tool(
            AgentTool(
                name="get_field_status",
                name_ar="الحصول على حالة الحقل",
                description="Get current status of a field (health, moisture, etc.)",
                description_ar="الحصول على الحالة الحالية للحقل (الصحة، الرطوبة، إلخ)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "include_history": {"type": "boolean", "default": False},
                    },
                    "required": ["field_id"],
                },
                handler=self._get_field_status,
                tags=["status", "monitoring"],
            )
        )

        # Tool 2: Calculate Irrigation Need
        self.register_tool(
            AgentTool(
                name="calculate_irrigation_need",
                name_ar="حساب احتياج الري",
                description="Calculate irrigation requirements based on conditions",
                description_ar="حساب متطلبات الري بناءً على الظروف",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "crop_type": {"type": "string"},
                        "soil_moisture": {"type": "number"},
                        "weather_forecast": {"type": "object"},
                        "growth_stage": {"type": "string"},
                    },
                    "required": ["field_id"],
                },
                handler=self._calculate_irrigation_need,
                tags=["irrigation", "calculation"],
            )
        )

        # Tool 3: Calculate Fertilizer Need
        self.register_tool(
            AgentTool(
                name="calculate_fertilizer_need",
                name_ar="حساب احتياج السماد",
                description="Calculate fertilizer requirements based on soil test",
                description_ar="حساب متطلبات السماد بناءً على تحليل التربة",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "crop_type": {"type": "string"},
                        "soil_test": {"type": "object"},
                        "target_yield": {"type": "number"},
                    },
                    "required": ["field_id"],
                },
                handler=self._calculate_fertilizer_need,
                tags=["fertilizer", "calculation"],
            )
        )

        # Tool 4: Diagnose Crop Issue
        self.register_tool(
            AgentTool(
                name="diagnose_crop_issue",
                name_ar="تشخيص مشكلة المحصول",
                description="Diagnose crop health issues based on symptoms",
                description_ar="تشخيص مشاكل صحة المحصول بناءً على الأعراض",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "crop_type": {"type": "string"},
                        "symptoms": {"type": "array", "items": {"type": "string"}},
                        "image_url": {"type": "string"},
                    },
                    "required": ["crop_type", "symptoms"],
                },
                handler=self._diagnose_crop_issue,
                tags=["diagnosis", "health"],
            )
        )

        # Tool 5: Create Task (Execute mode only)
        self.register_tool(
            AgentTool(
                name="create_task",
                name_ar="إنشاء مهمة",
                description="Create a farm task for execution",
                description_ar="إنشاء مهمة مزرعة للتنفيذ",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "task_type": {
                            "type": "string",
                            "enum": ["irrigation", "fertilizer", "spray", "harvest", "inspection"],
                        },
                        "description": {"type": "string"},
                        "scheduled_date": {"type": "string", "format": "date"},
                        "priority": {"type": "string", "enum": ["urgent", "high", "medium", "low"]},
                        "parameters": {"type": "object"},
                    },
                    "required": ["field_id", "task_type", "description"],
                },
                handler=self._create_task,
                requires_approval=True,
                is_destructive=False,
                tags=["task", "execution"],
            )
        )

        # Tool 6: Schedule Irrigation (Execute mode only)
        self.register_tool(
            AgentTool(
                name="schedule_irrigation",
                name_ar="جدولة الري",
                description="Schedule irrigation for a field",
                description_ar="جدولة الري للحقل",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "water_amount_mm": {"type": "number"},
                        "scheduled_time": {"type": "string", "format": "date-time"},
                        "duration_minutes": {"type": "integer"},
                        "method": {
                            "type": "string",
                            "enum": ["drip", "sprinkler", "flood", "pivot"],
                        },
                    },
                    "required": ["field_id", "water_amount_mm"],
                },
                handler=self._schedule_irrigation,
                requires_approval=True,
                is_destructive=False,
                tags=["irrigation", "scheduling"],
            )
        )

        # Tool 7: Generate Advisory Report
        self.register_tool(
            AgentTool(
                name="generate_advisory_report",
                name_ar="توليد تقرير استشاري",
                description="Generate a comprehensive advisory report",
                description_ar="توليد تقرير استشاري شامل",
                input_schema={
                    "type": "object",
                    "properties": {
                        "farm_id": {"type": "string"},
                        "field_ids": {"type": "array", "items": {"type": "string"}},
                        "report_type": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly", "seasonal"],
                        },
                        "include_recommendations": {"type": "boolean", "default": True},
                    },
                    "required": ["farm_id"],
                },
                handler=self._generate_advisory_report,
                tags=["report", "advisory"],
            )
        )

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """
        Decompose advisory task using LLM.
        تقسيم مهمة الاستشارة باستخدام نموذج اللغة
        """
        field_id = context.get("field_id")
        farm_id = context.get("farm_id")
        crop_type = context.get("crop_type", "unknown")

        # Detect language and intent
        is_arabic = any(ord(c) > 0x600 and ord(c) < 0x6FF for c in task)

        system_prompt = """أنت مستشار زراعي خبير. قم بتحليل سؤال المزارع وإنشاء خطة استشارية.

You are an expert agricultural advisor. Analyze the farmer's question and create an advisory plan.

Based on the question type, use these tools:
- Irrigation questions: get_field_status → calculate_irrigation_need → generate_advisory_report
- Fertilizer questions: get_field_status → calculate_fertilizer_need → generate_advisory_report
- Crop health/disease: get_field_status → diagnose_crop_issue → generate_advisory_report
- General status: get_field_status → generate_advisory_report

For EXECUTE mode, add: create_task or schedule_irrigation at the end.

Return JSON array of steps with: description, description_ar, tool_name, tool_input"""

        safe_task = escape_prompt_input(task)

        prompt = f"""Question: {safe_task}
Farm ID: {farm_id}
Field ID: {field_id}
Crop: {crop_type}
Mode: {self.mode.value}
Language detected: {"Arabic" if is_arabic else "English"}

Create an advisory plan as JSON array."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
            )

            steps = self._parse_advisory_plan(response.text, field_id, farm_id)

            if not steps:
                steps = self._create_default_advisory_steps(task, field_id, farm_id, is_arabic)

            return steps

        except Exception as e:
            logger.warning("llm_advisory_planning_failed", error=str(e))
            return self._create_default_advisory_steps(task, field_id, farm_id, is_arabic)

    def _parse_advisory_plan(
        self,
        llm_response: str,
        field_id: str | None,
        farm_id: str | None,
    ) -> list[AgentStep]:
        """Parse LLM response into advisory steps."""
        import json

        try:
            start = llm_response.find("[")
            end = llm_response.rfind("]") + 1

            if start >= 0 and end > start:
                json_str = llm_response[start:end]
                plan_data = json.loads(json_str)

                steps = []
                for i, item in enumerate(plan_data):
                    # Ensure tool_input has field_id and farm_id
                    tool_input = item.get("tool_input", {})
                    if field_id and "field_id" not in tool_input:
                        tool_input["field_id"] = field_id
                    if farm_id and "farm_id" not in tool_input:
                        tool_input["farm_id"] = farm_id

                    steps.append(
                        AgentStep(
                            step_id=str(uuid.uuid4()),
                            step_number=i + 1,
                            description=item.get("description", f"Step {i + 1}"),
                            description_ar=item.get("description_ar", f"الخطوة {i + 1}"),
                            tool_name=item.get("tool_name"),
                            tool_input=tool_input,
                        )
                    )

                return steps

        except json.JSONDecodeError:
            pass

        return []

    def _create_default_advisory_steps(
        self,
        task: str,
        field_id: str | None,
        farm_id: str | None,
        is_arabic: bool,
    ) -> list[AgentStep]:
        """Create default advisory workflow."""
        task_lower = task.lower()

        # Detect question type
        is_irrigation = any(w in task_lower for w in ["water", "irrigation", "ري", "سقي", "ماء"])
        is_fertilizer = any(w in task_lower for w in ["fertilizer", "nutrient", "سماد", "تسميد", "نيتروجين"])
        is_disease = any(w in task_lower for w in ["disease", "pest", "yellow", "مرض", "آفة", "اصفرار"])

        steps = [
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Get current field status",
                description_ar="الحصول على حالة الحقل الحالية",
                tool_name="get_field_status",
                tool_input={"field_id": field_id, "include_history": True},
            ),
        ]

        if is_irrigation:
            steps.append(
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=2,
                    description="Calculate irrigation requirements",
                    description_ar="حساب متطلبات الري",
                    tool_name="calculate_irrigation_need",
                    tool_input={"field_id": field_id},
                )
            )
        elif is_fertilizer:
            steps.append(
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=2,
                    description="Calculate fertilizer requirements",
                    description_ar="حساب متطلبات السماد",
                    tool_name="calculate_fertilizer_need",
                    tool_input={"field_id": field_id},
                )
            )
        elif is_disease:
            steps.append(
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=2,
                    description="Diagnose crop issue",
                    description_ar="تشخيص مشكلة المحصول",
                    tool_name="diagnose_crop_issue",
                    tool_input={"field_id": field_id, "symptoms": [], "crop_type": "wheat"},
                )
            )

        # Add report generation
        steps.append(
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=len(steps) + 1,
                description="Generate advisory report",
                description_ar="توليد تقرير استشاري",
                tool_name="generate_advisory_report",
                tool_input={"farm_id": farm_id, "field_ids": [field_id] if field_id else []},
            )
        )

        # In execute mode, add action step
        if self.mode == AgentMode.EXECUTE and is_irrigation:
            steps.append(
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=len(steps) + 1,
                    description="Schedule irrigation based on analysis",
                    description_ar="جدولة الري بناءً على التحليل",
                    tool_name="schedule_irrigation",
                    tool_input={"field_id": field_id},
                )
            )

        return steps

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate advisory step result."""
        if not result.success:
            return False, f"Tool {step.tool_name} failed: {result.error}"

        tool_name = step.tool_name

        if tool_name == "get_field_status":
            data = result.result or {}
            if not data.get("field_id"):
                return False, "Field not found"
            return True, None

        elif tool_name == "calculate_irrigation_need":
            data = result.result or {}
            water_amount = data.get("recommended_amount_mm", 0)
            if water_amount < 0 or water_amount > 100:
                return False, f"Unreasonable irrigation amount: {water_amount}mm"
            return True, None

        elif tool_name == "schedule_irrigation":
            # Validate in execute mode
            if self.mode == AgentMode.PLAN:
                return False, "Cannot schedule irrigation in PLAN mode"
            return True, None

        return True, None

    # Tool handlers
    async def _get_field_status(
        self,
        field_id: str,
        include_history: bool = False,
    ) -> dict[str, Any]:
        """Get field status from field-management-service."""
        logger.info("getting_field_status", field_id=field_id)

        return {
            "field_id": field_id,
            "name": "North Field",
            "name_ar": "الحقل الشمالي",
            "area_ha": 8.5,
            "crop": {
                "type": "wheat",
                "type_ar": "قمح",
                "variety": "Sakha 95",
                "growth_stage": "tillering",
                "growth_stage_ar": "التفريع",
                "planted_date": "2025-11-15",
            },
            "status": {
                "health_score": 75,
                "ndvi": 0.68,
                "soil_moisture": 38,
                "last_irrigation": "2026-01-18",
                "days_since_irrigation": 3,
            },
            "alerts": [],
        }

    async def _calculate_irrigation_need(
        self,
        field_id: str,
        crop_type: str | None = None,
        soil_moisture: float | None = None,
        weather_forecast: dict[str, Any] | None = None,
        growth_stage: str | None = None,
    ) -> dict[str, Any]:
        """Calculate irrigation requirements."""
        logger.info("calculating_irrigation", field_id=field_id)

        # Get current moisture if not provided
        soil_moisture = soil_moisture or 38

        # Calculate based on thresholds
        if soil_moisture < self.IRRIGATION_MOISTURE_LOW:
            urgency = "urgent"
            urgency_ar = "عاجل"
            recommended_mm = 30
        elif soil_moisture < 45:
            urgency = "soon"
            urgency_ar = "قريباً"
            recommended_mm = 25
        else:
            urgency = "not_needed"
            urgency_ar = "غير مطلوب"
            recommended_mm = 0

        return {
            "field_id": field_id,
            "current_moisture": soil_moisture,
            "target_moisture": 50,
            "recommended_amount_mm": recommended_mm,
            "urgency": urgency,
            "urgency_ar": urgency_ar,
            "optimal_time": "06:00",
            "optimal_time_reason": "Early morning to minimize evaporation",
            "optimal_time_reason_ar": "الصباح الباكر لتقليل التبخر",
            "considerations": {
                "weather": "No rain expected in next 72 hours",
                "weather_ar": "لا يتوقع هطول أمطار خلال 72 ساعة",
            },
        }

    async def _calculate_fertilizer_need(
        self,
        field_id: str,
        crop_type: str | None = None,
        soil_test: dict[str, Any] | None = None,
        target_yield: float | None = None,
    ) -> dict[str, Any]:
        """Calculate fertilizer requirements."""
        logger.info("calculating_fertilizer", field_id=field_id)

        # Simulated soil test
        soil_test = soil_test or {"nitrogen": 18, "phosphorus": 25, "potassium": 150}

        n_deficit = max(0, self.FERTILIZER_N_THRESHOLD - soil_test.get("nitrogen", 0))

        recommendations = []
        if n_deficit > 0:
            urea_kg = n_deficit * 2  # Simplified calculation
            recommendations.append(
                {
                    "fertilizer": "Urea 46%",
                    "fertilizer_ar": "يوريا 46%",
                    "rate_kg_ha": urea_kg,
                    "timing": "Now - tillering stage",
                    "timing_ar": "الآن - مرحلة التفريع",
                    "method": "Broadcast with dew",
                    "method_ar": "نثر مع الندى",
                }
            )

        return {
            "field_id": field_id,
            "soil_test": soil_test,
            "deficiencies": {
                "nitrogen": n_deficit > 0,
                "phosphorus": False,
                "potassium": False,
            },
            "recommendations": recommendations,
            "total_cost_estimate": 115,  # SAR
            "expected_roi": "1025%",
        }

    async def _diagnose_crop_issue(
        self,
        crop_type: str,
        symptoms: list[str],
        field_id: str | None = None,
        image_url: str | None = None,
    ) -> dict[str, Any]:
        """Diagnose crop health issues."""
        logger.info("diagnosing_crop_issue", crop_type=crop_type, symptoms=symptoms)

        # Simplified diagnosis
        diagnoses = []

        symptom_text = " ".join(symptoms).lower()

        if "yellow" in symptom_text or "اصفرار" in symptom_text:
            diagnoses.append(
                {
                    "condition": "Nitrogen Deficiency",
                    "condition_ar": "نقص النيتروجين",
                    "confidence": 0.85,
                    "symptoms_matched": ["yellowing leaves", "stunted growth"],
                    "treatment": "Apply Urea 46% at 46 kg/ha",
                    "treatment_ar": "تطبيق يوريا 46% بمعدل 46 كجم/هكتار",
                }
            )

        if "spots" in symptom_text or "بقع" in symptom_text:
            diagnoses.append(
                {
                    "condition": "Leaf Rust",
                    "condition_ar": "صدأ الأوراق",
                    "confidence": 0.70,
                    "symptoms_matched": ["brown spots", "pustules"],
                    "treatment": "Apply fungicide (Propiconazole)",
                    "treatment_ar": "تطبيق مبيد فطري (بروبيكونازول)",
                }
            )

        return {
            "field_id": field_id,
            "crop_type": crop_type,
            "symptoms_reported": symptoms,
            "diagnoses": diagnoses,
            "recommended_action": diagnoses[0]["treatment"] if diagnoses else "Consult agronomist",
        }

    async def _create_task(
        self,
        field_id: str,
        task_type: str,
        description: str,
        scheduled_date: str | None = None,
        priority: str = "medium",
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a farm task."""
        if self.mode == AgentMode.PLAN:
            return {
                "status": "simulated",
                "message": "Task would be created in EXECUTE mode",
                "task_preview": {
                    "field_id": field_id,
                    "task_type": task_type,
                    "description": description,
                },
            }

        logger.info("creating_task", field_id=field_id, task_type=task_type)

        return {
            "task_id": str(uuid.uuid4()),
            "status": "created",
            "field_id": field_id,
            "task_type": task_type,
            "description": description,
            "scheduled_date": scheduled_date or datetime.now(UTC).strftime("%Y-%m-%d"),
            "priority": priority,
        }

    async def _schedule_irrigation(
        self,
        field_id: str,
        water_amount_mm: float,
        scheduled_time: str | None = None,
        duration_minutes: int | None = None,
        method: str = "drip",
    ) -> dict[str, Any]:
        """Schedule irrigation."""
        if self.mode == AgentMode.PLAN:
            return {
                "status": "simulated",
                "message": "Irrigation would be scheduled in EXECUTE mode",
                "preview": {
                    "field_id": field_id,
                    "water_amount_mm": water_amount_mm,
                    "method": method,
                },
            }

        logger.info("scheduling_irrigation", field_id=field_id, amount=water_amount_mm)

        return {
            "schedule_id": str(uuid.uuid4()),
            "status": "scheduled",
            "field_id": field_id,
            "water_amount_mm": water_amount_mm,
            "scheduled_time": scheduled_time or "06:00",
            "duration_minutes": duration_minutes or 60,
            "method": method,
            "message": "Irrigation scheduled successfully",
            "message_ar": "تم جدولة الري بنجاح",
        }

    async def _generate_advisory_report(
        self,
        farm_id: str,
        field_ids: list[str] | None = None,
        report_type: str = "daily",
        include_recommendations: bool = True,
    ) -> dict[str, Any]:
        """Generate comprehensive advisory report."""
        logger.info("generating_report", farm_id=farm_id)

        # Gather all gathered data from steps
        getattr(self, "_gathered_data", {})

        report = {
            "report_id": str(uuid.uuid4()),
            "farm_id": farm_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "type": report_type,
            "summary": {
                "en": "Farm status is good. Minor irrigation needed for Field F003.",
                "ar": "حالة المزرعة جيدة. يحتاج الحقل F003 إلى ري بسيط.",
            },
            "fields_analyzed": field_ids or [],
            "recommendations": [],
            "alerts": [],
        }

        if include_recommendations:
            report["recommendations"] = [
                {
                    "priority": "high",
                    "category": "irrigation",
                    "action": "Apply 25mm irrigation to F003 within 48 hours",
                    "action_ar": "تطبيق 25 ملم ري للحقل F003 خلال 48 ساعة",
                    "reasoning": "Soil moisture at 38%, below optimal 50%",
                    "reasoning_ar": "رطوبة التربة 38%، أقل من المثالي 50%",
                },
            ]

        return report

    def _generate_summary(self, outputs: list[dict[str, Any]]) -> str:
        """Generate bilingual advisory summary."""
        report = None
        for out in outputs:
            if out.get("step") == "Generate advisory report":
                report = out.get("output", {})
                break

        if report and "summary" in report:
            summary = report["summary"]
            return f"""
## Advisory Summary | ملخص الاستشارة

**English:** {summary.get("en", "N/A")}

**العربية:** {summary.get("ar", "غير متوفر")}

---
Mode: {self.mode.value} | الوضع: {"تخطيط" if self.mode == AgentMode.PLAN else "تنفيذ"}
"""

        return "Advisory analysis completed. | اكتمل التحليل الاستشاري."

    # ========================================
    # SUB-AGENT MANAGEMENT
    # إدارة الوكلاء الفرعيين
    # ========================================

    def _register_default_capabilities(self) -> None:
        """Register advisor capabilities."""
        self.register_capability(
            AgentCapability(
                name="general_advisory",
                name_ar="الاستشارة العامة",
                description="Provide general agricultural advisory",
                description_ar="تقديم استشارات زراعية عامة",
                domains=["advisory", "farming"],
                skill_level=0.85,
            )
        )

    def get_irrigation_agent(self) -> IrrigationSubAgent:
        """
        Get or create the irrigation specialist sub-agent.
        الحصول على أو إنشاء وكيل متخصص الري

        Returns:
            IrrigationSubAgent instance
        """
        if self._irrigation_agent is None:
            self._irrigation_agent = self.spawn_sub_agent(
                IrrigationSubAgent,
                agent_id=f"{self.agent_id}-irrigation",
                name="Irrigation Specialist",
                name_ar="متخصص الري",
            )
        return self._irrigation_agent

    def get_fertilizer_agent(self) -> FertilizerSubAgent:
        """
        Get or create the fertilizer specialist sub-agent.
        الحصول على أو إنشاء وكيل متخصص التسميد

        Returns:
            FertilizerSubAgent instance
        """
        if self._fertilizer_agent is None:
            self._fertilizer_agent = self.spawn_sub_agent(
                FertilizerSubAgent,
                agent_id=f"{self.agent_id}-fertilizer",
                name="Fertilizer Specialist",
                name_ar="متخصص التسميد",
            )
        return self._fertilizer_agent

    def get_pest_control_agent(self) -> PestControlSubAgent:
        """
        Get or create the pest control specialist sub-agent.
        الحصول على أو إنشاء وكيل متخصص مكافحة الآفات

        Returns:
            PestControlSubAgent instance
        """
        if self._pest_agent is None:
            self._pest_agent = self.spawn_sub_agent(
                PestControlSubAgent,
                agent_id=f"{self.agent_id}-pest-control",
                name="Pest Control Specialist",
                name_ar="متخصص مكافحة الآفات",
            )
        return self._pest_agent

    def get_harvest_planner_agent(self) -> HarvestPlannerSubAgent:
        """
        Get or create the harvest planner sub-agent.
        الحصول على أو إنشاء وكيل تخطيط الحصاد

        Returns:
            HarvestPlannerSubAgent instance
        """
        if self._harvest_agent is None:
            self._harvest_agent = self.spawn_sub_agent(
                HarvestPlannerSubAgent,
                agent_id=f"{self.agent_id}-harvest",
                name="Harvest Planning Specialist",
                name_ar="متخصص تخطيط الحصاد",
            )
        return self._harvest_agent

    async def get_specialized_advice(
        self,
        domain: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get advice from the appropriate specialist sub-agent.
        الحصول على النصيحة من الوكيل الفرعي المتخصص المناسب

        Args:
            domain: Domain of expertise (irrigation, fertilizer, pest, harvest)
            task: The task/question
            context: Additional context

        Returns:
            Result from specialist agent
        """
        context = context or {}

        agent_map = {
            "irrigation": self.get_irrigation_agent,
            "water": self.get_irrigation_agent,
            "fertilizer": self.get_fertilizer_agent,
            "nutrition": self.get_fertilizer_agent,
            "pest": self.get_pest_control_agent,
            "disease": self.get_pest_control_agent,
            "harvest": self.get_harvest_planner_agent,
            "yield": self.get_harvest_planner_agent,
        }

        agent_getter = agent_map.get(domain.lower())
        if not agent_getter:
            return {
                "success": False,
                "error": f"No specialist for domain: {domain}",
                "error_ar": f"لا يوجد متخصص للمجال: {domain}",
            }

        specialist = agent_getter()

        logger.info(
            "delegating_to_specialist",
            domain=domain,
            specialist=specialist.agent_id,
            task=task[:50],
        )

        result = await specialist.run(task=task, context=context)

        # Store in memory for learning
        await self.store_memory(
            memory_type=MemoryType.EPISODIC,
            content={
                "type": "specialist_consultation",
                "domain": domain,
                "task": task,
                "specialist": specialist.agent_id,
                "success": result.get("success", False),
            },
            importance=0.6,
            tags=["delegation", domain],
        )

        return result

    # ========================================
    # COLLABORATIVE DECISION MAKING
    # صنع القرار التعاوني
    # ========================================

    async def make_collaborative_decision(
        self,
        topic: str,
        topic_ar: str,
        options: list[dict[str, Any]],
        domains_involved: list[str],
        context: dict[str, Any] | None = None,
        consensus_type: ConsensusType = ConsensusType.WEIGHTED,
    ) -> CollaborativeDecision:
        """
        Make a decision collaboratively with specialist sub-agents.
        اتخاذ قرار بالتعاون مع الوكلاء الفرعيين المتخصصين

        Args:
            topic: Decision topic | موضوع القرار
            topic_ar: Arabic topic | الموضوع بالعربية
            options: List of options to consider | قائمة الخيارات
            domains_involved: Domains to consult (irrigation, fertilizer, etc.)
            context: Additional context
            consensus_type: How to reach consensus

        Returns:
            CollaborativeDecision with final recommendation

        Example:
            decision = await advisor.make_collaborative_decision(
                topic="Best approach for Field F003 with water stress and nitrogen deficiency",
                topic_ar="أفضل نهج للحقل F003 مع إجهاد مائي ونقص نيتروجين",
                options=[
                    {"id": 0, "name": "Irrigate first", "name_ar": "الري أولاً"},
                    {"id": 1, "name": "Fertilize first", "name_ar": "التسميد أولاً"},
                    {"id": 2, "name": "Combined approach", "name_ar": "نهج مشترك"},
                ],
                domains_involved=["irrigation", "fertilizer"],
            )
        """
        context = context or {}

        # Create consensus proposal
        proposal = self.create_consensus_proposal(
            topic=topic,
            topic_ar=topic_ar,
            options=options,
            consensus_type=consensus_type,
        )

        # Gather specialist agents
        participating_agents = []
        individual_recommendations = []

        for domain in domains_involved:
            agent_getter = {
                "irrigation": self.get_irrigation_agent,
                "fertilizer": self.get_fertilizer_agent,
                "pest": self.get_pest_control_agent,
                "harvest": self.get_harvest_planner_agent,
            }.get(domain)

            if agent_getter:
                agent = agent_getter()
                participating_agents.append(agent)

                # Get specialist's analysis and vote
                analysis_task = f"Analyze and vote on: {topic}\nOptions: {options}"
                result = await agent.run(task=analysis_task, context=context)

                individual_recommendations.append(
                    {
                        "agent_id": agent.agent_id,
                        "domain": domain,
                        "analysis": result.get("outputs", []),
                    }
                )

        # Also include this coordinator's vote
        participating_agents.append(self)

        # Facilitate consensus
        consensus_result = await self.facilitate_consensus(
            proposal=proposal,
            participating_agents=participating_agents,
        )

        # Build final recommendation
        winning_option_idx = consensus_result.get("winning_option", 0)
        winning_option = options[winning_option_idx] if winning_option_idx < len(options) else options[0]

        decision = CollaborativeDecision(
            decision_id=proposal.proposal_id,
            topic=topic,
            topic_ar=topic_ar,
            participating_agents=[a.agent_id for a in participating_agents],
            final_recommendation=winning_option,
            confidence=consensus_result.get("weighted_score", 0.5) / len(participating_agents)
            if participating_agents
            else 0.5,
            consensus_type=consensus_type.value,
            individual_recommendations=individual_recommendations,
        )

        self.decision_history.append(decision)

        logger.info(
            "collaborative_decision_made",
            decision_id=decision.decision_id,
            topic=topic[:50],
            winning_option=winning_option.get("name"),
            confidence=decision.confidence,
        )

        return decision

    async def get_multi_domain_advice(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get comprehensive advice by consulting multiple specialists.
        الحصول على نصيحة شاملة بالتشاور مع متخصصين متعددين

        Args:
            task: The task/question
            context: Additional context

        Returns:
            Aggregated advice from all relevant specialists
        """
        context = context or {}
        task_lower = task.lower()

        # Determine which domains are relevant
        relevant_domains = []
        domain_keywords = {
            "irrigation": ["water", "irrigation", "ري", "سقي", "رطوبة"],
            "fertilizer": ["fertilizer", "nutrient", "سماد", "تسميد", "نيتروجين"],
            "pest": ["pest", "disease", "آفة", "مرض", "حشرة"],
            "harvest": ["harvest", "yield", "حصاد", "إنتاج", "جني"],
        }

        for domain, keywords in domain_keywords.items():
            if any(kw in task_lower for kw in keywords):
                relevant_domains.append(domain)

        # Default to irrigation and fertilizer if none detected
        if not relevant_domains:
            relevant_domains = ["irrigation", "fertilizer"]

        # Collect advice from each domain
        all_advice = {
            "task": task,
            "domains_consulted": relevant_domains,
            "specialist_advice": {},
            "combined_recommendations": [],
        }

        for domain in relevant_domains:
            result = await self.get_specialized_advice(
                domain=domain,
                task=task,
                context=context,
            )
            all_advice["specialist_advice"][domain] = result

            # Extract recommendations
            if result.get("success") and result.get("outputs"):
                for output in result.get("outputs", []):
                    all_advice["combined_recommendations"].append(
                        {
                            "domain": domain,
                            "recommendation": output.get("output"),
                        }
                    )

        return all_advice

    # ========================================
    # FARMER FEEDBACK LEARNING
    # التعلم من ملاحظات المزارع
    # ========================================

    async def record_farmer_feedback(
        self,
        recommendation_id: str,
        rating: int,
        outcome: str,
        comments: str | None = None,
        comments_ar: str | None = None,
        corrections: dict[str, Any] | None = None,
    ) -> None:
        """
        Record farmer feedback on a recommendation.
        تسجيل ملاحظات المزارع على توصية

        Args:
            recommendation_id: ID of the recommendation
            rating: 1-5 star rating
            outcome: success/partial/failure
            comments: Farmer comments (English)
            comments_ar: Farmer comments (Arabic)
            corrections: Any corrections to the advice

        Example:
            await advisor.record_farmer_feedback(
                recommendation_id="rec_001",
                rating=4,
                outcome="success",
                comments="The irrigation advice worked well",
                comments_ar="نصيحة الري نجحت بشكل جيد"
            )
        """
        feedback = {
            "rating": rating,
            "outcome": outcome,
            "comments": comments,
            "comments_ar": comments_ar,
            "corrections": corrections,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Store in outcomes tracking
        self.recommendation_outcomes[recommendation_id] = feedback
        self.farmer_satisfaction_scores.append(rating)

        # Learn from feedback
        await self.learn_from_feedback(
            task_id=recommendation_id,
            feedback=feedback,
        )

        logger.info(
            "farmer_feedback_recorded",
            recommendation_id=recommendation_id,
            rating=rating,
            outcome=outcome,
        )

    async def get_recommendation_with_learning(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get a recommendation enhanced by past learning.
        الحصول على توصية معززة بالتعلم السابق

        This method recalls similar past experiences and uses them
        to improve the current recommendation.

        Args:
            task: The task/question
            context: Additional context

        Returns:
            Recommendation with learning context
        """
        context = context or {}

        # Recall similar experiences
        similar_experiences = await self.recall_similar_experience(context)

        # Add successful patterns to context
        if similar_experiences:
            context["past_experiences"] = similar_experiences
            context["learning_applied"] = True

            # If we have a highly successful pattern, prioritize it
            for exp in similar_experiences:
                if exp.get("feedback", {}).get("rating", 0) >= 4:
                    context["proven_approach"] = exp

        # Get multi-domain advice
        advice = await self.get_multi_domain_advice(task=task, context=context)

        # Add learning metadata
        advice["learning_metadata"] = {
            "experiences_recalled": len(similar_experiences),
            "proven_approaches_found": sum(
                1 for exp in similar_experiences if exp.get("feedback", {}).get("rating", 0) >= 4
            ),
            "average_farmer_satisfaction": (
                sum(self.farmer_satisfaction_scores) / len(self.farmer_satisfaction_scores)
                if self.farmer_satisfaction_scores
                else 0
            ),
        }

        return advice

    def get_farmer_satisfaction_summary(self) -> dict[str, Any]:
        """
        Get a summary of farmer satisfaction metrics.
        الحصول على ملخص مقاييس رضا المزارع

        Returns:
            Summary of satisfaction scores and outcomes
        """
        if not self.farmer_satisfaction_scores:
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "success_rate": 0,
            }

        outcomes = list(self.recommendation_outcomes.values())
        successes = sum(1 for o in outcomes if o.get("outcome") == "success")

        return {
            "total_feedback": len(self.farmer_satisfaction_scores),
            "average_rating": sum(self.farmer_satisfaction_scores) / len(self.farmer_satisfaction_scores),
            "success_rate": successes / len(outcomes) if outcomes else 0,
            "rating_distribution": {i: self.farmer_satisfaction_scores.count(i) for i in range(1, 6)},
            "outcome_distribution": {
                "success": successes,
                "partial": sum(1 for o in outcomes if o.get("outcome") == "partial"),
                "failure": sum(1 for o in outcomes if o.get("outcome") == "failure"),
            },
        }
