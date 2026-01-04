# Sahool Vision - Service Layer
# طبقة الخدمات لسهول فيجن

from .diagnosis_service import DiagnosisService, diagnosis_service
from .disease_service import DiseaseService, disease_service
from .prediction_service import PredictionService, prediction_service

__all__ = [
    # Classes
    "DiseaseService",
    "PredictionService",
    "DiagnosisService",
    # Singleton instances
    "disease_service",
    "prediction_service",
    "diagnosis_service",
]
