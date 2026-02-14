"""
Copilot API Database Layer
طبقة قاعدة البيانات لـ Copilot API

PostgreSQL-based persistence for chat sessions and messages.
Uses asyncpg for async connection pooling.

Author: SAHOOL Platform Team
Updated: February 2026
"""

from .chat_store import (
    close_db,
    delete_session,
    get_session_messages,
    init_db,
    list_sessions,
    save_message,
)

__all__ = [
    "init_db",
    "close_db",
    "save_message",
    "get_session_messages",
    "list_sessions",
    "delete_session",
]
