# ============================================
# SAHOOL Field Service Dockerfile
# خدمة إدارة الحقول الزراعية
# Port: 8115
# ============================================

FROM python:3.11-slim

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="field-service"
LABEL version="16.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8115

# Create non-root user
RUN groupadd -r sahool && useradd -r -g sahool sahool

# Working directory
WORKDIR /app

# No system dependencies needed - using Python for healthcheck

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Change ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8115

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8115/healthz')" || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8115"]
