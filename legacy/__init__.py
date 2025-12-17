"""
SAHOOL Legacy Compatibility Layer
Provides backward-compatible imports during the domain split migration.

This module re-exports classes and functions from the new domain packages
to maintain compatibility with existing code that uses the old import paths.

DEPRECATION NOTICE:
- These imports are deprecated and will be removed in v17.0.0
- Please update your imports to use the new domain packages:
  - kernel_domain: Identity, Auth, Tenancy, Users
  - field_suite: Farms, Fields, Crops
  - advisor: AI, RAG, Context, Feedback

Example migration:
  # Old (deprecated)
  from legacy.auth import create_access_token

  # New (recommended)
  from kernel_domain.auth import create_access_token
"""

import warnings

__version__ = "16.0.0"

# Issue deprecation warning on import
warnings.warn(
    "The 'legacy' module is deprecated and will be removed in v17.0.0. "
    "Please migrate to the new domain packages: kernel_domain, field_suite, advisor.",
    DeprecationWarning,
    stacklevel=2,
)
