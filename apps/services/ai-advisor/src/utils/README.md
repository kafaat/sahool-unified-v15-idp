# PII Masking for AI Advisor Service

# إخفاء المعلومات الشخصية لخدمة المستشار الذكي

## Overview | نظرة عامة

This utility provides automatic masking of Personally Identifiable Information (PII) in application logs. It integrates seamlessly with structlog to ensure sensitive data is never logged in plain text.

توفر هذه الأداة إخفاءً تلقائيًا للمعلومات الشخصية في سجلات التطبيق. تتكامل بسلاسة مع structlog لضمان عدم تسجيل البيانات الحساسة بنص واضح.

## Features | الميزات

### Automatic PII Detection | كشف تلقائي للمعلومات الشخصية

The PII masker automatically detects and masks:

- **Email addresses** → `[EMAIL]`
- **Phone numbers** (including Arabic numerals) → `[PHONE]`
- **IP addresses** → `[IP]`
- **Credit card numbers** → `[CARD]`
- **Social Security Numbers (SSN)** → `[SSN]`
- **API keys** → `[API_KEY]`
- **JWT tokens** → `[JWT]`
- **Passwords** → `[PASSWORD]`

### Sensitive Field Detection | كشف الحقول الحساسة

Fields with sensitive names are completely redacted:

- `password`, `passwd`, `pwd`
- `secret`, `token`, `api_key`, `apikey`
- `authorization`, `auth`, `credential`
- `private_key`, `access_token`, `refresh_token`
- `session_id`, `cookie`
- `ssn`, `credit_card`, `card_number`, `cvv`, `pin`

## Usage | الاستخدام

### 1. Automatic Logging (Recommended) | التسجيل التلقائي (موصى به)

PII masking is automatically applied to all structlog log events:

```python
import structlog

logger = structlog.get_logger()

# This will automatically mask PII
logger.info(
    "user_login_attempt",
    email="user@example.com",           # Masked to [EMAIL]
    ip_address="192.168.1.100",         # Masked to [IP]
    api_key="sk-abc123def456"           # Masked to [REDACTED]
)

# Output (after masking):
# {
#   "event": "user_login_attempt",
#   "email": "[EMAIL]",
#   "ip_address": "[IP]",
#   "api_key": "[REDACTED]",
#   ...
# }
```

### 2. Manual Masking | الإخفاء اليدوي

For manual masking when needed:

```python
from utils import PIIMasker, safe_log

# Mask text
text = "Contact john@example.com for password reset"
masked_text = PIIMasker.mask_text(text)
# Result: "Contact [EMAIL] for [PASSWORD] reset"

# Mask dictionary
data = {
    "user": "john@example.com",
    "phone": "+966-555-1234",
    "password": "secret123"
}
masked_data = PIIMasker.mask_dict(data)
# Result: {
#   "user": "[EMAIL]",
#   "phone": "[PHONE]",
#   "password": "[REDACTED]"
# }

# Safe logging helper
sensitive_info = {
    "email": "farmer@example.com",
    "api_key": "sk-123456789",
    "action": "crop_analysis"
}
logger.info("operation", details=safe_log(sensitive_info))
```

### 3. Custom Pattern Masking | إخفاء الأنماط المخصصة

To add custom patterns:

```python
from utils.pii_masker import PIIMasker

# Add custom pattern
PIIMasker.PATTERNS['custom_id'] = (
    r'FARM-\d{6}',  # Pattern
    '[FARM_ID]'      # Replacement
)

# Re-compile patterns
PIIMasker._compiled_patterns = None
```

## Integration | التكامل

### Structlog Configuration | تكوين Structlog

The PII masking processor is integrated into structlog in `main.py`:

```python
from utils import pii_masking_processor

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        pii_masking_processor,  # ← PII masking happens here
        structlog.processors.JSONRenderer(),
    ]
)
```

## Testing | الاختبار

Run the test suite to verify PII masking:

```bash
# From the service directory
cd /home/user/sahool-unified-v15-idp/apps/services/ai-advisor

# Run tests
python -m src.utils.test_pii_masker
```

## Examples | أمثلة

### Example 1: API Request Logging

```python
@app.post("/v1/advisor/ask")
async def ask_question(request: QuestionRequest):
    # Log request (PII automatically masked)
    logger.info(
        "advisor_question_received",
        question=request.question,
        context=request.context,  # May contain email, phone, etc.
    )
    # All PII in context will be automatically masked
```

### Example 2: Error Logging with User Data

```python
try:
    result = await process_user_data(user_email="john@example.com")
except Exception as e:
    # Error details with PII are automatically masked
    logger.error(
        "processing_failed",
        user_email="john@example.com",  # Masked to [EMAIL]
        error=str(e),
        exc_info=True
    )
```

### Example 3: Debugging with Sensitive Data

```python
# Debug logging with potentially sensitive data
user_data = {
    "name": "Ahmed",
    "email": "ahmed@farm.sa",
    "phone": "+966-555-123456",
    "field_id": "FIELD-001",
    "api_credentials": {
        "api_key": "sk-abc123xyz789",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}

# Safe to log - all PII automatically masked
logger.debug("user_data_received", data=user_data)

# Output will have:
# - email masked to [EMAIL]
# - phone masked to [PHONE]
# - api_key masked to [REDACTED]
# - token masked to [JWT]
```

## Security Considerations | اعتبارات الأمان

1. **Defense in Depth**: PII masking is the last line of defense. Avoid logging sensitive data when possible.

2. **Performance**: The masking processor adds minimal overhead (~1-2ms per log event).

3. **False Positives**: Some patterns might over-match. Review logs to ensure legitimate data isn't masked unnecessarily.

4. **Custom Patterns**: Add patterns specific to your domain (e.g., farm IDs, customer codes).

5. **Compliance**: This helps with GDPR, CCPA, and other privacy regulations by preventing PII from being stored in logs.

## File Structure | هيكل الملفات

```
utils/
├── __init__.py           # Package initialization
├── pii_masker.py         # Core PII masking logic
├── log_processor.py      # Structlog processor integration
├── test_pii_masker.py    # Test suite
└── README.md            # This file
```

## Troubleshooting | استكشاف الأخطاء

### PII Not Being Masked

1. Check that `pii_masking_processor` is in the structlog processors list
2. Ensure it's placed **before** the JSONRenderer
3. Verify the processor is imported correctly

### Custom Patterns Not Working

1. Clear compiled patterns: `PIIMasker._compiled_patterns = None`
2. Ensure pattern is valid regex
3. Test pattern separately before adding

### Performance Issues

1. Check processor placement in structlog configuration
2. Simplify complex regex patterns
3. Consider limiting recursion depth for nested structures

## Support | الدعم

For issues or questions:

- Check the test suite for examples
- Review structlog documentation
- Consult the team security guidelines
