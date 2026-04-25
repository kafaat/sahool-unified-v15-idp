# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Value objects for the compliance plug-in interface. Skeleton — see ADR-016."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ComplianceOp(StrEnum):
    """Operations that compliance plug-ins gate."""

    EXPORT_PII = "EXPORT_PII"
    CROSS_REGION_TRANSFER = "CROSS_REGION_TRANSFER"
    STORE_PII = "STORE_PII"
    SHARE_WITH_THIRD_PARTY = "SHARE_WITH_THIRD_PARTY"
    USE_FOR_TRAINING = "USE_FOR_TRAINING"


class DataClass(StrEnum):
    """Data classification tier (aligns with ``docs/security/data-classification``)."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class PIIField(StrEnum):
    """PII field types subject to per-region rules."""

    EMAIL = "EMAIL"
    PHONE = "PHONE"
    NATIONAL_ID = "NATIONAL_ID"
    GEO_PRECISE = "GEO_PRECISE"  # < 100 m precision
    BIOMETRIC = "BIOMETRIC"


class SignatureAlgo(StrEnum):
    """Cryptographic signature algorithms (FIPS-mode restricts this set)."""

    RSA_PSS_SHA256 = "RSA_PSS_SHA256"
    ECDSA_P256_SHA256 = "ECDSA_P256_SHA256"
    ED25519 = "ED25519"


@dataclass(frozen=True)
class TenantContext:
    """Resolved tenant context (from JWT ``tid`` claim)."""

    tenant_id: str
    region: str  # ISO 3166-1 alpha-2 or "GLOBAL"
    compliance_profile: str  # "default" | "fips" | "nesa" | "gdpr"


@dataclass(frozen=True)
class Decision:
    """Plug-in's verdict on a single operation request."""

    allowed: bool
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EncryptionPolicy:
    """Required encryption posture (at-rest and in-transit)."""

    at_rest_algo: str  # e.g. "AES-256-GCM"
    in_transit_min_tls: str  # e.g. "TLS1.3"
    require_kms: bool = True
    require_hsm: bool = False  # FIPS sets this True


@dataclass(frozen=True)
class RetentionPolicy:
    """How long data must be retained / when it must be purged."""

    min_days: int
    max_days: int | None  # None == "no upper bound"
    purge_method: str = "crypto-shred"


@dataclass(frozen=True)
class PIIPolicy:
    """PII handling rules for a single field."""

    redact_in_logs: bool
    pseudonymize_in_analytics: bool
    require_consent: bool
