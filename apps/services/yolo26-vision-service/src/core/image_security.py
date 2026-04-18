"""
Image upload security validation for YOLO26 Vision Service.

Protects against image-decompression DoS attacks and malformed image
payloads by enforcing:
  - Magic-byte verification (JPEG/PNG/WebP only)
  - Content-Type / magic-byte agreement
  - Size cap (existing ``settings.max_upload_size_bytes``)
  - Pillow decompression-bomb guard (``Image.MAX_IMAGE_PIXELS``)
  - ``Image.verify()`` round-trip check on every upload

All user-facing errors are bilingual (Arabic / English) to match the
surrounding endpoints.
"""

from __future__ import annotations

import io

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from src.core.config import settings

# Cap Pillow's decompression-bomb guard at 40 Mpx. This covers plausible
# agricultural imagery (e.g. 8K drone stills ~33 Mpx) while rejecting the
# crafted multi-gigapixel payloads used in DoS attacks.
Image.MAX_IMAGE_PIXELS = 40_000_000

# Magic-byte signatures for the three supported image containers.
# Keys are ``(offset, signature_bytes)`` tuples; matching is performed
# with a simple ``startswith``/slice equality on the uploaded buffer.
_MAGIC_SIGNATURES: dict[str, tuple[int, bytes]] = {
    "image/jpeg": (0, b"\xff\xd8\xff"),
    "image/png": (0, b"\x89PNG\r\n\x1a\n"),
    # WebP uses a RIFF container; the "WEBP" marker lives at byte 8.
    "image/webp": (8, b"WEBP"),
}


def _detect_format(buf: bytes) -> str | None:
    """Return the detected MIME type from the first bytes, or None."""
    for mime, (offset, sig) in _MAGIC_SIGNATURES.items():
        end = offset + len(sig)
        if len(buf) >= end and buf[offset:end] == sig:
            # WebP also requires the RIFF header at offset 0.
            if mime == "image/webp" and not buf.startswith(b"RIFF"):
                continue
            return mime
    return None


def _reject(code: int, error: str, message: str, message_ar: str) -> None:
    raise HTTPException(
        status_code=code,
        detail={"error": error, "message": message, "message_ar": message_ar},
    )


async def validate_image_upload(file: UploadFile) -> bytes:
    """
    Validate an uploaded image and return its raw bytes.

    Enforces (in order):
      1. Non-empty ``Content-Type`` starting with ``image/``.
      2. Size within ``settings.max_upload_size_bytes``.
      3. Magic-byte match for JPEG / PNG / WebP.
      4. Agreement between the magic bytes and the declared Content-Type.
      5. Successful ``Image.verify()`` round-trip.

    Raises:
        HTTPException: 400 on format / integrity failures,
                       413 when the payload exceeds the size cap.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        _reject(
            status.HTTP_400_BAD_REQUEST,
            "Invalid file type",
            "File must be an image (JPEG, PNG, WebP)",
            "يجب أن يكون الملف صورة (JPEG، PNG، WebP)",
        )

    content = await file.read()

    if len(content) > settings.max_upload_size_bytes:
        _reject(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            "File too large",
            f"Maximum file size is {settings.max_upload_size_mb}MB",
            f"الحد الأقصى لحجم الملف هو {settings.max_upload_size_mb} ميجابايت",
        )

    detected = _detect_format(content)
    if detected is None:
        _reject(
            status.HTTP_400_BAD_REQUEST,
            "Unsupported image format",
            "unsupported image format",
            "تنسيق الصورة غير مدعوم",
        )

    # Magic bytes and declared Content-Type must agree — if not, reject.
    # Accept common synonyms (image/jpg ↔ image/jpeg).
    declared = (file.content_type or "").lower()
    declared_norm = "image/jpeg" if declared in {"image/jpg", "image/pjpeg"} else declared
    if declared_norm != detected:
        _reject(
            status.HTTP_400_BAD_REQUEST,
            "Content-Type mismatch",
            "unsupported image format",
            "تنسيق الصورة غير مدعوم",
        )

    # Integrity check. ``verify`` consumes the stream, so we parse a fresh
    # ``BytesIO`` each time the caller wants to decode the image again.
    try:
        with Image.open(io.BytesIO(content)) as probe:
            probe.verify()
    except Exception:
        _reject(
            status.HTTP_400_BAD_REQUEST,
            "Corrupt image",
            "unsupported image format",
            "تنسيق الصورة غير مدعوم",
        )

    return content
