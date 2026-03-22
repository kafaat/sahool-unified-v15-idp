"""Tests for configuration settings in Supply Chain Service."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")

import pytest


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_service_name(self):
        from src.core.config import Settings

        s = Settings()
        assert s.SERVICE_NAME == "supply-chain-service"

    def test_default_service_name_ar(self):
        from src.core.config import Settings

        s = Settings()
        assert s.SERVICE_NAME_AR == "خدمة سلسلة التوريد"

    def test_default_version(self):
        from src.core.config import Settings

        s = Settings()
        assert s.VERSION == "16.0.0"

    def test_default_port(self):
        from src.core.config import Settings

        s = Settings()
        assert s.PORT == 8230

    def test_default_environment(self):
        from src.core.config import Settings

        s = Settings()
        assert s.ENVIRONMENT in ("development", "test")

    def test_database_settings_defaults(self):
        from src.core.config import Settings

        s = Settings()
        assert s.DB_MIN_CONNECTIONS == 2
        assert s.DB_MAX_CONNECTIONS == 10

    def test_payment_settings_defaults(self):
        from src.core.config import Settings

        s = Settings()
        assert s.PAYMENT_GATEWAY_TIMEOUT == 30
        assert s.PAYMENT_ENABLED is True

    def test_delivery_settings_defaults(self):
        from src.core.config import Settings

        s = Settings()
        assert s.DELIVERY_SERVICE_TIMEOUT == 30
        assert s.DELIVERY_TRACKING_ENABLED is True

    def test_notification_settings_defaults(self):
        from src.core.config import Settings

        s = Settings()
        assert s.SMS_ENABLED is True
        assert s.PUSH_ENABLED is True
        assert s.EMAIL_ENABLED is True

    def test_supplier_settings_defaults(self):
        from src.core.config import Settings

        s = Settings()
        assert s.SUPPLIER_SEARCH_RADIUS_KM == 50.0
        assert s.MAX_SUPPLIERS_PER_QUERY == 10
        assert s.QUOTE_VALIDITY_HOURS == 24

    def test_order_settings_defaults(self):
        from src.core.config import Settings

        s = Settings()
        assert s.ORDER_TIMEOUT_HOURS == 48
        assert s.MAX_ORDER_ITEMS == 50
        assert s.AUTO_PURCHASE_ENABLED is True

    def test_jwt_settings_defaults(self):
        from src.core.config import Settings

        s = Settings()
        assert s.JWT_ALGORITHM == "HS256"

    def test_get_settings_returns_instance(self):
        from src.core.config import get_settings

        s = get_settings()
        assert s.SERVICE_NAME == "supply-chain-service"

    def test_settings_singleton(self):
        from src.core.config import settings

        assert settings is not None
        assert settings.SERVICE_NAME == "supply-chain-service"

    def test_debug_default_false(self):
        from src.core.config import Settings

        s = Settings()
        assert s.DEBUG is False

    def test_log_level_default(self):
        from src.core.config import Settings

        s = Settings()
        assert s.LOG_LEVEL == "INFO"
