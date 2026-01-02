#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - Main Simulation Runner
المشغل الرئيسي لمحاكيات منصة سهول
═══════════════════════════════════════════════════════════════════════════════════════

This script runs all simulators in parallel or individually:
- Comprehensive Services Simulator (جميع الخدمات)
- AI Agents Simulator (وكلاء الذكاء الاصطناعي)
- IoT Devices Simulator (أجهزة إنترنت الأشياء)

Usage:
    # Run all simulators
    python run_simulation.py --all --duration 300 --gateway http://localhost:8081

    # Run specific simulators
    python run_simulation.py --services --agents --duration 300

    # Run with custom configuration
    python run_simulation.py --all --users 50 --iot-devices 100 --duration 600

═══════════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import argparse
import sys
import os
import json
from datetime import datetime, timezone
import logging

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from comprehensive_simulator import ComprehensiveSimulator
from agents_simulator import AgentsSimulator
from iot_simulator import IoTSimulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sahool-simulation-runner")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

class SimulationRunner:
    """Main runner that orchestrates all simulators."""

    def __init__(
        self,
        gateway_url: str,
        run_services: bool = True,
        run_agents: bool = True,
        run_iot: bool = True,
        num_users: int = 10,
        num_iot_devices: int = 50,
        duration: int = 60,
    ):
        self.gateway_url = gateway_url
        self.run_services = run_services
        self.run_agents = run_agents
        self.run_iot = run_iot
        self.num_users = num_users
        self.num_iot_devices = num_iot_devices
        self.duration = duration
        self.results = {}

    async def run_services_simulator(self):
        """Run the comprehensive services simulator."""
        if not self.run_services:
            return

        logger.info("Starting Comprehensive Services Simulator...")
        simulator = ComprehensiveSimulator(
            gateway_url=self.gateway_url,
            num_users=self.num_users,
            duration_seconds=self.duration,
        )
        await simulator.run()
        self.results["services"] = {
            name: {
                "requests": stats.requests,
                "success": stats.success,
                "failed": stats.failed,
                "success_rate": stats.success_rate,
                "avg_latency_ms": stats.avg_latency,
            }
            for name, stats in simulator.stats.services.items()
        }

    async def run_agents_simulator(self):
        """Run the AI agents simulator."""
        if not self.run_agents:
            return

        logger.info("Starting AI Agents Simulator...")
        simulator = AgentsSimulator(
            gateway_url=self.gateway_url,
            num_users=max(1, self.num_users // 5),  # Fewer users for AI
            duration_seconds=self.duration,
        )
        await simulator.run()
        self.results["agents"] = {
            name: {
                "requests": stats.requests,
                "success": stats.success,
                "failed": stats.failed,
                "success_rate": stats.success_rate,
                "avg_latency_ms": stats.avg_latency,
            }
            for name, stats in simulator.stats.agents.items()
        }

    async def run_iot_simulator(self):
        """Run the IoT devices simulator."""
        if not self.run_iot:
            return

        logger.info("Starting IoT Devices Simulator...")
        # IoT gateway is usually on a different port
        iot_url = self.gateway_url.replace(":8081", ":8106")
        simulator = IoTSimulator(
            gateway_url=iot_url,
            num_devices=self.num_iot_devices,
            duration_seconds=self.duration,
        )
        await simulator.run()
        self.results["iot"] = {
            "messages_sent": simulator.stats.messages_sent,
            "messages_success": simulator.stats.messages_success,
            "messages_failed": simulator.stats.messages_failed,
            "success_rate": simulator.stats.success_rate,
            "avg_latency_ms": simulator.stats.avg_latency_ms,
        }

    async def run(self):
        """Run all selected simulators."""
        self.print_banner()

        # Run simulators in parallel
        tasks = []
        if self.run_services:
            tasks.append(asyncio.create_task(self.run_services_simulator()))
        if self.run_agents:
            tasks.append(asyncio.create_task(self.run_agents_simulator()))
        if self.run_iot:
            tasks.append(asyncio.create_task(self.run_iot_simulator()))

        if not tasks:
            logger.error("No simulators selected!")
            return

        await asyncio.gather(*tasks, return_exceptions=True)

        self.print_summary()
        self.save_results()

    def print_banner(self):
        """Print startup banner."""
        logger.info("")
        logger.info("═" * 80)
        logger.info("  ███████╗ █████╗ ██╗  ██╗ ██████╗  ██████╗ ██╗     ")
        logger.info("  ██╔════╝██╔══██╗██║  ██║██╔═══██╗██╔═══██╗██║     ")
        logger.info("  ███████╗███████║███████║██║   ██║██║   ██║██║     ")
        logger.info("  ╚════██║██╔══██║██╔══██║██║   ██║██║   ██║██║     ")
        logger.info("  ███████║██║  ██║██║  ██║╚██████╔╝╚██████╔╝███████╗")
        logger.info("  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝")
        logger.info("")
        logger.info("  Integrated Digital Platform - Comprehensive Simulation")
        logger.info("  منصة سهول الرقمية المتكاملة - المحاكاة الشاملة")
        logger.info("═" * 80)
        logger.info("")
        logger.info("  Configuration:")
        logger.info(f"    Gateway URL:    {self.gateway_url}")
        logger.info(f"    Duration:       {self.duration}s")
        logger.info(f"    Virtual Users:  {self.num_users}")
        logger.info(f"    IoT Devices:    {self.num_iot_devices}")
        logger.info("")
        logger.info("  Simulators:")
        logger.info(f"    Services:  {'✓ Enabled' if self.run_services else '✗ Disabled'}")
        logger.info(f"    AI Agents: {'✓ Enabled' if self.run_agents else '✗ Disabled'}")
        logger.info(f"    IoT:       {'✓ Enabled' if self.run_iot else '✗ Disabled'}")
        logger.info("")
        logger.info("═" * 80)
        logger.info("")

    def print_summary(self):
        """Print final summary."""
        logger.info("")
        logger.info("═" * 80)
        logger.info("  SIMULATION COMPLETE - اكتملت المحاكاة")
        logger.info("═" * 80)

        total_requests = 0
        total_success = 0

        if "services" in self.results:
            svc_requests = sum(s["requests"] for s in self.results["services"].values())
            svc_success = sum(s["success"] for s in self.results["services"].values())
            total_requests += svc_requests
            total_success += svc_success
            logger.info(f"  Services:  {svc_success}/{svc_requests} requests")

        if "agents" in self.results:
            agent_requests = sum(s["requests"] for s in self.results["agents"].values())
            agent_success = sum(s["success"] for s in self.results["agents"].values())
            total_requests += agent_requests
            total_success += agent_success
            logger.info(f"  AI Agents: {agent_success}/{agent_requests} requests")

        if "iot" in self.results:
            iot = self.results["iot"]
            total_requests += iot["messages_sent"]
            total_success += iot["messages_success"]
            logger.info(f"  IoT:       {iot['messages_success']}/{iot['messages_sent']} messages")

        overall_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
        logger.info("")
        logger.info(f"  Overall Success Rate: {overall_rate:.1f}%")
        logger.info("═" * 80)

    def save_results(self):
        """Save combined results to JSON."""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "configuration": {
                "gateway_url": self.gateway_url,
                "duration": self.duration,
                "num_users": self.num_users,
                "num_iot_devices": self.num_iot_devices,
                "simulators": {
                    "services": self.run_services,
                    "agents": self.run_agents,
                    "iot": self.run_iot,
                }
            },
            "results": self.results,
        }

        filename = f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"  Results saved to: {filename}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL IDP - Comprehensive Simulation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all simulators for 5 minutes
  python run_simulation.py --all --duration 300

  # Run only services and agents
  python run_simulation.py --services --agents --duration 120

  # Run with 100 users and 200 IoT devices
  python run_simulation.py --all --users 100 --iot-devices 200 --duration 600

  # Run against production
  python run_simulation.py --all --gateway https://api.sahool.app
        """
    )

    # Simulator selection
    parser.add_argument("--all", "-a", action="store_true",
                       help="Run all simulators")
    parser.add_argument("--services", "-s", action="store_true",
                       help="Run services simulator")
    parser.add_argument("--agents", action="store_true",
                       help="Run AI agents simulator")
    parser.add_argument("--iot", "-i", action="store_true",
                       help="Run IoT simulator")

    # Configuration
    parser.add_argument("--gateway", "-g", default="http://localhost:8081",
                       help="Kong Gateway URL (default: http://localhost:8081)")
    parser.add_argument("--users", "-u", type=int, default=10,
                       help="Number of virtual users (default: 10)")
    parser.add_argument("--iot-devices", type=int, default=50,
                       help="Number of IoT devices (default: 50)")
    parser.add_argument("--duration", "-d", type=int, default=60,
                       help="Duration in seconds (default: 60)")

    args = parser.parse_args()

    # Determine which simulators to run
    if args.all:
        run_services = run_agents = run_iot = True
    else:
        run_services = args.services
        run_agents = args.agents
        run_iot = args.iot

        # If no specific simulator selected, run all
        if not (run_services or run_agents or run_iot):
            run_services = run_agents = run_iot = True

    runner = SimulationRunner(
        gateway_url=args.gateway,
        run_services=run_services,
        run_agents=run_agents,
        run_iot=run_iot,
        num_users=args.users,
        num_iot_devices=args.iot_devices,
        duration=args.duration,
    )

    try:
        asyncio.run(runner.run())
    except KeyboardInterrupt:
        logger.info("\nSimulation stopped by user")

if __name__ == "__main__":
    main()
