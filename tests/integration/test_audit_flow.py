"""
SAHOOL Audit Flow Integration Tests
Tests the complete audit logging flow including hash chain integrity
"""

from __future__ import annotations

import json
import pytest
from datetime import datetime, timezone
from typing import Generator
from uuid import UUID, uuid4

from shared.libs.audit.hashchain import (
    build_canonical_string,
    compute_entry_hash,
    sha256_hex,
    verify_chain,
)
from shared.libs.audit.models import AuditLog
from shared.libs.audit.redact import (
    REDACTED,
    REDACTED_EMAIL,
    SENSITIVE_KEYS,
    is_sensitive_key,
    redact_dict,
    redact_value,
)
from shared.libs.audit.middleware import AuditContext


# ---------------------------------------------------------------------------
# Hash Chain Tests
# ---------------------------------------------------------------------------


class TestHashChain:
    """Test hash chain integrity"""

    def test_sha256_hex_consistent(self):
        """Same input produces same hash"""
        data = "test data"
        hash1 = sha256_hex(data)
        hash2 = sha256_hex(data)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex is 64 chars

    def test_sha256_hex_different_inputs(self):
        """Different inputs produce different hashes"""
        assert sha256_hex("data1") != sha256_hex("data2")

    def test_compute_entry_hash_with_prev(self):
        """Entry hash includes previous hash"""
        prev_hash = "abc123"
        canonical = "test|canonical|string"

        hash_with_prev = compute_entry_hash(prev_hash=prev_hash, canonical=canonical)
        hash_without_prev = compute_entry_hash(prev_hash=None, canonical=canonical)

        assert hash_with_prev != hash_without_prev

    def test_compute_entry_hash_first_entry(self):
        """First entry works with None prev_hash"""
        canonical = "test|canonical|string"
        entry_hash = compute_entry_hash(prev_hash=None, canonical=canonical)

        assert entry_hash is not None
        assert len(entry_hash) == 64

    def test_build_canonical_string_deterministic(self):
        """Canonical string is deterministic"""
        kwargs = {
            "tenant_id": "tenant-123",
            "actor_id": "actor-456",
            "actor_type": "user",
            "action": "field.create",
            "resource_type": "field",
            "resource_id": "field-789",
            "correlation_id": "corr-abc",
            "details_json": "{}",
            "created_at_iso": "2024-01-01T00:00:00+00:00",
        }

        canonical1 = build_canonical_string(**kwargs)
        canonical2 = build_canonical_string(**kwargs)

        assert canonical1 == canonical2

    def test_build_canonical_string_with_none_actor(self):
        """Canonical string handles None actor_id"""
        canonical = build_canonical_string(
            tenant_id="tenant-123",
            actor_id=None,
            actor_type="system",
            action="system.startup",
            resource_type="system",
            resource_id="system",
            correlation_id="corr-abc",
            details_json="{}",
            created_at_iso="2024-01-01T00:00:00+00:00",
        )

        assert "|system|" in canonical
        assert "||" in canonical  # Empty actor_id

    def test_verify_chain_valid(self):
        """Valid chain passes verification"""
        entries = []
        prev_hash = None

        for i in range(3):
            canonical = build_canonical_string(
                tenant_id="tenant-123",
                actor_id=f"actor-{i}",
                actor_type="user",
                action=f"action.{i}",
                resource_type="resource",
                resource_id=f"res-{i}",
                correlation_id=f"corr-{i}",
                details_json="{}",
                created_at_iso=f"2024-01-0{i+1}T00:00:00+00:00",
            )
            entry_hash = compute_entry_hash(prev_hash=prev_hash, canonical=canonical)

            entries.append({
                "tenant_id": "tenant-123",
                "actor_id": f"actor-{i}",
                "actor_type": "user",
                "action": f"action.{i}",
                "resource_type": "resource",
                "resource_id": f"res-{i}",
                "correlation_id": f"corr-{i}",
                "details_json": "{}",
                "created_at": f"2024-01-0{i+1}T00:00:00+00:00",
                "prev_hash": prev_hash,
                "entry_hash": entry_hash,
            })
            prev_hash = entry_hash

        is_valid, errors = verify_chain(iter(entries))
        assert is_valid
        assert len(errors) == 0

    def test_verify_chain_tampered(self):
        """Tampered chain fails verification"""
        entries = []
        prev_hash = None

        for i in range(3):
            canonical = build_canonical_string(
                tenant_id="tenant-123",
                actor_id=f"actor-{i}",
                actor_type="user",
                action=f"action.{i}",
                resource_type="resource",
                resource_id=f"res-{i}",
                correlation_id=f"corr-{i}",
                details_json="{}",
                created_at_iso=f"2024-01-0{i+1}T00:00:00+00:00",
            )
            entry_hash = compute_entry_hash(prev_hash=prev_hash, canonical=canonical)

            entries.append({
                "tenant_id": "tenant-123",
                "actor_id": f"actor-{i}",
                "actor_type": "user",
                "action": f"action.{i}",
                "resource_type": "resource",
                "resource_id": f"res-{i}",
                "correlation_id": f"corr-{i}",
                "details_json": "{}",
                "created_at": f"2024-01-0{i+1}T00:00:00+00:00",
                "prev_hash": prev_hash,
                "entry_hash": entry_hash,
            })
            prev_hash = entry_hash

        # Tamper with middle entry
        entries[1]["action"] = "action.TAMPERED"

        is_valid, errors = verify_chain(iter(entries))
        assert not is_valid
        assert len(errors) > 0
        assert "entry_hash mismatch" in errors[0]


