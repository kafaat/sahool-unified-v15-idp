FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8125/healthz || exit 1

EXPOSE 8125

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8125"]
