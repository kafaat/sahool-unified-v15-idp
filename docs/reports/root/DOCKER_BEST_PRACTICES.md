# أفضل ممارسات حاويات Docker | Docker Container Best Practices

**التاريخ | Date**: 2026-02-04  
**المنصة | Platform**: SAHOOL v16.0.0  
**الجمهور | Audience**: مطورو SAHOOL | SAHOOL Developers

---

## 🎯 المقدمة | Introduction

هذا الدليل يوثق أفضل الممارسات لبناء وتشغيل حاويات Docker في منصة SAHOOL.  
This guide documents best practices for building and running Docker containers in the SAHOOL platform.

---

## 🏗️ بناء الصور | Image Building

### 1. استخدام صور أساسية محددة الإصدار | Use Pinned Base Images

✅ **صحيح | Correct**:
```dockerfile
FROM python:3.11-slim-bookworm
FROM node:20-alpine
FROM postgis/postgis:16-3.4
```

❌ **خاطئ | Wrong**:
```dockerfile
FROM python:latest
FROM node:latest
FROM postgres:latest
```

**السبب | Reason**: الإصدارات المحددة تضمن بناء قابل للتكرار وأمان أفضل  
Pinned versions ensure reproducible builds and better security

---

### 2. بناء متعدد المراحل | Multi-Stage Builds

✅ **مثال قياسي | Standard Example**:
```dockerfile
# =============================================================================
# Build Stage
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Production Stage
# =============================================================================
FROM python:3.11-slim AS production

# Copy only runtime dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages \
                    /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/

# Run as non-root user
USER sahool

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

**الفوائد | Benefits**:
- تقليل حجم الصورة بنسبة 60-80% | Reduce image size by 60-80%
- إزالة أدوات البناء من الإنتاج | Remove build tools from production
- سطح هجوم أصغر | Smaller attack surface

---

### 3. استخدام .dockerignore | Use .dockerignore

✅ **نموذج قياسي | Standard Template**:
```dockerignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
build/
dist/
*.egg-info/

# Virtual environments
env/
venv/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation
*.md
!README.md
docs/

# Environment
.env
.env.*
!.env.example

# Logs
*.log
logs/

# Data (should be volume mounted)
data/
models/
*.db

# Docker
Dockerfile*
docker-compose*
.dockerignore

# Security
*.key
*.pem
credentials.json
secrets/
```

**الفوائد | Benefits**:
- بناء أسرع | Faster builds
- صور أصغر | Smaller images
- عدم تسريب الأسرار | No secret leaks

---

## 🔒 الأمان | Security

### 1. المستخدمين غير الجذر | Non-Root Users

✅ **صحيح | Correct**:
```dockerfile
# Create non-root user
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Set ownership
COPY --chown=sahool:sahool src/ ./src/

# Switch to non-root
USER sahool
```

❌ **خاطئ | Wrong**:
```dockerfile
# Running as root (default)
USER root
# or no USER directive at all
```

**الاستثناءات | Exceptions**:
- مرحلة التطوير فقط (development stage) | Development stage only
- يجب العودة إلى مستخدم محدود بعد التثبيت | Must switch back to restricted user after installation

```dockerfile
FROM production AS development

# Temporarily switch to root for dev tools
USER root

# Install dev dependencies
RUN apt-get update && apt-get install -y git vim

# Switch back to non-root
USER sahool
```

---

### 2. الأسرار والمتغيرات البيئية | Secrets & Environment Variables

❌ **خاطئ | Wrong**:
```dockerfile
ENV DATABASE_PASSWORD=my_password
ENV API_KEY=secret_key_123
```

✅ **صحيح | Correct**:
```dockerfile
# Use build arguments (never commit real secrets)
ARG BUILD_DATE
ENV BUILD_DATE=${BUILD_DATE}

# Load secrets at runtime
ENV DATABASE_PASSWORD_FILE=/run/secrets/db_password
```

**أفضل الممارسات | Best Practices**:
1. استخدام Docker Secrets | Use Docker Secrets
2. استخدام HashiCorp Vault | Use HashiCorp Vault
3. عدم تضمين الأسرار في الصورة | Never embed secrets in image
4. استخدام ملفات .env للتطوير فقط | Use .env files for development only

---

### 3. فحوصات الأمان | Security Scanning

```bash
# Scan with Trivy
trivy image sahool-service:latest

