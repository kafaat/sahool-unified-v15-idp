# SAHOOL Crop Intelligence Service
# ===========================
# Uses shared base image for consistency
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

# Build arguments
ARG SERVICE_NAME=crop-intelligence
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PORT=8095

WORKDIR /app

# Create non-root user
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool


# Install dependencies (using shared requirements)
COPY apps/services/crop-intelligence-service/requirements.txt .

# Copy shared libraries
COPY apps/services/shared ./shared/

# Copy source
COPY apps/services/crop-intelligence-service/src/ ./src/

# Upgrade pip, install dependencies, and set ownership
RUN pip install --upgrade pip || true && \
    pip install --no-cache-dir -r requirements.txt && \
    chown -R sahool:sahool /app

USER sahool

EXPOSE 8095

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8095/healthz')" || exit 1

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8095}"]
