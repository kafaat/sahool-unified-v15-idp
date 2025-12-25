# SAHOOL Notification Service v15.3
# خدمة الإشعارات المخصصة

FROM python:3.11-slim

LABEL maintainer="SAHOOL Team"
LABEL service="notification-service"
LABEL version="15.3.0"

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Configure apt to use HTTPS and install system dependencies
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/*.list /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Set ownership and switch to non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Default port (can be overridden via PORT env var)
ENV PORT=8110
EXPOSE 8110

# Health check (uses default port, overridden at runtime by docker-compose)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/healthz || exit 1

# Run the application (uses PORT environment variable)
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT}
