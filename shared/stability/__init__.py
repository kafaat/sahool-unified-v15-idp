"""
SAHOOL Platform Stability Framework
=====================================
إطار استقرار منصة سهول

A comprehensive stability framework that prevents drift, detects anomalies,
and auto-remediates common failure patterns across the SAHOOL platform.

Four Core Capabilities:
1. Unified Context (context.py) - Single RequestContext for tenant/correlation/trace
2. Config Policy (config_policy.py) - Policy-as-code environment validation
3. Contract Testing (contracts.py) - API + event schema contract verification
4. Drift Detection (drift_detector.py) - Config, schema, API, event drift detection
5. Auto-Remediation (remediation.py) - Automated fix for common failure patterns
6. Observability Kit (observability.py) - Unified metrics, health checks, SLI/SLO

Version: 1.0.0
"""

from __future__ import annotations

# ``retry_classifier`` depends on ``tenacity``, which is declared in
# ``pyproject.toml`` base extras and ``requirements/testing.txt`` but is *not*
# in ``requirements/base.txt``. Environments that install only the latter
# would otherwise fail at ``import shared.stability``. Re-export
# conditionally so importing this package never raises when tenacity is
# missing — callers can detect availability via ``build_retry is not None``.
try:
    from .retry_classifier import (
        DEFAULT_RETRYABLE,
        FailureClass,
        build_retry,
        classify,
        parse_retry_after,
    )

    _RETRY_CLASSIFIER_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when tenacity is absent
    DEFAULT_RETRYABLE = None  # type: ignore[assignment]
    FailureClass = None  # type: ignore[assignment]
    build_retry = None  # type: ignore[assignment]
    classify = None  # type: ignore[assignment]
    parse_retry_after = None  # type: ignore[assignment]
    _RETRY_CLASSIFIER_AVAILABLE = False

__version__ = "1.0.0"
__all__ = [
    "RequestContext",
    "UnifiedContextMiddleware",
    "get_request_context",
    "get_optional_context",
    "ConfigPolicy",
    "ConfigPolicyEngine",
    "ContractValidator",
    "DriftDetector",
    "DriftReport",
    "RemediationEngine",
    "StabilityHealthCheck",
]
if _RETRY_CLASSIFIER_AVAILABLE:
    __all__ += [
        # Retry classifier (PR-B)
        "FailureClass",
        "DEFAULT_RETRYABLE",
        "classify",
        "parse_retry_after",
        "build_retry",
    ]
