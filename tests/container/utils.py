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
# Caches
# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}
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
    cache_key = f"_src_{svc}"
    if cache_key not in _dockerfile_cache:
        src_dir = SERVICES_DIR / svc / "src"
        if not src_dir.exists():
            _dockerfile_cache[cache_key] = ""
            return ""
        combined = ""
        for f in sorted(src_dir.rglob("*.py"))[:max_files]:
            try:
                combined += f.read_text("utf-8", errors="ignore") + "\n"
            except OSError:
                continue
        _dockerfile_cache[cache_key] = combined
    return _dockerfile_cache[cache_key]


def load_compose() -> dict[str, Any]:
    """Load and cache the main docker-compose.yml (with sanitized env vars)."""
    global _compose_cache
    if _compose_cache is None:
        content = MAIN_COMPOSE.read_text("utf-8")
        sanitized = re.sub(r"\$\{([^:}]+):-(\d+)\}", r"\2", content)
        sanitized = re.sub(r"\$\{[^}]+\}", "placeholder", sanitized)
        _compose_cache = yaml.safe_load(sanitized) or {}
    return _compose_cache
