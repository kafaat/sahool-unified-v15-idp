# ============================================================================
# SAHOOL Code Fix Agent - Docker Image
# وكيل إصلاح الكود - صورة دوكر
# ============================================================================

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment to avoid pip root user warning
# إنشاء بيئة افتراضية لتجنب تحذير المستخدم الجذر
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements and constraints first for caching
COPY constraints.txt .
COPY apps/services/code-fix-agent/requirements.txt .

# Install dependencies with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip setuptools wheel || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip setuptools wheel

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# ============================================================================
# Production Image
# ============================================================================

FROM python:${PYTHON_VERSION}-slim-bookworm AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Copy virtual environment from builder
# نسخ البيئة الافتراضية من البناء
COPY --from=builder /opt/venv /opt/venv

# Set virtual environment path
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy shared modules (required for shared.ai imports)
COPY shared/ ./shared/

# Copy application code
COPY apps/services/code-fix-agent/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8162 \
    HOST=0.0.0.0 \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8162

# Health check - uses PORT env var
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os,httpx; httpx.get(f'http://localhost:{os.environ.get(\"PORT\",8162)}/healthz').raise_for_status()"

# Run application - uses PORT env var
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
