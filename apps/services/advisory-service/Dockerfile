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


# Configure pip for network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    cat > /root/.pip/pip.conf <<'EOF'
[global]
timeout = 300
retries = 10
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
                  https://pypi.org/simple/
[install]
prefer-binary = true
EOF

# Upgrade pip with fallback to Aliyun mirror
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip || \
    pip install --no-cache-dir --index-url https://pypi.org/simple --upgrade pip || true

# Install dependencies with fallback to Aliyun mirror
COPY apps/services/advisory-service/requirements.txt .
COPY constraints.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Try official PyPI first with long timeout, then fallback to Aliyun, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

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
