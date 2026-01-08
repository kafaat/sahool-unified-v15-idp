"""
File Upload Validators
أدوات التحقق من تحميل الملفات
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .mime_types import (
    ALLOWED_IMAGE_TYPES,
    get_mime_from_magic_bytes,
    is_mime_allowed,
    validate_mime_match,
)
from .virus_scanner import NoOpScanner, VirusScannerInterface


class FileValidationError(Exception):
    """
    Custom exception for file validation errors
    استثناء مخصص لأخطاء التحقق من الملفات
    """

    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


@dataclass
class FileValidationConfig:
    """
    Configuration for file validation
    إعدادات التحقق من الملفات
    """

    max_file_size: int = 10 * 1024 * 1024  # 10MB default
    allowed_mime_types: list[str] = None
    check_magic_bytes: bool = True
    strict_mime_check: bool = True
    scan_for_viruses: bool = False
    allow_executable: bool = False
    sanitize_filename: bool = True

    def __post_init__(self):
        if self.allowed_mime_types is None:
            self.allowed_mime_types = ALLOWED_IMAGE_TYPES.copy()


class FileValidator:
    """
    Comprehensive file upload validator
    أداة شاملة للتحقق من تحميل الملفات
    """

    def __init__(
        self,
        config: FileValidationConfig | None = None,
        virus_scanner: VirusScannerInterface | None = None,
    ):
        """
        Initialize file validator

        Args:
            config: Validation configuration
            virus_scanner: Virus scanner implementation (optional)
        """
        self.config = config or FileValidationConfig()
        self.virus_scanner = virus_scanner or NoOpScanner()

    async def validate(
        self,
        file_content: bytes,
        filename: str,
        declared_mime_type: str,
    ) -> dict:
        """
        Validate uploaded file
        التحقق من الملف المُحمّل

        Args:
            file_content: File content as bytes
            filename: Original filename
            declared_mime_type: MIME type from upload header

        Returns:
            Dictionary with validation results

        Raises:
            FileValidationError: If validation fails
        """
        # 1. Check file size
        self._validate_file_size(file_content)

        # 2. Sanitize filename
        safe_filename = sanitize_filename(filename) if self.config.sanitize_filename else filename

        # 3. Check MIME type whitelist
        self._validate_mime_type(declared_mime_type)

        # 4. Check magic bytes
        if self.config.check_magic_bytes:
            detected_mime = self._validate_magic_bytes(file_content, declared_mime_type)
        else:
            detected_mime = None

        # 5. Check for executables
        if not self.config.allow_executable:
            self._check_executable(file_content, filename)

        # 6. Scan for viruses
        if self.config.scan_for_viruses:
            await self._scan_virus(file_content, safe_filename)

        return {
            "valid": True,
            "original_filename": filename,
            "safe_filename": safe_filename,
            "declared_mime": declared_mime_type,
            "detected_mime": detected_mime,
            "file_size": len(file_content),
            "scanned_for_viruses": self.config.scan_for_viruses,
        }

    def _validate_file_size(self, file_content: bytes) -> None:
        """
        Validate file size
        التحقق من حجم الملف
        """
        file_size = len(file_content)

        if file_size == 0:
            raise FileValidationError("ملف فارغ / Empty file", error_code="EMPTY_FILE")

        if file_size > self.config.max_file_size:
            max_mb = self.config.max_file_size / (1024 * 1024)
            raise FileValidationError(
                f"حجم الملف كبير جداً. الحد الأقصى {max_mb}MB / File too large. Maximum {max_mb}MB",
                error_code="FILE_TOO_LARGE",
            )

    def _validate_mime_type(self, mime_type: str) -> None:
        """
        Validate MIME type against whitelist
        التحقق من نوع MIME مع القائمة البيضاء
        """
        if not is_mime_allowed(mime_type, self.config.allowed_mime_types):
            raise FileValidationError(
                f"نوع ملف غير مسموح: {mime_type} / Invalid file type: {mime_type}",
                error_code="INVALID_MIME_TYPE",
            )

    def _validate_magic_bytes(self, file_content: bytes, declared_mime: str) -> str | None:
        """
        Validate file content using magic bytes
        التحقق من محتوى الملف باستخدام البايتات السحرية
        """
        detected_mime = get_mime_from_magic_bytes(file_content)

        if detected_mime:
            is_valid = validate_mime_match(
                declared_mime, file_content, strict=self.config.strict_mime_check
            )

            if not is_valid:
                raise FileValidationError(
                    f"نوع الملف المُعلن ({declared_mime}) لا يتطابق مع المحتوى ({detected_mime}) / "
                    f"Declared type ({declared_mime}) doesn't match content ({detected_mime})",
                    error_code="MIME_MISMATCH",
                )

        return detected_mime

    def _check_executable(self, file_content: bytes, filename: str) -> None:
        """
        Check if file is executable
        التحقق من كون الملف قابل للتنفيذ
        """
        # Check file extension
        executable_extensions = [
            ".exe",
            ".bat",
            ".cmd",
            ".com",
            ".scr",
            ".vbs",
            ".js",
            ".jar",
            ".app",
            ".deb",
            ".rpm",
            ".sh",
            ".py",
            ".rb",
            ".pl",
            ".php",
            ".asp",
            ".aspx",
            ".jsp",
        ]

        file_ext = get_file_extension(filename).lower()
        if file_ext in executable_extensions:
            raise FileValidationError(
                "ملفات قابلة للتنفيذ غير مسموحة / Executable files not allowed",
                error_code="EXECUTABLE_NOT_ALLOWED",
            )

        # Check magic bytes for common executables
        executable_signatures = [
            b"MZ",  # Windows PE
            b"\x7fELF",  # Linux ELF
            b"#!",  # Script shebang
        ]

        for sig in executable_signatures:
            if file_content.startswith(sig):
                raise FileValidationError(
                    "ملف قابل للتنفيذ غير مسموح / Executable file not allowed",
                    error_code="EXECUTABLE_NOT_ALLOWED",
                )

    async def _scan_virus(self, file_content: bytes, filename: str) -> None:
        """
        Scan file for viruses
        فحص الملف بحثاً عن فيروسات
        """
        is_safe = await self.virus_scanner.scan(file_content, filename)

        if not is_safe:
            raise FileValidationError(
                "تم اكتشاف فيروس في الملف / Virus detected in file", error_code="VIRUS_DETECTED"
            )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks
    تعقيم اسم الملف لمنع هجمات اجتياز المسار وغيرها

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Get base name (remove any path components)
    filename = os.path.basename(filename)

    # Remove any null bytes
    filename = filename.replace("\x00", "")

    # Replace path separators with underscore
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove any leading dots to prevent hidden files
    filename = filename.lstrip(".")

    # Replace multiple spaces with single space
    filename = re.sub(r"\s+", " ", filename)

    # Remove or replace special characters (keep only alphanumeric, dots, hyphens, underscores)
    filename = re.sub(r"[^\w\s.-]", "_", filename)

    # Limit filename length (keep extension)
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_len = 255 - len(ext)
        filename = name[:max_name_len] + ext

    # If filename is empty after sanitization, generate a random one
    if not filename or filename == "_":
        import uuid

        filename = f"file_{uuid.uuid4().hex[:8]}"

    return filename


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    الحصول على امتداد الملف من اسم الملف

    Args:
        filename: Filename

    Returns:
        File extension (with dot) or empty string
    """
    return Path(filename).suffix


async def validate_file_upload(
    file_content: bytes,
    filename: str,
    declared_mime_type: str,
    config: FileValidationConfig | None = None,
    virus_scanner: VirusScannerInterface | None = None,
) -> dict:
    """
    Convenience function for file validation
    وظيفة ملائمة للتحقق من الملفات

    Args:
        file_content: File content as bytes
        filename: Original filename
        declared_mime_type: MIME type from upload header
        config: Optional validation configuration
        virus_scanner: Optional virus scanner

    Returns:
        Dictionary with validation results

    Raises:
        FileValidationError: If validation fails
    """
    validator = FileValidator(config=config, virus_scanner=virus_scanner)
    return await validator.validate(file_content, filename, declared_mime_type)
