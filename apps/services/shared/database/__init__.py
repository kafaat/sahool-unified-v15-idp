"""
SAHOOL Shared Database Layer
طبقة قاعدة البيانات المشتركة
"""

from .config import DatabaseConfig, get_database_url
from .session import (
    get_db,
    get_async_db,
    DatabaseSession,
    AsyncDatabaseSession,
    init_db,
    close_db,
)
from .base import Base, TimestampMixin, TenantMixin
from .repository import BaseRepository

__all__ = [
    "DatabaseConfig",
    "get_database_url",
    "get_db",
    "get_async_db",
    "DatabaseSession",
    "AsyncDatabaseSession",
    "init_db",
    "close_db",
    "Base",
    "TimestampMixin",
    "TenantMixin",
    "BaseRepository",
]
