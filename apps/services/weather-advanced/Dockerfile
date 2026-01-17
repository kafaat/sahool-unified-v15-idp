# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ ⚠️  FROZEN SERVICE - DO NOT USE IN PRODUCTION                              ║
# ║ This service has been replaced by: weather-service (port 8092)             ║
# ║ Port Conflict: 8092                                                         ║
# ║ See: docs/DEPRECATED_SERVICES.md                                           ║
# ╚════════════════════════════════════════════════════════════════════════════╝

FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool


# Upgrade pip and install build tools
# nats-py 2.9.0 requires setuptools>=68.0 for build dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade "setuptools>=68.0" wheel

# Install dependencies
COPY apps/services/weather-advanced/requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt

# Copy shared modules
COPY apps/services/shared ./shared/

# Copy source code
COPY apps/services/weather-advanced/src/ ./src/

# Set ownership and switch to non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Expose port (changed from 8092 to avoid conflict with weather-service)
EXPOSE 8126

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8126/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8126"]
