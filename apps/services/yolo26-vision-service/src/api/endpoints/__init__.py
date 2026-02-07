"""API endpoints for YOLO26 Vision Service."""

from src.api.endpoints import analysis, batch, detection, models

__all__ = ["detection", "analysis", "batch", "models"]
