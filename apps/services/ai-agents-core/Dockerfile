# SAHOOL AI Agents Core Service
# Port: 8161

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

# Create non-root user for security
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Install pip-install.sh helper for resilient multi-mirror pip installs
COPY docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh

# Install dependencies
COPY constraints.txt .
COPY apps/services/ai-agents-core/requirements.txt .
# Upgrade pip, setuptools, wheel (CVE-2024-6345, PYSEC-2025-49, CVE-2026-24049)
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"
RUN pip-install.sh -c constraints.txt -r requirements.txt

# Copy shared modules (required for imports from shared/)
COPY apps/services/shared/ ./shared/


# Copy source
COPY apps/services/ai-agents-core/src/ ./src/

# Set ownership to non-root user
RUN chown -R sahool:sahool /app

# Set Python path and default port
ENV PYTHONPATH=/app:/app/src \
    PYTHONUNBUFFERED=1 \
    PORT=8161

# Expose port
EXPOSE 8161

# Switch to non-root user

# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049)
RUN rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true
USER sahool

# Health check - uses PORT env var via shell
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8161)}/healthz')"

# Run with uvicorn for production ASGI server - uses PORT env var
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
