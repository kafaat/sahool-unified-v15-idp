"""
SAHOOL Service Integration Layer
طبقة تكامل الخدمات

This module provides:
- Service-to-service communication
- Service discovery
- Circuit breaker pattern
- Retry mechanisms
- Caching for inter-service calls
"""

from .circuit_breaker import CircuitBreaker, CircuitState
from .client import ServiceClient, get_service_client
from .discovery import ServiceDiscovery, ServiceHealth

__all__ = [
    "ServiceClient",
    "get_service_client",
    "ServiceDiscovery",
    "ServiceHealth",
    "CircuitBreaker",
    "CircuitState",
]
