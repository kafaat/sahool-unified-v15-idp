"""
Password Hashing & Validation
تشفير والتحقق من كلمات المرور
"""

import hashlib
import logging
import re
import secrets

from .config import get_auth_config

logger = logging.getLogger(__name__)

# Use bcrypt if available, fallback to PBKDF2
try:
    import bcrypt

    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt not available, using PBKDF2 for password hashing")


def hash_password(password: str) -> str:
    """
    Hash a password securely
    تشفير كلمة المرور بشكل آمن
    """
    if BCRYPT_AVAILABLE:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    else:
        # Fallback to PBKDF2
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return f"pbkdf2${salt}${hashed.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    التحقق من تطابق كلمة المرور مع التشفير
    """
    try:
        if BCRYPT_AVAILABLE and not hashed_password.startswith("pbkdf2$"):
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        else:
            # PBKDF2 format: pbkdf2$salt$hash
            parts = hashed_password.split("$")
            if len(parts) != 3 or parts[0] != "pbkdf2":
                return False
            salt = parts[1]
            stored_hash = parts[2]
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
            )
            return computed_hash.hex() == stored_hash
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength according to policy
    التحقق من قوة كلمة المرور حسب السياسة

    Returns:
        Tuple of (is_valid, error_message)
    """
    config = get_auth_config()
    errors = []

    if len(password) < config.password_min_length:
        errors.append(f"Password must be at least {config.password_min_length} characters")

    if config.password_require_uppercase and not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if config.password_require_lowercase and not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if config.password_require_digit and not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")

    if config.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")

    if errors:
        return False, "; ".join(errors)

    return True, ""


def generate_password(length: int = 16) -> str:
    """
    Generate a secure random password
    توليد كلمة مرور عشوائية آمنة
    """
    import string

    # Ensure we include required character types
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()"),
    ]

    # Fill the rest
    password.extend(secrets.choice(chars) for _ in range(length - 4))

    # Shuffle
    secrets.SystemRandom().shuffle(password)

    return "".join(password)
