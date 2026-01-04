"""
SAHOOL - Alembic Environment Configuration
تكوين بيئة Alembic
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# إضافة المسارات المطلوبة إلى sys.path
# Add required paths to sys.path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps" / "services" / "shared"))

# استيراد النماذج الأساسية
# Import base models
try:
    from apps.services.shared.database.base import Base
    from apps.services.shared.database.config import get_database_url
except ImportError:
    # محاولة بديلة
    # Fallback attempt
    from database.base import Base
    from database.config import get_database_url

# كائن تكوين Alembic
# Alembic Config object
config = context.config

# تفسير ملف التكوين لتسجيل Python
# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# تعيين عنوان URL من البيئة
# Set SQLAlchemy URL from environment
database_url = get_database_url(async_driver=False)
config.set_main_option("sqlalchemy.url", database_url)

# إضافة كائن MetaData للنماذج لدعم 'autogenerate'
# Add model's MetaData object for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    تشغيل الهجرات في وضع 'offline'.
    Run migrations in 'offline' mode.

    يقوم هذا بتكوين السياق باستخدام عنوان URL فقط
    وليس محرك، على الرغم من أن المحرك مقبول هنا أيضًا.
    من خلال تخطي إنشاء المحرك، لا نحتاج حتى إلى DBAPI متاح.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the
    Engine creation we don't even need a DBAPI to be available.

    تقوم الاستدعاءات إلى context.execute() هنا بإرسال السلسلة المعطاة إلى
    مخرجات النص البرمجي.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # دعم معاملات DDL
        # Support DDL transactions
        transaction_per_migration=True,
        # تضمين المخططات
        # Include schemas
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    تشغيل الهجرات في وضع 'online'.
    Run migrations in 'online' mode.

    في هذا السيناريو، نحتاج إلى إنشاء محرك
    وربط اتصال بالسياق.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # دعم معاملات DDL
            # Support DDL transactions
            transaction_per_migration=True,
            # تضمين المخططات
            # Include schemas
            include_schemas=True,
            # مقارنة الأنواع
            # Compare types
            compare_type=True,
            # مقارنة الفهارس
            # Compare indexes
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# تحديد وضع التشغيل
# Determine runtime mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
