"""
Database Session Management
إدارة جلسات قاعدة البيانات
"""

import logging
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

# Try async imports
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

from .config import DatabaseConfig, get_database_url
from .base import Base

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_async_engine = None
_SessionLocal = None
_AsyncSessionLocal = None


def init_db(
    config: Optional[DatabaseConfig] = None,
    create_tables: bool = False,
    async_mode: bool = False,
) -> None:
    """Initialize database connection"""
    global _engine, _async_engine, _SessionLocal, _AsyncSessionLocal

    if config is None:
        config = DatabaseConfig.from_env()

    # Synchronous engine
    _engine = create_engine(
        config.get_url(async_driver=False),
        poolclass=QueuePool,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        pool_recycle=config.pool_recycle,
        echo=config.echo,
    )

    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
    )

    # Add connection event listeners for debugging
    @event.listens_for(_engine, "connect")
    def on_connect(dbapi_connection, connection_record):
        logger.debug("Database connection established")

    @event.listens_for(_engine, "checkout")
    def on_checkout(dbapi_connection, connection_record, connection_proxy):
        logger.debug("Connection checked out from pool")

    # Async engine (if available)
    if async_mode and ASYNC_AVAILABLE:
        _async_engine = create_async_engine(
            config.get_url(async_driver=True),
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle,
            echo=config.echo,
        )

        _AsyncSessionLocal = async_sessionmaker(
            bind=_async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    # Create tables if requested
    if create_tables:
        Base.metadata.create_all(bind=_engine)
        logger.info("Database tables created")

    logger.info(f"Database initialized: {config.host}:{config.port}/{config.database}")


def close_db() -> None:
    """Close database connections"""
    global _engine, _async_engine

    if _engine:
        _engine.dispose()
        logger.info("Synchronous database connection closed")

    if _async_engine:
        # Note: async engine disposal should be done in async context
        logger.info("Async database engine marked for disposal")


def get_engine():
    """Get the SQLAlchemy engine"""
    if _engine is None:
        init_db()
    return _engine


def get_session_factory():
    """Get the session factory"""
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


# Synchronous session dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    استخدم هذا في FastAPI endpoints

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    if _SessionLocal is None:
        init_db()

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async session dependency for FastAPI
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency for FastAPI

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    if not ASYNC_AVAILABLE:
        raise RuntimeError("Async SQLAlchemy not available. Install sqlalchemy[asyncio] and asyncpg")

    if _AsyncSessionLocal is None:
        init_db(async_mode=True)

    async with _AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Context managers for manual usage
@contextmanager
def DatabaseSession() -> Generator[Session, None, None]:
    """
    Context manager for database session

    Usage:
        with DatabaseSession() as db:
            items = db.query(Item).all()
    """
    if _SessionLocal is None:
        init_db()

    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def AsyncDatabaseSession() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database session

    Usage:
        async with AsyncDatabaseSession() as db:
            result = await db.execute(select(Item))
            items = result.scalars().all()
    """
    if not ASYNC_AVAILABLE:
        raise RuntimeError("Async SQLAlchemy not available")

    if _AsyncSessionLocal is None:
        init_db(async_mode=True)

    async with _AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
