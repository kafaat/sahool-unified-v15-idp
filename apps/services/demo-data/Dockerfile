ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

LABEL maintainer="KAFAAT Team"
LABEL description="SAHOOL Demo Data Service - Simulates API data flow"
LABEL version="16.0.0"

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install dependencies with multi-mirror fallback for network resilience
# Mirrors: PyPI (official) → Aliyun → Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --upgrade pip && \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    httpx[http2] || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    httpx[http2] || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    httpx[http2]

# Copy application
COPY apps/services/demo-data/main.py .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Environment defaults
ENV KONG_URL=http://kong:8000 \
    LOG_LEVEL=INFO \
    DEMO_MODE=continuous \
    INTERVAL_SECONDS=30

# Health check - verify process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*main.py" || exit 1

CMD ["python", "-u", "main.py"]
