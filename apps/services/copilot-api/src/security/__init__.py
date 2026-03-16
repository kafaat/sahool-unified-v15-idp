"""
Copilot Security Module
وحدة أمان Copilot

Tool guardrails, access control, and security policies.
"""

from .allowlists import (
    BLOCKED_PATTERNS,
    DOMAIN_ALLOWLIST,
    MAX_ARGS_SIZE,
    MAX_PROMPT_CHARS,
    TOOL_ALLOWLIST,
)
from .guardrails import (
    ToolGuard,
    get_guard,
    guard_tool_call,
    is_domain_allowed,
    is_tool_allowed,
)

__all__ = [
    "ToolGuard",
    "get_guard",
    "guard_tool_call",
    "is_tool_allowed",
    "is_domain_allowed",
    "TOOL_ALLOWLIST",
    "DOMAIN_ALLOWLIST",
    "BLOCKED_PATTERNS",
    "MAX_ARGS_SIZE",
    "MAX_PROMPT_CHARS",
]
