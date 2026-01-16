# SAHOOL Agent Registry Service - Dockerfile
# ===========================================
# Port: 8121

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy requirements
COPY apps/services/agent-registry/requirements.txt .

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel && \
    pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Copy shared modules (required for imports from shared/)
COPY apps/services/shared/ ./shared/

# Make registry module available at root level for imports
RUN cp -r ./shared/registry ./registry

# Copy service code
COPY apps/services/agent-registry/src /app/src

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8121

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8121/healthz').raise_for_status()"

# Run the service
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8121"]
