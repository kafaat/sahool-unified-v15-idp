"""
Sahool Cache Module
==================

يوفر هذا المودول أدوات للتخزين المؤقت (Caching) مع دعم التوافر العالي

Modules:
    - redis_sentinel: Redis Sentinel client with high availability

Author: Sahool Platform Team
License: MIT
"""

from .redis_sentinel import (
    RedisSentinelClient,
    RedisSentinelConfig,
    CircuitBreaker,
    get_redis_client,
    close_redis_client,
)

__all__ = [
    'RedisSentinelClient',
    'RedisSentinelConfig',
    'CircuitBreaker',
    'get_redis_client',
    'close_redis_client',
]

__version__ = '1.0.0'