# Scan with Grype
grype sahool-service:latest

# Hadolint for Dockerfile linting
hadolint Dockerfile
```

**التكامل مع CI/CD | CI/CD Integration**:
```yaml
# .github/workflows/security-scan.yml
- name: Run Trivy Scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/kafaat/sahool-service:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
```

---

## ⚡ الأداء | Performance

### 1. تقليل الطبقات | Minimize Layers

❌ **خاطئ | Wrong**:
```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
```

✅ **صحيح | Correct**:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
```

**الفوائد | Benefits**:
- طبقة واحدة بدلاً من 5 | One layer instead of 5
- حجم أصغر | Smaller size
- بناء أسرع | Faster build

---

### 2. استخدام التخزين المؤقت | Use Caching Effectively

✅ **ترتيب صحيح | Correct Order**:
```dockerfile
# 1. Dependencies first (changes less frequently)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Application code last (changes frequently)
COPY src/ ./src/
```

❌ **ترتيب خاطئ | Wrong Order**:
```dockerfile
# Application code first - invalidates cache on every change
COPY . .

# Dependencies last - always rebuilt
RUN pip install -r requirements.txt
```

---

### 3. تحسين حجم الصورة | Optimize Image Size

**الاستراتيجيات | Strategies**:

1. **استخدام صور slim/alpine | Use slim/alpine images**:
   ```dockerfile
   FROM python:3.11-slim  # ~120 MB
   # vs
   FROM python:3.11       # ~900 MB
   ```

2. **إزالة ملفات التخزين المؤقت | Remove cache files**:
   ```dockerfile
   RUN pip install --no-cache-dir -r requirements.txt
   RUN apt-get clean && rm -rf /var/lib/apt/lists/*
   ```

3. **استخدام .dockerignore | Use .dockerignore**:
   - استبعاد node_modules،__pycache__، .git
   - Exclude node_modules, __pycache__, .git

---

## 🏥 الصحة والمراقبة | Health & Monitoring

### 1. فحوصات الصحة | Health Checks

✅ **مثال قياسي | Standard Example**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1
```

**أنواع فحوصات الصحة | Health Check Types**:

1. **HTTP Endpoint** (الأفضل | Preferred):
   ```dockerfile
   HEALTHCHECK CMD curl -f http://localhost:8080/healthz || exit 1
   ```

2. **TCP Check**:
   ```dockerfile
   HEALTHCHECK CMD nc -z localhost 8080 || exit 1
   ```

3. **Python Import Check** (خفيف | Lightweight):
   ```dockerfile
   HEALTHCHECK CMD python -c "import src.main" || exit 1
   ```

**معايير الفحص | Check Parameters**:
- `--interval`: كل 30 ثانية | Every 30 seconds
- `--timeout`: مهلة 10 ثوان | 10 second timeout
- `--start-period`: فترة بدء 30-45 ثانية | 30-45s startup period
- `--retries`: 3 محاولات | 3 retries

---

### 2. نقطة الصحة | Health Endpoint

```python
# src/main.py (FastAPI example)
@app.get("/healthz")
async def health_check():
    """Kubernetes liveness probe"""
    return {"status": "ok", "service": "service_name", "version": "16.0.0"}

@app.get("/readyz")
async def readiness_check():
    """Kubernetes readiness probe"""
    # Check dependencies
    db_ok = await check_database()
    nats_ok = await check_nats()
    
    if not (db_ok and nats_ok):
        raise HTTPException(status_code=503, detail="Not ready")
    
    return {
        "status": "ready",
        "database": db_ok,
        "nats": nats_ok
    }
```

---

## 🔗 الاعتماديات | Dependencies

### 1. ترتيب بدء الخدمات | Service Startup Order

✅ **صحيح | Correct**:
```yaml
# docker-compose.yml
services:
  app:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      nats:
        condition: service_started
```

❌ **خاطئ | Wrong**:
```yaml
services:
  app:
    depends_on:
      - postgres  # No health check condition
      - redis
```

---

### 2. انتظار التبعيات | Wait for Dependencies

**في كود التطبيق | In Application Code**:
```python
import asyncpg
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
async def connect_to_database():
    """Retry database connection with exponential backoff"""
    return await asyncpg.create_pool(DATABASE_URL)

# On startup
async def startup_event():
    app.state.db_pool = await connect_to_database()
