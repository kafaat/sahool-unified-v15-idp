# SAHOOL Equipment Service
# =========================
# Multi-stage build for optimized image size
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
RUN (apt-get update || (sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null; apt-get update)) && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip "setuptools>=68.0" wheel build || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip "setuptools>=68.0" wheel build

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/equipment-service/requirements.txt .
COPY constraints.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --user -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --user -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --user -c constraints.txt -r requirements.txt

# Stage 2: Production
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

# Build arguments
ARG SERVICE_NAME=equipment-service
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

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/sahool/.local
ENV PATH=/home/sahool/.local/bin:$PATH

# Copy root shared modules (shared.ai, shared.events, etc.)
COPY --chown=sahool:sahool shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py/, shared.middleware/, etc.)
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Copy source
COPY --chown=sahool:sahool apps/services/equipment-service/src/ ./src/

USER sahool

EXPOSE 8101

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8101/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8101"]
