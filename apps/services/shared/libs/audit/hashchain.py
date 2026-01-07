"""
SAHOOL Audit Hash Chain
Tamper-evident hash chain for audit log integrity
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator


def sha256_hex(data: str) -> str:
    """
    Compute SHA-256 hash of a string.

    Args:
        data: String to hash

    Returns:
        Hex-encoded SHA-256 hash
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_entry_hash(*, prev_hash: str | None, canonical: str) -> str:
    """
    Compute hash for an audit entry in the chain.

    The hash is computed as: SHA256(prev_hash + canonical)
    This creates a chain where modifying any entry would break
    all subsequent hashes.

    Args:
        prev_hash: Hash of the previous entry (None for first entry)
        canonical: Canonical string representation of the entry

    Returns:
        Hex-encoded SHA-256 hash
    """
    prefix = prev_hash or ""
    return sha256_hex(prefix + canonical)


def build_canonical_string(
    *,
    tenant_id: str,
    actor_id: str | None,
    actor_type: str,
    action: str,
    resource_type: str,
    resource_id: str,
    correlation_id: str,
    details_json: str,
    created_at_iso: str,
) -> str:
    """
    Build canonical string for hash computation.

    Uses a stable, deterministic format to ensure consistent hashing.

    Args:
        All audit entry fields

    Returns:
        Canonical string representation
    """
    # Pipe-delimited for simplicity; order is fixed
    return "|".join(
        [
            tenant_id,
            actor_id or "",
            actor_type,
            action,
            resource_type,
            resource_id,
            correlation_id,
            details_json,
            created_at_iso,
        ]
    )


def verify_chain(entries: Iterator[dict]) -> tuple[bool, list[str]]:
    """
    Verify the integrity of an audit log chain.

    Args:
        entries: Iterator of audit log entries (dict with required fields)

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    prev_hash = None

    for i, entry in enumerate(entries):
        stored_prev_hash = entry.get("prev_hash")
        stored_entry_hash = entry.get("entry_hash")

        # Check prev_hash matches expected
        if stored_prev_hash != prev_hash:
            errors.append(
                f"Entry {i}: prev_hash mismatch. Expected {prev_hash}, got {stored_prev_hash}"
            )

        # Recompute entry hash
        canonical = build_canonical_string(
            tenant_id=str(entry["tenant_id"]),
            actor_id=str(entry["actor_id"]) if entry.get("actor_id") else None,
            actor_type=entry["actor_type"],
            action=entry["action"],
            resource_type=entry["resource_type"],
            resource_id=entry["resource_id"],
            correlation_id=str(entry["correlation_id"]),
            details_json=entry["details_json"],
            created_at_iso=entry["created_at"],
        )
        computed_hash = compute_entry_hash(prev_hash=stored_prev_hash, canonical=canonical)

        if computed_hash != stored_entry_hash:
            errors.append(
                f"Entry {i}: entry_hash mismatch. Expected {computed_hash}, got {stored_entry_hash}"
            )

        prev_hash = stored_entry_hash

    return len(errors) == 0, errors
