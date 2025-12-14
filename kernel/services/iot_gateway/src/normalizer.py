"""
Sensor Data Normalizer - SAHOOL IoT Gateway
Converts various sensor payloads to standard format
"""

import json
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class NormalizedReading:
    """Standardized sensor reading"""

    device_id: str
    field_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    raw_topic: Optional[str] = None
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


# Sensor type mappings for various device formats
SENSOR_TYPE_ALIASES = {
    # Soil sensors
    "soil_moisture": ["sm", "moisture", "soil_moist", "vwc"],
    "soil_temperature": ["soil_temp", "st", "ground_temp"],
    "soil_ec": ["ec", "conductivity", "electrical_conductivity", "salinity"],
    "soil_ph": ["ph", "acidity"],
    # Weather sensors
    "air_temperature": ["temp", "temperature", "air_temp", "at"],
    "air_humidity": ["humidity", "rh", "relative_humidity", "air_humidity"],
    "wind_speed": ["wind", "ws", "wind_velocity"],
    "wind_direction": ["wind_dir", "wd"],
    "rainfall": ["rain", "precipitation", "precip"],
    "solar_radiation": ["solar", "radiation", "sr", "light"],
    "atmospheric_pressure": ["pressure", "atm", "baro"],
    # Water sensors
    "water_level": ["level", "wl", "tank_level"],
    "water_flow": ["flow", "flow_rate", "wf"],
    "water_pressure": ["water_press", "wp"],
    "water_quality": ["wq", "tds"],
    # Plant sensors
    "leaf_wetness": ["lw", "leaf_wet", "wetness"],
    "canopy_temperature": ["canopy_temp", "ct"],
}

# Unit mappings
UNIT_ALIASES = {
    "%": ["percent", "pct", "%"],
    "°C": ["celsius", "c", "deg_c", "degc"],
    "°F": ["fahrenheit", "f", "deg_f"],
    "mm": ["millimeter", "millimeters"],
    "m/s": ["meters_per_second", "mps"],
    "km/h": ["kilometers_per_hour", "kph"],
    "mS/cm": ["millisiemens", "ms_cm", "ec_unit"],
    "dS/m": ["decisiemens", "ds_m"],
    "lux": ["lx", "illuminance"],
    "W/m²": ["watts_per_m2", "solar_unit"],
    "hPa": ["hectopascal", "mbar"],
    "L/min": ["liters_per_minute", "lpm"],
    "m³/h": ["cubic_meters_per_hour", "cmh"],
}


def _normalize_sensor_type(raw_type: str) -> str:
    """Map raw sensor type to standard type"""
    raw_lower = raw_type.lower().strip()

    for standard, aliases in SENSOR_TYPE_ALIASES.items():
        if raw_lower == standard or raw_lower in aliases:
            return standard

    # Return as-is if no mapping found
    return raw_lower


def _normalize_unit(raw_unit: str) -> str:
    """Map raw unit to standard unit"""
    raw_lower = raw_unit.lower().strip()

    for standard, aliases in UNIT_ALIASES.items():
        if raw_lower == standard.lower() or raw_lower in aliases:
            return standard

    return raw_unit


def _get_default_unit(sensor_type: str) -> str:
    """Get default unit for sensor type"""
    DEFAULTS = {
        "soil_moisture": "%",
        "soil_temperature": "°C",
        "soil_ec": "mS/cm",
        "soil_ph": "",
        "air_temperature": "°C",
        "air_humidity": "%",
        "wind_speed": "m/s",
        "wind_direction": "°",
        "rainfall": "mm",
        "solar_radiation": "W/m²",
        "atmospheric_pressure": "hPa",
        "water_level": "cm",
        "water_flow": "L/min",
        "leaf_wetness": "%",
    }
    return DEFAULTS.get(sensor_type, "")


