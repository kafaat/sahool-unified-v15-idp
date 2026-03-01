# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL LLM Orchestrator Service
# Multi-stage build with security hardening
# Version: 16.0.0
# Updated: February 2026
# ═══════════════════════════════════════════════════════════════════════════════

ARG PYTHON_VERSION=3.11

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Configure pip with network resilience BEFORE any pip install
RUN mkdir -p ~/.pip && \
    cat > ~/.pip/pip.conf <<'EOF'
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://pypi.org/simple/
trusted-host = mirrors.aliyun.com
               pypi.tuna.tsinghua.edu.cn
               pypi.org
               files.pythonhosted.org
[install]
prefer-binary = true
EOF

# Upgrade pip with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --upgrade pip>=24.0 setuptools>=75.0 wheel>=0.44.0 || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    --upgrade pip>=24.0 setuptools>=75.0 wheel>=0.44.0 || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --upgrade pip>=24.0 setuptools>=75.0 wheel>=0.44.0

# Copy and install dependencies
COPY --chown=sahool:sahool apps/services/llm-orchestrator-service/requirements.txt /tmp/requirements.txt
COPY --chown=sahool:sahool docker/constraints-ai.txt /tmp/constraints-ai.txt

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -c /tmp/constraints-ai.txt -r /tmp/requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

# Labels
LABEL org.opencontainers.image.title="SAHOOL LLM Orchestrator Service" \
      org.opencontainers.image.version="16.0.0" \
      org.opencontainers.image.vendor="KAFAAT" \
      org.opencontainers.image.description="LLM Orchestrator Service for SAHOOL Platform"

# Install runtime dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    PYTHONUNBUFFERED=1 \
    PORT=8164

WORKDIR /app

# Copy shared libraries (root shared first, then service-shared overlay)
COPY --chown=sahool:sahool shared/ ./shared/
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Copy source
COPY --chown=sahool:sahool apps/services/llm-orchestrator-service/src/ ./src/

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8164

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/healthz')" || exit 1

# Run application
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
