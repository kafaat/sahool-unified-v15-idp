# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Agents module for LLM Orchestrator Service.
وحدة الوكلاء لخدمة تنسيق نماذج اللغة الكبيرة.
"""

from .executor import AgentExecutor
from .quick_responses import QuickResponse, get_quick_response, is_quick_query
from .registry import AgentInfo, AgentRegistry, get_agent_registry
from .router import RoutingResult, SimpleAgentRouter, get_router
from .routing_rules import Priority, RoutingRule, get_all_rules, get_rules_for_display

__all__ = [
    # Registry
    "AgentRegistry",
    "AgentInfo",
    "get_agent_registry",
    # Executor
    "AgentExecutor",
    # Router
    "SimpleAgentRouter",
    "RoutingResult",
    "get_router",
    # Routing Rules
    "RoutingRule",
    "Priority",
    "get_all_rules",
    "get_rules_for_display",
    # Quick Responses
    "QuickResponse",
    "get_quick_response",
    "is_quick_query",
]
