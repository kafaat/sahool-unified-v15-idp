"""
Service-to-Service Authentication for SAHOOL Platform
JWT-based authentication for microservices communication
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import UTC, datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import PyJWTError

from .config import config
from .models import AuthErrors, AuthException

logger = logging.getLogger(__name__)

# SECURITY FIX: Restrict to HS256 only — the platform's actual algorithm policy.
# Including RS* algorithms alongside HS* enables algorithm confusion attacks
# where an attacker signs with an RSA public key as an HMAC secret.
ALLOWED_ALGORITHMS = ["HS256"]

# List of services allowed to communicate with each other
ALLOWED_SERVICES = [
    "idp-service",
    "farm-service",
    "field-service",
    "crop-service",
    "weather-service",
    "advisory-service",
    "analytics-service",
    "equipment-service",
    "precision-ag-service",
    "notification-service",
    "payment-service",
    "user-service",
    "tenant-service",
    "inventory-service",
]

# Service communication matrix - defines which services can call which
# Format: {source_service: [list of allowed target services]}
SERVICE_COMMUNICATION_MATRIX = {
    "idp-service": ALLOWED_SERVICES,  # IDP can call all services
    "farm-service": [
        "field-service",
        "crop-service",
        "equipment-service",
        "user-service",
        "tenant-service",
    ],
    "field-service": [
        "crop-service",
        "weather-service",
        "precision-ag-service",
    ],
    "crop-service": [
        "weather-service",
        "advisory-service",
        "precision-ag-service",
    ],
    "weather-service": [
        "advisory-service",
        "analytics-service",
    ],
    "advisory-service": [
        "notification-service",
        "analytics-service",
    ],
    "analytics-service": [
        "notification-service",
    ],
    "equipment-service": [
        "inventory-service",
        "farm-service",
    ],
    "precision-ag-service": [
        "weather-service",
        "field-service",
        "crop-service",
    ],
    "notification-service": [],  # Notification service only receives calls
    "payment-service": [
        "user-service",
        "tenant-service",
        "notification-service",
    ],
    "user-service": [
        "tenant-service",
        "notification-service",
    ],
    "tenant-service": [
        "notification-service",
    ],
    "inventory-service": [
        "notification-service",
    ],
}


class ServiceTokenRevocationStore:
    """
    In-memory store for revoked service tokens.

    Tracks revoked service tokens by JTI (JWT ID) to prevent reuse
    after revocation. In production, consider using Redis for distributed
    revocation state.
    """

    def __init__(self):
        """Initialize the revocation store"""
        self.revoked_tokens: set[str] = set()
        self.revocation_timestamps: dict[str, datetime] = {}

    def revoke(self, jti: str) -> None:
        """
        Revoke a token by JTI.

        Args:
            jti: The JWT ID (jti claim) to revoke
        """
        self.revoked_tokens.add(jti)
        self.revocation_timestamps[jti] = datetime.now(UTC)
        logger.info(f"Service token revoked: {jti}")

    def is_revoked(self, jti: str) -> bool:
        """
        Check if a token is revoked.

        Args:
            jti: The JWT ID to check

        Returns:
            True if token is revoked, False otherwise
        """
        return jti in self.revoked_tokens

    def cleanup_expired(self, older_than: datetime) -> int:
        """
        Clean up revocation records older than specified datetime.

        Args:
            older_than: Remove revocations older than this datetime

        Returns:
            Number of revocations cleaned up
        """
        jtis_to_remove = [jti for jti, ts in self.revocation_timestamps.items() if ts < older_than]

        for jti in jtis_to_remove:
            self.revoked_tokens.discard(jti)
            del self.revocation_timestamps[jti]

        if jtis_to_remove:
            logger.info(f"Cleaned up {len(jtis_to_remove)} expired revocations")

        return len(jtis_to_remove)


class ServiceCallAuditLog:
    """
    Audit log for service-to-service calls.

    Tracks all service calls for security monitoring and debugging.
    In production, integrate with centralized logging system (ELK, Datadog, etc).
    """

    def __init__(self, max_entries: int = 10000):
        """
        Initialize audit log.

        Args:
            max_entries: Maximum entries to keep in memory
        """
        self.max_entries = max_entries
        self.log_entries: list[dict] = []

    def log_call(
        self,
        source_service: str,
        target_service: str,
        jti: str,
        success: bool,
        error_message: str | None = None,
    ) -> None:
        """
        Log a service-to-service call.

        Args:
            source_service: Name of calling service
            target_service: Name of target service
            jti: JWT ID of the token used
            success: Whether the call succeeded
            error_message: Error message if call failed
        """
        entry = {
            "timestamp": datetime.now(UTC),
            "source_service": source_service,
            "target_service": target_service,
            "jti": jti,
            "success": success,
            "error_message": error_message,
        }

        self.log_entries.append(entry)

        # Maintain max size
        if len(self.log_entries) > self.max_entries:
            self.log_entries = self.log_entries[-self.max_entries :]

        log_level = logging.INFO if success else logging.WARNING
        logger.log(
            log_level,
            f"Service call: {source_service} -> {target_service} | Status: {'success' if success else 'failed'}",
        )

    def get_logs_for_service(self, service_name: str, limit: int = 100) -> list[dict]:
        """
        Get audit logs for a specific service.

        Args:
            service_name: Service to get logs for
            limit: Maximum number of entries to return

        Returns:
            List of matching log entries
        """
        matching = [
            entry
            for entry in self.log_entries
            if entry["source_service"] == service_name or entry["target_service"] == service_name
        ]
        return matching[-limit:] if matching else []

    def get_failed_calls(self, hours: int = 1) -> list[dict]:
        """
        Get failed service calls from recent period.

        Args:
            hours: Look back this many hours

        Returns:
            List of failed call entries
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        return [entry for entry in self.log_entries if not entry["success"] and entry["timestamp"] > cutoff]


