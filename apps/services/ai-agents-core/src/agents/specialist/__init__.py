"""
SAHOOL Specialist Agents Layer
طبقة الوكلاء المتخصصة

Domain expert agents for:
- Disease diagnosis and treatment
- Yield prediction and optimization
- Irrigation planning
- Weather analysis

These agents provide deep analysis in their domains.
"""

from .disease_expert_agent import DiseaseExpertAgent
from .irrigation_advisor_agent import IrrigationAdvisorAgent
from .weather_analyst_agent import WeatherAnalystAgent
from .yield_predictor_agent import YieldPredictorAgent

__all__ = [
    "DiseaseExpertAgent",
    "YieldPredictorAgent",
    "IrrigationAdvisorAgent",
    "WeatherAnalystAgent"
]
