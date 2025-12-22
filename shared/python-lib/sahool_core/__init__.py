"""
SAHOOL Core Python Library
Shared utilities for all Python services.
"""

from .resilient_client import CircuitBreaker, CircuitState, circuit_breaker

__version__ = "15.5.0"
__all__ = ["CircuitBreaker", "CircuitState", "circuit_breaker"]
