"""Conftest for AI unit tests.

Auto-skips test modules that depend on optional packages
(structlog, pydantic, etc.) when those packages are not installed.
"""

from __future__ import annotations

import importlib
import pathlib

# Modules that require optional heavy dependencies
_OPTIONAL_DEPS = ["structlog", "pydantic"]
_missing = [d for d in _OPTIONAL_DEPS if importlib.util.find_spec(d) is None]

if _missing:
    _here = pathlib.Path(__file__).parent
    # Skip test files for modules that import structlog/pydantic transitively
    _skip_prefixes = ["test_knowledge", "test_ultrarag"]
    collect_ignore = [
        str(p)
        for p in _here.glob("*.py")
        if any(p.name.startswith(prefix) for prefix in _skip_prefixes)
    ]
