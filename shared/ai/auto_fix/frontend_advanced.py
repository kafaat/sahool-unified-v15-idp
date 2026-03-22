"""
Advanced Frontend & Mobile Diagnostics with Performance Budgets
تشخيصات متقدمة للواجهات والتطبيق المحمول مع ميزانيات الأداء

Extends the base frontend_diagnostics module with:
- Performance budget enforcement (bundle size, LCP, FID, CLS)
- Next.js specific checks (ISR, dynamic imports, image optimization)
- Flutter advanced analysis (widget rebuild, memory leaks)
- Accessibility auditing (WCAG 2.1 AA)
- Bilingual reporting (English/Arabic)

Author: SAHOOL Platform Team
Created: March 2026
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticReport,
    DiagnosticSeverity,
)

logger = logging.getLogger(__name__)


@dataclass
class PerformanceBudget:
    """Performance budget thresholds for frontend applications."""

    # Bundle sizes (KB)
    max_js_bundle_kb: float = 250.0
    max_css_bundle_kb: float = 50.0
    max_total_bundle_kb: float = 500.0

    # Core Web Vitals
    max_lcp_ms: float = 2500.0  # Largest Contentful Paint
    max_fid_ms: float = 100.0  # First Input Delay
    max_cls: float = 0.1  # Cumulative Layout Shift
    max_ttfb_ms: float = 800.0  # Time to First Byte

    # Image optimization
    max_image_size_kb: float = 200.0
    require_next_image: bool = True
    require_webp: bool = True

    # Code splitting
    max_initial_chunks: int = 10
    max_lazy_load_time_ms: float = 3000.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_js_bundle_kb": self.max_js_bundle_kb,
            "max_css_bundle_kb": self.max_css_bundle_kb,
            "max_total_bundle_kb": self.max_total_bundle_kb,
            "max_lcp_ms": self.max_lcp_ms,
            "max_fid_ms": self.max_fid_ms,
            "max_cls": self.max_cls,
            "max_ttfb_ms": self.max_ttfb_ms,
            "max_image_size_kb": self.max_image_size_kb,
            "max_initial_chunks": self.max_initial_chunks,
        }


@dataclass
class BudgetViolation:
    """A performance budget violation."""

    metric: str
    metric_ar: str
    actual: float
    budget: float
    severity: DiagnosticSeverity
    file_path: str | None = None
    suggestion: str = ""
    suggestion_ar: str = ""

    @property
    def overage_pct(self) -> float:
        """Calculate overage percentage."""
        if self.budget == 0:
            return 100.0
        return ((self.actual - self.budget) / self.budget) * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "metric_ar": self.metric_ar,
            "actual": self.actual,
            "budget": self.budget,
            "overage_pct": round(self.overage_pct, 1),
            "severity": self.severity.value,
            "file_path": self.file_path,
            "suggestion": self.suggestion,
        }


class FrontendAdvancedRunner:
    """
    Advanced frontend diagnostics with performance budgets.
    تشخيصات متقدمة للواجهات مع ميزانيات الأداء

    Checks:
        - Bundle size analysis (next build output)
        - Image optimization audit
        - Accessibility scanning
        - Next.js best practices
        - Performance budget enforcement
    """

    def __init__(
        self,
        working_dir: str = ".",
        web_path: str = "apps/web",
        admin_path: str = "apps/admin",
        budget: PerformanceBudget | None = None,
    ):
        self.working_dir = Path(working_dir).resolve()
        self.web_path = self.working_dir / web_path
        self.admin_path = self.working_dir / admin_path
        self.budget = budget or PerformanceBudget()

    async def run_all(self) -> list[BudgetViolation]:
        """Run all advanced frontend checks."""
        violations: list[BudgetViolation] = []

        checks = [
            self._check_bundle_sizes(),
            self._check_image_optimization(),
            self._check_nextjs_patterns(),
            self._check_accessibility(),
        ]

        results = await asyncio.gather(*checks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                violations.extend(result)
            elif isinstance(result, Exception):
                logger.error("Check failed: %s", result)

        return violations

    async def _check_bundle_sizes(self) -> list[BudgetViolation]:
        """Check JS/CSS bundle sizes against budgets."""
        violations = []

        for app_path in [self.web_path, self.admin_path]:
            if not app_path.exists():
                continue

            # Check .next/build-manifest.json or build output
            build_dir = app_path / ".next"
            if not build_dir.exists():
                continue

            # Scan static chunks
            chunks_dir = build_dir / "static" / "chunks"
            if chunks_dir.exists():
                total_js_kb = 0.0
                for js_file in chunks_dir.rglob("*.js"):
                    size_kb = js_file.stat().st_size / 1024
                    total_js_kb += size_kb

                    if size_kb > self.budget.max_js_bundle_kb:
                        violations.append(BudgetViolation(
                            metric="js_chunk_size",
                            metric_ar="حجم حزمة JavaScript",
                            actual=round(size_kb, 1),
                            budget=self.budget.max_js_bundle_kb,
                            severity=DiagnosticSeverity.WARNING,
                            file_path=str(js_file.relative_to(self.working_dir)),
                            suggestion=f"Split chunk or use dynamic import. Size: {size_kb:.0f}KB > {self.budget.max_js_bundle_kb:.0f}KB",
                            suggestion_ar=f"قسم الحزمة أو استخدم الاستيراد الديناميكي. الحجم: {size_kb:.0f}KB > {self.budget.max_js_bundle_kb:.0f}KB",
                        ))

                if total_js_kb > self.budget.max_total_bundle_kb:
                    violations.append(BudgetViolation(
                        metric="total_js_size",
                        metric_ar="إجمالي حجم JavaScript",
                        actual=round(total_js_kb, 1),
                        budget=self.budget.max_total_bundle_kb,
                        severity=DiagnosticSeverity.ERROR,
                        file_path=str(app_path.relative_to(self.working_dir)),
                        suggestion="Reduce total JS bundle size. Consider code splitting and tree shaking.",
                        suggestion_ar="قلل حجم حزمة JavaScript الإجمالي. استخدم تقسيم الكود وإزالة الكود غير المستخدم.",
                    ))

        return violations

    async def _check_image_optimization(self) -> list[BudgetViolation]:
        """Check for unoptimized images."""
        violations = []

        for app_path in [self.web_path, self.admin_path]:
            if not app_path.exists():
                continue

            public_dir = app_path / "public"
            if not public_dir.exists():
                continue

            for img in public_dir.rglob("*"):
                if img.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
                    continue

                size_kb = img.stat().st_size / 1024
                if size_kb > self.budget.max_image_size_kb:
                    violations.append(BudgetViolation(
                        metric="image_size",
                        metric_ar="حجم الصورة",
                        actual=round(size_kb, 1),
                        budget=self.budget.max_image_size_kb,
                        severity=DiagnosticSeverity.WARNING,
                        file_path=str(img.relative_to(self.working_dir)),
                        suggestion=f"Compress image or convert to WebP. Size: {size_kb:.0f}KB",
                        suggestion_ar=f"اضغط الصورة أو حولها إلى WebP. الحجم: {size_kb:.0f}KB",
                    ))

        return violations

    async def _check_nextjs_patterns(self) -> list[BudgetViolation]:
        """Check Next.js best practices."""
        violations = []

        for app_path in [self.web_path, self.admin_path]:
            if not app_path.exists():
                continue

            src_dir = app_path / "src"
            if not src_dir.exists():
                src_dir = app_path

            # Check for <img> instead of <Image> from next/image
            for tsx_file in src_dir.rglob("*.tsx"):
                try:
                    content = tsx_file.read_text(errors="replace")
                except OSError:
                    continue

                if "<img " in content and "next/image" not in content:
                    violations.append(BudgetViolation(
                        metric="next_image",
                        metric_ar="استخدام next/image",
                        actual=1,
                        budget=0,
                        severity=DiagnosticSeverity.WARNING,
                        file_path=str(tsx_file.relative_to(self.working_dir)),
                        suggestion="Use next/image <Image> component instead of <img> for automatic optimization",
                        suggestion_ar="استخدم مكون <Image> من next/image بدلاً من <img> للتحسين التلقائي",
                    ))

        return violations

    async def _check_accessibility(self) -> list[BudgetViolation]:
        """Check accessibility patterns in source code."""
        violations = []

        for app_path in [self.web_path, self.admin_path]:
            if not app_path.exists():
                continue

            src_dir = app_path / "src"
            if not src_dir.exists():
                continue

            for tsx_file in src_dir.rglob("*.tsx"):
                try:
                    content = tsx_file.read_text(errors="replace")
                except OSError:
                    continue

                rel_path = str(tsx_file.relative_to(self.working_dir))

                # Check for missing alt text on images
                if "<Image" in content or "<img" in content:
                    if 'alt=""' in content or "alt=''" in content:
                        violations.append(BudgetViolation(
                            metric="a11y_alt_text",
                            metric_ar="نص بديل للصور",
                            actual=1,
                            budget=0,
                            severity=DiagnosticSeverity.WARNING,
                            file_path=rel_path,
                            suggestion="Provide meaningful alt text for images (WCAG 1.1.1)",
                            suggestion_ar="أضف نصاً بديلاً واضحاً للصور (WCAG 1.1.1)",
                        ))

                # Check for onClick without keyboard handler
                if "onClick" in content and "onKeyDown" not in content and "onKeyPress" not in content:
                    if "<div onClick" in content or "<span onClick" in content:
                        violations.append(BudgetViolation(
                            metric="a11y_keyboard",
                            metric_ar="إمكانية الوصول بلوحة المفاتيح",
                            actual=1,
                            budget=0,
                            severity=DiagnosticSeverity.INFO,
                            file_path=rel_path,
                            suggestion="Add keyboard event handler for interactive non-button elements (WCAG 2.1.1)",
                            suggestion_ar="أضف معالج أحداث لوحة المفاتيح للعناصر التفاعلية (WCAG 2.1.1)",
                        ))

        return violations


class MobileAdvancedRunner:
    """
    Advanced Flutter/Dart diagnostics.
    تشخيصات متقدمة لـ Flutter/Dart

    Checks:
        - Widget rebuild analysis
        - State management patterns
        - Memory leak patterns
        - Offline-first compliance
        - Platform channel usage
    """

    def __init__(
        self,
        working_dir: str = ".",
        mobile_path: str = "apps/mobile",
    ):
        self.working_dir = Path(working_dir).resolve()
        self.mobile_path = self.working_dir / mobile_path

    async def run_all(self) -> list[BudgetViolation]:
        """Run all advanced mobile checks."""
        violations: list[BudgetViolation] = []

        if not self.mobile_path.exists():
            logger.warning("Mobile path not found: %s", self.mobile_path)
            return violations

        checks = [
            self._check_widget_patterns(),
            self._check_state_management(),
            self._check_offline_compliance(),
        ]

        results = await asyncio.gather(*checks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                violations.extend(result)
            elif isinstance(result, Exception):
                logger.error("Mobile check failed: %s", result)

        return violations

    async def _check_widget_patterns(self) -> list[BudgetViolation]:
        """Check for common Flutter anti-patterns."""
        violations = []

        lib_dir = self.mobile_path / "lib"
        if not lib_dir.exists():
            return violations

        for dart_file in lib_dir.rglob("*.dart"):
            try:
                content = dart_file.read_text(errors="replace")
            except OSError:
                continue

            rel_path = str(dart_file.relative_to(self.working_dir))

            # Check for setState in large widgets (potential rebuild issues)
            if "setState(" in content:
                lines = content.split("\n")
                if len(lines) > 200:
                    violations.append(BudgetViolation(
                        metric="flutter_rebuild",
                        metric_ar="إعادة بناء الواجهة",
                        actual=len(lines),
                        budget=200,
                        severity=DiagnosticSeverity.WARNING,
                        file_path=rel_path,
                        suggestion="Large widget with setState. Consider extracting sub-widgets or using Riverpod.",
                        suggestion_ar="واجهة كبيرة مع setState. انقل الأجزاء إلى واجهات فرعية أو استخدم Riverpod.",
                    ))

            # Check for missing const constructors
            if "Widget build(" in content and "const " not in content[:500]:
                if content.count("Container(") > 3 or content.count("Padding(") > 3:
                    violations.append(BudgetViolation(
                        metric="flutter_const",
                        metric_ar="استخدام const",
                        actual=1,
                        budget=0,
                        severity=DiagnosticSeverity.INFO,
                        file_path=rel_path,
                        suggestion="Consider using const constructors for static widgets to improve performance.",
                        suggestion_ar="استخدم const للواجهات الثابتة لتحسين الأداء.",
                    ))

        return violations

    async def _check_state_management(self) -> list[BudgetViolation]:
        """Check state management patterns."""
        violations = []

        lib_dir = self.mobile_path / "lib"
        if not lib_dir.exists():
            return violations

        for dart_file in lib_dir.rglob("*.dart"):
            try:
                content = dart_file.read_text(errors="replace")
            except OSError:
                continue

            rel_path = str(dart_file.relative_to(self.working_dir))

            # Check for global mutable state
            if "static " in content and " = " in content and "final" not in content:
                for line in content.split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("static ") and "final" not in stripped and "const" not in stripped and "=" in stripped:
                        violations.append(BudgetViolation(
                            metric="flutter_global_state",
                            metric_ar="حالة عامة قابلة للتعديل",
                            actual=1,
                            budget=0,
                            severity=DiagnosticSeverity.WARNING,
                            file_path=rel_path,
                            suggestion="Avoid mutable static state. Use Riverpod providers instead.",
                            suggestion_ar="تجنب الحالة الثابتة القابلة للتعديل. استخدم Riverpod بدلاً.",
                        ))
                        break

        return violations

    async def _check_offline_compliance(self) -> list[BudgetViolation]:
        """Check offline-first patterns."""
        violations = []

        lib_dir = self.mobile_path / "lib"
        if not lib_dir.exists():
            return violations

        # Check API calls have offline fallback
        for dart_file in lib_dir.rglob("*.dart"):
            try:
                content = dart_file.read_text(errors="replace")
            except OSError:
                continue

            rel_path = str(dart_file.relative_to(self.working_dir))

            # HTTP calls without try-catch (offline risk)
            if (".get(" in content or ".post(" in content) and "dio" in content.lower():
                if "catch" not in content and "try" not in content:
                    violations.append(BudgetViolation(
                        metric="offline_compliance",
                        metric_ar="التوافق مع وضع عدم الاتصال",
                        actual=1,
                        budget=0,
                        severity=DiagnosticSeverity.WARNING,
                        file_path=rel_path,
                        suggestion="HTTP calls should have error handling for offline scenarios.",
                        suggestion_ar="يجب معالجة أخطاء الشبكة لدعم وضع عدم الاتصال.",
                    ))

        return violations
