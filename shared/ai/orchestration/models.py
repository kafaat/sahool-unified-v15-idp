"""
Agent Orchestration Models
==========================
نماذج تنسيق الوكلاء

Pydantic v2 models for the agent orchestration framework including
swarm configuration, agent scoring, task routing, and consensus results.

Inspired by Claude-Flow architecture for multi-agent coordination.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import datetime, UTC
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class SwarmTopology(StrEnum):
    """
    Swarm communication topology.
    طوبولوجيا اتصال السرب
    """

    MESH = "mesh"  # All agents communicate with all | الكل يتواصل مع الكل
    HIERARCHICAL = "hierarchical"  # Tree structure | هيكل شجري
    STAR = "star"  # Central coordinator | منسق مركزي
    RING = "ring"  # Circular communication | اتصال دائري
    PIPELINE = "pipeline"  # Sequential processing | معالجة متسلسلة


class AgentCapability(StrEnum):
    """
    Agent capability types.
    أنواع قدرات الوكيل
    """

    CROP_ANALYSIS = "crop_analysis"  # تحليل المحاصيل
    IRRIGATION = "irrigation"  # الري
    PEST_DETECTION = "pest_detection"  # كشف الآفات
    WEATHER_ANALYSIS = "weather_analysis"  # تحليل الطقس
    SOIL_ANALYSIS = "soil_analysis"  # تحليل التربة
    YIELD_PREDICTION = "yield_prediction"  # توقع المحصول
    ADVISORY = "advisory"  # الاستشارات
    RESEARCH = "research"  # البحث
    PLANNING = "planning"  # التخطيط
    GENERAL = "general"  # عام


class TaskPriority(StrEnum):
    """
    Task priority levels.
    مستويات أولوية المهمة
    """

    CRITICAL = "critical"  # حرج - فوري
    HIGH = "high"  # عالي - خلال ساعات
    MEDIUM = "medium"  # متوسط - خلال يوم
    LOW = "low"  # منخفض - عند الإمكان


class TaskStatus(StrEnum):
    """
    Task execution status.
    حالة تنفيذ المهمة
    """

    PENDING = "pending"  # قيد الانتظار
    ROUTING = "routing"  # جاري التوجيه
    ASSIGNED = "assigned"  # تم التعيين
    IN_PROGRESS = "in_progress"  # قيد التنفيذ
    AGGREGATING = "aggregating"  # جاري التجميع
    COMPLETED = "completed"  # مكتمل
    FAILED = "failed"  # فشل
    CANCELLED = "cancelled"  # ملغى


class ConsensusType(StrEnum):
    """
    Consensus protocol types.
    أنواع بروتوكولات الإجماع
    """

    RAFT = "raft"  # Sequential consistency | الاتساق التسلسلي
    MAJORITY_VOTING = "majority_voting"  # Simple majority | الأغلبية البسيطة
    WEIGHTED_VOTING = "weighted_voting"  # Expertise-based | على أساس الخبرة
    UNANIMOUS = "unanimous"  # All must agree | يجب موافقة الجميع
    QUORUM = "quorum"  # Minimum required | الحد الأدنى المطلوب


class MemoryNamespace(StrEnum):
    """
    Collective memory namespace types.
    أنواع مساحات أسماء الذاكرة الجماعية
    """

    TASKS = "tasks"  # المهام
    PATTERNS = "patterns"  # الأنماط
    DECISIONS = "decisions"  # القرارات
    KNOWLEDGE = "knowledge"  # المعرفة
    AGENTS = "agents"  # الوكلاء
    ERRORS = "errors"  # الأخطاء


# ─────────────────────────────────────────────────────────────────────────────
# Agent Models
# ─────────────────────────────────────────────────────────────────────────────


class AgentProfile(BaseModel):
    """
    Profile of an agent in the system.
    ملف تعريف الوكيل في النظام
    """

    model_config = ConfigDict(use_enum_values=True)

    agent_id: str = Field(description="Unique agent identifier | معرف الوكيل الفريد")
    name: str = Field(description="Agent name (English)")
    name_ar: str = Field(description="Agent name (Arabic) | اسم الوكيل بالعربية")
    capabilities: list[AgentCapability] = Field(
        default_factory=list,
        description="Agent capabilities | قدرات الوكيل",
    )
    specialization: str | None = Field(
        default=None,
        description="Agent specialization | تخصص الوكيل",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata | بيانات وصفية إضافية",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp",
    )


class AgentScore(BaseModel):
    """
    Agent performance score for routing decisions.
    درجة أداء الوكيل لقرارات التوجيه
    """

    model_config = ConfigDict(use_enum_values=True)

    agent_id: str = Field(description="Agent identifier | معرف الوكيل")
    capability: AgentCapability = Field(description="Capability being scored")
    success_count: int = Field(default=0, description="Successful task count")
    failure_count: int = Field(default=0, description="Failed task count")
    total_tasks: int = Field(default=0, description="Total tasks handled")
    avg_execution_time_ms: float = Field(
        default=0.0,
        description="Average execution time in milliseconds",
    )
    q_value: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Q-learning value (0-1) | قيمة التعلم Q",
    )
    exploration_bonus: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Exploration bonus for UCB | مكافأة الاستكشاف",
    )
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last score update time",
    )

    @property
    def success_rate(self) -> float:
        """Calculate success rate | حساب معدل النجاح"""
        if self.total_tasks == 0:
            return 0.5  # Default for new agents
        return self.success_count / self.total_tasks

    @property
    def ucb_score(self) -> float:
        """
        Calculate Upper Confidence Bound score for exploration-exploitation balance.
        حساب درجة UCB لتوازن الاستكشاف والاستغلال
        """
        import math

        if self.total_tasks == 0:
            return float("inf")  # Encourage exploration of unused agents

        exploitation = self.q_value
        exploration = self.exploration_bonus * math.sqrt(
            math.log(self.total_tasks + 1) / (self.total_tasks + 1)
        )
        return exploitation + exploration


class AgentState(BaseModel):
    """
    Current state of an agent.
    الحالة الحالية للوكيل
    """

    model_config = ConfigDict(use_enum_values=True)

    agent_id: str
    is_available: bool = True
    current_task_id: str | None = None
    load: float = Field(default=0.0, ge=0.0, le=1.0, description="Current load 0-1")
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(UTC))
    error_count: int = Field(default=0, description="Recent error count")


# ─────────────────────────────────────────────────────────────────────────────
# Task Models
# ─────────────────────────────────────────────────────────────────────────────


class Task(BaseModel):
    """
    A task to be routed and executed by agents.
    مهمة يتم توجيهها وتنفيذها بواسطة الوكلاء
    """

    model_config = ConfigDict(use_enum_values=True)

    task_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique task identifier | معرف المهمة الفريد",
    )
    description: str = Field(description="Task description (English)")
    description_ar: str = Field(description="Task description (Arabic) | وصف المهمة بالعربية")
    required_capabilities: list[AgentCapability] = Field(
        default_factory=list,
        description="Required agent capabilities | القدرات المطلوبة",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority | أولوية المهمة",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Task context data | بيانات سياق المهمة",
    )
    tenant_id: str = Field(
        default="sahool",
        description="Tenant identifier | معرف المستأجر",
    )
    field_id: str | None = Field(
        default=None,
        description="Associated field ID | معرف الحقل المرتبط",
    )
    timeout_seconds: int = Field(
        default=300,
        description="Task timeout in seconds | مهلة المهمة بالثواني",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    """
    Result of a task execution.
    نتيجة تنفيذ المهمة
    """

    model_config = ConfigDict(use_enum_values=True)

    task_id: str = Field(description="Task identifier")
    agent_id: str = Field(description="Executing agent identifier")
    status: TaskStatus = Field(description="Execution status | حالة التنفيذ")
    success: bool = Field(description="Whether task succeeded")
    result: Any = Field(default=None, description="Task result data")
    error: str | None = Field(default=None, description="Error message if failed")
    error_ar: str | None = Field(default=None, description="Arabic error message")
    execution_time_ms: float = Field(
        default=0.0,
        description="Execution time in milliseconds",
    )
    started_at: datetime | None = None
    completed_at: datetime | None = None
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Result confidence score | درجة الثقة في النتيجة",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Swarm Models
# ─────────────────────────────────────────────────────────────────────────────


class SwarmConfig(BaseModel):
    """
    Configuration for swarm coordination.
    إعدادات تنسيق السرب
    """

    model_config = ConfigDict(use_enum_values=True)

    swarm_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique swarm identifier",
    )
    name: str = Field(description="Swarm name (English)")
    name_ar: str = Field(description="Swarm name (Arabic) | اسم السرب بالعربية")
    topology: SwarmTopology = Field(
        default=SwarmTopology.STAR,
        description="Communication topology | طوبولوجيا الاتصال",
    )
    min_agents: int = Field(
        default=1,
        ge=1,
        description="Minimum agents required | الحد الأدنى للوكلاء",
    )
    max_agents: int = Field(
        default=10,
        ge=1,
        description="Maximum agents allowed | الحد الأقصى للوكلاء",
    )
    consensus_type: ConsensusType = Field(
        default=ConsensusType.MAJORITY_VOTING,
        description="Consensus protocol | بروتوكول الإجماع",
    )
    consensus_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Consensus threshold (0-1) | عتبة الإجماع",
    )
    timeout_seconds: int = Field(
        default=60,
        description="Swarm operation timeout | مهلة عملية السرب",
    )
    enable_load_balancing: bool = Field(
        default=True,
        description="Enable load balancing | تفعيل موازنة الحمل",
    )
    retry_failed_tasks: bool = Field(
        default=True,
        description="Retry failed tasks | إعادة محاولة المهام الفاشلة",
    )
    max_retries: int = Field(default=3, ge=0, description="Maximum retries")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SwarmState(BaseModel):
    """
    Current state of a swarm.
    الحالة الحالية للسرب
    """

    model_config = ConfigDict(use_enum_values=True)

    swarm_id: str
    active_agents: list[str] = Field(default_factory=list)
    pending_tasks: int = Field(default=0)
    completed_tasks: int = Field(default=0)
    failed_tasks: int = Field(default=0)
    is_coordinating: bool = Field(default=False)
    current_task_id: str | None = None
    started_at: datetime | None = None
    last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SwarmResult(BaseModel):
    """
    Result of swarm execution.
    نتيجة تنفيذ السرب
    """

    model_config = ConfigDict(use_enum_values=True)

    swarm_id: str = Field(description="Swarm identifier")
    task_id: str = Field(description="Task identifier")
    success: bool = Field(description="Overall success status")
    agent_results: list[TaskResult] = Field(
        default_factory=list,
        description="Results from each agent | نتائج كل وكيل",
    )
    aggregated_result: Any = Field(
        default=None,
        description="Aggregated final result | النتيجة المجمعة النهائية",
    )
    consensus_reached: bool = Field(
        default=False,
        description="Whether consensus was reached | هل تم التوصل للإجماع",
    )
    consensus_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Consensus confidence | درجة ثقة الإجماع",
    )
    total_execution_time_ms: float = Field(default=0.0)
    agents_participated: int = Field(default=0)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    summary: str | None = Field(
        default=None,
        description="Summary of results (English)",
    )
    summary_ar: str | None = Field(
        default=None,
        description="Summary of results (Arabic) | ملخص النتائج بالعربية",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Consensus Models
# ─────────────────────────────────────────────────────────────────────────────


class Vote(BaseModel):
    """
    A vote from an agent in consensus.
    تصويت من وكيل في الإجماع
    """

    model_config = ConfigDict(use_enum_values=True)

    agent_id: str = Field(description="Voting agent identifier")
    value: Any = Field(description="Vote value/decision | قيمة/قرار التصويت")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in vote | الثقة في التصويت",
    )
    weight: float = Field(
        default=1.0,
        ge=0.0,
        description="Vote weight (for weighted voting) | وزن التصويت",
    )
    reasoning: str | None = Field(
        default=None,
        description="Reasoning for vote (English)",
    )
    reasoning_ar: str | None = Field(
        default=None,
        description="Reasoning for vote (Arabic) | تبرير التصويت بالعربية",
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConsensusResult(BaseModel):
    """
    Result of a consensus operation.
    نتيجة عملية الإجماع
    """

    model_config = ConfigDict(use_enum_values=True)

    consensus_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique consensus identifier",
    )
    consensus_type: ConsensusType = Field(description="Type of consensus used")
    reached: bool = Field(description="Whether consensus was reached | هل تم الإجماع")
    decision: Any = Field(
        default=None,
        description="Consensus decision | قرار الإجماع",
    )
    votes: list[Vote] = Field(
        default_factory=list,
        description="All votes cast | جميع الأصوات",
    )
    total_votes: int = Field(default=0)
    agreement_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Ratio of agreeing votes | نسبة الأصوات المتفقة",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence | الثقة الإجمالية",
    )
    rounds: int = Field(default=1, description="Number of voting rounds | عدد الجولات")
    dissenting_agents: list[str] = Field(
        default_factory=list,
        description="Agents that disagreed | الوكلاء المختلفون",
    )
    reasoning: str | None = Field(
        default=None,
        description="Consensus reasoning (English)",
    )
    reasoning_ar: str | None = Field(
        default=None,
        description="Consensus reasoning (Arabic) | تبرير الإجماع بالعربية",
    )
    duration_ms: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ─────────────────────────────────────────────────────────────────────────────
# Memory Models
# ─────────────────────────────────────────────────────────────────────────────


class MemoryEntry(BaseModel):
    """
    An entry in collective memory.
    إدخال في الذاكرة الجماعية
    """

    model_config = ConfigDict(use_enum_values=True)

    entry_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique entry identifier",
    )
    namespace: MemoryNamespace = Field(description="Memory namespace | مساحة اسم الذاكرة")
    key: str = Field(description="Entry key | مفتاح الإدخال")
    value: Any = Field(description="Entry value | قيمة الإدخال")
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] | None = Field(
        default=None,
        description="Vector embedding for similarity search",
    )
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = Field(
        default=None,
        description="Expiration time | وقت انتهاء الصلاحية",
    )
    tenant_id: str = Field(default="sahool")

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired | التحقق من انتهاء الصلاحية"""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at


