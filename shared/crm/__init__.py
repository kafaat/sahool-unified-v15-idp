"""
SAHOOL CRM Module
=================
وحدة إدارة علاقات العملاء

Farmer relationship management inspired by CordysCRM.

Features:
- Farmer lifecycle management
- Harvest deal pipeline
- Interaction tracking
- Natural language queries (SQLBot-inspired)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .farmer_crm import (
    # Enums
    DealStage,
    # Models
    Farmer,
    # Services
    FarmerCRMService,
    FarmerQueryBot,
    FarmerStatus,
    HarvestDeal,
    Interaction,
    InteractionType,
    Payment,
    SupplyContract,
)

__all__ = [
    # Enums
    "DealStage",
    "FarmerStatus",
    "InteractionType",
    # Models
    "Farmer",
    "HarvestDeal",
    "Interaction",
    "Payment",
    "SupplyContract",
    # Services
    "FarmerCRMService",
    "FarmerQueryBot",
]
