"""
Security module for AI Advisor service
وحدة الأمان لخدمة المستشار الذكي
"""

from .prompt_guard import PromptGuard, guard_prompt

__all__ = ["PromptGuard", "guard_prompt"]
