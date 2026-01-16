# SAHOOL File Upload Validation

## Overview

Comprehensive file upload validation module for SAHOOL services. Provides security-focused validation including:

- **File size validation** (configurable limits)
- **MIME type validation** with whitelist
- **Magic bytes validation** (content-based type detection)
- **Virus scanning integration** (ClamAV support)
- **Filename sanitization**
- **Executable detection and blocking**

## Features

### 1. File Size Validation

- Configurable maximum file size (default: 10MB)
- Empty file detection
- Clear error messages in English and Arabic

### 2. MIME Type Validation

- Whitelist-based MIME type checking
- Pre-configured lists for images, documents, archives, videos
- Custom MIME type lists supported

### 3. Magic Bytes Validation

- Content-based file type detection
- Prevents MIME type spoofing attacks
- Validates declared type matches actual content
- Strict and non-strict validation modes

### 4. Virus Scanning

- Pluggable virus scanner interface
- ClamAV integration (async)
- No-op scanner for development
- Cloud scanner stub for future integration

### 5. Security Features

- Executable file detection and blocking
- Path traversal protection in filenames
- Filename sanitization
- Null byte filtering

## Installation

The module is part of the shared utilities. No additional installation required.

```python
from shared.file_validation import (
    FileValidator,
    FileValidationConfig,
    FileValidationError,
    ALLOWED_IMAGE_TYPES,
    get_virus_scanner,
)
```

## Usage

### Basic Usage (FastAPI)

```python
from fastapi import FastAPI, File, HTTPException, UploadFile
from shared.file_validation import (
    FileValidator,
    FileValidationConfig,
    FileValidationError,
    ALLOWED_IMAGE_TYPES,
)

app = FastAPI()

# Initialize validator on startup
@app.on_event("startup")
async def startup_event():
    app.state.file_validator = FileValidator(
        config=FileValidationConfig(
            max_file_size=10 * 1024 * 1024,  # 10MB
            allowed_mime_types=ALLOWED_IMAGE_TYPES,
            check_magic_bytes=True,
            strict_mime_check=True,
            scan_for_viruses=False,
            allow_executable=False,
            sanitize_filename=True,
        )
    )

# Use in endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Read file content
    file_content = await file.read()

    # Validate
    try:
        result = await app.state.file_validator.validate(
            file_content=file_content,
            filename=file.filename,
            declared_mime_type=file.content_type,
        )

        # File is valid, proceed with processing
        return {
            "success": True,
            "filename": result["safe_filename"],
            "size": result["file_size"],
        }

    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
```

### With Virus Scanning (ClamAV)

```python
import os
from shared.file_validation import (
    FileValidator,
    FileValidationConfig,
    get_virus_scanner,
)

# Initialize with ClamAV scanner
virus_scanner = get_virus_scanner(
    scanner_type="clamav",
    host=os.getenv("CLAMAV_HOST", "localhost"),
    port=int(os.getenv("CLAMAV_PORT", "3310")),
)

validator = FileValidator(
    config=FileValidationConfig(
        max_file_size=10 * 1024 * 1024,
        allowed_mime_types=ALLOWED_IMAGE_TYPES,
        scan_for_viruses=True,
    ),
    virus_scanner=virus_scanner
)

# Use validator
result = await validator.validate(file_content, filename, mime_type)
```

### Custom Configuration

```python
from shared.file_validation import (
    FileValidationConfig,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_DOCUMENT_TYPES,
)

# Allow only images
config_images = FileValidationConfig(
    max_file_size=5 * 1024 * 1024,  # 5MB
    allowed_mime_types=ALLOWED_IMAGE_TYPES,
    check_magic_bytes=True,
    strict_mime_check=True,
)

# Allow images and documents
config_mixed = FileValidationConfig(
    max_file_size=20 * 1024 * 1024,  # 20MB
    allowed_mime_types=ALLOWED_IMAGE_TYPES + ALLOWED_DOCUMENT_TYPES,
    check_magic_bytes=True,
    strict_mime_check=False,  # More lenient
)

# Custom MIME types
config_custom = FileValidationConfig(
    max_file_size=50 * 1024 * 1024,
    allowed_mime_types=[
        "application/json",
        "text/csv",
        "application/xml",
    ],
    check_magic_bytes=False,  # Skip for text files
)
```

### Convenience Function

