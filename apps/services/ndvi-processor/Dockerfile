# ============================================
# SAHOOL NDVI Processor Dockerfile
# خدمة معالجة صور الأقمار الصناعية
# Multi-stage build for optimized image size
# Port: 8118
# ============================================

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# Install system dependencies for geo-spatial processing and compilation
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    libgdal-dev \
    gdal-bin \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
# setuptools>=78.1.1 for CVE-2024-6345, PYSEC-2025-49; wheel>=0.46.2 for CVE-2026-24049
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" build || \
    pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" build

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/ndvi-processor/requirements.txt .
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

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="ndvi-processor"
LABEL version="16.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    PORT=8118

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install only runtime geo-spatial libraries (no build tools)
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    libgdal32 \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/sahool/.local
ENV PATH=/home/sahool/.local/bin:$PATH

# Copy shared libraries
COPY --chown=sahool:sahool shared/ ./shared/

# Copy services shared modules (needed for errors_py module)
COPY --chown=sahool:sahool apps/services/shared/ ./apps/services/shared/


# Create compatibility layer: copy errors_py to shared/errors_py so imports work
RUN cp -r ./apps/services/shared/errors_py ./shared/ || true

# Copy source code
COPY --chown=sahool:sahool apps/services/ndvi-processor/src/ ./src/

# Create temp directory
RUN mkdir -p /tmp/ndvi && chown -R sahool:sahool /tmp/ndvi && \
    chown -R sahool:sahool /app

# Switch to non-root user

# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /home/sahool/.local/lib/python*/site-packages/setuptools* \
           /home/sahool/.local/lib/python*/site-packages/pip* \
           /home/sahool/.local/lib/python*/site-packages/wheel* \
           /home/sahool/.local/lib/python*/site-packages/pkg_resources* \
           /home/sahool/.local/lib/python*/site-packages/jaraco* \
           /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Expose port
EXPOSE 8118

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8118/healthz')" || exit 1

# Run application
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8118}"]
