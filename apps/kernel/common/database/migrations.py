"""
SAHOOL Database Migration Manager
مدير هجرة قاعدة البيانات

Provides utilities for managing database migrations with Alembic.
يوفر أدوات لإدارة هجرة قاعدة البيانات باستخدام Alembic.
"""

import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text, MetaData, Table, Column
from sqlalchemy import String, DateTime, Integer, Boolean
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


@dataclass
class MigrationInfo:
    """
    معلومات الهجرة
    Migration information
    """

    revision: str
    description: str
    timestamp: datetime
    checksum: str
    is_applied: bool = False


class MigrationManager:
    """
    مدير هجرة قاعدة البيانات
    Database Migration Manager

    Handles database schema migrations using Alembic.
    يدير هجرة مخطط قاعدة البيانات باستخدام Alembic.
    """

    def __init__(
        self,
        database_url: str,
        migrations_dir: Optional[str] = None,
        alembic_ini: Optional[str] = None,
    ):
        """
        Initialize migration manager.
        تهيئة مدير الهجرة.

        Args:
            database_url: Database connection URL
            migrations_dir: Path to migrations directory
            alembic_ini: Path to alembic.ini configuration file
        """
        self.database_url = database_url
        self.engine = create_engine(database_url)

        # تحديد مسار الهجرات
        # Determine migrations path
        if migrations_dir:
            self.migrations_dir = Path(migrations_dir)
        else:
            # استخدام المسار الافتراضي
            # Use default path
            current_dir = Path(__file__).parent
            self.migrations_dir = current_dir / "migrations"

        # تحديد مسار ملف التكوين
        # Determine config file path
        if alembic_ini:
            self.alembic_ini = Path(alembic_ini)
        else:
            self.alembic_ini = self.migrations_dir.parent / "alembic.ini"

        # إنشاء كائن التكوين
        # Create config object
        self.alembic_cfg = self._create_alembic_config()

    def _create_alembic_config(self) -> Config:
        """
        إنشاء تكوين Alembic
        Create Alembic configuration
        """
        # إنشاء ملف التكوين إذا لم يكن موجودًا
        # Create config file if it doesn't exist
        if not self.alembic_ini.exists():
            self._create_alembic_ini()

        cfg = Config(str(self.alembic_ini))
        cfg.set_main_option("script_location", str(self.migrations_dir))
        cfg.set_main_option("sqlalchemy.url", self.database_url)

        return cfg

    def _create_alembic_ini(self):
        """
        إنشاء ملف alembic.ini الافتراضي
        Create default alembic.ini file
        """
        alembic_ini_content = """# SAHOOL Database Migrations - Alembic Configuration
# تكوين هجرة قاعدة البيانات

[alembic]
# مسار نصوص الهجرة
# Path to migration scripts
script_location = %(here)s/database/migrations

# قالب يُستخدم لإنشاء ملفات الهجرة
# Template used to generate migration files
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s

# المنطقة الزمنية لطوابع وقت الهجرة
# Timezone for migration timestamps
timezone = UTC

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        self.alembic_ini.parent.mkdir(parents=True, exist_ok=True)
        self.alembic_ini.write_text(alembic_ini_content)

    def _ensure_migrations_table(self):
        """
        التأكد من وجود جدول تتبع الهجرات
        Ensure migrations tracking table exists
        """
        metadata = MetaData()

        # إنشاء جدول الهجرات المخصص
        # Create custom migrations table
        migrations_table = Table(
            "sahool_migrations",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("revision", String(64), unique=True, nullable=False),
            Column("description", String(255), nullable=False),
            Column("checksum", String(64), nullable=False),
            Column("applied_at", DateTime, nullable=False),
            Column("execution_time_ms", Integer, nullable=True),
            Column("applied_by", String(100), nullable=True),
            Column("is_rollback", Boolean, default=False),
        )

        metadata.create_all(self.engine)

    def _calculate_checksum(self, migration_file: Path) -> str:
        """
        حساب checksum لملف الهجرة
        Calculate checksum for migration file

        Args:
            migration_file: Path to migration file

        Returns:
            SHA256 checksum
        """
        content = migration_file.read_text()
        return hashlib.sha256(content.encode()).hexdigest()

    def create_migration(
        self, name: str, description: str = "", autogenerate: bool = False
    ) -> str:
        """
        إنشاء هجرة جديدة
        Create a new migration

        Args:
            name: Migration name (slug)
            description: Migration description
            autogenerate: Whether to auto-generate migration from models

        Returns:
            Path to created migration file
        """
        # التأكد من وجود دليل الهجرات
        # Ensure migrations directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # إنشاء الهجرة
        # Create migration
        if autogenerate:
            command.revision(
                self.alembic_cfg, message=description or name, autogenerate=True
            )
        else:
            command.revision(
                self.alembic_cfg, message=description or name, autogenerate=False
            )

        # العثور على ملف الهجرة الذي تم إنشاؤه
        # Find the created migration file
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        head = script_dir.get_current_head()

        return f"Migration created: {head}"

    def run_migrations(self, target_version: Optional[str] = None) -> Dict[str, Any]:
        """
        تشغيل الهجرات
        Run migrations

        Args:
            target_version: Target revision to migrate to (None = latest)

        Returns:
            Migration execution results
        """
        start_time = datetime.utcnow()

        # التأكد من وجود جدول الهجرات
        # Ensure migrations table exists
        self._ensure_migrations_table()

        # تشغيل الهجرات
        # Run migrations
        if target_version:
            command.upgrade(self.alembic_cfg, target_version)
        else:
            command.upgrade(self.alembic_cfg, "head")

        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds() * 1000

        return {
            "success": True,
            "target_version": target_version or "head",
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat(),
        }

    def rollback(self, steps: int = 1) -> Dict[str, Any]:
        """
        التراجع عن الهجرات
        Rollback migrations

        Args:
            steps: Number of steps to rollback

        Returns:
            Rollback execution results
        """
        start_time = datetime.utcnow()

        # حساب الإصدار المستهدف
        # Calculate target revision
        if steps == 1:
            target = "-1"
        else:
            target = f"-{steps}"

        # تنفيذ التراجع
        # Execute rollback
        command.downgrade(self.alembic_cfg, target)

        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds() * 1000

        return {
            "success": True,
            "steps": steps,
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat(),
        }

    def get_migration_status(self) -> Dict[str, Any]:
        """
        الحصول على حالة الهجرات
        Get migration status

        Returns:
            Migration status information
        """
        # الحصول على الإصدار الحالي
        # Get current revision
        with self.engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()

        # الحصول على قائمة الهجرات
        # Get migrations list
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)

        # الحصول على جميع الهجرات المتاحة
        # Get all available migrations
        available_migrations = []
        for revision in script_dir.walk_revisions():
            available_migrations.append(
                {
                    "revision": revision.revision,
                    "description": revision.doc,
                    "down_revision": revision.down_revision,
                }
            )

        # الحصول على الهجرات المطبقة
        # Get applied migrations
        applied_migrations = []
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        "SELECT revision, description, applied_at, checksum "
                        "FROM sahool_migrations ORDER BY applied_at"
                    )
                )
                for row in result:
                    applied_migrations.append(
                        {
                            "revision": row[0],
                            "description": row[1],
                            "applied_at": row[2].isoformat() if row[2] else None,
                            "checksum": row[3],
                        }
                    )
        except Exception:
            # الجدول غير موجود بعد
            # Table doesn't exist yet
            pass

        return {
            "current_revision": current_rev,
            "total_available": len(available_migrations),
            "total_applied": len(applied_migrations),
            "pending_migrations": len(available_migrations) - len(applied_migrations),
            "available_migrations": available_migrations,
            "applied_migrations": applied_migrations,
        }

    def validate_checksums(self) -> Dict[str, Any]:
        """
        التحقق من صحة checksums للهجرات المطبقة
        Validate checksums of applied migrations

        Returns:
            Validation results
        """
        conflicts = []

        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT revision, checksum FROM sahool_migrations")
            )

            for row in result:
                revision = row[0]
                stored_checksum = row[1]

                # البحث عن ملف الهجرة
                # Find migration file
                migration_file = self._find_migration_file(revision)

                if migration_file:
                    current_checksum = self._calculate_checksum(migration_file)

                    if current_checksum != stored_checksum:
                        conflicts.append(
                            {
                                "revision": revision,
                                "stored_checksum": stored_checksum,
                                "current_checksum": current_checksum,
                            }
                        )

        return {"has_conflicts": len(conflicts) > 0, "conflicts": conflicts}

    def _find_migration_file(self, revision: str) -> Optional[Path]:
        """
        العثور على ملف الهجرة بناءً على الإصدار
        Find migration file by revision
        """
        versions_dir = self.migrations_dir / "versions"
        if not versions_dir.exists():
            return None

        for file in versions_dir.glob("*.py"):
            if file.stem.startswith(revision):
                return file

        return None

    def seed_data(self, environment: str = "development") -> Dict[str, Any]:
        """
        تعبئة البيانات الأولية
        Seed initial data

        Args:
            environment: Environment name (development, staging, production)

        Returns:
            Seeding results
        """
        from .seeds.development import DevelopmentSeeder

        seeder_map = {
            "development": DevelopmentSeeder,
        }

        seeder_class = seeder_map.get(environment)
        if not seeder_class:
            return {
                "success": False,
                "error": f"No seeder found for environment: {environment}",
            }

        seeder = seeder_class(self.engine)
        result = seeder.seed()

        return result


class PostGISMigrationHelper:
    """
    مساعد هجرة PostGIS
    PostGIS Migration Helper

    Provides utilities for PostGIS-specific migrations.
    يوفر أدوات لهجرات PostGIS المحددة.
    """

    @staticmethod
    def enable_postgis_extension(conn) -> None:
        """
        تمكين امتداد PostGIS
        Enable PostGIS extension
        """
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))
        conn.commit()

    @staticmethod
    def create_spatial_index(
        conn, table: str, column: str, index_name: Optional[str] = None
    ) -> None:
        """
        إنشاء فهرس مكاني
        Create spatial index

        Args:
            conn: Database connection
            table: Table name
            column: Geometry column name
            index_name: Custom index name (optional)
        """
        if not index_name:
            index_name = f"idx_{table}_{column}_gist"

        conn.execute(
            text(f"CREATE INDEX {index_name} ON {table} USING GIST ({column})")
        )
        conn.commit()

    @staticmethod
    def add_geography_column(
        conn, table: str, column: str, srid: int = 4326, geometry_type: str = "POINT"
    ) -> None:
        """
        إضافة عمود جغرافي
        Add geography column

        Args:
            conn: Database connection
            table: Table name
            column: Column name
            srid: Spatial Reference System ID (default: 4326 for WGS84)
            geometry_type: Geometry type (POINT, LINESTRING, POLYGON, etc.)
        """
        conn.execute(
            text(
                f"ALTER TABLE {table} ADD COLUMN {column} "
                f"GEOGRAPHY({geometry_type}, {srid})"
            )
        )
        conn.commit()

    @staticmethod
    def add_geometry_column(
        conn, table: str, column: str, srid: int = 4326, geometry_type: str = "POINT"
    ) -> None:
        """
        إضافة عمود هندسي
        Add geometry column

        Args:
            conn: Database connection
            table: Table name
            column: Column name
            srid: Spatial Reference System ID
            geometry_type: Geometry type
        """
        conn.execute(
            text(
                f"SELECT AddGeometryColumn('{table}', '{column}', "
                f"{srid}, '{geometry_type}', 2)"
            )
        )
        conn.commit()
