FROM python:3.11-slim

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
COPY apps/services/code-review-service/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

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

# Expose API port (changed from 8096 to avoid conflict with virtual-sensors)
EXPOSE 8124

# Switch to non-root user
USER sahool

# Health check - verify API is responding
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8124/health').read()" || exit 1

# Run the service
CMD ["python", "-m", "src.main"]
