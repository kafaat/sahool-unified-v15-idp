"""
SAHOOL Alert Service - Comprehensive Database Tests
Tests for database configuration, get_db generator, init_db, drop_all_tables,
check_db_connection, and SessionLocal behavior.
"""

from unittest.mock import MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# check_db_connection Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestCheckDbConnection:
    """Tests for check_db_connection function."""

    def test_returns_false_when_session_local_is_none(self):
        with patch("src.database.SessionLocal", None):
            from src.database import check_db_connection

            result = check_db_connection()
            assert result is False

    def test_returns_true_on_successful_query(self):
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)

        with patch("src.database.SessionLocal", mock_session_factory):
            from src.database import check_db_connection

            result = check_db_connection()
            assert result is True
            mock_session.execute.assert_called_once()
            mock_session.close.assert_called_once()

    def test_returns_false_on_exception(self):
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("Connection refused")
        mock_session_factory = MagicMock(return_value=mock_session)

        with patch("src.database.SessionLocal", mock_session_factory):
            from src.database import check_db_connection

            result = check_db_connection()
            assert result is False
# ═══════════════════════════════════════════════════════════════════════════════
# get_db Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestGetDb:
    """Tests for get_db generator function."""

    def test_raises_when_session_local_is_none(self):
        with patch("src.database.SessionLocal", None):
            from src.database import get_db

            with pytest.raises(RuntimeError, match="Database not configured"):
                gen = get_db()
                next(gen)

    def test_yields_session_and_commits(self):
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)

        with patch("src.database.SessionLocal", mock_session_factory):
            from src.database import get_db

            gen = get_db()
            session = next(gen)
            assert session is mock_session

            # Simulate normal exit
            try:
                next(gen)
            except StopIteration:
                pass

            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    def test_rollbacks_on_exception(self):
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)

        with patch("src.database.SessionLocal", mock_session_factory):
            from src.database import get_db

            gen = get_db()
            session = next(gen)
            assert session is mock_session

            # Simulate exception
            with pytest.raises(ValueError):
                gen.throw(ValueError("test error"))

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
# ═══════════════════════════════════════════════════════════════════════════════
# init_db Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestInitDb:
    """Tests for init_db function."""

    def test_raises_when_engine_is_none(self):
        with patch("src.database.engine", None):
            from src.database import init_db

            with pytest.raises(RuntimeError, match="Database not configured"):
                init_db()

    def test_calls_create_all(self):
        mock_engine = MagicMock()

        with patch("src.database.engine", mock_engine):
            with patch("src.database.Base") as mock_base:
                from src.database import init_db

                init_db()
                mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)
# ═══════════════════════════════════════════════════════════════════════════════
# drop_all_tables Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestDropAllTables:
    """Tests for drop_all_tables function."""

    def test_raises_when_engine_is_none(self):
        with patch("src.database.engine", None):
            from src.database import drop_all_tables

            with pytest.raises(RuntimeError, match="Database not configured"):
                drop_all_tables()

    def test_calls_drop_all(self):
        mock_engine = MagicMock()

        with patch("src.database.engine", mock_engine):
            with patch("src.database.Base") as mock_base:
                from src.database import drop_all_tables

                drop_all_tables()
                mock_base.metadata.drop_all.assert_called_once_with(bind=mock_engine)
# ═══════════════════════════════════════════════════════════════════════════════
# Module-level Configuration Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestDatabaseModuleConfig:
    """Tests for module-level database configuration."""

    def test_database_url_from_env(self):
        from src.database import DATABASE_URL

        # In test environment, DATABASE_URL is likely empty
        assert isinstance(DATABASE_URL, str)

    def test_environment_detection(self):
        from src.database import ENVIRONMENT, IS_CI_OR_TEST

        assert isinstance(ENVIRONMENT, str)
        assert isinstance(IS_CI_OR_TEST, bool)

    def test_allow_dev_defaults(self):
        from src.database import ALLOW_DEV_DEFAULTS

        assert isinstance(ALLOW_DEV_DEFAULTS, bool)
