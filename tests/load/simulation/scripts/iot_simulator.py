#!/usr/bin/env python3
"""
SAHOOL IDP - IoT Device Simulator
محاكي أجهزة إنترنت الأشياء لمنصة سهول

This script simulates IoT devices sending telemetry data to the IoT gateway.
Can be used as an alternative to k6 for basic testing.

Usage:
    python iot_simulator.py --devices 10 --duration 60 --gateway http://localhost:8106
"""

import asyncio
import aiohttp
import argparse
import random
import time
import json
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SAUDI_FARM_LOCATIONS = [
    {"name": "Al-Kharj Farm", "lat": 24.1500, "lng": 47.3000, "region": "Riyadh"},
    {"name": "Al-Ahsa Oasis", "lat": 25.3800, "lng": 49.5900, "region": "Eastern"},
    {"name": "Tabuk Agricultural Zone", "lat": 28.3838, "lng": 36.5550, "region": "Tabuk"},
    {"name": "Wadi Al-Dawasir", "lat": 20.4910, "lng": 44.7800, "region": "Riyadh"},
    {"name": "Jizan Farm", "lat": 16.8892, "lng": 42.5511, "region": "Jizan"},
]

DEVICE_TYPES = {
    "soil_sensor": 0.40,
    "weather_station": 0.25,
    "irrigation_controller": 0.20,
    "gps_tracker": 0.15,
}

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SimulationStats:
    messages_sent: int = 0
    messages_success: int = 0
    messages_failed: int = 0
    total_latency_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.messages_sent == 0:
            return 0.0
        return (self.messages_success / self.messages_sent) * 100

    @property
    def avg_latency_ms(self) -> float:
        if self.messages_success == 0:
            return 0.0
        return self.total_latency_ms / self.messages_success

# ═══════════════════════════════════════════════════════════════════════════════
# DEVICE SIMULATORS
# ═══════════════════════════════════════════════════════════════════════════════

class IoTDevice:
    def __init__(self, device_id: str, device_type: str, location: dict):
        self.device_id = device_id
        self.device_type = device_type
        self.location = location
        self.battery_level = random.randint(50, 100)

    def generate_payload(self) -> Dict[str, Any]:
        raise NotImplementedError

