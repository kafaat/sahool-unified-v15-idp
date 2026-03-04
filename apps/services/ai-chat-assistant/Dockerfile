# SAHOOL AI Chat Assistant Service
# خدمة مساعد الشات الذكي
# Multi-stage build for optimized image size
# Port: 8260

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
RUN (apt-get update || (sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null; apt-get update)) && apt-get install -y --no-install-recommends \
    build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip "setuptools>=68.0" wheel build || \
    pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip "setuptools>=68.0" wheel build

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/ai-chat-assistant/requirements.txt .
COPY constraints.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --user -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --user -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --user -c constraints.txt -r requirements.txt

# Stage 2: Production
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="ai-chat-assistant"
LABEL version="16.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    PORT=8260

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/sahool/.local
ENV PATH=/home/sahool/.local/bin:$PATH

# Copy shared libraries
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Copy source code
COPY --chown=sahool:sahool apps/services/ai-chat-assistant/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8260

# Health check using Python (no curl dependency needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8260/healthz')" || exit 1

# Run application
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8260}"]
