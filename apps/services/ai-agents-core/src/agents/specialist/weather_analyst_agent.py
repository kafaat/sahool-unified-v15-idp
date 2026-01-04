"""
SAHOOL Weather Analyst Agent
وكيل محلل الطقس

Specialized agent for:
- Weather impact analysis
- Agricultural weather alerts
- Growing degree days calculation
- Climate risk assessment
"""

import logging
from datetime import datetime
from typing import Any

from ..base_agent import (
    AgentAction,
    AgentContext,
    AgentLayer,
    AgentPercept,
    AgentType,
    BaseAgent,
)

logger = logging.getLogger(__name__)


class WeatherAnalystAgent(BaseAgent):
    """وكيل محلل الطقس - Weather Analyst"""

    # Agricultural weather thresholds for Yemen
    THRESHOLDS = {
        "frost": {"temp": 2, "severity": "critical"},
        "cold": {"temp": 10, "severity": "warning"},
        "heat_stress": {"temp": 38, "severity": "warning"},
        "extreme_heat": {"temp": 45, "severity": "critical"},
        "heavy_rain": {"mm": 30, "severity": "warning"},
        "drought_risk": {"days_no_rain": 14, "severity": "warning"},
        "high_wind": {"speed_kmh": 40, "severity": "warning"},
        "sandstorm": {"visibility_km": 1, "severity": "critical"},
    }

    def __init__(self, agent_id: str = "weather_analyst_001"):
        super().__init__(
            agent_id=agent_id,
            name="Weather Analyst Agent",
            name_ar="وكيل محلل الطقس",
            agent_type=AgentType.MODEL_BASED,
            layer=AgentLayer.SPECIALIST,
            description="Expert agent for agricultural weather analysis",
            description_ar="وكيل خبير لتحليل الطقس الزراعي",
        )

        self.internal_model = {
            "gdd_accumulated": 0,
            "rain_deficit": 0,
            "heat_stress_days": 0,
            "cold_stress_days": 0,
        }

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال بيانات الطقس"""
        if percept.percept_type == "current_weather":
            self.state.beliefs["current"] = percept.data
            await self._update_model(percept.data)
        elif percept.percept_type == "forecast":
            self.state.beliefs["forecast"] = percept.data
        elif percept.percept_type == "historical":
            self.state.beliefs["historical"] = percept.data

        if not self.context:
            self.context = AgentContext()

    async def _update_model(self, weather: dict[str, Any]) -> None:
        """تحديث النموذج الداخلي"""
        temp_max = weather.get("temp_max", 25)
        temp_min = weather.get("temp_min", 15)
        base_temp = 10

        # Calculate GDD
        avg_temp = (temp_max + temp_min) / 2
        if avg_temp > base_temp:
            self.internal_model["gdd_accumulated"] += avg_temp - base_temp

        # Track stress days
        if temp_max > self.THRESHOLDS["heat_stress"]["temp"]:
            self.internal_model["heat_stress_days"] += 1
        if temp_min < self.THRESHOLDS["cold"]["temp"]:
            self.internal_model["cold_stress_days"] += 1

        # Rain tracking
        rain = weather.get("precipitation", 0)
        if rain < 1:
            self.internal_model["rain_deficit"] += 1
        else:
            self.internal_model["rain_deficit"] = 0

    async def think(self) -> AgentAction | None:
        """تحليل الطقس وإصدار التنبيهات"""
        current = self.state.beliefs.get("current", {})
        forecast = self.state.beliefs.get("forecast", [])

        alerts = []

        # Check current conditions
        temp = current.get("temperature", 25)
        if temp <= self.THRESHOLDS["frost"]["temp"]:
            alerts.append(("frost", "critical", "خطر صقيع"))
        elif temp >= self.THRESHOLDS["extreme_heat"]["temp"]:
            alerts.append(("extreme_heat", "critical", "حرارة شديدة"))
        elif temp >= self.THRESHOLDS["heat_stress"]["temp"]:
            alerts.append(("heat_stress", "warning", "إجهاد حراري"))

        # Check wind
        wind = current.get("wind_speed", 0)
        if wind >= self.THRESHOLDS["high_wind"]["speed_kmh"]:
            alerts.append(("high_wind", "warning", "رياح قوية"))

        # Check forecast for upcoming risks
        for day in forecast[:3]:
            if day.get("temp_max", 25) >= 45:
                alerts.append(("upcoming_heat", "warning", "موجة حر متوقعة"))
                break
            if day.get("precipitation", 0) >= 30:
                alerts.append(("heavy_rain", "warning", "أمطار غزيرة متوقعة"))
                break

        # Check drought risk
        if self.internal_model["rain_deficit"] >= 14:
            alerts.append(
                (
                    "drought_risk",
                    "warning",
                    f"خطر جفاف - {self.internal_model['rain_deficit']} يوم بدون مطر",
                )
            )

        if alerts:
            # Return most critical alert
            alerts.sort(key=lambda x: 0 if x[1] == "critical" else 1)
            alert = alerts[0]
            return AgentAction(
                action_type="weather_alert",
                parameters={
                    "alert_type": alert[0],
                    "severity": alert[1],
                    "message_ar": alert[2],
                    "all_alerts": [
                        {"type": a[0], "severity": a[1], "message": a[2]}
                        for a in alerts
                    ],
                    "gdd_accumulated": self.internal_model["gdd_accumulated"],
                },
                confidence=0.9,
                priority=1 if alert[1] == "critical" else 2,
                reasoning=alert[2],
                source_agent=self.agent_id,
            )

        # Normal weather report
        return AgentAction(
            action_type="weather_report",
            parameters={
                "status": "normal",
                "temperature": current.get("temperature"),
                "humidity": current.get("humidity"),
                "gdd_accumulated": self.internal_model["gdd_accumulated"],
                "message_ar": "الظروف الجوية طبيعية",
            },
            confidence=0.85,
            priority=4,
            reasoning="الطقس مناسب للزراعة",
            source_agent=self.agent_id,
        )

    async def act(self, action: AgentAction) -> dict[str, Any]:
        """تنفيذ الإجراء"""
        return {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "alert": (
                action.parameters if action.action_type == "weather_alert" else None
            ),
            "report": (
                action.parameters if action.action_type == "weather_report" else None
            ),
            "success": True,
        }

    def get_gdd(self) -> float:
        """الحصول على درجات الحرارة التراكمية"""
        return self.internal_model["gdd_accumulated"]
