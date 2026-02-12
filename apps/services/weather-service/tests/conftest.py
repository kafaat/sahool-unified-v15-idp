"""
Weather Service Test Configuration
تكوين اختبارات خدمة الطقس

Ensures correct module resolution for shared imports in CI.
"""

import sys
from pathlib import Path

# Ensure apps/services/shared resolves correctly.
# CI sets PYTHONPATH=$PWD which would resolve 'shared' to root-level shared/
# instead of apps/services/shared/. Insert the correct path first.
_service_dir = Path(__file__).resolve().parent.parent  # weather-service/
_services_dir = _service_dir.parent  # apps/services/
if str(_services_dir) not in sys.path:
    sys.path.insert(0, str(_services_dir))
if str(_service_dir) not in sys.path:
    sys.path.insert(0, str(_service_dir))
