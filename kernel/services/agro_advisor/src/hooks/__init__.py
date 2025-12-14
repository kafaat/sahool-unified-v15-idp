"""
SAHOOL Agro Advisor - Hooks
Event-driven automation hooks
"""

from .task_automation import FieldOpsClient, TaskAutomationHook, run_hook

__all__ = [
    "TaskAutomationHook",
    "FieldOpsClient",
    "run_hook",
]
