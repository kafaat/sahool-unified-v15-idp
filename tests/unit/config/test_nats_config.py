"""
اختبارات تكوين NATS
NATS Configuration Tests

Tests to validate NATS configuration file security settings and structure.
"""

import os
import re
import pytest
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Test Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def nats_config_path():
    """Get the path to the NATS configuration file."""
    # Navigate from tests/unit/config to config/nats/nats.conf
    base_dir = Path(__file__).parent.parent.parent.parent
    return base_dir / "config" / "nats" / "nats.conf"


@pytest.fixture
def nats_config_content(nats_config_path):
    """Read the NATS configuration file content."""
    if not nats_config_path.exists():
        pytest.skip(f"NATS config file not found: {nats_config_path}")
    return nats_config_path.read_text()


# ─────────────────────────────────────────────────────────────────────────────
# Configuration File Existence Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestNatsConfigExists:
    """Tests for NATS configuration file existence."""

    def test_config_file_exists(self, nats_config_path):
        """Test that NATS configuration file exists."""
        assert nats_config_path.exists(), f"NATS config not found: {nats_config_path}"

    def test_config_file_not_empty(self, nats_config_content):
        """Test that NATS configuration file is not empty."""
        assert len(nats_config_content) > 0, "NATS config file is empty"


# ─────────────────────────────────────────────────────────────────────────────
# Security Configuration Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestNatsSecurityConfig:
    """Tests for NATS security configuration."""

    def test_default_permissions_restricted(self, nats_config_content):
        """Test that default permissions are restricted to sahool.* subjects only."""
        # Check that default_permissions uses sahool.> not >
        # This ensures new users don't get full access by default
        assert "default_permissions" in nats_config_content

        # Look for the default_permissions block
        # Should contain sahool.> in allow, not just >
        default_perms_match = re.search(r"default_permissions\s*=\s*\{[\s\S]*?(?=users\s*=)", nats_config_content)
        assert default_perms_match, "default_permissions block not found"

        default_perms = default_perms_match.group()

        # Verify sahool.> is in the allow list for publish
        assert '"sahool.>"' in default_perms or "'sahool.>'" in default_perms, (
            "default_permissions should allow sahool.> subjects"
        )

        # Verify we're not allowing all subjects (">") in default permissions
        # The pattern should NOT have allow = [">"] in default_permissions
        dangerous_pattern = re.search(r'allow\s*=\s*\[\s*["\']>\s*["\']', default_perms)
        assert dangerous_pattern is None, "default_permissions should NOT allow '>' (all subjects) - security risk!"

    def test_system_subjects_denied(self, nats_config_content):
        """Test that system subjects ($SYS.>) are denied in default permissions."""
        default_perms_match = re.search(r"default_permissions\s*=\s*\{[\s\S]*?(?=users\s*=)", nats_config_content)
        assert default_perms_match, "default_permissions block not found"

        default_perms = default_perms_match.group()

        # Check that $SYS.> is in the deny list
        assert '"$SYS.>"' in default_perms or "'$SYS.>'" in default_perms, (
            "$SYS.> should be denied in default permissions"
        )

    def test_stream_deletion_denied(self, nats_config_content):
        """Test that JetStream stream deletion is denied in default permissions."""
        default_perms_match = re.search(r"default_permissions\s*=\s*\{[\s\S]*?(?=users\s*=)", nats_config_content)
        assert default_perms_match, "default_permissions block not found"

        default_perms = default_perms_match.group()

        # Check stream deletion denial
        assert "$JS.API.STREAM.DELETE" in default_perms, "Stream deletion should be denied in default permissions"

    def test_consumer_deletion_denied(self, nats_config_content):
        """Test that JetStream consumer deletion is denied in default permissions."""
        default_perms_match = re.search(r"default_permissions\s*=\s*\{[\s\S]*?(?=users\s*=)", nats_config_content)
        assert default_perms_match, "default_permissions block not found"

        default_perms = default_perms_match.group()

        # Check consumer deletion denial
        assert "$JS.API.CONSUMER.DELETE" in default_perms, "Consumer deletion should be denied in default permissions"

    @staticmethod
    def _get_user_block(content, username_var):
        """Extract the user block for a specific user variable from NATS config."""
        import re
        # Match from the user declaration to the next closing brace at the same level
        escaped = re.escape(username_var)
        pattern = rf'(\{{\s*\n\s*user:\s*{escaped}.*?\}})'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else ""

    def test_admin_user_requires_env_vars(self, nats_config_content):
        """Test that admin user credentials come from environment variables or bcrypt hashes."""
        assert "$NATS_ADMIN_USER" in nats_config_content, "Admin username should be from environment variable"
        # Scope password check to the admin user block specifically
        admin_block = self._get_user_block(nats_config_content, "$NATS_ADMIN_USER")
        has_env_password = "$NATS_ADMIN_PASSWORD" in admin_block
        has_bcrypt_password = "$2b$" in admin_block
        assert has_env_password or has_bcrypt_password, "Admin user block must have env var or bcrypt password"

    def test_app_user_requires_env_vars(self, nats_config_content):
        """Test that application user credentials come from environment variables or bcrypt hashes."""
        assert "$NATS_USER" in nats_config_content, "App username should be from environment variable"
        app_block = self._get_user_block(nats_config_content, "$NATS_USER")
        has_env_password = "$NATS_PASSWORD" in app_block
        has_bcrypt_password = "$2b$" in app_block
        assert has_env_password or has_bcrypt_password, "App user block must have env var or bcrypt password"

    def test_monitor_user_requires_env_vars(self, nats_config_content):
        """Test that monitor user credentials come from environment variables or bcrypt hashes."""
        assert "$NATS_MONITOR_USER" in nats_config_content, "Monitor username should be from environment variable"
        monitor_block = self._get_user_block(nats_config_content, "$NATS_MONITOR_USER")
        has_env_password = "$NATS_MONITOR_PASSWORD" in monitor_block
        has_bcrypt_password = "$2b$" in monitor_block
        assert has_env_password or has_bcrypt_password, "Monitor user block must have env var or bcrypt password"

    def test_no_hardcoded_passwords(self, nats_config_content):
        """Test that there are no hardcoded passwords (plaintext) in the configuration.
        Bcrypt hashes ($2b$...) are acceptable as they are not reversible."""
        # Common patterns for hardcoded passwords (excluding bcrypt hashes)
        dangerous_patterns = [
            r'password:\s*["\'][^$][^"\']+["\']',  # password: "something" (not starting with $)
            r"password:\s+[a-zA-Z0-9_]+\s",  # password: plaintext
        ]

        for pattern in dangerous_patterns:
            match = re.search(pattern, nats_config_content)
            # If there's a match, it should only be in comments
            if match:
                # Check if the match is in a comment line
                line_start = nats_config_content.rfind("\n", 0, match.start()) + 1
                line = nats_config_content[line_start : match.end()]
                assert line.strip().startswith("#"), f"Potential hardcoded password found: {match.group()}"


