"""
Unit tests for fallback_manager module
اختبارات وحدة لمدير الاحتياطي
"""

# Import the modules to test - use importlib to avoid namespace collision
# between repo root shared/ and apps/services/shared/
import importlib.util
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

_repo_root = Path(__file__).parent.parent.parent.parent
_module_path = _repo_root / "apps" / "services" / "shared" / "utils" / "fallback_manager.py"
_spec = importlib.util.spec_from_file_location("fallback_manager", _module_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
CircuitBreaker = _module.CircuitBreaker
CircuitState = _module.CircuitState


class TestCircuitBreaker:
    """Test CircuitBreaker functionality"""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initializes with correct defaults"""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 30
        assert cb.success_threshold == 3

    def test_circuit_breaker_custom_parameters(self):
        """Test circuit breaker with custom parameters"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10, success_threshold=2)
        assert cb.failure_threshold == 3
        assert cb.recovery_timeout == 10
        assert cb.success_threshold == 2

    def test_successful_call(self):
        """Test successful function call through circuit breaker"""
        cb = CircuitBreaker()

        def success_func():
            return "success"

        result, success = cb.call(success_func)
        assert result == "success"
        assert success is True
        assert cb.state == CircuitState.CLOSED

    def test_failed_call(self):
        """Test failed function call through circuit breaker"""
        cb = CircuitBreaker(failure_threshold=2)

        def failing_func():
            raise ValueError("Test error")

        # First failure
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.failure_count == 1
        assert cb.state == CircuitState.CLOSED

        # Second failure - should open circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.failure_count == 2
        assert cb.state == CircuitState.OPEN

    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold is reached"""
        cb = CircuitBreaker(failure_threshold=3)

        def failing_func():
            raise Exception("Simulated failure")

        # Make failures up to threshold
        for _ in range(3):
            with pytest.raises(Exception):
                cb.call(failing_func)

        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

    def test_circuit_breaker_state_transitions(self):
        """Test circuit breaker state transitions"""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        def failing_func():
            raise Exception("Error")

        # Initially closed
        assert cb.state == CircuitState.CLOSED

        # Fail to open circuit
        with pytest.raises(Exception):
            cb.call(failing_func)
        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        time.sleep(1.1)

        # Next call should attempt half-open
        def success_func():
            return "ok"

        result, success = cb.call(success_func)
        assert success is True
        # After successful call in half-open, should transition back to closed
        assert cb.state in [CircuitState.HALF_OPEN, CircuitState.CLOSED]

    def test_get_status(self):
        """Test get_status returns correct status"""
        cb = CircuitBreaker()
        status = cb.get_status()

        assert "state" in status
        assert "failure_count" in status
        assert "success_count" in status
        assert status["state"] == "closed"

    def test_reset_circuit_breaker(self):
        """Test manual reset of circuit breaker"""
        cb = CircuitBreaker(failure_threshold=1)

        def failing_func():
            raise Exception("Error")

        # Open the circuit
        with pytest.raises(Exception):
            cb.call(failing_func)
        assert cb.state == CircuitState.OPEN

        # Reset
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0


class TestCircuitState:
    """Test CircuitState enum"""

    def test_circuit_states_exist(self):
        """Test all circuit states are defined"""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


# Additional test for coverage
def test_module_import():
    """Test module can be imported via importlib"""
    # The module lives at apps/services/shared/utils/fallback_manager.py
    # and not directly importable as shared.utils.fallback_manager
    assert CircuitBreaker is not None
    assert CircuitState is not None
