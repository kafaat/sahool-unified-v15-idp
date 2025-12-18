FROM python:3.11-slim

WORKDIR /app

# Install build dependencies (needed for nats-py)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Create non-root user for security
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Install dependencies with increased timeout for slow networks
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=100 --retries=5 -r requirements.txt

# Copy source
COPY src/ ./src/

# Set ownership
RUN chown -R sahool:sahool /app

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER sahool

# No port exposed - this is a NATS worker service

# Health check - verify process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*worker" || exit 1

# Run worker
CMD ["python", "-m", "src.worker"]
