"""
SAHOOL AI Guardrails Module
وحدة حواجز الحماية للذكاء الاصطناعي

Centralized guardrails for all AI operations in SAHOOL platform.
"""

from .allowlists import (
    BLOCKED_PATTERNS,
    DANGEROUS_COMMANDS,
    DOMAIN_ALLOWLIST,
    TOOL_ALLOWLIST,
)
from .policy import (
    GuardPolicy,
    PolicyRule,
    load_policy,
    save_policy,
)
from .tool_guard import (
    GuardDecision,
    ToolCallContext,
    ToolGuard,
    get_guard,
    guard_tool_call,
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
