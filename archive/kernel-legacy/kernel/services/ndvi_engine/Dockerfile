# SAHOOL NDVI Engine Service
# ===========================
# Uses shared base image for consistency
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

# Build arguments
ARG SERVICE_NAME=ndvi-engine
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create non-root user
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip (non-fatal in case of network issues)
RUN pip install --upgrade pip || true

# Configure pip for better network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    cat > /root/.pip/pip.conf <<'EOF'
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://pypi.org/simple/
trusted-host = mirrors.aliyun.com
               pypi.tuna.tsinghua.edu.cn
               pypi.org
               files.pythonhosted.org
[install]
prefer-binary = true
EOF

# Install dependencies with resilient multi-mirror fallback strategy
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -r requirements.txt

# Copy shared libraries

# Copy source
COPY src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

EXPOSE 8097

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8097/healthz || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8097"]
