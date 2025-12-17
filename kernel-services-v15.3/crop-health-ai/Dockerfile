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

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

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

<<<<<<< HEAD
# Install only runtime system dependencies
# Note: libgl1-mesa-glx is replaced by libgl1 in newer Debian versions
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
=======
# Install only runtime system dependencies.
# `libgl1-mesa-glx` may not exist on some Debian slim variants; prefer `libgl1`
# when available and fall back to `libgl1-mesa-glx` otherwise.
RUN apt-get update && \
    (apt-cache show libgl1 >/dev/null 2>&1 && \
        apt-get install -y --no-install-recommends libgl1 libglib2.0-0 curl || \
        apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 curl) \
>>>>>>> 68c4f2a7b84c7c441a567209d85cf70ff80c5c7e
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY src/ ./src/

# Create directories for uploads and models
RUN mkdir -p /app/static/uploads /app/models

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 sahool && \
    chown -R sahool:sahool /app
USER sahool

# Expose port
EXPOSE 8095

# Health check using curl (more reliable than Python)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8095/healthz || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8095", "--workers", "2"]
