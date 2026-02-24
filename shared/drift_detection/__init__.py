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

# Models are leaf-level (no intra-package deps) — safe to import eagerly.
from shared.drift_detection.models import (
    DriftCategory,
    DriftReport,
    DriftResult,
    DriftSeverity,
    RemediationAction,
    RemediationResult,
    RemediationStrategy,
)

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
    "compare_with_baseline",
    "create_baseline",
    "load_baseline",
]

# Lazy-load engine, quality_gates, and remediation to avoid the
# RuntimeWarning that occurs when `python -m shared.drift_detection.engine`
# finds the submodule already in sys.modules (placed there by __init__
# eager imports) before the -m runner can execute it.
#
# Only modules within this package are allowed — the set is hardcoded
# to prevent arbitrary code loading (addresses Semgrep importlib finding).
_ALLOWED_MODULES: frozenset[str] = frozenset({
    "shared.drift_detection.engine",
    "shared.drift_detection.quality_gates",
    "shared.drift_detection.remediation",
})

_lazy_imports: dict[str, tuple[str, str]] = {
    "DriftDetectionEngine": ("shared.drift_detection.engine", "DriftDetectionEngine"),
    "QualityGatesEngine": ("shared.drift_detection.quality_gates", "QualityGatesEngine"),
    "AutoRemediationEngine": ("shared.drift_detection.remediation", "AutoRemediationEngine"),
    "compare_with_baseline": ("shared.drift_detection.engine", "compare_with_baseline"),
    "create_baseline": ("shared.drift_detection.engine", "create_baseline"),
    "load_baseline": ("shared.drift_detection.engine", "load_baseline"),
}


def __getattr__(name: str):
    if name in _lazy_imports:
        module_path, attr = _lazy_imports[name]
        if module_path not in _ALLOWED_MODULES:  # noqa: S105 — not a password
            raise ImportError(
                f"Module {module_path!r} is not in the allow-list"
            )
        import importlib

        mod = importlib.import_module(module_path)  # nosemgrep: python.lang.security.audit.non-literal-import
        return getattr(mod, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
