# SAHOOL Field Chat Service
# ==========================
# Uses shared base image for consistency
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

# Build arguments
ARG SERVICE_NAME=field-chat
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# Create non-root user
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Install build dependencies required to compile native wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    python3-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

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

# Install dependencies (using shared requirements)
COPY apps/services/field-chat/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Remove build-time packages to keep the runtime image small
RUN apt-get purge -y --auto-remove build-essential gcc python3-dev libpq-dev libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/* \
    || true

# Copy shared libraries (required for shared.errors_py, shared.cors_config)
COPY shared/ ./shared/

# Copy services shared modules (needed for errors_py module)
COPY apps/services/shared/ ./apps/services/shared/

# Create compatibility layer: copy errors_py to shared/errors_py so imports work
RUN cp -r ./apps/services/shared/errors_py ./shared/ || true

# Copy source
COPY apps/services/field-chat/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

EXPOSE 8099

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8099/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8099"]
