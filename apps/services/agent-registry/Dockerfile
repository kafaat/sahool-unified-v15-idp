# SAHOOL Agent Registry Service - Dockerfile
# ===========================================
# Port: 8160

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

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

# Install Python dependencies
RUN pip install --no-cache-dir --timeout=300 --retries=10 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

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
EXPOSE 8160

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8160/healthz')" || exit 1

# Run the service
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8160"]
