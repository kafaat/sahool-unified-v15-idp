# File Upload Validation - Implementation Summary

## Overview

Comprehensive file upload validation has been added to SAHOOL services to enhance security and prevent common file upload vulnerabilities.

## What Was Implemented

### 1. Shared Validation Module

Created a centralized file validation module at `/shared/file_validation/` with:

- **Core Validators** (`validators.py`)
  - File size validation (default 10MB limit)
  - MIME type whitelist validation
  - Magic bytes content validation
  - Executable file detection
  - Filename sanitization
  - Async validation support

- **MIME Type Support** (`mime_types.py`)
  - Pre-configured MIME type whitelists (images, documents, archives, videos)
  - Magic bytes signature detection
  - MIME type matching validation
  - Support for 20+ common file types

- **Virus Scanner Integration** (`virus_scanner.py`)
  - Abstract scanner interface
  - ClamAV implementation (async)
  - NoOp scanner for development
  - Cloud scanner stub for future integration

- **Documentation & Examples**
  - Comprehensive README with usage examples
  - Example code for common scenarios
  - Best practices and security guidelines

## Updated Services

### 1. Crop Health AI Service
**Location:** `/apps/services/crop-health-ai/src/main.py`

**Updated Endpoints:**
1. `POST /v1/diagnose` - Single plant image diagnosis
2. `POST /v1/diagnose/batch` - Batch image diagnosis (up to 20 images)
3. `POST /v1/expert-review` - Expert review request with image
4. `POST /v1/diagnose-with-action` - Diagnosis with action template (uses diagnose endpoint)

**Validation Applied:**
- ✅ File size validation (10MB limit)
- ✅ MIME type whitelist (image types only)
- ✅ Magic bytes validation
- ✅ Virus scanning integration point (configurable)
- ✅ Filename sanitization
- ✅ Executable blocking
- ✅ Fallback to basic validation if module unavailable

**Configuration:**
```python
# Environment variables
VIRUS_SCANNER=clamav|noop  # Default: noop
CLAMAV_HOST=localhost      # Default: localhost
CLAMAV_PORT=3310          # Default: 3310
```

## Validation Features

### 1. File Size Limits
- **Default:** 10MB
- **Configurable per service**
- **Error message:** Bilingual (English/Arabic)

### 2. MIME Type Validation
**Allowed image types:**
- image/jpeg
- image/jpg
- image/png
- image/gif
- image/webp
- image/bmp
- image/tiff

**Validation process:**
1. Check declared MIME type against whitelist
2. Validate content using magic bytes
3. Ensure declared type matches actual content

### 3. Magic Bytes Validation
**Detects actual file type by content:**
- JPEG: `FF D8 FF`
- PNG: `89 50 4E 47 0D 0A 1A 0A`
- GIF: `47 49 46 38`
- PDF: `25 50 44 46`
- And 15+ more types

### 4. Content Validation
- Checks first 32 bytes of file
- Prevents MIME type spoofing
- Strict and non-strict modes available

### 5. Virus Scanning
**ClamAV Integration:**
- Async scanning via clamd
- INSTREAM protocol for memory-safe scanning
- Configurable timeout (30s default)
- Health check support

**Fallback modes:**
- Development: NoOp scanner (no actual scanning)
- Production: ClamAV required for virus scanning

### 6. Security Features
**Executable Detection:**
- Extension-based blocking (.exe, .bat, .sh, etc.)
- Magic bytes detection (PE, ELF, scripts)
- Prevents code execution attacks

**Filename Sanitization:**
- Path traversal protection
- Null byte filtering
- Special character removal
- Length limiting (255 chars)
- Hidden file prevention

## Services Analyzed (No File Uploads Found)

The following services were analyzed but no file upload endpoints were found:

### NestJS Services
- chat-service
- crop-growth-model
- disaster-assessment
- iot-service
- lai-estimation
- marketplace-service
- research-core
- user-service
- yield-prediction
- yield-prediction-service

