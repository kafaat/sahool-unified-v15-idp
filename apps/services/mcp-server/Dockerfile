FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy requirements
COPY apps/services/mcp-server/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# Copy shared modules
COPY shared/ /app/shared/

# Copy service code
COPY apps/services/mcp-server/src/ /app/src/

# Set ownership
RUN chown -R sahool:sahool /app

# Set Python path
ENV PYTHONPATH=/app

# Switch to non-root user
USER sahool

# Default port (can be overridden via MCP_SERVER_PORT env var)
ENV MCP_SERVER_PORT=8201
EXPOSE 8201

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import os,httpx; httpx.get(f'http://localhost:{os.environ.get(\"MCP_SERVER_PORT\",8201)}/health')" || exit 1

# Run server
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${MCP_SERVER_PORT}"]
