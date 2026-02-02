# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Multi-Agent Orchestration Module
وحدة تنسيق الوكلاء المتعددين

Provides simple multi-agent orchestration using CrewAI.
"""

from .crewai_orchestrator import (
    CrewAIOrchestrator,
    AgentRole,
    AgriculturalCrew,
    TaskResult,
)

__all__ = [
    "CrewAIOrchestrator",
    "AgentRole",
    "AgriculturalCrew",
    "TaskResult",
]
