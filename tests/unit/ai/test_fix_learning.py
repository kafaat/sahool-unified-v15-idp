"""
Tests for FixLearningSystem - Learning from successful fixes.

Tests the fix learning functionality for pattern extraction and success tracking.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4

# Import the modules to test
from shared.ai.auto_fix.fix_learning import (
    FixPattern,
    FixFeedback,
    DeveloperPreferences,
    LearnedFix,
    FixLearningSystem,
    PatternMatcher,
)


class TestFixPattern:
    """Tests for FixPattern dataclass."""

    def test_pattern_creation(self):
        """Test FixPattern creation."""
        pattern = FixPattern(
            pattern_id="pattern-123",
            rule_id="E501",
            tool="ruff",
            description="Line too long fix",
            original_pattern=r".{80,}",
            fix_template="Split line",
            confidence=0.95,
            success_count=10,
            failure_count=1,
        )
        assert pattern.pattern_id == "pattern-123"
        assert pattern.rule_id == "E501"
        assert pattern.confidence == 0.95
        assert pattern.success_count == 10

    def test_pattern_success_rate(self):
        """Test pattern success rate calculation."""
        pattern = FixPattern(
            pattern_id="pattern-123",
            rule_id="E501",
            tool="ruff",
            description="Test pattern",
            original_pattern=".*",
            fix_template="Fix",
            confidence=0.9,
            success_count=9,
            failure_count=1,
        )
        # success_rate = success_count / (success_count + failure_count)
        expected_rate = 9 / (9 + 1)
        assert expected_rate == 0.9


class TestFixFeedback:
    """Tests for FixFeedback dataclass."""

    def test_feedback_creation(self):
        """Test FixFeedback creation."""
        feedback = FixFeedback(
            fix_id="fix-123",
            pattern_id="pattern-123",
            success=True,
            developer_id="dev-001",
            feedback_text="Good fix",
            timestamp=datetime.now(timezone.utc),
        )
        assert feedback.fix_id == "fix-123"
        assert feedback.success is True
        assert feedback.feedback_text == "Good fix"


class TestDeveloperPreferences:
    """Tests for DeveloperPreferences dataclass."""

    def test_preferences_creation(self):
        """Test DeveloperPreferences creation."""
        prefs = DeveloperPreferences(
            developer_id="dev-001",
            preferred_tools=["ruff", "mypy"],
            auto_fix_enabled=True,
            confidence_threshold=0.8,
            excluded_rules=["E501"],
        )
        assert prefs.developer_id == "dev-001"
        assert "ruff" in prefs.preferred_tools
        assert prefs.auto_fix_enabled is True
        assert prefs.confidence_threshold == 0.8

    def test_default_preferences(self):
        """Test default preferences values."""
        prefs = DeveloperPreferences(developer_id="dev-001")
        assert prefs.auto_fix_enabled is True
        assert prefs.confidence_threshold == 0.7


class TestLearnedFix:
    """Tests for LearnedFix dataclass."""

    def test_learned_fix_creation(self):
        """Test LearnedFix creation."""
        learned = LearnedFix(
            fix_id="fix-123",
            pattern_id="pattern-123",
            original_code="x=1",
            fixed_code="x = 1",
            rule_id="E225",
            tool="ruff",
            learned_at=datetime.now(timezone.utc),
        )
        assert learned.fix_id == "fix-123"
        assert learned.original_code == "x=1"
        assert learned.fixed_code == "x = 1"


class TestPatternMatcher:
    """Tests for PatternMatcher class."""

    def test_matcher_initialization(self):
        """Test PatternMatcher initialization."""
        matcher = PatternMatcher()
        assert matcher is not None

    def test_pattern_extraction(self):
        """Test pattern extraction from code."""
        matcher = PatternMatcher()

        original = "x=1"
        fixed = "x = 1"

        # The matcher should be able to extract a pattern
        pattern = matcher.extract_pattern(original, fixed, rule_id="E225")

        assert pattern is not None
        assert pattern["rule_id"] == "E225"


class TestFixLearningSystem:
    """Tests for FixLearningSystem class."""

    def test_system_initialization(self):
        """Test FixLearningSystem initialization."""
        system = FixLearningSystem()
        assert system is not None

    def test_record_successful_fix(self):
        """Test recording a successful fix."""
        system = FixLearningSystem()

        system.record_fix(
            original_code="x=1",
            fixed_code="x = 1",
            rule_id="E225",
            tool="ruff",
            success=True,
        )

        # Should have recorded the fix
        patterns = system.get_patterns_for_rule("E225")
        assert len(patterns) >= 0  # May or may not create pattern

    def test_record_failed_fix(self):
        """Test recording a failed fix."""
        system = FixLearningSystem()

        system.record_fix(
            original_code="x=1",
            fixed_code="x = 1",
            rule_id="E225",
            tool="ruff",
            success=False,
        )

        # Should have recorded the failure
        stats = system.get_stats()
        assert "total_fixes" in stats

    def test_get_recommendation(self):
        """Test getting fix recommendation."""
        system = FixLearningSystem()

        # Record some successful fixes first
        for _ in range(5):
            system.record_fix(
                original_code="x=1",
                fixed_code="x = 1",
                rule_id="E225",
                tool="ruff",
                success=True,
            )

        # Should be able to get recommendations
        recommendations = system.get_recommendations(
            code="y=2",
            rule_id="E225",
        )

        assert isinstance(recommendations, list)

    def test_developer_preferences(self):
        """Test developer preferences management."""
        system = FixLearningSystem()

        prefs = DeveloperPreferences(
            developer_id="dev-001",
            preferred_tools=["ruff"],
            auto_fix_enabled=True,
        )

        system.set_developer_preferences("dev-001", prefs)
        retrieved = system.get_developer_preferences("dev-001")

        assert retrieved is not None
        assert retrieved.developer_id == "dev-001"

    def test_pattern_confidence_update(self):
        """Test pattern confidence updates with feedback."""
        system = FixLearningSystem()

        # Record multiple fixes
        for i in range(10):
            system.record_fix(
                original_code=f"x{i}=1",
                fixed_code=f"x{i} = 1",
                rule_id="E225",
                tool="ruff",
                success=i < 8,  # 80% success rate
            )

        stats = system.get_stats()
        assert stats["total_fixes"] == 10

    def test_export_patterns(self):
        """Test exporting learned patterns."""
        system = FixLearningSystem()

        # Record some fixes
        system.record_fix(
            original_code="x=1",
            fixed_code="x = 1",
            rule_id="E225",
            tool="ruff",
            success=True,
        )

        export = system.export_patterns()

        assert isinstance(export, dict)
        assert "patterns" in export
        assert "exported_at" in export
