"""
SAHOOL Shared Database Layer
طبقة قاعدة البيانات المشتركة
"""

from .base import Base, TenantMixin, TimestampMixin
from .config import DatabaseConfig, get_database_url
from .repository import BaseRepository
from .session import (
    AsyncDatabaseSession,
    DatabaseSession,
    close_db,
    get_async_db,
    get_db,
    init_db,
)

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
