"""
Tests for Hydrology Service configuration.
اختبارات إعدادات خدمة الهيدرولوجيا
"""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Tests for the Settings configuration class."""

    def _create_settings(self, env_overrides=None):
        """Create fresh settings with optional env overrides."""
        from src.core.config import Settings

        env = {
            "DATABASE_URL": "",
            "NATS_URL": "",
            "ENVIRONMENT": "test",
        }
        if env_overrides:
            env.update(env_overrides)
        with patch.dict(os.environ, env, clear=False):
            return Settings()

    def test_default_values(self):
        """Test default settings values."""
        s = self._create_settings()
        assert s.service_name == "hydrology-service"
        assert s.service_name_ar == "خدمة الهيدرولوجيا"
        assert s.version == "16.0.0"
        assert s.port == 8165
        assert s.host == "0.0.0.0"
        assert s.debug is False
        assert s.log_level == "INFO"

    def test_database_defaults(self):
        """Test default database settings."""
        s = self._create_settings()
        assert s.db_pool_min_size == 2
        assert s.db_pool_max_size == 10

    def test_nats_defaults(self):
        """Test default NATS settings."""
        s = self._create_settings()
        assert s.nats_cluster_id == "sahool-cluster"

    def test_hydrology_analysis_defaults(self):
        """Test default hydrology analysis settings."""
        s = self._create_settings()
        assert s.default_dem_resolution == 30.0
        assert s.flow_accumulation_threshold == 100
        assert s.depression_fill_max_depth == 2.0
        assert s.wetness_index_high_threshold == 12.0
        assert s.basin_area_min_hectares == 0.5

    def test_external_service_defaults(self):
        """Test default external service URLs."""
        s = self._create_settings()
        assert "terrain-core-service" in s.terrain_service_url
        assert "weather-service" in s.weather_service_url

    def test_cache_ttl_default(self):
        """Test default cache TTL."""
        s = self._create_settings()
        assert s.cache_ttl_seconds == 3600

    def test_env_override(self):
        """Test environment variable overrides."""
        s = self._create_settings(
            {
                "PORT": "9999",
                "HOST": "127.0.0.1",
                "LOG_LEVEL": "DEBUG",
                "DEFAULT_DEM_RESOLUTION": "10.0",
                "FLOW_ACCUMULATION_THRESHOLD": "200",
            }
        )
        assert s.port == 9999
        assert s.host == "127.0.0.1"
        assert s.log_level == "DEBUG"
        assert s.default_dem_resolution == 10.0
        assert s.flow_accumulation_threshold == 200

    def test_get_settings_cached(self):
        """Test that get_settings returns cached instance."""
        from src.core.config import get_settings

        get_settings.cache_clear()
        with patch.dict(os.environ, {"ENVIRONMENT": "test", "DATABASE_URL": "", "NATS_URL": ""}):
            s1 = get_settings()
            s2 = get_settings()
            assert s1 is s2
        get_settings.cache_clear()
