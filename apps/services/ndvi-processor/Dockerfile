# ============================================
# SAHOOL NDVI Processor Dockerfile
# خدمة معالجة صور الأقمار الصناعية
# Port: 8101
# ============================================

FROM python:3.11-slim

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="ndvi-processor"
LABEL version="16.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8101

# Create non-root user
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Working directory
WORKDIR /app

# Install system dependencies for geo-spatial processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Copy shared configuration (needed for cors_config)
# Note: Build context must be set to apps/services/ directory
COPY shared/__init__.py ./shared/
COPY shared/config/ ./shared/config/

# Create temp directory
RUN mkdir -p /tmp/ndvi && chown -R sahool:sahool /tmp/ndvi

# Change ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8101

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8101/healthz')" || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8101"]
