FROM python:3.11-slim

WORKDIR /app

# ✅ No curl needed - using Python for healthcheck

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities FIRST
COPY ../../shared /app/shared/

# Copy source code
COPY src/ ./src/
COPY migrations/ ./migrations/

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# ✅ Python-based healthcheck (no curl dependency)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')"

# Expose port (internal only for Layer 2)
EXPOSE 8080

CMD ["python", "-m", "src.main"]
