# SAHOOL Copilot API Dockerfile
# Dockerfile لـ Copilot API

FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────────────────────────────────────
# Dependencies Stage
# ─────────────────────────────────────────────────────────────────────────────
FROM base as dependencies

# Copy requirements
COPY apps/services/copilot-api/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip && \
    pip install --no-cache-dir --timeout=300 --retries=10 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Production Stage
# ─────────────────────────────────────────────────────────────────────────────
FROM dependencies as production

# Copy application code
COPY apps/services/copilot-api/src/ ./src/

# Create non-root user for security
RUN groupadd -r copilot && useradd -r -g copilot copilot
RUN chown -R copilot:copilot /app
USER copilot

# Expose port
EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8088/healthz || exit 1

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8088"]

# ─────────────────────────────────────────────────────────────────────────────
# Development Stage
# ─────────────────────────────────────────────────────────────────────────────
FROM dependencies as development

# Install development dependencies
RUN pip install pytest pytest-asyncio pytest-cov mypy

# Copy application code
COPY apps/services/copilot-api/ .

# Set Python path
ENV PYTHONPATH=/app

# Run with reload for development
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8088", "--reload"]
