"""
Experience-Based Learning for AI Agents
التعلم القائم على الخبرة للوكلاء الذكية

Inspired by Acontext concepts, this module enables AI agents to:
1. Learn from successful task executions
2. Auto-generate SOPs (Standard Operating Procedures)
3. Apply learned patterns to new similar tasks
4. Continuously improve through feedback loops

مستوحى من مفاهيم Acontext، هذه الوحدة تمكن الوكلاء من:
١. التعلم من التنفيذات الناجحة
٢. توليد إجراءات التشغيل القياسية تلقائياً
٣. تطبيق الأنماط المتعلمة على المهام المشابهة
٤. التحسين المستمر عبر حلقات التغذية الراجعة
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any
from uuid import uuid4


class ExecutionStatus(str, Enum):
    """Status of task execution"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class SOPConfidence(str, Enum):
    """Confidence level of generated SOP"""
    HIGH = "high"        # 5+ successful executions
    MEDIUM = "medium"    # 3-4 successful executions
    LOW = "low"          # 1-2 successful executions
    EXPERIMENTAL = "experimental"  # 0 executions, generated from similar


@dataclass
class ExecutionStep:
    """
    A single step in task execution.
    خطوة واحدة في تنفيذ المهمة.
    """
    step_number: int
    action: str
    action_ar: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    duration_ms: int = 0
    success: bool = True
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_number": self.step_number,
            "action": self.action,
            "action_ar": self.action_ar,
            "parameters": self.parameters,
            "result": self.result,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionStep":
        return cls(
            step_number=data["step_number"],
            action=data["action"],
            action_ar=data.get("action_ar"),
            parameters=data.get("parameters", {}),
            result=data.get("result"),
            duration_ms=data.get("duration_ms", 0),
            success=data.get("success", True),
            error_message=data.get("error_message"),
        )


