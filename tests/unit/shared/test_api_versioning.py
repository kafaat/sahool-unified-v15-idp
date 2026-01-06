"""
Tests for API Versioning Middleware
اختبارات middleware إصدارات API
"""

import pytest
from shared.middleware.api_versioning import (
    APIVersion,
    VersionedRouter,
    extract_api_version,
    get_version_info,
    SUPPORTED_VERSIONS,
    DEFAULT_VERSION,
)


class TestAPIVersion:
    """Tests for APIVersion enum"""

    def test_v1_value(self):
        """Test V1 version value"""
        assert APIVersion.V1.value == "v1"

    def test_v2_value(self):
        """Test V2 version value"""
        assert APIVersion.V2.value == "v2"

    def test_latest_returns_v1(self):
        """Test latest() returns V1"""
        assert APIVersion.latest() == APIVersion.V1

    def test_all_versions(self):
        """Test all_versions() returns list of version strings"""
        versions = APIVersion.all_versions()
        assert "v1" in versions
        assert "v2" in versions

    def test_is_valid_v1(self):
        """Test is_valid() for v1"""
        assert APIVersion.is_valid("v1") is True
        assert APIVersion.is_valid("V1") is True

    def test_is_valid_v2(self):
        """Test is_valid() for v2"""
        assert APIVersion.is_valid("v2") is True

    def test_is_valid_invalid(self):
        """Test is_valid() for invalid versions"""
        assert APIVersion.is_valid("v99") is False
        assert APIVersion.is_valid("invalid") is False
        assert APIVersion.is_valid("") is False


class TestExtractAPIVersion:
    """Tests for extract_api_version function"""

    def test_extract_v1_from_path(self):
        """Test extracting v1 from /api/v1/fields"""
        version, path = extract_api_version("/api/v1/fields")
        assert version == APIVersion.V1
        assert path == "/api/fields"

    def test_extract_v1_from_nested_path(self):
        """Test extracting v1 from nested path"""
        version, path = extract_api_version("/api/v1/users/123/fields")
        assert version == APIVersion.V1
        assert path == "/api/users/123/fields"

    def test_extract_v2_from_path(self):
        """Test extracting v2 from path"""
        version, path = extract_api_version("/api/v2/fields")
        assert version == APIVersion.V2
        assert path == "/api/fields"

    def test_unversioned_api_path(self):
        """Test unversioned API path returns None"""
        version, path = extract_api_version("/api/fields")
        assert version is None
        assert path == "/api/fields"

    def test_non_api_path(self):
        """Test non-API path returns None"""
        version, path = extract_api_version("/health")
        assert version is None
        assert path == "/health"

    def test_root_path(self):
        """Test root path"""
        version, path = extract_api_version("/")
        assert version is None
        assert path == "/"

    def test_api_v1_root(self):
        """Test /api/v1 root path"""
        version, path = extract_api_version("/api/v1")
        assert version == APIVersion.V1
        assert path == "/api"

    def test_api_v1_trailing_slash(self):
        """Test /api/v1/ with trailing slash"""
        version, path = extract_api_version("/api/v1/")
        assert version == APIVersion.V1
        assert path == "/api/"

    def test_case_insensitive(self):
        """Test case insensitive version extraction"""
        version, path = extract_api_version("/api/V1/fields")
        assert version == APIVersion.V1


class TestVersionedRouter:
    """Tests for VersionedRouter class"""

    def test_versioned_router_v1_prefix(self):
        """Test VersionedRouter creates correct prefix for V1"""
        router = VersionedRouter(version=APIVersion.V1, prefix="/fields")
        assert router.prefix == "/api/v1/fields"
        assert router.api_version == APIVersion.V1

    def test_versioned_router_v2_prefix(self):
        """Test VersionedRouter creates correct prefix for V2"""
        router = VersionedRouter(version=APIVersion.V2, prefix="/users")
        assert router.prefix == "/api/v2/users"
        assert router.api_version == APIVersion.V2

    def test_versioned_router_no_prefix(self):
        """Test VersionedRouter with empty prefix"""
        router = VersionedRouter(version=APIVersion.V1, prefix="")
        assert router.prefix == "/api/v1"

    def test_versioned_router_default_version(self):
        """Test VersionedRouter uses default version"""
        router = VersionedRouter(prefix="/test")
        assert router.api_version == DEFAULT_VERSION


class TestGetVersionInfo:
    """Tests for get_version_info function"""

    def test_version_info_structure(self):
        """Test get_version_info returns correct structure"""
        info = get_version_info()

        assert "supported_versions" in info
        assert "default_version" in info
        assert "latest_version" in info
        assert "deprecated_versions" in info
        assert "version_format" in info
        assert "examples" in info

    def test_version_info_values(self):
        """Test get_version_info returns correct values"""
        info = get_version_info()

        assert info["default_version"] == DEFAULT_VERSION.value
        assert info["latest_version"] == APIVersion.latest().value
        assert info["version_format"] == "/api/v{N}/..."

    def test_supported_versions_in_info(self):
        """Test supported versions are in info"""
        info = get_version_info()

        for version in SUPPORTED_VERSIONS:
            assert version.value in info["supported_versions"]


class TestConstants:
    """Tests for module constants"""

    def test_supported_versions_not_empty(self):
        """Test SUPPORTED_VERSIONS is not empty"""
        assert len(SUPPORTED_VERSIONS) > 0

    def test_default_version_in_supported(self):
        """Test DEFAULT_VERSION is in SUPPORTED_VERSIONS"""
        assert DEFAULT_VERSION in SUPPORTED_VERSIONS

    def test_default_version_is_v1(self):
        """Test DEFAULT_VERSION is V1"""
        assert DEFAULT_VERSION == APIVersion.V1
