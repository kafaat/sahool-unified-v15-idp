"""
IoT Rules Engine - SAHOOL Agro Rules
Rule-based automation from sensor readings
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class TaskRecommendation:
    """Task recommendation from IoT rule"""
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    task_type: str
    priority: str
    urgency_hours: int
    metadata: dict = None

    def to_dict(self) -> dict:
        return {
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "description_ar": self.description_ar,
            "description_en": self.description_en,
            "task_type": self.task_type,
            "priority": self.priority,
            "urgency_hours": self.urgency_hours,
            "metadata": self.metadata or {},
        }


# Threshold configurations by crop (can be extended)
THRESHOLDS = {
    "default": {
        "soil_moisture": {"low": 20, "critical_low": 10, "high": 80},
        "soil_temperature": {"low": 10, "high": 35, "critical_high": 40},
        "soil_ec": {"low": 0.5, "high": 4.0, "critical_high": 6.0},
        "air_temperature": {"low": 5, "high": 38, "critical_high": 42},
        "air_humidity": {"low": 30, "high": 90},
    },
    "tomato": {
        "soil_moisture": {"low": 25, "critical_low": 15, "high": 75},
        "soil_temperature": {"low": 15, "high": 30, "critical_high": 35},
        "air_temperature": {"low": 10, "high": 32, "critical_high": 38},
    },
    "wheat": {
        "soil_moisture": {"low": 15, "critical_low": 8, "high": 70},
        "soil_temperature": {"low": 5, "high": 28, "critical_high": 35},
    },
    "coffee": {
        "soil_moisture": {"low": 30, "critical_low": 20, "high": 70},
        "soil_temperature": {"low": 18, "high": 28, "critical_high": 32},
        "air_temperature": {"low": 15, "high": 28, "critical_high": 32},
    },
}


def get_threshold(sensor_type: str, crop: str = "default") -> dict:
    """Get threshold values for sensor type and crop"""
    crop_thresholds = THRESHOLDS.get(crop, THRESHOLDS["default"])
    return crop_thresholds.get(sensor_type, THRESHOLDS["default"].get(sensor_type, {}))


def rule_from_sensor(
    sensor_type: str,
    value: float,
    crop: str = "default",
    context: dict = None,
) -> Optional[TaskRecommendation]:
    """
    Evaluate sensor reading and return task recommendation if triggered

    Args:
        sensor_type: Type of sensor (soil_moisture, air_temperature, etc.)
        value: Sensor reading value
        crop: Crop type for threshold lookup
        context: Additional context (field_id, device_id, etc.)

    Returns:
        TaskRecommendation if a rule is triggered, None otherwise
    """
    threshold = get_threshold(sensor_type, crop)
    if not threshold:
        return None

    context = context or {}

    # === SOIL MOISTURE RULES ===
    if sensor_type == "soil_moisture":
        if value < threshold.get("critical_low", 10):
            return TaskRecommendation(
                title_ar="ري طارئ - رطوبة حرجة",
                title_en="Emergency Irrigation - Critical Moisture",
                description_ar=f"رطوبة التربة {value}% أقل من الحد الحرج. يلزم ري فوري.",
                description_en=f"Soil moisture {value}% below critical threshold. Immediate irrigation required.",
                task_type="irrigation",
                priority="urgent",
                urgency_hours=2,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )
        elif value < threshold.get("low", 20):
            return TaskRecommendation(
                title_ar="تشغيل ري - انخفاض الرطوبة",
                title_en="Start Irrigation - Low Moisture",
                description_ar=f"رطوبة التربة {value}% أقل من {threshold['low']}%. يوصى بالري.",
                description_en=f"Soil moisture {value}% below {threshold['low']}%. Irrigation recommended.",
                task_type="irrigation",
                priority="high",
                urgency_hours=6,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )
        elif value > threshold.get("high", 80):
            return TaskRecommendation(
                title_ar="تحقق من الصرف - رطوبة عالية",
                title_en="Check Drainage - High Moisture",
                description_ar=f"رطوبة التربة {value}% مرتفعة. تحقق من الصرف ووقف الري.",
                description_en=f"Soil moisture {value}% is high. Check drainage and stop irrigation.",
                task_type="inspection",
                priority="medium",
                urgency_hours=24,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )

    # === AIR TEMPERATURE RULES ===
    elif sensor_type == "air_temperature":
        if value > threshold.get("critical_high", 42):
            return TaskRecommendation(
                title_ar="تنبيه حرارة حرجة",
                title_en="Critical Heat Alert",
                description_ar=f"درجة الحرارة {value}°C حرجة! تفعيل التبريد/التظليل فوراً.",
                description_en=f"Temperature {value}°C is critical! Activate cooling/shading immediately.",
                task_type="emergency",
                priority="urgent",
                urgency_hours=1,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )
        elif value > threshold.get("high", 38):
            return TaskRecommendation(
                title_ar="تنبيه حرارة عالية",
                title_en="High Temperature Alert",
                description_ar=f"درجة الحرارة {value}°C مرتفعة. تحقق من إجهاد النبات.",
                description_en=f"Temperature {value}°C is high. Check for plant stress.",
                task_type="inspection",
                priority="high",
                urgency_hours=4,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )
        elif value < threshold.get("low", 5):
            return TaskRecommendation(
                title_ar="تنبيه صقيع محتمل",
                title_en="Frost Warning",
                description_ar=f"درجة الحرارة {value}°C منخفضة. احتمال صقيع!",
                description_en=f"Temperature {value}°C is low. Possible frost!",
                task_type="emergency",
                priority="urgent",
                urgency_hours=2,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )

    # === SOIL TEMPERATURE RULES ===
    elif sensor_type == "soil_temperature":
        if value > threshold.get("critical_high", 40):
            return TaskRecommendation(
                title_ar="حرارة تربة حرجة",
                title_en="Critical Soil Temperature",
                description_ar=f"حرارة التربة {value}°C حرجة. تطبيق التغطية (mulching).",
                description_en=f"Soil temperature {value}°C is critical. Apply mulching.",
                task_type="manual",
                priority="high",
                urgency_hours=6,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )
        elif value > threshold.get("high", 35):
            return TaskRecommendation(
                title_ar="حرارة تربة مرتفعة",
                title_en="High Soil Temperature",
                description_ar=f"حرارة التربة {value}°C مرتفعة. يوصى بالري للتبريد.",
                description_en=f"Soil temperature {value}°C is high. Cooling irrigation recommended.",
                task_type="irrigation",
                priority="medium",
                urgency_hours=12,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )

    # === SOIL EC (SALINITY) RULES ===
    elif sensor_type == "soil_ec":
        if value > threshold.get("critical_high", 6.0):
            return TaskRecommendation(
                title_ar="ملوحة حرجة - غسيل تربة",
                title_en="Critical Salinity - Soil Leaching Required",
                description_ar=f"ملوحة التربة {value} mS/cm حرجة! يلزم غسيل التربة.",
                description_en=f"Soil EC {value} mS/cm is critical! Soil leaching required.",
                task_type="irrigation",
                priority="urgent",
                urgency_hours=4,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )
        elif value > threshold.get("high", 4.0):
            return TaskRecommendation(
                title_ar="ملوحة عالية",
                title_en="High Salinity Alert",
                description_ar=f"ملوحة التربة {value} mS/cm مرتفعة. زيادة كمية الري للغسيل.",
                description_en=f"Soil EC {value} mS/cm is high. Increase irrigation for leaching.",
                task_type="irrigation",
                priority="high",
                urgency_hours=12,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )

    # === AIR HUMIDITY RULES ===
    elif sensor_type == "air_humidity":
        if value > threshold.get("high", 90):
            return TaskRecommendation(
                title_ar="رطوبة جوية عالية - خطر أمراض",
                title_en="High Humidity - Disease Risk",
                description_ar=f"رطوبة الجو {value}% مرتفعة. خطر انتشار الأمراض الفطرية.",
                description_en=f"Air humidity {value}% is high. Risk of fungal disease spread.",
                task_type="inspection",
                priority="medium",
                urgency_hours=24,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )
        elif value < threshold.get("low", 30):
            return TaskRecommendation(
                title_ar="رطوبة جوية منخفضة",
                title_en="Low Humidity Alert",
                description_ar=f"رطوبة الجو {value}% منخفضة. تحقق من احتياج الري.",
                description_en=f"Air humidity {value}% is low. Check irrigation needs.",
                task_type="inspection",
                priority="low",
                urgency_hours=48,
                metadata={"sensor_type": sensor_type, "value": value, "threshold": threshold},
            )

    # === WATER FLOW RULES ===
    elif sensor_type == "water_flow":
        if value == 0:
            return TaskRecommendation(
                title_ar="توقف تدفق المياه",
                title_en="Water Flow Stopped",
                description_ar="لا يوجد تدفق مياه! تحقق من المضخة والصمامات.",
                description_en="No water flow detected! Check pump and valves.",
                task_type="maintenance",
                priority="urgent",
                urgency_hours=2,
                metadata={"sensor_type": sensor_type, "value": value},
            )

    # === WATER LEVEL RULES ===
    elif sensor_type == "water_level":
        if value < 20:  # 20% tank level
            return TaskRecommendation(
                title_ar="مستوى خزان منخفض",
                title_en="Low Tank Level",
                description_ar=f"مستوى الخزان {value}% منخفض. يلزم تعبئة الخزان.",
                description_en=f"Tank level {value}% is low. Refill required.",
                task_type="maintenance",
                priority="high",
                urgency_hours=6,
                metadata={"sensor_type": sensor_type, "value": value},
            )

    return None


def evaluate_combined_rules(
    readings: list[dict],
    crop: str = "default",
) -> list[TaskRecommendation]:
    """
    Evaluate multiple readings together for combined rules

    Args:
        readings: List of sensor readings [{sensor_type, value}, ...]
        crop: Crop type

    Returns:
        List of task recommendations
    """
    recommendations = []

    # Convert to lookup
    values = {r["sensor_type"]: r["value"] for r in readings}

    # Combined rule: High temp + Low moisture = urgent irrigation
    air_temp = values.get("air_temperature")
    soil_moisture = values.get("soil_moisture")

    if air_temp and soil_moisture:
        threshold = get_threshold("soil_moisture", crop)
        temp_threshold = get_threshold("air_temperature", crop)

        if air_temp > temp_threshold.get("high", 35) and soil_moisture < threshold.get("low", 25):
            recommendations.append(
                TaskRecommendation(
                    title_ar="ري + حرارة عالية - حالة طارئة",
                    title_en="Irrigation + High Temp - Emergency",
                    description_ar=f"حرارة {air_temp}°C + رطوبة تربة {soil_moisture}%. إجهاد نباتي محتمل!",
                    description_en=f"Temp {air_temp}°C + Soil moisture {soil_moisture}%. Plant stress risk!",
                    task_type="irrigation",
                    priority="urgent",
                    urgency_hours=2,
                    metadata={
                        "air_temperature": air_temp,
                        "soil_moisture": soil_moisture,
                        "rule": "combined_heat_drought",
                    },
                )
            )

    # Combined rule: High humidity + High leaf wetness = disease risk
    air_humidity = values.get("air_humidity")
    leaf_wetness = values.get("leaf_wetness")

    if air_humidity and leaf_wetness:
        if air_humidity > 85 and leaf_wetness > 80:
            recommendations.append(
                TaskRecommendation(
                    title_ar="خطر أمراض فطرية - رطوبة + بلل أوراق",
                    title_en="Fungal Disease Risk - Humidity + Leaf Wetness",
                    description_ar=f"رطوبة جو {air_humidity}% + بلل أوراق {leaf_wetness}%. رش وقائي موصى.",
                    description_en=f"Humidity {air_humidity}% + Leaf wetness {leaf_wetness}%. Preventive spray recommended.",
                    task_type="spray",
                    priority="high",
                    urgency_hours=6,
                    metadata={
                        "air_humidity": air_humidity,
                        "leaf_wetness": leaf_wetness,
                        "rule": "combined_disease_risk",
                    },
                )
            )

    return recommendations
