# SAHOOL Agro Rules Worker Service
# ==================================
# NATS-based worker (no HTTP port exposed)
# Multi-stage build for optimized production image
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS builder

# Build arguments
ARG SERVICE_NAME=agro-rules
ARG SERVICE_VERSION=16.0.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# Configure apt to use HTTPS and install build dependencies (needed for nats-py)
COPY docker/apt-update.sh /usr/local/bin/
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/*.list /etc/apt/sources.list 2>/dev/null || true && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    apt-transport-https \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools with multi-mirror fallback
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip "setuptools>=68.0" wheel build || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip "setuptools>=68.0" wheel build

# Configure pip for network resilience
RUN mkdir -p /root/.pip && \
    cat > /root/.pip/pip.conf <<'EOF'
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://pypi.org/simple/
[install]
prefer-binary = true
EOF

# Install dependencies (using shared requirements)
COPY constraints.txt .
COPY apps/services/agro-rules/requirements.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Try official PyPI first with long timeout, then fallback to Aliyun, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --prefix=/install \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --prefix=/install \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --prefix=/install \
    -c constraints.txt -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Production
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS production

ARG SERVICE_NAME=agro-rules
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install only runtime dependencies (procps for health check, no build-essential/gcc)
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    procps \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Copy installed packages from builder (no build tools)
COPY --from=builder /install /usr/local

# Copy source
COPY apps/services/agro-rules/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

# No port exposed - this is a NATS worker service

# Health check - verify process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*worker" || exit 1

CMD ["python", "-m", "src.worker"]
