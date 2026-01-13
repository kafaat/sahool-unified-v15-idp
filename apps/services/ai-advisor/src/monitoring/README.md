# LLM Cost Monitoring System

## Overview

The AI Advisor service includes comprehensive cost tracking for all LLM (Language Model) usage. This system monitors token usage, calculates costs, and enforces budget limits across all supported providers (Anthropic Claude, OpenAI GPT, Google Gemini).

## Features

- **Real-time Cost Tracking**: Automatically tracks input/output tokens and calculates costs for every LLM request
- **Multi-Provider Support**: Works seamlessly with Anthropic Claude, OpenAI GPT, and Google Gemini
- **Budget Limits**: Configurable daily and monthly spending limits
- **Per-User Tracking**: Track costs per user or tenant (optional)
- **Usage Statistics**: Detailed statistics via REST API endpoint
- **High-Cost Alerts**: Automatic logging of expensive requests

## Architecture

### Cost Tracker (`cost_tracker.py`)

The `CostTracker` class maintains:

- Usage records with timestamps, models, tokens, and costs
- Daily and monthly cost aggregates
- Configurable budget limits

### Integration Points

1. **LLM Provider Level**: Each provider (Anthropic, OpenAI, Gemini) automatically:
   - Extracts token counts from API responses
   - Calculates costs using current pricing
   - Records usage asynchronously

2. **API Level**: FastAPI endpoint exposes usage statistics

## Pricing (as of 2024)

| Model                      | Input (per 1K tokens) | Output (per 1K tokens) |
| -------------------------- | --------------------- | ---------------------- |
| claude-3-5-sonnet-20241022 | $0.003                | $0.015                 |
| claude-3-opus-20240229     | $0.015                | $0.075                 |
| gpt-4o                     | $0.005                | $0.015                 |
| gpt-4-turbo                | $0.010                | $0.030                 |
| gemini-1.5-pro             | $0.00125              | $0.005                 |

## Configuration

Default budget limits (can be modified in `cost_tracker.py`):

```python
daily_limit: float = 100.0      # $100/day
monthly_limit: float = 2000.0   # $2000/month
per_request_limit: float = 1.0  # $1/request
```

## Usage

### Get Cost Statistics

**Endpoint**: `GET /v1/advisor/cost/usage`

**Query Parameters**:

- `user_id` (optional): Filter statistics by user ID

**Response**:

```json
{
  "status": "success",
  "data": {
    "daily_cost_usd": 2.3456,
    "monthly_cost_usd": 45.6789,
    "daily_limit_usd": 100.0,
    "monthly_limit_usd": 2000.0,
    "total_requests": 150,
    "daily_remaining_usd": 97.6544,
    "monthly_remaining_usd": 1954.3211,
    "daily_usage_percent": 2.35,
    "monthly_usage_percent": 2.28
  },
  "user_id": "anonymous"
}
```

### Programmatic Access

```python
from monitoring import cost_tracker

# Get usage statistics
stats = cost_tracker.get_usage_stats(user_id="user123")

# Check if within budget
within_budget, message = await cost_tracker.check_budget(user_id="user123")
if not within_budget:
    print(f"Budget exceeded: {message}")

# Calculate cost for a hypothetical request
cost = cost_tracker.calculate_cost(
    model="claude-3-5-sonnet-20241022",
    input_tokens=1000,
    output_tokens=500
)
```

## LLM Response Fields

Each `LLMResponse` now includes cost information:

```python
@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens_used: int       # Total tokens
    input_tokens: int      # NEW: Input tokens
    output_tokens: int     # NEW: Output tokens
    cost: float           # NEW: Cost in USD
    latency_ms: float
    finish_reason: str
```

## Data Retention

By default, usage records are kept for 30 days. You can clean up old records:

```python
cost_tracker.cleanup_old_records(days=30)
```

## Monitoring & Alerts

The system automatically logs warnings for high-cost requests (>$0.10):

```
WARNING: High-cost request: $0.1234 for claude-3-5-sonnet-20241022
```

## Notes

- **Gemini Token Estimation**: Google Gemini doesn't easily provide token counts, so they're estimated using the formula: `tokens ≈ characters / 4`
- **Async Recording**: Cost recording is done asynchronously to avoid blocking LLM requests
- **Thread Safety**: The cost tracker uses asyncio locks for thread-safe operations

## Future Enhancements

- Database persistence for long-term analytics
- Webhook notifications for budget alerts
- Cost breakdown by request type
- Cost optimization recommendations
- Integration with cloud billing systems
