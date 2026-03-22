"""
Shared test fixtures for task-service tests.
"""

import os
import sys

_tests_dir = os.path.dirname(os.path.abspath(__file__))
_service_dir = os.path.normpath(os.path.join(_tests_dir, ".."))

# IMPORTANT: shared database path must be FIRST so that `from database import Base`
# resolves to the shared database package, not src/database.py
_shared_db_path = os.path.normpath(os.path.join(_service_dir, "..", "shared"))
# Remove if already in path, then re-insert at position 0
if _shared_db_path in sys.path:
    sys.path.remove(_shared_db_path)
sys.path.insert(0, _shared_db_path)
