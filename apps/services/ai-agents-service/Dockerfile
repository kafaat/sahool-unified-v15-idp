# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL AI Agents Service Dockerfile
# Multi-stage build with security hardening
# Port: 8130
# Version: 16.0.0
# Updated: February 2026
# ═══════════════════════════════════════════════════════════════════════════════

ARG PYTHON_VERSION=3.11

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --create-home sahool

USER sahool
WORKDIR /home/sahool

# Create virtual environment
ENV VIRTUAL_ENV=/home/sahool/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Configure pip with resilience and fallback (PyPI first for CI reliability)
RUN mkdir -p ~/.pip && \
    printf '[global]\ntimeout = 300\nretries = 10\nindex-url = https://pypi.org/simple/\nextra-index-url = https://mirrors.aliyun.com/pypi/simple/\n                  https://pypi.tuna.tsinghua.edu.cn/simple/\n[install]\nprefer-binary = true\n' > ~/.pip/pip.conf

# Upgrade pip (multi-mirror fallback)
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

# Copy and install dependencies
COPY --chown=sahool:sahool apps/services/ai-agents-service/requirements.txt /tmp/requirements.txt
COPY --chown=sahool:sahool docker/constraints-ai.txt /tmp/constraints-ai.txt

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Production
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

# Labels
LABEL org.opencontainers.image.title="SAHOOL AI Agents Service" \
      org.opencontainers.image.version="16.0.0" \
      org.opencontainers.image.vendor="KAFAAT" \
      org.opencontainers.image.description="AI Agents Service for autonomous agricultural intelligence"

# Install runtime dependencies (curl for health check)
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --create-home sahool

# Copy virtual environment
COPY --from=builder --chown=sahool:sahool /home/sahool/venv /home/sahool/venv

# Set environment
ENV VIRTUAL_ENV=/home/sahool/venv \
    PATH="/home/sahool/venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy shared modules (root shared first, then service-shared overlay)
COPY --chown=sahool:sahool shared/ ./shared/
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Copy source code
COPY --chown=sahool:sahool apps/services/ai-agents-service/src/ ./src/

# Create __init__.py files for Python packaging
RUN touch ./src/__init__.py \
    ./src/api/__init__.py \
    ./src/api/v1/__init__.py \
    ./src/events/__init__.py 2>/dev/null || true

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8130

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8130/healthz || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8130"]
