# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Contracts Module | وحدة العقود
#
# API contracts and schemas for the SAHOOL platform.
# عقود ومخططات API لمنصة سهول.
# ═══════════════════════════════════════════════════════════════════════════════

"""
SAHOOL Contracts Module - وحدة العقود

This module provides API contracts, event schemas, and action definitions
for inter-service communication in the SAHOOL platform.

هذه الوحدة توفر عقود API ومخططات الأحداث وتعريفات الإجراءات
للتواصل بين الخدمات في منصة سهول.

Submodules | الوحدات الفرعية:
- actions: Action schemas for service operations | مخططات الإجراءات
- events: Event schemas for NATS messaging | مخططات أحداث NATS
"""

from shared.contracts import actions, events
from shared.contracts.actions import *
from shared.contracts.events import *

__all__ = [
    # Submodule re-exports
    "actions",
    "events",
]

__version__ = "16.0.0"