def normalize(payload: str, topic: str = None) -> NormalizedReading:
    """
    Normalize raw sensor payload to standard format

    Supports multiple input formats:
    - Standard: {"device_id": "...", "field_id": "...", "type": "...", "value": ...}
    - Compact: {"d": "...", "f": "...", "t": "...", "v": ...}
    - Array: {"readings": [{"type": "...", "value": ...}, ...]}

    Args:
        payload: JSON string from sensor
        topic: Optional MQTT topic for context

    Returns:
        NormalizedReading with standardized fields
    """
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON payload: {e}")

    # Extract device_id (try multiple field names)
    device_id = (
        raw.get("device_id")
        or raw.get("deviceId")
        or raw.get("d")
        or raw.get("id")
        or _extract_device_from_topic(topic)
    )

    if not device_id:
        raise ValueError("Missing device_id in payload")

    # Extract field_id
    field_id = (
        raw.get("field_id")
        or raw.get("fieldId")
        or raw.get("f")
        or raw.get("field")
        or _extract_field_from_topic(topic)
    )

    if not field_id:
        raise ValueError("Missing field_id in payload")

    # Extract sensor type
    sensor_type_raw = (
        raw.get("type")
        or raw.get("sensor_type")
        or raw.get("sensorType")
        or raw.get("t")
        or _extract_type_from_topic(topic)
    )

    if not sensor_type_raw:
        raise ValueError("Missing sensor type in payload")

    sensor_type = _normalize_sensor_type(sensor_type_raw)

    # Extract value
    value_raw = raw.get("value") or raw.get("v") or raw.get("val")
    if value_raw is None:
        raise ValueError("Missing value in payload")

    try:
        value = float(value_raw)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid value: {value_raw}")

    # Extract unit
    unit_raw = raw.get("unit") or raw.get("u") or ""
    unit = _normalize_unit(unit_raw) if unit_raw else _get_default_unit(sensor_type)

    # Extract timestamp
    timestamp_raw = (
        raw.get("timestamp") or raw.get("ts") or raw.get("time") or raw.get("t")
    )

    if timestamp_raw:
        # Try to parse if it's a string
        if isinstance(timestamp_raw, str):
            timestamp = timestamp_raw
        elif isinstance(timestamp_raw, (int, float)):
            # Assume Unix timestamp
            timestamp = datetime.fromtimestamp(
                timestamp_raw, tz=timezone.utc
            ).isoformat()
        else:
            timestamp = datetime.now(timezone.utc).isoformat()
    else:
        timestamp = datetime.now(timezone.utc).isoformat()

    # Extract optional metadata
    metadata = raw.get("metadata") or raw.get("meta") or {}
    if raw.get("battery"):
        metadata["battery"] = raw["battery"]
    if raw.get("rssi"):
        metadata["rssi"] = raw["rssi"]

    return NormalizedReading(
        device_id=device_id,
        field_id=field_id,
        sensor_type=sensor_type,
        value=value,
        unit=unit,
        timestamp=timestamp,
        raw_topic=topic,
        metadata=metadata if metadata else None,
    )


def normalize_batch(payload: str, topic: str = None) -> list[NormalizedReading]:
    """
    Normalize batch payload with multiple readings

    Supports:
    - {"readings": [...]}
    - {"data": [...]}
    - [...]  (direct array)
    """
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON payload: {e}")

    # Find readings array
    if isinstance(raw, list):
        readings_raw = raw
    elif "readings" in raw:
        readings_raw = raw["readings"]
    elif "data" in raw:
        readings_raw = raw["data"]
    else:
        # Single reading
        return [normalize(payload, topic)]

    # Get common fields
    device_id = raw.get("device_id") or raw.get("d")
    field_id = raw.get("field_id") or raw.get("f")

    readings = []
    for r in readings_raw:
        # Inject common fields if not present
        if device_id and "device_id" not in r:
            r["device_id"] = device_id
        if field_id and "field_id" not in r:
            r["field_id"] = field_id

        readings.append(normalize(json.dumps(r), topic))

    return readings


def _extract_device_from_topic(topic: str) -> Optional[str]:
    """Extract device ID from MQTT topic"""
    if not topic:
        return None
    # Pattern: sahool/sensors/{device_id}/...
    parts = topic.split("/")
    if len(parts) >= 3 and parts[0] == "sahool" and parts[1] == "sensors":
        return parts[2]
    return None


def _extract_field_from_topic(topic: str) -> Optional[str]:
    """Extract field ID from MQTT topic"""
    if not topic:
        return None
    # Pattern: sahool/sensors/{device_id}/{field_id}/...
    parts = topic.split("/")
    if len(parts) >= 4 and parts[0] == "sahool":
        return parts[3]
    return None


def _extract_type_from_topic(topic: str) -> Optional[str]:
    """Extract sensor type from MQTT topic"""
    if not topic:
        return None
    # Pattern: sahool/sensors/{device_id}/{field_id}/{type}
    parts = topic.split("/")
    if len(parts) >= 5:
        return parts[4]
    return None
