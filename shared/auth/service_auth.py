"""
Service-to-Service Authentication for SAHOOL Platform
JWT-based authentication for microservices communication
"""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
from jwt import PyJWTError

from .config import config
from .models import AuthErrors, AuthException

# SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
# Never trust algorithm from environment variables or token header
ALLOWED_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]

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
                error=type(
                    "obj", (object,), ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL
                )(),
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

        return jwt.encode(
            payload, config.get_signing_key(), algorithm=config.JWT_ALGORITHM
        )

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
                    error=type(
                        "obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN
                    )(),
                    status_code=401,
                )

            algorithm = unverified_header["alg"]

            # Reject 'none' algorithm explicitly
            if algorithm.lower() == "none":
                raise AuthException(
                    error=type(
                        "obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN
                    )(),
                    status_code=401,
                )

            # Verify algorithm is in whitelist
            if algorithm not in ALLOWED_ALGORITHMS:
                raise AuthException(
                    error=type(
                        "obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN
                    )(),
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
                    error=type(
                        "obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN
                    )(),
                    status_code=401,
                )

            # Verify required fields
            service_name = payload.get("service_name")
            target_service = payload.get("target_service")

            if not service_name or not target_service:
                raise AuthException(
                    error=type(
                        "obj", (object,), ServiceAuthErrors.INVALID_SERVICE_TOKEN
                    )(),
                    status_code=401,
                )

            # Verify service names are valid
            if (
                service_name not in ALLOWED_SERVICES
                or target_service not in ALLOWED_SERVICES
            ):
                raise AuthException(
                    error=type("obj", (object,), ServiceAuthErrors.INVALID_SERVICE)(),
                    status_code=403,
                )

            return {
                "service_name": service_name,
                "target_service": target_service,
                "jti": payload.get("jti"),
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
