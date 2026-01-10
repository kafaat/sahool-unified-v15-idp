# ============================================
# SAHOOL Field Service Dockerfile
# خدمة إدارة الحقول الزراعية
# Port: 3000
# ============================================

FROM python:3.11-slim

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="field-service"
LABEL version="16.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    PORT=8115

# Create non-root user
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Working directory
WORKDIR /app

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* || true

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel build

# Configure pip for better network resilience
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf && \
    echo "default-timeout = 300" >> /root/.pip/pip.conf && \
    echo "[install]" >> /root/.pip/pip.conf && \
    echo "prefer-binary = true" >> /root/.pip/pip.conf

# Copy requirements first for caching
COPY apps/services/field-service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Copy shared modules
COPY shared/ ./shared/

# Copy services shared modules (needed for errors_py module)
COPY apps/services/shared/ ./apps/services/shared/

# Create compatibility layer: copy errors_py to shared/errors_py so imports work
RUN cp -r ./apps/services/shared/errors_py ./shared/ || true

# Copy source code
COPY apps/services/field-service/src/ ./src/

# Change ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8115

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8115/healthz')" || exit 1

# Run application
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8115}"]
