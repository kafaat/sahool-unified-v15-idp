FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 sahool && \
    useradd --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./kernel/services/iot_gateway/src/
COPY tests/ ./kernel/services/iot_gateway/tests/

# Set ownership
RUN chown -R sahool:sahool /app

# Set Python path
ENV PYTHONPATH=/app

# Switch to non-root user
USER sahool

# Expose port
EXPOSE 8096

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8096/healthz')" || exit 1

# Run service
CMD ["uvicorn", "kernel.services.iot_gateway.src.main:app", "--host", "0.0.0.0", "--port", "8096"]
