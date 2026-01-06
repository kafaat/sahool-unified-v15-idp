#!/usr/bin/env python3
"""
Batch update all Python services with structured JSON logging
"""

import re
from pathlib import Path

SERVICES_DIR = Path(__file__).parent

# Template for logging imports and setup
LOGGING_IMPORT_TEMPLATE = """
# Import shared logging configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared.logging_config import setup_logging, get_logger, RequestLoggingMiddleware

# Setup structured logging
setup_logging(service_name="{service_name}")
logger = get_logger(__name__)
"""

def update_python_service(service_path: Path, service_name: str) -> bool:
    """Update a Python service with structured logging"""
    main_file = service_path / "src" / "main.py"
    if not main_file.exists():
        main_file = service_path / "main.py"

    if not main_file.exists():
        print(f"  ⚠️  No main.py found")
        return False

    content = main_file.read_text()

    # Skip if already configured
    if "from shared.logging_config import" in content or "from ..shared.logging_config import" in content:
        print(f"  ✓  Already configured")
        return True

    if "setup_logging" in content:
        print(f"  ✓  Already has logging setup")
        return True

    # Check if service is deprecated or demo
    if "DEPRECATED" in content[:500] or service_name == "demo-data":
        print(f"  ⏭️  Skipped (deprecated/demo)")
        return False

    # Find the imports section
    # Look for FastAPI import
    fastapi_match = re.search(r'(from fastapi import .+)', content)
    if not fastapi_match:
        print(f"  ⚠️  No FastAPI import found")
        return False

    # Check if sys is already imported
    has_sys_import = re.search(r'^\s*import sys', content, re.MULTILINE)
    has_os_import = re.search(r'^\s*import os', content, re.MULTILINE)

    # Prepare logging setup code
    logging_code = f"""# Import shared logging configuration
{'# sys already imported above' if has_sys_import else 'import sys'}
{'# os already imported above' if has_os_import else 'import os'}
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared.logging_config import setup_logging, get_logger, RequestLoggingMiddleware

# Setup structured logging
setup_logging(service_name="{service_name}")
logger = get_logger(__name__)
"""

    # Find a good insertion point (after all imports)
    # Look for the last import statement before any class/function definitions
    import_pattern = r'((?:^(?:from|import)\s+.+$\s*)+)'
    matches = list(re.finditer(import_pattern, content, re.MULTILINE))

    if not matches:
        print(f"  ⚠️  Could not find import section")
        return False

    last_import = matches[-1]
    insertion_point = last_import.end()

    # Insert logging setup
    new_content = content[:insertion_point] + "\n" + logging_code + "\n" + content[insertion_point:]

    # Replace print statements in lifespan function
    # This is service-specific and would need careful handling
    new_content = re.sub(
        r'print\("(.+?)"\)',
        lambda m: f'logger.info("{m.group(1).lower().replace(" ", "_").replace("!", "").replace("...", "").strip()}")',
        new_content
    )

    # Add middleware to FastAPI app
    # Find app = FastAPI(... ) block
    app_pattern = r'(app = FastAPI\([^)]+\))'
    app_match = re.search(app_pattern, new_content, re.DOTALL)

    if app_match:
        app_end = app_match.end()
        middleware_code = '\n\n# Add request logging middleware\napp.add_middleware(RequestLoggingMiddleware, service_name="' + service_name + '")\n'
        new_content = new_content[:app_end] + middleware_code + new_content[app_end:]

    # Write updated content
    main_file.write_text(new_content)
    print(f"  ✅ Updated successfully")
    return True


# Services to update
SERVICES_TO_UPDATE = [
    ("crop-health", "crop-health"),
    ("crop-intelligence-service", "crop-intelligence"),
    ("satellite-service", "satellite-service"),
    ("ndvi-engine", "ndvi-engine"),
    ("ndvi-processor", "ndvi-processor"),
    ("weather-service", "weather-service"),
    ("weather-advanced", "weather-advanced"),
    ("alert-service", "alert-service"),
    ("notification-service", "notification-service"),
    ("field-core", "field-core"),
    ("field-service", "field-service"),
    ("field-ops", "field-ops"),
    ("field-intelligence", "field-intelligence"),
    ("field-management-service", "field-management"),
    ("field-chat", "field-chat"),
    ("task-service", "task-service"),
    ("equipment-service", "equipment-service"),
    ("inventory-service", "inventory-service"),
    ("billing-core", "billing-core"),
    ("user-service", "user-service"),
    ("irrigation-smart", "irrigation-smart"),
    ("fertilizer-advisor", "fertilizer-advisor"),
    ("agro-advisor", "agro-advisor"),
    ("advisory-service", "advisory-service"),
    ("astronomical-calendar", "astronomical-calendar"),
    ("vegetation-analysis-service", "vegetation-analysis"),
    ("yield-engine", "yield-engine"),
    ("iot-gateway", "iot-gateway"),
    ("ws-gateway", "ws-gateway"),
    ("virtual-sensors", "virtual-sensors"),
    ("provider-config", "provider-config"),
    ("indicators-service", "indicators-service"),
    ("ai-agents-core", "ai-agents-core"),
    ("code-review-service", "code-review"),
    ("mcp-server", "mcp-server"),
]

def main():
    print("=" * 70)
    print("Batch Updating Python Services with Structured JSON Logging")
    print("=" * 70)

    updated = 0
    skipped = 0
    errors = 0

    for service_dir, service_name in SERVICES_TO_UPDATE:
        print(f"\n📦 {service_dir}")
        service_path = SERVICES_DIR / service_dir

        if not service_path.exists():
            print(f"  ⚠️  Directory not found")
            errors += 1
            continue

        try:
            if update_python_service(service_path, service_name):
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Updated: {updated}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print(f"📊 Total: {updated + skipped + errors}")
    print("=" * 70)

if __name__ == "__main__":
    main()
