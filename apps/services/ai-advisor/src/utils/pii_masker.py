"""
PII Masker for Logging
إخفاء المعلومات الشخصية في السجلات
"""

import json
import re
from typing import Any


class PIIMasker:
    """Masks personally identifiable information in text and objects"""

    # PII patterns — require recognisable prefixes/structure to reduce
    # false positives from timestamps, coordinates, and numeric IDs.
    PATTERNS = {
        "email": (
            r"[a-zA-Z0-9](?:[a-zA-Z0-9._%+-]*[a-zA-Z0-9])?@[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,63}",
            "[EMAIL]",
        ),
        "phone": (
            r"(?:\+966|00966|05)\d{8,9}"  # Saudi format
            r"|(?:\+\d{1,3}[-.\s])\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",  # Intl with prefix
            "[PHONE]",
        ),
        "ip_address": (
            r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b",
            "[IP]",
        ),
        "credit_card": (r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b", "[CARD]"),
        "ssn": (r"\b(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b", "[SSN]"),
        "api_key": (
            r'(sk-[a-zA-Z0-9]{20,}|api[_-]?key["\s:=]+["\']?[a-zA-Z0-9]{20,})',
            "[API_KEY]",
        ),
        "jwt": (r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", "[JWT]"),
        "password": (r'(password|passwd|pwd)["\s:=]+["\']?[^\s"\']+', "[PASSWORD]"),
        # Arabic phone numbers (Arabic-Indic digits with Saudi prefix)
        "arabic_phone": (r"[\u0660-\u0669]{10,}", "[PHONE]"),
    }

    # Sensitive field names to mask entirely
    SENSITIVE_FIELDS = {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "auth",
        "credential",
        "private_key",
        "access_token",
        "refresh_token",
        "session_id",
        "cookie",
        "ssn",
        "credit_card",
        "card_number",
        "cvv",
        "pin",
    }

    _compiled_patterns = None

    @classmethod
    def _get_patterns(cls):
        if cls._compiled_patterns is None:
            cls._compiled_patterns = {
                name: (re.compile(pattern, re.IGNORECASE), replacement)
                for name, (pattern, replacement) in cls.PATTERNS.items()
            }
        return cls._compiled_patterns

    @classmethod
    def mask_text(cls, text: str) -> str:
        """Mask PII in text"""
        if not text or not isinstance(text, str):
            return text

        masked = text
        for _name, (pattern, replacement) in cls._get_patterns().items():
            masked = pattern.sub(replacement, masked)

        return masked

    @classmethod
    def mask_dict(cls, data: dict[str, Any], depth: int = 0) -> dict[str, Any]:
        """Recursively mask PII in dictionary"""
        if depth > 10:  # Prevent infinite recursion
            return data

        masked = {}
        for key, value in data.items():
            # Check if field name is sensitive
            if key.lower() in cls.SENSITIVE_FIELDS:
                masked[key] = "[REDACTED]"
            elif isinstance(value, str):
                masked[key] = cls.mask_text(value)
            elif isinstance(value, dict):
                masked[key] = cls.mask_dict(value, depth + 1)
            elif isinstance(value, list):
                masked[key] = [
                    (
                        cls.mask_dict(item, depth + 1)
                        if isinstance(item, dict)
                        else cls.mask_text(item)
                        if isinstance(item, str)
                        else item
                    )
                    for item in value
                ]
            else:
                masked[key] = value

        return masked

    @classmethod
    def mask_json(cls, json_str: str) -> str:
        """Mask PII in JSON string"""
        try:
            data = json.loads(json_str)
            masked = cls.mask_dict(data)
            return json.dumps(masked)
        except json.JSONDecodeError:
            return cls.mask_text(json_str)


def safe_log(data: str | dict | Any) -> str:
    """Safe logging helper that masks PII"""
    if isinstance(data, str):
        return PIIMasker.mask_text(data)
    elif isinstance(data, dict):
        return json.dumps(PIIMasker.mask_dict(data))
    else:
        return PIIMasker.mask_text(str(data))
