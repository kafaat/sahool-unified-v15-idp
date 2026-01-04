"""
SAHOOL Action Contracts
عقود الإجراءات - Field-First Action Templates

هذه الوحدة تعرّف قوالب الإجراءات الموحدة التي تُنتجها خدمات التحليل
وتُستهلك من الميدان (Mobile/Web)
"""

from .factory import ActionTemplateFactory
from .template import (
    ActionStep,
    ActionTemplate,
    Resource,
    TimeWindow,
)
from .types import (
    ActionStatus,
    ActionType,
    ResourceType,
    UrgencyLevel,
)

__all__ = [
    # Types
    "ActionType",
    "ActionStatus",
    "UrgencyLevel",
    "ResourceType",
    # Models
    "ActionTemplate",
    "ActionStep",
    "Resource",
    "TimeWindow",
    # Factory
    "ActionTemplateFactory",
]
