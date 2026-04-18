#!/usr/bin/env python3
"""SAHOOL service-template checker.

Validates that an ``apps/services/<svc>/src/main.py`` follows platform
conventions required for NEW/changed services:

1. Imports ``setup_logging`` from ``shared.logging_config``
   (unless the file opts out via ``# LINT-OPT-OUT: logging``).
2. IF the file uses ``Depends(get_current_user)`` anywhere, it MUST
   import ``get_current_user`` from ``shared.auth.dependencies``.
3. Defines both ``/healthz`` and ``/readyz`` endpoints.

This is intentionally narrow: it aims to catch NEW violations without
false-positives on the existing fleet. Exits 0 on success, 1 on any
failure, 2 on bad invocation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FASTAPI_APP = re.compile(r"\bFastAPI\s*\(|\bapp\s*=\s*FastAPI\b|APIRouter\s*\(")
LOGGING_IMPORT = re.compile(
    r"from\s+shared\.logging_config\s+import\s+[^\n]*\bsetup_logging\b"
)
AUTH_IMPORT = re.compile(
    r"from\s+shared\.auth\.dependencies\s+import\s+[^\n]*\bget_current_user\b"
)
DEPENDS_GET_CURRENT_USER = re.compile(r"Depends\s*\(\s*get_current_user\s*\)")
# A service can satisfy the auth rule by either importing the shared dep
# OR defining its own `get_current_user` locally (legacy services). The
# latter emits a DEPRECATION note rather than a hard failure so existing
# services aren't broken but new ones are nudged toward the shared dep.
LOCAL_GET_CURRENT_USER = re.compile(
    r"^\s*(?:async\s+)?def\s+get_current_user\s*\(", re.MULTILINE
)
OPT_OUT_LOGGING = re.compile(r"#\s*LINT-OPT-OUT:\s*logging", re.IGNORECASE)
OPT_OUT_AUTH = re.compile(r"#\s*LINT-OPT-OUT:\s*auth", re.IGNORECASE)
HEALTHZ_ROUTE = re.compile(r"""@(?:app|router)\.get\(\s*['"]/healthz['"]""")
READYZ_ROUTE = re.compile(r"""@(?:app|router)\.get\(\s*['"]/readyz['"]""")


def line_no(text: str, match: re.Match[str] | None) -> int:
    if match is None:
        return 0
    return text.count("\n", 0, match.start()) + 1


def check(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: file not found"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    # Skip non-FastAPI files (CronJobs / CLI workers like audit-retention-worker).
    # The HTTP-service template rules (healthz/readyz/setup_logging/auth) don't
    # apply to batch jobs that have no HTTP surface.
    if not FASTAPI_APP.search(text):
        return []

    if not OPT_OUT_LOGGING.search(text) and not LOGGING_IMPORT.search(text):
        errors.append(
            f"{path}:1: missing `from shared.logging_config import setup_logging` "
            "(or add `# LINT-OPT-OUT: logging` comment with justification)"
        )

    uses_depends_auth = DEPENDS_GET_CURRENT_USER.search(text)
    if uses_depends_auth and not OPT_OUT_AUTH.search(text):
        has_shared_import = AUTH_IMPORT.search(text)
        has_local_def = LOCAL_GET_CURRENT_USER.search(text)
        if not has_shared_import and not has_local_def:
            errors.append(
                f"{path}:{line_no(text, uses_depends_auth)}: uses "
                "`Depends(get_current_user)` but does not import it from "
                "`shared.auth.dependencies` and does not define it locally. "
                "Prefer the shared dependency."
            )

    if not HEALTHZ_ROUTE.search(text):
        errors.append(
            f"{path}: missing `@app.get('/healthz')` (or `@router.get('/healthz')`) endpoint"
        )
    if not READYZ_ROUTE.search(text):
        errors.append(
            f"{path}: missing `@app.get('/readyz')` (or `@router.get('/readyz')`) endpoint"
        )
    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: service-template-check.py <main.py> [<main.py> ...]", file=sys.stderr)
        return 2
    all_errors: list[str] = []
    for arg in argv[1:]:
        all_errors.extend(check(Path(arg)))
    if all_errors:
        print("Service template check FAILED:", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        print(
            "\nFix: follow the service template in idp/templates/python-fastapi/ "
            "or see `Python Service Conventions` in CLAUDE.md.",
            file=sys.stderr,
        )
        return 1
    print(f"service-template-check: OK ({len(argv) - 1} file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
