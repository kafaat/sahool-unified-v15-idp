"""
SAHOOL CRM Service - Database Module
=====================================
Database access layer for CRM service.

Provides repository classes for:
- Farmers (customers)
- Harvest Deals (opportunities)
- Interactions (activities)
"""

from .repository import (
    CRMRepository,
    FarmerRepository,
    DealRepository,
    InteractionRepository,
)

__all__ = [
    "CRMRepository",
    "FarmerRepository",
    "DealRepository",
    "InteractionRepository",
]
