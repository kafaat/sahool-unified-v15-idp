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
    FixOpsConfig,
    FixOpsOrchestrator,
    FixOpsSummary,
    SignalSource,
)
from .scheduler import (
    CheckFrequency,
    CheckResult,
    CheckType,
    FixOpsScheduler,
    LogAnalyzer,
    ScheduledCheck,
    analyze_logs,
    run_post_fix,
    run_pre_commit,
)
from .signals import (
    CISignal,
    LocalSignal,
    SignalCollector,
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
