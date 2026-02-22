# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Dataset Fingerprinting - بصمة مجموعة البيانات
================================================
Deterministic SHA-256 hash of a calibration dataset for deduplication
and audit trail linkage.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def fingerprint_dataset(payload: dict[str, Any]) -> str:
    """
    Produce a deterministic SHA-256 hex digest from a JSON-serialisable payload.
    إنتاج بصمة SHA-256 حتمية من حمولة JSON.

    The payload is serialised with sorted keys and minimal whitespace
    so the same logical dataset always produces the same fingerprint.

    Args:
        payload: Dict containing at minimum::

            {
                "tenant_id": str,
                "field_id": str,
                "season_id": str,
                "model_name": str,
                "model_version": str,
                "targets": [
                    {
                        "variable": str,
                        "weight": float,
                        "min_quality_score": float,
                        "obs_refs": [dict, ...],
                    },
                    ...
                ],
            }

    Returns:
        64-char hex SHA-256 digest.
    """
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
