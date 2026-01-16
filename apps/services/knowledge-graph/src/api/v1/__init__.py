"""
V1 API routes
مسارات API الإصدار 1
"""

from .graphs import router as graphs_router
from .entities import router as entities_router
from .relationships import router as relationships_router

__all__ = ["graphs_router", "entities_router", "relationships_router"]
