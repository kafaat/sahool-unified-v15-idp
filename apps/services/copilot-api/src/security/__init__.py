"""
Copilot Security Module
وحدة أمان Copilot

Tool guardrails, access control, and security policies.
"""

from .guardrails import (
    ToolGuard,
    guard_tool_call,
    is_tool_allowed,
    is_domain_allowed,
)
from .allowlists import (
    TOOL_ALLOWLIST,
    DOMAIN_ALLOWLIST,
    BLOCKED_PATTERNS,
    MAX_ARGS_SIZE,
    MAX_PROMPT_CHARS,
)

__all__ = [
    "ToolGuard",
    "guard_tool_call",
    "is_tool_allowed",
    "is_domain_allowed",
    "TOOL_ALLOWLIST",
    "DOMAIN_ALLOWLIST",
    "BLOCKED_PATTERNS",
    "MAX_ARGS_SIZE",
    "MAX_PROMPT_CHARS",
]
