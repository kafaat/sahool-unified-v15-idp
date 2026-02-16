# SAHOOL Field Chat Service
# ==========================
# Multi-stage build for optimized image size
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies required to compile native wheels
# Configure Debian mirror fallback for network-restricted environments
RUN set -e; \
    (apt-get update 2>/dev/null && apt-get install -y --no-install-recommends \
        build-essential gcc libpq-dev python3-dev libsqlite3-dev) || \
    ( \
        echo "Default apt sources failed, switching to mirror..."; \
        if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
            sed -i 's|URIs: http://deb.debian.org|URIs: https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources; \
        fi; \
        if [ -f /etc/apt/sources.list ]; then \
            sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list; \
        fi; \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            build-essential gcc libpq-dev python3-dev libsqlite3-dev \
    ) && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --upgrade pip "setuptools>=68.0" wheel build || \
    pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --upgrade pip "setuptools>=68.0" wheel build

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/field-chat/requirements.txt .
COPY constraints.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --user -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --user -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    --user -c constraints.txt -r requirements.txt

# Stage 2: Production
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

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
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install only runtime libraries (no build tools needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/sahool/.local
ENV PATH=/home/sahool/.local/bin:$PATH

# Copy root shared modules (shared.ai, shared.events, etc.)
COPY --chown=sahool:sahool shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py/, shared.middleware/, etc.)
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Copy source
COPY --chown=sahool:sahool apps/services/field-chat/src/ ./src/

USER sahool

EXPOSE 8099

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8099/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8099"]
