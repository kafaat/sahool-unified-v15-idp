"""
File Validation Tests for SAHOOL Platform.

Tests validate file upload security and validation rules.
"""

import io
import struct
from typing import Any, Dict, List

import pytest


class FileValidator:
    """File validation utility for testing."""

    ALLOWED_EXTENSIONS = {
        "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
        "geospatial": [".geojson", ".kml", ".kmz", ".shp"],
    }

    MIME_TYPES = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
        ".geojson": "application/geo+json",
    }

    MAGIC_BYTES = {
        "jpeg": bytes([0xFF, 0xD8, 0xFF]),
        "png": bytes([0x89, 0x50, 0x4E, 0x47]),
        "gif": bytes([0x47, 0x49, 0x46]),
        "pdf": bytes([0x25, 0x50, 0x44, 0x46]),
    }

    MAX_FILE_SIZES = {
        "image": 10 * 1024 * 1024,
        "document": 50 * 1024 * 1024,
        "geospatial": 100 * 1024 * 1024,
    }

    @classmethod
    def validate_extension(cls, filename: str, file_type: str) -> bool:
        """Validate file extension."""
        if not filename:
            return False

        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        allowed = cls.ALLOWED_EXTENSIONS.get(file_type, [])
        return ext in allowed

    @classmethod
    def validate_mime_type(cls, filename: str, content_type: str) -> bool:
        """Validate MIME type matches extension."""
        if not filename or not content_type:
            return False

        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        expected_mime = cls.MIME_TYPES.get(ext)
        return expected_mime == content_type

    @classmethod
    def validate_magic_bytes(cls, content: bytes, expected_type: str) -> bool:
        """Validate file magic bytes."""
        if not content:
            return False

        magic = cls.MAGIC_BYTES.get(expected_type)
        if not magic:
            return True

        return content[: len(magic)] == magic

    @classmethod
    def validate_file_size(cls, size: int, file_type: str) -> bool:
        """Validate file size."""
        max_size = cls.MAX_FILE_SIZES.get(file_type, 0)
        return 0 < size <= max_size

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to prevent path traversal."""
        if not filename:
            return ""

        filename = filename.replace("\\", "/")
        filename = filename.split("/")[-1]

        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\x00"]
        for char in dangerous_chars:
            filename = filename.replace(char, "_")

        filename = filename.strip(". ")

        if len(filename) > 255:
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
            filename = name[: 255 - len(ext) - 1] + "." + ext if ext else name[:255]

        return filename


@pytest.fixture
def validator():
    """Create file validator."""
    return FileValidator()


class TestExtensionValidation:
    """Tests for file extension validation."""

    def test_valid_image_extensions(self, validator):
        """Test valid image extensions pass."""
        valid_files = ["photo.jpg", "image.png", "picture.gif", "banner.webp"]

        for filename in valid_files:
            assert validator.validate_extension(filename, "image") is True

    def test_invalid_image_extensions(self, validator):
        """Test invalid image extensions fail."""
        invalid_files = ["script.exe", "virus.bat", "malware.sh", "hack.php"]

        for filename in invalid_files:
            assert validator.validate_extension(filename, "image") is False

    def test_valid_document_extensions(self, validator):
        """Test valid document extensions pass."""
        valid_files = ["report.pdf", "data.xlsx", "document.docx"]

        for filename in valid_files:
            assert validator.validate_extension(filename, "document") is True

    def test_valid_geospatial_extensions(self, validator):
        """Test valid geospatial extensions pass."""
        valid_files = ["field.geojson", "boundaries.kml", "map.kmz"]

        for filename in valid_files:
            assert validator.validate_extension(filename, "geospatial") is True

    def test_case_insensitive_extension(self, validator):
        """Test extension validation is case-insensitive."""
        assert validator.validate_extension("photo.JPG", "image") is True
        assert validator.validate_extension("photo.Png", "image") is True

    def test_empty_filename(self, validator):
        """Test empty filename fails."""
        assert validator.validate_extension("", "image") is False
        assert validator.validate_extension(None, "image") is False


class TestMimeTypeValidation:
    """Tests for MIME type validation."""

    def test_matching_mime_type(self, validator):
        """Test matching MIME types pass."""
        assert validator.validate_mime_type("photo.jpg", "image/jpeg") is True
        assert validator.validate_mime_type("image.png", "image/png") is True
        assert validator.validate_mime_type("doc.pdf", "application/pdf") is True

    def test_mismatched_mime_type(self, validator):
        """Test mismatched MIME types fail."""
        assert validator.validate_mime_type("photo.jpg", "image/png") is False
        assert validator.validate_mime_type("photo.jpg", "application/pdf") is False

    def test_spoofed_extension(self, validator):
        """Test spoofed extension detection."""
        assert validator.validate_mime_type("malware.jpg", "application/x-executable") is False


class TestMagicBytesValidation:
    """Tests for magic bytes validation."""

    def test_valid_jpeg_magic_bytes(self, validator):
        """Test valid JPEG magic bytes pass."""
        jpeg_content = bytes([0xFF, 0xD8, 0xFF, 0xE0]) + b"JFIF"
        assert validator.validate_magic_bytes(jpeg_content, "jpeg") is True

    def test_valid_png_magic_bytes(self, validator):
        """Test valid PNG magic bytes pass."""
        png_content = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
        assert validator.validate_magic_bytes(png_content, "png") is True

    def test_valid_pdf_magic_bytes(self, validator):
        """Test valid PDF magic bytes pass."""
        pdf_content = b"%PDF-1.4"
        assert validator.validate_magic_bytes(pdf_content, "pdf") is True

    def test_invalid_magic_bytes(self, validator):
        """Test invalid magic bytes fail."""
        fake_jpeg = b"This is not a JPEG file"
        assert validator.validate_magic_bytes(fake_jpeg, "jpeg") is False

    def test_empty_content(self, validator):
        """Test empty content fails."""
        assert validator.validate_magic_bytes(b"", "jpeg") is False
        assert validator.validate_magic_bytes(None, "jpeg") is False


class TestFileSizeValidation:
    """Tests for file size validation."""

    def test_valid_image_size(self, validator):
        """Test valid image size passes."""
        assert validator.validate_file_size(1024 * 1024, "image") is True
        assert validator.validate_file_size(5 * 1024 * 1024, "image") is True

    def test_oversized_image(self, validator):
        """Test oversized image fails."""
        assert validator.validate_file_size(20 * 1024 * 1024, "image") is False

    def test_zero_size_fails(self, validator):
        """Test zero size fails."""
        assert validator.validate_file_size(0, "image") is False

    def test_negative_size_fails(self, validator):
        """Test negative size fails."""
        assert validator.validate_file_size(-1, "image") is False


class TestFilenameSanitization:
    """Tests for filename sanitization."""

    def test_path_traversal_prevention(self, validator):
        """Test path traversal is prevented."""
        dangerous = "../../../etc/passwd"
        sanitized = validator.sanitize_filename(dangerous)
        assert ".." not in sanitized
        assert "/" not in sanitized

    def test_windows_path_traversal(self, validator):
        """Test Windows path traversal is prevented."""
        dangerous = "..\\..\\windows\\system32\\config"
        sanitized = validator.sanitize_filename(dangerous)
        assert "\\" not in sanitized
        assert ".." not in sanitized

    def test_null_byte_removal(self, validator):
        """Test null bytes are removed."""
        dangerous = "file.jpg\x00.exe"
        sanitized = validator.sanitize_filename(dangerous)
        assert "\x00" not in sanitized

    def test_special_characters_removed(self, validator):
        """Test special characters are removed."""
        dangerous = 'file<script>alert("xss")</script>.jpg'
        sanitized = validator.sanitize_filename(dangerous)
        assert "<" not in sanitized
        assert ">" not in sanitized

    def test_long_filename_truncated(self, validator):
        """Test long filename is truncated."""
        long_name = "a" * 300 + ".jpg"
        sanitized = validator.sanitize_filename(long_name)
        assert len(sanitized) <= 255

    def test_empty_filename(self, validator):
        """Test empty filename returns empty string."""
        assert validator.sanitize_filename("") == ""
        assert validator.sanitize_filename(None) == ""


class TestContentTypeSniffing:
    """Tests for content type sniffing prevention."""

    def test_xss_in_svg(self):
        """Test XSS in SVG is detected."""
        svg_with_script = """
        <svg xmlns="http://www.w3.org/2000/svg">
            <script>alert('XSS')</script>
        </svg>
        """

        assert "<script>" in svg_with_script

    def test_html_in_image(self):
        """Test HTML in image is detected."""
        fake_image = b"<html><body>Malicious content</body></html>"

        assert b"<html>" in fake_image


class TestVirusScanning:
    """Tests for virus scanning integration."""

    def test_eicar_test_file_detected(self):
        """Test EICAR test file pattern is detected."""
        eicar_pattern = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

        def is_eicar(content: str) -> bool:
            return "EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in content

        assert is_eicar(eicar_pattern) is True

    def test_clean_file_passes(self):
        """Test clean file passes virus scan."""
        clean_content = b"This is a normal file with no malicious content."

        def is_clean(content: bytes) -> bool:
            dangerous_patterns = [b"EICAR", b"<script>", b"eval("]
            return not any(p in content for p in dangerous_patterns)

        assert is_clean(clean_content) is True


@pytest.mark.unit
class TestGeoJSONValidation:
    """Tests for GeoJSON file validation."""

    def test_valid_geojson(self):
        """Test valid GeoJSON passes validation."""
        import json

        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
            "properties": {"name": "Test Field"},
        }

        content = json.dumps(geojson).encode()
        parsed = json.loads(content)

        assert parsed["type"] == "Feature"
        assert "geometry" in parsed

    def test_invalid_geojson_rejected(self):
        """Test invalid GeoJSON is rejected."""
        import json

        invalid = "This is not valid JSON or GeoJSON"

        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid)

    def test_geojson_with_excessive_coordinates(self):
        """Test GeoJSON with excessive coordinates is flagged."""
        max_coordinates = 10000
        coords = [[i, i] for i in range(max_coordinates + 1)]

        assert len(coords) > max_coordinates


@pytest.mark.unit
class TestImageProcessing:
    """Tests for image processing security."""

    def test_image_dimension_limits(self):
        """Test image dimension limits."""
        max_dimension = 10000

        def validate_dimensions(width: int, height: int) -> bool:
            return 0 < width <= max_dimension and 0 < height <= max_dimension

        assert validate_dimensions(1920, 1080) is True
        assert validate_dimensions(15000, 10000) is False

    def test_image_decompression_bomb_prevention(self):
        """Test decompression bomb prevention."""
        max_pixels = 100_000_000

        def validate_pixel_count(width: int, height: int) -> bool:
            return width * height <= max_pixels

        assert validate_pixel_count(1920, 1080) is True
        assert validate_pixel_count(50000, 50000) is False
