# SAHOOL Irrigation Smart Service
# Multi-stage build for optimized image size
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/irrigation-smart/requirements.txt .
COPY constraints.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --user -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --user -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --user -c constraints.txt -r requirements.txt

# Stage 2: Production
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/sahool/.local
ENV PATH=/home/sahool/.local/bin:$PATH

# Copy shared modules
COPY --chown=sahool:sahool apps/services/shared ./shared/

# Copy source code
COPY --chown=sahool:sahool apps/services/irrigation-smart/src/ ./src/

USER sahool

# Expose port
EXPOSE 8094

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8094/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8094"]
