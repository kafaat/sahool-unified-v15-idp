#!/usr/bin/env python3
"""
SAHOOL Kong Continuous Monitoring Script
=========================================

Continuous monitoring of Kong services with Prometheus metrics export.
مراقبة مستمرة لخدمات Kong مع تصدير مقاييس Prometheus.

Features:
- Polls all services every 30 seconds (configurable)
- Logs to file with timestamps
- Sends alerts for failures (webhook, email, Slack)
- Exports Prometheus metrics
- Tracks service uptime and response times

Usage:
    python monitor-kong.py [options]

Options:
    --interval SECONDS    Polling interval (default: 30)
    --log-file PATH       Log file path (default: kong-monitor.log)
    --metrics-port PORT   Prometheus metrics port (default: 9101)
    --alert-webhook URL   Webhook URL for alerts
    --alert-email EMAIL   Email for alerts (requires SMTP config)
    --critical-only       Monitor only critical services

Author: SAHOOL Platform Team
Version: 16.0.0
Last Updated: 2026-02-07
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from enum import Enum
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Callable

try:
    import aiohttp

    ASYNC_MODE = True
except ImportError:
    ASYNC_MODE = False
    import requests

# =============================================================================
# Configuration | التكوين
# =============================================================================

DEFAULT_INTERVAL = 30
DEFAULT_METRICS_PORT = 9101
DEFAULT_LOG_FILE = "kong-monitor.log"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


@dataclass
class ServiceMetrics:
    """Metrics for a single service."""

    name: str
    name_ar: str
    category: str
    critical: bool
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: str = ""
    response_time_ms: float = 0.0
    consecutive_failures: int = 0
    total_checks: int = 0
    successful_checks: int = 0
    uptime_percentage: float = 100.0
    last_error: str = ""

    @property
    def uptime(self) -> float:
        if self.total_checks == 0:
            return 100.0
        return (self.successful_checks / self.total_checks) * 100


@dataclass
class AlertConfig:
    """Alert configuration."""

    webhook_url: str | None = None
    email: str | None = None
    slack_webhook: str | None = None
    failure_threshold: int = 3  # Consecutive failures before alert


class PrometheusMetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint."""

    metrics_data: dict = {}

    def log_message(self, format: str, *args) -> None:
        """Suppress default HTTP logging."""
        pass

    def do_GET(self):
        """Handle GET requests for /metrics endpoint."""
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(self._generate_metrics().encode())
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"kong-monitor"}')
        else:
            self.send_response(404)
            self.end_headers()

    def _generate_metrics(self) -> str:
        """Generate Prometheus-format metrics."""
        lines = []

        # Metadata
        lines.append("# HELP sahool_kong_service_up Service health status (1=up, 0=down)")
        lines.append("# TYPE sahool_kong_service_up gauge")

        lines.append("# HELP sahool_kong_service_response_time_ms Service response time in milliseconds")
        lines.append("# TYPE sahool_kong_service_response_time_ms gauge")

        lines.append("# HELP sahool_kong_service_uptime_percent Service uptime percentage")
        lines.append("# TYPE sahool_kong_service_uptime_percent gauge")

        lines.append("# HELP sahool_kong_service_consecutive_failures Consecutive failure count")
        lines.append("# TYPE sahool_kong_service_consecutive_failures gauge")

        lines.append("# HELP sahool_kong_total_services Total number of monitored services")
        lines.append("# TYPE sahool_kong_total_services gauge")

        lines.append("# HELP sahool_kong_healthy_services Number of healthy services")
        lines.append("# TYPE sahool_kong_healthy_services gauge")

        metrics = PrometheusMetricsHandler.metrics_data

        # Summary metrics
        total = metrics.get("total_services", 0)
        healthy = metrics.get("healthy_services", 0)
        lines.append(f"sahool_kong_total_services {total}")
        lines.append(f"sahool_kong_healthy_services {healthy}")

        # Per-service metrics
        for service_name, data in metrics.get("services", {}).items():
            labels = f'service="{service_name}",category="{data.get("category", "")}",critical="{data.get("critical", False)}"'

            status_value = 1 if data.get("status") == "healthy" else 0
            lines.append(f"sahool_kong_service_up{{{labels}}} {status_value}")

            response_time = data.get("response_time_ms", 0)
            lines.append(f"sahool_kong_service_response_time_ms{{{labels}}} {response_time:.2f}")

            uptime = data.get("uptime_percentage", 100)
            lines.append(f"sahool_kong_service_uptime_percent{{{labels}}} {uptime:.2f}")

            failures = data.get("consecutive_failures", 0)
            lines.append(f"sahool_kong_service_consecutive_failures{{{labels}}} {failures}")

        return "\n".join(lines) + "\n"


