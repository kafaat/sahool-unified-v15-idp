# Mobile Sync API Contract
# عقد واجهة برمجة التطبيقات للمزامنة المحمولة

**Version:** 16.0.0  
**Last Updated:** 2026-02-11  
**Owner:** Mobile Team

---

## Overview | نظرة عامة

This document defines the API contract between the SAHOOL mobile app and backend services for offline-first synchronization.

يحدد هذا المستند عقد واجهة برمجة التطبيقات بين تطبيق سهول المحمول وخدمات الخادم للمزامنة دون اتصال.

---

## Mobile Sync Endpoints | نقاط نهاية المزامنة المحمولة

### Base URL
```
Production: https://api.sahool.app
Staging: https://staging-api.sahool.app  
Development: http://localhost:3000
```

### Required Headers
- `Authorization: Bearer <jwt_token>`
- `X-Tenant-ID: <tenant_uuid>`
- `X-Device-ID: <device_uuid>`

---

## Timeout Configuration | تكوين المهلة

### Recommended Timeouts for Mobile
```dart
const Duration connectTimeout = Duration(seconds: 60);  // Increased for mobile
const Duration sendTimeout = Duration(seconds: 90);     // Large payloads
const Duration receiveTimeout = Duration(seconds: 90);  // Large responses
```

**Rationale:** Mobile devices in rural areas may have slow/unstable connections.

---

## Rate Limiting | حد المعدل

### Mobile Sync Rate Limits
```yaml
sync_endpoints:
  max_requests: 30 per minute
  max_batch_size: 50 items
  
upload_endpoints:
  max_requests: 10 per minute
  max_file_size: 10 MB
```

---

## References | المراجع

- [Sync Engine Implementation](../lib/core/sync/sync_engine.dart)
- [Rate Limiter Configuration](../lib/core/http/rate_limiter.dart)
- [API Client](../lib/core/http/api_client.dart)

---

**Contact:** mobile-team@sahool.app
