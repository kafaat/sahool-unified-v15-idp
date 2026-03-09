"""
Pytest configuration for Task Service unit tests
تكوين Pytest لاختبارات وحدة خدمة المهام

This module sets up the Python path to allow importing from the
task-service/src package, while ensuring test isolation by evicting
any cached 'src.*' modules from other services at load time.
"""

import sys
from pathlib import Path

# Get the absolute path to the task service source directory
TASK_SERVICE_SRC = (
    Path(__file__).parent.parent.parent.parent / "apps" / "services" / "task-service" / "src"
)

# Add the parent directory of src to path so that we can import as a package
# This allows `from src.exceptions import ...` style imports
TASK_SERVICE_ROOT = TASK_SERVICE_SRC.parent

# Evict any cached src.* modules from other services (e.g. vegetation-analysis)
# that may have been loaded by earlier conftest files.
# This runs once at conftest load time (before test collection).
_stale = [k for k in sys.modules if k == "src" or k.startswith("src.")]
for _k in _stale:
    del sys.modules[_k]

# Add to path, ensuring task-service is first
_root_str = str(TASK_SERVICE_ROOT)
if _root_str in sys.path:
    sys.path.remove(_root_str)
sys.path.insert(0, _root_str)

_src_str = str(TASK_SERVICE_SRC)
if _src_str in sys.path:
    sys.path.remove(_src_str)
sys.path.insert(0, _src_str)
