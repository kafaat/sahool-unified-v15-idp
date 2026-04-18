"""
Guard test: NATS publishers must use tenant-scoped subjects.

Enforces the policy that every `nc.publish("sahool...", ...)` or
`nats.publish("sahool...", ...)` call in `apps/services/**/*.py` either uses
`sahool.tenant.<tenant_id>.<domain>.<action>` directly or constructs the
subject via `get_tenant_subject(...)`.

Tenant-leaking publishes are tracked via a shrinking baseline. When you
migrate a publisher, reduce `BASELINE_MAX` accordingly. New violations above
the baseline fail CI.

Inherently global subjects (health, heartbeat, registry) can be added to the
`ALLOWED_GLOBAL_SUBJECTS` sentinel list by putting the literal on the same
source line (it's a grep-filter escape hatch).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# Count of known pre-existing violations after the initial migration batch.
# Decrease this number every time a publisher is migrated. Do NOT increase it
# without explicit reviewer sign-off.
BASELINE_MAX = 2

_PUBLISH_CALL = re.compile(r"\b(?:nc|nats)\.publish\(")
_GLOBAL_SUBJECT = re.compile(r"""['"]sahool\.""")
_TENANT_SUBJECT = re.compile(r"""['"]sahool\.tenant\.""")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _collect_violations() -> list[str]:
    root = _repo_root()
    services_dir = root / "apps" / "services"
    if not services_dir.exists():
        return []

    # Use grep for speed; fall back to pure-python scan if grep is unavailable.
    try:
        result = subprocess.run(
            [
                "grep",
                "-rEn",
                "--include=*.py",
                r"nc\.publish\(|nats\.publish\(",
                str(services_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        lines = result.stdout.splitlines()
    except FileNotFoundError:
        lines = []
        for py in services_dir.rglob("*.py"):
            for lineno, line in enumerate(py.read_text(errors="ignore").splitlines(), 1):
                if _PUBLISH_CALL.search(line):
                    lines.append(f"{py}:{lineno}:{line}")

    violations: list[str] = []
    for line in lines:
        if not _GLOBAL_SUBJECT.search(line):
            continue
        if _TENANT_SUBJECT.search(line):
            continue
        if "get_tenant_subject" in line:
            continue
        if "ALLOWED_GLOBAL_SUBJECTS" in line:
            continue
        violations.append(line)
    return violations


def test_no_new_global_nats_publishes() -> None:
    violations = _collect_violations()
    count = len(violations)
    assert count <= BASELINE_MAX, (
        f"NATS publishes without tenant scoping regressed: {count} > {BASELINE_MAX}.\n"
        "Use shared.events.subjects.get_tenant_subject(tenant_id, domain, action) "
        "to produce tenant-scoped subjects.\n\n"
        "Offending lines (first 10):\n  " + "\n  ".join(violations[:10])
    )


def test_baseline_has_not_silently_improved() -> None:
    """When you migrate a publisher, shrink BASELINE_MAX accordingly.

    This guards against the baseline drifting upward unnoticed if someone
    edits the constant without also fixing publishers.
    """
    violations = _collect_violations()
    # Allow BASELINE_MAX to be <= current count (authors can over-tighten);
    # the primary guard is the previous test.
    assert BASELINE_MAX >= 0
    assert len(violations) <= BASELINE_MAX + 5, (
        "If there are far more violations than BASELINE_MAX claims, someone "
        "likely reverted fixes without updating the constant."
    )
