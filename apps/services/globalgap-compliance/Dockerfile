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
COPY docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh

COPY constraints.txt .
COPY apps/services/globalgap-compliance/requirements.txt .

# Install Python dependencies | تثبيت تبعيات Python
# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

RUN pip-install.sh -c constraints.txt -r requirements.txt

# Copy root shared modules first (shared.events, etc.)
COPY shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py, etc.)
COPY apps/services/shared/ ./shared/


# Copy source code | نسخ الكود المصدري
COPY apps/services/globalgap-compliance/src/ ./src/

# Change ownership | تغيير الملكية
RUN chown -R sahool:sahool /app

# Switch to non-root user | التبديل إلى مستخدم غير جذر

# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Expose port | عرض المنفذ
EXPOSE 8128

# Health check using Python | فحص الصحة باستخدام Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8128/healthz')" || exit 1

# Run application | تشغيل التطبيق
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8128"]
