"""
Algorithms module for Terrain Core Service
وحدة الخوارزميات لخدمة تحليل التضاريس

Contains:
- DEM processing (acquisition, resampling, hole filling)
- Terrain indicator calculations (slope, aspect, flow, TWI, curvature)
"""

from .dem_processor import DEMProcessor
from .terrain_indicators import TerrainIndicatorCalculator

__all__ = ["DEMProcessor", "TerrainIndicatorCalculator"]
