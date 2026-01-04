"""
LLM Cost Tracker
متتبع تكاليف نماذج اللغة
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Pricing per 1K tokens (approximate as of 2024)
LLM_PRICING = {
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "default": {"input": 0.01, "output": 0.03}
}

@dataclass
class UsageRecord:
    """Record of a single LLM usage"""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    user_id: str | None = None
    request_type: str | None = None

@dataclass
class CostTracker:
    """Tracks LLM costs per user/tenant"""

    # Cost limits
    daily_limit: float = 100.0  # $100/day
    monthly_limit: float = 2000.0  # $2000/month
    per_request_limit: float = 1.0  # $1/request

    # Storage
    _records: list = field(default_factory=list)
    _daily_costs: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    _monthly_costs: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request"""
        pricing = LLM_PRICING.get(model, LLM_PRICING["default"])
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        return round(input_cost + output_cost, 6)

    async def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        user_id: str | None = None,
        request_type: str | None = None
    ) -> UsageRecord:
        """Record LLM usage and return the record"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)

        record = UsageRecord(
            timestamp=datetime.now(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            user_id=user_id,
            request_type=request_type
        )

        async with self._lock:
            self._records.append(record)

            # Update daily/monthly aggregates
            date_key = record.timestamp.strftime("%Y-%m-%d")
            month_key = record.timestamp.strftime("%Y-%m")
            user_key = user_id or "anonymous"

            self._daily_costs[f"{user_key}:{date_key}"] += cost
            self._monthly_costs[f"{user_key}:{month_key}"] += cost

        # Log high-cost requests
        if cost > 0.1:
            logger.warning(f"High-cost request: ${cost:.4f} for {model}")

        return record

    async def check_budget(self, user_id: str | None = None) -> tuple[bool, str]:
        """Check if user is within budget limits"""
        user_key = user_id or "anonymous"
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")

        daily_cost = self._daily_costs.get(f"{user_key}:{today}", 0)
        monthly_cost = self._monthly_costs.get(f"{user_key}:{month}", 0)

        if daily_cost >= self.daily_limit:
            return False, f"Daily budget limit exceeded (${daily_cost:.2f}/${self.daily_limit})"

        if monthly_cost >= self.monthly_limit:
            return False, f"Monthly budget limit exceeded (${monthly_cost:.2f}/${self.monthly_limit})"

        return True, ""

    def get_usage_stats(self, user_id: str | None = None) -> dict:
        """Get usage statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        user_key = user_id or "anonymous"

        return {
            "daily_cost": self._daily_costs.get(f"{user_key}:{today}", 0),
            "monthly_cost": self._monthly_costs.get(f"{user_key}:{month}", 0),
            "daily_limit": self.daily_limit,
            "monthly_limit": self.monthly_limit,
            "total_requests": len(self._records)
        }

    def cleanup_old_records(self, days: int = 30):
        """Remove records older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        self._records = [r for r in self._records if r.timestamp > cutoff]


# Global cost tracker instance
cost_tracker = CostTracker()
