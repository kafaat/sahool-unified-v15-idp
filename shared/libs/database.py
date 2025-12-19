"""
Database Connection Pool Configuration
تكوين تجمع اتصالات قاعدة البيانات

Provides configuration for:
1. Connection pooling with SQLAlchemy
2. Retry logic with exponential backoff
3. Health checks
4. Connection lifecycle management
"""

import os
import logging
import asyncio
from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager
import time

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool, QueuePool
    from sqlalchemy import event, text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Database configuration with sensible defaults.
    تكوين قاعدة البيانات مع إعدادات افتراضية معقولة.
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_backoff_factor: float = 2.0,
    ):
        """
        Initialize database configuration.
        تهيئة تكوين قاعدة البيانات.
        
        Args:
            url: Database URL (defaults to DATABASE_URL env var)
            pool_size: Number of permanent connections
            max_overflow: Number of additional connections
            pool_timeout: Timeout for getting connection from pool
            pool_recycle: Recycle connections after this many seconds
            echo: Log all SQL statements
            max_retries: Maximum number of retry attempts
            retry_delay: Initial retry delay in seconds
            retry_backoff_factor: Backoff multiplier for retries
        """
        self.url = url or os.getenv("DATABASE_URL")
        if not self.url:
            raise ValueError("DATABASE_URL must be set")
        
        self.pool_size = int(os.getenv("DB_POOL_SIZE", pool_size))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", max_overflow))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", pool_timeout))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", pool_recycle))
        self.echo = os.getenv("DB_ECHO", str(echo)).lower() == "true"
        
        self.max_retries = int(os.getenv("DB_MAX_RETRIES", max_retries))
        self.retry_delay = float(os.getenv("DB_RETRY_DELAY_SECONDS", retry_delay))
        self.retry_backoff_factor = float(os.getenv("DB_RETRY_BACKOFF_FACTOR", retry_backoff_factor))


class DatabaseManager:
    """
    Database connection manager with pooling and retry logic.
    مدير اتصالات قاعدة البيانات مع التجميع وإعادة المحاولة.
    """
    
    def __init__(self, config: DatabaseConfig):
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required. Install with: pip install sqlalchemy[asyncio]")
        
        self.config = config
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[sessionmaker] = None
    
    def create_engine(self) -> AsyncEngine:
        """
        Create async database engine with connection pooling.
        إنشاء محرك قاعدة بيانات غير متزامن مع تجميع الاتصالات.
        
        Returns:
            AsyncEngine instance
        """
        engine = create_async_engine(
            self.config.url,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            echo=self.config.echo,
            pool_pre_ping=True,  # Enable connection health checks
        )
        
        # Register event listeners
        self._register_event_listeners(engine.sync_engine)
        
        logger.info(
            f"Database engine created: pool_size={self.config.pool_size}, "
            f"max_overflow={self.config.max_overflow}"
        )
        
        return engine
    
    def _register_event_listeners(self, engine) -> None:
        """Register SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(engine, "connect")
        def on_connect(dbapi_conn, connection_record):
            """Log new connections"""
            logger.debug("New database connection established")
        
        @event.listens_for(engine, "checkout")
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            """Log connection checkouts from pool"""
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(engine, "checkin")
        def on_checkin(dbapi_conn, connection_record):
            """Log connection returns to pool"""
            logger.debug("Connection returned to pool")
    
    async def initialize(self) -> None:
        """
        Initialize database connection.
        تهيئة اتصال قاعدة البيانات.
        """
        if self._engine is None:
            self._engine = self.create_engine()
            self._session_factory = sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # Test connection
            await self.health_check()
            
            logger.info("Database manager initialized")
    
    async def close(self) -> None:
        """
        Close database connection.
        إغلاق اتصال قاعدة البيانات.
        """
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database manager closed")
    
    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Get a database session with automatic commit/rollback.
        الحصول على جلسة قاعدة بيانات مع commit/rollback تلقائي.
        
        Usage:
            async with db_manager.session() as session:
                result = await session.execute(query)
        
        Yields:
            AsyncSession instance
        """
        if not self._session_factory:
            raise RuntimeError("Database manager not initialized")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a database operation with retry logic.
        تنفيذ عملية قاعدة بيانات مع إعادة المحاولة.
        
        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of func
            
        Raises:
            Last exception if all retries fail
        """
        delay = self.config.retry_delay
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.config.max_retries - 1:
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{self.config.max_retries}): {e}",
                        exc_info=True
                    )
                    await asyncio.sleep(delay)
                    delay *= self.config.retry_backoff_factor
                else:
                    logger.error(
                        f"Database operation failed after {self.config.max_retries} attempts: {e}",
                        exc_info=True
                    )
        
        raise last_exception
    
    async def health_check(self) -> bool:
        """
        Check database connectivity.
        التحقق من اتصال قاعدة البيانات.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with self.session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def get_pool_status(self) -> dict:
        """
        Get connection pool status.
        الحصول على حالة تجمع الاتصالات.
        
        Returns:
            Dictionary with pool statistics
        """
        if not self._engine:
            return {}
        
        pool = self._engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow(),
        }


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(config: Optional[DatabaseConfig] = None) -> DatabaseManager:
    """
    Get the global database manager instance.
    الحصول على نسخة مدير قاعدة البيانات العامة.
    
    Args:
        config: Optional configuration (used on first call)
        
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    
    if _db_manager is None:
        if config is None:
            config = DatabaseConfig()
        _db_manager = DatabaseManager(config)
    
    return _db_manager


async def init_db(config: Optional[DatabaseConfig] = None) -> DatabaseManager:
    """
    Initialize the global database manager.
    تهيئة مدير قاعدة البيانات العامة.
    
    Args:
        config: Optional configuration
        
    Returns:
        Initialized DatabaseManager instance
    """
    manager = get_db_manager(config)
    await manager.initialize()
    return manager


async def close_db() -> None:
    """
    Close the global database manager.
    إغلاق مدير قاعدة البيانات العامة.
    """
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None


# FastAPI dependency
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    FastAPI dependency for database sessions.
    تبعية FastAPI لجلسات قاعدة البيانات.
    
    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    manager = get_db_manager()
    async with manager.session() as session:
        yield session


# Lifespan integration for FastAPI
@asynccontextmanager
async def database_lifespan(app=None):
    """
    Lifespan context manager for database initialization.
    مدير سياق العمر لتهيئة قاعدة البيانات.
    
    Usage:
        app = FastAPI(lifespan=database_lifespan)
    """
    # Startup
    logger.info("Initializing database...")
    await init_db()
    
    yield
    
    # Shutdown
    logger.info("Closing database...")
    await close_db()
