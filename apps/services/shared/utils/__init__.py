"""
SAHOOL Shared Utilities
#/H'* E4*1C) D./E'* 3'GHD

Provides:
- FallbackManager: Circuit breaker and fallback patterns
- Utility functions for resilience
"""

from .fallback_manager import FallbackManager, fallback

__all__ = [
    "FallbackManager",
    "fallback",
]
