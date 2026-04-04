"""
OpenMultiAgent Framework
========================
إطار عمل OpenMultiAgent

High-level multi-agent orchestration framework for the SAHOOL platform.
Provides team-based agent coordination with shared memory, message bus,
task queuing, and agent pooling built on top of the existing orchestration layer.

إطار تنسيق متعدد الوكلاء عالي المستوى لمنصة سهول.
يوفر تنسيق الوكلاء القائم على الفريق مع الذاكرة المشتركة وناقل الرسائل
وقائمة انتظار المهام وتجميع الوكلاء المبني على طبقة التنسيق الحالية.

Components:
    - OpenMultiAgent: Main orchestrator for creating and running agent teams
    - Team: Coordinated group of agents with message bus and shared memory
    - AgentPool: Manages agent lifecycle and concurrency
    - TaskQueue: Priority-based async task queue
    - SharedMemory: Inter-agent shared state store
    - AgentRunner: Executes individual agent tasks via LLM providers

المكونات:
    - OpenMultiAgent: المنسق الرئيسي لإنشاء وتشغيل فرق الوكلاء
    - Team: مجموعة منسقة من الوكلاء مع ناقل رسائل وذاكرة مشتركة
    - AgentPool: إدارة دورة حياة الوكلاء والتزامن
    - TaskQueue: قائمة انتظار مهام غير متزامنة قائمة على الأولوية
    - SharedMemory: مخزن حالة مشتركة بين الوكلاء
    - AgentRunner: تنفيذ مهام الوكيل الفردية عبر مزودي LLM

Example:
    >>> from shared.ai.open_multi_agent import OpenMultiAgent, AgentConfig, TeamConfig
    >>> from shared.ai.orchestration.models import AgentCapability
    >>>
    >>> oma = OpenMultiAgent()
    >>> team = await oma.create_team(
    ...     name="Field Analysis Team",
    ...     agents=[
    ...         AgentConfig(
    ...             agent_id="crop_expert",
    ...             name="Crop Expert",
    ...             name_ar="خبير المحاصيل",
    ...             capabilities=[AgentCapability.CROP_ANALYSIS],
    ...         ),
    ...     ],
    ...     config=TeamConfig(max_concurrency=3, timeout_s=120),
    ... )
    >>> results = await oma.run_team(team, tasks=[...])

Author: SAHOOL Platform Team
Updated: April 2026
"""

__version__ = "1.0.0"

from .orchestrator import AgentConfig, AgentRunner, OpenMultiAgent, TeamConfig
from .team import AgentPool, MessageBus, SharedMemory, TaskQueue, Team, TeamStatus

__all__ = [
    # Version
    "__version__",
    # Orchestrator
    "OpenMultiAgent",
    "AgentConfig",
    "TeamConfig",
    "AgentRunner",
    # Team
    "Team",
    "TeamStatus",
    "AgentPool",
    "TaskQueue",
    "SharedMemory",
    "MessageBus",
]
