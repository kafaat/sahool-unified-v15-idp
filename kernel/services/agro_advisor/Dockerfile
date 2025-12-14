FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./kernel/services/agro_advisor/src/
COPY tests/ ./kernel/services/agro_advisor/tests/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8095

# Run service
CMD ["uvicorn", "kernel.services.agro_advisor.src.main:app", "--host", "0.0.0.0", "--port", "8095"]
