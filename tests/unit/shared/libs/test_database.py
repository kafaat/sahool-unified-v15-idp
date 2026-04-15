"""
Tests for shared/libs/database.py — Database utilities
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.libs.database import SQLALCHEMY_AVAILABLE

# Note: SQLALCHEMY_AVAILABLE is imported at module level and is used
# to conditionally skip tests when SQLAlchemy is not installed.


class TestDatabaseConfig:
    """Tests for DatabaseConfig configuration loading."""

    def test_config_with_explicit_url(self):
        from shared.libs.database import DatabaseConfig

        config = DatabaseConfig(url="postgresql+asyncpg://u:p@localhost/db")
        assert config.url == "postgresql+asyncpg://u:p@localhost/db"
        assert config.pool_size == 20
        assert config.max_overflow == 10
        assert config.pool_timeout == 30
        assert config.pool_recycle == 3600
        assert config.echo is False
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.retry_backoff_factor == 2.0

    def test_config_from_env_var(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://env@host/db")
        from shared.libs.database import DatabaseConfig

        config = DatabaseConfig()
        assert config.url == "postgresql+asyncpg://env@host/db"

    def test_config_raises_without_url(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        from shared.libs.database import DatabaseConfig

        with pytest.raises(ValueError, match="Database URL not configured"):
            DatabaseConfig()

    def test_config_env_overrides(self, monkeypatch):
        monkeypatch.setenv("DB_POOL_SIZE", "50")
        monkeypatch.setenv("DB_MAX_OVERFLOW", "25")
        monkeypatch.setenv("DB_POOL_TIMEOUT", "60")
        monkeypatch.setenv("DB_POOL_RECYCLE", "1800")
        monkeypatch.setenv("DB_ECHO", "true")
        monkeypatch.setenv("DB_MAX_RETRIES", "5")
        monkeypatch.setenv("DB_RETRY_DELAY_SECONDS", "2.0")
        monkeypatch.setenv("DB_RETRY_BACKOFF_FACTOR", "3.0")

        from shared.libs.database import DatabaseConfig

        config = DatabaseConfig(url="postgresql+asyncpg://u:p@h/d")
        assert config.pool_size == 50
        assert config.max_overflow == 25
        assert config.pool_timeout == 60
        assert config.pool_recycle == 1800
        assert config.echo is True
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.retry_backoff_factor == 3.0

    def test_config_echo_false_by_default(self, monkeypatch):
        monkeypatch.delenv("DB_ECHO", raising=False)
        from shared.libs.database import DatabaseConfig

        config = DatabaseConfig(url="postgresql+asyncpg://u:p@h/d")
        assert config.echo is False


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
class TestDatabaseManager:
    """Tests for DatabaseManager."""

    def _make_manager(self):
        from shared.libs.database import DatabaseConfig, DatabaseManager

        config = DatabaseConfig(url="postgresql+asyncpg://u:p@localhost/db")
        return DatabaseManager(config)

    def test_init_requires_sqlalchemy(self):
        """Test that DatabaseManager checks SQLALCHEMY_AVAILABLE."""
        import shared.libs.database as db_mod

        original = db_mod.SQLALCHEMY_AVAILABLE
        try:
            db_mod.SQLALCHEMY_AVAILABLE = False
            from shared.libs.database import DatabaseConfig

            config = DatabaseConfig(url="postgresql+asyncpg://u:p@h/d")
            with pytest.raises(ImportError, match="SQLAlchemy is required"):
                db_mod.DatabaseManager(config)
        finally:
            db_mod.SQLALCHEMY_AVAILABLE = original

    def test_session_raises_when_not_initialized(self):
        manager = self._make_manager()
        # _session_factory is None before initialize()
        assert manager._session_factory is None

    @pytest.mark.asyncio
    async def test_execute_with_retry_success_first_try(self):
        manager = self._make_manager()
        func = AsyncMock(return_value="ok")
        result = await manager.execute_with_retry(func, 1, key="val")
        assert result == "ok"
        func.assert_awaited_once_with(1, key="val")

    @pytest.mark.asyncio
    async def test_execute_with_retry_retries_on_failure(self):
        manager = self._make_manager()
        manager.config.max_retries = 3
        manager.config.retry_delay = 0.01
        manager.config.retry_backoff_factor = 1.0

        func = AsyncMock(side_effect=[ValueError("fail1"), ValueError("fail2"), "success"])
        result = await manager.execute_with_retry(func)
        assert result == "success"
        assert func.await_count == 3

    @pytest.mark.asyncio
    async def test_execute_with_retry_raises_after_exhaustion(self):
        manager = self._make_manager()
        manager.config.max_retries = 2
        manager.config.retry_delay = 0.01
        manager.config.retry_backoff_factor = 1.0

        func = AsyncMock(side_effect=RuntimeError("always fails"))
        with pytest.raises(RuntimeError, match="always fails"):
            await manager.execute_with_retry(func)
        assert func.await_count == 2

    @pytest.mark.asyncio
    async def test_close_disposes_engine(self):
        manager = self._make_manager()
        mock_engine = AsyncMock()
        manager._engine = mock_engine
        manager._session_factory = MagicMock()

        await manager.close()
        mock_engine.dispose.assert_awaited_once()
        assert manager._engine is None
        assert manager._session_factory is None

    @pytest.mark.asyncio
    async def test_close_noop_when_no_engine(self):
        manager = self._make_manager()
        await manager.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_get_pool_status_empty_when_no_engine(self):
        manager = self._make_manager()
        status = await manager.get_pool_status()
        assert status == {}


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
class TestGlobalFunctions:
    """Tests for module-level helper functions."""

    def setup_method(self):
        """Reset global state before each test."""
        import shared.libs.database as db_mod

        db_mod._db_manager = None

    def test_get_db_manager_creates_singleton(self):
        from shared.libs.database import DatabaseConfig, get_db_manager

        config = DatabaseConfig(url="postgresql+asyncpg://u:p@h/d")
        mgr1 = get_db_manager(config)
        mgr2 = get_db_manager()
        assert mgr1 is mgr2

    @pytest.mark.asyncio
    async def test_close_db_resets_global(self):
        import shared.libs.database as db_mod
        from shared.libs.database import DatabaseConfig, close_db, get_db_manager

        config = DatabaseConfig(url="postgresql+asyncpg://u:p@h/d")
        mgr = get_db_manager(config)
        # Mock the close method
        mgr.close = AsyncMock()
        await close_db()
        mgr.close.assert_awaited_once()
        assert db_mod._db_manager is None

    @pytest.mark.asyncio
    async def test_close_db_noop_when_none(self):
        from shared.libs.database import close_db

        await close_db()  # Should not raise

    @pytest.mark.asyncio
    async def test_database_lifespan(self):
        import shared.libs.database as db_mod
        from shared.libs.database import database_lifespan

        with patch.object(db_mod, "init_db", new_callable=AsyncMock) as mock_init, \
             patch.object(db_mod, "close_db", new_callable=AsyncMock) as mock_close:
            async with database_lifespan():
                mock_init.assert_awaited_once()
                mock_close.assert_not_awaited()
            mock_close.assert_awaited_once()


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
class TestDatabaseManagerExtended:
    """Extended tests for DatabaseManager session, health check, pool status."""

    def _make_manager(self):
        from shared.libs.database import DatabaseConfig, DatabaseManager

        config = DatabaseConfig(url="postgresql+asyncpg://u:p@localhost/db")
        return DatabaseManager(config)

    @pytest.mark.asyncio
    async def test_session_context_manager_commits(self):
        manager = self._make_manager()

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_factory = MagicMock(return_value=mock_session)
        manager._session_factory = mock_factory

        async with manager.session() as session:
            pass  # Simulate normal use

        mock_session.commit.assert_awaited_once()
        mock_session.rollback.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_session_context_manager_rolls_back_on_error(self):
        manager = self._make_manager()

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_factory = MagicMock(return_value=mock_session)
        manager._session_factory = mock_factory

        with pytest.raises(ValueError):
            async with manager.session() as session:
                raise ValueError("test error")

        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_session_raises_if_not_initialized(self):
        manager = self._make_manager()
        with pytest.raises(RuntimeError, match="not initialized"):
            async with manager.session():
                pass

    @pytest.mark.asyncio
    async def test_health_check_returns_false_on_error(self):
        manager = self._make_manager()

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_session.execute = AsyncMock(side_effect=RuntimeError("conn failed"))
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_factory = MagicMock(return_value=mock_session)
        manager._session_factory = mock_factory

        result = await manager.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_get_pool_status_returns_stats(self):
        manager = self._make_manager()
        mock_pool = MagicMock()
        mock_pool.size.return_value = 20
        mock_pool.checkedin.return_value = 18
        mock_pool.checkedout.return_value = 2
        mock_pool.overflow.return_value = 0

        mock_engine = MagicMock()
        mock_engine.pool = mock_pool
        manager._engine = mock_engine

        status = await manager.get_pool_status()
        assert status["size"] == 20
        assert status["checked_in"] == 18
        assert status["checked_out"] == 2
        assert status["overflow"] == 0
        assert status["total"] == 20
