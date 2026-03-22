"""
Shared test fixtures for task-service tests.
"""

import os
import sys

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Ensure shared database module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
