"""
MQTT Client - SAHOOL IoT Gateway
Connects to MQTT broker and forwards messages
"""

import asyncio
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# Using aiomqtt (formerly asyncio-mqtt)
try:
    from aiomqtt import Client, MqttError
except ImportError:
    # Fallback for older package name
    from asyncio_mqtt import Client, MqttError


MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")


@dataclass
class MqttMessage:
    """Parsed MQTT message"""

    topic: str
    payload: str
    qos: int
    retain: bool


class MqttClient:
    """
    Async MQTT client for IoT sensor data ingestion
    """

    def __init__(
        self,
        broker: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
    ):
        self.broker = broker or MQTT_BROKER
        self.port = port or MQTT_PORT
        self.username = username or MQTT_USERNAME
        self.password = password or MQTT_PASSWORD
        self._client: Client | None = None
        self._running = False
        self._reconnect_interval = 5

    async def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self._client = Client(
                hostname=self.broker,
                port=self.port,
                username=self.username if self.username else None,
                password=self.password if self.password else None,
            )
            print(f"📡 Connected to MQTT broker: {self.broker}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MQTT: {e}")
            return False

    async def subscribe(self, topic: str, handler: Callable[[MqttMessage], Any]):
        """
        Subscribe to topic and process messages with handler

        Args:
            topic: MQTT topic pattern (supports wildcards: +, #)
            handler: Async function to handle each message
        """
        self._running = True

        while self._running:
            try:
                async with Client(
                    hostname=self.broker,
                    port=self.port,
                    username=self.username if self.username else None,
                    password=self.password if self.password else None,
                ) as client:
                    await client.subscribe(topic)
                    print(f"📥 Subscribed to: {topic}")

                    async for message in client.messages:
                        try:
                            msg = MqttMessage(
                                topic=str(message.topic),
                                payload=message.payload.decode("utf-8"),
                                qos=message.qos,
                                retain=message.retain,
                            )
                            await handler(msg)
                        except Exception as e:
                            print(f"❌ Error processing message: {e}")

            except MqttError as e:
                print(f"⚠️ MQTT connection lost: {e}")
                if self._running:
                    print(f"🔄 Reconnecting in {self._reconnect_interval}s...")
                    await asyncio.sleep(self._reconnect_interval)

            except Exception as e:
                print(f"❌ MQTT error: {e}")
                if self._running:
                    await asyncio.sleep(self._reconnect_interval)

    async def publish(
        self, topic: str, payload: dict, qos: int = 1, retain: bool = False
    ):
        """Publish message to MQTT topic"""
        try:
            async with Client(
                hostname=self.broker,
                port=self.port,
                username=self.username if self.username else None,
                password=self.password if self.password else None,
            ) as client:
                message = json.dumps(payload)
                await client.publish(topic, message.encode(), qos=qos, retain=retain)
                print(f"📤 Published to {topic}")
        except Exception as e:
            print(f"❌ Failed to publish: {e}")
            raise

    def stop(self):
        """Stop the client"""
        self._running = False
        print("🛑 MQTT client stopping")


class MockMqttClient(MqttClient):
    """
    Mock MQTT client for testing without real broker
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._messages: list[MqttMessage] = []

    async def connect(self) -> bool:
        print("🧪 Mock MQTT client connected")
        return True

    async def subscribe(self, topic: str, handler: Callable[[MqttMessage], Any]):
        """Process queued messages"""
        self._running = True
        while self._running and self._messages:
            msg = self._messages.pop(0)
            await handler(msg)
            await asyncio.sleep(0.1)

    def queue_message(self, topic: str, payload: dict):
        """Queue a message for testing"""
        self._messages.append(
            MqttMessage(
                topic=topic,
                payload=json.dumps(payload),
                qos=1,
                retain=False,
            )
        )

    async def publish(
        self, topic: str, payload: dict, qos: int = 1, retain: bool = False
    ):
        print(f"🧪 Mock publish to {topic}: {payload}")
