"""
SAHOOL AI Agents Core
نواة وكلاء الذكاء الاصطناعي

Hierarchical Multi-Agent System with 4 layers:
1. Edge Layer    - Fast response (< 100ms)
2. Specialist    - Domain experts
3. Coordinator   - Decision integration
4. Learning      - Continuous improvement

Agent Types Implemented:
- Simple Reflex Agent (condition → action)
- Model-Based Agent (internal world model)
- Goal-Based Agent (goal-oriented decisions)
- Utility-Based Agent (optimal outcome selection)
- Learning Agent (reinforcement learning)
"""

from .base_agent import (
    AgentAction,
    AgentContext,
    AgentLayer,
    AgentPercept,
    AgentState,
    AgentStatus,
    AgentType,
    BaseAgent,
)
from .coordinator import MasterCoordinatorAgent
from .edge import DroneAgent, IoTAgent, MobileAgent
from .learning import FeedbackLearnerAgent, KnowledgeMinerAgent, ModelUpdaterAgent
from .specialist import (
    DiseaseExpertAgent,
    IrrigationAdvisorAgent,
    WeatherAnalystAgent,
    YieldPredictorAgent,
)

__version__ = "1.0.0"

__all__ = [
    # Base
    "BaseAgent",
    "AgentType",
    "AgentLayer",
    "AgentStatus",
    "AgentContext",
    "AgentAction",
    "AgentPercept",
    "AgentState",

    # Edge Layer
    "MobileAgent",
    "IoTAgent",
    "DroneAgent",

    # Specialist Layer
    "DiseaseExpertAgent",
    "YieldPredictorAgent",
    "IrrigationAdvisorAgent",
    "WeatherAnalystAgent",

    # Coordinator Layer
    "MasterCoordinatorAgent",

    # Learning Layer
    "FeedbackLearnerAgent",
    "ModelUpdaterAgent",
    "KnowledgeMinerAgent"
]
