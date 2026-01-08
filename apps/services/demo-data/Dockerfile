FROM python:3.12-slim

LABEL maintainer="KAFAAT Team"
LABEL description="SAHOOL Demo Data Service - Simulates API data flow"

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir httpx[http2]

# Copy application
COPY main.py .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Environment defaults
ENV KONG_URL=http://kong:8000 \
    LOG_LEVEL=INFO \
    DEMO_MODE=continuous \
    INTERVAL_SECONDS=30

CMD ["python", "-u", "main.py"]
