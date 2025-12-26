# ═══════════════════════════════════════════════════════════════════════════════
# Sahool Yield Engine - ML Crop Yield Prediction
# محرك توقع الإنتاجية
#
# Multi-stage build for optimized production image
# ═══════════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install build dependencies (needed for compiling Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Production
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS production

LABEL maintainer="Sahool Team <dev@sahool.io>"
LABEL service="yield-engine"
LABEL version="1.0.0"
LABEL description="ML-powered crop yield prediction for Yemen agriculture"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8117 \
    LOG_LEVEL=INFO

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY src/ .

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 sahool && \
    chown -R sahool:sahool /app
USER sahool

EXPOSE 8117

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8117/healthz')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8117", "--workers", "2"]
