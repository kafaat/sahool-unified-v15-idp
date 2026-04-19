# SAHOOL Logistics Service
# =========================
# Uses shared base image for consistency
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Build arguments
ARG SERVICE_NAME=logistics-service
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"
LABEL org.opencontainers.image.description="Agricultural logistics management service"

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

# Install dependencies
COPY constraints.txt .
# Install build dependencies for cryptography/bcrypt
COPY docker/apt-update.sh docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools with multi-mirror fallback
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" build

COPY apps/services/logistics-service/requirements.txt .

# Copy root shared modules (shared.ai, shared.events, etc.)
COPY shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py/, shared.middleware/, etc.)
COPY apps/services/shared/ ./shared/


# Copy source
COPY apps/services/logistics-service/src/ ./src/

# Install dependencies and set ownership
RUN pip-install.sh -c constraints.txt -r requirements.txt && \
    chown -R sahool:sahool /app


# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Default port (can be overridden via PORT env var)
ENV PORT=8167
EXPOSE 8167

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8167)}/healthz')" || exit 1

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
