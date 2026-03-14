# ===============================================================================
# SAHOOL WeChat Integration Service Dockerfile
# Port: 8135
# ===============================================================================

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

# Security: Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install system dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --upgrade pip || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --upgrade pip

# Install dependencies
COPY constraints.txt .
COPY apps/services/wechat-service/requirements.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Try Aliyun first with long timeout, then fallback to PyPI, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    -c constraints.txt -r requirements.txt

# Copy shared modules
COPY shared/ ./shared/

# Copy source code
COPY apps/services/wechat-service/src/ ./src/

# Create __init__.py files if needed
RUN touch ./src/__init__.py 2>/dev/null || true

# Set Python path for shared module imports
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Security: Change ownership and use non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Expose port
EXPOSE 8135

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8135/healthz || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8135"]
