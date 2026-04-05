ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

# Python environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool


# Upgrade pip to latest version with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

# Install dependencies
# Install build dependencies for cryptography/bcrypt
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY apps/services/indicators-service/requirements.txt .
COPY constraints.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Try PyPI first, then fallback to Aliyun, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# Remove build tools from runtime image (reduce attack surface)
RUN apt-get purge -y --auto-remove build-essential gcc libffi-dev 2>/dev/null; \
    rm -rf /var/lib/apt/lists/*

# Copy root shared modules (shared.events, shared.monitoring, etc.)
COPY shared/ ./shared/

# Copy services shared modules overlay (shared.errors_py, shared.logging_config, etc.)
COPY apps/services/shared/ ./shared/

# Resolve errors_py file/package ambiguity
RUN rm -f ./shared/errors_py.py

# Copy source code
COPY apps/services/indicators-service/src/ ./src/

# Set ownership and switch to non-root user
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

# Expose port
EXPOSE 8091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8091/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8091"]
