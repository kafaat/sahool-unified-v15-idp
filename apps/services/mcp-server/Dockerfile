# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL MCP Server Dockerfile
# Multi-stage build for optimized production image
# ═══════════════════════════════════════════════════════════════════════════════

ARG PYTHON_VERSION=3.11

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and constraints
COPY constraints.txt .
COPY apps/services/mcp-server/requirements.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

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
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy installed packages from builder (no gcc in production)
COPY --from=builder /install /usr/local

# Copy root shared modules (shared.ai, shared.events, etc.)
COPY shared/ /app/shared/

# Copy services shared modules overlay (shared.errors_py/, shared.middleware/, etc.)
COPY apps/services/shared/ /app/shared/

# Resolve errors_py file/package ambiguity
RUN rm -f s/shared/errors_py.py

# Copy service code
COPY apps/services/mcp-server/src/ /app/src/

# Set ownership
RUN chown -R sahool:sahool /app

# Set Python path
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user

# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Default port (can be overridden via MCP_SERVER_PORT env var)
# Changed from 8200 to 8201 to resolve conflict with HashiCorp Vault
ENV MCP_SERVER_PORT=8201
EXPOSE 8201

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import os,httpx; httpx.get(f'http://localhost:{os.environ.get(\"MCP_SERVER_PORT\",8201)}/health')" || exit 1

# Run server
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${MCP_SERVER_PORT}"]
