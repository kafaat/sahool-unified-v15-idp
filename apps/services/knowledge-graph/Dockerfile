# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ Knowledge Graph Service - Crop/Disease/Treatment Relationships             ║
# ║ خدمة الرسم البياني للمعرفة - العلاقات بين المحاصيل والأمراض والعلاجات      ║
# ║                                                                            ║
# ║ Multi-stage build for optimized production image                          ║
# ╚════════════════════════════════════════════════════════════════════════════╝

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder - Install dependencies
# ───────────────────────────────────────────────────────────────────────────────
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Install build dependencies (apt-update.sh handles mirror switching)
COPY docker/apt-update.sh docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PIP_NO_CACHE_DIR=1

# Upgrade pip and install build tools with multi-mirror fallback
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" build

# Install Python dependencies
COPY constraints.txt .
COPY apps/services/knowledge-graph/requirements.txt .
RUN pip-install.sh -c constraints.txt -r requirements.txt

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Production - Minimal runtime image
# ───────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

LABEL maintainer="Sahool Team <dev@sahool.io>"
LABEL service="knowledge-graph"
LABEL version="1.0.0"
LABEL description="Knowledge graph service for crop-disease-treatment relationships"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8140 \
    LOG_LEVEL=INFO

WORKDIR /app

# Install only runtime system dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy root shared modules first, then overlay with services shared
COPY shared/ ./shared/
COPY apps/services/shared/ ./shared/


# Copy application code
COPY apps/services/knowledge-graph/src/ ./src/

# Create data directories
RUN mkdir -p /app/data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 sahool && \
    chown -R sahool:sahool /app

# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Expose port
EXPOSE 8140

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8140/healthz')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8140", "--workers", "2"]
