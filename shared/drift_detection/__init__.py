"""
SAHOOL Drift Detection Framework
=================================
إطار كشف الانحراف - منصة سهول

Comprehensive drift detection and auto-remediation for the SAHOOL platform.
Covers 6 drift categories:
1. Config Drift   - GitOps desired vs actual state
2. Schema Drift   - DB schema vs expected migrations
3. API Drift      - Contract tests against staging/prod
4. Event Drift    - NATS schema registry version checks
5. Data Drift     - ML/NDVI distribution shift, sensor anomalies
6. Security Drift - Policy checks, secret rotation, compliance

Architecture:
    DriftDetectionEngine (orchestrator)
    ├── ConfigDriftDetector
    ├── SchemaDriftDetector
    ├── APIDriftDetector
    ├── EventDriftDetector
    ├── DataDriftDetector
    └── SecurityDriftDetector
    └── AutoRemediationEngine
    └── QualityGatesEngine
"""

from shared.drift_detection.models import (
    DriftCategory,
    DriftReport,
    DriftResult,
    DriftSeverity,
    RemediationAction,
    RemediationResult,
    RemediationStrategy,
)
from shared.drift_detection.engine import DriftDetectionEngine
from shared.drift_detection.quality_gates import QualityGatesEngine
from shared.drift_detection.remediation import AutoRemediationEngine

__all__ = [
    "DriftDetectionEngine",
    "QualityGatesEngine",
    "AutoRemediationEngine",
    "DriftCategory",
    "DriftSeverity",
    "DriftResult",
    "DriftReport",
    "RemediationAction",
    "RemediationResult",
    "RemediationStrategy",
]
