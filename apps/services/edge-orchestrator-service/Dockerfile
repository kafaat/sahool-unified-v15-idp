# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
#
# Edge Orchestrator Service Dockerfile
# خدمة تنسيق الحافة - ملف Docker
#
# Manages edge devices (Jetson Orin Nano, etc.) for agricultural AI inference.
# تدير أجهزة الحافة (Jetson Orin Nano، إلخ) للاستدلال بالذكاء الاصطناعي الزراعي.

# =============================================================================
# Build Stage | مرحلة البناء
# =============================================================================
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /app

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with multi-mirror fallback
# Note: Build context is repo root, so use full path
COPY constraints.txt .
COPY apps/services/edge-orchestrator-service/requirements.txt .
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

# =============================================================================
# Production Stage | مرحلة الإنتاج
# =============================================================================
FROM python:${PYTHON_VERSION}-slim AS production

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL org.opencontainers.image.title="Edge Orchestrator Service"
LABEL org.opencontainers.image.description="Manages edge devices for agricultural AI inference | تدير أجهزة الحافة للاستدلال بالذكاء الاصطناعي الزراعي"
LABEL org.opencontainers.image.version="16.0.0"
LABEL org.opencontainers.image.vendor="KAFAAT"
LABEL org.opencontainers.image.source="https://github.com/kafaat/sahool-unified-v15-idp"

# Security: Create non-root user
RUN groupadd --gid 1000 sahool && \
    useradd --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install runtime dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy Python packages from builder (use ARG to avoid hardcoded version path)
ARG PYTHON_VERSION=3.11
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy shared modules (required for shared.middleware, shared.auth, etc.)
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Copy application code
# Note: Build context is repo root, so use full path
COPY --chown=sahool:sahool apps/services/edge-orchestrator-service/src ./src

# Create necessary directories
RUN mkdir -p /data/uploads /data/models /data/logs && \
    chown -R sahool:sahool /data

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8180 \
    HOST=0.0.0.0 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8180

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8180/healthz || exit 1

# Switch to non-root user
USER sahool

# Use tini as init system
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8180"]

# =============================================================================
# Development Stage | مرحلة التطوير
# =============================================================================
FROM production AS development

USER root

# Install development dependencies (apt-update.sh inherited from production stage)
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install dev Python packages with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    pytest pytest-asyncio pytest-cov ruff mypy ipython || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    pytest pytest-asyncio pytest-cov ruff mypy ipython || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    pytest pytest-asyncio pytest-cov ruff mypy ipython

USER sahool

ENV ENVIRONMENT=development \
    DEBUG=true \
    LOG_LEVEL=DEBUG

# Enable hot reload for development
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8180", "--reload"]