class KongMonitor:
    """
    Continuous Kong service monitor.
    مراقب خدمات Kong المستمر.
    """

    def __init__(
        self,
        interval: int = DEFAULT_INTERVAL,
        log_file: str = DEFAULT_LOG_FILE,
        metrics_port: int = DEFAULT_METRICS_PORT,
        alert_config: AlertConfig | None = None,
        critical_only: bool = False,
        kong_url: str = "http://localhost:8000",
    ):
        self.interval = interval
        self.log_file = Path(log_file)
        self.metrics_port = metrics_port
        self.alert_config = alert_config or AlertConfig()
        self.critical_only = critical_only
        self.kong_url = kong_url.rstrip("/")

        self.script_dir = Path(__file__).parent
        self.services_json_path = self.script_dir / "kong-services.json"

        self.services: list[dict] = []
        self.service_metrics: dict[str, ServiceMetrics] = {}
        self.running = False
        self.metrics_server: HTTPServer | None = None

        # Setup file logging
        self._setup_file_logging()

    def _setup_file_logging(self):
        """Setup file-based logging."""
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(file_handler)

    def load_services(self) -> bool:
        """Load services from JSON registry."""
        if not self.services_json_path.exists():
            logger.error(f"Service registry not found: {self.services_json_path}")
            return False

        with open(self.services_json_path) as f:
            data = json.load(f)
            self.services = data.get("services", [])

        # Filter critical only if requested
        if self.critical_only:
            self.services = [s for s in self.services if s.get("critical", False)]

        # Initialize metrics for each service
        for svc in self.services:
            name = svc["name"]
            self.service_metrics[name] = ServiceMetrics(
                name=name,
                name_ar=svc.get("name_ar", name),
                category=svc.get("category", "unknown"),
                critical=svc.get("critical", False),
            )

        logger.info(f"Loaded {len(self.services)} services for monitoring")
        return True

    async def check_service(self, service: dict) -> tuple[ServiceStatus, float, str]:
        """
        Check single service health.
        فحص صحة خدمة واحدة.
        """
        host = service["host"]
        port = service["port"]
        health_endpoint = service.get("health_endpoint", "/healthz")
        expected_status = service.get("expected_status", 200)
        timeout_ms = service.get("timeout_ms", 5000)

        url = f"http://{host}:{port}{health_endpoint}"
        timeout_sec = timeout_ms / 1000

        start_time = time.time()

        try:
            if ASYNC_MODE:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout_sec)) as response:
                        duration = (time.time() - start_time) * 1000
                        if response.status == expected_status:
                            return ServiceStatus.HEALTHY, duration, ""
                        else:
                            return ServiceStatus.UNHEALTHY, duration, f"Status {response.status}"
            else:
                response = requests.get(url, timeout=timeout_sec)
                duration = (time.time() - start_time) * 1000
                if response.status_code == expected_status:
                    return ServiceStatus.HEALTHY, duration, ""
                else:
                    return ServiceStatus.UNHEALTHY, duration, f"Status {response.status_code}"

        except TimeoutError:
            duration = (time.time() - start_time) * 1000
            return ServiceStatus.UNREACHABLE, duration, "Timeout"
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ServiceStatus.UNREACHABLE, duration, str(e)

    async def check_all_services(self):
        """Check health of all services."""
        tasks = []
        for svc in self.services:
            tasks.append(self.check_service(svc))

        results = await asyncio.gather(*tasks)

        healthy_count = 0
        for svc, (status, response_time, error) in zip(self.services, results):
            name = svc["name"]
            metrics = self.service_metrics[name]

            # Update metrics
            metrics.total_checks += 1
            metrics.last_check = datetime.now(UTC).isoformat()
            metrics.response_time_ms = response_time
            metrics.status = status

            if status == ServiceStatus.HEALTHY:
                metrics.successful_checks += 1
                metrics.consecutive_failures = 0
                healthy_count += 1
            else:
                metrics.consecutive_failures += 1
                metrics.last_error = error

                # Check if we need to send alert
                if metrics.consecutive_failures >= self.alert_config.failure_threshold:
                    await self._send_alert(metrics)

            metrics.uptime_percentage = metrics.uptime

            # Log status
            status_icon = "OK" if status == ServiceStatus.HEALTHY else "FAIL"
            logger.info(
                f"[{status_icon}] {name}: {status.value} "
                f"({response_time:.1f}ms) - Uptime: {metrics.uptime_percentage:.1f}%"
            )

        # Update Prometheus metrics
        self._update_prometheus_metrics(healthy_count)

    def _update_prometheus_metrics(self, healthy_count: int):
        """Update Prometheus metrics data."""
        PrometheusMetricsHandler.metrics_data = {
            "total_services": len(self.services),
            "healthy_services": healthy_count,
            "services": {
                name: {
                    "status": m.status.value,
                    "category": m.category,
                    "critical": m.critical,
                    "response_time_ms": m.response_time_ms,
                    "uptime_percentage": m.uptime_percentage,
                    "consecutive_failures": m.consecutive_failures,
                }
                for name, m in self.service_metrics.items()
            },
        }

    async def _send_alert(self, metrics: ServiceMetrics):
        """Send alert for service failure."""
        alert_data = {
            "service": metrics.name,
            "service_ar": metrics.name_ar,
            "status": metrics.status.value,
            "consecutive_failures": metrics.consecutive_failures,
            "last_error": metrics.last_error,
            "category": metrics.category,
            "critical": metrics.critical,
            "timestamp": datetime.now(UTC).isoformat(),
            "platform": "SAHOOL",
            "message": f"Service {metrics.name} has failed {metrics.consecutive_failures} consecutive times",
            "message_ar": f"الخدمة {metrics.name_ar} فشلت {metrics.consecutive_failures} مرات متتالية",
        }

        logger.warning(f"ALERT: {alert_data['message']}")

        # Send webhook alert
        if self.alert_config.webhook_url:
            try:
                if ASYNC_MODE:
                    async with aiohttp.ClientSession() as session:
                        await session.post(
                            self.alert_config.webhook_url,
                            json=alert_data,
                            timeout=aiohttp.ClientTimeout(total=10),
                        )
                else:
                    requests.post(self.alert_config.webhook_url, json=alert_data, timeout=10)
                logger.info(f"Alert sent to webhook for {metrics.name}")
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {e}")

        # Send Slack alert
        if self.alert_config.slack_webhook:
            slack_payload = {
                "text": ":warning: *SAHOOL Alert* - Service Down",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [
                            {"title": "Service", "value": metrics.name, "short": True},
                            {"title": "Status", "value": metrics.status.value, "short": True},
                            {
                                "title": "Failures",
                                "value": str(metrics.consecutive_failures),
                                "short": True,
                            },
                            {"title": "Category", "value": metrics.category, "short": True},
                            {
                                "title": "Error",
                                "value": metrics.last_error[:100] if metrics.last_error else "N/A",
                            },
                        ],
                    }
                ],
            }
            try:
                if ASYNC_MODE:
                    async with aiohttp.ClientSession() as session:
                        await session.post(
                            self.alert_config.slack_webhook,
                            json=slack_payload,
                            timeout=aiohttp.ClientTimeout(total=10),
                        )
                else:
                    requests.post(self.alert_config.slack_webhook, json=slack_payload, timeout=10)
                logger.info(f"Slack alert sent for {metrics.name}")
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")

    def _start_metrics_server(self):
        """Start the Prometheus metrics HTTP server."""
        try:
            self.metrics_server = HTTPServer(("0.0.0.0", self.metrics_port), PrometheusMetricsHandler)
            logger.info(f"Prometheus metrics server started on port {self.metrics_port}")
            self.metrics_server.serve_forever()
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")

    def stop(self):
        """Stop the monitor gracefully."""
        logger.info("Stopping Kong monitor...")
        self.running = False
        if self.metrics_server:
            self.metrics_server.shutdown()

    async def run(self):
        """Main monitoring loop."""
        if not self.load_services():
            return

        self.running = True

        # Start metrics server in a separate thread
        metrics_thread = Thread(target=self._start_metrics_server, daemon=True)
        metrics_thread.start()

        logger.info(f"Starting monitoring loop (interval: {self.interval}s)")
        logger.info(f"Log file: {self.log_file.absolute()}")
        logger.info(f"Metrics endpoint: http://localhost:{self.metrics_port}/metrics")
        print()

        while self.running:
            try:
                logger.info("-" * 60)
                logger.info(f"Health check started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                await self.check_all_services()

                # Summary
                total = len(self.services)
                healthy = sum(1 for m in self.service_metrics.values() if m.status == ServiceStatus.HEALTHY)
                logger.info(f"Summary: {healthy}/{total} services healthy ({healthy * 100 // total}%)")

                # Wait for next interval
                await asyncio.sleep(self.interval)

            except asyncio.CancelledError:
                logger.info("Monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retry


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SAHOOL Kong Continuous Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python monitor-kong.py
  python monitor-kong.py --interval 60 --critical-only
  python monitor-kong.py --alert-webhook https://example.com/webhook
  python monitor-kong.py --metrics-port 9102 --log-file /var/log/kong-monitor.log

Environment Variables:
  KONG_GATEWAY_URL     Kong gateway URL (default: http://localhost:8000)
  ALERT_WEBHOOK_URL    Webhook URL for alerts
  SLACK_WEBHOOK_URL    Slack webhook URL for alerts
        """,
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE, help=f"Log file path (default: {DEFAULT_LOG_FILE})")
    parser.add_argument(
        "--metrics-port",
        type=int,
        default=DEFAULT_METRICS_PORT,
        help=f"Prometheus metrics port (default: {DEFAULT_METRICS_PORT})",
    )
    parser.add_argument(
        "--kong-url",
        default=os.environ.get("KONG_GATEWAY_URL", "http://localhost:8000"),
        help="Kong gateway URL",
    )
    parser.add_argument(
        "--alert-webhook",
        default=os.environ.get("ALERT_WEBHOOK_URL"),
        help="Webhook URL for alerts",
    )
    parser.add_argument(
        "--slack-webhook",
        default=os.environ.get("SLACK_WEBHOOK_URL"),
        help="Slack webhook URL for alerts",
    )
    parser.add_argument(
        "--failure-threshold",
        type=int,
        default=3,
        help="Consecutive failures before alert (default: 3)",
    )
    parser.add_argument("--critical-only", action="store_true", help="Monitor only critical services")

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    print()
    print("=" * 78)
    print("  SAHOOL Kong Continuous Monitor")
    print("  مراقب Kong المستمر لمنصة سهول")
    print("=" * 78)
    print()
    print(f"  Interval:          {args.interval} seconds")
    print(f"  Log File:          {args.log_file}")
    print(f"  Metrics Port:      {args.metrics_port}")
    print(f"  Kong URL:          {args.kong_url}")
    print(f"  Critical Only:     {args.critical_only}")
    print()
    print("  Press Ctrl+C to stop")
    print()
    print("=" * 78)
    print()

    alert_config = AlertConfig(
        webhook_url=args.alert_webhook,
        slack_webhook=args.slack_webhook,
        failure_threshold=args.failure_threshold,
    )

    monitor = KongMonitor(
        interval=args.interval,
        log_file=args.log_file,
        metrics_port=args.metrics_port,
        alert_config=alert_config,
        critical_only=args.critical_only,
        kong_url=args.kong_url,
    )

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\n")
        monitor.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the monitor
    asyncio.run(monitor.run())


if __name__ == "__main__":
    main()
