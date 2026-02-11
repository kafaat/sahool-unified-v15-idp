"""
Task Service Routes - مسارات خدمة المهام

This module exports all route modules for the task service.
"""

from .astronomical import router as astronomical_router
from .ndvi import router as ndvi_router
from .tasks import router as tasks_router

__all__ = [
    "tasks_router",
    "astronomical_router",
    "ndvi_router",
]
