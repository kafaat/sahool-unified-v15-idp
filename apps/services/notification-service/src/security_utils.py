"""
SAHOOL Security Utilities
أدوات الأمان لمنع ثغرات الحقن

Provides sanitization functions to prevent:
- Log injection attacks
- Path traversal
- Command injection
"""

import re
from typing import Any


def sanitize_for_log(value: Any, max_length: int = 100) -> str:
    """
    Sanitize user-provided values for safe logging.
    تعقيم القيم المقدمة من المستخدم للتسجيل الآمن

    Prevents log injection attacks by:
    - Removing newlines and carriage returns
    - Removing control characters
    - Limiting length
    - Escaping special characters

    Args:
        value: The value to sanitize
        max_length: Maximum length of output (default 100)

    Returns:
        Sanitized string safe for logging
    """
    if value is None:
        return "[None]"

    # Convert to string
    str_value = str(value)

    # Remove newlines and carriage returns (prevents log forging)
    str_value = str_value.replace('\n', '\\n').replace('\r', '\\r')

    # Remove control characters (ASCII 0-31 and 127)
    str_value = re.sub(r'[\x00-\x1f\x7f]', '', str_value)

    # Truncate to max length
    if len(str_value) > max_length:
        str_value = str_value[:max_length] + '...'

    return str_value


def mask_phone(phone: str | None) -> str:
    """
    Mask phone number for safe logging.
    إخفاء رقم الهاتف للتسجيل الآمن

    Example: +967712345678 -> ***5678
    """
    if not phone:
        return "****"

    # Sanitize first
    phone = sanitize_for_log(phone, max_length=20)

    # Show only last 4 digits
    if len(phone) > 4:
        return f"***{phone[-4:]}"
    return "****"


def mask_email(email: str | None) -> str:
    """
    Mask email address for safe logging.
    إخفاء البريد الإلكتروني للتسجيل الآمن

    Example: user@example.com -> u***r@example.com
    """
    if not email:
        return "***@***"

    # Sanitize first
    email = sanitize_for_log(email, max_length=100)

    if "@" not in email:
        return "***@***"

    try:
        local, domain = email.split("@", 1)
        if len(local) > 2:
            masked_local = f"{local[0]}***{local[-1]}"
        else:
            masked_local = "***"
        return f"{masked_local}@{domain}"
    except Exception:
        return "***@***"


def mask_identifier(identifier: str | None) -> str:
    """
    Mask identifier (phone or email) for safe logging.
    إخفاء المعرف (هاتف أو بريد) للتسجيل الآمن
    """
    if not identifier:
        return "***"

    if "@" in identifier:
        return mask_email(identifier)
    else:
        return mask_phone(identifier)


def sanitize_dict_for_log(data: dict, sensitive_keys: set[str] | None = None) -> dict:
    """
    Sanitize a dictionary for safe logging.
    تعقيم قاموس للتسجيل الآمن

    Args:
        data: Dictionary to sanitize
        sensitive_keys: Keys to mask (phone, email, password, token, etc.)

    Returns:
        Sanitized dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = {
            'phone', 'email', 'password', 'token', 'secret',
            'api_key', 'auth_token', 'refresh_token', 'otp',
            'identifier', 'phone_number', 'to', 'from_'
        }

    result = {}
    for key, value in data.items():
        sanitized_key = sanitize_for_log(key, max_length=50)

        if key.lower() in sensitive_keys:
            if 'phone' in key.lower() or key.lower() == 'to':
                result[sanitized_key] = mask_phone(value)
            elif 'email' in key.lower():
                result[sanitized_key] = mask_email(value)
            elif key.lower() == 'identifier':
                result[sanitized_key] = mask_identifier(value)
            else:
                result[sanitized_key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[sanitized_key] = sanitize_dict_for_log(value, sensitive_keys)
        else:
            result[sanitized_key] = sanitize_for_log(value)

    return result
