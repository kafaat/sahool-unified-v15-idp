"""
SAHOOL Coordinator Agent Layer
طبقة وكيل المنسق

Master coordination agent for:
- Conflict resolution between agents
- Priority-based decision making
- Resource allocation
- Unified recommendations
"""

from .master_coordinator import MasterCoordinatorAgent

__all__ = ["MasterCoordinatorAgent"]
