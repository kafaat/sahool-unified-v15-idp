FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create logs directory and set ownership
RUN mkdir -p /app/logs && \
    chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Health check - verify process is running
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "python.*src.main" || exit 1

# Run the service
CMD ["python", "-m", "src.main"]
