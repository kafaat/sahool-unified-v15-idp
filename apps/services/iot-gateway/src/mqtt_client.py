"""
MQTT Client - SAHOOL IoT Gateway
Connects to MQTT broker and forwards messages
"""

import asyncio
import json
import logging
import os
import ssl
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# Using aiomqtt (formerly asyncio-mqtt)
try:
    from aiomqtt import Client, MqttError
except ImportError:
    # Fallback for older package name
    from asyncio_mqtt import Client, MqttError

logger = logging.getLogger(__name__)

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
# Support both MQTT_USER (docker-compose) and MQTT_USERNAME (legacy) env vars
MQTT_USERNAME = os.getenv("MQTT_USER", os.getenv("MQTT_USERNAME", ""))
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

# TLS configuration
# MQTT_TLS_ENABLED: set to "true" to enable TLS (recommended for production).
# When unset, TLS is auto-enabled for port 8883 and disabled for port 1883.
_tls_env = os.getenv("MQTT_TLS_ENABLED", "").lower()
if _tls_env == "true":
    MQTT_TLS_ENABLED = True
elif _tls_env == "false":
    MQTT_TLS_ENABLED = False
else:
    # Auto-detect: enable TLS when the standard TLS port is used
    MQTT_TLS_ENABLED = MQTT_PORT == 8883

MQTT_TLS_CA_CERTS = os.getenv("MQTT_TLS_CA_CERTS")  # Path to CA bundle (optional)
MQTT_TLS_CERTFILE = os.getenv("MQTT_TLS_CERTFILE")  # Client certificate (optional)
MQTT_TLS_KEYFILE = os.getenv("MQTT_TLS_KEYFILE")  # Client private key (optional)

# Warn operators when running without TLS in non-local environments
_environment = os.getenv("ENVIRONMENT", "development").lower()
if not MQTT_TLS_ENABLED and _environment not in ("development", "test", "local"):
    logger.warning(
        "MQTT TLS is DISABLED (port %s, ENVIRONMENT=%s). "
        "Set MQTT_PORT=8883 and MQTT_TLS_ENABLED=true for production deployments "
        "to encrypt IoT sensor data in transit.",
        MQTT_PORT,
        _environment,
    )


def _build_tls_params() -> dict[str, Any]:
    """Build TLS parameters for the aiomqtt Client when TLS is enabled."""
    if not MQTT_TLS_ENABLED:
        return {}
    ctx = ssl.create_default_context(cafile=MQTT_TLS_CA_CERTS)
    if MQTT_TLS_CERTFILE and MQTT_TLS_KEYFILE:
        ctx.load_cert_chain(certfile=MQTT_TLS_CERTFILE, keyfile=MQTT_TLS_KEYFILE)
    return {"tls_context": ctx}


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
        self._tls_params = _build_tls_params()
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
                **self._tls_params,
            )
            logger.info("Connected to MQTT broker: %s:%s (TLS=%s)", self.broker, self.port, bool(self._tls_params))
            return True
        except Exception as e:
            logger.error("Failed to connect to MQTT: %s", e)
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
                    **self._tls_params,
                ) as client:
                    await client.subscribe(topic)
                    logger.info("Subscribed to MQTT topic: %s (TLS=%s)", topic, bool(self._tls_params))

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
                            logger.error("Error processing MQTT message: %s", e)

            except MqttError as e:
                logger.warning("MQTT connection lost: %s", e)
                if self._running:
                    logger.info("Reconnecting in %ss...", self._reconnect_interval)
                    await asyncio.sleep(self._reconnect_interval)

            except Exception as e:
                logger.error("MQTT error: %s", e)
                if self._running:
                    await asyncio.sleep(self._reconnect_interval)

    async def publish(self, topic: str, payload: dict, qos: int = 1, retain: bool = False):
        """Publish message to MQTT topic"""
        try:
            async with Client(
                hostname=self.broker,
                port=self.port,
                username=self.username if self.username else None,
                password=self.password if self.password else None,
                **self._tls_params,
            ) as client:
                message = json.dumps(payload)
                await client.publish(topic, message.encode(), qos=qos, retain=retain)
                logger.debug("Published to MQTT topic: %s", topic)
        except Exception as e:
            logger.error("Failed to publish to MQTT: %s", e)
            raise

    def stop(self):
        """Stop the client"""
        self._running = False
        logger.info("MQTT client stopping")


class MockMqttClient(MqttClient):
    """
    Mock MQTT client for testing without real broker
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._messages: list[MqttMessage] = []

    async def connect(self) -> bool:
        logger.info("Mock MQTT client connected")
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

    async def publish(self, topic: str, payload: dict, qos: int = 1, retain: bool = False):
        logger.debug("Mock publish to %s: %s", topic, payload)
