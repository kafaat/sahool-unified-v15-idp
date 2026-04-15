"""v1 API package for inventory-service."""

from .inventory import router as inventory_router

__all__ = ["inventory_router"]
