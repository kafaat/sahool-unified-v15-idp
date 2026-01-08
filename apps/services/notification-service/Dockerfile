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

# No system dependencies needed - using Python for healthcheck

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY apps/services/notification-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY apps/services/shared ./shared/

# Copy application code
COPY apps/services/notification-service/src/ ./src/

# Set ownership and switch to non-root user
RUN chown -R sahool:sahool /app
USER sahool

# Default port (can be overridden via PORT env var)
ENV PORT=8110
EXPOSE 8110

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8110/healthz')" || exit 1

# Run the application (uses PORT environment variable)
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
