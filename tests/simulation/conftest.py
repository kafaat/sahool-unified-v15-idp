"""Shared fixtures + path setup for ``tests/simulation/``.

Why this file exists
--------------------
``tests/simulation/test_ground_vision.py`` imports the service's internal
modules with paths like::

    from apps.services.ground_vision_service.src.core.geo_projection import ...

Python can't resolve that: the directory on disk is
``apps/services/ground-vision-service/`` (hyphen, not underscore), and
hyphens are invalid in Python module names. Every test in that file was
failing at collection time with ``ModuleNotFoundError``.

The idiomatic fix — already used by the service's own test suite at
``apps/services/ground-vision-service/tests/conftest.py`` — is to put the
service directory on ``sys.path`` and import from ``src.X`` directly.
This conftest does that once for every test in ``tests/simulation/``.

We keep the import-aliasing narrow: only the ground-vision-service module
tree is exposed under the ``apps.services.ground_vision_service`` name,
so tests can keep their original imports without rewriting 26 call-sites.
Nothing else in the monorepo is affected — ``sys.path`` additions are
local to the importing process and cleared between pytest workers.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

_SERVICE_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "apps"
    / "services"
    / "ground-vision-service"
)

# Make ``from src.<pkg>`` work when tests import via the alias below.
if _SERVICE_DIR.is_dir() and str(_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICE_DIR))

# Expose the hyphenated service under its Python-legal underscored alias so
# the test file's existing ``from apps.services.ground_vision_service.src.X
# import Y`` imports resolve.
if _SERVICE_DIR.is_dir():
    # Build the ``apps.services.ground_vision_service`` package chain as
    # *packages* (not plain modules) by setting ``__path__`` on each — this
    # is what ``from pkg.submodule import X`` needs. Without ``__path__``
    # Python treats the name as a leaf module and refuses to look for
    # submodules inside it.
    def _ensure_pkg(name: str, paths: list[str]) -> types.ModuleType:
        mod = sys.modules.get(name)
        if mod is None:
            mod = types.ModuleType(name)
            sys.modules[name] = mod
        # Merge paths so any legitimately installed package with the same
        # name keeps working.
        existing = list(getattr(mod, "__path__", []) or [])
        mod.__path__ = list(dict.fromkeys(existing + paths))  # type: ignore[attr-defined]
        return mod

    repo_root = Path(__file__).resolve().parent.parent.parent
    apps_mod = _ensure_pkg("apps", [str(repo_root / "apps")])
    services_mod = _ensure_pkg("apps.services", [str(repo_root / "apps" / "services")])
    apps_mod.services = services_mod  # type: ignore[attr-defined]

    # The service itself is a package whose contents live under the
    # hyphenated directory — ``__path__`` redirects Python there when
    # resolving ``apps.services.ground_vision_service.src.*``.
    gv_alias = _ensure_pkg(
        "apps.services.ground_vision_service",
        [str(_SERVICE_DIR)],
    )
    services_mod.ground_vision_service = gv_alias  # type: ignore[attr-defined]
