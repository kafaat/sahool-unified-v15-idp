# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
LLM Orchestrator Integrations Module
وحدة تكاملات منسق نماذج اللغة الكبيرة

Integrates external tools and libraries:
- AraBERT for Arabic NLP
- Sentinel Hub for satellite NDVI
- AgML for agricultural ML datasets
- CrewAI for multi-agent orchestration
"""

from .nlp_service import NLPService
from .satellite_service import SatelliteService
from .ml_service import MLService
from .crew_service import CrewService

__all__ = [
    "NLPService",
    "SatelliteService",
    "MLService",
    "CrewService",
]
