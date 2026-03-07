"""
Unit tests for AI A/B Testing module.
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestABTestingModule:
    """Test the A/B testing framework."""

    def test_ab_test_status_enum(self):
        """ABTestStatus should have standard lifecycle states."""
        try:
            from shared.ai.ab_testing import ABTestStatus
        except ImportError:
            pytest.skip("ab_testing not available")

        values = [s.value for s in ABTestStatus]
        # Should have at minimum draft/running/completed states
        assert len(values) >= 3, f"ABTestStatus should have at least 3 states, got {len(values)}"

    def test_metric_goal_enum(self):
        """MetricGoal should define optimization directions."""
        try:
            from shared.ai.ab_testing import MetricGoal
        except ImportError:
            pytest.skip("ab_testing not available")

        values = [g.value for g in MetricGoal]
        assert len(values) >= 2, "MetricGoal should have at least minimize/maximize"
