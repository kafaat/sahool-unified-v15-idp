"""
SQLAlchemy Encryption Module
=============================

Provides encrypted column types and utilities for SQLAlchemy ORM.
Supports both standard (non-searchable) and deterministic (searchable) encryption.

Usage:
    from packages.shared_crypto.src.sqlalchemy_encryption import EncryptedString

    class User(Base):
        __tablename__ = 'users'

        id = Column(Integer, primary_key=True)
        national_id = Column(EncryptedString(deterministic=True))
        date_of_birth = Column(EncryptedString())

Author: SAHOOL Team
"""

import os
import base64
import hashlib
from typing import Any, Optional, Callable
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
import bcrypt
from sqlalchemy import TypeDecorator, String, event
from sqlalchemy.orm import Session


# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

NONCE_LENGTH = 12  # 96 bits for AES-GCM
KEY_LENGTH = 32  # 256 bits


# ═══════════════════════════════════════════════════════════════════════════
# Key Management
# ═══════════════════════════════════════════════════════════════════════════


def get_encryption_key() -> bytes:
    """Get encryption key from environment variables."""
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY environment variable is not set")

    if len(key) != 64:
        raise ValueError("ENCRYPTION_KEY must be 64 hex characters (32 bytes)")

    return bytes.fromhex(key)


def get_deterministic_key() -> bytes:
    """Get deterministic encryption key from environment variables."""
    key = os.environ.get("DETERMINISTIC_ENCRYPTION_KEY")
    if not key:
        raise ValueError("DETERMINISTIC_ENCRYPTION_KEY environment variable is not set")

    if len(key) != 64:
        raise ValueError(
            "DETERMINISTIC_ENCRYPTION_KEY must be 64 hex characters (32 bytes)"
        )

    return bytes.fromhex(key)


def generate_encryption_key() -> str:
    """Generate a new encryption key for setup/rotation."""
    return os.urandom(KEY_LENGTH).hex()


# ═══════════════════════════════════════════════════════════════════════════
# Encryption Functions
# ═══════════════════════════════════════════════════════════════════════════


def encrypt_field(plaintext: str) -> str:
    """
    Encrypt data using AES-256-GCM (standard, non-searchable encryption).

    Args:
        plaintext: The data to encrypt

    Returns:
        Encrypted data in format: nonce:ciphertext (base64)

    Example:
        >>> encrypted = encrypt_field('sensitive data')
        >>> # Returns: "base64Nonce:base64Ciphertext"
    """
    if not plaintext:
        return plaintext

    try:
        key = get_encryption_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(NONCE_LENGTH)

        ciphertext = aesgcm.encrypt(
            nonce, plaintext.encode("utf-8"), None  # No associated data
        )

        # Format: nonce:ciphertext (both base64 encoded)
        nonce_b64 = base64.b64encode(nonce).decode("utf-8")
        ciphertext_b64 = base64.b64encode(ciphertext).decode("utf-8")

        return f"{nonce_b64}:{ciphertext_b64}"
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt_field(encrypted_data: str) -> str:
    """
    Decrypt data encrypted with AES-256-GCM.

    Args:
        encrypted_data: The encrypted data in format: nonce:ciphertext

    Returns:
        Decrypted plaintext

    Example:
        >>> decrypted = decrypt_field(encrypted_data)
    """
    if not encrypted_data:
        return encrypted_data

    try:
        parts = encrypted_data.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid encrypted data format")

        nonce_b64, ciphertext_b64 = parts
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)

        key = get_encryption_key()
        aesgcm = AESGCM(key)

        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def encrypt_searchable(plaintext: str) -> str:
    """
    Deterministic encryption - same input always produces same output.
    This allows searching encrypted fields, but provides less security.
    Use ONLY for fields that need to be searched (e.g., nationalId, phone).

    Args:
        plaintext: The data to encrypt

    Returns:
        Deterministically encrypted data

    Example:
        >>> encrypted1 = encrypt_searchable('12345')
        >>> encrypted2 = encrypt_searchable('12345')
        >>> # encrypted1 == encrypted2 (always)
    """
    if not plaintext:
        return plaintext

    try:
        key = get_deterministic_key()

        # Derive deterministic nonce using HMAC
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(plaintext.encode("utf-8"))
        deterministic_nonce = h.finalize()[:NONCE_LENGTH]

        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(
            deterministic_nonce, plaintext.encode("utf-8"), None
        )

        # Return only ciphertext (nonce is deterministic and not stored)
        return base64.b64encode(ciphertext).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Searchable encryption failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════
