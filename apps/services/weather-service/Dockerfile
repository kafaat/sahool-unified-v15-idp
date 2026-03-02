# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Weather Service
# Multi-stage build for optimized production image
# Version: 16.0.0
# ═══════════════════════════════════════════════════════════════════════════════

ARG PYTHON_VERSION=3.11

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder | المرحلة 1: البناء
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for build
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --create-home sahool

USER sahool
WORKDIR /home/sahool

# Create virtual environment
ENV VIRTUAL_ENV=/home/sahool/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip and build tools with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --upgrade pip>=24.0 setuptools>=75.0 wheel>=0.44.0 || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --upgrade pip>=24.0 setuptools>=75.0 wheel>=0.44.0

# Configure pip for network resilience with multi-mirror fallback
# Mirrors: Aliyun (primary) → Tsinghua → Tencent → PyPI (global fallback)
RUN mkdir -p ~/.pip && \
    cat > ~/.pip/pip.conf <<'EOF'
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://mirrors.cloud.tencent.com/pypi/simple
                  https://pypi.org/simple/
trusted-host = mirrors.aliyun.com
               pypi.tuna.tsinghua.edu.cn
               mirrors.cloud.tencent.com
               pypi.org
               files.pythonhosted.org
[install]
prefer-binary = true
EOF

# Copy and install dependencies
COPY --chown=sahool:sahool apps/services/weather-service/requirements.txt /tmp/requirements.txt
COPY --chown=sahool:sahool constraints.txt /tmp/constraints.txt

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    -c /tmp/constraints.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -c /tmp/constraints.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -c /tmp/constraints.txt -r /tmp/requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Production | المرحلة 2: الإنتاج
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

# Build arguments
ARG SERVICE_NAME=weather-service
ARG SERVICE_VERSION=16.0.0

# Labels
LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}" \
      org.opencontainers.image.version="${SERVICE_VERSION}" \
      org.opencontainers.image.vendor="KAFAAT" \
      org.opencontainers.image.description="Weather Service - Weather data and forecasts"

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --create-home sahool

# Copy virtual environment from builder
COPY --from=builder --chown=sahool:sahool /home/sahool/venv /home/sahool/venv

# Set virtual environment path
ENV VIRTUAL_ENV=/home/sahool/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy shared modules
COPY --chown=sahool:sahool shared/ /app/shared/
COPY --chown=sahool:sahool apps/services/shared/ /app/shared/

# Copy application code
COPY --chown=sahool:sahool apps/services/weather-service/src /app/src

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8092

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8092

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8092/healthz')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8092"]
