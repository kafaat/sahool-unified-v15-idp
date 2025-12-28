# GlobalGAP Supply Chain Portal API Client
# عميل واجهة برمجة بوابة سلسلة التوريد GlobalGAP

## Overview / نظرة عامة

This client provides integration with GlobalGAP's Supply Chain Portal API for certificate verification and producer search functionality. It is designed to be reusable across all SAHOOL services.

يوفر هذا العميل التكامل مع واجهة برمجة بوابة سلسلة التوريد GlobalGAP لوظائف التحقق من الشهادات والبحث عن المنتجين. تم تصميمه ليكون قابلاً لإعادة الاستخدام عبر جميع خدمات SAHOOL.

## Features / المميزات

- ✅ **Async/Await Support** - Built with httpx for high-performance async operations
- ✅ **Certificate Verification** - Verify GlobalGAP certificates by GGN number
- ✅ **Producer Search** - Search for certified producers and farms
- ✅ **Batch Operations** - Verify multiple certificates concurrently
- ✅ **Rate Limiting** - Built-in token bucket rate limiter
- ✅ **Retry Logic** - Automatic retry with exponential backoff
- ✅ **Mock Mode** - Test without real API access
- ✅ **Arabic Support** - Full bilingual error messages and documentation
- ✅ **Type Safety** - Full type hints and Pydantic-compatible models
- ✅ **Error Handling** - Comprehensive custom exceptions
- ✅ **Logging** - Structured logging with structlog

## Installation / التثبيت

The client is part of the SAHOOL shared library. Ensure the following dependencies are installed:

العميل جزء من مكتبة SAHOOL المشتركة. تأكد من تثبيت التبعيات التالية:

```bash
pip install httpx==0.28.1 structlog==24.4.0 tenacity==8.5.0
```

## Quick Start / البداية السريعة

### Basic Usage / الاستخدام الأساسي

```python
from shared.globalgap import GlobalGAPClient

# Initialize client
client = GlobalGAPClient(
    api_key="your-api-key",
    mock_mode=False,  # Set to True for testing
)

# Verify a certificate
cert = await client.verify_certificate("4063061891234")
print(f"Status: {cert.status}")
print(f"Valid: {cert.is_valid()}")
```

### Using Context Manager / استخدام مدير السياق

```python
async with GlobalGAPClient(api_key="your-key") as client:
    cert = await client.verify_certificate("4063061891234")
    print(f"Expires in {cert.days_until_expiry()} days")
```

## API Reference / مرجع واجهة البرمجة

### GlobalGAPClient

Main client class for interacting with GlobalGAP API.

الفئة الرئيسية للعميل للتفاعل مع واجهة برمجة GlobalGAP.

#### Constructor / المُنشئ

```python
GlobalGAPClient(
    api_key: Optional[str] = None,
    base_url: str = "https://www.globalgap.org/api/v1",
    timeout: int = 30,
    max_retries: int = 3,
    rate_limit: int = 10,
    rate_limit_period: int = 60,
    mock_mode: bool = False,
)
```

**Parameters:**

- `api_key`: GlobalGAP API key (optional for mock mode)
- `base_url`: Base URL for the API
- `timeout`: Request timeout in seconds (default: 30)
- `max_retries`: Maximum number of retry attempts (default: 3)
- `rate_limit`: Number of requests allowed per period (default: 10)
- `rate_limit_period`: Rate limit period in seconds (default: 60)
- `mock_mode`: Enable mock mode for testing (default: False)

#### Methods / الطرق

##### verify_certificate

Verify a GlobalGAP certificate by GGN number.

التحقق من شهادة GlobalGAP بواسطة رقم GGN.

```python
async def verify_certificate(self, ggn: str) -> CertificateInfo
```

**Parameters:**
- `ggn`: GlobalGAP Number (13 digits starting with 4)

**Returns:** `CertificateInfo` object

**Raises:**
- `InvalidGGN`: If GGN format is invalid
- `CertificateNotFound`: If certificate doesn't exist
- `GlobalGAPAPIError`: On API errors

**Example:**
```python
cert = await client.verify_certificate("4063061891234")
if cert.is_valid():
    print(f"Valid until: {cert.valid_to}")
```

##### get_certificate_status

Get certificate status only (lightweight operation).

الحصول على حالة الشهادة فقط (عملية خفيفة).

```python
async def get_certificate_status(self, ggn: str) -> CertificateStatus
```

**Parameters:**
- `ggn`: GlobalGAP Number

**Returns:** `CertificateStatus` enum value

**Example:**
```python
status = await client.get_certificate_status("4063061891234")
if status == CertificateStatus.VALID:
    print("Certificate is valid")
```

##### search_producers

Search for certified producers.

البحث عن المنتجين المعتمدين.

