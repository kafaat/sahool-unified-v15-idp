# SAHOOL Notification Service
# خدمة الإشعارات المخصصة
# Multi-stage build for optimized image size
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/notification-service/requirements.txt .
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

LABEL maintainer="SAHOOL Team"
LABEL service="notification-service"
LABEL version="16.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/sahool/.local
ENV PATH=/home/sahool/.local/bin:$PATH

# Copy root shared modules first (shared.cache, shared.middleware.security_headers, etc.)
COPY --chown=sahool:sahool shared/ ./shared/

# Copy services shared modules (merge into shared/ without overwriting root modules)
COPY --chown=sahool:sahool apps/services/shared/ ./services_shared/

# Resolve errors_py file/package ambiguity
RUN rm -f ./shared/errors_py.py

# Copy application code
COPY --chown=sahool:sahool apps/services/notification-service/src/ ./src/

# Copy migration files and config for Tortoise ORM built-in migrations
COPY --chown=sahool:sahool apps/services/notification-service/migrations/ ./migrations/
COPY --chown=sahool:sahool apps/services/notification-service/pyproject.toml ./pyproject.toml


# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /home/sahool/.local/lib/python*/site-packages/setuptools* \
           /home/sahool/.local/lib/python*/site-packages/pip* \
           /home/sahool/.local/lib/python*/site-packages/wheel* \
           /home/sahool/.local/lib/python*/site-packages/pkg_resources* \
           /home/sahool/.local/lib/python*/site-packages/jaraco* \
           /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Default port (can be overridden via PORT env var)
ENV PORT=8110
EXPOSE 8110

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8110/healthz')" || exit 1

# Run the application (uses PORT environment variable)
# NOTE: In production, run migrations before starting the app:
#   python -m tortoise migrate
# This can be done via an init container in Kubernetes or an entrypoint script.
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8110"]
