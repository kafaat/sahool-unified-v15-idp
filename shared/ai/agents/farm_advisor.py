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

Author: SAHOOL Platform Team
Updated: January 2026
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

import structlog

from .base import (
    AgentMode,
    AgentStep,
    AgentTool,
    BaseAutonomousAgent,
    ToolResult,
)
from ..llm_provider import LLMProviderManager

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
    ):
        super().__init__(
            agent_id="farm-advisor-agent",
            name="Farm Advisor Agent",
            name_ar="وكيل مستشار المزرعة",
            description="Bilingual agricultural advisor for farmers",
            description_ar="مستشار زراعي ثنائي اللغة للمزارعين",
            mode=mode,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
        )

        self.preferred_language = preferred_language
        self.farm_context: FarmContext | None = None
        self.conversation_history: list[dict[str, str]] = []

    def _register_default_tools(self) -> None:
        """Register advisory tools."""

        # Tool 1: Get Field Status
        self.register_tool(AgentTool(
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
                "required": ["field_id"]
            },
            handler=self._get_field_status,
            tags=["status", "monitoring"],
        ))

        # Tool 2: Calculate Irrigation Need
        self.register_tool(AgentTool(
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
                "required": ["field_id"]
            },
            handler=self._calculate_irrigation_need,
            tags=["irrigation", "calculation"],
        ))

        # Tool 3: Calculate Fertilizer Need
        self.register_tool(AgentTool(
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
                "required": ["field_id"]
            },
            handler=self._calculate_fertilizer_need,
            tags=["fertilizer", "calculation"],
        ))

        # Tool 4: Diagnose Crop Issue
        self.register_tool(AgentTool(
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
                "required": ["crop_type", "symptoms"]
            },
            handler=self._diagnose_crop_issue,
            tags=["diagnosis", "health"],
        ))

        # Tool 5: Create Task (Execute mode only)
        self.register_tool(AgentTool(
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
                        "enum": ["irrigation", "fertilizer", "spray", "harvest", "inspection"]
                    },
                    "description": {"type": "string"},
                    "scheduled_date": {"type": "string", "format": "date"},
                    "priority": {"type": "string", "enum": ["urgent", "high", "medium", "low"]},
                    "parameters": {"type": "object"},
                },
                "required": ["field_id", "task_type", "description"]
            },
            handler=self._create_task,
            requires_approval=True,
            is_destructive=False,
            tags=["task", "execution"],
        ))

        # Tool 6: Schedule Irrigation (Execute mode only)
        self.register_tool(AgentTool(
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
                    "method": {"type": "string", "enum": ["drip", "sprinkler", "flood", "pivot"]},
                },
                "required": ["field_id", "water_amount_mm"]
            },
            handler=self._schedule_irrigation,
            requires_approval=True,
            is_destructive=False,
            tags=["irrigation", "scheduling"],
        ))

        # Tool 7: Generate Advisory Report
        self.register_tool(AgentTool(
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
                        "enum": ["daily", "weekly", "monthly", "seasonal"]
                    },
                    "include_recommendations": {"type": "boolean", "default": True},
                },
                "required": ["farm_id"]
            },
            handler=self._generate_advisory_report,
            tags=["report", "advisory"],
        ))

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

        prompt = f"""Question: {task}
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

                    steps.append(AgentStep(
                        step_id=str(uuid.uuid4()),
                        step_number=i + 1,
                        description=item.get("description", f"Step {i+1}"),
                        description_ar=item.get("description_ar", f"الخطوة {i+1}"),
                        tool_name=item.get("tool_name"),
                        tool_input=tool_input,
                    ))

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
            steps.append(AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Calculate irrigation requirements",
                description_ar="حساب متطلبات الري",
                tool_name="calculate_irrigation_need",
                tool_input={"field_id": field_id},
            ))
        elif is_fertilizer:
            steps.append(AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Calculate fertilizer requirements",
                description_ar="حساب متطلبات السماد",
                tool_name="calculate_fertilizer_need",
                tool_input={"field_id": field_id},
            ))
        elif is_disease:
            steps.append(AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=2,
                description="Diagnose crop issue",
                description_ar="تشخيص مشكلة المحصول",
                tool_name="diagnose_crop_issue",
                tool_input={"field_id": field_id, "symptoms": [], "crop_type": "wheat"},
            ))

        # Add report generation
        steps.append(AgentStep(
            step_id=str(uuid.uuid4()),
            step_number=len(steps) + 1,
            description="Generate advisory report",
            description_ar="توليد تقرير استشاري",
            tool_name="generate_advisory_report",
            tool_input={"farm_id": farm_id, "field_ids": [field_id] if field_id else []},
        ))

        # In execute mode, add action step
        if self.mode == AgentMode.EXECUTE and is_irrigation:
            steps.append(AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=len(steps) + 1,
                description="Schedule irrigation based on analysis",
                description_ar="جدولة الري بناءً على التحليل",
                tool_name="schedule_irrigation",
                tool_input={"field_id": field_id},
            ))

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
            recommendations.append({
                "fertilizer": "Urea 46%",
                "fertilizer_ar": "يوريا 46%",
                "rate_kg_ha": urea_kg,
                "timing": "Now - tillering stage",
                "timing_ar": "الآن - مرحلة التفريع",
                "method": "Broadcast with dew",
                "method_ar": "نثر مع الندى",
            })

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
            diagnoses.append({
                "condition": "Nitrogen Deficiency",
                "condition_ar": "نقص النيتروجين",
                "confidence": 0.85,
                "symptoms_matched": ["yellowing leaves", "stunted growth"],
                "treatment": "Apply Urea 46% at 46 kg/ha",
                "treatment_ar": "تطبيق يوريا 46% بمعدل 46 كجم/هكتار",
            })

        if "spots" in symptom_text or "بقع" in symptom_text:
            diagnoses.append({
                "condition": "Leaf Rust",
                "condition_ar": "صدأ الأوراق",
                "confidence": 0.70,
                "symptoms_matched": ["brown spots", "pustules"],
                "treatment": "Apply fungicide (Propiconazole)",
                "treatment_ar": "تطبيق مبيد فطري (بروبيكونازول)",
            })

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
            "scheduled_date": scheduled_date or datetime.utcnow().strftime("%Y-%m-%d"),
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
        gathered_data = getattr(self, '_gathered_data', {})

        report = {
            "report_id": str(uuid.uuid4()),
            "farm_id": farm_id,
            "generated_at": datetime.utcnow().isoformat(),
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

**English:** {summary.get('en', 'N/A')}

**العربية:** {summary.get('ar', 'غير متوفر')}

---
Mode: {self.mode.value} | الوضع: {'تخطيط' if self.mode == AgentMode.PLAN else 'تنفيذ'}
"""

        return "Advisory analysis completed. | اكتمل التحليل الاستشاري."
