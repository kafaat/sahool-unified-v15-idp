#!/usr/bin/env python3
"""
Script to add shared middleware to SAHOOL services
Adds RequestLoggingMiddleware, TenantContextMiddleware, and ObservabilityMiddleware
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Base directory
BASE_DIR = Path("/home/user/sahool-unified-v15-idp")
SERVICES_DIR = BASE_DIR / "apps" / "services"


def find_python_services() -> List[Path]:
    """Find all FastAPI Python services"""
    services = []
    for main_py in SERVICES_DIR.glob("*/src/main.py"):
        if "archive" not in str(main_py) and "node_modules" not in str(main_py):
            services.append(main_py)
    return services


def find_typescript_services() -> List[Path]:
    """Find all NestJS TypeScript services"""
    services = []
    for main_ts in SERVICES_DIR.glob("*/src/main.ts"):
        if "archive" not in str(main_ts) and "node_modules" not in str(main_ts):
            services.append(main_ts)
    return services


def check_has_shared_middleware(file_path: Path) -> Tuple[bool, str]:
    """Check if service already has shared middleware"""
    content = file_path.read_text()

    if file_path.suffix == ".py":
        # Check for Python middleware
        if "RequestLoggingMiddleware" in content and "from shared.middleware import" in content:
            return True, "RequestLoggingMiddleware"
        if "from shared.logging_config import" in content and "RequestLoggingMiddleware" in content:
            return True, "shared.logging_config"
        return False, ""
    else:
        # Check for TypeScript middleware
        if "RequestLoggingInterceptor" in content and "shared/middleware" in content:
            return True, "RequestLoggingInterceptor"
        return False, ""


def update_python_service(file_path: Path, dry_run: bool = True) -> bool:
    """Update a Python FastAPI service with shared middleware"""
    content = file_path.read_text()

    # Skip if already has shared middleware
    has_middleware, middleware_type = check_has_shared_middleware(file_path)
    if has_middleware:
        print(f"  ✓ Already has {middleware_type}")
        return False

    # Check if it's a FastAPI service
    if "FastAPI" not in content:
        print(f"  ⚠ Not a FastAPI service, skipping")
        return False

    service_name = file_path.parent.parent.name

    # Add imports at the top after existing imports
    import_pattern = r"(from fastapi import.*?\n)"
    import_addition = f"""
# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.middleware import (
    RequestLoggingMiddleware,
    TenantContextMiddleware,
    setup_cors,
)
from shared.observability.middleware import ObservabilityMiddleware

"""

    # Only add if not already present
    if "from shared.middleware import" not in content:
        content = re.sub(import_pattern, r"\1" + import_addition, content, count=1)

    # Add middleware setup after app creation
    app_pattern = r"(app = FastAPI\([^)]*\))"
    middleware_addition = f"""

# ============== Shared Middleware Setup ==============
# Middleware order: Last added = First executed

# 1. CORS - Secure cross-origin configuration
setup_cors(app)

# 2. Observability - Tracing, metrics, and monitoring
app.add_middleware(
    ObservabilityMiddleware,
    service_name="{service_name}",
    metrics_collector=None,
)

# 3. Request Logging - Correlation IDs and structured logging
app.add_middleware(
    RequestLoggingMiddleware,
    service_name="{service_name}",
    log_request_body=os.getenv("LOG_REQUEST_BODY", "false").lower() == "true",
    log_response_body=False,
)

# 4. Tenant Context - Multi-tenancy isolation (optional, uncomment if needed)
# app.add_middleware(
#     TenantContextMiddleware,
#     require_tenant=True,
#     exempt_paths=["/health", "/healthz", "/readyz", "/docs", "/redoc", "/openapi.json"],
# )
"""

    # Only add if no middleware section exists
    if "# Shared Middleware Setup" not in content and "RequestLoggingMiddleware" not in content:
        content = re.sub(app_pattern, r"\1" + middleware_addition, content, count=1)

    if not dry_run:
        file_path.write_text(content)
        print(f"  ✓ Updated with shared middleware")
        return True
    else:
        print(f"  ○ Would add shared middleware (dry run)")
        return True


def update_typescript_service(file_path: Path, dry_run: bool = True) -> bool:
    """Update a TypeScript NestJS service with shared middleware"""
    content = file_path.read_text()

    # Skip if already has shared middleware
    has_middleware, middleware_type = check_has_shared_middleware(file_path)
    if has_middleware:
        print(f"  ✓ Already has {middleware_type}")
        return False

    service_name = file_path.parent.parent.name

    # Add import
    if "RequestLoggingInterceptor" not in content:
        import_pattern = r"(import.*?from.*?errors.*?;)"
        import_addition = "\nimport { RequestLoggingInterceptor } from '../../shared/middleware/request-logging';"
        content = re.sub(import_pattern, r"\1" + import_addition, content, count=1)

    # Add interceptor
    if "useGlobalInterceptors" not in content:
        # Find the bootstrap function and add after useGlobalPipes
        pipes_pattern = r"(app\.useGlobalPipes\([^)]+\)\s*\);)"
        interceptor_addition = f"""

  // ============== Middleware Setup ==============
  // Global request logging interceptor with correlation IDs
  app.useGlobalInterceptors(new RequestLoggingInterceptor('{service_name}'));"""

        content = re.sub(pipes_pattern, r"\1" + interceptor_addition, content, count=1)

    if not dry_run:
        file_path.write_text(content)
        print(f"  ✓ Updated with shared middleware")
        return True
    else:
        print(f"  ○ Would add shared middleware (dry run)")
        return True


def main():
    """Main function"""
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    else:
        print("🚀 UPDATING SERVICES - Files will be modified\n")

    # Update Python services
    print("=" * 60)
    print("Python FastAPI Services")
    print("=" * 60)
    python_services = find_python_services()
    python_updated = 0

    for service_path in sorted(python_services):
        service_name = service_path.parent.parent.name
        print(f"\n📦 {service_name}")
        if update_python_service(service_path, dry_run):
            python_updated += 1

    # Update TypeScript services
    print("\n" + "=" * 60)
    print("TypeScript NestJS Services")
    print("=" * 60)
    typescript_services = find_typescript_services()
    typescript_updated = 0

    for service_path in sorted(typescript_services):
        service_name = service_path.parent.parent.name
        print(f"\n📦 {service_name}")
        if update_typescript_service(service_path, dry_run):
            typescript_updated += 1

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Python services checked: {len(python_services)}")
    print(f"Python services updated: {python_updated}")
    print(f"TypeScript services checked: {len(typescript_services)}")
    print(f"TypeScript services updated: {typescript_updated}")
    print(f"Total updated: {python_updated + typescript_updated}")

    if dry_run:
        print("\n💡 Run without --dry-run to apply changes")
    else:
        print("\n✅ All services updated successfully!")


if __name__ == "__main__":
    main()
