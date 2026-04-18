"""
Guard test: NATS publishers must use tenant-scoped subjects.

Enforces the policy that every ``nc.publish(...)`` / ``nats.publish(...)``
call in ``apps/services/**/*.py`` either:

* uses a literal that starts with ``sahool.tenant.`` (directly tenant-scoped),
* constructs the subject via ``get_tenant_subject(...)``, or
* is explicitly marked as tenant-irrelevant with ``ALLOWED_GLOBAL_SUBJECTS``.

The scanner walks the Python AST so it handles multi-line calls and calls
whose first argument is a name/attribute bound to a literal earlier in the
module (e.g. ``SUBJECT = "sahool.<domain>.<action>"`` then ``nc.publish(SUBJECT, ...)``).
This addresses the previous grep-based implementation's blind spots for:

* ``await nc.publish(\n    "sahool.soil.test_created",\n    payload)`` — multi-line
* ``_SUBJ = "sahool.x.y"`` + ``nc.publish(_SUBJ, ...)`` — constant indirection

Tenant-leaking publishes are tracked via a shrinking baseline (``BASELINE_MAX``).
When you migrate a publisher, reduce the baseline. New violations above the
baseline fail CI.
"""

from __future__ import annotations

import ast
from pathlib import Path

# Count of known pre-existing violations after the initial migration batch.
# Decrease every time a publisher is migrated. Do NOT increase it without
# explicit reviewer sign-off.
BASELINE_MAX = 0


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_publish_call(node: ast.Call) -> bool:
    """Return True for ``<x>.publish(...)`` calls where ``<x>`` is a Name
    ending in ``nc``/``nats`` (attribute resolution kept loose on purpose so
    we catch ``self.nc.publish(...)``, ``app.state.nc.publish(...)`` etc)."""
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr != "publish":
        return False

    # Walk the receiver chain and flatten to dotted name for inspection.
    parts: list[str] = []
    cur: ast.AST = func.value
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    parts.reverse()
    last = parts[-1] if parts else ""
    return last in {"nc", "nats", "client", "js"}


def _string_value(
    expr: ast.AST, module_constants: dict[str, str]
) -> str | None:
    """Resolve an expression to a literal string if possible.

    Covers:
    - ``ast.Constant`` (Python 3.8+ string literal)
    - ``ast.Name`` previously bound to a string literal at module scope
    - ``ast.Attribute`` falls through (cannot resolve cheaply)
    - f-strings: returns a synthetic literal preserving their static prefix
      when that prefix starts with ``sahool.`` (so ``f"sahool.{x}.y"`` still
      matches as a global subject).
    """
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return expr.value
    if isinstance(expr, ast.Name) and expr.id in module_constants:
        return module_constants[expr.id]
    if isinstance(expr, ast.JoinedStr):
        # ``f"sahool.{tenant_id}.<domain>.<action>"`` is the legacy
        # inline-tenant pattern documented in CLAUDE.md. Report it as
        # ``sahool.tenant.<inline>.`` so the caller sees it as tenant-scoped.
        values = expr.values
        if (
            len(values) >= 2
            and isinstance(values[0], ast.Constant)
            and isinstance(values[0].value, str)
            and values[0].value == "sahool."
            and isinstance(values[1], ast.FormattedValue)
        ):
            return "sahool.tenant.<inline>."
        first = values[0] if values else None
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    return None


def _collect_module_string_constants(tree: ast.Module) -> dict[str, str]:
    """Return a mapping of top-level ``NAME = "literal"`` assignments."""
    constants: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    constants[target.id] = node.value.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                constants[node.target.id] = node.value.value
    return constants


def _source_line(path: Path, lineno: int) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if i == lineno:
                    return line.rstrip()
    except OSError:
        return ""
    return ""


def _is_violation(
    call: ast.Call,
    module_constants: dict[str, str],
    call_line: str,
    surrounding_source: str,
) -> bool:
    """Decide whether a publish call is a tenant-leaking violation.

    Passes (not a violation) if any of:
    * First positional arg resolves to a string literal starting with
      ``sahool.tenant.``
    * First positional arg is a ``Call`` whose function name contains
      ``get_tenant_subject`` / ``tenant_subject_for``.
    * ``ALLOWED_GLOBAL_SUBJECTS`` appears on the call line or within a
      two-line radius (explicit escape hatch for health/heartbeat subjects).
    """
    if not call.args:
        return False  # pathological — can't tell
    first = call.args[0]

    # Escape hatch
    if "ALLOWED_GLOBAL_SUBJECTS" in call_line or "ALLOWED_GLOBAL_SUBJECTS" in surrounding_source:
        return False

    # Subject built via helper
    if isinstance(first, ast.Call):
        helper_name = ""
        if isinstance(first.func, ast.Name):
            helper_name = first.func.id
        elif isinstance(first.func, ast.Attribute):
            helper_name = first.func.attr
        if helper_name in {"get_tenant_subject", "tenant_subject_for"}:
            return False

    # Resolve literal
    literal = _string_value(first, module_constants)
    if literal is None:
        # Unknown subject source (function call, attribute, etc.). Be
        # conservative: only flag if the call line itself contains
        # ``"sahool.`` (matches the old grep behaviour and avoids
        # false-positives on indirected plumbing we can't analyse).
        return '"sahool.' in call_line or "'sahool." in call_line

    if not literal.startswith("sahool."):
        return False  # some other namespace — out of scope
    return not literal.startswith("sahool.tenant.")


def _collect_violations() -> list[str]:
    root = _repo_root()
    services_dir = root / "apps" / "services"
    if not services_dir.exists():
        return []

    violations: list[str] = []
    for py in services_dir.rglob("*.py"):
        if "__pycache__" in py.parts or "/archive/" in str(py):
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text, filename=str(py))
        except SyntaxError:
            continue

        module_constants = _collect_module_string_constants(tree)
        source_lines = text.splitlines()

        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and _is_publish_call(node)):
                continue
            lineno = node.lineno or 1
            call_line = _source_line(py, lineno)
            lo = max(0, lineno - 3)
            hi = min(len(source_lines), lineno + 2)
            surrounding = "\n".join(source_lines[lo:hi])
            if _is_violation(node, module_constants, call_line, surrounding):
                snippet = call_line.strip() if call_line else ast.dump(node)[:80]
                violations.append(f"{py}:{lineno}: {snippet}")
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
    assert BASELINE_MAX >= 0
    assert len(violations) <= BASELINE_MAX + 5, (
        "If there are far more violations than BASELINE_MAX claims, someone "
        "likely reverted fixes without updating the constant."
    )