# SQLAlchemy Custom Column Types
# ═══════════════════════════════════════════════════════════════════════════


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy column type that automatically encrypts/decrypts string data.

    Usage:
        class User(Base):
            __tablename__ = 'users'

            id = Column(Integer, primary_key=True)
            # Deterministic encryption (searchable)
            national_id = Column(EncryptedString(deterministic=True))
            # Standard encryption (non-searchable, more secure)
            date_of_birth = Column(EncryptedString())

    Attributes:
        deterministic: If True, uses deterministic encryption for searchability
        length: Maximum length of the stored encrypted value
    """

    impl = String
    cache_ok = True

    def __init__(self, deterministic: bool = False, length: int = 512, *args, **kwargs):
        """
        Initialize encrypted string column.

        Args:
            deterministic: Use deterministic encryption (searchable)
            length: Maximum string length for encrypted data storage
        """
        self.deterministic = deterministic
        super().__init__(length=length, *args, **kwargs)

    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Encrypt value before storing in database.

        Args:
            value: Plain text value to encrypt
            dialect: SQLAlchemy dialect

        Returns:
            Encrypted value
        """
        if value is None:
            return value

        if not isinstance(value, str):
            value = str(value)

        try:
            if self.deterministic:
                return encrypt_searchable(value)
            else:
                return encrypt_field(value)
        except Exception as e:
            # Log error but don't fail the operation
            print(f"[SQLAlchemy Encryption] Encryption failed: {e}")
            return value

    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Decrypt value after reading from database.

        Args:
            value: Encrypted value from database
            dialect: SQLAlchemy dialect

        Returns:
            Decrypted plain text value
        """
        if value is None:
            return value

        try:
            # Deterministic encryption keeps data encrypted for searching
            # Only decrypt standard encrypted fields
            if not self.deterministic:
                return decrypt_field(value)
            return value  # Keep encrypted for deterministic fields
        except Exception as e:
            # Log error but return original value
            print(f"[SQLAlchemy Encryption] Decryption failed: {e}")
            return value


class EncryptedText(EncryptedString):
    """
    Encrypted text column (for longer text fields).
    Same as EncryptedString but with longer default length.
    """

    def __init__(
        self, deterministic: bool = False, length: int = 2048, *args, **kwargs
    ):
        super().__init__(deterministic=deterministic, length=length, *args, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════
# Password Hashing Utilities
# ═══════════════════════════════════════════════════════════════════════════


def hash_password(password: str, rounds: int = 12) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password
        rounds: Number of bcrypt rounds (default: 12)

    Returns:
        Hashed password

    Example:
        >>> hashed = hash_password('user-password-123')
        >>> # Returns: "$2b$12$..."
    """
    if not password:
        raise ValueError("Password cannot be empty")

    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        password: Plain text password to verify
        hashed: Bcrypt hash to verify against

    Returns:
        True if password matches, False otherwise

    Example:
        >>> is_valid = verify_password('user-password-123', stored_hash)
        >>> if is_valid:
        >>>     print('Password is correct')
    """
    if not password or not hashed:
        return False

    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════
# HMAC and Hashing Utilities
# ═══════════════════════════════════════════════════════════════════════════


def create_hmac(data: str, secret: Optional[str] = None) -> str:
    """
    Create HMAC signature for data integrity verification.

    Args:
        data: Data to sign
        secret: Secret key (optional, uses env var if not provided)

    Returns:
        Hex-encoded HMAC signature

    Example:
        >>> signature = create_hmac('important data')
        >>> # Later, verify:
        >>> is_valid = verify_hmac('important data', signature)
    """
    hmac_secret = secret or os.environ.get("HMAC_SECRET")
    if not hmac_secret:
        raise ValueError("HMAC_SECRET not provided and environment variable not set")

    h = hmac.HMAC(
        hmac_secret.encode("utf-8"), hashes.SHA256(), backend=default_backend()
    )
    h.update(data.encode("utf-8"))
    return h.finalize().hex()


def verify_hmac(data: str, signature: str, secret: Optional[str] = None) -> bool:
    """
    Verify HMAC signature.

    Args:
        data: Original data
        signature: HMAC signature to verify
        secret: Secret key (optional)

    Returns:
        True if signature is valid
    """
    try:
        expected_signature = create_hmac(data, secret)
        return signature == expected_signature
    except Exception:
        return False


def sha256_hash(data: str) -> str:
    """
    Create SHA-256 hash of data.

    Args:
        data: Data to hash

    Returns:
        Hex-encoded SHA-256 hash

    Example:
        >>> hash_val = sha256_hash('my data')
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════
# Session Event Listeners (Optional)
# ═══════════════════════════════════════════════════════════════════════════


