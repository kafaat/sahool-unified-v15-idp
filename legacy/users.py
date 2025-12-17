"""
SAHOOL Legacy Users Compatibility
Re-exports from kernel_domain.users

DEPRECATED: Use kernel_domain.users instead
"""

import warnings

warnings.warn(
    "legacy.users is deprecated. Use kernel_domain.users instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from kernel_domain.users import (
    User,
    UserProfile,
    UserService,
)

__all__ = [
    "User",
    "UserProfile",
    "UserService",
]
