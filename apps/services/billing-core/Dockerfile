# SAHOOL Billing Core Service
# خدمة الفوترة الأساسية
# Version: 15.4.0
# Port: 8089

FROM python:3.11-slim

# Labels
LABEL org.opencontainers.image.title="SAHOOL Billing Core"
LABEL org.opencontainers.image.version="15.4.0"
LABEL org.opencontainers.image.vendor="KAFAAT"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel build

# Configure pip for better network resilience
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 300" >> /root/.pip/pip.conf && \
    echo "retries = 10" >> /root/.pip/pip.conf && \
    echo "default-timeout = 300" >> /root/.pip/pip.conf && \
    echo "[install]" >> /root/.pip/pip.conf && \
    echo "prefer-binary = true" >> /root/.pip/pip.conf

# Copy and install requirements
COPY apps/services/billing-core/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Copy shared libraries (required for shared.middleware, shared.observability, shared.errors_py)
COPY shared/ ./shared/

# Copy services shared modules (needed for errors_py module)
COPY apps/services/shared/ ./apps/services/shared/

# Create compatibility layer: copy errors_py to shared/errors_py so imports work
RUN cp -r ./apps/services/shared/errors_py ./shared/ || true

# Copy application source
COPY apps/services/billing-core/src ./src

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

EXPOSE 8089

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8089/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8089"]