### FastAPI Services (No File Uploads)
- crop-intelligence-service
- field-ops
- satellite-service
- vegetation-analysis-service
- weather-service
- advisory-service
- agent-registry
- alert-service
- agro-advisor
- ai-advisor
- ai-agents-core (only has examples)
- astronomical-calendar
- billing-core
- equipment-service
- fertilizer-advisor
- field-chat
- field-intelligence
- field-management-service
- field-service
- globalgap-compliance
- indicators-service
- inventory-service
- iot-gateway
- irrigation-smart
- mcp-server
- ndvi-processor
- notification-service
- provider-config
- task-service
- virtual-sensors
- weather-advanced
- weather-core
- ws-gateway
- yield-engine
- field-core
- crop-health
- ndvi-engine

**Note:** The code-review-service has file path-based review but not traditional file uploads.

## Integration Guide

### For FastAPI Services

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from shared.file_validation import (
    FileValidator,
    FileValidationConfig,
    FileValidationError,
    ALLOWED_IMAGE_TYPES,
    get_virus_scanner,
)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Initialize virus scanner
    virus_scanner_type = os.getenv("VIRUS_SCANNER", "noop")
    app.state.virus_scanner = get_virus_scanner(
        virus_scanner_type,
        host=os.getenv("CLAMAV_HOST", "localhost"),
        port=int(os.getenv("CLAMAV_PORT", "3310"))
    )

    # Initialize file validator
    app.state.file_validator = FileValidator(
        config=FileValidationConfig(
            max_file_size=10 * 1024 * 1024,  # 10MB
            allowed_mime_types=ALLOWED_IMAGE_TYPES,
            check_magic_bytes=True,
            strict_mime_check=True,
            scan_for_viruses=virus_scanner_type != "noop",
            allow_executable=False,
            sanitize_filename=True,
        ),
        virus_scanner=app.state.virus_scanner
    )

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
        # Process validated file
        return {"success": True, "filename": result["safe_filename"]}
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
```

### For NestJS Services

```typescript
import { Controller, Post, UseInterceptors, UploadedFile, BadRequestException } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';

@Controller('upload')
export class UploadController {
  @Post()
  @UseInterceptors(
    FileInterceptor('file', {
      limits: {
        fileSize: 10 * 1024 * 1024, // 10MB
      },
      fileFilter: (req, file, cb) => {
        const allowedMimes = [
          'image/jpeg',
          'image/png',
          'image/gif',
          'image/webp'
        ];

        if (allowedMimes.includes(file.mimetype)) {
          cb(null, true);
        } else {
          cb(new BadRequestException('Invalid file type'), false);
        }
      },
    })
  )
  async uploadFile(@UploadedFile() file: Express.Multer.File) {
    // Additional validation for magic bytes
    const buffer = file.buffer;
    const isPNG = buffer[0] === 0x89 && buffer[1] === 0x50;
    const isJPEG = buffer[0] === 0xFF && buffer[1] === 0xD8;

    if (!isPNG && !isJPEG && file.mimetype.startsWith('image/')) {
      throw new BadRequestException('File content does not match declared type');
    }

    // Process validated file
    return {
      success: true,
      filename: file.originalname,
      size: file.size,
    };
  }
}
```

## Environment Configuration

### Development
```bash
# No virus scanning
VIRUS_SCANNER=noop
```

### Production
```bash
# Enable ClamAV scanning
VIRUS_SCANNER=clamav
CLAMAV_HOST=clamav-service
CLAMAV_PORT=3310
```

### Docker Compose
```yaml
services:
  clamav:
    image: clamav/clamav:latest
    ports:
      - "3310:3310"
    volumes:
      - clamav-data:/var/lib/clamav
    healthcheck:
      test: ["CMD", "clamdscan", "--ping", "1"]
      interval: 30s

  crop-health-ai:
    build: ./apps/services/crop-health-ai
    environment:
      - VIRUS_SCANNER=clamav
      - CLAMAV_HOST=clamav
      - CLAMAV_PORT=3310
    depends_on:
      clamav:
        condition: service_healthy

