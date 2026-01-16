# SAHOOL Inventory Service
# ============================
# Agricultural inventory management and analytics
# Version: 1.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

# Build arguments
ARG SERVICE_NAME=inventory-service
ARG SERVICE_VERSION=1.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create non-root user
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Upgrade pip and install build tools (non-fatal in case of network issues)
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel || true

# Install dependencies
COPY apps/services/inventory-service/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Copy shared libraries
COPY shared/ ./shared/

# Copy services shared modules (needed for errors_py module)
COPY apps/services/shared/ ./apps/services/shared/

# Create compatibility layer: copy errors_py to shared/errors_py so imports work
RUN cp -r ./apps/services/shared/errors_py ./shared/ || true

# Copy source
COPY apps/services/inventory-service/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

# Default port (can be overridden via PORT env var)
ENV PORT=8116
EXPOSE 8116

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8116/healthz')" || exit 1

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
