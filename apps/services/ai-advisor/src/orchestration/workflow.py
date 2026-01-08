"""
Workflow Manager
مدير سير العمل

Manages multi-step workflows for complex agricultural tasks.
يدير سير العمل متعدد الخطوات للمهام الزراعية المعقدة.
"""

from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger()


class WorkflowStatus(str, Enum):
    """Workflow execution status | حالة تنفيذ سير العمل"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class WorkflowStep:
    """
    Individual step in a workflow
    خطوة فردية في سير العمل
    """

    def __init__(
        self,
        name: str,
        action: Callable,
        description: str,
        depends_on: list[str] | None = None,
    ):
        """
        Initialize workflow step
        تهيئة خطوة سير العمل

        Args:
            name: Step name | اسم الخطوة
            action: Async function to execute | دالة غير متزامنة للتنفيذ
            description: Step description | وصف الخطوة
            depends_on: Names of steps this depends on | أسماء الخطوات التي تعتمد عليها
        """
        self.name = name
        self.action = action
        self.description = description
        self.depends_on = depends_on or []
        self.status = WorkflowStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None


class Workflow:
    """
    Workflow orchestration for complex multi-step processes
    تنسيق سير العمل للعمليات المعقدة متعددة الخطوات

    Examples of workflows:
    - Complete field analysis (satellite → field analyst → disease detection → recommendations)
    - Comprehensive diagnosis (symptoms → disease identification → treatment → prevention)
    - Harvest planning (yield prediction → quality assessment → timing → market analysis)

    أمثلة على سير العمل:
    - تحليل شامل للحقل (أقمار صناعية → محلل حقول → كشف أمراض → توصيات)
    - تشخيص شامل (أعراض → تحديد مرض → علاج → وقاية)
    - تخطيط الحصاد (توقع محصول → تقييم جودة → توقيت → تحليل سوق)
    """

    def __init__(self, name: str, description: str):
        """
        Initialize workflow
        تهيئة سير العمل

        Args:
            name: Workflow name | اسم سير العمل
            description: Workflow description | وصف سير العمل
        """
        self.name = name
        self.description = description
        self.steps: dict[str, WorkflowStep] = {}
        self.status = WorkflowStatus.PENDING
        self.results = {}
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None

        logger.info("workflow_created", workflow_name=name)

    def add_step(
        self,
        name: str,
        action: Callable,
        description: str,
        depends_on: list[str] | None = None,
    ) -> "Workflow":
        """
        Add a step to the workflow
        إضافة خطوة إلى سير العمل

        Args:
            name: Step name | اسم الخطوة
            action: Async function to execute | دالة غير متزامنة للتنفيذ
            description: Step description | وصف الخطوة
            depends_on: Names of steps this depends on | الخطوات التي تعتمد عليها

        Returns:
            Self for chaining | نفسه للتسلسل
        """
        step = WorkflowStep(
            name=name,
            action=action,
            description=description,
            depends_on=depends_on,
        )
        self.steps[name] = step

        logger.debug(
            "workflow_step_added",
            workflow_name=self.name,
            step_name=name,
            depends_on=depends_on,
        )

        return self

    async def execute(
        self,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the workflow
        تنفيذ سير العمل

        Args:
            context: Initial context for the workflow | السياق الأولي لسير العمل

        Returns:
            Workflow execution results | نتائج تنفيذ سير العمل
        """
        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.utcnow()
        context = context or {}

        logger.info(
            "workflow_execution_started",
            workflow_name=self.name,
            num_steps=len(self.steps),
        )

        try:
            # Execute steps in dependency order
            # تنفيذ الخطوات حسب ترتيب التبعية
            executed_steps = set()

            while len(executed_steps) < len(self.steps):
                # Find steps that can be executed now
                # العثور على الخطوات القابلة للتنفيذ الآن
                ready_steps = [
                    step
                    for step_name, step in self.steps.items()
                    if step_name not in executed_steps
                    and all(dep in executed_steps for dep in step.depends_on)
                ]

                if not ready_steps:
                    # Circular dependency or missing dependency
                    # تبعية دائرية أو تبعية مفقودة
                    remaining = set(self.steps.keys()) - executed_steps
                    raise ValueError(f"Cannot resolve dependencies for steps: {remaining}")

                # Execute ready steps
                # تنفيذ الخطوات الجاهزة
                for step in ready_steps:
                    await self._execute_step(step, context)
                    executed_steps.add(step.name)

            self.status = WorkflowStatus.COMPLETED
            self.completed_at = datetime.utcnow()

            logger.info(
                "workflow_execution_completed",
                workflow_name=self.name,
                duration_seconds=(self.completed_at - self.started_at).total_seconds(),
            )

            return {
                "workflow_name": self.name,
                "status": self.status.value,
                "results": self.results,
                "execution_time": (self.completed_at - self.started_at).total_seconds(),
            }

        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.completed_at = datetime.utcnow()

            logger.error("workflow_execution_failed", workflow_name=self.name, error=str(e))

            return {
                "workflow_name": self.name,
                "status": self.status.value,
                "error": str(e),
                "partial_results": self.results,
            }

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: dict[str, Any],
    ):
        """
        Execute a single workflow step
        تنفيذ خطوة واحدة من سير العمل

        Args:
            step: Step to execute | الخطوة المراد تنفيذها
            context: Workflow context | سياق سير العمل
        """
        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.utcnow()

        logger.debug("workflow_step_started", workflow_name=self.name, step_name=step.name)

        try:
            # Prepare step input from previous results
            # تحضير مدخلات الخطوة من النتائج السابقة
            step_input = {
                "context": context,
                "previous_results": self.results,
            }

            # Execute step action
            # تنفيذ إجراء الخطوة
            result = await step.action(step_input)

            step.result = result
            step.status = WorkflowStatus.COMPLETED
            step.completed_at = datetime.utcnow()

            # Store result for dependent steps
            # تخزين النتيجة للخطوات التابعة
            self.results[step.name] = result

            logger.info(
                "workflow_step_completed",
                workflow_name=self.name,
                step_name=step.name,
                duration_seconds=(step.completed_at - step.started_at).total_seconds(),
            )

        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()

            logger.error(
                "workflow_step_failed",
                workflow_name=self.name,
                step_name=step.name,
                error=str(e),
            )

            raise

    def get_status(self) -> dict[str, Any]:
        """
        Get workflow status
        الحصول على حالة سير العمل

        Returns:
            Workflow status information | معلومات حالة سير العمل
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "total_steps": len(self.steps),
            "completed_steps": sum(
                1 for step in self.steps.values() if step.status == WorkflowStatus.COMPLETED
            ),
            "failed_steps": sum(
                1 for step in self.steps.values() if step.status == WorkflowStatus.FAILED
            ),
            "steps": [
                {
                    "name": step.name,
                    "description": step.description,
                    "status": step.status.value,
                    "depends_on": step.depends_on,
                }
                for step in self.steps.values()
            ],
        }


# Pre-defined workflow templates
# قوالب سير العمل المحددة مسبقاً


async def create_field_analysis_workflow(
    supervisor,
    field_id: str,
    include_disease_check: bool = True,
    include_irrigation_advice: bool = True,
) -> Workflow:
    """
    Create comprehensive field analysis workflow
    إنشاء سير عمل شامل لتحليل الحقل

    Args:
        supervisor: Supervisor instance | مثيل المشرف
        field_id: Field identifier | معرف الحقل
        include_disease_check: Include disease analysis | تضمين تحليل الأمراض
        include_irrigation_advice: Include irrigation recommendations | تضمين توصيات الري

    Returns:
        Configured workflow | سير العمل المكوّن
    """
    workflow = Workflow(
        name="comprehensive_field_analysis",
        description=f"Complete analysis for field {field_id}",
    )

    # Step 1: Gather satellite data
    # الخطوة 1: جمع بيانات الأقمار الصناعية
    async def gather_satellite_data(input_data):
        field_analyst = supervisor.agents.get("field_analyst")
        return await field_analyst.analyze_field(field_id)

    workflow.add_step(
        name="satellite_analysis",
        action=gather_satellite_data,
        description="Gather and analyze satellite imagery and NDVI data",
    )

    # Step 2: Analyze field health (depends on satellite data)
    # الخطوة 2: تحليل صحة الحقل (يعتمد على بيانات الأقمار الصناعية)
    if include_disease_check:

        async def check_diseases(input_data):
            disease_expert = supervisor.agents.get("disease_expert")
            satellite_result = input_data["previous_results"]["satellite_analysis"]
            return await disease_expert.assess_risk(
                crop_type=input_data["context"].get("crop_type", "wheat"),
                location=field_id,
                season="current",
                environmental_conditions=satellite_result,
            )

        workflow.add_step(
            name="disease_assessment",
            action=check_diseases,
            description="Assess disease risks based on field conditions",
            depends_on=["satellite_analysis"],
        )

    # Step 3: Irrigation recommendations
    # الخطوة 3: توصيات الري
    if include_irrigation_advice:

        async def irrigation_recommendations(input_data):
            irrigation_advisor = supervisor.agents.get("irrigation_advisor")
            input_data["previous_results"]["satellite_analysis"]
            return await irrigation_advisor.recommend_irrigation(
                crop_type=input_data["context"].get("crop_type", "wheat"),
                growth_stage=input_data["context"].get("growth_stage", "vegetative"),
                soil_data={},
                weather_data={},
            )

        workflow.add_step(
            name="irrigation_recommendation",
            action=irrigation_recommendations,
            description="Generate irrigation recommendations",
            depends_on=["satellite_analysis"],
        )

    return workflow
