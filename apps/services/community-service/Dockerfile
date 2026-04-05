# SAHOOL Community Service
# ========================
# Rocket.Chat integration for farmer community messaging
# Version: 16.0.0

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Build arguments
ARG SERVICE_NAME=community-service
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# Create non-root user
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Install tini for proper PID 1 signal handling
RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*

# Configure pip for network resilience with fallback mirrors
RUN mkdir -p /root/.pip && \
    printf '[global]\ntimeout = 300\nretries = 10\nindex-url = https://mirrors.aliyun.com/pypi/simple/\nextra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/\n                  https://pypi.org/simple/\n[install]\nprefer-binary = true\n' > /root/.pip/pip.conf

# Upgrade pip with fallback to Aliyun mirror
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --index-url https://pypi.org/simple --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || true

# Install dependencies with resilient multi-mirror fallback strategy
# Try official PyPI first with long timeout, then fallback to Aliyun, finally Tencent
COPY apps/services/community-service/requirements.txt .
COPY constraints.txt .
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# Copy shared libraries
COPY apps/services/shared/ ./shared/

# Resolve errors_py file/package ambiguity
RUN rm -f s/shared/errors_py.py

# Copy source
COPY apps/services/community-service/src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app


# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Default port
ENV PORT=8133
EXPOSE 8133

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8133/healthz')" || exit 1

ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8133"]
