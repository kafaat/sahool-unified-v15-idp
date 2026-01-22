"""
SAHOOL Integrations Package
===========================
حزمة تكاملات سهول

Third-party integrations for SAHOOL agricultural platform.

Available Integrations:
- wechat: WeChat messaging integration for farmer communication

Author: SAHOOL Platform Team
Updated: January 2026
"""

from . import wechat

__all__ = [
    "wechat",
]

__version__ = "1.0.0"
