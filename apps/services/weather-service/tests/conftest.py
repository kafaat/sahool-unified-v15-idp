"""
Weather Service Test Configuration
تكوين اختبارات خدمة الطقس

Ensures correct module resolution for shared imports in CI.
"""

import sys
from pathlib import Path

# Add project root first so shared.auth resolves to the root shared/ module
# (not apps/services/shared/ which has a different User model with hashed_password)
_service_dir = Path(__file__).resolve().parent.parent  # weather-service/
_project_root = _service_dir.parent.parent.parent  # sahool-unified-v15-idp/
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
if str(_service_dir) not in sys.path:
    sys.path.insert(0, str(_service_dir))
