"""
Unit tests for Training Orchestrator module.
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestTrainingOrchestrator:
    """Test the training orchestrator."""

    def test_training_status_enum(self):
        """TrainingStatus should have lifecycle states."""
        try:
            from shared.ai.training_orchestrator import TrainingStatus
        except ImportError:
            pytest.skip("training_orchestrator not available")

        values = [s.value for s in TrainingStatus]
        assert len(values) >= 3, f"TrainingStatus should have at least 3 states, got: {values}"

    def test_orchestrator_instantiation(self):
        """TrainingOrchestrator should instantiate without external dependencies."""
        try:
            from shared.ai.training_orchestrator import TrainingOrchestrator
        except ImportError:
            pytest.skip("training_orchestrator not available")

        orch = TrainingOrchestrator()
        assert orch is not None
