# ============================================
# SAHOOL Terrain Core Service Dockerfile
# خدمة تحليل التضاريس الأساسية
# Port: 8185
# Multi-stage build for optimized production image
# ============================================

ARG PYTHON_VERSION=3.11

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder | المرحلة 1: البناء
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="terrain-core-service"
LABEL description="Terrain analysis service with DEM processing and terrain indicators"
LABEL description_ar="خدمة تحليل التضاريس مع معالجة نماذج الارتفاعات ومؤشرات التضاريس"
LABEL version="16.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

# GDAL configuration
ENV GDAL_CACHEMAX=256 \
    GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=.tif,.tiff,.vrt,.xml

# Working directory
WORKDIR /app

# Install system dependencies for geospatial processing (build + runtime)
# GDAL and related libraries for DEM processing
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    # GDAL and geospatial libraries
    libgdal-dev \
    gdal-bin \
    # Build tools (only needed in builder stage)
    build-essential \
    gcc \
    g++ \
    # Required by rasterio/GDAL
    libgeos-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    # NumPy and SciPy dependencies
    libopenblas-dev \
    liblapack-dev \
    # Image processing
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    # Networking
    curl \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip and install build tools with multi-mirror fallback
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip "setuptools>=68.0" wheel build numpy || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip "setuptools>=68.0" wheel build numpy

# Configure pip for better network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf && \
    echo "default-timeout = 300" >> /root/.pip/pip.conf && \
    echo "[install]" >> /root/.pip/pip.conf && \
    echo "prefer-binary = true" >> /root/.pip/pip.conf

# Copy requirements and constraints first for caching
COPY constraints.txt .
COPY apps/services/terrain-core-service/requirements.txt .

# Install Python dependencies with multi-mirror fallback
# Install GDAL Python bindings matching system version
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    GDAL==$(gdal-config --version) || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    GDAL==$(gdal-config --version)

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Production | المرحلة 2: الإنتاج
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8185 \
    GDAL_CACHEMAX=256 \
    GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=.tif,.tiff,.vrt,.xml

WORKDIR /app

# Install runtime-only geospatial libraries (no build-essential, gcc, g++)
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    libgdal32 \
    gdal-bin \
    libgeos-c1v5 \
    libproj25 \
    proj-data \
    proj-bin \
    libopenblas0 \
    liblapack3 \
    libjpeg62-turbo \
    libpng16-16 \
    libtiff6 \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Copy installed Python packages from builder
ARG PYTHON_VERSION
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy shared libraries
COPY shared/ ./shared/

# Copy services shared modules (needed for errors_py module)
COPY apps/services/shared/ ./apps/services/shared/

# Create compatibility layer: copy errors_py to shared/errors_py so imports work
RUN cp -r ./apps/services/shared/errors_py ./shared/ || true

# Copy source code
COPY apps/services/terrain-core-service/src/ ./src/

# Create temp and cache directories
RUN mkdir -p /tmp/terrain /tmp/terrain/dem_cache && \
    chown -R sahool:sahool /tmp/terrain

# Change ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8185

# Health check using Python
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8185/healthz')" || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["tini", "--"]

# Run application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8185"]