# ---------------------------------------------------------------------------
# Redaction Tests
# ---------------------------------------------------------------------------


class TestRedaction:
    """Test PII redaction"""

    def test_sensitive_keys_detected(self):
        """Known sensitive keys are detected"""
        for key in ["password", "token", "secret", "api_key", "ssn"]:
            assert is_sensitive_key(key)

    def test_sensitive_keys_case_insensitive(self):
        """Key detection is case insensitive"""
        assert is_sensitive_key("PASSWORD")
        assert is_sensitive_key("Token")
        assert is_sensitive_key("API_KEY")

    def test_redact_dict_simple(self):
        """Simple dictionary redaction"""
        data = {
            "username": "john",
            "password": "secret123",
            "email": "john@example.com",
        }

        redacted = redact_dict(data)

        assert redacted["username"] == "john"
        assert redacted["password"] == REDACTED
        assert redacted["email"] == REDACTED_EMAIL

    def test_redact_dict_nested(self):
        """Nested dictionary redaction"""
        data = {
            "user": {
                "name": "john",
                "credentials": {
                    "password": "secret123",
                    "api_key": "key123",
                }
            }
        }

        redacted = redact_dict(data)

        assert redacted["user"]["name"] == "john"
        assert redacted["user"]["credentials"]["password"] == REDACTED
        assert redacted["user"]["credentials"]["api_key"] == REDACTED

    def test_redact_dict_list(self):
        """List in dictionary redaction"""
        data = {
            "users": [
                {"name": "john", "token": "tok1"},
                {"name": "jane", "token": "tok2"},
            ]
        }

        redacted = redact_dict(data)

        assert redacted["users"][0]["name"] == "john"
        assert redacted["users"][0]["token"] == REDACTED
        assert redacted["users"][1]["token"] == REDACTED

    def test_redact_dict_max_depth(self):
        """Max depth prevents infinite recursion"""
        # Create deeply nested structure
        data: dict = {"level": 0}
        current = data
        for i in range(15):
            current["nested"] = {"level": i + 1}
            current = current["nested"]

        redacted = redact_dict(data, max_depth=5)

        # Should hit max depth and return error marker
        assert "_error" in str(redacted)

    def test_redact_value_jwt(self):
        """JWT tokens are redacted"""
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        assert redact_value(jwt) == REDACTED

    def test_redact_value_email(self):
        """Email addresses are partially redacted"""
        email = "john.doe@example.com"
        assert redact_value(email) == REDACTED_EMAIL

    def test_redact_value_preserves_safe(self):
        """Safe values are preserved"""
        assert redact_value("hello") == "hello"
        assert redact_value(123) == 123
        assert redact_value(True) is True


# ---------------------------------------------------------------------------
# Audit Context Tests
# ---------------------------------------------------------------------------


class TestAuditContext:
    """Test audit context management"""

    def test_audit_context_creation(self):
        """AuditContext can be created"""
        ctx = AuditContext(
            tenant_id=uuid4(),
            actor_id=uuid4(),
            actor_type="user",
            correlation_id=uuid4(),
            ip="192.168.1.1",
            user_agent="TestAgent/1.0",
        )

        assert ctx.tenant_id is not None
        assert ctx.actor_type == "user"

    def test_audit_context_optional_fields(self):
        """Optional fields can be None"""
        ctx = AuditContext(
            tenant_id=None,
            actor_id=None,
            actor_type="system",
            correlation_id=uuid4(),
            ip=None,
            user_agent=None,
        )

        assert ctx.tenant_id is None
        assert ctx.actor_id is None
        assert ctx.ip is None


# ---------------------------------------------------------------------------
# Audit Log Model Tests
# ---------------------------------------------------------------------------


