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

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

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

# TYPE_CHECKING imports satisfy static analysers (CodeQL, mypy, pyright) while
# avoiding the RuntimeWarning that occurs when ``python -m
# shared.drift_detection.engine`` finds the submodule already in sys.modules.
if TYPE_CHECKING:
    from shared.drift_detection.engine import (
        DriftDetectionEngine as DriftDetectionEngine,
    )
    from shared.drift_detection.engine import (
        compare_with_baseline as compare_with_baseline,
    )
    from shared.drift_detection.engine import (
        create_baseline as create_baseline,
    )
    from shared.drift_detection.engine import (
        load_baseline as load_baseline,
    )
    from shared.drift_detection.quality_gates import (
        QualityGatesEngine as QualityGatesEngine,
    )
    from shared.drift_detection.remediation import (
        AutoRemediationEngine as AutoRemediationEngine,
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

# ---------------------------------------------------------------------------
# Lazy runtime imports
# ---------------------------------------------------------------------------
# Only modules within this package are allowed — the set is hardcoded
# to prevent arbitrary code loading (addresses Semgrep importlib finding).
_ALLOWED_MODULES: frozenset[str] = frozenset(
    {
        "shared.drift_detection.engine",
        "shared.drift_detection.quality_gates",
        "shared.drift_detection.remediation",
    }
)

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
            raise ImportError(f"Module {module_path!r} is not in the allow-list")
        import importlib

        mod = importlib.import_module(module_path)  # nosemgrep: python.lang.security.audit.non-literal-import
        val = getattr(mod, attr)
        # Cache on the module so __getattr__ is not called again for this name.
        setattr(sys.modules[__name__], name, val)
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
