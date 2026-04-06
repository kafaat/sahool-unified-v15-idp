ARG PYTHON_VERSION=3.11

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

# Install system dependencies needed for building
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for clean copy to production
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
COPY constraints.txt .
COPY apps/services/code-review-service/requirements.txt .
# Install with resilient multi-mirror fallback strategy
# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# Strip build tools from venv (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /app/venv/lib/python*/site-packages/setuptools* \
           /app/venv/lib/python*/site-packages/pip* \
           /app/venv/lib/python*/site-packages/wheel* \
           /app/venv/lib/python*/site-packages/_distutils_hack* \
           /app/venv/lib/python*/site-packages/pkg_resources* \
           /app/venv/lib/python*/site-packages/jaraco* \
           /app/venv/bin/pip* 2>/dev/null || true

# ── Stage 2: Production ─────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

WORKDIR /app

# Install runtime-only system dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Copy virtual environment from builder
COPY --from=builder --chown=sahool:sahool /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy shared modules (platform shared/ first, then service-specific overlay)
COPY --chown=sahool:sahool shared/ ./shared/
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Resolve errors_py file/package ambiguity
RUN rm -f ./shared/errors_py.py

# Create logs directory
RUN mkdir -p /app/logs && chown -R sahool:sahool /app/logs

# Copy application code
COPY --chown=sahool:sahool apps/services/code-review-service/src/ ./src/
COPY --chown=sahool:sahool apps/services/code-review-service/config/ ./config/

# Set Python path for shared module imports
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Expose API port (standardized to 8102 per docker-compose.yml)
EXPOSE 8102

# Switch to non-root user
USER sahool

# Health check - verify API is responding
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8102/health').read()" || exit 1

# Run the service
CMD ["python", "-m", "src.main"]
