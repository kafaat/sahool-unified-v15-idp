# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Crop Cards - بطاقات المحاصيل المحايدة
=======================================
Location-neutral crop parameter cards. Physics + thresholds only — never
region/farm/yield_history/calibration. The Decision Kernel uses these as
the canonical, portable parameter source.

Schema is locked (``extra="forbid"``) so any non-physical field (e.g.
``region:``) fails validation immediately — neutrality is mechanical, not
voluntary.
"""

from shared.crop_cards.loader import (
    CropCardSchemaError,
    list_cards,
    load_card,
)
from shared.crop_cards.schema import CropCard

__all__ = [
    "CropCard",
    "load_card",
    "list_cards",
    "CropCardSchemaError",
]
