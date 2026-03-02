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

# Upgrade pip with multi-mirror fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --upgrade pip || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --upgrade pip

# Install dependencies
COPY constraints.txt .
COPY apps/services/lowcode-engine/requirements.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Try Aliyun mirror first with long timeout, then fallback to PyPI, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -c constraints.txt -r requirements.txt

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
