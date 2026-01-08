"""
Mock Utilities for AI Agents Testing
أدوات الاختبار الوهمية

Provides mocks for external AI services and dependencies.
"""

from .ai_service_mocks import (
    MockAIService,
    MockDiseaseDetectionModel,
    MockWeatherAPI,
    MockYieldPredictionModel,
)

__all__ = [
    "MockAIService",
    "MockDiseaseDetectionModel",
    "MockYieldPredictionModel",
    "MockWeatherAPI",
]