```

---

## 📝 التوثيق | Documentation

### 1. Labels (التصنيفات) | Labels

```dockerfile
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL org.opencontainers.image.title="Service Name"
LABEL org.opencontainers.image.description="Service description | وصف الخدمة"
LABEL org.opencontainers.image.version="16.0.0"
LABEL org.opencontainers.image.vendor="KAFAAT"
LABEL org.opencontainers.image.source="https://github.com/kafaat/sahool-unified-v15-idp"
LABEL org.opencontainers.image.licenses="Proprietary"
```

---

### 2. تعليقات وتوثيق | Comments & Documentation

```dockerfile
# =============================================================================
# Service Name Dockerfile
# اسم الخدمة - ملف Docker
# =============================================================================

# -----------------------------------------------------------------------------
# Build Stage | مرحلة البناء
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Install build dependencies
# تثبيت متطلبات البناء
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential `# Compiler tools | أدوات الترجمة` \
    curl            `# Download utility | أداة التحميل` \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Production Stage | مرحلة الإنتاج
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS production
```

---

## 🔧 البيئات | Environments

### 1. مراحل متعددة للبيئات | Multi-Stage for Environments

```dockerfile
# Production (default)
FROM python:3.11-slim AS production
USER sahool
ENV ENVIRONMENT=production

# Development
FROM production AS development
USER root
RUN apt-get update && apt-get install -y git vim
USER sahool
ENV ENVIRONMENT=development
ENV DEBUG=true

# Testing
FROM production AS testing
RUN pip install pytest pytest-cov
ENV ENVIRONMENT=test
```

**الاستخدام | Usage**:
```bash
# Production
docker build --target production -t service:prod .

# Development
docker build --target development -t service:dev .

# Testing
docker build --target testing -t service:test .
```

---

## 📊 المقاييس | Metrics

### 1. Prometheus Metrics

```python
# src/main.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")
```

---

## ✅ قائمة تدقيق | Checklist

### قبل النشر | Before Deployment

- [ ] استخدام صورة أساسية محددة الإصدار | Use pinned base image
- [ ] إضافة ملف .dockerignore | Add .dockerignore file
- [ ] بناء متعدد المراحل | Multi-stage build
- [ ] تشغيل كمستخدم غير جذر | Run as non-root user
- [ ] إضافة فحص صحة | Add health check
- [ ] إضافة labels (التصنيفات) | Add labels
- [ ] اختبار الصورة | Test the image
- [ ] فحص الأمان (Trivy/Grype) | Security scan
- [ ] فحص Dockerfile (Hadolint) | Lint Dockerfile
- [ ] توثيق المنافذ | Document ports
- [ ] توثيق المتغيرات البيئية | Document environment variables
- [ ] إضافة README.md للخدمة | Add service README.md

### أثناء التطوير | During Development

- [ ] استخدام docker-compose للتطوير المحلي | Use docker-compose for local dev
- [ ] استخدام volumes للـ hot reload | Use volumes for hot reload
- [ ] تمكين السجلات المفصلة | Enable verbose logging
- [ ] استخدام مرحلة development | Use development stage

---

## 🆘 استكشاف الأخطاء | Troubleshooting

### 1. حجم الصورة كبير | Large Image Size

```bash
# Check layer sizes
docker history sahool-service:latest

# Analyze with dive
dive sahool-service:latest
```

**الحلول | Solutions**:
- استخدام صور slim/alpine | Use slim/alpine images
- إزالة أدوات البناء | Remove build tools
- استخدام بناء متعدد المراحل | Use multi-stage build

---

### 2. بناء بطيء | Slow Build

**الحلول | Solutions**:
- إضافة .dockerignore | Add .dockerignore
- ترتيب COPY للاستفادة من التخزين المؤقت | Order COPY for caching
- استخدام BuildKit | Use BuildKit

```bash
# Enable BuildKit
DOCKER_BUILDKIT=1 docker build -t service:latest .
```

---

### 3. فحص الصحة يفشل | Health Check Fails

```bash
# Check health status
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' container_id | jq
```

---

## 📚 موارد إضافية | Additional Resources

- **الوثائق الرسمية | Official Documentation**: https://docs.docker.com/develop/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **SAHOOL Documentation**: `docs/`
- **Service Registry**: `governance/services.yaml`

---

**آخر تحديث | Last Updated**: 2026-02-04  
**الإصدار | Version**: 1.0
