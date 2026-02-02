# Leveling Optimizer Service Dockerfile
# خدمة تحسين التسوية

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Builder stage
FROM base AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configure pip for network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf && \
    echo "trusted-host = pypi.org files.pythonhosted.org pypi.tuna.tsinghua.edu.cn" >> /root/.pip/pip.conf

# Copy requirements first for better caching
# Note: Build context is repo root, so use full path
COPY apps/services/leveling-optimizer-service/requirements.txt .

# Install Python dependencies with fallback to Tsinghua mirror
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt || \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# Production stage
FROM base AS production

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
# Note: Build context is repo root, so use full path
COPY --chown=appuser:appgroup apps/services/leveling-optimizer-service/src ./src

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8170

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8170/healthz || exit 1

# Labels
LABEL org.opencontainers.image.title="Leveling Optimizer Service" \
    org.opencontainers.image.description="Agricultural field leveling optimization service for SAHOOL" \
    org.opencontainers.image.version="16.0.0" \
    org.opencontainers.image.vendor="KAFAAT" \
    org.opencontainers.image.source="https://github.com/kafaat/sahool"

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8170"]
