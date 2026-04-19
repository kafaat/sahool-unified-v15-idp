# SAHOOL Irrigation Smart Service
# Multi-stage build for optimized image size
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
COPY docker/apt-update.sh docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/irrigation-smart/requirements.txt .
COPY constraints.txt .
RUN pip-install.sh --user -c constraints.txt -r requirements.txt

# Stage 2: Production
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

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

# Copy shared modules
# NOTE: the service imports BOTH `apps/services/shared/*` (errors_py,
# logging_config, middleware, observability, etc. — available at /app/shared/
# via the COPY below) AND `shared.events.subjects` + `shared.db.ssl` from
# the top-level `shared/` tree. Those subpackages are NOT in
# apps/services/shared/, so we layer them on top without shadowing the
# apps/services/shared/ contents.
COPY --chown=sahool:sahool apps/services/shared ./shared/
COPY --chown=sahool:sahool shared/events/       ./shared/events/
COPY --chown=sahool:sahool shared/db/           ./shared/db/

# Copy source code
COPY --chown=sahool:sahool apps/services/irrigation-smart/src/ ./src/

# Ship migrations so operators can apply them from the image (psql or init
# container). /api/v1/irrigation/schedules reads/writes the table created
# by migrations/001_create_irrigation_schedules.sql.
COPY --chown=sahool:sahool apps/services/irrigation-smart/migrations/ ./migrations/


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

# Expose port
EXPOSE 8094

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8094/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8094"]
