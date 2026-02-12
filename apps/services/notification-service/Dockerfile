# SAHOOL Notification Service v15.3
# خدمة الإشعارات المخصصة

FROM python:3.11-slim-bookworm

LABEL maintainer="SAHOOL Team"
LABEL service="notification-service"
LABEL version="15.3.0"

WORKDIR /app

# Create non-root user for security
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# No system dependencies needed - Using Python for healthcheck

# Upgrade pip to latest version
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip

# Copy requirements first for better caching
COPY apps/services/notification-service/requirements.txt .
# Install dependencies with resilient multi-mirror fallback strategy
# Try official PyPI first with long timeout, then fallback to Aliyun, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -r requirements.txt

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
