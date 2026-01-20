"""
SAHOOL Auto-Fix Module
======================
وحدة الإصلاح التلقائي لمنصة سهول

Automated code analysis and fixing with multi-tool support,
audit trail integration, and bilingual reporting.

Features:
    - Multi-tool diagnostics (Ruff, ESLint, Mypy, Bandit, Dart)
    - Automated fix generation with multiple strategies
    - Safe fix application with rollback support
    - Full audit trail for all operations
    - Bilingual reports (English/Arabic)

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

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .diagnostics import CodeDiagnostics, DiagnosticError
from .engine import AutoFixEngine, quick_diagnose, quick_fix
from .fixers import CodeFixer, FixerError
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

__version__ = "1.0.0"

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
]
