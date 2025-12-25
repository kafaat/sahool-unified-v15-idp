# SAHOOL Agro Advisor Service
# ============================
# Uses shared base image for consistency
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

# Build arguments
ARG SERVICE_NAME=agro-advisor
ARG SERVICE_VERSION=16.0.0

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


# Upgrade pip (non-fatal in case of network issues)
RUN pip install --upgrade pip || true

# Install dependencies (using shared requirements)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared libraries

# Copy source
COPY src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

# Default port (can be overridden via PORT env var)
ENV PORT=8105
EXPOSE 8105

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8105/healthz')" || exit 1

CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT}
