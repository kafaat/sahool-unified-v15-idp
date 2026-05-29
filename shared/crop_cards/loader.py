# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Crop Card Loader - محمّل بطاقات المحاصيل
==========================================
Safe YAML loader with path-traversal guard and strict id regex.

Refuses to read anything outside ``cards/``; refuses crop_ids that contain
slashes, dots, or uppercase letters. Both protect against the loader being
abused as an arbitrary file read.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from shared.crop_cards.schema import CropCard


class CropCardSchemaError(ValueError):
    """Raised when a card's YAML fails schema validation or path checks."""


_SAFE_ID = re.compile(r"^[a-z0-9_]{1,32}$")
_CARDS_DIR = Path(__file__).resolve().parent / "cards"


def _safe_crop_id(crop_id: str) -> str:
    if not _SAFE_ID.match(crop_id):
        raise CropCardSchemaError(f"unsafe crop_id {crop_id!r}; must match [a-z0-9_]{{1,32}}")
    return crop_id


def load_card(crop_id: str) -> CropCard:
    """
    Load a crop card by id. Raises:
        CropCardSchemaError    – on invalid id, path traversal, or validation failure
        FileNotFoundError      – when no card exists for the (valid) id
    """
    safe = _safe_crop_id(crop_id)
    path = (_CARDS_DIR / f"{safe}.yaml").resolve()

    cards_root = _CARDS_DIR.resolve()
    if not path.is_relative_to(cards_root):
        raise CropCardSchemaError(f"path escapes cards dir: {crop_id!r}")

    if not path.exists():
        raise FileNotFoundError(f"unknown crop_id: {safe}")

    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    try:
        return CropCard.model_validate(data)
    except Exception as exc:
        raise CropCardSchemaError(f"validation failed for {safe!r}: {exc}") from exc


def list_cards() -> list[str]:
    """Return crop_ids of all available cards (excluding files starting with '_')."""
    if not _CARDS_DIR.exists():
        return []
    return sorted(p.stem for p in _CARDS_DIR.glob("*.yaml") if not p.stem.startswith("_"))


__all__ = [
    "CropCardSchemaError",
    "load_card",
    "list_cards",
]