```python
from shared.file_validation import validate_file_upload, FileValidationConfig

# Quick validation without creating validator instance
result = await validate_file_upload(
    file_content=file_bytes,
    filename="photo.jpg",
    declared_mime_type="image/jpeg",
    config=FileValidationConfig(max_file_size=5 * 1024 * 1024)
)
```

## Configuration Options

### FileValidationConfig

| Parameter            | Type      | Default             | Description                        |
| -------------------- | --------- | ------------------- | ---------------------------------- |
| `max_file_size`      | int       | 10MB                | Maximum file size in bytes         |
| `allowed_mime_types` | List[str] | ALLOWED_IMAGE_TYPES | List of allowed MIME types         |
| `check_magic_bytes`  | bool      | True                | Validate content using magic bytes |
| `strict_mime_check`  | bool      | True                | Require exact MIME match           |
| `scan_for_viruses`   | bool      | False               | Enable virus scanning              |
| `allow_executable`   | bool      | False               | Allow executable files             |
| `sanitize_filename`  | bool      | True                | Sanitize uploaded filenames        |

## Predefined MIME Type Lists

```python
from shared.file_validation import (
    ALLOWED_IMAGE_TYPES,
    ALLOWED_DOCUMENT_TYPES,
    ALLOWED_ARCHIVE_TYPES,
    ALLOWED_VIDEO_TYPES,
)

# ALLOWED_IMAGE_TYPES
["image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp", "image/tiff"]

# ALLOWED_DOCUMENT_TYPES
["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ...]

# ALLOWED_ARCHIVE_TYPES
["application/zip", "application/x-tar", "application/gzip", ...]

# ALLOWED_VIDEO_TYPES
["video/mp4", "video/mpeg", "video/quicktime", ...]
```

## Error Handling

The validator raises `FileValidationError` with specific error codes:

```python
try:
    await validator.validate(file_content, filename, mime_type)
except FileValidationError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.error_code}")
```

### Error Codes

- `EMPTY_FILE`: File is empty
- `FILE_TOO_LARGE`: File exceeds maximum size
- `INVALID_MIME_TYPE`: MIME type not in whitelist
- `MIME_MISMATCH`: Declared MIME doesn't match content
- `EXECUTABLE_NOT_ALLOWED`: Executable file detected
- `VIRUS_DETECTED`: Virus found in file

## Virus Scanner Configuration

### Using ClamAV

1. Install ClamAV daemon:

```bash
# Ubuntu/Debian
sudo apt-get install clamav-daemon clamav-freshclam

# Start daemon
sudo systemctl start clamav-daemon
```

2. Configure in your service:

```python
virus_scanner = get_virus_scanner(
    scanner_type="clamav",
    host="localhost",
    port=3310,
)
```

3. Set environment variables:

```bash
export VIRUS_SCANNER=clamav
export CLAMAV_HOST=localhost
export CLAMAV_PORT=3310
```

### Docker Compose Example

```yaml
services:
  clamav:
    image: clamav/clamav:latest
    ports:
      - "3310:3310"
    volumes:
      - clamav-data:/var/lib/clamav
    environment:
      - CLAMAV_NO_FRESHCLAM=false
    healthcheck:
      test: ["CMD", "clamdscan", "--ping", "1"]
      interval: 30s
      timeout: 10s
      retries: 3

  your-service:
    build: .
    depends_on:
      clamav:
        condition: service_healthy
    environment:
      - VIRUS_SCANNER=clamav
      - CLAMAV_HOST=clamav
      - CLAMAV_PORT=3310

volumes:
  clamav-data:
```

## Best Practices

### 1. Always Validate File Content

Don't trust the declared MIME type or file extension. Always validate content.

### 2. Use Appropriate File Size Limits

- Images: 5-10MB
- Documents: 10-20MB
- Videos: 50-100MB
- Archives: 20-50MB

### 3. Enable Virus Scanning in Production

Use ClamAV or cloud scanning service for production environments.

### 4. Sanitize Filenames

Always enable filename sanitization to prevent path traversal attacks.

### 5. Log Validation Failures

Log failed validations for security monitoring:

```python
try:
    await validator.validate(...)
except FileValidationError as e:
    logger.warning(f"File validation failed: {e.message} (code: {e.error_code})")
    raise HTTPException(status_code=400, detail=e.message)
```

### 6. Use Strict Mode for Critical Applications

