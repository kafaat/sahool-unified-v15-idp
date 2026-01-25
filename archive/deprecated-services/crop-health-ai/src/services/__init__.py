# Sahool Vision - Service Layer
# طبقة الخدمات لسهول فيجن

from .context_compression import ContextCompressionService, context_compression_service
from .diagnosis_service import DiagnosisService, diagnosis_service
from .disease_service import DiseaseService, disease_service
from .evaluation_scorer import EvaluationScorer, evaluation_scorer
from .field_memory import FieldMemory, field_memory
from .prediction_service import PredictionService, prediction_service

__all__ = [
    # Classes
    "DiseaseService",
    "PredictionService",
    "DiagnosisService",
    "ContextCompressionService",
    "FieldMemory",
    "EvaluationScorer",
    # Singleton instances
    "disease_service",
    "prediction_service",
    "diagnosis_service",
    "context_compression_service",
    "field_memory",
    "evaluation_scorer",
]
