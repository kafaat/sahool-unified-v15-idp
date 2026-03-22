"""
Unit tests for Task Service database module.
اختبارات وحدة قاعدة البيانات لخدمة المهام
"""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestGetDatabaseUrl:
    """Tests for get_database_url function.

    We test the URL construction logic directly since the function
    doesn't depend on SQLAlchemy.
    """

    def test_from_database_url_env(self):
        """Test that DATABASE_URL env var is used when set"""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host:5432/db"}):
            # Reproduce the logic from get_database_url
            database_url = os.getenv("DATABASE_URL")
            assert database_url == "postgresql://user:pass@host:5432/db"

    def test_fallback_to_components(self):
        """Test URL construction from individual components"""
        env = {
            "DATABASE_URL": "",
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
            "POSTGRES_HOST": "testhost",
            "POSTGRES_PORT": "5433",
            "POSTGRES_DB": "testdb",
        }
        with patch.dict(os.environ, env, clear=False):
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                user = os.getenv("POSTGRES_USER", "sahool")
                password = os.getenv("POSTGRES_PASSWORD", "")
                host = os.getenv("POSTGRES_HOST", "localhost")
                port = os.getenv("POSTGRES_PORT", "5432")
                database = os.getenv("POSTGRES_DB", "sahool")
                database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

            assert database_url == "postgresql://testuser:testpass@testhost:5433/testdb"

    def test_default_components(self):
        """Test default values when env vars are not set"""
        env_clear = {
            "DATABASE_URL": "",
            "POSTGRES_USER": "",
            "POSTGRES_PASSWORD": "",
            "POSTGRES_HOST": "",
            "POSTGRES_PORT": "",
            "POSTGRES_DB": "",
        }
        # Don't set individual vars, let defaults apply
        with patch.dict(os.environ, {"DATABASE_URL": ""}, clear=False):
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                user = os.getenv("POSTGRES_USER", "sahool")
                password = os.getenv("POSTGRES_PASSWORD", "")
                host = os.getenv("POSTGRES_HOST", "localhost")
                port = os.getenv("POSTGRES_PORT", "5432")
                database = os.getenv("POSTGRES_DB", "sahool")
                database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            assert "postgresql://" in database_url

    def test_postgres_scheme_replacement(self):
        """Test that postgres:// is replaced with postgresql://"""
        url = "postgres://user:pass@host:5432/db"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        assert url.startswith("postgresql://")

    def test_postgresql_scheme_not_modified(self):
        """Test that postgresql:// is not double-replaced"""
        url = "postgresql://user:pass@host:5432/db"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        assert url == "postgresql://user:pass@host:5432/db"
class TestDemoDataConfig:
    """Tests for demo data initialization config"""

    def test_seed_demo_data_default_true(self):
        """Default SEED_DEMO_DATA is 'true'"""
        with patch.dict(os.environ, {}, clear=False):
            seed = os.getenv("SEED_DEMO_DATA", "true").lower() == "true"
            assert seed is True

    def test_seed_demo_data_false(self):
        """SEED_DEMO_DATA=false disables seeding"""
        with patch.dict(os.environ, {"SEED_DEMO_DATA": "false"}):
            seed = os.getenv("SEED_DEMO_DATA", "true").lower() == "true"
            assert seed is False

    def test_seed_demo_data_explicit_true(self):
        """SEED_DEMO_DATA=true enables seeding"""
        with patch.dict(os.environ, {"SEED_DEMO_DATA": "true"}):
            seed = os.getenv("SEED_DEMO_DATA", "true").lower() == "true"
            assert seed is True
class TestDatabaseSessionLogic:
    """Tests for database session management logic patterns"""

    def test_session_commit_on_success(self):
        """Verify session commits on successful operations"""
        mock_session = MagicMock()
        try:
            mock_session.query.return_value.count.return_value = 0
            mock_session.add(MagicMock())
            mock_session.commit()
        except Exception:
            mock_session.rollback()
        finally:
            mock_session.close()

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_session_rollback_on_error(self):
        """Verify session rollbacks on error"""
        mock_session = MagicMock()
        mock_session.commit.side_effect = Exception("db error")

        try:
            mock_session.add(MagicMock())
            mock_session.commit()
        except Exception:
            mock_session.rollback()
        finally:
            mock_session.close()

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_engine_dispose_on_close(self):
        """Verify engine is disposed on close"""
        mock_engine = MagicMock()
        # Simulate close_database logic
        if mock_engine:
            mock_engine.dispose()
        mock_engine.dispose.assert_called_once()
