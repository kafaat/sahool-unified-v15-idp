"""Test configuration for terrain-core-service."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src modules from other services to avoid cross-contamination in CI
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _mod in list(sys.modules):
    if not (_mod == "src" or _mod.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_service_root):
        del sys.modules[_mod]

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from src.main import app

    return TestClient(app)
