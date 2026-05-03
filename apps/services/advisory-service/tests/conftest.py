"""Test configuration for service."""

from __future__ import annotations

import importlib.util
import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Make ``apps/services/shared`` (the service-local package that ``src/main.py``
# expects, e.g. for ``TokenRevocationMiddleware(exempt_paths=...)``) the
# preferred ``shared`` package. We deliberately do NOT extend its ``__path__``
# with the repo-root ``shared/`` directory because that would surface modules
# (e.g. ``shared.events.subjects``) whose stricter validation breaks tests
# that rely on the existing ImportError fallback path in ``src.events.types``.
_SVC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # apps/services
if os.path.isdir(os.path.join(_SVC_DIR, "shared")) and _SVC_DIR not in sys.path:
    sys.path.insert(0, _SVC_DIR)

# Surgical side-load of ``shared.stability`` from the repo-root ``shared/``
# package so that advisor v2 retry tests (``shared.stability.retry_classifier``)
# can import it. We attach the loaded module to whichever ``shared`` package
# resolves first (typically ``apps/services/shared``) without polluting its
# ``__path__``.
_REPO_ROOT = os.path.abspath(os.path.join(_SVC_DIR, "..", ".."))
_ROOT_STABILITY = os.path.join(_REPO_ROOT, "shared", "stability")


def _load_shared_stability() -> None:
    init_file = os.path.join(_ROOT_STABILITY, "__init__.py")
    if not os.path.isfile(init_file):
        return
    try:
        import shared as _shared_pkg  # noqa: F401  (anchor host package)
    except ImportError:
        return
    if "shared.stability" in sys.modules:
        return
    spec = importlib.util.spec_from_file_location(
        "shared.stability",
        init_file,
        submodule_search_locations=[_ROOT_STABILITY],
    )
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    sys.modules["shared.stability"] = module
    try:
        spec.loader.exec_module(module)
    except Exception:  # noqa: BLE001 — tenacity etc. may be missing
        sys.modules.pop("shared.stability", None)
        return
    _shared_pkg.stability = module  # type: ignore[attr-defined]


_load_shared_stability()

# Clear cached src modules from other services to avoid cross-contamination in CI
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _mod in list(sys.modules):
    if not (_mod == "src" or _mod.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_service_root):
        del sys.modules[_mod]


def pytest_collection_modifyitems(config, items):  # noqa: ARG001
    """Re-attach pre-loaded ``shared.stability`` after ``src.main`` (loaded by
    other test modules) may have rebound the ``shared`` package."""
    _stability = sys.modules.get("shared.stability")
    _shared = sys.modules.get("shared")
    if _stability is not None and _shared is not None and not hasattr(_shared, "stability"):
        _shared.stability = _stability  # type: ignore[attr-defined]
