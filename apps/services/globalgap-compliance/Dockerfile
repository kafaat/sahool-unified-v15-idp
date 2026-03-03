# ============================================
# SAHOOL GlobalGAP Compliance Service Dockerfile
# خدمة الامتثال لمعايير GlobalGAP
# Port: 8128
# ============================================

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

# Labels | العلامات
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="globalgap-compliance"
LABEL version="16.0.0"

# Environment | البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8128

# Create non-root user | إنشاء مستخدم غير جذر
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Working directory | دليل العمل
WORKDIR /app

# Copy requirements and constraints first for caching | نسخ المتطلبات أولاً للتخزين المؤقت
COPY constraints.txt .
COPY apps/services/globalgap-compliance/requirements.txt .

# Install Python dependencies | تثبيت تبعيات Python
# Install dependencies with resilient multi-mirror fallback strategy
# Try Aliyun first with long timeout, then fallback to PyPI, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# Copy root shared modules first (shared.events, etc.)
COPY shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py, etc.)
COPY apps/services/shared/ ./shared/

# Copy source code | نسخ الكود المصدري
COPY apps/services/globalgap-compliance/src/ ./src/

# Change ownership | تغيير الملكية
RUN chown -R sahool:sahool /app

# Switch to non-root user | التبديل إلى مستخدم غير جذر
USER sahool

# Expose port | عرض المنفذ
EXPOSE 8128

# Health check using Python | فحص الصحة باستخدام Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8128/healthz')" || exit 1

# Run application | تشغيل التطبيق
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8128"]
