# SAHOOL USSD Gateway Service
# ============================
# SMS/USSD/WhatsApp support for basic phones
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Build arguments
ARG SERVICE_NAME=ussd-gateway
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"
LABEL org.opencontainers.image.description="SMS/USSD gateway for basic phones"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# Create non-root user for security
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel build

# Install dependencies
COPY apps/services/ussd-gateway/requirements.txt .

# Copy shared libraries
COPY shared/ ./shared/

# Copy source
COPY apps/services/ussd-gateway/src/ ./src/

# Install dependencies and set ownership
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt && \
    chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

EXPOSE 8180

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8180/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8180"]
