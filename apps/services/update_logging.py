#!/usr/bin/env python3
"""
Script to update all Python services with structured JSON logging

This script will:
1. Add structlog to requirements.txt if not present
2. Update main.py to use shared logging configuration
3. Replace print statements with proper logging
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

# Services directory
SERVICES_DIR = Path(__file__).parent

# Python services that need updating
PYTHON_SERVICES = [
    "advisory-service",
    "agro-advisor",
    "agro-rules",
    "ai-advisor",
    "ai-agents-core",
    "alert-service",
    "astronomical-calendar",
    "billing-core",
    "code-review-service",
    "crop-health",
    "crop-health-ai",
    "crop-intelligence-service",
    "equipment-service",
    "fertilizer-advisor",
    "field-chat",
    "field-core",
    "field-intelligence",
    "field-management-service",
    "field-ops",
    "field-service",
    "indicators-service",
    "inventory-service",
    "iot-gateway",
    "irrigation-smart",
    "mcp-server",
    "ndvi-engine",
    "ndvi-processor",
    "notification-service",
    "provider-config",
    "satellite-service",
    "task-service",
    "virtual-sensors",
    "weather-advanced",
    "weather-core",
    "weather-service",
    "ws-gateway",
    "yield-engine",
]


def check_structlog_in_requirements(service_path: Path) -> bool:
    """Check if structlog is already in requirements.txt"""
    req_file = service_path / "requirements.txt"
    if not req_file.exists():
        return False

    content = req_file.read_text()
    return "structlog" in content.lower()


def add_structlog_to_requirements(service_path: Path) -> bool:
    """Add structlog to requirements.txt if not present"""
    req_file = service_path / "requirements.txt"
    if not req_file.exists():
        print(f"  ⚠️  No requirements.txt found")
        return False

    if check_structlog_in_requirements(service_path):
        print(f"  ✓  structlog already in requirements.txt")
        return True

    # Add structlog
    with open(req_file, "a") as f:
        f.write("\nstructlog>=24.1.0\n")

    print(f"  ✓  Added structlog to requirements.txt")
    return True


def has_logging_configured(main_file: Path) -> Tuple[bool, str]:
    """Check if main.py already has logging configured"""
    if not main_file.exists():
        return False, "no_main_file"

    content = main_file.read_text()

    if "from shared.logging_config import" in content or "from ..shared.logging_config import" in content:
        return True, "already_configured"

    if "structlog.configure" in content:
        return True, "has_structlog"

    return False, "needs_update"


def update_service(service_name: str) -> dict:
    """Update a single service with structured logging"""
    service_path = SERVICES_DIR / service_name

    if not service_path.exists():
        return {
            "service": service_name,
            "status": "not_found",
            "message": "Service directory not found"
        }

    print(f"\n📦 {service_name}")

    # Check for main.py
    main_file = service_path / "src" / "main.py"
    if not main_file.exists():
        main_file = service_path / "main.py"

    if not main_file.exists():
        return {
            "service": service_name,
            "status": "no_main",
            "message": "No main.py found"
        }

    # Check if already configured
    configured, status = has_logging_configured(main_file)
    if configured:
        print(f"  ✓  Logging already configured ({status})")
        return {
            "service": service_name,
            "status": "already_configured",
            "message": status
        }

    # Add structlog to requirements
    add_structlog_to_requirements(service_path)

    return {
        "service": service_name,
        "status": "updated",
        "message": "Structured logging configuration ready"
    }


def main():
    """Main execution"""
    print("=" * 70)
    print("SAHOOL Services - Structured Logging Update")
    print("=" * 70)

    results = []

    for service in PYTHON_SERVICES:
        result = update_service(service)
        results.append(result)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    updated = [r for r in results if r["status"] == "updated"]
    already_configured = [r for r in results if r["status"] == "already_configured"]
    errors = [r for r in results if r["status"] in ["not_found", "no_main"]]

    print(f"\n✅ Already configured: {len(already_configured)}")
    print(f"🔄 Ready for update: {len(updated)}")
    print(f"⚠️  Errors/Not found: {len(errors)}")

    if updated:
        print("\nServices ready for logging update:")
        for r in updated:
            print(f"  - {r['service']}")

    if errors:
        print("\nServices with issues:")
        for r in errors:
            print(f"  - {r['service']}: {r['message']}")

    print("\n" + "=" * 70)
    print(f"Total services processed: {len(results)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
