"""
SAHOOL DLQ Monitoring and Alerting
===================================
مراقبة وتنبيهات قائمة انتظار الرسائل الفاشلة

Background task for monitoring DLQ accumulation and triggering alerts.

Features:
- Periodic DLQ size checking
- Threshold-based alerting
- Alert history tracking
- Integration with notification service
- Prometheus metrics export (future)

Usage:
    # Start monitoring
    monitor = DLQMonitor()
    await monitor.start()

    # Or run as background task in FastAPI
    @app.on_event("startup")
    async def startup():
        app.state.dlq_monitor = DLQMonitor()
        await app.state.dlq_monitor.start()

    @app.on_event("shutdown")
    async def shutdown():
        await app.state.dlq_monitor.stop()
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from .dlq_config import DLQConfig

logger = logging.getLogger(__name__)

# NATS client - lazy import
_nats_available = False

try:
    import nats
    from nats.js import JetStreamContext

    _nats_available = True
except ImportError:
    logger.warning("NATS not available for DLQ monitoring")


# ─────────────────────────────────────────────────────────────────────────────
# Alert Models
# ─────────────────────────────────────────────────────────────────────────────


class DLQAlert(BaseModel):
    """DLQ alert notification."""

    alert_id: str
    timestamp: datetime
    severity: str  # warning, critical
    message: str
    message_count: int
    threshold: int
    stream_name: str

    # Additional context
    messages_by_subject: Dict[str, int] = Field(default_factory=dict)
    messages_by_error: Dict[str, int] = Field(default_factory=dict)
    oldest_message_age_hours: Optional[float] = None


class DLQMonitorStats(BaseModel):
    """DLQ monitoring statistics."""

    monitor_running: bool
    last_check_time: Optional[datetime] = None
    total_checks: int = 0
    alerts_triggered: int = 0
    current_dlq_size: int = 0
    current_dlq_bytes: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# DLQ Monitor
# ─────────────────────────────────────────────────────────────────────────────


class DLQMonitor:
    """
    Background monitor for DLQ accumulation.
    مراقب قائمة انتظار الرسائل الفاشلة
    """

    def __init__(
        self,
        config: Optional[DLQConfig] = None,
        alert_callback: Optional[Callable[[DLQAlert], None]] = None,
    ):
        """
        Initialize DLQ monitor.

        Args:
            config: DLQ configuration
            alert_callback: Function to call when alert is triggered
        """
        self.config = config or DLQConfig()
        self.alert_callback = alert_callback

        self._nc = None
        self._js: Optional[JetStreamContext] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None

        # Statistics
        self._total_checks = 0
        self._alerts_triggered = 0
        self._last_check_time: Optional[datetime] = None
        self._last_alert_time: Optional[datetime] = None
        self._alert_cooldown = timedelta(minutes=15)  # Don't spam alerts

    async def connect(self):
        """Connect to NATS."""
        if not _nats_available:
            raise RuntimeError("NATS not available")

        if self._nc:
            return

        try:
            self._nc = await nats.connect()
            self._js = self._nc.jetstream()
            logger.info("✅ DLQ Monitor connected to NATS")

        except Exception as e:
            logger.error(f"❌ Failed to connect DLQ Monitor: {e}")
            raise

    async def close(self):
        """Close NATS connection."""
        if self._nc:
            await self._nc.close()
            self._nc = None
            self._js = None

    async def start(self):
        """Start monitoring DLQ."""
        if self._running:
            logger.warning("DLQ Monitor already running")
            return

        if not self.config.alert_enabled:
            logger.info("DLQ alerting disabled")
            return

        await self.connect()

        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())

        logger.info(
            f"🚀 DLQ Monitor started "
            f"(threshold: {self.config.alert_threshold}, "
            f"interval: {self.config.alert_check_interval_seconds}s)"
        )

    async def stop(self):
        """Stop monitoring."""
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        await self.close()

        logger.info("🛑 DLQ Monitor stopped")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_dlq_size()
                await asyncio.sleep(self.config.alert_check_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DLQ monitor loop: {e}")
                await asyncio.sleep(60)  # Back off on errors

    async def _check_dlq_size(self):
        """Check DLQ size and trigger alerts if needed."""
        try:
            if not self._js:
                return

            # Get stream info
            stream_info = await self._js.stream_info(self.config.dlq_stream_name)

            message_count = stream_info.state.messages
            byte_count = stream_info.state.bytes

            self._total_checks += 1
            self._last_check_time = datetime.utcnow()

            logger.debug(f"DLQ check: {message_count} messages, {byte_count:,} bytes")

            # Check threshold
            if message_count >= self.config.alert_threshold:
                await self._trigger_alert(stream_info, message_count)

        except Exception as e:
            logger.error(f"Failed to check DLQ size: {e}")

    async def _trigger_alert(self, stream_info, message_count: int):
        """Trigger DLQ alert."""
        # Check cooldown
        if self._last_alert_time:
            time_since_last = datetime.utcnow() - self._last_alert_time
            if time_since_last < self._alert_cooldown:
                logger.debug(
                    f"Alert cooldown active (last: {time_since_last.seconds}s ago)"
                )
                return

        # Calculate severity
        severity = "warning"
        if message_count >= self.config.alert_threshold * 2:
            severity = "critical"

        # Calculate oldest message age
        oldest_age_hours = None
        if stream_info.state.first_ts:
            age = datetime.utcnow() - stream_info.state.first_ts
            oldest_age_hours = age.total_seconds() / 3600

        # Create alert
        alert = DLQAlert(
            alert_id=f"dlq-{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            severity=severity,
            message=f"DLQ threshold exceeded: {message_count} messages (threshold: {self.config.alert_threshold})",
            message_count=message_count,
            threshold=self.config.alert_threshold,
            stream_name=self.config.dlq_stream_name,
            oldest_message_age_hours=oldest_age_hours,
        )

        self._alerts_triggered += 1
        self._last_alert_time = datetime.utcnow()

        logger.warning(
            f"⚠️  DLQ ALERT: {alert.message} "
            f"(severity: {severity}, oldest: {oldest_age_hours:.1f}h)"
        )

        # Call alert callback
        if self.alert_callback:
            try:
                if asyncio.iscoroutinefunction(self.alert_callback):
                    await self.alert_callback(alert)
                else:
                    self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def get_stats(self) -> DLQMonitorStats:
        """Get monitoring statistics."""
        return DLQMonitorStats(
            monitor_running=self._running,
            last_check_time=self._last_check_time,
            total_checks=self._total_checks,
            alerts_triggered=self._alerts_triggered,
            current_dlq_size=0,  # Would need to query
            current_dlq_bytes=0,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Alert Integrations
# ─────────────────────────────────────────────────────────────────────────────


async def send_dlq_alert_to_slack(alert: DLQAlert, webhook_url: str):
    """
    Send DLQ alert to Slack.

    Args:
        alert: DLQ alert
        webhook_url: Slack webhook URL
    """
    import aiohttp

    color = "#ff9900" if alert.severity == "warning" else "#ff0000"

    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"🚨 DLQ Alert: {alert.severity.upper()}",
                "text": alert.message,
                "fields": [
                    {
                        "title": "Message Count",
                        "value": str(alert.message_count),
                        "short": True,
                    },
                    {
                        "title": "Threshold",
                        "value": str(alert.threshold),
                        "short": True,
                    },
                    {
                        "title": "Stream",
                        "value": alert.stream_name,
                        "short": True,
                    },
                    {
                        "title": "Oldest Message",
                        "value": (
                            f"{alert.oldest_message_age_hours:.1f} hours"
                            if alert.oldest_message_age_hours
                            else "N/A"
                        ),
                        "short": True,
                    },
                ],
                "footer": "SAHOOL DLQ Monitor",
                "ts": int(alert.timestamp.timestamp()),
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload) as response:
            if response.status != 200:
                logger.error(f"Failed to send Slack alert: {response.status}")


async def send_dlq_alert_email(alert: DLQAlert, to_email: str, from_email: str):
    """
    Send DLQ alert via email.

    Args:
        alert: DLQ alert
        to_email: Recipient email
        from_email: Sender email
    """
    # Implementation would use your email service
    logger.info(f"Would send email alert to {to_email}")


async def log_dlq_alert(alert: DLQAlert):
    """
    Log DLQ alert (default callback).

    Args:
        alert: DLQ alert
    """
    logger.warning(
        f"DLQ ALERT [{alert.severity.upper()}]: {alert.message} "
        f"(messages: {alert.message_count}, threshold: {alert.threshold})"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────────────────────


async def example_usage():
    """Example of using DLQ monitor."""

    # Create monitor with Slack alerts
    async def alert_handler(alert: DLQAlert):
        # Send to multiple channels
        await log_dlq_alert(alert)

        # Uncomment to enable Slack
        # await send_dlq_alert_to_slack(
        #     alert,
        #     webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
        # )

    monitor = DLQMonitor(alert_callback=alert_handler)

    # Start monitoring
    await monitor.start()

    # Monitor runs in background
    # Keep application running
    try:
        while True:
            await asyncio.sleep(60)
            stats = monitor.get_stats()
            logger.info(f"Monitor stats: {stats}")

    except KeyboardInterrupt:
        logger.info("Stopping monitor...")
        await monitor.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