@dataclass
class TaskExecution:
    """
    Record of a complete task execution.
    سجل لتنفيذ مهمة كاملة.
    """
    id: str
    task_type: str
    task_description: str
    task_description_ar: str | None
    context: dict[str, Any]
    steps: list[ExecutionStep]
    status: ExecutionStatus
    total_duration_ms: int
    timestamp: datetime
    tenant_id: str
    agent_id: str
    outcome_score: float | None = None  # 0.0 to 1.0
    feedback: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "task_type": self.task_type,
            "task_description": self.task_description,
            "task_description_ar": self.task_description_ar,
            "context": self.context,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status.value,
            "total_duration_ms": self.total_duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "outcome_score": self.outcome_score,
            "feedback": self.feedback,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskExecution":
        return cls(
            id=data["id"],
            task_type=data["task_type"],
            task_description=data["task_description"],
            task_description_ar=data.get("task_description_ar"),
            context=data.get("context", {}),
            steps=[ExecutionStep.from_dict(s) for s in data.get("steps", [])],
            status=ExecutionStatus(data["status"]),
            total_duration_ms=data.get("total_duration_ms", 0),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            tenant_id=data["tenant_id"],
            agent_id=data["agent_id"],
            outcome_score=data.get("outcome_score"),
            feedback=data.get("feedback"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SOP:
    """
    Standard Operating Procedure - learned from successful executions.
    إجراء تشغيل قياسي - متعلم من التنفيذات الناجحة.
    """
    id: str
    task_type: str
    name: str
    name_ar: str | None
    description: str
    description_ar: str | None
    steps: list[dict[str, Any]]  # Generalized steps
    preconditions: list[str]
    postconditions: list[str]
    confidence: SOPConfidence
    success_count: int
    failure_count: int
    avg_duration_ms: int
    created_at: datetime
    updated_at: datetime
    source_executions: list[str]  # IDs of executions that contributed
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "task_type": self.task_type,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "steps": self.steps,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "confidence": self.confidence.value,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "avg_duration_ms": self.avg_duration_ms,
            "success_rate": self.success_rate,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "source_executions": self.source_executions,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SOP":
        return cls(
            id=data["id"],
            task_type=data["task_type"],
            name=data["name"],
            name_ar=data.get("name_ar"),
            description=data["description"],
            description_ar=data.get("description_ar"),
            steps=data.get("steps", []),
            preconditions=data.get("preconditions", []),
            postconditions=data.get("postconditions", []),
            confidence=SOPConfidence(data.get("confidence", "low")),
            success_count=data.get("success_count", 0),
            failure_count=data.get("failure_count", 0),
            avg_duration_ms=data.get("avg_duration_ms", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            source_executions=data.get("source_executions", []),
            metadata=data.get("metadata", {}),
        )


class ExperienceStore:
    """
    In-memory store for executions and SOPs.
    مخزن في الذاكرة للتنفيذات وإجراءات التشغيل القياسية.

    Note: In production, this should be backed by a database.
    """

    def __init__(self):
        self._executions: dict[str, TaskExecution] = {}
        self._sops: dict[str, SOP] = {}
        self._task_type_index: dict[str, list[str]] = {}  # task_type -> execution_ids
        self._sop_type_index: dict[str, list[str]] = {}   # task_type -> sop_ids

    async def store_execution(self, execution: TaskExecution) -> None:
        """Store a task execution"""
        self._executions[execution.id] = execution

        # Update index
        if execution.task_type not in self._task_type_index:
            self._task_type_index[execution.task_type] = []
        self._task_type_index[execution.task_type].append(execution.id)

    async def get_execution(self, execution_id: str) -> TaskExecution | None:
        """Get execution by ID"""
        return self._executions.get(execution_id)

    async def get_executions_by_type(
        self,
        task_type: str,
        status: ExecutionStatus | None = None,
        limit: int = 100
    ) -> list[TaskExecution]:
        """Get executions by task type"""
        ids = self._task_type_index.get(task_type, [])
        executions = [self._executions[id] for id in ids if id in self._executions]

        if status:
            executions = [e for e in executions if e.status == status]

        # Sort by timestamp descending
        executions.sort(key=lambda x: x.timestamp, reverse=True)
        return executions[:limit]

    async def store_sop(self, sop: SOP) -> None:
        """Store or update an SOP"""
        self._sops[sop.id] = sop

        # Update index
        if sop.task_type not in self._sop_type_index:
            self._sop_type_index[sop.task_type] = []
        if sop.id not in self._sop_type_index[sop.task_type]:
            self._sop_type_index[sop.task_type].append(sop.id)

    async def get_sop(self, sop_id: str) -> SOP | None:
        """Get SOP by ID"""
        return self._sops.get(sop_id)

    async def get_sops_by_type(self, task_type: str) -> list[SOP]:
        """Get all SOPs for a task type"""
        ids = self._sop_type_index.get(task_type, [])
        return [self._sops[id] for id in ids if id in self._sops]

    async def get_best_sop(self, task_type: str) -> SOP | None:
        """Get the best SOP for a task type (highest confidence and success rate)"""
        sops = await self.get_sops_by_type(task_type)
        if not sops:
            return None

        # Sort by confidence (HIGH > MEDIUM > LOW > EXPERIMENTAL) then by success rate
        confidence_order = {
            SOPConfidence.HIGH: 4,
            SOPConfidence.MEDIUM: 3,
            SOPConfidence.LOW: 2,
            SOPConfidence.EXPERIMENTAL: 1,
        }

        sops.sort(
            key=lambda x: (confidence_order[x.confidence], x.success_rate),
            reverse=True
        )
        return sops[0]


class ExperienceLearner:
    """
    Main class for experience-based learning.
    الفئة الرئيسية للتعلم القائم على الخبرة.

    This class:
    1. Records task executions
    2. Extracts patterns from successful executions
    3. Generates SOPs automatically
    4. Recommends SOPs for new tasks
    """

    def __init__(self, store: ExperienceStore | None = None):
        self.store = store or ExperienceStore()
        self._min_executions_for_sop = 2  # Minimum successful executions to generate SOP

    async def record_execution(
        self,
        task_type: str,
        task_description: str,
        steps: list[ExecutionStep],
        status: ExecutionStatus,
        context: dict[str, Any],
        tenant_id: str,
        agent_id: str,
        task_description_ar: str | None = None,
        outcome_score: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TaskExecution:
        """
        Record a task execution and potentially update SOPs.
        تسجيل تنفيذ مهمة وربما تحديث إجراءات التشغيل القياسية.
        """
        # Calculate total duration
        total_duration = sum(s.duration_ms for s in steps)

        # Create execution record
        execution = TaskExecution(
            id=str(uuid4()),
            task_type=task_type,
            task_description=task_description,
            task_description_ar=task_description_ar,
            context=context,
            steps=steps,
            status=status,
            total_duration_ms=total_duration,
            timestamp=datetime.now(UTC),
            tenant_id=tenant_id,
            agent_id=agent_id,
            outcome_score=outcome_score,
            metadata=metadata or {},
        )

        # Store execution
        await self.store.store_execution(execution)

        # If successful, try to update or create SOP
        if status == ExecutionStatus.SUCCESS:
            await self._process_successful_execution(execution)
        elif status == ExecutionStatus.FAILURE:
            await self._process_failed_execution(execution)

        return execution

    async def _process_successful_execution(self, execution: TaskExecution) -> None:
        """Process a successful execution to update/create SOPs"""
        # Get existing successful executions for this task type
        similar_executions = await self.store.get_executions_by_type(
            execution.task_type,
            status=ExecutionStatus.SUCCESS
        )

        # Check if we have enough for SOP generation
        if len(similar_executions) >= self._min_executions_for_sop:
            await self._generate_or_update_sop(execution.task_type, similar_executions)

    async def _process_failed_execution(self, execution: TaskExecution) -> None:
        """Process a failed execution to update SOP statistics"""
        sops = await self.store.get_sops_by_type(execution.task_type)
        for sop in sops:
            sop.failure_count += 1
            sop.updated_at = datetime.now(UTC)
            # Downgrade confidence if failure rate is too high
            if sop.success_rate < 0.5 and sop.confidence == SOPConfidence.HIGH:
                sop.confidence = SOPConfidence.MEDIUM
            elif sop.success_rate < 0.3:
                sop.confidence = SOPConfidence.LOW
            await self.store.store_sop(sop)

    async def _generate_or_update_sop(
        self,
        task_type: str,
        executions: list[TaskExecution]
    ) -> SOP:
        """
        Generate or update an SOP from successful executions.
        توليد أو تحديث إجراء تشغيل قياسي من التنفيذات الناجحة.
        """
        # Get existing SOP or create new
        existing_sops = await self.store.get_sops_by_type(task_type)

        if existing_sops:
            sop = existing_sops[0]  # Update the first one
            sop.source_executions = list(set(
                sop.source_executions + [e.id for e in executions[:10]]
            ))[:20]  # Keep last 20 sources
        else:
            sop = SOP(
                id=str(uuid4()),
                task_type=task_type,
                name=f"SOP for {task_type}",
                name_ar=f"إجراء تشغيل قياسي لـ {task_type}",
                description=self._extract_description(executions),
                description_ar=self._extract_description_ar(executions),
                steps=[],
                preconditions=[],
                postconditions=[],
                confidence=SOPConfidence.LOW,
                success_count=0,
                failure_count=0,
                avg_duration_ms=0,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                source_executions=[e.id for e in executions[:10]],
            )

        # Extract generalized steps from executions
        sop.steps = self._extract_generalized_steps(executions)

        # Extract pre/post conditions
        sop.preconditions = self._extract_preconditions(executions)
        sop.postconditions = self._extract_postconditions(executions)

        # Update statistics
        sop.success_count = len([e for e in executions if e.status == ExecutionStatus.SUCCESS])
        sop.avg_duration_ms = sum(e.total_duration_ms for e in executions) // len(executions)
        sop.updated_at = datetime.now(UTC)

        # Update confidence based on count
        if sop.success_count >= 5:
            sop.confidence = SOPConfidence.HIGH
        elif sop.success_count >= 3:
            sop.confidence = SOPConfidence.MEDIUM
        else:
            sop.confidence = SOPConfidence.LOW

        await self.store.store_sop(sop)
        return sop

    def _extract_description(self, executions: list[TaskExecution]) -> str:
        """Extract a common description from executions"""
        if not executions:
            return ""
        # Use the most common description pattern
        descriptions = [e.task_description for e in executions]
        return descriptions[0] if descriptions else ""

    def _extract_description_ar(self, executions: list[TaskExecution]) -> str | None:
        """Extract Arabic description if available"""
        for e in executions:
            if e.task_description_ar:
                return e.task_description_ar
        return None

    def _extract_generalized_steps(
        self,
        executions: list[TaskExecution]
    ) -> list[dict[str, Any]]:
        """
        Extract generalized steps from multiple executions.
        استخراج خطوات معممة من تنفيذات متعددة.

        This identifies common patterns across executions.
        """
        if not executions:
            return []

        # Group steps by action type
        step_patterns: dict[int, dict[str, int]] = {}  # step_number -> {action: count}

        for execution in executions:
            for step in execution.steps:
                if step.step_number not in step_patterns:
                    step_patterns[step.step_number] = {}

                action = step.action
                step_patterns[step.step_number][action] = (
                    step_patterns[step.step_number].get(action, 0) + 1
                )

        # Create generalized steps from most common actions
        generalized = []
        for step_num in sorted(step_patterns.keys()):
            actions = step_patterns[step_num]
            most_common = max(actions.items(), key=lambda x: x[1])

            # Find example step for parameters
            example_step = None
            for execution in executions:
                for step in execution.steps:
                    if step.step_number == step_num and step.action == most_common[0]:
                        example_step = step
                        break
                if example_step:
                    break

            generalized.append({
                "step_number": step_num,
                "action": most_common[0],
                "action_ar": example_step.action_ar if example_step else None,
                "frequency": most_common[1] / len(executions),
                "example_parameters": example_step.parameters if example_step else {},
            })

        return generalized

    def _extract_preconditions(self, executions: list[TaskExecution]) -> list[str]:
        """Extract common preconditions from execution contexts"""
        preconditions = []

        # Look for common context keys
        common_keys: set[str] = set()
        for execution in executions:
            if execution.context:
                if not common_keys:
                    common_keys = set(execution.context.keys())
                else:
                    common_keys &= set(execution.context.keys())

        for key in common_keys:
            preconditions.append(f"Context must include '{key}'")

        return preconditions

    def _extract_postconditions(self, executions: list[TaskExecution]) -> list[str]:
        """Extract common postconditions from successful executions"""
        postconditions = []

        # Look at final step results
        for execution in executions:
            if execution.steps and execution.steps[-1].result:
                result_keys = execution.steps[-1].result.keys()
                for key in result_keys:
                    condition = f"Final result should include '{key}'"
                    if condition not in postconditions:
                        postconditions.append(condition)

        return postconditions[:5]  # Limit to 5 postconditions

    async def get_recommended_sop(
        self,
        task_type: str,
        context: dict[str, Any] | None = None
    ) -> SOP | None:
        """
        Get the recommended SOP for a task type.
        الحصول على إجراء التشغيل القياسي الموصى به لنوع المهمة.
        """
        return await self.store.get_best_sop(task_type)

    async def get_execution_guidance(
        self,
        task_type: str,
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Get guidance for executing a task based on learned experience.
        الحصول على إرشادات لتنفيذ مهمة بناءً على الخبرة المتعلمة.
        """
        sop = await self.get_recommended_sop(task_type, context)

        if not sop:
            return {
                "has_sop": False,
                "message": "No SOP available for this task type",
                "message_ar": "لا يوجد إجراء تشغيل قياسي متاح لهذا النوع من المهام",
                "suggestion": "Execute the task and record the outcome to build experience",
            }

        return {
            "has_sop": True,
            "sop_id": sop.id,
            "sop_name": sop.name,
            "sop_name_ar": sop.name_ar,
            "confidence": sop.confidence.value,
            "success_rate": f"{sop.success_rate:.1%}",
            "avg_duration_ms": sop.avg_duration_ms,
            "recommended_steps": sop.steps,
            "preconditions": sop.preconditions,
            "postconditions": sop.postconditions,
        }

    async def get_learning_stats(self, task_type: str | None = None) -> dict[str, Any]:
        """
        Get statistics about learned experience.
        الحصول على إحصائيات حول الخبرة المتعلمة.
        """
        if task_type:
            executions = await self.store.get_executions_by_type(task_type)
            sops = await self.store.get_sops_by_type(task_type)
        else:
            executions = list(self.store._executions.values())
            sops = list(self.store._sops.values())

        success_count = len([e for e in executions if e.status == ExecutionStatus.SUCCESS])
        failure_count = len([e for e in executions if e.status == ExecutionStatus.FAILURE])

        return {
            "total_executions": len(executions),
            "successful_executions": success_count,
            "failed_executions": failure_count,
            "success_rate": success_count / len(executions) if executions else 0,
            "total_sops": len(sops),
            "high_confidence_sops": len([s for s in sops if s.confidence == SOPConfidence.HIGH]),
            "medium_confidence_sops": len([s for s in sops if s.confidence == SOPConfidence.MEDIUM]),
            "task_types_covered": list({e.task_type for e in executions}),
        }


# Singleton instance for global access
_default_learner: ExperienceLearner | None = None


def get_experience_learner() -> ExperienceLearner:
    """Get the default experience learner instance"""
    global _default_learner
    if _default_learner is None:
        _default_learner = ExperienceLearner()
    return _default_learner


# Convenience functions
async def record_task_execution(
    task_type: str,
    task_description: str,
    steps: list[dict[str, Any]],
    success: bool,
    context: dict[str, Any],
    tenant_id: str,
    agent_id: str,
    **kwargs
) -> TaskExecution:
    """
    Convenience function to record a task execution.
    دالة مساعدة لتسجيل تنفيذ مهمة.
    """
    learner = get_experience_learner()

    # Convert dict steps to ExecutionStep objects
    execution_steps = [
        ExecutionStep(
            step_number=i + 1,
            action=s.get("action", "unknown"),
            action_ar=s.get("action_ar"),
            parameters=s.get("parameters", {}),
            result=s.get("result"),
            duration_ms=s.get("duration_ms", 0),
            success=s.get("success", True),
        )
        for i, s in enumerate(steps)
    ]

    return await learner.record_execution(
        task_type=task_type,
        task_description=task_description,
        steps=execution_steps,
        status=ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILURE,
        context=context,
        tenant_id=tenant_id,
        agent_id=agent_id,
        **kwargs
    )


async def get_task_guidance(
    task_type: str,
    context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Get guidance for executing a task.
    الحصول على إرشادات لتنفيذ مهمة.
    """
    learner = get_experience_learner()
    return await learner.get_execution_guidance(task_type, context)
