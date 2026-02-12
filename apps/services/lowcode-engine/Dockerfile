# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Low-Code Engine Dockerfile
# Port: 8132
# ═══════════════════════════════════════════════════════════════════════════════

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

# Security: Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip

# Install dependencies
COPY apps/services/lowcode-engine/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# Copy shared modules
COPY shared/ ./shared/

# Copy source code
COPY apps/services/lowcode-engine/src/ ./src/

# Create __init__.py files
RUN touch ./src/__init__.py ./src/api/__init__.py ./src/api/v1/__init__.py ./src/events/__init__.py 2>/dev/null || true

# Security: Change ownership and use non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Expose port
EXPOSE 8132

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8132/healthz || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8132"]
