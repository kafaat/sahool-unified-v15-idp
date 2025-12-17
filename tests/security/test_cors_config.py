"""
Unit tests for CORS configuration
"""
import os
import pytest
from shared.config.cors_config import CORSSettings, get_cors_config


class TestCORSSettings:
    """Test CORS configuration settings."""
    
    def test_production_origins_defined(self):
        """Test that production origins are explicitly defined."""
        settings = CORSSettings()
        assert len(settings.allowed_origins) > 0
        assert "https://admin.sahool.io" in settings.allowed_origins
        assert "https://app.sahool.io" in settings.allowed_origins
        
    def test_no_wildcard_in_production_origins(self):
        """Test that wildcard is not in production origins."""
        settings = CORSSettings()
        assert "*" not in settings.allowed_origins
        
    def test_development_origins_include_localhost(self):
        """Test that development origins include localhost."""
        settings = CORSSettings()
        assert any("localhost" in origin for origin in settings.dev_origins)
        
    def test_development_environment_includes_dev_origins(self, monkeypatch):
        """Test that development environment includes dev origins."""
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings = CORSSettings()
        all_origins = settings.all_origins
        
        # Should include both production and dev origins
        assert "https://admin.sahool.io" in all_origins
        assert "http://localhost:3000" in all_origins
        
    def test_production_environment_excludes_dev_origins(self, monkeypatch):
        """Test that production environment excludes dev origins."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        settings = CORSSettings()
        all_origins = settings.all_origins
        
        # Should only include production origins
        assert "https://admin.sahool.io" in all_origins
        assert "http://localhost:3000" not in all_origins
        
    def test_custom_origins_added_in_production(self, monkeypatch):
        """Test that custom origins can be added via env var."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("ALLOWED_ORIGINS", "https://custom.example.com,https://another.com")
        settings = CORSSettings()
        all_origins = settings.all_origins
        
        assert "https://custom.example.com" in all_origins
        assert "https://another.com" in all_origins
        
    def test_credentials_enabled(self):
        """Test that credentials are enabled."""
        settings = CORSSettings()
        assert settings.allow_credentials is True
        
    def test_allowed_methods_include_common_http_methods(self):
        """Test that common HTTP methods are allowed."""
        settings = CORSSettings()
        methods = settings.allow_methods
        
        assert "GET" in methods
        assert "POST" in methods
        assert "PUT" in methods
        assert "DELETE" in methods
        assert "OPTIONS" in methods
        
    def test_allowed_headers_include_auth_and_content_type(self):
        """Test that essential headers are allowed."""
        settings = CORSSettings()
        headers = settings.allow_headers
        
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert "Accept" in headers


class TestGetCorsConfig:
    """Test get_cors_config function."""
    
    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        config = get_cors_config()
        assert isinstance(config, dict)
        
    def test_includes_all_required_keys(self):
        """Test that config includes all required CORS keys."""
        config = get_cors_config()
        
        required_keys = [
            "allow_origins",
            "allow_credentials",
            "allow_methods",
            "allow_headers",
            "expose_headers",
            "max_age",
        ]
        
        for key in required_keys:
            assert key in config
            
    def test_allow_origins_is_list(self):
        """Test that allow_origins is a list."""
        config = get_cors_config()
        assert isinstance(config["allow_origins"], list)
        
    def test_no_wildcard_in_origins(self):
        """Test that wildcard is not in allowed origins."""
        config = get_cors_config()
        assert "*" not in config["allow_origins"]
        
    def test_config_is_usable_with_fastapi(self):
        """Test that config format is compatible with FastAPI."""
        config = get_cors_config()
        
        # FastAPI CORSMiddleware expects these types
        assert isinstance(config["allow_origins"], list)
        assert isinstance(config["allow_credentials"], bool)
        assert isinstance(config["allow_methods"], list)
        assert isinstance(config["allow_headers"], list)
        assert isinstance(config["max_age"], int)


@pytest.mark.integration
class TestCORSIntegration:
    """Integration tests for CORS configuration."""
    
    def test_cors_config_can_be_imported_in_services(self):
        """Test that CORS config can be imported in services."""
        # This test verifies the import path works
        from shared.config.cors_config import get_cors_config
        config = get_cors_config()
        assert config is not None
        
    def test_environment_switching_works(self, monkeypatch):
        """Test that environment switching affects allowed origins."""
        from shared.config.cors_config import CORSSettings
        
        # Test development
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings_dev = CORSSettings()
        dev_count = len(settings_dev.all_origins)
        
        # Test production
        monkeypatch.setenv("ENVIRONMENT", "production")
        settings_prod = CORSSettings()
        prod_count = len(settings_prod.all_origins)
        
        # Development should have more origins (includes localhost)
        assert dev_count > prod_count