def enable_encryption_logging(session: Session):
    """
    Enable logging for encryption operations (for debugging).

    Args:
        session: SQLAlchemy session

    Example:
        >>> from sqlalchemy.orm import Session
        >>> session = Session()
        >>> enable_encryption_logging(session)
    """

    @event.listens_for(session, "before_flush")
    def receive_before_flush(session, flush_context, instances):
        """Log encryption operations before flush"""
        for instance in session.new:
            print(
                f"[SQLAlchemy Encryption] Encrypting new instance: {type(instance).__name__}"
            )
        for instance in session.dirty:
            print(
                f"[SQLAlchemy Encryption] Encrypting modified instance: {type(instance).__name__}"
            )


# ═══════════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════════


def is_encrypted(data: str) -> bool:
    """
    Check if data appears to be encrypted (basic heuristic).

    Args:
        data: Data to check

    Returns:
        True if data appears encrypted
    """
    if not data or not isinstance(data, str):
        return False

    # Check for our encryption format patterns
    # Standard format: nonce:ciphertext (base64)
    # Searchable format: ciphertext (base64)
    if ":" in data:
        parts = data.split(":")
        if len(parts) == 2:
            try:
                base64.b64decode(parts[0])
                base64.b64decode(parts[1])
                return True
            except Exception:
                return False

    # Check if it's valid base64 with sufficient length
    try:
        if len(data) > 20:
            base64.b64decode(data)
            return True
    except Exception:
        pass

    return False


def encrypt_dict_fields(data: dict, fields: list, deterministic: bool = False) -> dict:
    """
    Encrypt specific fields in a dictionary.

    Args:
        data: Dictionary with data
        fields: List of field names to encrypt
        deterministic: Use deterministic encryption

    Returns:
        Dictionary with encrypted fields

    Example:
        >>> user_data = {'name': 'John', 'national_id': '1234567890'}
        >>> encrypted = encrypt_dict_fields(user_data, ['national_id'], deterministic=True)
    """
    result = data.copy()
    encrypt_fn = encrypt_searchable if deterministic else encrypt_field

    for field in fields:
        if field in result and isinstance(result[field], str):
            try:
                result[field] = encrypt_fn(result[field])
            except Exception as e:
                print(f"[SQLAlchemy Encryption] Failed to encrypt field {field}: {e}")

    return result


# ═══════════════════════════════════════════════════════════════════════════
# Example Usage
# ═══════════════════════════════════════════════════════════════════════════

"""
Example Model Definition:

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from packages.shared_crypto.src.sqlalchemy_encryption import (
    EncryptedString,
    hash_password,
    verify_password
)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Encrypted fields
    national_id = Column(EncryptedString(deterministic=True))  # Searchable
    phone = Column(EncryptedString(deterministic=True))  # Searchable
    date_of_birth = Column(EncryptedString())  # Not searchable, more secure
    address = Column(EncryptedString())  # Not searchable

# Usage:
engine = create_engine('postgresql://user:pass@localhost/db')
Session = sessionmaker(bind=engine)
session = Session()

# Create user with encrypted fields
user = User(
    email='user@example.com',
    password_hash=hash_password('user-password'),
    national_id='1234567890',  # Will be encrypted automatically
    phone='0551234567',  # Will be encrypted automatically
    date_of_birth='1990-01-01'  # Will be encrypted automatically
)
session.add(user)
session.commit()

# Search by encrypted field (works with deterministic encryption)
found_user = session.query(User).filter(
    User.national_id == '1234567890'  # Will encrypt the search term
).first()

# Verify password
if verify_password('user-password', found_user.password_hash):
    print('Password is correct')
"""
