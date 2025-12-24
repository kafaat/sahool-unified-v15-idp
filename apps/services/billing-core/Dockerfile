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
    PYTHONPATH=/app

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Configure apt to use HTTPS and install dependencies
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/*.list /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates apt-transport-https && \
    rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
# Note: shared libraries will be mounted or copied at deployment time if needed
COPY src ./src

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

EXPOSE 8089

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8089/healthz || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8089"]
