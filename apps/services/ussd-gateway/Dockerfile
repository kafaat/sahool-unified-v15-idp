# SAHOOL USSD Gateway Service
# ============================
# Handles USSD communication for feature phone users
# Version: 16.0.0

FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Install dependencies
COPY apps/services/ussd-gateway/requirements.txt .

# Copy shared libraries
COPY shared/ ./shared/

# Copy source
COPY apps/services/ussd-gateway/src/ ./src/

# Install dependencies and set ownership
RUN pip install --no-cache-dir --timeout=300 --retries=10 -r requirements.txt && \
    chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8130

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8130/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8130"]
