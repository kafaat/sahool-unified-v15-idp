# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
API endpoints module for LLM Orchestrator Service.
وحدة نقاط النهاية API لخدمة تنسيق نماذج اللغة الكبيرة.
"""

from .orchestrator import router

__all__ = ["router"]
