# SAHOOL Astronomical Calendar Service
# خدمة التقويم الفلكي الزراعي
# Multi-stage build for optimized image size
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

ENV PIP_NO_CACHE_DIR=1

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip

# Install dependencies with resilient multi-mirror fallback strategy
COPY constraints.txt .
COPY apps/services/astronomical-calendar/requirements.txt .
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

LABEL maintainer="SAHOOL Team <dev@sahool.io>"
LABEL description="Astronomical Calendar Service for Traditional Yemeni Farming"
LABEL version="16.0.0"

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/sahool/.local
ENV PATH=/home/sahool/.local/bin:$PATH

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8111

# Copy root shared modules (shared.ai, shared.events, etc.)
COPY --chown=sahool:sahool shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py/, shared.middleware/, etc.)
COPY --chown=sahool:sahool apps/services/shared/ ./shared/

# Copy application code
COPY --chown=sahool:sahool apps/services/astronomical-calendar/src/ ./src/

USER sahool

# Expose port
EXPOSE 8111

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8111/healthz').raise_for_status()" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8111"]
