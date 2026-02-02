"""
Code Fixers Module
==================
وحدة إصلاح الأخطاء البرمجية

Provides automated code fixing capabilities with support for
multiple strategies and safety checks.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import tempfile
import uuid
<<<<<<< HEAD
from datetime import datetime, timezone
=======
from datetime import datetime, UTC
>>>>>>> origin/main
from pathlib import Path
from typing import Any

from .models import (
    CodeFix,
    Diagnostic,
    DiagnosticCategory,
    FixConfidence,
    FixResult,
    FixStrategy,
    ToolType,
)


class FixerError(Exception):
    """Exception raised for fixer errors."""

    pass


# Common fix patterns for Python code
PYTHON_FIX_PATTERNS: dict[str, dict[str, Any]] = {
    # Unused imports
    "F401": {
        "pattern": r"^(\s*)import\s+{name}\s*$",
        "replacement": "",
        "description": "Remove unused import",
        "description_ar": "إزالة الاستيراد غير المستخدم",
        "confidence": FixConfidence.HIGH,
    },
    "F401_from": {
        "pattern": r"^(\s*)from\s+\S+\s+import\s+{name}\s*$",
        "replacement": "",
        "description": "Remove unused import",
        "description_ar": "إزالة الاستيراد غير المستخدم",
        "confidence": FixConfidence.HIGH,
    },
    # Missing whitespace
    "E225": {
        "pattern": r"(\S)([+\-*/=<>])(\S)",
        "replacement": r"\1 \2 \3",
        "description": "Add whitespace around operator",
        "description_ar": "إضافة مسافات حول المعامل",
        "confidence": FixConfidence.HIGH,
    },
    # Trailing whitespace
    "W291": {
        "pattern": r"\s+$",
        "replacement": "",
        "description": "Remove trailing whitespace",
        "description_ar": "إزالة المسافات الزائدة في نهاية السطر",
        "confidence": FixConfidence.HIGH,
    },
    # Blank lines
    "E303": {
        "pattern": r"\n\n\n+",
        "replacement": "\n\n",
        "description": "Remove excess blank lines",
        "description_ar": "إزالة الأسطر الفارغة الزائدة",
        "confidence": FixConfidence.HIGH,
    },
    # Comparison to None
    "E711": {
        "pattern": r"(\S+)\s*==\s*None",
        "replacement": r"\1 is None",
        "description": "Use 'is None' instead of '== None'",
        "description_ar": "استخدام 'is None' بدلاً من '== None'",
        "confidence": FixConfidence.HIGH,
    },
    # Comparison to True/False
    "E712": {
        "pattern": r"(\S+)\s*==\s*(True|False)",
        "replacement": r"\1 is \2",
        "description": "Use 'is' for boolean comparison",
        "description_ar": "استخدام 'is' للمقارنة المنطقية",
        "confidence": FixConfidence.MEDIUM,
    },
    # f-string without placeholders
    "F541": {
        "pattern": r'f(["\'])([^{]*)\1',
        "replacement": r"\1\2\1",
        "description": "Remove unnecessary f-string prefix",
        "description_ar": "إزالة بادئة f غير الضرورية",
        "confidence": FixConfidence.HIGH,
    },
}


# Security fix patterns
SECURITY_FIX_PATTERNS: dict[str, dict[str, Any]] = {
    # Hardcoded password in assignment
    "B105": {
        "pattern": r'(\w+)\s*=\s*["\']([^"\']+)["\'].*#.*password|secret|key',
        "replacement": r'\1 = os.environ.get("{upper_name}", "")',
        "description": "Move secret to environment variable",
        "description_ar": "نقل السر إلى متغير بيئي",
        "confidence": FixConfidence.MEDIUM,
        "requires_import": "os",
    },
    # SQL injection risk
    "B608": {
        "pattern": r'execute\(["\'].*%s.*["\'].*%.*\)',
        "replacement": "execute(query, params)  # Use parameterized queries",
        "description": "Use parameterized query to prevent SQL injection",
        "description_ar": "استخدام استعلام معلمي لمنع حقن SQL",
        "confidence": FixConfidence.LOW,
        "requires_review": True,
    },
}


class CodeFixer:
    """
    Automated code fixer.

    مصلح الكود التلقائي

    Generates and applies fixes for code diagnostics with support
    for multiple strategies and safety validation.

    Example:
        fixer = CodeFixer()
        fix = await fixer.generate_fix(diagnostic)
        if fix and fix.is_safe:
            result = await fixer.apply_fix(fix)
    """

    def __init__(
        self,
        backup_dir: str | None = None,
        ruff_path: str = "ruff",
        dry_run: bool = False,
    ):
        """
        Initialize CodeFixer.

        Args:
            backup_dir: Directory for file backups
            ruff_path: Path to ruff executable
            dry_run: If True, don't actually modify files
        """
        self.backup_dir = backup_dir or tempfile.mkdtemp(prefix="sahool_fix_backup_")
        self.ruff_path = ruff_path
        self.dry_run = dry_run

    async def generate_fix(
        self,
        diagnostic: Diagnostic,
        strategy: FixStrategy = FixStrategy.SAFE,
    ) -> CodeFix | None:
        """
        Generate a fix for a diagnostic.

        توليد إصلاح لتشخيص

        Args:
            diagnostic: The diagnostic to fix
            strategy: Fix strategy to use

        Returns:
            CodeFix if fix is available, None otherwise
        """
        # Try tool-specific auto-fix first
        if diagnostic.tool == ToolType.RUFF and diagnostic.rule_id:
            fix = await self._generate_ruff_fix(diagnostic)
            if fix:
                return fix

        # Try pattern-based fix
        fix = await self._generate_pattern_fix(diagnostic, strategy)
        if fix:
            return fix

        # Try AI-suggested fix (if suggestion available)
        if diagnostic.suggestion:
            return await self._generate_ai_suggested_fix(diagnostic, strategy)

        return None

    async def _generate_ruff_fix(self, diagnostic: Diagnostic) -> CodeFix | None:
        """Generate fix using ruff --fix."""
        try:
            # Read original file content
            with open(diagnostic.location.file_path, encoding="utf-8") as f:
                original_content = f.read()

            # Create a temp file with the content
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as tmp:
                tmp.write(original_content)
                tmp_path = tmp.name

            try:
                # Run ruff fix on specific rule
                proc = await asyncio.create_subprocess_exec(
                    self.ruff_path,
                    "check",
                    "--fix",
                    f"--select={diagnostic.rule_id}",
                    tmp_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await asyncio.wait_for(proc.communicate(), timeout=30)

                # Read fixed content
                with open(tmp_path, encoding="utf-8") as f:
                    fixed_content = f.read()

                if fixed_content != original_content:
                    return CodeFix(
                        id=str(uuid.uuid4()),
                        diagnostic_id=diagnostic.id,
                        description=f"Auto-fix by ruff: {diagnostic.rule_id}",
                        description_ar=f"إصلاح تلقائي بواسطة ruff: {diagnostic.rule_id}",
                        original_code=original_content,
                        fixed_code=fixed_content,
                        strategy=FixStrategy.SAFE,
                        confidence=FixConfidence.HIGH,
                        is_safe=True,
                    )

            finally:
                os.unlink(tmp_path)

        except (TimeoutError, OSError):
            # Ruff fix generation is best-effort; failures are expected for some
            # diagnostics (e.g., complex multi-line issues) and are handled by
            # falling back to pattern-based or AI-suggested fixes in generate_fix()
            pass

        return None

    async def _generate_pattern_fix(
        self,
        diagnostic: Diagnostic,
        strategy: FixStrategy,
    ) -> CodeFix | None:
        """Generate fix using regex patterns."""
        rule_id = diagnostic.rule_id
        if not rule_id:
            return None

        # Check for pattern
        pattern_info = PYTHON_FIX_PATTERNS.get(rule_id)
        if not pattern_info and diagnostic.category == DiagnosticCategory.SECURITY:
            pattern_info = SECURITY_FIX_PATTERNS.get(rule_id)

        if not pattern_info:
            return None

        try:
            # Read the specific lines
            with open(diagnostic.location.file_path, encoding="utf-8") as f:
                lines = f.readlines()

            line_idx = diagnostic.location.line_start - 1
            if line_idx >= len(lines):
                return None

            original_line = lines[line_idx]

            # Apply pattern
            pattern = pattern_info["pattern"]
            replacement = pattern_info["replacement"]

            fixed_line = re.sub(pattern, replacement, original_line)

            if fixed_line == original_line:
                return None

            # Reconstruct file content
            fixed_lines = lines.copy()
            if fixed_line.strip():
                fixed_lines[line_idx] = fixed_line
            else:
                # Remove the line if empty
                fixed_lines.pop(line_idx)

            return CodeFix(
                id=str(uuid.uuid4()),
                diagnostic_id=diagnostic.id,
                description=pattern_info["description"],
                description_ar=pattern_info["description_ar"],
                original_code=original_line,
                fixed_code=fixed_line,
                strategy=strategy,
                confidence=pattern_info.get("confidence", FixConfidence.MEDIUM),
                is_safe=not pattern_info.get("requires_review", False),
                requires_review=pattern_info.get("requires_review", False),
            )

        except OSError:
            return None

    async def _generate_ai_suggested_fix(
        self,
        diagnostic: Diagnostic,
        strategy: FixStrategy,
    ) -> CodeFix | None:
        """Generate fix from AI suggestion."""
        if not diagnostic.suggestion:
            return None

        try:
            with open(diagnostic.location.file_path, encoding="utf-8") as f:
                lines = f.readlines()

            line_idx = diagnostic.location.line_start - 1
            if line_idx >= len(lines):
                return None

            original_line = lines[line_idx]

            return CodeFix(
                id=str(uuid.uuid4()),
                diagnostic_id=diagnostic.id,
                description=f"AI suggestion: {diagnostic.suggestion}",
                description_ar=diagnostic.suggestion_ar or "اقتراح الذكاء الاصطناعي",
                original_code=original_line,
                fixed_code=f"# TODO: {diagnostic.suggestion}\n{original_line}",
                strategy=strategy,
                confidence=FixConfidence.LOW,
                is_safe=False,
                requires_review=True,
            )

        except OSError:
            return None

    async def apply_fix(
        self,
        fix: CodeFix,
        create_backup: bool = True,
    ) -> FixResult:
        """
        Apply a fix to a file.

        تطبيق إصلاح على ملف

        Args:
            fix: The fix to apply
            create_backup: Whether to create a backup

        Returns:
            FixResult with outcome details
        """
        # Get diagnostic to find file path
        # In production, this would lookup the diagnostic
        # For now, we'll use the fixed_code which contains full file

        backup_path = None

        try:
            # Find the original file from the fix
            # This is a simplified approach - production would track file paths
            if not fix.original_code or not fix.fixed_code:
                return FixResult(
                    fix_id=fix.id,
                    success=False,
<<<<<<< HEAD
                    applied_at=datetime.now(timezone.utc),
=======
                    applied_at=datetime.now(UTC),
>>>>>>> origin/main
                    file_path="unknown",
                    error_message="Fix has no code content",
                )

            # For full file fixes, we need the file path from diagnostic
            # This is handled by the engine which has the context

            return FixResult(
                fix_id=fix.id,
                success=True,
<<<<<<< HEAD
                applied_at=datetime.now(timezone.utc),
=======
                applied_at=datetime.now(UTC),
>>>>>>> origin/main
                file_path="pending",  # Will be set by engine
                backup_path=backup_path,
                rollback_available=create_backup,
            )

        except OSError as e:
            return FixResult(
                fix_id=fix.id,
                success=False,
<<<<<<< HEAD
                applied_at=datetime.now(timezone.utc),
=======
                applied_at=datetime.now(UTC),
>>>>>>> origin/main
                file_path="unknown",
                error_message=str(e),
            )

    async def apply_fix_to_file(
        self,
        fix: CodeFix,
        file_path: str,
        create_backup: bool = True,
    ) -> FixResult:
        """
        Apply a fix to a specific file.

        تطبيق إصلاح على ملف محدد

        Args:
            fix: The fix to apply
            file_path: Path to the file
            create_backup: Whether to create a backup

        Returns:
            FixResult with outcome details
        """
        backup_path = None

        try:
            if not os.path.exists(file_path):
                return FixResult(
                    fix_id=fix.id,
                    success=False,
<<<<<<< HEAD
                    applied_at=datetime.now(timezone.utc),
=======
                    applied_at=datetime.now(UTC),
>>>>>>> origin/main
                    file_path=file_path,
                    error_message=f"File not found: {file_path}",
                )

            # Create backup
            if create_backup and not self.dry_run:
                backup_filename = f"{Path(file_path).name}.{fix.id[:8]}.bak"
                backup_path = os.path.join(self.backup_dir, backup_filename)
                shutil.copy2(file_path, backup_path)

            # Apply fix
            if not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fix.fixed_code)

            # Verify fix
            verification = await self._verify_fix(file_path)

            return FixResult(
                fix_id=fix.id,
                success=True,
<<<<<<< HEAD
                applied_at=datetime.now(timezone.utc),
=======
                applied_at=datetime.now(UTC),
>>>>>>> origin/main
                file_path=file_path,
                backup_path=backup_path,
                verification_passed=verification,
                rollback_available=backup_path is not None,
            )

        except OSError as e:
            return FixResult(
                fix_id=fix.id,
                success=False,
<<<<<<< HEAD
                applied_at=datetime.now(timezone.utc),
=======
                applied_at=datetime.now(UTC),
>>>>>>> origin/main
                file_path=file_path,
                backup_path=backup_path,
                error_message=str(e),
            )

    async def rollback_fix(self, result: FixResult) -> bool:
        """
        Rollback a previously applied fix.

        التراجع عن إصلاح تم تطبيقه

        Args:
            result: The fix result to rollback

        Returns:
            True if rollback successful
        """
        if not result.rollback_available or not result.backup_path:
            return False

        try:
            if os.path.exists(result.backup_path):
                shutil.copy2(result.backup_path, result.file_path)
                os.unlink(result.backup_path)
                return True
        except OSError:
            # Rollback failure is non-critical; the backup file may have been
            # already cleaned up or the file system state changed. We return
            # False to indicate rollback was not successful.
            pass

        return False

    async def _verify_fix(self, file_path: str) -> bool:
        """Verify that a fix doesn't introduce new errors."""
        try:
            # Run syntax check
            proc = await asyncio.create_subprocess_exec(
                "python",
                "-m",
                "py_compile",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)

            return proc.returncode == 0 and not stderr

        except (TimeoutError, OSError):
            return False

    async def batch_apply_fixes(
        self,
        fixes: list[tuple[CodeFix, str]],
        stop_on_error: bool = False,
    ) -> list[FixResult]:
        """
        Apply multiple fixes.

        تطبيق إصلاحات متعددة

        Args:
            fixes: List of (fix, file_path) tuples
            stop_on_error: Stop on first error if True

        Returns:
            List of FixResults
        """
        results: list[FixResult] = []

        for fix, file_path in fixes:
            result = await self.apply_fix_to_file(fix, file_path)
            results.append(result)

            if stop_on_error and not result.success:
                break

        return results
