"""
SAHOOL Auto-Fix Module
======================
وحدة الإصلاح التلقائي لمنصة سهول

Automated code analysis and fixing with multi-tool support,
audit trail integration, 8-layer quality system, and bilingual reporting.

Features:
    - Multi-tool diagnostics (Ruff, ESLint, Mypy, Bandit, Dart)
    - Automated fix generation with multiple strategies
    - Safe fix application with rollback support
    - Full audit trail for all operations
    - Platform health checks
    - Bilingual reports (English/Arabic)
    - 8-layer quality orchestration system
    - Advanced frontend and mobile diagnostics with performance budgets

Quick Start:
    from shared.ai.auto_fix import AutoFixEngine, quick_diagnose, quick_fix

    # Quick diagnostic
    report = await quick_diagnose("src/main.py")
    print(f"Found {len(report.diagnostics)} issues")

    # Quick fix
    report, results = await quick_fix("src/", strategy=FixStrategy.SAFE)
    print(f"Fixed {len([r for r in results if r.success])} issues")

    # Full control
    engine = AutoFixEngine(dry_run=True)
    report = await engine.diagnose("src/")
    plan = await engine.generate_fix_plan(report)
    results = await engine.apply_fix_plan(plan, report)

    # Health check
    from shared.ai.auto_fix import quick_health_check
    report = await quick_health_check()
    print(f"Status: {report.overall_status}")

    # CLI usage
    python -m shared.ai.auto_fix.diagnostic_cli --all --fix

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .auto_audit import (
    AuditAction,
    AuditLogEntry,
    AuditSeverity,
    AuditSummary,
    AutoAudit,
    audit_operation,
    create_audit,
)
from .diagnostics import CodeDiagnostics, DiagnosticError
from .engine import AutoFixEngine, quick_diagnose, quick_fix
from .fixers import CodeFixer, FixerError
from .frontend_diagnostics import (
    FrontendDiagnosticConfig,
    FrontendDiagnosticRunner,
    FrontendTool,
    MobileDiagnosticConfig,
    MobileDiagnosticRunner,
    MobileTool,
    UnifiedDiagnosticRunner,
    diagnose_all_platforms,
    diagnose_frontend,
    diagnose_mobile,
)
from .health_check import (
    ComponentType,
    HealthChecker,
    HealthCheckResult,
    HealthReport,
    HealthStatus,
    check_infrastructure,
    quick_health_check,
)
from .frontend_advanced import (
    FrontendAdvancedRunner,
    MobileAdvancedRunner,
    PerformanceBudget,
)
from .quality_layers import (
    LayerResult,
    QualityLayer,
    QualityOrchestrator,
    QualityReport,
    generate_markdown_report,
    run_quality_scan,
)
from .models import (
    AuditEntry,
    CodeFix,
    CodeLocation,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticReport,
    DiagnosticSeverity,
    FixConfidence,
    FixPlan,
    FixResult,
    FixStrategy,
    ToolType,
)

__version__ = "2.0.0"

__all__ = [
    # Engine
    "AutoFixEngine",
    "quick_diagnose",
    "quick_fix",
    # Diagnostics
    "CodeDiagnostics",
    "DiagnosticError",
    # Fixers
    "CodeFixer",
    "FixerError",
    # Frontend & Mobile Diagnostics
    "FrontendDiagnosticConfig",
    "FrontendDiagnosticRunner",
    "FrontendTool",
    "MobileDiagnosticConfig",
    "MobileDiagnosticRunner",
    "MobileTool",
    "UnifiedDiagnosticRunner",
    "diagnose_frontend",
    "diagnose_mobile",
    "diagnose_all_platforms",
    # Health Check
    "HealthChecker",
    "HealthCheckResult",
    "HealthReport",
    "HealthStatus",
    "ComponentType",
    "quick_health_check",
    "check_infrastructure",
    # Auto Audit
    "AutoAudit",
    "AuditAction",
    "AuditSeverity",
    "AuditLogEntry",
    "AuditSummary",
    "create_audit",
    "audit_operation",
    # Models
    "AuditEntry",
    "CodeFix",
    "CodeLocation",
    "Diagnostic",
    "DiagnosticCategory",
    "DiagnosticReport",
    "DiagnosticSeverity",
    "FixConfidence",
    "FixPlan",
    "FixResult",
    "FixStrategy",
    "ToolType",
    # Quality Orchestrator
    "QualityOrchestrator",
    "QualityReport",
    "QualityLayer",
    "LayerResult",
    "run_quality_scan",
    "generate_markdown_report",
    # Frontend Advanced
    "FrontendAdvancedRunner",
    "MobileAdvancedRunner",
    "PerformanceBudget",
]
