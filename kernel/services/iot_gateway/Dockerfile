FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./kernel/services/iot_gateway/src/
COPY tests/ ./kernel/services/iot_gateway/tests/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8096

# Run service
CMD ["uvicorn", "kernel.services.iot_gateway.src.main:app", "--host", "0.0.0.0", "--port", "8096"]