```python
async def search_producers(
    self,
    query: str,
    country: Optional[str] = None,
    product_category: Optional[str] = None,
    limit: int = 20,
) -> List[Producer]
```

**Parameters:**
- `query`: Search query (name, location, etc.)
- `country`: Filter by country code (ISO 2-letter)
- `product_category`: Filter by product category
- `limit`: Maximum number of results (default: 20)

**Returns:** List of `Producer` objects

**Example:**
```python
producers = await client.search_producers(
    query="organic farm",
    country="SA",
    product_category="vegetables"
)
```

##### batch_verify_certificates

Verify multiple certificates concurrently.

التحقق من شهادات متعددة بشكل متزامن.

```python
async def batch_verify_certificates(
    self,
    ggns: List[str]
) -> Dict[str, CertificateInfo]
```

**Parameters:**
- `ggns`: List of GlobalGAP Numbers

**Returns:** Dictionary mapping GGN to CertificateInfo

**Example:**
```python
results = await client.batch_verify_certificates([
    "4063061891234",
    "4063061891235",
])
for ggn, cert in results.items():
    print(f"{ggn}: {cert.status}")
```

### Data Models / نماذج البيانات

#### CertificateInfo

Certificate information model.

نموذج معلومات الشهادة.

```python
@dataclass
class CertificateInfo:
    ggn: str
    status: CertificateStatus
    valid_from: datetime
    valid_to: datetime
    scope: str
    cb_name: str
    product_categories: List[str]
    producer_name: Optional[str]
    country: Optional[str]
    sub_scopes: List[str]
    raw_data: Dict[str, Any]

    def is_valid() -> bool
    def days_until_expiry() -> int
```

**Methods:**
- `is_valid()`: Check if certificate is currently valid
- `days_until_expiry()`: Calculate days until expiry (negative if expired)

#### CertificateStatus

Certificate status enumeration.

تعداد حالات الشهادة.

```python
class CertificateStatus(str, Enum):
    VALID = "valid"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"
```

#### Producer

Producer/farm information model.

نموذج معلومات المنتج/المزرعة.

```python
@dataclass
class Producer:
    name: str
    country: str
    products: List[str]
    certification_status: CertificateStatus
    ggn: Optional[str]
    location: Optional[str]
    certification_date: Optional[datetime]
    raw_data: Dict[str, Any]
```

### Exceptions / الاستثناءات

All exceptions inherit from `GlobalGAPAPIError` and include bilingual error messages.

جميع الاستثناءات ترث من `GlobalGAPAPIError` وتتضمن رسائل خطأ ثنائية اللغة.

#### GlobalGAPAPIError

Base exception for all API errors.

الاستثناء الأساسي لجميع أخطاء واجهة البرمجة.

```python
class GlobalGAPAPIError(Exception):
    message: str
    message_ar: str
    status_code: Optional[int]
    details: Dict[str, Any]

    def to_dict(lang: str = "en") -> Dict[str, Any]
```

#### CertificateNotFound

Raised when certificate is not found.

يُثار عندما لا يتم العثور على الشهادة.

```python
raise CertificateNotFound("4063061891234")
```

#### InvalidGGN

Raised when GGN format is invalid.

يُثار عندما يكون تنسيق GGN غير صالح.

```python
raise InvalidGGN("123456")
```

#### RateLimitExceeded

Raised when rate limit is exceeded.

يُثار عند تجاوز حد المعدل.

```python
raise RateLimitExceeded(retry_after=60)
```

#### AuthenticationError

Raised when authentication fails.

يُثار عند فشل المصادقة.

```python
raise AuthenticationError()
```

## Configuration / الإعدادات

### Environment Variables / متغيرات البيئة

```bash
# GlobalGAP API Key
export GLOBALGAP_API_KEY="your-api-key"

# Optional: Override base URL
export GLOBALGAP_BASE_URL="https://api.globalgap.org/v1"
```

### Usage in Code / الاستخدام في الكود

```python
import os
from shared.globalgap import GlobalGAPClient

api_key = os.getenv("GLOBALGAP_API_KEY")
base_url = os.getenv("GLOBALGAP_BASE_URL", "https://www.globalgap.org/api/v1")

client = GlobalGAPClient(
    api_key=api_key,
    base_url=base_url,
)
```

## Mock Mode / وضع المحاكاة

For testing and development without real API access:

للاختبار والتطوير بدون الوصول الفعلي لواجهة البرمجة:

```python
# Enable mock mode
client = GlobalGAPClient(mock_mode=True)

# Returns mock data
cert = await client.verify_certificate("4063061891234")
print(cert.status)  # Returns: CertificateStatus.VALID
```

Mock mode returns realistic test data without making actual API calls.

