"""
SAHOOL Edge Agents Layer
طبقة الوكلاء الطرفية

Fast response agents (< 100ms) for:
- Mobile devices
- IoT sensors
- Drone processing

These agents work offline and provide instant responses.
"""

from .drone_agent import DroneAgent
from .iot_agent import IoTAgent
from .mobile_agent import MobileAgent

__all__ = ["MobileAgent", "IoTAgent", "DroneAgent"]
