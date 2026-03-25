"""
Shared test utilities for container tests.
أدوات مشتركة لاختبارات الحاويات

Provides cached Dockerfile/requirements parsing used by all group tests.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

# ---------------------------------------------------------------------------
# Caches (separate per content type to avoid key collisions)
# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}
_source_cache: dict[str, str] = {}
_compose_cache: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# File Readers (cached)
# ---------------------------------------------------------------------------


def read_dockerfile(svc: str) -> str:
    """Read and cache a service's Dockerfile content."""
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


def read_requirements(svc: str) -> str:
    """Read and cache a service's requirements.txt content."""
    if svc not in _requirements_cache:
        path = SERVICES_DIR / svc / "requirements.txt"
        _requirements_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _requirements_cache[svc]


def req_packages(svc: str) -> set[str]:
    """Return normalized package names from a service's requirements.txt."""
    text = read_requirements(svc)
    pkgs: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[>=<!\[;]", line)[0].strip().lower().replace("-", "_")
        if name:
            pkgs.add(name)
    return pkgs


def read_all_source(svc: str, max_files: int = 25) -> str:
    """Read all Python source files from a service's src/ directory (cached)."""
    if svc not in _source_cache:
        src_dir = SERVICES_DIR / svc / "src"
        if not src_dir.exists():
            _source_cache[svc] = ""
            return ""
        combined = ""
        for f in sorted(src_dir.rglob("*.py"))[:max_files]:
            try:
                combined += f.read_text("utf-8", errors="ignore") + "\n"
            except OSError:
                continue
        _source_cache[svc] = combined
    return _source_cache[svc]


def load_compose() -> dict[str, Any]:
    """Load and cache the main docker-compose.yml.

    Note: yaml.safe_load coerces YAML 1.1 booleans (no/off/on → False/True).
    Tests comparing restart policies should accept both string and boolean forms.
    """
    global _compose_cache
    if _compose_cache is None:
        content = MAIN_COMPOSE.read_text("utf-8")
        sanitized = re.sub(r"\$\{([^:}]+):-(\d+)\}", r"\2", content)
        sanitized = re.sub(r"\$\{[^}]+\}", "placeholder", sanitized)
        _compose_cache = yaml.safe_load(sanitized) or {}
    return _compose_cache