class ServiceCallRateLimiter:
    """
    Rate limiter for service-to-service calls.

    Prevents service abuse by limiting call rate per source-target pair.
    """

    def __init__(self, calls_per_minute: int = 100):
        """
        Initialize rate limiter.

        Args:
            calls_per_minute: Maximum calls per minute per source-target pair
        """
        self.calls_per_minute = calls_per_minute
        self.call_timestamps: dict[str, list[float]] = defaultdict(list)

    def _get_key(self, source: str, target: str) -> str:
        """Get rate limit key for a service pair"""
        return f"{source}::{target}"

    def is_allowed(self, source_service: str, target_service: str) -> tuple[bool, int]:
        """
        Check if a service call is allowed.

        Args:
            source_service: Calling service
            target_service: Target service

        Returns:
            Tuple of (is_allowed, remaining_calls)
        """
        import time

        key = self._get_key(source_service, target_service)
        now = time.time()
        minute_ago = now - 60

        # Remove old timestamps
        self.call_timestamps[key] = [ts for ts in self.call_timestamps[key] if ts > minute_ago]

        current_count = len(self.call_timestamps[key])
        remaining = max(0, self.calls_per_minute - current_count)

        if current_count >= self.calls_per_minute:
            logger.warning(
                f"Rate limit exceeded for {source_service} -> {target_service}: "
                f"{current_count}/{self.calls_per_minute} calls/min"
            )
            return False, 0

        self.call_timestamps[key].append(now)
        return True, remaining - 1


# Global instances
_revocation_store = ServiceTokenRevocationStore()
_audit_log = ServiceCallAuditLog()
_rate_limiter = ServiceCallRateLimiter()


class ServiceAuthErrors:
    """Service authentication specific error messages"""

    INVALID_SERVICE = {
        "en": "Invalid service name",
        "ar": "اسم الخدمة غير صالح",
        "code": "invalid_service",
    }

    UNAUTHORIZED_SERVICE_CALL = {
        "en": "Service is not authorized to call the target service",
        "ar": "الخدمة غير مصرح لها باستدعاء الخدمة المستهدفة",
        "code": "unauthorized_service_call",
    }

    INVALID_SERVICE_TOKEN = {
        "en": "Invalid service authentication token",
        "ar": "رمز مصادقة الخدمة غير صالح",
        "code": "invalid_service_token",
    }


