"""
SAHOOL TLS Utilities
Shared mTLS configuration for service-to-service communication
"""

from __future__ import annotations

import ssl
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class TlsConfig:
    """
    TLS configuration for mTLS connections.

    All services should use the same CA certificate to establish trust.
    Each service has its own client certificate and key.
    """

    ca_cert: Path
    client_cert: Path
    client_key: Path

    def validate(self) -> None:
        """Validate that all certificate files exist"""
        if not self.ca_cert.exists():
            raise FileNotFoundError(f"CA certificate not found: {self.ca_cert}")
        if not self.client_cert.exists():
            raise FileNotFoundError(f"Client certificate not found: {self.client_cert}")
        if not self.client_key.exists():
            raise FileNotFoundError(f"Client key not found: {self.client_key}")


def build_mtls_ssl_context(
    cfg: TlsConfig,
    verify_hostname: bool = False,
) -> ssl.SSLContext:
    """
    Build a shared mTLS client SSLContext.

    Use this for all service-to-service HTTP clients to ensure
    consistent mTLS implementation across the platform.

    Args:
        cfg: TLS configuration with paths to certificates
        verify_hostname: Whether to verify hostname (internal SANs may vary)

    Returns:
        ssl.SSLContext configured for mTLS

    Example:
        ```python
        import httpx
        from shared.libs.security.tls import TlsConfig, build_mtls_ssl_context

        cfg = TlsConfig(
            ca_cert=Path("infra/pki/ca.crt"),
            client_cert=Path("infra/pki/kernel/tls.crt"),
            client_key=Path("infra/pki/kernel/tls.key"),
        )
        ssl_ctx = build_mtls_ssl_context(cfg)
        client = httpx.Client(verify=ssl_ctx)
        ```
    """
    cfg.validate()

    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.check_hostname = verify_hostname

    # Load CA certificate for verifying server
    ctx.load_verify_locations(cafile=str(cfg.ca_cert))

    # Load client certificate and key for client authentication
    ctx.load_cert_chain(
        certfile=str(cfg.client_cert),
        keyfile=str(cfg.client_key),
    )

    return ctx


def build_server_ssl_context(
    cert_path: Path,
    key_path: Path,
    ca_cert_path: Optional[Path] = None,
    require_client_cert: bool = True,
) -> ssl.SSLContext:
    """
    Build SSL context for server-side mTLS.

    Use this for services that need to verify client certificates.

    Args:
        cert_path: Path to server certificate
        key_path: Path to server private key
        ca_cert_path: Path to CA certificate for client verification
        require_client_cert: Whether to require client certificate

    Returns:
        ssl.SSLContext configured for server-side mTLS
    """
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # Load server certificate
    ctx.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

    if require_client_cert and ca_cert_path:
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(cafile=str(ca_cert_path))
    else:
        ctx.verify_mode = ssl.CERT_OPTIONAL

    return ctx


def get_default_tls_config(service_name: str) -> TlsConfig:
    """
    Get default TLS configuration for a service.

    Uses standard paths under infra/pki/.

    Args:
        service_name: Name of the service (e.g., 'kernel', 'field_suite')

    Returns:
        TlsConfig with standard paths
    """
    base = Path("infra/pki")
    return TlsConfig(
        ca_cert=base / "ca.crt",
        client_cert=base / service_name / "tls.crt",
        client_key=base / service_name / "tls.key",
    )
