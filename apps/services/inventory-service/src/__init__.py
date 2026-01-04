"""
SAHOOL Inventory Service
Inventory management with FIFO, batch tracking, and input application tracking
"""

__version__ = "1.0.0"

from .application_tracker import (
    ApplicationMethod,
    ApplicationPlan,
    ApplicationPurpose,
    ApplicationTracker,
    InputApplication,
)
