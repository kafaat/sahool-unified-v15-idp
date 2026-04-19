# =============================================================================
# YOLO26 Vision Service Dockerfile
# Multi-stage build with CUDA support for GPU-accelerated inference
# =============================================================================

# Global ARG must be declared before first FROM to be usable in FROM instructions
ARG PYTHON_VERSION=3.11

# -----------------------------------------------------------------------------
# Stage 1: Base image with CUDA
# -----------------------------------------------------------------------------
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04 AS base

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3.11-distutils \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgeos-dev \
    libproj-dev \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    fonts-dejavu-core \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --set python3 /usr/bin/python3.11 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# NVIDIA CUDA Library Path (CRITICAL for GPU)
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
ENV CUDA_HOME=/usr/local/cuda
ENV PATH="${PATH}:${CUDA_HOME}/bin"

# Create non-root user for security (UID/GID 1000 for consistency)
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool sahool

# -----------------------------------------------------------------------------
# Stage 2: Builder stage for dependencies
# -----------------------------------------------------------------------------
FROM base AS builder

# Install build dependencies (apt-update.sh inherited from base stage)
COPY docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip with multi-mirror fallback
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

# Copy constraints and requirements files
COPY docker/constraints-ai.txt /tmp/constraints-ai.txt
COPY apps/services/yolo26-vision-service/requirements.txt /tmp/requirements.txt

# Install PyTorch with CUDA support first (pinned versions)
# Disable pip.conf to prevent mirror hash conflicts with torch dependencies
RUN PIP_CONFIG_FILE=/dev/null pip install --no-cache-dir --timeout=300 --retries=10 \
    torch==2.2.0 \
    torchvision==0.17.0 \
    --index-url https://download.pytorch.org/whl/cu121 \
    --extra-index-url https://pypi.org/simple

# Install remaining dependencies with constraints and multi-mirror fallback
RUN pip-install.sh -c /tmp/constraints-ai.txt -r /tmp/requirements.txt

# -----------------------------------------------------------------------------
# Stage 3: Production image
# -----------------------------------------------------------------------------
FROM base AS production

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/src /app/models /app/logs /app/data \
    && chown -R sahool:sahool /app

# Copy shared modules (required for shared.middleware, shared.auth, etc.)
COPY --chown=sahool:sahool apps/services/shared/ /app/shared/


# Copy application code
# Note: Build context is repo root, so use full path
COPY --chown=sahool:sahool apps/services/yolo26-vision-service/src/ /app/src/
COPY --chown=sahool:sahool apps/services/yolo26-vision-service/requirements.txt /app/

# Create __init__.py files for proper Python packaging
RUN touch /app/src/__init__.py \
    && touch /app/src/api/__init__.py \
    && touch /app/src/api/endpoints/__init__.py \
    && touch /app/src/core/__init__.py \
    && touch /app/src/models/__init__.py \
    && touch /app/src/events/__init__.py

# Environment variables
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO
ENV HOST=0.0.0.0
ENV PORT=8150
ENV MODEL_BASE_PATH=/app/models
ENV DEVICE=cuda:0
ENV HALF_PRECISION=true
ENV ENABLE_TENSORRT=false

# NVIDIA container toolkit settings
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8150/healthz || exit 1

# Expose port
EXPOSE 8150

# Switch to non-root user

# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8150", "--workers", "1"]

# -----------------------------------------------------------------------------
# Stage 4: Development image
# -----------------------------------------------------------------------------
FROM production AS development

# Switch back to root for development setup
USER root

# Install development dependencies with multi-mirror fallback
RUN pip-install.sh pytest pytest-asyncio pytest-cov httpx black ruff mypy ipython

# Set development environment
ENV ENVIRONMENT=development
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG

# Switch back to non-root user
USER sahool

# Run with auto-reload in development
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8150", "--reload"]

# -----------------------------------------------------------------------------
# Stage 5: CPU-only image (for environments without GPU)
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS cpu-only

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
# Note: libgl1-mesa-glx replaced by libgl1 in Debian Trixie
COPY docker/apt-update.sh docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    fonts-dejavu-core \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user (UID/GID 1000 for consistency)
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool sahool

# Set working directory
WORKDIR /app

# Copy constraints and requirements
COPY docker/constraints-ai.txt /tmp/constraints-ai.txt
COPY apps/services/yolo26-vision-service/requirements.txt /tmp/requirements.txt

# Upgrade pip with multi-mirror fallback
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

# Install PyTorch CPU - disable pip.conf to prevent mirror hash conflicts
# (Tsinghua mirror sympy hash differs from PyTorch index expected hash)
RUN PIP_CONFIG_FILE=/dev/null pip install --no-cache-dir --timeout=300 --retries=10 \
    torch torchvision \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple

# Install remaining dependencies with multi-mirror fallback
RUN pip-install.sh -c /tmp/constraints-ai.txt -r /tmp/requirements.txt

# Create directories
RUN mkdir -p /app/src /app/models /app/logs /app/data \
    && chown -R sahool:sahool /app

# Copy shared modules (required for shared.middleware, shared.auth, etc.)
COPY --chown=sahool:sahool apps/services/shared/ /app/shared/

# Copy application code
# Note: Build context is repo root, so use full path
COPY --chown=sahool:sahool apps/services/yolo26-vision-service/src/ /app/src/

# Create __init__.py files
RUN touch /app/src/__init__.py \
    && touch /app/src/api/__init__.py \
    && touch /app/src/api/endpoints/__init__.py \
    && touch /app/src/core/__init__.py \
    && touch /app/src/models/__init__.py \
    && touch /app/src/events/__init__.py

# Environment variables
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO
ENV HOST=0.0.0.0
ENV PORT=8150
ENV MODEL_BASE_PATH=/app/models
ENV DEVICE=cpu
ENV HALF_PRECISION=false
ENV ENABLE_TENSORRT=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8150/healthz || exit 1

# Expose port
EXPOSE 8150

# Switch to non-root user
USER sahool

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8150", "--workers", "1"]
