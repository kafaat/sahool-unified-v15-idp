# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL AI Advisor Service Dockerfile
# Multi-stage build with security hardening
# Version: 16.0.0
# Updated: February 2026
# ملف Docker متعدد المراحل لخدمة المستشار الذكي
# ═══════════════════════════════════════════════════════════════════════════════

ARG PYTHON_VERSION=3.11

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder | المرحلة 1: البناء
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Install build dependencies | تثبيت تبعيات البناء
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for build | إنشاء مستخدم غير جذر للبناء
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --create-home sahool

USER sahool
WORKDIR /home/sahool

# Create virtual environment | إنشاء بيئة افتراضية
ENV VIRTUAL_ENV=/home/sahool/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Configure pip for network resilience (PyPI first for CI reliability)
RUN mkdir -p ~/.pip && \
    printf '[global]\ntimeout = 300\nretries = 10\nindex-url = https://pypi.org/simple/\nextra-index-url = https://mirrors.aliyun.com/pypi/simple/\n                  https://pypi.tuna.tsinghua.edu.cn/simple/\n[install]\nprefer-binary = true\n' > ~/.pip/pip.conf

# Upgrade pip and build tools (multi-mirror fallback)
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.0" "setuptools>=75.0" "wheel>=0.44.0" build || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.0" "setuptools>=75.0" "wheel>=0.44.0" build

# Copy requirements and constraints | نسخ المتطلبات والقيود
COPY --chown=sahool:sahool apps/services/ai-advisor/requirements.txt /tmp/requirements.txt
COPY --chown=sahool:sahool docker/constraints-ai.txt /tmp/constraints-ai.txt

# Install Python dependencies (PyPI first, Aliyun fallback, Tencent fallback)
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Production | المرحلة 2: الإنتاج
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

# Labels
LABEL org.opencontainers.image.title="SAHOOL AI Advisor Service | خدمة المستشار الذكي" \
      org.opencontainers.image.version="16.0.0" \
      org.opencontainers.image.vendor="KAFAAT" \
      org.opencontainers.image.description="AI-powered agricultural advisor with natural language query support"

# Install minimal runtime dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Create non-root user | إنشاء مستخدم غير جذر
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --create-home sahool

# Copy virtual environment from builder | نسخ البيئة الافتراضية من البناء
COPY --from=builder --chown=sahool:sahool /home/sahool/venv /home/sahool/venv

# Set virtual environment path | تعيين مسار البيئة الافتراضية
ENV VIRTUAL_ENV=/home/sahool/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy shared modules | نسخ الوحدات المشتركة
# Copy root shared modules first (shared.ai, shared.events, etc.)
COPY --chown=sahool:sahool shared/ /app/shared/

# Copy services shared modules overlay (shared.errors_py, shared.middleware, etc.)
COPY --chown=sahool:sahool apps/services/shared/ /app/shared/

# Copy application code | نسخ كود التطبيق
COPY --chown=sahool:sahool apps/services/ai-advisor/src /app/src

# Set environment variables | تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8112

# Switch to non-root user | التبديل إلى مستخدم غير جذر
USER sahool

# Expose port | كشف المنفذ
EXPOSE 8112

# Health check | فحص الصحة
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8112/healthz')" || exit 1

# Run the application | تشغيل التطبيق
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8112"]
