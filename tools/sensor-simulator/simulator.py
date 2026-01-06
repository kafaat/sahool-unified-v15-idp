#!/usr/bin/env python3
"""
SAHOOL IoT Sensor Simulator
محاكي حساسات إنترنت الأشياء

This script simulates IoT sensors sending data to the MQTT broker.
Useful for testing and development without real hardware.

Usage:
    python simulator.py --broker localhost --field field-1

Features:
    - Simulates multiple sensor types
    - Realistic data patterns (daily/seasonal variations)
    - Configurable intervals
    - JSON and raw value publishing
"""

import argparse
import json
import math
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

# =============================================================================
# Configuration
# =============================================================================

DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 1883
DEFAULT_FIELD_ID = "field-1"
DEFAULT_FARM_ID = "farm-1"
DEFAULT_TENANT = "default"
DEFAULT_INTERVAL = 5  # seconds

# Sensor types and their configurations
SENSORS = {
    "soil_moisture": {
        "min": 20,
        "max": 80,
        "unit": "%",
        "noise": 2,
        "trend": "daily",  # varies with time of day
    },
    "soil_temperature": {
        "min": 15,
        "max": 35,
        "unit": "°C",
        "noise": 0.5,
        "trend": "daily",
    },
    "air_temperature": {
        "min": 18,
        "max": 42,
        "unit": "°C",
        "noise": 1,
        "trend": "daily",
    },
    "air_humidity": {
        "min": 30,
        "max": 80,
        "unit": "%",
        "noise": 3,
        "trend": "inverse_daily",  # higher at night
    },
    "light_intensity": {
        "min": 0,
        "max": 100000,
        "unit": "lux",
        "noise": 1000,
        "trend": "daylight",  # follows sun
    },
    "water_level": {
        "min": 10,
        "max": 100,
        "unit": "cm",
        "noise": 1,
        "trend": "stable",
    },
    "ph_level": {
        "min": 5.5,
        "max": 7.5,
        "unit": "pH",
        "noise": 0.1,
        "trend": "stable",
    },
    "ec_level": {
        "min": 0.5,
        "max": 3.0,
        "unit": "mS/cm",
        "noise": 0.1,
        "trend": "stable",
    },
}

# =============================================================================
# Sensor Simulator Class
# =============================================================================


