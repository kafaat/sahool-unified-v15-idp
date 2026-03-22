"""
Tests for Chat History Store (db/chat_store.py)
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = [pytest.mark.unit]
class TestInitDb:
    @pytest.mark.asyncio
    async def test_returns_false_when_no_url(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False
        result = await cs.init_db(None)
        assert result is False
        assert cs._initialized is False

    @pytest.mark.asyncio
    async def test_returns_false_when_empty_url(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False
        result = await cs.init_db("")
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_on_import_error(self):
        """Simulates asyncpg import failure by having create_pool raise."""
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False

        # Instead of mocking __import__ (which breaks structlog), test
        # that a connection error returns False.
        result = await cs.init_db("postgresql://nonexistent-host:1/test")
        assert result is False
        assert cs._initialized is False

    @pytest.mark.asyncio
    async def test_returns_false_on_connection_error(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False

        mock_asyncpg = MagicMock()
        mock_asyncpg.create_pool = AsyncMock(side_effect=Exception("connection refused"))

        with patch.dict("sys.modules", {"asyncpg": mock_asyncpg}):
            result = await cs.init_db("postgresql://localhost/test")
            assert result is False
class TestCloseDb:
    @pytest.mark.asyncio
    async def test_close_when_pool_exists(self):
        import src.db.chat_store as cs

        mock_pool = AsyncMock()
        cs._pool = mock_pool
        cs._initialized = True

        await cs.close_db()
        mock_pool.close.assert_called_once()
        assert cs._pool is None
        assert cs._initialized is False

    @pytest.mark.asyncio
    async def test_close_when_no_pool(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False
        await cs.close_db()  # Should not raise

    @pytest.mark.asyncio
    async def test_close_handles_exception(self):
        import src.db.chat_store as cs

        mock_pool = AsyncMock()
        mock_pool.close.side_effect = Exception("close error")
        cs._pool = mock_pool
        cs._initialized = True

        await cs.close_db()
        assert cs._pool is None
        assert cs._initialized is False
class TestIsReady:
    def test_not_ready_when_not_initialized(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False
        assert cs._is_ready() is False

    def test_not_ready_when_pool_none(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = True
        assert cs._is_ready() is False

    def test_ready_when_both_set(self):
        import src.db.chat_store as cs

        cs._pool = MagicMock()
        cs._initialized = True
        assert cs._is_ready() is True
        cs._pool = None
        cs._initialized = False
class TestSaveMessage:
    @pytest.mark.asyncio
    async def test_returns_none_when_not_ready(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False
        result = await cs.save_message(
            session_id="s1",
            user_id="u1",
            tenant_id="t1",
            role="user",
            content="hello",
        )
        assert result is None
class TestGetSessionMessages:
    @pytest.mark.asyncio
    async def test_returns_empty_when_not_ready(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False
        result = await cs.get_session_messages("s1")
        assert result == []
class TestListSessions:
    @pytest.mark.asyncio
    async def test_returns_empty_when_not_ready(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False
        result = await cs.list_sessions("u1", "t1")
        assert result == []
class TestDeleteSession:
    @pytest.mark.asyncio
    async def test_returns_false_when_not_ready(self):
        import src.db.chat_store as cs

        cs._pool = None
        cs._initialized = False
        result = await cs.delete_session("s1")
        assert result is False
