# SAHOOL Agro Advisor Service
# ============================
# Uses shared base image for consistency
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Build arguments
ARG SERVICE_NAME=agro-advisor
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


<<<<<<< HEAD
# Upgrade pip (non-fatal in case of network issues)
# Upgrade pip with resilient fallback
RUN pip install --no-cache-dir --timeout=300 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip || \
    pip install --no-cache-dir --timeout=300 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --upgrade pip || true
=======
# Configure pip for network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf && \
    echo "trusted-host = pypi.org files.pythonhosted.org pypi.tuna.tsinghua.edu.cn" >> /root/.pip/pip.conf

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip || true
>>>>>>> f99c62da2680b351d221bafb033e854a2b05532c

# Install dependencies with fallback to Tsinghua mirror
COPY apps/services/advisory-service/requirements.txt .
<<<<<<< HEAD
# Install dependencies with resilient multi-mirror fallback strategy
# Try Aliyun mirror first (fast in China), fallback to official PyPI
RUN pip install --no-cache-dir --timeout=300 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=300 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt
=======
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt || \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
>>>>>>> f99c62da2680b351d221bafb033e854a2b05532c

# Copy shared libraries
COPY apps/services/shared/ ./shared/

# Copy source
COPY apps/services/advisory-service/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

# Default port (can be overridden via PORT env var)
ENV PORT=8093
EXPOSE 8093

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8093/healthz')" || exit 1

CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
