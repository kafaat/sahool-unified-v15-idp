ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

LABEL maintainer="KAFAAT Team"
LABEL description="SAHOOL Demo Data Service - Simulates API data flow"
LABEL version="16.0.0"

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy constraints for version pinning consistency
COPY docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh

COPY constraints.txt .

# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

RUN pip-install.sh -c constraints.txt 'httpx[http2]'

# Copy application
COPY apps/services/demo-data/main.py .

# Create non-root user (standard sahool user)
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool && \
    chown -R sahool:sahool /app


# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Environment defaults
ENV KONG_URL=http://kong:8000 \
    LOG_LEVEL=INFO \
    DEMO_MODE=continuous \
    INTERVAL_SECONDS=30

# Health check - verify process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*main.py" || exit 1

CMD ["python", "-u", "main.py"]
