"""Tests for YOLO26 Vision Service configuration."""



class TestSettings:
    """Test configuration settings."""

    def test_default_port(self, _test_env):
        """Service should default to port 8150."""
        from src.core.config import Settings

        settings = Settings()
        assert settings.port == 8150

    def test_default_model_variant(self, _test_env):
        """Default model variant should be 'm' (medium)."""
        from src.core.config import Settings

        settings = Settings()
        assert settings.default_model_variant == "m"

    def test_test_environment(self, _test_env):
        """Environment should be 'test' in test mode."""
        from src.core.config import Settings

        settings = Settings()
        assert settings.environment == "test"

    def test_is_not_production(self, _test_env):
        """Should not be production in test mode."""
        from src.core.config import Settings

        settings = Settings()
        assert not settings.is_production

    def test_max_upload_size_bytes(self, _test_env):
        """Upload size should convert MB to bytes correctly."""
        from src.core.config import Settings

        settings = Settings()
        assert settings.max_upload_size_bytes == 50 * 1024 * 1024

    def test_cors_origins_from_string(self, _test_env):
        """CORS origins should parse from comma-separated string."""
        from src.core.config import Settings

        origins = Settings.parse_cors_origins("http://localhost:3000,http://localhost:8080")
        assert len(origins) == 2
        assert "http://localhost:3000" in origins

    def test_confidence_threshold_range(self, _test_env):
        """Confidence threshold must be between 0 and 1."""
        from src.core.config import Settings

        settings = Settings()
        assert 0.0 <= settings.default_confidence_threshold <= 1.0

    def test_iou_threshold_range(self, _test_env):
        """IoU threshold must be between 0 and 1."""
        from src.core.config import Settings

        settings = Settings()
        assert 0.0 <= settings.default_iou_threshold <= 1.0

    def test_cpu_device_in_tests(self, _test_env, monkeypatch):
        """Device should be CPU in test environment."""
        monkeypatch.setenv("DEVICE", "cpu")
        from src.core.config import Settings

        settings = Settings()
        assert settings.device == "cpu"
