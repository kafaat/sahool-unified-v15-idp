"""
AI Agents Module
وحدة وكلاء الذكاء الاصطناعي

Contains specialized agents for different agricultural tasks.
تحتوي على وكلاء متخصصين لمهام زراعية مختلفة.
"""

from .base_agent import BaseAgent
from .disease_expert import DiseaseExpertAgent
from .field_analyst import FieldAnalystAgent
from .irrigation_advisor import IrrigationAdvisorAgent
from .yield_predictor import YieldPredictorAgent

__all__ = [
    "BaseAgent",
    "FieldAnalystAgent",
    "DiseaseExpertAgent",
    "IrrigationAdvisorAgent",
    "YieldPredictorAgent",
]
