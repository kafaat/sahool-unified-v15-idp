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

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
# Note: shared libraries will be mounted or copied at deployment time if needed
COPY src ./src

# Copy Alembic migrations
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

EXPOSE 8089

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8089/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8089"]
