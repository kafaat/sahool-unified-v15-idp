"""
Mock AI Service Implementations
تطبيقات خدمات الذكاء الاصطناعي الوهمية

Mocks for external AI services to enable testing without dependencies.
"""

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock


class MockAIService:
    """
    Mock AI service for general predictions
    خدمة ذكاء اصطناعي وهمية للتنبؤات العامة
    """

    def __init__(self, should_fail: bool = False, delay_ms: int = 50):
        self.should_fail = should_fail
        self.delay_ms = delay_ms
        self.call_count = 0
        self.last_request = None

    async def predict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Make a prediction"""
        self.call_count += 1
        self.last_request = data

        if self.should_fail:
            raise Exception("Mock AI service failure")

        return {
            "prediction": "test_prediction",
            "confidence": 0.85,
            "processing_time_ms": self.delay_ms,
            "timestamp": datetime.now().isoformat(),
        }

    def reset(self):
        """Reset mock state"""
        self.call_count = 0
        self.last_request = None


class MockDiseaseDetectionModel:
    """
    Mock disease detection model
    نموذج اكتشاف الأمراض الوهمي
    """

    def __init__(self, diseases: dict[str, float] | None = None):
        """
        Initialize with predefined disease predictions

        Args:
            diseases: Dict mapping disease_id to confidence score
        """
        self.diseases = diseases or {
            "wheat_leaf_rust": 0.87,
            "tomato_late_blight": 0.92,
            "coffee_leaf_rust": 0.78,
        }
        self.call_count = 0

    async def detect_disease(self, image_data: dict[str, Any]) -> dict[str, Any]:
        """Detect disease from image"""
        self.call_count += 1

        # Return first disease by default
        disease_id = list(self.diseases.keys())[0]
        confidence = self.diseases[disease_id]

        return {
            "disease_id": disease_id,
            "confidence": confidence,
            "affected_area": 25.5,
            "severity": "medium",
            "bounding_boxes": [{"x": 100, "y": 100, "width": 50, "height": 50}],
            "processing_time_ms": 45,
        }

    def set_disease(self, disease_id: str, confidence: float = 0.85):
        """Set specific disease to return"""
        self.diseases = {disease_id: confidence}

    async def classify_image(self, image_path: str) -> dict[str, Any]:
        """Classify image (alternative interface)"""
        return await self.detect_disease({"path": image_path})


class MockYieldPredictionModel:
    """
    Mock yield prediction model
    نموذج تنبؤ الإنتاج الوهمي
    """

    def __init__(self, base_yield: float = 4500.0):
        self.base_yield = base_yield
        self.call_count = 0

    async def predict_yield(self, context: dict[str, Any]) -> dict[str, Any]:
        """Predict crop yield"""
        self.call_count += 1

        # Simple mock calculation
        ndvi = context.get("ndvi", 0.75)
        soil_moisture = context.get("soil_moisture", 0.40)
        temperature = context.get("temperature", 25)

        # Adjust yield based on conditions
        yield_factor = (ndvi + soil_moisture) / 2
        temp_factor = 1.0 if 18 <= temperature <= 30 else 0.9

        predicted_yield = self.base_yield * yield_factor * temp_factor

        return {
            "predicted_yield_kg_per_ha": round(predicted_yield, 2),
            "confidence": 0.82,
            "factors": {
                "ndvi_score": ndvi,
                "moisture_score": soil_moisture,
                "temperature_score": temp_factor,
            },
            "range": {
                "min": round(predicted_yield * 0.85, 2),
                "max": round(predicted_yield * 1.15, 2),
            },
        }


class MockWeatherAPI:
    """
    Mock weather API service
    خدمة الطقس الوهمية
    """

    def __init__(self, conditions: str = "sunny", temperature: float = 28.0):
        self.conditions = conditions
        self.temperature = temperature
        self.call_count = 0

    async def get_current_weather(self, lat: float, lon: float) -> dict[str, Any]:
        """Get current weather"""
        self.call_count += 1

        return {
            "temperature": self.temperature,
            "humidity": 45,
            "wind_speed": 10,
            "conditions": self.conditions,
            "pressure": 1013,
            "uv_index": 7,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_forecast(self, lat: float, lon: float, days: int = 7) -> dict[str, Any]:
        """Get weather forecast"""
        self.call_count += 1

        forecast_days = []
        for i in range(days):
            forecast_days.append(
                {
                    "day": i,
                    "temp_max": self.temperature + 2,
                    "temp_min": self.temperature - 5,
                    "humidity": 45 + (i * 2),
                    "rain_probability": 10 + (i * 5),
                    "conditions": self.conditions,
                }
            )

        return {
            "location": {"lat": lat, "lon": lon},
            "forecast": forecast_days,
            "updated_at": datetime.now().isoformat(),
        }

    def set_conditions(self, conditions: str, temperature: float):
        """Set weather conditions"""
        self.conditions = conditions
        self.temperature = temperature


class MockIrrigationController:
    """
    Mock irrigation controller
    وحدة التحكم في الري الوهمية
    """

    def __init__(self):
        self.valve_state = "closed"
        self.pump_state = "off"
        self.water_flow_rate = 0.0
        self.total_water_used = 0.0
        self.commands_log = []

    async def open_valve(self) -> dict[str, Any]:
        """Open irrigation valve"""
        self.valve_state = "open"
        self.water_flow_rate = 50.0  # L/min
        self.commands_log.append({"action": "open_valve", "timestamp": datetime.now()})

        return {"success": True, "valve_state": self.valve_state}

    async def close_valve(self) -> dict[str, Any]:
        """Close irrigation valve"""
        self.valve_state = "closed"
        self.water_flow_rate = 0.0
        self.commands_log.append({"action": "close_valve", "timestamp": datetime.now()})

        return {"success": True, "valve_state": self.valve_state}

    async def start_pump(self) -> dict[str, Any]:
        """Start water pump"""
        self.pump_state = "on"
        self.commands_log.append({"action": "start_pump", "timestamp": datetime.now()})

        return {"success": True, "pump_state": self.pump_state}

    async def stop_pump(self) -> dict[str, Any]:
        """Stop water pump"""
        self.pump_state = "off"
        self.commands_log.append({"action": "stop_pump", "timestamp": datetime.now()})

        return {"success": True, "pump_state": self.pump_state}

    def get_status(self) -> dict[str, Any]:
        """Get controller status"""
        return {
            "valve_state": self.valve_state,
            "pump_state": self.pump_state,
            "water_flow_rate": self.water_flow_rate,
            "total_water_used": self.total_water_used,
            "commands_count": len(self.commands_log),
        }


class MockSensorDevice:
    """
    Mock sensor device
    جهاز استشعار وهمي
    """

    def __init__(self, device_id: str, sensor_type: str):
        self.device_id = device_id
        self.sensor_type = sensor_type
        self.readings = []
        self.is_online = True
        self.battery_level = 100

    async def read(self) -> dict[str, Any]:
        """Read sensor value"""
        if not self.is_online:
            raise ConnectionError(f"Sensor {self.device_id} is offline")

        # Generate mock reading based on sensor type
        value_map = {
            "soil_moisture": 0.35,
            "temperature": 28.5,
            "humidity": 50.0,
            "soil_ec": 1.8,
            "soil_ph": 7.0,
        }

        value = value_map.get(self.sensor_type, 0.0)

        reading = {
            "device_id": self.device_id,
            "sensor_type": self.sensor_type,
            "value": value,
            "unit": self._get_unit(),
            "battery_level": self.battery_level,
            "timestamp": datetime.now().isoformat(),
        }

        self.readings.append(reading)
        return reading

    def _get_unit(self) -> str:
        """Get unit for sensor type"""
        unit_map = {
            "soil_moisture": "%",
            "temperature": "°C",
            "humidity": "%",
            "soil_ec": "dS/m",
            "soil_ph": "pH",
        }
        return unit_map.get(self.sensor_type, "")

    def set_offline(self):
        """Simulate device going offline"""
        self.is_online = False

    def set_online(self):
        """Restore device online"""
        self.is_online = True


# Helper functions for creating mocks


def create_mock_ai_service() -> MockAIService:
    """Factory function for MockAIService"""
    return MockAIService()


def create_mock_disease_model() -> MockDiseaseDetectionModel:
    """Factory function for MockDiseaseDetectionModel"""
    return MockDiseaseDetectionModel()


def create_mock_weather_api() -> MockWeatherAPI:
    """Factory function for MockWeatherAPI"""
    return MockWeatherAPI()
