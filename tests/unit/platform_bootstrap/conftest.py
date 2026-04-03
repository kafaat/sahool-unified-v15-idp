"""
Configure PYTHONPATH so tests can import from packages/platform-bootstrap/src/
and apps/services/ai-advisor/src/ using dotted module paths.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]

# Map packages/platform-bootstrap → importable as platform_bootstrap
_PLATFORM_BOOTSTRAP = _ROOT / "packages" / "platform-bootstrap"
_PLATFORM_BOOTSTRAP_SRC = _PLATFORM_BOOTSTRAP / "src"

# Map apps/services/ai-advisor → importable as apps.services.ai_advisor
_AI_ADVISOR_SRC = _ROOT / "apps" / "services" / "ai-advisor"

for p in [str(_ROOT), str(_PLATFORM_BOOTSTRAP), str(_PLATFORM_BOOTSTRAP_SRC), str(_AI_ADVISOR_SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Make packages/platform-bootstrap importable as "platform_bootstrap"
# by creating a namespace alias via sys.modules if needed
import importlib

# Ensure the directory is importable as platform_bootstrap
_pb_init = _PLATFORM_BOOTSTRAP_SRC / "__init__.py"
if _pb_init.exists() and "platform_bootstrap" not in sys.modules:
    # Add the parent so "from platform_bootstrap.event_bus import ..." works
    parent = str(_PLATFORM_BOOTSTRAP_SRC.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
