"""
SAHOOL Task Handlers
معالجات المهام

Task handlers for different background job types.
معالجات المهام لأنواع مختلفة من المهام الخلفية.

Author: SAHOOL Platform Team
License: MIT
"""

from .satellite_processing import handle_satellite_image_processing
from .ndvi_calculation import handle_ndvi_calculation
from .disease_detection import handle_disease_detection
from .report_generation import handle_report_generation
from .notification_send import handle_notification_send
from .data_export import handle_data_export
from .model_inference import handle_model_inference

__all__ = [
    "handle_satellite_image_processing",
    "handle_ndvi_calculation",
    "handle_disease_detection",
    "handle_report_generation",
    "handle_notification_send",
    "handle_data_export",
    "handle_model_inference",
]
