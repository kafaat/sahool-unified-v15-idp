# SAHOOL Skills Service | خدمة المهارات

**Version**: 16.0.0
**Port**: 8121

## Overview | نظرة عامة

The Skills Service manages AI model skill compression, memory storage/recall, and performance evaluation for the SAHOOL platform. This service provides capabilities for:

**خدمة المهارات** تدير ضغط مهارات نماذج الذكاء الاصطناعي وتخزين/استرجاع الذاكرة وتقييم الأداء لمنصة سهول. توفر الخدمة القدرات التالية:

- **Skill Compression**: Reduce skill data size while maintaining functionality
  **ضغط المهارات**: تقليل حجم بيانات المهارات مع الحفاظ على الوظيفة

- **Memory Management**: Store and recall skills with TTL support
  **إدارة الذاكرة**: تخزين واستدعاء المهارات مع دعم TTL

- **Performance Evaluation**: Assess skill performance against configured metrics
  **تقييم الأداء**: تقييم أداء المهارات مقابل المقاييس المكونة

## Quick Start | البدء السريع

### Local Development | التطوير المحلي

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python src/main.py

# Service will be available at http://localhost:8121
```

### Docker

```bash
# Build
docker build -t sahool-skills-service .

# Run
docker run -p 8121:8121 \
  -e ENVIRONMENT=development \
  -e LOG_LEVEL=INFO \
  sahool-skills-service
```

### Docker Compose

```bash
# From project root
make dev

# Service starts automatically on port 8121
```

## API Endpoints | نقاط النهاية

### Health Checks | فحوصات الصحة

- `GET /healthz` - Liveness probe | اختبار الحياة
- `GET /readyz` - Readiness probe | اختبار الجاهزية
- `GET /` - Service information | معلومات الخدمة

### Core Endpoints | نقاط النهاية الأساسية

#### 1. Compress Skill | ضغط المهارة
```http
POST /compress
Content-Type: application/json

{
  "skill_id": "model-v1-compress",
  "skill_data": {
    "weights": [...],
    "config": {...}
  },
  "compression_level": 6,
  "target_size_kb": 512
}
```

**Response**: `CompressResponse` with compression metrics
**الاستجابة**: `CompressResponse` مع مقاييس الضغط

#### 2. Store Skill in Memory | تخزين المهارة في الذاكرة
```http
POST /memory/store
Content-Type: application/json

{
  "skill_id": "model-v1",
  "namespace": "inference",
  "skill_data": {...},
  "ttl_seconds": 3600,
  "metadata": {
    "version": "1.0",
    "algorithm": "transformer"
  }
}
```

**Response**: `MemoryStoreResponse` with storage confirmation
**الاستجابة**: `MemoryStoreResponse` مع تأكيد التخزين

#### 3. Recall Skill from Memory | استدعاء المهارة من الذاكرة
```http
POST /memory/recall
Content-Type: application/json

{
  "skill_id": "model-v1",
  "namespace": "inference",
  "include_metadata": true
}
```

**Response**: `MemoryRecallResponse` with skill data if found
**الاستجابة**: `MemoryRecallResponse` مع بيانات المهارة إذا وجدت

#### 4. Evaluate Skill | تقييم المهارة
```http
POST /evaluate
Content-Type: application/json

{
  "skill_id": "model-v1",
  "input_data": {
    "text": "sample input"
  },
  "expected_output": {
    "prediction": "expected value"
  },
  "metrics": ["accuracy", "latency", "memory"]
}
```

**Response**: `EvaluateResponse` with performance metrics
**الاستجابة**: `EvaluateResponse` مع مقاييس الأداء

## Architecture | الهندسة المعمارية

### Service Stack | مكدس الخدمة

- **Framework**: FastAPI 0.115.5
- **Server**: Uvicorn
- **Serialization**: Pydantic v2.10+
- **Testing**: pytest, pytest-asyncio
- **Caching**: Redis (token revocation, optional in-memory)
  **التخزين المؤقت**: Redis (إلغاء رمز التحقق، اختياري في الذاكرة)

### Data Flow

```
Client Request
    ↓
[Middleware: Request ID, Token Revocation]
    ↓
[Route Handler]
    ↓
[Business Logic]
    ↓
