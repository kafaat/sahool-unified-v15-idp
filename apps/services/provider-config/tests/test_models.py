"""
Tests for provider-config models.py
اختبارات نماذج تكوين المزودين
"""

import os
import sys
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestProviderConfigModel:
    """Tests for the ProviderConfig SQLAlchemy model"""

    def _make_config(self, **overrides):
        """Helper to create a mock ProviderConfig with to_dict from the real class"""
        from src.models import ProviderConfig

        defaults = {
            "id": uuid.uuid4(),
            "tenant_id": "tenant-001",
            "provider_type": "map",
            "provider_name": "openstreetmap",
            "api_key": None,
            "api_secret": None,
            "priority": "primary",
            "enabled": True,
            "config_data": None,
            "created_at": datetime(2025, 1, 15, 10, 0, 0),
            "updated_at": datetime(2025, 1, 15, 10, 0, 0),
            "created_by": "admin",
            "updated_by": None,
            "version": 1,
        }
        defaults.update(overrides)
        mock = MagicMock(spec=ProviderConfig)
        for k, v in defaults.items():
            setattr(mock, k, v)
        # Bind the real to_dict method
        mock.to_dict = lambda: ProviderConfig.to_dict(mock)
        return mock

    def test_to_dict_basic(self):
        """Test basic to_dict conversion"""
        config = self._make_config()
        result = config.to_dict()

        assert result["tenant_id"] == "tenant-001"
        assert result["provider_type"] == "map"
        assert result["provider_name"] == "openstreetmap"
        assert result["priority"] == "primary"
        assert result["enabled"] is True
        assert result["version"] == 1
        assert result["has_api_key"] is False
        assert result["config_data"] == {}

    def test_to_dict_with_api_key(self):
        """Test to_dict shows has_api_key=True when api_key is set"""
        config = self._make_config(api_key="secret-key-123")
        result = config.to_dict()

        assert result["has_api_key"] is True
        # Should NOT expose actual key
        assert "secret-key-123" not in str(result)

    def test_to_dict_with_config_data(self):
        """Test to_dict includes config_data when present"""
        config = self._make_config(config_data={"max_zoom": 19, "supports_offline": True})
        result = config.to_dict()

        assert result["config_data"] == {"max_zoom": 19, "supports_offline": True}

    def test_to_dict_none_config_data_becomes_empty_dict(self):
        """Test that None config_data is returned as empty dict"""
        config = self._make_config(config_data=None)
        result = config.to_dict()
        assert result["config_data"] == {}

    def test_to_dict_id_is_string(self):
        """Test that id is serialized as string"""
        test_id = uuid.uuid4()
        config = self._make_config(id=test_id)
        result = config.to_dict()
        assert result["id"] == str(test_id)

    def test_to_dict_created_at_isoformat(self):
        """Test timestamps are ISO formatted"""
        config = self._make_config(created_at=datetime(2025, 6, 15, 12, 30, 0))
        result = config.to_dict()
        assert result["created_at"] == "2025-06-15T12:30:00"

    def test_to_dict_none_timestamps(self):
        """Test that None timestamps return None"""
        config = self._make_config(created_at=None, updated_at=None)
        result = config.to_dict()
        assert result["created_at"] is None
        assert result["updated_at"] is None

    def test_tablename(self):
        """Test table name is correct"""
        from src.models import ProviderConfig

        assert ProviderConfig.__tablename__ == "provider_configs"

    def test_table_has_indexes(self):
        """Test that table_args contains expected indexes"""
        from src.models import ProviderConfig

        index_names = {idx.name for idx in ProviderConfig.__table_args__ if hasattr(idx, "name")}
        assert "idx_tenant_provider_type" in index_names
        assert "idx_tenant_provider_name" in index_names
        assert "idx_tenant_type_enabled" in index_names
        assert "idx_tenant_type_priority" in index_names


