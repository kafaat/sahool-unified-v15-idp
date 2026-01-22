FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY ../../shared /app/shared

# Copy service code
COPY src/ /app/src/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8130

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8130/healthz || exit 1

# Run service
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8130"]
