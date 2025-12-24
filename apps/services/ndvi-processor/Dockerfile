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

# Configure apt to use HTTPS and install system dependencies for geo-spatial
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/*.list /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    apt-transport-https \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create temp directory
RUN mkdir -p /tmp/ndvi && chown -R sahool:sahool /tmp/ndvi

# Change ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8101

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8101/healthz || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8101"]
