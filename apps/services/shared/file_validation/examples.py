"""
Examples of using SAHOOL File Validation Module
أمثلة على استخدام وحدة التحقق من الملفات في SAHOOL
"""

import asyncio
from pathlib import Path

from .mime_types import (
    ALLOWED_DOCUMENT_TYPES,
    ALLOWED_IMAGE_TYPES,
    get_mime_from_magic_bytes,
)
from .validators import (
    FileValidationConfig,
    FileValidationError,
    FileValidator,
    sanitize_filename,
)
from .virus_scanner import get_virus_scanner


async def example_basic_validation():
    """
    Example 1: Basic file validation
    مثال 1: التحقق الأساسي من الملفات
    """
    print("=" * 70)
    print("Example 1: Basic File Validation")
    print("مثال 1: التحقق الأساسي من الملفات")
    print("=" * 70)

    # Create validator with default configuration
    validator = FileValidator()

    # Sample PNG file content (just the header)
    png_header = b"\x89PNG\r\n\x1a\n"
    sample_content = png_header + b"\x00" * 1000  # Add some padding

    try:
        result = await validator.validate(
            file_content=sample_content, filename="test_image.png", declared_mime_type="image/png"
        )

        print("\n✅ Validation successful!")
        print(f"Original filename: {result['original_filename']}")
        print(f"Safe filename: {result['safe_filename']}")
        print(f"Declared MIME: {result['declared_mime']}")
        print(f"Detected MIME: {result['detected_mime']}")
        print(f"File size: {result['file_size']} bytes")

    except FileValidationError as e:
        print(f"\n❌ Validation failed: {e.message}")
        print(f"Error code: {e.error_code}")


async def example_custom_configuration():
    """
    Example 2: Custom validation configuration
    مثال 2: إعدادات التحقق المخصصة
    """
    print("\n" + "=" * 70)
    print("Example 2: Custom Configuration")
    print("مثال 2: إعدادات مخصصة")
    print("=" * 70)

    # Create custom configuration for documents
    config = FileValidationConfig(
        max_file_size=20 * 1024 * 1024,  # 20MB
        allowed_mime_types=ALLOWED_DOCUMENT_TYPES,
        check_magic_bytes=True,
        strict_mime_check=False,  # More lenient
        scan_for_viruses=False,
        allow_executable=False,
        sanitize_filename=True,
    )

    validator = FileValidator(config=config)

    # Sample PDF content
    pdf_header = b"%PDF-1.4"
    sample_pdf = pdf_header + b"\x00" * 2000

    try:
        result = await validator.validate(
            file_content=sample_pdf, filename="document.pdf", declared_mime_type="application/pdf"
        )

        print("\n✅ PDF validation successful!")
        print(f"Configuration: max_size={config.max_file_size / (1024 * 1024)}MB")
        print(f"Allowed types: {len(config.allowed_mime_types)} document types")
        print(f"Validated file: {result['safe_filename']}")

    except FileValidationError as e:
        print(f"\n❌ Validation failed: {e.message}")


async def example_virus_scanning():
    """
    Example 3: Virus scanning integration
    مثال 3: تكامل فحص الفيروسات
    """
    print("\n" + "=" * 70)
    print("Example 3: Virus Scanning")
    print("مثال 3: فحص الفيروسات")
    print("=" * 70)

    # Get virus scanner (ClamAV or NoOp)
    virus_scanner = get_virus_scanner(
        scanner_type="clamav",  # Change to "noop" if ClamAV not available
        host="localhost",
        port=3310,
    )

    # Check if scanner is available
    is_available = await virus_scanner.is_available()
    print(f"\nVirus scanner available: {is_available}")

    if not is_available:
        print("⚠️  ClamAV not available. Using NoOp scanner for demonstration.")
        virus_scanner = get_virus_scanner(scanner_type="noop")

    # Create validator with virus scanning
    config = FileValidationConfig(
        max_file_size=10 * 1024 * 1024,
        allowed_mime_types=ALLOWED_IMAGE_TYPES,
        scan_for_viruses=True,
    )

    validator = FileValidator(config=config, virus_scanner=virus_scanner)

    # Sample image
    jpg_header = b"\xff\xd8\xff"
    sample_image = jpg_header + b"\x00" * 5000

    try:
        result = await validator.validate(
            file_content=sample_image, filename="photo.jpg", declared_mime_type="image/jpeg"
        )

        print("\n✅ Validation with virus scanning successful!")
        print(f"Scanned for viruses: {result['scanned_for_viruses']}")

    except FileValidationError as e:
        print(f"\n❌ Validation failed: {e.message}")


