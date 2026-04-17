"""Unit tests for policy resolution — no I/O, no DB."""

from __future__ import annotations

import pytest
from src.policies import (
    KNOWN_CATEGORIES,
    RetentionPolicy,
    describe,
    resolve_policies,
)


class TestResolvePolicies:
    def test_empty_env_produces_no_policies(self) -> None:
        """No default + no overrides → zero policies; worker should no-op."""
        assert resolve_policies({}) == []

    def test_default_only_applies_to_every_known_category(self) -> None:
        policies = resolve_policies({"AUDIT_RETENTION_DEFAULT_DAYS": "90"})
        assert len(policies) == len(KNOWN_CATEGORIES)
        assert all(p.retention_days == 90 for p in policies)
        assert {p.category for p in policies} == set(KNOWN_CATEGORIES)

    def test_category_override_wins_over_default(self) -> None:
        policies = resolve_policies(
            {
                "AUDIT_RETENTION_DEFAULT_DAYS": "90",
                "AUDIT_RETENTION_BILLING_DAYS": "1825",
            }
        )
        billing = next(p for p in policies if p.category == "billing")
        system = next(p for p in policies if p.category == "system")
        assert billing.retention_days == 1825
        assert system.retention_days == 90  # default still applies

    def test_per_category_only_skips_categories_without_override(self) -> None:
        """Without a default, ONLY explicitly configured categories get policies."""
        policies = resolve_policies(
            {
                "AUDIT_RETENTION_AUTHENTICATION_DAYS": "90",
                "AUDIT_RETENTION_SECURITY_DAYS": "365",
            }
        )
        assert len(policies) == 2
        assert {p.category for p in policies} == {"authentication", "security"}

    def test_rejects_zero_days(self) -> None:
        with pytest.raises(ValueError, match="must be > 0"):
            resolve_policies({"AUDIT_RETENTION_DEFAULT_DAYS": "0"})

    def test_rejects_negative_days(self) -> None:
        with pytest.raises(ValueError, match="must be > 0"):
            resolve_policies({"AUDIT_RETENTION_DEFAULT_DAYS": "-7"})

    def test_rejects_non_integer(self) -> None:
        with pytest.raises(ValueError, match="not an integer"):
            resolve_policies({"AUDIT_RETENTION_DEFAULT_DAYS": "forever"})

    def test_error_message_names_the_offending_variable(self) -> None:
        """Deployment debugging hinges on the env var name being in the error."""
        with pytest.raises(ValueError, match="AUDIT_RETENTION_BILLING_DAYS"):
            resolve_policies({"AUDIT_RETENTION_BILLING_DAYS": "bad"})

    def test_unknown_category_env_var_is_silently_ignored(self) -> None:
        """A typo like AUDIT_RETENTION_AUTH_DAYS (vs AUTHENTICATION) should
        NOT produce a policy. Safer to skip than to crash — the operator
        sees a misconfiguration via the resolved-policies log line."""
        policies = resolve_policies(
            {
                "AUDIT_RETENTION_AUTH_DAYS": "30",  # typo — no such category
                "AUDIT_RETENTION_AUTHENTICATION_DAYS": "90",
            }
        )
        auth = [p for p in policies if p.category == "authentication"]
        assert len(auth) == 1
        assert auth[0].retention_days == 90
        # No bogus "auth" category in the result.
        assert all(p.category in KNOWN_CATEGORIES for p in policies)


class TestRetentionPolicyDataclass:
    def test_rejects_zero_days(self) -> None:
        with pytest.raises(ValueError, match="must be > 0"):
            RetentionPolicy(category="authentication", retention_days=0)

    def test_rejects_unknown_category(self) -> None:
        with pytest.raises(ValueError, match="unknown category"):
            RetentionPolicy(category="not_a_category", retention_days=90)


class TestDescribe:
    def test_empty_policies_describes_noop(self) -> None:
        assert "no-op" in describe([])

    def test_describe_lists_every_policy(self) -> None:
        policies = [
            RetentionPolicy(category="authentication", retention_days=90),
            RetentionPolicy(category="billing", retention_days=1825),
        ]
        out = describe(policies)
        assert "authentication" in out
        assert "90" in out
        assert "billing" in out
        assert "1825" in out
