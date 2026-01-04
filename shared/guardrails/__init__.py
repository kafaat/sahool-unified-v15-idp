"""
SAHOOL AI Safety Guardrails
============================
Comprehensive AI safety guardrails for the SAHOOL agricultural platform.

Based on Google's Secure AI Agents framework and OWASP LLM Top 10.

Features:
- Input filtering (prompt injection, PII, toxic content)
- Output filtering (safety checks, hallucination detection, PII leakage)
- Policy-based enforcement (topic restrictions, rate limiting)
- FastAPI middleware integration
- Multi-level trust system

Author: SAHOOL Platform Team
Updated: December 2025
"""

from .input_filter import (
    InputFilter,
    InputFilterResult,
    PIIDetector,
    PromptInjectionDetector,
    ToxicityFilter,
    compute_input_hash,
    input_filter,
    sanitize_input,
)
from .middleware import (
    GuardrailsConfig,
    GuardrailsMiddleware,
    ViolationLogger,
    get_violation_stats,
    setup_guardrails,
    violation_logger,
)
from .output_filter import (
    CitationChecker,
    HallucinationDetector,
    OutputFilter,
    OutputFilterResult,
    PIILeakageDetector,
    SafetyContentChecker,
    output_filter,
    sanitize_output,
    truncate_output,
)
from .policies import (
    INPUT_VALIDATION_POLICIES,
    OUTPUT_VALIDATION_POLICIES,
    RATE_LIMIT_POLICIES,
    ContentSafetyLevel,
    InputValidationPolicy,
    OutputValidationPolicy,
    PolicyManager,
    RateLimitPolicy,
    TopicPolicy,
    TrustLevel,
    policy_manager,
)

__version__ = "1.0.0"

__all__ = [
    # Input Filtering
    "InputFilter",
    "InputFilterResult",
    "PIIDetector",
    "PromptInjectionDetector",
    "ToxicityFilter",
    "input_filter",
    "sanitize_input",
    "compute_input_hash",
    # Output Filtering
    "OutputFilter",
    "OutputFilterResult",
    "HallucinationDetector",
    "SafetyContentChecker",
    "CitationChecker",
    "PIILeakageDetector",
    "output_filter",
    "sanitize_output",
    "truncate_output",
    # Policies
    "TrustLevel",
    "ContentSafetyLevel",
    "TopicPolicy",
    "RateLimitPolicy",
    "InputValidationPolicy",
    "OutputValidationPolicy",
    "PolicyManager",
    "policy_manager",
    "RATE_LIMIT_POLICIES",
    "INPUT_VALIDATION_POLICIES",
    "OUTPUT_VALIDATION_POLICIES",
    # Middleware
    "GuardrailsMiddleware",
    "GuardrailsConfig",
    "ViolationLogger",
    "violation_logger",
    "setup_guardrails",
    "get_violation_stats",
]


# ─────────────────────────────────────────────────────────────────────────────
# Quick Start Examples
# ─────────────────────────────────────────────────────────────────────────────

"""
Quick Start - FastAPI Integration
==================================

1. Basic setup with default config:

```python
from fastapi import FastAPI
from shared.guardrails import setup_guardrails, GuardrailsConfig

app = FastAPI()

# Enable guardrails with default settings
setup_guardrails(app)
```

2. Custom configuration:

```python
config = GuardrailsConfig(
    enabled=True,
    block_violations=True,
    mask_pii=True,
    strict_topic_check=True,  # Require agriculture-related topics
    strict_paths=["/api/v1/ai/chat", "/api/v1/recommendations"],
)
setup_guardrails(app, config)
```

3. Manual filtering (without middleware):

```python
from shared.guardrails import input_filter, output_filter, TrustLevel

# Filter user input
result = input_filter.filter_input(
    text=user_prompt,
    trust_level=TrustLevel.BASIC,
    mask_pii=True
)

if not result.is_safe:
    return {"error": result.violations}

# Use filtered input for AI call
ai_response = await call_ai_model(result.filtered_text)

# Filter AI output
output_result = output_filter.filter_output(
    text=ai_response,
    trust_level=TrustLevel.BASIC,
    language="ar"
)

return {"response": output_result.filtered_output}
```

4. Check violations and stats:

```python
from shared.guardrails import get_violation_stats

stats = get_violation_stats()
print(f"Total violations: {stats['total_violations']}")
print(f"Critical violations: {stats['critical_violations']}")
```

5. Custom trust level determination:

```python
from shared.guardrails import policy_manager, TrustLevel

trust_level = policy_manager.get_user_trust_level(
    user_id="user123",
    roles=["farmer", "verified"],
    is_premium=True,
    is_verified=True,
    account_age_days=120
)
# Returns: TrustLevel.PREMIUM
```

Topic Restrictions
==================

SAHOOL guardrails enforce agriculture-focused topics:

Allowed topics:
- Agriculture, farming, crops, irrigation
- Weather, climate, seasons
- Livestock, animals
- Agricultural technology, IoT, precision farming
- Market prices, subsidies, insurance

Blocked topics:
- Illegal content (terrorism, weapons, drugs)
- Harmful content (self-harm, hate speech)
- Off-topic (politics, religion, gambling, adult content)

Trust Levels
============

- BLOCKED: All requests rejected
- UNTRUSTED: New users, strictest guardrails
- BASIC: Verified users, standard guardrails
- TRUSTED: Established users, relaxed guardrails
- PREMIUM: Premium subscribers, minimal guardrails
- ADMIN: System admins, bypass most checks

Each level has different policies for:
- Input validation (max length, checks enabled)
- Output validation (disclaimers, citations)
- Rate limiting (requests/minute, tokens/day)
"""
