"""
نماذج بيانات المستشعرات - SAHOOL IoT
Sensor Data Models - SAHOOL IoT
"""

from .sensor_data import (
    AggregatedData,
    AggregationMethod,
    SensorHealth,
    SensorReading,
    TimeGranularity,
)

__all__ = [
    "SensorReading",
    "AggregatedData",
    "SensorHealth",
    "AggregationMethod",
    "TimeGranularity",
]