class ServiceToken:
    """
    Service Token Manager for service-to-service authentication.

    This class handles creation and verification of JWT tokens specifically
    designed for inter-service communication in the SAHOOL platform.

    Example:
        >>> # Create a service token
        >>> token_manager = ServiceToken()
        >>> token = token_manager.create(
        ...     service_name="farm-service",
        ...     target_service="field-service"
        ... )
        >>>
        >>> # Verify a service token
        >>> payload = token_manager.verify(token)
        >>> print(payload["service_name"], payload["target_service"])
    """

    @staticmethod
    def create(
        service_name: str,
        target_service: str,
        ttl: int = 300,
        extra_claims: dict | None = None,
    ) -> str:
        """
        Create a service-to-service JWT token.

        Args:
            service_name: Name of the calling service
            target_service: Name of the target service
            ttl: Time-to-live in seconds (default: 300 seconds / 5 minutes)
            extra_claims: Additional claims to include in the token

        Returns:
            Encoded JWT token string

        Raises:
            AuthException: If service names are invalid or unauthorized

        Example:
            >>> token = ServiceToken.create(
            ...     service_name="farm-service",
            ...     target_service="field-service",
            ...     ttl=600
            ... )
        """
        # Validate service names
        if service_name not in ALLOWED_SERVICES:
            raise AuthException(
                error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE)(),
                status_code=403,
            )

        if target_service not in ALLOWED_SERVICES:
            raise AuthException(
                error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE)(),
                status_code=403,
            )

        # Check if service is allowed to call target service
        allowed_targets = SERVICE_COMMUNICATION_MATRIX.get(service_name, [])
        if target_service not in allowed_targets:
            raise AuthException(
                error=type("obj", (object,), ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL)(),
                status_code=403,
            )

        now = datetime.now(UTC)
        expire = now + timedelta(seconds=ttl)

        # Generate unique token ID
        jti = str(uuid.uuid4())

        payload = {
            "sub": service_name,  # Subject: calling service
            "service_name": service_name,
            "target_service": target_service,
            "type": "service",  # Special type for service tokens
            "exp": expire,
            "iat": now,
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
            "jti": jti,
        }

        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(payload, config.get_signing_key(), algorithm=config.JWT_ALGORITHM)

    @staticmethod
    def verify(token: str) -> dict:
        """
        Verify and decode a service JWT token.

        Args:
            token: JWT token string

        Returns:
            Dictionary with service_name and target_service

        Raises:
            AuthException: If token is invalid, expired, or not a service token

        Example:
            >>> payload = ServiceToken.verify(token)
            >>> service = payload["service_name"]
            >>> target = payload["target_service"]

        Security: Uses hardcoded algorithm whitelist to prevent algorithm confusion attacks
        """
        try:
            # SECURITY FIX: Decode header to validate algorithm before verification
            unverified_header = jwt.get_unverified_header(token)

            if not unverified_header or "alg" not in unverified_header:
                raise AuthException(
                    error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN)(),
                    status_code=401,
                )

            algorithm = unverified_header["alg"]

            # Reject 'none' algorithm explicitly
            if algorithm.lower() == "none":
                raise AuthException(
                    error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN)(),
                    status_code=401,
                )

            # Verify algorithm is in whitelist
            if algorithm not in ALLOWED_ALGORITHMS:
                raise AuthException(
                    error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN)(),
                    status_code=401,
                )

            # SECURITY FIX: Use hardcoded whitelist instead of environment variable
            payload = jwt.decode(
                token,
                config.get_verification_key(),
                algorithms=ALLOWED_ALGORITHMS,
                issuer=config.JWT_ISSUER,
                audience=config.JWT_AUDIENCE,
                options={
                    "require": ["sub", "exp", "iat", "type"],
                },
            )

            # Verify it's a service token
            if payload.get("type") != "service":
                raise AuthException(
                    error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN)(),
                    status_code=401,
                )

            # Verify required fields
            service_name = payload.get("service_name")
            target_service = payload.get("target_service")
            jti = payload.get("jti")

            if not service_name or not target_service:
                raise AuthException(
                    error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN)(),
                    status_code=401,
                )

            # Verify service names are valid
            if service_name not in ALLOWED_SERVICES or target_service not in ALLOWED_SERVICES:
                raise AuthException(
                    error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE)(),
                    status_code=403,
                )

            # Check if token is revoked
            if jti and _revocation_store.is_revoked(jti):
                logger.warning(f"Revoked service token used: {jti}")
                raise AuthException(
                    error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN)(),
                    status_code=401,
                )

            return {
                "service_name": service_name,
                "target_service": target_service,
                "jti": jti,
                "exp": datetime.fromtimestamp(payload["exp"], tz=UTC),
                "iat": datetime.fromtimestamp(payload["iat"], tz=UTC),
            }

        except jwt.ExpiredSignatureError:
            raise AuthException(AuthErrors.EXPIRED_TOKEN)
        except jwt.InvalidIssuerError:
            raise AuthException(AuthErrors.INVALID_ISSUER)
        except jwt.InvalidAudienceError:
            raise AuthException(AuthErrors.INVALID_AUDIENCE)
        except PyJWTError:
            raise AuthException(
                error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN)(),
                status_code=401,
            )


