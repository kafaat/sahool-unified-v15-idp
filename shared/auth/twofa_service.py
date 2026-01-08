"""
Two-Factor Authentication (2FA) Service for SAHOOL Platform
خدمة المصادقة الثنائية لمنصة سهول

Provides TOTP-based 2FA functionality including:
- Secret generation
- QR code generation
- TOTP verification
- Backup code management
"""

import base64
import io
import logging
import secrets
import string

try:
    import pyotp
    import qrcode

    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    logging.warning("pyotp or qrcode not installed. Install with: pip install pyotp qrcode[pil]")

logger = logging.getLogger(__name__)

# Configuration
TOTP_ISSUER = "SAHOOL Agricultural Platform"
TOTP_ALGORITHM = "SHA1"
TOTP_DIGITS = 6
TOTP_INTERVAL = 30  # seconds
BACKUP_CODE_COUNT = 10
BACKUP_CODE_LENGTH = 8


class TwoFactorAuthService:
    """
    Two-Factor Authentication Service
    خدمة المصادقة الثنائية
    """

    def __init__(self, issuer: str = TOTP_ISSUER):
        """
        Initialize 2FA service.

        Args:
            issuer: The issuer name for TOTP (shown in authenticator apps)
        """
        if not PYOTP_AVAILABLE:
            raise ImportError(
                "pyotp and qrcode are required for 2FA. Install with: pip install pyotp qrcode[pil]"
            )
        self.issuer = issuer

    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret.

        Returns:
            Base32-encoded secret string
        """
        secret = pyotp.random_base32()
        logger.info("Generated new TOTP secret")
        return secret

    def generate_totp_uri(self, secret: str, account_name: str, issuer: str | None = None) -> str:
        """
        Generate TOTP provisioning URI for QR code.

        Args:
            secret: The TOTP secret
            account_name: Account identifier (usually email)
            issuer: Optional issuer override

        Returns:
            otpauth:// URI string
        """
        totp = pyotp.TOTP(
            secret,
            issuer=issuer or self.issuer,
            digits=TOTP_DIGITS,
            interval=TOTP_INTERVAL,
        )
        uri = totp.provisioning_uri(name=account_name, issuer_name=issuer or self.issuer)
        logger.debug(f"Generated TOTP URI for account: {account_name}")
        return uri

    def generate_qr_code(self, secret: str, account_name: str, issuer: str | None = None) -> str:
        """
        Generate QR code for TOTP setup.

        Args:
            secret: The TOTP secret
            account_name: Account identifier (usually email)
            issuer: Optional issuer override

        Returns:
            Base64-encoded PNG image data
        """
        uri = self.generate_totp_uri(secret, account_name, issuer)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_data = buffer.getvalue()
        img_base64 = base64.b64encode(img_data).decode("utf-8")

        logger.info(f"Generated QR code for account: {account_name}")
        return f"data:image/png;base64,{img_base64}"

    def verify_totp(self, secret: str, token: str, valid_window: int = 1) -> bool:
        """
        Verify a TOTP token.

        Args:
            secret: The TOTP secret
            token: The 6-digit TOTP code to verify
            valid_window: Number of intervals before/after to accept (default 1)

        Returns:
            True if token is valid
        """
        if not token or not secret:
            return False

        # Remove any whitespace from token
        token = token.strip().replace(" ", "")

        # Validate token format
        if not token.isdigit() or len(token) != TOTP_DIGITS:
            logger.warning(f"Invalid TOTP token format: {token}")
            return False

        totp = pyotp.TOTP(
            secret,
            digits=TOTP_DIGITS,
            interval=TOTP_INTERVAL,
        )

        # Verify with time window
        is_valid = totp.verify(token, valid_window=valid_window)

        if is_valid:
            logger.info("TOTP token verified successfully")
        else:
            logger.warning("TOTP token verification failed")

        return is_valid

    def generate_backup_codes(
        self, count: int = BACKUP_CODE_COUNT, length: int = BACKUP_CODE_LENGTH
    ) -> list[str]:
        """
        Generate backup codes for account recovery.

        Args:
            count: Number of backup codes to generate
            length: Length of each backup code

        Returns:
            List of backup codes
        """
        codes = []
        alphabet = string.ascii_uppercase + string.digits
        alphabet = alphabet.replace("O", "").replace("0", "")  # Remove confusing chars

        for _ in range(count):
            code = "".join(secrets.choice(alphabet) for _ in range(length))
            # Format as XXXX-XXXX for readability
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)

        logger.info(f"Generated {count} backup codes")
        return codes

    def hash_backup_code(self, code: str) -> str:
        """
        Hash a backup code for secure storage.

        Args:
            code: The backup code to hash

        Returns:
            Hashed backup code
        """
        # Remove formatting
        clean_code = code.replace("-", "").strip()

        # Use simple hash for backup codes (they're single-use anyway)
        import hashlib

        return hashlib.sha256(clean_code.encode()).hexdigest()

    def verify_backup_code(self, code: str, hashed_codes: list[str]) -> tuple[bool, str | None]:
        """
        Verify a backup code against stored hashes.

        Args:
            code: The backup code to verify
            hashed_codes: List of hashed backup codes

        Returns:
            Tuple of (is_valid, matched_hash)
        """
        if not code or not hashed_codes:
            return False, None

        # Hash the provided code
        code_hash = self.hash_backup_code(code)

        # Check if it matches any stored hash
        if code_hash in hashed_codes:
            logger.info("Backup code verified successfully")
            return True, code_hash

        logger.warning("Backup code verification failed")
        return False, None

    def get_current_totp(self, secret: str) -> str:
        """
        Get the current TOTP code (for testing purposes).

        Args:
            secret: The TOTP secret

        Returns:
            Current 6-digit TOTP code
        """
        totp = pyotp.TOTP(secret, digits=TOTP_DIGITS, interval=TOTP_INTERVAL)
        return totp.now()


# Singleton instance
_twofa_service: TwoFactorAuthService | None = None


def get_twofa_service() -> TwoFactorAuthService:
    """
    Get the global 2FA service instance.

    Returns:
        TwoFactorAuthService instance
    """
    global _twofa_service
    if _twofa_service is None:
        _twofa_service = TwoFactorAuthService()
    return _twofa_service


def set_twofa_service(service: TwoFactorAuthService) -> None:
    """
    Set the global 2FA service instance.

    Args:
        service: TwoFactorAuthService instance to use
    """
    global _twofa_service
    _twofa_service = service
    logger.info(f"2FA service set to {type(service).__name__}")
