"""
SAHOOL Irrigation Advisor Agent
وكيل مستشار الري

Specialized agent for:
- Irrigation scheduling
- Water optimization
- Deficit irrigation strategies
- Crop water requirements
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from ..base_agent import (
    BaseAgent, AgentType, AgentLayer,
    AgentContext, AgentAction, AgentPercept
)

logger = logging.getLogger(__name__)


class IrrigationAdvisorAgent(BaseAgent):
    """وكيل مستشار الري - Irrigation Advisor"""

    # Crop coefficients (Kc) for Yemen
    CROP_KC = {
        "wheat": {"initial": 0.3, "mid": 1.15, "late": 0.4},
        "tomato": {"initial": 0.6, "mid": 1.15, "late": 0.8},
        "corn": {"initial": 0.3, "mid": 1.2, "late": 0.5},
        "date_palm": {"initial": 0.9, "mid": 0.95, "late": 0.95},
        "coffee": {"initial": 0.9, "mid": 0.95, "late": 0.9},
        "alfalfa": {"initial": 0.4, "mid": 1.2, "late": 1.15},
        "grape": {"initial": 0.3, "mid": 0.85, "late": 0.45}
    }

    def __init__(self, agent_id: str = "irrigation_advisor_001"):
        super().__init__(
            agent_id=agent_id,
            name="Irrigation Advisor Agent",
            name_ar="وكيل مستشار الري",
            agent_type=AgentType.GOAL_BASED,
            layer=AgentLayer.SPECIALIST,
            description="Expert agent for irrigation optimization",
            description_ar="وكيل خبير لتحسين الري"
        )

        self.state.goals = [
            "optimize_water_use",
            "prevent_water_stress",
            "maximize_water_efficiency"
        ]

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال البيانات"""
        if percept.percept_type == "soil_moisture":
            self.state.beliefs["soil_moisture"] = percept.data
        elif percept.percept_type == "weather_forecast":
            self.state.beliefs["weather"] = percept.data
        elif percept.percept_type == "crop_info":
            self.state.beliefs["crop"] = percept.data
        elif percept.percept_type == "et0_data":
            self.state.beliefs["et0"] = percept.data

        if not self.context:
            self.context = AgentContext()

    async def think(self) -> Optional[AgentAction]:
        """حساب احتياجات الري"""
        crop = self.state.beliefs.get("crop", {})
        crop_type = crop.get("type", "wheat")
        growth_stage = crop.get("growth_stage", "mid")

        # Calculate ETc
        et0 = self.state.beliefs.get("et0", {}).get("value", 5)
        kc = self.CROP_KC.get(crop_type, self.CROP_KC["wheat"]).get(growth_stage, 1.0)
        etc = et0 * kc

        # Check soil moisture
        soil_moisture = self.state.beliefs.get("soil_moisture", {}).get("value", 0.4)

        # Check upcoming rain
        weather = self.state.beliefs.get("weather", {})
        rain_expected = weather.get("rain_next_24h", 0)

        # Decision logic
        if soil_moisture < 0.25:
            urgency = "immediate"
            amount = etc * 1.5  # Extra to recover
        elif soil_moisture < 0.35 and rain_expected < 5:
            urgency = "today"
            amount = etc
        elif rain_expected >= 10:
            urgency = "skip"
            amount = 0
        else:
            urgency = "scheduled"
            amount = etc

        return AgentAction(
            action_type="irrigation_recommendation",
            parameters={
                "amount_mm": round(amount, 1),
                "urgency": urgency,
                "etc_mm": round(etc, 1),
                "soil_moisture": soil_moisture,
                "rain_expected": rain_expected,
                "duration_minutes": round(amount * 6, 0)  # Approx based on system
            },
            confidence=0.85,
            priority=1 if urgency == "immediate" else 2,
            reasoning=f"احتياج الري: {amount:.1f} مم - {'عاجل' if urgency == 'immediate' else 'مجدول'}",
            source_agent=self.agent_id
        )

    async def act(self, action: AgentAction) -> Dict[str, Any]:
        """تنفيذ التوصية"""
        return {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "recommendation": {
                "water_amount_mm": action.parameters.get("amount_mm"),
                "duration_minutes": action.parameters.get("duration_minutes"),
                "urgency": action.parameters.get("urgency"),
                "message_ar": action.reasoning
            },
            "success": True
        }
