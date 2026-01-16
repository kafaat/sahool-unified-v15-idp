# ============================================
# SAHOOL GlobalGAP Compliance Service Dockerfile
# خدمة الامتثال لمعايير GlobalGAP
# Port: 8123
# ============================================

FROM python:3.11-slim

# Labels | العلامات
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="globalgap-compliance"
LABEL version="1.0.0"

# Environment | البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8123

# Create non-root user | إنشاء مستخدم غير جذر
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Working directory | دليل العمل
WORKDIR /app

# Copy requirements first for caching | نسخ المتطلبات أولاً للتخزين المؤقت
COPY apps/services/globalgap-compliance/requirements.txt .

# Upgrade pip and install build tools | ترقية pip وتثبيت أدوات البناء
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel && \
    pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Copy shared modules (required for imports from shared/) | نسخ الوحدات المشتركة
COPY apps/services/shared/ ./shared/

# Copy source code | نسخ الكود المصدري
COPY apps/services/globalgap-compliance/src/ ./src/

# Change ownership | تغيير الملكية
RUN chown -R sahool:sahool /app

# Switch to non-root user | التبديل إلى مستخدم غير جذر
USER sahool

# Expose port | عرض المنفذ
EXPOSE 8123

# Health check using Python | فحص الصحة باستخدام Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8123/health/live')" || exit 1

# Run application | تشغيل التطبيق
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8123"]