def create_service_token(
    service_name: str,
    target_service: str,
    ttl: int = 300,
    extra_claims: dict | None = None,
) -> str:
    """
    Create a service-to-service JWT token.

    Convenience function for ServiceToken.create().

    Args:
        service_name: Name of the calling service
        target_service: Name of the target service
        ttl: Time-to-live in seconds (default: 300 seconds / 5 minutes)
        extra_claims: Additional claims to include in the token

    Returns:
        Encoded JWT token string

    Raises:
        AuthException: If service names are invalid or unauthorized

    Example:
        >>> token = create_service_token(
        ...     service_name="farm-service",
        ...     target_service="field-service"
        ... )
    """
    return ServiceToken.create(
        service_name=service_name,
        target_service=target_service,
        ttl=ttl,
        extra_claims=extra_claims,
    )


def verify_service_token(token: str) -> dict:
    """
    Verify and decode a service JWT token.

    Convenience function for ServiceToken.verify().

    Args:
        token: JWT token string

    Returns:
        Dictionary with service_name and target_service

    Raises:
        AuthException: If token is invalid, expired, or not a service token

    Example:
        >>> payload = verify_service_token(token)
        >>> print(f"Service: {payload['service_name']} -> {payload['target_service']}")
    """
    return ServiceToken.verify(token)


def is_service_authorized(service_name: str, target_service: str) -> bool:
    """
    Check if a service is authorized to call another service.

    Args:
        service_name: Name of the calling service
        target_service: Name of the target service

    Returns:
        True if authorized, False otherwise

    Example:
        >>> if is_service_authorized("farm-service", "field-service"):
        ...     # Make the service call
        ...     pass
    """
    if service_name not in ALLOWED_SERVICES:
        return False

    if target_service not in ALLOWED_SERVICES:
        return False

    allowed_targets = SERVICE_COMMUNICATION_MATRIX.get(service_name, [])
    return target_service in allowed_targets


def get_allowed_targets(service_name: str) -> list[str]:
    """
    Get list of services that a given service can call.

    Args:
        service_name: Name of the service

    Returns:
        List of allowed target service names

    Example:
        >>> targets = get_allowed_targets("farm-service")
        >>> print(targets)  # ['field-service', 'crop-service', ...]
    """
    return SERVICE_COMMUNICATION_MATRIX.get(service_name, [])


# Service Token Revocation Functions


def revoke_service_token(jti: str) -> None:
    """
    Revoke a service token by JTI.

    This immediately invalidates the token, even if not yet expired.
    Useful for emergency revocation or when a service is compromised.

    Args:
        jti: The JWT ID (jti claim) to revoke

    Example:
        >>> revoke_service_token("token-jti-uuid-here")
    """
    _revocation_store.revoke(jti)


def is_service_token_revoked(jti: str) -> bool:
    """
    Check if a service token is revoked.

    Args:
        jti: The JWT ID to check

    Returns:
        True if token is revoked, False otherwise

    Example:
        >>> if is_service_token_revoked(token_jti):
        ...     print("Token has been revoked")
    """
    return _revocation_store.is_revoked(jti)


