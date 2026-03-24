# Leveling Optimizer Service Dockerfile
# خدمة تحسين التسوية

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 sahool \
    && useradd --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Builder stage
FROM base AS builder

# Install build dependencies (apt-update.sh inherited from base stage)
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configure pip for network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf

# Copy requirements and constraints first for better caching
# Note: Build context is repo root, so use full path
COPY constraints.txt .
COPY apps/services/leveling-optimizer-service/requirements.txt .

# Install Python dependencies with multi-mirror fallback
# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# Production stage
FROM base AS production

# Copy installed packages from builder
ARG PYTHON_VERSION
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy shared modules (required for shared.middleware, shared.auth, etc.)
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Copy application code
# Note: Build context is repo root, so use full path
COPY --chown=sahool:sahool apps/services/leveling-optimizer-service/src ./src

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8170

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8170/healthz || exit 1

# Labels
LABEL org.opencontainers.image.title="Leveling Optimizer Service" \
    org.opencontainers.image.description="Agricultural field leveling optimization service for SAHOOL" \
    org.opencontainers.image.version="16.0.0" \
    org.opencontainers.image.vendor="KAFAAT" \
    org.opencontainers.image.source="https://github.com/kafaat/sahool"

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8170"]
