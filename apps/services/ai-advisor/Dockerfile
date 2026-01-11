# Multi-stage Dockerfile for AI Advisor Service
# ملف Docker متعدد المراحل لخدمة المستشار الذكي

# Stage 1: Builder
# المرحلة 1: البناء
FROM python:3.11-slim AS builder

# Set working directory | تعيين مجلد العمل
WORKDIR /app

# Install system dependencies | تثبيت تبعيات النظام
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements | نسخ المتطلبات
COPY apps/services/ai-advisor/requirements.txt .

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel build

# Configure pip for better network resilience
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf && \
    echo "default-timeout = 300" >> /root/.pip/pip.conf && \
    echo "[install]" >> /root/.pip/pip.conf && \
    echo "prefer-binary = true" >> /root/.pip/pip.conf

# Install Python dependencies | تثبيت تبعيات Python
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Stage 2: Runtime
# المرحلة 2: وقت التشغيل
FROM python:3.11-slim

# Set working directory | تعيين مجلد العمل
WORKDIR /app

# No runtime system dependencies needed - using Python for healthcheck

# Copy Python packages from builder | نسخ حزم Python من البناء
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user | إنشاء مستخدم غير جذر
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Copy shared modules | نسخ الوحدات المشتركة
COPY --chown=appuser:appuser apps/services/shared/ /app/shared/

# Copy application code | نسخ كود التطبيق
COPY --chown=appuser:appuser apps/services/ai-advisor/src /app/src

# Switch to non-root user | التبديل إلى مستخدم غير جذر
USER appuser

# Set environment variables | تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8112

# Expose port | كشف المنفذ
EXPOSE 8112

# Health check | فحص الصحة
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8112/healthz')" || exit 1

# Run the application | تشغيل التطبيق
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8112"]
