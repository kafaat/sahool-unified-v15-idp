"""
AI Audit Logging Module
=======================
وحدة تسجيل تدقيق الذكاء الاصطناعي

Provides comprehensive audit logging for all AI operations including:
- Agent invocations and responses
- LLM provider calls and costs
- Safety violations and guardrail triggers
- Model version changes

Features:
    - Structured logging with correlation IDs
    - Cost tracking per operation
    - Safety scoring
    - Async batch writing
    - PostgreSQL and file-based storage

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Cost limits per tenant per hour/day (USD)
DEFAULT_HOURLY_COST_LIMIT = float(os.environ.get("AI_HOURLY_COST_LIMIT", "50.0"))
DEFAULT_DAILY_COST_LIMIT = float(os.environ.get("AI_DAILY_COST_LIMIT", "500.0"))

# Warning threshold as a fraction of the limit (e.g., warn at 80%)
COST_WARNING_THRESHOLD = float(os.environ.get("AI_COST_WARNING_THRESHOLD", "0.8"))


class AuditEventType(StrEnum):
    """Types of AI audit events."""

    # Agent Events
    AGENT_INVOCATION = "agent_invocation"
    AGENT_RESPONSE = "agent_response"
    AGENT_ERROR = "agent_error"

    # LLM Events
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    LLM_ERROR = "llm_error"
    LLM_FALLBACK = "llm_fallback"

    # Safety Events
    SAFETY_CHECK = "safety_check"
    SAFETY_VIOLATION = "safety_violation"
    GUARDRAIL_TRIGGERED = "guardrail_triggered"

    # Model Events
    MODEL_DEPLOYED = "model_deployed"
    MODEL_ROLLBACK = "model_rollback"

    # Auto-Fix Events
    AUTO_FIX_DIAGNOSE = "auto_fix_diagnose"
    AUTO_FIX_APPLY = "auto_fix_apply"
    AUTO_FIX_ROLLBACK = "auto_fix_rollback"


class SafetyLevel(StrEnum):
    """Safety levels for AI operations."""

    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


@dataclass
class AuditEvent:
    """
    A single AI audit event.

    حدث تدقيق واحد للذكاء الاصطناعي
    """

    id: str
    timestamp: datetime
    event_type: AuditEventType
    tenant_id: str
    user_id: str | None = None
    agent_id: str | None = None
    correlation_id: str | None = None

    # Request/Response data
    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    input_hash: str | None = None
    output_hash: str | None = None

    # Performance metrics
    latency_ms: float | None = None
    token_count_input: int | None = None
    token_count_output: int | None = None

    # Cost tracking
    cost_usd: float | None = None
    llm_provider: str | None = None
    model_name: str | None = None

    # Safety tracking
    safety_level: SafetyLevel = SafetyLevel.SAFE
    safety_score: float | None = None
    safety_details: dict[str, Any] | None = None

    # Error tracking
    error_message: str | None = None
    error_code: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "correlation_id": self.correlation_id,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "latency_ms": self.latency_ms,
            "token_count_input": self.token_count_input,
            "token_count_output": self.token_count_output,
            "cost_usd": self.cost_usd,
            "llm_provider": self.llm_provider,
            "model_name": self.model_name,
            "safety_level": self.safety_level.value,
            "safety_score": self.safety_score,
            "safety_details": self.safety_details,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)


# LLM Provider Cost Configuration (per 1K tokens)
LLM_COSTS = {
    "anthropic": {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
        "claude-opus-4": {"input": 0.015, "output": 0.075},
    },
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    },
    "google": {
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    },
    "ollama": {
        # Local models - no API cost, only compute
        "codellama:7b": {"input": 0.0, "output": 0.0},
        "codellama:13b": {"input": 0.0, "output": 0.0},
        "deepseek-coder:6.7b": {"input": 0.0, "output": 0.0},
        "llama2:7b": {"input": 0.0, "output": 0.0},
    },
}


def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Calculate the cost of an LLM call.

    حساب تكلفة طلب LLM

    Args:
        provider: LLM provider name
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    provider_costs = LLM_COSTS.get(provider.lower(), {})

    # Try exact match first, then partial match
    model_costs = provider_costs.get(model.lower())
    if not model_costs:
        for model_key, costs in provider_costs.items():
            if model_key in model.lower() or model.lower() in model_key:
                model_costs = costs
                break

    if not model_costs:
        return 0.0

    input_cost = (input_tokens / 1000) * model_costs["input"]
    output_cost = (output_tokens / 1000) * model_costs["output"]

    return round(input_cost + output_cost, 6)


def hash_content(content: str | dict | None) -> str | None:
    """Generate a hash of content for audit trail."""
    if content is None:
        return None

    import hashlib

    if isinstance(content, dict):
        content = json.dumps(content, sort_keys=True, ensure_ascii=False)

    return hashlib.sha256(content.encode()).hexdigest()[:16]


class CostLimitExceeded(Exception):
    """Raised when a tenant exceeds their AI cost limit.

    يُطرح عندما يتجاوز المستأجر حد تكلفة الذكاء الاصطناعي
    """

    def __init__(self, tenant_id: str, window: str, current_cost: float, limit: float):
        self.tenant_id = tenant_id
        self.window = window
        self.current_cost = current_cost
        self.limit = limit
        super().__init__(
            f"AI cost limit exceeded for tenant '{tenant_id}': "
            f"{window} cost ${current_cost:.4f} >= limit ${limit:.2f}"
        )


class CostTracker:
    """In-memory cost tracker per tenant with hourly and daily windows.

    متتبع التكلفة في الذاكرة لكل مستأجر مع نوافذ بالساعة واليوم
    """

    def __init__(
        self,
        hourly_limit: float = DEFAULT_HOURLY_COST_LIMIT,
        daily_limit: float = DEFAULT_DAILY_COST_LIMIT,
    ):
        self.hourly_limit = hourly_limit
        self.daily_limit = daily_limit
        # {tenant_id: {"hourly_cost": float, "hourly_reset": datetime,
        #              "daily_cost": float, "daily_reset": datetime}}
        self._tenant_costs: dict[str, dict[str, Any]] = {}

    def _get_or_create(self, tenant_id: str) -> dict[str, Any]:
        """Get or initialize cost tracking entry for a tenant."""
        now = datetime.now(UTC)
        if tenant_id not in self._tenant_costs:
            self._tenant_costs[tenant_id] = {
                "hourly_cost": 0.0,
                "hourly_reset": now,
                "daily_cost": 0.0,
                "daily_reset": now,
            }
        entry = self._tenant_costs[tenant_id]

        # Reset hourly window if more than 1 hour has passed
        hourly_elapsed = (now - entry["hourly_reset"]).total_seconds()
        if hourly_elapsed >= 3600:
            entry["hourly_cost"] = 0.0
            entry["hourly_reset"] = now

        # Reset daily window if more than 24 hours have passed
        daily_elapsed = (now - entry["daily_reset"]).total_seconds()
        if daily_elapsed >= 86400:
            entry["daily_cost"] = 0.0
            entry["daily_reset"] = now

        return entry

    def check_cost_limit(self, tenant_id: str, additional_cost: float = 0.0) -> bool:
        """Check if a tenant is within cost limits.

        Args:
            tenant_id: Tenant identifier
            additional_cost: Prospective cost to add (for pre-check)

        Returns:
            True if within limits, False if limit would be exceeded.

        Raises:
            CostLimitExceeded: When the limit is exceeded and additional_cost > 0.
        """
        entry = self._get_or_create(tenant_id)
        projected_hourly = entry["hourly_cost"] + additional_cost
        projected_daily = entry["daily_cost"] + additional_cost

        # Check hourly limit
        if projected_hourly >= self.hourly_limit:
            logger.warning(
                "AI hourly cost limit exceeded for tenant %s: $%.4f >= $%.2f",
                tenant_id, projected_hourly, self.hourly_limit,
            )
            if additional_cost > 0:
                raise CostLimitExceeded(
                    tenant_id, "hourly", projected_hourly, self.hourly_limit,
                )
            return False

        # Check daily limit
        if projected_daily >= self.daily_limit:
            logger.warning(
                "AI daily cost limit exceeded for tenant %s: $%.4f >= $%.2f",
                tenant_id, projected_daily, self.daily_limit,
            )
            if additional_cost > 0:
                raise CostLimitExceeded(
                    tenant_id, "daily", projected_daily, self.daily_limit,
                )
            return False

        # Warn when approaching limits
        if projected_hourly >= self.hourly_limit * COST_WARNING_THRESHOLD:
            logger.warning(
                "AI hourly cost approaching limit for tenant %s: $%.4f / $%.2f (%.0f%%)",
                tenant_id, projected_hourly, self.hourly_limit,
                (projected_hourly / self.hourly_limit) * 100,
            )
        if projected_daily >= self.daily_limit * COST_WARNING_THRESHOLD:
            logger.warning(
                "AI daily cost approaching limit for tenant %s: $%.4f / $%.2f (%.0f%%)",
                tenant_id, projected_daily, self.daily_limit,
                (projected_daily / self.daily_limit) * 100,
            )

        return True

    def record_cost(self, tenant_id: str, cost: float) -> None:
        """Record a cost for a tenant."""
        entry = self._get_or_create(tenant_id)
        entry["hourly_cost"] += cost
        entry["daily_cost"] += cost

    def get_tenant_usage(self, tenant_id: str) -> dict[str, Any]:
        """Get current cost usage for a tenant."""
        entry = self._get_or_create(tenant_id)
        return {
            "tenant_id": tenant_id,
            "hourly_cost": round(entry["hourly_cost"], 4),
            "hourly_limit": self.hourly_limit,
            "hourly_remaining": round(max(0, self.hourly_limit - entry["hourly_cost"]), 4),
            "daily_cost": round(entry["daily_cost"], 4),
            "daily_limit": self.daily_limit,
            "daily_remaining": round(max(0, self.daily_limit - entry["daily_cost"]), 4),
        }


# Global cost tracker instance
_cost_tracker: CostTracker | None = None


def get_cost_tracker() -> CostTracker:
    """Get or create the global cost tracker."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker


