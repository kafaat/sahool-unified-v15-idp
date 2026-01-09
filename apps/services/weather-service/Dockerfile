# SAHOOL Weather Core Service
# ============================
# Uses shared base image for consistency
# Version: 16.0.0
FROM python:3.11-slim

# Build arguments
ARG SERVICE_NAME=weather-core
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


# Install dependencies (using shared requirements)
COPY apps/services/weather-service/requirements.txt .

# Copy shared libraries (from repo root)
COPY shared/ ./shared/

# Copy source
COPY apps/services/weather-service/src/ ./src/

# Upgrade pip, install dependencies, and set ownership
RUN pip install --upgrade pip || true && \
    pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt && \
    chown -R sahool:sahool /app

USER sahool

# Default port (can be overridden via PORT env var)
ENV PORT=8092
EXPOSE 8092

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8092/healthz')" || exit 1

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
