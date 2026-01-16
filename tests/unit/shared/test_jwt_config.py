"""
Tests for JWT Configuration
اختبارات إعدادات JWT
"""

import os

import pytest


class TestJWTConfig:
    """Tests for JWTConfig class"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup and teardown for each test"""
        # Store original env vars
        # Note: JWT_PUBLIC_KEY and JWT_PRIVATE_KEY removed - RS256 deprecated
        self.original_env = {}
        env_vars = [
            "JWT_SECRET_KEY",
            "JWT_SECRET",
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "JWT_REFRESH_TOKEN_EXPIRE_DAYS",
            "JWT_ISSUER",
            "JWT_AUDIENCE",
            "RATE_LIMIT_ENABLED",
            "RATE_LIMIT_REQUESTS",
            "RATE_LIMIT_WINDOW_SECONDS",
            "TOKEN_REVOCATION_ENABLED",
            "REDIS_URL",
            "REDIS_HOST",
            "REDIS_PORT",
            "REDIS_DB",
            "REDIS_PASSWORD",
            "ENVIRONMENT",
        ]
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
        yield
        # Restore original env vars
        for var, value in self.original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

    def test_jwt_config_import(self):
        """Test JWTConfig can be imported"""
        # Import directly to avoid jwt dependency
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "JWTConfig")

    def test_jwt_algorithm_default(self):
        """Test default JWT algorithm is HS256"""
        os.environ.pop("JWT_ALGORITHM", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.JWT_ALGORITHM == "HS256"

    def test_jwt_issuer_default(self):
        """Test default JWT issuer"""
        os.environ.pop("JWT_ISSUER", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.JWT_ISSUER == "sahool-platform"

    def test_jwt_audience_default(self):
        """Test default JWT audience"""
        os.environ.pop("JWT_AUDIENCE", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.JWT_AUDIENCE == "sahool-api"

    def test_access_token_expire_default(self):
        """Test default access token expiry is 30 minutes"""
        os.environ.pop("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_refresh_token_expire_default(self):
        """Test default refresh token expiry is 7 days"""
        os.environ.pop("JWT_REFRESH_TOKEN_EXPIRE_DAYS", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS == 7

    def test_token_header_default(self):
        """Test default token header is Authorization"""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.TOKEN_HEADER == "Authorization"
        assert module.JWTConfig.TOKEN_PREFIX == "Bearer"

    def test_rate_limit_enabled_default(self):
        """Test rate limiting is enabled by default"""
        os.environ.pop("RATE_LIMIT_ENABLED", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.RATE_LIMIT_ENABLED is True

    def test_rate_limit_requests_default(self):
        """Test default rate limit is 100 requests"""
        os.environ.pop("RATE_LIMIT_REQUESTS", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.RATE_LIMIT_REQUESTS == 100

    def test_rate_limit_window_default(self):
        """Test default rate limit window is 60 seconds"""
        os.environ.pop("RATE_LIMIT_WINDOW_SECONDS", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.RATE_LIMIT_WINDOW_SECONDS == 60

    def test_token_revocation_enabled_default(self):
        """Test token revocation is enabled by default"""
        os.environ.pop("TOKEN_REVOCATION_ENABLED", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.TOKEN_REVOCATION_ENABLED is True

    def test_redis_host_default(self):
        """Test default Redis host is localhost"""
        os.environ.pop("REDIS_HOST", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.REDIS_HOST == "localhost"

    def test_redis_port_default(self):
        """Test default Redis port is 6379"""
        os.environ.pop("REDIS_PORT", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.REDIS_PORT == 6379

    def test_redis_db_default(self):
        """Test default Redis DB is 0"""
        os.environ.pop("REDIS_DB", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.REDIS_DB == 0

    def test_jwt_algorithm_is_hs256_only(self):
        """Test JWT algorithm is always HS256 (RS256 deprecated)"""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # RS256 is deprecated - algorithm is always HS256
        assert module.JWTConfig.JWT_ALGORITHM == "HS256"

    def test_access_token_expire_from_env(self):
        """Test access token expiry from environment"""
        os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES == 60

    def test_validate_development_no_error(self):
        """Test validation passes in development"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ.pop("JWT_SECRET_KEY", None)
        os.environ.pop("JWT_SECRET", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Should not raise in development
        module.JWTConfig.validate()

    def test_validate_production_requires_secret(self):
        """Test validation requires secret in production"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_ALGORITHM"] = "HS256"
        os.environ.pop("JWT_SECRET_KEY", None)
        os.environ.pop("JWT_SECRET", None)
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with pytest.raises(ValueError, match="JWT_SECRET"):
            module.JWTConfig.validate()

    def test_validate_production_with_valid_secret(self):
        """Test validation passes with valid secret in production"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_ALGORITHM"] = "HS256"
        os.environ["JWT_SECRET_KEY"] = "a" * 32  # 32 character secret
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Should not raise
        module.JWTConfig.validate()

    def test_get_signing_key_hs256(self):
        """Test get_signing_key for HS256"""
        os.environ["JWT_ALGORITHM"] = "HS256"
        os.environ["JWT_SECRET_KEY"] = "test_secret_key"
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        key = module.JWTConfig.get_signing_key()
        assert key == "test_secret_key"

    def test_get_verification_key_hs256(self):
        """Test get_verification_key for HS256"""
        os.environ["JWT_ALGORITHM"] = "HS256"
        os.environ["JWT_SECRET_KEY"] = "test_secret_key"
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        key = module.JWTConfig.get_verification_key()
        assert key == "test_secret_key"



    def test_rate_limit_disabled_from_env(self):
        """Test rate limiting can be disabled"""
        os.environ["RATE_LIMIT_ENABLED"] = "false"
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.RATE_LIMIT_ENABLED is False

    def test_token_revocation_disabled_from_env(self):
        """Test token revocation can be disabled"""
        os.environ["TOKEN_REVOCATION_ENABLED"] = "false"
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.JWTConfig.TOKEN_REVOCATION_ENABLED is False

    def test_config_singleton_exists(self):
        """Test config singleton is created"""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "config", "/home/user/sahool-unified-v15-idp/shared/auth/config.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "config")
        assert isinstance(module.config, module.JWTConfig)
