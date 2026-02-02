# ═══════════════════════════════════════════════════════════════════════════════
# Ground Vision Service Dockerfile
# خدمة الرؤية الأرضية
# ═══════════════════════════════════════════════════════════════════════════════

# Build stage for dependencies
<<<<<<< HEAD
FROM python:3.12-slim as builder
=======
FROM python:3.11-slim-bookworm as builder
>>>>>>> origin/main

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
<<<<<<< HEAD
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
=======
COPY apps/services/ground-vision-service/requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip && \
    pip install --no-cache-dir --timeout=300 --retries=10 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --prefix=/install -r requirements.txt
>>>>>>> origin/main

# ═══════════════════════════════════════════════════════════════════════════════
# Production stage
# ═══════════════════════════════════════════════════════════════════════════════

<<<<<<< HEAD
FROM python:3.12-slim
=======
FROM python:3.11-slim-bookworm
>>>>>>> origin/main

LABEL org.opencontainers.image.title="Ground Vision Service"
LABEL org.opencontainers.image.description="High-frequency agricultural monitoring using tower cameras"
LABEL org.opencontainers.image.version="16.0.0"
LABEL org.opencontainers.image.vendor="KAFAAT"
LABEL org.opencontainers.image.source="https://github.com/kafaat/sahool-unified-v15-idp"

WORKDIR /app

<<<<<<< HEAD
# Install runtime dependencies
=======
# Install runtime dependencies (Bookworm package names)
>>>>>>> origin/main
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgdal32 \
    libgeos-c1v5 \
    libproj25 \
    # OpenCV dependencies
<<<<<<< HEAD
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
=======
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
>>>>>>> origin/main
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
<<<<<<< HEAD
COPY src/ ./src/
=======
COPY apps/services/ground-vision-service/requirements.txt .
COPY apps/services/ground-vision-service/src/ ./src/
>>>>>>> origin/main

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

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
