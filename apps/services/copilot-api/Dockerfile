# SAHOOL Copilot API Dockerfile
# Dockerfile لـ Copilot API

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────────────────────────────────────
# Dependencies Stage
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS dependencies

# Copy requirements and constraints
COPY constraints.txt .
COPY apps/services/copilot-api/requirements.txt .

# Install Python dependencies with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip setuptools wheel || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip setuptools wheel

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -c constraints.txt -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Production Stage
# ─────────────────────────────────────────────────────────────────────────────
FROM dependencies AS production

# Copy shared modules (required for shared.ai imports)
COPY shared/ ./shared/

# Copy application code
COPY apps/services/copilot-api/src/ ./src/

# Create non-root user for security (standard sahool user)
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool
RUN chown -R sahool:sahool /app
USER sahool

# Expose port
EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8088/healthz || exit 1

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8088"]

# ─────────────────────────────────────────────────────────────────────────────
# Development Stage
# ─────────────────────────────────────────────────────────────────────────────
FROM dependencies AS development

# Install development dependencies with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    pytest pytest-asyncio pytest-cov mypy || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    pytest pytest-asyncio pytest-cov mypy

# Copy application code
COPY apps/services/copilot-api/ .

# Set Python path
ENV PYTHONPATH=/app

# Run with reload for development
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8088", "--reload"]
