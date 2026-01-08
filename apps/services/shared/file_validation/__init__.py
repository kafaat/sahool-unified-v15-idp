"""
SAHOOL File Upload Validation Module
وحدة التحقق من تحميل الملفات

Provides comprehensive file upload validation including:
- File size validation
- MIME type validation with whitelist
- Magic bytes validation
- Virus scanning integration point
- File sanitization

توفر التحقق الشامل من تحميل الملفات بما في ذلك:
- التحقق من حجم الملف
- التحقق من نوع MIME مع قائمة بيضاء
- التحقق من البايتات السحرية
- نقطة تكامل فحص الفيروسات
- تعقيم الملفات
"""

from .mime_types import (
    ALLOWED_ARCHIVE_TYPES,
    ALLOWED_DOCUMENT_TYPES,
    ALLOWED_IMAGE_TYPES,
    get_mime_from_magic_bytes,
)
from .validators import (
    FileValidationConfig,
    FileValidationError,
    FileValidator,
    get_file_extension,
    sanitize_filename,
    validate_file_upload,
)
from .virus_scanner import (
    ClamAVScanner,
    NoOpScanner,
    VirusScannerInterface,
)

__all__ = [
    "FileValidator",
    "FileValidationError",
    "FileValidationConfig",
    "validate_file_upload",
    "get_file_extension",
    "sanitize_filename",
    "ALLOWED_IMAGE_TYPES",
    "ALLOWED_DOCUMENT_TYPES",
    "ALLOWED_ARCHIVE_TYPES",
    "get_mime_from_magic_bytes",
    "VirusScannerInterface",
    "ClamAVScanner",
    "NoOpScanner",
]
