"""
SAHOOL Database Migrations
هجرة قاعدة البيانات

This package contains database migration scripts for SAHOOL.
تحتوي هذه الحزمة على نصوص هجرة قاعدة البيانات لـ SAHOOL.
"""

__version__ = "1.0.0"

# Export from parent module
# تصدير من الوحدة الأب
try:
    from ..migrations import (
        MigrationInfo,
        MigrationManager,
        PostGISMigrationHelper,
    )
    __all__ = ["MigrationManager", "MigrationInfo", "PostGISMigrationHelper"]
except ImportError:
    # Parent module not available, exports will be empty
    # الوحدة الأب غير متوفرة
    __all__ = []
