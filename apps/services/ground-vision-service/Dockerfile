# ═══════════════════════════════════════════════════════════════════════════════
# Ground Vision Service Dockerfile
# خدمة الرؤية الأرضية
# ═══════════════════════════════════════════════════════════════════════════════

# Build stage for dependencies
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements, constraints and install dependencies with multi-mirror fallback
COPY constraints.txt .
COPY apps/services/ground-vision-service/requirements.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip setuptools wheel || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip setuptools wheel

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --prefix=/install -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --prefix=/install -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --prefix=/install -c constraints.txt -r requirements.txt

# ═══════════════════════════════════════════════════════════════════════════════
# Production stage
# ═══════════════════════════════════════════════════════════════════════════════

FROM python:${PYTHON_VERSION}-slim-bookworm AS production

LABEL org.opencontainers.image.title="Ground Vision Service"
LABEL org.opencontainers.image.description="High-frequency agricultural monitoring using tower cameras"
LABEL org.opencontainers.image.version="16.0.0"
LABEL org.opencontainers.image.vendor="KAFAAT"
LABEL org.opencontainers.image.source="https://github.com/kafaat/sahool-unified-v15-idp"

WORKDIR /app

# Install runtime dependencies (Bookworm package names)
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    libpq5 \
    libgdal32 \
    libgeos-c1v5 \
    libproj25 \
    # OpenCV dependencies
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash sahool

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy root shared modules (shared.ai, shared.events, etc.)
COPY shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py/, shared.middleware/, etc.)
COPY apps/services/shared/ ./shared/

# Copy application code
COPY apps/services/ground-vision-service/requirements.txt .
COPY apps/services/ground-vision-service/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8182 \
    LOG_LEVEL=INFO \
    ENVIRONMENT=production

# Expose port
EXPOSE 8182

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8182/healthz')" || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8182"]
