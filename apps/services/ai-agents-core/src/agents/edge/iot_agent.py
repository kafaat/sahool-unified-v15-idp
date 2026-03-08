"""
SAHOOL IoT Edge Agent
وكيل إنترنت الأشياء الطرفي

Real-time sensor processing for:
- Soil moisture monitoring
- Temperature alerts
- Humidity tracking
- Water flow control
- Automated irrigation triggers

Target response time: < 50ms
"""

import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Any

from ..base_agent import AgentAction, AgentContext, AgentLayer, AgentPercept, AgentType, BaseAgent

logger = logging.getLogger(__name__)


class IoTAgent(BaseAgent):
    """
    وكيل إنترنت الأشياء الطرفي
    IoT Edge Agent for real-time sensor processing
    """

    # Sensor thresholds for Yemen climate
    THRESHOLDS = {
        "soil_moisture": {
            "critical_low": 0.15,  # 15%
            "low": 0.25,  # 25%
            "optimal_min": 0.35,  # 35%
            "optimal_max": 0.65,  # 65%
            "high": 0.80,  # 80%
            "critical_high": 0.90,  # 90% (waterlogging)
        },
        "temperature": {
            "frost": 2,  # °C
            "cold": 10,  # °C
            "optimal_min": 18,  # °C
            "optimal_max": 32,  # °C
            "hot": 38,  # °C
            "critical_hot": 45,  # °C
        },
        "humidity": {
            "critical_low": 20,  # %
            "low": 30,  # %
            "optimal_min": 40,  # %
            "optimal_max": 70,  # %
            "high": 85,  # %
            "critical_high": 95,  # %
        },
        "soil_ec": {
            "low": 0.5,  # dS/m
            "optimal_min": 1.0,  # dS/m
            "optimal_max": 2.5,  # dS/m
            "high": 4.0,  # dS/m - salinity warning
            "critical": 6.0,  # dS/m - critical salinity
        },
        "soil_ph": {
            "acidic": 5.5,
            "optimal_min": 6.0,
            "optimal_max": 7.5,
            "alkaline": 8.0,
            "critical_alkaline": 8.5,
        },
    }

    def __init__(self, agent_id: str = "iot_edge_001", device_id: str = ""):
        super().__init__(
            agent_id=agent_id,
            name="IoT Edge Agent",
            name_ar="وكيل إنترنت الأشياء الطرفي",
            agent_type=AgentType.MODEL_BASED,  # Maintains internal model
            layer=AgentLayer.EDGE,
            description="Real-time sensor processing and automated control",
            description_ar="معالجة المستشعرات في الوقت الفعلي والتحكم الآلي",
        )

        self.device_id = device_id

        # Sensor data buffers (sliding window for trend analysis)
        self.sensor_buffers: dict[str, deque] = {
            "soil_moisture": deque(maxlen=60),  # Last 60 readings
            "temperature": deque(maxlen=60),
            "humidity": deque(maxlen=60),
            "soil_ec": deque(maxlen=30),
            "soil_ph": deque(maxlen=30),
            "water_flow": deque(maxlen=30),
        }

        # Internal model state (Model-Based Agent)
        self.internal_model = {
            "current_state": {},
            "predicted_state": {},
            "trend": {},
            "anomalies": [],
            "last_irrigation": None,
            "irrigation_in_progress": False,
        }

        # Actuator states
        self.actuators = {
            "irrigation_valve": {"state": "closed", "last_change": None},
            "pump": {"state": "off", "last_change": None},
            "fan": {"state": "off", "last_change": None},
        }

        # Alert cooldown to prevent spam
        self.alert_cooldown: dict[str, datetime] = {}
        self.cooldown_period = timedelta(minutes=15)

        self._init_rules()

    def _init_rules(self) -> None:
        """تهيئة قواعد التحكم الآلي"""
        # Critical moisture - immediate irrigation
        self.add_rule(
            condition=lambda ctx: (
                ctx.sensor_data.get("soil_moisture", 1) < self.THRESHOLDS["soil_moisture"]["critical_low"]
                and not self.internal_model["irrigation_in_progress"]
            ),
            action=AgentAction(
                action_type="start_irrigation",
                parameters={"duration_minutes": 30, "urgency": "critical"},
                confidence=0.98,
                priority=1,
                reasoning="رطوبة التربة حرجة - أقل من 15%",
            ),
        )

        # Low moisture - scheduled irrigation
        self.add_rule(
            condition=lambda ctx: (
                ctx.sensor_data.get("soil_moisture", 1) < self.THRESHOLDS["soil_moisture"]["low"]
                and not self.internal_model["irrigation_in_progress"]
                and self._check_cooldown("irrigation_alert")
            ),
            action=AgentAction(
                action_type="irrigation_recommendation",
                parameters={"duration_minutes": 20, "urgency": "medium"},
                confidence=0.9,
                priority=2,
                reasoning="رطوبة التربة منخفضة - أقل من 25%",
            ),
        )

        # Critical temperature
        self.add_rule(
            condition=lambda ctx: (
                ctx.sensor_data.get("temperature", 25) > self.THRESHOLDS["temperature"]["critical_hot"]
            ),
            action=AgentAction(
                action_type="heat_emergency",
                parameters={"action": "activate_cooling"},
                confidence=0.99,
                priority=1,
                reasoning="درجة الحرارة خطيرة - أعلى من 45°C",
            ),
        )

        # Frost warning
        self.add_rule(
            condition=lambda ctx: ctx.sensor_data.get("temperature", 25) <= self.THRESHOLDS["temperature"]["frost"],
            action=AgentAction(
                action_type="frost_emergency",
                parameters={"action": "activate_heating"},
                confidence=0.99,
                priority=1,
                reasoning="خطر الصقيع - درجة الحرارة أقل من 2°C",
            ),
        )

        # Salinity warning
        self.add_rule(
            condition=lambda ctx: (
                ctx.sensor_data.get("soil_ec", 0) > self.THRESHOLDS["soil_ec"]["high"]
                and self._check_cooldown("salinity_alert")
            ),
            action=AgentAction(
                action_type="salinity_alert",
                parameters={"ec_value": 0},  # Value populated at runtime by rule engine
                confidence=0.95,
                priority=2,
                reasoning="ملوحة التربة مرتفعة - قد تؤثر على المحصول",
            ),
        )

    def _check_cooldown(self, alert_type: str) -> bool:
        """التحقق من فترة الانتظار بين التنبيهات"""
        last_alert = self.alert_cooldown.get(alert_type)
        if last_alert is None:
            return True
        return datetime.now() - last_alert > self.cooldown_period

    def _set_cooldown(self, alert_type: str) -> None:
        """تعيين فترة الانتظار"""
        self.alert_cooldown[alert_type] = datetime.now()

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال بيانات المستشعرات"""
        if percept.percept_type == "sensor_batch":
            # Batch sensor update
            for sensor_type, value in percept.data.items():
                if sensor_type in self.sensor_buffers:
                    self.sensor_buffers[sensor_type].append({"value": value, "timestamp": datetime.now()})

            # Update context
            if self.context:
                self.context.sensor_data.update(percept.data)
            else:
                self.context = AgentContext(sensor_data=percept.data)

        elif percept.percept_type == "single_sensor":
            sensor_type = percept.data.get("type")
            value = percept.data.get("value")
            if sensor_type and sensor_type in self.sensor_buffers:
                self.sensor_buffers[sensor_type].append({"value": value, "timestamp": datetime.now()})
                if self.context:
                    self.context.sensor_data[sensor_type] = value

        # Update internal model (Model-Based Agent behavior)
        await self._update_internal_model()

    async def _update_internal_model(self) -> None:
        """تحديث النموذج الداخلي"""
        # Current state
        self.internal_model["current_state"] = {
            sensor: self._get_latest_value(sensor) for sensor in self.sensor_buffers
        }

        # Calculate trends
        self.internal_model["trend"] = {sensor: self._calculate_trend(sensor) for sensor in self.sensor_buffers}

        # Predict next state
        self.internal_model["predicted_state"] = {
            sensor: self._predict_next_value(sensor) for sensor in self.sensor_buffers
        }

        # Detect anomalies
        anomalies = await self._detect_anomalies()
        if anomalies:
            self.internal_model["anomalies"] = anomalies

    def _get_latest_value(self, sensor: str) -> float | None:
        """الحصول على آخر قيمة للمستشعر"""
        buffer = self.sensor_buffers.get(sensor)
        if buffer and len(buffer) > 0:
            return buffer[-1]["value"]
        return None

    def _calculate_trend(self, sensor: str) -> dict[str, Any]:
        """حساب الاتجاه"""
        buffer = self.sensor_buffers.get(sensor)
        if not buffer or len(buffer) < 5:
            return {"direction": "unknown", "rate": 0}

        values = [r["value"] for r in list(buffer)[-10:]]
        avg_first_half = sum(values[: len(values) // 2]) / (len(values) // 2)
        avg_second_half = sum(values[len(values) // 2 :]) / (len(values) - len(values) // 2)

        diff = avg_second_half - avg_first_half
        if abs(diff) < 0.01:
            direction = "stable"
        elif diff > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return {
            "direction": direction,
            "rate": diff,
            "rate_per_hour": diff * 6,  # Assuming 10-min intervals
        }

    def _predict_next_value(self, sensor: str) -> float | None:
        """توقع القيمة التالية"""
        buffer = self.sensor_buffers.get(sensor)
        if not buffer or len(buffer) < 3:
            return None

        # Simple linear extrapolation
        values = [r["value"] for r in list(buffer)[-5:]]
        if len(values) >= 2:
            trend = values[-1] - values[-2]
            return values[-1] + trend
        return values[-1]

    async def _detect_anomalies(self) -> list[dict[str, Any]]:
        """اكتشاف الشذوذ"""
        anomalies = []

        for sensor, buffer in self.sensor_buffers.items():
            if len(buffer) < 10:
                continue

            values = [r["value"] for r in buffer]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std_dev = variance**0.5

            latest = values[-1]

            # Z-score based anomaly detection
            if std_dev > 0:
                z_score = abs(latest - mean) / std_dev
                if z_score > 3:  # More than 3 standard deviations
                    anomalies.append(
                        {
                            "sensor": sensor,
                            "value": latest,
                            "expected_range": (mean - 2 * std_dev, mean + 2 * std_dev),
                            "z_score": z_score,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

        return anomalies

    async def think(self) -> AgentAction | None:
        """التفكير واتخاذ القرار"""
        if not self.context:
            return None

        # 1. Check for anomalies first (highest priority)
        if self.internal_model.get("anomalies"):
            anomaly = self.internal_model["anomalies"][0]
            return AgentAction(
                action_type="anomaly_alert",
                parameters=anomaly,
                confidence=0.85,
                priority=1,
                reasoning=f"قراءة غير طبيعية من مستشعر {anomaly['sensor']}",
                source_agent=self.agent_id,
            )

        # 2. Check rules
        action = self.evaluate_rules(self.context)
        if action:
            action.source_agent = self.agent_id
            # Enrich rule-based actions with actual sensor values
            if action.action_type == "salinity_alert":
                action.parameters["ec_value"] = self.context.sensor_data.get("soil_ec", 0)
            return action

        # 3. Predictive action based on trends
        predicted_action = await self._predictive_action()
        if predicted_action:
            return predicted_action

        return None

    async def _predictive_action(self) -> AgentAction | None:
        """إجراء استباقي بناءً على التوقعات"""
        moisture_trend = self.internal_model["trend"].get("soil_moisture", {})
        moisture_predicted = self.internal_model["predicted_state"].get("soil_moisture")

        if moisture_predicted and moisture_trend.get("direction") == "decreasing":
            # Predict moisture will be low soon
            if moisture_predicted < self.THRESHOLDS["soil_moisture"]["low"]:
                return AgentAction(
                    action_type="predictive_irrigation",
                    parameters={
                        "predicted_moisture": moisture_predicted,
                        "time_to_low": "30 minutes",
                        "suggested_action": "schedule_irrigation",
                    },
                    confidence=0.75,
                    priority=3,
                    reasoning="توقع انخفاض الرطوبة خلال 30 دقيقة",
                    source_agent=self.agent_id,
                )

        return None

    async def act(self, action: AgentAction) -> dict[str, Any]:
        """تنفيذ الإجراء"""
        result = {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "success": True,
        }

        if action.action_type == "start_irrigation":
            # Control irrigation valve
            self.actuators["irrigation_valve"]["state"] = "open"
            self.actuators["pump"]["state"] = "on"
            self.internal_model["irrigation_in_progress"] = True
            self.internal_model["last_irrigation"] = datetime.now()

            duration = action.parameters.get("duration_minutes", 20)
            result["actuator_commands"] = [
                {"device": "valve", "command": "open"},
                {"device": "pump", "command": "on"},
                {"schedule": f"close_after_{duration}_minutes"},
            ]
            self._set_cooldown("irrigation_alert")

        elif action.action_type == "stop_irrigation":
            self.actuators["irrigation_valve"]["state"] = "closed"
            self.actuators["pump"]["state"] = "off"
            self.internal_model["irrigation_in_progress"] = False

            result["actuator_commands"] = [
                {"device": "valve", "command": "close"},
                {"device": "pump", "command": "off"},
            ]

        elif action.action_type == "heat_emergency":
            result["notification"] = {
                "type": "emergency",
                "title": "🔥 طوارئ حرارة",
                "body": action.reasoning,
                "channels": ["sms", "push", "call"],
            }

        elif action.action_type == "frost_emergency":
            result["notification"] = {
                "type": "emergency",
                "title": "❄️ طوارئ صقيع",
                "body": action.reasoning,
                "channels": ["sms", "push", "call"],
            }

        elif action.action_type == "anomaly_alert":
            self._set_cooldown(f"anomaly_{action.parameters.get('sensor')}")
            result["notification"] = {
                "type": "warning",
                "title": "⚠️ قراءة غير طبيعية",
                "body": action.reasoning,
            }

        return result

    def get_sensor_status(self) -> dict[str, Any]:
        """الحصول على حالة المستشعرات"""
        return {
            "current_values": self.internal_model["current_state"],
            "trends": self.internal_model["trend"],
            "predictions": self.internal_model["predicted_state"],
            "anomalies": self.internal_model["anomalies"],
            "actuators": self.actuators,
            "irrigation_in_progress": self.internal_model["irrigation_in_progress"],
        }
