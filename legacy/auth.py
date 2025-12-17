"""
SAHOOL Legacy Auth Compatibility
Re-exports from kernel_domain.auth

DEPRECATED: Use kernel_domain.auth instead
"""

import warnings

warnings.warn(
    "legacy.auth is deprecated. Use kernel_domain.auth instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from kernel_domain.auth import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)

__all__ = [
    "create_access_token",
    "decode_token",
    "hash_password",
    "verify_password",
]
