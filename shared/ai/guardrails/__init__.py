"""
SAHOOL AI Guardrails Module
وحدة حواجز الحماية للذكاء الاصطناعي

Centralized guardrails for all AI operations in SAHOOL platform.
"""

from .tool_guard import (
    ToolGuard,
    GuardDecision,
    ToolCallContext,
    guard_tool_call,
    get_guard,
)
from .allowlists import (
    TOOL_ALLOWLIST,
    DOMAIN_ALLOWLIST,
    BLOCKED_PATTERNS,
    DANGEROUS_COMMANDS,
)
from .policy import (
    GuardPolicy,
    PolicyRule,
    load_policy,
    save_policy,
)

__all__ = [
    "ToolGuard",
    "GuardDecision",
    "ToolCallContext",
    "guard_tool_call",
    "get_guard",
    "TOOL_ALLOWLIST",
    "DOMAIN_ALLOWLIST",
    "BLOCKED_PATTERNS",
    "DANGEROUS_COMMANDS",
    "GuardPolicy",
    "PolicyRule",
    "load_policy",
    "save_policy",
]
