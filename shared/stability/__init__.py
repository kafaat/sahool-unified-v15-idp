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
