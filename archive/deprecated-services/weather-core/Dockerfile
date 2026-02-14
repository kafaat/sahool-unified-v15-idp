# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Weather Core Service
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

# Configure pip for network resilience
RUN mkdir -p ~/.pip && \
    cat > ~/.pip/pip.conf <<'EOF'
[global]
timeout = 600
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.org/simple/
trusted-host = mirrors.aliyun.com
[install]
prefer-binary = true
EOF

# Upgrade pip and build tools
RUN pip install --no-cache-dir --upgrade \
    pip>=24.0 \
    "setuptools>=68.0" \
    wheel>=0.44.0

# Copy and install dependencies
COPY --chown=sahool:sahool apps/services/weather-core/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --timeout=600 --retries=10 \
    -r /tmp/requirements.txt || \
    (sleep 5 && pip install --no-cache-dir --timeout=600 --retries=10 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r /tmp/requirements.txt)

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime | المرحلة 2: وقت التشغيل
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

# Build arguments
ARG SERVICE_NAME=weather-core
ARG SERVICE_VERSION=16.0.0

# Labels
LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}" \
      org.opencontainers.image.version="${SERVICE_VERSION}" \
      org.opencontainers.image.vendor="KAFAAT" \
      org.opencontainers.image.description="Weather Core Service - Weather data and forecasts"

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
COPY --chown=sahool:sahool apps/services/weather-core/src /app/src

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
