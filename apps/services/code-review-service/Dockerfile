ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Install Python dependencies
COPY constraints.txt .
COPY apps/services/code-review-service/requirements.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Try Aliyun mirror first with long timeout, then fallback to PyPI, finally Tencent
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
COPY apps/services/shared/ ./shared/

# Create logs directory and set ownership first
RUN mkdir -p /app/logs && \
    chown -R sahool:sahool /app

# Copy application code
COPY apps/services/code-review-service/src/ ./src/
COPY apps/services/code-review-service/config/ ./config/

# Ensure ownership is correct after copying
RUN chown -R sahool:sahool /app

# Expose API port (standardized to 8102 per docker-compose.yml)
EXPOSE 8102

# Switch to non-root user
USER sahool

# Health check - verify API is responding
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8102/health').read()" || exit 1

# Run the service
CMD ["python", "-m", "src.main"]
