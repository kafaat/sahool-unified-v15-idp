# SAHOOL Field Intelligence Service
# خدمة ذكاء الحقول والقواعد الآلية
# =====================
# Field Intelligence and Automation Rules Service
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

# Build arguments
ARG SERVICE_NAME=field-intelligence
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"
LABEL org.opencontainers.image.description="Field Intelligence and Automation Rules Service"
LABEL maintainer="SAHOOL Team <dev@sahool.io>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# Create non-root user
# إنشاء مستخدم غير جذري للأمان
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel build

# Configure pip for better network resilience
# إعداد pip لتحسين مقاومة الشبكة
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf && \
    echo "default-timeout = 300" >> /root/.pip/pip.conf && \
    echo "[install]" >> /root/.pip/pip.conf && \
    echo "prefer-binary = true" >> /root/.pip/pip.conf

# Install dependencies
# تثبيت المتطلبات
COPY apps/services/field-intelligence/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Copy shared libraries
# نسخ المكتبات المشتركة
COPY apps/services/shared/ ./shared/

# Copy source
# نسخ الكود المصدري
COPY apps/services/field-intelligence/src/ ./src/

# Set ownership
# تعيين الملكية
RUN chown -R sahool:sahool /app

USER sahool

# Expose port
# فتح المنفذ
EXPOSE 8120

# Health check
# فحص الصحة
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8120/healthz')" || exit 1

# Run the application
# تشغيل التطبيق
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8120"]