# ─────────────────────────────────────────────────────────────────────────────
# JetStream Configuration Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestNatsJetStreamConfig:
    """Tests for NATS JetStream configuration."""

    def test_jetstream_enabled(self, nats_config_content):
        """Test that JetStream is enabled in the configuration."""
        # Look for jetstream block (not commented out)
        jetstream_match = re.search(r"^jetstream\s*\{", nats_config_content, re.MULTILINE)
        assert jetstream_match, "JetStream should be enabled in configuration"

    def test_jetstream_store_dir_configured(self, nats_config_content):
        """Test that JetStream storage directory is configured."""
        assert "store_dir:" in nats_config_content, "JetStream store_dir should be configured"

    def test_jetstream_memory_limit_set(self, nats_config_content):
        """Test that JetStream memory limit is configured."""
        assert "max_memory_store:" in nats_config_content, "JetStream max_memory_store should be configured"

    def test_jetstream_file_limit_set(self, nats_config_content):
        """Test that JetStream file storage limit is configured."""
        assert "max_file_store:" in nats_config_content, "JetStream max_file_store should be configured"


# ─────────────────────────────────────────────────────────────────────────────
# Server Configuration Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestNatsServerConfig:
    """Tests for NATS server configuration."""

    def test_server_name_set(self, nats_config_content):
        """Test that server name is configured."""
        assert "server_name:" in nats_config_content, "Server name should be configured"
        assert "sahool" in nats_config_content.lower(), "Server name should contain 'sahool'"

    def test_listen_port_configured(self, nats_config_content):
        """Test that listen port is configured."""
        assert "listen:" in nats_config_content, "Listen address should be configured"
        # Check for standard NATS port
        assert "4222" in nats_config_content, "Standard NATS port 4222 should be configured"

    def test_http_monitoring_port_configured(self, nats_config_content):
        """Test that HTTP monitoring port is configured."""
        assert "http_port:" in nats_config_content or "http:" in nats_config_content, (
            "HTTP monitoring port should be configured"
        )
        # Check for standard monitoring port
        assert "8222" in nats_config_content, "Standard monitoring port 8222 should be configured"

    def test_max_connections_set(self, nats_config_content):
        """Test that max connections limit is set."""
        assert "max_connections:" in nats_config_content, "max_connections should be configured"

    def test_max_payload_set(self, nats_config_content):
        """Test that max payload size is set."""
        assert "max_payload:" in nats_config_content, "max_payload should be configured"


