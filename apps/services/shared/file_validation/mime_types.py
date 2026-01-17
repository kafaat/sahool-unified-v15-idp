"""
MIME Type Definitions and Magic Bytes Validation
تعريفات أنواع MIME والتحقق من البايتات السحرية
"""

# MIME Type Whitelists - قوائم بيضاء لأنواع MIME
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
]

ALLOWED_DOCUMENT_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
]

ALLOWED_ARCHIVE_TYPES = [
    "application/zip",
    "application/x-zip-compressed",
    "application/x-tar",
    "application/gzip",
    "application/x-7z-compressed",
]

ALLOWED_VIDEO_TYPES = [
    "video/mp4",
    "video/mpeg",
    "video/quicktime",
    "video/x-msvideo",
    "video/webm",
]

# Magic Bytes for common file types - البايتات السحرية لأنواع الملفات الشائعة
# Format: (magic_bytes, mime_type, extension)
MAGIC_BYTES_SIGNATURES: list[tuple[bytes, str, str]] = [
    # Images
    (b"\xff\xd8\xff", "image/jpeg", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "image/png", "png"),
    (b"GIF87a", "image/gif", "gif"),
    (b"GIF89a", "image/gif", "gif"),
    (b"RIFF", "image/webp", "webp"),  # followed by WEBP
    (b"BM", "image/bmp", "bmp"),
    (b"II*\x00", "image/tiff", "tiff"),  # Little-endian TIFF
    (b"MM\x00*", "image/tiff", "tiff"),  # Big-endian TIFF
    # Documents
    (b"%PDF", "application/pdf", "pdf"),
    (b"PK\x03\x04", "application/zip", "zip"),  # Also used by docx, xlsx, etc.
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "application/msword", "doc"),  # MS Office
    # Archives
    (b"\x1f\x8b", "application/gzip", "gz"),
    (b"7z\xbc\xaf\x27\x1c", "application/x-7z-compressed", "7z"),
    (b"Rar!\x1a\x07", "application/x-rar-compressed", "rar"),
    # Video
    (b"\x00\x00\x00\x18ftypmp42", "video/mp4", "mp4"),
    (b"\x00\x00\x00\x1cftypmp42", "video/mp4", "mp4"),
    (b"\x00\x00\x00\x20ftypmp42", "video/mp4", "mp4"),
]


def get_mime_from_magic_bytes(file_bytes: bytes, max_check: int = 32) -> str | None:
    """
    Detect MIME type from file magic bytes
    كشف نوع MIME من البايتات السحرية للملف

    Args:
        file_bytes: First bytes of the file
        max_check: Maximum bytes to check (default: 32)

    Returns:
        MIME type string or None if not detected
    """
    if not file_bytes:
        return None

    # Check only the first max_check bytes
    header = file_bytes[:max_check]

    for magic_bytes, mime_type, _ in MAGIC_BYTES_SIGNATURES:
        if header.startswith(magic_bytes):
            return mime_type

    return None


def validate_mime_match(declared_mime: str, file_bytes: bytes, strict: bool = True) -> bool:
    """
    Validate that declared MIME type matches file content
    التحقق من تطابق نوع MIME المعلن مع محتوى الملف

    Args:
        declared_mime: MIME type from file header
        file_bytes: First bytes of the file
        strict: If True, requires exact match. If False, allows similar types.

    Returns:
        True if MIME type matches content
    """
    detected_mime = get_mime_from_magic_bytes(file_bytes)

    if not detected_mime:
        # If we can't detect, allow in non-strict mode
        return not strict

    if strict:
        return declared_mime == detected_mime

    # In non-strict mode, check if they're in the same category
    declared_category = declared_mime.split("/")[0]
    detected_category = detected_mime.split("/")[0]

    return declared_category == detected_category


def is_mime_allowed(mime_type: str, allowed_types: list[str]) -> bool:
    """
    Check if MIME type is in allowed list
    التحقق من وجود نوع MIME في القائمة المسموحة

    Args:
        mime_type: MIME type to check
        allowed_types: List of allowed MIME types

    Returns:
        True if MIME type is allowed
    """
    return mime_type in allowed_types


def get_extension_from_mime(mime_type: str) -> str | None:
    """
    Get file extension from MIME type
    الحصول على امتداد الملف من نوع MIME

    Args:
        mime_type: MIME type

    Returns:
        File extension (without dot) or None
    """
    mime_to_ext: dict[str, str] = {
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/bmp": "bmp",
        "image/tiff": "tiff",
        "application/pdf": "pdf",
        "application/zip": "zip",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/plain": "txt",
        "text/csv": "csv",
        "video/mp4": "mp4",
        "video/mpeg": "mpeg",
    }

    return mime_to_ext.get(mime_type)