class SoilSensor(IoTDevice):
    def generate_payload(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "readings": [
                {
                    "type": "soil_moisture",
                    "depth_cm": 20,
                    "value": 15 + random.random() * 45,
                    "unit": "percent",
                },
                {
                    "type": "soil_temperature",
                    "depth_cm": 20,
                    "value": 15 + random.random() * 25,
                    "unit": "celsius",
                },
            ],
            "location": {
                "latitude": self.location["lat"] + (random.random() - 0.5) * 0.02,
                "longitude": self.location["lng"] + (random.random() - 0.5) * 0.02,
                "farm_name": self.location["name"],
                "region": self.location["region"],
            },
            "battery_level": self.battery_level,
            "signal_strength": -30 - random.randint(0, 60),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

class WeatherStation(IoTDevice):
    def generate_payload(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "readings": {
                "temperature": {"value": 20 + random.random() * 30, "unit": "celsius"},
                "humidity": {"value": 10 + random.random() * 50, "unit": "percent"},
                "pressure": {"value": 1000 + random.random() * 30, "unit": "hPa"},
                "wind_speed": {"value": random.random() * 30, "unit": "m/s"},
                "wind_direction": {"value": random.randint(0, 360), "unit": "degrees"},
                "solar_radiation": {"value": 200 + random.random() * 800, "unit": "W/m2"},
            },
            "location": {
                "latitude": self.location["lat"],
                "longitude": self.location["lng"],
                "farm_name": self.location["name"],
                "region": self.location["region"],
            },
            "battery_level": self.battery_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

class IrrigationController(IoTDevice):
    def generate_payload(self) -> Dict[str, Any]:
        zones = random.randint(4, 8)
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "controller_status": random.choice(["running", "standby", "maintenance"]),
            "zones": [
                {
                    "zone_id": i,
                    "status": random.choice(["active", "idle", "scheduled"]),
                    "flow_rate": random.random() * 50,
                }
                for i in range(1, zones + 1)
            ],
            "total_water_today": random.randint(100, 5000),
            "pressure": 2 + random.random() * 4,
            "location": {
                "latitude": self.location["lat"],
                "longitude": self.location["lng"],
                "farm_name": self.location["name"],
            },
            "battery_level": self.battery_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

class GPSTracker(IoTDevice):
    def generate_payload(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "tracker_type": random.choice(["vehicle", "equipment", "personnel"]),
            "position": {
                "latitude": self.location["lat"] + (random.random() - 0.5) * 0.02,
                "longitude": self.location["lng"] + (random.random() - 0.5) * 0.02,
                "altitude": random.randint(100, 500),
                "accuracy": random.randint(3, 15),
                "speed": random.random() * 5,
                "heading": random.randint(0, 360),
            },
            "motion": {
                "is_moving": random.random() > 0.3,
                "distance_today": random.randint(0, 100),
            },
            "battery_level": self.battery_level,
            "signal_strength": -30 - random.randint(0, 70),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

# ═══════════════════════════════════════════════════════════════════════════════
# SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class IoTSimulator:
    def __init__(self, gateway_url: str, num_devices: int, duration_seconds: int):
        self.gateway_url = gateway_url.rstrip("/")
        self.num_devices = num_devices
        self.duration_seconds = duration_seconds
        self.devices: List[IoTDevice] = []
        self.stats = SimulationStats()
        self.running = False

    def create_devices(self):
        """Create simulated devices based on distribution."""
        device_id = 0
        for device_type, ratio in DEVICE_TYPES.items():
            count = max(1, int(self.num_devices * ratio))
            for _ in range(count):
                location = random.choice(SAUDI_FARM_LOCATIONS)
                device_id += 1
                dev_id = f"{device_type}_{device_id:04d}"

                if device_type == "soil_sensor":
                    device = SoilSensor(dev_id, device_type, location)
                elif device_type == "weather_station":
                    device = WeatherStation(dev_id, device_type, location)
                elif device_type == "irrigation_controller":
                    device = IrrigationController(dev_id, device_type, location)
                else:
                    device = GPSTracker(dev_id, device_type, location)

                self.devices.append(device)

        logger.info(f"Created {len(self.devices)} simulated devices")

    async def send_telemetry(self, session: aiohttp.ClientSession, device: IoTDevice):
        """Send telemetry data for a device."""
        payload = device.generate_payload()
        topic = f"sahool/iot/{device.device_type}/{device.location['region'].lower()}/{device.device_id}"

        data = {
            "topic": topic,
            "payload": payload,
            "qos": 1,
            "retain": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        headers = {
            "Content-Type": "application/json",
            "X-Device-ID": device.device_id,
            "X-Device-Type": device.device_type,
        }

        start_time = time.time()
        self.stats.messages_sent += 1

        try:
            async with session.post(
                f"{self.gateway_url}/api/iot/telemetry",
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                latency = (time.time() - start_time) * 1000

                if response.status in [200, 201, 202, 404]:
                    self.stats.messages_success += 1
                    self.stats.total_latency_ms += latency
                else:
                    self.stats.messages_failed += 1
                    logger.warning(f"Device {device.device_id}: HTTP {response.status}")

        except asyncio.TimeoutError:
            self.stats.messages_failed += 1
            logger.warning(f"Device {device.device_id}: Timeout")
        except aiohttp.ClientError as e:
            self.stats.messages_failed += 1
            logger.warning(f"Device {device.device_id}: {e}")

    async def device_loop(self, session: aiohttp.ClientSession, device: IoTDevice):
        """Run continuous telemetry loop for a device."""
        interval = {
            "soil_sensor": 30,
            "weather_station": 60,
            "irrigation_controller": 45,
            "gps_tracker": 10,
        }.get(device.device_type, 30)

        while self.running:
            await self.send_telemetry(session, device)
            await asyncio.sleep(interval + random.random() * 5)

    async def run(self):
        """Run the simulation."""
        self.create_devices()
        self.running = True

        logger.info("=" * 70)
        logger.info("  SAHOOL IDP - IoT Simulation Started")
        logger.info("  محاكاة أجهزة إنترنت الأشياء")
        logger.info("=" * 70)
        logger.info(f"  Gateway URL: {self.gateway_url}")
        logger.info(f"  Devices: {len(self.devices)}")
        logger.info(f"  Duration: {self.duration_seconds}s")
        logger.info("=" * 70)

        async with aiohttp.ClientSession() as session:
            # Start all device loops
            tasks = [
                asyncio.create_task(self.device_loop(session, device))
                for device in self.devices
            ]

            # Run for specified duration
            await asyncio.sleep(self.duration_seconds)
            self.running = False

            # Cancel all tasks
            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

        self.print_results()

    def print_results(self):
        """Print simulation results."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("  SIMULATION RESULTS - نتائج المحاكاة")
        logger.info("=" * 70)
        logger.info(f"  Messages Sent:     {self.stats.messages_sent}")
        logger.info(f"  Messages Success:  {self.stats.messages_success}")
        logger.info(f"  Messages Failed:   {self.stats.messages_failed}")
        logger.info(f"  Success Rate:      {self.stats.success_rate:.2f}%")
        logger.info(f"  Avg Latency:       {self.stats.avg_latency_ms:.2f}ms")
        logger.info("=" * 70)

        # Save results to JSON
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "configuration": {
                "gateway_url": self.gateway_url,
                "num_devices": self.num_devices,
                "duration_seconds": self.duration_seconds,
            },
            "results": {
                "messages_sent": self.stats.messages_sent,
                "messages_success": self.stats.messages_success,
                "messages_failed": self.stats.messages_failed,
                "success_rate": self.stats.success_rate,
                "avg_latency_ms": self.stats.avg_latency_ms,
            }
        }

        results_file = "iot_simulation_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"  Results saved to: {results_file}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL IoT Device Simulator - محاكي أجهزة إنترنت الأشياء"
    )
    parser.add_argument(
        "--gateway", "-g",
        default="http://localhost:8106",
        help="IoT Gateway URL (default: http://localhost:8106)"
    )
    parser.add_argument(
        "--devices", "-d",
        type=int,
        default=10,
        help="Number of devices to simulate (default: 10)"
    )
    parser.add_argument(
        "--duration", "-t",
        type=int,
        default=60,
        help="Duration in seconds (default: 60)"
    )

    args = parser.parse_args()

    simulator = IoTSimulator(
        gateway_url=args.gateway,
        num_devices=args.devices,
        duration_seconds=args.duration
    )

    try:
        asyncio.run(simulator.run())
    except KeyboardInterrupt:
        logger.info("\nSimulation stopped by user")

if __name__ == "__main__":
    main()
