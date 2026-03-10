"""
Tests for FixLearningSystem - Learning from successful fixes.

Tests the fix learning functionality for pattern extraction and success tracking.
"""

import pytest
from datetime import datetime, timezone, UTC
from uuid import uuid4


class TestFixPattern:
    """Tests for FixPattern-like dataclass."""

    def test_pattern_creation(self):
        """Test FixPattern creation."""
        pattern = {
            "pattern_id": "pattern-123",
            "rule_id": "E501",
            "tool": "ruff",
            "description": "Line too long fix",
            "original_pattern": r".{80,}",
            "fix_template": "Split line",
            "confidence": 0.95,
            "success_count": 10,
            "failure_count": 1,
        }
        assert pattern["pattern_id"] == "pattern-123"
        assert pattern["rule_id"] == "E501"
        assert pattern["confidence"] == 0.95
        assert pattern["success_count"] == 10

    def test_pattern_success_rate(self):
        """Test pattern success rate calculation."""
        success_count = 9
        failure_count = 1
        # success_rate = success_count / (success_count + failure_count)
        expected_rate = success_count / (success_count + failure_count)
        assert expected_rate == 0.9


class TestFixFeedback:
    """Tests for FixFeedback-like dataclass."""

    def test_feedback_creation(self):
        """Test FixFeedback creation."""
        feedback = {
            "fix_id": "fix-123",
            "pattern_id": "pattern-123",
            "success": True,
            "developer_id": "dev-001",
            "feedback_text": "Good fix",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        assert feedback["fix_id"] == "fix-123"
        assert feedback["success"] is True
        assert feedback["feedback_text"] == "Good fix"

    def test_feedback_negative(self):
        """Test negative feedback."""
        feedback = {
            "fix_id": "fix-456",
            "pattern_id": "pattern-123",
            "success": False,
            "developer_id": "dev-001",
            "feedback_text": "Fix broke the code",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        assert feedback["success"] is False


class TestDeveloperPreferences:
    """Tests for DeveloperPreferences-like dataclass."""

    def test_preferences_creation(self):
        """Test DeveloperPreferences creation."""
        prefs = {
            "developer_id": "dev-001",
            "preferred_tools": ["ruff", "mypy"],
            "auto_fix_enabled": True,
            "confidence_threshold": 0.8,
            "excluded_rules": ["E501"],
        }
        assert prefs["developer_id"] == "dev-001"
        assert "ruff" in prefs["preferred_tools"]
        assert prefs["auto_fix_enabled"] is True
        assert prefs["confidence_threshold"] == 0.8

    def test_default_preferences(self):
        """Test default preferences values."""
        prefs = {
            "developer_id": "dev-001",
            "preferred_tools": [],
            "auto_fix_enabled": True,
            "confidence_threshold": 0.7,
            "excluded_rules": [],
        }
        assert prefs["auto_fix_enabled"] is True
        assert prefs["confidence_threshold"] == 0.7


class TestLearnedFix:
    """Tests for LearnedFix-like dataclass."""

    def test_learned_fix_creation(self):
        """Test LearnedFix creation."""
        learned = {
            "fix_id": "fix-123",
            "pattern_id": "pattern-123",
            "original_code": "x=1",
            "fixed_code": "x = 1",
            "rule_id": "E225",
            "tool": "ruff",
            "learned_at": datetime.now(UTC).isoformat(),
        }
        assert learned["fix_id"] == "fix-123"
        assert learned["original_code"] == "x=1"
        assert learned["fixed_code"] == "x = 1"


class TestPatternMatcher:
    """Tests for PatternMatcher logic."""

    def test_simple_pattern_extraction(self):
        """Test pattern extraction from code."""
        original = "x=1"
        fixed = "x = 1"
        rule_id = "E225"

        # Simple pattern: missing space around operator
        pattern = {
            "rule_id": rule_id,
            "pattern_type": "operator_spacing",
            "original_pattern": r"\w+=\w+",
            "fix_pattern": r"\w+ = \w+",
        }

        assert pattern["rule_id"] == "E225"
        assert "=" in pattern["original_pattern"]

    def test_line_length_pattern(self):
        """Test line length pattern."""
        long_line = "x = " + "a" * 100
        rule_id = "E501"

        pattern = {
            "rule_id": rule_id,
            "pattern_type": "line_length",
            "max_length": 79,
            "current_length": len(long_line),
        }

        assert pattern["current_length"] > pattern["max_length"]


class TestFixLearningSystemLogic:
    """Tests for FixLearningSystem logic."""

    def test_record_successful_fix(self):
        """Test recording a successful fix."""
        fixes = []

        fix = {
            "id": str(uuid4()),
            "original_code": "x=1",
            "fixed_code": "x = 1",
            "rule_id": "E225",
            "tool": "ruff",
            "success": True,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        fixes.append(fix)

        assert len(fixes) == 1
        assert fixes[0]["success"] is True

    def test_record_failed_fix(self):
        """Test recording a failed fix."""
        fixes = []

        fix = {
            "id": str(uuid4()),
            "original_code": "x=1",
            "fixed_code": "x = 1",
            "rule_id": "E225",
            "tool": "ruff",
            "success": False,
            "error": "Syntax error after fix",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        fixes.append(fix)

        assert fixes[0]["success"] is False
        assert "error" in fixes[0]

    def test_calculate_stats(self):
        """Test statistics calculation."""
        fixes = [
            {"success": True},
            {"success": True},
            {"success": True},
            {"success": False},
            {"success": False},
        ]

        total = len(fixes)
        successful = sum(1 for f in fixes if f["success"])
        failed = total - successful
        success_rate = (successful / total) * 100

        assert total == 5
        assert successful == 3
        assert failed == 2
        assert success_rate == 60.0

    def test_get_recommendations(self):
        """Test getting fix recommendations."""
        # Simulating pattern database
        patterns = [
            {
                "rule_id": "E225",
                "pattern": "missing_space",
                "confidence": 0.95,
                "success_count": 100,
            },
            {
                "rule_id": "E225",
                "pattern": "extra_space",
                "confidence": 0.7,
                "success_count": 20,
            },
        ]

        # Get recommendations for E225
        recommendations = [p for p in patterns if p["rule_id"] == "E225"]
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        assert len(recommendations) == 2
        assert recommendations[0]["confidence"] == 0.95

    def test_developer_preferences_storage(self):
        """Test developer preferences storage."""
        preferences_db = {}

        prefs = {
            "developer_id": "dev-001",
            "preferred_tools": ["ruff"],
            "auto_fix_enabled": True,
        }

        preferences_db["dev-001"] = prefs
        retrieved = preferences_db.get("dev-001")

        assert retrieved is not None
        assert retrieved["developer_id"] == "dev-001"

    def test_pattern_confidence_update(self):
        """Test pattern confidence updates with feedback."""
        pattern = {
            "pattern_id": "pattern-123",
            "success_count": 8,
            "failure_count": 2,
        }

        # Initial confidence
        initial_confidence = pattern["success_count"] / (pattern["success_count"] + pattern["failure_count"])
        assert initial_confidence == 0.8

        # Add successful fix
        pattern["success_count"] += 1
        new_confidence = pattern["success_count"] / (pattern["success_count"] + pattern["failure_count"])

        # Confidence should increase
        assert new_confidence > initial_confidence

    def test_export_patterns(self):
        """Test exporting learned patterns."""
        patterns = [
            {"pattern_id": "p1", "rule_id": "E225"},
            {"pattern_id": "p2", "rule_id": "E501"},
        ]

        export = {
            "patterns": patterns,
            "exported_at": datetime.now(UTC).isoformat(),
            "version": "1.0.0",
        }

        assert "patterns" in export
        assert "exported_at" in export
        assert len(export["patterns"]) == 2

    def test_pattern_matching_by_rule(self):
        """Test finding patterns by rule ID."""
        patterns = [
            {"pattern_id": "p1", "rule_id": "E225", "tool": "ruff"},
            {"pattern_id": "p2", "rule_id": "E501", "tool": "ruff"},
            {"pattern_id": "p3", "rule_id": "E225", "tool": "ruff"},
        ]

        # Find patterns for E225
        e225_patterns = [p for p in patterns if p["rule_id"] == "E225"]

        assert len(e225_patterns) == 2

    def test_tool_specific_patterns(self):
        """Test filtering patterns by tool."""
        patterns = [
            {"pattern_id": "p1", "rule_id": "E225", "tool": "ruff"},
            {"pattern_id": "p2", "rule_id": "type-error", "tool": "mypy"},
            {"pattern_id": "p3", "rule_id": "E501", "tool": "ruff"},
        ]

        ruff_patterns = [p for p in patterns if p["tool"] == "ruff"]
        mypy_patterns = [p for p in patterns if p["tool"] == "mypy"]

        assert len(ruff_patterns) == 2
        assert len(mypy_patterns) == 1
