FROM python:3.11-slim

LABEL maintainer="KAFAAT Team"
LABEL description="SAHOOL Demo Data Service - Simulates API data flow"
LABEL version="16.0.0"

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install dependencies with retry for network resilience
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip && \
    pip install --no-cache-dir --timeout=300 --retries=10 -i https://mirrors.aliyun.com/pypi/simple/ httpx[http2]

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