يُرجع وضع المحاكاة بيانات اختبار واقعية بدون إجراء مكالمات فعلية لواجهة البرمجة.

## Rate Limiting / تحديد المعدل

The client includes built-in rate limiting using a token bucket algorithm:

يتضمن العميل تحديداً مدمجاً للمعدل باستخدام خوارزمية دلو الرموز:

```python
client = GlobalGAPClient(
    rate_limit=10,         # 10 requests
    rate_limit_period=60,  # per 60 seconds
)
```

When rate limit is exceeded, the client automatically waits before making the next request.

عند تجاوز حد المعدل، ينتظر العميل تلقائياً قبل إجراء الطلب التالي.

## Retry Logic / منطق إعادة المحاولة

Automatic retry with exponential backoff for failed requests:

إعادة محاولة تلقائية مع تراجع أسي للطلبات الفاشلة:

```python
client = GlobalGAPClient(
    max_retries=3,  # Retry up to 3 times
)
```

Retry strategy:
- Initial wait: 2 seconds
- Maximum wait: 10 seconds
- Exponential backoff multiplier: 1

## Error Handling / معالجة الأخطاء

### Basic Error Handling / معالجة الأخطاء الأساسية

```python
from shared.globalgap import (
    GlobalGAPClient,
    CertificateNotFound,
    InvalidGGN,
    GlobalGAPAPIError,
)

try:
    cert = await client.verify_certificate(ggn)
except CertificateNotFound as e:
    print(f"Certificate not found: {e.message_ar}")
except InvalidGGN as e:
    print(f"Invalid GGN: {e.message_ar}")
except GlobalGAPAPIError as e:
    print(f"API error: {e.message_ar}")
```

### Bilingual Error Messages / رسائل الخطأ ثنائية اللغة

```python
try:
    cert = await client.verify_certificate(ggn)
except GlobalGAPAPIError as e:
    # Get error in English
    error_en = e.to_dict(lang="en")

    # Get error in Arabic
    error_ar = e.to_dict(lang="ar")

    # Return to API
    return {"error": error_ar}
```

## Integration Examples / أمثلة التكامل

### SAHOOL Farm Management Integration / تكامل إدارة المزارع SAHOOL

```python
from shared.globalgap import GlobalGAPClient

async def verify_farm_certificate(farm_id: str, ggn: str):
    """Verify and update farm certification status"""

    async with GlobalGAPClient(api_key=api_key) as client:
        try:
            cert = await client.verify_certificate(ggn)

            # Update farm record in database
            await db.farms.update_one(
                {"_id": farm_id},
                {
                    "$set": {
                        "globalgap.status": cert.status.value,
                        "globalgap.valid_until": cert.valid_to,
                        "globalgap.verified_at": datetime.now(),
                        "globalgap.cb_name": cert.cb_name,
                        "globalgap.products": cert.product_categories,
                    }
                }
            )

            # Send notification if expiring soon
            if cert.days_until_expiry() <= 60:
                await send_expiry_notification(farm_id, cert)

            return cert

        except CertificateNotFound:
            # Mark as not certified
            await db.farms.update_one(
                {"_id": farm_id},
                {"$set": {"globalgap.status": "not_found"}}
            )
            raise
```

### Scheduled Certificate Monitoring / مراقبة الشهادات المجدولة

```python
from shared.globalgap import GlobalGAPClient

async def monitor_certificates():
    """Daily job to check all farm certificates"""

    # Get all farms with GlobalGAP certification
    farms = await db.farms.find({"globalgap.ggn": {"$exists": True}})

    ggns = [farm["globalgap"]["ggn"] for farm in farms]

    async with GlobalGAPClient(api_key=api_key) as client:
        # Batch verify all certificates
        results = await client.batch_verify_certificates(ggns)

        # Process results
        for ggn, cert in results.items():
            farm = next(f for f in farms if f["globalgap"]["ggn"] == ggn)

            # Update database
            await db.farms.update_one(
                {"_id": farm["_id"]},
                {
                    "$set": {
                        "globalgap.status": cert.status.value,
                        "globalgap.last_checked": datetime.now(),
                    }
                }
            )

            # Alert if expired or expiring soon
            if cert.status == CertificateStatus.EXPIRED:
                await alert_expired_certificate(farm["_id"], cert)
            elif cert.days_until_expiry() <= 30:
                await alert_expiring_certificate(farm["_id"], cert)
```

### API Endpoint Integration / تكامل نقطة نهاية واجهة البرمجة

