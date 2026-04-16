"""
Fix Learning System
====================
نظام التعلم من الإصلاحات

Learns from successful code fixes to improve future fix suggestions.
Tracks fix patterns, success rates, and developer preferences.

Features:
- Pattern extraction from successful fixes
- Success rate tracking by rule/category
- Developer preference learning
- Fix suggestion ranking
- Export for model fine-tuning

Author: SAHOOL Platform Team
Created: January 2026
"""

import hashlib
import json
import os
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

from .models import (
    CodeFix,
    Diagnostic,
    DiagnosticCategory,
    FixResult,
    ToolType,
)

logger = structlog.get_logger()


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class FixPattern:
    """
    A learned fix pattern.
    نمط إصلاح متعلَّم
    """

    pattern_id: str
    rule_id: str
    tool: ToolType
    category: DiagnosticCategory

    # Pattern details
    original_pattern: str  # Regex pattern matching original code
    fix_pattern: str  # Template for fix
    context_lines: int  # Lines of context needed

    # Statistics
    success_count: int = 0
    failure_count: int = 0
    total_applications: int = 0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_used: datetime | None = None
    examples: list[dict] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0

    @property
    def confidence(self) -> float:
        """Calculate confidence based on success rate and sample size."""
        if self.total_applications < 5:
            return 0.5  # Low confidence with few samples
        return min(0.95, self.success_rate * (1 - 5 / (self.total_applications + 5)))


@dataclass
class FixFeedback:
    """
    Feedback on a fix application.
    ملاحظات على تطبيق إصلاح
    """

    feedback_id: str
    fix_id: str
    rule_id: str
    tool: ToolType

    # Outcome
    accepted: bool
    reverted: bool = False

    # Context
    file_path: str | None = None
    original_code: str | None = None
    fixed_code: str | None = None

    # Developer info
    developer_id: str | None = None
    comment: str | None = None

    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class DeveloperPreferences:
    """
    Learned developer preferences.
    تفضيلات المطور المتعلَّمة
    """

    developer_id: str

    # Style preferences
    preferred_fix_style: dict[str, str] = field(default_factory=dict)  # rule -> style
    avoided_patterns: list[str] = field(default_factory=list)

    # Tool preferences
    trusted_tools: list[ToolType] = field(default_factory=list)
    ignored_rules: list[str] = field(default_factory=list)

    # Statistics
    total_fixes_accepted: int = 0
    total_fixes_rejected: int = 0

    @property
    def acceptance_rate(self) -> float:
        total = self.total_fixes_accepted + self.total_fixes_rejected
        return self.total_fixes_accepted / total if total > 0 else 0.5


@dataclass
class LearnedFix:
    """
    A fix suggestion enhanced with learning.
    اقتراح إصلاح معزز بالتعلم
    """

    original_fix: CodeFix
    confidence: float
    pattern_id: str | None = None
    similar_fixes: list[str] = field(default_factory=list)
    developer_preference_score: float = 0.5
    reasoning: str | None = None
    reasoning_ar: str | None = None


# ============================================================================
# FIX LEARNING SYSTEM
# ============================================================================