class PatternMatch(BaseModel):
    """
    A pattern match result from memory.
    نتيجة مطابقة نمط من الذاكرة
    """

    model_config = ConfigDict(use_enum_values=True)

    entry: MemoryEntry = Field(description="Matched memory entry")
    similarity: float = Field(
        ge=0.0,
        le=1.0,
        description="Similarity score | درجة التشابه",
    )
    match_type: str = Field(
        default="semantic",
        description="Type of match (exact, semantic, pattern)",
    )


class MemoryStats(BaseModel):
    """
    Statistics for collective memory.
    إحصائيات الذاكرة الجماعية
    """

    total_entries: int = Field(default=0)
    by_namespace: dict[str, int] = Field(default_factory=dict)
    cache_hits: int = Field(default=0)
    cache_misses: int = Field(default=0)
    avg_access_time_ms: float = Field(default=0.0)
    memory_usage_bytes: int = Field(default=0)
    last_cleanup: datetime | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Routing Models
# ─────────────────────────────────────────────────────────────────────────────


class RoutingDecision(BaseModel):
    """
    A routing decision for a task.
    قرار توجيه لمهمة
    """

    model_config = ConfigDict(use_enum_values=True)

    decision_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique decision identifier",
    )
    task_id: str = Field(description="Task being routed")
    selected_agent_id: str = Field(description="Selected agent | الوكيل المختار")
    candidate_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Scores of candidate agents | درجات الوكلاء المرشحين",
    )
    selection_method: str = Field(
        default="q_learning",
        description="Method used for selection | طريقة الاختيار",
    )
    exploration_used: bool = Field(
        default=False,
        description="Whether exploration was used | هل تم استخدام الاستكشاف",
    )
    reasoning: str | None = Field(
        default=None,
        description="Selection reasoning (English)",
    )
    reasoning_ar: str | None = Field(
        default=None,
        description="Selection reasoning (Arabic) | تبرير الاختيار بالعربية",
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RouterStats(BaseModel):
    """
    Statistics for the agent router.
    إحصائيات موجه الوكلاء
    """

    total_routing_decisions: int = Field(default=0)
    exploration_count: int = Field(default=0)
    exploitation_count: int = Field(default=0)
    avg_routing_time_ms: float = Field(default=0.0)
    successful_routings: int = Field(default=0)
    failed_routings: int = Field(default=0)
    agents_registered: int = Field(default=0)
    by_capability: dict[str, int] = Field(default_factory=dict)