Enable strict MIME checking for applications handling sensitive data.

### 7. Implement Rate Limiting

Add rate limiting to file upload endpoints to prevent abuse:

```python
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

@app.post("/upload")
@limiter.limit("10/minute")  # 10 uploads per minute
async def upload_file(request: Request, file: UploadFile = File(...)):
    # ... validation logic
    pass
```

## Integration Examples

### Example 1: Image Upload Service

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from shared.file_validation import FileValidator, FileValidationConfig, ALLOWED_IMAGE_TYPES

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.state.validator = FileValidator(
        config=FileValidationConfig(
            max_file_size=5 * 1024 * 1024,  # 5MB for images
            allowed_mime_types=ALLOWED_IMAGE_TYPES,
            check_magic_bytes=True,
            strict_mime_check=True,
        )
    )

@app.post("/api/v1/upload-profile-photo")
async def upload_profile_photo(photo: UploadFile = File(...)):
    content = await photo.read()

    try:
        result = await app.state.validator.validate(
            file_content=content,
            filename=photo.filename,
            declared_mime_type=photo.content_type,
        )
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

    # Process validated image
    safe_filename = result["safe_filename"]
    # ... save to storage

    return {"success": True, "filename": safe_filename}
```

### Example 2: Document Upload with Virus Scanning

```python
import os
from shared.file_validation import (
    FileValidator,
    FileValidationConfig,
    ALLOWED_DOCUMENT_TYPES,
    get_virus_scanner,
)

@app.on_event("startup")
async def startup():
    scanner = get_virus_scanner(
        scanner_type=os.getenv("VIRUS_SCANNER", "noop"),
        host=os.getenv("CLAMAV_HOST", "localhost"),
        port=int(os.getenv("CLAMAV_PORT", "3310")),
    )

    app.state.validator = FileValidator(
        config=FileValidationConfig(
            max_file_size=20 * 1024 * 1024,  # 20MB for documents
            allowed_mime_types=ALLOWED_DOCUMENT_TYPES,
            scan_for_viruses=os.getenv("VIRUS_SCANNER") == "clamav",
        ),
        virus_scanner=scanner
    )
```

## Testing

### Unit Tests Example

```python
import pytest
from shared.file_validation import FileValidator, FileValidationConfig, FileValidationError

@pytest.mark.asyncio
async def test_valid_image():
    validator = FileValidator(config=FileValidationConfig())

    # PNG magic bytes
    png_content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100

    result = await validator.validate(
        file_content=png_content,
        filename="test.png",
        declared_mime_type="image/png"
    )

    assert result["valid"] is True
    assert result["detected_mime"] == "image/png"

@pytest.mark.asyncio
async def test_file_too_large():
    validator = FileValidator(
        config=FileValidationConfig(max_file_size=1024)  # 1KB
    )

    large_content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 2000  # 2KB

    with pytest.raises(FileValidationError) as exc:
        await validator.validate(
            file_content=large_content,
            filename="large.png",
            declared_mime_type="image/png"
        )

    assert exc.value.error_code == "FILE_TOO_LARGE"
```

## Security Considerations

1. **Never trust client-provided data**: Always validate content, not just headers
2. **Defense in depth**: Use multiple validation layers (size, type, content, virus scan)
3. **Fail securely**: When validation fails or errors occur, reject the file
4. **Monitor and log**: Track validation failures for security analysis
5. **Keep virus definitions updated**: Ensure ClamAV database is current
6. **Isolate file processing**: Process uploaded files in isolated environments
7. **Set appropriate timeouts**: Prevent DoS through slow uploads

## Troubleshooting

### ClamAV Connection Issues

```python
# Check if ClamAV is available
scanner = get_virus_scanner(scanner_type="clamav")
is_available = await scanner.is_available()
print(f"ClamAV available: {is_available}")
```

### MIME Type Mismatch

If you're getting MIME mismatch errors for valid files:

1. Use non-strict mode: `strict_mime_check=False`
2. Check if the MIME type is in your allowed list
3. Verify the file isn't corrupted

### Performance Optimization

For high-volume applications:

1. Disable virus scanning for small files
2. Use async processing for large files
3. Implement file size pre-check before full validation
4. Cache validation results for duplicate files (use file hash)

## Support

For issues or questions, please create an issue in the SAHOOL repository.

## License

Part of the SAHOOL unified platform.