```python
from fastapi import APIRouter, HTTPException
from shared.globalgap import GlobalGAPClient, CertificateNotFound, InvalidGGN

router = APIRouter()

@router.get("/certificates/{ggn}")
async def get_certificate(ggn: str, lang: str = "en"):
    """Get GlobalGAP certificate information"""

    async with GlobalGAPClient(api_key=api_key) as client:
        try:
            cert = await client.verify_certificate(ggn)

            return {
                "ggn": cert.ggn,
                "status": cert.status.value,
                "valid_from": cert.valid_from.isoformat(),
                "valid_to": cert.valid_to.isoformat(),
                "is_valid": cert.is_valid(),
                "days_until_expiry": cert.days_until_expiry(),
                "producer": cert.producer_name,
                "country": cert.country,
                "products": cert.product_categories,
            }

        except (CertificateNotFound, InvalidGGN) as e:
            error = e.to_dict(lang=lang)
            raise HTTPException(
                status_code=error["status_code"],
                detail=error
            )
```

## Testing / الاختبار

### Unit Tests / اختبارات الوحدة

```python
import pytest
from shared.globalgap import GlobalGAPClient, CertificateStatus

@pytest.mark.asyncio
async def test_verify_certificate_mock():
    """Test certificate verification in mock mode"""

    async with GlobalGAPClient(mock_mode=True) as client:
        cert = await client.verify_certificate("4063061891234")

        assert cert.ggn == "4063061891234"
        assert cert.status == CertificateStatus.VALID
        assert cert.is_valid() is True

@pytest.mark.asyncio
async def test_invalid_ggn():
    """Test invalid GGN handling"""

    from shared.globalgap import InvalidGGN

    async with GlobalGAPClient(mock_mode=True) as client:
        with pytest.raises(InvalidGGN):
            await client.verify_certificate("invalid")
```

### Integration Tests / اختبارات التكامل

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_api():
    """Test with real GlobalGAP API (requires API key)"""

    import os
    api_key = os.getenv("GLOBALGAP_API_KEY")

    if not api_key:
        pytest.skip("No API key available")

    async with GlobalGAPClient(api_key=api_key, mock_mode=False) as client:
        cert = await client.verify_certificate("4063061891234")
        assert cert.ggn == "4063061891234"
```

## Logging / التسجيل

The client uses structlog for structured logging:

يستخدم العميل structlog للتسجيل المنظم:

```python
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

# Logs will include structured data
# السجلات ستتضمن بيانات منظمة
# {
#   "event": "globalgap_certificate_verified",
#   "ggn": "4063061891234",
#   "status": "valid",
#   "is_valid": true,
#   "timestamp": "2024-12-28T12:00:00Z"
# }
```

## Performance Considerations / اعتبارات الأداء

### Concurrent Operations / العمليات المتزامنة

Use batch operations for verifying multiple certificates:

استخدم العمليات الدُفعية للتحقق من شهادات متعددة:

```python
# ❌ Slow: Sequential verification
for ggn in ggns:
    cert = await client.verify_certificate(ggn)

# ✅ Fast: Batch verification
results = await client.batch_verify_certificates(ggns)
```

### Connection Reuse / إعادة استخدام الاتصال

Use context manager to reuse HTTP connection:

استخدم مدير السياق لإعادة استخدام اتصال HTTP:

```python
# ✅ Connection is reused
async with GlobalGAPClient(api_key=api_key) as client:
    cert1 = await client.verify_certificate(ggn1)
    cert2 = await client.verify_certificate(ggn2)
    # Client closed automatically
```

## Security / الأمان

### API Key Management / إدارة مفتاح واجهة البرمجة

- **Never commit API keys to version control**
- Store API keys in environment variables or secret management systems
- Use different API keys for development, staging, and production

- **لا تلتزم أبداً بمفاتيح واجهة البرمجة في التحكم بالإصدار**
- قم بتخزين مفاتيح واجهة البرمجة في متغيرات البيئة أو أنظمة إدارة الأسرار
- استخدم مفاتيح واجهة برمجة مختلفة للتطوير والتجهيز والإنتاج

### HTTPS Only / HTTPS فقط

The client enforces HTTPS for all API calls to ensure data privacy.

يفرض العميل HTTPS لجميع مكالمات واجهة البرمجة لضمان خصوصية البيانات.

## Support / الدعم

### Documentation / التوثيق

- **API Client Documentation**: `/home/user/sahool-unified-v15-idp/shared/globalgap/API_CLIENT_README.md`
- **Usage Examples**: `/home/user/sahool-unified-v15-idp/shared/globalgap/api_client_examples.py`
- **Source Code**: `/home/user/sahool-unified-v15-idp/shared/globalgap/api_client.py`

### Contact / الاتصال

For issues or questions:

للمشاكل أو الأسئلة:

- SAHOOL Platform Team
- Email: support@sahool.sa

## License / الترخيص

Copyright © 2024 SAHOOL Platform. All rights reserved.

حقوق النشر © 2024 منصة SAHOOL. جميع الحقوق محفوظة.
