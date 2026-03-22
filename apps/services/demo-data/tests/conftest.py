"""Test configuration for demo-data.

Note: demo-data is a standalone data generation script, not a FastAPI service.
It does not expose HTTP endpoints directly.
"""

import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src module to avoid cross-service contamination in CI
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]
