"""
conftest.py for tests/unit/services/

Patches sys.modules so that imports like
    apps.services.vegetation_analysis_service.src.agricultural_land_detector
resolve correctly even though the directory on disk uses hyphens:
    apps/services/vegetation-analysis-service/src/
"""

import importlib
import sys
import types
from pathlib import Path

# Root of the repository
_REPO = Path(__file__).resolve().parent.parent.parent.parent

# Map of underscore module names -> hyphenated directory names
_SERVICE_ALIASES = {
    "vegetation_analysis_service": "vegetation-analysis-service",
}


def _ensure_service_alias(underscore_name: str, hyphen_name: str) -> None:
    """Register a fake package so Python can import service modules by underscore name."""
    service_dir = _REPO / "apps" / "services" / hyphen_name
    src_dir = service_dir / "src"

    if not src_dir.is_dir():
        return

    # Ensure apps and apps.services are importable packages
    for mod_name in ("apps", "apps.services"):
        if mod_name not in sys.modules:
            pkg = types.ModuleType(mod_name)
            pkg.__path__ = []
            pkg.__package__ = mod_name
            sys.modules[mod_name] = pkg

    # Register the service package (apps.services.vegetation_analysis_service)
    full_name = f"apps.services.{underscore_name}"
    if full_name not in sys.modules:
        pkg = types.ModuleType(full_name)
        pkg.__path__ = [str(service_dir)]
        pkg.__package__ = full_name
        sys.modules[full_name] = pkg
        # Also set as attribute on parent
        sys.modules["apps.services"].__dict__[underscore_name] = pkg

    # Register the src sub-package (apps.services.vegetation_analysis_service.src)
    src_name = f"{full_name}.src"
    if src_name not in sys.modules:
        pkg = types.ModuleType(src_name)
        pkg.__path__ = [str(src_dir)]
        pkg.__package__ = src_name
        sys.modules[src_name] = pkg

    # Evict any cached bare 'src.*' modules from other services to prevent
    # cross-service contamination when tests run together
    stale = [k for k in sys.modules if k == "src" or k.startswith("src.")]
    for k in stale:
        del sys.modules[k]

    # Add src dir to sys.path so relative imports within the service work
    src_str = str(src_dir)
    if src_str in sys.path:
        sys.path.remove(src_str)
    sys.path.insert(0, src_str)

    # Add service dir to sys.path for packages that import from service root
    svc_str = str(service_dir)
    if svc_str in sys.path:
        sys.path.remove(svc_str)
    sys.path.insert(0, svc_str)


# Apply all aliases at import time (conftest.py is loaded before tests)
for _uname, _hname in _SERVICE_ALIASES.items():
    _ensure_service_alias(_uname, _hname)