class TestAuditLogModel:
    """Test AuditLog model"""

    def test_to_dict(self):
        """to_dict produces correct output"""
        log = AuditLog(
            id=uuid4(),
            tenant_id=uuid4(),
            actor_id=uuid4(),
            actor_type="user",
            action="field.create",
            resource_type="field",
            resource_id="field-123",
            correlation_id=uuid4(),
            ip="192.168.1.1",
            user_agent="TestAgent/1.0",
            details_json="{}",
            prev_hash=None,
            entry_hash="abc123",
            created_at=datetime.now(timezone.utc),
        )

        data = log.to_dict()

        assert "id" in data
        assert "tenant_id" in data
        assert "action" in data
        assert data["action"] == "field.create"

    def test_repr(self):
        """__repr__ produces useful output"""
        log = AuditLog(
            id=uuid4(),
            tenant_id=uuid4(),
            actor_id=None,
            actor_type="system",
            action="system.startup",
            resource_type="system",
            resource_id="app",
            correlation_id=uuid4(),
            details_json="{}",
            prev_hash=None,
            entry_hash="abc123",
            created_at=datetime.now(timezone.utc),
        )

        repr_str = repr(log)

        assert "AuditLog" in repr_str
        assert "system.startup" in repr_str


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------


class TestAuditIntegration:
    """Integration tests for audit flow"""

    def test_full_audit_flow(self):
        """Test complete audit entry creation flow"""
        tenant_id = uuid4()
        actor_id = uuid4()
        correlation_id = uuid4()

        # Simulate request context
        ctx = AuditContext(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_type="user",
            correlation_id=correlation_id,
            ip="192.168.1.1",
            user_agent="TestClient/1.0",
        )

        # Create audit details
        details = {
            "field_name": "Wheat Field North",
            "area_hectares": 25.5,
            "password": "should_be_redacted",  # This should be redacted
        }

        # Redact sensitive data
        safe_details = redact_dict(details)

        assert safe_details["field_name"] == "Wheat Field North"
        assert safe_details["password"] == REDACTED

        # Build canonical string
        details_json = json.dumps(safe_details, sort_keys=True)
        created_at = datetime.now(timezone.utc).isoformat()

        canonical = build_canonical_string(
            tenant_id=str(tenant_id),
            actor_id=str(actor_id),
            actor_type="user",
            action="field.create",
            resource_type="field",
            resource_id="field-001",
            correlation_id=str(correlation_id),
            details_json=details_json,
            created_at_iso=created_at,
        )

        # Compute entry hash
        entry_hash = compute_entry_hash(prev_hash=None, canonical=canonical)

        assert len(entry_hash) == 64

    def test_chain_continuity(self):
        """Test that chain maintains continuity"""
        tenant_id = uuid4()
        prev_hash = None
        entries = []

        # Create 10 entries
        for i in range(10):
            created_at = datetime.now(timezone.utc).isoformat()
            canonical = build_canonical_string(
                tenant_id=str(tenant_id),
                actor_id=str(uuid4()),
                actor_type="user",
                action=f"test.action_{i}",
                resource_type="test",
                resource_id=f"test-{i}",
                correlation_id=str(uuid4()),
                details_json=json.dumps({"iteration": i}),
                created_at_iso=created_at,
            )

            entry_hash = compute_entry_hash(prev_hash=prev_hash, canonical=canonical)

            entries.append({
                "tenant_id": str(tenant_id),
                "actor_id": str(uuid4()),
                "actor_type": "user",
                "action": f"test.action_{i}",
                "resource_type": "test",
                "resource_id": f"test-{i}",
                "correlation_id": str(uuid4()),
                "details_json": json.dumps({"iteration": i}),
                "created_at": created_at,
                "prev_hash": prev_hash,
                "entry_hash": entry_hash,
            })

            prev_hash = entry_hash

        # Each entry should have unique hash
        hashes = [e["entry_hash"] for e in entries]
        assert len(hashes) == len(set(hashes))

        # First entry should have no prev_hash
        assert entries[0]["prev_hash"] is None

        # All others should have prev_hash
        for entry in entries[1:]:
            assert entry["prev_hash"] is not None


# ---------------------------------------------------------------------------
# Sensitive Keys Coverage Test
# ---------------------------------------------------------------------------


class TestSensitiveKeysCoverage:
    """Verify all expected sensitive keys are covered"""

    def test_authentication_keys(self):
        """Authentication-related keys are sensitive"""
        auth_keys = ["password", "token", "access_token", "refresh_token", "jwt", "bearer"]
        for key in auth_keys:
            assert key in SENSITIVE_KEYS, f"{key} should be in SENSITIVE_KEYS"

    def test_secret_keys(self):
        """Secret-related keys are sensitive"""
        secret_keys = ["secret", "api_key", "private_key", "client_secret"]
        for key in secret_keys:
            assert key in SENSITIVE_KEYS, f"{key} should be in SENSITIVE_KEYS"

    def test_pii_keys(self):
        """PII-related keys are sensitive"""
        pii_keys = ["ssn", "credit_card", "cvv"]
        for key in pii_keys:
            assert key in SENSITIVE_KEYS, f"{key} should be in SENSITIVE_KEYS"
