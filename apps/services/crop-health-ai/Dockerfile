# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ ⚠️  FROZEN SERVICE - DO NOT USE IN PRODUCTION                              ║
# ║ This service has been replaced by: crop-intelligence-service (port 8095)  ║
# ║ Port Conflict: 8095                                                         ║
# ║ See: docs/DEPRECATED_SERVICES.md                                           ║
# ╚════════════════════════════════════════════════════════════════════════════╝
#
# ═══════════════════════════════════════════════════════════════════════════════
# Sahool Vision - Crop Health AI Service
# خدمة سهول فيجن للذكاء الاصطناعي
#
# Multi-stage build for optimized production image
# ═══════════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder - Install dependencies
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Configure apt to use HTTPS and install build dependencies
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/*.list /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

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

# Install Python dependencies
COPY apps/services/crop-health-ai/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Production - Minimal runtime image
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS production

LABEL maintainer="Sahool Team <dev@sahool.io>"
LABEL service="crop-health-ai"
LABEL version="2.2.0"
LABEL description="AI-powered plant disease detection for Yemen agriculture"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PORT=8095 \
    LOG_LEVEL=INFO

WORKDIR /app

# Install only runtime system dependencies for OpenCV
# libgl1 and libglib2.0-0 are required for cv2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy shared modules
COPY apps/services/shared ./shared/

# Copy application code
COPY apps/services/crop-health-ai/src/ ./src/

# Create directories for uploads and models
RUN mkdir -p /app/static/uploads /app/models

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 sahool && \
    chown -R sahool:sahool /app
USER sahool

# Expose port
EXPOSE 8095

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8095/healthz')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8095", "--workers", "2"]