[Response]
```

## Configuration | الإعداد

### Environment Variables | متغيرات البيئة

| Variable        | Default       | Description              | الوصف |
| --------------- | ------------- | ------------------------ | --- |
| `PORT`          | `8121`        | Service port             | منفذ الخدمة |
| `ENVIRONMENT`   | `development` | Environment mode         | وضع البيئة |
| `LOG_LEVEL`     | `INFO`        | Logging level            | مستوى السجل |
| `REDIS_URL`     | (optional)    | Redis connection URL     | عنوان اتصال Redis |

### Docker Compose Variables | متغيرات Docker Compose

```bash
# From .env
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Testing | الاختبار

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_compress.py -v
```

### Test Markers | علامات الاختبار

- `@pytest.mark.unit` - Fast, no I/O | سريع، بدون إدخال/إخراج
- `@pytest.mark.integration` - API/database tests | اختبارات واجهة برمجية/قاعدة البيانات
- `@pytest.mark.slow` - Long-running tests | الاختبارات التي تستغرق وقتاً طويلاً

## Security | الأمان

### Authentication | المصادقة

- JWT token validation via `get_current_user` dependency
  التحقق من رمز JWT عبر تبعية `get_current_user`
- Token revocation support (Redis-backed)
  دعم إلغاء الرمز (مدعوم بـ Redis)
- Exempt paths: `/healthz`, `/readyz`, `/docs`
  المسارات المعفاة: `/healthz`, `/readyz`, `/docs`

### Input Validation | التحقق من الإدخال

- All request bodies validated with Pydantic
  يتم التحقق من جميع أجسام الطلب مع Pydantic
- Type hints enforce schema compliance
  تلميحات الأنواع تفرض الامتثال للمخطط
- Custom validators for business rules
  متحققات مخصصة لقواعد العمل

### Container Security | أمان الحاوية

- Non-root user (sahool)
  مستخدم غير جذر (سهول)
- Read-only root filesystem (optional)
  نظام ملفات جذر للقراءة فقط (اختياري)
- No privilege escalation
  بدون تصعيد الامتيازات
- Resource limits configured
  حدود الموارد المكونة

## Monitoring | المراقبة

### Health Endpoints | نقاط نهاية الصحة

Both return `status: "ok"` when healthy:
كلاهما يعيد `status: "ok"` عندما تكون سليمة:

```bash
curl http://localhost:8121/healthz
curl http://localhost:8121/readyz
```

### Logs | السجلات

Structured JSON logging for observability:
السجلات المنظمة JSON للملاحظة:

```bash
# View logs
docker logs sahool-skills-service

# Follow logs
docker logs -f sahool-skills-service
```

## Development | التطوير

### Project Structure | هيكل المشروع

```
skills-service/
├── Dockerfile              # Container definition | تعريف الحاوية
├── .dockerignore           # Docker build exclusions | استثناءات بناء Docker
├── requirements.txt        # Python dependencies | تبعيات Python
├── README.md               # This file | هذا الملف
├── src/
│   ├── __init__.py
│   └── main.py             # FastAPI app + endpoints | تطبيق FastAPI + نقاط النهاية
└── tests/
    └── (test files)        # اختبار الملفات
```

### Code Style | نمط الكود

- Python 3.11+
- Type hints required | تلميحات الأنواع مطلوبة
- Pydantic models for validation | نماذج Pydantic للتحقق
- Structured logging | السجلات المنظمة

### Adding Endpoints | إضافة نقاط النهاية

1. Create request/response models in `main.py`
   إنشاء نماذج الطلب/الاستجابة في `main.py`
2. Add route handler with `@app.post()` or `@app.get()`
   إضافة معالج المسار مع `@app.post()` أو `@app.get()`
3. Include authentication if needed: `user: User = Depends(get_current_user)`
   تضمين المصادقة إذا لزم الأمر: `user: User = Depends(get_current_user)`
4. Add tests in `tests/`
   إضافة اختبارات في `tests/`

### Adding Dependencies | إضافة التبعيات

1. Update `requirements.txt`
   تحديث `requirements.txt`
2. Rebuild: `docker build .`
   إعادة البناء: `docker build .`
3. Or reinstall locally: `pip install -r requirements.txt`
   أو إعادة التثبيت محلياً: `pip install -r requirements.txt`

## Troubleshooting | استكشاف الأخطاء

### Service won't start | الخدمة لن تبدأ

```bash
# Check logs
docker logs sahool-skills-service

# Verify port is available
lsof -i :8121

# Test connection
curl http://localhost:8121/healthz
```

### High memory usage | استخدام الذاكرة العالي

- Check compression level settings
  تحقق من إعدادات مستوى الضغط
- Monitor skill data sizes
  مراقبة أحجام بيانات المهارات
- Review TTL configuration for memory storage
  مراجعة إعدادات TTL لتخزين الذاكرة
- Use evaluation metrics to optimize
  استخدم مقاييس التقييم للتحسين

## Performance Tuning | ضبط الأداء

### Compression | الضغط

- Lower `compression_level` for faster compression
  خفض `compression_level` للضغط الأسرع
- Higher `compression_level` for better compression ratio
  رفع `compression_level` لنسبة ضغط أفضل
- Use `target_size_kb` for size-constrained scenarios
  استخدم `target_size_kb` للسيناريوهات المقيدة بالحجم

### Memory | الذاكرة

- Set appropriate `ttl_seconds` (avoid accumulation)
  اضبط `ttl_seconds` المناسب (تجنب التراكم)
- Use namespaces to organize skills
  استخدم المساحات لتنظيم المهارات
- Monitor Redis memory usage
  مراقبة استخدام ذاكرة Redis

## References | المراجع

- **Main Docs**: `/docs` (Swagger UI) | الوثائق الرئيسية
- **ReDoc**: `/redoc` | ReDoc
- **OpenAPI Schema**: `/openapi.json` | مخطط OpenAPI

## License | الترخيص

Proprietary - KAFAAT 2024-2026
ملك خاص - KAFAAT 2024-2026

---

**Service Owner**: KAFAAT Team | مالك الخدمة
**Last Updated**: January 2026 | آخر تحديث: يناير 2026
