# ═══════════════════════════════════════════════════════════════════════════════
# Virtual Sensors Engine - Dockerfile
# محرك المستشعرات الافتراضية - FAO-56 ET0 Calculations
#
# Multi-stage build for optimized production image
# ═══════════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder - Install dependencies
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install build dependencies (needed for compiling Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with retry logic for network resilience
COPY apps/services/virtual-sensors/requirements.txt .
# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel && \
    pip install --no-cache-dir \
    --timeout=300 \
    --retries=10 \
    -r requirements.txt || \
    (sleep 5 && pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt)

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Production - Minimal runtime image
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS production

LABEL maintainer="Sahool Team <dev@sahool.io>"
LABEL service="virtual-sensors"
LABEL version="2.0.0"
LABEL description="Virtual Sensors Engine for Smart Irrigation - FAO-56 ET0"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8119 \
    LOG_LEVEL=INFO

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy shared modules
COPY apps/services/shared ./shared/

# Copy application code
COPY apps/services/virtual-sensors/src/ ./src/

# Create non-root user for security (consistent with other services)
RUN useradd --create-home --shell /bin/bash --uid 1000 sahool && \
    chown -R sahool:sahool /app
USER sahool

# Expose port (can be overridden via PORT env var)
EXPOSE 8119

# Health check using Python (no curl needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD sh -c "python -c \"import urllib.request, os; port=os.getenv('PORT', '8119'); urllib.request.urlopen(f'http://localhost:{port}/healthz')\"" || exit 1

# Run the application
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8119}"]
