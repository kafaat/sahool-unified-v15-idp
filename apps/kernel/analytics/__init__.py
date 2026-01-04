"""
تحليلات SAHOOL - SAHOOL Analytics
==================================
نظام تحليل نشاط المستخدمين والمزارعين

User and farmer activity analytics system
"""

from .models import (
    # Models
    AnalyticsEvent,
    CohortAnalysis,
    # Enums
    EventType,
    FarmerAnalytics,
    FeatureUsage,
    Governorate,
    RegionalMetrics,
    TimePeriod,
    UserMetrics,
    UserRole,
)
from .user_analytics import (
    InMemoryStorage,
    UserAnalyticsService,
)

__all__ = [
    # Enums
    "EventType",
    "UserRole",
    "Governorate",
    "TimePeriod",
    # Models
    "AnalyticsEvent",
    "UserMetrics",
    "CohortAnalysis",
    "FeatureUsage",
    "RegionalMetrics",
    "FarmerAnalytics",
    # Services
    "UserAnalyticsService",
    "InMemoryStorage",
]

__version__ = "1.0.0"
