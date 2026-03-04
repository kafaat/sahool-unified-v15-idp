# ═══════════════════════════════════════════════════════════════════════════════
# Virtual Sensors Engine - Dockerfile
# محرك المستشعرات الافتراضية - FAO-56 ET0 Calculations
#
# Multi-stage build for optimized production image
# ═══════════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder - Install dependencies
# ───────────────────────────────────────────────────────────────────────────────
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Install build dependencies (needed for compiling Python packages)
RUN (apt-get update || (sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null; apt-get update)) && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with multi-mirror fallback
COPY constraints.txt .
COPY apps/services/virtual-sensors/requirements.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip setuptools wheel || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip setuptools wheel

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Production - Minimal runtime image
# ───────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

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