volumes:
  clamav-data:
```

## Error Responses

All validation errors return HTTP 400 with bilingual error messages:

```json
{
  "detail": "حجم الصورة كبير جداً (الحد الأقصى 10 ميجابايت) / File too large. Maximum 10MB"
}
```

### Error Codes
- `EMPTY_FILE`: File is empty
- `FILE_TOO_LARGE`: Exceeds size limit
- `INVALID_MIME_TYPE`: Type not in whitelist
- `MIME_MISMATCH`: Declared type doesn't match content
- `EXECUTABLE_NOT_ALLOWED`: Executable file detected
- `VIRUS_DETECTED`: Virus found (ClamAV)

## Security Benefits

1. **Prevents MIME Type Spoofing:** Magic bytes validation
2. **Blocks Malicious Files:** Virus scanning integration
3. **Prevents Code Execution:** Executable detection
4. **Protects File System:** Filename sanitization
5. **Prevents DoS:** File size limits
6. **Defense in Depth:** Multiple validation layers

## Testing

### Manual Testing
```bash
# Test valid image upload
curl -X POST http://localhost:8095/v1/diagnose \
  -F "image=@test_image.jpg" \
  -F "field_id=FIELD-001"

# Test invalid file type
curl -X POST http://localhost:8095/v1/diagnose \
  -F "image=@malicious.exe" \
  -F "field_id=FIELD-001"

# Test oversized file (>10MB)
curl -X POST http://localhost:8095/v1/diagnose \
  -F "image=@large_file.jpg" \
  -F "field_id=FIELD-001"
```

### Unit Testing
See `/shared/file_validation/examples.py` for comprehensive test examples.

## Performance Considerations

1. **File Size Validation:** O(1) - instant
2. **MIME Type Validation:** O(1) - instant
3. **Magic Bytes Check:** O(1) - checks first 32 bytes only
4. **Filename Sanitization:** O(n) - where n is filename length
5. **Virus Scanning:** O(file_size) - can be slow for large files

**Recommendations:**
- Disable virus scanning for files < 1MB if performance critical
- Use async processing for large files
- Implement rate limiting on upload endpoints

## Future Improvements

1. **Cloud Virus Scanning:** Integrate AWS S3 Malware Scanning or VirusTotal
2. **Image Dimension Validation:** Check resolution limits
3. **File Format Validation:** Deep file structure validation
4. **Content Analysis:** AI-based inappropriate content detection
5. **Duplicate Detection:** Hash-based duplicate file detection
6. **Quarantine System:** Automatic quarantine for suspicious files

## Monitoring

### Metrics to Track
- Upload attempts per endpoint
- Validation failures by type
- File sizes distribution
- Virus detections (if any)
- Processing time per validation

### Logging
All validation failures are logged with:
- Timestamp
- Endpoint
- Filename
- Error code
- Client IP (if available)

## Compliance

This implementation helps meet:
- **OWASP Top 10:** Addresses unrestricted file upload vulnerabilities
- **PCI DSS:** File upload security requirements
- **GDPR:** Data protection through security measures
- **ISO 27001:** Information security controls

## Documentation

- **Full Documentation:** `/shared/file_validation/README.md`
- **Examples:** `/shared/file_validation/examples.py`
- **This Summary:** `/docs/file-upload-validation-summary.md`

## Support

For questions or issues:
1. Check the README in `/shared/file_validation/`
2. Review examples in `/shared/file_validation/examples.py`
3. Create an issue in the SAHOOL repository

---

**Implementation Date:** January 2026
**Status:** ✅ Complete
**Affected Services:** 1 (crop-health-ai)
**Lines of Code Added:** ~1,000+
**Security Level:** High
