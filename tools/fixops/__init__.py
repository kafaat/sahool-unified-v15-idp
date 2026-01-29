"""
SAHOOL FixOps Tools
أدوات FixOps لسهول

Automated operations orchestration for code fixing and deployment.

Features:
- Signal collection from CI/CD and local tools (20+ tools)
- Auto-fix integration with shared/ai/auto_fix
- Scheduled and periodic checks
- Log file analysis
- Pre-commit and post-fix verification
"""

from .orchestrator import (
    FixOpsOrchestrator,
    FixOpsSummary,
    FixOpsConfig,
    SignalSource,
)
from .signals import (
    SignalCollector,
    CISignal,
    LocalSignal,
)
from .scheduler import (
    FixOpsScheduler,
    LogAnalyzer,
    CheckType,
    CheckFrequency,
    ScheduledCheck,
    CheckResult,
    run_pre_commit,
    run_post_fix,
    analyze_logs,
)

__all__ = [
    # Orchestrator
    "FixOpsOrchestrator",
    "FixOpsSummary",
    "FixOpsConfig",
    "SignalSource",
    # Signals
    "SignalCollector",
    "CISignal",
    "LocalSignal",
    # Scheduler
    "FixOpsScheduler",
    "LogAnalyzer",
    "CheckType",
    "CheckFrequency",
    "ScheduledCheck",
    "CheckResult",
    # Convenience functions
    "run_pre_commit",
    "run_post_fix",
    "analyze_logs",
]
