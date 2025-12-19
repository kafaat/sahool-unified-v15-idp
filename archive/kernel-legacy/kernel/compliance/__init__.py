"""
SAHOOL Compliance Module
GDPR, data export, and compliance management
"""

from .routes_gdpr import router as gdpr_router

__all__ = ["gdpr_router"]