class SensorSimulator:
    """Simulates IoT sensors sending data to MQTT broker"""

    def __init__(
        self,
        broker: str = DEFAULT_BROKER,
        port: int = DEFAULT_PORT,
        tenant: str = DEFAULT_TENANT,
        farm_id: str = DEFAULT_FARM_ID,
        field_id: str = DEFAULT_FIELD_ID,
        username: str = None,
        password: str = None,
    ):
        self.broker = broker
        self.port = port
        self.tenant = tenant
        self.farm_id = farm_id
        self.field_id = field_id
        self.username = username
        self.password = password
        self.client: mqtt.Client | None = None
        self.running = False
        self.sensor_states: dict[str, float] = {}

        # Initialize sensor states with random starting values
        for sensor, config in SENSORS.items():
            mid = (config["max"] + config["min"]) / 2
            self.sensor_states[sensor] = mid

    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(
                client_id=f"simulator-{self.field_id}-{int(time.time())}"
            )

            # Set authentication if credentials provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
                print(f"🔐 Using authentication: {self.username}")

            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    print(f"✅ Connected to MQTT broker at {self.broker}:{self.port}")
                elif rc == 5:
                    print(f"❌ Connection failed: Authentication error (code {rc})")
                else:
                    print(f"❌ Connection failed with code {rc}")

            def on_disconnect(client, userdata, rc):
                print(f"⚠️ Disconnected from broker (rc={rc})")

            self.client.on_connect = on_connect
            self.client.on_disconnect = on_disconnect

            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            return True

        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("Disconnected from broker")

    def _get_topic(self, sensor_type: str) -> str:
        """Build MQTT topic for sensor"""
        return f"sahool/{self.tenant}/farm/{self.farm_id}/field/{self.field_id}/sensor/{sensor_type}"

    def _calculate_value(self, sensor_type: str, config: dict) -> float:
        """Calculate realistic sensor value based on time and trend"""
        current_hour = datetime.now().hour
        base_value = self.sensor_states[sensor_type]

        # Apply trend based on time of day
        trend = config.get("trend", "stable")

        if trend == "daily":
            # Peak at 2 PM (14:00), lowest at 6 AM
            phase = (current_hour - 6) / 12 * math.pi
            factor = (math.sin(phase) + 1) / 2  # 0 to 1
            target = config["min"] + factor * (config["max"] - config["min"])

        elif trend == "inverse_daily":
            # Opposite of daily (humidity higher at night)
            phase = (current_hour - 6) / 12 * math.pi
            factor = (math.sin(phase) + 1) / 2
            target = config["max"] - factor * (config["max"] - config["min"])

        elif trend == "daylight":
            # Zero at night, peak at noon
            if 6 <= current_hour <= 18:
                phase = (current_hour - 6) / 6 * math.pi / 2
                factor = math.sin(phase)
                target = config["min"] + factor * (config["max"] - config["min"])
            else:
                target = config["min"]

        else:  # stable
            target = (config["max"] + config["min"]) / 2

        # Smooth transition (exponential moving average)
        alpha = 0.1  # smoothing factor
        new_value = alpha * target + (1 - alpha) * base_value

        # Add noise
        noise = random.gauss(0, config["noise"])
        new_value += noise

        # Clamp to valid range
        new_value = max(config["min"], min(config["max"], new_value))

        # Update state
        self.sensor_states[sensor_type] = new_value

        return round(new_value, 2)

    def publish_sensor_data(self, sensor_type: str):
        """Publish sensor data to MQTT"""
        if not self.client:
            return

        config = SENSORS.get(sensor_type)
        if not config:
            return

        value = self._calculate_value(sensor_type, config)
        topic = self._get_topic(sensor_type)

        # Create payload
        payload = {
            "deviceId": f"{self.field_id}-{sensor_type}",
            "sensorType": sensor_type,
            "value": value,
            "unit": config["unit"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "quality": "good" if config["min"] < value < config["max"] else "warning",
        }

        # Publish
        self.client.publish(topic, json.dumps(payload), qos=1)

        return value

    def publish_device_status(self):
        """Publish device online status"""
        if not self.client:
            return

        topic = f"sahool/{self.tenant}/farm/{self.farm_id}/field/{self.field_id}/device/status"

        payload = {
            "deviceId": f"{self.field_id}-gateway",
            "type": "gateway",
            "name": f"حقل {self.field_id} - البوابة الرئيسية",
            "status": "online",
            "battery": random.randint(80, 100),
            "rssi": random.randint(-70, -40),  # WiFi signal strength
            "uptime": random.randint(1000, 100000),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self.client.publish(topic, json.dumps(payload), qos=1, retain=True)

    def run(self, interval: int = DEFAULT_INTERVAL):
        """Run the simulator"""
        if not self.connect():
            return

        self.running = True
        print(f"\n🚜 Starting sensor simulation for field: {self.field_id}")
        print(
            f"📡 Publishing to: sahool/{self.tenant}/farm/{self.farm_id}/field/{self.field_id}/sensor/*"
        )
        print(f"⏱️  Interval: {interval} seconds")
        print("-" * 60)

        try:
            cycle = 0
            while self.running:
                cycle += 1
                timestamp = datetime.now().strftime("%H:%M:%S")

                print(f"\n[{timestamp}] Cycle {cycle}")

                # Publish all sensor readings
                for sensor_type in SENSORS:
                    value = self.publish_sensor_data(sensor_type)
                    if value is not None:
                        unit = SENSORS[sensor_type]["unit"]
                        print(f"  📊 {sensor_type}: {value}{unit}")

                # Publish device status every 10 cycles
                if cycle % 10 == 0:
                    self.publish_device_status()
                    print("  📱 Device status: online")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⛔ Stopping simulator...")
            self.running = False

        finally:
            self.disconnect()


# =============================================================================
# Multi-Field Simulator
# =============================================================================


class MultiFarmSimulator:
    """Simulate multiple fields at once"""

    def __init__(self, broker: str, port: int, fields: list, username: str = None, password: str = None):
        self.simulators = []
        for field_id in fields:
            sim = SensorSimulator(
                broker=broker,
                port=port,
                field_id=field_id,
                username=username,
                password=password,
            )
            self.simulators.append(sim)

    def run(self, interval: int = DEFAULT_INTERVAL):
        """Run all simulators"""
        for sim in self.simulators:
            if not sim.connect():
                print(f"Failed to connect simulator for {sim.field_id}")

        print(f"\n🚜 Multi-field simulation started ({len(self.simulators)} fields)")

        try:
            while True:
                for sim in self.simulators:
                    for sensor_type in SENSORS:
                        sim.publish_sensor_data(sensor_type)
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n⛔ Stopping all simulators...")
            for sim in self.simulators:
                sim.disconnect()


# =============================================================================
# CLI
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL IoT Sensor Simulator - محاكي حساسات إنترنت الأشياء"
    )
    parser.add_argument(
        "--broker",
        "-b",
        default=DEFAULT_BROKER,
        help=f"MQTT broker address (default: {DEFAULT_BROKER})",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DEFAULT_PORT,
        help=f"MQTT broker port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--field",
        "-f",
        default=DEFAULT_FIELD_ID,
        help=f"Field ID to simulate (default: {DEFAULT_FIELD_ID})",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Publishing interval in seconds (default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--multi",
        "-m",
        nargs="+",
        help="Simulate multiple fields (e.g., --multi field-1 field-2 field-3)",
    )
    parser.add_argument(
        "--username",
        "-u",
        default=None,
        help="MQTT username for authentication",
    )
    parser.add_argument(
        "--password",
        "-P",
        default=None,
        help="MQTT password for authentication",
    )

    args = parser.parse_args()

    print(
        """
╔═══════════════════════════════════════════════════════════════════╗
║              SAHOOL IoT Sensor Simulator 🌾                       ║
║              محاكي حساسات إنترنت الأشياء                          ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    )

    if args.multi:
        simulator = MultiFarmSimulator(
            broker=args.broker,
            port=args.port,
            fields=args.multi,
            username=args.username,
            password=args.password,
        )
    else:
        simulator = SensorSimulator(
            broker=args.broker,
            port=args.port,
            field_id=args.field,
            username=args.username,
            password=args.password,
        )

    simulator.run(interval=args.interval)


if __name__ == "__main__":
    main()
