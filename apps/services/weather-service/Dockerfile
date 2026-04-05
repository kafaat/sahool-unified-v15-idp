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

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
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
# setuptools>=78.1.1 for CVE-2024-6345, PYSEC-2025-49; wheel>=0.46.2 for CVE-2026-24049
# jaraco.context>=6.1.0 for CVE-2026-23949 (pinned here as constraints.txt is not yet copied)
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" "jaraco.context>=6.1.0" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" "jaraco.context>=6.1.0"

# Configure pip for network resilience with multi-mirror fallback
# Mirrors: Aliyun (primary) → Tsinghua → Tencent → PyPI (global fallback)
RUN mkdir -p ~/.pip && \
    printf '[global]\ntimeout = 300\nretries = 10\nindex-url = https://mirrors.aliyun.com/pypi/simple/\nextra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/\n                  https://mirrors.cloud.tencent.com/pypi/simple\n                  https://pypi.org/simple/\n[install]\nprefer-binary = true\n' > ~/.pip/pip.conf

# Copy and install dependencies
COPY --chown=sahool:sahool apps/services/weather-service/requirements.txt /tmp/requirements.txt
COPY --chown=sahool:sahool constraints.txt /tmp/constraints.txt

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c /tmp/constraints.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple \
    -c /tmp/constraints.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
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

# Upgrade system packages and install minimal runtime dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends ca-certificates \
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

# Strip build tools from production venv (reduces attack surface and CVE footprint)
RUN pip uninstall -y pip setuptools wheel 2>/dev/null || true; \
    rm -rf /home/sahool/venv/lib/python*/site-packages/pip* \
           /home/sahool/venv/lib/python*/site-packages/setuptools* \
           /home/sahool/venv/lib/python*/site-packages/wheel* \
           /home/sahool/venv/lib/python*/site-packages/_distutils_hack* \
           /home/sahool/venv/lib/python*/site-packages/pkg_resources* \
           /home/sahool/venv/lib/python*/site-packages/jaraco/context* \
           /home/sahool/venv/lib/python*/site-packages/jaraco.context-*.dist-info \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/jaraco/context* \
           /usr/local/lib/python*/site-packages/jaraco.context-*.dist-info 2>/dev/null || true && \
    if python -c "import pip" 2>/dev/null; then echo "ERROR: pip still present after stripping" >&2; exit 1; fi && \
    if python -c "import jaraco.context" 2>/dev/null; then echo "ERROR: jaraco.context still present after stripping" >&2; exit 1; fi

# Copy shared modules
# Order matters: apps/services/shared/ overlays on top of shared/
# to provide service-specific implementations (auth, errors_py, middleware).
COPY --chown=sahool:sahool shared/ /app/shared/
COPY --chown=sahool:sahool apps/services/shared/ /app/shared/

# Resolve module ambiguity: when both errors_py.py (file) and errors_py/ (package)
# exist, Python prefers the package but this can cause import confusion.
# Remove the standalone file since the package version is authoritative.
RUN rm -f /app/shared/errors_py.py

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

# Health check - start_period gives the service enough time to initialize
# connections (DB, NATS) before health checks count toward failure threshold
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8092/healthz')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8092"]
