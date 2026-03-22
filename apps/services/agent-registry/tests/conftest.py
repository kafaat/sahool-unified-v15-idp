"""Test configuration for agent-registry."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src module to avoid cross-service contamination in CI
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from src.main import app

    return TestClient(app)
