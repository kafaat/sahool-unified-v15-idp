"""
SAHOOL Kernel Domain
Core platform capabilities: Identity, Auth, Tenancy, Users

Architecture Rules:
- kernel_domain can import from: shared
- kernel_domain CANNOT import from: field_suite, advisor
"""

__version__ = "16.0.0"
