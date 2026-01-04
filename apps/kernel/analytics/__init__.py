"""
تحليلات SAHOOL - SAHOOL Analytics
==================================
نظام تحليل نشاط المستخدمين والمزارعين

User and farmer activity analytics system
"""

from .models import (
    # Enums
    EventType,
    UserRole,
    Governorate,
    TimePeriod,
    # Models
    AnalyticsEvent,
    UserMetrics,
    CohortAnalysis,
    FeatureUsage,
    RegionalMetrics,
    FarmerAnalytics,
)

from .user_analytics import (
    UserAnalyticsService,
    InMemoryStorage,
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
