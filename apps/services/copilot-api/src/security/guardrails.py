"""
Tool Guardrails System
نظام حواجز حماية الأدوات

ToolSafe-inspired guardrails for secure tool execution.
Implements multi-layer validation before any tool call.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import fnmatch
import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from typing import Any, Optional

import structlog

from .allowlists import (
    BLOCKED_PATTERNS,
    DANGEROUS_COMMANDS,
    DOMAIN_ALLOWLIST,
    ENABLE_EXTERNAL,
    MAX_ARGS_SIZE,
    MAX_FILES_CHANGED,
    TOOL_ALLOWLIST,
)

logger = structlog.get_logger(__name__)

# Domain validation regex
_DOMAIN_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$")


@dataclass
class GuardDecision:
    """
    Result of a guard check.
    نتيجة فحص الحماية
    """

    allowed: bool
    reason: str
    reason_ar: str = ""
    layer: str = "unknown"
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "reason_ar": self.reason_ar,
            "layer": self.layer,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ToolCallContext:
    """
    Context for a tool call.
    سياق استدعاء الأداة
    """

    tool: str
    args: dict[str, Any]
    session_id: str | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class ToolGuard:
    """
    Multi-layer tool call guardrails.
    حواجز حماية متعددة الطبقات لاستدعاءات الأدوات

    Implements:
    - Layer 1: Tool Allowlist
    - Layer 2: Size Validation
    - Layer 3: Pattern Blocking
    - Layer 4: External Access Control
    - Layer 5: Dangerous Command Detection
    - Layer 6: Custom Validators
    """

    def __init__(
        self,
        tool_allowlist: frozenset[str] | None = None,
        domain_allowlist: frozenset[str] | None = None,
        blocked_patterns: frozenset[str] | None = None,
        enable_external: bool | None = None,
        custom_validators: list[Callable[[ToolCallContext], GuardDecision | None]] | None = None,
        audit_callback: Callable[[ToolCallContext, GuardDecision], None] | None = None,
    ):
        """
        Initialize ToolGuard.

        Args:
            tool_allowlist: Set of allowed tool names
            domain_allowlist: Set of allowed domains
            blocked_patterns: Set of blocked file patterns
            enable_external: Whether external access is allowed
            custom_validators: Custom validation functions
            audit_callback: Callback for audit logging
        """
        self.tool_allowlist = tool_allowlist or TOOL_ALLOWLIST
        self.domain_allowlist = domain_allowlist or DOMAIN_ALLOWLIST
        self.blocked_patterns = blocked_patterns or BLOCKED_PATTERNS
        self.enable_external = enable_external if enable_external is not None else ENABLE_EXTERNAL
        self.custom_validators = custom_validators or []
        self.audit_callback = audit_callback

        # Statistics
        self._stats = {
            "total_checks": 0,
            "allowed": 0,
            "blocked": 0,
            "by_layer": {},
        }

    def check(self, context: ToolCallContext) -> GuardDecision:
        """
        Perform all guard checks on a tool call.
        إجراء جميع فحوصات الحماية على استدعاء أداة

        Args:
            context: Tool call context

        Returns:
            GuardDecision with result
        """
        start_time = time.time()
        self._stats["total_checks"] += 1

        # Layer 1: Tool Allowlist
        decision = self._check_tool_allowlist(context)
        if not decision.allowed:
            self._record_block("tool_allowlist", context, decision)
            return decision

        # Layer 2: Size Validation
        decision = self._check_size_limits(context)
        if not decision.allowed:
            self._record_block("size_limits", context, decision)
            return decision

        # Layer 3: Pattern Blocking
        decision = self._check_blocked_patterns(context)
        if not decision.allowed:
            self._record_block("blocked_patterns", context, decision)
            return decision

        # Layer 4: External Access Control
        decision = self._check_external_access(context)
        if not decision.allowed:
            self._record_block("external_access", context, decision)
            return decision

        # Layer 5: Dangerous Command Detection
        decision = self._check_dangerous_commands(context)
        if not decision.allowed:
            self._record_block("dangerous_commands", context, decision)
            return decision

        # Layer 6: Custom Validators
        for validator in self.custom_validators:
            try:
                custom_decision = validator(context)
                if custom_decision and not custom_decision.allowed:
                    self._record_block("custom_validator", context, custom_decision)
                    return custom_decision
            except Exception as e:
                logger.warning("Custom validator error", error=str(e))

        # All checks passed
        elapsed_ms = (time.time() - start_time) * 1000
        self._stats["allowed"] += 1

        decision = GuardDecision(
            allowed=True,
            reason="All guard checks passed",
            reason_ar="جميع فحوصات الحماية ناجحة",
            layer="all",
            details={"check_time_ms": elapsed_ms},
        )

        if self.audit_callback:
            self.audit_callback(context, decision)

        return decision

    def _check_tool_allowlist(self, context: ToolCallContext) -> GuardDecision:
        """Layer 1: Check if tool is in allowlist"""
        tool = context.tool

        if tool in self.tool_allowlist:
            return GuardDecision(
                allowed=True,
                reason="Tool is allowed",
                reason_ar="الأداة مسموحة",
                layer="tool_allowlist",
            )

        # Check for wildcard matches (e.g., "code.*" matches "code.analyze")
        tool_prefix = tool.rsplit(".", 1)[0] + ".*" if "." in tool else tool + ".*"
        if tool_prefix in self.tool_allowlist:
            return GuardDecision(
                allowed=True,
                reason="Tool matches wildcard pattern",
                reason_ar="الأداة تطابق نمط عام",
                layer="tool_allowlist",
            )

        return GuardDecision(
            allowed=False,
            reason=f"Tool '{tool}' is not in the allowlist",
            reason_ar=f"الأداة '{tool}' ليست في قائمة المسموحات",
            layer="tool_allowlist",
            details={"tool": tool, "allowed_count": len(self.tool_allowlist)},
        )

    def _check_size_limits(self, context: ToolCallContext) -> GuardDecision:
        """Layer 2: Check argument size limits"""
        try:
            serialized = json.dumps(context.args, ensure_ascii=False)
            size = len(serialized)

            if size > MAX_ARGS_SIZE:
                return GuardDecision(
                    allowed=False,
                    reason=f"Tool arguments too large: {size} > {MAX_ARGS_SIZE} bytes",
                    reason_ar=f"وسائط الأداة كبيرة جداً: {size} > {MAX_ARGS_SIZE} بايت",
                    layer="size_limits",
                    details={"size": size, "max_size": MAX_ARGS_SIZE},
                )

            return GuardDecision(
                allowed=True,
                reason="Size within limits",
                reason_ar="الحجم ضمن الحدود",
                layer="size_limits",
            )

        except (TypeError, ValueError) as e:
            return GuardDecision(
                allowed=False,
                reason=f"Cannot serialize tool arguments: {e}",
                reason_ar=f"لا يمكن تسلسل وسائط الأداة: {e}",
                layer="size_limits",
            )

    def _check_blocked_patterns(self, context: ToolCallContext) -> GuardDecision:
        """Layer 3: Check for blocked file patterns"""
        args_str = json.dumps(context.args, ensure_ascii=False)

        for pattern in self.blocked_patterns:
            # Check if pattern appears in args
            if fnmatch.fnmatch(args_str, f"*{pattern}*"):
                return GuardDecision(
                    allowed=False,
                    reason=f"Blocked pattern detected: {pattern}",
                    reason_ar=f"تم اكتشاف نمط محظور: {pattern}",
                    layer="blocked_patterns",
                    details={"pattern": pattern},
                )

            # Check specific path arguments
            for key in ("path", "file", "file_path", "target", "source"):
                if key in context.args:
                    path = str(context.args[key])
                    # Normalize path separators
                    path_normalized = path.replace("\\", "/")
                    if fnmatch.fnmatch(path_normalized, pattern):
                        return GuardDecision(
                            allowed=False,
                            reason=f"Path matches blocked pattern: {pattern}",
                            reason_ar=f"المسار يطابق نمط محظور: {pattern}",
                            layer="blocked_patterns",
                            details={"path": path, "pattern": pattern},
                        )

        return GuardDecision(
            allowed=True,
            reason="No blocked patterns found",
            reason_ar="لم يتم العثور على أنماط محظورة",
            layer="blocked_patterns",
        )

    def _check_external_access(self, context: ToolCallContext) -> GuardDecision:
        """Layer 4: Check external access permissions"""
        # Check if this is an external tool
        if context.tool.startswith("external."):
            if not self.enable_external:
                return GuardDecision(
                    allowed=False,
                    reason="External access is disabled",
                    reason_ar="الوصول الخارجي معطل",
                    layer="external_access",
                )

        # Check for URL/host arguments
        for key in ("url", "host", "domain", "endpoint", "base_url"):
            if key in context.args:
                host = str(context.args[key]).lower().strip()

                # Extract domain from URL if needed
                if "://" in host:
                    from urllib.parse import urlparse

                    parsed = urlparse(host)
                    host = parsed.hostname or ""

                if not self._is_domain_allowed(host):
                    return GuardDecision(
                        allowed=False,
                        reason=f"Domain '{host}' is not in the allowlist",
                        reason_ar=f"النطاق '{host}' ليس في قائمة المسموحات",
                        layer="external_access",
                        details={"domain": host},
                    )

        return GuardDecision(
            allowed=True,
            reason="External access check passed",
            reason_ar="فحص الوصول الخارجي ناجح",
            layer="external_access",
        )

    def _check_dangerous_commands(self, context: ToolCallContext) -> GuardDecision:
        """Layer 5: Check for dangerous commands"""
        args_str = json.dumps(context.args, ensure_ascii=False).lower()

        for dangerous in DANGEROUS_COMMANDS:
            if dangerous.lower() in args_str:
                return GuardDecision(
                    allowed=False,
                    reason=f"Dangerous command detected: {dangerous}",
                    reason_ar=f"تم اكتشاف أمر خطير: {dangerous}",
                    layer="dangerous_commands",
                    details={"command": dangerous},
                )

        return GuardDecision(
            allowed=True,
            reason="No dangerous commands detected",
            reason_ar="لم يتم اكتشاف أوامر خطيرة",
            layer="dangerous_commands",
        )

    def _is_domain_allowed(self, host: str) -> bool:
        """Check if a domain is in the allowlist"""
        host = host.lower().strip()

        if not host:
            return False

        if not _DOMAIN_RE.match(host):
            # Allow localhost and IP addresses
            if host in ("localhost", "127.0.0.1", "::1"):
                return True
            return False

        # Exact match or subdomain match
        return any(host == domain or host.endswith("." + domain) for domain in self.domain_allowlist)

    def _record_block(self, layer: str, context: ToolCallContext, decision: GuardDecision) -> None:
        """Record a blocked call"""
        self._stats["blocked"] += 1
        self._stats["by_layer"][layer] = self._stats["by_layer"].get(layer, 0) + 1

        logger.warning(
            "Tool call blocked",
            tool=context.tool,
            layer=layer,
            reason=decision.reason,
            session_id=context.session_id,
        )

        if self.audit_callback:
            self.audit_callback(context, decision)

    def get_stats(self) -> dict[str, Any]:
        """Get guard statistics"""
        return {
            **self._stats,
            "block_rate": (
                self._stats["blocked"] / self._stats["total_checks"] if self._stats["total_checks"] > 0 else 0
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global guard instance
_global_guard: ToolGuard | None = None


def get_guard() -> ToolGuard:
    """Get or create global ToolGuard instance"""
    global _global_guard
    if _global_guard is None:
        _global_guard = ToolGuard()
    return _global_guard


def guard_tool_call(
    tool: str,
    args: dict[str, Any],
    session_id: str | None = None,
) -> GuardDecision:
    """
    Convenience function to check a tool call.
    دالة مساعدة لفحص استدعاء أداة

    Args:
        tool: Tool name
        args: Tool arguments
        session_id: Session identifier

    Returns:
        GuardDecision with result
    """
    context = ToolCallContext(
        tool=tool,
        args=args,
        session_id=session_id,
    )
    return get_guard().check(context)


def is_tool_allowed(tool: str) -> bool:
    """Check if a tool is in the allowlist"""
    return tool in TOOL_ALLOWLIST


def is_domain_allowed(domain: str) -> bool:
    """Check if a domain is in the allowlist"""
    return get_guard()._is_domain_allowed(domain)