class FixLearningSystem:
    """
    System for learning from successful code fixes.
    نظام للتعلم من إصلاحات الكود الناجحة

    Provides:
    - Pattern extraction from successful fixes
    - Success rate tracking
    - Developer preference learning
    - Fix suggestion ranking
    - Export for model training

    Example:
        learning = FixLearningSystem()

        # Record successful fix
        learning.record_fix_success(fix, diagnostic, result)

        # Get ranked fixes
        ranked_fixes = learning.rank_fixes(fixes, diagnostic, developer_id="dev1")

        # Export for training
        learning.export_training_data("training_data.jsonl")
    """

    def __init__(self, data_dir: str | None = None):
        """
        Initialize fix learning system.

        Args:
            data_dir: Directory for storing learning data
        """
        self._data_dir = data_dir or ".sahool/learning"

        # In-memory storage
        self._patterns: dict[str, FixPattern] = {}
        self._feedback: list[FixFeedback] = []
        self._developer_prefs: dict[str, DeveloperPreferences] = {}

        # Statistics
        self._rule_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
        self._category_stats: dict[DiagnosticCategory, dict[str, int]] = defaultdict(
            lambda: {"success": 0, "failure": 0, "total": 0}
        )

        # Load existing data
        self._load_data()

        logger.info("fix_learning_system_initialized", data_dir=self._data_dir)

    def record_fix_success(
        self,
        fix: CodeFix,
        diagnostic: Diagnostic,
        result: FixResult,
        developer_id: str | None = None,
    ) -> None:
        """
        Record a successful fix application.
        تسجيل تطبيق إصلاح ناجح

        Args:
            fix: The applied fix
            diagnostic: The original diagnostic
            result: The fix result
            developer_id: Optional developer identifier
        """
        if not result.success:
            self._record_failure(fix, diagnostic, developer_id)
            return

        # Update rule statistics
        rule_id = diagnostic.rule_id or "unknown"
        self._rule_stats[rule_id]["success"] += 1
        self._rule_stats[rule_id]["total"] += 1

        # Update category statistics
        self._category_stats[diagnostic.category]["success"] += 1
        self._category_stats[diagnostic.category]["total"] += 1

        # Extract and store pattern
        pattern = self._extract_pattern(fix, diagnostic)
        if pattern:
            if pattern.pattern_id in self._patterns:
                existing = self._patterns[pattern.pattern_id]
                existing.success_count += 1
                existing.total_applications += 1
                existing.last_used = datetime.now(UTC)
                # Add example if we have few
                if len(existing.examples) < 10:
                    existing.examples.append(
                        {
                            "original": fix.original_code,
                            "fixed": fix.new_code,
                            "file": diagnostic.location.file_path,
                        }
                    )
            else:
                pattern.success_count = 1
                pattern.total_applications = 1
                self._patterns[pattern.pattern_id] = pattern

        # Update developer preferences
        if developer_id:
            self._update_developer_preference(developer_id, fix, diagnostic, accepted=True)

        # Store feedback
        feedback = FixFeedback(
            feedback_id=str(uuid.uuid4()),
            fix_id=fix.id,
            rule_id=rule_id,
            tool=diagnostic.tool,
            accepted=True,
            file_path=diagnostic.location.file_path,
            original_code=fix.original_code,
            fixed_code=fix.new_code,
            developer_id=developer_id,
        )
        self._feedback.append(feedback)

        logger.debug(
            "fix_success_recorded",
            rule_id=rule_id,
            pattern_id=pattern.pattern_id if pattern else None,
        )

        # Persist periodically
        if len(self._feedback) % 100 == 0:
            self._save_data()

    def _record_failure(
        self,
        fix: CodeFix,
        diagnostic: Diagnostic,
        developer_id: str | None = None,
    ) -> None:
        """Record a failed or rejected fix."""
        rule_id = diagnostic.rule_id or "unknown"

        self._rule_stats[rule_id]["failure"] += 1
        self._rule_stats[rule_id]["total"] += 1

        self._category_stats[diagnostic.category]["failure"] += 1
        self._category_stats[diagnostic.category]["total"] += 1

        # Update pattern if exists
        pattern_id = self._compute_pattern_id(fix, diagnostic)
        if pattern_id in self._patterns:
            self._patterns[pattern_id].failure_count += 1
            self._patterns[pattern_id].total_applications += 1

        if developer_id:
            self._update_developer_preference(developer_id, fix, diagnostic, accepted=False)

    def record_fix_rejection(
        self,
        fix: CodeFix,
        diagnostic: Diagnostic,
        developer_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        """
        Record that a fix was rejected by developer.
        تسجيل رفض المطور للإصلاح
        """
        self._record_failure(fix, diagnostic, developer_id)

        feedback = FixFeedback(
            feedback_id=str(uuid.uuid4()),
            fix_id=fix.id,
            rule_id=diagnostic.rule_id or "unknown",
            tool=diagnostic.tool,
            accepted=False,
            file_path=diagnostic.location.file_path,
            original_code=fix.original_code,
            fixed_code=fix.new_code,
            developer_id=developer_id,
            comment=reason,
        )
        self._feedback.append(feedback)

    def record_fix_revert(
        self,
        fix: CodeFix,
        diagnostic: Diagnostic,
        developer_id: str | None = None,
    ) -> None:
        """
        Record that a fix was reverted.
        تسجيل التراجع عن الإصلاح
        """
        # Count reverts more heavily than rejections
        rule_id = diagnostic.rule_id or "unknown"
        self._rule_stats[rule_id]["failure"] += 2  # Weight reverts more
        self._rule_stats[rule_id]["total"] += 1

        pattern_id = self._compute_pattern_id(fix, diagnostic)
        if pattern_id in self._patterns:
            self._patterns[pattern_id].failure_count += 2

        feedback = FixFeedback(
            feedback_id=str(uuid.uuid4()),
            fix_id=fix.id,
            rule_id=rule_id,
            tool=diagnostic.tool,
            accepted=False,
            reverted=True,
            file_path=diagnostic.location.file_path,
            developer_id=developer_id,
        )
        self._feedback.append(feedback)

    def rank_fixes(
        self,
        fixes: list[CodeFix],
        diagnostic: Diagnostic,
        developer_id: str | None = None,
    ) -> list[LearnedFix]:
        """
        Rank fixes based on learned patterns and success rates.
        ترتيب الإصلاحات بناءً على الأنماط المتعلَّمة ومعدلات النجاح

        Args:
            fixes: List of possible fixes
            diagnostic: The diagnostic to fix
            developer_id: Optional developer for preference matching

        Returns:
            List of fixes ranked by confidence
        """
        learned_fixes = []

        for fix in fixes:
            # Calculate base confidence from rule success rate
            rule_id = diagnostic.rule_id or "unknown"
            rule_stats = self._rule_stats.get(rule_id)

            if rule_stats and rule_stats["total"] > 0:
                base_confidence = rule_stats["success"] / rule_stats["total"]
            else:
                base_confidence = 0.5

            # Check for matching pattern
            pattern_id = self._compute_pattern_id(fix, diagnostic)
            pattern = self._patterns.get(pattern_id)

            if pattern:
                # Use pattern confidence if available
                pattern_confidence = pattern.confidence
                confidence = 0.6 * pattern_confidence + 0.4 * base_confidence
            else:
                confidence = base_confidence

            # Apply developer preferences
            dev_score = 0.5
            if developer_id and developer_id in self._developer_prefs:
                prefs = self._developer_prefs[developer_id]

                # Check if rule is ignored
                if rule_id in prefs.ignored_rules:
                    confidence *= 0.1

                # Check tool preference
                if diagnostic.tool in prefs.trusted_tools:
                    confidence *= 1.1

                dev_score = prefs.acceptance_rate

            # Find similar fixes
            similar = self._find_similar_patterns(fix, diagnostic)

            learned_fix = LearnedFix(
                original_fix=fix,
                confidence=min(0.99, confidence),
                pattern_id=pattern_id if pattern else None,
                similar_fixes=similar[:3],
                developer_preference_score=dev_score,
                reasoning=self._generate_reasoning(fix, diagnostic, pattern),
                reasoning_ar=self._generate_reasoning_ar(fix, diagnostic, pattern),
            )
            learned_fixes.append(learned_fix)

        # Sort by confidence descending
        learned_fixes.sort(key=lambda x: x.confidence, reverse=True)

        return learned_fixes

    def get_rule_success_rate(self, rule_id: str) -> float:
        """Get success rate for a specific rule."""
        stats = self._rule_stats.get(rule_id)
        if not stats or stats["total"] == 0:
            return 0.5
        return stats["success"] / stats["total"]

    def get_category_success_rate(self, category: DiagnosticCategory) -> float:
        """Get success rate for a category."""
        stats = self._category_stats.get(category)
        if not stats or stats["total"] == 0:
            return 0.5
        return stats["success"] / stats["total"]

    def get_statistics(self) -> dict[str, Any]:
        """Get learning system statistics."""
        return {
            "total_patterns": len(self._patterns),
            "total_feedback": len(self._feedback),
            "total_developers": len(self._developer_prefs),
            "rule_stats": {
                rule: {
                    "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0,
                    "total": stats["total"],
                }
                for rule, stats in list(self._rule_stats.items())[:20]
            },
            "category_stats": {
                cat.value: {
                    "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0,
                    "total": stats["total"],
                }
                for cat, stats in self._category_stats.items()
            },
            "top_patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "rule_id": p.rule_id,
                    "success_rate": p.success_rate,
                    "total_applications": p.total_applications,
                }
                for p in sorted(
                    self._patterns.values(),
                    key=lambda x: x.total_applications,
                    reverse=True,
                )[:10]
            ],
        }

    def export_training_data(self, output_path: str, min_samples: int = 5) -> int:
        """
        Export training data for model fine-tuning.
        تصدير بيانات التدريب لضبط النموذج

        Args:
            output_path: Path to output JSONL file
            min_samples: Minimum samples for inclusion

        Returns:
            Number of examples exported
        """
        examples = []

        # Export from feedback
        for fb in self._feedback:
            if fb.accepted and fb.original_code and fb.fixed_code:
                examples.append(
                    {
                        "type": "code_fix",
                        "rule_id": fb.rule_id,
                        "tool": fb.tool.value,
                        "original": fb.original_code,
                        "fixed": fb.fixed_code,
                        "file_path": fb.file_path,
                    }
                )

        # Export from patterns with examples
        for pattern in self._patterns.values():
            if pattern.total_applications >= min_samples:
                for example in pattern.examples:
                    examples.append(
                        {
                            "type": "pattern_fix",
                            "pattern_id": pattern.pattern_id,
                            "rule_id": pattern.rule_id,
                            "tool": pattern.tool.value,
                            "category": pattern.category.value,
                            "original": example["original"],
                            "fixed": example["fixed"],
                            "confidence": pattern.confidence,
                        }
                    )

        # Write JSONL
        with open(output_path, "w") as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")

        logger.info("training_data_exported", count=len(examples), path=output_path)
        return len(examples)

    def _extract_pattern(self, fix: CodeFix, diagnostic: Diagnostic) -> FixPattern | None:
        """Extract a pattern from a fix."""
        if not fix.original_code or not fix.new_code:
            return None

        pattern_id = self._compute_pattern_id(fix, diagnostic)

        # Create simple pattern (can be enhanced with AST parsing)
        original_pattern = re.escape(fix.original_code.strip())
        fix_pattern = fix.new_code.strip()

        return FixPattern(
            pattern_id=pattern_id,
            rule_id=diagnostic.rule_id or "unknown",
            tool=diagnostic.tool,
            category=diagnostic.category,
            original_pattern=original_pattern,
            fix_pattern=fix_pattern,
            context_lines=3,
            examples=[
                {
                    "original": fix.original_code,
                    "fixed": fix.new_code,
                    "file": diagnostic.location.file_path,
                }
            ],
        )

    def _compute_pattern_id(self, fix: CodeFix, diagnostic: Diagnostic) -> str:
        """Compute unique pattern ID."""
        content = f"{diagnostic.rule_id}:{diagnostic.tool.value}:{fix.original_code or ''}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @staticmethod
    def _legacy_pattern_id(content: str) -> str:
        """Compute legacy MD5-based pattern ID for migration compatibility."""
        return hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[
            :16
        ]  # nosemgrep: insecure-hash-algorithm-md5

    def _find_similar_patterns(self, fix: CodeFix, diagnostic: Diagnostic) -> list[str]:
        """Find similar patterns."""
        similar = []
        rule_id = diagnostic.rule_id or "unknown"

        for pattern in self._patterns.values():
            if pattern.rule_id == rule_id and pattern.success_rate > 0.7:
                similar.append(pattern.pattern_id)

        return similar

    def _update_developer_preference(
        self,
        developer_id: str,
        fix: CodeFix,
        diagnostic: Diagnostic,
        accepted: bool,
    ) -> None:
        """Update developer preferences."""
        if developer_id not in self._developer_prefs:
            self._developer_prefs[developer_id] = DeveloperPreferences(developer_id=developer_id)

        prefs = self._developer_prefs[developer_id]

        if accepted:
            prefs.total_fixes_accepted += 1
            if diagnostic.tool not in prefs.trusted_tools:
                prefs.trusted_tools.append(diagnostic.tool)
        else:
            prefs.total_fixes_rejected += 1

    def _generate_reasoning(
        self,
        fix: CodeFix,
        diagnostic: Diagnostic,
        pattern: FixPattern | None,
    ) -> str:
        """Generate reasoning for fix suggestion."""
        parts = []

        if pattern:
            parts.append(
                f"Based on {pattern.total_applications} similar fixes with {pattern.success_rate:.0%} success rate"
            )

        rule_rate = self.get_rule_success_rate(diagnostic.rule_id or "unknown")
        if rule_rate > 0.8:
            parts.append(f"Rule {diagnostic.rule_id} fixes have high success rate ({rule_rate:.0%})")
        elif rule_rate < 0.5:
            parts.append(f"Caution: Rule {diagnostic.rule_id} fixes have low success rate ({rule_rate:.0%})")

        return ". ".join(parts) if parts else "Standard fix suggestion"

    def _generate_reasoning_ar(
        self,
        fix: CodeFix,
        diagnostic: Diagnostic,
        pattern: FixPattern | None,
    ) -> str:
        """Generate Arabic reasoning for fix suggestion."""
        parts = []

        if pattern:
            parts.append(f"بناءً على {pattern.total_applications} إصلاحات مماثلة بمعدل نجاح {pattern.success_rate:.0%}")

        rule_rate = self.get_rule_success_rate(diagnostic.rule_id or "unknown")
        if rule_rate > 0.8:
            parts.append(f"إصلاحات القاعدة {diagnostic.rule_id} لديها معدل نجاح عالي ({rule_rate:.0%})")
        elif rule_rate < 0.5:
            parts.append(f"تحذير: إصلاحات القاعدة {diagnostic.rule_id} لديها معدل نجاح منخفض ({rule_rate:.0%})")

        return ". ".join(parts) if parts else "اقتراح إصلاح قياسي"

    def _load_data(self) -> None:
        """Load persisted learning data.

        Supports migration from legacy MD5-based pattern IDs to SHA256.
        Patterns stored with old MD5 IDs are re-keyed under both the
        original (legacy) ID and the new SHA256 ID so lookups work
        regardless of which scheme generated the key.
        """
        if not os.path.exists(self._data_dir):
            return

        # Load patterns
        patterns_path = os.path.join(self._data_dir, "patterns.json")
        if os.path.exists(patterns_path):
            try:
                with open(patterns_path) as f:
                    data = json.load(f)
                    for p in data:
                        pattern = FixPattern(
                            pattern_id=p["pattern_id"],
                            rule_id=p["rule_id"],
                            tool=ToolType(p["tool"]),
                            category=DiagnosticCategory(p["category"]),
                            original_pattern=p["original_pattern"],
                            fix_pattern=p["fix_pattern"],
                            context_lines=p.get("context_lines", 3),
                            success_count=p.get("success_count", 0),
                            failure_count=p.get("failure_count", 0),
                            total_applications=p.get("total_applications", 0),
                            examples=p.get("examples", []),
                        )
                        # Store under the persisted ID (works for both old and new)
                        self._patterns[pattern.pattern_id] = pattern

                        # Migrate: also index under the new SHA256 ID so
                        # _compute_pattern_id lookups match legacy entries.
                        content = f"{pattern.rule_id}:{pattern.tool.value}:{pattern.original_pattern or ''}"
                        new_id = hashlib.sha256(content.encode()).hexdigest()[:16]
                        if new_id != pattern.pattern_id:
                            self._patterns[new_id] = pattern
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Failed to load patterns", error=str(e))

        # Load statistics
        stats_path = os.path.join(self._data_dir, "stats.json")
        if os.path.exists(stats_path):
            try:
                with open(stats_path) as f:
                    data = json.load(f)
                    self._rule_stats.update(data.get("rule_stats", {}))
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Failed to load stats", error=str(e))

    def _save_data(self) -> None:
        """Save learning data to disk."""
        os.makedirs(self._data_dir, exist_ok=True)

        # Save patterns
        patterns_path = os.path.join(self._data_dir, "patterns.json")
        patterns_data = [
            {
                "pattern_id": p.pattern_id,
                "rule_id": p.rule_id,
                "tool": p.tool.value,
                "category": p.category.value,
                "original_pattern": p.original_pattern,
                "fix_pattern": p.fix_pattern,
                "context_lines": p.context_lines,
                "success_count": p.success_count,
                "failure_count": p.failure_count,
                "total_applications": p.total_applications,
                "examples": p.examples[:10],
            }
            for p in self._patterns.values()
        ]
        with open(patterns_path, "w") as f:
            json.dump(patterns_data, f, indent=2)

        # Save statistics
        stats_path = os.path.join(self._data_dir, "stats.json")
        with open(stats_path, "w") as f:
            json.dump(
                {
                    "rule_stats": dict(self._rule_stats),
                },
                f,
                indent=2,
            )

        logger.debug("learning_data_saved")

    def save(self) -> None:
        """Manually trigger data save."""
        self._save_data()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_fix_learning_system(data_dir: str | None = None) -> FixLearningSystem:
    """
    Factory function to create a fix learning system.
    دالة لإنشاء نظام التعلم من الإصلاحات
    """
    return FixLearningSystem(data_dir=data_dir)
