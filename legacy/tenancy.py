"""
SAHOOL Legacy Tenancy Compatibility
Re-exports from kernel_domain.tenancy

DEPRECATED: Use kernel_domain.tenancy instead
"""

import warnings

warnings.warn(
    "legacy.tenancy is deprecated. Use kernel_domain.tenancy instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from kernel_domain.tenancy import (
    Tenant,
    TenantPlan,
    TenantSettings,
    TenantService,
    TenantStatus,
)

__all__ = [
    "Tenant",
    "TenantPlan",
    "TenantSettings",
    "TenantService",
    "TenantStatus",
]
