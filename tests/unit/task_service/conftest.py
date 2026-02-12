"""
Pytest configuration for Task Service unit tests
تكوين Pytest لاختبارات وحدة خدمة المهام

This module sets up the Python path to allow importing from the
task-service/src package.
"""

import sys
import os
from pathlib import Path

# Get the absolute path to the task service source directory
TASK_SERVICE_SRC = (
    Path(__file__).parent.parent.parent.parent / "apps" / "services" / "task-service" / "src"
)

# Add the parent directory of src to path so that we can import as a package
# This allows `from src.exceptions import ...` style imports
TASK_SERVICE_ROOT = TASK_SERVICE_SRC.parent

# Add to path if not already present
if str(TASK_SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(TASK_SERVICE_ROOT))

# Also add the src directory directly for backward compatibility
if str(TASK_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(TASK_SERVICE_SRC))
