"""
Event Registry
==============

Central registry for all domain events with version management.
"""

from typing import Dict, Optional, Type, List
from .base import BaseEvent


class EventRegistry:
    """
    Central registry for all SAHOOL domain events.

    Provides:
    - Event type to class mapping
    - Version compatibility checking
    - Schema validation
    """

    _events: Dict[str, Dict[str, Type[BaseEvent]]] = {}

    @classmethod
    def register(cls, event_class: Type[BaseEvent]):
        """Register an event class"""
        event_type = event_class.EVENT_TYPE
        version = event_class.EVENT_VERSION

        if event_type not in cls._events:
            cls._events[event_type] = {}

        cls._events[event_type][version] = event_class

    @classmethod
    def get_event_class(cls, event_type: str, version: str = None) -> Optional[Type[BaseEvent]]:
        """Get event class by type and optional version"""
        if event_type not in cls._events:
            return None

        versions = cls._events[event_type]
        if version:
            return versions.get(version)

        # Return latest version
        latest = sorted(versions.keys(), reverse=True)[0]
        return versions[latest]

    @classmethod
    def list_events(cls) -> List[str]:
        """List all registered event types"""
        return list(cls._events.keys())

    @classmethod
    def list_versions(cls, event_type: str) -> List[str]:
        """List all versions for an event type"""
        if event_type not in cls._events:
            return []
        return sorted(cls._events[event_type].keys())

    @classmethod
    def is_compatible(cls, event_type: str, version: str, min_version: str) -> bool:
        """Check if a version is compatible with minimum required version"""
        def parse_version(v):
            return tuple(map(int, v.split('.')))

        return parse_version(version) >= parse_version(min_version)


# Auto-register all events
def _register_all_events():
    from . import field_events, crop_events, weather_events, iot_events, analytics_events

    for module in [field_events, crop_events, weather_events, iot_events, analytics_events]:
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, BaseEvent) and obj != BaseEvent:
                if hasattr(obj, 'EVENT_TYPE') and obj.EVENT_TYPE:
                    EventRegistry.register(obj)


_register_all_events()