async def example_mime_type_detection():
    """
    Example 4: MIME type detection from magic bytes
    مثال 4: كشف نوع MIME من البايتات السحرية
    """
    print("\n" + "=" * 70)
    print("Example 4: MIME Type Detection")
    print("مثال 4: كشف نوع MIME")
    print("=" * 70)

    # Test different file types
    test_files = [
        (b"\xff\xd8\xff", "JPEG"),
        (b"\x89PNG\r\n\x1a\n", "PNG"),
        (b"GIF89a", "GIF"),
        (b"%PDF", "PDF"),
        (b"PK\x03\x04", "ZIP/Office"),
    ]

    for magic_bytes, file_type in test_files:
        sample = magic_bytes + b"\x00" * 100
        detected_mime = get_mime_from_magic_bytes(sample)
        print(f"{file_type:15} -> {detected_mime}")


def example_filename_sanitization():
    """
    Example 5: Filename sanitization
    مثال 5: تعقيم أسماء الملفات
    """
    print("\n" + "=" * 70)
    print("Example 5: Filename Sanitization")
    print("مثال 5: تعقيم أسماء الملفات")
    print("=" * 70)

    # Test various problematic filenames
    test_filenames = [
        "../../etc/passwd",
        "file<script>alert('xss')</script>.jpg",
        "../../../sensitive.txt",
        "file\x00.txt.exe",
        "normal_file.jpg",
        "ملف_عربي.png",
        "file   with   spaces.pdf",
        ".hidden_file",
        "very" + "_long" * 100 + ".txt",
    ]

    print("\nOriginal -> Sanitized")
    print("-" * 70)
    for filename in test_filenames:
        safe = sanitize_filename(filename)
        print(f"{filename[:40]:40} -> {safe}")


async def example_error_handling():
    """
    Example 6: Error handling
    مثال 6: معالجة الأخطاء
    """
    print("\n" + "=" * 70)
    print("Example 6: Error Handling")
    print("مثال 6: معالجة الأخطاء")
    print("=" * 70)

    validator = FileValidator(
        config=FileValidationConfig(max_file_size=1024)  # Very small: 1KB
    )

    # Test 1: File too large
    print("\nTest 1: File too large")
    large_file = b"\x89PNG\r\n\x1a\n" + b"\x00" * 2000  # 2KB
    try:
        await validator.validate(large_file, "large.png", "image/png")
    except FileValidationError as e:
        print(f"❌ {e.error_code}: {e.message}")

    # Test 2: Empty file
    print("\nTest 2: Empty file")
    try:
        await validator.validate(b"", "empty.png", "image/png")
    except FileValidationError as e:
        print(f"❌ {e.error_code}: {e.message}")

    # Test 3: Invalid MIME type
    print("\nTest 3: Invalid MIME type")
    pdf_content = b"%PDF-1.4" + b"\x00" * 100
    try:
        await validator.validate(pdf_content, "doc.pdf", "application/pdf")
    except FileValidationError as e:
        print(f"❌ {e.error_code}: {e.message}")

    # Test 4: MIME mismatch (declared PNG, actually JPEG)
    print("\nTest 4: MIME type mismatch")
    jpg_content = b"\xff\xd8\xff" + b"\x00" * 100
    try:
        await validator.validate(jpg_content, "fake.png", "image/png")
    except FileValidationError as e:
        print(f"❌ {e.error_code}: {e.message}")


async def example_batch_validation():
    """
    Example 7: Batch file validation
    مثال 7: التحقق من دفعة من الملفات
    """
    print("\n" + "=" * 70)
    print("Example 7: Batch Validation")
    print("مثال 7: التحقق من دفعة من الملفات")
    print("=" * 70)

    validator = FileValidator()

    # Sample files
    files = [
        (b"\x89PNG\r\n\x1a\n" + b"\x00" * 1000, "image1.png", "image/png"),
        (b"\xff\xd8\xff" + b"\x00" * 1000, "image2.jpg", "image/jpeg"),
        (b"GIF89a" + b"\x00" * 1000, "image3.gif", "image/gif"),
        (b"%PDF-1.4" + b"\x00" * 1000, "doc.pdf", "application/pdf"),  # Should fail
    ]

    valid_files = []
    invalid_files = []

    for content, filename, mime_type in files:
        try:
            result = await validator.validate(content, filename, mime_type)
            valid_files.append(result)
            print(f"✅ {filename}: Valid")
        except FileValidationError as e:
            invalid_files.append((filename, e.error_code))
            print(f"❌ {filename}: {e.error_code}")

    print("\nSummary:")
    print(f"Valid files: {len(valid_files)}")
    print(f"Invalid files: {len(invalid_files)}")


async def main():
    """
    Run all examples
    تشغيل جميع الأمثلة
    """
    print("\n" + "═" * 70)
    print("SAHOOL File Validation Examples")
    print("أمثلة التحقق من الملفات في SAHOOL")
    print("═" * 70)

    # Run all async examples
    await example_basic_validation()
    await example_custom_configuration()
    await example_virus_scanning()
    await example_mime_type_detection()
    example_filename_sanitization()
    await example_error_handling()
    await example_batch_validation()

    print("\n" + "═" * 70)
    print("All examples completed!")
    print("اكتملت جميع الأمثلة!")
    print("═" * 70)


if __name__ == "__main__":
    asyncio.run(main())