# ─────────────────────────────────────────────────────────────────────────────
# Subject Namespace Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestNatsSubjectNamespaces:
    """Tests for NATS subject namespace configuration."""

    def test_sahool_namespace_allowed(self, nats_config_content):
        """Test that sahool.> namespace is allowed."""
        assert '"sahool.>"' in nats_config_content or "'sahool.>'" in nats_config_content, (
            "sahool.> namespace should be allowed"
        )

    def test_inbox_namespace_allowed(self, nats_config_content):
        """Test that _INBOX.> namespace is allowed for request-reply."""
        assert '"_INBOX.>"' in nats_config_content or "'_INBOX.>'" in nats_config_content, (
            "_INBOX.> namespace should be allowed for request-reply patterns"
        )

    def test_field_namespace_for_app_user(self, nats_config_content):
        """Test that field.> namespace is allowed for application user."""
        # This should be in the app user permissions
        assert '"field.>"' in nats_config_content or "'field.>'" in nats_config_content, (
            "field.> namespace should be allowed for app user"
        )

    def test_weather_namespace_for_app_user(self, nats_config_content):
        """Test that weather.> namespace is allowed for application user."""
        assert '"weather.>"' in nats_config_content or "'weather.>'" in nats_config_content, (
            "weather.> namespace should be allowed for app user"
        )

    def test_iot_namespace_for_app_user(self, nats_config_content):
        """Test that iot.> namespace is allowed for application user."""
        assert '"iot.>"' in nats_config_content or "'iot.>'" in nats_config_content, (
            "iot.> namespace should be allowed for app user"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Logging Configuration Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestNatsLoggingConfig:
    """Tests for NATS logging configuration."""

    def test_logtime_enabled(self, nats_config_content):
        """Test that log timestamps are enabled."""
        assert "logtime:" in nats_config_content, "logtime should be configured"

    def test_log_file_configured(self, nats_config_content):
        """Test that log file is configured."""
        assert "log_file:" in nats_config_content, "log_file should be configured"

    def test_debug_disabled_by_default(self, nats_config_content):
        """Test that debug mode is disabled by default."""
        # Look for uncommented debug: false
        debug_match = re.search(r"^debug:\s*false", nats_config_content, re.MULTILINE)
        assert debug_match, "debug should be set to false by default"

    def test_trace_disabled_by_default(self, nats_config_content):
        """Test that trace mode is disabled by default."""
        trace_match = re.search(r"^trace:\s*false", nats_config_content, re.MULTILINE)
        assert trace_match, "trace should be set to false by default"


# ─────────────────────────────────────────────────────────────────────────────
# User Role Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestNatsUserRoles:
    """Tests for NATS user role configurations."""

    def test_admin_user_has_full_access(self, nats_config_content):
        """Test that admin user has full access (>)."""
        # Find the admin user block
        admin_block_match = re.search(
            r"\$NATS_ADMIN_USER[\s\S]*?permissions\s*=\s*\{[\s\S]*?\}[\s\S]*?\}",
            nats_config_content,
        )
        assert admin_block_match, "Admin user block not found"

        admin_block = admin_block_match.group()
        # Admin should have allow = [">"] for publish and subscribe
        assert 'allow = [">"]' in admin_block or "allow = ['>']" in admin_block, (
            "Admin user should have full access (>)"
        )

    def test_monitor_user_read_only(self, nats_config_content):
        """Test that monitor user has read-only access."""
        # Find the monitor user block
        monitor_block_match = re.search(
            r"\$NATS_MONITOR_USER[\s\S]*?permissions\s*=\s*\{[\s\S]*?\}[\s\S]*?\}",
            nats_config_content,
        )
        assert monitor_block_match, "Monitor user block not found"

        monitor_block = monitor_block_match.group()
        # Monitor should have deny = [">"] for publish
        assert 'deny = [">"]' in monitor_block or "deny = ['>']" in monitor_block, (
            "Monitor user should have publish denied (read-only)"
        )

    def test_three_user_types_defined(self, nats_config_content):
        """Test that three user types are defined (admin, app, monitor)."""
        assert "$NATS_ADMIN_USER" in nats_config_content, "Admin user not defined"
        assert "$NATS_USER" in nats_config_content, "App user not defined"
        assert "$NATS_MONITOR_USER" in nats_config_content, "Monitor user not defined"