def get_revocation_store() -> ServiceTokenRevocationStore:
    """
    Get the global service token revocation store.

    Useful for manual management of revocations or integration with
    external systems (Redis, database, etc).

    Returns:
        ServiceTokenRevocationStore instance
    """
    return _revocation_store


# Service Call Audit Logging Functions


def get_audit_log() -> ServiceCallAuditLog:
    """
    Get the global service call audit log.

    Provides access to audit logs for monitoring and debugging.

    Returns:
        ServiceCallAuditLog instance

    Example:
        >>> audit_log = get_audit_log()
        >>> failed_calls = audit_log.get_failed_calls(hours=1)
        >>> print(f"Failed calls in last hour: {len(failed_calls)}")
    """
    return _audit_log


def log_service_call(
    source_service: str,
    target_service: str,
    jti: str,
    success: bool,
    error_message: str | None = None,
) -> None:
    """
    Log a service-to-service call for audit trail.

    Should be called in service middleware/interceptors to track
    all inter-service communication.

    Args:
        source_service: Name of calling service
        target_service: Name of target service
        jti: JWT ID of the token used
        success: Whether the call succeeded
        error_message: Error message if call failed

    Example:
        >>> log_service_call(
        ...     source_service="farm-service",
        ...     target_service="field-service",
        ...     jti="token-jti",
        ...     success=True
        ... )
    """
    _audit_log.log_call(source_service, target_service, jti, success, error_message)


def get_service_audit_logs(service_name: str, limit: int = 100) -> list[dict]:
    """
    Get audit logs for a specific service.

    Args:
        service_name: Service to get logs for
        limit: Maximum number of entries to return

    Returns:
        List of audit log entries

    Example:
        >>> logs = get_service_audit_logs("farm-service", limit=50)
        >>> for log in logs:
        ...     print(f"{log['timestamp']}: {log['source_service']} -> {log['target_service']}")
    """
    return _audit_log.get_logs_for_service(service_name, limit)


# Service Call Rate Limiting Functions


def get_rate_limiter() -> ServiceCallRateLimiter:
    """
    Get the global service call rate limiter.

    Provides access to rate limiting for service-to-service calls.

    Returns:
        ServiceCallRateLimiter instance
    """
    return _rate_limiter


def check_service_call_rate_limit(source_service: str, target_service: str) -> tuple[bool, int]:
    """
    Check if a service call should be rate limited.

    Args:
        source_service: Name of calling service
        target_service: Name of target service

    Returns:
        Tuple of (is_allowed, remaining_calls_in_minute)

    Example:
        >>> allowed, remaining = check_service_call_rate_limit("farm-service", "field-service")
        >>> if not allowed:
        ...     print("Rate limit exceeded")
        ... else:
        ...     print(f"Allowed. {remaining} calls remaining this minute")
    """
    return _rate_limiter.is_allowed(source_service, target_service)


def get_service_call_stats(source_service: str, target_service: str) -> dict:
    """
    Get statistics for service calls between two services.

    Args:
        source_service: Name of calling service
        target_service: Name of target service

    Returns:
        Dictionary with call statistics

    Example:
        >>> stats = get_service_call_stats("farm-service", "field-service")
        >>> print(f"Recent calls: {stats['recent_call_count']}")
    """
    key = f"{source_service}::{target_service}"
    limiter = _rate_limiter
    audit = _audit_log

    # Get recent calls from rate limiter
    recent_calls = len(limiter.call_timestamps.get(key, []))

    # Get success/failure stats from audit log
    logs = audit.get_logs_for_service(source_service, limit=1000)
    logs = [log for log in logs if log["target_service"] == target_service]

    success_count = sum(1 for log in logs if log["success"])
    failure_count = len(logs) - success_count

    return {
        "source_service": source_service,
        "target_service": target_service,
        "recent_call_count": recent_calls,
        "rate_limit": limiter.calls_per_minute,
        "recent_calls_in_last_minute": recent_calls,
        "audit_log_entries": len(logs),
        "successful_calls": success_count,
        "failed_calls": failure_count,
        "success_rate": success_count / len(logs) if logs else 0,
    }
