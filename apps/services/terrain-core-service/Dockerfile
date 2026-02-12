# ============================================
# SAHOOL Terrain Core Service Dockerfile
# خدمة تحليل التضاريس الأساسية
# Port: 8160
# ============================================

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="terrain-core-service"
LABEL description="Terrain analysis service with DEM processing and terrain indicators"
LABEL description_ar="خدمة تحليل التضاريس مع معالجة نماذج الارتفاعات ومؤشرات التضاريس"
LABEL version="16.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    PORT=8185 \
    # GDAL configuration
    GDAL_CACHEMAX=256 \
    GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=.tif,.tiff,.vrt,.xml

# Create non-root user
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Working directory
WORKDIR /app

# Install system dependencies for geospatial processing
# GDAL and related libraries for DEM processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    # GDAL and geospatial libraries
    libgdal-dev \
    gdal-bin \
    # Build tools
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

# GDAL version is determined at runtime via gdal-config

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/  --no-cache-dir --upgrade pip && \
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir --upgrade "setuptools>=68.0" wheel build numpy

# Configure pip for better network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf && \
    echo "default-timeout = 300" >> /root/.pip/pip.conf && \
    echo "trusted-host = pypi.org files.pythonhosted.org pypi.tuna.tsinghua.edu.cn" >> /root/.pip/pip.conf && \
    echo "[install]" >> /root/.pip/pip.conf && \
    echo "prefer-binary = true" >> /root/.pip/pip.conf

# Copy requirements first for caching
COPY apps/services/terrain-core-service/requirements.txt .

# Install Python dependencies
# Install GDAL Python bindings matching system version, with fallback to Tsinghua mirror
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir --timeout=300 --retries=10 GDAL==$(gdal-config --version) && \
    (pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir --timeout=300 --retries=10 -r requirements.txt || \
     pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt)

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

# Run application
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8185}"]
