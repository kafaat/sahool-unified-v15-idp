"""
Import isolation for per-service test suites.

Ensures each service's `src/` package is importable without conflicts
when multiple services share the same `src` module name in a monorepo.

Usage in conftest.py:
    from tests._helpers.import_isolation import isolate_service_imports
    isolate_service_imports(__file__)
"""

import os
import sys


def isolate_service_imports(conftest_file: str) -> None:
    """Add service root to sys.path and clear stale src module cache.

    Args:
        conftest_file: Pass ``__file__`` from the calling conftest.py.
    """
    service_root = os.path.abspath(os.path.join(os.path.dirname(conftest_file), ".."))

    if service_root not in sys.path:
        sys.path.insert(0, service_root)

    # Clear cached src modules from *other* services to avoid cross-contamination
    for mod_name in list(sys.modules):
        if not (mod_name == "src" or mod_name.startswith("src.")):
            continue
        mod_obj = sys.modules.get(mod_name)
        mod_file = getattr(mod_obj, "__file__", None) or ""
        if not mod_file or not os.path.abspath(mod_file).startswith(service_root):
            del sys.modules[mod_name]