class AIAuditLogger:
    """
    Centralized audit logger for AI operations.

    مسجل تدقيق مركزي لعمليات الذكاء الاصطناعي

    Example:
        logger = AIAuditLogger(tenant_id="sahool")

        # Log agent invocation
        event = logger.log_agent_invocation(
            agent_id="field-analyst",
            input_data={"query": "What is the NDVI for field 003?"},
            user_id="farmer-123"
        )

        # Log response with cost
        logger.log_agent_response(
            correlation_id=event.correlation_id,
            output_data={"ndvi": 0.72, "health": "good"},
            latency_ms=1250,
            token_count_input=150,
            token_count_output=80,
            llm_provider="anthropic",
            model_name="claude-3-haiku"
        )

        # Get audit summary
        summary = logger.get_summary()
    """

    def __init__(
        self,
        tenant_id: str,
        storage_path: str | None = None,
        max_buffer_size: int = 100,
        flush_interval_seconds: float = 30.0,
        on_event_callback: Callable[[AuditEvent], None] | None = None,
    ):
        """
        Initialize AIAuditLogger.

        Args:
            tenant_id: Tenant identifier
            storage_path: Path for file-based storage (optional)
            max_buffer_size: Max events before auto-flush
            flush_interval_seconds: Auto-flush interval
            on_event_callback: Callback for each event (for external systems)
        """
        self.tenant_id = tenant_id
        self.storage_path = storage_path
        self.max_buffer_size = max_buffer_size
        self.flush_interval_seconds = flush_interval_seconds
        self.on_event_callback = on_event_callback

        self._buffer: list[AuditEvent] = []
        self._events: list[AuditEvent] = []
        self._lock = asyncio.Lock()

        # Metrics
        self._total_events = 0
        self._total_cost = 0.0
        self._total_tokens_input = 0
        self._total_tokens_output = 0
        self._safety_violations = 0

        # Ensure storage directory exists
        if storage_path:
            Path(storage_path).mkdir(parents=True, exist_ok=True)

    def _create_event(
        self,
        event_type: AuditEventType,
        **kwargs,
    ) -> AuditEvent:
        """Create a new audit event."""
        event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            event_type=event_type,
            tenant_id=self.tenant_id,
            **kwargs,
        )

        # Update metrics
        self._total_events += 1
        if event.cost_usd:
            self._total_cost += event.cost_usd
        if event.token_count_input:
            self._total_tokens_input += event.token_count_input
        if event.token_count_output:
            self._total_tokens_output += event.token_count_output
        if event.safety_level in [SafetyLevel.HIGH_RISK, SafetyLevel.BLOCKED]:
            self._safety_violations += 1

        # Add to buffer
        self._buffer.append(event)
        self._events.append(event)

        # Trigger callback if set
        if self.on_event_callback:
            self.on_event_callback(event)

        # Auto-flush if buffer is full
        if len(self._buffer) >= self.max_buffer_size:
            asyncio.create_task(self.flush())

        return event

    def log_agent_invocation(
        self,
        agent_id: str,
        input_data: dict[str, Any],
        user_id: str | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log an agent invocation.

        تسجيل استدعاء وكيل
        """
        return self._create_event(
            event_type=AuditEventType.AGENT_INVOCATION,
            agent_id=agent_id,
            user_id=user_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            input_data=input_data,
            input_hash=hash_content(input_data),
            metadata=metadata or {},
        )

    def log_agent_response(
        self,
        correlation_id: str,
        output_data: dict[str, Any],
        latency_ms: float,
        token_count_input: int = 0,
        token_count_output: int = 0,
        llm_provider: str | None = None,
        model_name: str | None = None,
        safety_score: float | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log an agent response.

        تسجيل استجابة وكيل
        """
        # Calculate cost
        cost_usd = 0.0
        if llm_provider and model_name and token_count_input and token_count_output:
            cost_usd = calculate_cost(llm_provider, model_name, token_count_input, token_count_output)

        # Enforce cost limits
        if cost_usd > 0:
            tracker = get_cost_tracker()
            # Check limit (logs warning when approaching, raises on exceed)
            try:
                tracker.check_cost_limit(self.tenant_id, additional_cost=cost_usd)
            except CostLimitExceeded:
                logger.error(
                    "Cost limit exceeded for tenant %s, cost=$%.4f blocked",
                    self.tenant_id, cost_usd,
                )
                raise
            tracker.record_cost(self.tenant_id, cost_usd)

        # Determine safety level from score
        safety_level = SafetyLevel.SAFE
        if safety_score is not None:
            if safety_score < 0.3:
                safety_level = SafetyLevel.HIGH_RISK
            elif safety_score < 0.5:
                safety_level = SafetyLevel.MEDIUM_RISK
            elif safety_score < 0.7:
                safety_level = SafetyLevel.LOW_RISK

        return self._create_event(
            event_type=AuditEventType.AGENT_RESPONSE,
            agent_id=agent_id,
            user_id=user_id,
            correlation_id=correlation_id,
            output_data=output_data,
            output_hash=hash_content(output_data),
            latency_ms=latency_ms,
            token_count_input=token_count_input,
            token_count_output=token_count_output,
            cost_usd=cost_usd,
            llm_provider=llm_provider,
            model_name=model_name,
            safety_level=safety_level,
            safety_score=safety_score,
            metadata=metadata or {},
        )

    def log_agent_error(
        self,
        correlation_id: str,
        error_message: str,
        error_code: str | None = None,
        agent_id: str | None = None,
        latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log an agent error.

        تسجيل خطأ وكيل
        """
        return self._create_event(
            event_type=AuditEventType.AGENT_ERROR,
            agent_id=agent_id,
            correlation_id=correlation_id,
            error_message=error_message,
            error_code=error_code,
            latency_ms=latency_ms,
            safety_level=SafetyLevel.MEDIUM_RISK,
            metadata=metadata or {},
        )

    def log_llm_request(
        self,
        llm_provider: str,
        model_name: str,
        input_data: dict[str, Any],
        correlation_id: str | None = None,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log an LLM request.

        تسجيل طلب LLM
        """
        return self._create_event(
            event_type=AuditEventType.LLM_REQUEST,
            agent_id=agent_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            input_data=input_data,
            input_hash=hash_content(input_data),
            llm_provider=llm_provider,
            model_name=model_name,
            metadata=metadata or {},
        )

    def log_llm_response(
        self,
        correlation_id: str,
        llm_provider: str,
        model_name: str,
        output_data: dict[str, Any],
        latency_ms: float,
        token_count_input: int,
        token_count_output: int,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log an LLM response.

        تسجيل استجابة LLM
        """
        cost_usd = calculate_cost(llm_provider, model_name, token_count_input, token_count_output)

        # Enforce cost limits
        if cost_usd > 0:
            tracker = get_cost_tracker()
            try:
                tracker.check_cost_limit(self.tenant_id, additional_cost=cost_usd)
            except CostLimitExceeded:
                logger.error(
                    "Cost limit exceeded for tenant %s, cost=$%.4f blocked",
                    self.tenant_id, cost_usd,
                )
                raise
            tracker.record_cost(self.tenant_id, cost_usd)

        return self._create_event(
            event_type=AuditEventType.LLM_RESPONSE,
            agent_id=agent_id,
            correlation_id=correlation_id,
            output_data=output_data,
            output_hash=hash_content(output_data),
            latency_ms=latency_ms,
            token_count_input=token_count_input,
            token_count_output=token_count_output,
            cost_usd=cost_usd,
            llm_provider=llm_provider,
            model_name=model_name,
            metadata=metadata or {},
        )

    def log_llm_fallback(
        self,
        correlation_id: str,
        from_provider: str,
        to_provider: str,
        reason: str,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log an LLM provider fallback.

        تسجيل انتقال احتياطي لـ LLM
        """
        return self._create_event(
            event_type=AuditEventType.LLM_FALLBACK,
            agent_id=agent_id,
            correlation_id=correlation_id,
            llm_provider=to_provider,
            error_message=reason,
            metadata={
                "from_provider": from_provider,
                "to_provider": to_provider,
                **(metadata or {}),
            },
        )

    def log_safety_violation(
        self,
        correlation_id: str,
        violation_type: str,
        severity: SafetyLevel,
        details: dict[str, Any],
        agent_id: str | None = None,
        user_id: str | None = None,
        blocked: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log a safety violation.

        تسجيل انتهاك أمان
        """
        return self._create_event(
            event_type=AuditEventType.SAFETY_VIOLATION,
            agent_id=agent_id,
            user_id=user_id,
            correlation_id=correlation_id,
            safety_level=SafetyLevel.BLOCKED if blocked else severity,
            safety_details={
                "violation_type": violation_type,
                "blocked": blocked,
                **details,
            },
            metadata=metadata or {},
        )

    def log_auto_fix(
        self,
        action: str,
        files_affected: list[str],
        fixes_count: int,
        success: bool,
        details: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log an auto-fix operation.

        تسجيل عملية إصلاح تلقائي
        """
        event_type = {
            "diagnose": AuditEventType.AUTO_FIX_DIAGNOSE,
            "apply": AuditEventType.AUTO_FIX_APPLY,
            "rollback": AuditEventType.AUTO_FIX_ROLLBACK,
        }.get(action, AuditEventType.AUTO_FIX_APPLY)

        return self._create_event(
            event_type=event_type,
            correlation_id=correlation_id or str(uuid.uuid4()),
            output_data={
                "action": action,
                "files_affected": files_affected,
                "fixes_count": fixes_count,
                "success": success,
                **(details or {}),
            },
            safety_level=SafetyLevel.SAFE if success else SafetyLevel.MEDIUM_RISK,
            metadata=metadata or {},
        )

    async def flush(self) -> int:
        """
        Flush buffered events to storage.

        Returns:
            Number of events flushed
        """
        async with self._lock:
            if not self._buffer:
                return 0

            events_to_flush = self._buffer.copy()
            self._buffer.clear()

        # Write to file if storage path configured
        if self.storage_path:
            filename = f"ai_audit_{datetime.now(UTC).strftime('%Y%m%d')}.jsonl"
            filepath = os.path.join(self.storage_path, filename)

            with open(filepath, "a", encoding="utf-8") as f:
                for event in events_to_flush:
                    f.write(event.to_json() + "\n")

        return len(events_to_flush)

    def get_events(
        self,
        event_type: AuditEventType | None = None,
        agent_id: str | None = None,
        correlation_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """
        Get filtered audit events.

        الحصول على أحداث التدقيق المفلترة
        """
        events = self._events

        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if agent_id:
            events = [e for e in events if e.agent_id == agent_id]
        if correlation_id:
            events = [e for e in events if e.correlation_id == correlation_id]
        if since:
            events = [e for e in events if e.timestamp >= since]

        return events[-limit:]

    def get_summary(self) -> dict[str, Any]:
        """
        Get audit summary statistics.

        الحصول على ملخص إحصائيات التدقيق
        """
        return {
            "tenant_id": self.tenant_id,
            "total_events": self._total_events,
            "total_cost_usd": round(self._total_cost, 4),
            "total_tokens_input": self._total_tokens_input,
            "total_tokens_output": self._total_tokens_output,
            "total_tokens": self._total_tokens_input + self._total_tokens_output,
            "safety_violations": self._safety_violations,
            "events_by_type": self._count_by_type(),
            "cost_by_provider": self._cost_by_provider(),
            "buffer_size": len(self._buffer),
        }

    def _count_by_type(self) -> dict[str, int]:
        """Count events by type."""
        counts: dict[str, int] = {}
        for event in self._events:
            key = event.event_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _cost_by_provider(self) -> dict[str, float]:
        """Calculate cost by provider."""
        costs: dict[str, float] = {}
        for event in self._events:
            if event.llm_provider and event.cost_usd:
                costs[event.llm_provider] = costs.get(event.llm_provider, 0) + event.cost_usd
        return {k: round(v, 4) for k, v in costs.items()}

    def clear(self) -> None:
        """Clear all events and reset metrics."""
        self._buffer.clear()
        self._events.clear()
        self._total_events = 0
        self._total_cost = 0.0
        self._total_tokens_input = 0
        self._total_tokens_output = 0
        self._safety_violations = 0


# Global audit logger instance (lazy initialization)
_global_logger: AIAuditLogger | None = None


def get_audit_logger(tenant_id: str = "sahool") -> AIAuditLogger:
    """
    Get or create the global audit logger.

    الحصول على أو إنشاء مسجل التدقيق العالمي
    """
    global _global_logger
    if _global_logger is None or _global_logger.tenant_id != tenant_id:
        import tempfile

        default_path = os.path.join(tempfile.gettempdir(), "sahool_ai_audit")
        storage_path = os.getenv("AI_AUDIT_STORAGE_PATH", default_path)
        _global_logger = AIAuditLogger(tenant_id=tenant_id, storage_path=storage_path)
    return _global_logger


# Convenience functions
def log_agent_call(
    agent_id: str,
    input_data: dict[str, Any],
    output_data: dict[str, Any],
    latency_ms: float,
    token_count_input: int = 0,
    token_count_output: int = 0,
    llm_provider: str = "anthropic",
    model_name: str = "claude-3-haiku",
    user_id: str | None = None,
    tenant_id: str = "sahool",
) -> tuple[AuditEvent, AuditEvent]:
    """
    Convenience function to log a complete agent call.

    دالة مساعدة لتسجيل استدعاء وكيل كامل
    """
    logger = get_audit_logger(tenant_id)

    invocation = logger.log_agent_invocation(
        agent_id=agent_id,
        input_data=input_data,
        user_id=user_id,
    )

    response = logger.log_agent_response(
        correlation_id=invocation.correlation_id,
        output_data=output_data,
        latency_ms=latency_ms,
        token_count_input=token_count_input,
        token_count_output=token_count_output,
        llm_provider=llm_provider,
        model_name=model_name,
        agent_id=agent_id,
        user_id=user_id,
    )

    return invocation, response


def get_cost_summary(tenant_id: str = "sahool") -> dict[str, Any]:
    """
    Get cost summary for a tenant.

    الحصول على ملخص التكلفة للمستأجر
    """
    logger = get_audit_logger(tenant_id)
    summary = logger.get_summary()
    return {
        "total_cost_usd": summary["total_cost_usd"],
        "total_tokens": summary["total_tokens"],
        "cost_by_provider": summary["cost_by_provider"],
        "total_requests": summary["total_events"],
    }
