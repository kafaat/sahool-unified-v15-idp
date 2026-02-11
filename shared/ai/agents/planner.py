"""
Planner Agent
=============
وكيل التخطيط

Read-only planning agent inspired by OpenCode's Plan mode.
Creates execution plans without making changes.

Features:
- Safe exploration of codebase/data
- Creates detailed execution plans
- Requests approval before execution
- No write operations
- Seasonal planning with crop calendars (NEW)
- Resource optimization with constraints (NEW)
- Risk assessment with mitigation strategies (NEW)
- Collaborative planning with specialist agents (NEW)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import structlog

from ..llm_provider import LLMProviderManager
from .base import (
    AgentCapability,
    AgentMode,
    AgentStep,
    AgentTool,
    BaseAutonomousAgent,
    CollaborationRole,
    ConsensusProposal,
    ConsensusType,
    MemoryType,
    ToolResult,
)

if TYPE_CHECKING:
    from .farm_advisor import FarmAdvisorAgent

logger = structlog.get_logger()


class Season(StrEnum):
    """Agricultural seasons."""

    WINTER = "winter"  # شتاء - Nov-Feb
    SPRING = "spring"  # ربيع - Mar-Apr
    SUMMER = "summer"  # صيف - May-Aug
    FALL = "fall"  # خريف - Sep-Oct


class RiskCategory(StrEnum):
    """Risk categories for planning."""

    WEATHER = "weather"  # طقس
    PEST = "pest"  # آفات
    DISEASE = "disease"  # أمراض
    MARKET = "market"  # سوق
    RESOURCE = "resource"  # موارد
    OPERATIONAL = "operational"  # تشغيلي
    FINANCIAL = "financial"  # مالي


@dataclass
class SeasonalPlan:
    """
    Seasonal agricultural plan.
    الخطة الزراعية الموسمية
    """

    plan_id: str
    season: Season
    year: int
    farm_id: str
    title: str
    title_ar: str
    fields_planned: list[dict[str, Any]] = field(default_factory=list)
    crop_calendar: list[dict[str, Any]] = field(default_factory=list)
    resource_allocation: dict[str, Any] = field(default_factory=dict)
    budget: dict[str, float] = field(default_factory=dict)
    risks: list[dict[str, Any]] = field(default_factory=list)
    milestones: list[dict[str, Any]] = field(default_factory=list)
    status: str = "draft"  # draft, approved, active, completed
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "season": self.season.value,
            "year": self.year,
            "farm_id": self.farm_id,
            "title": self.title,
            "title_ar": self.title_ar,
            "fields_planned": self.fields_planned,
            "crop_calendar": self.crop_calendar,
            "resource_allocation": self.resource_allocation,
            "budget": self.budget,
            "risks": self.risks,
            "milestones": self.milestones,
            "status": self.status,
        }


@dataclass
class ResourceAllocation:
    """
    Resource allocation for planning.
    تخصيص الموارد للتخطيط
    """

    resource_type: str  # water, labor, equipment, seed, fertilizer
    resource_type_ar: str
    total_available: float
    unit: str
    allocated: dict[str, float] = field(default_factory=dict)  # field_id -> amount
    utilization_percent: float = 0.0
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_type": self.resource_type,
            "resource_type_ar": self.resource_type_ar,
            "total_available": self.total_available,
            "unit": self.unit,
            "allocated": self.allocated,
            "utilization_percent": self.utilization_percent,
            "constraints": self.constraints,
        }


@dataclass
class RiskAssessment:
    """
    Risk assessment for a plan.
    تقييم المخاطر للخطة
    """

    risk_id: str
    category: RiskCategory
    title: str
    title_ar: str
    description: str
    description_ar: str
    probability: str  # low, medium, high
    impact: str  # low, medium, high, critical
    risk_score: float  # 0-100
    mitigation_strategies: list[dict[str, str]] = field(default_factory=list)
    contingency_plan: str | None = None
    contingency_plan_ar: str | None = None
    owner: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_id": self.risk_id,
            "category": self.category.value,
            "title": self.title,
            "title_ar": self.title_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "probability": self.probability,
            "impact": self.impact,
            "risk_score": self.risk_score,
            "mitigation_strategies": self.mitigation_strategies,
            "contingency_plan": self.contingency_plan,
            "contingency_plan_ar": self.contingency_plan_ar,
        }


@dataclass
class CollaborativePlan:
    """
    Plan created collaboratively with multiple agents.
    خطة تم إنشاؤها بالتعاون مع وكلاء متعددين
    """

    plan_id: str
    title: str
    title_ar: str
    participating_agents: list[str]
    agent_contributions: dict[str, dict[str, Any]]
    consensus_reached: bool
    final_plan: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "title": self.title,
            "title_ar": self.title_ar,
            "participating_agents": self.participating_agents,
            "agent_contributions": self.agent_contributions,
            "consensus_reached": self.consensus_reached,
            "final_plan": self.final_plan,
        }


@dataclass
class ExecutionPlan:
    """
    Execution plan generated by the planner.
    خطة التنفيذ المولدة من المخطط
    """

    plan_id: str
    title: str
    title_ar: str
    description: str
    description_ar: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    estimated_duration_minutes: int = 0
    risk_level: str = "low"  # low, medium, high
    requires_approval: bool = True
    resources_needed: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "title": self.title,
            "title_ar": self.title_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "steps": self.steps,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "resources_needed": self.resources_needed,
            "created_at": self.created_at.isoformat(),
        }


class PlannerAgent(BaseAutonomousAgent):
    """
    Read-only Planner Agent with advanced planning capabilities.
    وكيل التخطيط للقراءة فقط مع قدرات تخطيط متقدمة

    Inspired by OpenCode's Plan agent:
    - Analyzes requests without making changes
    - Creates detailed execution plans
    - Identifies risks and requirements
    - Returns plan for approval

    Enhanced capabilities:
    - Seasonal planning with crop calendars
    - Resource optimization with constraints
    - Risk assessment with mitigation strategies
    - Collaborative planning with specialist agents

    Use cases:
    - Seasonal planning for farms
    - Crop rotation planning
    - Resource allocation
    - Risk assessment
    - Multi-agent collaborative planning

    Example:
        planner = PlannerAgent()

        # Create seasonal plan
        seasonal_plan = await planner.create_seasonal_plan(
            farm_id="FARM-001",
            season=Season.WINTER,
            year=2026,
            fields=["F001", "F002", "F003"]
        )

        # Collaborative planning
        collab_plan = await planner.create_collaborative_plan(
            objective="Optimize irrigation for drought conditions",
            collaborators=[irrigation_agent, weather_agent]
        )
    """

    # Crop calendars by region
    CROP_CALENDARS = {
        "wheat": {
            "winter": {"plant_month": 11, "harvest_month": 5, "duration_days": 150},
            "spring": {"plant_month": 2, "harvest_month": 6, "duration_days": 120},
        },
        "barley": {
            "winter": {"plant_month": 11, "harvest_month": 4, "duration_days": 130},
        },
        "date_palm": {
            "annual": {"pollination_month": 3, "harvest_month": 9},
        },
        "tomato": {
            "winter": {"plant_month": 10, "harvest_month": 3, "duration_days": 120},
            "summer": {"plant_month": 3, "harvest_month": 7, "duration_days": 100},
        },
    }

    def __init__(
        self,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        enable_collaboration: bool = True,
    ):
        """
        Initialize Planner Agent.
        تهيئة وكيل التخطيط

        Args:
            tenant_id: Tenant ID for multi-tenancy
            llm_manager: LLM provider manager
            enable_collaboration: Enable collaborative planning with other agents
        """
        super().__init__(
            agent_id="planner-agent",
            name="Planner Agent",
            name_ar="وكيل التخطيط",
            description="Read-only planning agent for agricultural operations",
            description_ar="وكيل تخطيط للقراءة فقط للعمليات الزراعية",
            mode=AgentMode.PLAN,  # Always PLAN mode
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            collaboration_role=CollaborationRole.COORDINATOR,
        )

        self.current_plan: ExecutionPlan | None = None
        self.enable_collaboration = enable_collaboration

        # === NEW: Seasonal planning state ===
        self.seasonal_plans: dict[str, SeasonalPlan] = {}
        self.resource_allocations: dict[str, ResourceAllocation] = {}
        self.risk_assessments: list[RiskAssessment] = []

        # === NEW: Collaborative planning state ===
        self.collaborative_plans: dict[str, CollaborativePlan] = {}
        self.pending_collaborations: dict[str, ConsensusProposal] = {}

    def _register_default_tools(self) -> None:
        """Register read-only planning tools."""

        # Tool 1: Analyze Field History
        self.register_tool(
            AgentTool(
                name="analyze_field_history",
                name_ar="تحليل تاريخ الحقل",
                description="Analyze historical data for a field (crops, yields, issues)",
                description_ar="تحليل البيانات التاريخية للحقل (المحاصيل، الإنتاج، المشاكل)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "years": {"type": "integer", "default": 3},
                    },
                    "required": ["field_id"],
                },
                handler=self._analyze_field_history,
                tags=["analysis", "history"],
            )
        )

        # Tool 2: Check Resource Availability
        self.register_tool(
            AgentTool(
                name="check_resources",
                name_ar="فحص الموارد",
                description="Check availability of resources (water, equipment, labor)",
                description_ar="فحص توفر الموارد (المياه، المعدات، العمالة)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "farm_id": {"type": "string"},
                        "resource_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["water", "equipment", "labor"],
                        },
                        "date_range": {"type": "object"},
                    },
                    "required": ["farm_id"],
                },
                handler=self._check_resources,
                tags=["resources", "availability"],
            )
        )

        # Tool 3: Assess Weather Window
        self.register_tool(
            AgentTool(
                name="assess_weather_window",
                name_ar="تقييم نافذة الطقس",
                description="Assess optimal weather windows for operations",
                description_ar="تقييم النوافذ الجوية المثلى للعمليات",
                input_schema={
                    "type": "object",
                    "properties": {
                        "location": {"type": "object"},
                        "operation_type": {
                            "type": "string",
                            "enum": ["planting", "irrigation", "spraying", "harvest"],
                        },
                        "days_ahead": {"type": "integer", "default": 14},
                    },
                    "required": ["operation_type"],
                },
                handler=self._assess_weather_window,
                tags=["weather", "timing"],
            )
        )

        # Tool 4: Evaluate Crop Rotation Options
        self.register_tool(
            AgentTool(
                name="evaluate_rotation",
                name_ar="تقييم التناوب المحصولي",
                description="Evaluate crop rotation options for a field",
                description_ar="تقييم خيارات التناوب المحصولي للحقل",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_id": {"type": "string"},
                        "current_crop": {"type": "string"},
                        "season": {"type": "string"},
                        "constraints": {"type": "object"},
                    },
                    "required": ["field_id"],
                },
                handler=self._evaluate_rotation,
                tags=["rotation", "planning"],
            )
        )

        # Tool 5: Calculate Costs
        self.register_tool(
            AgentTool(
                name="calculate_costs",
                name_ar="حساب التكاليف",
                description="Calculate estimated costs for an operation",
                description_ar="حساب التكاليف المقدرة لعملية",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation_type": {"type": "string"},
                        "field_id": {"type": "string"},
                        "area_ha": {"type": "number"},
                        "inputs": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["operation_type"],
                },
                handler=self._calculate_costs,
                tags=["costs", "budget"],
            )
        )

        # Tool 6: Assess Risks
        self.register_tool(
            AgentTool(
                name="assess_risks",
                name_ar="تقييم المخاطر",
                description="Assess risks for a planned operation",
                description_ar="تقييم المخاطر لعملية مخطط لها",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "object"},
                        "field_id": {"type": "string"},
                        "timing": {"type": "string"},
                    },
                    "required": ["operation"],
                },
                handler=self._assess_risks,
                tags=["risk", "assessment"],
            )
        )

        # Tool 7: Generate Plan Document
        self.register_tool(
            AgentTool(
                name="generate_plan_document",
                name_ar="توليد وثيقة الخطة",
                description="Generate a formal execution plan document",
                description_ar="توليد وثيقة خطة تنفيذ رسمية",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "title_ar": {"type": "string"},
                        "steps": {"type": "array"},
                        "resources": {"type": "array"},
                        "risks": {"type": "array"},
                        "costs": {"type": "object"},
                    },
                    "required": ["title", "steps"],
                },
                handler=self._generate_plan_document,
                tags=["document", "plan"],
            )
        )

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """
        Decompose planning task into analysis steps.
        تقسيم مهمة التخطيط إلى خطوات تحليلية
        """
        field_id = context.get("field_id")
        farm_id = context.get("farm_id")

        # Detect planning type from task
        task_lower = task.lower()

        is_planting = any(w in task_lower for w in ["plant", "زراعة", "بذر"])
        is_rotation = any(w in task_lower for w in ["rotation", "تناوب"])
        is_season = any(w in task_lower for w in ["season", "موسم", "plan", "خطة"])

        steps = [
            # Always start with history analysis
            AgentStep(
                step_id=str(uuid.uuid4()),
                step_number=1,
                description="Analyze field history and past performance",
                description_ar="تحليل تاريخ الحقل والأداء السابق",
                tool_name="analyze_field_history",
                tool_input={"field_id": field_id, "years": 3},
            ),
        ]

        if is_rotation:
            steps.append(
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=2,
                    description="Evaluate crop rotation options",
                    description_ar="تقييم خيارات التناوب المحصولي",
                    tool_name="evaluate_rotation",
                    tool_input={"field_id": field_id},
                )
            )

        if is_planting or is_season:
            steps.extend(
                [
                    AgentStep(
                        step_id=str(uuid.uuid4()),
                        step_number=len(steps) + 1,
                        description="Assess weather windows for operations",
                        description_ar="تقييم النوافذ الجوية للعمليات",
                        tool_name="assess_weather_window",
                        tool_input={"operation_type": "planting", "days_ahead": 14},
                    ),
                    AgentStep(
                        step_id=str(uuid.uuid4()),
                        step_number=len(steps) + 2,
                        description="Check resource availability",
                        description_ar="فحص توفر الموارد",
                        tool_name="check_resources",
                        tool_input={"farm_id": farm_id},
                    ),
                ]
            )

        # Always assess risks and costs
        steps.extend(
            [
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=len(steps) + 1,
                    description="Calculate estimated costs",
                    description_ar="حساب التكاليف المقدرة",
                    tool_name="calculate_costs",
                    tool_input={"operation_type": "seasonal_plan", "field_id": field_id},
                ),
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=len(steps) + 2,
                    description="Assess risks and mitigation strategies",
                    description_ar="تقييم المخاطر واستراتيجيات التخفيف",
                    tool_name="assess_risks",
                    tool_input={"operation": {"type": "seasonal_plan"}, "field_id": field_id},
                ),
                # Final plan document
                AgentStep(
                    step_id=str(uuid.uuid4()),
                    step_number=len(steps) + 3,
                    description="Generate execution plan document",
                    description_ar="توليد وثيقة خطة التنفيذ",
                    tool_name="generate_plan_document",
                    tool_input={
                        "title": f"Execution Plan for {field_id or 'Farm'}",
                        "title_ar": f"خطة تنفيذ للحقل {field_id or 'المزرعة'}",
                    },
                ),
            ]
        )

        return steps

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate planning step result."""
        if not result.success:
            return False, f"Analysis step failed: {result.error}"

        # All read-only operations are valid if they return data
        if result.result is None:
            return False, "No data returned from analysis"

        return True, None

    async def create_plan(
        self,
        objective: str,
        context: dict[str, Any] | None = None,
    ) -> ExecutionPlan:
        """
        Convenience method to create an execution plan.
        طريقة مريحة لإنشاء خطة تنفيذ

        Args:
            objective: What needs to be planned
            context: Additional context

        Returns:
            ExecutionPlan ready for approval
        """
        context = context or {}

        # Run the planning workflow
        result = await self.run(task=objective, context=context)

        # Extract plan from result
        if result.get("success") and self.current_plan:
            return self.current_plan

        # Create basic plan from steps
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            title=objective[:100],
            title_ar=objective[:100],
            description=f"Execution plan for: {objective}",
            description_ar=f"خطة تنفيذ لـ: {objective}",
            steps=[s.to_dict() for s in self.steps],
            requires_approval=True,
        )

    # Tool handlers (read-only analysis)
    async def _analyze_field_history(
        self,
        field_id: str,
        years: int = 3,
    ) -> dict[str, Any]:
        """Analyze field history."""
        logger.info("analyzing_field_history", field_id=field_id, years=years)

        return {
            "field_id": field_id,
            "analysis_period_years": years,
            "crop_history": [
                {"season": "2025-winter", "crop": "wheat", "yield_t_ha": 4.5},
                {"season": "2024-summer", "crop": "fallow", "yield_t_ha": 0},
                {"season": "2024-winter", "crop": "barley", "yield_t_ha": 3.8},
            ],
            "average_yield_t_ha": 4.15,
            "soil_health_trend": "stable",
            "issues_reported": ["nitrogen_deficiency_2024", "water_stress_2025"],
            "recommendations_from_history": [
                "Increase nitrogen application by 10%",
                "Consider earlier irrigation start",
            ],
        }

    async def _check_resources(
        self,
        farm_id: str,
        resource_types: list[str] | None = None,
        date_range: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Check resource availability."""
        logger.info("checking_resources", farm_id=farm_id)

        return {
            "farm_id": farm_id,
            "resources": {
                "water": {
                    "available": True,
                    "capacity_m3_day": 500,
                    "current_usage_pct": 60,
                    "status": "adequate",
                },
                "equipment": {
                    "tractor": {"available": True, "next_maintenance": "2026-02-15"},
                    "sprayer": {"available": True, "calibrated": True},
                    "harvester": {"available": False, "available_from": "2026-04-01"},
                },
                "labor": {
                    "permanent_workers": 5,
                    "seasonal_available": True,
                    "peak_season_covered": True,
                },
            },
            "constraints": ["Harvester not available until April"],
        }

    async def _assess_weather_window(
        self,
        operation_type: str,
        location: dict[str, float] | None = None,
        days_ahead: int = 14,
    ) -> dict[str, Any]:
        """Assess weather windows."""
        logger.info("assessing_weather", operation=operation_type)

        return {
            "operation_type": operation_type,
            "analysis_days": days_ahead,
            "optimal_windows": [
                {
                    "start": "2026-01-23",
                    "end": "2026-01-25",
                    "confidence": 0.85,
                    "conditions": "Clear, 15-20°C, low wind",
                },
                {
                    "start": "2026-01-28",
                    "end": "2026-01-30",
                    "confidence": 0.75,
                    "conditions": "Partly cloudy, 12-18°C",
                },
            ],
            "avoid_dates": ["2026-01-26", "2026-01-27"],
            "avoid_reason": "60% rain probability",
        }

    async def _evaluate_rotation(
        self,
        field_id: str,
        current_crop: str | None = None,
        season: str | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate crop rotation options."""
        logger.info("evaluating_rotation", field_id=field_id)

        return {
            "field_id": field_id,
            "current_crop": current_crop or "wheat",
            "rotation_options": [
                {
                    "crop": "legume (chickpea)",
                    "crop_ar": "بقوليات (حمص)",
                    "score": 92,
                    "benefits": ["Nitrogen fixation", "Break disease cycle"],
                    "benefits_ar": ["تثبيت النيتروجين", "كسر دورة المرض"],
                },
                {
                    "crop": "barley",
                    "crop_ar": "شعير",
                    "score": 78,
                    "benefits": ["Lower water requirement", "Similar management"],
                },
                {
                    "crop": "fallow",
                    "crop_ar": "بور",
                    "score": 65,
                    "benefits": ["Soil recovery", "Moisture conservation"],
                },
            ],
            "recommendation": "legume (chickpea)",
            "recommendation_ar": "بقوليات (حمص)",
        }

    async def _calculate_costs(
        self,
        operation_type: str,
        field_id: str | None = None,
        area_ha: float | None = None,
        inputs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Calculate operation costs."""
        logger.info("calculating_costs", operation=operation_type)

        area = area_ha or 8.5

        return {
            "operation_type": operation_type,
            "area_ha": area,
            "costs": {
                "seeds": {"amount": 1200 * area, "unit": "SAR"},
                "fertilizer": {"amount": 450 * area, "unit": "SAR"},
                "labor": {"amount": 300 * area, "unit": "SAR"},
                "equipment": {"amount": 200 * area, "unit": "SAR"},
                "water": {"amount": 150 * area, "unit": "SAR"},
            },
            "total_cost_sar": 2300 * area,
            "cost_per_ha_sar": 2300,
            "expected_revenue_sar": 8500 * area,
            "expected_profit_sar": 6200 * area,
            "roi_percent": 269,
        }

    async def _assess_risks(
        self,
        operation: dict[str, Any],
        field_id: str | None = None,
        timing: str | None = None,
    ) -> dict[str, Any]:
        """Assess operation risks."""
        logger.info("assessing_risks", operation=operation.get("type"))

        return {
            "operation": operation,
            "risk_level": "medium",
            "risks": [
                {
                    "risk": "Weather variability",
                    "risk_ar": "تقلب الطقس",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "Monitor forecasts, flexible scheduling",
                    "mitigation_ar": "مراقبة التوقعات، جدولة مرنة",
                },
                {
                    "risk": "Pest outbreak",
                    "risk_ar": "تفشي الآفات",
                    "probability": "low",
                    "impact": "medium",
                    "mitigation": "Regular scouting, preventive treatment",
                },
                {
                    "risk": "Water shortage",
                    "risk_ar": "نقص المياه",
                    "probability": "low",
                    "impact": "high",
                    "mitigation": "Efficient irrigation, backup source",
                },
            ],
            "overall_risk_score": 45,
            "recommendation": "Proceed with standard precautions",
        }

    async def _generate_plan_document(
        self,
        title: str,
        title_ar: str | None = None,
        steps: list[dict[str, Any]] | None = None,
        resources: list[str] | None = None,
        risks: list[dict[str, Any]] | None = None,
        costs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate formal plan document."""
        logger.info("generating_plan_document", title=title)

        # Gather data from previous steps
        getattr(self, "gathered_data", {})

        plan = ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            title=title,
            title_ar=title_ar or title,
            description="Comprehensive execution plan based on analysis",
            description_ar="خطة تنفيذ شاملة بناءً على التحليل",
            steps=steps or [s.to_dict() for s in self.steps],
            estimated_duration_minutes=120,
            risk_level="medium",
            requires_approval=True,
            resources_needed=resources or ["water", "labor", "equipment"],
        )

        self.current_plan = plan

        return {
            "plan": plan.to_dict(),
            "status": "ready_for_approval",
            "message": "Plan generated successfully. Awaiting approval.",
            "message_ar": "تم توليد الخطة بنجاح. في انتظار الموافقة.",
        }

    def _generate_summary(self, outputs: list[dict[str, Any]]) -> str:
        """Generate planning summary."""
        if self.current_plan:
            return f"""
## Execution Plan | خطة التنفيذ

**Title | العنوان:** {self.current_plan.title}
**العنوان:** {self.current_plan.title_ar}

**Risk Level | مستوى المخاطرة:** {self.current_plan.risk_level}
**Estimated Duration | المدة المقدرة:** {self.current_plan.estimated_duration_minutes} minutes

**Status:** Ready for approval | جاهز للموافقة

---
This plan was generated in read-only mode. No changes have been made.
تم توليد هذه الخطة في وضع القراءة فقط. لم يتم إجراء أي تغييرات.
"""

        return "Planning analysis completed. | اكتمل تحليل التخطيط."

    # ========================================
    # NEW: CAPABILITY REGISTRATION
    # تسجيل القدرات
    # ========================================

    def _register_default_capabilities(self) -> None:
        """Register planner capabilities."""
        self.register_capability(
            AgentCapability(
                name="seasonal_planning",
                name_ar="التخطيط الموسمي",
                description="Create comprehensive seasonal agricultural plans",
                description_ar="إنشاء خطط زراعية موسمية شاملة",
                domains=["planning", "seasonal", "calendar"],
                skill_level=0.9,
            )
        )
        self.register_capability(
            AgentCapability(
                name="resource_optimization",
                name_ar="تحسين الموارد",
                description="Optimize resource allocation across fields",
                description_ar="تحسين تخصيص الموارد عبر الحقول",
                domains=["planning", "resources", "optimization"],
                skill_level=0.85,
            )
        )
        self.register_capability(
            AgentCapability(
                name="risk_assessment",
                name_ar="تقييم المخاطر",
                description="Assess and mitigate agricultural risks",
                description_ar="تقييم وتخفيف المخاطر الزراعية",
                domains=["planning", "risk", "mitigation"],
                skill_level=0.85,
            )
        )

    # ========================================
    # SEASONAL PLANNING
    # التخطيط الموسمي
    # ========================================

    async def create_seasonal_plan(
        self,
        farm_id: str,
        season: Season,
        year: int,
        fields: list[str],
        crops: dict[str, str] | None = None,
        budget_sar: float | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> SeasonalPlan:
        """
        Create a comprehensive seasonal plan.
        إنشاء خطة موسمية شاملة

        Args:
            farm_id: Farm identifier
            season: Target season
            year: Target year
            fields: List of field IDs to plan
            crops: Optional mapping of field_id -> crop_type
            budget_sar: Optional budget constraint in SAR
            constraints: Additional constraints

        Returns:
            SeasonalPlan with full details

        Example:
            plan = await planner.create_seasonal_plan(
                farm_id="FARM-001",
                season=Season.WINTER,
                year=2026,
                fields=["F001", "F002", "F003"],
                crops={"F001": "wheat", "F002": "barley"},
                budget_sar=50000
            )
        """
        constraints = constraints or {}

        logger.info(
            "creating_seasonal_plan",
            farm_id=farm_id,
            season=season.value,
            year=year,
            num_fields=len(fields),
        )

        # Generate crop calendar
        crop_calendar = await self._generate_crop_calendar(
            fields=fields,
            crops=crops or {},
            season=season,
            year=year,
        )

        # Allocate resources
        resource_allocation = await self._optimize_resource_allocation(
            farm_id=farm_id,
            fields=fields,
            crops=crops or {},
            constraints=constraints,
        )

        # Assess risks
        risks = await self._assess_seasonal_risks(
            season=season,
            crops=list((crops or {}).values()),
        )

        # Generate milestones
        milestones = self._generate_milestones(crop_calendar, season, year)

        # Calculate budget
        budget = await self._calculate_seasonal_budget(
            fields=fields,
            crops=crops or {},
            resource_allocation=resource_allocation,
        )

        # Fields planning details
        fields_planned = [
            {
                "field_id": f,
                "crop": (crops or {}).get(f, "wheat"),
                "area_ha": 8.5,  # Would fetch from field service
                "status": "planned",
            }
            for f in fields
        ]

        # Create plan
        plan = SeasonalPlan(
            plan_id=str(uuid.uuid4()),
            season=season,
            year=year,
            farm_id=farm_id,
            title=f"Seasonal Plan - {season.value.title()} {year}",
            title_ar=f"الخطة الموسمية - {self._get_season_arabic(season)} {year}",
            fields_planned=fields_planned,
            crop_calendar=crop_calendar,
            resource_allocation=resource_allocation,
            budget=budget,
            risks=[r.to_dict() for r in risks],
            milestones=milestones,
            status="draft",
        )

        self.seasonal_plans[plan.plan_id] = plan

        # Store in memory
        await self.store_memory(
            memory_type=MemoryType.EPISODIC,
            content={
                "type": "seasonal_plan_created",
                "plan_id": plan.plan_id,
                "farm_id": farm_id,
                "season": season.value,
                "year": year,
            },
            importance=0.8,
            tags=["planning", "seasonal", farm_id],
        )

        logger.info(
            "seasonal_plan_created",
            plan_id=plan.plan_id,
            num_fields=len(fields),
            total_budget=sum(budget.values()),
        )

        return plan

    async def _generate_crop_calendar(
        self,
        fields: list[str],
        crops: dict[str, str],
        season: Season,
        year: int,
    ) -> list[dict[str, Any]]:
        """Generate crop calendar for fields."""
        calendar = []

        for field_id in fields:
            crop = crops.get(field_id, "wheat")
            crop_info = self.CROP_CALENDARS.get(crop, {}).get(season.value, {})

            if crop_info:
                plant_date = datetime(
                    year if crop_info.get("plant_month", 1) >= 9 else year,
                    crop_info.get("plant_month", 11),
                    15,  # Mid-month
                )
                harvest_date = plant_date + timedelta(days=crop_info.get("duration_days", 150))

                calendar.append(
                    {
                        "field_id": field_id,
                        "crop": crop,
                        "crop_ar": self._get_crop_arabic(crop),
                        "plant_date": plant_date.strftime("%Y-%m-%d"),
                        "expected_harvest": harvest_date.strftime("%Y-%m-%d"),
                        "growth_stages": self._get_growth_stages(crop, plant_date),
                    }
                )

        return calendar

    def _get_growth_stages(
        self,
        crop: str,
        plant_date: datetime,
    ) -> list[dict[str, Any]]:
        """Generate growth stages timeline."""
        if crop == "wheat":
            return [
                {
                    "stage": "germination",
                    "stage_ar": "الإنبات",
                    "date": (plant_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                },
                {
                    "stage": "tillering",
                    "stage_ar": "التفريع",
                    "date": (plant_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                },
                {
                    "stage": "stem_extension",
                    "stage_ar": "استطالة الساق",
                    "date": (plant_date + timedelta(days=60)).strftime("%Y-%m-%d"),
                },
                {
                    "stage": "heading",
                    "stage_ar": "التسنبل",
                    "date": (plant_date + timedelta(days=90)).strftime("%Y-%m-%d"),
                },
                {
                    "stage": "grain_fill",
                    "stage_ar": "امتلاء الحبوب",
                    "date": (plant_date + timedelta(days=120)).strftime("%Y-%m-%d"),
                },
                {
                    "stage": "maturity",
                    "stage_ar": "النضج",
                    "date": (plant_date + timedelta(days=150)).strftime("%Y-%m-%d"),
                },
            ]
        return []

    async def _optimize_resource_allocation(
        self,
        farm_id: str,
        fields: list[str],
        crops: dict[str, str],
        constraints: dict[str, Any],
    ) -> dict[str, Any]:
        """Optimize resource allocation across fields."""
        total_area = len(fields) * 8.5  # Simplified

        # Water allocation
        water_need = total_area * 500  # m3/ha for season

        # Labor allocation
        labor_need = total_area * 0.5  # Worker-days per ha

        # Equipment allocation
        equipment_hours = total_area * 5  # Hours per ha

        return {
            "water": {
                "total_m3": water_need,
                "by_field": {f: water_need / len(fields) for f in fields},
                "unit": "m3",
            },
            "labor": {
                "total_worker_days": labor_need,
                "by_field": {f: labor_need / len(fields) for f in fields},
                "unit": "worker-days",
            },
            "equipment": {
                "total_hours": equipment_hours,
                "by_field": {f: equipment_hours / len(fields) for f in fields},
                "unit": "hours",
            },
            "constraints_applied": list(constraints.keys()),
        }

    async def _assess_seasonal_risks(
        self,
        season: Season,
        crops: list[str],
    ) -> list[RiskAssessment]:
        """Assess risks for the seasonal plan."""
        risks = []

        # Weather risk
        weather_risk = RiskAssessment(
            risk_id=str(uuid.uuid4()),
            category=RiskCategory.WEATHER,
            title="Weather Variability",
            title_ar="تقلب الطقس",
            description="Unexpected weather patterns may affect crop growth",
            description_ar="قد تؤثر أنماط الطقس غير المتوقعة على نمو المحاصيل",
            probability="medium",
            impact="high",
            risk_score=65,
            mitigation_strategies=[
                {"en": "Monitor weather forecasts daily", "ar": "مراقبة توقعات الطقس يومياً"},
                {"en": "Maintain flexible irrigation schedule", "ar": "الحفاظ على جدول ري مرن"},
            ],
            contingency_plan="Have backup water source ready",
            contingency_plan_ar="تجهيز مصدر مياه احتياطي",
        )
        risks.append(weather_risk)

        # Pest risk
        if season == Season.SPRING:
            pest_risk = RiskAssessment(
                risk_id=str(uuid.uuid4()),
                category=RiskCategory.PEST,
                title="Spring Pest Outbreak",
                title_ar="تفشي آفات الربيع",
                description="Increased pest activity during spring warming",
                description_ar="زيادة نشاط الآفات خلال ارتفاع درجات حرارة الربيع",
                probability="high" if "wheat" in crops else "medium",
                impact="medium",
                risk_score=55,
                mitigation_strategies=[
                    {"en": "Regular field scouting", "ar": "المسح الميداني المنتظم"},
                    {"en": "Preventive treatment", "ar": "المعالجة الوقائية"},
                ],
            )
            risks.append(pest_risk)

        # Resource risk
        resource_risk = RiskAssessment(
            risk_id=str(uuid.uuid4()),
            category=RiskCategory.RESOURCE,
            title="Water Shortage",
            title_ar="نقص المياه",
            description="Potential water supply limitations",
            description_ar="قيود محتملة على إمدادات المياه",
            probability="low",
            impact="high",
            risk_score=45,
            mitigation_strategies=[
                {"en": "Efficient irrigation system", "ar": "نظام ري كفء"},
                {"en": "Water storage", "ar": "تخزين المياه"},
            ],
        )
        risks.append(resource_risk)

        self.risk_assessments.extend(risks)
        return risks

    def _generate_milestones(
        self,
        crop_calendar: list[dict[str, Any]],
        season: Season,
        year: int,
    ) -> list[dict[str, Any]]:
        """Generate milestones for the plan."""
        milestones = []

        # Planting milestone
        if crop_calendar:
            first_plant = min(c.get("plant_date", "") for c in crop_calendar)
            milestones.append(
                {
                    "id": str(uuid.uuid4()),
                    "name": "Season Start - Planting",
                    "name_ar": "بداية الموسم - الزراعة",
                    "date": first_plant,
                    "status": "pending",
                }
            )

            # Mid-season milestone
            milestones.append(
                {
                    "id": str(uuid.uuid4()),
                    "name": "Mid-Season Review",
                    "name_ar": "مراجعة منتصف الموسم",
                    "date": (
                        datetime.strptime(first_plant, "%Y-%m-%d") + timedelta(days=75)
                    ).strftime("%Y-%m-%d"),
                    "status": "pending",
                }
            )

            # Harvest milestone
            last_harvest = max(c.get("expected_harvest", "") for c in crop_calendar)
            milestones.append(
                {
                    "id": str(uuid.uuid4()),
                    "name": "Season End - Harvest",
                    "name_ar": "نهاية الموسم - الحصاد",
                    "date": last_harvest,
                    "status": "pending",
                }
            )

        return milestones

    async def _calculate_seasonal_budget(
        self,
        fields: list[str],
        crops: dict[str, str],
        resource_allocation: dict[str, Any],
    ) -> dict[str, float]:
        """Calculate seasonal budget."""
        total_area = len(fields) * 8.5

        return {
            "seeds_sar": 1200 * total_area,
            "fertilizer_sar": 450 * total_area,
            "pesticides_sar": 200 * total_area,
            "labor_sar": 300 * total_area,
            "equipment_sar": 200 * total_area,
            "water_sar": 150 * total_area,
            "contingency_sar": 200 * total_area,
            "total_sar": 2700 * total_area,
        }

    def _get_season_arabic(self, season: Season) -> str:
        """Get Arabic name for season."""
        return {
            Season.WINTER: "الشتاء",
            Season.SPRING: "الربيع",
            Season.SUMMER: "الصيف",
            Season.FALL: "الخريف",
        }.get(season, "الموسم")

    def _get_crop_arabic(self, crop: str) -> str:
        """Get Arabic name for crop."""
        return {
            "wheat": "قمح",
            "barley": "شعير",
            "date_palm": "نخيل",
            "tomato": "طماطم",
        }.get(crop, crop)

    # ========================================
    # RISK ASSESSMENT
    # تقييم المخاطر
    # ========================================

    async def assess_risks(
        self,
        plan_context: dict[str, Any],
        categories: list[RiskCategory] | None = None,
    ) -> list[RiskAssessment]:
        """
        Assess risks for a given planning context.
        تقييم المخاطر لسياق تخطيط معين

        Args:
            plan_context: Context including fields, crops, season
            categories: Risk categories to assess (None = all)

        Returns:
            List of RiskAssessment objects
        """
        categories = categories or list(RiskCategory)
        risks = []

        for category in categories:
            assessment = await self._assess_risk_category(category, plan_context)
            if assessment:
                risks.append(assessment)

        return risks

    async def _assess_risk_category(
        self,
        category: RiskCategory,
        context: dict[str, Any],
    ) -> RiskAssessment | None:
        """Assess a specific risk category."""
        # Would implement detailed risk analysis per category
        # For now, return a basic assessment
        return RiskAssessment(
            risk_id=str(uuid.uuid4()),
            category=category,
            title=f"{category.value.title()} Risk",
            title_ar=f"مخاطر {category.value}",
            description=f"Assessment of {category.value} risks",
            description_ar=f"تقييم مخاطر {category.value}",
            probability="medium",
            impact="medium",
            risk_score=50,
            mitigation_strategies=[{"en": "Monitor and adapt", "ar": "المراقبة والتكيف"}],
        )

    # ========================================
    # COLLABORATIVE PLANNING
    # التخطيط التعاوني
    # ========================================

    async def create_collaborative_plan(
        self,
        objective: str,
        objective_ar: str | None = None,
        collaborators: list[BaseAutonomousAgent] | None = None,
        context: dict[str, Any] | None = None,
    ) -> CollaborativePlan:
        """
        Create a plan collaboratively with other agents.
        إنشاء خطة بالتعاون مع وكلاء آخرين

        Args:
            objective: Planning objective
            objective_ar: Arabic objective
            collaborators: List of agents to collaborate with
            context: Planning context

        Returns:
            CollaborativePlan with contributions from all agents

        Example:
            plan = await planner.create_collaborative_plan(
                objective="Optimize irrigation for drought conditions",
                objective_ar="تحسين الري لظروف الجفاف",
                collaborators=[irrigation_agent, weather_agent]
            )
        """
        context = context or {}
        collaborators = collaborators or []

        logger.info(
            "creating_collaborative_plan",
            objective=objective[:50],
            num_collaborators=len(collaborators),
        )

        # Register collaborators as partners
        for agent in collaborators:
            self.register_collaboration_partner(agent)

        # Collect contributions from each agent
        agent_contributions = {}

        # This planner's contribution (coordinator perspective)
        planner_analysis = await self.run(task=objective, context=context)
        agent_contributions[self.agent_id] = {
            "role": "coordinator",
            "analysis": planner_analysis,
        }

        # Get contributions from collaborators
        for agent in collaborators:
            try:
                contribution = await agent.run(
                    task=f"Provide your expert analysis for: {objective}",
                    context=context,
                )
                agent_contributions[agent.agent_id] = {
                    "role": agent.collaboration_role.value,
                    "analysis": contribution,
                    "capabilities": [c.name for c in agent.get_capabilities()],
                }
            except Exception as e:
                logger.warning(
                    "collaborator_contribution_failed",
                    agent_id=agent.agent_id,
                    error=str(e),
                )
                agent_contributions[agent.agent_id] = {
                    "role": agent.collaboration_role.value,
                    "error": str(e),
                }

        # Create consensus proposal if multiple contributors
        consensus_reached = True
        if len(agent_contributions) > 1:
            options = [
                {
                    "id": i,
                    "contributor": agent_id,
                    "summary": contrib.get("analysis", {}).get("summary", "N/A")[:100],
                }
                for i, (agent_id, contrib) in enumerate(agent_contributions.items())
                if "analysis" in contrib
            ]

            if options:
                proposal = self.create_consensus_proposal(
                    topic=f"Best approach for: {objective[:50]}",
                    topic_ar=f"أفضل نهج لـ: {(objective_ar or objective)[:50]}",
                    options=options,
                    consensus_type=ConsensusType.WEIGHTED,
                )

                # Facilitate consensus
                result = await self.facilitate_consensus(
                    proposal=proposal,
                    participating_agents=collaborators + [self],
                )

                consensus_reached = result.get("decided", False)

        # Synthesize final plan
        final_plan = self._synthesize_collaborative_plan(
            objective=objective,
            contributions=agent_contributions,
            context=context,
        )

        collab_plan = CollaborativePlan(
            plan_id=str(uuid.uuid4()),
            title=f"Collaborative Plan: {objective[:50]}",
            title_ar=f"خطة تعاونية: {(objective_ar or objective)[:50]}",
            participating_agents=[self.agent_id] + [a.agent_id for a in collaborators],
            agent_contributions=agent_contributions,
            consensus_reached=consensus_reached,
            final_plan=final_plan,
        )

        self.collaborative_plans[collab_plan.plan_id] = collab_plan

        logger.info(
            "collaborative_plan_created",
            plan_id=collab_plan.plan_id,
            consensus_reached=consensus_reached,
            num_contributors=len(agent_contributions),
        )

        return collab_plan

    def _synthesize_collaborative_plan(
        self,
        objective: str,
        contributions: dict[str, dict[str, Any]],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Synthesize contributions into final plan."""
        # Extract recommendations from each contributor
        all_recommendations = []
        for agent_id, contrib in contributions.items():
            analysis = contrib.get("analysis", {})
            if "outputs" in analysis:
                for output in analysis.get("outputs", []):
                    all_recommendations.append(
                        {
                            "source": agent_id,
                            "recommendation": output,
                        }
                    )

        return {
            "objective": objective,
            "contributors": list(contributions.keys()),
            "synthesized_recommendations": all_recommendations[:10],
            "execution_steps": self._derive_execution_steps(all_recommendations),
            "estimated_duration": "Based on collaborative analysis",
        }

    def _derive_execution_steps(
        self,
        recommendations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Derive execution steps from recommendations."""
        steps = []
        for i, rec in enumerate(recommendations[:5]):
            steps.append(
                {
                    "step": i + 1,
                    "action": f"Implement recommendation from {rec.get('source', 'unknown')}",
                    "priority": "high" if i < 2 else "medium",
                }
            )
        return steps

    async def plan_with_specialists(
        self,
        objective: str,
        domains: list[str],
        advisor_agent: FarmAdvisorAgent | None = None,
        context: dict[str, Any] | None = None,
    ) -> CollaborativePlan:
        """
        Plan using specialist sub-agents from FarmAdvisorAgent.
        التخطيط باستخدام الوكلاء الفرعيين المتخصصين

        Args:
            objective: Planning objective
            domains: Domains to include (irrigation, fertilizer, pest, harvest)
            advisor_agent: FarmAdvisorAgent with specialist sub-agents
            context: Planning context

        Returns:
            CollaborativePlan with specialist contributions
        """
        context = context or {}

        if not advisor_agent:
            # Return a basic plan without specialists
            return CollaborativePlan(
                plan_id=str(uuid.uuid4()),
                title=f"Plan: {objective[:50]}",
                title_ar=f"خطة: {objective[:50]}",
                participating_agents=[self.agent_id],
                agent_contributions={},
                consensus_reached=False,
                final_plan={"objective": objective, "note": "No specialist agents available"},
            )

        # Get specialists for requested domains
        specialists = []
        domain_agents = {
            "irrigation": advisor_agent.get_irrigation_agent,
            "fertilizer": advisor_agent.get_fertilizer_agent,
            "pest": advisor_agent.get_pest_control_agent,
            "harvest": advisor_agent.get_harvest_planner_agent,
        }

        for domain in domains:
            if domain in domain_agents:
                specialists.append(domain_agents[domain]())

        # Create collaborative plan with specialists
        return await self.create_collaborative_plan(
            objective=objective,
            collaborators=specialists,
            context=context,
        )
