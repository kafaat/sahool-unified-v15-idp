"""
AI Agents Module
وحدة وكلاء الذكاء الاصطناعي

Contains specialized agents for different agricultural tasks.
تحتوي على وكلاء متخصصين لمهام زراعية مختلفة.
"""

from .base_agent import BaseAgent
from .field_analyst import FieldAnalystAgent
from .disease_expert import DiseaseExpertAgent
from .irrigation_advisor import IrrigationAdvisorAgent
from .yield_predictor import YieldPredictorAgent
from .ecological_expert import EcologicalExpertAgent
from .pest_management_agent import PestManagementAgent
from .market_intelligence_agent import MarketIntelligenceAgent
from .soil_science_agent import SoilScienceAgent
from .emergency_response_agent import EmergencyResponseAgent
from .realtime_monitor_agent import RealtimeMonitorAgent
from .compliance_agent import ComplianceAgent

__all__ = [
    "BaseAgent",
    "FieldAnalystAgent",
    "DiseaseExpertAgent",
    "IrrigationAdvisorAgent",
    "YieldPredictorAgent",
    "EcologicalExpertAgent",
    "PestManagementAgent",
    "MarketIntelligenceAgent",
    "SoilScienceAgent",
    "EmergencyResponseAgent",
    "RealtimeMonitorAgent",
    "ComplianceAgent",
]
