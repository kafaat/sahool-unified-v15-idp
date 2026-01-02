"""
SAHOOL Edge Agents Layer
طبقة الوكلاء الطرفية

Fast response agents (< 100ms) for:
- Mobile devices
- IoT sensors
- Drone processing

These agents work offline and provide instant responses.
"""

from .mobile_agent import MobileAgent
from .iot_agent import IoTAgent
from .drone_agent import DroneAgent

__all__ = ["MobileAgent", "IoTAgent", "DroneAgent"]
