"""
SAHOOL Audit Retention — Policy resolution.

A retention policy is a ``(category, retention_days)`` pair. Categories
match the ``chk_category`` CHECK constraint on audit_log (authentication,
authorization, configuration, catalog, kubernetes, field_ops, billing,
compliance, security, data, system, user_management, code_change).

Policies come from environment variables, one per category, of the form::

    AUDIT_RETENTION_<CATEGORY_UPPER>_DAYS=<int>

Plus a platform-wide fallback::

    AUDIT_RETENTION_DEFAULT_DAYS=<int>

Categories with no env var and no default are SKIPPED (we never delete
what we don't have an explicit policy for). This keeps the worker safe
by construction — a misconfigured deployment deletes nothing rather
than deleting everything.

The module is deliberately side-effect-free: the only way to resolve
policies is to pass in the env mapping, which makes unit testing
trivial and keeps the runtime one-shot.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

# Must stay in sync with chk_category in migrations/001_create_audit_log.sql.
# Any new category added there must be added here too, or the worker will
# silently refuse to apply a policy for it.
KNOWN_CATEGORIES: tuple[str, ...] = (
    "authentication",
    "authorization",
    "configuration",
    "catalog",
    "kubernetes",
    "field_ops",
    "billing",
    "compliance",
    "security",
    "data",
    "system",
    "user_management",
    "code_change",
)

DEFAULT_ENV_VAR = "AUDIT_RETENTION_DEFAULT_DAYS"
CATEGORY_ENV_PREFIX = "AUDIT_RETENTION_"
CATEGORY_ENV_SUFFIX = "_DAYS"


@dataclass(frozen=True)
class RetentionPolicy:
    """A single (category, retention_days) rule."""

    category: str
    retention_days: int

    def __post_init__(self) -> None:
        if self.retention_days <= 0:
            raise ValueError(f"retention_days must be > 0 for category={self.category!r}, got {self.retention_days}")
        if self.category not in KNOWN_CATEGORIES:
            raise ValueError(f"unknown category {self.category!r}; must be one of {KNOWN_CATEGORIES}")


def _parse_positive_int(raw: str, env_var: str) -> int:
    """Parse ``raw`` as a positive int or raise ``ValueError``.

    We reject 0 and negatives here rather than in ``RetentionPolicy`` so
    the env-var name is in the error message — much easier to debug a
    typo in a deployment manifest.
    """
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{env_var}={raw!r} is not an integer") from exc
    if value <= 0:
        raise ValueError(
            f"{env_var}={value} must be > 0 (retention days cannot be zero "
            "or negative — use an unset variable to skip a category)"
        )
    return value


def resolve_policies(env: Mapping[str, str]) -> list[RetentionPolicy]:
    """Build the list of policies from an environment mapping.

    Resolution rules:
      1. A per-category override (AUDIT_RETENTION_<CATEGORY>_DAYS) wins.
      2. Otherwise AUDIT_RETENTION_DEFAULT_DAYS applies to every known
         category.
      3. If neither is set for a category, the category is skipped — no
         policy is emitted, no rows will be deleted for it.

    ``env`` is accepted as a parameter rather than read from ``os.environ``
    so tests can pass in a controlled dict without monkey-patching.
    """
    default_raw = env.get(DEFAULT_ENV_VAR)
    default_days: int | None = _parse_positive_int(default_raw, DEFAULT_ENV_VAR) if default_raw else None

    policies: list[RetentionPolicy] = []
    for category in KNOWN_CATEGORIES:
        env_var = f"{CATEGORY_ENV_PREFIX}{category.upper()}{CATEGORY_ENV_SUFFIX}"
        override_raw = env.get(env_var)
        if override_raw:
            days = _parse_positive_int(override_raw, env_var)
        elif default_days is not None:
            days = default_days
        else:
            # No policy for this category; skip it. The operator can
            # inspect the worker's logs to see which categories were
            # skipped and why.
            continue
        policies.append(RetentionPolicy(category=category, retention_days=days))

    return policies


def describe(policies: list[RetentionPolicy]) -> str:
    """Human-readable summary for logs and the --dry-run output."""
    if not policies:
        return "no retention policies configured (worker is a no-op)"
    lines = [f"  {p.category:<18s} → {p.retention_days:>5d} days" for p in policies]
    return "retention policies:\n" + "\n".join(lines)
