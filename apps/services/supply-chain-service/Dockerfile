# Supply Chain Service Dockerfile
# Multi-stage build for optimized production image

# Build stage
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

# Install build dependencies
COPY docker/apt-update.sh docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements, constraints and install dependencies with multi-mirror fallback
COPY constraints.txt .
COPY apps/services/supply-chain-service/requirements.txt .
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

RUN pip-install.sh --user -c constraints.txt -r requirements.txt

# Production stage
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

# Security: Run as non-root user
RUN groupadd --gid 1000 sahool && \
    useradd --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/sahool/.local

# Copy shared libraries
COPY --chown=sahool:sahool apps/services/shared/ ./shared/


# Copy application code
COPY --chown=sahool:sahool apps/services/supply-chain-service/src ./src

# Set environment variables
ENV PATH=/home/sahool/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Service-specific environment
ENV SERVICE_NAME=supply-chain-service
ENV PORT=8230
ENV LOG_LEVEL=INFO

# Expose port
EXPOSE 8230

# Switch to non-root user

# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /home/sahool/.local/lib/python*/site-packages/setuptools* \
           /home/sahool/.local/lib/python*/site-packages/pip* \
           /home/sahool/.local/lib/python*/site-packages/wheel* \
           /home/sahool/.local/lib/python*/site-packages/pkg_resources* \
           /home/sahool/.local/lib/python*/site-packages/jaraco* \
           /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8230/healthz')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8230"]
