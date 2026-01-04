"""
SAHOOL Audit Redaction
PII and sensitive data redaction for audit logging
"""

from __future__ import annotations

import re
from typing import Any

# Keys that should always be redacted
SENSITIVE_KEYS: set[str] = {
    # Authentication
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "jwt",
    "bearer",
    "authorization",
    # Secrets
    "secret",
    "secret_key",
    "api_key",
    "apikey",
    "private_key",
    "client_secret",
    # Personal
    "otp",
    "pin",
    "ssn",
    "social_security",
    "credit_card",
    "card_number",
    "cvv",
    "cvc",
    # Keys
    "key",
    "encryption_key",
    "signing_key",
}

# Patterns for value-based redaction
SENSITIVE_PATTERNS: list[tuple[str, re.Pattern]] = [
    # JWT tokens
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
    # Email (partial redaction)
    ("email", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
    # Phone numbers (various formats)
    ("phone", re.compile(r"\+?[0-9]{10,15}")),
]

REDACTED = "***REDACTED***"
REDACTED_EMAIL = "***@***.***"


def redact_dict(
    d: dict[str, Any], depth: int = 0, max_depth: int = 10
) -> dict[str, Any]:
    """
    Recursively redact sensitive data from a dictionary.

    This function:
    - Redacts values for known sensitive keys
    - Redacts values matching sensitive patterns
    - Recursively processes nested dictionaries and lists
    - Prevents infinite recursion with max_depth

    Args:
        d: Dictionary to redact
        depth: Current recursion depth
        max_depth: Maximum recursion depth

    Returns:
        New dictionary with sensitive values redacted
    """
    if depth >= max_depth:
        return {"_error": "max_depth_exceeded"}

    out: dict[str, Any] = {}

    for key, value in d.items():
        key_lower = key.lower()

        # Check if key is sensitive
        if key_lower in SENSITIVE_KEYS:
            out[key] = REDACTED
            continue

        # Handle nested structures
        if isinstance(value, dict):
            out[key] = redact_dict(value, depth + 1, max_depth)
        elif isinstance(value, list):
            out[key] = [
                (
                    redact_dict(item, depth + 1, max_depth)
                    if isinstance(item, dict)
                    else redact_value(item)
                )
                for item in value
            ]
        else:
            out[key] = redact_value(value)

    return out


def redact_value(value: Any) -> Any:
    """
    Redact sensitive patterns from a single value.

    Args:
        value: Value to check and potentially redact

    Returns:
        Original value or redacted version
    """
    if not isinstance(value, str):
        return value

    # Check for JWT
    if SENSITIVE_PATTERNS[0][1].match(value):
        return REDACTED

    # Partial email redaction (keep domain hint)
    email_match = SENSITIVE_PATTERNS[1][1].search(value)
    if email_match and "@" in value:
        return REDACTED_EMAIL

    return value


def redact_string(s: str) -> str:
    """
    Redact sensitive patterns from a string.

    Useful for log messages.

    Args:
        s: String to redact

    Returns:
        Redacted string
    """
    result = s

    # Redact JWTs
    result = SENSITIVE_PATTERNS[0][1].sub(REDACTED, result)

    return result


def is_sensitive_key(key: str) -> bool:
    """Check if a key name is considered sensitive"""
    return key.lower() in SENSITIVE_KEYS