class TestConfigVersionModel:
    """Tests for the ConfigVersion SQLAlchemy model"""

    def _make_version(self, **overrides):
        """Helper to create a mock ConfigVersion with to_dict from the real class"""
        from src.models import ConfigVersion

        defaults = {
            "id": uuid.uuid4(),
            "config_id": uuid.uuid4(),
            "tenant_id": "tenant-001",
            "provider_type": "weather",
            "provider_name": "open_meteo",
            "api_key": None,
            "api_secret": None,
            "priority": "primary",
            "enabled": True,
            "config_data": None,
            "version": 2,
            "change_type": "updated",
            "changed_at": datetime(2025, 2, 10, 8, 0, 0),
            "changed_by": "admin",
            "change_reason": "Updated API key",
        }
        defaults.update(overrides)
        mock = MagicMock(spec=ConfigVersion)
        for k, v in defaults.items():
            setattr(mock, k, v)
        mock.to_dict = lambda: ConfigVersion.to_dict(mock)
        return mock

    def test_to_dict_basic(self):
        """Test basic ConfigVersion to_dict"""
        cv = self._make_version()
        result = cv.to_dict()

        assert result["tenant_id"] == "tenant-001"
        assert result["provider_type"] == "weather"
        assert result["provider_name"] == "open_meteo"
        assert result["version"] == 2
        assert result["change_type"] == "updated"
        assert result["changed_by"] == "admin"
        assert result["change_reason"] == "Updated API key"

    def test_to_dict_ids_are_strings(self):
        """Test that UUIDs are serialized to strings"""
        test_id = uuid.uuid4()
        config_id = uuid.uuid4()
        cv = self._make_version(id=test_id, config_id=config_id)
        result = cv.to_dict()
        assert result["id"] == str(test_id)
        assert result["config_id"] == str(config_id)

    def test_to_dict_none_changed_at(self):
        """Test None changed_at returns None"""
        cv = self._make_version(changed_at=None)
        result = cv.to_dict()
        assert result["changed_at"] is None

    def test_to_dict_none_config_data_becomes_empty_dict(self):
        """Test None config_data is returned as empty dict"""
        cv = self._make_version(config_data=None)
        result = cv.to_dict()
        assert result["config_data"] == {}

    def test_tablename(self):
        """Test table name"""
        from src.models import ConfigVersion

        assert ConfigVersion.__tablename__ == "config_versions"

    def test_table_has_indexes(self):
        """Test ConfigVersion indexes exist"""
        from src.models import ConfigVersion

        index_names = {idx.name for idx in ConfigVersion.__table_args__ if hasattr(idx, "name")}
        assert "idx_config_version" in index_names
        assert "idx_tenant_changed_at" in index_names
        assert "idx_tenant_provider_changed" in index_names


class TestDatabaseClass:
    """Tests for the Database utility class"""

    @patch("src.models.create_engine")
    @patch("src.models.sessionmaker")
    def test_init_creates_engine(self, mock_sessionmaker, mock_create_engine):
        """Test that Database init creates engine with correct params"""
        from src.models import Database

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        db = Database("postgresql://localhost/test")

        mock_create_engine.assert_called_once_with(
            "postgresql://localhost/test",
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        assert db.engine == mock_engine

    @patch("src.models.create_engine")
    @patch("src.models.sessionmaker")
    def test_create_tables(self, mock_sessionmaker, mock_create_engine):
        """Test create_tables calls Base.metadata.create_all"""
        from src.models import Base, Database

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        db = Database("postgresql://localhost/test")

        with patch.object(Base.metadata, "create_all") as mock_create_all:
            db.create_tables()
            mock_create_all.assert_called_once_with(bind=mock_engine)

    @patch("src.models.create_engine")
    @patch("src.models.sessionmaker")
    def test_get_session_yields_and_closes(self, mock_sessionmaker, mock_create_engine):
        """Test get_session yields a session and closes it"""
        from src.models import Database

        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_sessionmaker.return_value = MagicMock(return_value=mock_session)

        db = Database("postgresql://localhost/test")
        gen = db.get_session()
        session = next(gen)
        assert session == mock_session

        # Exhaust the generator to trigger finally
        with pytest.raises(StopIteration):
            next(gen)
        mock_session.close.assert_called_once()
