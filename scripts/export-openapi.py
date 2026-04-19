#!/usr/bin/env python3
"""Export OpenAPI specs from every FastAPI service under apps/services/.

For each service that exposes ``app = FastAPI(...)`` in ``src/main.py``, this
script imports the module in isolation and writes the schema to
``apps/services/<name>/openapi.yaml``. Services whose modules cannot be
imported (missing runtime deps, DB access at import time, etc.) are skipped
with a structured reason so the export is best-effort and deterministic.

Usage:
    python scripts/export-openapi.py
    python scripts/export-openapi.py --service advisory-service
    python scripts/export-openapi.py --format json --fail-fast

Exit codes:
    0  at least one spec exported and no fatal error
    1  every service failed to import
    2  invalid arguments / environment
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = REPO_ROOT / "apps" / "services"


@dataclass
class ExportResult:
    exported: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "exported_count": len(self.exported),
            "skipped_count": len(self.skipped),
            "exported": sorted(self.exported),
            "skipped": [{"service": s, "reason": r} for s, r in sorted(self.skipped)],
        }


def discover_services() -> list[Path]:
    if not SERVICES_DIR.exists():
        raise FileNotFoundError(f"services dir not found: {SERVICES_DIR}")
    return sorted(
        p.parent.parent
        for p in SERVICES_DIR.glob("*/src/main.py")
        if p.is_file()
    )


def _prepare_sys_path(service_dir: Path) -> None:
    """Match sys.path hacks services use at runtime.

    Services expect ``apps/services`` and repo root on sys.path so
    ``from shared.xxx import yyy`` works. The service directory itself
    is added so ``src`` is importable as a top-level package.
    """
    for p in (str(REPO_ROOT), str(SERVICES_DIR), str(service_dir)):
        if p not in sys.path:
            sys.path.insert(0, p)


def _unload_between_services() -> None:
    """Drop service-local module caches so the next import is fresh.

    Every service ships a top-level ``src`` package; leaving cached
    ``src`` entries between imports would leak one service's app into
    the next.
    """
    to_drop = [
        name
        for name in sys.modules
        if name == "src" or name.startswith("src.") or name.startswith("_sahool_svc_")
    ]
    for name in to_drop:
        sys.modules.pop(name, None)


def extract_openapi(service_dir: Path) -> dict[str, Any]:
    """Import service main.py and return its OpenAPI schema.

    Raises on any failure. Caller decides whether to skip or abort.
    """
    service_name = service_dir.name
    main_py = service_dir / "src" / "main.py"
    if not main_py.exists():
        raise FileNotFoundError(f"{main_py} not found")

    _prepare_sys_path(service_dir)
    _unload_between_services()

    # Services use relative imports (``from .events import ...``), so we must
    # import them as a real package. Every service has ``src/__init__.py``;
    # with ``service_dir`` on sys.path, ``import src.main`` resolves correctly.
    import importlib

    module = importlib.import_module("src.main")
    app = getattr(module, "app", None)
    if app is None:
        raise AttributeError(f"{service_name}: no 'app' attribute in main.py")
    if not hasattr(app, "openapi"):
        raise AttributeError(
            f"{service_name}: app is not a FastAPI instance ({type(app).__name__})"
        )

    schema = app.openapi()

    if not isinstance(schema, dict):
        raise TypeError(f"{service_name}: app.openapi() returned {type(schema).__name__}")
    _normalise_integer_bounds(schema)
    return schema


# Keywords where a numeric value must match the declared ``type`` for the
# schema to be strictly valid JSON Schema / OpenAPI 3.1. FastAPI sometimes
# emits them as integer-valued floats (``365.0``) on ``type: integer``
# fields, which several validators flag as a schema error.
_INTEGER_BOUND_KEYS = ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf")


def _is_integer_type(t: Any) -> bool:
    """Return True if the schema's ``type`` is (or includes) ``integer``."""
    if t == "integer":
        return True
    if isinstance(t, list) and "integer" in t:
        return True
    return False


def _normalise_integer_bounds(node: Any) -> None:
    """Recursively coerce integer-valued floats on ``type: integer`` fields.

    Only the five numeric bound keywords are touched, and only when the value
    is a float whose fractional part is zero — fractional values get left
    alone so a real schema bug still surfaces.
    """
    if isinstance(node, dict):
        if _is_integer_type(node.get("type")):
            for key in _INTEGER_BOUND_KEYS:
                val = node.get(key)
                if isinstance(val, float) and val.is_integer():
                    node[key] = int(val)
        for v in node.values():
            _normalise_integer_bounds(v)
    elif isinstance(node, list):
        for item in node:
            _normalise_integer_bounds(item)


def write_spec(service_dir: Path, schema: dict[str, Any], fmt: str) -> Path:
    suffix = "yaml" if fmt == "yaml" else "json"
    out = service_dir / f"openapi.{suffix}"
    if fmt == "yaml":
        # ``sort_keys=True`` is the critical knob: FastAPI's internal dict order
        # depends on which modules imported Pydantic models in what sequence,
        # which drifts with transitive deps. Sorted output is byte-stable across
        # environments. Key order isn't semantic in OpenAPI, so we're free to
        # normalise it.
        text = yaml.safe_dump(
            schema,
            sort_keys=True,
            allow_unicode=True,
            default_flow_style=False,
            width=4096,
            indent=2,
        )
    else:
        text = json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    out.write_text(text, encoding="utf-8")
    return out


def export_all(
    services: list[Path],
    fmt: str,
    fail_fast: bool,
    only: str | None,
) -> ExportResult:
    result = ExportResult()

    # Test-mode envs so services that read env at import time don't explode.
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("JWT_SECRET_KEY", "openapi-export-placeholder-key-32chars")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")
    os.environ.setdefault("DATABASE_URL", "")
    os.environ.setdefault("NATS_URL", "")
    os.environ.setdefault("REDIS_URL", "")

    for service_dir in services:
        name = service_dir.name
        if only and name != only:
            continue
        try:
            schema = extract_openapi(service_dir)
            out = write_spec(service_dir, schema, fmt)
            rel = out.relative_to(REPO_ROOT)
            print(f"[ok]   {name:42s} -> {rel}")
            result.exported.append(name)
        except BaseException as exc:
            reason = f"{type(exc).__name__}: {exc}".splitlines()[0][:200]
            print(f"[skip] {name:42s} {reason}", file=sys.stderr)
            if os.environ.get("OPENAPI_EXPORT_DEBUG"):
                traceback.print_exc(file=sys.stderr)
            result.skipped.append((name, reason))
            if fail_fast:
                raise

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--format", choices=("yaml", "json"), default="yaml")
    parser.add_argument("--service", help="Export a single service by directory name")
    parser.add_argument("--fail-fast", action="store_true", help="Abort on first error")
    parser.add_argument(
        "--summary-json",
        type=Path,
        help="Write exported/skipped lists to this path (for CI consumption)",
    )
    args = parser.parse_args()

    try:
        services = discover_services()
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not services:
        print("error: no services found with src/main.py", file=sys.stderr)
        return 2

    result = export_all(services, args.format, args.fail_fast, args.service)

    print(
        f"\nSummary: exported={len(result.exported)} skipped={len(result.skipped)} "
        f"total={len(result.exported) + len(result.skipped)}"
    )

    if args.summary_json:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(result.as_dict(), indent=2))
        print(f"Summary written to {args.summary_json}")

    # Non-zero if *every* service failed (likely environment/tool issue, not service bugs).
    if not result.exported:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
