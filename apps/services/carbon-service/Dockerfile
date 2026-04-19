ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

# Python environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

# Create non-root user (platform standard)
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

COPY docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh

COPY apps/services/carbon-service/requirements.txt .
COPY constraints.txt .

# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

RUN pip-install.sh -c constraints.txt -r requirements.txt

# Copy root shared modules first
COPY shared/ ./shared/

# Copy services shared modules overlay
COPY apps/services/shared/ ./shared/

# Copy application
COPY apps/services/carbon-service/src/ ./src/

# Change ownership to non-root user
RUN chown -R sahool:sahool /app

# Strip build tools from production image
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true

USER sahool

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8195/healthz')" || exit 1

EXPOSE 8195

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8195"]
