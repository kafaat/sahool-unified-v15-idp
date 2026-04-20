"""Test configuration for test-harness-sidecar.

Adds the service directory to ``sys.path`` so tests can do
``from src.main import app`` — same pattern the rest of the platform
services use in their own ``tests/conftest.py``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Repo root for ``shared.*`` imports
_HERE = Path(__file__).resolve().parent
_SERVICE_DIR = _HERE.parent
_REPO_ROOT = _SERVICE_DIR.parent.parent.parent

for p in (str(_REPO_ROOT), str(_SERVICE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Test-mode env so Settings doesn't refuse to construct + DSN doesn't blow up
os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("TEST_SEED_TOKEN", "x" * 32)
os.environ.setdefault("POSTGRES_DSN", "postgresql://postgres:postgres@127.0.0.1:5432/postgres")
