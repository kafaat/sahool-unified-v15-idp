"""
Tests for billing-core database module.
Covers: Engine creation, session management, health checks, init/drop/close.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_db")


class TestDatabaseConfig:
    """Test database configuration and URL handling"""

    def test_database_url_env_override(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://user:pass@host:5432/db"}):
            # Re-import to pick up env var
            import importlib

            from src import database

            importlib.reload(database)
            assert "asyncpg" in database.DATABASE_URL

    def test_database_url_sync_to_async_conversion(self):
        """Test that postgresql:// is converted to postgresql+asyncpg://"""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host:5432/db"}):
            import importlib

            from src import database

            importlib.reload(database)
            assert database.DATABASE_URL.startswith("postgresql+asyncpg://")

    def test_database_url_psycopg2_conversion(self):
        """Test that psycopg2 driver is converted to asyncpg"""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql+psycopg2://user:pass@host:5432/db"}):
            import importlib

            from src import database

            importlib.reload(database)
            assert "asyncpg" in database.DATABASE_URL
            assert "psycopg2" not in database.DATABASE_URL

    def test_is_dev_for_test_env(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "test"}):
            import importlib

            from src import database

            importlib.reload(database)
            assert database.IS_DEV is True

    def test_is_dev_for_production_env(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "DATABASE_URL": "postgresql+asyncpg://x:y@h:5432/d"}):
            import importlib

            from src import database

            importlib.reload(database)
            assert database.IS_DEV is False

    def test_build_url_from_individual_vars(self):
        env = {
            "DATABASE_URL": "",
            "POSTGRES_HOST": "myhost",
            "POSTGRES_PORT": "5433",
            "POSTGRES_USER": "myuser",
            "POSTGRES_PASSWORD": "mypass",
            "POSTGRES_DB": "mydb",
            "ENVIRONMENT": "test",
        }
        with patch.dict(os.environ, env, clear=False):
            import importlib

            from src import database

            importlib.reload(database)
            assert "myhost" in database.DATABASE_URL
            assert "5433" in database.DATABASE_URL
            assert "myuser" in database.DATABASE_URL
            assert "mydb" in database.DATABASE_URL


class TestEngineCreation:
    """Test engine and session factory creation"""

    def test_get_engine_creates_engine(self):
        # Reset global state
        import src.database as db_mod
        from src.database import _engine

        db_mod._engine = None
        db_mod._session_factory = None

        with patch("src.database.create_async_engine") as mock_create:
            mock_create.return_value = MagicMock()
            engine = db_mod.get_engine()
            assert engine is not None
            mock_create.assert_called_once()

        # Cleanup
        db_mod._engine = None
        db_mod._session_factory = None

    def test_get_engine_returns_cached(self):
        import src.database as db_mod

        mock_engine = MagicMock()
        db_mod._engine = mock_engine
        result = db_mod.get_engine()
        assert result is mock_engine
        db_mod._engine = None

    def test_get_session_factory_creates_factory(self):
        import src.database as db_mod

        db_mod._engine = None
        db_mod._session_factory = None

        with patch("src.database.create_async_engine") as mock_create:
            mock_create.return_value = MagicMock()
            factory = db_mod.get_session_factory()
            assert factory is not None

        db_mod._engine = None
        db_mod._session_factory = None

    def test_get_session_factory_returns_cached(self):
        import src.database as db_mod

        mock_factory = MagicMock()
        db_mod._session_factory = mock_factory
        result = db_mod.get_session_factory()
        assert result is mock_factory
        db_mod._session_factory = None


class TestCloseDb:
    """Test database close/dispose"""

    @pytest.mark.asyncio
    async def test_close_db_disposes_engine(self):
        import src.database as db_mod

        mock_engine = AsyncMock()
        db_mod._engine = mock_engine
        db_mod._session_factory = MagicMock()

        await db_mod.close_db()

        mock_engine.dispose.assert_awaited_once()
        assert db_mod._engine is None
        assert db_mod._session_factory is None

    @pytest.mark.asyncio
    async def test_close_db_noop_when_no_engine(self):
        import src.database as db_mod

        db_mod._engine = None
        db_mod._session_factory = None

        # Should not raise
        await db_mod.close_db()
        assert db_mod._engine is None


class TestDbHealthCheck:
    """Test database health check"""

    @pytest.mark.asyncio
    async def test_db_health_check_healthy(self):
        import src.database as db_mod

        with patch.object(db_mod, "check_db_connection", new_callable=AsyncMock, return_value=True):
            result = await db_mod.db_health_check()
            assert result["status"] == "healthy"
            assert result["database"] == "postgresql"

    @pytest.mark.asyncio
    async def test_db_health_check_unhealthy(self):
        import src.database as db_mod

        with patch.object(db_mod, "check_db_connection", new_callable=AsyncMock, return_value=False):
            result = await db_mod.db_health_check()
            assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_db_health_check_exception(self):
        import src.database as db_mod

        with patch.object(db_mod, "check_db_connection", new_callable=AsyncMock, side_effect=Exception("conn error")):
            result = await db_mod.db_health_check()
            assert result["status"] == "unhealthy"
            assert "conn error" in result["error"]


class TestCheckDbConnection:
    """Test check_db_connection"""

    @pytest.mark.asyncio
    async def test_check_db_connection_success(self):
        import src.database as db_mod

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch.object(db_mod, "get_db_context", return_value=mock_ctx):
            result = await db_mod.check_db_connection()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_db_connection_failure(self):
        import src.database as db_mod

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("connection refused"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch.object(db_mod, "get_db_context", return_value=mock_ctx):
            result = await db_mod.check_db_connection()
            assert result is False
